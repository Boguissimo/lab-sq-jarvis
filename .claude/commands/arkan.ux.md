---
description: "Arkan fase 05 — UX Spec: transforma spec em especificação de componentes UI com fluxos, estados e interações. Produz ux-spec.md aprovado pelo desenvolvedor."
mode: geracao
fase: 05-ux
nivel: feature
tecnica: "Structured Output + Few-Shot Prompting"
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/check-prerequisites.sh
arquivo: .arkan/memory/constitution.md
arquivo: .arkan/templates/05-ux/ux-spec-template.md
campo-obrigatorio: ## Requirements in $FEATURE_DIR/03-spec/spec.md

## PÓS-CONDIÇÕES

arquivo: $FEATURE_DIR/05-ux/ux-spec.md
campo-obrigatorio: ## Fluxos de Tela in $FEATURE_DIR/05-ux/ux-spec.md

## Outline

O texto após `/arkan.ux` é opcional — foco específico (ex: "apenas fluxo de cadastro"). A feature é inferida da branch atual.

**Este command é CONDICIONAL**: gerar apenas se a feature envolve componentes UI. Heurística:
- Spec menciona "componente", "tela", "página", "interface", "formulário", "botão" → gerar
- Spec lista arquivos `.tsx`, `.vue`, `.svelte` no plan → gerar
- Feature puramente backend/CLI/script → registrar "Nenhum componente UI — ux-spec.md não gerado" e sugerir `/arkan.plan`

### Fase 0 — Setup (automático)

1. Verificar pré-condições: `.arkan/scripts/check-prerequisites.sh --json --command .claude/commands/arkan.ux.md`
   - Se falhar: exibir lista de falhas e **parar**
2. Definir `FEATURE_DIR` a partir do JSON retornado
3. Verificar se a feature tem componentes UI (heurística acima)
   - Se não tem: informar ao desenvolvedor e encerrar

### Fase 1 — Carregamento de Contexto (sem interação)

Carregar silenciosamente:
- `$FEATURE_DIR/03-spec/spec.md` — user stories, cenários de aceitação, cenários de erro
- `$FEATURE_DIR/04-architecture/plan.md` (se existe) — estrutura de arquivos UI, ADRs relevantes
- `$FEATURE_DIR/04-architecture/data-model.md` (se existe) — entidades e estados (state machines → estados de componente)
- `.arkan/memory/stack.md` — framework UI utilizado (React, Vue, Svelte…)

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

**Indexador de código** (declarado em `.arkan/memory/stack.md`, quando disponível):
- Busca por tema no indexador (ou busca por texto, se não houver indexador) — encontrar componentes existentes reutilizáveis
- Para componentes identificados: busca por símbolo no indexador (ou busca por texto, se não houver indexador) — props, dependências
- Montar lista de componentes que **NÃO devem ser criados** (reutilizar)

### Fase 2 — Geração da UX Spec

> Agente: UI Spec Writer → .arkan/agents/05-ux/ui-spec-writer.md

**Instrução**: Ler `.arkan/agents/05-ux/ui-spec-writer.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: `spec.md` (user stories, cenários), `plan.md` (estrutura UI, ADRs), `data-model.md` (state machines), `stack.md` (framework UI), componentes existentes via o indexador de código declarado em `.arkan/memory/stack.md`.

**Exibir cabeçalho antes de cada resposta**:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  FASE 05 — UX  ·  MODO: ASSISTÊNCIA
Agente: UI Spec Writer  ·  Step: [nome do step]
Ação esperada: [o que o desenvolvedor deve fazer agora]
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Fase 3 — Aprovação Final

Apresentar ux-spec.md completo ao desenvolvedor:
- "UX spec gerada. Há algum fluxo ou componente que deseja revisar?"
- Aplicar ajustes solicitados
- **Princípio VIII**: agente propõe estrutura, desenvolvedor decide

### Fase 4 — Finalização

1. Garantir que `ux-spec.md` está salvo em `$FEATURE_DIR/05-ux/ux-spec.md`
2. Verificar PÓS-CONDIÇÕES: `.arkan/scripts/check-prerequisites.sh --pos --command .claude/commands/arkan.ux.md`
3. Reportar ao desenvolvedor:
   - Componentes documentados: N
   - Fluxos documentados: N
   - Próximo passo: `/arkan.plan` (para incluir ux-spec na arquitetura) ou `/arkan.tasks` (se plan já existe)
   - **Reflexão heurística** sobre a ux-spec recém-gerada:

     ```text
     /arkan.critica-ui --alvo=$FEATURE_DIR/05-ux/ux-spec.md
     ```

     Invoca crítica adversarial contra Nielsen 10 + Hick/Fitts/Miller e, quando `.arkan/config.md` declara `agente-dominio` (e não veio `--sem-dominio`), delega reflexão de domínio a esse agente. Produz artefato anexo em `$FEATURE_DIR/05-ux/critica/` sem modificar a ux-spec.
     - **Obrigatória quando o projeto declarar essa exigência na sua constituição** (critério de cada projeto — ex.: um campo em `status.md` marcando a feature como sujeita a revisão heurística obrigatória): executar antes de encerrar a fase 05 e registrar o caminho do artefato de crítica na resposta final.
     - Opcional nos demais casos — recomendada para fluxos complexos.

## Guidelines

- Documentação em **PT-BR**
- Spec de UX foca em **comportamento** — o desenvolvedor decide a apresentação visual
- Estados de componente devem ser **exaustivos** — todo estado possível documentado
- Componentes existentes têm **prioridade** — criar novo só quando não há alternativa
- Fluxos devem referenciar **estados de componente** — conectar UI à lógica
- Se o indexador de código declarado em `.arkan/memory/stack.md` não estiver disponível: propor componentes com base na spec + stack.md, sem garantia de reuso
