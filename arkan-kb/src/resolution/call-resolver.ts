// @@T013 [US1] [FR-002] Resolucao de chamadas cross-file

import type { GraphNode, GraphEdge } from "../graph/types.js"

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

/** Mapa de simbolo exportado -> nodeId */
type SymbolTable = Map<string, string>

/** Mapa de arquivo -> simbolos importados (binding -> sourceFile) */
type ImportMap = Map<string, Map<string, string>>

// ---------------------------------------------------------------------------
// Construir SymbolTable global
// ---------------------------------------------------------------------------

export function construirSymbolTable(nos: GraphNode[]): SymbolTable {
  const tabela: SymbolTable = new Map()

  for (const no of nos) {
    if (
      no.label === "Function" ||
      no.label === "Class" ||
      no.label === "Interface"
    ) {
      const tipado = no as { exportado?: boolean; nome: string; id: string }
      if (tipado.exportado) {
        // Global: nome -> id (ultimo ganha, ok para MVP)
        tabela.set(no.nome, no.id)
      }
    }
  }

  return tabela
}

// ---------------------------------------------------------------------------
// Construir ImportMap
// ---------------------------------------------------------------------------

// @@T013 [US1] construirImportMap
export function construirImportMap(
  arestas: GraphEdge[],
  resolvedImports: Map<string, string | null>,
): ImportMap {
  const mapa: ImportMap = new Map()

  for (const aresta of arestas) {
    if (aresta.tipo !== "IMPORTS") continue
    if (!aresta.targetId.startsWith("__IMPORT__:")) continue

    const modulo = aresta.targetId.replace("__IMPORT__:", "")
    const sourceFileId = aresta.sourceId

    // Obter file path do source
    const sourceFilePath = sourceFileId.replace("File:", "").replace(/:.*/, "")

    const chave = `${sourceFilePath}:${modulo}`
    const resolvedPath = resolvedImports.get(chave)

    if (!resolvedPath) continue

    const bindings =
      (aresta.propriedades?.["bindings"] as string[] | undefined) ?? []

    if (!mapa.has(sourceFilePath)) {
      mapa.set(sourceFilePath, new Map())
    }

    for (const binding of bindings) {
      mapa.get(sourceFilePath)!.set(binding, resolvedPath)
    }
  }

  return mapa
}

// ---------------------------------------------------------------------------
// Resolver chamadas __UNRESOLVED_CALL__
// ---------------------------------------------------------------------------

// @@T013 [US1] resolverChamadas
export function resolverChamadas(
  arestas: GraphEdge[],
  nos: GraphNode[],
  symbolTable: SymbolTable,
  importMap: ImportMap,
): GraphEdge[] {
  const arestasResolvidas: GraphEdge[] = []

  for (const aresta of arestas) {
    if (!aresta.targetId.startsWith("__UNRESOLVED_CALL__:")) {
      arestasResolvidas.push(aresta)
      continue
    }

    const calleeName = aresta.targetId.replace("__UNRESOLVED_CALL__:", "")

    // Extrair o nome simples (para "obj.metodo", pegar "metodo")
    const nomeParts = calleeName.split(".")
    const nomeSimples = nomeParts[nomeParts.length - 1]!

    // Obter o file path do caller
    const callerNode = nos.find((n) => n.id === aresta.sourceId)
    const callerFilePath = callerNode?.filePath

    // 1. Tentar resolver via import scope
    if (callerFilePath && importMap.has(callerFilePath)) {
      const fileImports = importMap.get(callerFilePath)!
      const sourceFile = fileImports.get(nomeSimples)

      if (sourceFile) {
        // Buscar o simbolo no arquivo fonte
        const targetNode = nos.find(
          (n) =>
            n.filePath === sourceFile &&
            n.nome === nomeSimples &&
            (n.label === "Function" ||
              n.label === "Class" ||
              n.label === "Method"),
        )

        if (targetNode) {
          arestasResolvidas.push({
            ...aresta,
            targetId: targetNode.id,
            confianca: 0.9, // import-scoped
          })
          continue
        }
      }
    }

    // 2. Tentar resolver via SymbolTable global
    const globalTarget = symbolTable.get(nomeSimples)
    if (globalTarget) {
      arestasResolvidas.push({
        ...aresta,
        targetId: globalTarget,
        confianca: 0.5, // global fuzzy
      })
      continue
    }

    // 3. Nao resolvido — descartar (chamada externa ou built-in)
    // Nao incluir na lista final
  }

  return arestasResolvidas
}
