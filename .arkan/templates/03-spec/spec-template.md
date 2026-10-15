# Especificação da Feature: [NOME DA FEATURE]

**Branch**: `[NNN-short-name]`
**Criado em**: [DATA]
**Status**: Rascunho
**Input**: Ideação `01-discovery/ideacao.md`

---

## Cenários de Usuário e Testes

<!--
  User stories devem ser priorizadas como jornadas independentes.
  Cada story deve ser TESTÁVEL INDEPENDENTEMENTE — se implementar apenas uma, tem um MVP viável.
  Prioridades: P1 = mais crítica. Cada story é uma fatia autônoma de funcionalidade.
-->

### User Story 1 — [Título Breve] (Prioridade: P1)

[Descrever a jornada do usuário em linguagem natural.]

**Por que P1**: [Valor e justificativa da prioridade.]

**Independent Test**: [Como testar esta story de forma isolada.]

**Cenários de Aceitação**:

1. **Dado** [estado inicial], **Quando** [ação], **Então** [resultado esperado]
2. **Dado** [estado inicial], **Quando** [ação], **Então** [resultado esperado]

**Cenários de Erro**:

1. **Dado** [condição de falha], **Quando** [ação], **Então** [comportamento esperado do sistema]

---

### User Story 2 — [Título Breve] (Prioridade: P2)

[Descrever a jornada do usuário em linguagem natural.]

**Por que P2**: [Valor e justificativa.]

**Independent Test**: [Como testar de forma isolada.]

**Cenários de Aceitação**:

1. **Dado** [estado inicial], **Quando** [ação], **Então** [resultado esperado]

**Cenários de Erro**:

1. **Dado** [condição de falha], **Quando** [ação], **Então** [comportamento esperado]

---

### Edge Cases

- [Edge case relevante 1]
- [Edge case relevante 2]

---

## Definições normativas

<!--
  Todo adjetivo de qualidade ("rápido", "adequado", "sem degradação") e todo limiar
  usado em FR/NFR/SC deve ter entrada nesta tabela ou número inline no requisito.
  Termo indefinido = [NEEDS CLARIFICATION]. Se a spec não usa termos qualitativos,
  registrar "Nenhum termo qualitativo — requisitos usam valores diretos."
-->

| Termo | Definição mensurável |
| --- | --- |
| [termo usado nos requisitos] | [definição com número, enum ou condição verificável] |

---

## Requirements

### Requisitos Funcionais

- **FR-001**: O sistema DEVE [requisito verificável em linguagem imperativa]
- **FR-002**: O sistema DEVE [requisito verificável]

### Requisitos Não-Funcionais

- **NFR-001**: [Requisito de qualidade — performance, segurança, compatibilidade, idioma]
- **NFR-002**: [Requisito de qualidade]

### Key Entities

- **[Entidade 1]**: [Definição precisa. Campos relevantes. O que a distingue de entidades similares.]
- **[Entidade 2]**: [Definição precisa.]

---

## Invariantes

<!--
  Para cada princípio da Constitution (core + projeto) relevante a esta feature,
  gerar um invariante. Adicionar invariantes específicos do domínio conforme necessário.
  Formato: - **INV-NN — [Nome].** Regra. **Teste:** como detectar a violação
  (comando, query ou procedimento executável — não uma aspiração).
  Invariante sem Teste é decoração: o QA §3 herda o Teste como método de verificação.
-->

- **INV-01 — [Spec Governa Código].** A spec é a fonte de verdade. Divergências são resolvidas na direção spec→código, exceto Clarifications aprovadas. **Teste:** verificar que nenhum alinhamento altera a spec sem Clarification explícita.

- **INV-02 — [Conclusividade dos Artefatos].** Cada artefato gerado deve ser autocontido. **Teste:** agente da fase seguinte opera lendo apenas o diretório da feature, sem consultas externas.

- **INV-03 — [Invariante de domínio].** [Regra específica desta feature — o que nunca pode acontecer.] **Teste:** [query SQL, chamada de API ou passo manual que detecta a violação.]

---

## Critérios de Sucesso

### Resultados Mensuráveis

<!--
  Todo SC precisa de Instrumento (como medir em runtime) e Baseline (valor atual).
  Sem instrumento, o critério é decorativo; sem baseline, a comparação é impossível.
  O ops-report da fase 10 executa estes instrumentos — escrever algo executável.
-->

- **SC-001**: [condição objetiva, com número ou percentual]. **Instrumento:** [query SQL / evento / comando / procedimento manual descrito]. **Baseline:** [valor atual medido, ou "N/A — funcionalidade nova"]
- **SC-002**: [condição objetiva]. **Instrumento:** [como medir]. **Baseline:** [valor ou N/A]

---

## Clarifications

### Sessão [YYYY-MM-DD]

**C1 — [Tópico]**: [Decisão tomada e como foi aplicada na spec. Referência ao FR ou seção afetada.]
