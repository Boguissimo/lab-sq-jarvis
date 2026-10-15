---
description: "Arkan fase 02 — Proposta comercial/técnica: transforma ideação em proposta com escopo, estimativa e Go/No-Go. Produz proposta.md aprovado pelo desenvolvedor."
mode: assistencia
fase: 02-proposta
nivel: feature
tecnica: "Decomposition Prompting + Plan-and-Solve + Structured Output"
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/check-prerequisites.sh
arquivo: .arkan/memory/constitution.md
arquivo: .arkan/templates/02-proposta/proposta-template.md
campo-obrigatorio: ## Síntese in $FEATURE_DIR/01-discovery/ideacao.md

## PÓS-CONDIÇÕES

arquivo: $FEATURE_DIR/02-proposta/proposta.md
campo-obrigatorio: ## Go/No-Go in $FEATURE_DIR/02-proposta/proposta.md

## Outline

O texto após `/arkan.proposta` é opcional — contexto adicional (ex: "cliente precisa de budget até sexta"). A feature é inferida da branch atual.

### Fase 0 — Setup (automático)

1. Verificar pré-condições: `.arkan/scripts/check-prerequisites.sh --json --command .claude/commands/arkan.proposta.md`
   - Se falhar: exibir lista de falhas e **parar**
2. Definir `FEATURE_DIR` a partir do JSON retornado

### Fase 1 — Carregamento de Contexto (sem interação)

Carregar silenciosamente:
- `$FEATURE_DIR/01-discovery/ideacao.md` — especialmente `## Síntese`, `## Decisões Tomadas`
- `$FEATURE_DIR/03-spec/spec.md` (se existe) — user stories, FRs, critérios de sucesso
- `.arkan/memory/stack.md` — complexidade técnica, restrições de plataforma (impacta estimativa)
- `.arkan/memory/constitution.md` — princípios relevantes

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

**Indexador de código** (declarado em `.arkan/memory/stack.md`, quando disponível):
- Busca por tema no indexador (ou busca por texto, se não houver indexador) — identificar código existente reutilizável
- Reutilização de código existente reduz estimativa → incluir no cálculo

### Fase 2 — Geração da Proposta

**Exibir cabeçalho antes de cada resposta**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  FASE 02 — Proposta  ·  MODO: ASSISTÊNCIA
Agente: [Proposal Writer / Estimator]  ·  Step: [nome do step]
Ação esperada: [o que o desenvolvedor deve fazer agora]
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Agente 1 — Proposal Writer**:

> Agente: Proposal Writer → .arkan/agents/transversal/proposal-writer.md

**Instrução**: Ler `.arkan/agents/transversal/proposal-writer.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: `## Síntese` e `## Decisões Tomadas` da ideacao.md, user stories da spec.md (se existir), `stack.md`.

**Agente 2 — Estimator**:

> Agente: Estimator → .arkan/agents/transversal/estimator.md

**Instrução**: Ler `.arkan/agents/transversal/estimator.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: escopo aprovado pelo Proposal Writer, `stack.md`, código reutilizável via o indexador de código declarado em `.arkan/memory/stack.md` (se disponível).

**Modelo de cobrança** `## 3.`:
- Perguntar ao desenvolvedor qual modalidade se aplica (Fixed / T&M / Retainer / Interno)
- Preencher valores conforme resposta
- **Princípio VIII**: agente não decide valores — apenas estrutura a seção

**Riscos e dependências** `## 4.`:
- Identificar riscos da síntese + incertezas da estimativa
- Classificar por probabilidade e impacto

### Fase 3 — Go/No-Go

Apresentar proposta completa ao desenvolvedor:
- Resumo: escopo + estimativa total + principais riscos
- Perguntar: "Deseja prosseguir com a feature? (Go/No-Go)"

Preencher `## Go/No-Go` com a decisão e data.

**Se No-Go**: registrar motivo e sugerir `/arkan.ideacao` para reavaliar escopo.
**Se Go**: registrar condições acordadas e sugerir próximo passo.

### Fase 4 — Finalização

1. Garantir que `proposta.md` está salvo em `$FEATURE_DIR/02-proposta/proposta.md`
2. Verificar PÓS-CONDIÇÕES: `.arkan/scripts/check-prerequisites.sh --pos --command .claude/commands/arkan.proposta.md`
3. Reportar ao desenvolvedor:
   - Decisão Go/No-Go registrada
   - Se Go: próximo passo `/arkan.spec`

## Guidelines

- Documentação em **PT-BR**
- Estimativas com **ranges** — estimativas pontuais fingem precisão que não existe
- Premissas devem ser **explícitas** — estimativa sem premissa é garantia de surpresa
- Escopo deve ser **verificável** — cada item de escopo tem critério de "está feito ou não está"
- Valores de cobrança são fornecidos pelo desenvolvedor — agente estrutura, não decide
- Se o indexador de código declarado em `.arkan/memory/stack.md` não estiver disponível: estimar sem contexto de reuso, com nota ao desenvolvedor
