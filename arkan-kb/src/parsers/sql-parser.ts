// @@T010 [US1] [FR-003] Parser de migrations SQL — extrai Table, Column, RPC, Policy

import type {
  TableNode,
  RPCNode,
  GraphNode,
  GraphEdge,
  BaseNode,
} from "../graph/types.js"
import { gerarCodeNodeId } from "../graph/types.js"

export interface SqlParseResult {
  nos: GraphNode[]
  arestas: GraphEdge[]
  erros: string[]
}

// ---------------------------------------------------------------------------
// Regex patterns para SQL de Supabase migrations
// ---------------------------------------------------------------------------

const CREATE_TABLE_REGEX =
  /CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:(\w+)\.)?(\w+)\s*\(/gi

const ALTER_TABLE_REGEX =
  /ALTER\s+TABLE\s+(?:(?:IF\s+EXISTS\s+)?(?:(\w+)\.)?(\w+))/gi

const CREATE_FUNCTION_REGEX =
  /CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+(?:(\w+)\.)?(\w+)\s*\(([^)]*)\)\s*RETURNS\s+((?:SETOF\s+)?(?:TABLE\s*\([^)]*\)|[\w.]+(?:\[\])?))/gi

const CREATE_POLICY_REGEX =
  /CREATE\s+POLICY\s+"([^"]+)"\s+ON\s+(?:(\w+)\.)?(\w+)/gi

const CREATE_INDEX_REGEX =
  /CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s+ON\s+(?:(\w+)\.)?(\w+)/gi

const COLUMN_REGEX =
  /^\s+(\w+)\s+([\w()]+(?:\[\])?)/gm

// ---------------------------------------------------------------------------
// Parser
// ---------------------------------------------------------------------------

export function parsearSql(
  conteudo: string,
  filePath: string,
): SqlParseResult {
  const nos: GraphNode[] = []
  const arestas: GraphEdge[] = []
  const erros: string[] = []

  // --- Tables ---
  let match: RegExpExecArray | null

  const tabelasEncontradas = new Set<string>()

  CREATE_TABLE_REGEX.lastIndex = 0
  while ((match = CREATE_TABLE_REGEX.exec(conteudo)) !== null) {
    const schema = match[1] ?? "public"
    const nome = match[2]!
    const chaveTabela = `${schema}.${nome}`

    if (tabelasEncontradas.has(chaveTabela)) continue
    tabelasEncontradas.add(chaveTabela)

    const node: TableNode = {
      id: gerarCodeNodeId("Table", filePath, nome),
      label: "Table",
      nome,
      schema,
      migrationFile: filePath,
      filePath,
      conteudo: `tabela ${schema}.${nome}`,
    }
    nos.push(node)
  }

  // --- Foreign Keys (REFERENCES inline e FOREIGN KEY constraint) ---
  // Pattern inline: coluna UUID REFERENCES tabela(coluna)
  const fkInlineRegex =
    /(\w+)\s+\w+(?:\[\])?\s+REFERENCES\s+(\w+)\s*\(\s*\w+\s*\)/gi
  // Pattern constraint: FOREIGN KEY (coluna) REFERENCES tabela(coluna)
  const fkConstraintRegex =
    /FOREIGN\s+KEY\s*\(\s*(\w+)\s*\)\s+REFERENCES\s+(\w+)\s*\(\s*\w+\s*\)/gi

  for (const regex of [fkInlineRegex, fkConstraintRegex]) {
    regex.lastIndex = 0
    while ((match = regex.exec(conteudo)) !== null) {
      const tabelaReferenciada = match[2]!

      // Encontrar em qual CREATE TABLE estamos (buscar para tras)
      const posicao = match.index
      let tabelaOrigem: string | undefined
      CREATE_TABLE_REGEX.lastIndex = 0
      let ultimaTabela: RegExpExecArray | null = null
      let m2: RegExpExecArray | null
      while ((m2 = CREATE_TABLE_REGEX.exec(conteudo)) !== null) {
        if (m2.index > posicao) break
        ultimaTabela = m2
      }
      if (ultimaTabela) tabelaOrigem = ultimaTabela[2]

      if (tabelaOrigem) {
        const sourceNode = nos.find(
          (n) => n.label === "Table" && n.nome === tabelaOrigem,
        )
        // Target pode estar no mesmo arquivo ou em outra migration
        const targetNode = nos.find(
          (n) => n.label === "Table" && n.nome === tabelaReferenciada,
        )

        if (sourceNode) {
          if (targetNode) {
            arestas.push({
              sourceId: sourceNode.id,
              targetId: targetNode.id,
              tipo: "REFERENCES_TABLE",
              confianca: 1.0,
            })
          } else {
            // Criar aresta com ID sintetico para tabelas de outra migration
            arestas.push({
              sourceId: sourceNode.id,
              targetId: `Table:external:${tabelaReferenciada}`,
              tipo: "REFERENCES_TABLE",
              confianca: 0.9,
            })
          }
        }
      }
    }
  }

  // --- RPC Functions ---
  CREATE_FUNCTION_REGEX.lastIndex = 0
  while ((match = CREATE_FUNCTION_REGEX.exec(conteudo)) !== null) {
    const nome = match[2]!
    const parametros = match[3]?.trim() ?? ""
    const tipoRetorno = match[4]?.trim() ?? "void"

    const node: RPCNode = {
      id: gerarCodeNodeId("RPC", filePath, nome),
      label: "RPC",
      nome,
      parametros,
      tipoRetorno,
      migrationFile: filePath,
      filePath,
      conteudo: `${nome}(${parametros}) RETURNS ${tipoRetorno}`,
    }
    nos.push(node)

    // Detectar tabelas referenciadas no corpo da funcao
    for (const tabela of tabelasEncontradas) {
      const nomeTabela = tabela.split(".")[1]!
      if (conteudo.includes(nomeTabela)) {
        const tabelaNode = nos.find(
          (n) => n.label === "Table" && n.nome === nomeTabela,
        )
        if (tabelaNode) {
          arestas.push({
            sourceId: node.id,
            targetId: tabelaNode.id,
            tipo: "USES_TABLE",
            confianca: 0.8,
          })
        }
      }
    }
  }

  // --- Policies ---
  CREATE_POLICY_REGEX.lastIndex = 0
  while ((match = CREATE_POLICY_REGEX.exec(conteudo)) !== null) {
    const nomePolicy = match[1]!
    const tabela = match[3]!

    const policyNode: BaseNode = {
      id: gerarCodeNodeId("Policy" as any, filePath, nomePolicy),
      label: "Policy" as any,
      nome: nomePolicy,
      filePath,
      conteudo: `policy "${nomePolicy}" on ${tabela}`,
      propriedades: { tabela },
    }
    nos.push(policyNode)

    // Linkar policy -> table
    const tabelaNode = nos.find(
      (n) => n.label === "Table" && n.nome === tabela,
    )
    if (tabelaNode) {
      arestas.push({
        sourceId: policyNode.id,
        targetId: tabelaNode.id,
        tipo: "CONTAINS",
        confianca: 1.0,
      })
    }
  }

  return { nos, arestas, erros }
}
