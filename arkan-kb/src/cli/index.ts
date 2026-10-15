#!/usr/bin/env node

// @@T003 [US1] [US6] [FR-014] CLI entry point com commander
import { Command } from "commander"
import { readFileSync } from "node:fs"
import { resolve, dirname } from "node:path"
import { fileURLToPath } from "node:url"

const __dirname = dirname(fileURLToPath(import.meta.url))

function carregarVersao(): string {
  try {
    const pkg = JSON.parse(
      readFileSync(resolve(__dirname, "../../package.json"), "utf-8"),
    )
    return pkg.version ?? "0.0.0"
  } catch {
    return "0.0.0"
  }
}

const programa = new Command()

programa
  .name("arkan-kb")
  .description(
    "Motor de inteligencia spec+code — transforma especificacoes Arkan e codigo-fonte em grafo de conhecimento unificado",
  )
  .version(carregarVersao())

programa
  .command("analyze")
  .description("Indexar specs e codigo-fonte no grafo de conhecimento")
  .option("--force", "Re-indexar tudo (ignorar cache incremental)")
  .option("--embeddings", "Gerar embeddings semanticos (opcional)")
  .option("--verbose", "Log detalhado de arquivos processados")
  .action(async (opcoes) => {
    const { executarAnalise } = await import("../pipeline/index.js")
    await executarAnalise(opcoes)
  })

programa
  .command("mcp")
  .description("Iniciar MCP Server (stdio) para integracao com Claude Code")
  .action(async () => {
    const { iniciarServidorMcp } = await import("../mcp/server.js")
    await iniciarServidorMcp()
  })

programa
  .command("status")
  .description("Exibir saude e estatisticas do indice")
  .action(async () => {
    const { exibirStatus } = await import("../pipeline/index.js")
    await exibirStatus()
  })

programa
  .command("query <texto>")
  .description("Buscar no grafo de conhecimento")
  .option("--limit <n>", "Numero maximo de resultados", "10")
  .option("--include-inferred", "Incluir arestas inferidas (confianca < 0.5)")
  .action(async (texto, opcoes) => {
    const { executarQuery } = await import("../analysis/search.js")
    await executarQuery(texto, opcoes)
  })

programa
  .command("export-graph")
  .description("Exportar grafo para JSON (consumido pelo viewer HTML)")
  .option("--output <path>", "Caminho do arquivo de saida")
  .action(async (opcoes) => {
    const { exportarGrafo } = await import("./export-graph.js")
    await exportarGrafo(opcoes)
  })

programa
  .command("suggest-annotations")
  .description("Sugerir anotacoes @@TXXX para funcoes/classes sem anotacao")
  .option("--min <n>", "Confianca minima (0-1)", "0.5")
  .option("--limit <n>", "Numero maximo de propostas", "20")
  .option("--interactive", "Modo interativo: revisar uma a uma")
  .option("--apply-all", "Aplicar automaticamente todas acima do threshold")
  .action(async (opcoes) => {
    const { resolve, join } = await import("node:path")
    const { existsSync } = await import("node:fs")
    const { KBStorage } = await import("../graph/storage.js")
    const { gerarPropostas, aplicarAnotacao, aplicarLote } = await import(
      "../analysis/annotator.js"
    )

    const dbPath = join(resolve("."), ".arkan-kb", "index.db")
    if (!existsSync(dbPath)) {
      console.error("Indice nao encontrado. Execute: arkan-kb analyze")
      process.exit(1)
    }

    const storage = await KBStorage.criar(dbPath)
    const resultado = gerarPropostas(storage)
    storage.fechar()

    const minConfianca = parseFloat(opcoes.min ?? "0.5")
    const limite = parseInt(opcoes.limit ?? "20", 10)
    const filtradas = resultado.propostas
      .filter((p) => p.confianca >= minConfianca)
      .slice(0, limite)

    if (filtradas.length === 0) {
      console.log("Nenhuma proposta de anotacao encontrada.")
      return
    }

    // --apply-all: aplicar lote automaticamente
    if (opcoes.applyAll) {
      console.log(`Aplicando ${filtradas.length} anotacoes (confianca >= ${(minConfianca * 100).toFixed(0)}%)...`)
      const lote = aplicarLote(filtradas)
      console.log()
      console.log(`Resumo: ${lote.aplicadas} aplicadas, ${lote.ignoradas} ignoradas`)
      return
    }

    // --interactive: revisar uma a uma
    if (opcoes.interactive) {
      const { createInterface } = await import("node:readline")
      const rl = createInterface({ input: process.stdin, output: process.stdout })
      const perguntar = (q: string): Promise<string> =>
        new Promise((res) => rl.question(q, res))

      let aplicadas = 0
      let ignoradas = 0

      console.log(
        `${filtradas.length} propostas (confianca >= ${(minConfianca * 100).toFixed(0)}%)`,
      )
      console.log()

      for (let i = 0; i < filtradas.length; i++) {
        const p = filtradas[i]!
        console.log(`[${i + 1}/${filtradas.length}] // ${p.anotacaoSugerida}`)
        console.log(`  File: ${p.filePath}:${p.linha}`)
        console.log(`  Confianca: ${(p.confianca * 100).toFixed(0)}%`)
        for (const ev of p.evidencias) {
          console.log(`  Evidencia: ${ev}`)
        }

        const resp = await perguntar("  (s)im / (n)ao / (e)ditar / (q)uit: ")
        const r = resp.trim().toLowerCase()

        if (r === "s" || r === "sim") {
          aplicarAnotacao(p.filePath, p.linha, p.anotacaoSugerida)
          aplicadas++
          console.log("  ✓ Aplicada\n")
        } else if (r === "e" || r === "editar") {
          const nova = await perguntar("  Nova anotacao: ")
          if (nova.trim()) {
            aplicarAnotacao(p.filePath, p.linha, nova.trim())
            aplicadas++
            console.log("  ✓ Aplicada (editada)\n")
          } else {
            ignoradas++
            console.log("  — Ignorada (vazio)\n")
          }
        } else if (r === "q" || r === "quit") {
          ignoradas += filtradas.length - i - 1
          console.log()
          break
        } else {
          ignoradas++
          console.log("  — Ignorada\n")
        }
      }

      rl.close()
      console.log(`Resumo: ${aplicadas} aplicadas, ${ignoradas} ignoradas de ${filtradas.length}`)
      return
    }

    // Default: apenas listar
    console.log(
      `Propostas de anotacao (${filtradas.length}/${resultado.totalSimbolosSemAnotacao} simbolos sem anotacao):`,
    )
    console.log()

    for (const p of filtradas) {
      console.log(`  // ${p.anotacaoSugerida}`)
      console.log(`    File: ${p.filePath}:${p.linha}`)
      console.log(`    Confianca: ${(p.confianca * 100).toFixed(0)}%`)
      for (const ev of p.evidencias) {
        console.log(`    Evidencia: ${ev}`)
      }
      console.log()
    }
  })

programa
  .command("audit-coverage")
  .description("Auditoria de cobertura spec↔code por feature — mostra gaps")
  .option("--feature <nome>", "Filtrar por feature (match parcial)")
  .option("--orphans", "Listar arquivos orfaos (funcoes sem link spec)")
  .option("--tasks", "Listar tasks sem File:")
  .option("--json", "Output em JSON")
  .action(async (opcoes) => {
    const { resolve, join } = await import("node:path")
    const { existsSync } = await import("node:fs")
    const { KBStorage } = await import("../graph/storage.js")
    const { auditarCobertura } = await import("../analysis/audit-coverage.js")

    const dbPath = join(resolve("."), ".arkan-kb", "index.db")
    if (!existsSync(dbPath)) {
      console.error("Indice nao encontrado. Execute: arkan-kb analyze")
      process.exit(1)
    }

    const storage = await KBStorage.criar(dbPath)
    const resultado = auditarCobertura(storage, opcoes.feature)
    storage.fechar()

    if (opcoes.json) {
      console.log(JSON.stringify(resultado, null, 2))
      return
    }

    // Resumo global
    const g = resultado.resumoGlobal
    console.log("ARKAN-KB — Auditoria de Cobertura spec↔code")
    console.log("=".repeat(60))
    console.log(`  Features:      ${g.totalFeatures}`)
    console.log(`  Tasks:         ${g.totalTasks} (${g.tasksComFile} com File:, ${g.tasksSemFile} sem)`)
    console.log(`  Funcoes:       ${g.totalFuncoes}`)
    console.log(`    Anotadas:    ${g.funcoesAnotadas} (${g.percentualCobertura}%)`)
    console.log(`    Heuristica:  ${g.funcoesComHeuristica}`)
    console.log(`    Sem link:    ${g.funcoesSemLink}`)
    console.log()

    // Por feature (ordenar por pior cobertura)
    const features = [...resultado.features].sort(
      (a, b) => a.percentualCobertura - b.percentualCobertura,
    )

    console.log("POR FEATURE (pior cobertura primeiro):")
    console.log("-".repeat(60))

    for (const f of features) {
      if (f.totalTasks === 0 && f.totalFuncoesCodigo === 0) continue

      const barra = gerarBarra(f.percentualCobertura)
      console.log(
        `  ${f.feature.padEnd(35)} ${barra} ${f.percentualCobertura}%`,
      )
      console.log(
        `    Tasks: ${f.totalTasks} (${f.tasksComFile} File:, ${f.tasksSemFile} sem) | Code: ${f.totalFuncoesCodigo} (${f.funcoesAnotadas} @@, ${f.funcoesComHeuristica} heur, ${f.funcoesSemLink} orfao)`,
      )

      // --tasks: listar tasks sem File:
      if (opcoes.tasks) {
        const semFile = f.tasksDetalhes.filter((t) => !t.temFile)
        if (semFile.length > 0) {
          console.log(`    Tasks sem File:`)
          for (const t of semFile.slice(0, 10)) {
            console.log(`      ${t.taskId} ${t.taskNome.slice(0, 60)}`)
          }
          if (semFile.length > 10) {
            console.log(`      ... +${semFile.length - 10} tasks`)
          }
        }
      }

      // --orphans: listar arquivos orfaos
      if (opcoes.orphans && f.arquivosOrfaos.length > 0) {
        console.log(`    Arquivos orfaos (${f.arquivosOrfaos.length}):`)
        for (const a of f.arquivosOrfaos.slice(0, 5)) {
          console.log(
            `      ${a.filePath} (${a.totalFuncoes} funcoes sem link)`,
          )
        }
        if (f.arquivosOrfaos.length > 5) {
          console.log(`      ... +${f.arquivosOrfaos.length - 5} arquivos`)
        }
      }

      console.log()
    }
  })

programa
  .command("apply-annotation")
  .description("Aplicar uma anotacao @@TXXX a um arquivo")
  .requiredOption("--file <path>", "Caminho do arquivo")
  .requiredOption("--line <n>", "Numero da linha")
  .requiredOption("--annotation <text>", "Texto da anotacao (ex: @@T005 [US1])")
  .action(async (opcoes) => {
    const { aplicarAnotacao } = await import("../analysis/annotator.js")
    const linha = parseInt(opcoes.line, 10)
    aplicarAnotacao(opcoes.file, linha, opcoes.annotation)
    console.log(`Anotacao aplicada em ${opcoes.file}:${linha}`)
  })

function gerarBarra(percentual: number): string {
  const largura = 20
  const preenchido = Math.round((percentual / 100) * largura)
  const vazio = largura - preenchido
  return `[${"█".repeat(preenchido)}${"░".repeat(vazio)}]`
}

programa.parse()
