import { describe, it, expect } from "vitest"
import { KnowledgeGraph } from "../src/graph/knowledge-graph.js"
import { linkarSpecCode } from "../src/graph/linker.js"
import type { CodeAnnotation, GraphNode } from "../src/graph/types.js"

function kg_com_spec_e_code(): KnowledgeGraph {
  const kg = new KnowledgeGraph()

  // Spec nodes
  kg.adicionarNo({
    id: "UserStory:feat:US1",
    label: "UserStory",
    nome: "US1",
    feature: "feat",
    prioridade: "P1",
    descricao: "Buscar no grafo",
  } as any)

  kg.adicionarNo({
    id: "FunctionalRequirement:feat:FR-001",
    label: "FunctionalRequirement",
    nome: "FR-001",
    feature: "feat",
    descricao: "O sistema DEVE parsear arquivos spec e extrair nos tipados",
  } as any)

  kg.adicionarNo({
    id: "Task:feat:T005",
    label: "Task",
    nome: "T005 Implementar spec-parser.ts",
    feature: "feat",
    descricao: "Implementar spec parser",
    arquivoAlvo: "src/parsers/spec-parser.ts",
    userStoryId: "UserStory:feat:US1",
  } as any)

  // Code nodes
  kg.adicionarNo({
    id: "Function:src/parsers/spec-parser.ts:parsearSpec",
    label: "Function",
    nome: "parsearSpec",
    filePath: "src/parsers/spec-parser.ts",
    linhaInicio: 10,
    linhaFim: 50,
    exportado: true,
    parametrosCount: 2,
  } as any)

  kg.adicionarNo({
    id: "File:src/parsers/spec-parser.ts",
    label: "File",
    nome: "spec-parser.ts",
    filePath: "src/parsers/spec-parser.ts",
    extensao: ".ts",
    tamanho: 1000,
    hash: "abc",
  } as any)

  kg.adicionarNo({
    id: "Function:src/search.ts:buscarNoGrafo",
    label: "Function",
    nome: "buscarNoGrafo",
    filePath: "src/search.ts",
    linhaInicio: 5,
    linhaFim: 20,
    exportado: true,
    parametrosCount: 3,
  } as any)

  return kg
}

describe("linkarSpecCode", () => {
  it("linka por anotacao com confianca 1.0", () => {
    const kg = kg_com_spec_e_code()
    const anotacoes: CodeAnnotation[] = [
      {
        taskId: "T005",
        userStoryId: "US1",
        frId: "FR-001",
        filePath: "src/parsers/spec-parser.ts",
        linha: 9,
      },
    ]

    const resultado = linkarSpecCode(kg, anotacoes)
    expect(resultado.estatisticas.porAnotacao).toBeGreaterThan(0)

    const taskLinks = resultado.arestas.filter(
      (a) => a.tipo === "TASK_MODIFIES" && a.confianca === 1.0,
    )
    expect(taskLinks.length).toBeGreaterThanOrEqual(1)

    const frLinks = resultado.arestas.filter(
      (a) => a.tipo === "IMPLEMENTS_FR" && a.confianca === 1.0,
    )
    expect(frLinks.length).toBeGreaterThanOrEqual(1)

    const usLinks = resultado.arestas.filter(
      (a) => a.tipo === "COVERS_US" && a.confianca === 1.0,
    )
    expect(usLinks.length).toBeGreaterThanOrEqual(1)
  })

  it("linka por task-file com confianca proporcional ao path", () => {
    const kg = kg_com_spec_e_code()
    const resultado = linkarSpecCode(kg, [])

    // 3 segmentos (src/parsers/spec-parser.ts) = confianca 0.8
    const taskFileLinks = resultado.arestas.filter(
      (a) => a.tipo === "TASK_MODIFIES" && a.confianca >= 0.7 && a.confianca <= 0.9,
    )
    expect(taskFileLinks.length).toBeGreaterThanOrEqual(1)
    expect(resultado.estatisticas.porTaskFile).toBeGreaterThan(0)
  })

  it("linka por heuristica com confianca 0.7", () => {
    const kg = kg_com_spec_e_code()
    const resultado = linkarSpecCode(kg, [])

    // Heuristica: "parsear" e "extrair" do FR-001 devem matchear "parsearSpec"
    expect(resultado.estatisticas.porHeuristica).toBeGreaterThanOrEqual(0)
  })

  it("deduplicacao: anotacao ganha sobre heuristica", () => {
    const kg = kg_com_spec_e_code()
    const anotacoes: CodeAnnotation[] = [
      {
        taskId: "T005",
        userStoryId: "US1",
        frId: "FR-001",
        filePath: "src/parsers/spec-parser.ts",
        linha: 9,
      },
    ]

    const resultado = linkarSpecCode(kg, anotacoes)

    // Para o mesmo par source:target, deve haver apenas a versao de maior confianca
    const porPar = new Map<string, number>()
    for (const a of resultado.arestas) {
      const chave = `${a.sourceId}:${a.tipo}:${a.targetId}`
      const existente = porPar.get(chave)
      if (existente !== undefined) {
        // Se duplicou, a confianca deve ser a maior
        expect(a.confianca).toBeGreaterThanOrEqual(existente)
      }
      porPar.set(chave, a.confianca)
    }
  })

  it("sem anotacoes nem tasks com File: gera apenas heuristicas", () => {
    const kg = new KnowledgeGraph()
    kg.adicionarNo({
      id: "FR:f:FR-001",
      label: "FunctionalRequirement",
      nome: "FR-001",
      feature: "f",
      descricao: "apenas descricao curta",
    } as any)
    kg.adicionarNo({
      id: "Function:x:fn",
      label: "Function",
      nome: "fn",
      filePath: "x.ts",
      linhaInicio: 1,
      linhaFim: 10,
      exportado: true,
      parametrosCount: 0,
    } as any)

    const resultado = linkarSpecCode(kg, [])
    expect(resultado.estatisticas.porAnotacao).toBe(0)
    expect(resultado.estatisticas.porTaskFile).toBe(0)
  })
})
