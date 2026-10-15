// @@T030 [US6] [FR-013] MCP Server stdio para integracao com Claude Code

import { Server } from "@modelcontextprotocol/sdk/server/index.js"
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js"
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js"
import { resolve, join } from "node:path"
import { existsSync } from "node:fs"
import { KBStorage } from "../graph/storage.js"
import { buscarNoGrafo } from "../analysis/search.js"
import { obterContextoPorNome } from "../analysis/context.js"
import { calcularImpactoPorNome } from "../analysis/impact.js"
import { detectarMudancas } from "../analysis/detect-changes.js"
import { validarConstitution } from "../analysis/constraints.js"

// ---------------------------------------------------------------------------
// Connection Pool (singleton com timeout de inatividade)
// ---------------------------------------------------------------------------

let storageInstance: KBStorage | null = null
let storageTimer: ReturnType<typeof setTimeout> | null = null
const INATIVIDADE_MS = 30_000

async function obterStorage(): Promise<KBStorage> {
  // Resetar timer de inatividade
  if (storageTimer) {
    clearTimeout(storageTimer)
  }
  storageTimer = setTimeout(() => {
    if (storageInstance) {
      storageInstance.fechar()
      storageInstance = null
      storageTimer = null
    }
  }, INATIVIDADE_MS)

  if (storageInstance) return storageInstance

  const rootDir = resolve(".")
  const dbPath = join(rootDir, ".arkan-kb", "index.db")
  if (!existsSync(dbPath)) {
    throw new Error(
      "Indice Arkan-KB nao encontrado. Execute: arkan-kb analyze",
    )
  }
  storageInstance = await KBStorage.criar(dbPath)
  return storageInstance
}

// ---------------------------------------------------------------------------
// MCP Server
// ---------------------------------------------------------------------------

// @@T030 [US6] iniciarServidorMcp
export async function iniciarServidorMcp(): Promise<void> {
  const server = new Server(
    {
      name: "arkan-kb",
      version: "0.1.0",
    },
    {
      capabilities: {
        tools: {},
        resources: {},
      },
    },
  )

  // --- Tools ---

  server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [
      {
        name: "query",
        description:
          "Buscar no grafo de conhecimento unificado (specs + codigo). Retorna nos rankeados por relevancia.",
        inputSchema: {
          type: "object" as const,
          properties: {
            query: { type: "string", description: "Texto de busca" },
            limit: {
              type: "number",
              description: "Maximo de resultados (default: 10)",
            },
          },
          required: ["query"],
        },
      },
      {
        name: "context",
        description:
          "Visao 360 de um simbolo ou elemento de spec: callers, callees, features envolvidas.",
        inputSchema: {
          type: "object" as const,
          properties: {
            name: {
              type: "string",
              description: "Nome do simbolo ou elemento",
            },
          },
          required: ["name"],
        },
      },
      {
        name: "impact",
        description:
          "Blast radius: quem sera afetado se este simbolo mudar. Retorna niveis d=1 (WILL BREAK), d=2 (LIKELY AFFECTED), d=3 (MAY NEED TESTING).",
        inputSchema: {
          type: "object" as const,
          properties: {
            target: {
              type: "string",
              description: "Nome do simbolo alvo",
            },
            direction: {
              type: "string",
              enum: ["upstream", "downstream"],
              description: "upstream = quem chama; downstream = quem e chamado",
            },
          },
          required: ["target"],
        },
      },
      {
        name: "detect_changes",
        description:
          "Mapear git diff para simbolos e features afetados no grafo.",
        inputSchema: {
          type: "object" as const,
          properties: {
            scope: {
              type: "string",
              enum: ["staged", "unstaged", "all", "compare"],
              description: "Escopo do diff (default: all)",
            },
            base_ref: {
              type: "string",
              description: "Branch base para compare (default: main)",
            },
          },
        },
      },
      {
        name: "validate",
        description:
          "Validar Constitution constraints executaveis (P1, P5, P9). Retorna violacoes.",
        inputSchema: {
          type: "object" as const,
          properties: {},
        },
      },
      {
        name: "audit_coverage",
        description:
          "Auditoria de cobertura spec↔code por feature. Mostra tasks sem File:, funcoes sem anotacao, arquivos orfaos.",
        inputSchema: {
          type: "object" as const,
          properties: {
            feature: {
              type: "string",
              description: "Filtrar por feature (match parcial). Omitir para todas.",
            },
          },
        },
      },
      {
        name: "annotate",
        description:
          "Sugerir ou aplicar anotacoes @@TXXX em codigo legado. 'suggest' retorna propostas; 'apply' aplica uma anotacao especifica.",
        inputSchema: {
          type: "object" as const,
          properties: {
            action: {
              type: "string",
              enum: ["suggest", "apply"],
              description: "suggest = listar propostas; apply = aplicar uma anotacao",
            },
            min_confidence: {
              type: "number",
              description: "Confianca minima para suggest (default: 0.5)",
            },
            limit: {
              type: "number",
              description: "Maximo de propostas para suggest (default: 20)",
            },
            file: {
              type: "string",
              description: "Caminho do arquivo (obrigatorio para apply)",
            },
            line: {
              type: "number",
              description: "Numero da linha (obrigatorio para apply)",
            },
            annotation: {
              type: "string",
              description: "Texto da anotacao (obrigatorio para apply)",
            },
          },
          required: ["action"],
        },
      },
    ],
  }))

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const storage = await obterStorage()
    try {
      switch (request.params.name) {
        case "query": {
          const { query, limit } = request.params.arguments as {
            query: string
            limit?: number
          }
          const resultados = buscarNoGrafo(storage, query, limit ?? 10)
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify(
                  resultados.map((r) => ({
                    label: r.no.label,
                    nome: r.no.nome,
                    feature: r.no.feature,
                    filePath: r.no.filePath,
                    score: r.score,
                  })),
                  null,
                  2,
                ),
              },
            ],
          }
        }

        case "context": {
          const { name } = request.params.arguments as { name: string }
          const ctx = obterContextoPorNome(storage, name)
          if (!ctx) {
            return {
              content: [
                { type: "text" as const, text: `Simbolo "${name}" nao encontrado no indice.` },
              ],
            }
          }
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify(
                  {
                    no: {
                      label: ctx.no.label,
                      nome: ctx.no.nome,
                      feature: ctx.no.feature,
                      filePath: ctx.no.filePath,
                    },
                    incoming: ctx.incoming.map((a) => ({
                      from: a.sourceId,
                      tipo: a.tipo,
                      confianca: a.confianca,
                    })),
                    outgoing: ctx.outgoing.map((a) => ({
                      to: a.targetId,
                      tipo: a.tipo,
                      confianca: a.confianca,
                    })),
                    features: ctx.features,
                  },
                  null,
                  2,
                ),
              },
            ],
          }
        }

        case "impact": {
          const { target, direction } = request.params.arguments as {
            target: string
            direction?: "upstream" | "downstream"
          }
          const resultado = calcularImpactoPorNome(
            storage,
            target,
            direction ?? "upstream",
          )
          if (!resultado) {
            return {
              content: [
                { type: "text" as const, text: `Simbolo "${target}" nao encontrado.` },
              ],
            }
          }
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify(
                  {
                    alvo: resultado.alvo.nome,
                    direcao: resultado.direcao,
                    risco: resultado.risco,
                    totalAfetados: resultado.totalAfetados,
                    niveis: resultado.niveis.map((n) => ({
                      profundidade: n.profundidade,
                      rotulo: n.rotulo,
                      count: n.nos.length,
                      nos: n.nos.map((no) => ({
                        label: no.label,
                        nome: no.nome,
                        filePath: no.filePath,
                      })),
                    })),
                  },
                  null,
                  2,
                ),
              },
            ],
          }
        }

        case "detect_changes": {
          const { scope, base_ref } = (request.params.arguments ?? {}) as {
            scope?: string
            base_ref?: string
          }
          const resultado = detectarMudancas(
            storage,
            (scope as any) ?? "all",
            base_ref,
          )
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify(
                  {
                    resumo: resultado.resumo,
                    arquivosAlterados: resultado.arquivosAlterados,
                    nosAfetados: resultado.nosAfetados.map((n) => ({
                      label: n.label,
                      nome: n.nome,
                      feature: n.feature,
                    })),
                    featuresAfetadas: resultado.featuresAfetadas,
                  },
                  null,
                  2,
                ),
              },
            ],
          }
        }

        case "validate": {
          const resultado = validarConstitution(storage)
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify(resultado, null, 2),
              },
            ],
          }
        }

        case "audit_coverage": {
          const { feature: feat } = (request.params.arguments ?? {}) as {
            feature?: string
          }
          const { auditarCobertura } = await import("../analysis/audit-coverage.js")
          const resultado = auditarCobertura(storage, feat)
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify(resultado, null, 2),
              },
            ],
          }
        }

        case "annotate": {
          const { action, min_confidence, limit, file, line, annotation } =
            (request.params.arguments ?? {}) as {
              action: "suggest" | "apply"
              min_confidence?: number
              limit?: number
              file?: string
              line?: number
              annotation?: string
            }

          if (action === "suggest") {
            const { gerarPropostas } = await import("../analysis/annotator.js")
            const resultado = gerarPropostas(storage)
            const minConf = min_confidence ?? 0.5
            const lim = limit ?? 20
            const filtradas = resultado.propostas
              .filter((p) => p.confianca >= minConf)
              .slice(0, lim)
            return {
              content: [
                {
                  type: "text" as const,
                  text: JSON.stringify(
                    {
                      totalSimbolosSemAnotacao: resultado.totalSimbolosSemAnotacao,
                      totalPropostas: filtradas.length,
                      propostas: filtradas.map((p) => ({
                        filePath: p.filePath,
                        linha: p.linha,
                        simbolo: p.nomeSimboloCode,
                        anotacao: p.anotacaoSugerida,
                        confianca: p.confianca,
                        evidencias: p.evidencias,
                      })),
                    },
                    null,
                    2,
                  ),
                },
              ],
            }
          }

          if (action === "apply") {
            if (!file || !line || !annotation) {
              return {
                content: [
                  {
                    type: "text" as const,
                    text: "Parametros obrigatorios para apply: file, line, annotation",
                  },
                ],
                isError: true,
              }
            }
            const { aplicarAnotacao } = await import("../analysis/annotator.js")
            aplicarAnotacao(file, line, annotation)
            return {
              content: [
                {
                  type: "text" as const,
                  text: JSON.stringify(
                    { status: "ok", mensagem: `Anotacao aplicada em ${file}:${line}` },
                    null,
                    2,
                  ),
                },
              ],
            }
          }

          return {
            content: [
              {
                type: "text" as const,
                text: `Acao desconhecida: ${action}. Use "suggest" ou "apply".`,
              },
            ],
            isError: true,
          }
        }

        default:
          return {
            content: [
              {
                type: "text" as const,
                text: `Ferramenta desconhecida: ${request.params.name}`,
              },
            ],
            isError: true,
          }
      }
    } catch (e) {
      return {
        content: [
          {
            type: "text" as const,
            text: `Erro: ${e instanceof Error ? e.message : String(e)}`,
          },
        ],
        isError: true,
      }
    }
    // Connection pool gerencia lifecycle — nao fechar aqui
  })

  // --- Resources ---

  server.setRequestHandler(ListResourcesRequestSchema, async () => ({
    resources: [
      {
        uri: "arkan-kb://status",
        name: "Status do Indice",
        description: "Estatisticas e saude do indice Arkan-KB",
        mimeType: "application/json",
      },
    ],
  }))

  server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
    if (request.params.uri === "arkan-kb://status") {
      const storage = await obterStorage()
      const meta = storage.obterMetadata()
      const nosPorLabel = storage.contarNosPorLabel()

      return {
        contents: [
          {
            uri: request.params.uri,
            mimeType: "application/json",
            text: JSON.stringify({ meta, nosPorLabel }, null, 2),
          },
        ],
      }
    }

    return {
      contents: [
        {
          uri: request.params.uri,
          mimeType: "text/plain",
          text: "Recurso nao encontrado",
        },
      ],
    }
  })

  // --- Start ---

  const transport = new StdioServerTransport()
  await server.connect(transport)
}
