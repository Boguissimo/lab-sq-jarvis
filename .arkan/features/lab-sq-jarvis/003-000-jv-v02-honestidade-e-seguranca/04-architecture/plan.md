# Plano de Implementação — 003-000-jv-v02-honestidade-e-seguranca (JV-V02)

**Branch**: `lab-sq-jarvis/003-000-jv-v02-honestidade-e-seguranca` | **Data**: 2026-10-16 | **Spec**: `03-spec/spec.md`
> **Status**: rascunho — aguardando aprovação do desenvolvedor

---

## Sumário

O JV-V02 estende o programa do V01 com seis casos de controle novos mais uma etapa de calibração simulada, um módulo de regras de segurança e o histórico de configuração com reversão. A abordagem é **aditiva**: o REF-001-A e todas as asserções do V01 continuam intactos (INV-210); os módulos novos são funções puras e a interface só apresenta (ADR-03 do V01).

---

## Contexto Técnico

**Linguagem/Runtime**: Python 3.11–3.14 (como no V01)
**Dependências Principais**: PySide6 6.10.2, pyqtgraph 0.14.0, numpy 2.4.6 — **nenhuma nova**
**Storage**: SQLite local + cofre por hash em `%LOCALAPPDATA%\LabSQJarvis` (ou `JARVIS_DADOS`); **o banco do V01 já existe na máquina do desenvolvedor e precisa continuar abrindo** (ADR-207)
**Testes**: pytest 8.3.4 + pytest-qt 4.4.0; 45 testes do V01 mantidos, mais os do V02
**Plataforma**: Windows 10/11 (alvo); QA de máquina em Linux com `QT_QPA_PLATFORM=offscreen`
**Tipo de Projeto**: aplicativo desktop de uso pessoal
**Metas de Performance**: N/A — a análise de um caso (grade de ~460 pontos) roda em menos de 1 s; a geração de todos os casos em menos de 5 s
**Restrições**: sem IA; sem escrita no DSP (SEG-11); Core do Arkan intacto; PT-BR
**Escala**: um desenvolvedor, dezenas de sessões

---

## Constitution Check

### Core (I–VIII)

| Princípio | Verificação |
| --- | --- |
| I. Spec Governa Código | PASS — cada módulo e teste do plano cita o FR/INV da spec aprovada |
| II. Gate Obrigatório | PASS — `check-prerequisites` roda antes de cada fase; este plano só segue com PASS |
| III. Conclusividade | PASS — nenhum `[NEEDS CLARIFICATION]` aberto; limiares provisórios estão declarados, não pendentes |
| IV. Modo Declarado | PASS — feature de peso Code, pipeline completo |
| V. PT-BR First | PASS — identificadores, textos e documentos em português |
| VI. Especialização por Modo | PASS — agente de domínio do projeto declarado em `.arkan/config.md`, sem alteração |
| VII. Independência Estrutural | PASS — nenhuma importação de código de outras features; módulos novos dependem só de módulos do próprio Jarvis |
| VIII. Agente Propõe, Humano Decide | PASS — ideação e spec aprovadas; este plano e as ADRs aguardam sua aprovação |

### Projeto (P1–P14)

| Princípio | Verificação |
| --- | --- |
| P1. Cadeia de conhecimento explícita | PASS — a etapa de calibração reutiliza os tipos de registro existentes; `DERIVACOES_PERMITIDAS` não muda (ADR-205, ADR-204) |
| P2. Originais imutáveis | PASS — arquivo de ajuste entra no cofre por hash, sem leitura nem alteração; tabela nova com gatilho de só inserção |
| P3. Cálculo determinístico; IA só identificada | PASS — ruído, vales, mudança de nível e deficit são cálculos versionados; sem IA |
| P4. Reduzir o risco ao equipamento | PASS — módulo `seguranca.py`; sem dado confirmado, reforço bloqueado; aprovação não verifica |
| P5. Nada é inventado | PASS — SEG-02, 07 e 09 não ganham modelo sem fonte (FR-212); equipamento `planejado` nunca alimenta regra |
| P6. Diagnóstico com uma variável; calibração com conjunto | PASS — `comprometida` só no teste de diagnóstico; etapa de calibração tem resultado próprio e sem atribuição causal |
| P7. Incerteza e limitação declaradas | PASS — ruído estimado vira incerteza declarada; limites e provisórios visíveis na tela |
| P8. Critérios só mudam por decisão | PASS — limiares novos nascem provisórios na spec aprovada; mudanças futuras exigem JV-D |
| P9. IA substituível | N/A — sem IA neste incremento |
| P10. Não reinventar REW nem PC-Tool | PASS — formato de texto do REW mantido; arquivo do PC-Tool opaco |
| P11. Uma fonte canônica por estado | PASS — feature map e `status.md` atualizados ao fim; sem duplicar estado |
| P12. Três gates | PASS — G1 testes, G2 revisão, G3 roteiro no Windows |
| P13. Sessão guiada; rastreabilidade | PASS — cada resultado mostra a origem dos números e abre a cadeia |
| P14. Pessoal primeiro | PASS — nenhum recurso comercial |

**Resultado**: PASS

---

## Estrutura do Projeto

### Documentação (esta feature)

```
.arkan/features/lab-sq-jarvis/003-000-jv-v02-honestidade-e-seguranca/
├── 01-discovery/ideacao.md
├── 03-spec/spec.md
├── 04-architecture/{plan.md, data-model.md, quickstart.md}
├── 06-planning/tasks.md          (/arkan.tasks)
└── 08-qa/qa-report.md            (/arkan.qa)
```

### Código-fonte

```
src/jarvis/
├── calculos.py            [alterado] + ruido_estimado, vales_individuais, mudanca_nivel_via, deficit_cruzamento
├── regras.py              [alterado] + I-3, reordenação de hipóteses; VERSAO 1.1
├── seguranca.py           [novo]     classificação e regras SEG; resultados por regra
├── calibracao.py          [novo]     etapa de calibração: resultado, texto, sem atribuição causal
├── configuracao.py        [novo]     nomes sugeridos, reversão (arquivo / receita / não garantida)
├── persistencia.py        [alterado] + tabela aprovacao, user_version, migração, integridade estendida
├── sessao.py              [alterado] + portão de qualidade, comprometida, métodos da etapa e da configuração
├── referencia/
│   ├── ref001.py          [intacto]  REF-001-A byte a byte
│   ├── casos.py           [novo]     catálogo e gerador dos demais casos
│   └── dados/<CASO>/      [novo]     arquivos gerados dos 7 casos novos
└── interface/
    ├── janela.py          [alterado] seletor de caso, novos resultados; orquestra
    ├── seguranca_view.py  [novo]     bloco "Verificação de segurança"
    └── configuracao_view.py [novo]   arquivos de ajuste, confirmação de configuração, reversão
tests/  test_casos.py, test_seguranca.py, test_calibracao.py, test_configuracao.py [novos]
        test_calculos.py, test_regras.py, test_sessao.py, test_persistencia.py, test_interface.py [ampliados]
```

---

## ADRs

| ADR | Decisão | Motivo | Alternativas descartadas | Consequência |
| --- | --- | --- | --- | --- |
| ADR-201 | **Catálogo de casos parametrizado** em `referencia/casos.py` (nome, descrição, parâmetros, semente) reaproveitando `grade_frequencias`, `linkwitz_riley_4` e o formato de manifesto de `ref001.py`; REF-001-A não muda | INV-208 e INV-210: determinismo e V01 intacto; um ponto único para criar variantes | um gerador por caso; arquivos escritos à mão | novos casos custam parâmetros, não código; variantes de teste (calibração, ruído) saem do mesmo gerador |
| ADR-202 | Ruído estimado = desvio padrão do resíduo entre o nível e sua média móvel de 7 pontos, entre 200 Hz e 10 kHz | cálculo determinístico só com os dados que o arquivo traz; definição normativa da spec | relação sinal-ruído por coerência (exige repetições); comparar medições repetidas (exige duas medições) | subestima ruído de baixa frequência; limiares provisórios calibrados nos casos simulados e declarados como tal |
| ADR-203 | O portão de qualidade em `Servico.analisar` **devolve um resultado** `nao_da_para_concluir` (motivo, o que falta) em vez de lançar `ErroDoPercurso` | a interface precisa mostrar a explicação, e o diário e a cadeia registram a recusa | exceção (perde a estrutura da explicação) | `estado()["analise"]` ganha campos `qualidade` e `conclui`; a interface do V01 continua lendo os demais |
| ADR-204 | `seguranca.py` com funções puras; resultado por regra (`aprovada`/`bloqueada`/`não verificável`, motivo, valor provisório); SEG-02, 07 e 09 constantes `não verificável`. **Aprovação de nível B** em tabela própria `aprovacao` (só inserção), não como `decisao` ligada à recomendação | `DERIVACOES_PERMITIDAS` reflete o P1 (JV-D038); ligar decisão à recomendação exigiria emenda à constituição (P8) | registrar aprovação como `decisao ← recomendacao` (emenda P1); guardar dentro da recomendação (registro é imutável) | a aprovação é auditável sem mudar a cadeia; a integridade confere que toda aprovação aponta para uma recomendação existente |
| ADR-205 | A etapa de calibração reutiliza `recomendacao`, `experimento` e `conclusao`, com `tipo_intervencao: "etapa de calibração"` e vocabulário de resultado próprio | derivações já permitidas (`conclusao ← experimento`); sem emenda | tipos novos de registro (exigem emenda P1) | a interface distingue pelo campo `tipo_intervencao`; testes garantem que veredito de teste e resultado de etapa não se misturam (INV-206) |
| ADR-206 | Arquivo de ajuste = arquivo opaco no cofre, `arquivo_original.tipo = 'ajuste-pctool'`, ligado em `configuracao.arquivo_sha256`; reversão como função pura em `configuracao.py` | JV-D039/D040; coluna `arquivo_sha256` já existe no esquema | ler o conteúdo (F019); só valores | nada é interpretado; o nome sugerido segue `JV-AAAA-MM-DD-S<sessão>-antes/-depois` |
| ADR-207 | **Migração do esquema** com `PRAGMA user_version` (V01 = 1, V02 = 2): `CREATE TABLE/TRIGGER IF NOT EXISTS`, idempotente, sem alterar dados | o banco do V01 já existe no Windows do desenvolvedor e guarda sessões que ele quer ver no Histórico | recriar o banco; migração manual | teste abre um banco no formato do V01 e confere que as sessões continuam; backup do arquivo antes da primeira migração |
| ADR-208 | Comprometida detectada por duas vias: (a) configuração declarada "depois" ≠ proposta; (b) mudança de nível de via entre "antes" e "depois" individuais. O manifesto do caso passa a aceitar `depois.configuracao_declarada` e medição individual `via_b` do "depois" | decisão do desenvolvedor registrada na spec; (a) sozinha não pega o que o usuário não declara | só (a) | `sessao.importar_depois` aceita arquivos extras opcionais; sem eles, só (a) atua |
| ADR-209 | Interface: `janela.py` orquestra; blocos novos em `seguranca_view.py` e `configuracao_view.py`; seletor de caso lê o catálogo; a etapa de calibração aparece no passo 4 quando o caso for do tipo `etapa_calibracao` | `janela.py` já tem 638 linhas; ADR-03: a interface não calcula | tudo em `janela.py`; novo passo na barra lateral | os cinco passos e o Histórico não mudam |
| ADR-210 | Versionar o que muda: `regras.VERSAO` 1.0 → 1.1; funções novas de `calculos` com versão própria em `VERSOES`; `INCREMENTO = "JV-V02"`, versão 0.2.0 | INV-208 e rastreabilidade (cada cálculo grava a versão) | não versionar | sessões do V01 continuam citando as versões com que foram feitas |

---

## Dependências e Interfaces

### Dependências (esta feature consome)

| Depende de | Como | Observação |
| --- | --- | --- |
| JV-V01 em `main` | `sessao.Servico`, `calculos`, `regras`, `persistencia`, `ref001`, interface | mantido sem quebra (INV-210) |
| Constituição v0.4.0, regras de segurança v0.4.0 | requisitos e invariantes; SEG-01 a SEG-13 | provisórios continuam provisórios |
| PySide6, pyqtgraph, numpy | `requirements.txt` | sem novas dependências |
| Partes de F002, F003, F005, F006, F007 | entregues neste incremento | registro de entregas no feature map ao fim (JV-D041) |

### Interfaces Expostas (contratos internos)

- `casos.listar() -> list[Caso]`; `casos.gerar(nome, pasta, **variantes) -> Path`.
- `calculos.ruido_estimado(r) -> dict`; `vales_individuais(r) -> dict`; `mudanca_nivel_via(antes, depois, faixa) -> dict`; `deficit_cruzamento(soma, potencias, indices) -> dict`.
- `regras.avaliar(...)` ganha parâmetros opcionais `vales_individuais` e `qualidade`; chamadas do V01 continuam válidas.
- `seguranca.classificar(rec) -> str`; `seguranca.avaliar(rec, equipamento) -> list[ResultadoRegra]`.
- `calibracao.resultado(deficit_antes, deficit_depois, qualidade) -> dict`.
- `configuracao.nome_sugerido(...)`, `configuracao.reversao(configuracao, anterior, arquivo_antes) -> dict`.
- `Servico` ganha: `propor_etapa`, `registrar_etapa_aplicada`, `importar_depois_etapa`, `concluir_etapa`, `aprovar(recomendacao, escopo)`, `arquivar_ajuste(configuracao, caminho)`, `confirmar_configuracao_inicial`, `reversao()`.

---

## Mapa de Agentes por Fase

| Fase | Modo | Command | Agente(s) | Técnica(s) | Artefato de Saída |
| --- | --- | --- | --- | --- | --- |
| 01 — Discovery | Assistência | `arkan.ideacao` | Research, Intake, Briefing | debate estruturado | `01-discovery/ideacao.md` |
| 03 — Spec | Geração | `arkan.spec` | Spec Writer, NFR, BDD, Business Rules | definições normativas, INV com teste | `03-spec/spec.md` |
| 04 — Architecture | Geração | `arkan.plan` | Architect, Data Modeler, API Designer, Security Analyst | ADRs, Constitution Check | `04-architecture/plan.md` |
| 06 — Planning | Geração | `arkan.tasks` | Task Planner | decomposição por bloco | `06-planning/tasks.md` |
| 07 — Implement | Assistência | `arkan.implement` | Implementador | task a task, G1 | `src/`, `tests/` |
| 08 — QA | Orquestração | `arkan.qa` | QA | spec↔código, UAT, invariantes | `08-qa/qa-report.md` |
| 09 — Deploy | Assistência | `arkan.deploy` | Deploy (N/A: uso local, entrega por `main`) | — | registro no feature map |

---

## Sequência de Implementação

### Fase 0 — Fundação (bloqueia o resto)

1. `casos.py` e dados dos casos novos; teste de determinismo e de conteúdo esperado de cada caso (FR-201, INV-208).
2. Migração do esquema com `user_version`, tabela `aprovacao` e teste com banco no formato do V01 (ADR-207).

### Fase 1 — Bloco 1: casos e honestidade (US-01 a US-04)

3. `calculos`: ruído, vales individuais, mudança de nível (FR-202).
4. `regras`: I-3 e reordenação das hipóteses (FR-204); `sessao`: portão de qualidade (FR-203), N4 (FR-205), N5 (FR-206), `comprometida` (FR-207), REF-001-B (FR-208).
5. Interface: seletor de caso e resultados (FR-209). **Ponto de teste G3 do bloco 1.**

### Fase 2 — Bloco 2: segurança (US-05)

6. `seguranca.py`: classes, SEG-01/03/04/05/06/08/10/11/12/13, SEG-02/07/09 não verificáveis (FR-210 a FR-213, FR-216); testes de casos permitidos, limítrofes, proibidos e de propriedade.
7. Aprovação nível B (tabela `aprovacao`) e `seguranca_view.py` (FR-214, FR-215). **Ponto de teste G3 do bloco 2.**

### Fase 3 — Bloco 3: calibração e configuração (US-06, US-07)

8. `calibracao.py` e REF-002-A (FR-217, FR-218).
9. `configuracao.py`, arquivo opaco, confirmação inicial, reversão e `configuracao_view.py` (FR-219 a FR-221).
10. Integridade estendida (FR-222). **Ponto de teste G3 do bloco 3.**

### Fase N — Polish

11. `COMO-EXPERIMENTAR.md` atualizado, capturas de tela (`ferramentas/capturas.py`), pacote, QA e registro de entregas.
