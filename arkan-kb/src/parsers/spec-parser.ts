// @@T005 [US1] [FR-001] Parser de specs Arkan — extrai nos tipados de Markdown

import { unified } from "unified"
import remarkParse from "remark-parse"
import { visit } from "unist-util-visit"
import type {
  UserStoryNode,
  FunctionalRequirementNode,
  NonFunctionalRequirementNode,
  InvariantNode,
  DataEntityNode,
  TaskNode,
  DecisionNode,
  GraphNode,
  BaseNode,
} from "../graph/types.js"
import { gerarNodeId } from "../graph/types.js"

// ---------------------------------------------------------------------------
// Tipos internos
// ---------------------------------------------------------------------------

interface SpecParseResult {
  nos: GraphNode[]
  erros: string[]
}

interface HeadingNode {
  type: "heading"
  depth: number
  children: Array<{ type: string; value?: string }>
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function textoDeHeading(node: HeadingNode): string {
  return node.children
    .filter((c) => c.type === "text" || c.type === "inlineCode")
    .map((c) => c.value ?? "")
    .join("")
}

/**
 * Normaliza CRLF/CR para LF antes de qualquer regex.
 *
 * Em JavaScript o `.` das expressoes regulares NAO casa `\r` (que e terminador
 * de linha na especificacao). Entao todo padrao que atravessa o fim de linha —
 * como `(.+?)(?:\n|$)` — falha calado em arquivo salvo no Windows, devolvendo
 * string vazia em vez de erro. Metade dos `.md` de `.arkan/features` esta em
 * CRLF, entao normalizar na entrada e a unica forma de o parser ser
 * independente de quem gravou o arquivo.
 */
function normalizarQuebras(conteudo: string): string {
  return conteudo.replace(/\r\n?/g, "\n")
}

// @@[FR-003] extrairTextoAteProximoHeading
// @@T005 [US1] extrairTextoAteProximoHeading
function extrairTextoAteProximoHeading(
  linhas: string[],
  indiceInicio: number,
  nivelHeading: number,
): string {
  const resultado: string[] = []
  for (let i = indiceInicio; i < linhas.length; i++) {
    const match = linhas[i]?.match(/^(#{1,6})\s/)
    if (match && (match[1]?.length ?? 99) <= nivelHeading) break
    resultado.push(linhas[i] ?? "")
  }
  return resultado.join("\n").trim()
}

// ---------------------------------------------------------------------------
// Parser de spec.md — UserStory, FR, NFR, Invariant, DataEntity
// ---------------------------------------------------------------------------

// @@T005 [US1] parsearSpec
export function parsearSpec(
  conteudo: string,
  feature: string,
  filePath: string,
): SpecParseResult {
  const nos: GraphNode[] = []
  const erros: string[] = []
  const linhas = conteudo.split("\n")

  // --- User Stories ---
  // Pattern A: ### User Story N — Titulo (Prioridade: PX)
  // Pattern B: ### USN — Titulo
  // Pattern C: ### USN (PX): Titulo
  const usRegexA =
    /^###\s+User\s+Story\s+(\d+)\s*[—–-]\s*(.+?)\s*\(Prioridade:\s*(P[1-4])\)/i
  const usRegexB = /^###\s+US(\d+)\s*[—–-]\s*(.+)/i
  const usRegexC = /^###\s+US(\d+)\s*\((P[1-4])\):\s*(.+)/i
  for (let i = 0; i < linhas.length; i++) {
    const matchA = linhas[i]?.match(usRegexA)
    const matchB = !matchA ? linhas[i]?.match(usRegexB) : null
    const matchC = !matchA && !matchB ? linhas[i]?.match(usRegexC) : null
    const match = matchA ?? matchB ?? matchC
    if (!match) continue

    let numero: string, titulo: string, prioridade: string | undefined
    if (matchA) {
      numero = matchA[1]!; titulo = matchA[2]!.trim(); prioridade = matchA[3]
    } else if (matchC) {
      numero = matchC[1]!; titulo = matchC[3]!.trim(); prioridade = matchC[2]
    } else {
      numero = match[1]!; titulo = match[2]!.trim(); prioridade = undefined
    }

    const descricao = extrairTextoAteProximoHeading(linhas, i + 1, 3)
    const node: UserStoryNode = {
      id: gerarNodeId("UserStory", feature, `US${numero}`),
      label: "UserStory",
      nome: `US${numero} — ${titulo}`,
      prioridade: (prioridade as "P1" | "P2" | "P3" | "P4") ?? undefined,
      descricao,
      filePath,
      feature,
    }
    nos.push(node)
  }

  // --- Requisitos Funcionais ---
  // Pattern A: - **FR-NNN**: Descricao (lista)
  // Pattern B: ### FR-NNN: Descricao (heading)
  // Pattern C: | FR-NNN | Descricao | ... | (tabela)
  // Pattern D: - **FR-NNN** [USN]: Descricao (lista com US)
  const frIds = new Set<string>()
  const frRegexA = /^-\s+\*\*FR-(\d{3})\*\*:?\s*(?:\[US\d+\]:?)?\s*(.+)/
  const frRegexB = /^###\s+FR-(\d{3}):?\s*(.+)/
  const frRegexC = /^\|\s*FR-(\d{3})\s*\|\s*([^|]+)/
  for (const linha of linhas) {
    const match = linha?.match(frRegexA) ?? linha?.match(frRegexB) ?? linha?.match(frRegexC)
    if (!match) continue

    const numero = match[1]!
    const frId = `FR-${numero}`
    if (frIds.has(frId)) continue
    frIds.add(frId)

    const descricao = match[2]!.trim().replace(/\s*\|\s*$/, "").replace(/\s*\|\s*US\d+\s*\|?\s*$/, "")

    const node: FunctionalRequirementNode = {
      id: gerarNodeId("FunctionalRequirement", feature, frId),
      label: "FunctionalRequirement",
      nome: frId,
      descricao,
      filePath,
      feature,
    }
    nos.push(node)
  }

  // --- Requisitos Nao-Funcionais ---
  // Pattern A: - **NFR-NNN**: Descricao (lista)
  // Pattern B: ### NFR-NNN: Descricao (heading)
  // Pattern C: | NFR-NNN | Descricao | (tabela)
  const nfrIds = new Set<string>()
  const nfrRegexA = /^-\s+\*\*NFR-(\d{3})\*\*:?\s*(.+)/
  const nfrRegexB = /^###\s+NFR-(\d{3}):?\s*(.+)/
  const nfrRegexC = /^\|\s*NFR-(\d{3})\s*\|\s*([^|]+)/
  for (const linha of linhas) {
    const match = linha?.match(nfrRegexA) ?? linha?.match(nfrRegexB) ?? linha?.match(nfrRegexC)
    if (!match) continue

    const numero = match[1]!
    const nfrId = `NFR-${numero}`
    if (nfrIds.has(nfrId)) continue
    nfrIds.add(nfrId)

    const descricao = match[2]!.trim().replace(/\s*\|\s*$/, "")

    const node: NonFunctionalRequirementNode = {
      id: gerarNodeId("NonFunctionalRequirement", feature, nfrId),
      label: "NonFunctionalRequirement",
      nome: nfrId,
      descricao,
      filePath,
      feature,
    }
    nos.push(node)
  }

  // --- Invariantes ---
  // Pattern A: N. **[Nome].** Descricao. Teste: como verificar.
  // Pattern B: ### INV-NNN: Nome / ### INV-NNN — Nome
  // Pattern C: - **INV-NNN**: Descricao / - **INVN**: Descricao
  // Pattern D: N. **INV-NNN — Nome**: Descricao
  const invRegexA = /^(\d+)\.\s+\*\*\[?([^\].*]+?)\]?\.\*\*\s*(.+)/
  const invRegexB = /^###\s+INV-?(\d{3})\s*[:\s—–-]\s*(.+)/
  const invRegexC = /^-\s+\*\*INV-?(\d+)\*\*:?\s*(.+)/
  const invRegexD = /^(\d+)\.\s+\*\*INV-?(\d{3})\s*[—–-]\s*([^*]+)\*\*:?\s*(.+)/
  const invIds = new Set<string>()
  let dentroDeInvariantes = false
  for (let i = 0; i < linhas.length; i++) {
    const linha = linhas[i]
    if (linha?.match(/^##\s+Invariantes/i)) {
      dentroDeInvariantes = true
      continue
    }
    if (dentroDeInvariantes && linha?.match(/^##\s/)) {
      dentroDeInvariantes = false
      continue
    }

    // Pattern B e C podem aparecer fora da secao "Invariantes"
    const matchB = linha?.match(invRegexB)
    const matchC = !matchB ? linha?.match(invRegexC) : null
    const matchD = !matchB && !matchC ? linha?.match(invRegexD) : null
    const matchA = dentroDeInvariantes && !matchB && !matchC && !matchD ? linha?.match(invRegexA) : null

    let numero: string, nomeInv: string, descricao: string

    if (matchB) {
      numero = matchB[1]!; nomeInv = matchB[2]!.trim(); descricao = nomeInv
    } else if (matchC) {
      numero = matchC[1]!; nomeInv = `INV-${numero}`; descricao = matchC[2]!.trim()
    } else if (matchD) {
      numero = matchD[2]!; nomeInv = matchD[3]!.trim(); descricao = matchD[4]!.trim()
    } else if (matchA) {
      numero = matchA[1]!; nomeInv = matchA[2]!.trim(); descricao = matchA[3]!.trim()
    } else {
      continue
    }

    const invId = `INV-${numero}`
    if (invIds.has(invId)) continue
    invIds.add(invId)

    // Separar descricao e teste
    const testeMatch = descricao.match(/(.+?)Teste:\s*(.+)/)
    const descricaoFinal = testeMatch ? testeMatch[1]!.trim() : descricao
    const teste = testeMatch ? testeMatch[2]!.trim() : undefined

    // Verificar se e executavel — lista de exemplo com nomes de principio que
    // costumam ser executaveis (arquitetura, enum fechado, migrations, fluxo de
    // feedback, "spec governa codigo"). Cada projeto usa os nomes dos seus
    // proprios principios; ajuste esta lista para casar com os seus.
    const principiosExecutaveis = [
      "Modelo de Dominio",
      "Enum Fechado",
      "Migrations",
      "Feedback Apos Exercicio",
      "Feedback Após Exercício",
      "Spec Governa",
    ]
    const executavel = principiosExecutaveis.some((p) =>
      nomeInv.toLowerCase().includes(p.toLowerCase()),
    )

    const node: InvariantNode = {
      id: gerarNodeId("Invariant", feature, `INV-${numero}`),
      label: "Invariant",
      nome: `INV-${numero} — ${nomeInv}`,
      descricao: descricaoFinal,
      teste,
      executavel,
      filePath,
      feature,
    }
    nos.push(node)
  }

  // --- Key Entities ---
  // Pattern: - **NomeEntidade**: Descricao
  let dentroDeEntidades = false
  for (const linha of linhas) {
    if (linha?.match(/^###\s+Key\s+Entit/i)) {
      dentroDeEntidades = true
      continue
    }
    if (dentroDeEntidades && linha?.match(/^##/)) {
      dentroDeEntidades = false
      continue
    }
    if (!dentroDeEntidades) continue

    const match = linha?.match(/^-\s+\*\*([^*]+)\*\*:\s*(.+)/)
    if (!match) continue

    const nome = match[1]!.trim()
    const descricao = match[2]!.trim()

    const node: DataEntityNode = {
      id: gerarNodeId("DataEntity", feature, nome),
      label: "DataEntity",
      nome,
      descricao,
      filePath,
      feature,
    }
    nos.push(node)
  }

  if (nos.length === 0) {
    erros.push(`Nenhum no extraido de ${filePath} — verificar formato do Markdown`)
  }

  return { nos, erros }
}

// ---------------------------------------------------------------------------
// Parser de tasks.md — Task nodes
// ---------------------------------------------------------------------------

// @@T006 [US1] [FR-001] Extracao de Tasks
export function parsearTasks(
  conteudo: string,
  feature: string,
  filePath: string,
): SpecParseResult {
  const nos: GraphNode[] = []
  const erros: string[] = []
  const linhas = conteudo.split("\n")
  const taskIds = new Set<string>()

  // Pattern A: - [ ] T001 [P] [US1] Descricao  (checkbox list)
  // Pattern A2: - [X] T001 (#209) [P] [US1] Descricao  (checkbox + issue ref)
  const taskRegexA =
    /^-\s+\[[ xX]\]\s+(T-?\d{3})\s*(?:\(#\d+\))?\s*(\[P\])?\s*(\[US\d+\])?\s*(.+)/

  // Pattern B: ### T001 (#194) — [x] [US4] Descricao  (heading with checkbox)
  // Pattern B2: ### T001 — Descricao [US1, US3]  (heading without checkbox)
  // Pattern B3: ### T-001: Descricao  (heading with hyphen in ID)
  const taskRegexB =
    /^###\s+(T-?\d{3})\s*(?:\(#\d+\))?\s*[—–:-]?\s*(?:\[[ xX]\])?\s*(?:\[(?:P|US\d+)\]\s*)*(.+)/

  let faseAtual = ""

  for (let i = 0; i < linhas.length; i++) {
    const linha = linhas[i]

    // Detectar fase — ambos formatos: "## Fase N:" e "## Phase N:"
    const faseMatch = linha?.match(/^##\s+(?:Fase|Phase)\s+(\d+)\s*[:\s—–-]\s*(.+)/)
    if (faseMatch) {
      faseAtual = `Fase ${faseMatch[1]} — ${faseMatch[2]!.trim()}`
      continue
    }

    const matchA = linha?.match(taskRegexA)
    const matchB = !matchA ? linha?.match(taskRegexB) : null
    const match = matchA ?? matchB

    if (!match) continue

    // Normalizar task ID: T-001 → T001
    const taskIdRaw = match[1]!
    const taskId = taskIdRaw.replace("-", "")

    // Evitar duplicatas
    if (taskIds.has(taskId)) continue
    taskIds.add(taskId)

    const paralelizavel = matchA ? !!matchA[2] : (linha?.includes("[P]") ?? false)

    // Extrair descricao
    let descricao: string
    if (matchA) {
      descricao = matchA[4]!.trim()
    } else {
      // Pattern B: descricao pode ter [USn, USm] no final — remover
      descricao = match[2]!.trim().replace(/\s*\[US[\d,\s]+\]\s*$/, "").trim()
    }

    // Extrair user story — de [USN] no match ou de [USN, USM] no final
    let userStoryId: string | undefined
    const usInline = matchA?.[3]?.match(/US(\d+)/)
    if (usInline) {
      userStoryId = gerarNodeId("UserStory", feature, `US${usInline[1]}`)
    } else {
      const usInDesc = linha?.match(/\[US(\d+)/)
      if (usInDesc) {
        userStoryId = gerarNodeId("UserStory", feature, `US${usInDesc[1]}`)
      }
    }

    // Detectar se esta concluida
    const concluida = /\[x\]/i.test(linha ?? "") || /Status:\s*done/i.test("") // checked below

    const node: TaskNode = {
      id: gerarNodeId("Task", feature, taskId),
      label: "Task",
      nome: `${taskId} — ${descricao}`,
      descricao,
      fase: faseAtual,
      paralelizavel,
      userStoryId,
      filePath,
      feature,
      propriedades: { concluida },
    }

    // Procurar File:/Arquivo: nas sub-linhas (ate proxima task ou secao)
    for (let j = i + 1; j < linhas.length; j++) {
      const subLinha = linhas[j]!
      // Parar ao encontrar proxima task, secao, ou separador
      if (/^-\s+\[/i.test(subLinha) || /^###?\s+T-?\d{3}/i.test(subLinha) || /^##\s/.test(subLinha) || /^\*\*Checkpoint/.test(subLinha) || /^---$/.test(subLinha)) break

      // File: path  ou  **File**: path  ou  **Arquivo**: path  ou  `File: path`
      const fileMatch = subLinha.match(
        /(?:^\s*-\s+|\*\*)?\s*(?:File|Files|Arquivo)s?\*?\*?:\s*`?([^`,\n]+)`?/i,
      )
      if (fileMatch) {
        node.arquivoAlvo = fileMatch[1]!.trim()
        break
      }
    }

    // Tambem checar status done em sub-linhas (para format heading)
    if (!concluida) {
      for (let j = i + 1; j < linhas.length && j < i + 15; j++) {
        const subLinha = linhas[j]!
        if (/^###?\s+T-?\d{3}/i.test(subLinha) || /^##\s/.test(subLinha)) break
        if (/\*\*Status\*\*:\s*done/i.test(subLinha)) {
          node.propriedades = { concluida: true }
          break
        }
      }
    }

    nos.push(node)
  }

  if (nos.length === 0) {
    erros.push(
      `Nenhuma task extraida de ${filePath} — verificar formato TXXX`,
    )
  }

  return { nos, erros }
}

// ---------------------------------------------------------------------------
// Parser de ideacao.md — Decision nodes
// ---------------------------------------------------------------------------

// @@T007 [US1] [FR-001] Extracao de Decisions
export function parsearIdeacao(
  conteudo: string,
  feature: string,
  filePath: string,
): SpecParseResult {
  const nos: GraphNode[] = []
  const erros: string[] = []
  const linhas = normalizarQuebras(conteudo).split("\n")

  // Pattern: ### D1 — Titulo
  // ou:      ### DN — Titulo da decisao
  const decisaoRegex = /^###\s+D(\d+)\s*[—–-]\s*(.+)/

  for (let i = 0; i < linhas.length; i++) {
    const match = linhas[i]?.match(decisaoRegex)
    if (!match) continue

    const numero = match[1]!
    const titulo = match[2]!.trim()
    const blocoTexto = extrairTextoAteProximoHeading(linhas, i + 1, 3)

    // Extrair opcao escolhida (pattern: **Decisao**: Opcao X)
    const opcaoMatch = blocoTexto.match(
      /\*\*Decis[aã]o\*\*:\s*(.+?)(?:\n|$)/,
    )
    const opcaoEscolhida = opcaoMatch ? opcaoMatch[1]!.trim() : ""

    // Extrair fundamentacao (pattern: **Fundamentacao**: ...)
    const fundMatch = blocoTexto.match(
      /\*\*Fundamenta[cç][aã]o\*\*:\s*([\s\S]+?)(?=\n\*\*|\n###|$)/,
    )
    const fundamentacao = fundMatch ? fundMatch[1]!.trim() : ""

    const node: DecisionNode = {
      id: gerarNodeId("Decision", feature, `D${numero}`),
      label: "Decision",
      nome: `D${numero} — ${titulo}`,
      titulo,
      opcaoEscolhida,
      fundamentacao,
      filePath,
      feature,
    }
    nos.push(node)
  }

  return { nos, erros }
}

// ---------------------------------------------------------------------------
// Parser unificado — detecta tipo de arquivo e extrai todos os nos
// ---------------------------------------------------------------------------

// @@[FR-001] parsearArquivoSpec
// @@T005 [US1] parsearArquivoSpec
export function parsearArquivoSpec(
  conteudo: string,
  feature: string,
  filePath: string,
): SpecParseResult {
  const nomeArquivo = filePath.split("/").pop() ?? filePath

  if (nomeArquivo === "tasks.md") {
    return parsearTasks(conteudo, feature, filePath)
  }

  if (nomeArquivo === "ideacao.md") {
    return parsearIdeacao(conteudo, feature, filePath)
  }

  // Default: spec.md, plan.md, ou qualquer outro .md
  return parsearSpec(conteudo, feature, filePath)
}
