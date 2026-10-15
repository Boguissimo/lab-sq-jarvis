---
description: "Arkan fase 08 — Alinhamento spec↔código: detecta divergências e propõe correções na direção correta (spec governa código). Produz relatório categorizado por direção."
mode: geracao
fase: 08-qa
nivel: feature
tecnica: "ReAct + Chain-of-Verification (CoVe)"
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/check-prerequisites.sh
arquivo: .arkan/memory/constitution.md
campo-obrigatorio: ## Requirements in $FEATURE_DIR/03-spec/spec.md

## PÓS-CONDIÇÕES

arquivo: $FEATURE_DIR/08-qa/alinhamento-report.md

## Outline

O texto após `/arkan.alinhamento` é opcional — especifica foco (ex: "apenas data-model", "invariantes"). A feature é inferida da branch atual.

### Princípio Fundamental: Spec-Driven Development (SDD)

```
Constitution (.arkan/memory/constitution.md) — inviolável
    | governa
Spec (fonte de verdade do design)
    | governa
Código (implementação da spec)
```

**A spec governa o código, NUNCA o contrário.** Quando há divergência:

| Tipo | Direção da correção | Ação |
| --- | --- | --- |
| Código viola Constitution | Código → mudar | **CRÍTICO**: código DEVE mudar |
| Código viola spec sem justificativa | Código → mudar OU spec → Clarification | **ALTO**: código muda, ou registrar Clarification formal |
| Código adiantou spec (não especificado) | Spec → registrar | **MÉDIO**: adicionar Clarification documentando a decisão |
| Spec com erro factual (tipo, nome errado) | Spec → correção factual | **MÉDIO**: corrigir fato errado na spec |
| Design especificado nunca implementado | Avaliar | **BAIXO**: backlog ou dead spec |

**Em NENHUM caso** a spec é atualizada silenciosamente para "refletir o código". Toda alteração requer justificativa explícita.

### Fase 0 — Setup (automático)

1. Verificar pré-condições: `.arkan/scripts/check-prerequisites.sh --json --command .claude/commands/arkan.alinhamento.md`
   - Se falhar: exibir lista de falhas e **parar**
2. Definir `FEATURE_DIR` a partir do JSON retornado

### Fase 1 — Carregamento de Artefatos (sem interação)

**Exibir cabeçalho**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  FASE 08 — QA  ·  MODO: GERAÇÃO
Agente: Aligner  ·  Step: Carregamento de contexto
Ação esperada: aguardar — análise automática em progresso
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Carregar em paralelo todos os artefatos da feature:
- `$FEATURE_DIR/03-spec/spec.md` — user stories, FRs, NFRs, **Invariantes**
- `$FEATURE_DIR/04-architecture/plan.md` — ADRs, interfaces expostas, estrutura esperada
- `$FEATURE_DIR/06-planning/tasks.md` — tasks e estado de cada uma
- `$FEATURE_DIR/04-architecture/data-model.md` (se existe) — schema esperado
- `$FEATURE_DIR/04-architecture/contracts/` (se existe) — contratos de interface
- `$FEATURE_DIR/01-discovery/ideacao.md` (se existe) — decisões originais
- `.arkan/memory/constitution.md` — Princípios I-VIII

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

**Descobrir código implementado** (cascata de ferramentas — usar a primeira disponível):

1. **arkan-kb MCP** (preferencial):
   - `mcp__arkan-kb__query({query: "<keywords da feature>"})` — encontrar arquivos e símbolos indexados (ou busca por texto, se não houver indexador)
   - `mcp__arkan-kb__context({name: "<símbolo>"})` — definição; confirme callers e conexões no próprio indexador, estado atual (ou busca por texto, se não houver indexador)
   - `mcp__arkan-kb__impact({target: "<símbolo>", direction: "upstream"})` — blast radius (ou busca por texto, se não houver indexador)
   - `mcp__arkan-kb__audit_coverage()` — gaps spec↔código (ou busca por texto, se não houver indexador)
2. **Grep/Glob** (fallback final):
   - Buscar por keywords da feature nos diretórios de código e de migrações declarados em `.arkan/memory/stack.md`
   - Usar `File:` das tasks concluídas `[x]` para identificar arquivos

Registrar no relatório qual ferramenta foi usada para discovery.

### Fase 2 — Inventário de Divergências

> Agente: Aligner → .arkan/agents/transversal/aligner.md

**Instrução**: Ler `.arkan/agents/transversal/aligner.md` e executar conforme `## PROMPT` do agente. Verificar `## PRÉ-CONDIÇÕES` antes de iniciar; validar `## PÓS-CONDIÇÕES` ao concluir.

Antes de ativar o agente, injetar: `spec.md`, `constitution.md`, código identificado na Fase 1, `plan.md`, `data-model.md`, `contracts/`, `ideacao.md` (quando existirem).

### Fase 3 — Verificação por Chain-of-Verification

Para cada divergência encontrada, executar verificação adicional:
1. **Re-ler** o trecho de código relevante para confirmar a divergência (não assumir)
2. **Re-ler** o trecho da spec relevante para confirmar o que foi especificado
3. **Determinar direção** com justificativa explícita
4. Se direção ambígua: marcar como `[REQUER DECISÃO]` para o desenvolvedor

### Fase 4 — Produção do Relatório

Salvar em `$FEATURE_DIR/08-qa/alinhamento-report.md`:

```markdown
# Alinhamento: Feature [NNN] — [Nome]

**Data**: [DATA]
**Status Geral**: ALINHADO | DIVERGÊNCIAS MENORES | DIVERGÊNCIAS SIGNIFICATIVAS

---

## Resumo Executivo

- Total de divergências: N
- Críticas (CRÍTICO): N
- Altas (ALTO): N
- Médias (MÉDIO): N
- Baixas (BAIXO): N

---

## Divergências por Direção

### Código deve mudar (spec governa)
[Divergências onde o código está errado segundo spec/Constitution]

### Spec precisa de Clarification (código adiantou ou decisão mudou)
[Divergências onde o código evoluiu legitimamente e a spec precisa registrar]

### Spec precisa de correção factual (erro de precisão)
[Nomes, tipos errados na spec — não muda design]

### Backlog ou dead spec (design não implementado)
[Partes da spec que nunca foram implementadas — decidir se manter ou deferir]

---

## Tabela de Ações

| # | Severidade | Arquivo | Tipo | Descrição |
| --- | --- | --- | --- | --- |
| 1 | CRÍTICO | `spec.md` | Invariante violado | ... |
| 2 | ALTO | `arquivo.ts` | Código deve mudar | ... |
```

### Fase 5 — Aplicação de Correções (com aprovação)

Apresentar relatório ao desenvolvedor. Para cada divergência:

**Correções factuais na spec** (tipos, nomes errados): propor correção com justificativa → aguardar aprovação → aplicar

**Clarifications** (spec precisa registrar decisão do código): redigir como `C[N]` formal na spec com formato:
```markdown
**C[N] — [Título] (alinhamento [data])**
[Descrição da divergência]
**Decisão**: [O que foi decidido]
**Justificativa**: [Por que esta decisão está correta]
**Alterações aplicadas**: [Quais artefatos foram alterados]
```

**Correções no código** (código deve mudar): propor a correção → aguardar aprovação → implementar

**[REQUER DECISÃO]**: apresentar contexto + opções → aguardar escolha do desenvolvedor → aplicar

**Princípio VIII**: agente propõe direção e correção, desenvolvedor aprova cada uma.

### Fase 6 — Finalização

1. Garantir que `alinhamento-report.md` está salvo em `$FEATURE_DIR/08-qa/`
2. Reportar ao desenvolvedor:
   - Status final após correções aplicadas
   - Divergências deixadas para backlog (se houver)
   - Próximo passo sugerido: `/arkan.qa` (se disponível) ou `/arkan.deploy`

## Guidelines

- **NUNCA atualizar spec silenciosamente** — toda alteração requer justificativa visível
- **Constitution é inviolável** — violações são sempre CRÍTICO, código sempre muda
- **Clarifications são permanentes** — uma vez registrada, faz parte da spec; não reescrever FRs originais
- Distinguir **correção factual** (corrigir `tabela_a` → `tabela_b` quando código usa `tabela_b`) de **mudança de design** (sempre requer Clarification)
- Se não souber a direção, **perguntar ao desenvolvedor** — divergências ambíguas não devem ser resolvidas unilateralmente
- Documentação em **PT-BR**
