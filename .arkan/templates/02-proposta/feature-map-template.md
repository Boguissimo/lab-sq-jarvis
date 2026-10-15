# Feature Map: [NOME DO PROJETO]

> **Projeto**: [nome-do-projeto]
> **Input**: [vision.md](../01-discovery/vision.md) | [briefing.md](../01-discovery/briefing.md)
> **Status**: Proposta — aguardando aprovação do desenvolvedor
> **Data**: [DATA]

---

## Resumo da Decomposição

**Total de features propostas**: [N]
**Features P1 (MVP)**: [N]
**Features P2**: [N]
**Features P3**: [N]

---

## Features Propostas

<!--
  Cada feature é uma unidade autônoma de desenvolvimento:
  - Tem valor entregável independente
  - Pode ser iniciada via /arkan.ideacao
  - Status inicial: pendente

  Dependências: listar apenas dependências bloqueantes
  (feature Y não pode começar sem feature X completa).
-->

| # | Nome | Descrição | Prioridade | Depende de | Status |
| --- | --- | --- | --- | --- | --- |
| F001 | [nome-feature] | [O que esta feature entrega ao usuário] | P1 | — | pendente |
| F002 | [nome-feature] | [O que esta feature entrega ao usuário] | P1 | F001 | pendente |
| F003 | [nome-feature] | [O que esta feature entrega ao usuário] | P2 | F001 | pendente |
| F004 | [nome-feature] | [O que esta feature entrega ao usuário] | P2 | — | pendente |
| F005 | [nome-feature] | [O que esta feature entrega ao usuário] | P3 | F002, F003 | pendente |

**Status possíveis**: `pendente` | `em-andamento` | `concluida`

---

## Mapa de Dependências

<!--
  Representação visual das dependências entre features.
  Usar texto se diagrama não for viável.
-->

```
MVP (P1):
  F001 → F002
  F001 (independente)

V1.0 (P2):
  F001 → F003
  F004 (independente)

Roadmap (P3):
  F002 + F003 → F005
```

---

## Sequência Sugerida de Desenvolvimento

### Fase 1 — MVP (P1)

1. F001 — [nome]: [por que começar aqui]
2. F002 — [nome]: [depende de F001]

### Fase 2 — V1.0 (P2)

3. F003 — [nome]: pode iniciar após F001
4. F004 — [nome]: independente, pode rodar em paralelo com F003

### Fase 3 — Roadmap (P3)

5. F005 — [nome]: aguarda F002 + F003

---

## Como Usar Este Mapa

Para iniciar o desenvolvimento de uma feature:

1. Verificar que as dependências estão `concluida`
2. Invocar `/arkan.ideacao [descrição da feature]`
3. Atualizar o status desta feature para `em-andamento`
4. Quando concluída: atualizar para `concluida`

Para atualizar este documento após o desenvolvimento avançar:

- Atualizar coluna `Status` conforme features evoluem
- Adicionar novas features descobertas durante o desenvolvimento
- Registrar mudanças de prioridade com data e justificativa

---

## Histórico de Revisões

| Data | Mudança | Justificativa |
| --- | --- | --- |
| [DATA] | Versão inicial gerada por `/arkan.projeto` | Decomposição a partir de [briefing/vision] |
