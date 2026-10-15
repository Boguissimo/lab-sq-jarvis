// @@T024 [US3] [FR-007] Visao 360 de um simbolo ou elemento de spec

import { KBStorage } from "../graph/storage.js"
import type { GraphNode, GraphEdge } from "../graph/types.js"
import { resolverNoPorNome } from "./resolver.js"

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

export interface ContextResult {
  no: GraphNode
  incoming: GraphEdge[]
  outgoing: GraphEdge[]
  incomingNos: GraphNode[]
  outgoingNos: GraphNode[]
  features: string[]
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

/** INV-7: confiancaMinima default 0.5 — arestas inferidas ocultas por default */
export function obterContexto(
  storage: KBStorage,
  nodeId: string,
  confiancaMinima: number = 0.5,
): ContextResult | null {
  const no = storage.obterNo(nodeId)
  if (!no) return null

  const incoming = storage.obterArestasDoNo(nodeId, "in")
    .filter((a) => a.confianca >= confiancaMinima)
  const outgoing = storage.obterArestasDoNo(nodeId, "out")
    .filter((a) => a.confianca >= confiancaMinima)

  const incomingNos: GraphNode[] = []
  for (const a of incoming) {
    const n = storage.obterNo(a.sourceId)
    if (n) incomingNos.push(n)
  }

  const outgoingNos: GraphNode[] = []
  for (const a of outgoing) {
    const n = storage.obterNo(a.targetId)
    if (n) outgoingNos.push(n)
  }

  // Features envolvidas
  const features = new Set<string>()
  if (no.feature) features.add(no.feature)
  for (const n of [...incomingNos, ...outgoingNos]) {
    if (n.feature) features.add(n.feature)
  }

  return {
    no,
    incoming,
    outgoing,
    incomingNos,
    outgoingNos,
    features: [...features],
  }
}

// ---------------------------------------------------------------------------
// Context por nome (busca fuzzy + contexto do primeiro resultado)
// ---------------------------------------------------------------------------

// @@T024 [US3] obterContextoPorNome
export function obterContextoPorNome(
  storage: KBStorage,
  nome: string,
): ContextResult | null {
  const no = resolverNoPorNome(storage, nome)
  if (!no) return null
  return obterContexto(storage, no.id)
}
