# Ideação: [NOME DA FEATURE]

> **Feature**: [NNN-short-name]
> **Status**: Ideação (pré-spec) — documento vivo
> **Propósito**: Registrar o raciocínio, tensões e decisões que fundamentarão a especificação formal.
> **Participantes**: [Desenvolvedor] + Claude
> **Data**: [DATA]

---

## Contexto Inicial

### O problema que a feature resolve

[Descrever a lacuna, necessidade ou dor que motivou esta feature.]

### O que já existe

[Listar artefatos existentes relevantes: documentação, código, decisões anteriores encontradas durante a investigação.]

### O que este debate precisa resolver

[Listar as perguntas abertas identificadas na investigação. Cada pergunta vira uma decisão em §Decisões Tomadas.]

---

## Decisões Tomadas

<!--
  Cada decisão segue o formato abaixo.
  Não simular múltiplas personas — registrar alternativas, fundamentação e consequências diretamente.
  O desenvolvedor participa como decisor; o agente propõe com fundamentação.
-->

### D1 — [Título da decisão]

**Contexto**: [Por que esta decisão é necessária — qual tensão ou ambiguidade ela resolve.]

**Alternativas consideradas**:

- **A)** [Opção A] — [prós e contras concretos]
- **B)** [Opção B] — [prós e contras concretos]

**Decisão**: [Opção escolhida]

**Fundamentação**: [Por que esta opção vence — com referência a evidências do codebase, restrições técnicas ou decisões anteriores.]

**Consequências**: [O que muda com esta decisão. Limitações conhecidas. O que fica mais fácil e o que fica mais difícil.]

---

## Dúvidas Resolvidas

### [Pergunta que surgiu durante o debate]?

**Decisão: [Resposta direta].** [Fundamentação — por que essa resposta, com referência a evidências do codebase ou docs se disponível.]

---

## Síntese

**Nome**: [Nome da feature]

**Definição**: [Uma frase que define o que a feature entrega e para quem.]

**Escopo — o que entra**:

1. [Item de escopo 1]
2. [Item de escopo 2]

**Fora do escopo**:

- [O que fica para features futuras e por quê]

---

## Obrigações da Superfície Crítica

<!--
  OBRIGATÓRIO quando `superficie-critica: sim` no status.md (gate bloqueante).
  Se a feature não toca superfície crítica: remover esta seção.
  O que conta como "crítico", e a política para cada superfície, é decisão de
  cada projeto — declarada em .arkan/projects/<projeto>/constitution.md, seção
  "Decisões de contexto". "Se não houver resposta clara → feature não entra."
-->

| Pergunta | Resposta |
| --- | --- |
| Qual superfície crítica esta feature toca | [conforme declarado na constituição do projeto] |
| Por que essa mudança é necessária nessa superfície | [justificativa] |
| A mudança respeita a política do projeto para essa superfície? | [Sim / Não — justificar contra a constituição] |
| Métrica que prova sucesso | [métrica declarada pelo projeto — vira SC-NNN na spec, com Instrumento] |
| Risco introduzido | [descrição + mitigação] |

---

## Próximos Passos

- [x] Definir escopo da feature
- [x] Debater tensões de design
- [x] Investigar codebase/docs existentes
- [x] Resolver dúvidas abertas
- [ ] Executar `/arkan.spec` alimentado pela síntese desta ideação
- [ ] Gerar spec formal → `03-spec/spec.md`
- [ ] `/arkan.plan` para plano técnico
- [ ] `/arkan.tasks` para tarefas de implementação
