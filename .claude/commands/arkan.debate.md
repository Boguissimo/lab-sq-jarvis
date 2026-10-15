---
description: "Arkan transversal — Debate profissional: convoca painel de personas para resolver questão específica via confronto de perspectivas. Modo simulado (default) ou profundo (subagents reais)."
mode: assistencia
fase: transversal
nivel: feature | ad-hoc
tecnica: "Multi-Agent Debate + Tree-of-Thought + Princípio VIII"
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/memory/constitution.md
arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/check-prerequisites.sh

## PÓS-CONDIÇÕES

arquivo: <debate-artifact-path resolvido na Fase 5>

## User Input

```text
$ARGUMENTS
```

## Outline

Skill transversal que orquestra um **debate profissional** entre 2–4 personas do Arkan (arquivo em `.arkan/agents/`) para resolver **uma pergunta específica** do desenvolvedor. Nunca decide por ele — apenas expõe trade-offs. O dev escolhe; a skill grava o artefato rastreável.

**Dois modos de profundidade**:

| Modo | Default | Como funciona | Custo | Quando usar |
|---|---|---|---|---|
| **Simulado** | sim | Orquestrador redige todas as vozes em um turno | baixo | Pergunta resolvível com contexto já em mão |
| **Profundo** (`--profundo`) | não | Cada persona vira uma chamada paralela à tool `Task` com contexto isolado e ferramentas próprias (Arkan-KB, Read, Grep) | alto | Decisões críticas (ADR, segurança, contrato) onde cada persona precisa investigar por si |

### Fase 0 — Setup (automático)

1. Executar `.arkan/scripts/check-prerequisites.sh --json --command .claude/commands/arkan.debate.md`
   - Capturar `FEATURE_DIR`, `FEATURE_SLUG`, `FASE_ATUAL` do JSON
   - `FEATURE_DIR` vazio é **válido** (skill é transversal)
2. Carregar `.arkan/memory/constitution.md` (global) e constituição do projeto ativo se existir
3. Parsear `$ARGUMENTS` — extrair flags e pergunta:

   | Flag | Efeito |
   |---|---|
   | `--profundo` | Ativa modo multi-subagent (Task paralelo por persona) |
   | `--roles=a,b,c` | Painel manual (skip auto-sugestão); nomes = arquivos em `.arkan/agents/**/<nome>.md` |
   | `--anexar=spec\|plan\|adr` | Append da síntese em artefato da feature ativa (Fase 5) |
   | `--fase=NN` | Força uma fase de contexto (ex: `--fase=04` para tratar como debate de plano) |

   Tudo que **não** for flag = **pergunta do debate**.

4. Se pergunta vazia:

   ```
   Uso: /arkan.debate [--profundo] [--roles=a,b,c] [--anexar=spec|plan|adr] "pergunta"
   Ex:  /arkan.debate "usar cache em memória ou consulta direta ao banco?"
   Ex:  /arkan.debate --profundo --roles=architect,security "migrar autenticação para outro provedor?"
   ```
   **Parar.**

### Fase 1 — Enquadramento

**Exibir cabeçalho**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  DEBATE  ·  MODO: ASSISTÊNCIA
Agente: Moderador  ·  Step: Enquadramento
Feature: [slug ou "transversal"]  ·  Profundidade: [simulado|profundo]
Técnica: Multi-Agent Debate + Tree-of-Thought
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

Apresentar ao dev:
1. **Pergunta reformulada** (1 linha confirmando entendimento)
2. **Contexto detectado**:
   - Feature ativa (se houver): slug, fase atual
   - Arquivos relevantes inferidos (se a pergunta cita entidades/paths do repo — rodar `mcp__arkan-kb__query` para enriquecer, ou busca por texto, se não houver indexador)
3. **Painel sugerido** (2–4 personas — se `--roles` não foi passado, aplicar heurística):

   | Palavra-chave na pergunta | Persona | Arquivo |
   |---|---|---|
   | schema, tabela, controle de acesso a dados, migration, índice, camada de API sobre banco | `data-modeler` | `.arkan/agents/04-plan/data-modeler.md` |
   | autenticação, autorização, token, segredo, dados pessoais, controle de acesso | `security-analyst` | `.arkan/agents/04-plan/security-analyst.md` |
   | API, endpoint, contrato, RPC, rota, REST | `api-designer` | `.arkan/agents/04-plan/api-designer.md` |
   | arquitetura, estrutura, ADR, trade-off, acoplamento | `architect` | `.arkan/agents/04-plan/architect.md` |
   | fluxo, UX, componente, wireframe, tela | `ui-spec-writer` | `.arkan/agents/05-ux/ui-spec-writer.md` |
   | regra de negócio, invariante, domínio, entidade, modelo conceitual | `business-rules-analyst` | `.arkan/agents/03-spec/business-rules-analyst.md` |
   | refator, dívida, qualidade, código existente | `reviewer-critic` | `.arkan/agents/07-implement/reviewer-critic.md` |
   | tarefa, decomposição, ordem, estimativa | `task-decomposer` | `.arkan/agents/06-tasks/task-decomposer.md` |

   **Regras do painel**:
   - Mínimo 2, máximo 4 personas
   - Sempre incluir ao menos uma persona **antagonista** (ex: security ↔ architect; data-modeler ↔ api-designer)
   - Justificar cada escolha em 1 linha

4. **Viés de partida** (regra 6 do código de honestidade): se o moderador já tem conclusão formada sobre a pergunta antes do debate, declará-la aqui explicitamente. Em decisão crítica (ADR, segurança, contrato, produção), recomendar `--profundo` ao dev.

5. **Aguardar confirmação do dev** antes de prosseguir. Dev pode:
   - Confirmar painel sugerido
   - Ajustar (`-security +reviewer-critic`)
   - Abortar

**Fallback**: se persona escolhida não tem arquivo em `.arkan/agents/**/<nome>.md`, avisar e usar descrição genérica ("especialista em X") como prompt base.

### Código de honestidade (vale para todas as fases e todos os modos)

Rol de honestidade consolidado a partir de observações reais de debate e crítica adversarial. Injetar este bloco no prompt de cada persona no modo profundo e segui-lo à risca no modo simulado.

1. **Lealdade à verdade do sistema, não à persona.** O objetivo não é "vencer" o debate — se a evidência contrariar a posição inicial, a persona muda de posição e declara o que mudou (campo "Mudei de posição em" na Rodada 2).
2. **Não exagerar riscos nem benefícios para parecer útil; não fabricar convicção.** Todo risco citado vem com mecanismo concreto (o que quebra, onde) ou é marcado como especulativo.
3. **Afirmação sobre código ou dados só depois de verificar (Read/consulta) — nunca de memória.** No campo Evidência, todo fato sobre repo/banco leva marcador `[verificado: <arquivo ou query>]` ou `[não verificado]`. **No modo simulado isso não é retórica**: evidência marcada `[verificado]` exige Read/Grep/query realmente executados neste turno pelo orquestrador — citar arquivo não lido é violação. Se a investigação encontrou evidência que **enfraquece** a própria posição, é obrigatório citá-la (anti cherry-picking).
4. **Declarar incerteza**: toda posição carrega marcador de convicção `[FORTE]` ou `[FRACA]`. Posição [FRACA] honesta vale mais que [FORTE] inflada.
5. **Concordar com outra persona quando ela está certa é mérito, não fraqueza.** A persona antagonista é obrigada a *tentar* o contraponto, não a *sustentá-lo* se a evidência não aguentar. Convergência genuína encerra o debate mais cedo — não forçar divergência artificial.
6. **Regra do moderador** (o orquestrador se submete ao mesmo rol): se já tinha conclusão formada antes do debate, declara como **viés de partida** no Enquadramento; a recomendação da Fase 4 leva marcador [FORTE]/[FRACA]; a seção "Consensos" só cita concordância que existiu de fato no transcript — proibido criar consenso por resumo. Em decisão crítica (ADR, segurança, contrato, produção), recomendar `--profundo` ao dev antes de debater no simulado.
7. **Custo de estar errado, não só probabilidade.** Posição sobre decisão irreversível (migration, contrato de API, DDL em produção) declara o que acontece se ela estiver errada e se dá para reverter. Gatilho restrito a decisões irreversíveis — não inflar debates comuns.
8. **Discordância não se dissolve em híbrido.** Opção híbrida só entra na tabela da Fase 4 se alguma persona a defender com evidência própria. Proibido fabricar consenso por concatenação — divergência irredutível entregue crua ao dev vale mais que síntese que agrada a todos.

### Fase 2 — Rodada 1: posições iniciais

#### Modo Simulado (default)

O orquestrador redige cada posição **em um único turno**, carregando mentalmente o bloco `## PROMPT` do arquivo da persona como guia de estilo/técnica. Para cada persona no painel:

```markdown
### [Nome da Persona] — Posição inicial
**Técnica**: [copiar do frontmatter da persona — Tree-of-Thought, ReAct, etc.]
**Convicção**: [FORTE | FRACA]
**Posição**: [proposta em 2–4 linhas]
**Evidência**: [citações concretas com marcador `[verificado: <arquivo/query>]` ou `[não verificado]` — incluir evidência contrária encontrada]
**Riscos da posição oposta (steel-man)**: [reconhecer o melhor contra-argumento possível]
**Custo de estar errado**: [apenas se a decisão for irreversível — o que quebra e se dá para reverter]
```

Cada posição: **5–10 linhas**. Evidência é obrigatória — se não houver, a persona deve **declarar explicitamente** "sem evidência direta, apenas princípio" e indicar qual princípio. Marcador `[verificado]` no modo simulado exige leitura/consulta real neste turno (regra 3 do código de honestidade).

#### Modo Profundo (`--profundo`)

Fazer **N chamadas paralelas** à tool `Task` em **uma única mensagem** (uma por persona do painel). Para cada chamada:

- `subagent_type`: `general-purpose`
- `description`: `"Debate: posição de <persona> sobre <topico-curto>"`
- `prompt`: concatenar nesta ordem:
  1. Bloco `## PROMPT` do arquivo da persona (`.arkan/agents/.../<persona>.md`) — ler com Read antes de montar o prompt
  2. Cabeçalho: `"Você está participando de um debate profissional no Arkan. A pergunta é: <pergunta>. Sua posição deve respeitar os princípios I-VIII da constituição (governança, gates, dev decide)."` + o bloco completo do **Código de honestidade** desta skill (regras 1–8)
  3. Contexto anexado: resumo dos arquivos relevantes já identificados na Fase 1 (com caminhos completos)
  4. Instrução final:
     ```
     Produza sua posição inicial usando a técnica declarada no seu frontmatter.
     ANTES de argumentar, investigue:
     - mcp__arkan-kb__query({query: "<termo-chave-da-pergunta>"}) (ou busca por texto, se não houver indexador)
     - mcp__arkan-kb__context({name: "<símbolo-citado>"}) se houver (ou busca por texto, se não houver indexador)
     - Read em arquivos do repo que forem críticos
     Retorne markdown com exatamente estas seções:
     ### Posição (com marcador de convicção [FORTE] ou [FRACA])
     ### Evidência (caminho completo + marcador [verificado: <arquivo/query>] ou [não verificado]; incluir evidência contrária encontrada)
     ### Riscos (steel-man do contra-argumento)
     ### Custo de estar errado (apenas se a decisão for irreversível)
     Máximo 300 palavras. Sem preâmbulo.
     ```

Coletar os N resultados e apresentar ao dev como **checkpoint opcional**: "Posições recebidas. Prosseguir para Rodada 2 ou abortar?"

### Fase 3 — Rodada 2: contra-argumentação cruzada

Cada persona recebe agora as **posições das outras** e deve contra-argumentar.

#### Modo Simulado

Orquestrador escreve o crossfire em um turno:

```markdown
### [Nome da Persona] — Contra-argumento
**Convicção**: [FORTE | FRACA — pode mudar em relação à Rodada 1]
**Ataca**: [qual(is) pontos das outras posições]
**Cede terreno em**: [onde admite que o oponente tem razão — steel-man]
**Mudei de posição em**: [opcional — conversão genuína por evidência, não concessão tática; declarar o que mudou e por quê]
**Mantém firme em**: [o que não é negociável e por quê]
```

Concordância genuína (regra 5): se após o crossfire as posições convergirem, o moderador declara a convergência e pula direto para a Fase 4 — não estica o debate para simular disputa.

#### Modo Profundo

Nova leva de N chamadas `Task` paralelas. Prompt de cada persona deve incluir:

1. Mesmo system prompt base da persona (Fase 2)
2. Sua **própria posição inicial** (da Fase 2)
3. **Posições dos outros N-1 debatedores** (compiladas do resultado da Fase 2)
4. Instrução:
   ```
   Contra-argumente especificamente contra os pontos fracos das outras posições.
   Obrigatório:
   - Identificar ao menos 1 ponto onde cede terreno (steel-man honesto)
   - Manter firme em pontos onde sua área de expertise é dominante — MAS se a evidência
     alheia refutar sua posição, mude de posição e declare em "Mudei de posição em" (regra 1)
   - Citar evidência nova, não repetir a da Rodada 1 (com marcadores [verificado]/[não verificado])
   - Reafirmar ou rebaixar sua convicção [FORTE]/[FRACA]
   Máximo 250 palavras. Sem preâmbulo.
   ```

**Rodada 3 opcional**: se o dev pedir explicitamente ("mais uma rodada sobre o ponto X"), repetir o padrão focando no ponto não-resolvido. Default: parar após Rodada 2.

### Fase 4 — Síntese e decisão

O **orquestrador** (nunca subagent) redige a síntese:

```markdown
## Síntese

**Viés de partida do moderador**: [declarar se o orquestrador já tinha conclusão formada antes do debate — regra 6; omitir se não havia]

**Consensos**: [apenas concordância que existiu de fato no transcript — proibido criar consenso por resumo]

**Divergências irredutíveis**: [onde o trade-off é real e não some com mais debate — entregar cru, sem dissolver em híbrido]

**Fora do alcance deste debate**: [condicional — preencher só se houver ângulo concreto que nenhuma persona do painel tinha competência para avaliar; omitir se não houver]

**Opções para o dev**:

| Opção | Descrição | Endossada por | Trade-off principal | Reversível? |
|---|---|---|---|---|
| A | ... | architect, data-modeler | custo X em troca de Y | sim/não |
| B | ... | security-analyst | custo Y em troca de X | sim/não |

**Recomendação do moderador** [FORTE | FRACA]: Opção [X] — [1 linha de justificativa baseada nos consensos]
```

**Opção híbrida** (regra 8): só entra na tabela se alguma persona a defendeu com evidência própria durante as rodadas. O moderador **não fabrica** opção C por concatenação diplomática das posições A e B.

**Aguardar resposta do dev** (Princípio VIII — agente propõe, dev decide). Dev pode responder:
- `A` / `B` / `C` — escolha direta
- `híbrida: <descrição>` — nova opção composta
- `diferir` — gravar como DIFERIDO e não forçar decisão
- `reformular: <nova pergunta>` — recomeçar da Fase 1

### Fase 5 — Gravação do artefato

**Resolver caminho** conforme contexto:

| Situação | Caminho |
|---|---|
| `FEATURE_DIR` definido + `--anexar=spec` | `$FEATURE_DIR/03-spec/debates/YYYY-MM-DD-<slug>.md` + append em `spec.md` seção `## Debates` |
| `FEATURE_DIR` definido + `--anexar=plan` | `$FEATURE_DIR/04-architecture/debates/YYYY-MM-DD-<slug>.md` + append de ADR em `plan.md` se aplicável |
| `FEATURE_DIR` definido + `--anexar=adr` | Novo ADR em `$FEATURE_DIR/04-architecture/plan.md` + transcript em `$FEATURE_DIR/04-architecture/debates/` |
| `FEATURE_DIR` definido sem `--anexar` | `$FEATURE_DIR/debates/YYYY-MM-DD-<slug>.md` |
| `FEATURE_DIR` vazio (transversal) | `.arkan/debates/transversal/YYYY-MM-DD-<slug>.md` |

**Slug**: primeiros 5 termos significativos da pergunta, kebab-case, max 40 chars, PT-BR.

**Criar diretório pai se não existir** (mkdir -p). Data em ISO `YYYY-MM-DD`. Se já existe artefato no mesmo dia com mesmo slug, sufixar `-2`, `-3`, etc.

**Template inline** do artefato:

```markdown
# Debate — <pergunta original>

**Data**: YYYY-MM-DD
**Feature**: <slug ou "transversal">
**Fase**: <FASE_ATUAL ou "ad-hoc">
**Profundidade**: simulado | profundo
**Painel**: persona-a, persona-b, ...
**Moderador**: Arkan Debate (arkan.debate.md)

## Pergunta

<reformulada na Fase 1>

## Contexto

<arquivos/trechos relevantes levantados na Fase 1 — caminhos completos>

## Rodada 1 — Posições iniciais

### [Persona A]
**Técnica**: ...
**Convicção**: [FORTE | FRACA]
**Posição**: ...
**Evidência**: ... (marcadores [verificado]/[não verificado])
**Riscos (steel-man)**: ...
**Custo de estar errado**: ... (se decisão irreversível)

### [Persona B]
...

## Rodada 2 — Contra-argumentos

### [Persona A]
**Convicção**: [FORTE | FRACA]
**Ataca**: ...
**Cede terreno**: ...
**Mudei de posição em**: ... (se houve conversão genuína)
**Mantém firme**: ...

### [Persona B]
...

## Síntese

**Viés de partida do moderador**: ... (se havia)
**Consensos**: ... (só o que existiu no transcript)
**Divergências irredutíveis**: ...
**Fora do alcance deste debate**: ... (condicional)
**Opções apresentadas**: ...
**Recomendação do moderador** [FORTE | FRACA]: ...

## Decisão

**Escolhida**: Opção [X] | DIFERIDA | REFORMULADA
**Justificativa do dev**: <texto do dev>
**Impacto**: <arquivos/artefatos afetados, se houver>

## Histórico

- YYYY-MM-DD HH:MM — debate iniciado
- YYYY-MM-DD HH:MM — decisão registrada
```

**Se dev escolheu `diferir`**: gravar tudo normalmente, mas na seção `## Decisão` escrever `DIFERIDA` e registrar o motivo. Skill **não recusa fechar**, mas marca o artefato como pendente.

**Se `--anexar` estiver ativo**: mostrar **diff do append** no arquivo alvo antes de aplicar. Aguardar confirmação do dev. Criar a seção `## Debates` no alvo se não existir.

### Fase 6 — Finalização

1. Reportar ao dev:
   - Caminho absoluto do artefato criado (clicável)
   - Sumário de 3 linhas (pergunta → decisão → impacto)
   - Se `--anexar`: confirmar append feito, mostrar range de linhas afetadas
2. **Sugerir** commit message (não executar commit):
   ```
   chore(arkan): debate — <pergunta curta> [feature: <slug ou "transversal">]
   ```
3. **Nunca** rodar `git commit` automaticamente (Princípio VIII).

## Guidelines

- Documentação e artefatos em **PT-BR**
- **Princípio VIII**: agente propõe, dev decide — debate **nunca** fecha sem entrada explícita do dev na Fase 4
- Painel mínimo 2, máximo 4 personas — acima disso ruído supera sinal
- Sempre incluir ao menos uma persona antagonista quando possível
- **Código de honestidade (regras 1–8)** rege todas as personas E o moderador — ver seção dedicada antes da Fase 2
- **Evidência obrigatória** em toda posição — declarações sem evidência devem explicitar "sem evidência direta, apenas princípio"; fatos sobre repo/banco levam marcador `[verificado: <fonte>]` ou `[não verificado]`, e no modo simulado `[verificado]` exige leitura/consulta real no turno
- **Steel-man obrigatório**: toda posição reconhece o melhor contra-argumento do oponente — inclusive evidência contrária encontrada na própria investigação (anti cherry-picking)
- **Convicção declarada** [FORTE]/[FRACA] em toda posição e na recomendação do moderador — [FRACA] honesta vale mais que [FORTE] inflada
- **Mudar de posição por evidência é mérito** — registrar em "Mudei de posição em"; convergência genuína encerra o debate mais cedo
- **Sem híbrido fabricado**: opção híbrida só se defendida por persona com evidência própria
- Modo profundo default é `general-purpose` subagent (não existem subagent_types específicos por persona — o prompt é que carrega a identidade)
- Arkan-KB é a fonte primária de evidência no modo profundo; fallback para Read/Grep
- **Não criar** personas novas dentro desta skill — reusar as personas existentes em `.arkan/agents/`
- **Não invocar** esta skill recursivamente (debate dentro de debate)
- Artefato de debate é **permanente** — faz parte do histórico de decisão do projeto
- Commit **nunca** é automático — apenas sugestão no final
- Falha ao resolver persona → avisar dev, oferecer fallback genérico, nunca abortar silenciosamente

## Variações e inovações observadas

Esta seção registra padrões emergentes em execuções reais do skill que se mostraram úteis em contextos específicos. **Não substituem** o fluxo padrão (Fases 0–6) — são extensões opcionais que o moderador pode propor ao dev quando o cenário recomenda.

### Inovação 1 — Fase 0.5: briefing inicial de domínio por persona designada

Antes da Rodada 1 adversarial, uma persona do painel (tipicamente a mais próxima do domínio em debate — ex.: especialista no domínio do produto, redator técnico, ontologista) **produz um briefing didático** sobre o domínio, suas entidades, modelo operacional e princípios constitucionais relevantes. O output desse briefing é capturado e injetado como **contexto compartilhado** em todas as Tasks da Rodada 1, garantindo que o painel inteiro opere com o mesmo modelo mental antes de divergir.

- **Quando usar**: debates em domínios complexos ou multidisciplinares onde o painel inclui personas externas (não-Arkan, sem familiaridade prévia com o projeto). Sem briefing, cada persona recebe pacote auto-contido e modelos mentais incompatíveis emergem — a Rodada 2 vira tradução de jargão em vez de confronto de mérito.
- **Quando não usar**: debates rápidos ou em domínios já dominados por todas as personas (ex.: debate puramente arquitetural entre architect, security e api-designer sobre controle de acesso a dados). Briefing acrescenta uma Task de custo e overhead de contexto que não se paga.

### Inovação 2 — Rodadas paralelas para frentes distintas do mesmo escopo

Em vez de uma Rodada 1 única, o moderador dispara **Rodada 1A e Rodada 1B em paralelo** (ou 1A/1B/1C), cada uma cobrindo uma frente distinta do mesmo escopo, com insumos e contexto próprios. Cada persona do painel responde **uma vez por frente** — o mesmo painel é reaplicado a cada frente — porque os insumos são fundamentalmente diferentes e merecem tratamento separado mas relacionado. A síntese da Fase 4 cruza as conclusões das frentes para identificar consensos transversais e divergências locais.

- **Quando usar**: escopo do debate envolve duas ou mais frentes com insumos/contextos distintos que merecem tratamento separado mas comparável (ex.: "migrar o armazenamento" contra "migrar a autenticação" — mesmo painel, contextos heterogêneos).
- **Quando não usar**: quando as frentes são variações superficiais que poderiam ser tratadas como cenários de uma resposta única; quando o painel é pequeno (2 personas) e duplicar Tasks dobra custo sem ganho proporcional de sinal.

### Inovação 3 — Painel especializado com agentes externos não-Arkan

O painel padrão do skill assume personas existentes em `.arkan/agents/` (arquivos `.md` com frontmatter e bloco `## PROMPT`). Em debates cujo eixo central envolve **expertise externa ao desenvolvimento de software** — domínio de produto, redação técnica, especialização operacional, mercado específico — esse painel é insuficiente. A inovação consiste em **convocar personas improvisadas via `subagent_type: general-purpose`** com prompt rico em identidade e técnica, mesmo sem arquivo de definição em `.arkan/agents/`. Funcionam como "consultores externos convidados" e devem coexistir com personas Arkan padrão para preservar o ângulo de governança.

Exemplos de personas externas já usadas: Redator técnico, Engenheiro de prompt, Especialista no domínio do produto, Revisor de idioma, Especialista no mercado do cliente.

- **Quando usar**: debates cujo eixo central exige expertise externa (domínio de produto, redação técnica, mercado específico, operação especializada). O painel Arkan padrão cobre engenharia/arquitetura — não cobre, por exemplo, "como redigir a documentação voltada ao usuário final" ou "como o mercado-alvo do produto avalia qualidade". Sempre manter pelo menos uma persona Arkan padrão no painel como contrapeso de governança.
- **Quando não usar**: debates puramente arquiteturais ou de governança, onde o painel Arkan padrão (architect, security-analyst, reviewer-critic, business-rules-analyst, etc.) já cobre os ângulos relevantes. Improvisar personas externas em domínio coberto introduz ruído sem ganho.

### Inovação 4 — Sub-agente independente adversarial (anti viés de auto-aprovação)

**Contexto**: quando um pipeline produz correções (de auditoria, de bug, de implementação) e essas correções precisam ser **revalidadas**, há risco de viés de auto-aprovação se a revalidação for feita pelo mesmo "perfil" de sub-agente que aplicou a correção. O sub-agente tende a confirmar o que vê em vez de procurar regressões. Empiricamente observado: uma auditoria v1.0 honesta (score 5/10, 4 CRITICAL + 5 HIGH) foi seguida de correções aplicadas por sub-agentes paralelos; a auditoria v2.0, redigida pelo mesmo perfil de sub-agente, validou as correções e atribuiu falsamente 9/10. Apenas a v3.0, disparada com instrução explícita "adversarial, não confie na v2.0", rebaixou para 6/10 e descobriu 3 CRITICAL + 5 HIGH novos (regressões + lacunas que a v2.0 perdeu).

**Mecanismo**:

- Quando dispatch um sub-agente para **revalidar correções**, o prompt DEVE incluir **instrução explícita**:
  - "Não confie nos relatos do sub-agente que aplicou a correção"
  - "Sua tarefa é encontrar problemas que ele perdeu, regressões introduzidas, edge cases não considerados"
  - "Verifique evidência fresca: leia código, rode SQL, faça grep — não confie em relatos"
- O `subagent_type` deve ser **diferente** quando viável (ex.: se a correção foi `general-purpose`, a validação pode ser `Explore` ou outro especializado)
- O prompt deve **versionar a auditoria** (v1.0, v2.0, v3.0) e instruir o sub-agente a **comparar** com a versão anterior procurando regressões
- Deve incluir **lista explícita de coisas a verificar** que tipicamente são perdidas: race conditions, transações atômicas, idempotência, edge cases de schema, integração entre artefatos

**Quando usar**:

- Pós-correção em audit-report (re-auditoria deve sempre ser adversarial)
- Pós-implementação de tasks complexas em pipeline arkan (pré-promoção shadow→público)
- Validação de migration de schema em produção

**Quando não usar**:

- Tarefas triviais ou puramente determinísticas (validar typecheck, lint)
- Quando há tempo curto e o custo de uma terceira instância adversarial supera o ganho marginal

**Exemplo de instrução adversarial efetiva**:

```text
Você é um auditor sênior adversarial. Sua tarefa: revalidar correções da v2.0 com olhar fresco.
Não confie na v2.0. A v2.0 pode ter viés de auto-aprovação.
Procure: regressões introduzidas, achados perdidos pela v2.0, edge cases.
Verifique: race conditions, transações atômicas, idempotência, integração entre artefatos.
Use evidência fresca: SQL real, leitura linha-a-linha, grep.
Seja honesto: se rebaixar score, rebaixe.
```

**Referência de origem desta inovação**:

- Observado numa auditoria real em 2026: a versão 1.0 foi honesta (nota 5 de 10, quatro achados críticos); as correções foram aplicadas por subagentes paralelos; a versão 2.0, escrita pelo mesmo perfil de subagente, validou as próprias correções e deu nota 9; só a versão 3.0, disparada com instrução explícita de não confiar na 2.0, rebaixou para 6 e descobriu três achados críticos novos, entre regressões e lacunas.

### Referência de origem

Os dois primeiros debates transversais que validaram este desenho ficaram no repositório onde o Arkan nasceu — o primeiro, sem as inovações acima, reuniu sete personas em vinte e duas trocas adversariais; o segundo já as aplicava. As inovações acima são o que sobreviveu deles.
