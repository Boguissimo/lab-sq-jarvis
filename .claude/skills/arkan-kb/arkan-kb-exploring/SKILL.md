---
name: arkan-kb-exploring
description: "Use when the user asks how code works, wants to understand architecture, trace execution flows, or explore how specs connect to code. Examples: \"How does X work?\", \"What calls this function?\", \"Which feature implements this?\""
---

# Exploring with Arkan-KB

## When to Use

- "How does authentication work?"
- "Which feature covers this code?"
- "Show me the spec-to-code mapping"
- "Where is the database logic?"
- Understanding code or specs you haven't seen before

## Workflow

```
1. READ arkan-kb://status                                    → Check index stats and freshness
2. mcp__arkan-kb__query({query: "<concept>"})                → Find specs + code related to concept
3. mcp__arkan-kb__context({name: "<symbol or spec element>"}) → Deep dive: callers, callees, features
4. Read source files or spec files for details
```

> If step 1 says index is missing → run `node arkan-kb/dist/cli/index.js analyze` in terminal.

## Checklist

```
- [ ] READ arkan-kb://status
- [ ] mcp__arkan-kb__query for the concept you want to understand
- [ ] Review returned nodes (specs and code grouped by relevance)
- [ ] mcp__arkan-kb__context on key symbols for callers/callees/features
- [ ] Read source or spec files for implementation details
```

## Tools

**mcp__arkan-kb__query** — find specs and code related to a concept:

```
mcp__arkan-kb__query({query: "agendamento de tarefas"})
→ SpecElements: FR-003 (scheduling), INV-2 (scheduling constraint)
→ CodeSymbols: calcularProximaExecucao, atualizarAgendamento
→ Ranked by relevance
```

**mcp__arkan-kb__context** — 360-degree view of a symbol or spec element:

```
mcp__arkan-kb__context({name: "calcularProximaExecucao"})
→ Incoming calls: processarEvento, agendarExecucao
→ Outgoing calls: aplicarRegraDeAgendamento, salvarEstado
→ Features: 110-001-fluxo-usuario
→ Spec links: IMPLEMENTS_FR → FR-003
```

## Rastreabilidade de specs

Arkan-KB relaciona specs e features ao código através das próprias ferramentas MCP acima
(`query`, `context`, `impact`). Quando o índice não está disponível, use Grep/Glob diretamente.

## Example: "How does the content-generation pipeline work?"

```
1. READ arkan-kb://status                           → node counts and freshness
2. mcp__arkan-kb__query({query: "geracao de conteudo"})
   → SpecElements: FR-012 (content generation), T015 (task: implement gerador-conteudo)
   → CodeSymbols: gerarConteudo, criarConteudo, validarConteudo
3. mcp__arkan-kb__context({name: "gerarConteudo"})
   → Incoming: pipelineETL, triggerGeracaoConteudo
   → Outgoing: criarConteudo, validarConteudo, salvarConteudo
   → Feature: 102-000-geracao-conteudo
4. Read src/jobs/geracao-conteudo.ts for implementation
```
