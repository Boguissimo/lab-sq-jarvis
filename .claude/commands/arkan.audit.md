---
description: Arkan fase 08 — Auditoria profunda spec↔código↔banco de dados com scoring de qualidade.
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/check-prerequisites.sh
arquivo: .arkan/memory/constitution.md
campo-obrigatorio: ## Requirements in $FEATURE_DIR/03-spec/spec.md

## PÓS-CONDIÇÕES

arquivo: $FEATURE_DIR/08-qa/audit-report.md

## Outline

### Fase 0 — Setup (automático)

1. Verificar pré-condições
2. Definir `FEATURE_DIR`

### Fase 1 — Carregamento completo

**Exibir cabeçalho**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  FASE 08 — QA  ·  MODO: VERIFICAÇÃO
Agente: Schema Auditor  ·  Step: Auditoria profunda
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Carregar TODOS os artefatos:
- `03-spec/spec.md`, `04-architecture/plan.md`, `06-planning/tasks.md`
- `04-architecture/data-model.md`, `04-architecture/contracts/`, `04-architecture/research.md`
- `04-architecture/quickstart.md`, `04-architecture/inventario-existente.md`
- `01-discovery/ideacao*.md` (se existe)
- `.arkan/memory/constitution.md`

### Fase 2 — Descobrir código (cascata de ferramentas)

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

Usar a primeira ferramenta disponível:

1. **arkan-kb MCP** (preferencial):
   - `mcp__arkan-kb__query({query: "<keywords da feature>"})` — encontrar arquivos indexados (ou busca por texto, se não houver indexador)
   - `mcp__arkan-kb__context({name: "<símbolo>"})` — definição; confirme callers e conexões no próprio indexador, dependências (ou busca por texto, se não houver indexador)
   - `mcp__arkan-kb__audit_coverage()` — gaps spec↔código automáticos (ou busca por texto, se não houver indexador)
2. **Grep/Glob** (fallback final): buscar keywords nos diretórios de código e de migrações declarados em `.arkan/memory/stack.md`

Ler arquivos de código e migrations SQL identificados. Registrar qual ferramenta foi usada.

### Fase 3 — Cross-reference (auditoria principal)

> **Dependência opcional — banco.** As dimensões marcadas 🗄️ abaixo só rodam se `.arkan/memory/stack.md` declarar um banco acessível por servidor de contexto. Sem isso, o comando segue pelo caminho que não toca banco e **declara no artefato**, para cada dimensão marcada, "não avaliável — nenhum banco declarado em `.arkan/memory/stack.md`", em vez de fingir que passou.

| Dimensão | O que audita |
|----------|-------------|
| Spec ↔ Código | Cada FR implementado corretamente/completamente? |
| Spec ↔ Database 🗄️ | Migrations correspondem ao schema documentado? |
| Código ↔ Database 🗄️ | Nomes de colunas, constraints, tipos corretos? |
| Migrations 🗄️ | Replay do zero sem erros? Ordem correta? |
| Tasks ↔ Realidade | Tasks [x] realmente presentes no código? |
| Naming | Nomenclatura consistente spec↔código (↔banco 🗄️, se aplicável)? |
| Constitution | Todos os princípios vigentes do projeto (P1..Pn em `.arkan/projects/<projeto>/constitution.md`) respeitados? |

### Fase 4 — Classificar e pontuar

Severidade: CRITICAL → LOW (mesma escala do alinhamento).

**Score de qualidade**: baseado em:
- 0 CRITICAL = +3
- 0 HIGH = +2
- Cobertura FRs >90% = +2
- Constitution 100% = +1
- Naming consistente = +1
- Migrations corretas 🗄️ = +1 — **apenas se banco declarado** em `.arkan/memory/stack.md`

Sem banco declarado, o ponto de "Migrations corretas" **não entra na base**: o score é **X/9** e o relatório declara, na dimensão 🗄️, "não avaliável — nenhum banco declarado em `.arkan/memory/stack.md`" — nunca aprovado por omissão.

### Fase 5 — Produzir relatório

Salvar em `$FEATURE_DIR/08-qa/audit-report.md`:

```markdown
# Auditoria: Feature [NNN] — [Nome]

**Data**: [DATA]
**Qualidade**: X/10 (ou X/9 se banco não declarado — ver Fase 4)

## CRÍTICO
[Findings críticos]

## ALTO
[Findings altos]

## MÉDIO / BAIXO
[Findings menores]

## Coisas Bem Feitas
[O que está correto e bem implementado]

## Recomendações
[Ações ordenadas por prioridade]
```

### Fase 6 — Discussão

Apresentar relatório. Para CRITICAL/HIGH, propor correção. Dev decide.

## Guidelines

- Auditoria inclui banco de dados (migrations, schema, constraints) **quando `.arkan/memory/stack.md` declarar um banco acessível por servidor de contexto** — diferencial do alinhamento; sem banco declarado, as dimensões 🗄️ são registradas como não avaliáveis, nunca como aprovadas por omissão
- Crítica genuína — não cosmética. Focar em problemas reais.
- Coisas bem feitas: reconhecer explicitamente o que está correto
- Score é objetivo — baseado nos critérios definidos (X/10 com banco declarado, X/9 sem — ver Fase 4)
- Documentação em **PT-BR**
