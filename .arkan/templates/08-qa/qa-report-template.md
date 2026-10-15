# Relatório de QA: [NOME DA FEATURE]

> **Feature**: [NNN-short-name]
> **Input**: [spec.md](../03-spec/spec.md) | [tasks.md](../06-planning/tasks.md)
> **Status**: QA em andamento
> **Data**: [DATA]
> **Revisado por**: [Nome / Agente]

---

## Resultado do QA

**Resultado**: ☐ APROVADO — pode prosseguir para deploy  /  ☐ REPROVADO — bloqueadores pendentes  /  ☐ APROVADO COM RESSALVAS — itens não-bloqueadores registrados

**Bloqueadores abertos**: [N]
**Divergências spec↔código**: [N]
**Itens de UAT pendentes**: [N]

---

## 1. Divergências Spec↔Código

<!--
  Resultado da execução de /arkan.alinhamento (se executado).
  Ou levantamento manual das divergências encontradas.
  Para cada divergência: classificar direção e status de resolução.
-->

| # | Severidade | Tipo | Descrição | Direção da correção | Status |
| --- | --- | --- | --- | --- | --- |
| D01 | CRÍTICO / ALTO / MÉDIO / BAIXO | [Tipo] | [Descrição] | Código muda / Spec → Clarification / Correção factual | Aberto / Resolvido |

**Divergências críticas sem resolução**: [N]

---

## 2. Checklist UAT (User Acceptance Testing)

<!--
  Verificar cada cenário de aceitação da spec.
  Testar manualmente ou via script de verificação (quickstart.md).
  Para cada item: PASS, FAIL ou N/A com observações.
-->

### User Story 1 — [Título]

| Cenário | Resultado | Observação |
| --- | --- | --- |
| **Dado** [estado], **Quando** [ação], **Então** [resultado] | PASS / FAIL / N/A | [Observação se FAIL] |
| [Cenário de erro 1] | PASS / FAIL / N/A | [Observação] |

### User Story 2 — [Título]

| Cenário | Resultado | Observação |
| --- | --- | --- |
| [Cenário] | PASS / FAIL / N/A | [Observação] |

### Edge Cases

| Caso | Resultado | Observação |
| --- | --- | --- |
| [Edge case 1] | PASS / FAIL / N/A | [Observação] |

---

## 3. Verificação de Invariantes

<!--
  Verificar cada invariante definido em spec.md ## Invariantes.
  Invariante violado = bloqueador imediato.
-->

| Invariante | Verificação | Status |
| --- | --- | --- |
| [Spec Governa Código] | [Como foi verificado] | PASS / FAIL |
| [Gate Obrigatório] | [Como foi verificado] | PASS / FAIL |
| [Conclusividade dos Artefatos] | [Como foi verificado] | PASS / FAIL |
| [Modo Declarado] | [Como foi verificado] | PASS / FAIL |
| [PT-BR First] | [Como foi verificado] | PASS / FAIL |

---

## 4. Bloqueadores

<!--
  Itens que impedem o deploy. Deve estar vazia para APROVADO.
  Para cada bloqueador: responsável e prazo para resolução.
-->

| # | Descrição | Responsável | Prazo | Status |
| --- | --- | --- | --- | --- |
| B01 | [Descrição do bloqueador] | [Responsável] | [Data] | Aberto / Resolvido |

---

## 5. Itens Não-Bloqueadores (Ressalvas)

<!--
  Problemas identificados que não impedem o deploy mas devem ser endereçados.
  Registrar como tech debt se não resolvido antes do deploy.
-->

| # | Descrição | Prioridade | Quando endereçar |
| --- | --- | --- | --- |
| R01 | [Descrição] | Alta / Média / Baixa | Antes do deploy / Próxima sprint / Backlog |

---

## 6. Decisão Final

**Decisão**: ☐ APROVADO  /  ☐ APROVADO COM RESSALVAS  /  ☐ REPROVADO

**Condições para aprovação** (se ressalvas ou reprovado):
- [Condição 1]
- [Condição 2]

**Data da decisão**: [DATA]

**Próximo passo**: `/arkan.deploy` para prosseguir com deploy
