---
description: "Arkan transversal — Crítica heurística de UI/UX: lê artefato (ux-spec, componente, rota, plan) e produz reflexão adversarial contra Nielsen 10 + Hick/Fitts/Miller, delegando ao agente de domínio do projeto quando declarado em .arkan/config.md. Artefato sempre anexo — nunca modifica o alvo."
mode: assistencia
fase: transversal
nivel: feature | ad-hoc
tecnica: "Adversarial Heuristic Review + Chain-of-Thought + Princípio VIII"
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/memory/constitution.md
arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/check-prerequisites.sh
arquivo: .arkan/config.md
arquivo: .arkan/agents/transversal/ux-critic.md
arquivo: .arkan/templates/critica-ui/ux-heuristics-template.md

## PÓS-CONDIÇÕES

arquivo: <critica-artifact-path resolvido na Fase 5>

## User Input

```text
$ARGUMENTS
```

## Outline

Skill transversal que orquestra uma **crítica heurística estruturada** de um artefato UI/UX. Nunca decide por ele — apenas expõe findings com evidência e trade-offs, e (quando `.arkan/config.md` declara `agente-dominio`) delega reflexão de domínio a esse agente. O dev escolhe item a item; a skill grava o artefato anexo, rastreável e nunca modifica o alvo.

**Princípios invioláveis**:
- **Princípio III (Conclusividade)**: o artefato alvo **nunca é modificado** — a crítica é sempre anexo separado. Se o dev aceitar recomendações, ele edita o alvo em passo separado.
- **Princípio VIII (Agente Propõe, Humano Decide)**: cada recomendação é decidida **individualmente** pelo dev — aceita, rejeita ou difere. Não há decisão em bloco.
- **Corpus fechado**: Nielsen 10 + Hick + Fitts + Miller. Mudanças no corpus exigem novo debate transversal, não decisão local.
- **Fluxo → Corpus (ordem inegociável)**: o ux-critic lê o artefato primeiro, imagina persona, identifica atritos em linguagem natural, **depois** nomeia contra o corpus. Inverter a ordem vira checklist burocrático.

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

**Dois modos de profundidade** (mesma lógica do `/arkan.debate`):

| Modo | Default | Como funciona | Custo | Quando usar |
|---|---|---|---|---|
| **Simulado** | sim | Orquestrador redige as vozes (ux-critic + agente de domínio) em turnos do próprio moderador, carregando mentalmente os blocos `## PROMPT` dos agentes | baixo | Artefato resolvível com o contexto já em mão |
| **Profundo** (`--profundo`) | não | Cada agente vira uma chamada `Task` sequencial (ux-critic → agente de domínio), com contexto isolado e ferramentas próprias (Arkan-KB quando disponível, senão Read/Grep) | alto | Artefato grande, exige investigação; múltiplas telas do mesmo fluxo |

**Single-agent com delegação condicional**: diferente do debate (2-4 personas em paralelo), aqui há no máximo **2 agentes sequenciais**: `ux-critic` sempre, o agente declarado em `agente-dominio` (`.arkan/config.md`) quando preenchido. Execução sequencial porque o agente de domínio recebe os findings do ux-critic como input.

### Fase 0 — Setup (automático)

1. Executar `.arkan/scripts/check-prerequisites.sh --json --command .claude/commands/arkan.critica-ui.md`
   - Capturar `PROJECT`, `FEATURE_DIR`, `FEATURE_SLUG`, `FASE_ATUAL` do JSON
   - `FEATURE_DIR` vazio é **válido** (skill é transversal)
2. Ler `.arkan/config.md` e capturar o campo `agente-dominio` do frontmatter — guardar o valor (vazio ou nome do agente) para decidir a Fase 3
3. Carregar `.arkan/memory/constitution.md` (global) e constituição do projeto ativo se existir
4. Parsear `$ARGUMENTS` — extrair flags e alvo:

   | Flag | Efeito |
   |---|---|
   | `--alvo=<path>` | Caminho explícito do artefato alvo (ganha sempre) |
   | `--pergunta="<texto>"` | Pergunta dirigida personalizada; default: "qual é o pior momento deste artefato para o usuário?" |
   | `--sem-dominio` | Pula a delegação ao agente de domínio, mesmo com `agente-dominio` declarado; em conflito com `--com-dominio`, `--sem-dominio` vence |
   | `--com-dominio` | Força a tentativa de delegação e o aviso explícito quando `agente-dominio` está vazio — não ativa a fase sozinha (ver condição de ativação na Fase 3) |
   | `--profundo` | Ativa modo multi-subagent (Task sequencial ux-critic → agente de domínio) |

   Tudo que **não** for flag é ignorado (ao contrário do debate, a pergunta não vem no texto livre — vem via `--pergunta`).

5. **Resolver alvo** na seguinte ordem:
   - Se `--alvo=<path>` foi passado: usar direto
   - Se não foi passado e `FEATURE_DIR` existe e `$FEATURE_DIR/05-ux/ux-spec.md` existe: usar esse arquivo
   - Caso contrário: exibir tela de Uso e **parar**

6. **Tipar o alvo** após resolução:

   | Tipo de arquivo | Tratamento |
   |---|---|
   | `.md` | Ler como corpo único (ux-spec, plan, ideacao, debate, qualquer outro) |
   | `.tsx / .vue / .jsx` | Ler arquivo único + Grep rápido dos componentes irmãos importados (profundidade 1, max 5 arquivos) para enriquecer contexto |
   | Página de aplicação web que se compõe com layout ancestral | Mesma regra de `.tsx` + incluir o arquivo de layout ancestral mais próximo, se o framework do projeto tiver esse conceito |
   | Diretório | Glob `**/*.{tsx,vue,jsx}` limitado a **15 arquivos**; acima disso, listar e pedir afunilamento ao dev — **nunca processar silenciosamente** |

7. Se alvo resolvido não existe no disco: avisar o dev com caminho tentado e **parar**

8. Se `--alvo` ausente e `FEATURE_DIR` vazio: exibir tela de Uso e **parar**:

   ```
   Uso: /arkan.critica-ui [--alvo=<path>] [--pergunta="..."] [--sem-dominio] [--com-dominio] [--profundo]

   Exemplos:
     /arkan.critica-ui
       (default: usa $FEATURE_DIR/05-ux/ux-spec.md se feature ativa)

     /arkan.critica-ui --alvo=.arkan/features/<projeto>/110-000-exemplo/05-ux/ux-spec.md

     /arkan.critica-ui --alvo=src/components/formulario-cadastro.tsx \
                       --pergunta="este componente protege o usuário de erros de digitação?"

     /arkan.critica-ui --alvo=src/app/painel/ \
                       --sem-dominio

     /arkan.critica-ui --profundo --alvo=.arkan/features/<projeto>/112-000-exemplo/05-ux/ux-spec.md
   ```
   **Parar.**

### Fase 1 — Enquadramento

**Exibir cabeçalho**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  CRÍTICA-UI  ·  MODO: ASSISTÊNCIA
Agente: Moderador  ·  Step: Enquadramento
Alvo: [caminho curto]  ·  Profundidade: [simulado|profundo]
Domínio: [ativo (<agente>) | opt-out (--sem-dominio) | não (nenhum agente declarado)]
Técnica: Adversarial Heuristic Review + Chain-of-Thought
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Apresentar ao dev:

1. **Alvo detectado** — caminho absoluto + tipo (ux-spec | componente | rota | plan | diretório) + tamanho (linhas para arquivos `.md`, props+estados para `.tsx`, lista de arquivos para diretório)
2. **Projeto e domínio** — `PROJECT=<nome>`; se `.arkan/config.md` declara `agente-dominio` e não veio `--sem-dominio`, declarar que Fase 3 delegará a esse agente
3. **Corpus aplicado** (sempre fechado):
   - **Nielsen 10**: N1 Visibility, N2 Match Real World, N3 User Control, N4 Consistency, N5 Error Prevention, N6 Recognition vs Recall, N7 Flexibility, N8 Aesthetic Minimalist, N9 Error Recovery, N10 Help/Docs
   - **Leis cognitivas**: Hick (log₂ opções), Fitts (distância/largura alvo), Miller (7±2 chunks)
4. **Pergunta dirigida** — texto da flag `--pergunta` ou default: *"qual é o pior momento deste artefato para o usuário?"*
5. **Ordem de execução** — "Fase 2: ux-critic lê e produz Findings; Fase 3: agente de domínio recebe os findings e reflete pelo ângulo do domínio (se aplicável); Fase 4: síntese + decisão item a item"

**Aguardar confirmação do dev** antes de prosseguir. Dev pode:
- Confirmar (segue para Fase 2)
- Ajustar pergunta dirigida: `"reformular: <nova pergunta>"`
- Trocar alvo: `"alvo: <novo path>"`
- Desligar domínio: `"sem domínio"`
- Abortar

**Fallback**: se `.arkan/agents/transversal/ux-critic.md` não existir, **abortar com erro claro** — nunca usar descrição genérica. O agente é pré-condição.

### Fase 2 — Leitura Adversarial (ux-critic)

#### Modo Simulado (default)

O orquestrador lê `.arkan/agents/transversal/ux-critic.md` bloco `## PROMPT`, carrega mentalmente o corpus canônico (Nielsen 10 + Hick/Fitts/Miller), o Framework de 5 passos (Chain-of-Thought fluxo→corpus), e produz os Findings **em um único turno**, seguindo o **Formato de saída obrigatório** declarado no contrato do agente.

O orquestrador deve:

1. Ler o artefato alvo **por inteiro** (usar Read, respeitando o limite de 15 arquivos do Glob no caso de diretório)
2. Executar o Framework de reflexão em 5 passos **em ordem**:
   - Passo 1: ler integral (sem nomear heurística)
   - Passo 2: imaginar persona executando tarefa
   - Passo 3: listar pontos de atrito em linguagem natural
   - Passo 4: mapear cada atrito a 1-2 itens do corpus (descartar não-ancorados)
   - Passo 5: atribuir severidade (alta/média/baixa com critérios explícitos) e propor ação não-visual
3. Executar Self-Refine antes de emitir: ancoragem obrigatória, severidade honesta, evidência citada literalmente, máximo 5 Findings
4. Saída no formato obrigatório do ux-critic: `## Findings — UX Critic` + `### Contexto` + `### Persona e tarefa simuladas` + `### Findings` (tabela) + `### Atritos sem ancoragem no corpus (descartados ou redirecionados)` + `### Conflitos entre usabilidade e domínio sinalizados` + `### Status final`

#### Modo Profundo (`--profundo`)

Fazer **1 chamada** à tool `Task` com:

- `subagent_type`: `general-purpose`
- `description`: `"Crítica-UI: UX Critic analisa <alvo-curto>"`
- `prompt`: concatenar nesta ordem:
  1. Bloco `## PROMPT` completo de `.arkan/agents/transversal/ux-critic.md` (ler com Read antes de montar)
  2. Cabeçalho: `"Você é o UX Critic executando no modo profundo do /arkan.critica-ui. O alvo é: <caminho>. Tipo do alvo: <tipo>. Pergunta dirigida: <texto>. Sua análise deve respeitar os princípios I-VIII da constituição Arkan."`
  3. Contexto anexado: conteúdo completo do artefato alvo (se `.md`) OU lista de caminhos + conteúdo dos primeiros 3-5 arquivos (se diretório)
  4. Instrução final:
     ```
     Execute o Framework de reflexão em 5 passos na ordem especificada em
     .arkan/agents/transversal/ux-critic.md, usando exclusivamente o corpus
     canônico (Nielsen 10 + Hick/Fitts/Miller). Antes de emitir, execute
     mcp__arkan-kb__query({query: "<termo-chave-do-alvo>"}) para contexto (ou busca por texto, se não houver indexador).
     Retorne markdown no Formato de saída obrigatório declarado no seu contrato.
     Máximo 5 Findings. Sem preâmbulo.
     ```

Coletar o resultado e apresentar ao dev como **checkpoint opcional**:
```
Findings do UX Critic recebidos. Prosseguir para a Reflexão do Agente
de Domínio ou abortar?
```

### Fase 3 — Reflexão do Agente de Domínio (condicional)

**Condição de ativação**: campo `agente-dominio` preenchido em `.arkan/config.md` **E NÃO** `--sem-dominio`. Em conflito entre as duas chaves, **`--sem-dominio` vence**.

**Se condição for falsa** (nenhum agente de domínio declarado, ou agente declarado com `--sem-dominio`): **pular a fase inteira** e registrar na seção do template o valor correspondente do campo `Domínio delegado`:

```
Reflexão do Agente de Domínio
Domínio delegado: não (nenhum agente de domínio declarado) | opt-out (--sem-dominio)
```

**`--com-dominio`** não altera a condição acima — não inventa agente onde não há declaração. O que ela faz é forçar a tentativa e tornar explícito, na mensagem ao dev, que o pulo aconteceu apesar do pedido: com `agente-dominio` vazio, avisa que `.arkan/config.md` não declara agente de domínio e pula a fase da mesma forma.

Seguir direto para Fase 4.

#### Modo Simulado (default)

O orquestrador lê `.arkan/agents/transversal/<agente-dominio>.md` (caminho resolvido a partir do campo `agente-dominio` em `.arkan/config.md`) bloco `## PROMPT`, carrega mentalmente as Regras absolutas do agente (invariantes inegociáveis) e o Framework de reflexão declarado no contrato dele, e produz o parecer **em um único turno**, seguindo o **Formato de saída obrigatório** do contrato do agente.

**Input crítico**: o parecer do agente de domínio recebe como entrada **os Findings do ux-critic da Fase 2**, além do artefato alvo. O agente precisa ver os findings para poder detectar conflitos reais entre usabilidade e domínio em cima do que o UX Critic já sinalizou.

Pergunta dirigida derivada automaticamente para o agente de domínio:
> *"Este artefato respeita os invariantes declarados no seu arquivo de agente? Algum achado de usabilidade da Fase 2 entra em conflito com eles?"*

Saída no formato obrigatório do agente de domínio, definido pelo seu próprio contrato — o command espera minimamente: `## Reflexão do Agente de Domínio` + `### Contexto` + `### Áreas do domínio impactadas` + `### Regras do domínio em jogo` (tabela) + `### Conflitos entre usabilidade e domínio detectados` + `### Limites do domínio atingidos` + `### Carga cognitiva` + `### Recomendações do agente de domínio` + `### Invariantes do domínio verificados` + `### Status final (Agente de Domínio)`.

**Se o agente de domínio retornar `Fora do escopo do domínio`**: registrar a seção como info curta (3 linhas: status + justificativa do agente + "Fase 4 prosseguirá sem contribuição de domínio") — **não alertar como problema**. Rigor é seletivo.

#### Modo Profundo (`--profundo`)

Fazer **1 chamada sequencial** (não paralela com Fase 2) à tool `Task` com:

- `subagent_type`: `general-purpose`
- `description`: `"Crítica-UI: agente de domínio reflete sobre <alvo-curto>"`
- `prompt`: concatenar nesta ordem:
  1. Bloco `## PROMPT` completo do arquivo declarado em `agente-dominio` (`.arkan/agents/transversal/<agente-dominio>.md`, ler com Read antes de montar)
  2. Cabeçalho: `"Você é o agente de domínio executando no modo profundo do /arkan.critica-ui. O alvo é: <caminho>. Fase do alvo: <05-ux ou ad-hoc ou produção>. Pergunta dirigida: <pergunta derivada acima>."`
  3. Contexto anexado: conteúdo do artefato alvo + **Findings completos do UX Critic** (resultado literal da Fase 2)
  4. Instrução final:
     ```
     Execute o framework de reflexão especificado no seu próprio contrato,
     na ordem nele definida. Dê atenção especial aos conflitos entre
     usabilidade e domínio que o crítico tenha sinalizado na Fase 2.
     Antes de emitir, verifique rastreabilidade de cada
     recomendação à documentação de domínio declarada em
     `.arkan/memory/stack.md`.
     Retorne markdown no formato de saída obrigatório declarado no seu contrato.
     Sem preâmbulo.
     ```

Coletar o resultado e apresentar ao dev.

### Fase 4 — Síntese e Priorização

O **orquestrador** (nunca subagent) redige a síntese combinando:

1. **Conflitos entre usabilidade e domínio (resolução)** — consolidar todos os conflitos detectados pelo UX Critic (Fase 2) e/ou pelo agente de domínio (Fase 3). Aplicar a regra:

   > Quando há regra de domínio em jogo, **o domínio vence** — convenção herdada; se o projeto adotante declarar outra regra de resolução, ela prevalece. UX Critic propõe X, agente de domínio propõe Z → Z prevalece. Registrar o conflito como aprendizado, não como bloqueio.

   Formato:

   ```markdown
   ## Conflitos entre usabilidade e domínio

   | # | Heurística UX | Regra de domínio | Decisão | Justificativa |
   |---|---|---|---|---|
   | 1 | N5 Error Prevention | [regra do domínio] | domínio vence | [trecho da documentação de domínio] |
   ```

   Se nenhum: "Nenhum conflito entre usabilidade e domínio detectado."

2. **Síntese priorizada** — tabela unificada com todas as ações propostas (findings UX + recomendações do agente de domínio), ordenada por severidade:

   ```markdown
   ## Síntese e Priorização

   | # | Ação proposta | Origem | Severidade | Esforço estimado | Decisão do dev |
   |---|---|---|---|---|---|
   | 1 | [ação concreta não-visual] | ux-critic / agente de domínio / ambos | alta | ~2h | [aguardando] |
   | 2 | [...] | ... | média | ~1h | [aguardando] |
   ```

   Esforço estimado é opcional — se o orquestrador não tem base para estimar, usar `não estimado`.

3. **Apresentar ao dev** a tabela de síntese e **aguardar decisão item a item** (Princípio VIII):

   Dev pode responder:
   - `1: aceita, 2: rejeita, 3: difere` — decisão explícita por item
   - `tudo: aceita` — atalho para todos aceitos
   - `tudo: difere` — atalho para todos diferidos
   - `X: justificar <texto>` — para rejeições com justificativa
   - `pular para gravação` — aceita tudo silenciosamente (registrado como "aceita sem comentário")

   **Não avançar** para Fase 5 enquanto houver itens sem decisão, exceto se dev responder `pular para gravação`.

4. **Regra absoluta**: o command **nunca** edita o artefato alvo. Se o dev aceita recomendações, ele fará as edições em passo separado, depois. Este command só produz o artefato de crítica. Princípio III preservado.

### Fase 5 — Gravação do artefato

**Resolver caminho** conforme contexto:

| Situação | Caminho |
|---|---|
| `FEATURE_DIR` definido e alvo **dentro** da feature (ou alvo default `$FEATURE_DIR/05-ux/ux-spec.md`) | `$FEATURE_DIR/05-ux/critica/YYYY-MM-DD-<slug>.md` |
| `FEATURE_DIR` definido e alvo **fora** da feature (ex: componente em `src/components/...`) | `.arkan/critica-ui/ad-hoc/YYYY-MM-DD-<slug>.md` |
| `FEATURE_DIR` vazio (transversal puro) | `.arkan/critica-ui/transversal/YYYY-MM-DD-<slug>.md` |

**Slug**: kebab-case do nome do arquivo/diretório alvo (sem extensão), max 40 chars, PT-BR. Se alvo é ux-spec.md: `ux-spec`. Se alvo é `src/components/formulario-cadastro.tsx`: `formulario-cadastro`. Se alvo é diretório: nome do diretório folha.

**Criar diretório pai se não existir** (`mkdir -p`). Data em ISO `YYYY-MM-DD`. Se já existe artefato no mesmo dia com mesmo slug, sufixar `-2`, `-3`, etc.

**Template inline** do artefato (espelha `.arkan/templates/critica-ui/ux-heuristics-template.md` — manter sincronizados):

```markdown
---
title: Crítica UI/UX — <alvo>
status: em-construcao
updated: YYYY-MM-DD
---

# Crítica UI/UX — <alvo>

**Data**: YYYY-MM-DD
**Alvo**: <caminho absoluto + tipo>
**Feature**: <slug ou "transversal">
**Fase do alvo**: <05-ux | produção | rascunho | ad-hoc>
**Projeto**: <PROJECT>
**Corpus**: Nielsen 10 + Hick + Fitts + Miller
**Pergunta dirigida**: <texto>
**Domínio delegado**: sim (<agente>) | não (nenhum agente de domínio declarado) | opt-out (`--sem-dominio`) | N/A (fora do escopo do domínio)
**Profundidade**: simulado | profundo
**Orquestrador**: Arkan Crítica-UI (`.claude/commands/arkan.critica-ui.md`)

## Alvo analisado
<resumo + caminhos lidos>

## Pergunta dirigida
<texto>

## Leitura Adversarial — UX Critic
<saída completa do ux-critic no formato obrigatório: Contexto, Persona, Findings, Atritos sem ancoragem, Conflitos entre usabilidade e domínio sinalizados, Status>

## Reflexão do Agente de Domínio
<saída completa do agente OU a linha registrada na Fase 3 quando a delegação foi pulada ("não" ou "opt-out", conforme o motivo)>

## Conflitos entre usabilidade e domínio (resolução)
<tabela consolidada OU "Nenhum conflito entre usabilidade e domínio detectado">

## Síntese e Priorização
<tabela priorizada>

## Decisão
**Aceitas**: <lista>
**Rejeitadas**: <lista com justificativas>
**Diferidas**: <lista com motivos>
**Justificativa do dev**: <texto>
**Impacto no artefato alvo**: <arquivos que o dev pretende editar — command NÃO edita>

## Histórico
- YYYY-MM-DD HH:MM — crítica iniciada (alvo: ...)
- YYYY-MM-DD HH:MM — findings ux-critic registrados
- YYYY-MM-DD HH:MM — parecer do agente de domínio registrado (ou N/A)
- YYYY-MM-DD HH:MM — síntese apresentada
- YYYY-MM-DD HH:MM — decisão do dev registrada
```

**Se dev pulou decisões** (`pular para gravação`): gravar tudo normalmente, e na seção `## Decisão` registrar "Todas as ações aceitas sem comentário — dev optou por pular revisão item a item".

**Este comando não tem `--anexar`** (diferente do `/arkan.debate`): o artefato de crítica **sempre** é anexo separado, nunca sobrescreve nem faz append no alvo. Modificar o alvo violaria Princípio III.

### Fase 6 — Finalização

1. Reportar ao dev:
   - Caminho absoluto do artefato criado (clicável)
   - Sumário de 3 linhas:
     - **Alvo**: `<caminho-curto>` (N linhas / M componentes)
     - **Findings**: X altos, Y médios, Z baixos. Domínio: [aprovado | ressalvas | requer revisão | não (nenhum agente de domínio declarado) | opt-out (`--sem-dominio`) | fora do escopo do domínio]
     - **Decisão**: N aceitas, M rejeitadas, K diferidas
2. **Sugerir** commit message (não executar commit):
   ```
   chore(arkan): critica-ui — <alvo-curto> [feature: <slug ou "transversal">]
   ```
3. **Nunca** rodar `git commit` automaticamente (Princípio VIII).
4. **Nunca** editar o artefato alvo como "favor" ao dev — mesmo se ele aceitou todas as recomendações. As edições do alvo são responsabilidade separada do dev, em outro turno.

## Guidelines

- Documentação e artefatos em **PT-BR**
- **Princípio III (Conclusividade)**: o artefato alvo **nunca é modificado** sob nenhuma circunstância — a crítica é sempre anexo. Isso não é preferência, é invariante.
- **Princípio VIII**: decisão por item, não em bloco. Command **nunca** fecha Fase 4 sem input explícito do dev (exceto com `pular para gravação`, que ainda é decisão explícita).
- **Corpus fechado**: Nielsen 10 + Hick/Fitts/Miller. Nunca citar Shneiderman, Lidwell, WCAG ou outros — mudanças exigem novo debate transversal, não decisão local.
- **Ordem fluxo→corpus**: o ux-critic deve começar pelo artefato e pela persona, não pelo checklist. Inverter essa ordem é bug semântico.
- **Single-agent + delegação condicional**: no máximo 2 agentes (ux-critic sempre, o agente declarado em `agente-dominio` se aplicável). **Sequencial**, nunca paralelo — o agente de domínio precisa dos findings do ux-critic.
- **Não invocar** esta skill recursivamente (crítica da crítica).
- **Não invocar** esta skill contra o artefato desta própria skill — auto-referência é bug.
- **Fallback**: se `.arkan/agents/transversal/ux-critic.md` não existir, abortar com erro claro. Nunca usar descrição genérica.
- **Delegação de domínio automática** quando `.arkan/config.md` declara `agente-dominio`; sem declaração, a Fase 3 é pulada e registrada como `não (nenhum agente de domínio declarado)` no artefato.
- **Máximo 5 Findings** por crítica — mais que isso é ruído. Força priorização.
- **Severidade baseada em critério explícito**, não em feeling: alta = bloqueador, média = fricção real, baixa = polimento.
- **Evidência obrigatória**: toda recomendação tem trecho **citado literalmente** do artefato alvo. Paráfrase = descartar.
- **Não prescrever visual**: propostas descrevem comportamento, nunca CSS, cores, espaçamentos, fontes, tamanhos. O dev decide apresentação.
- **Conflitos entre usabilidade e domínio**: UX Critic sinaliza, o agente de domínio (quando delegado) resolve. Quando há regra de domínio em jogo, o domínio vence — aprendizado registrado no artefato, não bloqueio do fluxo.
- **Artefato de crítica é permanente** — faz parte do histórico de decisão do projeto. Nunca deletar, apenas superseder com nova crítica datada.
- **Commit nunca é automático** — apenas sugestão no final.
- **Nunca inventar heurística**: se não está no corpus canônico, é atrito sem ancoragem, vai para a lista de descartados.
- **Skill transversal**: funciona com `FEATURE_DIR` vazio. Nunca bloqueia por falta de feature ativa — apenas ajusta o caminho do artefato.
