// @@T042 [US1] Exportar grafo para JSON (consumido pelo viewer HTML)

import { resolve, join } from "node:path"
import { existsSync, writeFileSync } from "node:fs"
import { KBStorage } from "../graph/storage.js"
import { detectarProjeto } from "../pipeline/file-discovery.js"

/** Infere projeto a partir do filePath ou feature */
function resolverProjeto(filePath: string | undefined, feature: string | undefined): string {
  if (filePath) return detectarProjeto(filePath)

  // Para nos de spec: filePath contem o path completo .arkan/features/{projeto}/...
  // Mas se nao tem filePath, inferir do feature name
  if (!feature || feature === "global") return "global"

  // Features .specify/ (legado) nao tem projeto identificavel no path
  return "projeto-padrao"
}

export async function exportarGrafo(opcoes: {
  output?: string
}): Promise<void> {
  const rootDir = resolve(".")
  const dbPath = join(rootDir, ".arkan-kb", "index.db")

  if (!existsSync(dbPath)) {
    console.error("Indice nao encontrado. Execute: arkan-kb analyze")
    process.exit(1)
  }

  const storage = await KBStorage.criar(dbPath)

  // Exportar todos os nos com campos essenciais (sem data blob inteiro)
  const nosRaw = storage.todosOsNos()
  const nos = nosRaw.map((n) => ({
    id: n.id,
    label: n.label,
    nome: n.nome,
    feature: n.feature ?? null,
    projeto: resolverProjeto(n.filePath, n.feature),
    filePath: n.filePath ?? null,
    descricao: (n as any).descricao ?? (n as any).conteudo ?? null,
    prioridade: (n as any).prioridade ?? null,
    linhaInicio: (n as any).linhaInicio ?? null,
    exportado: (n as any).exportado ?? null,
  }))

  // Exportar arestas
  const arestasRaw = storage.todasAsArestas()
  const arestas = arestasRaw.map((a) => ({
    source: a.sourceId,
    target: a.targetId,
    tipo: a.tipo,
    confianca: a.confianca,
  }))

  // Metadata
  const meta = storage.obterMetadata()
  const nosPorLabel = storage.contarNosPorLabel()

  const grafo = {
    meta,
    nosPorLabel,
    nos,
    arestas,
  }

  const outputPath = opcoes.output ?? join(rootDir, ".arkan-kb", "grafo-data.json")
  writeFileSync(outputPath, JSON.stringify(grafo), "utf-8")

  console.log(`Grafo exportado: ${outputPath}`)
  console.log(`  Nos: ${nos.length} | Arestas: ${arestas.length}`)
  console.log(`  Tamanho: ${(Buffer.byteLength(JSON.stringify(grafo)) / 1048576).toFixed(1)}MB`)

  storage.fechar()
}
