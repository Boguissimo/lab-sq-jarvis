// @@T034 [US7] [FR-011] Parser de git log — mapear commits a features e arquivos

import { execSync } from "node:child_process"

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

export interface GitCommit {
  hash: string
  message: string
  arquivos: string[]
  feature?: string
  scope?: string
  tipo?: string
  taskIds?: string[]
}

export interface GitFeatureMap {
  feature: string
  commits: GitCommit[]
  arquivos: Set<string>
}

export interface GitLogResult {
  commits: GitCommit[]
  porFeature: Map<string, GitFeatureMap>
  arquivoParaFeatures: Map<string, string[]>
  totalCommits: number
  totalArquivos: number
  totalFeaturesDetectadas: number
}

// ---------------------------------------------------------------------------
// Patterns de commit message
// ---------------------------------------------------------------------------

// feat(scope): descricao | fix(scope): descricao
const CONVENTIONAL_RE = /^(\w+)\(([^)]+)\):\s*(.+)$/

// Mapeamento de commit scopes conhecidos para feature IDs — lista de exemplo.
// Cada projeto adota as proprias convencoes de scope; acrescente as suas aqui,
// ou apague as entradas de exemplo se preferir resolver so pelo padrao no corpo
// da mensagem (FEATURE_IN_MSG_RE, logo abaixo).
const SCOPE_TO_FEATURE: Record<string, string> = {
  "arkan-kb": "101-000-arkan-kb",
  "arkan": "global",
  "db": "global",
}

// Pattern para extrair feature do message body
const FEATURE_IN_MSG_RE = /\b(\d{3})-(?:\d{3}-)?([\w-]+)\b/g

// Pattern para extrair task IDs
const TASK_RE = /\b(T\d{3})\b/g

// ---------------------------------------------------------------------------
// Parser
// ---------------------------------------------------------------------------

export function parsearGitLog(rootDir: string): GitLogResult {
  // Obter log completo com arquivos
  let logRaw: string
  try {
    logRaw = execSync(
      'git log --all --format="COMMIT:%H %s" --name-only',
      {
        cwd: rootDir,
        encoding: "utf-8",
        maxBuffer: 50 * 1024 * 1024, // 50MB
      },
    )
  } catch {
    return {
      commits: [],
      porFeature: new Map(),
      arquivoParaFeatures: new Map(),
      totalCommits: 0,
      totalArquivos: 0,
      totalFeaturesDetectadas: 0,
    }
  }

  const linhas = logRaw.split("\n")
  const commits: GitCommit[] = []
  let commitAtual: GitCommit | null = null

  for (const linha of linhas) {
    if (linha.startsWith("COMMIT:")) {
      // Salvar commit anterior
      if (commitAtual) commits.push(commitAtual)

      const match = linha.match(/^COMMIT:(\w+)\s+(.+)$/)
      if (!match) continue

      const hash = match[1]!
      const message = match[2]!

      // Parse conventional commit
      const convMatch = message.match(CONVENTIONAL_RE)
      const tipo = convMatch?.[1]
      const scope = convMatch?.[2]
      const feature = scope ? resolverFeature(scope, message) : resolverFeaturePorMsg(message)

      // Extrair task IDs
      const taskMatches = message.match(TASK_RE)
      const taskIds = taskMatches ? [...new Set(taskMatches)] : undefined

      commitAtual = {
        hash,
        message,
        arquivos: [],
        feature: feature ?? undefined,
        scope: scope ?? undefined,
        tipo: tipo ?? undefined,
        taskIds,
      }
    } else if (commitAtual && linha.trim().length > 0) {
      // Linha de arquivo
      const arquivo = linha.trim()
      // Filtrar apenas arquivos de codigo
      if (
        arquivo.endsWith(".ts") ||
        arquivo.endsWith(".tsx") ||
        arquivo.endsWith(".js") ||
        arquivo.endsWith(".jsx") ||
        arquivo.endsWith(".sql")
      ) {
        commitAtual.arquivos.push(arquivo)
      }
    }
  }
  if (commitAtual) commits.push(commitAtual)

  // Agrupar por feature
  const porFeature = new Map<string, GitFeatureMap>()
  for (const commit of commits) {
    if (!commit.feature || commit.feature === "global") continue
    if (!porFeature.has(commit.feature)) {
      porFeature.set(commit.feature, {
        feature: commit.feature,
        commits: [],
        arquivos: new Set(),
      })
    }
    const fm = porFeature.get(commit.feature)!
    fm.commits.push(commit)
    for (const arq of commit.arquivos) {
      fm.arquivos.add(arq)
    }
  }

  // Mapa reverso: arquivo → features
  const arquivoParaFeatures = new Map<string, string[]>()
  for (const [feature, fm] of porFeature) {
    for (const arq of fm.arquivos) {
      if (!arquivoParaFeatures.has(arq)) arquivoParaFeatures.set(arq, [])
      const features = arquivoParaFeatures.get(arq)!
      if (!features.includes(feature)) features.push(feature)
    }
  }

  return {
    commits,
    porFeature,
    arquivoParaFeatures,
    totalCommits: commits.length,
    totalArquivos: new Set(commits.flatMap((c) => c.arquivos)).size,
    totalFeaturesDetectadas: porFeature.size,
  }
}

// ---------------------------------------------------------------------------
// Resolver feature a partir do scope
// ---------------------------------------------------------------------------

function resolverFeature(scope: string, message: string): string | null {
  // Lookup direto
  const direto = SCOPE_TO_FEATURE[scope.toLowerCase()]
  if (direto && direto !== "global") return direto

  // Tentar match no message
  return resolverFeaturePorMsg(message) ?? direto ?? null
}

function resolverFeaturePorMsg(message: string): string | null {
  const matches = [...message.matchAll(FEATURE_IN_MSG_RE)]
  if (matches.length === 0) return null

  // Pegar a feature mais especifica (com NNN-CCC-slug)
  for (const m of matches) {
    const numero = m[1]!
    const slug = m[2]!
    // Procurar no mapa de scopes
    const candidate = `${numero}-000-${slug}`
    // Verificar se o slug match algum scope conhecido
    for (const [, featureId] of Object.entries(SCOPE_TO_FEATURE)) {
      if (featureId.includes(slug)) return featureId
    }
    return candidate
  }

  return null
}
