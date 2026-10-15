// @@T012 [US1] [FR-002] Resolucao de imports TS/JS — converte modulos em file paths

import { resolve, dirname, join } from "node:path"
import { existsSync } from "node:fs"

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

export interface ImportResolution {
  /** Modulo original (ex: "../graph/types.js") */
  modulo: string
  /** Caminho resolvido relativo ao root (ex: "arkan-kb/src/graph/types.ts") */
  resolvedPath: string | null
  /** Se o modulo e externo (node_modules) */
  externo: boolean
}

// ---------------------------------------------------------------------------
// Resolver
// ---------------------------------------------------------------------------

const TS_EXTENSIONS = [".ts", ".tsx", ".js", ".jsx", ".mjs"]

/** Raiz do app/pacote do importador (ex: "apps/<app>", "packages/<pkg>") para resolver `@/`. */
function obterRaizModulo(importadorPath: string): string | null {
  const segs = importadorPath.replace(/\\/g, "/").split("/")
  if ((segs[0] === "apps" || segs[0] === "packages") && segs[1]) {
    return `${segs[0]}/${segs[1]}`
  }
  return null
}

/**
 * Candidatos de basePath (absolutos) para um modulo. Suporta imports relativos
 * (./, ../) e os aliases do monorepo `@workspace/<pkg>` e `@/`. Cada candidato e
 * validado por existsSync no chamador — alias errado vira null, nunca aresta falsa.
 */
function candidatosBasePath(
  modulo: string,
  importadorPath: string,
  rootDir: string,
): string[] {
  if (modulo.startsWith(".") || modulo.startsWith("/")) {
    return [resolve(dirname(resolve(rootDir, importadorPath)), modulo)]
  }
  if (modulo.startsWith("@workspace/")) {
    const resto = modulo.slice("@workspace/".length)
    const [pkg, ...rest] = resto.split("/")
    const sub = rest.join("/")
    return [
      resolve(rootDir, "packages", pkg!, "src", sub),
      resolve(rootDir, "packages", pkg!, sub),
    ]
  }
  if (modulo.startsWith("@/")) {
    const raiz = obterRaizModulo(importadorPath)
    if (!raiz) return []
    const sub = modulo.slice(2)
    return [
      resolve(rootDir, raiz, sub),
      resolve(rootDir, raiz, "src", sub),
    ]
  }
  return []
}

export function resolverImport(
  modulo: string,
  importadorPath: string,
  rootDir: string,
): ImportResolution {
  const candidatos = candidatosBasePath(modulo, importadorPath, rootDir)
  // Modulo externo (lib em node_modules) — nenhum candidato local
  if (candidatos.length === 0) {
    return { modulo, resolvedPath: null, externo: true }
  }

  const paraRelativo = (caminho: string): string =>
    caminho.replace(rootDir, "").replace(/\\/g, "/").replace(/^\//, "")

  for (let basePath of candidatos) {
    // Remover extensao .js (TS usa .js nos imports mas arquivo real e .ts)
    if (basePath.endsWith(".js")) basePath = basePath.slice(0, -3)

    // Arquivo direto
    for (const ext of TS_EXTENSIONS) {
      if (existsSync(basePath + ext)) {
        return { modulo, resolvedPath: paraRelativo(basePath + ext), externo: false }
      }
    }
    // index do diretorio (barrel)
    for (const ext of TS_EXTENSIONS) {
      const idx = join(basePath, `index${ext}`)
      if (existsSync(idx)) {
        return { modulo, resolvedPath: paraRelativo(idx), externo: false }
      }
    }
  }

  return { modulo, resolvedPath: null, externo: false }
}

// ---------------------------------------------------------------------------
// Resolver em batch
// ---------------------------------------------------------------------------

// @@T012 [US1] resolverImportsBatch
export function resolverImportsBatch(
  imports: Array<{ modulo: string; importadorPath: string }>,
  rootDir: string,
): Map<string, ImportResolution> {
  const resultados = new Map<string, ImportResolution>()

  for (const imp of imports) {
    const chave = `${imp.importadorPath}:${imp.modulo}`
    if (!resultados.has(chave)) {
      resultados.set(
        chave,
        resolverImport(imp.modulo, imp.importadorPath, rootDir),
      )
    }
  }

  return resultados
}
