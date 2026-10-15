// @@T008 [US1] [FR-001] Testes unitarios do spec-parser
import { describe, it, expect } from "vitest"
import { readFileSync } from "node:fs"
import { resolve, dirname } from "node:path"
import { fileURLToPath } from "node:url"
import {
  parsearSpec,
  parsearTasks,
  parsearIdeacao,
  parsearArquivoSpec,
} from "../src/parsers/spec-parser.js"

const __dirname = dirname(fileURLToPath(import.meta.url))

function lerFixture(nome: string): string {
  return readFileSync(resolve(__dirname, "fixtures", nome), "utf-8")
}

// ---------------------------------------------------------------------------
// spec.md
// ---------------------------------------------------------------------------

describe("parsearSpec", () => {
  const conteudo = lerFixture("sample-spec.md")
  const resultado = parsearSpec(conteudo, "001-teste", "03-spec/spec.md")

  it("extrai user stories com prioridade", () => {
    const stories = resultado.nos.filter((n) => n.label === "UserStory")
    expect(stories).toHaveLength(2)

    const us1 = stories[0]!
    expect(us1.nome).toContain("US1")
    expect(us1.nome).toContain("Buscar conceitos")
    expect((us1 as any).prioridade).toBe("P1")

    const us2 = stories[1]!
    expect(us2.nome).toContain("US2")
    expect((us2 as any).prioridade).toBe("P2")
  })

  it("extrai requisitos funcionais", () => {
    const frs = resultado.nos.filter(
      (n) => n.label === "FunctionalRequirement",
    )
    expect(frs).toHaveLength(3)
    expect(frs[0]!.nome).toBe("FR-001")
    expect((frs[0] as any).descricao).toContain("parsear spec.md")
  })

  it("extrai requisitos nao-funcionais", () => {
    const nfrs = resultado.nos.filter(
      (n) => n.label === "NonFunctionalRequirement",
    )
    expect(nfrs).toHaveLength(2)
    expect(nfrs[0]!.nome).toBe("NFR-001")
  })

  it("extrai invariantes com flag executavel", () => {
    const invs = resultado.nos.filter((n) => n.label === "Invariant")
    expect(invs.length).toBeGreaterThanOrEqual(3)

    // INV-2 (Ontology-First) deve ser executavel
    const inv2 = invs.find((n) => n.nome.includes("INV-2"))
    expect(inv2).toBeDefined()
    expect((inv2 as any).executavel).toBe(true)

    // INV-4 (Gate Obrigatorio) nao e executavel
    const inv4 = invs.find((n) => n.nome.includes("INV-4"))
    expect(inv4).toBeDefined()
    expect((inv4 as any).executavel).toBe(false)
  })

  it("extrai key entities", () => {
    const entidades = resultado.nos.filter((n) => n.label === "DataEntity")
    expect(entidades).toHaveLength(2)
    expect(entidades[0]!.nome).toBe("SpecNode")
    expect(entidades[1]!.nome).toBe("GraphEdge")
  })

  it("nao gera erros para fixture valida", () => {
    expect(resultado.erros).toHaveLength(0)
  })

  it("extrai >= 5 tipos de no", () => {
    const tipos = new Set(resultado.nos.map((n) => n.label))
    expect(tipos.size).toBeGreaterThanOrEqual(5)
  })
})

// ---------------------------------------------------------------------------
// tasks.md
// ---------------------------------------------------------------------------

describe("parsearTasks", () => {
  const conteudo = lerFixture("sample-tasks.md")
  const resultado = parsearTasks(conteudo, "001-teste", "06-planning/tasks.md")

  it("extrai tasks com IDs corretos", () => {
    expect(resultado.nos).toHaveLength(7)
    expect(resultado.nos[0]!.nome).toContain("T001")
    expect(resultado.nos[4]!.nome).toContain("T005")
  })

  it("detecta tasks paralelizaveis", () => {
    const t002 = resultado.nos.find((n) => n.nome.includes("T002"))
    expect((t002 as any).paralelizavel).toBe(true)

    const t001 = resultado.nos.find((n) => n.nome.includes("T001"))
    expect((t001 as any).paralelizavel).toBe(false)
  })

  it("detecta tasks concluidas", () => {
    const t004 = resultado.nos.find((n) => n.nome.includes("T004"))
    expect((t004 as any).propriedades?.concluida).toBe(true)

    const t003 = resultado.nos.find((n) => n.nome.includes("T003"))
    expect((t003 as any).propriedades?.concluida).toBe(false)
  })

  it("extrai user story ID", () => {
    const t003 = resultado.nos.find((n) => n.nome.includes("T003"))
    expect((t003 as any).userStoryId).toContain("US1")
  })

  it("extrai fase", () => {
    const t001 = resultado.nos.find((n) => n.nome.includes("T001"))
    expect((t001 as any).fase).toContain("Fase 1")

    const t003 = resultado.nos.find((n) => n.nome.includes("T003"))
    expect((t003 as any).fase).toContain("Fase 2")
  })
})

// ---------------------------------------------------------------------------
// ideacao.md
// ---------------------------------------------------------------------------

describe("parsearIdeacao", () => {
  const conteudo = lerFixture("sample-ideacao.md")
  const resultado = parsearIdeacao(
    conteudo,
    "001-teste",
    "01-discovery/ideacao.md",
  )

  it("extrai decisions com titulo", () => {
    expect(resultado.nos).toHaveLength(2)
    expect(resultado.nos[0]!.nome).toContain("D1")
    expect(resultado.nos[0]!.nome).toContain("Formato de persistencia")
  })

  it("extrai opcao escolhida", () => {
    const d1 = resultado.nos[0]!
    expect((d1 as any).opcaoEscolhida).toContain("SQLite")
  })

  it("extrai fundamentacao", () => {
    const d1 = resultado.nos[0]!
    expect((d1 as any).fundamentacao).toContain("Zero dependencia")
  })

  // Regressao: metade dos .md de .arkan/features esta em CRLF e o `.` das regex
  // em JS nao casa `\r`. Este teste fixa as duas quebras explicitamente para que
  // a protecao nao dependa de como a fixture foi gravada no disco.
  it.each([
    ["LF", "\n"],
    ["CRLF", "\r\n"],
  ])("extrai opcao escolhida com quebra %s", (_nome, quebra) => {
    const conteudoNormalizado = conteudo.replace(/\r\n?/g, "\n")
    const conteudoComQuebra = conteudoNormalizado.replace(/\n/g, quebra)
    const parcial = parsearIdeacao(
      conteudoComQuebra,
      "001-teste",
      "01-discovery/ideacao.md",
    )
    expect((parcial.nos[0] as any).opcaoEscolhida).toContain("SQLite")
    expect((parcial.nos[1] as any).opcaoEscolhida).toContain("remark")
  })
})

// ---------------------------------------------------------------------------
// parsearArquivoSpec — deteccao automatica
// ---------------------------------------------------------------------------

describe("parsearArquivoSpec", () => {
  it("detecta tasks.md e usa parsearTasks", () => {
    const conteudo = lerFixture("sample-tasks.md")
    const resultado = parsearArquivoSpec(
      conteudo,
      "001-teste",
      "06-planning/tasks.md",
    )
    expect(resultado.nos[0]!.label).toBe("Task")
  })

  it("detecta ideacao.md e usa parsearIdeacao", () => {
    const conteudo = lerFixture("sample-ideacao.md")
    const resultado = parsearArquivoSpec(
      conteudo,
      "001-teste",
      "01-discovery/ideacao.md",
    )
    expect(resultado.nos[0]!.label).toBe("Decision")
  })

  it("detecta spec.md e usa parsearSpec", () => {
    const conteudo = lerFixture("sample-spec.md")
    const resultado = parsearArquivoSpec(
      conteudo,
      "001-teste",
      "03-spec/spec.md",
    )
    const tipos = new Set(resultado.nos.map((n) => n.label))
    expect(tipos.has("UserStory")).toBe(true)
    expect(tipos.has("FunctionalRequirement")).toBe(true)
  })
})
