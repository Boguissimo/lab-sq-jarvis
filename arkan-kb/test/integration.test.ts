// Testes de integracao: pipeline end-to-end + annotator + incremental

import { describe, it, expect, beforeAll, afterAll } from "vitest"
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync, cpSync } from "node:fs"
import { join } from "node:path"
import { KnowledgeGraph } from "../src/graph/knowledge-graph.js"
import { KBStorage } from "../src/graph/storage.js"
import { linkarSpecCode } from "../src/graph/linker.js"
import { parsearArquivoSpec } from "../src/parsers/spec-parser.js"
import { parsearCodigo } from "../src/parsers/code-parser.js"
import { parsearSql } from "../src/parsers/sql-parser.js"
import { buscarNoGrafo } from "../src/analysis/search.js"
import { obterContextoPorNome } from "../src/analysis/context.js"
import { calcularImpactoPorNome } from "../src/analysis/impact.js"
import { validarConstitution } from "../src/analysis/constraints.js"
import { gerarPropostas, aplicarAnotacao } from "../src/analysis/annotator.js"
import { carregarHashes, salvarHashes, filtrarAlterados } from "../src/pipeline/incremental.js"
import type { CodeAnnotation } from "../src/graph/types.js"

const FIXTURES_DIR = join(import.meta.dirname, "fixtures")
const TMP_DIR = join(import.meta.dirname, ".tmp-integration")

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function lerFixture(nome: string): string {
  return readFileSync(join(FIXTURES_DIR, nome), "utf-8")
}

function criarGrafoCompleto() {
  const kg = new KnowledgeGraph()
  const anotacoes: CodeAnnotation[] = []

  // Parse spec
  const spec = parsearArquivoSpec(lerFixture("sample-spec.md"), "teste", "spec.md")
  for (const no of spec.nos) kg.adicionarNo(no)

  // Parse tasks
  const tasks = parsearArquivoSpec(lerFixture("sample-tasks.md"), "teste", "tasks.md")
  for (const no of tasks.nos) kg.adicionarNo(no)

  // Parse code
  const code = parsearCodigo(lerFixture("sample-code.ts"), "packages/teste/src/code.ts")
  for (const no of code.nos) kg.adicionarNo(no)
  for (const aresta of code.arestas) kg.adicionarAresta(aresta)
  anotacoes.push(...code.anotacoes)

  // Parse SQL
  const sql = parsearSql(lerFixture("sample-migration.sql"), "migrations/001.sql")
  for (const no of sql.nos) kg.adicionarNo(no)
  for (const aresta of sql.arestas) kg.adicionarAresta(aresta)

  // Link spec↔code
  const linkResult = linkarSpecCode(kg, anotacoes)
  for (const aresta of linkResult.arestas) kg.adicionarAresta(aresta)

  return { kg, linkResult, anotacoes }
}

// ---------------------------------------------------------------------------
// Suite 1: Pipeline end-to-end
// ---------------------------------------------------------------------------

describe("Pipeline end-to-end", () => {
  let storage: KBStorage
  let dbPath: string

  beforeAll(async () => {
    if (existsSync(TMP_DIR)) rmSync(TMP_DIR, { recursive: true })
    mkdirSync(TMP_DIR, { recursive: true })
    dbPath = join(TMP_DIR, "test.db")

    const { kg } = criarGrafoCompleto()

    storage = await KBStorage.criar(dbPath)
    storage.salvarNos(kg.exportarNos())
    storage.salvarArestas(kg.exportarArestas())
  })

  afterAll(() => {
    storage?.fechar()
    if (existsSync(TMP_DIR)) rmSync(TMP_DIR, { recursive: true })
  })

  it("deve indexar nos de spec + code + sql", () => {
    const total = storage.contarNos()
    expect(total).toBeGreaterThan(10)

    const porLabel = storage.contarNosPorLabel()
    expect(porLabel["UserStory"]).toBeGreaterThanOrEqual(2)
    expect(porLabel["FunctionalRequirement"]).toBeGreaterThanOrEqual(3)
    expect(porLabel["Task"]).toBeGreaterThanOrEqual(5)
    expect(porLabel["Function"]).toBeGreaterThanOrEqual(3)
  })

  it("deve criar arestas spec↔code", () => {
    const totalArestas = storage.contarArestas()
    expect(totalArestas).toBeGreaterThan(5)
  })

  it("deve buscar por texto e retornar resultados rankeados", () => {
    const resultados = buscarNoGrafo(storage, "FR-001", 5)
    expect(resultados.length).toBeGreaterThan(0)
    expect(resultados[0]!.score).toBeGreaterThan(0)
  })

  it("deve buscar user stories por nome", () => {
    // US sao armazenadas como "US1 — Buscar conceitos no grafo"
    const resultados = buscarNoGrafo(storage, "Buscar conceitos", 5)
    expect(resultados.length).toBeGreaterThan(0)
    expect(resultados.some((r) => r.no.label === "UserStory")).toBe(true)
  })

  it("deve retornar contexto de um simbolo", () => {
    const ctx = obterContextoPorNome(storage, "parsearArquivo")
    expect(ctx).not.toBeNull()
    expect(ctx!.no.label).toBe("Function")
    // parsearArquivo chama processarConteudo → deve ter outgoing
    expect(ctx!.outgoing.length).toBeGreaterThan(0)
  })

  it("deve calcular impacto upstream", () => {
    // processarConteudo e chamado por parsearArquivo
    const impacto = calcularImpactoPorNome(storage, "processarConteudo", "upstream")
    expect(impacto).not.toBeNull()
    expect(impacto!.totalAfetados).toBeGreaterThan(0)
  })

  it("deve validar constitution sem crash", () => {
    const resultado = validarConstitution(storage)
    expect(resultado).toBeDefined()
    expect(resultado.principiosVerificados).toBeGreaterThanOrEqual(0)
  })

  it("deve detectar tabelas SQL", () => {
    const porLabel = storage.contarNosPorLabel()
    expect(porLabel["Table"]).toBeGreaterThanOrEqual(1)
  })
})

// ---------------------------------------------------------------------------
// Suite 2: Annotator end-to-end
// ---------------------------------------------------------------------------

describe("Annotator end-to-end", () => {
  let storage: KBStorage
  let tmpCodePath: string

  beforeAll(async () => {
    if (existsSync(TMP_DIR)) rmSync(TMP_DIR, { recursive: true })
    mkdirSync(TMP_DIR, { recursive: true })

    const dbPath = join(TMP_DIR, "annotator.db")
    const { kg } = criarGrafoCompleto()

    storage = await KBStorage.criar(dbPath)
    storage.salvarNos(kg.exportarNos())
    storage.salvarArestas(kg.exportarArestas())

    // Copiar fixture para tmp (para testar apply sem modificar fixtures)
    tmpCodePath = join(TMP_DIR, "sample-code.ts")
    cpSync(join(FIXTURES_DIR, "sample-code.ts"), tmpCodePath)
  })

  afterAll(() => {
    storage?.fechar()
    if (existsSync(TMP_DIR)) rmSync(TMP_DIR, { recursive: true })
  })

  it("deve gerar propostas para simbolos sem anotacao", () => {
    const resultado = gerarPropostas(storage)
    expect(resultado.totalSimbolosSemAnotacao).toBeGreaterThan(0)
    // Nem todos terao propostas (depende de heuristicas)
    expect(resultado).toBeDefined()
  })

  it("deve aplicar anotacao a um arquivo", () => {
    const antes = readFileSync(tmpCodePath, "utf-8")
    const linhaFuncao = antes.split("\n").findIndex((l) => l.includes("function validarFormato")) + 1

    aplicarAnotacao(tmpCodePath, linhaFuncao, "@@T099 [US1] validarFormato")

    const depois = readFileSync(tmpCodePath, "utf-8")
    expect(depois).toContain("// @@T099 [US1] validarFormato")
    // Anotacao deve estar ANTES da funcao
    const linhas = depois.split("\n")
    const idxAnotacao = linhas.findIndex((l) => l.includes("@@T099"))
    const idxFuncao = linhas.findIndex((l) => l.includes("function validarFormato"))
    expect(idxAnotacao).toBeLessThan(idxFuncao)
  })

  it("deve detectar anotacao aplicada no re-parse", () => {
    const conteudo = readFileSync(tmpCodePath, "utf-8")
    const resultado = parsearCodigo(conteudo, tmpCodePath)
    // Deve encontrar a anotacao @@T099
    const anotacao099 = resultado.anotacoes.find((a) => a.taskId === "T099")
    expect(anotacao099).toBeDefined()
    expect(anotacao099!.userStoryId).toBe("US1")
  })
})

// ---------------------------------------------------------------------------
// Suite 3: Incremental
// ---------------------------------------------------------------------------

describe("Incremental re-indexacao", () => {
  const tmpDir = join(TMP_DIR, "incremental")

  beforeAll(() => {
    if (existsSync(tmpDir)) rmSync(tmpDir, { recursive: true })
    mkdirSync(tmpDir, { recursive: true })
  })

  afterAll(() => {
    if (existsSync(TMP_DIR)) rmSync(TMP_DIR, { recursive: true })
  })

  it("deve salvar e carregar hashes", () => {
    const hashes = { "file1.ts": "abc123", "file2.ts": "def456" }
    salvarHashes(tmpDir, hashes)
    const loaded = carregarHashes(tmpDir)
    expect(loaded).toEqual(hashes)
  })

  it("deve filtrar arquivos nao alterados", () => {
    const hashesAnteriores = { "a.ts": "hash1", "b.ts": "hash2" }

    // Criar arquivos reais para hashear
    writeFileSync(join(tmpDir, "a.ts"), "const a = 1")
    writeFileSync(join(tmpDir, "b.ts"), "const b = 2")

    const arquivos = [
      { caminhoRelativo: "a.ts", caminhoAbsoluto: join(tmpDir, "a.ts"), extensao: ".ts", tamanho: 12, tipo: "code" as const },
      { caminhoRelativo: "b.ts", caminhoAbsoluto: join(tmpDir, "b.ts"), extensao: ".ts", tamanho: 12, tipo: "code" as const },
    ]

    // Primeira vez: todos alterados (hashes anteriores nao batem)
    const r1 = filtrarAlterados(arquivos, hashesAnteriores)
    expect(r1.alterados.length).toBe(2)

    // Segunda vez com hashes corretos: 0 alterados
    const r2 = filtrarAlterados(arquivos, r1.hashesNovos)
    expect(r2.alterados.length).toBe(0)

    // Modificar um arquivo: 1 alterado
    writeFileSync(join(tmpDir, "b.ts"), "const b = 999")
    const r3 = filtrarAlterados(arquivos, r1.hashesNovos)
    expect(r3.alterados.length).toBe(1)
    expect(r3.alterados[0]!.caminhoRelativo).toBe("b.ts")
  })
})
