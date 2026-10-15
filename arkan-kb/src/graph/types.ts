// @@T004 [US1] [FR-001] [FR-002] [FR-003] [FR-004] Tipos do grafo de conhecimento

// ---------------------------------------------------------------------------
// Node Labels
// ---------------------------------------------------------------------------

/** Tipos de no extraidos de especificacoes Arkan */
export type SpecNodeLabel =
  | "UserStory"
  | "FunctionalRequirement"
  | "NonFunctionalRequirement"
  | "Invariant"
  | "Task"
  | "Decision"
  | "DataEntity"
  | "ConstitutionPrinciple"

/** Tipos de no extraidos de codigo-fonte */
export type CodeNodeLabel =
  | "Function"
  | "Class"
  | "Method"
  | "Interface"
  | "File"
  | "Import"

/** Tipos de no extraidos de migrations SQL */
export type SqlNodeLabel = "Table" | "Column" | "RPC" | "Policy" | "SqlIndex"

/** Todos os tipos de no suportados */
export type NodeLabel = SpecNodeLabel | CodeNodeLabel | SqlNodeLabel | "Feature"

// ---------------------------------------------------------------------------
// Edge Types
// ---------------------------------------------------------------------------

/** Arestas entre nos de spec */
export type SpecEdgeType =
  | "CONTAINS_FR"
  | "VALIDATES"
  | "DEPENDS_ON"
  | "COVERS_ENTITY"

/** Arestas entre nos de codigo */
export type CodeEdgeType =
  | "CALLS"
  | "IMPORTS"
  | "EXTENDS"
  | "IMPLEMENTS"
  | "HAS_METHOD"
  | "CONTAINS"
  | "ACCESSES"

/** Arestas cross-domain (spec ↔ code) */
export type CrossEdgeType =
  | "IMPLEMENTS_FR"
  | "VALIDATES_INV"
  | "COVERS_US"
  | "TASK_MODIFIES"
  | "USES_TABLE"
  | "CREATES_TABLE"
  | "REFERENCES_TABLE"
  | "CALLS_RPC"

/** Arestas cross-feature */
export type FeatureEdgeType = "SHARES_ENTITY" | "DEPENDS_ON_FEATURE"

/** Todos os tipos de aresta suportados */
export type EdgeType =
  | SpecEdgeType
  | CodeEdgeType
  | CrossEdgeType
  | FeatureEdgeType

// ---------------------------------------------------------------------------
// Node Interfaces
// ---------------------------------------------------------------------------

/** Propriedades base de todo no */
export interface BaseNode {
  id: string
  label: NodeLabel
  nome: string
  filePath?: string
  feature?: string
  conteudo?: string
  propriedades?: Record<string, unknown>
}

/** No de User Story */
export interface UserStoryNode extends BaseNode {
  label: "UserStory"
  prioridade: "P1" | "P2" | "P3" | "P4"
  descricao: string
}

/** No de Requisito Funcional */
export interface FunctionalRequirementNode extends BaseNode {
  label: "FunctionalRequirement"
  descricao: string
  userStoryId?: string
}

/** No de Requisito Nao-Funcional */
export interface NonFunctionalRequirementNode extends BaseNode {
  label: "NonFunctionalRequirement"
  descricao: string
  categoria?: string
}

/** No de Invariante */
export interface InvariantNode extends BaseNode {
  label: "Invariant"
  descricao: string
  teste?: string
  executavel: boolean
}

/** No de Task */
export interface TaskNode extends BaseNode {
  label: "Task"
  descricao: string
  fase?: string
  paralelizavel: boolean
  arquivoAlvo?: string
  userStoryId?: string
}

/** No de Decisao */
export interface DecisionNode extends BaseNode {
  label: "Decision"
  titulo: string
  opcaoEscolhida: string
  fundamentacao: string
}

/** No de Entidade de Dados */
export interface DataEntityNode extends BaseNode {
  label: "DataEntity"
  descricao: string
  campos?: string[]
}

/** No de Funcao (codigo) */
export interface FunctionNode extends BaseNode {
  label: "Function"
  linhaInicio: number
  linhaFim: number
  exportado: boolean
  parametrosCount: number
}

/** No de Classe (codigo) */
export interface ClassNode extends BaseNode {
  label: "Class"
  linhaInicio: number
  linhaFim: number
  exportado: boolean
}

/** No de Metodo (codigo) */
export interface MethodNode extends BaseNode {
  label: "Method"
  classeId: string
  linhaInicio: number
  linhaFim: number
}

/** No de Interface (codigo) */
export interface InterfaceNode extends BaseNode {
  label: "Interface"
  linhaInicio: number
  linhaFim: number
  exportado: boolean
}

/** No de Arquivo */
export interface FileNode extends BaseNode {
  label: "File"
  extensao: string
  tamanho: number
  hash: string
}

/** No de Tabela SQL */
export interface TableNode extends BaseNode {
  label: "Table"
  schema?: string
  migrationFile: string
}

/** No de RPC SQL */
export interface RPCNode extends BaseNode {
  label: "RPC"
  parametros?: string
  tipoRetorno?: string
  migrationFile: string
}

/** Union de todos os tipos de no */
export type GraphNode =
  | UserStoryNode
  | FunctionalRequirementNode
  | NonFunctionalRequirementNode
  | InvariantNode
  | TaskNode
  | DecisionNode
  | DataEntityNode
  | FunctionNode
  | ClassNode
  | MethodNode
  | InterfaceNode
  | FileNode
  | TableNode
  | RPCNode
  | BaseNode

// ---------------------------------------------------------------------------
// Edge Interface
// ---------------------------------------------------------------------------

/** Aresta do grafo com score de confianca */
export interface GraphEdge {
  sourceId: string
  targetId: string
  tipo: EdgeType
  confianca: number
  propriedades?: Record<string, unknown>
}

// ---------------------------------------------------------------------------
// Annotation (@@TXXX [USXX] [FR-XXX])
// ---------------------------------------------------------------------------

/** Anotacao explicita encontrada no codigo */
export interface CodeAnnotation {
  taskId: string
  userStoryId: string
  frId?: string
  invId?: string
  descricao?: string
  filePath: string
  linha: number
}

// ---------------------------------------------------------------------------
// Metadata
// ---------------------------------------------------------------------------

/** Metadata do indice */
export interface IndexMetadata {
  versao: string
  ultimoCommit: string
  indexadoEm: string
  estatisticas: {
    arquivos: number
    nosSpec: number
    nosCodigo: number
    nosSql: number
    arestas: number
    features: number
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Gera ID de no no formato Label:feature:identifier */
export function gerarNodeId(
  label: NodeLabel,
  feature: string,
  identificador: string,
): string {
  return `${label}:${feature}:${identificador}`
}

/** Gera ID de no de codigo no formato Label:filePath:symbolName */
// @@T004 gerarCodeNodeId
// // @@T004 gerarCodeNodeId
// @@T004 gerarCodeNodeId
export function gerarCodeNodeId(
  label: CodeNodeLabel | SqlNodeLabel,
  filePath: string,
  nome: string,
): string {
  return `${label}:${filePath}:${nome}`
}
