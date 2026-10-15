// @@T016 [US4] [FR-004] Linking spec↔code — arestas cross-domain

import type { GraphEdge, CodeAnnotation } from "./types.js"
import { KnowledgeGraph } from "./knowledge-graph.js"
import type { GitLogResult } from "../parsers/git-log-parser.js"

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

export interface LinkResult {
  arestas: GraphEdge[]
  estatisticas: {
    porAnotacao: number
    porTaskFile: number
    porGitLog: number
    porHeuristica: number
    total: number
  }
}

// ---------------------------------------------------------------------------
// Estrategia 1: Anotacoes explicitas @@TXXX (confianca 1.0)
// ---------------------------------------------------------------------------

function linkarPorAnotacao(
  anotacoes: CodeAnnotation[],
  kg: KnowledgeGraph,
): GraphEdge[] {
  const arestas: GraphEdge[] = []

  for (const anot of anotacoes) {
    // Task -> File/Function (TASK_MODIFIES)
    const taskNos = kg.buscarNosPorLabel("Task")
    const taskNo = taskNos.find((t) => t.nome.startsWith(anot.taskId))

    // Encontrar a funcao/classe logo abaixo da anotacao
    const codeNos = kg.exportarNos().filter(
      (n) =>
        n.filePath === anot.filePath &&
        (n.label === "Function" || n.label === "Class" || n.label === "Method"),
    )

    // Encontrar o no de codigo mais proximo (proxima linha apos anotacao)
    const codeNoMaisProximo = codeNos
      .filter((n) => {
        const linhaInicio = (n as any).linhaInicio as number | undefined
        return linhaInicio !== undefined && linhaInicio >= anot.linha
      })
      .sort(
        (a, b) =>
          ((a as any).linhaInicio as number) -
          ((b as any).linhaInicio as number),
      )[0]

    if (codeNoMaisProximo && taskNo) {
      arestas.push({
        sourceId: codeNoMaisProximo.id,
        targetId: taskNo.id,
        tipo: "TASK_MODIFIES",
        confianca: 1.0,
        propriedades: { origem: "anotacao" },
      })
    }

    // FR -> Code (IMPLEMENTS_FR)
    if (anot.frId) {
      const frNos = kg.buscarNosPorLabel("FunctionalRequirement")
      const frNo = frNos.find((f) => f.nome === anot.frId)
      if (frNo && codeNoMaisProximo) {
        arestas.push({
          sourceId: codeNoMaisProximo.id,
          targetId: frNo.id,
          tipo: "IMPLEMENTS_FR",
          confianca: 1.0,
          propriedades: { origem: "anotacao" },
        })
      }
    }

    // US -> Code (COVERS_US)
    if (anot.userStoryId) {
      const usNos = kg.buscarNosPorLabel("UserStory")
      const usNo = usNos.find((u) =>
        u.id.includes(anot.userStoryId),
      )
      if (usNo && codeNoMaisProximo) {
        arestas.push({
          sourceId: codeNoMaisProximo.id,
          targetId: usNo.id,
          tipo: "COVERS_US",
          confianca: 1.0,
          propriedades: { origem: "anotacao" },
        })
      }
    }

    // INV -> Code (VALIDATES_INV)
    if (anot.invId) {
      const invNos = kg.buscarNosPorLabel("Invariant")
      const invNo = invNos.find((i) => i.id.includes(anot.invId!))
      if (invNo && codeNoMaisProximo) {
        arestas.push({
          sourceId: codeNoMaisProximo.id,
          targetId: invNo.id,
          tipo: "VALIDATES_INV",
          confianca: 1.0,
          propriedades: { origem: "anotacao" },
        })
      }
    }
  }

  return arestas
}

// ---------------------------------------------------------------------------
// Estrategia 2: tasks.md File: field (confianca 0.9)
// ---------------------------------------------------------------------------

// @@T016 [US4] linkarPorTaskFile
function linkarPorTaskFile(kg: KnowledgeGraph): GraphEdge[] {
  const arestas: GraphEdge[] = []
  const tasks = kg.buscarNosPorLabel("Task")

  for (const task of tasks) {
    const arquivoAlvo = (task as any).arquivoAlvo as string | undefined
    if (!arquivoAlvo) continue

    // Ignorar paths genericos (< 2 segmentos — ex: "page.tsx", "index.ts")
    const segmentos = arquivoAlvo.replace(/\\/g, "/").split("/").filter(Boolean)
    if (segmentos.length < 2) continue

    // Confianca proporcional a especificidade do path
    const confiancaBase = segmentos.length >= 4 ? 0.9 : segmentos.length >= 3 ? 0.8 : 0.7

    // Encontrar nos de codigo no arquivo alvo
    const codeNos = kg.exportarNos().filter(
      (n) =>
        n.filePath?.replace(/\\/g, "/").endsWith(arquivoAlvo.replace(/\\/g, "/")) &&
        n.label === "File",
    )

    for (const codeNo of codeNos) {
      arestas.push({
        sourceId: task.id,
        targetId: codeNo.id,
        tipo: "TASK_MODIFIES",
        confianca: confiancaBase,
        propriedades: { origem: "task-file" },
      })
    }

    // Linkar US da task -> File
    const userStoryId = (task as any).userStoryId as string | undefined
    if (userStoryId) {
      const usNo = kg.obterNo(userStoryId)
      if (usNo) {
        for (const codeNo of codeNos) {
          arestas.push({
            sourceId: codeNo.id,
            targetId: usNo.id,
            tipo: "COVERS_US",
            confianca: Math.max(0.6, confiancaBase - 0.1),
            propriedades: { origem: "task-file-us" },
          })
        }
      }
    }
  }

  return arestas
}

// ---------------------------------------------------------------------------
// Estrategia 3: Heuristica de nome (confianca 0.7)
// ---------------------------------------------------------------------------

// Stopwords: termos genericos que aparecem em quase todo FR e nao indicam relacao
const STOPWORDS_FR = new Set([
  "sistema", "deve", "poder", "permitir", "usuario", "forma",
  "atraves", "quando", "apenas", "todos", "acessar", "criar",
  "listar", "exibir", "retornar", "receber", "enviar", "salvar",
  "funcao", "metodo", "classe", "arquivo", "modulo", "componente",
  "dados", "campo", "valor", "tipo", "lista", "informacao",
  "resultado", "processo", "estado", "status", "resposta",
  "string", "number", "object", "array", "boolean",
  "implementar", "expor", "ferramenta", "aceitar", "texto",
  "suportar", "fornecer", "incluir", "configurar", "definir",
])

// @@T016 [US4] linkarPorHeuristica
function linkarPorHeuristica(kg: KnowledgeGraph): GraphEdge[] {
  const arestas: GraphEdge[] = []
  const frs = kg.buscarNosPorLabel("FunctionalRequirement")
  const funcoes = kg.buscarNosPorLabel("Function")
  const classes = kg.buscarNosPorLabel("Class")
  const metodos = kg.buscarNosPorLabel("Method")
  const codeNos = [...funcoes, ...classes, ...metodos]

  // Pre-indexar: FRs com muitos matches provaveis sao penalizados
  const frPalavras = new Map<string, string[]>()
  for (const fr of frs) {
    const descricao = ((fr as any).descricao as string ?? "").toLowerCase()
    const palavrasChave = descricao
      .split(/\s+/)
      .map((p) => p.replace(/[^a-záàâãéèêíïóôõöúç]/g, ""))
      .filter((p) => p.length > 5)
      .filter((p) => !STOPWORDS_FR.has(p))
    // Deduplicar
    frPalavras.set(fr.id, [...new Set(palavrasChave)])
  }

  // Limitar: FRs com <= 2 palavras-chave uteis sao muito genericos — pular
  const frsValidos = frs.filter((fr) => (frPalavras.get(fr.id)?.length ?? 0) > 2)

  // Contar quantos code nodes cada FR matcha (para penalizar FRs catch-all)
  const frMatchCount = new Map<string, number>()

  for (const fr of frsValidos) {
    const palavrasChave = frPalavras.get(fr.id) ?? []
    let matchCount = 0

    for (const codeNo of codeNos) {
      // Tokenizar camelCase/snake_case do nome da funcao
      const tokens = tokenizarNome(codeNo.nome)
      const matches = palavrasChave.filter((p) =>
        tokens.some((t) => t.includes(p) || p.includes(t)),
      )

      if (matches.length >= 2) {
        matchCount++
      }
    }

    frMatchCount.set(fr.id, matchCount)
  }

  // Gerar arestas com confianca ajustada
  for (const fr of frsValidos) {
    const palavrasChave = frPalavras.get(fr.id) ?? []
    const totalMatches = frMatchCount.get(fr.id) ?? 0

    // FR que matcha > 50 funcoes e catch-all — reduzir confianca drasticamente
    if (totalMatches > 50) continue // Ignorar FR catch-all completamente

    for (const codeNo of codeNos) {
      const tokens = tokenizarNome(codeNo.nome)
      const matches = palavrasChave.filter((p) =>
        tokens.some((t) => t.includes(p) || p.includes(t)),
      )

      if (matches.length < 2) continue

      // Heuristica de NOME e palpite, nao fato: teto 0.49 mantem essas arestas
      // ABAIXO do corte de impact/context (>=0.5), entao nao poluem o blast radius.
      // Continuam visiveis para audit_coverage e buscas com threshold menor.
      // - Mais matches = mais confianca (bonus +0.05 por match extra)
      // - FR com muitos matches globais = penalidade
      const bonusMatches = Math.min(0.15, (matches.length - 2) * 0.05)
      const penalidade = totalMatches > 20 ? 0.2 : totalMatches > 10 ? 0.1 : 0
      const confianca = Math.max(0.3, Math.min(0.49, 0.45 + bonusMatches - penalidade))

      arestas.push({
        sourceId: codeNo.id,
        targetId: fr.id,
        tipo: "IMPLEMENTS_FR",
        confianca,
        propriedades: {
          origem: "heuristica",
          matchedTerms: matches,
        },
      })
    }
  }

  return arestas
}

/** Tokeniza camelCase/PascalCase/snake_case em palavras lowercase */
// @@T016 [US4] tokenizarNome
function tokenizarNome(nome: string): string[] {
  return nome
    // camelCase → camel_Case
    .replace(/([a-z])([A-Z])/g, "$1_$2")
    // PascalCase → Pascal_Case
    .replace(/([A-Z])([A-Z][a-z])/g, "$1_$2")
    .toLowerCase()
    .split(/[_\-.\s]+/)
    .filter((t) => t.length > 2)
}

// ---------------------------------------------------------------------------
// Estrategia 4: Git log — commits linkam arquivos a features (confianca 0.85)
// ---------------------------------------------------------------------------

// @@T016 [US4] linkarPorGitLog
function linkarPorGitLog(
  kg: KnowledgeGraph,
  gitLog: GitLogResult | undefined,
): GraphEdge[] {
  if (!gitLog) return []

  const arestas: GraphEdge[] = []
  const tasks = kg.buscarNosPorLabel("Task")
  const codeNos = [
    ...kg.buscarNosPorLabel("Function"),
    ...kg.buscarNosPorLabel("Class"),
    ...kg.buscarNosPorLabel("Method"),
    ...kg.buscarNosPorLabel("File"),
  ]

  // Index: filePath → code nodes
  const fileToCode = new Map<string, typeof codeNos>()
  for (const no of codeNos) {
    if (!no.filePath) continue
    const pathNorm = no.filePath.replace(/\\/g, "/")
    if (!fileToCode.has(pathNorm)) fileToCode.set(pathNorm, [])
    fileToCode.get(pathNorm)!.push(no)
  }

  // Index: feature → tasks
  const featureToTasks = new Map<string, typeof tasks>()
  for (const task of tasks) {
    if (!task.feature) continue
    if (!featureToTasks.has(task.feature)) featureToTasks.set(task.feature, [])
    featureToTasks.get(task.feature)!.push(task)
  }

  // Para cada feature no git log, linkar arquivos do commit às tasks da feature
  for (const [feature, fm] of gitLog.porFeature) {
    const featureTasks = featureToTasks.get(feature)
    if (!featureTasks || featureTasks.length === 0) continue

    for (const arquivo of fm.arquivos) {
      const nos = fileToCode.get(arquivo)
      if (!nos) continue

      // Encontrar task mais especifica:
      // 1. Task com File: que match este arquivo
      // 2. Primeira task da feature como fallback
      let taskAlvo = featureTasks.find((t) => {
        const arq = ((t as any).arquivoAlvo as string) ?? ""
        return arq && arquivo.endsWith(arq.replace(/\\/g, "/"))
      })

      if (!taskAlvo) {
        // Fallback: task mencionada no commit
        for (const commit of fm.commits) {
          if (!commit.arquivos.includes(arquivo)) continue
          if (commit.taskIds) {
            for (const tid of commit.taskIds) {
              taskAlvo = featureTasks.find((t) =>
                t.nome.startsWith(tid),
              )
              if (taskAlvo) break
            }
          }
          if (taskAlvo) break
        }
      }

      if (!taskAlvo) continue

      for (const codeNo of nos) {
        // Nao criar se ja existe aresta de maior confianca
        arestas.push({
          sourceId: codeNo.id,
          targetId: taskAlvo.id,
          tipo: "TASK_MODIFIES",
          confianca: 0.85,
          propriedades: { origem: "git-log", feature },
        })
      }
    }
  }

  return arestas
}

// ---------------------------------------------------------------------------
// Linkar tudo
// ---------------------------------------------------------------------------

// @@T016 [US4] linkarSpecCode
export function linkarSpecCode(
  kg: KnowledgeGraph,
  anotacoes: CodeAnnotation[],
  gitLog?: GitLogResult,
): LinkResult {
  const porAnotacao = linkarPorAnotacao(anotacoes, kg)
  const porTaskFile = linkarPorTaskFile(kg)
  const porGitLog = linkarPorGitLog(kg, gitLog)
  const porHeuristica = linkarPorHeuristica(kg)

  // Deduplicar: anotacao > task-file > git-log > heuristica
  const arestasUnicas = new Map<string, GraphEdge>()

  // Processar em ordem de menor confianca -> maior (ultimo ganha)
  for (const aresta of [...porHeuristica, ...porGitLog, ...porTaskFile, ...porAnotacao]) {
    const chave = `${aresta.sourceId}:${aresta.tipo}:${aresta.targetId}`
    const existente = arestasUnicas.get(chave)
    if (!existente || aresta.confianca > existente.confianca) {
      arestasUnicas.set(chave, aresta)
    }
  }

  const todasArestas = [...arestasUnicas.values()]

  return {
    arestas: todasArestas,
    estatisticas: {
      porAnotacao: porAnotacao.length,
      porTaskFile: porTaskFile.length,
      porGitLog: porGitLog.length,
      porHeuristica: porHeuristica.length,
      total: todasArestas.length,
    },
  }
}
