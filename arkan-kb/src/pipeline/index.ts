// @@T018 [US1] [FR-014] Orquestrador do pipeline de indexacao

import { readFileSync, existsSync, mkdirSync } from "node:fs"
import { join, resolve } from "node:path"
import { execSync } from "node:child_process"
import { KnowledgeGraph } from "../graph/knowledge-graph.js"
import { KBStorage } from "../graph/storage.js"
import { linkarSpecCode } from "../graph/linker.js"
import {
  parsearArquivoSpec,
} from "../parsers/spec-parser.js"
import {
  parsearCodigo,
  type CodeParseResult,
} from "../parsers/code-parser.js"
import { parsearSql } from "../parsers/sql-parser.js"
import {
  descobrirArquivos,
  detectarFeature,
  type ArquivoDescoberto,
} from "./file-discovery.js"
import type {
  CodeAnnotation,
  IndexMetadata,
  GraphNode,
  GraphEdge,
} from "../graph/types.js"
import { carregarHashes, salvarHashes, filtrarAlterados } from "./incremental.js"
import { resolverImportsBatch } from "../resolution/import-resolver.js"
import { construirImportMap, resolverChamadas } from "../resolution/call-resolver.js"

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

export interface OpcoesAnalise {
  force?: boolean
  embeddings?: boolean
  verbose?: boolean
}

// ---------------------------------------------------------------------------
// Pipeline
// ---------------------------------------------------------------------------

export async function executarAnalise(opcoes: OpcoesAnalise): Promise<void> {
  const rootDir = resolve(".")
  const kbDir = join(rootDir, ".arkan-kb")
  const dbPath = join(kbDir, "index.db")

  console.log("arkan-kb analyze")
  console.log(`Root: ${rootDir}`)

  // Criar diretorio .arkan-kb
  if (!existsSync(kbDir)) {
    mkdirSync(kbDir, { recursive: true })
  }

  // Fase 1: Discovery
  console.log("\n[1/7] Descobrindo arquivos...")
  const todosArquivos = descobrirArquivos({ rootDir, verbose: opcoes.verbose })

  // Incremental: filtrar apenas alterados (a menos que --force)
  let arquivos = todosArquivos
  let hashesNovos: Record<string, string> | undefined
  if (!opcoes.force) {
    const hashesAnteriores = carregarHashes(kbDir)
    const resultado = filtrarAlterados(todosArquivos, hashesAnteriores)
    hashesNovos = resultado.hashesNovos
    if (resultado.alterados.length < todosArquivos.length) {
      console.log(`  Incremental: ${resultado.alterados.length}/${todosArquivos.length} arquivos alterados`)
      arquivos = resultado.alterados
    }
  }

  const specs = arquivos.filter((a) => a.tipo === "spec")
  const codes = arquivos.filter((a) => a.tipo === "code")
  const sqls = arquivos.filter((a) => a.tipo === "sql")
  console.log(
    `  ${specs.length} specs | ${codes.length} code | ${sqls.length} sql`,
  )

  // Fase 2: Parsing
  const kg = new KnowledgeGraph()
  const todasAnotacoes: CodeAnnotation[] = []
  const todasChamadasRpc: import("../parsers/code-parser.js").ChamadaRpc[] = []
  // Arestas de codigo brutas (inclui IMPORTS e CALLS nao resolvidas) para resolucao cross-file
  const todasArestasCodigo: GraphEdge[] = []
  let errosTotal = 0

  console.log("\n[2/6] Parseando specs...")
  for (const arquivo of specs) {
    try {
      const conteudo = readFileSync(arquivo.caminhoAbsoluto, "utf-8")
      const feature = detectarFeature(arquivo.caminhoRelativo)
      const resultado = parsearArquivoSpec(
        conteudo,
        feature,
        arquivo.caminhoRelativo,
      )
      for (const no of resultado.nos) kg.adicionarNo(no)
      errosTotal += resultado.erros.length
      if (opcoes.verbose && resultado.erros.length > 0) {
        for (const erro of resultado.erros) console.log(`  WARN: ${erro}`)
      }
    } catch (e) {
      errosTotal++
      if (opcoes.verbose) {
        console.log(`  ERRO: ${arquivo.caminhoRelativo}: ${e}`)
      }
    }
  }

  console.log("\n[3/6] Parseando codigo...")
  let codeCount = 0
  for (const arquivo of codes) {
    try {
      const conteudo = readFileSync(arquivo.caminhoAbsoluto, "utf-8")
      const resultado = parsearCodigo(conteudo, arquivo.caminhoRelativo)
      for (const no of resultado.nos) kg.adicionarNo(no)
      for (const aresta of resultado.arestas) kg.adicionarAresta(aresta)
      todasArestasCodigo.push(...resultado.arestas)
      todasAnotacoes.push(...resultado.anotacoes)
      todasChamadasRpc.push(...resultado.chamadasRpc)
      codeCount++
    } catch (e) {
      errosTotal++
      if (opcoes.verbose) {
        console.log(`  ERRO: ${arquivo.caminhoRelativo}: ${e}`)
      }
    }
  }
  console.log(`  ${codeCount} arquivos processados`)

  console.log("\n[4/6] Parseando SQL...")
  for (const arquivo of sqls) {
    try {
      const conteudo = readFileSync(arquivo.caminhoAbsoluto, "utf-8")
      const resultado = parsearSql(conteudo, arquivo.caminhoRelativo)
      for (const no of resultado.nos) kg.adicionarNo(no)
      for (const aresta of resultado.arestas) kg.adicionarAresta(aresta)
    } catch (e) {
      errosTotal++
      if (opcoes.verbose) {
        console.log(`  ERRO: ${arquivo.caminhoRelativo}: ${e}`)
      }
    }
  }

  // Resolver FKs cross-migration: arestas com target sintetico Table:external:*
  // precisam ser resolvidas para o no real da tabela que pode estar em outro arquivo SQL
  const arestasFK: import("../graph/types.js").GraphEdge[] = []
  for (const arquivo of sqls) {
    try {
      const conteudo = readFileSync(arquivo.caminhoAbsoluto, "utf-8")
      const resultado = parsearSql(conteudo, arquivo.caminhoRelativo)
      for (const aresta of resultado.arestas) {
        if (aresta.tipo === "REFERENCES_TABLE" && aresta.targetId.startsWith("Table:external:")) {
          const nomeTabela = aresta.targetId.replace("Table:external:", "")
          const noReal = kg.buscarNoPorLabelENome("Table", nomeTabela)
          if (noReal) {
            arestasFK.push({ ...aresta, targetId: noReal.id })
          } else {
            arestasFK.push(aresta) // manter sintetico para auditoria
          }
        }
      }
    } catch { /* ja contabilizado acima */ }
  }
  for (const aresta of arestasFK) {
    if (!aresta.targetId.startsWith("Table:external:")) {
      kg.adicionarAresta(aresta)
    }
  }

  // Resolver chamadas `.rpc("nome")` -> no RPC mais recente (por timestamp da migration).
  // Migrations versionam a mesma funcao varias vezes; o caller real aponta para a vigente.
  const rpcMaisRecentePorNome = new Map<string, { id: string; ts: string }>()
  for (const no of kg.buscarNosPorLabel("RPC")) {
    const ts = (no.filePath?.split(/[\\/]/).pop() ?? "").match(/^\d+/)?.[0] ?? "0"
    const atual = rpcMaisRecentePorNome.get(no.nome)
    if (!atual || ts > atual.ts) {
      rpcMaisRecentePorNome.set(no.nome, { id: no.id, ts })
    }
  }
  let chamadasRpcResolvidas = 0
  for (const chamada of todasChamadasRpc) {
    const alvo = rpcMaisRecentePorNome.get(chamada.rpcNome)
    if (!alvo) continue // RPC desconhecida (ou nome dinamico) — ignorar
    kg.adicionarAresta({
      sourceId: chamada.callerNodeId,
      targetId: alvo.id,
      tipo: "CALLS_RPC",
      confianca: 0.9, // nome literal -> alta confianca
      propriedades: { origem: "rpc-literal", linha: chamada.linha },
    })
    chamadasRpcResolvidas++
  }
  console.log(`  RPC calls resolvidas: ${chamadasRpcResolvidas}/${todasChamadasRpc.length}`)

  // Resolver chamadas cross-file IMPORT-SCOPED (B1): callers que chamam um simbolo importado.
  // Reusa import-resolver + call-resolver. O fallback global "ultimo-vence" fica DESLIGADO
  // (symbolTable vazia) — so a resolucao precisa, via import real, sobrevive (conf 0.9).
  const importsParaResolver = todasArestasCodigo
    .filter((a) => a.tipo === "IMPORTS" && a.targetId.startsWith("__IMPORT__:"))
    .map((a) => ({
      modulo: a.targetId.replace("__IMPORT__:", ""),
      importadorPath: a.sourceId.replace("File:", "").replace(/:.*/, ""),
    }))
  const resolucoesImport = resolverImportsBatch(importsParaResolver, rootDir)
  const resolvedImports = new Map<string, string | null>()
  for (const [chave, res] of resolucoesImport) resolvedImports.set(chave, res.resolvedPath)
  const importMap = construirImportMap(todasArestasCodigo, resolvedImports)
  const arestasResolvidas = resolverChamadas(
    todasArestasCodigo,
    kg.exportarNos(),
    new Map(), // symbolTable vazia -> desliga fallback global
    importMap,
  )
  let callsCrossFile = 0
  for (const a of arestasResolvidas) {
    if (a.tipo === "CALLS" && a.confianca === 0.9 && !a.targetId.startsWith("__")) {
      kg.adicionarAresta(a)
      callsCrossFile++
    }
  }
  console.log(`  CALLS cross-file (import-scoped) resolvidas: ${callsCrossFile}`)

  // Fase 3: Git log parsing
  console.log("\n[5/7] Parseando git log...")
  let gitLog: import("../parsers/git-log-parser.js").GitLogResult | undefined
  try {
    const { parsearGitLog } = await import("../parsers/git-log-parser.js")
    gitLog = parsearGitLog(rootDir)
    console.log(
      `  ${gitLog.totalCommits} commits | ${gitLog.totalArquivos} arquivos | ${gitLog.totalFeaturesDetectadas} features`,
    )
  } catch (e) {
    if (opcoes.verbose) console.log(`  Git log indisponivel: ${e}`)
  }

  // Fase 4: Linking spec↔code
  console.log("\n[6/7] Linkando spec↔code...")
  const linkResult = linkarSpecCode(kg, todasAnotacoes, gitLog)
  for (const aresta of linkResult.arestas) kg.adicionarAresta(aresta)
  console.log(
    `  Anotacoes: ${linkResult.estatisticas.porAnotacao} | Task-File: ${linkResult.estatisticas.porTaskFile} | Git-Log: ${linkResult.estatisticas.porGitLog} | Heuristica: ${linkResult.estatisticas.porHeuristica}`,
  )

  // Fase 4: Persistir
  if (kg.totalNos === 0) {
    console.log("\nNenhuma alteracao detectada — indice inalterado.")
    if (hashesNovos) {
      salvarHashes(kbDir, hashesNovos)
    }
    return
  }

  console.log("\n[6/7] Persistindo no SQLite...")
  const storage = await KBStorage.criar(dbPath)

  if (opcoes.force) {
    storage.limpar()
  }

  storage.salvarNos(kg.exportarNos())
  storage.salvarArestas(kg.exportarArestas())

  // Metadata
  let ultimoCommit = ""
  try {
    ultimoCommit = execSync("git rev-parse HEAD", { encoding: "utf-8" }).trim()
  } catch {
    // sem git
  }

  const stats = kg.estatisticasPorLabel()
  const meta: IndexMetadata = {
    versao: "0.1.0",
    ultimoCommit,
    indexadoEm: new Date().toISOString(),
    estatisticas: {
      arquivos: arquivos.length,
      nosSpec: (stats["UserStory"] ?? 0) +
        (stats["FunctionalRequirement"] ?? 0) +
        (stats["NonFunctionalRequirement"] ?? 0) +
        (stats["Invariant"] ?? 0) +
        (stats["Task"] ?? 0) +
        (stats["Decision"] ?? 0) +
        (stats["DataEntity"] ?? 0),
      nosCodigo: (stats["Function"] ?? 0) +
        (stats["Class"] ?? 0) +
        (stats["Method"] ?? 0) +
        (stats["Interface"] ?? 0) +
        (stats["File"] ?? 0),
      nosSql: (stats["Table"] ?? 0) +
        (stats["RPC"] ?? 0) +
        (stats["Policy"] ?? 0),
      arestas: kg.totalArestas,
      features: new Set(
        kg
          .exportarNos()
          .map((n) => n.feature)
          .filter(Boolean),
      ).size,
    },
  }

  storage.salvarMetadata(meta)

  // Totais reais do banco (inclui nos anteriores + incrementais)
  const totalNosDb = storage.contarNos()
  const totalArestasDb = storage.contarArestas()

  storage.fechar()

  // Salvar hashes para incremental
  if (hashesNovos) {
    salvarHashes(kbDir, hashesNovos)
  }

  // Resumo
  const incremental = !opcoes.force
  console.log("\n" + "=".repeat(50))
  console.log(`ARKAN-KB — Indexacao completa${incremental ? " (incremental)" : ""}`)
  console.log("=".repeat(50))
  if (incremental) {
    console.log(`  Incremento:`)
    console.log(`    Nos:      +${kg.totalNos}`)
    console.log(`      Spec:   +${meta.estatisticas.nosSpec}`)
    console.log(`      Code:   +${meta.estatisticas.nosCodigo}`)
    console.log(`      SQL:    +${meta.estatisticas.nosSql}`)
    console.log(`    Arestas:  +${kg.totalArestas}`)
    console.log("")
  }
  console.log(`  Total no banco:`)
  console.log(`    Nos:      ${totalNosDb}`)
  console.log(`    Arestas:  ${totalArestasDb}`)
  console.log(`  Features: ${meta.estatisticas.features}`)
  console.log(`  Erros:    ${errosTotal}`)
  console.log(`  DB:       ${dbPath}`)
}

// ---------------------------------------------------------------------------
// Status
// ---------------------------------------------------------------------------

// @@T018 [US1] exibirStatus
export async function exibirStatus(): Promise<void> {
  const rootDir = resolve(".")
  const dbPath = join(rootDir, ".arkan-kb", "index.db")

  if (!existsSync(dbPath)) {
    console.log("Indice nao encontrado. Execute: arkan-kb analyze")
    return
  }

  const storage = await KBStorage.criar(dbPath)
  const meta = storage.obterMetadata()

  if (!meta) {
    console.log("Metadata nao encontrada. Re-execute: arkan-kb analyze")
    storage.fechar()
    return
  }

  const nosPorLabel = storage.contarNosPorLabel()

  console.log("ARKAN-KB — Status do Indice")
  console.log("=".repeat(50))
  console.log(`  Versao:      ${meta.versao}`)
  console.log(`  Ultimo commit: ${meta.ultimoCommit.slice(0, 8)}`)
  console.log(`  Indexado em: ${meta.indexadoEm}`)
  console.log(`  Nos total:   ${storage.contarNos()}`)
  console.log(`  Arestas:     ${storage.contarArestas()}`)
  console.log(`  Features:    ${meta.estatisticas.features}`)
  console.log()
  console.log("  Nos por tipo:")
  for (const [label, count] of Object.entries(nosPorLabel).sort(
    (a, b) => b[1] - a[1],
  )) {
    console.log(`    ${label.padEnd(25)} ${count}`)
  }

  storage.fechar()
}
