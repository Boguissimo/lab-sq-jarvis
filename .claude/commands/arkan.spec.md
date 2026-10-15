---
description: "Arkan fase 03 — Especificação de feature: transforma ideação em spec formal com user stories, requisitos e invariantes. Produz spec.md aprovado pelo desenvolvedor."
mode: geracao
fase: 03-spec
nivel: feature
tecnica: "Few-Shot Prompting + Structured Output + BDD"
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/check-prerequisites.sh
arquivo: .arkan/memory/constitution.md
arquivo: .arkan/templates/03-spec/spec-template.md
campo-obrigatorio: ## Síntese in $FEATURE_DIR/01-discovery/ideacao.md

## PÓS-CONDIÇÕES

arquivo: $FEATURE_DIR/03-spec/spec.md
campo-obrigatorio: ## Requirements in $FEATURE_DIR/03-spec/spec.md
campo-obrigatorio: ## Invariantes in $FEATURE_DIR/03-spec/spec.md

## Outline

O texto após `/arkan.spec` é opcional — contexto adicional para a geração. A feature é inferida da branch atual.

### Fase 0 — Setup (automático)

1. Verificar pré-condições: `.arkan/scripts/check-prerequisites.sh --json --command .claude/commands/arkan.spec.md`
   - Se falhar: exibir lista de falhas e **parar**. Não prosseguir sem pré-condições satisfeitas.
2. Definir `FEATURE_DIR` a partir do JSON retornado pelo script (campo `FEATURE_DIR`)
3. Registrar: branch atual, caminho da feature, nome inferido

### Fase 1 — Carregamento de Contexto (sem interação)

Carregar silenciosamente:

**Artefatos da feature**:
- Ler `$FEATURE_DIR/01-discovery/ideacao.md` — extrair especialmente `## Síntese`, `## Decisões Tomadas`, `## Dúvidas Resolvidas`
- Se `$FEATURE_DIR/status.md` existe: ler campos `projeto:` e `fase-atual:`

**Memória do projeto**:
- Ler `.arkan/memory/constitution.md` — princípios I-VIII (invariantes obrigatórios)
- Ler `.arkan/memory/glossario.md` — termos e definições canônicos
- Ler `.arkan/memory/stack.md` — restrições tecnológicas para NFRs

**Template**:
- Ler `.arkan/templates/03-spec/spec-template.md` — estrutura e instruções de cada seção

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

**Indexador de código** (declarado em `.arkan/memory/stack.md`, quando disponível):
- Busca por tema no indexador (ou busca por texto, se não houver indexador) — encontrar entidades e contratos existentes
- Para entidades identificadas na síntese: busca por símbolo no indexador (ou busca por texto, se não houver indexador) — entender campos e relacionamentos

**Consolidar antes de gerar**:
- User stories mencionadas explicitamente na síntese
- Entidades e seus campos (da síntese + indexador de código, quando disponível)
- Restrições e decisões (de `## Decisões Tomadas`)
- Dúvidas ainda abertas (de `## Dúvidas Resolvidas`) — marcar como `[NEEDS CLARIFICATION]` apenas se críticas

### Fase 2 — Geração da Spec (Agentes)

Criar `$FEATURE_DIR/03-spec/spec.md` a partir do template. Preencher seção por seção:

**Exibir cabeçalho antes de cada resposta**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  FASE 03 — Spec  ·  MODO: GERAÇÃO
Agente: Spec Writer  ·  Step: [nome do step atual]
Ação esperada: [o que o desenvolvedor deve fazer agora]
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Agente 1 — Spec Writer**:

> Agente: Spec Writer → .arkan/agents/03-spec/spec-writer.md

**Instrução**: Ler `.arkan/agents/03-spec/spec-writer.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: `## Síntese` e `## Decisões Tomadas` da ideacao.md, template de spec, entidades via o indexador de código declarado em `.arkan/memory/stack.md` (quando disponível).

**Agente 2 — NFR Writer**:

> Agente: NFR Writer → .arkan/agents/03-spec/nfr-writer.md

**Instrução**: Ler `.arkan/agents/03-spec/nfr-writer.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: user stories geradas pelo Spec Writer, `stack.md`, `constitution.md`.

**Agente 3 — BDD Writer**:

> Agente: BDD Writer → .arkan/agents/03-spec/bdd-writer.md

**Instrução**: Ler `.arkan/agents/03-spec/bdd-writer.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: FRs gerados pelo NFR Writer, `constitution.md`, domínio da feature (da síntese da ideação).

**Agente 4 — Business Rules Analyst**:

> Agente: Business Rules Analyst → .arkan/agents/03-spec/business-rules-analyst.md

**Instrução**: Ler `.arkan/agents/03-spec/business-rules-analyst.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: spec gerada pelos agentes 1-3, `## Decisões Tomadas` da ideacao.md.

### Fase 3 — Apresentação e Aprovação

1. Exibir resumo da spec gerada:
   - Número de user stories e prioridades
   - Número de FRs e NFRs
   - Número de invariantes
   - Marcadores `[NEEDS CLARIFICATION]` abertos (se houver)

2. Apresentar ao desenvolvedor para aprovação:
   - **Se 0 marcadores abertos**: "Spec gerada. Deseja revisar alguma seção antes de prosseguir?"
   - **Se marcadores existem**: listar cada dúvida aberta e perguntar resolução antes de finalizar

3. Para cada `[NEEDS CLARIFICATION]` aberto:
   - Apresentar o contexto e opções disponíveis
   - Aguardar decisão do desenvolvedor
   - Aplicar decisão na spec (substituir marcador por texto definitivo)
   - Registrar em `## Clarifications` com data e decisão tomada
   - **Princípio VIII**: agente propõe opções, desenvolvedor decide

4. Após aprovação: garantir que nenhum `[NEEDS CLARIFICATION]` permanece aberto na spec final

### Fase 4 — Finalização

1. Garantir que `spec.md` está completo e salvo em `$FEATURE_DIR/03-spec/spec.md`
2. Verificar PÓS-CONDIÇÕES: `.arkan/scripts/check-prerequisites.sh --pos --command .claude/commands/arkan.spec.md`
3. Reportar ao desenvolvedor:
   - Caminho do arquivo gerado
   - Resumo das user stories (nome + prioridade)
   - Próximo passo: `/arkan.plan`

## Guidelines

- Documentação em **PT-BR** — nenhuma seção em inglês
- Spec foca em **O QUÊ** (comportamento) e **POR QUÊ** (valor), nunca em **COMO** (implementação)
- User stories devem ser independentes — cada uma entrega valor sem as outras
- Requisitos funcionais devem ser verificáveis — evitar linguagem vaga ("de forma eficiente", "quando necessário")
- **Definições normativas primeiro**: todo adjetivo de qualidade ou limiar usado em FR/NFR/SC deve ter entrada na tabela `## Definições normativas` (com número, enum ou condição verificável) ou valor inline; termo indefinido vira `[NEEDS CLARIFICATION]`
- Invariantes são contratos — não podem ser violados sem Clarification explícita. Formato `INV-NN` com campo **Teste:** obrigatório (comando/query/procedimento que detecta a violação — o QA herda este teste como método)
- Critérios de sucesso (SC-NNN) exigem **Instrumento:** (como medir em runtime) e **Baseline:** (valor atual ou "N/A — funcionalidade nova"); o ops-report da fase 10 executa estes instrumentos
- Se o indexador de código declarado em `.arkan/memory/stack.md` não estiver disponível: operar com base apenas na ideação + constitution, com nota ao desenvolvedor
- Nunca finalizar com marcadores `[NEEDS CLARIFICATION]` abertos (Constituição, Princípio III)
