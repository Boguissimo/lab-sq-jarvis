---
description: "Arkan fase 07 — Implementação: executa tasks uma a uma com contexto completo da feature, validando contra spec e invariantes. Pergunta se continua após cada task."
mode: geracao
fase: 07-implementation
nivel: feature
tecnica: "ReAct + Agent Loops + FLARE + Self-Refine + Adversarial Prompting"
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/check-prerequisites.sh
arquivo: .arkan/memory/constitution.md
campo-obrigatorio: ## Fase 1 in $FEATURE_DIR/06-planning/tasks.md

## PÓS-CONDIÇÕES

campo-obrigatorio: ## Fase 1 in $FEATURE_DIR/06-planning/tasks.md

## Outline

O texto após `/arkan.implement` é opcional — especifica qual task ou fase iniciar (ex: "T005", "Fase 2"). Se vazio, inicia pela primeira task incompleta.

### Fase 0 — Setup (automático)

1. Verificar pré-condições: `.arkan/scripts/check-prerequisites.sh --json --require-tasks --include-tasks --command .claude/commands/arkan.implement.md`
   - Se falhar: exibir lista de falhas e **parar**
2. Definir `FEATURE_DIR` e `TASKS_FILE` a partir do JSON retornado

### Fase 1 — Carregamento de Contexto Completo (sem interação)

Carregar silenciosamente **antes de implementar qualquer task**:

**Obrigatórios**:
- Ler `$FEATURE_DIR/06-planning/tasks.md` — lista completa de tasks e estado atual
- Ler `$FEATURE_DIR/04-architecture/plan.md` — estrutura de projeto, ADRs, interfaces
- Ler `$FEATURE_DIR/03-spec/spec.md` — user stories, FRs, NFRs, **Invariantes**

**Complementares** (se existirem):
- `$FEATURE_DIR/04-architecture/data-model.md` — entidades, campos, state machines
- `$FEATURE_DIR/04-architecture/contracts/` — interfaces a implementar
- `$FEATURE_DIR/04-architecture/inventario-existente.md` — arquivos MODIFICAR / CRIAR / NAO_TOCAR
- `$FEATURE_DIR/04-architecture/research.md` — decisões técnicas e oportunidades de reuso
- `$FEATURE_DIR/04-architecture/quickstart.md` — cenários de verificação

**Construir mapa de contexto**:
- `INVENTARIO_NAO_TOCAR`: lista de arquivos marcados `NAO_TOCAR` (se inventário existe)
- `INVARIANTES`: lista de invariantes da spec (para validação pós-implementação)
- `INTERFACES_EXPOSTAS`: contratos que NÃO mudar (do plan.md)
- `PROXIMA_TASK`: primeira task com `- [ ]` na lista

### Fase 2 — Loop de Implementação

**Exibir cabeçalho antes de cada task**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  FASE 07 — Implementação  ·  MODO: GERAÇÃO
Agente: Implementer  ·  Task: [ID] — [Descrição]
Ação esperada: revisar implementação e confirmar continuar / parar / pular
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Para cada task**:

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

**2a. Entender a task**:
- Ler descrição completa e `File:` indicado
- Verificar contexto arquitetural no plan.md (ADR relacionado, se houver)
- Explorar codebase para padrões existentes (cascata: `mcp__arkan-kb__query` (ou busca por texto, se não houver indexador) → Grep/Glob)

**2b. Análise de impacto** (apenas para tasks que **modificam** símbolos existentes):
- Cascata: `mcp__arkan-kb__impact({target: "<símbolo>", direction: "upstream"})` (ou busca por texto, se não houver indexador) → análise manual via Grep
- Se impacto HIGH ou CRITICAL (>15 símbolos ou caminho crítico):
  - Exibir blast radius ao desenvolvedor
  - **PARAR e perguntar**: "Análise de impacto indica risco HIGH/CRITICAL. Prosseguir? (sim/não)"
- Se impacto LOW/MEDIUM: registrar símbolos afetados e prosseguir
- Pular esta etapa para tasks que **apenas criam** novos arquivos

**2c. Verificar NAO_TOCAR** (antes de qualquer edição):
- Se o arquivo alvo está em `INVENTARIO_NAO_TOCAR`:
  - **PARAR**: "Este arquivo está marcado NAO_TOCAR no inventário. Prosseguir? (sim/não)"
  - Só editar com confirmação explícita

**2d. Agente Implementer**:

> Agente: Implementer → .arkan/agents/07-implement/implementer.md

**Instrução**: Ler `.arkan/agents/07-implement/implementer.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: arquivo atual a modificar, task completa (descrição, File:, ADR), padrões do codebase, `contracts/`, `stack.md`.

**2e. Agente Reviewer/Critic**:

> Agente: Reviewer/Critic → .arkan/agents/07-implement/reviewer-critic.md

**Instrução**: Ler `.arkan/agents/07-implement/reviewer-critic.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: código implementado na etapa 2d, `spec.md` (cenários, Invariantes, State Machines), `plan.md` (interfaces expostas), `INVENTARIO_NAO_TOCAR`.

**2f. Anotar código com rastreabilidade** (após implementação aprovada pelo reviewer):
- Para cada função/classe/arquivo **criado ou significativamente modificado** nesta task:
  - Adicionar comentário `// @@TXXX [USN] descricao` no topo da função/classe
  - Formato: `// @@T003 [US1] Habilitar showBack e onBack em todos os steps`
  - Se task referencia FRs: incluir `[FR-NNN]` — ex: `// @@T011 [US3] [FR-011] Cleanup em cascata`
- Cascata de aplicação: `mcp__arkan-kb__annotate` (preferencial) → inserção manual via Edit, se não houver indexador
- **Não anotar**: imports, tipos triviais, ou arquivos com apenas 1 linha alterada
- Anotações permitem ao arkan-kb linkar spec↔código automaticamente via `audit_coverage`

**2g. Marcar task concluída**:

- Se todas as verificações passaram: atualizar `tasks.md` — `- [ ]` → `- [x]`
- Reportar brevemente o que foi implementado

**2h. Perguntar ao desenvolvedor**:
```
Task [ID] concluída. O que deseja fazer?
  A) Continuar — próxima task: [ID+1] [descrição]
  B) Parar — revisar o que foi feito
  C) Pular — ir para task específica (informe o ID)
```
- Aguardar resposta antes de prosseguir (Constituição, Princípio VIII)

### Fase 3 — Checkpoint de Fase

Quando todas as tasks de uma fase são concluídas, exibir checkpoint antes de iniciar a próxima:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHECKPOINT: [Nome da Fase] — todas as tasks completas
[Resumo do que foi implementado]
[Se fase de Fundação: lembrar que user stories agora podem começar]
Próxima fase: [Nome] — [N] tasks
Continuar? (sim/não)
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Fase 4 — Quando Bloqueada

Se uma task não pode ser implementada:
1. Explicar o bloqueio claramente (arquivo não encontrado, dependência faltando, contrato ambíguo)
2. Sugerir alternativas (pular para outra task, ajustar o plan, criar artefato faltante)
3. **Não tentar contornar o bloqueio com workarounds** — reportar e aguardar instrução

### Fase 5 — Finalização (quando todas as tasks estão `[x]`)

1. Exibir resumo final:
   - Total de tasks implementadas
   - User stories completas
   - Tasks que ficaram pendentes (se houver) com motivo
2. Sugerir próximos passos:
   - `/arkan.alinhamento` — verificar conformidade spec↔código
   - `/arkan.qa` — se disponível

## Guidelines

- Implementar **UMA task por vez** — não acumular mudanças de múltiplas tasks
- Sempre **ler o arquivo atual** antes de modificar — nunca sobrescrever sem leitura prévia
- **Padrões existentes** têm prioridade sobre preferências do agente — consistência antes de elegância
- **PT-BR obrigatório** para nomes de variáveis, funções, comentários e documentação inline
- Atualizar `tasks.md` **após cada task** — não acumular
- Cascata de discovery: arkan-kb MCP (ou busca por texto, se não houver indexador) → Grep/Glob. Se nenhum disponível: implementar com base nos arquivos lidos, registrar que análise de impacto foi pulada
- Tasks `[P]` dentro de uma fase: podem ser implementadas em qualquer ordem, mas ainda uma por vez
- Nunca avançar de fase sem aprovação explícita (checkpoint) do desenvolvedor
