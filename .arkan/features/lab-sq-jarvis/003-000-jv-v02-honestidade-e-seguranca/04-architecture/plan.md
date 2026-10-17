# Plano de Implementação — 003-000-jv-v02-honestidade-e-seguranca (JV-V02)

**Branch**: `lab-sq-jarvis/003-000-jv-v02-honestidade-e-seguranca` | **Data**: 2026-10-15 | **Spec**: `03-spec/spec.md` (com emendas E1 e E2)
> **Status**: **revisão R1 aprovada** pelo desenvolvedor em 2026-10-15 (nível B), incluindo os pontos para aprovação listados no fim · **complemento R1.1** (emenda E2: casos REF-003-S, ruído não estimável descritivo, fixture permanente): **aprovado em 2026-10-15 (nível B)** · **complemento R1.2** (emenda E3, revisão adversarial A01–A09; ADR-212 nova): **aprovado em 2026-10-15 (nível B)** · **complemento R1.3** (emenda E4: critério de aceite do SC-208 e confirmação de mudança): **decisões do desenvolvedor registradas em 2026-10-16; redação final aguarda conferência e aprovação expressa**
> **R1** (2026-10-15) aplica a revisão externa (`docs/revisoes/jv-v02-revisao-tecnica-do-plano.md`, itens 1 a 12) e a emenda E1 da spec. Situação das ADRs:
> - **Revistas:** ADR-202, 204, 205, 207 e 208.
> - **Ajustadas:** ADR-201, 203, 206, 209 e 210.
> - **Nova:** ADR-211.
>
> Contém a matriz de rastreabilidade e os critérios de teste de cada correção. A versão anterior está no commit `e2ab7ff`.

---

## Sumário

O JV-V02 estende o programa do V01 com seis casos de controle novos e quatro variantes de uma etapa de calibração simulada. Acrescenta também um módulo de regras de segurança que decide a admissibilidade das recomendações, e o histórico de configuração com reversão documentada.

A abordagem é **aditiva**: o REF-001-A e todas as asserções do V01 continuam intactos (INV-210). Os módulos novos são funções puras, e a interface só apresenta (ADR-03 do V01).

A R1 acrescenta três frentes que a revisão mostrou necessárias:
- **Migração real do banco legado** do V01 (versão 0), com backup e recusa segura.
- **Interpretação congelada no registro** (INV-211): reabrir uma sessão não reexecuta regras.
- **Estimador de irregularidade e detector de mudança** que não confundem defeito acústico com ruído (E1).

---

## Contexto Técnico

**Linguagem/Runtime**: Python 3.11–3.14 (como no V01)
**Dependências Principais**: PySide6 6.10.2, pyqtgraph 0.14.0, numpy 2.4.6 — **nenhuma nova**
**Storage**: SQLite local + cofre por hash em `%LOCALAPPDATA%\LabSQJarvis` (ou `JARVIS_DADOS`); **o banco do V01 já existe na máquina do desenvolvedor, tem `user_version` 0 e guarda sessões que não podem ser perdidas** (ADR-207)
**Testes**: pytest 8.3.4 + pytest-qt 4.4.0; 45 testes do V01 mantidos sem alterar asserções, mais os do V02
**Plataforma**: Windows 10/11 (alvo); QA de máquina em Linux com `QT_QPA_PLATFORM=offscreen`
**Tipo de Projeto**: aplicativo desktop de uso pessoal
**Metas de Performance**: a análise de um caso (grade de ~460 pontos) roda em menos de 1 s; a geração de todos os casos em menos de 5 s; a varredura de validação (SC-208) em menos de 60 s
**Restrições**: sem IA; sem escrita no DSP (SEG-11); Core do Arkan intacto; PT-BR
**Escala**: um desenvolvedor, dezenas de sessões

---

## Constitution Check

### Core (I–VIII)

| Princípio | Verificação |
| --- | --- |
| I. Spec Governa Código | PASS — cada módulo e teste cita FR/INV/SC da spec; a matriz de rastreabilidade abaixo fecha FR-201 a FR-223, INV-201 a INV-215 (INV-215 da E4) e SC-201 a SC-209 (conferido por script a cada emenda) |
| II. Gate Obrigatório | PASS — `check-prerequisites` roda antes de cada fase; este plano só segue com PASS |
| III. Conclusividade | PASS — nenhum `[NEEDS CLARIFICATION]` aberto; limiares provisórios estão declarados, não pendentes |
| IV. Modo Declarado | PASS — feature de peso Code, pipeline completo |
| V. PT-BR First | PASS — identificadores, textos e documentos em português |
| VI. Especialização por Modo | PASS — agente de domínio do projeto declarado em `.arkan/config.md`, sem alteração |
| VII. Independência Estrutural | PASS — nenhuma importação de código de outras features |
| VIII. Agente Propõe, Humano Decide | PASS — E1/R1 e E2/R1.1 aprovadas em nível B em 2026-10-15; E3/R1.2 aprovadas em nível B em 2026-10-15 |

### Projeto (P1–P14)

| Princípio | Verificação |
| --- | --- |
| P1. Cadeia de conhecimento explícita | PASS — etapa de calibração e avaliação de regras reutilizam tipos existentes; `DERIVACOES_PERMITIDAS` não muda (ADR-204, 205, 210) |
| P2. Originais imutáveis | PASS — arquivo de ajuste no cofre por hash, sem leitura; `aprovacao` só inserção; **`configuracao` ganha gatilho de só inserção** na migração (R1, item 9) |
| P3. Cálculo determinístico; IA só identificada | PASS — σ̂, vales, detector, deficit são cálculos versionados com entradas por hash; sem IA |
| P4. Reduzir o risco ao equipamento | PASS — `seguranca.py` decide admissibilidade antes do registro; bloqueada nunca é executável; aprovação não verifica |
| P5. Nada é inventado | PASS — SEG-02/07/09 sem modelo (FR-212); suavização não é inferida, é declarada (E1) |
| P6. Diagnóstico com uma variável; calibração com conjunto | PASS — detector de mudança por via (E1); etapa sem atribuição causal |
| P7. Incerteza e limitação declaradas | PASS — σ̂ vira incerteza declarada; "não estimável", "não verificada" e resolução do detector sempre visíveis (INV-212) |
| P8. Critérios só mudam por decisão | PASS — limiares centralizados em `limiares.py` com rótulo provisório; validação (SC-208) não ajusta limiar sem `JV-D` |
| P9. IA substituível | N/A — sem IA neste incremento |
| P10. Não reinventar REW nem PC-Tool | PASS — formato de texto do REW mantido; arquivo do PC-Tool opaco |
| P11. Uma fonte canônica por estado | PASS — `status.md` e feature map atualizados ao fim |
| P12. Três gates | PASS — G1 testes, G2 revisão, G3 roteiro no Windows (um ponto por bloco) |
| P13. Sessão guiada; rastreabilidade | PASS — interpretação lida do registro (INV-211); cada número abre a cadeia |
| P14. Pessoal primeiro | PASS — nenhum recurso comercial |

**Resultado**: PASS

---

## Estrutura do Projeto

### Documentação (esta feature)

```
.arkan/features/lab-sq-jarvis/003-000-jv-v02-honestidade-e-seguranca/
├── 01-discovery/ideacao.md
├── 03-spec/spec.md                 (emenda E1)
├── 04-architecture/{plan.md, data-model.md, quickstart.md}
├── 06-planning/tasks.md            (/arkan.tasks)
└── 08-qa/{qa-report.md, validacao-limiares.md}
```

### Código-fonte

```
src/jarvis/
├── limiares.py            [novo]     todos os limiares do V02 com valor, rótulo provisório e FR de origem (ADR-211)
├── calculos.py            [alterado] + irregularidade, vales_individuais, faixa_util, detector_mudanca_via,
│                                       condicoes_comparaveis, deficit_cruzamento; entradas_sha256
├── regras.py              [alterado] + I-3, reordenação, portão de qualidade; VERSAO 1.1
├── regras_v1_0.py         [novo]     cópia congelada das regras 1.0, usada só para ler sessões legadas (INV-211)
├── seguranca.py           [novo]     classificação, regras SEG, admissibilidade; VERSAO "0.4.0" (regras canônicas)
├── calibracao.py          [novo]     resultado da etapa com precedência; texto sem atribuição causal
├── configuracao.py        [novo]     nome sugerido, reversão documentada (arquivo / receita / não documentada)
├── persistencia.py        [alterado] abertura com detecção de versão; aprovacao; ultima_configuracao; integridade
├── migracao.py            [novo]     impressão digital do esquema, backup, migração 0 → 2 transacional (ADR-207)
├── sessao.py              [alterado] dois fluxos (teste, etapa); portão de qualidade; comprometida com detector;
│                                       estado() lê interpretação registrada
├── referencia/
│   ├── ref001.py          [intacto]  REF-001-A byte a byte
│   ├── modelo.py          [novo]     modelo físico: alto-falante, filtros, atraso, polaridade, reflexão → H(f);
│                                       camada de aquisição: ruído e erros depois do modelo (ADR-201)
│   ├── casos.py           [novo]     catálogo dos casos e variantes
│   └── dados/<CASO>/      [novo]     arquivos gerados
└── interface/
    ├── janela.py          [alterado] seletor de caso, resultados novos; orquestra
    ├── seguranca_view.py  [novo]     "Verificação de segurança" e "alteração bloqueada"
    └── configuracao_view.py [novo]   arquivos de ajuste, confirmação inicial, reversão documentada
tests/
├── dados/banco-v01/       [novo]     banco e cofre produzidos pelo V01 real (main@389e580) + README de geração
├── test_casos.py, test_seguranca.py, test_calibracao.py, test_configuracao.py,
│   test_migracao.py, test_integridade.py, test_validacao_limiares.py          [novos]
└── test_calculos.py, test_regras.py, test_sessao.py, test_persistencia.py, test_interface.py   [ampliados]
ferramentas/gerar_banco_v01.py   [novo]  roda o percurso do V01 num checkout de 389e580 e grava a fixture
```

---

## ADRs

### ADR-201 — Modelo físico único e catálogo de casos *(ajustada na R1, item 10)*
- **Decisão:** `referencia/modelo.py` calcula a resposta complexa de cada via no microfone como um produto:
  - resposta do alto-falante (plana ou com ressonância e rolagem);
  - filtro (LR4, PEQ);
  - polaridade;
  - atraso (distância e ajuste do DSP);
  - efeitos acústicos (reflexão 1 + g·e^(−jωτ)).

  A soma é a soma complexa das vias. A **camada de aquisição** vem depois e aplica a cada arquivo, independentemente:
  - ruído relativo complexo (σ e semente no manifesto);
  - erros de aquisição (posição, ganho de entrada);
  - quantização do arquivo.

  `referencia/casos.py` descreve cada caso por parâmetros do modelo e da aquisição. O REF-001-A continua gerado por `ref001.py`, byte a byte.
- **Motivo:** INV-208 e INV-210. Determinismo não garante plausibilidade: magnitude, fase e soma precisam sair do mesmo H(f).
- **Alternativas descartadas:** perturbações independentes de magnitude e fase; um gerador por caso; arquivos escritos à mão.
- **Consequência:** um teste confere que a soma "antes do ruído" é a soma complexa das vias, e que nível e fase vêm do mesmo H. As variantes de teste (ruído, posição, ganho, filtro estreito) saem do mesmo gerador e alimentam o SC-208.

### ADR-202 — Irregularidade ponto a ponto (σ̂) *(revista na R1, item 3; emenda E1)*
- **Decisão:** a função `calculos.irregularidade(r, suavizacao)` faz duas coisas:
  1. Confere as condições de aplicação: grade logarítmica uniforme em ±0,5 %, ≥ 24 pontos por oitava, suavização `nenhuma`.
  2. Calcula σ̂ = 1,4826 · MAD(Δ²L) / √6 entre 200 Hz e 10 kHz.

  O resultado é `{sigma_db | None, aplicavel, condicoes{...}, classificacao: aprovada|aviso|reprovada|nao_estimavel, limiares}`. A função roda em **todas** as medições usadas na análise, inclusive somas.
- **Motivo:** o método anterior media curvatura espectral. Ele reprovaria a soma do REF-001-A (2,27 dB) e confundiria reflexões com ruído. A segunda diferença anula curvas suaves, e a mediana ignora o fundo de vales estreitos (evidência na Clarification E1).
- **Alternativas descartadas:**
  - resíduo × média móvel (mede o defeito, não o ruído);
  - coerência (exige repetições);
  - inferir suavização pela autocorrelação de Δ²: o teste mostrou que ela não separa os casos com segurança.
- **Consequência:** σ̂ não enxerga ruído correlacionado nem de baixa frequência (limite declarado). Arquivo externo sem declaração de suavização dá `nao_estimavel` (INV-212). **R1.1 (E2):** as observações descritivas continuam (curvas, níveis, sobreposição, soma de potências, vales, indícios marcados "qualidade não estimada"); só o que depende da qualidade fica limitado (incerteza não quantificada, veredito ≤ `inconclusiva`, etapa ≤ `inconclusivo`, bandas do detector inconclusivas, nenhuma hipótese confirmada). Os limiares 0,5 e 1,5 dB são candidatos e validados no SC-208.

### ADR-203 — Portão de qualidade devolve resultado *(ajustada)*
- **Decisão:** `Servico.analisar` devolve `nao_da_para_concluir` (motivo, o que falta) em vez de lançar `ErroDoPercurso`.
  - **R1:** o portão considera `reprovada` (bloqueia hipóteses, INV-201) e `nao_estimavel` (análise segue, incerteza "não quantificada", veredito no máximo `inconclusiva`).
  - O resultado do portão é **gravado** no cálculo `avaliacao_regras` (ADR-210).
- **Motivo:** a interface precisa mostrar a explicação, e o diário e a cadeia registram a recusa.
- **Alternativas descartadas:** exceção (perde a estrutura da explicação).
- **Consequência:** `estado()["analise"]` ganha `qualidade` e `conclui`; as chaves do V01 continuam lá.

### ADR-204 — Segurança, admissibilidade e aprovação *(revista na R1, itens 4 e 6)*
- **Decisão:** `seguranca.py` tem três funções puras: `classificar(alteracao)`, `avaliar(alteracao, equipamento) -> list[ResultadoRegra]` e `admissibilidade(classe, resultados) -> {admissivel, estado: recomendada|bloqueada, motivo, falta[], nao_verificadas[]}`, que segue a definição normativa E1.
  - **Toda** recomendação passa por elas **antes** do registro, inclusive a de polaridade: `propor_teste` deixa de gravar um bloco de segurança fixo no código.
  - Uma alteração bloqueada é registrada como `recomendacao` com `admissibilidade.admissivel = false`, título "Alteração bloqueada — não recomendada" e **sem receita**. `registrar_aplicacao` e `aprovar` a recusam.
  - **Aprovação de nível B** fica na tabela própria `aprovacao` (só inserção). Ela só é aceita para recomendação **existente**, do tipo `recomendacao`, **da mesma sessão**, **sensível**, **admissível** e ainda não aprovada.
  - O escopo (canal, parâmetro, de, para) precisa coincidir com a alteração da recomendação, e o momento precisa ser posterior ao registro dela.
  - A aprovação não altera `seguranca.regras[]`; o teste compara antes e depois.
- **Motivo:** P4 e JV-D032. A revisão (item 4) pede que o SEG participe da admissibilidade. `DERIVACOES_PERMITIDAS` reflete o P1, e aprovação é autorização do usuário, não derivação técnica.
- **Alternativas descartadas:**
  - aprovação como `decisao ← recomendacao` (exige emenda ao P1);
  - avaliar SEG só para exibição (permitiria recomendar algo bloqueado).
- **Consequência:** a verificação se dá em três camadas: serviço, gatilho `BEFORE INSERT` (recomendação existente, mesma sessão, tipo certo) e rotina de integridade.
  - **R1.1 (E2, FR-223):** polaridade e atrasos não são sensíveis, então os casos de referência não exercitam aprovação nem bloqueio. Por isso entram os casos sintéticos `REF-003-S1` (**R1.2/E3:** reforço com equipamento confirmado → **bloqueado por SEG-07**, já que margem digital não tem método; sem exceção de simulação), `-S2` (mesmo reforço, equipamento `planejado` → bloqueado por SEG-12 e SEG-07) e `-S3` (corte com regra sem dado → risco decrescente com aviso → aprovação B). O manifesto traz `equipamento` (sintético, com `estado`) e `alteracao_candidata`; o serviço ganha `avaliar_alteracao_candidata()`, que passa pela mesma classificação, regras e admissibilidade de qualquer recomendação. Exercitados em `test_sessao.py::test_s1_s2_s3`, `test_interface.py::test_casos_seguranca` e no G3 do bloco 2 (SC-209), além do SC-204.

### ADR-205 — Dois fluxos no serviço: teste de diagnóstico e etapa de calibração *(revista na R1, item 2)*
- **Decisão:** reutilizar `recomendacao`, `experimento` e `conclusao` com `tipo_intervencao` ∈ {`teste de diagnóstico`, `etapa de calibração`}, sem tocar em `DERIVACOES_PERMITIDAS`.
  - A sessão de etapa usa `modo = "etapa-simulada"`. `modo = "calibracao"` continua recusado até o V04, o que preserva o teste do V01.
  - Adaptações explícitas no serviço:

  | Método | Teste de diagnóstico | Etapa de calibração |
  | --- | --- | --- |
  | `propor_teste` | como no V01 + admissibilidade SEG | recusa ("use propor_etapa") |
  | `propor_etapa` (novo) | recusa | exige objetivo e limites (SEG-13) registrados antes; recusa com deficit "antes" ≤ 3 dB |
  | `registrar_aplicacao` | `variavel` (comportamento do V01) | `conjunto`: todos os parâmetros entram na nova configuração declarada; recusa alteração bloqueada ou sensível sem aprovação |
  | `importar_depois` | soma + vias individuais opcionais | soma + vias opcionais; exige objetivo registrado |
  | `concluir` / `concluir_etapa` | veredito com precedência E1 | resultado da etapa; cada um recusa o fluxo do outro |
  | `decidir` | manter/reverter com `configuracao.reversao` | idem |
  | `estado()` | chaves do V01 + `fluxo`, `verificacao_variavel_unica` | `fluxo`, `etapa`, `resultado_etapa` |
  | `resumo()` | como no V01 + `comprometida` e limitações | "Etapa de calibração: <resultado>; não verificados: …" |
- **Motivo:** `propor_teste`, `registrar_aplicacao`, `estado` e `resumo` pressupõem `variavel`, `previsao` e `veredito` (revisão, item 2).
- **Alternativas descartadas:** tipos novos de registro (exigem emenda ao P1); um único método com `if` espalhado sem recusa explícita.
- **Consequência:** os testes cobrem criar, executar, encerrar, listar no Histórico e reabrir os dois fluxos. Veredito de teste e resultado de etapa nunca se misturam (INV-206 e integridade).

### ADR-206 — Arquivo de ajuste opaco e reversão documentada *(ajustada na R1, item 8)*
- **Decisão:** o arquivo de ajuste é um arquivo opaco no cofre (`arquivo_original.tipo = 'ajuste-pctool'`), ligado por `configuracao.arquivo_sha256`.
  - A função pura `configuracao.reversao(...)` devolve `{documentada, modo: arquivo|receita|nenhum, falta[], confirmacao_fisica: false, aviso}`.
  - **R1:** `Banco.ultima_configuracao()` busca a mais recente **entre sessões** (`ORDER BY id DESC LIMIT 1`), com a sessão de origem. `decidir("reverter")` usa a reversão documentada no lugar da cópia da primeira configuração da sessão.
- **Motivo:** JV-D039/D040. O V01 só consulta configurações da sessão informada (revisão, item 8). Arquivar não garante compatibilidade com o DSP nem aplicação correta.
- **Alternativas descartadas:** ler o conteúdo (é a F019); guardar só valores.
- **Consequência:** a chave `garantida` dos registros do V01 continua legível; a interface a apresenta como "documentada". A confirmação física (nova medição comparada ao "antes") fica fora do V02 e é dita na tela.

### ADR-207 — Migração do banco legado *(corrigida na R1, item 1)*
- **Decisão:** `Banco.__init__` é reorganizado. **Nada roda antes da detecção de versão.**
  1. **Arquivo inexistente ou sem tabelas** → cria o esquema 2 numa transação e grava `user_version = 2`.
  2. **Arquivo existente** → abre em **somente leitura** (`file:…?mode=ro`) e lê `user_version` e a **impressão digital** do esquema: nomes e SQL normalizado de tabelas e gatilhos em `sqlite_master`.
  3. **`user_version = 0` e impressão igual à do V01** → executa, nesta ordem:
     - **backup consistente** pela API `Connection.backup` em `jarvis.antes-v02-<AAAAMMDD-HHMMSS>.db`;
     - `PRAGMA integrity_check` do backup e contagem de linhas igual à do original; só então abre para escrita;
     - `BEGIN IMMEDIATE`, comandos individuais (**sem** `executescript`, que faz commit implícito) e `PRAGMA user_version = 2`;
     - `COMMIT`. Em erro: `ROLLBACK`, o backup fica e o erro é explicado ao usuário.
  4. **`user_version = 2`** com a impressão do V02 → abre normalmente. É a idempotência: uma segunda abertura não faz backup nem altera nada.
  5. **Qualquer outro caso** (versão 1, maior que 2, ou impressão desconhecida) → `ErroVersaoBanco`, **sem modificar o arquivo**.

  O que a migração 0 → 2 faz:
  - cria `aprovacao` e seus gatilhos;
  - cria os gatilhos de só inserção de `configuracao`;
  - cria o gatilho `BEFORE INSERT` de `aprovacao`.

  Nenhuma linha do V01 é alterada e o cofre não é tocado.
- **Motivo:** o V01 não grava `user_version` (o banco do desenvolvedor está em 0) e roda o esquema antes de qualquer migração (revisão, item 1, confirmado no código).
- **Alternativas descartadas:**
  - `CREATE … IF NOT EXISTS` no V01 sem versão (não distingue um banco desconhecido);
  - recriar o banco;
  - migração manual.
- **Consequência:** `test_migracao.py` usa uma **fixture produzida pelo V01 real**: `ferramentas/gerar_banco_v01.py` roda o percurso completo do REF-001-A num checkout de `main@389e580` e grava `tests/dados/banco-v01/`. **R1.1 (E2):** a fixture contém só dados sintéticos (sessões do REF-001-A), é versionada, nunca é regenerada sem `JV-D` e fica permanente como teste de regressão da migração. Um teste confere que os originais do cofre da fixture são os arquivos do REF-001-A. No G3 do bloco 1, o desenvolvedor abre o próprio banco no Windows, com o backup gerado.

### ADR-208 — `comprometida`: verificação da variável única por via *(ampliada na R1, item 7; emenda E1)*
- **Decisão:** a verificação tem duas partes.
  - **(a)** Configuração declarada "depois" contra a proposta.
  - **(b)** Para **cada via** com medição individual "antes" e "depois":
    - `condicoes_comparaveis` (posição, `ganho_entrada_db`, `referencia_nivel`);
    - `faixa_util`;
    - `detector_mudanca_via`: média > 1,0 dB, ou bandas deslizantes de 1/3 de oitava > max(1,5; 3σΔ);
    - resultado `mudança detectada` | `mudança não detectada (resolução …)` | `verificação inconclusiva`. Sem dado, a via fica "não verificada".

  O veredito segue a **precedência E1**, e tudo fica gravado em `conclusao.dados.verificacao_variavel_unica`. O manifesto aceita `via_a` e `via_b` com `momento: "depois"`.
- **Motivo:** a média entre 1 e 10 kHz não detectou EQ estreita (0 %). O detector híbrido detectou o N3 em 100 % dos casos, sem falso positivo em "só polaridade" até σ = 1,5 (evidência na Clarification E1). *(E4: a medição ampliada em `08-qa/validacao-limiares-e4.md` mostrou 87/1 000 alarmes indicativos e 12/1 000 confirmados em σ = 1,5 dB; a frase de 'sem falso positivo até σ = 1,5' não vale e fica como limitação conhecida. Texto original preservado.)*
- **Alternativas descartadas:** só (a); máximo pontual sem suavização (falsos positivos com ruído); limiar único sem margem de ruído.
- **Consequência:**
  - Sem medições individuais "depois", vale só (a), com o aviso. O REF-001-A continua `confirmada` (INV-210).
  - Variantes de teste do N3: só declarada; só medida; posição diferente ⇒ inconclusiva; ruído alto ⇒ resolução maior.
  - **R1.2 (E3, A03/A07):** a comparabilidade é **declarada**. `mudança detectada` com uma só medição "depois" é indicativa e leva no máximo a `inconclusiva`; só com repetição (segunda medição individual "depois", com o microfone recolocado) ela vira `comprometida`. O N3 passa a ter duas **aquisições independentes** "depois" do tweeter, cada uma com registro e `aquisicao_id` próprios, ambas com +3 dB. O texto diz que a mudança foi reproduzida, mas não identifica o parâmetro. **Serviço:** `Servico._medicao(papel, momento)` devolve só a última medição; o V02 acrescenta `_medicoes(papel, momento) -> list`, e `importar_depois` aceita várias medições por via. Uma cópia com o mesmo SHA-256 ou o mesmo `aquisicao_id` é recusada como repetição. **Presunções:** só para caso do catálogo interno com proveniência verificada (caso listado em `casos.listar()` e SHA-256 dos arquivos iguais aos gerados); `simulado: true` sozinho não concede nada (INV-214). O veredito `confirmada` passa a exigir somas "antes" e "depois" com aquisição comparável declarada; sem isso, "melhora observada, sem confirmação causal". Testes novos:
    - `test_n3_sem_repeticao_inconclusiva`;
    - `test_reposicionamento_nao_compromete` (o gerador desloca um nulo estreito sem mexer no DSP);
    - `test_depois_outra_posicao_nao_confirma`;
    - `test_copia_nao_e_repeticao`, `test_mudanca_reproduzida_nao_nomeia_parametro`;
    - (E4) `test_repeticao_exige_faixa_compativel`: duas aquisições com mudança no mesmo sentido mas em faixas disjuntas ⇒ indicativa, não confirmada;
    - `test_casos.py::test_proveniencia_catalogo` (arquivo do catálogo alterado em 1 byte perde as presunções), `test_sessao.py::test_simulado_declarado_nao_presume`.

### ADR-212 — Correções do V01 na fundação *(nova na R1.2; revisão adversarial A02, A04, A06)*
- **Decisão:**
  - **A04 — portão básico obrigatório:** `Servico.analisar` recusa medição com `qualidade_basica.aprovada = false`, explicando o motivo (faixa não coberta, valores inválidos). `calculos.diferenca_fase` e `sobreposicao` exigem amostras mínimas (≥ 8 pontos e ≥ 1/3 de oitava de sobreposição, provisório em `limiares.py`); abaixo disso, fase e atraso ficam "não calculáveis", sem regressão degenerada.
  - **A06 — cofre atômico e reconciliado:** `guardar_original` copia para `cofre/.tmp/<uuid>`, confere o hash da cópia, move com `os.replace` (atômico no mesmo volume) e só então insere o inventário. Se o arquivo já existe, confere o hash e **reconcilia** (`INSERT OR IGNORE` sempre), em vez de retornar antes do inventário. `integridade()` passa a varrer o cofre físico: acusa arquivo sem linha em `arquivo_original`, linha sem arquivo, hash divergente e restos em `.tmp`.
  - **A02 — referência temporal declarada:** `calculos.referencia_temporal` passa a exigir `tipo` ≠ `nenhuma`, `id`, `taxa_amostragem` e `posicao_microfone` presentes e não vazios, e devolve `{compativel, declarada: true, motivos}`. A interface diz "declarada compatível". A versão sobe para 1.1, e a interpretação das sessões antigas fica congelada (INV-211).
- **Motivo:** os três defeitos foram reproduzidos no código do V01 durante a conferência da revisão adversarial.
  - A02: medições sem `id` nem taxa saíam compatíveis.
  - A04: o portão básico era ignorado, e um único ponto de sobreposição dava atraso 0 com `RankWarning`.
  - A06: um arquivo órfão não entrava no inventário, e a integridade não acusava nada.
- **Alternativas descartadas:** deixar para um incremento de manutenção (o V02 depende do portão e da integridade); confiar em `chmod` e gatilhos como garantia física. "Imutável" passa a ser política de preservação e detecção, não impossibilidade física.
- **Consequência:** os testes do V01 continuam passando, porque o REF-001-A cobre a faixa, tem todos os campos de referência e não tem órfãos. Testes negativos novos:
  - `test_sessao.py::test_qualidade_basica_reprovada_bloqueia`;
  - `test_calculos.py::test_sobreposicao_insuficiente`, `::test_referencia_campos_ausentes`;
  - `test_persistencia.py::test_falha_entre_copia_e_insert_reconcilia`, `::test_orfao_no_cofre_detectado`, `::test_tmp_residual_detectado`.

### ADR-213 — Origem declarada como registro primário `declaracao` *(patch do P1; JV-D046)*
- **Decisão:** `persistencia.PREFIXOS["declaracao"] = "L"`; `DERIVACOES_PERMITIDAS["calculo"]` aceita `declaracao`; `declaracao` não é destino de derivação. `Servico._registrar_declaracao`, chamada por `importar_caso`, guarda o manifesto no cofre e registra uma declaração por manifesto quando ele traz `equipamento` ou `alteracao_candidata`. `Banco._problemas_de_declaracao` confere, na `integridade()`, ausência de origens, marca, hash no cofre, snapshot contra o manifesto preservado e coerência de caso.
- **Motivo:** `avaliacao_seguranca` usa dado declarado; derivá-la de medição falsearia a proveniência (P1, P3). Alternativa B (cálculo sem origem) rejeitada por abrir exceção por nome.
- **Consequências:** segundo tipo-raiz, contido por: só `calculo` deriva, hash e snapshot conferidos, marca `declarado`. Sem migração; histórico intacto (INV-211). A JV-T228 consome a declaração; a interface (JV-T230) deve dizer que é afirmação, não prova do estado físico.

### ADR-209 — Interface *(ajustada)*
- **Decisão:** `janela.py` orquestra; os blocos novos ficam em `seguranca_view.py` e `configuracao_view.py`. O seletor de caso lê o catálogo, e a etapa aparece no passo 4 quando a sessão é `etapa-simulada`.
  - **R1:** a interface mostra:
    - "Alteração bloqueada — não recomendada", sem botão de aplicar;
    - o resultado do detector por via, com resolução;
    - "ruído não estimável";
    - "reversão documentada (restauração física não confirmada)".
- **Motivo:** `janela.py` já tem 638 linhas; ADR-03: a interface não calcula.
- **Alternativas descartadas:** tudo em `janela.py`; um passo novo na barra lateral.
- **Consequência:** os cinco passos e o Histórico não mudam; o Histórico mostra o modo da sessão.

### ADR-210 — Versionamento e interpretação congelada *(ajustada na R1, item 5; INV-211)*
- **Decisão:**
  - `regras.VERSAO` passa de 1.0 para 1.1.
  - As funções novas de `calculos` ganham versão em `VERSOES`, e `seguranca.VERSAO` = "0.4.0" (regras canônicas).
  - `INCREMENTO = "JV-V02"`, versão 0.2.0.
  - **R1:** todo cálculo grava `entradas_sha256`: o hash do arquivo, para medições, e o SHA-256 do JSON canônico de `dados`, para outros registros.
  - A **avaliação das regras** passa a ser gravada como cálculo `avaliacao_regras`, derivado dos cálculos que usa (`calculo ← calculo`, já permitido). Ela guarda versão, snapshot dos limiares, portão de qualidade, sugestão, motivo e ordem das hipóteses.
  - `estado()` **lê** essa avaliação e não chama mais `regras.avaliar`.
  - Para sessões do V01, que não têm `avaliacao_regras`, `estado()` usa `regras_v1_0.py` (cópia congelada) e marca a análise como "reconstruída pelas regras 1.0".
- **Motivo:** o `estado()` do V01 reexecuta `regras.avaliar` a cada abertura (`sessao.py:485`), então mudar as regras mudaria a interpretação histórica (revisão, item 5).
- **Alternativas descartadas:** não versionar; exigir retroativamente metadados das sessões V01.
- **Consequência:** reabrir uma sessão nunca muda o que ela disse. Um teste grava a sessão, troca `regras.VERSAO` e os limiares por monkeypatch, reabre e compara.

### ADR-211 — Limiares centralizados e validação por varredura *(nova na R1; SC-208)*
- **Decisão:** `limiares.py` reúne todos os limiares do V02 como `{valor, unidade, provisorio, origem: "spec E1 / FR-…"}`. `regras.LIMIARES` e `sessao.CRITERIO_ACEITE` do V01 continuam onde estão, para não mexer nas asserções do V01.
  - Cada registro grava o snapshot dos limiares que usou.
  - `test_validacao_limiares.py` varre σ, amplitudes de mudança, Q de filtros, deficit e limites SEG, com valores logo abaixo e logo acima de cada limite, e escreve `08-qa/validacao-limiares.md` com falsos positivos e falsos negativos.
- **Motivo:** revisão, "Avaliação dos limiares provisórios": validar sem ajustar só para os casos de referência passarem (P8).
- **Alternativas descartadas:** limiares espalhados nos módulos; validação só pelos casos de referência.
- **Consequência:** mudar um limiar é uma alteração num único lugar, com `JV-D` e reexecução da varredura.

---

## Dependências e Interfaces

### Dependências (esta feature consome)

| Depende de | Como | Observação |
| --- | --- | --- |
| JV-V01 em `main` (`389e580`) | `sessao.Servico`, `calculos`, `regras`, `persistencia`, `ref001`, interface | mantido sem quebra (INV-210); fixture do banco gerada a partir dele |
| Constituição v0.4.0, regras de segurança v0.4.0 | requisitos e invariantes; SEG-01 a SEG-13; classes de risco (seção 1) | provisórios continuam provisórios |
| PySide6, pyqtgraph, numpy | `requirements.txt` | sem novas dependências |
| Partes de F002, F003, F005, F006, F007 | entregues neste incremento | registro de entregas no feature map ao fim (JV-D041) |

### Interfaces Expostas (contratos internos)

- `modelo.resposta_via(params, f) -> complex[]`; `modelo.adquirir(H, aquisicao, semente) -> RespostaFrequencia`; `casos.listar() -> list[Caso]`; `casos.gerar(nome, pasta) -> Path`.
- `calculos.irregularidade(r, suavizacao) -> dict`; `vales_individuais(r) -> dict`; `faixa_util(r) -> list[int]`; `condicoes_comparaveis(meta_antes, meta_depois) -> dict`; `detector_mudanca_via(antes, depois, sigma_antes, sigma_depois, faixa) -> dict`; `deficit_cruzamento(soma, potencias, indices) -> dict`.
- `regras.avaliar(..., vales_individuais=None, qualidade=None)`: as chamadas do V01 continuam válidas.
- `seguranca.classificar(alteracao) -> str`; `seguranca.avaliar(alteracao, equipamento) -> list[ResultadoRegra]`; `seguranca.admissibilidade(classe, resultados) -> dict`.
- `calibracao.resultado(deficit_antes, deficit_depois, qualidade, referencia) -> dict`.
- `configuracao.nome_sugerido(...)`; `configuracao.reversao(alteracoes, anterior, arquivo_antes) -> dict`.
- `migracao.detectar(caminho) -> Versao`; `migracao.migrar_0_para_2(caminho) -> Path` (devolve o backup).
- `Banco.ultima_configuracao() -> dict | None`; `Banco.nova_aprovacao(...)`.
- `Servico` ganha `propor_etapa`, `importar_depois_etapa`, `concluir_etapa`, `aprovar(recomendacao, escopo)`, `arquivar_ajuste(configuracao, caminho)`, `confirmar_configuracao_inicial`, `reversao()`.

---

## Mapa de Agentes por Fase

| Fase | Modo | Command | Agente(s) | Técnica(s) | Artefato de Saída |
| --- | --- | --- | --- | --- | --- |
| 01 — Discovery | Assistência | `arkan.ideacao` | Research, Intake, Briefing | debate estruturado | `01-discovery/ideacao.md` |
| 03 — Spec | Geração | `arkan.spec` / `arkan.clarify` | Spec Writer, NFR, BDD, Business Rules | definições normativas, INV com teste; emenda E1 | `03-spec/spec.md` |
| 04 — Architecture | Geração | `arkan.plan` | Architect, Data Modeler, API Designer, Security Analyst | ADRs, Constitution Check, matriz | `04-architecture/plan.md` |
| 06 — Planning | Geração | `arkan.tasks` | Task Planner | decomposição por bloco | `06-planning/tasks.md` |
| 07 — Implement | Assistência | `arkan.implement` | Implementador | task a task, G1 | `src/`, `tests/` |
| 08 — QA | Orquestração | `arkan.qa` | QA | spec↔código, UAT, invariantes, validação de limiares | `08-qa/qa-report.md`, `08-qa/validacao-limiares.md` |
| 09 — Deploy | Assistência | `arkan.deploy` | Deploy (N/A: uso local, entrega por `main`) | — | registro no feature map |

---

## Sequência de Implementação

### Fase 0 — Fundação (bloqueia o resto)

0. **Correções do V01** (ADR-212, R1.2): portão básico obrigatório e amostras mínimas (A04), cofre atômico e reconciliado com varredura física na integridade (A06), referência temporal declarada com campos obrigatórios (A02). Cada correção vem acompanhada dos seus testes negativos, e a suíte do V01 continua passando.
1. **Migração** (ADR-207): `migracao.py`, reorganização de `Banco.__init__`, `aprovacao` e gatilhos de `configuracao`; fixture do V01 real; `test_migracao.py`.
2. **Interpretação congelada** (ADR-210, INV-211): `avaliacao_regras` gravada, `entradas_sha256`, `regras_v1_0.py`, `estado()` lendo do registro. Isto vem **antes** de mexer em `regras.py`.
3. **Modelo físico e catálogo** (ADR-201): `modelo.py`, `casos.py`, dados dos casos e variantes; testes de determinismo, coerência física e REF-001-A byte a byte.
4. **Contratos de qualidade e de segurança** (ADR-202, 204, 211): `limiares.py`, `calculos.irregularidade`, `seguranca.classificar`/`avaliar`/`admissibilidade` com testes de contrato. Eles vêm antes de qualquer recomendação nova.

### Fase 1 — Bloco 1: casos e honestidade (US-01 a US-04)

5. `calculos`: vales individuais, faixa útil, condições comparáveis, detector (FR-202, FR-204, FR-207).
6. `regras` 1.1: I-3, reordenação, portão de qualidade (FR-203, FR-204). `sessao`: N4 (FR-205), N5 (FR-206), `comprometida` com precedência (FR-207), REF-001-B (FR-208).
7. Validação por varredura de σ̂ e do detector (SC-208 a, b).
8. Interface: seletor de caso e resultados (FR-209). **Ponto de teste G3 do bloco 1**, que inclui abrir o banco real do desenvolvedor (migração com backup).

### Fase 2 — Bloco 2: segurança (US-05, US-08)

9. `seguranca.py` completo: SEG-01/03/04/05/06/08/10/11/12/13 e SEG-02/07/09 não verificáveis (FR-210 a FR-213); casos permitidos, limítrofes e proibidos; teste de propriedade (SC-204).
10. Integração: `propor_teste` passa pela admissibilidade (FR-211); alteração bloqueada; aprovação de nível B com integridade (FR-216); `seguranca_view.py` (FR-214, FR-215); varredura dos limites SEG (SC-208 c).
11. Casos de segurança `REF-003-S1` a `S3` no catálogo, `avaliar_alteracao_candidata()` e telas de admissão, bloqueio e aprovação (FR-223, SC-209). **Ponto de teste G3 do bloco 2**, que percorre os três casos no Windows.

### Fase 3 — Bloco 3: calibração, configuração e fluxo completo (US-06, US-07)

12. `calibracao.py`, fluxo `etapa-simulada` no serviço (ADR-205), quatro variantes e casos-limite (FR-217, FR-218, SC-203).
13. `configuracao.py`, arquivo opaco, última configuração entre sessões, reversão documentada, `configuracao_view.py` (FR-219 a FR-221, SC-205).
14. Integridade estendida com inconsistências deliberadas (FR-222).
15. Fluxo completo dos dois tipos de sessão: criar, executar, encerrar, Histórico, reabrir (sem recálculo). **Ponto de teste G3 do bloco 3.**

### Fase N — Polish

16. `COMO-EXPERIMENTAR.md` atualizado, capturas de tela (`ferramentas/capturas.py`), `08-qa/validacao-limiares.md` consolidado, pacote, QA e registro de entregas.

---

## Matriz de rastreabilidade

Legenda de módulos: `calc` = `calculos.py`, `seg` = `seguranca.py`, `cal` = `calibracao.py`, `conf` = `configuracao.py`, `pers` = `persistencia.py`, `mig` = `migracao.py`, `ses` = `sessao.py`, `UI` = `interface/*`. Testes em `tests/`. Bloco: F = fundação, 1/2/3 = blocos.

### Requisitos funcionais

| Req. | Módulo(s) | Teste(s) | ADR | Bloco |
| --- | --- | --- | --- | --- |
| FR-201 | `referencia/modelo.py`, `referencia/casos.py` | `test_casos.py::test_deterministico`, `::test_coerencia_fisica`, `::test_conteudo_esperado[caso]`, `::test_ruido_registrado`, `::test_ref001a_intacto` | 201 | F |
| FR-202 | `calc.irregularidade`, `limiares` | `test_calculos.py::test_irregularidade_ruido_conhecido`, `::test_irregularidade_nao_confunde_vale`, `::test_condicoes_aplicacao`, `::test_nao_estimavel_nao_aprova` | 202 | F/1 |
| FR-203 | `regras` (portão), `ses.analisar` | `test_sessao.py::test_n2`, `::test_qualidade_limita_conclusao` | 203 | 1 |
| FR-204 | `calc.vales_individuais`, `regras` (I-3) | `test_regras.py::test_i3_reordena_hipoteses`, `test_sessao.py::test_n1` | 210 | 1 |
| FR-205 | `calc.referencia_temporal` (1.1, declarada), `ses.analisar` | `test_sessao.py::test_n4`, `test_calculos.py::test_referencia_campos_ausentes` | 212 | F/1 |
| FR-206 | `regras`, `ses.decidir_sem_intervencao` | `test_sessao.py::test_n5` | — | 1 |
| FR-207 | `calc.faixa_util`, `calc.condicoes_comparaveis`, `calc.detector_mudanca_via`, `ses.importar_depois`, `ses.concluir` | `test_calculos.py::test_detector_mudanca`, `test_sessao.py::test_n3`, `::test_n3_so_declarada`, `::test_n3_so_medida`, `::test_n3_posicao_diferente_inconclusiva`, `::test_n3_sem_repeticao_inconclusiva`, `::test_reposicionamento_nao_compromete`, `::test_repeticao_exige_faixa_compativel`, `::test_sem_dados_nao_e_sem_mudanca` | 208 | 1 |
| FR-208 | `ses.concluir` (incerteza de σ̂; aquisição comparável declarada) | `test_sessao.py::test_ref001b`, `::test_nao_estimavel_limita_veredito`, `::test_depois_outra_posicao_nao_confirma` | 202, 203, 208 | 1 |
| FR-209 | `UI/janela.py` | `test_interface.py::test_seletor_casos`, `::test_textos_resultados`, `::test_mudanca_suspeita_sem_afirmar_dsp` | 209 | 1 |
| FR-210 | `seg.classificar` | `test_seguranca.py::test_classificacao` | 204 | 2 |
| FR-211 | `seg.avaliar`, `seg.admissibilidade`, `ses.propor_teste` | `test_seguranca.py::test_seg01` … `::test_seg13` (permitido/limítrofe/proibido), `::test_admissibilidade`, `test_sessao.py::test_polaridade_passa_por_seguranca` | 204 | F/2 |
| FR-212 | `seg` | `test_seguranca.py::test_seg02_07_09_nao_verificaveis` | 204 | 2 |
| FR-213 | `seg` | `test_seguranca.py::test_seg12_planejado_nao_confirma` | 204 | 2 |
| FR-214 | `seg`, `UI/seguranca_view.py` | `test_seguranca.py::test_provisorios_rotulados`, `test_interface.py::test_provisorio_visivel` | 204, 209 | 2 |
| FR-215 | `UI/seguranca_view.py` | `test_interface.py::test_verificacao_em_toda_recomendacao`, `::test_bloqueada_sem_aplicar` | 209 | 2 |
| FR-223 | `referencia/casos.py` (REF-003-S), `seg`, `ses.avaliar_alteracao_candidata`, `ses.aprovar`, `UI/seguranca_view.py` | `test_casos.py::test_conteudo_esperado[REF-003-S*]`, `test_sessao.py::test_s1_s2_s3`, `test_interface.py::test_casos_seguranca` | 204 | 2 |
| FR-216 | `pers` (`aprovacao`), `ses.aprovar` | `test_seguranca.py::test_aprovacao_nao_verifica`, `test_persistencia.py::test_aprovacao_integridade[*]` | 204 | 2 |
| FR-217 | `cal`, `ses.propor_etapa`, `ses.concluir_etapa`, `calc.deficit_cruzamento` | `test_calibracao.py::test_variantes[atingido,parcial,nao-atingido,inconclusivo]`, `::test_casos_limite`, `::test_objetivo_ja_atendido` | 205 | 3 |
| FR-218 | `cal`, `ses` | `test_calibracao.py::test_nao_verificado_lista_origem` | 205 | 3 |
| FR-219 | `conf.nome_sugerido`, `pers.guardar_original`, `ses.arquivar_ajuste` | `test_configuracao.py::test_arquivo_opaco`, `::test_nome_sugerido` | 206 | 3 |
| FR-220 | `pers.ultima_configuracao`, `ses.confirmar_configuracao_inicial`, `UI/configuracao_view.py` | `test_configuracao.py::test_ultima_entre_sessoes`, `test_interface.py::test_confirmacao_inicial` | 206 | 3 |
| FR-221 | `conf.reversao`, `ses.decidir` | `test_configuracao.py::test_reversao_tres_desfechos`, `::test_documentada_nao_e_fisica`, `::test_chave_garantida_v01_legivel` | 206 | 3 |
| FR-222 | `pers.integridade` | `test_integridade.py::test_inconsistencia[*]` (uma por verificação do data-model) | 204, 206, 207 | 3 |

### Invariantes

| Inv. | Módulo(s) | Teste(s) |
| --- | --- | --- |
| INV-201 | `regras`, `ses`, `calc.irregularidade` | `test_sessao.py::test_qualidade_limita_conclusao`, `test_calculos.py::test_irregularidade_nao_confunde_vale` |
| INV-202 | `ses.concluir` | `test_sessao.py::test_comprometida_nao_refuta` |
| INV-203 | `seg`, `ses`, `pers` | `test_seguranca.py::test_aprovacao_nao_verifica`, `::test_admissibilidade`, `::test_propriedade_sem_violacao` |
| INV-204 | `seg` (SEG-06), `regras` | `test_seguranca.py::test_seg06`, `test_sessao.py::test_n1` |
| INV-205 | `conf.reversao` | `test_configuracao.py::test_reversao_nao_documentada`, `::test_documentada_nao_e_fisica` |
| INV-206 | `cal` | `test_calibracao.py::test_sem_atribuicao_causal` |
| INV-207 | `conf`, `pers` | `test_configuracao.py::test_arquivo_opaco`; QA: busca por escrita ao DSP |
| INV-208 | `modelo`, `casos`, todos os cálculos | `test_casos.py::test_deterministico` |
| INV-209 | — | QA: `git diff` das pastas do Core contra a fundação |
| INV-210 | todos | suíte do V01 sem alterar asserções; `test_migracao.py::test_v01_real_migra_preservando` |
| INV-211 | `ses.estado`, `regras_v1_0`, `pers` | `test_sessao.py::test_reabrir_nao_recalcula`, `test_persistencia.py::test_sessao_v01_legivel` |
| INV-212 | `calc`, `ses` | `test_calculos.py::test_nao_estimavel_nao_aprova`, `::test_nao_estimavel_preserva_descritivo`, `test_sessao.py::test_sem_dados_nao_e_sem_mudanca` |
| INV-213 | `referencia/casos.py`, `ref001.py` | `test_casos.py::test_deterministico`, `::test_ref001a_intacto` |
| INV-215 (E4) | `ses._verificacao_variavel_unica` (confirmação), `calc.detector_mudanca_via` | `test_sessao.py::test_repeticao_exige_faixa_compativel`, `::test_copia_nao_e_repeticao` |
| INV-214 | `referencia/casos.py` (hashes esperados), `ses._importar_medicao` (proveniência), `calc.irregularidade`, `calc.condicoes_comparaveis` | `test_casos.py::test_proveniencia_catalogo`, `test_sessao.py::test_simulado_declarado_nao_presume` |

### Critérios de sucesso

| SC | Instrumento | Bloco |
| --- | --- | --- |
| SC-201 | `test_sessao.py::test_n1` a `::test_n5` | 1 |
| SC-202 | `test_sessao.py::test_ref001b` | 1 |
| SC-203 | `test_calibracao.py` (4 variantes + casos-limite) | 3 |
| SC-204 | `test_seguranca.py::test_propriedade_sem_violacao` (1 000 alterações, semente fixa) | 2 |
| SC-205 | `test_configuracao.py::test_reversao_tres_desfechos` | 3 |
| SC-206 | roteiro `COMO-EXPERIMENTAR.md` no Windows (G3 por bloco) | 1/2/3 |
| SC-207 | `python -m pytest` em Linux (V01 + V02) | N |
| SC-208 | (E4: critério revisto) `test_validacao_limiares.py` → `08-qa/validacao-limiares.md` (preservado) e `ferramentas/medir_e4.py` → `08-qa/validacao-limiares-e4.md`; `test_oraculos.py` (vetores analíticos: quadratura, LR4, atraso puro), `test_metamorficos.py` (ganho global, troca de vias); domínio declarado: só simulado (E3) | 1/2/3 |
| SC-209 | `test_sessao.py::test_s1_s2_s3`, `test_interface.py::test_casos_seguranca`, G3 do bloco 2 | 2 |

---

## Critérios de teste das correções da revisão

| # | Correção | Critério de aceite (teste) |
| --- | --- | --- |
| 1 | Migração (ADR-207) | `test_migracao.py`. **Primeiro grupo — o caso normal:** <ul><li>`test_banco_novo_nasce_v2`: `user_version` = 2 e esquema completo.</li><li>`test_v01_real_migra_preservando`: a fixture do V01 vai para v2 e o dump de todas as tabelas do V01 fica idêntico; a sessão abre no Histórico e o cofre não é tocado.</li><li>`test_backup_consistente`: o backup existe, passa em `integrity_check` e tem as mesmas linhas do original.</li><li>`test_idempotente`: a segunda abertura não cria backup nem altera bytes.</li></ul> **Segundo grupo — falhas e recusas:** <ul><li>`test_falha_no_meio_reverte`: falha injetada após a primeira criação ⇒ `user_version` continua 0, nenhuma tabela nova, backup presente.</li><li>`test_versao_desconhecida_recusada` (`user_version` = 99) e `test_impressao_desconhecida_recusada` (v0 com tabela estranha): erro, e o SHA-256 do arquivo fica igual.</li></ul> |
| 2 | Dois fluxos (ADR-205) | `test_sessao.py`: <ul><li>`test_fluxo_etapa_completo`: criar, executar e encerrar.</li><li>`test_historico_lista_os_dois_fluxos` e `test_reabrir_etapa`: estado igual antes e depois de fechar o banco.</li><li>`test_metodos_recusam_outro_fluxo`: `propor_teste` numa etapa e `concluir` numa etapa são recusados.</li><li>`test_resumo_por_fluxo`.</li><li>`test_modo_calibracao_ainda_nao_disponivel` (V01) continua passando.</li></ul> |
| 3 | Irregularidade σ̂ (ADR-202) | <ul><li>Casos sem ruído (REF-001-A ×4, reflexões g ≤ 0,9, cancelamentos): σ̂ ≤ 0,05 dB.</li><li>Ruído σ ∈ {0,3; 0,5; 1,0; 1,5; 2,0}, isolado e combinado com vale ou cancelamento: \|σ̂ − σ\| ≤ 0,15σ + 0,05 dB.</li><li>Grade linear, < 24 pt/oit, suavização declarada ou desconhecida: `nao_estimavel`, nunca `aprovada`.</li></ul> |
| 4 | Admissibilidade SEG (ADR-204) | `test_seguranca.py::test_admissibilidade` com quatro situações: <ul><li>Risco crescente sem dado: bloqueada, sem receita, `aprovar` recusa.</li><li>Risco decrescente com `não verificável`: admitida com lista e aviso.</li><li>Não sensível: admitida com SEG-08/11.</li><li>Polaridade herdada: o bloco `seguranca` vem de `seg.avaliar`, não de constante.</li></ul> |
| 5 | Rastreabilidade (ADR-210, INV-211) | <ul><li>`test_reabrir_nao_recalcula`: grava a sessão, faz monkeypatch de `regras.avaliar` (lança se chamado) e dos limiares, reabre e compara o estado.</li><li>Todo cálculo novo tem `versao`, `limiares` e `entradas_sha256`; um hash conferido contra o arquivo do cofre.</li><li>`test_sessao_v01_legivel`: a sessão da fixture abre com "reconstruída pelas regras 1.0".</li></ul> |
| 6 | Integridade da aprovação (ADR-204) | Parametrização `test_aprovacao_integridade[*]`. **Recusas no serviço e no gatilho:** <ul><li>recomendação inexistente;</li><li>recomendação de outra sessão;</li><li>registro de outro tipo;</li><li>recomendação bloqueada ou não sensível;</li><li>escopo diferente da alteração;</li><li>aprovação duplicada;</li><li>nível ≠ B.</li></ul> **Verificações complementares:** <ul><li>a aprovação não altera `seguranca.regras[]`;</li><li>a rotina de integridade acusa uma aprovação inserida com `foreign_keys` desligado.</li></ul> |
| 7 | Detector de mudança (ADR-208) | <ul><li>Validação com 200 sementes por cenário: zero falsos positivos em "só polaridade" até σ = 1,5; N3 (+3 dB) detectado em 100 %.</li><li>Mudanças de ganho de ±1,5 dB e de corte detectadas sem ruído; filtros estreitos com taxas registradas.</li><li>Posição, ganho de entrada ou referência de nível diferentes ⇒ `verificação inconclusiva`.</li><li>Sem vias "depois" ⇒ aviso, e o REF-001-A continua `confirmada`.</li></ul> |
| 8 | Configuração e reversão (ADR-206) | <ul><li>`test_ultima_entre_sessoes`: a sessão 2 mostra a configuração final da sessão 1 com a origem.</li><li>Três desfechos.</li><li>Texto e dados sempre com `confirmacao_fisica: false`.</li><li>Registros do V01 com `garantida` lidos como "documentada".</li></ul> |
| 9 | Integridade estendida (FR-222) | `test_integridade.py`: uma inconsistência deliberada por verificação do data-model, inserida com SQL direto e gatilhos ou FK desligados no teste; cada uma aparece em `integridade()` com mensagem própria. `configuracao` recusa UPDATE e DELETE |
| 10 | Gerador coerente (ADR-201) | <ul><li>`test_coerencia_fisica`: a soma "sem aquisição" é igual à soma complexa das vias, com erro < 1e-9.</li><li>Nível e fase de cada arquivo derivam do mesmo H.</li><li>O ruído entra só na camada de aquisição.</li><li>REF-001-A byte a byte.</li></ul> |
| 11 | Critérios de aceitação | <ul><li>SC-203: quatro variantes e casos-limite (deficit ≤ 3 dB "antes", deficit negativo → 0, piora, redução de exatamente 50 % ⇒ `parcial`).</li><li>SC-204: 1 000 alterações com semente fixa.</li><li>SC-205: três desfechos.</li><li>SC-206: G3 no Windows.</li><li>SC-207: suíte completa sem alterar as asserções do V01.</li></ul> |
| 12 | Documentação | Datas de aprovação na data local (2026-10-15); "reversão documentada" em spec, plano e interface; QA confere por busca que não restou "reversão garantida" em texto exibido |

---

## Pontos para aprovação (nível B)

1. **Emenda E1 da spec**, com o complemento do agente (suavização declarada; ruído não estimável ⇒ veredito no máximo `inconclusiva`).
2. **Esta revisão R1 do plano** e do `data-model.md`: ADRs revistas, ADR-211 nova, matriz e critérios.
3. **Fixture do banco V01**: gerar a partir de `main@389e580` com `ferramentas/gerar_banco_v01.py` e versionar o binário em `tests/dados/banco-v01/`.
4. **Observação de cobertura**: nos percursos dos casos do V02 nenhuma recomendação é sensível (polaridade e atrasos não são). Bloqueio e aprovação de nível B ficam exercidos por testes de serviço com alterações sintéticas e pelo SC-204, não pelo roteiro do G3. → **Resolvido na E2** com os casos REF-003-S (FR-223, SC-209).

Decisões da E2 sobre esses pontos (2026-10-15): (1) ruído não estimável preserva o descritivo e limita o que depende da qualidade; (3) fixture gerada pelo V01 original, só sintética, permanente; (4) casos REF-003-S nos testes e no G3; casos de referência existentes inalterados (INV-213). Redação do complemento R1.1 aprovada em 2026-10-15 (nível B).

### Complemento R1.2 — emenda E3 (revisão adversarial, `docs/revisoes/revisao-adversarial-projeto.md`)

| Achado | Onde ficou | Critério de teste |
| --- | --- | --- |
| A01 | spec US-08, FR-223, SC-209; ADR-204 | S1 bloqueado por SEG-07 com equipamento confirmado; S2 por SEG-12 e SEG-07; S3 admitido com aprovação B; nenhum caminho admite reforço |
| A02 | spec, definição normativa e FR-205; ADR-212 | campos ausentes ⇒ incompatível; rótulo "declarada" em tela e dados |
| A03 | spec, precedência e FR-208; ADR-208 | "depois" em outra posição, ganho ou nível ⇒ "melhora observada", no máximo `inconclusiva` |
| A04 | ADR-212 (fundação) | grade estreita recusada; sobreposição < mínimo ⇒ fase "não calculável", sem `RankWarning` |
| A05 | spec SC-208 e limites; ADR-211 | oráculos analíticos e metamórficos; ruído correlacionado; relatório marca "domínio simulado" |
| A06 | ADR-212 (fundação); data-model, integridade | falha simulada entre a cópia e o INSERT reconcilia; órfão, linha sem arquivo e `.tmp` acusados |
| A07 | spec, detector e "repetição"; ADR-208; data-model | sem repetição ⇒ no máximo `inconclusiva`; reposicionamento simulado não compromete; N3 com duas aquisições independentes ⇒ `comprometida` sem nomear parâmetro; cópia (mesmo hash ou `aquisicao_id`) não é repetição |
| Proveniência (ajuste) | spec, definição e INV-214; ADR-201 | presunções só para catálogo com hashes conferidos; `simulado: true` externo ⇒ tratado como externo |
| A08 | spec, objetivo da etapa | texto exibido nunca diz "alinhado" nem "calibrado"; oráculo de quadratura: deficit 0 sem afirmar alinhamento |
| A09 | Constitution Check (I e VIII) corrigido | matriz conferida por script; duas avaliações separadas. **(i) G3 do bloco 3 do V02:** comparação de **esforço operacional** com dados sintéticos (tempo e passos de 2 ou 3 tarefas, Jarvis contra REW + planilha), registrada no QA como custo de fluxo. **(ii) VP-10 (utilidade real):** fica para incremento com medições reais. Nenhuma conclusão sobre vantagem na calibração do carro sai do V02 |

**Aprovado (nível B) em 2026-10-15:** redação da emenda E3 na spec e deste complemento R1.2 (ADR-212 nova; ADR-204, 208, 211 e Fase 0 ajustadas; matriz e data-model).

### Complemento R1.3 — emenda E4 (divergências do SC-208) — *decisões registradas; redação final aguarda conferência*

Origem: spec, Clarifications da Sessão 2026-10-16. Não muda arquitetura, ADRs nem limiares; muda o **critério de aceite** do SC-208 e a confirmação de mudança.

| Item | Onde fica | Critério de teste / evidência |
| --- | --- | --- |
| SC-208(a): viés e dispersão no lugar do critério por realização; sem limite de dispersão novo | spec SC-208(a); ADR-211 | `test_validacao_limiares.py` mantém a asserção de viés médio; `ferramentas/medir_e4.py` registra EAM, dp, percentis, proporção fora da tolerância original (22/1 400 preservados), falsas aprovações/reprovações perto de 0,5 e 1,5 dB |
| SC-208(b): desempenho observado, critério de aceitação e limitação não resolvida | spec SC-208(b); ADR-208 | taxas de indicativas, confirmadas e falsos negativos por σ, com N; **sem meta de taxa de falsos positivos**; detector **não validado** em σ = 1,5 dB |
| Confirmação exige faixa de frequência compatível | spec definição "Mudança indicativa e confirmada", FR-207, INV-215; ADR-208 | `test_calculos.py::test_repeticao_exige_faixa_compativel_calculo`, `test_sessao.py::test_repeticao_exige_faixa_compativel` (JV-T222A, implementada) |
| Texto "mudança suspeita; repetir a medição", sem afirmar alteração do DSP | FR-209; ADR-209 | `test_interface.py::test_mudanca_suspeita_sem_afirmar_dsp` (JV-T222B; passando) |
| Custo operacional (repetições pedidas) | spec SC-208(b); roteiro G3 | contagem registrada no G3 e no uso real; sem limiar |

**Limitação conhecida que a E4 declara:** em σ = 1,5 dB há falsos positivos confirmados (12/1 000; 10/1 000 com faixa compatível), porque as duas comparações "depois × antes" compartilham o mesmo "antes". Redesenho do detector (por exemplo, repetir também o "antes") fica fora do V02, para validação posterior; um limite admissível de falsos positivos exige justificativa e teste independentes.

**Limitação técnica da confirmação de faixa (registrada; algoritmo não redesenhado):** `calculos.repeticao_confirma` exige só **interseção não vazia** das faixas de mudança (uma "mudança geral" usa a faixa útil inteira e cruza com qualquer outra) e `Servico._verificacao_variavel_unica` avalia **apenas as duas primeiras detecções positivas** da via, na ordem de importação. Isso não demonstra que a diferença ocorreu na mesma região fisicamente relevante. Investigação posterior (junto com a independência do "antes").

**Linguagem (conferência final):** nenhum texto afirma alteração no DSP. "A medição não identifica a causa" substitui "o parâmetro alterado não é identificado pela medição"; uma alteração adicional só aparece como **declarada** pelo usuário, nunca como comprovada.

**Pontos para a conferência final (nível B):** (1) redação da E4 na spec; (2) este complemento R1.3; (3) as tasks JV-T222A/B, já implementadas aguardando commit; (4) `pytest` completo em Linux com as libs de Qt (2026-10-16): 211 passando e 1 `xfail`; falta a execução no Windows (G3).

### ADR-214 — Alteração candidata (JV-T228; JV-D047)
- **Decisão:** `Servico.avaliar_alteracao_candidata()` lê o manifesto do cofre (declaração conferida por `_problemas_de_declaracao`), chama `seguranca.classificar/avaliar/admissibilidade` sem alterá-las, registra o `calculo` `avaliacao_seguranca` com origem única na `declaracao` e a `recomendacao` derivada dele (bloqueada ⇒ sem receita). `registrar_aplicacao` e `estado()` ramificam por `tipo_intervencao`; o fluxo de polaridade fica intocado, e `propor_teste` recusa sessão com alteração candidata.
- **Motivo:** a avaliação usa dado declarado; sem previsão acústica, sem "depois" e sem veredito.
- **Consequências:** o parâmetro EQ ausente só entra com a premissa declarada `de = 0 dB`. A interface (JV-T230) continua pendente e deve dizer que a aprovação autoriza o ato e não verifica nada.
