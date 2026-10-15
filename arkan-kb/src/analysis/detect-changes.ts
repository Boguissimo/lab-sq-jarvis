// @@T026 [US3] [FR-009] Detect changes — mapear git diff para simbolos afetados

import { execSync } from "node:child_process"
import { KBStorage } from "../graph/storage.js"
import type { GraphNode } from "../graph/types.js"

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

export interface DetectChangesResult {
  arquivosAlterados: string[]
  nosAfetados: GraphNode[]
  featuresAfetadas: string[]
  resumo: string
}

// ---------------------------------------------------------------------------
// Detect Changes
// ---------------------------------------------------------------------------

export function detectarMudancas(
  storage: KBStorage,
  scope: "staged" | "unstaged" | "all" | "compare" = "all",
  baseRef?: string,
): DetectChangesResult {
  let arquivos: string[] = []

  try {
    let cmd: string
    switch (scope) {
      case "staged":
        cmd = "git diff --cached --name-only"
        break
      case "unstaged":
        cmd = "git diff --name-only"
        break
      case "compare":
        cmd = `git diff ${baseRef ?? "main"}...HEAD --name-only`
        break
      default:
        cmd = "git diff --name-only HEAD"
    }

    const output = execSync(cmd, { encoding: "utf-8" }).trim()
    arquivos = output ? output.split("\n").filter(Boolean) : []
  } catch {
    return {
      arquivosAlterados: [],
      nosAfetados: [],
      featuresAfetadas: [],
      resumo: "Erro ao executar git diff",
    }
  }

  if (arquivos.length === 0) {
    return {
      arquivosAlterados: [],
      nosAfetados: [],
      featuresAfetadas: [],
      resumo: "Nenhum arquivo alterado",
    }
  }

  // Buscar nos que referenciam os arquivos alterados
  const nosAfetados: GraphNode[] = []
  const featuresSet = new Set<string>()

  for (const arquivo of arquivos) {
    // Buscar nos cujo filePath contém o arquivo
    const nosPorArquivo = storage.buscarNosPorLabel("File").filter(
      (n) => n.filePath === arquivo,
    )

    // Tambem buscar funcoes/classes no arquivo
    for (const label of [
      "Function",
      "Class",
      "Method",
      "Interface",
      "UserStory",
      "FunctionalRequirement",
      "Task",
    ] as const) {
      const nosDoLabel = storage.buscarNosPorLabel(label)
      for (const no of nosDoLabel) {
        if (no.filePath === arquivo || no.filePath?.endsWith(arquivo)) {
          nosAfetados.push(no)
          if (no.feature) featuresSet.add(no.feature)
        }
      }
    }

    nosAfetados.push(...nosPorArquivo)
    for (const no of nosPorArquivo) {
      if (no.feature) featuresSet.add(no.feature)
    }
  }

  // Deduplicar
  const nosUnicos = [
    ...new Map(nosAfetados.map((n) => [n.id, n])).values(),
  ]

  const featuresAfetadas = [...featuresSet]

  const resumo = [
    `${arquivos.length} arquivo(s) alterado(s)`,
    `${nosUnicos.length} simbolo(s) afetado(s)`,
    `${featuresAfetadas.length} feature(s) afetada(s)`,
    featuresAfetadas.length > 0
      ? `Features: ${featuresAfetadas.join(", ")}`
      : "",
  ]
    .filter(Boolean)
    .join(" | ")

  return {
    arquivosAlterados: arquivos,
    nosAfetados: nosUnicos,
    featuresAfetadas,
    resumo,
  }
}
