---
description: "Arkan — Verifica implementacao das GitHub Issues criadas por taskstoissues. Cruza issues-map, tasks.md, GitHub e codigo. Produz issues-audit.md."
mode: analise
fase: 08-qa
nivel: feature
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/check-prerequisites.sh
campo-obrigatorio: ## Issues Criadas in $FEATURE_DIR/06-planning/issues-map.md
campo-obrigatorio: ## Fase 1 in $FEATURE_DIR/06-planning/tasks.md

## PÓS-CONDIÇÕES

arquivo: $FEATURE_DIR/08-qa/issues-audit.md
campo-obrigatorio: ## Conclusao in $FEATURE_DIR/08-qa/issues-audit.md

## Outline

O texto apos `/arkan.verificaissues` e opcional — pode especificar escopo ou filtro:

- Sem argumento: analisa issues **Open** da feature ativa
- `closed`: analisa apenas issues **Closed**
- `all`: analisa **Open + Closed**
- `Fase N`: filtra por fase especifica (ex: "Fase 2")

### Fase 0 — Setup (automatico)

1. Verificar pre-condicoes: `.arkan/scripts/check-prerequisites.sh --json --require-tasks --include-tasks --command .claude/commands/arkan.verificaissues.md`
   - Se falhar: exibir lista de falhas e **parar**
   - Se `issues-map.md` nao existe: orientar executar `/arkan.taskstoissues` primeiro e **parar**
2. Definir `FEATURE_DIR` e `TASKS_FILE` a partir do JSON retornado

### Fase 1 — Carregamento de Contexto (sem interacao)

Carregar silenciosamente:

- Ler `$FEATURE_DIR/06-planning/issues-map.md` — mapa canonico de issues criadas
- Ler `$FEATURE_DIR/06-planning/tasks.md` — estado atual das tasks (`[x]`/`[ ]`)
- Ler `$FEATURE_DIR/03-spec/spec.md` — nome da feature

Construir:

- `FEATURE_NAME`: nome da feature
- `OWNER_REPO`: extrair do frontmatter do `issues-map.md` (campo `repo`)
- `ISSUES_MAP`: tabela task -> issue number -> fase -> labels
- `TASKS_STATE`: mapa task -> estado (`[x]`/`[ ]`)
- `SCOPE`: filtro de escopo (Open/Closed/All/Fase N) — derivado de `$ARGUMENTS`

### Fase 2 — Consulta ao GitHub

Para cada issue no `ISSUES_MAP`:

1. Consultar estado via `mcp__github__issue_read` (owner, repo, issue_number)
2. Capturar: state (open/closed), updated_at, assignees, comments_count
3. Aplicar filtro de `SCOPE`:
   - Se `SCOPE` = Open (padrao): incluir apenas issues com state=open
   - Se `SCOPE` = Closed: incluir apenas issues com state=closed
   - Se `SCOPE` = All: incluir todas
   - Se `SCOPE` = Fase N: filtrar pela coluna Fase do issues-map

**Exibir cabecalho**:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  Verificacao de Issues
Feature: [FEATURE_NAME]  ·  Repo: [OWNER/REPO]
Escopo: [SCOPE]  ·  Issues no escopo: [N]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Fase 3 — Verificacao de Implementacao

Para cada issue no escopo, verificar existencia de codigo:

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

**Descoberta de codigo** (cascata de ferramentas):

1. **arkan-kb** (preferencial): `mcp__arkan-kb__query({query: "<keywords da task>"})` para encontrar simbolos relacionados (ou busca por texto, se não houver indexador)
2. **Grep/Glob** (fallback): buscar keywords da descricao da task nos diretórios de código e de migrações declarados em `.arkan/memory/stack.md`

**Heuristica de implementacao**:

- Codigo encontrado com correspondencia direta a descricao da task → **Implementado**
- Codigo parcial (ex: migration existe mas hook nao) → **Parcialmente implementado**
- Nenhum codigo encontrado → **Nao implementado**

### Fase 4 — Classificacao

Para cada issue, cruzar as 3 fontes e classificar:

| Issue State | tasks.md | Codigo | Classificacao | Icone |
|-------------|----------|--------|---------------|-------|
| Open | `[ ]` | Nao | **Pendente** | ⏳ |
| Open | `[ ]` | Parcial | **Em progresso** | 🔧 |
| Open | `[x]` | Sim | **Pronta para fechar** | ✅ |
| Open | `[x]` | Nao | **Falso positivo** | ⚠️ |
| Closed | `[x]` | Sim | **Concluida** | ✔️ |
| Closed | `[x]` | Nao | **Regressao** | 🔴 |
| Closed | `[ ]` | Nao | **Inconsistencia** | ❌ |
| Closed | `[ ]` | Sim | **tasks.md desatualizado** | 📝 |
| — | — | — | **Issue deletada** | 💀 |

A classificacao **Issue deletada** aplica-se quando o `issues-map.md` referencia uma issue que nao existe mais no GitHub (404).

### Fase 5 — Geracao do Relatorio

Salvar `$FEATURE_DIR/08-qa/issues-audit.md`:

```markdown
---
feature: [FEATURE_NAME]
repo: OWNER/REPO
escopo: [SCOPE]
gerado-em: YYYY-MM-DD
total-analisadas: N
---

## Resumo

| Metrica | Valor |
|---------|-------|
| Issues analisadas | N |
| Concluidas (✔️) | N |
| Prontas para fechar (✅) | N |
| Em progresso (🔧) | N |
| Pendentes (⏳) | N |
| Inconsistencias (❌/⚠️) | N |
| Regressoes (🔴) | N |
| Progresso geral | N% |

## Detalhamento por Fase

### Fase 1 — [Nome da Fase]

| Issue | Task | State | tasks.md | Codigo | Classificacao |
|-------|------|-------|----------|--------|---------------|
| #123 | T001 | Open | [ ] | Nao | ⏳ Pendente |
| #124 | T002 | Open | [x] | Sim | ✅ Pronta p/ fechar |

### Fase 2 — [Nome da Fase]

...

## Acoes Recomendadas

### Criticas (requerem acao imediata)

- 🔴 **Regressao**: #NNN (TXXX) — codigo removido apos fechamento. Investigar.
- ❌ **Inconsistencia**: #NNN (TXXX) — issue fechada sem implementacao. Reabrir ou justificar.

### Recomendadas

- ✅ **Fechar issues**: #NNN, #NNN — implementacao verificada, prontas para fechamento.
- 📝 **Atualizar tasks.md**: TXXX, TXXX — tasks implementadas mas nao marcadas `[x]`.

### Informativas

- ⏳ **Pendentes**: N issues aguardando implementacao.
- 🔧 **Em progresso**: N issues com implementacao parcial.

## Conclusao

[Analise qualitativa: feature esta X% implementada considerando issues no escopo.
 N bloqueadores criticos encontrados. N acoes recomendadas.
 Proximo passo sugerido: /arkan.qa, /arkan.implement, ou fechar issues prontas.]
```

### Fase 6 — Apresentacao ao Desenvolvedor

Exibir resumo no terminal:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  Verificacao de Issues  ·  CONCLUIDO
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Progresso: [N]% ([concluidas + prontas] / [total])

  ✔️  Concluidas:          N
  ✅ Prontas p/ fechar:    N
  🔧 Em progresso:         N
  ⏳ Pendentes:            N
  ⚠️  Atencao necessaria:  N

Relatorio salvo em: $FEATURE_DIR/08-qa/issues-audit.md
```

Se houver itens criticos (Regressao ou Inconsistencia):

```text
⚠️  ATENCAO: [N] itens criticos encontrados. Ver secao "Acoes Recomendadas" no relatorio.
```

Se todas issues estiverem concluidas:

```text
✔️  Todas as issues no escopo estao concluidas. Proximo passo: /arkan.qa
```

## Guidelines

- Preferir `mcp__github__*` para consulta de issues; se indisponível, usar a CLI `gh` (`gh auth login` necessario) como alternativa — registrar qual foi usado
- Documentacao e relatorio em **PT-BR**
- Verificacao de codigo deve ser baseada em evidencia real (arkan-kb/grep) — nao em presuncao
- **Nunca fechar issues automaticamente** — apenas recomendar fechamento ao desenvolvedor
- Se `issues-map.md` nao existe: orientar `/arkan.taskstoissues` e parar (nao tentar inferir issues)
- Se arkan-kb indisponivel: usar grep como fallback e registrar limitacao no relatorio
- Classificacao "Parcialmente implementado" requer justificativa (o que falta)
- Decisao de fechar issues e sempre do desenvolvedor (Constituicao, Principio VIII)
- Se `$ARGUMENTS` especifica filtro: aplicar na Fase 2 e registrar escopo no relatorio
