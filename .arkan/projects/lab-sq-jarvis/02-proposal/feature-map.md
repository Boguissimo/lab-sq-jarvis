# Feature Map: Lab SQ Jarvis

> **Projeto**: lab-sq-jarvis
> **Input**: [vision.md](../01-discovery/vision.md) | [briefing.md](../01-discovery/briefing.md) | anexo [proposta-consolidada.md](proposta-consolidada.md)
> **Status**: Proposta (v2, revisão 2) — aguardando aprovação do desenvolvedor
> **Data**: 2026-10-15

Siglas: **REW** — Room EQ Wizard; **API** — interface de programação; **IA** — inteligência artificial;
**DSP** — processador digital de sinais; **SEG** — regra de segurança; **Doc/Code** — peso da feature
no Arkan (documental ou com código).

---

## Resumo da Decomposição

**Total de features propostas**: 22
**Marco 1 — Protótipo técnico (P1)**: 10 (F001–F010)
**Marco 2 — Versão pessoal utilizável (P1)**: 7 (F011–F017)
**Depois da versão pessoal (P3)**: 5 (F018–F022)

Os dois marcos são prioridade P1: a versão pessoal é o objetivo; o protótipo técnico é o caminho
seguro até ela (JV-D019).

---

## Features Propostas

### Marco 1 — Protótipo técnico: o ciclo completo funciona com casos conhecidos

| # | Nome | Descrição | Prioridade | Peso | Depende de | Status |
| --- | --- | --- | --- | --- | --- | --- |
| F001 | fundacao-projeto | Ratificar constituição, regras de segurança, decisões, fontes e agente de domínio | P1 | Doc | — | pendente |
| F002 | casos-de-referencia | Gerador determinístico de casos com verdade conhecida (família REF-001 e controles negativos), em formato de exportação do REW; definição das métricas, sem metas | P1 | Code | F001 | pendente |
| F003 | registro-e-historico | Banco local com cadastro, originais imutáveis, cadeia de conhecimento (inclusive percepção), histórico de configurações do DSP, critérios versionados, diário e rotina de integridade | P1 | Code | F001 | pendente |
| F004 | importacao-arquivos-rew | Importar respostas ao impulso e respostas em frequência exportadas pelo REW, com os metadados necessários | P1 | Code | F002, F003 | pendente |
| F005 | calculos-deterministicos | Resposta em frequência, suavização, qualidade da medição, **verificação de referência temporal**, diferença de fase, atraso relativo, soma prevista, comparação previsto × medido | P1 | Code | F002, F003 | pendente |
| F006 | indicios-e-hipoteses | Detectores que geram indícios e regras que formulam e ordenam hipóteses, com o que as confirmaria ou refutaria | P1 | Code | F005 | pendente |
| F007 | experimento-e-seguranca | Teste de uma variável com previsão, regras SEG, aprovação de nível B, receita básica e veredito (`confirmada`, `refutada`, `inconclusiva`, `comprometida`) | P1 | Code | F006 | pendente |
| F008 | sessao-guiada | Aplicativo desktop com o fluxo de cinco passos, registro de percepção antes e depois, histórico e abertura com dois cliques; recebe F004–F007 e F009 à medida que ficam prontas | P1 | Code | F003 | pendente |
| F009 | assistente-ia | Conversa com IA substituível; ferramentas só de leitura; verificador de números por origem, grandeza, unidade e canal; selo de estimativa; registro e controle de envios | P1 | Code | F003, F006 | pendente |
| F010 | aceite-prototipo-tecnico | Percorrer a família REF-001 pelo fluxo guiado e avaliar os critérios PT-01 a PT-10 | P1 | Doc | F004, F007, F008, F009 | pendente |

### Marco 2 — Versão pessoal utilizável: sessões reais no Focus

| # | Nome | Descrição | Prioridade | Peso | Depende de | Status |
| --- | --- | --- | --- | --- | --- | --- |
| F011 | cadastro-focus | Cadastrar e confirmar os equipamentos realmente instalados no Ford Focus, com fichas técnicas e posições; planejados ficam marcados como tal | P1 | Code | F003 | pendente |
| F012 | protocolo-de-medicao | “O que preciso medir”: canais, posições, referência temporal, nível e passo a passo no REW para cada tipo de investigação, com verificação de qualidade na importação | P1 | Code | F005, F008 | pendente |
| F013 | medicoes-reais | Importar e analisar medições reais do Focus por arquivo (**sem depender da API do REW**, JV-D027) | P1 | Code | F004, F011, F012 | pendente |
| F014 | diagnostico-ampliado | Ligar percepções a mecanismos e medições; casos de atraso, nível esquerdo/direito, modos do habitáculo, corte inadequado e polaridade em condições reais; sequência de ajuste de referência com fontes (JV-D029); métricas medidas, metas só por decisão | P1 | Code | F006 | pendente |
| F015 | receita-pc-tool | Receita passo a passo para o modelo e a versão reais do PC-Tool, indicando quando usar TuneEQ ou ATM; exportação opcional de filtros no formato aceito pelo PC-Tool | P1 | Code | F007, F011 | pendente |
| F016 | retomada-e-aprendizado | Resumo de cada sessão, retomada a partir do resumo, linha do tempo das configurações, observações aprendidas e preferências pessoais versionadas | P1 | Code | F003, F008 | pendente |
| F017 | validacao-pessoal | Sessões reais no Focus avaliadas pelos critérios VP-01 a VP-10; inclui, se aprovado, uma sessão de referência com Flat Liner ou TuneEQ/ATM (JV-D018) | P1 | Doc | F010, F013, F014, F015, F016 | pendente |

### Depois da versão pessoal (roadmap)

| # | Nome | Descrição | Prioridade | Peso | Depende de | Status |
| --- | --- | --- | --- | --- | --- | --- |
| F018 | leitura-api-rew | Ler medições direto da API local do REW (conveniência) | P3 | Code | F004 | pendente |
| F019 | leitura-arquivo-helix | Ler o arquivo de ajuste do PC-Tool, após inspeção de um arquivo real | P3 | Code | F003 + arquivo real | pendente |
| F020 | comparacao-cega | Audição com nível igualado e comparação cega, ligada aos experimentos | P3 | Code | F007, F008 | pendente |
| F021 | medicao-automatizada-rew | Disparar varreduras pela API do REW (exige licença Pro) | P3 | Code | F018 | pendente |
| F022 | avaliacao-comercial | Avaliar se a ferramenta tem potencial comercial (JV-D017) | P3 | Doc | F017 | pendente |

**Status possíveis**: `pendente` | `em-andamento` | `concluida`

---

## Mapa de Dependências

```
Marco 1 — Protótipo técnico
  F001 ─┬─→ F002 ─┬──────────────→ F004 ────────────────────┐
        │         └─→ F005 → F006 ─┬─→ F007 ────────────────┤
        └─→ F003 ─┬─→ F004         └─→ F009 ────────────────┼─→ F010
                  ├─→ F005                                   │
                  ├─→ F009                                   │
                  └─→ F008 ──────────────────────────────────┘

Marco 2 — Versão pessoal (todas convergem em F017, que também exige F010)
  F003 → F011 (pode começar cedo: depende só dos seus dados do carro)
  F005 + F008 → F012
  F004 + F011 + F012 → F013          ← sem API do REW
  F006 → F014
  F007 + F011 → F015
  F003 + F008 → F016
  F010 + F013 + F014 + F015 + F016 → F017

Depois
  F004 → F018 → F021 (licença Pro)
  F003 + arquivo real → F019
  F007 + F008 → F020
  F017 → F022
```

---

## Sequência Sugerida de Desenvolvimento

### Marco 1 — Protótipo técnico

1. F001 — fundação: base normativa.
2. F002 e F003 em paralelo — verdade de referência e registro.
3. F005 — cálculos, testados contra F002.
4. F008 — sessão guiada, começa logo após F003 e recebe as demais partes.
5. F004 — importação de arquivos.
6. F006 — indícios e hipóteses.
7. F007 — experimento e segurança.
8. F009 — assistente de IA.
9. F010 — aceite do protótipo técnico.

**Em paralelo, a qualquer momento**: o desenvolvedor reúne os dados do Focus (fichas técnicas,
posições), que alimentam a F011.

### Marco 2 — Versão pessoal utilizável

10. F011 — cadastro do Focus (pode antecipar).
11. F012 — protocolo de medição.
12. F013 — medições reais.
13. F014 — diagnóstico ampliado.
14. F015 — receita para o PC-Tool.
15. F016 — retomada e aprendizado.
16. F017 — validação pessoal.

### Depois

17. F018 a F022, conforme o uso mostrar necessidade.

---

## Estimativa

> Dias de trabalho assistido por agente, incluindo revisões e aprovações do desenvolvedor. Ranges,
> nunca valores pontuais.

| Épico | Features | Range (dias) | Incerteza | Justificativa |
| --- | --- | --- | --- | --- |
| Fundação | F001 | 1–2 | Baixa | artefatos já redigidos |
| Verdade de referência | F002 | 3–6 | Média | tolerâncias e métricas exigem debate técnico |
| Registro e importação | F003, F004 | 5–9 | Média | formato de exportação do REW conhecido por fontes secundárias |
| Cálculo e diagnóstico | F005, F006 | 6–11 | Média | rotinas clássicas; suíte de validação extensa |
| Experimento e segurança | F007 | 4–8 | Média | muitos casos limítrofes |
| Sessão guiada | F008 | 5–9 | Média | primeiro aplicativo desktop; fluxo precisa ser simples |
| IA | F009 | 4–8 | Alta | verificador de números sem precedente no projeto |
| Aceite | F010 | 1–2 | Baixa | — |
| **Marco 1 — soma** | | **29–55** | | |
| **Marco 1 — com buffer de 20%** | | **35–66** | | incerteza geral média |
| Dados reais | F011, F012, F013 | 7–15 | Alta | depende do equipamento disponível e das condições de medição no carro |
| Diagnóstico ampliado | F014 | 6–12 | Alta | casos reais menos limpos; fontes a reunir |
| Receita e retomada | F015, F016 | 6–12 | Média | — |
| Validação pessoal | F017 | 3–8 | Alta | depende do tempo disponível para sessões no carro |
| **Marco 2 — soma** | | **22–47** | | |
| **Marco 2 — com buffer de 30%** | | **29–61** | | incerteza geral alta (mundo real) |

**Premissas**: aprovação de cada fase em até um dia; REW exporta nos formatos citados nas fontes;
o desenvolvedor terá microfone de medição, interface e o DSP instalados antes da F013; um provedor de
IA disponível para F009.

---

## Como Usar Este Mapa

1. Verificar que as dependências estão `concluida`.
2. Invocar `/arkan.ideacao [descrição da feature]` numa branch `lab-sq-jarvis/NNN-CCC-slug`.
3. Atualizar o status desta feature para `em-andamento`.
4. Quando concluída: atualizar para `concluida`.

---

## Histórico de Revisões

| Data | Mudança | Justificativa |
| --- | --- | --- |
| 2026-10-15 | Versão inicial (v1, 18 features, MVP de 10) gerada por `/arkan.projeto` | Decomposição a partir do briefing, da visão e das decisões JV-D001 a JV-D016 |
| 2026-10-15 | v2: dois marcos (JV-D019); F008 vira sessão guiada com percepção (JV-D020, JV-D021); medições reais sem dependência da API do REW (JV-D027); novas F012 protocolo de medição, F016 retomada e aprendizado, F017 validação pessoal, F022 avaliação comercial no fim (JV-D017); comparação cega e API do REW passam para depois da versão pessoal | Revisão 2 do desenvolvedor |
