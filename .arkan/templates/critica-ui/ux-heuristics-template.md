---
title: Crítica UI/UX — [ALVO]
status: em-construcao
updated: YYYY-MM-DD
---

# Crítica UI/UX — [ALVO]

**Data**: YYYY-MM-DD
**Alvo**: [caminho absoluto + tipo: ux-spec | componente | rota | plan | trecho]
**Feature**: [slug ou "transversal"]
**Fase do alvo**: [05-ux | produção | rascunho | ad-hoc]
**Projeto**: [nome do projeto]
**Corpus**: Nielsen 10 + Hick + Fitts + Miller
**Pergunta dirigida**: [texto conforme Fase 1]
**Domínio delegado**: sim ([agente]) | não (nenhum agente de domínio declarado) | opt-out (`--sem-dominio`) | N/A (fora do escopo do domínio)
**Profundidade**: simulado | profundo
**Orquestrador**: Arkan Crítica-UI (`.claude/commands/arkan.critica-ui.md`)

<!--
  Este artefato é ANEXO ao alvo. Nunca modifica o artefato alvo — só documenta
  a crítica e a decisão do dev. Se uma recomendação for aceita, o dev edita o
  alvo separadamente; este arquivo registra que foi aceita, não a aplica.
-->

---

## Alvo analisado

<!--
  Resumo do conteúdo lido em 3-5 linhas, com caminhos completos.
  Se ux-spec: componentes documentados, fluxos, estados.
  Se componente .tsx: props, estados internos, handlers principais.
  Se página que se compõe com layout ancestral, se o framework do projeto tiver esse conceito: arquivo + o layout ancestral mais próximo.
  Se diretório: lista de arquivos considerados (com limite aplicado).
-->

[Resumo]

**Caminhos lidos**:
- [caminho 1]
- [caminho 2]

---

## Pergunta dirigida

<!-- Pergunta que guiou a crítica. Default (se ausente): "qual é o pior momento deste artefato para o usuário?" -->

[Pergunta]

---

## Leitura Adversarial — UX Critic

<!--
  Saída estruturada do agente ux-critic conforme contrato em
  .arkan/agents/transversal/ux-critic.md. Ordem fluxo→corpus obrigatória.
-->

### Contexto
[1-2 frases: qual artefato, qual fase, qual pergunta]

### Persona e tarefa simuladas
[2-3 frases: quem é o usuário imaginado, qual tarefa, qual contexto]

### Findings

| # | Severidade | Heurística | Momento | Evidência (citação literal) | Impacto | Proposta |
|---|---|---|---|---|---|---|
| 1 | alta/média/baixa | N[1-10] / Hick / Fitts / Miller | [seção, estado, fluxo, linha] | "[citação]" | [impacto] | [proposta não-visual] |

### Atritos sem ancoragem no corpus (descartados ou redirecionados)
- [atrito] — razão (ex: vago, fora do escopo, redirecionado para a11y futuro)

### Conflitos entre usabilidade e domínio sinalizados (pré-delegação)
- [Finding #N]: N<heurística> conflita potencialmente com <regra de domínio> — decisão diferida ao agente de domínio abaixo, se houver.
- Se nenhum: "Nenhum conflito entre usabilidade e domínio pré-sinalizado."

### Status final (UX Critic)
**[Sem bloqueadores / Com fricções / Requer revisão]**

**Justificativa**: [fundamentação concisa]

---

## Reflexão do Agente de Domínio

<!--
  Condicional: só preencher se `.arkan/config.md` declara `agente-dominio` e não veio
  `--sem-dominio`, OU se foi passado `--com-dominio` em qualquer projeto.

  Formato definido pelo contrato do agente declarado em `agente-dominio`
  (arquivo correspondente em `.arkan/agents/transversal/`).

  Se delegação foi pulada: substituir esta seção inteira por uma linha curta:
  "Domínio delegado: N/A — [razão: nenhum agente de domínio declarado | opt-out por chave | fora do escopo do domínio]"
-->

### Contexto
[1-2 frases: qual artefato, qual fase, qual pergunta dirigida]

### Áreas do domínio impactadas
- [quais áreas/conceitos do domínio do projeto este artefato toca, e por quê — definidos pelo agente declarado]

### Regras do domínio em jogo

| Regra | Status | Evidência |
|---|---|---|
| [regra 1, definida pelo agente de domínio] | ✅/⚠️/❌ | [trecho citado] |
| [regra 2] | ✅/⚠️/❌ | [trecho citado] |

### Conflitos entre usabilidade e domínio detectados
[Lista — heurística × regra de domínio × resolução proposta. Se nenhum: "Nenhum conflito detectado."]

### Limites do domínio atingidos
[Referência a documento de limites do domínio, se aplicável. Se nenhum: "Nenhum limite atingido."]

### Carga cognitiva
- Esforço imposto pela interface, evitável em tese (ex.: navegação confusa, passos redundantes): [reduzido / mantido / aumentado] — [justificativa]
- Esforço exigido pela própria tarefa, inerente a ela: [preservado / distorcido] — [justificativa]

### Recomendações do agente de domínio
1. [Ação concreta] — rastreio: [documento do domínio que sustenta a ação]
2. [...]

### Invariantes do domínio verificados
- [ ] Entidade canônica do domínio identificada
- [ ] Rastreabilidade de origem
- [ ] Existe uma unidade mínima de conteúdo do domínio que deveria ser atômica e testável? Qual é, e este artefato a respeita?
- [ ] O domínio exige alguma devolutiva ao usuário após a ação dele (acerto/erro, sucesso/falha, aprovado/reprovado)? Este artefato entrega isso quando aplicável?
- [ ] Relações entre entidades do domínio conferidas
- [ ] Esforço imposto pela interface minimizado; esforço da própria tarefa preservado
- [ ] [demais invariantes do domínio, declarados pelo agente]

### Status final (Agente de Domínio)
**[Aprovado / Aprovado com ressalvas / Requer revisão / Fora do escopo do domínio]**

**Justificativa**: [fundamentação rastreada aos documentos do domínio]

**Próximos passos**: [ações sugeridas — veto irrestrito do dev]

---

## Conflitos entre usabilidade e domínio (resolução)

<!--
  Consolidar conflitos entre usabilidade e domínio detectados pelo UX Critic e/ou pelo agente de domínio.
  Regra de resolução: quando uma regra de domínio está em jogo, o domínio vence — mas essa é a
  convenção padrão deste framework; declare a regra de resolução do seu projeto se for outra.
  Registrar cada conflito com: heurística UX envolvida, regra de domínio, decisão.

  Se nenhum conflito: "Nenhum conflito entre usabilidade e domínio detectado."
-->

| # | Heurística UX | Regra de domínio | Decisão | Justificativa |
|---|---|---|---|---|
| 1 | N<X> | [regra] | domínio vence / UX vence / compatível | [rastreamento] |

---

## Síntese e Priorização

<!--
  Combinação priorizada dos Findings UX + Recomendações do agente de domínio.
  Cada linha é um item decidível individualmente pelo dev.
-->

| # | Ação proposta | Origem | Severidade | Esforço estimado | Decisão do dev |
|---|---|---|---|---|---|
| 1 | [ação concreta] | ux-critic / agente de domínio / ambos | alta/média/baixa | ~Xh / não estimado | aceita / rejeita / difere |
| 2 | ... | ... | ... | ... | ... |

---

## Decisão

**Aceitas**: [lista de #s] — dev editará o artefato alvo separadamente para aplicá-las
**Rejeitadas**: [lista de #s com justificativa curta de cada]
**Diferidas**: [lista de #s com motivo da postergação]

**Justificativa do dev** (livre): [texto do dev]

**Impacto no artefato alvo**: [arquivos que o dev pretende editar em resposta às aceitas — o command **não** edita automaticamente. Princípio III preservado.]

---

## Histórico

- YYYY-MM-DD HH:MM — crítica iniciada (alvo: [caminho])
- YYYY-MM-DD HH:MM — findings ux-critic registrados
- YYYY-MM-DD HH:MM — parecer do agente de domínio registrado (ou N/A)
- YYYY-MM-DD HH:MM — síntese apresentada
- YYYY-MM-DD HH:MM — decisão do dev registrada
