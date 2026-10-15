// @@T015 [US1] [FR-005] Grafo de conhecimento — implementacao leve sem Graphology

import type { GraphNode, GraphEdge, NodeLabel, EdgeType } from "./types.js"

// ---------------------------------------------------------------------------
// KnowledgeGraph — grafo dirigido multi-aresta com Maps para O(1) lookup
// ---------------------------------------------------------------------------

export class KnowledgeGraph {
  private nos: Map<string, GraphNode> = new Map()
  private arestas: Map<string, GraphEdge> = new Map()
  private arestasOut: Map<string, Set<string>> = new Map()
  private arestasIn: Map<string, Set<string>> = new Map()

  // --- Nos ---

  // @@T015 [US1] adicionarNo
  adicionarNo(no: GraphNode): void {
    this.nos.set(no.id, no)
    if (!this.arestasOut.has(no.id)) this.arestasOut.set(no.id, new Set())
    if (!this.arestasIn.has(no.id)) this.arestasIn.set(no.id, new Set())
  }

  // @@T015 [US1] obterNo
  obterNo(id: string): GraphNode | undefined {
    return this.nos.get(id)
  }

  // @@T015 [US1] buscarNosPorLabel
  buscarNosPorLabel(label: NodeLabel): GraphNode[] {
    const resultado: GraphNode[] = []
    for (const no of this.nos.values()) {
      if (no.label === label) resultado.push(no)
    }
    return resultado
  }

  // @@T015 [US1] buscarNosPorFeature
  buscarNosPorFeature(feature: string): GraphNode[] {
    const resultado: GraphNode[] = []
    for (const no of this.nos.values()) {
      if (no.feature === feature) resultado.push(no)
    }
    return resultado
  }

  // @@T015 [US1] buscarNosPorNome
  buscarNosPorNome(nome: string): GraphNode[] {
    const resultado: GraphNode[] = []
    const termoLower = nome.toLowerCase()
    for (const no of this.nos.values()) {
      if (no.nome.toLowerCase().includes(termoLower)) resultado.push(no)
    }
    return resultado
  }

  // Buscar primeiro no que tenha label e nome exatos
  // @@T015 [US1] buscarNoPorLabelENome
  buscarNoPorLabelENome(label: string, nome: string): GraphNode | undefined {
    for (const no of this.nos.values()) {
      if (no.label === label && no.nome === nome) return no
    }
    return undefined
  }

  // @@T015 [US1] temNo
  temNo(id: string): boolean {
    return this.nos.has(id)
  }

  // --- Arestas ---

  // @@T015 [US1] adicionarAresta
  adicionarAresta(aresta: GraphEdge): void {
    // Ignorar arestas para targets nao resolvidos
    if (aresta.targetId.startsWith("__")) return
    if (!this.nos.has(aresta.sourceId)) return
    if (!this.nos.has(aresta.targetId)) return

    const chave = `${aresta.sourceId}->${aresta.tipo}->${aresta.targetId}`

    // Se ja existe e nova confianca e maior, substituir
    const existente = this.arestas.get(chave)
    if (existente && aresta.confianca <= existente.confianca) return

    this.arestas.set(chave, aresta)
    this.arestasOut.get(aresta.sourceId)?.add(chave)
    this.arestasIn.get(aresta.targetId)?.add(chave)
  }

  // @@T015 [US1] obterArestasDoNo
  obterArestasDoNo(
    nodeId: string,
    direcao: "in" | "out" | "all" = "all",
  ): GraphEdge[] {
    const resultado: GraphEdge[] = []

    if (direcao === "out" || direcao === "all") {
      const outKeys = this.arestasOut.get(nodeId)
      if (outKeys) {
        for (const key of outKeys) {
          const aresta = this.arestas.get(key)
          if (aresta) resultado.push(aresta)
        }
      }
    }

    if (direcao === "in" || direcao === "all") {
      const inKeys = this.arestasIn.get(nodeId)
      if (inKeys) {
        for (const key of inKeys) {
          const aresta = this.arestas.get(key)
          if (aresta) resultado.push(aresta)
        }
      }
    }

    return resultado
  }

  // @@T015 [US1] obterArestasPorTipo
  obterArestasPorTipo(tipo: EdgeType): GraphEdge[] {
    const resultado: GraphEdge[] = []
    for (const aresta of this.arestas.values()) {
      if (aresta.tipo === tipo) resultado.push(aresta)
    }
    return resultado
  }

  // --- Traversal ---

  // @@T015 [US1] bfs
  bfs(
    startId: string,
    direcao: "out" | "in",
    maxDepth: number = 3,
    filtroTipoAresta?: EdgeType[],
  ): Array<{ no: GraphNode; profundidade: number }> {
    if (!this.nos.has(startId)) return []

    const visitados = new Set<string>()
    const resultado: Array<{ no: GraphNode; profundidade: number }> = []
    const fila: Array<{ id: string; profundidade: number }> = [
      { id: startId, profundidade: 0 },
    ]

    while (fila.length > 0) {
      const { id, profundidade } = fila.shift()!
      if (visitados.has(id) || profundidade > maxDepth) continue
      visitados.add(id)

      if (id !== startId) {
        const no = this.nos.get(id)
        if (no) resultado.push({ no, profundidade })
      }

      // Obter vizinhos
      const edgeKeys =
        direcao === "out"
          ? this.arestasOut.get(id)
          : this.arestasIn.get(id)

      if (!edgeKeys) continue

      for (const key of edgeKeys) {
        const aresta = this.arestas.get(key)
        if (!aresta) continue

        // Filtrar por tipo de aresta
        if (filtroTipoAresta && !filtroTipoAresta.includes(aresta.tipo)) {
          continue
        }

        const vizinhoId =
          direcao === "out" ? aresta.targetId : aresta.sourceId

        if (!visitados.has(vizinhoId)) {
          fila.push({ id: vizinhoId, profundidade: profundidade + 1 })
        }
      }
    }

    return resultado
  }

  // --- Estatisticas ---

  get totalNos(): number {
    return this.nos.size
  }

  get totalArestas(): number {
    return this.arestas.size
  }

  // @@T015 [US1] estatisticasPorLabel
  estatisticasPorLabel(): Record<string, number> {
    const contagem: Record<string, number> = {}
    for (const no of this.nos.values()) {
      contagem[no.label] = (contagem[no.label] ?? 0) + 1
    }
    return contagem
  }

  // --- Serialization ---

  // @@T015 [US1] exportarNos
  exportarNos(): GraphNode[] {
    return [...this.nos.values()]
  }

  // @@T015 [US1] exportarArestas
  exportarArestas(): GraphEdge[] {
    return [...this.arestas.values()]
  }
}
