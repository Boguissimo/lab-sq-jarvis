// @@T009 [US1] [FR-002] Parser de codigo TS/JS via TypeScript Compiler API

import ts from "typescript"
import type {
  FunctionNode,
  ClassNode,
  MethodNode,
  InterfaceNode,
  FileNode,
  GraphNode,
  GraphEdge,
  CodeAnnotation,
} from "../graph/types.js"
import { gerarCodeNodeId } from "../graph/types.js"

// ---------------------------------------------------------------------------
// Tipos internos
// ---------------------------------------------------------------------------

export interface CodeParseResult {
  nos: GraphNode[]
  arestas: GraphEdge[]
  anotacoes: CodeAnnotation[]
  erros: string[]
  /** Chamadas `.rpc("nome")` a funcoes SQL — resolvidas no pipeline apos parse do SQL */
  chamadasRpc: ChamadaRpc[]
}

/** Chamada a uma RPC Supabase via literal string (`supabase.rpc("nome")`) */
export interface ChamadaRpc {
  callerNodeId: string
  rpcNome: string
  linha: number
}

interface ImportInfo {
  modulo: string
  bindings: string[]
  filePath: string
  linha: number
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function ehExportado(node: ts.Node): boolean {
  const modifiers = ts.canHaveModifiers(node)
    ? ts.getModifiers(node)
    : undefined
  return modifiers?.some((m) => m.kind === ts.SyntaxKind.ExportKeyword) ?? false
}

// @@T009 [US1] obterLinha
function obterLinha(sourceFile: ts.SourceFile, pos: number): number {
  return sourceFile.getLineAndCharacterOfPosition(pos).line + 1
}

// @@T009 [US1] obterLinhaFim
function obterLinhaFim(sourceFile: ts.SourceFile, node: ts.Node): number {
  return sourceFile.getLineAndCharacterOfPosition(node.getEnd()).line + 1
}

// @@T009 [US1] contarParametros
function contarParametros(
  params: ts.NodeArray<ts.ParameterDeclaration>,
): number {
  return params.length
}

/** Primeira linha de descricao do no: JSDoc estruturado ou comentario-lider de linha/bloco. */
function obterResumoDoc(node: ts.Node, sourceFile: ts.SourceFile): string {
  // 1. JSDoc estruturado
  for (const jsDoc of ts.getJSDocCommentsAndTags(node)) {
    const comentario = (jsDoc as ts.JSDoc).comment
    const texto = typeof comentario === "string" ? comentario : ""
    if (texto.trim()) return texto.trim().split(/\r?\n/)[0]!.slice(0, 200)
  }
  // 2. Comentario-lider // ou /* */ — ignora linhas de anotacao @@T
  const fonte = sourceFile.text
  const ranges = ts.getLeadingCommentRanges(fonte, node.getFullStart()) ?? []
  for (const range of ranges) {
    const limpo = fonte
      .slice(range.pos, range.end)
      .replace(/^\s*\/\/+/gm, "")
      .replace(/^\s*\/\*+|\*+\/\s*$/g, "")
      .replace(/^\s*\*/gm, "")
    const primeira = limpo
      .split(/\r?\n/)
      .map((l) => l.trim())
      .find((l) => l.length > 0 && !l.startsWith("@@"))
    if (primeira) return primeira.slice(0, 200)
  }
  return ""
}

/** Nomes dos parametros, separados por virgula (para enriquecer a busca FTS). */
function listarParametros(
  params: ts.NodeArray<ts.ParameterDeclaration>,
  sourceFile: ts.SourceFile,
): string {
  return params.map((p) => p.name.getText(sourceFile)).join(", ")
}

/** Monta o `conteudo` indexavel de um no de codigo: assinatura + resumo do JSDoc. */
function montarConteudoCodigo(assinatura: string, resumo: string): string {
  return resumo ? `${assinatura} — ${resumo}` : assinatura
}

// ---------------------------------------------------------------------------
// Extrair anotacoes @@TXXX [USXX] [FR-XXX]
// ---------------------------------------------------------------------------

// @@T011 [US4] [FR-004] Parser de anotacoes @@TXXX
// [USx], [FR-xxx], [INV-x] sao TODOS opcionais. Anotacao minima: `@@TXXX descricao`.
const ANNOTATION_REGEX =
  /@@(T\d{3})\s*(?:\[US(\d+)\])?\s*(?:\[(FR-\d{3})\])?\s*(?:\[(INV-\d+)\])?\s*(.*)/

export function extrairAnotacoes(
  conteudo: string,
  filePath: string,
): CodeAnnotation[] {
  const anotacoes: CodeAnnotation[] = []
  const linhas = conteudo.split("\n")

  for (let i = 0; i < linhas.length; i++) {
    const match = linhas[i]?.match(ANNOTATION_REGEX)
    if (!match) continue

    anotacoes.push({
      taskId: match[1]!,
      userStoryId: match[2] ? `US${match[2]}` : "US0",
      frId: match[3] ?? undefined,
      invId: match[4] ?? undefined,
      descricao: match[5]?.trim() || undefined,
      filePath,
      linha: i + 1,
    })
  }

  return anotacoes
}

// ---------------------------------------------------------------------------
// Parser principal
// ---------------------------------------------------------------------------

// @@T009 [US1] parsearCodigo
export function parsearCodigo(
  conteudo: string,
  filePath: string,
): CodeParseResult {
  const nos: GraphNode[] = []
  const arestas: GraphEdge[] = []
  const erros: string[] = []

  // Extrair anotacoes antes do parse AST
  const anotacoes = extrairAnotacoes(conteudo, filePath)

  const sourceFile = ts.createSourceFile(
    filePath,
    conteudo,
    ts.ScriptTarget.Latest,
    true,
    filePath.endsWith(".tsx") || filePath.endsWith(".jsx")
      ? ts.ScriptKind.TSX
      : ts.ScriptKind.TS,
  )

  // Nó de arquivo
  const extensao = filePath.split(".").pop() ?? ""
  const fileNode: FileNode = {
    id: gerarCodeNodeId("File", filePath, filePath),
    label: "File",
    nome: filePath.split("/").pop() ?? filePath,
    filePath,
    extensao,
    tamanho: conteudo.length,
    hash: hashSimples(conteudo),
  }
  nos.push(fileNode)

  // Imports coletados para resolucao
  const imports: ImportInfo[] = []

  // Chamadas coletadas para resolucao
  const chamadas: Array<{
    callerNodeId: string
    calleeName: string
    linha: number
  }> = []

  // Chamadas `.rpc("nome")` a funcoes SQL — resolvidas no pipeline
  const chamadasRpc: ChamadaRpc[] = []

  // Stack para rastrear contexto (classe atual)
  let classeAtualId: string | undefined

  // @@T009 [US1] visitarNo
  function visitarNo(node: ts.Node): void {
    // --- Functions ---
    if (ts.isFunctionDeclaration(node) && node.name) {
      const nome = node.name.text
      const nodeId = gerarCodeNodeId("Function", filePath, nome)

      const funcNode: FunctionNode = {
        id: nodeId,
        label: "Function",
        nome,
        filePath,
        conteudo: montarConteudoCodigo(
          `${nome}(${listarParametros(node.parameters, sourceFile)})`,
          obterResumoDoc(node, sourceFile),
        ),
        linhaInicio: obterLinha(sourceFile, node.getStart()),
        linhaFim: obterLinhaFim(sourceFile, node),
        exportado: ehExportado(node),
        parametrosCount: contarParametros(node.parameters),
      }
      nos.push(funcNode)

      // CONTAINS: File -> Function
      arestas.push({
        sourceId: fileNode.id,
        targetId: nodeId,
        tipo: "CONTAINS",
        confianca: 1.0,
      })

      // Coletar chamadas dentro da funcao
      coletarChamadas(node, nodeId)
    }

    // --- Arrow functions exportadas (export const foo = () => {}) ---
    if (
      ts.isVariableStatement(node) &&
      ehExportado(node)
    ) {
      for (const decl of node.declarationList.declarations) {
        if (
          ts.isIdentifier(decl.name) &&
          decl.initializer &&
          (ts.isArrowFunction(decl.initializer) ||
            ts.isFunctionExpression(decl.initializer))
        ) {
          const nome = decl.name.text
          const nodeId = gerarCodeNodeId("Function", filePath, nome)
          const init = decl.initializer

          const funcNode: FunctionNode = {
            id: nodeId,
            label: "Function",
            nome,
            filePath,
            conteudo: montarConteudoCodigo(
              `${nome}(${listarParametros(init.parameters, sourceFile)})`,
              obterResumoDoc(node, sourceFile),
            ),
            linhaInicio: obterLinha(sourceFile, node.getStart()),
            linhaFim: obterLinhaFim(sourceFile, node),
            exportado: true,
            parametrosCount: contarParametros(init.parameters),
          }
          nos.push(funcNode)

          arestas.push({
            sourceId: fileNode.id,
            targetId: nodeId,
            tipo: "CONTAINS",
            confianca: 1.0,
          })

          coletarChamadas(init, nodeId)
        }
      }
    }

    // --- Classes ---
    if (ts.isClassDeclaration(node) && node.name) {
      const nome = node.name.text
      const nodeId = gerarCodeNodeId("Class", filePath, nome)

      const classNode: ClassNode = {
        id: nodeId,
        label: "Class",
        nome,
        filePath,
        conteudo: montarConteudoCodigo(`class ${nome}`, obterResumoDoc(node, sourceFile)),
        linhaInicio: obterLinha(sourceFile, node.getStart()),
        linhaFim: obterLinhaFim(sourceFile, node),
        exportado: ehExportado(node),
      }
      nos.push(classNode)

      arestas.push({
        sourceId: fileNode.id,
        targetId: nodeId,
        tipo: "CONTAINS",
        confianca: 1.0,
      })

      // Heritage: extends / implements
      if (node.heritageClauses) {
        for (const clause of node.heritageClauses) {
          for (const type of clause.types) {
            const heritageName = type.expression.getText(sourceFile)
            const edgeTipo =
              clause.token === ts.SyntaxKind.ExtendsKeyword
                ? "EXTENDS"
                : "IMPLEMENTS"

            // Aresta pendente — target resolve depois
            arestas.push({
              sourceId: nodeId,
              targetId: `__UNRESOLVED__:${heritageName}`,
              tipo: edgeTipo as "EXTENDS" | "IMPLEMENTS",
              confianca: 0.7,
            })
          }
        }
      }

      // Processar membros
      const prevClasse = classeAtualId
      classeAtualId = nodeId

      for (const member of node.members) {
        if (ts.isMethodDeclaration(member) && member.name) {
          const metodoNome = member.name.getText(sourceFile)
          const metodoId = gerarCodeNodeId(
            "Method",
            filePath,
            `${nome}.${metodoNome}`,
          )

          const metodoNode: MethodNode = {
            id: metodoId,
            label: "Method",
            nome: metodoNome,
            classeId: nodeId,
            filePath,
            conteudo: montarConteudoCodigo(
              `${nome}.${metodoNome}(${listarParametros(member.parameters, sourceFile)})`,
              obterResumoDoc(member, sourceFile),
            ),
            linhaInicio: obterLinha(sourceFile, member.getStart()),
            linhaFim: obterLinhaFim(sourceFile, member),
          }
          nos.push(metodoNode)

          arestas.push({
            sourceId: nodeId,
            targetId: metodoId,
            tipo: "HAS_METHOD",
            confianca: 1.0,
          })

          coletarChamadas(member, metodoId)
        }
      }

      classeAtualId = prevClasse
      return // Nao visitar filhos — ja processamos os membros
    }

    // --- Interfaces ---
    if (ts.isInterfaceDeclaration(node)) {
      const nome = node.name.text
      const nodeId = gerarCodeNodeId("Interface", filePath, nome)

      const membros = node.members
        .map((m) => m.name?.getText(sourceFile) ?? "")
        .filter(Boolean)
        .join(", ")
      const ifaceNode: InterfaceNode = {
        id: nodeId,
        label: "Interface",
        nome,
        filePath,
        conteudo: montarConteudoCodigo(
          membros ? `interface ${nome} { ${membros} }` : `interface ${nome}`,
          obterResumoDoc(node, sourceFile),
        ),
        linhaInicio: obterLinha(sourceFile, node.getStart()),
        linhaFim: obterLinhaFim(sourceFile, node),
        exportado: ehExportado(node),
      }
      nos.push(ifaceNode)

      arestas.push({
        sourceId: fileNode.id,
        targetId: nodeId,
        tipo: "CONTAINS",
        confianca: 1.0,
      })
    }

    // --- Imports ---
    if (ts.isImportDeclaration(node)) {
      const moduleSpecifier = node.moduleSpecifier
      if (ts.isStringLiteral(moduleSpecifier)) {
        const modulo = moduleSpecifier.text
        const bindings: string[] = []

        if (node.importClause) {
          // Default import
          if (node.importClause.name) {
            bindings.push(node.importClause.name.text)
          }
          // Named imports
          if (
            node.importClause.namedBindings &&
            ts.isNamedImports(node.importClause.namedBindings)
          ) {
            for (const el of node.importClause.namedBindings.elements) {
              bindings.push(el.name.text)
            }
          }
          // Namespace import
          if (
            node.importClause.namedBindings &&
            ts.isNamespaceImport(node.importClause.namedBindings)
          ) {
            bindings.push(`* as ${node.importClause.namedBindings.name.text}`)
          }
        }

        imports.push({
          modulo,
          bindings,
          filePath,
          linha: obterLinha(sourceFile, node.getStart()),
        })
      }
    }

    ts.forEachChild(node, visitarNo)
  }

  // @@T009 [US1] coletarChamadas
  function coletarChamadas(node: ts.Node, callerNodeId: string): void {
    // @@T009 [US1] visitarExpressao
    function visitarExpressao(child: ts.Node): void {
      if (ts.isCallExpression(child)) {
        const expr = child.expression
        let calleeName: string

        if (ts.isIdentifier(expr)) {
          calleeName = expr.text
        } else if (ts.isPropertyAccessExpression(expr)) {
          calleeName = expr.getText(sourceFile)
          // Detectar `algo.rpc("nome_funcao")` (Supabase RPC via literal string)
          if (expr.name.text === "rpc") {
            // Desembrulha `as`/`satisfies`/parênteses antes de testar o literal:
            // `supabase.rpc("nome" as never, ...)` (contorno de tipo do PostgREST)
            // tem o 1º arg como AsExpression, não StringLiteral.
            let arg0 = child.arguments[0]
            while (
              arg0 &&
              (ts.isAsExpression(arg0) ||
                ts.isSatisfiesExpression(arg0) ||
                ts.isParenthesizedExpression(arg0))
            ) {
              arg0 = arg0.expression
            }
            if (arg0 && ts.isStringLiteralLike(arg0)) {
              chamadasRpc.push({
                callerNodeId,
                rpcNome: arg0.text,
                linha: obterLinha(sourceFile, child.getStart()),
              })
            }
          }
        } else {
          // Expressao complexa — pular
          ts.forEachChild(child, visitarExpressao)
          return
        }

        chamadas.push({
          callerNodeId,
          calleeName,
          linha: obterLinha(sourceFile, child.getStart()),
        })
      }

      ts.forEachChild(child, visitarExpressao)
    }

    ts.forEachChild(node, visitarExpressao)
  }

  // Executar visita
  ts.forEachChild(sourceFile, visitarNo)

  // Converter imports em arestas IMPORTS (file-level)
  for (const imp of imports) {
    arestas.push({
      sourceId: fileNode.id,
      targetId: `__IMPORT__:${imp.modulo}`,
      tipo: "IMPORTS",
      confianca: 0.9,
      propriedades: { bindings: imp.bindings, linha: imp.linha },
    })
  }

  // Converter chamadas em arestas CALLS (pendente resolucao cross-file)
  for (const chamada of chamadas) {
    // Tentar resolver localmente (mesmo arquivo)
    const targetLocal = nos.find(
      (n) =>
        (n.label === "Function" || n.label === "Method") &&
        n.nome === chamada.calleeName,
    )

    if (targetLocal) {
      arestas.push({
        sourceId: chamada.callerNodeId,
        targetId: targetLocal.id,
        tipo: "CALLS",
        confianca: 0.95, // same-file
      })
    } else {
      // Chamada nao resolvida — sera resolvida no linker
      arestas.push({
        sourceId: chamada.callerNodeId,
        targetId: `__UNRESOLVED_CALL__:${chamada.calleeName}`,
        tipo: "CALLS",
        confianca: 0.5,
        propriedades: { calleeName: chamada.calleeName, linha: chamada.linha },
      })
    }
  }

  return { nos, arestas, anotacoes, erros, chamadasRpc }
}

// ---------------------------------------------------------------------------
// Hash simples para deteccao de mudancas
// ---------------------------------------------------------------------------

// @@T009 [US1] hashSimples
function hashSimples(conteudo: string): string {
  let hash = 0
  for (let i = 0; i < conteudo.length; i++) {
    const char = conteudo.charCodeAt(i)
    hash = ((hash << 5) - hash + char) | 0
  }
  return hash.toString(36)
}
