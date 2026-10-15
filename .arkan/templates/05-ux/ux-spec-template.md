# UX Spec: [NOME DA FEATURE]

> **Feature**: [NNN-short-name]
> **Input**: [spec.md](../03-spec/spec.md)
> **Status**: Rascunho
> **Data**: [DATA]

<!--
  Esta spec prescreve COMPORTAMENTO e ESTRUTURA — não estilo visual.
  Não especificar classes Tailwind, cores, espaçamentos ou fontes.
  O desenvolvedor decide a apresentação visual; a spec define o que é exibido e quando.
-->

---

## Componentes

<!--
  Para cada componente UI da feature: localização no código, props, estados possíveis.
  Listar também componentes que NÃO devem ser criados (reutilizar existentes).
-->

### [NomeDoComponente]

**Arquivo**: `[caminho/para/componente.tsx]`
**Descrição**: [O que este componente faz e quando é usado]
**Segmento/fase do usuário** (se o projeto declarar esse conceito): [valor conforme a constituição do projeto / N/A — o projeto não usa esse conceito]

<!--
  Critério de verificação: quando o projeto declarar segmentos ou fases de
  usuário (ex.: nível de experiência, plano contratado, estágio de uma jornada),
  features de UX declaram para qual segmento/fase foram projetadas, e as regras
  permitidas/proibidas por segmento ficam a critério do projeto, declaradas na
  constituição dele. Sem esse conceito no projeto: usar N/A.
-->

**Props**:

| Prop | Tipo | Obrigatória | Descrição |
| --- | --- | --- | --- |
| [prop1] | [tipo] | Sim / Não | [Descrição] |
| [prop2] | [tipo] | Sim / Não | [Descrição] |

**Estados**:

| Estado | Trigger | O que exibir |
| --- | --- | --- |
| loading | [quando ocorre] | [o que mostrar ao usuário] |
| empty | [quando ocorre] | [o que mostrar — mensagem, CTA] |
| error | [quando ocorre] | [o que mostrar — mensagem de erro, retry] |
| populated | [quando ocorre] | [conteúdo principal] |

**Componentes existentes a reutilizar**: [listar componentes que NÃO devem ser reimplementados]

---

### [OutroComponente]

**Arquivo**: `[caminho/para/componente.tsx]`
**Descrição**: [Descrição]

**Estados**:

| Estado | Trigger | O que exibir |
| --- | --- | --- |
| [estado] | [trigger] | [exibição] |

---

## Componentes que NÃO devem ser criados

<!--
  Listar componentes existentes no projeto que já servem ao propósito.
  Evita reimplementação desnecessária.
-->

| Componente existente | Localização | Por que reutilizar |
| --- | --- | --- |
| [NomeComponente] | `[caminho]` | [Já faz X — criar novo seria duplicata] |

---

## Fluxos de Tela

<!--
  Descrever cada fluxo como sequência numerada: ação → resultado.
  Cada fluxo corresponde a uma user story da spec.
  Referenciar estados dos componentes envolvidos.
-->

### Fluxo 1 — [Título] (US1)

**Pré-condição**: [Estado inicial do sistema / usuário]

1. Usuário [ação] → sistema exibe [resultado] no componente [X] (estado: loading)
2. Sistema processa → componente [X] transiciona para estado: [populated / error]
3. [Se populated]: exibe [conteúdo específico]
4. [Se error]: exibe [mensagem + ação disponível]

**Pós-condição**: [Estado final após fluxo completado com sucesso]

---

### Fluxo 2 — [Título] (US2)

**Pré-condição**: [Estado inicial]

1. [Passo 1]
2. [Passo 2]

**Pós-condição**: [Estado final]

---

## Fluxos de Erro

<!--
  Descrever como o sistema se comporta em condições de falha.
  Derivar dos "Cenários de Erro" da spec.
-->

### Erro: [Tipo de Erro]

**Quando ocorre**: [Condição que dispara]
**Componente afetado**: [NomeDoComponente] (estado: error)
**O que exibir**: [Mensagem específica + ações disponíveis]
**Recuperação**: [Como o usuário sai deste estado]

---

## Especificações de Interação

<!--
  Comportamentos de interação que não são óbvios.
  Ex: debounce em busca, confirmação antes de deletar, feedback de ações assíncronas.
-->

| Interação | Comportamento |
| --- | --- |
| [Ação do usuário] | [O que o sistema faz — timing, feedback, validação] |
| [Ação do usuário] | [Comportamento] |

**Acessibilidade** (requisitos mínimos):
- [Requisito de acessibilidade 1 — ex: formulário com labels acessíveis]
- [Requisito de acessibilidade 2]
