---
description: Arkan fase 03 — Checklist de qualidade de requisitos: valida clareza, completude e testabilidade dos FRs da spec.
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/check-prerequisites.sh
arquivo: .arkan/memory/constitution.md
campo-obrigatorio: ## Requirements in $FEATURE_DIR/03-spec/spec.md

## PÓS-CONDIÇÕES

arquivo: $FEATURE_DIR/08-qa/checklists/quality.md

## Outline

### Fase 0 — Setup (automático)

1. Verificar pré-condições
2. Definir `FEATURE_DIR`

### Fase 1 — Carregamento

**Exibir cabeçalho**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  FASE 03 — SPEC  ·  MODO: VERIFICAÇÃO
Agente: Checklist Writer  ·  Step: Validação de requisitos
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Carregar: spec.md, plan.md (se existe), tasks.md (se existe), constitution.md

### Fase 2 — Gerar checklist de qualidade

Avaliar cada FR/NFR/SC em 9 dimensões:

| Dimensão | O que valida |
|----------|-------------|
| Completude | Todos os cenários cobertos? Inputs/outputs definidos? |
| Clareza | Linguagem objetiva? Sem "adequadamente", "eficientemente"? |
| Consistência | Sem contradições entre FRs? Terminologia uniforme? |
| Critérios de Aceitação | Cada FR tem cenário verificável? |
| Cobertura de Cenários | Happy path + error path + edge cases? |
| Edge Cases | Condições de contorno documentadas? |
| NFRs | Performance, segurança, acessibilidade especificados? |
| Dependências | FKs, APIs externas, features predecessoras declaradas? |
| Ambiguidades | Zero `[NEEDS CLARIFICATION]` pendentes? |

Formato dos itens:
```
- [ ] CHK### Descrição [Dimensão, Spec §FR-NNN]
```

Soft cap: 40 itens. Merge duplicatas se exceder.

### Fase 3 — Salvar checklist

Salvar em `$FEATURE_DIR/08-qa/checklists/quality.md`. Append se já existe (nunca substituir).

### Fase 4 — Relatório

Exibir: total de itens, itens por dimensão, score de qualidade (% de dimensões cobertas).

## Guidelines

- Valida REQUISITOS, não implementação
- CORRETO: "FRs de erro definidos para todos os endpoints?" (testa spec)
- ERRADO: "Botão de login funciona?" (testa código)
- 80% dos itens devem referenciar `[Spec §FR-NNN]`
- Documentação em **PT-BR**
