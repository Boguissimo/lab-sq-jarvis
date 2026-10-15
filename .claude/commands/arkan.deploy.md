---
description: "Arkan fase 09 — Deploy: orquestra checklist de deploy com confirmação explícita por etapa. Transiciona feature para em-producao após deploy verificado."
mode: orquestracao
fase: 09-deploy
nivel: feature
tecnica: "ReAct + Structured Output"
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/check-prerequisites.sh
arquivo: .arkan/scripts/update-status.sh
arquivo: .arkan/memory/constitution.md
arquivo: .arkan/templates/09-deploy/deploy-checklist-template.md
campo-obrigatorio: ## Resultado do QA in $FEATURE_DIR/08-qa/qa-report.md

## PÓS-CONDIÇÕES

arquivo: $FEATURE_DIR/09-deploy/deploy-checklist.md
campo-obrigatorio: ## Resultado do Deploy in $FEATURE_DIR/09-deploy/deploy-checklist.md

## Outline

> Agente: Deploy Orchestrator → .arkan/agents/09-deploy/deploy-orchestrator.md

O texto após `/arkan.deploy` é opcional — contexto adicional (ex: "deploy em staging primeiro"). A feature é inferida da branch atual.

**Modo Orquestração com confirmações explícitas**: NENHUMA etapa de deploy é executada automaticamente. Cada fase requer confirmação explícita do desenvolvedor antes de prosseguir.

**AVISO**: este command transiciona o `status.md` da feature para `em-producao` após deploy verificado. Esta é uma ação irreversível de estado — o desenvolvedor deve confirmar explicitamente.

### Fase 0 — Setup e Gate de Segurança (automático)

1. Verificar pré-condições: `.arkan/scripts/check-prerequisites.sh --json --command .claude/commands/arkan.deploy.md`
   - Se falhar: exibir lista de falhas e **parar**
2. Definir `FEATURE_DIR` a partir do JSON retornado
3. **Gate de QA**: ler `$FEATURE_DIR/08-qa/qa-report.md` e verificar `## Resultado do QA`:
   - Se status é REPROVADO: **PARAR** — "QA reprovado. Resolva os bloqueadores antes do deploy."
   - Se status é APROVADO ou APROVADO COM RESSALVAS: prosseguir
4. Se APROVADO COM RESSALVAS: listar as ressalvas e perguntar ao desenvolvedor:
   - "QA aprovado com ressalvas. Deseja prosseguir com o deploy mesmo assim? (sim/não)"
   - Registrar confirmação no checklist

### Fase 1 — Inicialização do Checklist

**Exibir cabeçalho**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  FASE 09 — Deploy  ·  MODO: ORQUESTRAÇÃO
Orquestrador: Deploy Orchestrator  ·  Step: Inicialização
⚠️  ATENÇÃO: Nenhuma etapa será executada sem confirmação explícita.
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Criar `$FEATURE_DIR/09-deploy/deploy-checklist.md` a partir do template.

Preencher cabeçalho: feature, data, fase atual do qa-report.

Exibir resumo inicial:
- Feature: [NNN-short-name]
- Status do QA: [APROVADO / APROVADO COM RESSALVAS]
- Ressalvas abertas (se houver): [N]

**Confirmação obrigatória antes de iniciar**:
```
Pronto para iniciar o deploy de [NNN-nome-feature].
Esta operação irá:
  1. Verificar pré-requisitos de deploy
  2. Executar o deploy em produção
  3. Verificar a feature em produção
  4. Transicionar status para em-producao

Confirma que deseja prosseguir? (sim/não)
```
Se não: encerrar sem alterações.

### Fase 2 — Pré-Deploy (com confirmação por item)

Itens do checklist são classificados como **[BLOQUEANTE]** ou **[AVISO]**:
- **[BLOQUEANTE]**: deploy NÃO prossegue sem este item verificado. Sem exceções.
- **[AVISO]**: registrar justificativa se não verificado e prosseguir com aprovação explícita.

Para cada item da seção `## Fase 1 — Pré-Deploy` do template:

1. Apresentar o item ao desenvolvedor: classificação, o que verificar e como
2. Aguardar confirmação: "Item verificado? (sim/não/pular)"
3. Marcar `[x]` no checklist conforme resposta
4. Se item **[BLOQUEANTE]** não verificado: **NÃO permitir pular** — exigir resolução ou abortar

Ao final da fase — verificar itens BLOQUEANTE:

Se há BLOQUEANTE não verificado:
```
⛔ DEPLOY BLOQUEADO: [N] item(ns) BLOQUEANTE(S) não verificado(s):
  - [lista de itens BLOQUEANTE falhados]

O deploy NÃO pode prosseguir sem resolver estes itens.
Opções:
  A) Resolver agora — verificar os itens pendentes
  B) Abortar — encerrar o deploy
```
NÃO oferecer opção de prosseguir sem resolver BLOQUEANTES.

Se apenas AVISO não verificados:
```
Pré-deploy com avisos: [N] item(ns) de AVISO não verificado(s):
  - [lista com justificativa de cada]
Prosseguir para o deploy? (sim/não)
```
Se não: encerrar. O checklist fica salvo com o estado atual para retomada.

### Fase 3 — Deploy (confirmação por comando)

**⚠️ ZONA DE PRODUÇÃO** — cada comando deve ser confirmado individualmente.

Para cada etapa da seção `## Fase 2 — Deploy`:

1. Exibir o que será executado: comando, local, impacto
2. Perguntar: "Executar esta etapa? (sim/não)"
3. **NÃO executar comandos diretamente** — apresentar ao desenvolvedor para execução manual
4. Aguardar confirmação do resultado: "Resultado: (sucesso/falha)"
5. Registrar no checklist: `[x]` sucesso ou `[ ]` com descrição da falha

**Se qualquer etapa falhar**:
```
⚠️  FALHA DETECTADA: [descrição]

Opções:
  A) Executar rollback — reverter ao estado pré-deploy
  B) Tentar corrigir e continuar — [o que precisa ser corrigido]
  C) Parar e investigar — manter estado atual sem rollback

Qual opção? (A/B/C)
```
Registrar decisão no checklist.

### Fase 4 — Pós-Deploy: Verificação em Produção

Para cada item da seção `## Fase 3 — Pós-Deploy`:

1. Apresentar o que verificar: cenário de teste, como executar
2. Aguardar resultado: "Resultado: (pass/fail)"
3. Registrar no checklist

**Smoke test obrigatório** (não pular):
- Verificar que a funcionalidade principal da feature P1 está operando em produção
- Resultado FAIL aqui → oferecer rollback imediatamente

### Fase 5 — Transição de Estado

**Somente após todos os itens de pós-deploy PASS**.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Deploy verificado com sucesso.

Próxima ação: transicionar status da feature para em-producao.
Esta ação marca a feature como em produção no status.md.

Confirma a transição para em-producao? (sim/não)
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Se sim:
- `.arkan/scripts/update-status.sh --file $FEATURE_DIR/status.md --field status --value em-producao`
- `.arkan/scripts/update-status.sh --file $FEATURE_DIR/status.md --field fase-atual --value 10-ops`

Se não: registrar que a transição foi adiada e encerrar sem alterar status.

### Fase 6 — Finalização

1. Registrar resultado final no checklist: data, status conforme regra do template:
   - **SUCESSO**: todos BLOQUEANTE `[x]` e desenvolvedor confirmou
   - **COM DESVIOS**: todos BLOQUEANTE `[x]` mas há AVISO não verificados (listar justificativas)
   - **FALHA**: algum BLOQUEANTE `[ ]` ou rollback executado
   - **PARCIAL**: deploy interrompido antes de concluir todas as fases
2. Garantir que `deploy-checklist.md` está salvo em `$FEATURE_DIR/09-deploy/`
3. Verificar PÓS-CONDIÇÕES: `.arkan/scripts/check-prerequisites.sh --pos --command .claude/commands/arkan.deploy.md`
4. Reportar ao desenvolvedor:
   - Status do deploy
   - Status.md atualizado para: `em-producao` (se confirmado)
   - Próximo passo: `/arkan.ops` para monitoramento em produção

## Guidelines

- Documentação em **PT-BR**
- **Cada confirmação é um gate** — sem confirmação, sem execução
- O agente **nunca executa comandos de deploy diretamente** — apresenta ao desenvolvedor para execução manual
- Rollback plan deve ser definido **antes** do deploy — não depois que algo falha
- Transição para `em-producao` é **irreversível de estado** — exige confirmação explícita separada
- Se em dúvida: parar e perguntar — deploy é a operação com maior blast radius possível
- Deploy parcial (algumas etapas falharam) deve ser documentado explicitamente no checklist
- Checklist salvo incrementalmente — pode ser retomado se a sessão for interrompida
