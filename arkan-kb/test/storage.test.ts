import { describe, it, expect, afterEach } from "vitest"
import { KBStorage } from "../src/graph/storage.js"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { unlinkSync, existsSync } from "node:fs"
import type { GraphNode, GraphEdge } from "../src/graph/types.js"

function tempDbPath(): string {
  return join(tmpdir(), `arkan-kb-test-${Date.now()}-${Math.random().toString(36).slice(2)}.db`)
}

const dbPaths: string[] = []

afterEach(() => {
  for (const p of dbPaths) {
    if (existsSync(p)) {
      try { unlinkSync(p) } catch { /* ignore */ }
    }
  }
  dbPaths.length = 0
})

function criarNo(id: string, label: string, nome: string, feature?: string): GraphNode {
  return { id, label: label as any, nome, feature, filePath: `src/${nome}.ts` }
}

describe("KBStorage", () => {
  it("cria banco e salva/recupera nos", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)

    const storage = await KBStorage.criar(dbPath)
    const nos: GraphNode[] = [
      criarNo("Function:src/foo.ts:foo", "Function", "foo", "feat-001"),
      criarNo("Class:src/bar.ts:Bar", "Class", "Bar", "feat-002"),
    ]

    storage.salvarNos(nos)
    expect(storage.contarNos()).toBe(2)

    const recuperado = storage.obterNo("Function:src/foo.ts:foo")
    expect(recuperado).toBeDefined()
    expect(recuperado!.nome).toBe("foo")
    expect(recuperado!.label).toBe("Function")

    storage.fechar()
  })

  it("salva e recupera arestas", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)

    const storage = await KBStorage.criar(dbPath)
    storage.salvarNos([criarNo("A", "Function", "a"), criarNo("B", "Function", "b")])

    const arestas: GraphEdge[] = [
      { sourceId: "A", targetId: "B", tipo: "CALLS", confianca: 0.9 },
    ]
    storage.salvarArestas(arestas)
    expect(storage.contarArestas()).toBe(1)

    const out = storage.obterArestasDoNo("A", "out")
    expect(out).toHaveLength(1)
    expect(out[0]!.targetId).toBe("B")
    expect(out[0]!.confianca).toBe(0.9)

    const inEdges = storage.obterArestasDoNo("B", "in")
    expect(inEdges).toHaveLength(1)

    storage.fechar()
  })

  it("busca por label", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)

    const storage = await KBStorage.criar(dbPath)
    storage.salvarNos([
      criarNo("F1", "Function", "fn1"),
      criarNo("C1", "Class", "Cls1"),
      criarNo("F2", "Function", "fn2"),
    ])

    const funcoes = storage.buscarNosPorLabel("Function")
    expect(funcoes).toHaveLength(2)

    const classes = storage.buscarNosPorLabel("Class")
    expect(classes).toHaveLength(1)

    storage.fechar()
  })

  it("busca texto com FTS5 ou LIKE", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)

    const storage = await KBStorage.criar(dbPath)
    storage.salvarNos([
      criarNo("FR:feat:FR-001", "FunctionalRequirement", "FR-001", "feat-001"),
      criarNo("FR:feat:FR-002", "FunctionalRequirement", "FR-002", "feat-001"),
      criarNo("F:src:foo", "Function", "processarQuestao", "feat-007"),
    ])

    // Buscar por nome parcial — funciona em FTS5 (token "processarquestao") e LIKE
    const resultados = storage.buscarTexto("processarQuestao")
    expect(resultados.length).toBeGreaterThanOrEqual(1)
    expect(resultados[0]!.nome).toBe("processarQuestao")

    const vazio = storage.buscarTexto("xyzzy_inexistente")
    expect(vazio).toHaveLength(0)

    storage.fechar()
  })

  it("salva e recupera metadata", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)

    const storage = await KBStorage.criar(dbPath)
    storage.salvarMetadata({
      versao: "0.1.0",
      ultimoCommit: "abc123",
      indexadoEm: "2026-03-24",
      estatisticas: { arquivos: 10, nosSpec: 5, nosCodigo: 100, nosSql: 3, arestas: 50, features: 2 },
    })

    const meta = storage.obterMetadata()
    expect(meta).toBeDefined()
    expect(meta!.versao).toBe("0.1.0")
    expect(meta!.estatisticas.nosSpec).toBe(5)

    storage.fechar()
  })

  it("limpar remove todos os dados", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)

    const storage = await KBStorage.criar(dbPath)
    storage.salvarNos([criarNo("A", "Function", "a")])
    storage.salvarArestas([{ sourceId: "A", targetId: "A", tipo: "CALLS", confianca: 1.0 }])
    expect(storage.contarNos()).toBe(1)

    storage.limpar()
    expect(storage.contarNos()).toBe(0)
    expect(storage.contarArestas()).toBe(0)

    storage.fechar()
  })

  it("contarNosPorLabel retorna mapa correto", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)

    const storage = await KBStorage.criar(dbPath)
    storage.salvarNos([
      criarNo("F1", "Function", "a"),
      criarNo("F2", "Function", "b"),
      criarNo("C1", "Class", "C"),
    ])

    const mapa = storage.contarNosPorLabel()
    expect(mapa["Function"]).toBe(2)
    expect(mapa["Class"]).toBe(1)

    storage.fechar()
  })

  it("persistencia sobrevive fechar/reabrir", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)

    let storage = await KBStorage.criar(dbPath)
    storage.salvarNos([criarNo("X", "Function", "persistente")])
    storage.fechar()

    storage = await KBStorage.criar(dbPath)
    const no = storage.obterNo("X")
    expect(no).toBeDefined()
    expect(no!.nome).toBe("persistente")
    storage.fechar()
  })
})
