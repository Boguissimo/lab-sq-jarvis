import { describe, it, expect, afterEach } from "vitest"
import { KBStorage } from "../src/graph/storage.js"
import { calcularImpacto } from "../src/analysis/impact.js"
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
    if (existsSync(p)) try { unlinkSync(p) } catch { /* */ }
  }
  dbPaths.length = 0
})

function criarGrafoLinear(storage: KBStorage) {
  // A -> B -> C -> D (chain de chamadas)
  const nos: GraphNode[] = [
    { id: "F:A", label: "Function", nome: "funcaoA" } as GraphNode,
    { id: "F:B", label: "Function", nome: "funcaoB" } as GraphNode,
    { id: "F:C", label: "Function", nome: "funcaoC" } as GraphNode,
    { id: "F:D", label: "Function", nome: "funcaoD" } as GraphNode,
  ]
  storage.salvarNos(nos)

  const arestas: GraphEdge[] = [
    { sourceId: "F:A", targetId: "F:B", tipo: "CALLS", confianca: 0.95 },
    { sourceId: "F:B", targetId: "F:C", tipo: "CALLS", confianca: 0.95 },
    { sourceId: "F:C", targetId: "F:D", tipo: "CALLS", confianca: 0.95 },
  ]
  storage.salvarArestas(arestas)
}

describe("calcularImpacto", () => {
  it("retorna null para no inexistente", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)
    const storage = await KBStorage.criar(dbPath)

    const resultado = calcularImpacto(storage, "nao-existe")
    expect(resultado).toBeNull()

    storage.fechar()
  })

  it("upstream: quem chama B = A (d=1)", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)
    const storage = await KBStorage.criar(dbPath)
    criarGrafoLinear(storage)

    const resultado = calcularImpacto(storage, "F:B", "upstream")
    expect(resultado).not.toBeNull()
    expect(resultado!.alvo.nome).toBe("funcaoB")
    expect(resultado!.direcao).toBe("upstream")

    // d=1: A chama B diretamente
    expect(resultado!.niveis[0]!.profundidade).toBe(1)
    expect(resultado!.niveis[0]!.nos).toHaveLength(1)
    expect(resultado!.niveis[0]!.nos[0]!.nome).toBe("funcaoA")

    storage.fechar()
  })

  it("downstream: B chama C (d=1), C chama D (d=2)", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)
    const storage = await KBStorage.criar(dbPath)
    criarGrafoLinear(storage)

    const resultado = calcularImpacto(storage, "F:B", "downstream")
    expect(resultado).not.toBeNull()

    // d=1: B chama C
    expect(resultado!.niveis[0]!.nos).toHaveLength(1)
    expect(resultado!.niveis[0]!.nos[0]!.nome).toBe("funcaoC")

    // d=2: C chama D
    expect(resultado!.niveis[1]!.nos).toHaveLength(1)
    expect(resultado!.niveis[1]!.nos[0]!.nome).toBe("funcaoD")

    storage.fechar()
  })

  it("risco LOW para poucos afetados", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)
    const storage = await KBStorage.criar(dbPath)
    criarGrafoLinear(storage)

    const resultado = calcularImpacto(storage, "F:D", "upstream")
    expect(resultado!.risco).toBe("LOW")

    storage.fechar()
  })

  it("risco HIGH para muitos callers diretos", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)
    const storage = await KBStorage.criar(dbPath)

    // Criar 10 funcoes que chamam o mesmo alvo
    const nos: GraphNode[] = [
      { id: "F:target", label: "Function", nome: "alvo" } as GraphNode,
    ]
    const arestas: GraphEdge[] = []

    for (let i = 0; i < 10; i++) {
      nos.push({ id: `F:caller${i}`, label: "Function", nome: `caller${i}` } as GraphNode)
      arestas.push({
        sourceId: `F:caller${i}`,
        targetId: "F:target",
        tipo: "CALLS",
        confianca: 0.9,
      })
    }

    storage.salvarNos(nos)
    storage.salvarArestas(arestas)

    const resultado = calcularImpacto(storage, "F:target", "upstream")
    expect(resultado!.risco).toBe("HIGH")
    expect(resultado!.totalAfetados).toBe(10)

    storage.fechar()
  })

  it("no sem arestas retorna 0 afetados", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)
    const storage = await KBStorage.criar(dbPath)

    storage.salvarNos([{ id: "F:solitario", label: "Function", nome: "solitario" } as GraphNode])

    const resultado = calcularImpacto(storage, "F:solitario", "upstream")
    expect(resultado!.totalAfetados).toBe(0)
    expect(resultado!.niveis).toHaveLength(0)
    expect(resultado!.risco).toBe("LOW")

    storage.fechar()
  })
})
