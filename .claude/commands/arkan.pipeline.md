---
description: "Arkan pipeline — Meta-orquestrador: executa o ciclo completo 01-10 com gates de qualidade (analyze, verificaissues, audit) e debates profissionais em pontos de bifurcação."
mode: orquestracao
nivel: feature
tecnica: "ReAct + Multi-Agent Debate + Structured Output"
fases:
  - 01-discovery: arkan.ideacao
  - 02-proposta: arkan.proposta
  - 03-spec: arkan.spec
  - 04-architecture: arkan.plan
  - 05-ux: arkan.ux (opcional)
  - 06-planning: arkan.tasks
  - "gate 06->07": arkan.analyze (obrigatório, Fase 2.4) + arkan.taskstoissues (opcional)
  - 07-development: arkan.implement
  - "gate 07->08": arkan.verificaissues (condicional, Fase 2.6) + arkan.audit (opcional, preventivo)
  - 08-qa: arkan.qa
  - "gate 08->09": arkan.audit (Fase 2.5, adversarial condicional)
  - 09-deploy: arkan.deploy
  - 10-ops: arkan.ops
artefatos-produzidos:
  - $FEATURE_DIR/pipeline-log.md (raiz)
  - $FEATURE_DIR/08-qa/analyze-report.md (gate 06->07)
  - $FEATURE_DIR/06-planning/issues-map.md (gate 06->07, opcional)
  - $FEATURE_DIR/08-qa/issues-audit.md (gate 07->08, condicional)
  - $FEATURE_DIR/08-qa/audit-report.md (gate 07->08 e/ou Fase 2.5, versionado v1.0, v2.0...)
  - $FEATURE_DIR/08-qa/qa-report.md (08-qa)
  - $FEATURE_DIR/09-deploy/deploy-checklist.md (09-deploy)
  - $FEATURE_DIR/10-ops/ops-report.md (10-ops)
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/check-prerequisites.sh
arquivo: .arkan/memory/constitution.md
campo-obrigatorio: status in $FEATURE_DIR/status.md

## PÓS-CONDIÇÕES

arquivo: $FEATURE_DIR/pipeline-log.md
campo-obrigatorio: ## Execuções in $FEATURE_DIR/pipeline-log.md

## Outline

O texto após `/arkan.pipeline` é opcional. Flags disponíveis:

- `--from NN-fase` — entrar diretamente numa fase específica (ex: `--from 03-spec`)
- `--ate NN-fase` — parar após uma fase específica (ex: `--ate 06-planning`)
- `--debate-scope` — ativar debate de escopo na transição 01→02

Se nenhuma flag for passada: detectar fase automaticamente pelo campo `fase-atual` de `$FEATURE_DIR/status.md`.

**Modo Meta-Orquestração**: este command executa cada fase em sequência, delegando o comportamento aos commands individuais. Entre fases, verifica se a transição exige debate profissional — e se sim, conduz o debate antes de avançar. O desenvolvedor confirma cada avanço (Princípio VIII).

### Fase 0 — Setup (automático)

1. Verificar pré-condições: `.arkan/scripts/check-prerequisites.sh --json --command .claude/commands/arkan.pipeline.md`
   - Se falhar: exibir lista de falhas e **parar**
2. Definir `FEATURE_DIR` a partir do JSON retornado
3. Ler `$FEATURE_DIR/status.md`:
   - Extrair `fase-atual` e `status`
   - Se argumento `--from` foi passado: usar como `FASE_ENTRADA`
   - Caso contrário: usar `fase-atual` do status.md como `FASE_ENTRADA`
4. Verificar se `$FEATURE_DIR/pipeline-log.md` já existe:
   - Se sim: modo **retomada** — ler log para exibir histórico de execuções anteriores; incrementar número de execução
   - Se não: modo **novo** — esta será a execução #1
5. Determinar `FASE_SAIDA`:
   - Se argumento `--ate` foi passado: usar como `FASE_SAIDA`
   - Caso contrário: `10-ops`

### Fase 1 — Orientação (sem interação)

**Exibir cabeçalho**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  PIPELINE  ·  MODO: META-ORQUESTRAÇÃO
Feature: [NNN-nome-feature]
Entrada: [FASE_ENTRADA]  →  Saída: [FASE_SAIDA]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Exibir mapa do pipeline com estado de cada fase:

```
PIPELINE — [NNN-nome-feature]
  ✓ = concluída    →  = fase atual    ○ = pendente    ⚡= debate nesta transição

  [✓/→/○]  01 — Discovery      (ideacao.md)
               ↓ ⚡ debate de escopo (apenas com --debate-scope)
  [✓/→/○]  02 — Proposta       (proposta.md)
               ↓
  [✓/→/○]  03 — Spec           (spec.md)
               ↓ ⚡ debate arquitetural (se 2+ abordagens identificadas)
  [✓/→/○]  04 — Architecture   (plan.md)
               ↓
  [✓/→/○]  05 — UX             (ux-spec.md)  [opcional]
               ↓
  [✓/→/○]  06 — Planning       (tasks.md)
               ↓ 🧪 análise de consistência (obrigatória: /arkan.analyze → analyze-report.md)
               ↓ 📋 tasks → issues (opcional: /arkan.taskstoissues → issues-map.md)
               ↓ ⚡ debate de risco (se tasks HIGH/CRITICAL detectadas)
  [✓/→/○]  07 — Development    (tasks.md → [x])
               ↓ 🔍 verificação de issues (condicional: /arkan.verificaissues → issues-audit.md, só se issues-map.md existe)
  [✓/→/○]  08 — QA
               ↓ 🛡️ auditoria preventiva (opcional: /arkan.audit → audit-report.md, recomendado se há migrations)
               ↓ orquestração QA (/arkan.qa → qa-report.md)
               ↓ 🛡️ re-auditoria adversarial (Fase 2.5: /arkan.audit se RESSALVAS ou correções)
               ↓ ⚡ debate go/no-go (se APROVADO COM RESSALVAS)
  [✓/→/○]  09 — Deploy         (deploy-checklist.md)
               ↓
  [✓/→/○]  10 — Ops            (ops-report.md)
```

Exibir confirmação inicial:

```
Iniciar pipeline a partir de [FASE_ENTRADA]?
(sim / não / --ate [fase] para limitar o escopo desta sessão)
```

Se não: encerrar sem alterações.

### Fase 2 — Loop de Execução (fase por fase)

Para cada fase desde `FASE_ENTRADA` até `FASE_SAIDA`, em ordem:

**2a. Anunciar início da fase**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  PIPELINE  ·  FASE [NN] — [Nome]
Delegando para: .claude/commands/arkan.[command].md
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**2b. Executar o comportamento da fase**:

Seguir o Outline completo do command correspondente (conforme `.claude/commands/arkan.[X].md`). Adaptação única: ao final da fase, em vez de sugerir o próximo command isolado, retornar ao pipeline para o gate de transição.

Mapeamento de fases → commands:

| Fase | Command | Adaptação |
|------|---------|-----------|
| 01-discovery | arkan.ideacao | Feature já criada — pular a execução de `create-feature.sh` na Fase 0 do command |
| 02-proposta | arkan.proposta | — |
| 03-spec | arkan.spec | — |
| 04-architecture | arkan.plan | — |
| 05-ux | arkan.ux | Perguntar ao dev se UX se aplica; se não: pular e registrar no log como "N/A — não aplicável" |
| 06-planning | arkan.tasks | — |
| 06→07 (obrigatório) | arkan.analyze | Gate de qualidade: análise cruzada spec↔plan↔tasks. Se findings CRITICAL: bloquear avanço e propor correção (ver Fase 2.4) |
| 06→07 (opcional) | arkan.taskstoissues | Oferecer ao dev no gate de transição; se aceito, executar antes de avançar |
| 07-development | arkan.implement | Loop de tasks até todas `[x]`; retornar ao pipeline após checkpoint final de fase |
| 07→08 (condicional) | arkan.verificaissues | Disparado apenas se `06-planning/issues-map.md` existe. Reconcilia GitHub↔tasks.md↔código (ver Fase 2.6) |
| 08-qa (preventivo, opcional) | arkan.audit | Auditoria profunda spec↔código↔BD. Recomendar default=sim quando feature toca migrations/schema. Alimenta o `arkan.qa` (não substitui) |
| 08-qa | arkan.qa | — |
| 08-qa (re-auditoria após correções) | arkan.audit (com instrução adversarial) | Disparado se status do qa-report indicar ressalvas ou se houve correções no ciclo (ver Fase 2.5) |
| 09-deploy | arkan.deploy | — |
| 10-ops | arkan.ops | Ciclo #1 — execução única nesta invocação do pipeline |

**2c. Checkpoint de conclusão de fase**:

Ao retornar do comportamento da fase:

- Verificar que o artefato principal da fase existe (ex: `spec.md`, `plan.md`, `qa-report.md`)
- Registrar fase como concluída no `pipeline-log.md` (ver formato na Fase 4)
- Atualizar `$FEATURE_DIR/status.md` com a nova `fase-atual` via `.arkan/scripts/update-status.sh`

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHECKPOINT: Fase [NN] — [Nome] concluída
Artefato gerado: [caminho do artefato principal]
Próxima fase: [NN+1] — [Nome]
[⚡ Debate necessário antes de avançar: [tópico] — aguardar debate abaixo]
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**2d. Gate de transição**:

Antes de avançar para a próxima fase:

1. **Transição 06→07 (obrigatório — análise de consistência)**: se a fase concluída é `06-planning`, executar `/arkan.analyze` automaticamente antes de qualquer outro step do gate. Ver Fase 2.4 para mecânica e tratamento de findings. Se houver bloqueio por CRITICAL não-resolvido, **parar** o pipeline aqui.
2. **Transição 06→07 (opcional — issues)**: após `analyze` concluído sem bloqueio, oferecer ao dev:
   ```
   Deseja criar GitHub Issues para as tasks? (/arkan.taskstoissues)
   (sim / não — prosseguir direto para implementação)
   ```
   Se sim: executar o comportamento de `/arkan.taskstoissues` antes de avançar. Se não: prosseguir normalmente.
3. **Transição 07→08 (condicional — verificação de issues)**: se a fase concluída é `07-development` **e** `$FEATURE_DIR/06-planning/issues-map.md` existe, executar `/arkan.verificaissues` automaticamente. Ver Fase 2.6 para mecânica e tratamento de classificações críticas (Regressão/Inconsistência).
4. **Transição 07→08 (opcional — auditoria preventiva)**: ao entrar em `08-qa`, antes de invocar `arkan.qa`, oferecer ao dev:
   ```
   Deseja executar auditoria profunda spec↔código↔BD antes do QA? (/arkan.audit)
   (sim — recomendado se há migrations / não — ir direto ao /arkan.qa)
   ```
   Se sim: executar `/arkan.audit` produzindo `audit-report.md`. Os findings ficam disponíveis como contexto adicional para o `arkan.qa` na Fase 2b. Se não: prosseguir direto para `/arkan.qa`.
5. Verificar se a transição ativa um debate (condições na Fase 3)
6. Se debate ativado: conduzir debate conforme Fase 3, aguardar confirmação, registrar no log
7. Perguntar:
   ```
   Avançar para Fase [NN+1] — [Nome]? (sim / não / --ate aqui para pausar)
   ```
8. Se não ou `--ate aqui`: salvar estado atual no log e encerrar com instrução de retomada:
   ```
   Pipeline pausado. Para retomar: /arkan.pipeline --from [NN+1-nome]
   ```

### Fase 2.4 — Análise de Consistência (gate 06-planning → 07-development)

Após `arkan.tasks` concluir e produzir `tasks.md` na fase `06-planning`, executar **automaticamente** `/arkan.analyze` antes de qualquer outro step do gate 06→07. Esta fase é **obrigatória** — não pergunta ao dev se quer rodar.

Esta fase existe para mitigar o **custo assimétrico de bugs descobertos tarde**: detectar FR sem task, drift de terminologia spec↔plan, ou violação constitucional **antes** de gastar tokens em implementação custa minutos; descobrir o mesmo problema durante o QA custa horas.

#### 2.4a — Mecânica

- Delegar para o comportamento completo de `.claude/commands/arkan.analyze.md`
- Saída obrigatória: `$FEATURE_DIR/08-qa/analyze-report.md`
- Registrar no `pipeline-log.md` como step do gate 06→07

#### 2.4b — Decisão pós-análise

```text
após /arkan.analyze concluir, ler analyze-report.md:
  if findings CRITICAL detectados:
    → apresentar ao dev a lista de findings CRITICAL com proposta de correção
    → aguardar decisão do dev:
        a) "corrigir agora" → aplicar correções, re-rodar /arkan.analyze, repetir gate
        b) "registrar como ressalva e prosseguir" → registrar override no pipeline-log.md (Princípio VIII) e avançar
        c) "pausar pipeline" → salvar estado e encerrar com instrução de retomada
  if findings HIGH detectados (sem CRITICAL):
    → apresentar resumo ao dev, perguntar se deseja corrigir antes ou seguir
  if apenas MEDIUM/LOW ou nenhum finding:
    → registrar análise como concluída e seguir para o próximo step do gate (taskstoissues opcional)
```

### Fase 2.5 — Re-auditoria Adversarial (gate 08-qa → 09-deploy)

Após `arkan.qa` concluir e produzir `qa-report.md` na fase `08-qa`, **se o status é `APROVADO COM RESSALVAS`** ou **se houve correções no ciclo de iteração**, executar uma **re-auditoria adversarial** antes de liberar a transição para `09-deploy`.

Esta fase existe para mitigar o **viés de auto-aprovação sem verificação adversarial**: empiricamente, sub-agentes do mesmo perfil que aplicaram correções tendem a confirmar o que veem em vez de procurar regressões. Ver Inovação 4 do `arkan.debate.md` para a lição empírica de origem.

#### 2.5a — Quando ativar

**Gatilho por evento, verificado mecanicamente — nunca por status autorrelatado** (debate 2026-08-06: "o gatilho não pode ler o documento escrito pelo processo do qual deveria desconfiar; enforcement opt-in pelo vigiado não é enforcement"):

- Ativar sempre que houver **qualquer mudança em arquivos da feature (código ou artefatos) posterior à primeira geração do `qa-report.md`** — detectar via `git log`/`git diff` sobre os paths da feature desde o timestamp/commit do primeiro qa-report, não via declaração do ciclo.
- O campo de status do `qa-report.md` **não participa da condição**: um relatório "APROVADO" e limpo com correções por baixo é exatamente o caso que o viés de auto-aprovação produz (v2.0 do caso 123-000: 9/10 falso).

Pular a Fase 2.5 **apenas** quando o diff pós-QA for vazio (nenhuma mudança na feature desde o primeiro qa-report).

#### 2.5b — Mecânica

- Disparar **sub-agente independente adversarial** via tool `Task`
- `subagent_type` deve ser **diferente** quando viável daquele que aplicou as correções (ex.: se a correção foi `general-purpose`, a re-auditoria pode ser `Explore` ou outro especializado)
- O prompt deve seguir o **padrão de Inovação 4 do `arkan.debate.md`**, incluindo:
  - Instrução explícita: "não confie na v(N-1), procure regressões e achados perdidos"
  - Versionamento: identificar a auditoria atual como `audit-report.md vN.0` e instruir comparação com a versão anterior
  - Lista explícita de coisas a verificar: race conditions, transações atômicas, idempotência, edge cases de schema, integração entre artefatos
  - Obrigação de evidência fresca: SQL real, leitura linha-a-linha, grep — não confiar em relatos
- Saída: `audit-report.md` com versão incrementada (sobrescreve com versão atualizada, mantendo histórico de versões anteriores em apêndice ou seção "Histórico de versões")

#### 2.5c — Decisão pós-re-auditoria

```text
após re-auditoria adversarial concluir:
  if findings CRITICAL/HIGH novos detectados:
    → registrar como execução em loop no pipeline-log.md
    → voltar para fase 08-qa (loop de correção)
    → após nova rodada de correção, repetir Fase 2.5
  if score rebaixado em > 1 ponto vs. versão anterior:
    → tratar como sinal de regressão; voltar para 08-qa
  if score igual/superior e sem CRITICAL/HIGH novo:
    → liberar gate 08 → 09 (avançar para deploy)
```

Registrar a decisão no `pipeline-log.md` na seção da execução corrente, com referência à versão do `audit-report.md` produzida.

> Nota: o command `/arkan.audit` tem **dois usos distintos** no pipeline. (1) **Preventivo** (gate 07→08, opcional): roda antes de `/arkan.qa` para mapear divergências spec↔código↔BD e alimentar o QA. (2) **Adversarial** (Fase 2.5, automático condicional): roda depois de `/arkan.qa` quando há ressalvas/correções, com instrução adversarial e versionamento. Não confundir os dois.

### Fase 2.6 — Verificação de Issues (gate 07-development → 08-qa)

Após `arkan.implement` concluir o loop de tasks na fase `07-development`, **se** `$FEATURE_DIR/06-planning/issues-map.md` existe (ou seja, o dev aceitou rodar `/arkan.taskstoissues` no gate 06→07), executar **automaticamente** `/arkan.verificaissues` antes de avançar para `08-qa`.

Esta fase existe para fechar o ciclo de issues: detectar **regressões** (issue fechada, código sumiu), **falsos positivos** (task `[x]` mas issue ainda Open) e **inconsistências** (issue fechada sem código). Sem este gate, o GitHub vira lixeira de issues órfãs e o `arkan.qa` opera sobre estado desalinhado.

#### 2.6a — Quando ativar

- `$FEATURE_DIR/06-planning/issues-map.md` existe E
- Fase concluída é `07-development`

Se `issues-map.md` não existe: pular Fase 2.6 e ir direto para o próximo step do gate (auditoria preventiva opcional, depois `08-qa`). Não tentar inferir issues.

#### 2.6b — Mecânica

- Delegar para o comportamento completo de `.claude/commands/arkan.verificaissues.md`
- Escopo padrão: `all` (cobre Open + Closed) — diferente do default standalone (`open`), porque no gate queremos panorama completo antes do QA
- Saída obrigatória: `$FEATURE_DIR/08-qa/issues-audit.md`
- Registrar no `pipeline-log.md` como step do gate 07→08

#### 2.6c — Decisão pós-verificação

```text
após /arkan.verificaissues concluir, ler issues-audit.md:
  if Regressão (🔴) detectada:
    → bloquear avanço; apresentar ao dev a lista com sugestão de investigação
    → aguardar decisão: a) investigar agora, b) registrar como ressalva e prosseguir, c) pausar
  if Inconsistência (❌) detectada (issue fechada sem implementação):
    → apresentar ao dev: reabrir issue OU justificar fechamento no log
    → não bloqueia, mas exige decisão explícita
  if apenas Pendente/Em progresso/Pronta p/ fechar:
    → apresentar resumo, perguntar se deseja fechar issues prontas antes do QA (recomendado)
    → seguir para próximo step do gate (auditoria preventiva opcional)
```

Registrar a decisão no `pipeline-log.md` com referência ao `issues-audit.md` produzido.

### Fase 3 — Debates Profissionais

Os debates são conduzidos em transições específicas. Cada debate segue o formato abaixo.

#### 3.1 — Quando ativar

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

| Transição | Condição de ativação | Tópico |
|-----------|---------------------|--------|
| 01→02 (discovery→proposta) | Flag `--debate-scope` passada | Escopo e priorização do MVP |
| 03→04 (spec→plan) | Spec menciona 2+ abordagens arquiteturais OU o agente Architect identificou ADRs com alternativas não-triviais | Escolha de abordagem técnica |
| 06→07 (planning→development) | Tasks.md contém tasks com risco HIGH ou CRITICAL (>15 símbolos afetados, identificados via o indexador de código declarado em `.arkan/memory/stack.md`) | Ordem de ataque e estratégia de paralelismo |
| 08→09 (qa→deploy) | qa-report.md tem status `APROVADO COM RESSALVAS` | Go/No-Go: shipar agora ou corrigir antes? |

Para verificar a condição: ler o artefato produzido na fase que acabou de concluir antes de decidir se o debate é ativado. Se a condição não for atendida, avançar diretamente para o gate de transição (2d).

#### 3.2 — Personas por transição

**Discovery → Proposta** (`--debate-scope`):

- **Intake Analyst** — foca na completude da ideação: "o problema está bem definido o suficiente para estimar?"
- **Scope Guardian** — foca na contenção de escopo: "o que fica fora do MVP para não comprometer a entrega?"
- **Dev Advocate** — foca na viabilidade técnica: "o que é implementável com a stack atual no prazo?"

**Spec → Plan**:

- **Arquiteto Sênior** — defende robustez e extensibilidade: "a decisão precisa aguentar os próximos 2 anos"
- **Desenvolvedor Pragmático** — defende simplicidade e velocidade: "a decisão mais simples que resolve o problema agora"
- **Analista de Risco** — defende segurança e reversibilidade: "qual decisão é mais fácil de desfazer se errarmos?"

**Planning → Development**:

- **Risk Analyzer** — defende começar pelo risco maior: "tarefas de alto impacto primeiro reduzem surpresas tardias"
- **Task Decomposer** — defende a sequência natural: "fundação → user stories → polish, na ordem que bloqueia menos"

**QA → Deploy** (apenas com ressalvas):

- **QA Lead** — defende corrigir antes: "ressalvas em produção viram bugs críticos com usuarios reais"
- **Engenheiro de Entrega** — defende shipar: "valor parado tem custo; ressalvas têm plano de correção"
- **Product Owner** — defende o que maximiza valor: "quais ressalvas afetam o usuário agora vs. quais podem esperar?"

#### 3.3 — Formato do debate

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  DEBATE  ·  [Tópico]
Transição: Fase [NN] → Fase [NN+1]
Questão central: [qual decisão precisa ser tomada]
Alternativas: [lista das opções identificadas nos artefatos]
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

── POSIÇÕES INICIAIS ───────────────────

▸ [PERSONA A] — [papel]
  Defende: [alternativa X]
  Argumento: [2-3 frases baseadas em evidências dos artefatos da feature]

▸ [PERSONA B] — [papel]
  Defende: [alternativa Y]
  Argumento: [2-3 frases com perspectiva diferente, baseadas nos mesmos artefatos]

▸ [PERSONA C] — [papel]  (se 3 personas)
  Defende: [alternativa Z ou variante de X/Y]
  Argumento: [2-3 frases]

── REBATE ──────────────────────────────

▸ [PERSONA A] responde:
  [1-2 frases — rebate o argumento mais forte de B e/ou C]

▸ [PERSONA B] responde:
  [1-2 frases — rebate o argumento mais forte de A e/ou C]

▸ [PERSONA C] responde:  (se aplicável)
  [1-2 frases]

── SÍNTESE ─────────────────────────────

Consenso: [onde todas as personas concordam]
Divergência central: [o ponto que ainda separa as posições]
Argumento mais fundamentado: [qual persona tem a posição mais sólida neste contexto e por quê]

── RECOMENDAÇÃO ────────────────────────

Posição recomendada: [alternativa X/Y/Z]
Fundamentação: [1-2 frases — por que esta posição vence no contexto específico desta feature]

Confirma esta recomendação?
(sim / outra opção: [descreva] / pular debate)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Se o dev confirma "sim"**: registrar decisão no `pipeline-log.md` e avançar para o gate de transição (2d).

**Se o dev propõe alternativa diferente**: registrar a posição do dev como decisão final sem novo debate — o dev sempre tem a última palavra (Constituição, Princípio VIII). Registrar no log: `"Decisão do desenvolvedor (override): [posição informada]"`.

**Se o debate não chega a consenso claro** (posições igualmente fundamentadas): apresentar ao dev os dois lados sem recomendar e pedir decisão direta. O dev decide — não o agente.

**Se o dev responde "pular debate"**: registrar no log como "debate pulado por decisão do dev" e avançar para o gate de transição.

#### 3.4 — Argumentos baseados em evidências

**Regra crítica**: cada argumento de persona DEVE referenciar artefatos reais da feature — não princípios genéricos. Antes de gerar as posições:

- Ler o artefato mais recente da fase (ex: `spec.md` antes do debate spec→plan; `qa-report.md` antes do debate qa→deploy)
- Extrair elementos concretos: user stories, FRs, invariantes, ADRs, ressalvas do QA, tasks marcadas com risco
- Usar esses elementos como evidência nas posições

Exemplo correto: *"A spec define os invariantes INV-002 e INV-005 que exigem validação em múltiplos layers — a abordagem monolítica (ADR-001 alternativa B) concentra essa validação num único ponto e viola INV-005 ao não isolar o domínio de autenticação."*

Exemplo incorreto: *"Em geral, arquiteturas distribuídas são mais seguras."*

### Fase 4 — Finalização

Quando `FASE_SAIDA` é atingida (ou o dev pausa antes):

**4a. Exibir resumo da execução**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  PIPELINE  ·  SESSÃO CONCLUÍDA
Feature: [NNN-nome-feature]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Fases executadas nesta sessão:
  ✓  [NN] [Nome] → [artefato gerado]
  ...

Debates realizados: [N]
  ⚡ [Tópico] → [decisão tomada] ([confirmado / override do dev / pulado])

[Se pipeline não chegou ao fim:]
Próxima fase: [NN+1] — [Nome]
Para retomar: /arkan.pipeline --from [NN+1-nome]

[Se pipeline chegou ao fim:]
Pipeline completo. Feature em produção e monitorada.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**4b. Salvar/atualizar `$FEATURE_DIR/pipeline-log.md`**:

Formato do arquivo:

```
# Pipeline Log: [NNN-nome-feature]

> Criado em: [YYYY-MM-DD]
> Última atualização: [YYYY-MM-DD]

---

## Execuções

### Execução #[N] — [YYYY-MM-DD]

**Entrada**: Fase [NN] — [Nome]
**Saída**: Fase [NN] — [Nome] ([concluída / pausada pelo dev])

#### Fases desta execução

| Fase | Status | Artefato | Observações |
|------|--------|----------|-------------|
| 01-discovery | ✓ concluída | ideacao.md | — |
| 05-ux | — N/A — | — | Não aplicável — feature sem interface gráfica |
| ...

#### Steps de gate desta execução

| Gate | Step | Status | Artefato | Decisão / Observações |
|------|------|--------|----------|-----------------------|
| 06→07 | /arkan.analyze (obrigatório) | ✓ concluído | 08-qa/analyze-report.md | 0 CRITICAL, 2 HIGH corrigidos antes de avançar |
| 06→07 | /arkan.taskstoissues (opcional) | — pulado — | — | Dev optou por não criar issues |
| 07→08 | /arkan.verificaissues (condicional) | — N/A — | — | issues-map.md inexistente (taskstoissues não rodou) |
| 07→08 | /arkan.audit (opcional, preventivo) | ✓ concluído | 08-qa/audit-report.md v1.0 | Score 8/10, alimentou /arkan.qa |
| 08→09 | /arkan.audit (Fase 2.5, adversarial) | ✓ concluído | 08-qa/audit-report.md v2.0 | Score mantido, sem CRITICAL novo, gate liberado |

#### Debates desta execução

##### DEBATE-[NNN] — [Tópico]

- **Transição**: Fase [NN] → Fase [NN+1]
- **Questão**: [qual decisão foi tomada]
- **Posição recomendada**: [qual persona venceu e por quê]
- **Decisão final**: [confirmado / override: detalhe / pulado]
- **Evidências usadas**: [artefatos referenciados pelos agentes]
```

**4c. Verificar PÓS-CONDIÇÕES**:

`.arkan/scripts/check-prerequisites.sh --pos --command .claude/commands/arkan.pipeline.md`

## Guidelines

- Documentação em **PT-BR**
- O pipeline **não substitui** os commands individuais — delega a eles; cada command mantém sua autonomia quando invocado diretamente
- **Uma fase por vez**: nunca executar duas fases em paralelo — o pipeline é sequencial por design
- **Debates baseados em evidências**: argumentos sem referência a artefatos reais da feature são inválidos — refazer com evidências concretas antes de apresentar ao dev
- **Princípio VIII inviolável**: o dev pode sempre confirmar, rejeitar ou ignorar a recomendação do debate — o pipeline nunca pressiona implicitamente por uma escolha
- **Adversarial sempre na re-validação**: qualquer re-auditoria, re-validação ou re-revisão de correções DEVE ser feita por sub-agente independente com instrução adversarial explícita (ver Fase 2.5 e Inovação 4 do `arkan.debate.md`). O Princípio VIII (dev decide) **não substitui** verificação adversarial — apenas adiciona-se a ela
- **Fase 05-UX é opcional**: perguntar ao dev antes de entrar; se não aplicável, registrar no log e avançar
- **Pipeline pode ser pausado** em qualquer gate de transição — o estado é salvo no `pipeline-log.md` e o dev pode retomar com `--from [próxima fase]`
- **Retomada idempotente**: ao retomar com `--from`, não re-executar fases já concluídas — verificar artefatos existentes e registrar que foram encontrados como "pré-existentes"
- **Debate não bloqueia**: se o dev optar por pular (resposta "pular debate"), registrar no log e avançar sem penalidade
- **Sem debates em cascata**: um debate por transição; ao concluir, o pipeline avança sem acionar outro debate imediatamente
- Registrar cada decisão de debate no `pipeline-log.md` com fundamentação — futuros ciclos de `/arkan.ops` podem referenciar estas decisões como contexto histórico
- Se o indexador de código declarado em `.arkan/memory/stack.md` não estiver disponível na verificação de risco (transição planning→development): pedir ao dev se há tasks de alto impacto identificadas manualmente, e ativar debate apenas se dev confirmar
- **`/arkan.analyze` é obrigatório no gate 06→07** — não pergunta ao dev se quer rodar (Fase 2.4). Findings CRITICAL bloqueiam avanço; o dev pode aplicar correção, registrar override (Princípio VIII) ou pausar
- **`/arkan.verificaissues` é condicional no gate 07→08** — só dispara se `06-planning/issues-map.md` existe (Fase 2.6). Regressões bloqueiam avanço; inconsistências exigem decisão explícita do dev
- **`/arkan.audit` tem dois usos no pipeline**: (1) preventivo no gate 07→08, opcional, antes do `/arkan.qa` — alimenta o QA com achados de schema/migrations; (2) adversarial na Fase 2.5, automático condicional ao status do `qa-report.md`. Os dois produzem `audit-report.md` (versionado v1.0, v2.0, …) — não confundir os papéis
- **Cada artefato de gate vai ao `pipeline-log.md`**: `analyze-report.md`, `issues-audit.md`, `audit-report.md` (cada versão) devem ser referenciados na seção "Steps de gate desta execução" da execução corrente
