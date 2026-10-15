---
name: arkan-kb-auditing
description: "Use when the user wants to check spec-code coverage, validate Constitution constraints, or add traceability annotations. Examples: \"What's missing from the spec?\", \"Audit coverage\", \"Add annotations\", \"Validate constraints\""
---

# Auditing with Arkan-KB

## When to Use

- "What tasks don't have code yet?"
- "Which functions aren't linked to a spec?"
- "Audit the coverage of this feature"
- "Validate Constitution constraints"
- "Add traceability annotations"
- After implementation — to verify completeness
- During QA — to find gaps

## Workflow

```
1. mcp__arkan-kb__audit_coverage({feature: "NNN-name"})    → Find spec-code gaps
2. mcp__arkan-kb__validate()                                → Check Constitution constraints
3. mcp__arkan-kb__annotate({action: "suggest"})             → Propose @@TXXX annotations
4. Review and apply annotations as needed
```

> If "Indice nao encontrado" → run `node arkan-kb/dist/cli/index.js analyze` in terminal.

## Checklist

```
- [ ] mcp__arkan-kb__audit_coverage for the target feature
- [ ] Review tasks without File: references (unimplemented?)
- [ ] Review unannotated code symbols (missing traceability?)
- [ ] Review orphan files (not linked to any feature?)
- [ ] mcp__arkan-kb__validate for Constitution violations
- [ ] mcp__arkan-kb__annotate({action: "suggest"}) for annotation proposals
- [ ] Apply approved annotations
```

## Tools

**mcp__arkan-kb__audit_coverage** — spec-code coverage report:

```
mcp__arkan-kb__audit_coverage({feature: "110-001"})

→ Tasks without File: references:
  - T023: Implementar componente de progresso
  - T025: Adicionar animacao de transicao

→ Unannotated code symbols:
  - calcularProgresso (src/lib/progresso.ts:15) — no @@TXXX annotation

→ Orphan files:
  - src/components/navegacao/legacy-nav.tsx — not linked to any feature
```

**mcp__arkan-kb__validate** — check Constitution constraints:

```
mcp__arkan-kb__validate()

→ Violations:
  - P1: Unidade sem referencia a conceito encontrada (unidade_id: 42)
  - P5: Task T023 sem File: na spec (feature: 110-001)
  - P9: Funcao sem anotacao @@TXXX em caminho critico
```

**mcp__arkan-kb__annotate** — suggest or apply annotations:

```
mcp__arkan-kb__annotate({action: "suggest", min_confidence: 0.7})

→ Proposals:
  - src/lib/agendamento.ts:42 → // @@T015 calcularProximaExecucao
  - src/jobs/etl.ts:8 → // @@T031 processarLote
  (confidence: 0.85, 0.72)
```

```
mcp__arkan-kb__annotate({
  action: "apply",
  file: "src/lib/agendamento.ts",
  line: 42,
  annotation: "// @@T015"
})
→ Applied annotation to line 42
```

## Coverage Metrics

| Metric                  | Meaning                                          |
| ----------------------- | ------------------------------------------------ |
| Tasks with File:        | Spec tasks that reference implementation files    |
| Annotated symbols       | Code symbols with `@@TXXX` traceability           |
| Orphan files            | Source files not linked to any feature             |
| Constitution violations | Broken P1/P5/P9 constraints                       |

## Example: "Audit coverage of the reporting feature"

```
1. mcp__arkan-kb__audit_coverage({feature: "110-001"})
   → 38/42 tasks have File: references
   → 4 tasks missing: T023, T025, T048, T049
   → 12 unannotated symbols in feature scope

2. mcp__arkan-kb__validate()
   → P5 violation: T023 has no File: reference
   → No P1 or P9 violations

3. mcp__arkan-kb__annotate({action: "suggest"})
   → 8 high-confidence proposals for unannotated symbols

4. Review and apply: 6 accepted, 2 rejected (false positives)
```
