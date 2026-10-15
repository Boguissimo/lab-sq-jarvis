---
description: "Arkan — Debug estruturado: orquestra triagem, investigacao, correcao, verificacao e registro de bugs com artefatos rastreaveis."
mode: orquestracao
fase: transversal
nivel: ad-hoc
tecnica: "ReAct + Socratic Prompting + Chain-of-Verification"
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/memory/constitution.md
arquivo: .arkan/agents/debug/triage-agent.md
arquivo: .arkan/agents/debug/investigator-agent.md
arquivo: .arkan/templates/debug/bug-report-template.md

## PÓS-CONDIÇÕES

arquivo: $REPORT_FILE
arquivo: .arkan/memory/bugfixes.md
campo-obrigatorio: ## 4. Causa Raiz in $REPORT_FILE
campo-obrigatorio: ## 7. Registro in $REPORT_FILE

## Outline

O texto apos `/arkan.debug` e a descricao do bug. Flags opcionais:

- `--orfao` — bug sem feature associada (salva em `.arkan/debug/`)
- `--prod` — forcar modo producao (override da deteccao automatica)
- `--feature NNN-slug` — ancorar em feature especifica (override da deteccao por branch)

Se nenhum texto fornecido: perguntar ao dev "Descreva o bug que voce observou."

### Fase 0 — Setup (automatico)

1. **Identificar feature**:
   - Se `--feature NNN-slug` passado: usar diretamente
   - Se `--orfao` passado: modo orfao, `DEBUG_DIR = .arkan/debug/`
   - Caso contrario: inferir da branch git ativa
     ```bash
     BRANCH=$(git branch --show-current)
     ```
     - Buscar feature correspondente em `.arkan/features/*/` pelo nome da branch
     - Se encontrada: `FEATURE_DIR` resolvido, `DEBUG_DIR = $FEATURE_DIR/debug/`
     - Se nao encontrada: perguntar ao dev — ancorar em feature ou modo orfao

2. **Detectar modo**:
   - Se `--prod` passado: modo producao
   - Se `FEATURE_DIR` resolvido: ler `$FEATURE_DIR/status.md`
     - Se `status: em-producao`: modo producao
     - Caso contrario: modo desenvolvimento
   - Se orfao: modo desenvolvimento (default)

3. **Criar estrutura**:
   ```bash
   mkdir -p "$DEBUG_DIR"
   ```
   - Determinar `BUG_NUMBER`: contar `bug-report-*.md` existentes em `$DEBUG_DIR` + 1
   - `BUG_ID = BUG-$(date +%Y%m%d)-$(printf "%03d" $BUG_NUMBER)`
   - `REPORT_FILE = $DEBUG_DIR/bug-report-$(printf "%03d" $BUG_NUMBER).md`

4. **Exibir cabecalho**:
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ARKAN  ·  DEBUG  ·  MODO: ORQUESTRACAO
   Feature: [NNN-slug ou "orfao"]
   Modo: [Desenvolvimento / Producao]
   Bug ID: [BUG-YYYYMMDD-NNN]
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

### Fase 1 — Triagem

**Exibir cabecalho**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  DEBUG  ·  TRIAGEM
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

> Agente: Triage Agent → .arkan/agents/debug/triage-agent.md

**Instrucao**: Ler `.arkan/agents/debug/triage-agent.md` e executar conforme `## PROMPT` do agente. Verificar `## PRE-CONDICOES` antes de iniciar; validar `## POS-CONDICOES` ao concluir.

Antes de ativar o agente, injetar: descricao do bug ($ARGUMENTS), feature identificada, modo detectado.

Ao concluir, o Triage Agent entrega:
- Sintoma estruturado
- Classificacao (1 das 6 categorias)
- Status de reproducao
- Se producao: avaliacao de impacto

### Fase 2 — Investigacao

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

**Exibir cabecalho**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  DEBUG  ·  INVESTIGACAO
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

> Agente: Investigator Agent → .arkan/agents/debug/investigator-agent.md

**Instrucao**: Ler `.arkan/agents/debug/investigator-agent.md` e executar conforme `## PROMPT` do agente. Verificar `## PRE-CONDICOES` antes de iniciar; validar `## POS-CONDICOES` ao concluir.

Antes de ativar o agente, injetar: saida do Triage Agent (sintoma, classificacao, reproducao), feature e modo.

Ao concluir, o Investigator Agent entrega:
- Causa raiz com evidencia
- Hipoteses investigadas (confirmadas e descartadas)
- Proposta de correcao minima
- Ferramentas usadas

**Decisao do dev** (obrigatoria — Constitution VIII):
```
Aplicar esta correcao? (sim / ajustar / investigar mais)
```

- Se "sim": avancar para Fase 3
- Se "ajustar": dev descreve ajuste, Investigator refina proposta
- Se "investigar mais": Investigator amplia busca com novo contexto do dev

### Fase 3 — Correcao

O desenvolvedor aplica o fix. O agente pode assistir se solicitado:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  DEBUG  ·  CORRECAO
Acao esperada: desenvolvedor aplica o fix
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Proposta de correcao:
  Arquivo: [caminho]
  Mudanca: [descricao]

Deseja que eu assista na aplicacao? (sim / nao — ja apliquei)
```

- Se "sim": aplicar as mudancas propostas usando Edit/Write tools
- Se "nao": dev ja aplicou, avancar para verificacao

**NUNCA aplicar fix sem confirmacao explicita do dev.**

### Fase 4 — Verificacao

**4a. Aligner (se feature possui spec.md)**:

> Agente: Aligner → .arkan/agents/transversal/aligner.md

Invocar Aligner com:
- `spec.md` da feature (se existir)
- Codigo modificado pelo fix
- Foco: verificar que o fix nao introduziu divergencia spec→codigo

Se feature nao possui spec.md: pular Aligner e registrar como "N/A — sem spec".

**4b. Checklist de nao-regressao**:

Carregar `.arkan/templates/debug/fix-verification-checklist.md` e percorrer com o dev:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  DEBUG  ·  VERIFICACAO
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Aligner: [Alinhado / Divergencia: detalhe / N/A]

Checklist de nao-regressao:
  [✓/✗] Fix resolve o sintoma original
  [✓/✗] Nao introduz novos erros
  [✓/✗] Fluxos adjacentes intactos
  [✓/✗] Invariantes respeitados
  [✓/✗] TypeScript compila (se aplicavel)

Resultado: [APROVADO / REPROVADO — motivo]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Se REPROVADO: retornar a Fase 3 para ajuste do fix.

### Fase 5 — Registro

**5a. Gerar bug-report**:

Preencher `.arkan/templates/debug/bug-report-template.md` com todos os dados coletados nas fases anteriores. Salvar como `$REPORT_FILE`.

**5b. Atualizar bugfixes.md**:

Adicionar entrada em `.arkan/memory/bugfixes.md`:

```markdown
| BUG-YYYYMMDD-NNN | NNN-slug | Classificacao | Causa raiz (1 linha) | Fix (1 linha) | YYYY-MM-DD |
```

**5c. Retroalimentacao producao** (apenas modo producao):

Se modo producao e feature possui diretorio `10-ops/`:
- Criar ou atualizar referencia ao bug-report em `$FEATURE_DIR/10-ops/`

**5d. Exibir resumo final**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  DEBUG  ·  CONCLUIDO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Bug: [BUG-YYYYMMDD-NNN]
Feature: [NNN-slug ou "orfao"]
Classificacao: [tipo]
Modo: [dev / producao]
Causa raiz: [1 linha]
Fix: [1 linha]
Verificacao: [APROVADO]

Artefatos gerados:
  [REPORT_FILE]
  .arkan/memory/bugfixes.md (atualizado)
  [Se producao: $FEATURE_DIR/10-ops/ (referenciado)]

Sugerir: git add + commit do fix e artefatos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Guidelines

- Documentacao em **PT-BR**
- **Constitution VIII inviolavel**: NUNCA aplicar fix sem confirmacao do dev
- **Framework obrigatorio**: os 7 steps do bug-report devem estar presentes, mesmo com profundidade minima
- **Cascata de ferramentas**: arkan-kb (ou busca por texto, se não houver indexador) → grep (registrar qual foi usada)
- **Correcao minima**: nao "melhorar" codigo adjacente ao bug — apenas corrigir a causa raiz
- **Aligner opcional**: so invocado se feature possui spec.md; caso contrario, N/A
- **Bug orfao**: se nenhuma feature identificavel e dev confirma, salvar em `.arkan/debug/`
- **Modo producao**: steps adicionais (impacto, mitigacao, referencia em 10-ops/) sao obrigatorios
- **Transparencia**: hipoteses descartadas devem ser registradas no bug-report (nao so a confirmada)
- **Eficiencia**: maximo 3 perguntas na triagem, maximo 3 hipoteses na investigacao
- Nao criar branch git automaticamente — sugerir ao dev se fix e complexo (>3 arquivos)
