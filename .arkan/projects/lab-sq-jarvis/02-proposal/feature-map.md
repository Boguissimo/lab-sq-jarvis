# Feature Map: Lab SQ Jarvis

> **Projeto**: lab-sq-jarvis
> **Input**: [vision.md](../01-discovery/vision.md) | [briefing.md](../01-discovery/briefing.md) | anexo [preparacao-mvp.md](preparacao-mvp.md)
> **Status**: Proposta — aguardando aprovação do desenvolvedor
> **Data**: 2026-10-15

---

## Resumo da Decomposição

**Total de features propostas**: 18
**Features P1 (MVP)**: 10
**Features P2**: 6
**Features P3**: 2

---

## Features Propostas

| # | Nome | Descrição | Prioridade | Peso proposto | Depende de | Status |
| --- | --- | --- | --- | --- | --- | --- |
| F001 | fundacao-projeto | Ratificar constituição, regras de segurança, registro de decisões, fontes e agente de domínio; a base normativa que as demais features verificam | P1 | Doc | — | pendente |
| F002 | casos-de-referencia | Gerador determinístico de casos acústicos com verdade conhecida (família REF-001 e controles negativos), em formato de exportação do REW, com definição das métricas de diagnóstico | P1 | Code | F001 | pendente |
| F003 | registro-da-cadeia | Banco local com cadastro, originais imutáveis por hash, cadeia de conhecimento, critérios versionados, diário só de acréscimo e rotina de integridade | P1 | Code | F001 | pendente |
| F004 | importacao-rew-arquivos | Importar respostas ao impulso e respostas em frequência exportadas pelo REW, com metadados obrigatórios, para a cadeia | P1 | Code | F002, F003 | pendente |
| F005 | calculos-deterministicos | Rotinas validadas para o MVP: resposta em frequência, suavização, soma complexa prevista, diferença de fase, atraso relativo, verificação de qualidade, comparação previsto × medido | P1 | Code | F002, F003 | pendente |
| F006 | indicios-e-hipoteses | Detectores que geram indícios a partir de cálculos e regras que formulam e ordenam hipóteses com o que as confirmaria ou refutaria | P1 | Code | F005 | pendente |
| F007 | experimento-assistido | Recomendação de uma variável com previsão calculada, verificação SEG, aprovação de nível B quando sensível, registro antes/depois e veredito com incerteza | P1 | Code | F006 | pendente |
| F008 | assistente-ia | Conversa com IA substituível (provedor simulado + provedores reais), ferramentas só de leitura da cadeia, verificador de números, selo de estimativa exploratória, registro e controle de envios | P1 | Code | F003, F006 | pendente |
| F009 | interface-desktop | Aplicativo desktop (tecnologia em JV-D011) com as telas mínimas do MVP e abertura com dois cliques | P1 | Code | F003 | pendente |
| F010 | demonstracao-mvp | Percorrer o ciclo REF-001 pela interface, avaliar os critérios CA-01 a CA-12 e registrar o resultado | P1 | Doc | F004, F007, F008, F009 | pendente |
| F011 | leitura-api-rew | Ler medições diretamente da API local do REW, como alternativa à exportação de arquivos | P2 | Code | F004 | pendente |
| F012 | cadastro-focus | Cadastrar e confirmar os equipamentos reais do Ford Focus, com fichas técnicas e posições | P2 | Code | F003 | pendente |
| F013 | medicoes-reais | Incorporar progressivamente medições reais do Focus e comparar com os casos de referência | P2 | Code | F010, F011, F012 | pendente |
| F014 | receita-e-exportacao-pc-tool | Receita de alteração passo a passo e exportação de filtros no formato aceito pelo PC-Tool | P2 | Code | F007 | pendente |
| F015 | ampliacao-casos-e-metricas | Ampliar a família de casos (atraso, nível L/R, modos do habitáculo, corte inadequado) e medir as métricas de diagnóstico; propor metas só então | P2 | Code | F006 | pendente |
| F016 | leitura-ajuste-helix | Ler o arquivo de ajuste do PC-Tool, após inspeção de um arquivo real | P2 | Code | F003 + arquivo real disponível | pendente |
| F017 | medicao-automatizada-rew | Disparar varreduras pela API do REW (exige licença Pro) | P3 | Code | F011 | pendente |
| F018 | audicao-estruturada | Sessões de audição com nível igualado e comparação cega, ligadas aos experimentos | P3 | Code | F007 | pendente |

**Status possíveis**: `pendente` | `em-andamento` | `concluida`

---

## Mapa de Dependências

```
MVP (P1):
  F001 ─┬─→ F002 ─┬────────────→ F004 ──────────────────────────┐
        │         └─→ F005 ─→ F006 ─┬─→ F007 ───────────────────┤
        └─→ F003 ─┬─→ F004          └─→ F008 ───────────────────┤
                  ├─→ F005                                       ├─→ F010
                  ├─→ F008                                       │
                  └─→ F009 ──────────────────────────────────────┘

V1.0 (P2):
  F004 → F011
  F003 → F012
  F010 + F011 + F012 → F013
  F007 → F014
  F006 → F015
  F003 + arquivo real → F016

Roadmap (P3):
  F011 → F017 (licença Pro)
  F007 → F018
```

---

## Sequência Sugerida de Desenvolvimento

### Fase 1 — MVP (P1)

1. F001 — fundação: base normativa; nada é verificável sem ela.
2. F002 — casos de referência: define a verdade antes do código que será testado contra ela.
3. F003 — registro da cadeia: pode correr em paralelo com F002.
4. F005 — cálculos: testados contra F002, registrados em F003.
5. F004 — importação: usa os arquivos gerados em F002.
6. F009 — interface: pode começar após F003, em paralelo com F004–F006, recebendo telas à medida que as features chegam.
7. F006 — indícios e hipóteses.
8. F007 — experimento assistido (segurança incluída).
9. F008 — assistente de IA.
10. F010 — demonstração e aceite do MVP.

### Fase 2 — V1.0 (P2)

11. F012 — cadastro do Focus (pode começar cedo, assim que o desenvolvedor tiver os dados).
12. F011 — API do REW.
13. F015 — ampliação de casos e métricas.
14. F014 — receita e exportação.
15. F013 — medições reais.
16. F016 — arquivo do HELIX, quando houver arquivo real.

### Fase 3 — Roadmap (P3)

17. F017 — medição automatizada.
18. F018 — audição estruturada.

---

## Estimativa (P1)

> Dias de trabalho assistido por agente, incluindo as revisões e aprovações do desenvolvedor em cada
> fase do Arkan. Ranges, nunca valores pontuais.

| Épico (features) | Range (dias) | Incerteza | Justificativa |
| --- | --- | --- | --- |
| Fundação (F001) | 1–2 | Baixa | artefatos já redigidos; falta ratificação |
| Verdade de referência (F002) | 3–6 | Média | definição de tolerâncias e métricas exige debate técnico |
| Persistência e cadeia (F003, F004) | 5–9 | Média | modelo epistêmico novo; formato de exportação do REW conhecido só por fontes nível 4 |
| Cálculo e diagnóstico (F005, F006) | 6–11 | Média | rotinas clássicas, mas suíte de validação extensa |
| Experimento e segurança (F007) | 4–8 | Média | regras SEG com muitos casos limítrofes |
| IA (F008) | 4–8 | Alta | verificador de números e independência de fornecedor sem precedente no projeto |
| Interface e demonstração (F009, F010) | 6–11 | Média | primeira aplicação desktop do projeto; empacotamento Windows |
| **Soma** | **29–55** | | |
| **Com buffer de 20%** (incerteza geral média) | **35–66** | | |

**Premissas**: o desenvolvedor aprova cada fase em até um dia; o REW exporta nos formatos citados
nas fontes; nenhuma medição real é exigida no MVP; um provedor de IA estará disponível para o
critério CA-08 (G2).

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
| 2026-10-15 | Versão inicial gerada por `/arkan.projeto` | Decomposição a partir do briefing, da visão e das decisões JV-D001 a JV-D016 |
