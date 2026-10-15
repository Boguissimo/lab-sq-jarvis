---
description: "Arkan fase 08 — QA: orquestra verificação spec↔código + UAT + invariantes. Produz qa-report.md com decisão Go/No-Go para deploy."
mode: orquestracao
fase: 08-qa
nivel: feature
tecnica: "ReAct + Chain-of-Verification + Adversarial Prompting"
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/check-prerequisites.sh
arquivo: .arkan/memory/constitution.md
arquivo: .arkan/templates/08-qa/qa-report-template.md
campo-obrigatorio: ## Requirements in $FEATURE_DIR/03-spec/spec.md
campo-obrigatorio: ## Fase 1 in $FEATURE_DIR/06-planning/tasks.md

## PÓS-CONDIÇÕES

arquivo: $FEATURE_DIR/08-qa/qa-report.md
campo-obrigatorio: ## Resultado do QA in $FEATURE_DIR/08-qa/qa-report.md

## Outline

O texto após `/arkan.qa` é opcional — foco específico (ex: "apenas invariantes", "UAT da US2"). A feature é inferida da branch atual.

**Modo Orquestração**: este command coordena múltiplos agentes em sequência, cada um com foco específico. O desenvolvedor aprova a decisão final (Go/No-Go) explicitamente.

### Fase 0 — Setup (automático)

1. Verificar pré-condições: `.arkan/scripts/check-prerequisites.sh --json --require-tasks --include-tasks --command .claude/commands/arkan.qa.md`
   - Se falhar: exibir lista de falhas e **parar**
   - Verificar que tasks.md tem tasks marcadas `[x]` — se todas são `[ ]`, desenvolvimento não iniciado
2. Definir `FEATURE_DIR` e `TASKS_FILE` a partir do JSON retornado

### Fase 1 — Carregamento de Contexto (sem interação)

**Exibir cabeçalho**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  FASE 08 — QA  ·  MODO: ORQUESTRAÇÃO
Orquestrador: QA Agent  ·  Step: Carregamento de contexto
Ação esperada: aguardar — verificação automática em progresso
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Carregar em paralelo:
- `$FEATURE_DIR/03-spec/spec.md` — user stories, FRs, cenários de aceitação, cenários de erro, **Invariantes**
- `$FEATURE_DIR/06-planning/tasks.md` — tasks e estado (quais `[x]`, quais `[ ]`)
- `$FEATURE_DIR/04-architecture/plan.md` — interfaces expostas, ADRs
- `$FEATURE_DIR/04-architecture/data-model.md` (se existe) — state machines
- `$FEATURE_DIR/04-architecture/quickstart.md` (se existe) — como verificar a feature

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

**Descobrir código implementado** (cascata de ferramentas — usar a primeira disponível):

1. **arkan-kb MCP** (preferencial): `mcp__arkan-kb__query({query: "<keywords>"})` → `mcp__arkan-kb__context({name: "<símbolo>"})` → `mcp__arkan-kb__audit_coverage()` (ou busca por texto, se não houver indexador)
2. **Grep/Glob** (fallback final): buscar keywords nos diretórios de código e de migrações declarados em `.arkan/memory/stack.md`

Ler arquivos de código identificados para verificação. Registrar qual ferramenta foi usada.

### Fase 2 — Verificação de Aceitação

> Agente: QA Agent → .arkan/agents/08-qa/qa-agent.md

**Instrução**: Ler `.arkan/agents/08-qa/qa-agent.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: `spec.md` (cenários de aceitação, cenários de erro, edge cases, Invariantes), `tasks.md` (estado das tasks), código implementado, `quickstart.md` (se existe).

### Fase 3 — Alinhamento Spec↔Código

> Agente: Aligner → .arkan/agents/transversal/aligner.md

**Instrução**: Ler `.arkan/agents/transversal/aligner.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: `spec.md` (Invariantes, FRs), `constitution.md`, `data-model.md` (se existe), `plan.md` (interfaces expostas), código implementado.

### Fase 4 — Revisão Adversarial

> Agente: Auditor → .arkan/agents/08-qa/auditor.md

**Instrução**: Ler `.arkan/agents/08-qa/auditor.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: achados das Fases 2 e 3, `spec.md` (invariantes, cenários, edge cases), código implementado.

### Fase 5 — Produção do Relatório

Salvar `$FEATURE_DIR/08-qa/qa-report.md` a partir do template com todos os resultados.

Calcular status geral:
- Qualquer FAIL em invariante ou cenário P1 → **REPROVADO** (bloqueador)
- Todos P1 PASS, alguns P2+ FAIL → **APROVADO COM RESSALVAS**
- Todos PASS → **APROVADO**

### Fase 6 — Decisão Go/No-Go (desenvolvedor)

Exibir ao desenvolvedor:
- Status geral: APROVADO / APROVADO COM RESSALVAS / REPROVADO
- Bloqueadores: lista de itens que impedem o deploy
- Ressalvas: itens não-bloqueadores que devem ser endereçados

Se REPROVADO: listar bloqueadores com sugestão de correção. **Não avançar para deploy.**
Se APROVADO COM RESSALVAS: listar ressalvas e perguntar ao desenvolvedor se deseja prosseguir assim mesmo.
Se APROVADO: sugerir `/arkan.deploy`.

**Decisão do desenvolvedor** (obrigatória):
- "Aprovar e prosseguir para deploy"
- "Reprovar — corrigir bloqueadores primeiro"
- "Aprovar com ressalvas registradas"

Registrar decisão no `## Resultado do QA` do relatório.

### Fase 7 — Finalização

1. Garantir que `qa-report.md` está salvo em `$FEATURE_DIR/08-qa/qa-report.md`
2. Verificar PÓS-CONDIÇÕES: `.arkan/scripts/check-prerequisites.sh --pos --command .claude/commands/arkan.qa.md`
3. Reportar ao desenvolvedor:
   - Decisão registrada
   - Se aprovado: próximo passo `/arkan.deploy`
   - Se reprovado: lista de bloqueadores a corrigir

## Guidelines

- Documentação em **PT-BR**
- **Bloqueador** = qualquer item que impede uso seguro em produção; tudo o mais é ressalva
- Invariantes e Constitution são invioláveis — violação é sempre bloqueador CRÍTICO
- Verificação deve ser baseada em código real (lido via o indexador de código declarado em `.arkan/memory/stack.md`/Read) — não em presunção
- Tasks `[ ]` de P1 são sempre bloqueadores; tasks `[ ]` de P2+ são ressalvas
- Se o indexador de código declarado em `.arkan/memory/stack.md` não estiver disponível: verificar com base em arquivos lidos diretamente, registrar limitação
- Decisão final de Go/No-Go é sempre do desenvolvedor (Constituição, Princípio VIII)
