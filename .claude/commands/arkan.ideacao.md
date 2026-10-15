---
description: "Arkan fase 01 — Ideação de feature: debate estruturado do problema até a síntese de escopo. Produz ideacao.md aprovado pelo desenvolvedor."
mode: assistencia
fase: 01-discovery
nivel: feature
tecnica: "Socratic Prompting + ReAct"
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/create-feature.sh
arquivo: .arkan/scripts/check-prerequisites.sh
arquivo: .arkan/memory/constitution.md

## PÓS-CONDIÇÕES

arquivo: $FEATURE_DIR/01-discovery/ideacao.md
campo-obrigatorio: ## Síntese in $FEATURE_DIR/01-discovery/ideacao.md
campo-obrigatorio: ## Decisões Tomadas in $FEATURE_DIR/01-discovery/ideacao.md

## Outline

O texto após `/arkan.ideacao` é a descrição da feature. Se vazio, pergunte ao desenvolvedor.

### Fase 0 — Setup (automático)

1. Verificar pré-condições: `.arkan/scripts/check-prerequisites.sh --json`
2. Gerar `short-name` (2-4 palavras, action-noun, ex: `pipeline-conteudos`)
3. Determinar próximo número NNN: `.arkan/scripts/create-feature.sh` (verificar branches e diretórios existentes)
4. Executar: `.arkan/scripts/create-feature.sh --json --short-name "nome" "Descrição"`
   - **IMPORTANTE**: executar este script apenas **uma vez** por feature
5. Definir `FEATURE_DIR` como `.arkan/features/NNN-short-name`

**Auto-detect de projeto**: verificar se `.arkan/project/status.md` existe com `status: features-definidas`.
Se sim: perguntar ao desenvolvedor — "Um projeto foi iniciado para este repositório. Deseja associar esta feature ao projeto? (sim/não)"
Se sim: registrar `projeto: [nome do projeto]` no `status.md` da feature via `.arkan/scripts/update-status.sh`

### Fase 1 — Investigação Automática (sem interação)

> Agente: Research Agent → .arkan/agents/01-discovery/research-agent.md

**Instrução**: Ler `.arkan/agents/01-discovery/research-agent.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

Antes de ativar o agente, carregar: `constitution.md`, `glossario.md`, `stack.md`; codebase via o indexador de código declarado em `.arkan/memory/stack.md`, quando disponível.

### Fase 2 — Debate Interativo (seção por seção)

> Agente: Intake Agent → .arkan/agents/transversal/intake-agent.md

**Instrução**: Ler `.arkan/agents/transversal/intake-agent.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Criar `FEATURE_DIR/01-discovery/ideacao.md` a partir de `.arkan/templates/01-discovery/ideacao-template.md`.

Antes de ativar o agente, injetar: achados do Research Agent (Fase 1), descrição da feature, template de ideacao.md.

> Agente: Briefing Agent → .arkan/agents/01-discovery/briefing-agent.md

**Instrução**: Ler `.arkan/agents/01-discovery/briefing-agent.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: debate completo e Decisões Tomadas das seções anteriores.

**Exibir cabeçalho antes de cada resposta**:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  FASE 01 — Discovery  ·  MODO: ASSISTÊNCIA
Agente: [Intake Agent / Briefing Agent]  ·  Step: [nome do step atual]
Ação esperada: [o que o desenvolvedor deve fazer agora]
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Fase 2.5 — Classificação de Peso da Feature

Após a síntese aprovada, propor o peso da feature conforme `.arkan/memory/feature-weights.md`:

```
Peso proposto: [Code / Doc / Config]
Justificativa: [por que este peso — quais artefatos serão produzidos]

- Code: pipeline completo (01-10) — código executável, integrações
- Doc: pipeline simplificado — markdown, templates, reorganização
- Config: pipeline mínimo — edição pontual, correção

Confirma o peso proposto? (sim / [outro peso])
```

Se confirmado: `.arkan/scripts/update-status.sh --file $FEATURE_DIR/status.md --field peso --value [peso]`

O peso determina quais fases do pipeline são obrigatórias nas etapas seguintes.

**Superfície crítica** — perguntar em seguida:

```text
Esta feature toca uma superfície que a constituição do projeto declara como
crítica (ver "Decisões de contexto" em .arkan/projects/<projeto>/constitution.md
— ex.: dinheiro e dado financeiro, dado de paciente, experiência de aprendizado
do aluno, conforme o que o projeto declarar)?
Superfície crítica: [sim / não]
```

- Se a constituição do projeto não declarar nenhuma superfície crítica, ou a feature não a toca → `nao`
- Registrar: `.arkan/scripts/update-status.sh --file $FEATURE_DIR/status.md --field superficie-critica --value [sim|nao]`
- **Se `sim`: a seção `## Obrigações da Superfície Crítica` da ideação é OBRIGATÓRIA e BLOQUEANTE** (gate no `qa-mecanico.sh`) — preencher as perguntas da seção, referenciando a política que a constituição do projeto declarar para essa superfície. Sem respostas claras, a feature não avança para `/arkan.spec`.

### Fase 3 — Finalização

1. Garantir que `ideacao.md` está completo e salvo
2. Verificar PÓS-CONDIÇÕES: `check-prerequisites.sh --pos --command .claude/commands/arkan.ideacao.md`
3. Reportar ao desenvolvedor: caminho do arquivo, branch criada, peso classificado
4. Sugerir próximo passo conforme peso:
   - **Code**: `/arkan.spec`
   - **Doc**: `/arkan.spec` (modo simplificado)
   - **Config**: `/arkan.tasks` (pular spec e plan)

## Guidelines

- Documentação em **PT-BR**
- Cada decisão deve ter fundamentação — o "por que", não só o "o que"
- Descobertas do codebase devem incluir caminhos de arquivo e nomes de símbolos
- O documento deve ser autocontido — quem não participou do debate deve entender as decisões
- Se o indexador de código declarado em `.arkan/memory/stack.md` não estiver disponível: operar em modo degradado com nota explícita ao desenvolvedor (Constituição, Restrições)
- Nunca avançar de seção sem aprovação explícita do desenvolvedor (Constituição, Princípio VIII)
