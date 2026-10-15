---
description: "Arkan — Converte tasks do tasks.md em GitHub Issues com labels, dependencias e checklists por fase."
mode: geracao
fase: 06-planning
nivel: feature
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/check-prerequisites.sh
campo-obrigatorio: ## Fase 1 in $FEATURE_DIR/06-planning/tasks.md

## PÓS-CONDIÇÕES

arquivo: $FEATURE_DIR/06-planning/issues-map.md
campo-obrigatorio: ## Issues Criadas in $FEATURE_DIR/06-planning/issues-map.md
tasks.md atualizado com issue numbers.

## Outline

O texto apos `/arkan.taskstoissues` e opcional — pode especificar fase ou filtro (ex: "Fase 2", "apenas P1"). Se vazio, converte todas as tasks incompletas.

### Fase 0 — Setup (automatico)

1. Verificar pre-condicoes: `.arkan/scripts/check-prerequisites.sh --json --require-tasks --include-tasks --command .claude/commands/arkan.taskstoissues.md`
   - Se falhar: exibir lista de falhas e **parar**
2. Definir `FEATURE_DIR` e `TASKS_FILE` a partir do JSON retornado

### Fase 1 — Carregamento de Contexto (sem interacao)

Carregar silenciosamente:

- Ler `$FEATURE_DIR/06-planning/tasks.md` — lista completa de tasks e estado
- Ler `$FEATURE_DIR/03-spec/spec.md` — nome da feature, user stories com prioridades
- Ler `$FEATURE_DIR/04-architecture/plan.md` — estrutura do projeto (para links)

Construir:
- `FEATURE_NAME`: nome da feature (do cabecalho do tasks.md ou spec.md)
- `TASKS_INCOMPLETAS`: lista de tasks com `- [ ]`
- `FASES`: agrupamento de tasks por fase (## Fase N)
- `USER_STORIES`: mapa USN -> descricao (da spec)

### Fase 2 — Validacao GitHub

```bash
git remote get-url origin
```

- Se nao for URL GitHub (`github.com`): **parar** com erro
- Extrair `OWNER/REPO` da URL

**Exibir cabecalho**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  Tasks to Issues
Feature: [FEATURE_NAME]  ·  Repo: [OWNER/REPO]
Tasks incompletas: [N]  ·  Fases: [N]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Fase 3 — Geracao de Issues (por fase)

Para cada fase com tasks incompletas:

**3a. Gerar batch da fase**:

Para cada task `- [ ]` na fase:

- **Title**: `[FEATURE_NAME] TXXX — Descricao`
  - Ex: `[Pipeline Livros] T005 — Criar migration conteudo_didatico`

- **Body**:
  ```markdown
  ## Contexto

  **Feature**: FEATURE_NAME
  **Spec**: [link relativo para spec.md no repo]
  **Plano**: [link relativo para plan.md no repo]
  **Fase**: N — Nome da Fase

  ## Task

  [Descricao completa do tasks.md, incluindo sub-itens]

  ## Arquivo(s)

  [File: paths extraidos da task]

  ## Dependencias

  [Outras tasks/issues que devem ser concluidas primeiro]
  [Se `(depende de TXXX)` no tasks.md, referenciar issue correspondente]

  ## Criterios de Aceite

  [Derivados da user story correspondente — extrair da spec.md]
  [Se task nao tem [USN], usar criterios gerais da fase]
  ```

- **Labels**:
  - `feature` (sempre)
  - `fase-N` (numero da fase, ex: `fase-1`, `fase-3`)
  - `USN` se task tem tag de user story (ex: `US1`, `US2`)
  - `parallelizable` se task tem `[P]`

**3b. Apresentar batch ao desenvolvedor**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BATCH: Fase N — [Nome da Fase]
Issues: [N]  ·  Paralelas: [N com [P]]
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. [FEATURE_NAME] TXXX — Descricao | Labels: feature, fase-N, US1
2. [FEATURE_NAME] TXXX — Descricao | Labels: feature, fase-N, parallelizable
...

Criar estas [N] issues? (sim/nao/ajustar)
```

- Aguardar aprovacao antes de criar (Constituicao, Principio VIII)
- Se "ajustar": aplicar modificacoes e re-apresentar

### Fase 4 — Criacao de Issues

Apos aprovacao de cada batch:

```text
mcp__github__issue_write({method: "create", owner: "OWNER", repo: "REPO",
  title: "...", body: "...", labels: ["feature", "fase-N", "US1"]})
```

> GitHub via MCP (`mcp__github__*`) é o caminho padrão deste comando — os exemplos acima assumem esse caminho. Se o projeto não tiver o MCP do GitHub configurado, usar a CLI `gh` como alternativa (requer `gh auth login`); registrar no relatório final (Fase 7) qual caminho foi usado.

- Criar issues na ordem do tasks.md
- Capturar numero da issue retornado no resultado da tool (`#NNN`)
- Para tasks com dependencias: adicionar cross-reference no body apontando para issue ja criada

### Fase 5 — Atualizacao do tasks.md

1. Para cada issue criada, atualizar a task correspondente:
   - De: `- [ ] T001 [P] [US1] Descricao`
   - Para: `- [ ] T001 (#123) [P] [US1] Descricao`

2. Salvar `$FEATURE_DIR/06-planning/tasks.md`

### Fase 6 — Geracao do issues-map.md

Salvar (ou fazer merge em) `$FEATURE_DIR/06-planning/issues-map.md`:

```markdown
---
feature: [FEATURE_NAME]
repo: OWNER/REPO
gerado-em: YYYY-MM-DD
atualizado-em: YYYY-MM-DD
total-issues: N
---

## Issues Criadas

| Task | Issue | Fase | Labels | Titulo |
|------|-------|------|--------|--------|
| T001 | #123 | 1 | feature, fase-1, US1 | [Feature] T001 — Desc |
| T002 | #124 | 1 | feature, fase-1, P | [Feature] T002 — Desc |
| T005 | #127 | 2 | feature, fase-2 | [Feature] T005 — Desc |
```

**Regras de merge**: se `issues-map.md` ja existe (execucao anterior):
- Manter entradas existentes intactas
- Adicionar novas entradas ao final da tabela
- Atualizar `atualizado-em` e `total-issues` no frontmatter
- **Nunca** remover entradas existentes

### Fase 7 — Relatorio Final

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  Tasks to Issues  ·  CONCLUIDO
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Issues criadas: [N]
Por fase:
  Fase 1 (Setup): [N] issues
  Fase 2 (Fundacao): [N] issues
  Fase 3 (US1): [N] issues
  ...

URLs:
  #123 — T001 Descricao
  #124 — T002 Descricao
  ...

tasks.md atualizado com issue numbers.
issues-map.md salvo em $FEATURE_DIR/06-planning/issues-map.md
```

## Guidelines

- Apenas criar issues para **tasks incompletas** (`- [ ]`)
- Agrupar por **fase** para criacao em batch
- **Perguntar antes de criar** cada batch — nunca criar sem aprovacao
- Preferir GitHub via MCP (`mcp__github__*`); se indisponível, usar a CLI `gh` (`gh auth login` necessario) como alternativa — registrar qual foi usado
- Conteudo das issues em **PT-BR** (quando tasks estao em PT-BR)
- **Cross-references** entre issues dependentes
- Se task ja tem `(#NNN)`: pular — issue ja existe
- Se `$ARGUMENTS` especifica fase: filtrar apenas essa fase
- Nunca criar issues em repositorio diferente do remote
