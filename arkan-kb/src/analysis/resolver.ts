// @@T024 [US3] Resolucao de no por nome — prefere match exato e versao mais recente

import { KBStorage } from "../graph/storage.js"
import type { GraphNode } from "../graph/types.js"

/** Extrai o timestamp da migration do filePath (`.../YYYYMMDDHHMMSS_*.sql`) */
function timestampMigration(no: GraphNode): string {
  const base = no.filePath?.split(/[\\/]/).pop() ?? ""
  return base.match(/^\d+/)?.[0] ?? "0"
}

/**
 * Resolve um nome para o no mais relevante.
 *
 * Entidades versionadas por migration (RPC, Table, Policy) aparecem como N nos
 * — um por arquivo SQL que as redefine. O ranking FTS tende a devolver a versao
 * mais antiga; aqui preferimos o match exato de nome e, entre empates, a migration
 * mais recente, para que impact/context apontem para a definicao vigente.
 */
export function resolverNoPorNome(
  storage: KBStorage,
  nome: string,
): GraphNode | null {
  // 1) Match exato direto nos nós armazenados (sem ranking FTS, sem corte top-N).
  // Garante que a definição vigente nunca seja descartada por cair fora do top-N
  // do FTS — caso comum em nomes populares e RPCs versionadas por migration.
  const exatos = storage.buscarNosPorNome(nome)
  if (exatos.length > 0) {
    // Entre matches exatos, a migration mais recente vence (string de digitos comparavel)
    return exatos.reduce((maisRecente, atual) =>
      timestampMigration(atual) > timestampMigration(maisRecente) ? atual : maisRecente,
    )
  }

  // 2) Fallback textual (FTS/LIKE) quando não há match exato de nome.
  const candidatos = storage.buscarTexto(nome, 10)
  if (candidatos.length === 0) return null
  return candidatos[0]!
}
