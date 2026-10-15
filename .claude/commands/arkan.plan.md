---
description: "Arkan fase 04 — Plano de implementação: transforma spec em arquitetura técnica com ADRs, modelo de dados e contratos. Produz plan.md aprovado pelo desenvolvedor."
mode: geracao
fase: 04-architecture
nivel: feature
tecnica: "Tree-of-Thought + Chain-of-Thought + Structured Output + Adversarial Prompting"
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/check-prerequisites.sh
arquivo: .arkan/memory/constitution.md
arquivo: .arkan/templates/04-architecture/plan-template.md
campo-obrigatorio: ## Requirements in $FEATURE_DIR/03-spec/spec.md

## PÓS-CONDIÇÕES

arquivo: $FEATURE_DIR/04-architecture/plan.md
campo-obrigatorio: ## ADRs in $FEATURE_DIR/04-architecture/plan.md
campo-obrigatorio: ## Dependências e Interfaces in $FEATURE_DIR/04-architecture/plan.md

## Outline

O texto após `/arkan.plan` é opcional — contexto adicional para a geração. A feature é inferida da branch atual.

### Fase 0 — Setup (automático)

1. Verificar pré-condições: `.arkan/scripts/check-prerequisites.sh --json --command .claude/commands/arkan.plan.md`
   - Se falhar: exibir lista de falhas e **parar**. Não prosseguir sem pré-condições satisfeitas.
2. Definir `FEATURE_DIR` a partir do JSON retornado pelo script (campo `FEATURE_DIR`)
3. Registrar: branch atual, caminho da feature, nome inferido

### Fase 1 — Carregamento de Contexto (sem interação)

Carregar silenciosamente:

**Artefatos da feature**:
- Ler `$FEATURE_DIR/03-spec/spec.md` — extrair user stories, FRs, NFRs, Key Entities, Invariantes
- Ler `$FEATURE_DIR/01-discovery/ideacao.md` — extrair `## Decisões Tomadas` (fundamentação arquitetural)
- Se `$FEATURE_DIR/status.md` existe: ler `projeto:` e `fase-atual:`

**Memória do projeto**:
- Ler `.arkan/memory/constitution.md` — princípios core I-VIII (verification table obrigatória no plan)
- Ler `.arkan/projects/<projeto>/constitution.md` — princípios do projeto P1..Pn vigentes (segunda tabela obrigatória no Constitution Check; listar todos, marcando N/A com justificativa quando não aplicável)
- Ler `.arkan/memory/stack.md` — linguagem, frameworks, banco de dados, restrições de plataforma
- Ler `.arkan/memory/glossario.md` — entidades e definições canônicos

**Template**:
- Ler `.arkan/templates/04-architecture/plan-template.md` — estrutura e seções obrigatórias

**Code Intelligence** (cascata — usar a primeira disponível):

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

1. **arkan-kb MCP** (preferencial):
   - `mcp__arkan-kb__query({query: "<tema da feature>"})` — encontrar símbolos e execution flows (ou busca por texto, se não houver indexador)
   - `mcp__arkan-kb__context({name: "<entidade>"})` — definição; confirme callers e conexões no próprio indexador, dependências (ou busca por texto, se não houver indexador)
   - `mcp__arkan-kb__impact({target: "<símbolo>", direction: "upstream"})` — blast radius (ou busca por texto, se não houver indexador)
   - `mcp__arkan-kb__audit_coverage()` — gaps spec↔código (ou busca por texto, se não houver indexador)
2. **Grep/Glob** (fallback final): buscar keywords nos diretórios de código e de migrações declarados em `.arkan/memory/stack.md`

Se impact retornar HIGH/CRITICAL: alertar o desenvolvedor **antes** de incluir a modificação no plano

### Fase 2 — Geração do Plano (Agentes)

Criar `$FEATURE_DIR/04-architecture/plan.md` a partir do template.

**Exibir cabeçalho antes de cada resposta**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  FASE 04 — Architecture  ·  MODO: GERAÇÃO
Agente: [nome do agente atual]  ·  Step: [nome do step]
Ação esperada: [o que o desenvolvedor deve fazer agora]
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Agente 1 — Architect**:

> Agente: Architect → .arkan/agents/04-plan/architect.md

**Instrução**: Ler `.arkan/agents/04-plan/architect.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: `spec.md`, `ideacao.md` (Decisões Tomadas), `constitution.md`, `stack.md`, `glossario.md`, caminhos via o indexador de código declarado em `.arkan/memory/stack.md` (quando disponível).

**Agente 2 — Data Modeler**:

> Agente: Data Modeler → .arkan/agents/04-plan/data-modeler.md

**Instrução**: Ler `.arkan/agents/04-plan/data-modeler.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: Key Entities da spec, `ideacao.md` (decisões de design), `stack.md`.

**Agente 3 — API Designer**:

> Agente: API Designer → .arkan/agents/04-plan/api-designer.md

**Instrução**: Ler `.arkan/agents/04-plan/api-designer.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: FRs e NFRs da spec, `## Dependências e Interfaces` do plan, `stack.md`.

**Agente 4 — Security Analyst**:

> Agente: Security Analyst → .arkan/agents/04-plan/security-analyst.md

**Instrução**: Ler `.arkan/agents/04-plan/security-analyst.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: plano completo dos agentes 1-3, `spec.md` (Invariantes), `constitution.md`.

**Mapa de Agentes por Fase**:

- Tabela: Fase | Nível | Modo | Command | Agente(s) | Técnica(s) | Artefato de Saída
- Listar todos os commands do workflow Arkan que esta feature ativa

### Fase 3 — Apresentação e Aprovação

1. Exibir resumo do plano gerado:
   - Número de ADRs
   - Arquivos a criar/modificar
   - State machines geradas (se houver)
   - Alertas de impacto HIGH/CRITICAL (se houver)

2. Apresentar ao desenvolvedor para aprovação:
   - "Plano gerado. Há alguma decisão arquitetural que deseja revisar?"
   - Listar ADRs e aguardar confirmação ou ajuste

3. Para cada ajuste solicitado:
   - Aplicar no plan.md (e data-model.md se relevante)
   - Registrar como nota no ADR afetado: "Ajustado em [data]: [motivo]"
   - **Princípio VIII**: agente propõe, desenvolvedor decide

4. Após aprovação: confirmar que plan.md tem `## ADRs` e `## Dependências e Interfaces` preenchidos

### Fase 4 — Finalização

1. Garantir que todos os artefatos estão salvos:
   - `$FEATURE_DIR/04-architecture/plan.md` (obrigatório)
   - `$FEATURE_DIR/04-architecture/data-model.md` (se entidades)
   - `$FEATURE_DIR/04-architecture/contracts/` (se interfaces)
   - `$FEATURE_DIR/04-architecture/quickstart.md` (sempre)
2. Verificar PÓS-CONDIÇÕES: `.arkan/scripts/check-prerequisites.sh --pos --command .claude/commands/arkan.plan.md`
3. Reportar ao desenvolvedor:
   - Caminhos dos artefatos gerados
   - ADRs criados (título + status)
   - Próximo passo: `/arkan.tasks`

## Guidelines

- Documentação em **PT-BR** — nenhuma seção em inglês
- Plano DEVE ser implementável — sem hand-waving ou "a definir depois"
- Referenciar **caminhos e símbolos reais** — não inventar paths que não existem no repo
- Preferir reutilizar padrões existentes (identificados via o indexador de código declarado em `.arkan/memory/stack.md`) antes de propor novos
- ADRs devem incluir alternativas descartadas com justificativa — não só o que foi escolhido
- Constitution Check PASS é obrigatório para prosseguir (Constituição, Princípio II)
- Se o indexador de código declarado em `.arkan/memory/stack.md` não estiver disponível: operar com base na spec + stack.md, com nota ao desenvolvedor e sem inventário de impacto
- Nunca finalizar sem aprovação explícita do desenvolvedor (Constituição, Princípio VIII)
