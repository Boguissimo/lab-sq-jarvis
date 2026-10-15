// @@T025 [US3] [FR-008] Blast radius — impacto upstream/downstream

import { KBStorage } from "../graph/storage.js"
import type { GraphNode, GraphEdge } from "../graph/types.js"
import { resolverNoPorNome } from "./resolver.js"

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

export interface ImpactResult {
  alvo: GraphNode
  direcao: "upstream" | "downstream"
  niveis: ImpactLevel[]
  risco: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
  totalAfetados: number
}

export interface ImpactLevel {
  profundidade: number
  rotulo: string
  nos: GraphNode[]
}

// ---------------------------------------------------------------------------
// Impact
// ---------------------------------------------------------------------------

/** INV-7: confiancaMinima default 0.5 — arestas inferidas ignoradas no traversal */
export function calcularImpacto(
  storage: KBStorage,
  nodeId: string,
  direcao: "upstream" | "downstream" = "upstream",
  maxDepth: number = 3,
  confiancaMinima: number = 0.5,
): ImpactResult | null {
  const alvo = storage.obterNo(nodeId)
  if (!alvo) return null

  const visitados = new Set<string>()
  const niveis: ImpactLevel[] = []
  let fila: string[] = [nodeId]
  visitados.add(nodeId)

  const rotulos = [
    "WILL BREAK — callers diretos",
    "LIKELY AFFECTED — dependentes indiretos",
    "MAY NEED TESTING — transitivos",
  ]

  for (let d = 1; d <= maxDepth; d++) {
    const proximaFila: string[] = []
    const nosNesteNivel: GraphNode[] = []

    for (const id of fila) {
      const tipo = direcao === "upstream" ? "in" : "out"
      const arestas = storage.obterArestasDoNo(id, tipo)
        .filter((a) => a.confianca >= confiancaMinima)

      for (const aresta of arestas) {
        const vizinhoId =
          direcao === "upstream" ? aresta.sourceId : aresta.targetId

        if (visitados.has(vizinhoId)) continue
        visitados.add(vizinhoId)

        const vizinho = storage.obterNo(vizinhoId)
        if (vizinho) {
          nosNesteNivel.push(vizinho)
          proximaFila.push(vizinhoId)
        }
      }
    }

    if (nosNesteNivel.length > 0) {
      niveis.push({
        profundidade: d,
        rotulo: rotulos[d - 1] ?? `Profundidade ${d}`,
        nos: nosNesteNivel,
      })
    }

    fila = proximaFila
  }

  const totalAfetados = niveis.reduce((sum, n) => sum + n.nos.length, 0)
  const d1Count = niveis[0]?.nos.length ?? 0

  let risco: ImpactResult["risco"]
  if (d1Count > 15) risco = "CRITICAL"
  else if (d1Count > 8) risco = "HIGH"
  else if (d1Count > 3) risco = "MEDIUM"
  else risco = "LOW"

  return {
    alvo,
    direcao,
    niveis,
    risco,
    totalAfetados,
  }
}

// ---------------------------------------------------------------------------
// Impact por nome (busca + impacto)
// ---------------------------------------------------------------------------

// @@T025 [US4] calcularImpactoPorNome
export function calcularImpactoPorNome(
  storage: KBStorage,
  nome: string,
  direcao: "upstream" | "downstream" = "upstream",
): ImpactResult | null {
  const no = resolverNoPorNome(storage, nome)
  if (!no) return null
  return calcularImpacto(storage, no.id, direcao)
}
