---
description: Arkan fase 06 — Análise de consistência cruzada spec↔plan↔tasks antes da implementação.
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/check-prerequisites.sh
arquivo: .arkan/memory/constitution.md
campo-obrigatorio: ## Requirements in $FEATURE_DIR/03-spec/spec.md
arquivo: $FEATURE_DIR/04-architecture/plan.md
arquivo: $FEATURE_DIR/06-planning/tasks.md

## PÓS-CONDIÇÕES

arquivo: $FEATURE_DIR/08-qa/analyze-report.md

## Outline

### Fase 0 — Setup (automático)

1. Verificar pré-condições (spec + plan + tasks devem existir)
2. Definir `FEATURE_DIR`

### Fase 1 — Carregamento

**Exibir cabeçalho**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  TRANSIÇÃO 06→07  ·  MODO: VERIFICAÇÃO
Agente: Consistency Analyzer  ·  Step: Análise cruzada
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Carregar em paralelo:
- `$FEATURE_DIR/03-spec/spec.md` — user stories, FRs, invariantes
- `$FEATURE_DIR/04-architecture/plan.md` — ADRs, interfaces, data model
- `$FEATURE_DIR/06-planning/tasks.md` — tasks e dependências
- `.arkan/memory/constitution.md` — princípios

### Fase 2 — Construir modelos semânticos

Extrair de cada artefato:
- **Spec**: inventário de FRs, user stories, invariantes, entidades
- **Plan**: ADRs, interfaces expostas, tabelas/colunas, dependências
- **Tasks**: mapa task→FR, task→arquivo, fases e checkpoints

### Fase 3 — Detecção de inconsistências (máx. 50 findings)

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

| Passe | O que detecta |
|-------|---------------|
| A. Duplicação | FRs redundantes, tasks duplicadas |
| B. Ambiguidade | Adjetivos vagos, placeholders `[TBD]`; termo qualitativo em FR/NFR sem entrada em `## Definições normativas`; SC sem `**Instrumento:**`/`**Baseline:**`; invariante sem `**Teste:**` |
| C. Sub-especificação | FRs sem objeto/resultado definido |
| D. Constitution | Violações dos princípios vigentes (core I-VIII + projeto P1..Pn em `.arkan/projects/<projeto>/constitution.md`) |
| E. Cobertura | FRs sem tasks, tasks sem FRs |
| F. Inconsistência | Drift de terminologia, entidades divergentes spec↔plan |
| G. Codebase (arkan-kb → Grep) | Scope creep, mudanças colaterais, impacto não documentado. Usar cascata: `mcp__arkan-kb__query` (ou busca por texto, se não houver indexador) → Grep/Glob |

### Fase 4 — Classificar severidade

| Severidade | Critério |
|-----------|---------|
| CRITICAL | Bloqueia implementação — FR sem task, invariante sem cobertura |
| HIGH | Risco alto — ambiguidade em FR P1, entidade divergente |
| MEDIUM | Risco moderado — duplicação, terminologia inconsistente |
| LOW | Cosmético — formatação, ordem |

### Fase 5 — Produzir relatório

Salvar em `$FEATURE_DIR/08-qa/analyze-report.md`:

```markdown
# Análise de Consistência: Feature [NNN] — [Nome]

**Data**: [DATA]
**Artefatos analisados**: spec.md, plan.md, tasks.md

## Métricas de Cobertura

- FRs com tasks: X/Y (Z%)
- Tasks com FRs: X/Y (Z%)
- Invariantes com cobertura: X/Y (Z%)
- Constitution compliance: X/Y princípios verificados

## Findings

| # | Severidade | Passe | Artefato | Descrição |
|---|-----------|-------|----------|-----------|
| 1 | CRITICAL | E | spec.md | FR-007 sem task correspondente |
| ... |

## Recomendações

[Ações ordenadas por prioridade]
```

### Fase 6 — Oferecer remediação

Apresentar findings ao dev. Para cada CRITICAL/HIGH, propor correção. Aguardar aprovação antes de aplicar.

## Guidelines

- Gate de qualidade — se CRITICAL encontrado, recomendar corrigir antes de `/arkan.implement`
- Máximo 50 findings por análise
- Cada finding deve referenciar artefato e seção específica
- Documentação em **PT-BR**
