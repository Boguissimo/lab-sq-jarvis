# Visão do Projeto: Lab SQ Jarvis

> **Projeto**: lab-sq-jarvis
> **Input**: [briefing.md](briefing.md)
> **Status**: **Proposta (revisão 2) — aguardando aprovação do desenvolvedor**
> **Data**: 2026-10-15

Siglas: **REW** — Room EQ Wizard; **PC-Tool** — programa que configura o HELIX; **DSP** — processador
digital de sinais; **IA** — inteligência artificial; **SEG** — regra de segurança; **PT/VP** —
critérios do Protótipo Técnico e da Versão Pessoal.

---

## 1. Vision Statement

> Um engenheiro de calibração ao lado do desenvolvedor: guia cada sessão no Focus — do que se percebe
> ao que mudou —, explica o porquê com base nas medições e no equipamento real, propõe um teste de
> cada vez com o resultado esperado e lembra de tudo na sessão seguinte. Trabalha com o REW e o
> PC-Tool, reduzindo os riscos ao equipamento dentro do que é conhecido, sem prometer o que não pode
> garantir.

**Proposta de valor**: entender e aprender enquanto ajusta, com um histórico que se acumula — em vez
de só chegar a uma curva-alvo.

---

## 2. Indicadores de Sucesso

| Indicador | Baseline | Meta | Marco |
| --- | --- | --- | --- |
| Critérios PT-01 a PT-10 atendidos | — | todos | Marco 1 |
| Recomendações exibidas que violam regras SEG | não controlado | 0 | Marcos 1 e 2 |
| Sessões reais completas no Focus | 0 | ≥ 3, em ≥ 2 dias (proposta) | Marco 2 |
| Orientações compreendidas nas duas últimas sessões | — | todas “entendi” (proposta) | Marco 2 |
| Sessão retomada só pelo resumo | — | ≥ 1 | Marco 2 |
| Declaração de utilidade do desenvolvedor (VP-10) | — | positiva, justificada | Marco 2 |
| Métricas de diagnóstico | inexistentes | definidas e medidas, **sem meta** (JV-D008) | Marcos 1 e 2 |

**Indicador primário**: Marco 2 atendido — critérios VP-01 a VP-10.

---

## 3. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
| --- | --- | --- | --- |
| O Jarvis não ajudar mais que ferramentas já existentes | Média | Alto | sessão de referência com Flat Liner ou TuneEQ/ATM (JV-D018); critério VP-10 compara |
| Fluxo guiado ficar complexo demais | Média | Alto | sessão em cinco passos; cadeia por trás; critério PT-10 e VP-03 |
| IA apresentar número sem origem ou fora de contexto | Média | Alto | verificador por origem, grandeza, unidade e canal (JV-D026) |
| Recomendação causar dano ao equipamento | Baixa | Crítico | regras SEG, aprovação nominal, bloqueio sem dado confirmado; limites declarados (JV-D022) |
| Medições do carro sem referência temporal | Alta | Médio | protocolo de medição (F012); recusa explícita de análises de fase (JV-D023) |
| Diagnóstico ajustado em casos simulados falhar no carro | Alta | Médio | limite de generalização (JV-D025); testes discriminantes; F014 |
| Formato do arquivo do PC-Tool inacessível | Média | Baixo | ajustes à mão com receita; leitura só depois (F019) |
| Defeitos do Core do Arkan travarem gates | Média | Baixo | registro (JV-D015) e verificação equivalente |

**Risco crítico**: dano ao equipamento por recomendação.

---

## 4. Prioridades Acordadas

### P1 — Marco 1: Protótipo técnico

- Fundação; casos de referência; registro e histórico; importação de arquivos; cálculos; indícios e
  hipóteses; experimento e segurança; sessão guiada com percepção; assistente de IA; aceite.

### P1 — Marco 2: Versão pessoal utilizável

- Cadastro do Focus; protocolo de medição; medições reais; diagnóstico ampliado; receita para o
  PC-Tool; retomada e aprendizado; validação pessoal.

### P3 — Depois da versão pessoal

- API do REW; arquivo do HELIX; comparação cega; medição automatizada; avaliação comercial.

### Fora do Escopo (decisão explícita)

- Assinatura, SaaS e oficinas antes da versão pessoal (JV-D017).
- Escrever no DSP (JV-D004).
- EQ automático e geração de sinais de medição (P10).
- Competição SQ como requisito (JV-D013).

---

## 5. Próximos Passos

- [ ] Aprovar o conjunto revisado (briefing, visão, constituição v0.2.0, regras de segurança v0.2.0,
      feature map v2, proposta consolidada, comparação de ferramentas)
- [ ] Decidir as propostas pendentes: JV-D011, JV-D015, JV-D016, JV-D018 (sessão de referência),
      JV-D029 e as quantidades dos critérios VP
- [ ] Iniciar F001 via `/arkan.ideacao`

### Histórico de revisões

| Data | Mudança |
| --- | --- |
| 2026-10-15 | Versão inicial |
| 2026-10-15 | Revisão 2: retirada a promessa “nunca arrisca o equipamento”; indicadores por marco; riscos de não superar ferramentas existentes e de complexidade do fluxo; prioridades por marco |
