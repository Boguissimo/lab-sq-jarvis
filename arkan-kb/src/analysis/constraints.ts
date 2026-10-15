// @@T033 [US5] [FR-012] [INV-005] Validacao de Constitution constraints

import { KBStorage } from "../graph/storage.js"
import type { GraphNode } from "../graph/types.js"

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

export interface Violacao {
  principio: string
  codigo: string
  descricao: string
  localizacao: string
  severidade: "ERROR" | "WARNING"
}

export interface ValidacaoResult {
  violacoes: Violacao[]
  principiosVerificados: number
  status: "PASS" | "FAIL"
}

// ---------------------------------------------------------------------------
// P1 — Conceito obrigatorio: unidade de conteudo sem conceito canonico
// ---------------------------------------------------------------------------
//
// Exemplo de constraint de projeto: cada projeto define os seus proprios
// principios em `.arkan/projects/<projeto>/constitution.md` e pode ter uma
// validacao equivalente a esta, ajustada ao proprio schema. Os nomes de
// tabela abaixo sao um exemplo — troque pelos do seu dominio.

function validarP1(storage: KBStorage): Violacao[] {
  const violacoes: Violacao[] = []

  // Buscar tabela de unidades de conteudo e verificar que tem FK para conceito
  const tabelas = storage.buscarNosPorLabel("Table")
  const tabelaUnidade = tabelas.find(
    (t) =>
      t.nome === "unidades_conteudo" ||
      t.nome === "unidade" ||
      t.nome === "unidade_conteudo",
  )

  if (!tabelaUnidade) {
    // Nao tem tabela de unidade — nao aplicavel
    return violacoes
  }

  // Verificar via arestas se a unidade referencia um conceito (FK direta ou REFERENCES_TABLE)
  const arestas = storage.obterArestasDoNo(tabelaUnidade.id, "out")
  const temFkConceito = arestas.some((a) => {
    // Checar por ID sintetico de tabela externa (Table:external:conceito)
    if (a.targetId.includes("conceito")) return true
    const target = storage.obterNo(a.targetId)
    return target?.nome?.includes("conceito")
  })

  if (!temFkConceito) {
    violacoes.push({
      principio: "P1",
      codigo: "P1-001",
      descricao:
        "Tabela de unidade de conteudo nao tem FK para conceito canonico (violacao de conceito obrigatorio)",
      localizacao: tabelaUnidade.filePath ?? "desconhecido",
      severidade: "ERROR",
    })
  }

  return violacoes
}

// ---------------------------------------------------------------------------
// P5 — Tipos padronizados de exercicio: apenas TP-001 a TP-006
// ---------------------------------------------------------------------------

// @@T033 [US5] validarP5
function validarP5(storage: KBStorage): Violacao[] {
  const violacoes: Violacao[] = []

  // Buscar funcoes/classes que mencionem tipos de exercicio
  const funcoes = storage.buscarNosPorLabel("Function")
  const tiposValidos = [
    "TP-001",
    "TP-002",
    "TP-003",
    "TP-004",
    "TP-005",
    "TP-006",
  ]

  // Verificar via FRs se a spec define tipos fora do padrao
  const frs = storage.buscarNosPorLabel("FunctionalRequirement")
  for (const fr of frs) {
    const descricao = ((fr as any).descricao as string) ?? ""
    const tipoMatch = descricao.match(/TP-\d{3}/g)
    if (tipoMatch) {
      for (const tipo of tipoMatch) {
        if (!tiposValidos.includes(tipo)) {
          violacoes.push({
            principio: "P5",
            codigo: "P5-001",
            descricao: `FR referencia tipo de exercicio invalido: ${tipo} (validos: TP-001 a TP-006)`,
            localizacao: fr.filePath ?? "desconhecido",
            severidade: "ERROR",
          })
        }
      }
    }
  }

  return violacoes
}

// ---------------------------------------------------------------------------
// P9 — Feedback apos exercicio: todo fluxo de exercicio exibe a unidade apos a resposta
// ---------------------------------------------------------------------------

// @@T033 [US5] validarP9
function validarP9(storage: KBStorage): Violacao[] {
  const violacoes: Violacao[] = []

  // Verificar via invariantes se existe um invariante de feedback pos-exercicio
  const invariantes = storage.buscarNosPorLabel("Invariant")
  const temInvFeedback = invariantes.some(
    (inv) =>
      inv.nome.toLowerCase().includes("feedback apos exercicio") ||
      inv.nome.toLowerCase().includes("feedback após exercício") ||
      inv.nome.toLowerCase().includes("feedback"),
  )

  if (invariantes.length > 0 && !temInvFeedback) {
    violacoes.push({
      principio: "P9",
      codigo: "P9-001",
      descricao:
        "Nenhum invariante define o fluxo de feedback pos-exercicio (P9 nao coberto na spec)",
      localizacao: "spec.md",
      severidade: "WARNING",
    })
  }

  return violacoes
}

// ---------------------------------------------------------------------------
// Validacao completa
// ---------------------------------------------------------------------------

// @@T033 [US5] validarConstitution
export function validarConstitution(storage: KBStorage): ValidacaoResult {
  const violacoes: Violacao[] = []

  violacoes.push(...validarP1(storage))
  violacoes.push(...validarP5(storage))
  violacoes.push(...validarP9(storage))

  const temErro = violacoes.some((v) => v.severidade === "ERROR")

  return {
    violacoes,
    principiosVerificados: 3,
    status: temErro ? "FAIL" : "PASS",
  }
}
