---
name: arkan-kb-impact-analysis
description: "Use when the user wants to know what will break if they change something, or needs safety analysis before editing code. Examples: \"Is it safe to change X?\", \"What depends on this?\", \"What will break?\", \"What features are affected?\""
---

# Impact Analysis with Arkan-KB

## When to Use

- "Is it safe to change this function?"
- "What will break if I modify X?"
- "Show me the blast radius"
- "Which features are affected?"
- Before making non-trivial code changes
- Before committing — to understand what your changes affect

## Workflow

```
1. mcp__arkan-kb__impact({target: "X", direction: "upstream"})   → What depends on this
2. mcp__arkan-kb__context({name: "X"})                           → See features involved
3. mcp__arkan-kb__detect_changes()                                → Map current git changes to affected features
4. Assess risk and report to user
```

> If "Indice nao encontrado" → run `node arkan-kb/dist/cli/index.js analyze` in terminal.

## Checklist

```
- [ ] mcp__arkan-kb__impact({target, direction: "upstream"}) to find dependents
- [ ] Review d=1 items first (these WILL BREAK)
- [ ] mcp__arkan-kb__context to check which features are involved
- [ ] mcp__arkan-kb__detect_changes() for pre-commit check
- [ ] Assess risk level and report to user
- [ ] If HIGH/CRITICAL: warn user before proceeding
```

## Understanding Output

| Depth | Risk Level       | Meaning                  |
| ----- | ---------------- | ------------------------ |
| d=1   | **WILL BREAK**   | Direct callers/importers |
| d=2   | LIKELY AFFECTED  | Indirect dependencies    |
| d=3   | MAY NEED TESTING | Transitive effects       |

## Risk Assessment

| Affected                                  | Risk     |
| ------------------------------------------ | -------- |
| <5 symbols, 1 feature                      | LOW      |
| 5-15 symbols, 2-3 features                 | MEDIUM   |
| >15 symbols or many features               | HIGH     |
| Critical path (auth, agendamento, pagamentos) | CRITICAL |

## Tools

**mcp__arkan-kb__impact** — the primary tool for blast radius:

```
mcp__arkan-kb__impact({
  target: "calcularProximaExecucao",
  direction: "upstream"
})

→ d=1 (WILL BREAK):
  - processarEvento (src/lib/agendamento.ts:42)
  - agendarExecucao (src/jobs/agendamento.ts:15)

→ d=2 (LIKELY AFFECTED):
  - filaEventos (src/app/fila/page.tsx:22)
```

**mcp__arkan-kb__detect_changes** — git-diff based impact:

```
mcp__arkan-kb__detect_changes({scope: "staged"})

→ Changed: 5 symbols in 3 files
→ Affected features: 110-001-fluxo-usuario, 103-000-pipeline-dados
→ Risk: MEDIUM
```

## Rastreabilidade de specs

Arkan-KB relaciona specs e features ao código através das próprias ferramentas MCP acima
(`query`, `context`, `impact`). Quando o índice não está disponível, use Grep/Glob diretamente.

## Example: "What breaks if I change calcularProximaExecucao?"

```
1. mcp__arkan-kb__impact({target: "calcularProximaExecucao", direction: "upstream"})
   → d=1: processarEvento, agendarExecucao (WILL BREAK)
   → d=2: filaEventos (LIKELY AFFECTED)

2. mcp__arkan-kb__context({name: "calcularProximaExecucao"})
   → Features: 110-001-fluxo-usuario
   → Spec links: IMPLEMENTS_FR → FR-003 (scheduling)

3. Risk: 2 direct callers, 1 feature, scheduling critical path = CRITICAL
   → WARN USER before proceeding
```
