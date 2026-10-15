// @@T019 [US1] [FR-014] Descoberta de arquivos com filtros

import { readdirSync, statSync, readFileSync, existsSync } from "node:fs"
import { join, relative, extname } from "node:path"

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

export interface ArquivoDescoberto {
  caminhoRelativo: string
  caminhoAbsoluto: string
  extensao: string
  tamanho: number
  tipo: "spec" | "code" | "sql" | "outro"
}

export interface OpcoesDiscovery {
  rootDir: string
  maxTamanho?: number // bytes, default 512KB
  verbose?: boolean
}

// ---------------------------------------------------------------------------
// Padroes
// ---------------------------------------------------------------------------

const EXTENSOES_CODE = new Set([".ts", ".tsx", ".js", ".jsx", ".mjs"])
const EXTENSOES_SQL = new Set([".sql"])
const EXTENSOES_SPEC = new Set([".md"])

const DIRS_IGNORADOS = new Set([
  "node_modules",
  ".git",
  ".next",
  "dist",
  "build",
  ".turbo",
  ".arkan",
  ".specify",
  ".trigger",
  ".expo",
  ".cache",
  "coverage",
  "playwright-report",
  "test-results",
  ".arkan-kb",
  "__generated__",
  ".vinxi",
])

const DIRS_SPEC = [
  ".arkan/features",
  ".arkan/projects",
  ".specify/features",
]

const DIRS_CODE = [
  "apps",
  "packages",
  "scripts",
]

// Diretorios de migracao mais comuns. Cada projeto pode declarar o seu (que nao
// precisa estar nesta lista) em `.arkan/memory/stack.md`; o indexador ainda nao
// le esse arquivo aqui — ajuste esta constante ao seu layout se o seu diretorio
// de migrations nao for nenhum destes.
const DIRS_SQL = [
  "migrations",
  "db/migrations",
]

const MAX_TAMANHO_PADRAO = 512 * 1024 // 512KB

// ---------------------------------------------------------------------------
// Discovery
// ---------------------------------------------------------------------------

export function descobrirArquivos(opcoes: OpcoesDiscovery): ArquivoDescoberto[] {
  const { rootDir, maxTamanho = MAX_TAMANHO_PADRAO, verbose } = opcoes
  const resultado: ArquivoDescoberto[] = []

  // Descobrir specs
  for (const dir of DIRS_SPEC) {
    const dirAbsoluto = join(rootDir, dir)
    if (existsSync(dirAbsoluto)) {
      percorrerDiretorio(dirAbsoluto, rootDir, "spec", resultado, maxTamanho, verbose)
    }
  }

  // Descobrir codigo
  for (const dir of DIRS_CODE) {
    const dirAbsoluto = join(rootDir, dir)
    if (existsSync(dirAbsoluto)) {
      percorrerDiretorio(dirAbsoluto, rootDir, "code", resultado, maxTamanho, verbose)
    }
  }

  // Descobrir SQL
  for (const dir of DIRS_SQL) {
    const dirAbsoluto = join(rootDir, dir)
    if (existsSync(dirAbsoluto)) {
      percorrerDiretorio(dirAbsoluto, rootDir, "sql", resultado, maxTamanho, verbose)
    }
  }

  return resultado
}

// @@T019 [US1] percorrerDiretorio
function percorrerDiretorio(
  dir: string,
  rootDir: string,
  tipoEsperado: "spec" | "code" | "sql",
  resultado: ArquivoDescoberto[],
  maxTamanho: number,
  verbose?: boolean,
): void {
  let entries: string[]
  try {
    entries = readdirSync(dir)
  } catch {
    return
  }

  for (const entry of entries) {
    const caminhoAbsoluto = join(dir, entry)

    let stat
    try {
      stat = statSync(caminhoAbsoluto)
    } catch {
      continue
    }

    if (stat.isDirectory()) {
      // Ignora dirs fixos e qualquer pasta de lixo (.trash, .trash-dashboard-usuario, ...)
      if (DIRS_IGNORADOS.has(entry) || entry.startsWith(".trash")) continue
      percorrerDiretorio(caminhoAbsoluto, rootDir, tipoEsperado, resultado, maxTamanho, verbose)
      continue
    }

    if (!stat.isFile()) continue
    if (stat.size > maxTamanho) {
      if (verbose) console.log(`Pulando (> ${maxTamanho}b): ${entry}`)
      continue
    }

    const ext = extname(entry)
    let tipo: ArquivoDescoberto["tipo"] = "outro"

    if (tipoEsperado === "spec" && EXTENSOES_SPEC.has(ext)) {
      // Apenas arquivos que contem US/FR/Task/Decision/INV
      const nomeArquivo = entry.toLowerCase()
      const SPEC_FILES = ["spec.md", "tasks.md", "ideacao.md"]
      if (!SPEC_FILES.includes(nomeArquivo)) continue
      tipo = "spec"
    } else if (tipoEsperado === "code" && EXTENSOES_CODE.has(ext)) {
      tipo = "code"
    } else if (tipoEsperado === "sql" && EXTENSOES_SQL.has(ext)) {
      tipo = "sql"
    } else {
      continue // Ignorar arquivos que nao correspondem ao tipo esperado
    }

    resultado.push({
      caminhoRelativo: relative(rootDir, caminhoAbsoluto).replace(/\\/g, "/"),
      caminhoAbsoluto,
      extensao: ext,
      tamanho: stat.size,
      tipo,
    })
  }
}

// ---------------------------------------------------------------------------
// Detectar feature de um arquivo spec
// ---------------------------------------------------------------------------

// @@T019 [US1] detectarFeature
export function detectarFeature(caminhoRelativo: string): string {
  // Pattern: .arkan/features/{projeto}/{NNN-CCC-slug}/...
  const arkanMatch = caminhoRelativo.match(
    /\.arkan\/features\/[\w-]+\/([\w-]+)\//,
  )
  if (arkanMatch) return arkanMatch[1]!

  // Pattern: .specify/features/{NNN-slug}/...
  const specifyMatch = caminhoRelativo.match(
    /\.specify\/features\/([\w-]+)\//,
  )
  if (specifyMatch) return specifyMatch[1]!

  return "global"
}

/** Extrai nome do projeto do caminho relativo */
// @@T019 [US1] detectarProjeto
export function detectarProjeto(caminhoRelativo: string): string {
  // Pattern: .arkan/features/{projeto}/{NNN-CCC-slug}/...
  const arkanMatch = caminhoRelativo.match(
    /\.arkan\/features\/([\w-]+)\/[\w-]+\//,
  )
  if (arkanMatch) return arkanMatch[1]!

  // .specify/ nao tem projeto no path — usar o padrao
  const specifyMatch = caminhoRelativo.match(
    /\.specify\/features\//,
  )
  if (specifyMatch) return "projeto-padrao"

  // Codigo em apps/{app}/ — extrair app como projeto
  const appMatch = caminhoRelativo.match(/^apps\/([\w-]+)\//)
  if (appMatch) return appMatch[1]!

  // Codigo em packages/{pkg}/
  const pkgMatch = caminhoRelativo.match(/^packages\/([\w-]+)\//)
  if (pkgMatch) return pkgMatch[1]!

  return "global"
}
