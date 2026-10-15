// @@T034 [US7] [FR-011] Auditoria de cobertura spec↔code por feature

import { KBStorage } from "../graph/storage.js"
import type { GraphNode, GraphEdge } from "../graph/types.js"

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

export interface TaskCoverage {
  taskId: string
  taskNome: string
  feature: string
  temFile: boolean
  arquivosAlvo: string[]
  funcoesLinkadas: number
  funcoesAnotadas: number // confianca 1.0
}

export interface ArquivoOrfao {
  filePath: string
  funcoes: string[]
  totalFuncoes: number
}

export interface FeatureCoverage {
  feature: string
  totalTasks: number
  tasksComFile: number
  tasksSemFile: number
  totalFuncoesCodigo: number
  funcoesAnotadas: number
  funcoesComHeuristica: number
  funcoesSemLink: number
  percentualCobertura: number
  tasksDetalhes: TaskCoverage[]
  arquivosOrfaos: ArquivoOrfao[]
}

export interface AuditResult {
  features: FeatureCoverage[]
  resumoGlobal: {
    totalFeatures: number
    totalTasks: number
    tasksComFile: number
    tasksSemFile: number
    totalFuncoes: number
    funcoesAnotadas: number
    funcoesComHeuristica: number
    funcoesSemLink: number
    percentualCobertura: number
  }
}

// ---------------------------------------------------------------------------
// Auditoria
// ---------------------------------------------------------------------------

export function auditarCobertura(
  storage: KBStorage,
  filtroFeature?: string,
): AuditResult {
  // Carregar todos os nos e arestas relevantes
  const tasks = storage.buscarNosPorLabel("Task")
  const funcoes = storage.buscarNosPorLabel("Function")
  const classes = storage.buscarNosPorLabel("Class")
  const metodos = storage.buscarNosPorLabel("Method")
  const codeNos = [...funcoes, ...classes, ...metodos]

  // Agrupar por feature
  const featureSet = new Set<string>()
  for (const t of tasks) if (t.feature) featureSet.add(t.feature)
  for (const c of codeNos) if (c.feature) featureSet.add(c.feature)

  const features = [...featureSet].sort()
  const featuresFiltradas = filtroFeature
    ? features.filter((f) => f.includes(filtroFeature))
    : features

  const resultados: FeatureCoverage[] = []

  for (const feature of featuresFiltradas) {
    const featureTasks = tasks.filter((t) => t.feature === feature)
    // Coletar arquivos linkados a tasks desta feature (via File: ou arestas)
    const arquivosFeature = new Set<string>()
    for (const task of featureTasks) {
      const arquivoAlvo = ((task as any).arquivoAlvo as string) ?? ""
      if (arquivoAlvo) arquivosFeature.add(arquivoAlvo.replace(/\\/g, "/"))
      // Tambem via arestas TASK_MODIFIES
      const arestas = storage.obterArestasDoNo(task.id, "out")
      for (const a of arestas) {
        if (a.tipo === "TASK_MODIFIES") {
          const targetNo = storage.obterNo(a.targetId)
          if (targetNo?.filePath) arquivosFeature.add(targetNo.filePath.replace(/\\/g, "/"))
        }
      }
    }

    // Funcoes de codigo: por feature explicita OU por arquivo linkado
    const featureCode = codeNos.filter((c) => {
      if (c.feature === feature) return true
      if (!c.filePath) return false
      const pathNorm = c.filePath.replace(/\\/g, "/")
      // Match por arquivo exato
      if (arquivosFeature.has(pathNorm)) return true
      // Match por path parcial (File: pode ser relativo)
      for (const af of arquivosFeature) {
        if (pathNorm.endsWith(af) || af.endsWith(pathNorm)) return true
      }
      return false
    })

    const tasksDetalhes: TaskCoverage[] = []

    for (const task of featureTasks) {
      const arquivoAlvo = ((task as any).arquivoAlvo as string) ?? ""
      const temFile = arquivoAlvo.length > 0

      // Contar funcoes linkadas a esta task
      const arestas = storage.obterArestasDoNo(task.id, "all")
      const arestasCode = arestas.filter(
        (a) =>
          a.tipo === "TASK_MODIFIES" ||
          a.tipo === "IMPLEMENTS_FR" ||
          a.tipo === "COVERS_US",
      )
      const anotadas = arestasCode.filter((a) => a.confianca >= 1.0)

      tasksDetalhes.push({
        taskId: task.nome.match(/^(T\d{3})/)?.[1] ?? task.nome,
        taskNome: task.nome,
        feature,
        temFile,
        arquivosAlvo: temFile ? [arquivoAlvo] : [],
        funcoesLinkadas: arestasCode.length,
        funcoesAnotadas: anotadas.length,
      })
    }

    // Contar funcoes com/sem anotacao
    let anotadas = 0
    let comHeuristica = 0
    let semLink = 0

    for (const codeNo of featureCode) {
      const arestas = storage.obterArestasDoNo(codeNo.id, "all")
      const specArestas = arestas.filter(
        (a) =>
          a.tipo === "TASK_MODIFIES" ||
          a.tipo === "IMPLEMENTS_FR" ||
          a.tipo === "COVERS_US",
      )

      if (specArestas.some((a) => a.confianca >= 1.0)) {
        anotadas++
      } else if (specArestas.some((a) => a.confianca >= 0.5)) {
        comHeuristica++
      } else {
        semLink++
      }
    }

    // Arquivos orfaos: arquivos com funcoes que nao tem nenhuma aresta spec
    const porArquivo = new Map<string, string[]>()
    for (const codeNo of featureCode) {
      if (!codeNo.filePath) continue
      const arestas = storage.obterArestasDoNo(codeNo.id, "all")
      const temSpec = arestas.some(
        (a) =>
          a.tipo === "TASK_MODIFIES" ||
          a.tipo === "IMPLEMENTS_FR" ||
          a.tipo === "COVERS_US",
      )
      if (!temSpec) {
        if (!porArquivo.has(codeNo.filePath)) porArquivo.set(codeNo.filePath, [])
        porArquivo.get(codeNo.filePath)!.push(codeNo.nome)
      }
    }

    const arquivosOrfaos: ArquivoOrfao[] = [...porArquivo.entries()]
      .map(([filePath, funcoes]) => ({
        filePath,
        funcoes,
        totalFuncoes: funcoes.length,
      }))
      .sort((a, b) => b.totalFuncoes - a.totalFuncoes)

    const totalCode = featureCode.length
    const percentual = totalCode > 0 ? Math.round((anotadas / totalCode) * 100) : 0

    resultados.push({
      feature,
      totalTasks: featureTasks.length,
      tasksComFile: tasksDetalhes.filter((t) => t.temFile).length,
      tasksSemFile: tasksDetalhes.filter((t) => !t.temFile).length,
      totalFuncoesCodigo: totalCode,
      funcoesAnotadas: anotadas,
      funcoesComHeuristica: comHeuristica,
      funcoesSemLink: semLink,
      percentualCobertura: percentual,
      tasksDetalhes,
      arquivosOrfaos,
    })
  }

  // Resumo global
  const totalTasks = resultados.reduce((s, f) => s + f.totalTasks, 0)
  const tasksComFile = resultados.reduce((s, f) => s + f.tasksComFile, 0)
  const totalFuncoes = resultados.reduce((s, f) => s + f.totalFuncoesCodigo, 0)
  const funcoesAnotadas = resultados.reduce((s, f) => s + f.funcoesAnotadas, 0)
  const funcoesComHeuristica = resultados.reduce((s, f) => s + f.funcoesComHeuristica, 0)
  const funcoesSemLink = resultados.reduce((s, f) => s + f.funcoesSemLink, 0)
  const percentualGlobal = totalFuncoes > 0 ? Math.round((funcoesAnotadas / totalFuncoes) * 100) : 0

  return {
    features: resultados,
    resumoGlobal: {
      totalFeatures: resultados.length,
      totalTasks,
      tasksComFile,
      tasksSemFile: totalTasks - tasksComFile,
      totalFuncoes,
      funcoesAnotadas,
      funcoesComHeuristica,
      funcoesSemLink,
      percentualCobertura: percentualGlobal,
    },
  }
}
