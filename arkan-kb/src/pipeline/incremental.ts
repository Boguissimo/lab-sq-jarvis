// @@T020 [US1] [FR-014] Re-indexacao incremental por hash de arquivo

import { createHash } from "node:crypto"
import { readFileSync, existsSync, writeFileSync, mkdirSync } from "node:fs"
import { join, dirname } from "node:path"
import type { ArquivoDescoberto } from "./file-discovery.js"

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

interface FileHashMap {
  [caminhoRelativo: string]: string
}

// ---------------------------------------------------------------------------
// Calcular hash SHA256
// ---------------------------------------------------------------------------

function hashArquivo(caminhoAbsoluto: string): string {
  const conteudo = readFileSync(caminhoAbsoluto)
  return createHash("sha256").update(conteudo).digest("hex").slice(0, 16)
}

// ---------------------------------------------------------------------------
// Carregar/Salvar hashes
// ---------------------------------------------------------------------------

// @@T020 caminhoHashes
// // @@T020 caminhoHashes
// @@T020 caminhoHashes
function caminhoHashes(kbDir: string): string {
  return join(kbDir, "file-hashes.json")
}

// // @@T020 carregarHashes
// @@T020 carregarHashes
// @@T020 carregarHashes
export function carregarHashes(kbDir: string): FileHashMap {
  const caminho = caminhoHashes(kbDir)
  if (!existsSync(caminho)) return {}
  try {
    return JSON.parse(readFileSync(caminho, "utf-8")) as FileHashMap
  } catch {
    return {}
  }
}
// // @@T020 salvarHashes

// @@T020 salvarHashes
export function salvarHashes(kbDir: string, hashes: FileHashMap): void {
  // @@T020 salvarHashes
  const caminho = caminhoHashes(kbDir)
  const dir = dirname(caminho)
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true })
  writeFileSync(caminho, JSON.stringify(hashes, null, 2), "utf-8")
}

// ---------------------------------------------------------------------------
// Filtrar arquivos alterados
// // @@T020 filtrarAlterados
// ---------------------------------------------------------------------------

// @@T020 filtrarAlterados
export function filtrarAlterados(
  // @@T020 filtrarAlterados
  arquivos: ArquivoDescoberto[],
  hashesAnteriores: FileHashMap,
): { alterados: ArquivoDescoberto[]; hashesNovos: FileHashMap } {
  const hashesNovos: FileHashMap = {}
  const alterados: ArquivoDescoberto[] = []

  for (const arquivo of arquivos) {
    const hashAtual = hashArquivo(arquivo.caminhoAbsoluto)
    hashesNovos[arquivo.caminhoRelativo] = hashAtual

    const hashAnterior = hashesAnteriores[arquivo.caminhoRelativo]
    if (hashAnterior !== hashAtual) {
      alterados.push(arquivo)
    }
  }

  return { alterados, hashesNovos }
}
