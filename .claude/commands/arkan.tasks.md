---
description: "Arkan fase 06 — Planejamento de tasks: decompõe plano técnico em lista ordenada de tasks implementáveis. Produz tasks.md aprovado pelo desenvolvedor."
mode: geracao
fase: 06-planning
nivel: feature
tecnica: "Decomposition Prompting + Plan-and-Solve + Tree-of-Thought"
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/check-prerequisites.sh
arquivo: .arkan/memory/constitution.md
arquivo: .arkan/templates/06-planning/tasks-template.md
campo-obrigatorio: ## Sequência de Implementação in $FEATURE_DIR/04-architecture/plan.md

## PÓS-CONDIÇÕES

arquivo: $FEATURE_DIR/06-planning/tasks.md
campo-obrigatorio: ## Fase 1 in $FEATURE_DIR/06-planning/tasks.md

## Outline

O texto após `/arkan.tasks` é opcional — instrução para atualizar tasks existentes ou focar em um subconjunto. A feature é inferida da branch atual.

### Fase 0 — Setup (automático)

1. Verificar pré-condições: `.arkan/scripts/check-prerequisites.sh --json --command .claude/commands/arkan.tasks.md`
   - Se falhar: exibir lista de falhas e **parar**. Não prosseguir sem pré-condições satisfeitas.
2. Definir `FEATURE_DIR` a partir do JSON retornado pelo script (campo `FEATURE_DIR`)
3. Verificar se `$FEATURE_DIR/06-planning/tasks.md` já existe:
   - Se sim: modo **atualização** — preservar tasks `[x]` concluídas, regenerar apenas `[ ]` abertas ou adicionar novas
   - Se não: modo **criação** — gerar do zero

### Fase 1 — Carregamento de Contexto (sem interação)

Carregar silenciosamente:

**Artefatos da feature** (obrigatórios):
- Ler `$FEATURE_DIR/04-architecture/plan.md` — extrair `## Sequência de Implementação`, `## Estrutura do Projeto`, `## ADRs`, `## Dependências e Interfaces`
- Ler `$FEATURE_DIR/03-spec/spec.md` — extrair user stories com prioridades, Invariantes

**Artefatos da feature** (complementares, se existirem):
- `$FEATURE_DIR/04-architecture/data-model.md` — entidades, campos, state machines
- `$FEATURE_DIR/04-architecture/contracts/` — interfaces a implementar
- `$FEATURE_DIR/04-architecture/research.md` — decisões técnicas, oportunidades de reuso
- `$FEATURE_DIR/04-architecture/quickstart.md` — critério de verificação do MVP

**Template**:
- Ler `.arkan/templates/06-planning/tasks-template.md` — formato e estrutura de fases

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

**Indexador de código** (declarado em `.arkan/memory/stack.md`, quando disponível):
- Para cada entidade/conceito-chave extraído do plan:
  busca por tema no indexador (ou busca por texto, se não houver indexador) — encontrar execution flows relacionados
- Para símbolos que serão **modificados** (não criados):
  busca por símbolo no indexador (ou busca por texto, se não houver indexador) — identificar arquivo exato e símbolos relacionados
- Usar paths retornados pelo indexador de código nos campos `File:` das tasks
- Se o indexador de código declarado em `.arkan/memory/stack.md` não estiver disponível: inferir paths a partir da `## Estrutura do Projeto` do plan

### Fase 2 — Geração das Tasks (Agentes)

Criar `$FEATURE_DIR/06-planning/tasks.md` a partir do template.

**Exibir cabeçalho antes de cada resposta**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  FASE 06 — Planning  ·  MODO: GERAÇÃO
Agente: [nome do agente atual]  ·  Step: [nome do step]
Ação esperada: [o que o desenvolvedor deve fazer agora]
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Agente 1 — Task Decomposer**:

> Agente: Task Decomposer → .arkan/agents/06-tasks/task-decomposer.md

**Instrução**: Ler `.arkan/agents/06-tasks/task-decomposer.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: `plan.md` (Sequência de Implementação, Estrutura do Projeto, ADRs), `spec.md` (user stories com prioridades, Invariantes), template de tasks, paths reais do codebase (via o indexador de código declarado em `.arkan/memory/stack.md` ou Estrutura do Projeto).

**Agente 2 — Risk Analyzer**:

> Agente: Risk Analyzer → .arkan/agents/06-tasks/risk-analyzer.md

**Instrução**: Ler `.arkan/agents/06-tasks/risk-analyzer.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: lista de tasks gerada pelo Task Decomposer.

### Fase 3 — Apresentação e Aprovação

1. Exibir resumo das tasks geradas:
   - Número total de tasks por fase
   - Tasks marcadas `[P]` (paralelas)
   - Tasks com `[NEEDS PATH]` para revisão do desenvolvedor (se houver)
   - Estimativa de fases bloqueantes vs paralelas

2. Apresentar ao desenvolvedor para aprovação:
   - "Tasks geradas. Deseja ajustar alguma fase ou adicionar tasks não cobertas pelo plano?"

3. Para cada ajuste solicitado:
   - Adicionar, remover ou mover tasks conforme instrução
   - Renumerar IDs se necessário (manter sequência TXXX sem gaps)
   - **Princípio VIII**: agente propõe decomposição, desenvolvedor valida e ajusta

4. Verificar que todas as user stories P1 da spec têm ao menos uma task

### Fase 4 — Finalização

1. Garantir que `tasks.md` está completo e salvo em `$FEATURE_DIR/06-planning/tasks.md`
2. Verificar PÓS-CONDIÇÕES: `.arkan/scripts/check-prerequisites.sh --pos --command .claude/commands/arkan.tasks.md`
3. Reportar ao desenvolvedor:
   - Caminho do arquivo gerado
   - Número de tasks por fase
   - Próximo passo: `/arkan.implement`

## Guidelines

- Documentação em **PT-BR** — nenhuma seção em inglês
- Tasks devem ser **atômicas** e **independentemente verificáveis**
- Preferir tasks menores sobre tasks maiores — granularidade favorece checkpoints
- Campo `File:` é **obrigatório** — nunca omitir; inferir do plan se o indexador de código declarado em `.arkan/memory/stack.md` não estiver disponível
- Paralelismo `[P]` deve ser real — apenas quando arquivos diferentes e sem dependência de estado
- Testes são **opcionais** — incluir apenas se explicitamente solicitado na spec
- Modo atualização: nunca remover tasks `[x]` concluídas — apenas adicionar ou ajustar `[ ]` abertas
- Se o indexador de código declarado em `.arkan/memory/stack.md` não estiver disponível: operar com base no plan + estrutura de arquivos inferida, com nota ao desenvolvedor
