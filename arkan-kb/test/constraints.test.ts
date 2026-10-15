import { describe, it, expect, afterEach } from "vitest"
import { KBStorage } from "../src/graph/storage.js"
import { validarConstitution } from "../src/analysis/constraints.js"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { unlinkSync, existsSync } from "node:fs"
import type { GraphNode } from "../src/graph/types.js"

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

describe("validarConstitution", () => {
  it("retorna PASS para grafo vazio (nenhuma violacao aplicavel)", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)
    const storage = await KBStorage.criar(dbPath)

    const resultado = validarConstitution(storage)
    expect(resultado.status).toBe("PASS")
    expect(resultado.principiosVerificados).toBe(3)
    expect(resultado.violacoes).toHaveLength(0)

    storage.fechar()
  })

  it("P5: detecta tipo de exercicio invalido em FR", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)
    const storage = await KBStorage.criar(dbPath)

    storage.salvarNos([
      {
        id: "FR:f:FR-099",
        label: "FunctionalRequirement",
        nome: "FR-099",
        feature: "f",
        descricao: "O sistema DEVE gerar exercicios do tipo TP-007 e TP-001",
      } as GraphNode,
    ])

    const resultado = validarConstitution(storage)
    const p5 = resultado.violacoes.filter((v) => v.principio === "P5")
    expect(p5.length).toBe(1)
    expect(p5[0]!.codigo).toBe("P5-001")
    expect(p5[0]!.descricao).toContain("TP-007")
    expect(resultado.status).toBe("FAIL")

    storage.fechar()
  })

  it("P5: tipos validos TP-001 a TP-006 nao geram violacao", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)
    const storage = await KBStorage.criar(dbPath)

    storage.salvarNos([
      {
        id: "FR:f:FR-001",
        label: "FunctionalRequirement",
        nome: "FR-001",
        feature: "f",
        descricao: "Gerar TP-001 MCQ e TP-003 Lacunas",
      } as GraphNode,
    ])

    const resultado = validarConstitution(storage)
    const p5 = resultado.violacoes.filter((v) => v.principio === "P5")
    expect(p5).toHaveLength(0)

    storage.fechar()
  })

  it("P9: warning quando invariantes existem mas nenhum cobre feedback pos-exercicio", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)
    const storage = await KBStorage.criar(dbPath)

    storage.salvarNos([
      {
        id: "Invariant:f:INV-001",
        label: "Invariant",
        nome: "INV-001 Spec Governa Codigo",
        feature: "f",
        descricao: "Spec e fonte de verdade",
        executavel: false,
      } as GraphNode,
    ])

    const resultado = validarConstitution(storage)
    const p9 = resultado.violacoes.filter((v) => v.principio === "P9")
    expect(p9.length).toBe(1)
    expect(p9[0]!.severidade).toBe("WARNING")
    // WARNING nao causa FAIL
    expect(resultado.status).toBe("PASS")

    storage.fechar()
  })

  it("P9: sem warning quando invariante cobre feedback pos-exercicio", async () => {
    const dbPath = tempDbPath()
    dbPaths.push(dbPath)
    const storage = await KBStorage.criar(dbPath)

    storage.salvarNos([
      {
        id: "Invariant:f:INV-006",
        label: "Invariant",
        nome: "INV-006 Invariante de Feedback Apos Exercicio",
        feature: "f",
        descricao: "Unidade sempre exibida apos resposta ao exercicio",
        executavel: true,
      } as GraphNode,
    ])

    const resultado = validarConstitution(storage)
    const p9 = resultado.violacoes.filter((v) => v.principio === "P9")
    expect(p9).toHaveLength(0)

    storage.fechar()
  })
})
