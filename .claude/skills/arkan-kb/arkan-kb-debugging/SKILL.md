---
name: arkan-kb-debugging
description: "Use when the user is debugging a bug, tracing an error, or asking why something fails. Examples: \"Why is X failing?\", \"Where does this error come from?\", \"Trace this bug\""
---

# Debugging with Arkan-KB

## When to Use

- "Why is this function failing?"
- "Trace where this error comes from"
- "Who calls this method?"
- "This endpoint returns 500"
- Investigating bugs, errors, or unexpected behavior

## Workflow

```
1. mcp__arkan-kb__query({query: "<error or symptom>"})      → Find related specs + code
2. mcp__arkan-kb__context({name: "<suspect>"})               → See callers/callees/features
3. mcp__arkan-kb__detect_changes({scope: "compare"})         → Check if recent changes caused it
4. Read source files to confirm root cause
```

> If "Indice nao encontrado" → run `node arkan-kb/dist/cli/index.js analyze` in terminal.

## Checklist

```
- [ ] Understand the symptom (error message, unexpected behavior)
- [ ] mcp__arkan-kb__query for error text or related code
- [ ] Identify the suspect function from returned results
- [ ] mcp__arkan-kb__context to see callers, callees, and feature context
- [ ] For regressions: mcp__arkan-kb__detect_changes to see what branch changed
- [ ] Read source files to confirm root cause
```

## Debugging Patterns

| Symptom              | Arkan-KB Approach                                            |
| -------------------- | ------------------------------------------------------------ |
| Error message        | `query` for error text → `context` on throw sites            |
| Wrong return value   | `context` on the function → trace callees for data flow      |
| Intermittent failure | `context` → look for external calls, async deps              |
| Performance issue    | `context` → find symbols with many callers (hot paths)       |
| Recent regression    | `detect_changes({scope: "compare", base_ref: "main"})`       |
| Spec violation       | `validate` → check if Constitution constraints are broken    |

## Tools

**mcp__arkan-kb__query** — find code related to error:

```
mcp__arkan-kb__query({query: "erro validacao unidade"})
→ CodeSymbols: validarUnidade, verificarConceito, RN_UNIDADE_001
→ SpecElements: INV-3 (unidade must reference conceito)
```

**mcp__arkan-kb__context** — full context for a suspect:

```
mcp__arkan-kb__context({name: "validarUnidade"})
→ Incoming calls: pipelineUnidade, criarUnidade
→ Outgoing calls: verificarConceito, verificarAtomicidade
→ Features: 103-000-pipeline-dados
→ Spec links: VALIDATES_INV → INV-3
```

**mcp__arkan-kb__detect_changes** — check what your branch changed:

```
mcp__arkan-kb__detect_changes({scope: "compare", base_ref: "main"})
→ Changed symbols: validarUnidade, criarUnidade
→ Affected features: 103-000-pipeline-dados
→ Risk: changes touch spec-validated code
```

## Example: "Unidade validation fails silently"

```
1. mcp__arkan-kb__query({query: "validacao unidade silenciosa"})
   → CodeSymbols: validarUnidade, verificarConceito
   → SpecElements: INV-3 (unidade must reference conceito)

2. mcp__arkan-kb__context({name: "validarUnidade"})
   → Outgoing: verificarConceito (returns boolean, no error thrown!)
   → Feature: 103-000-pipeline-dados

3. Root cause: verificarConceito returns false but validarUnidade doesn't propagate the error
```
