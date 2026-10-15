// @@T037 [US8] [FR-015] Anotacao retroativa de codigo legado

import { readFileSync, writeFileSync } from "node:fs"
import { KBStorage } from "../graph/storage.js"
import type { GraphNode, GraphEdge } from "../graph/types.js"

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

export interface PropostaAnotacao {
  filePath: string
  linha: number
  nomeSimboloCode: string
  anotacaoSugerida: string
  evidencias: string[]
  confianca: number
}

export interface AnnotatorResult {
  propostas: PropostaAnotacao[]
  totalSimbolosSemAnotacao: number
  totalPropostas: number
}

// ---------------------------------------------------------------------------
// Gerar propostas de anotacao
// ---------------------------------------------------------------------------

export function gerarPropostas(storage: KBStorage): AnnotatorResult {
  const propostas: PropostaAnotacao[] = []

  // Buscar funcoes e classes no grafo
  const funcoes = storage.buscarNosPorLabel("Function")
  const classes = storage.buscarNosPorLabel("Class")
  const metodos = storage.buscarNosPorLabel("Method")
  const codeNos = [...funcoes, ...classes, ...metodos]

  // Buscar tasks com File: definido
  const tasks = storage.buscarNosPorLabel("Task")

  let semAnotacao = 0

  for (const codeNo of codeNos) {
    if (!codeNo.filePath) continue

    // Verificar se ja tem anotacao (aresta com confianca 1.0)
    const arestas = storage.obterArestasDoNo(codeNo.id, "out")
    const jaAnotado = arestas.some(
      (a) =>
        (a.tipo === "IMPLEMENTS_FR" ||
          a.tipo === "COVERS_US" ||
          a.tipo === "TASK_MODIFIES") &&
        a.confianca >= 1.0,
    )

    if (jaAnotado) continue
    semAnotacao++

    // Buscar arestas heuristicas existentes
    const arestasHeuristicas = arestas.filter(
      (a) =>
        (a.tipo === "IMPLEMENTS_FR" ||
          a.tipo === "COVERS_US" ||
          a.tipo === "TASK_MODIFIES") &&
        a.confianca > 0.0 &&
        a.confianca < 1.0,
    )

    if (arestasHeuristicas.length === 0) continue

    // Encontrar a task mais provavel
    const taskAresta = arestasHeuristicas.find(
      (a) => a.tipo === "TASK_MODIFIES",
    )
    const frAresta = arestasHeuristicas.find(
      (a) => a.tipo === "IMPLEMENTS_FR",
    )
    const usAresta = arestasHeuristicas.find((a) => a.tipo === "COVERS_US")

    // Tambem procurar task via File: match (exigir path especifico)
    // Filtrar: so considerar tasks cuja File: referencia path do codigo
    // E penalizar tasks de features que nao se relacionam ao path do codigo
    const taskCandidatas = tasks.filter((t) => {
      const arquivoAlvo = ((t as any).arquivoAlvo as string) ?? ""
      if (!arquivoAlvo) return false
      const segmentos = arquivoAlvo.replace(/\\/g, "/").split("/").filter(Boolean)
      if (segmentos.length < 2) return false
      return codeNo.filePath?.replace(/\\/g, "/").endsWith(arquivoAlvo.replace(/\\/g, "/"))
    })

    // Preferir task cuja feature esta no path do codigo
    // Se nenhuma feature match — descartar todas (evitar cross-feature contamination)
    const pathNorm = (codeNo.filePath ?? "").replace(/\\/g, "/").toLowerCase()

    const taskComFeatureMatch = taskCandidatas.find((t) => {
      const feature = (t.feature ?? "").toLowerCase()
      // Extrair nome da feature sem prefixo numerico (101-000-arkan-kb → arkan-kb)
      const nomeFeature = feature.replace(/^\d+-\d+-/, "").replace(/-/g, "")
      return nomeFeature.length > 2 && pathNorm.includes(nomeFeature)
    })

    // Se nenhuma task tem feature match com o path: so usar se houver task unica
    const taskPorFile = taskComFeatureMatch ?? (taskCandidatas.length === 1 ? taskCandidatas[0] : undefined)

    // Construir anotacao sugerida — 3 fontes independentes:
    // 1. Task por File: match direto (se disponivel)
    // 2. Aresta TASK_MODIFIES no grafo (confianca >= 0.7)
    // 3. Aresta IMPLEMENTS_FR no grafo (heuristica de nome)
    const partes: string[] = []
    const evidencias: string[] = []
    let confianca = 0

    // Fonte 1: Task por File match (mais confiavel)
    if (taskPorFile) {
      const taskId = taskPorFile.nome.match(/^(T\d{3})/)?.[1] ?? ""
      partes.push(taskId)
      const arquivoAlvo = ((taskPorFile as any).arquivoAlvo as string) ?? ""
      const segmentos = arquivoAlvo.replace(/\\/g, "/").split("/").filter(Boolean)
      const confTaskFile = segmentos.length >= 4 ? 0.9 : segmentos.length >= 3 ? 0.8 : 0.7
      evidencias.push(
        `tasks.md ${taskId} referencia File: ${arquivoAlvo} (${segmentos.length} segmentos)`,
      )
      confianca = Math.max(confianca, confTaskFile)
      const usId = (taskPorFile as any).userStoryId as string | undefined
      if (usId) {
        const usMatch = usId.match(/US(\d+)/)
        if (usMatch) partes.push(`[US${usMatch[1]}]`)
      }
    }

    // Fonte 2: Aresta TASK_MODIFIES no grafo (so se nao veio de taskPorFile)
    // E so se a confianca da aresta e >= 0.7
    if (partes.length === 0 && taskAresta && taskAresta.confianca >= 0.7) {
      const targetNo = storage.obterNo(taskAresta.targetId)
      if (targetNo) {
        const taskId = targetNo.nome.match(/^(T\d{3})/)?.[1] ?? ""
        if (taskId) {
          partes.push(taskId)
          evidencias.push(
            `Aresta TASK_MODIFIES conf=${taskAresta.confianca.toFixed(2)} → ${targetNo.nome.slice(0, 50)}`,
          )
          confianca = Math.max(confianca, taskAresta.confianca)
          // US da task
          const usId = (targetNo as any).userStoryId as string | undefined
          if (usId) {
            const usMatch = usId.match(/US(\d+)/)
            if (usMatch) partes.push(`[US${usMatch[1]}]`)
          }
        }
      }
    }

    // Fonte 3: FR por heuristica (complementar, nao substitui task)
    if (frAresta) {
      const targetNo = storage.obterNo(frAresta.targetId)
      if (targetNo) {
        const frId = targetNo.nome.match(/(FR-\d{3})/)?.[1] ?? ""
        const frFeature = targetNo.feature ?? ""
        // So adicionar FR se feature do FR faz sentido para o path do codigo
        // (evitar cross-feature contamination)
        const pathParts = pathNorm.split("/")
        const frFeatureNome = frFeature.replace(/^\d+-\d+-/, "").replace(/-/g, "").toLowerCase()
        const featureRelevante = frFeatureNome.length <= 2 ||
          pathParts.some(p => p.includes(frFeatureNome)) ||
          partes.length === 0 // Se nao tem task, aceitar FR como unica evidencia
        if (frId && featureRelevante) {
          partes.push(`[${frId}]`)
          evidencias.push(
            `Heuristica de nome match com ${frId} da feature ${frFeature} (conf=${frAresta.confianca.toFixed(2)})`,
          )
          // FR sozinho tem confianca menor
          confianca = Math.max(confianca, partes.length > 1 ? frAresta.confianca : frAresta.confianca * 0.8)
        }
      }
    }

    // US por aresta (complementar)
    if (usAresta && !partes.some((p) => p.startsWith("[US"))) {
      const targetNo = storage.obterNo(usAresta.targetId)
      const usMatch = targetNo?.id.match(/US(\d+)/)
      if (usMatch) partes.push(`[US${usMatch[1]}]`)
    }

    if (partes.length === 0) continue

    // Formatar: @@T005 [US1] [FR-002] NomeSimbolo
    const anotacao = `@@${partes.join(" ")} ${codeNo.nome}`

    propostas.push({
      filePath: codeNo.filePath,
      linha: (codeNo as any).linhaInicio ?? 1,
      nomeSimboloCode: codeNo.nome,
      anotacaoSugerida: anotacao,
      evidencias,
      confianca,
    })
  }

  // Ordenar por confianca (maior primeiro)
  propostas.sort((a, b) => b.confianca - a.confianca)

  return {
    propostas,
    totalSimbolosSemAnotacao: semAnotacao,
    totalPropostas: propostas.length,
  }
}

// ---------------------------------------------------------------------------
// Aplicar anotacao a um arquivo
// ---------------------------------------------------------------------------

export function aplicarAnotacao(
  filePath: string,
  linha: number,
  anotacao: string,
): void {
  const conteudo = readFileSync(filePath, "utf-8")
  const linhas = conteudo.split("\n")

  // Inserir comentario acima da linha indicada
  const indice = Math.max(0, linha - 1)
  const indentacao = linhas[indice]?.match(/^(\s*)/)?.[1] ?? ""
  linhas.splice(indice, 0, `${indentacao}// ${anotacao}`)

  writeFileSync(filePath, linhas.join("\n"), "utf-8")
}

// ---------------------------------------------------------------------------
// Aplicar lote de anotacoes (reverse-line para evitar deslocamento)
// ---------------------------------------------------------------------------

export interface ResultadoLote {
  aplicadas: number
  ignoradas: number
  detalhes: Array<{
    proposta: PropostaAnotacao
    status: "aplicada" | "ignorada" | "editada"
  }>
}

// @@T037 [US8] aplicarLote
export function aplicarLote(propostas: PropostaAnotacao[]): ResultadoLote {
  const detalhes: ResultadoLote["detalhes"] = []

  // Agrupar por arquivo
  const porArquivo = new Map<string, PropostaAnotacao[]>()
  for (const p of propostas) {
    if (!porArquivo.has(p.filePath)) porArquivo.set(p.filePath, [])
    porArquivo.get(p.filePath)!.push(p)
  }

  // Para cada arquivo, ordenar por linha decrescente (maior primeiro)
  // Assim inserir na linha 50 nao desloca a linha 20
  for (const [filePath, grupo] of porArquivo) {
    grupo.sort((a, b) => b.linha - a.linha)
    for (const p of grupo) {
      try {
        aplicarAnotacao(filePath, p.linha, p.anotacaoSugerida)
        detalhes.push({ proposta: p, status: "aplicada" })
      } catch {
        detalhes.push({ proposta: p, status: "ignorada" })
      }
    }
  }

  return {
    aplicadas: detalhes.filter((d) => d.status === "aplicada").length,
    ignoradas: detalhes.filter((d) => d.status === "ignorada").length,
    detalhes,
  }
}
