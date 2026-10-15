# Relatório Operacional: [NOME DA FEATURE]

> **Feature**: [NNN-short-name]
> **Período**: [DATA INICIAL] a [DATA FINAL]
> **Status**: [em-producao]
> **Gerado em**: [DATA]

---

## 1. Erros Recentes

<!--
  Registrar erros observados em produção no período.
  Alimentar manualmente a partir de logs, Sentry, ou observação direta.
  Para cada erro: frequência, impacto, status de resolução.
-->

| Data | Erro | Frequência | Impacto | Status |
| --- | --- | --- | --- | --- |
| [DATA] | [Descrição do erro] | [N ocorrências] | Alto / Médio / Baixo | Aberto / Resolvido / Monitorando |

**Erros críticos sem resolução**: [N]

### Erros conhecidos (consolidado de `debug/` e `bugfixes.md`)

<!--
  Catálogo vivo: uma linha por bug já investigado da feature. É a primeira coisa
  a consultar ao ver um sintoma repetido. "Prevenção em vigor" vazia = tech debt
  TD-NNN automático na seção 3. Lista com mais de ~10 erros: extrair para
  arquivo irmão `10-ops/erros-conhecidos.md` e manter aqui só o resumo.
-->

| ID | Sintoma (como reconhecer) | Mensagem/log exato | Causa (1 linha) | Prevenção em vigor | Bug-report |
| --- | --- | --- | --- | --- | --- |
| [BUG-YYYYMMDD-NNN] | [o que o usuário/operador vê] | [mensagem literal] | [causa raiz resumida] | [teste/constraint/gate — ou vazio ⇒ TD] | [`debug/bug-report-NNN.md`] |

**Observações**:

[Padrões identificados, correlações entre erros, contexto relevante.]

---

## 2. Feedback Categorizado

<!--
  Registrar feedback de usuários recebido no período.
  Categorizar por tipo para facilitar priorização.
  Alimentar manualmente a partir de canais de feedback disponíveis.
-->

### Bugs reportados por usuários

| Data | Relato | Reproduzível | Prioridade |
| --- | --- | --- | --- |
| [DATA] | [Descrição] | Sim / Não / Parcial | Alta / Média / Baixa |

### Pedidos de melhoria

| Data | Pedido | Frequência | Impacto estimado |
| --- | --- | --- | --- |
| [DATA] | [Descrição] | [N pedidos similares] | Alto / Médio / Baixo |

### Elogios e pontos positivos

- [Data]: [O que funcionou bem]

**Padrão identificado no feedback**: [O que o feedback revela sobre uso real vs. esperado]

---

## 3. Tech Debt

<!--
  Registrar dívida técnica identificada durante operação e manutenção.
  Priorizar por impacto na estabilidade e na capacidade de evoluir a feature.
-->

| # | Descrição | Localização | Impacto | Quando endereçar |
| --- | --- | --- | --- | --- |
| TD-001 | [Descrição do tech debt] | `caminho/arquivo.ts` | Alto / Médio / Baixo | Imediato / Próxima sprint / Backlog |

**Tech debt crítico** (impacta estabilidade ou segurança): [N itens]

---

## 4. Métricas de Uso

<!--
  Executar o Instrumento de cada SC da spec e registrar o valor lido.
  Feature com superficie-critica: sim — a tabela ABRE com as métricas que a
  ideação (seção Obrigações da Superfície Crítica) e os SCs referenciam, e
  responde o checklist pós-release abaixo.
  Regra anti-teatro: KPI/SC sem instrumento disponível = "sem instrumento — não
  avaliável" (vira tech debt de instrumentação na seção 3), NUNCA preenchido como
  se medido.
-->

| Métrica | Instrumento (da spec) | Valor atual | Meta (spec) | Status |
| --- | --- | --- | --- | --- |
| [KPI/SC-NNN] | [query/evento/comando] | [Valor lido] | [Meta] | Dentro / Abaixo / Acima / Sem instrumento — não avaliável |

**Checklist pós-release da superfície crítica** (apenas se `superficie-critica: sim`):

- [ ] Métrica das Obrigações da Superfície Crítica mantida ou melhorada (ou declarada não avaliável — instrumento na dívida)
- [ ] Nenhuma regra da constituição do projeto para essa superfície violada (verificar contra as telas/fluxos entregues)
- [ ] Gatilho de rollback de produto (deploy-checklist) reavaliado com o valor lido

---

## 5. Ações Sugeridas

<!--
  Lista priorizada de ações para o próximo ciclo.
  Derivada das seções anteriores.
-->

### Imediato (resolver antes da próxima revisão)

- [ ] [Ação urgente 1] — [referência ao erro ou feedback]
- [ ] [Ação urgente 2]

### Próximo ciclo

- [ ] [Melhoria 1] — baseada em feedback
- [ ] [Tech debt 1] — TD-001

### Backlog

- [ ] [Item de backlog 1]

---

## 6. Próxima Revisão Sugerida

**Data sugerida**: [DATA — baseada na frequência de erros e volume de feedback]

**Periodicidade recomendada**: Semanal / Quinzenal / Mensal

**Justificativa**: [Por que esta periodicidade? Alta frequência de erros → mais frequente; sistema estável → menos frequente]

---

## Histórico de Relatórios

| Data | Status geral | Ações tomadas |
| --- | --- | --- |
| [DATA] | [Status] | [Resumo das ações tomadas desde o relatório anterior] |
