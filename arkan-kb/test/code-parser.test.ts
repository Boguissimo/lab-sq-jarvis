// @@T014 [US1] [FR-002] [FR-003] Testes do code-parser e sql-parser
import { describe, it, expect } from "vitest"
import { readFileSync } from "node:fs"
import { resolve, dirname } from "node:path"
import { fileURLToPath } from "node:url"
import { parsearCodigo, extrairAnotacoes } from "../src/parsers/code-parser.js"
import { parsearSql } from "../src/parsers/sql-parser.js"

const __dirname = dirname(fileURLToPath(import.meta.url))

function lerFixture(nome: string): string {
  return readFileSync(resolve(__dirname, "fixtures", nome), "utf-8")
}

// ---------------------------------------------------------------------------
// code-parser.ts
// ---------------------------------------------------------------------------

describe("parsearCodigo", () => {
  const conteudo = lerFixture("sample-code.ts")
  const resultado = parsearCodigo(conteudo, "test/fixtures/sample-code.ts")

  it("extrai no de arquivo", () => {
    const arquivos = resultado.nos.filter((n) => n.label === "File")
    expect(arquivos).toHaveLength(1)
    expect(arquivos[0]!.nome).toBe("sample-code.ts")
  })

  it("extrai funcoes exportadas e privadas", () => {
    const funcoes = resultado.nos.filter((n) => n.label === "Function")
    const nomes = funcoes.map((f) => f.nome)
    expect(nomes).toContain("parsearArquivo")
    expect(nomes).toContain("processarConteudo")
    expect(nomes).toContain("validarFormato")

    const parsear = funcoes.find((f) => f.nome === "parsearArquivo")
    expect((parsear as any).exportado).toBe(true)

    const processar = funcoes.find((f) => f.nome === "processarConteudo")
    expect((processar as any).exportado).toBe(false)
  })

  it("extrai arrow functions exportadas", () => {
    const funcoes = resultado.nos.filter((n) => n.label === "Function")
    const criarPadrao = funcoes.find((f) => f.nome === "criarPadrao")
    expect(criarPadrao).toBeDefined()
    expect((criarPadrao as any).exportado).toBe(true)
  })

  it("extrai classes com metodos", () => {
    const classes = resultado.nos.filter((n) => n.label === "Class")
    expect(classes).toHaveLength(1)
    expect(classes[0]!.nome).toBe("GerenciadorIndice")

    const metodos = resultado.nos.filter((n) => n.label === "Method")
    const nomesMetodos = metodos.map((m) => m.nome)
    expect(nomesMetodos).toContain("adicionar")
    expect(nomesMetodos).toContain("buscar")
    expect(nomesMetodos).toContain("listar")
  })

  it("extrai interfaces", () => {
    const ifaces = resultado.nos.filter((n) => n.label === "Interface")
    expect(ifaces).toHaveLength(1)
    expect(ifaces[0]!.nome).toBe("ConfiguracaoParser")
  })

  it("gera arestas CONTAINS (File -> simbolos)", () => {
    const contains = resultado.arestas.filter((a) => a.tipo === "CONTAINS")
    expect(contains.length).toBeGreaterThanOrEqual(3)
  })

  it("gera arestas HAS_METHOD (Class -> Method)", () => {
    const hasMethods = resultado.arestas.filter((a) => a.tipo === "HAS_METHOD")
    expect(hasMethods).toHaveLength(3)
  })

  it("detecta chamadas entre funcoes do mesmo arquivo", () => {
    const calls = resultado.arestas.filter(
      (a) => a.tipo === "CALLS" && a.confianca >= 0.9,
    )
    // parsearArquivo chama processarConteudo e resolve
    expect(calls.length).toBeGreaterThanOrEqual(1)
  })

  it("gera arestas IMPORTS", () => {
    const imports = resultado.arestas.filter((a) => a.tipo === "IMPORTS")
    expect(imports.length).toBeGreaterThanOrEqual(1)
  })
})

// ---------------------------------------------------------------------------
// extrairAnotacoes
// ---------------------------------------------------------------------------

describe("extrairAnotacoes", () => {
  it("extrai anotacoes @@TXXX do codigo", () => {
    const conteudo = lerFixture("sample-code.ts")
    const anotacoes = extrairAnotacoes(conteudo, "test/fixtures/sample-code.ts")
    expect(anotacoes).toHaveLength(1)
    expect(anotacoes[0]!.taskId).toBe("T004")
    expect(anotacoes[0]!.userStoryId).toBe("US1")
    expect(anotacoes[0]!.frId).toBe("FR-002")
  })

  it("extrai anotacao com INV", () => {
    const codigo = `// @@T033 [US5] [FR-012] [INV-005] Validar P1`
    const anotacoes = extrairAnotacoes(codigo, "test.ts")
    expect(anotacoes).toHaveLength(1)
    expect(anotacoes[0]!.invId).toBe("INV-005")
  })

  it("retorna vazio sem anotacoes", () => {
    const codigo = `export function foo() { return 1 }`
    const anotacoes = extrairAnotacoes(codigo, "test.ts")
    expect(anotacoes).toHaveLength(0)
  })
})

// ---------------------------------------------------------------------------
// sql-parser.ts
// ---------------------------------------------------------------------------

describe("parsearSql", () => {
  const conteudo = lerFixture("sample-migration.sql")
  const resultado = parsearSql(conteudo, "migrations/test.sql")

  it("extrai tabelas", () => {
    const tabelas = resultado.nos.filter((n) => n.label === "Table")
    expect(tabelas).toHaveLength(2)
    const nomes = tabelas.map((t) => t.nome)
    expect(nomes).toContain("categorias")
    expect(nomes).toContain("itens")
  })

  it("extrai funcoes RPC", () => {
    const rpcs = resultado.nos.filter((n) => n.label === "RPC")
    expect(rpcs).toHaveLength(1)
    expect(rpcs[0]!.nome).toBe("buscar_itens_por_categoria")
  })

  it("extrai policies", () => {
    const policies = resultado.nos.filter((n) => n.label === "Policy")
    expect(policies).toHaveLength(1)
    expect(policies[0]!.nome).toBe("Users can view own items")
  })

  it("gera arestas USES_TABLE (RPC -> Table)", () => {
    const usesTable = resultado.arestas.filter((a) => a.tipo === "USES_TABLE")
    expect(usesTable.length).toBeGreaterThanOrEqual(1)
  })
})
