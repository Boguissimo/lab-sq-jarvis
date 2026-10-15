---
description: "Arkan nível projeto — fases 01-02: transforma descrição de sistema complexo em feature-map.md aprovado pelo desenvolvedor, com decomposição proposta pelo agente."
mode: assistencia
fase: 01-discovery
nivel: projeto
tecnica: "Socratic Prompting + ReAct + Tree-of-Thought + Decomposition"
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/create-project.sh
arquivo: .arkan/scripts/check-prerequisites.sh
arquivo: .arkan/scripts/update-status.sh
arquivo: .arkan/memory/constitution.md
arquivo: .arkan/templates/01-discovery/briefing-template.md
arquivo: .arkan/templates/01-discovery/vision-template.md
arquivo: .arkan/templates/02-proposta/feature-map-template.md

## PÓS-CONDIÇÕES

arquivo: .arkan/project/status.md
campo-obrigatorio: ## Features Propostas in .arkan/project/02-proposal/feature-map.md

## Outline

O texto após `/arkan.projeto` é a descrição do sistema complexo. Se vazio, pergunte ao desenvolvedor.

### Fase 0 — Setup (automático)

1. Verificar pré-condições: `.arkan/scripts/check-prerequisites.sh --json --command .claude/commands/arkan.projeto.md`
   - Se falhar: exibir lista de falhas e **parar**
2. Executar: `.arkan/scripts/create-project.sh --json --name "nome-inferido" "Descrição"`
   - **IMPORTANTE**: executar este script apenas **uma vez** por projeto
   - Se `ALREADY_EXISTS: true`: prosseguir com o projeto existente (modo retomada)
   - Se `ALREADY_EXISTS: false`: novo projeto iniciado
3. Definir `PROJECT_DIR` como `.arkan/project`
4. Exibir ao desenvolvedor: status atual do projeto (se retomada, resumir o que já existe)

### Fase 1 — Investigação Automática (sem interação)

Antes do debate, investigar silenciosamente o que já existe:

**Memória do projeto**:
- Ler `.arkan/memory/constitution.md` — princípios a respeitar na decomposição
- Ler `.arkan/memory/glossario.md` — termos relevantes
- Ler `.arkan/memory/stack.md` — restrições tecnológicas que impactam a decomposição

**Projeto existente** (se retomada):
- Ler `$PROJECT_DIR/01-discovery/briefing.md` (se existe) — problema já documentado
- Ler `$PROJECT_DIR/01-discovery/vision.md` (se existe) — prioridades já acordadas
- Ler `$PROJECT_DIR/02-proposal/feature-map.md` (se existe) — decomposição anterior

**Features já existentes**:
- Escanear `.arkan/features/` — quais features já foram criadas com `projeto:` este projeto
- Verificar status de cada feature existente em `status.md`

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

**Indexador de código** (declarado em `.arkan/memory/stack.md`, quando disponível):
- Busca por tema no indexador (ou busca por texto, se não houver indexador) — encontrar execução flows e módulos relacionados
- Usar achados para informar a decomposição (evitar reinventar o que já existe)

**Consolidar achados**:
- O que já está implementado como features
- O que ainda não foi decomposto
- Restrições ou dependências técnicas já identificadas

### Fase 2 — Briefing (Fase 01 do projeto)

> Agente: Intake Agent → .arkan/agents/transversal/intake-agent.md

**Instrução**: Ler `.arkan/agents/transversal/intake-agent.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: descrição do sistema, `constitution.md`, `glossario.md`, `stack.md`, achados da Fase 1, templates (`briefing-template.md`, `vision-template.md`).

Após aprovação: `.arkan/scripts/update-status.sh --file $PROJECT_DIR/status.md --field fase-atual --value 02-proposal`

**Exibir cabeçalho antes de cada resposta**:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  NÍVEL PROJETO  ·  FASE 01 — Discovery  ·  MODO: ASSISTÊNCIA
Agente: Intake Agent  ·  Step: [nome do step atual]
Ação esperada: [o que o desenvolvedor deve fazer agora]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Fase 3 — Decomposição em Features (Fase 02 do projeto)

> Agente: Proposal Writer → .arkan/agents/transversal/proposal-writer.md

**Instrução**: Ler `.arkan/agents/transversal/proposal-writer.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

> Agente: Estimator → .arkan/agents/transversal/estimator.md

**Instrução**: Ler `.arkan/agents/transversal/estimator.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar os agentes, injetar: `vision.md` aprovado, features já existentes (`.arkan/features/`), template `feature-map-template.md`.

**Apresentar ao desenvolvedor**: N features, distribuição P1/P2/P3, sequência sugerida. Aguardar aprovação ou ajuste; registrar ajustes no `## Histórico de Revisões`.

**Após aprovação final**:
- `.arkan/scripts/update-status.sh --file $PROJECT_DIR/status.md --field status --value features-definidas`
- `.arkan/scripts/update-status.sh --file $PROJECT_DIR/status.md --field fase-atual --value 02-proposal`

### Fase 4 — Gate Bloqueante (se projeto já tinha features)

Se durante a sessão for detectado que:
- Uma feature já iniciada (`em-andamento`) contradiz a decomposição proposta
- O `feature-map.md` anterior foi alterado de forma incompatível

**Não alterar silenciosamente** — apresentar ao desenvolvedor as 3 opções:

```
⚠️  GATE: Inconsistência detectada entre feature-map e feature existente.

Feature afetada: [NNN-nome-feature]
Inconsistência: [descrição]

Opções:
  A) Adaptar aqui — ajustar o feature-map para refletir o que já foi decidido na feature
  B) Marcar origem para revisão — sinalizar no feature-map que esta entrada precisa ser revisitada
  C) Registrar e prosseguir — documentar a divergência e continuar com o estado atual

Qual opção? (A/B/C)
```

### Fase 5 — Finalização

1. Garantir que todos os artefatos estão salvos:
   - `$PROJECT_DIR/01-discovery/briefing.md`
   - `$PROJECT_DIR/01-discovery/vision.md`
   - `$PROJECT_DIR/02-proposal/feature-map.md`
   - `$PROJECT_DIR/status.md` com `status: features-definidas`
2. Verificar PÓS-CONDIÇÕES: `.arkan/scripts/check-prerequisites.sh --pos --command .claude/commands/arkan.projeto.md`
3. Reportar ao desenvolvedor:
   - Features P1 (MVP): lista com nomes
   - Próximo passo: `/arkan.ideacao` para a primeira feature P1
   - Como retomar: invocar `/arkan.projeto` novamente para revisar o feature-map

## Guidelines

- Documentação em **PT-BR**
- **O agente propõe a decomposição** — o desenvolvedor não precisa listar as features; o agente as infere do briefing e vision
- Cada feature proposta deve ser autônoma: se implementada sozinha, entrega valor
- Dependências entre features devem ser mínimas e justificadas — evitar criar coupling artificial
- Não criar mais features do que o necessário — preferir features menores e bem definidas a features grandes e vagas
- Retorno entre fases é sempre explícito via gate bloqueante — nunca automático (Constituição, Restrições)
- Se o indexador de código declarado em `.arkan/memory/stack.md` não estiver disponível: operar com base no briefing/vision + memória, com nota ao desenvolvedor
- Nunca avançar de fase sem aprovação explícita do desenvolvedor (Constituição, Princípio VIII)
