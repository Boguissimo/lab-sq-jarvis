// @@T023 [US2] [FR-006] Busca hibrida BM25 via SQLite FTS5

import { KBStorage } from "../graph/storage.js"
import type { GraphNode } from "../graph/types.js"
import { resolve, join } from "node:path"
import { existsSync } from "node:fs"

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

export interface ResultadoBusca {
  no: GraphNode
  score: number
  contexto?: string
}

export interface OpcoesQuery {
  limit?: string
  includeInferred?: boolean
}

// ---------------------------------------------------------------------------
// Busca no Storage (FTS5)
// ---------------------------------------------------------------------------

export function buscarNoGrafo(
  storage: KBStorage,
  termo: string,
  limite: number = 10,
): ResultadoBusca[] {
  // Buscar com margem extra para re-ranking
  const nos = storage.buscarTexto(termo, limite * 3)
  const termoLower = termo.toLowerCase()
  const tokens = termoLower.split(/[\s\-_./]+/).filter((t) => t.length > 1)

  const scored = nos.map((no) => {
    let score = 0
    const nomeLower = no.nome.toLowerCase()
    const descLower = ((no as any).descricao as string ?? "").toLowerCase()

    // Match exato no nome: +3
    if (nomeLower === termoLower) score += 3
    // Nome contem o termo inteiro: +2
    else if (nomeLower.includes(termoLower)) score += 2
    // Nome contem tokens: +0.5 por token
    else {
      for (const t of tokens) {
        if (nomeLower.includes(t)) score += 0.5
      }
    }

    // Descricao contem termo: +1
    if (descLower.includes(termoLower)) score += 1
    // Descricao contem tokens: +0.2 por token
    for (const t of tokens) {
      if (descLower.includes(t)) score += 0.2
    }

    // filePath contem termo ou tokens: +0.5
    const filePathLower = (no.filePath ?? "").toLowerCase()
    if (filePathLower.includes(termoLower)) score += 0.5
    else {
      for (const t of tokens) {
        if (filePathLower.includes(t)) score += 0.2
      }
    }

    // feature contem termo ou tokens: +0.3
    const featureLower = (no.feature ?? "").toLowerCase()
    if (featureLower.includes(termoLower)) score += 0.3
    else {
      for (const t of tokens) {
        if (featureLower.includes(t)) score += 0.1
      }
    }

    // Bonus: label spec (mais relevante para queries conceituais)
    if (["UserStory", "FunctionalRequirement", "Invariant", "Task", "Decision"].includes(no.label)) {
      score += 0.3
    }

    return { no, score }
  })

  return scored
    .filter((s) => s.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limite)
}

// ---------------------------------------------------------------------------
// CLI wrapper
// ---------------------------------------------------------------------------

// @@T023 [US2] executarQuery
export async function executarQuery(
  texto: string,
  opcoes: OpcoesQuery,
): Promise<void> {
  const rootDir = resolve(".")
  const dbPath = join(rootDir, ".arkan-kb", "index.db")

  if (!existsSync(dbPath)) {
    console.error("Indice nao encontrado. Execute: arkan-kb analyze")
    process.exit(1)
  }

  const storage = await KBStorage.criar(dbPath)
  const limite = parseInt(opcoes.limit ?? "10", 10)
  const resultados = buscarNoGrafo(storage, texto, limite)

  if (resultados.length === 0) {
    console.log(`Nenhum resultado para "${texto}"`)
    storage.fechar()
    return
  }

  console.log(`Resultados para "${texto}" (${resultados.length}):`)
  console.log()

  for (const r of resultados) {
    const label = r.no.label.padEnd(25)
    const feature = r.no.feature ? `[${r.no.feature}]` : ""
    console.log(`  ${label} ${r.no.nome} ${feature}`)
    if (r.no.filePath) {
      console.log(`    ${r.no.filePath}`)
    }
  }

  storage.fechar()
}
