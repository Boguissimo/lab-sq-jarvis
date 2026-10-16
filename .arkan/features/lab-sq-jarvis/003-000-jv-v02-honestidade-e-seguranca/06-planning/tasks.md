# Tasks — 003-000-jv-v02-honestidade-e-seguranca (JV-V02)

**Input**: [spec.md](../03-spec/spec.md) (E1–E3) | [plan.md](../04-architecture/plan.md) (R1–R1.2) | [data-model.md](../04-architecture/data-model.md) | [quickstart.md](../04-architecture/quickstart.md)
**Status**: aprovado pelo desenvolvedor em 2026-10-15 (Princípio VIII).

> Formato: `JV-T2NN [P?] [US?] — descrição`. Gate de cada task: G1 = teste automatizado; G2 = revisão técnica; G3 = desenvolvedor no Windows.
> `[P]` = pode rodar em paralelo com outras `[P]` da mesma fase (arquivos diferentes, sem estado compartilhado).
> Regra transversal: toda task termina com `python -m pytest` verde, incluindo os 45 testes do V01 **sem alterar asserções** (INV-210). Os testes fazem parte das tasks porque a spec e a matriz de rastreabilidade os exigem.
> Paths inferidos da `## Estrutura do Projeto` do plano (não há indexador de código configurado).

---

## Fase 0 — Fundação (bloqueia o resto)

**⚠️ CRÍTICO**: nenhuma recomendação nova e nenhuma mudança em `regras.py` antes do fim desta fase.

### 0a. Correções do V01 (ADR-212)

- [x] JV-T201 [P] — Limiares do V02 centralizados: `{valor, unidade, provisorio, origem}`, incluindo as amostras mínimas da ADR-212 (ADR-211). Gate: G1. Evidência: `tests/test_limiares.py` (todo limiar tem origem e rótulo provisório).
  - File: `src/jarvis/limiares.py`
- [x] JV-T202 — A04: portão básico obrigatório em `Servico.analisar`; amostras mínimas em `diferenca_fase` e `sobreposicao` (fase e atraso "não calculáveis", sem `RankWarning`) (depende de T201). Gate: G1. Evidência: `test_sessao.py::test_qualidade_basica_reprovada_bloqueia`, `test_calculos.py::test_sobreposicao_insuficiente`.
  - File: `src/jarvis/calculos.py`, `src/jarvis/sessao.py`
- [x] JV-T203 [P] — A02: `referencia_temporal` 1.1 exige `tipo` ≠ `nenhuma`, `id`, `taxa_amostragem`, `posicao_microfone`; devolve `{compativel, declarada: true, motivos}` (FR-205). Gate: G1. Evidência: `test_calculos.py::test_referencia_campos_ausentes`.
  - File: `src/jarvis/calculos.py`
- [x] JV-T204 [P] — A06: cofre atômico (`.tmp/<uuid>`, hash, `os.replace`, `INSERT OR IGNORE` sempre) e varredura física em `integridade()`. Gate: G1. Evidência: `test_persistencia.py::test_falha_entre_copia_e_insert_reconcilia`, `::test_orfao_no_cofre_detectado`, `::test_tmp_residual_detectado`.
  - File: `src/jarvis/persistencia.py`

> T202 e T203 tocam `calculos.py` em funções diferentes; se feitas em paralelo, integrar com cuidado (ou fazer em sequência).

### 0b. Migração (ADR-207)

- [x] JV-T205 [P] — Gerador da fixture: roda o percurso do REF-001-A num checkout de `main@389e580` e grava banco + cofre + README de geração; fixture só sintética, versionada, permanente. Gate: G1/G2. Evidência: `tests/dados/banco-v01/` commitado; teste confere que os originais do cofre são os arquivos do REF-001-A.
  - File: `ferramentas/gerar_banco_v01.py`, `tests/dados/banco-v01/`
- [x] JV-T206 — `migracao.py`: impressão digital do esquema, `detectar()`, backup por `Connection.backup` + `integrity_check` + contagem, migração 0 → 2 transacional sem `executescript` (depende de T204). Gate: G1. Evidência: parte de `tests/test_migracao.py`.
  - File: `src/jarvis/migracao.py`
- [x] JV-T207 — `Banco.__init__` reorganizado (nada antes da detecção; abertura `mode=ro`); esquema 2 com `aprovacao`, gatilho `BEFORE INSERT` e gatilhos de só inserção em `configuracao`; `ErroVersaoBanco` (depende de T205, T206). Gate: G1. Evidência: `test_migracao.py` completo (critério 1 do plano: 4 casos normais + 3 recusas/falhas).
  - File: `src/jarvis/persistencia.py`, `tests/test_migracao.py`

### 0c. Interpretação congelada (ADR-210, INV-211)

- [x] JV-T208 [P] — `regras_v1_0.py`: cópia congelada das regras 1.0, só para leitura de sessões legadas. Gate: G1. Evidência: teste de equivalência com `regras.py` atual antes de qualquer mudança.
  - File: `src/jarvis/regras_v1_0.py`
- [x] JV-T209 — `entradas_sha256` em todo cálculo; cálculo `avaliacao_regras` gravado (versão, snapshot de limiares, portão, sugestão, ordem); `estado()` lê do registro e usa `regras_v1_0` para sessões V01 ("reconstruída pelas regras 1.0") (depende de T207, T208). Gate: G1. Evidência: `test_sessao.py::test_reabrir_nao_recalcula`, `test_persistencia.py::test_sessao_v01_legivel`.
  - File: `src/jarvis/sessao.py`, `src/jarvis/persistencia.py`

### 0d. Modelo físico e catálogo (ADR-201)

- [x] JV-T210 [P] — `modelo.py`: H(f) por via (alto-falante, LR4/PEQ, polaridade, atraso, reflexão) e camada de aquisição separada (ruído, posição, ganho, quantização). Gate: G1. Evidência: `test_casos.py::test_coerencia_fisica` (soma sem aquisição = soma complexa, erro < 1e-9).
  - File: `src/jarvis/referencia/modelo.py`
- [x] JV-T211 — `casos.py`: catálogo (REF-001-B, N1–N5, REF-002-A ×4, REF-003-S1–S3, variantes de teste) com hashes esperados para proveniência; geração dos dados (depende de T210). Gate: G1. Evidência: `test_casos.py::test_deterministico`, `::test_ruido_registrado`, `::test_ref001a_intacto`, `::test_proveniencia_catalogo`.
  - File: `src/jarvis/referencia/casos.py`, `src/jarvis/referencia/dados/`

### 0e. Contratos de qualidade e segurança (ADR-202, 204, 211)

- [x] JV-T212 [P] — `calculos.irregularidade`: condições de aplicação e σ̂ = 1,4826·MAD(Δ²L)/√6; `nao_estimavel` preserva o descritivo (FR-202, INV-212) (depende de T201). Gate: G1. Evidência: `test_calculos.py::test_irregularidade_ruido_conhecido`, `::test_irregularidade_nao_confunde_vale`, `::test_condicoes_aplicacao`, `::test_nao_estimavel_nao_aprova` (critério 3). `test_nao_estimavel_preserva_descritivo` fica na JV-T216, onde o portão usa σ̂.
  - File: `src/jarvis/calculos.py`
- [x] JV-T213 [P] — Contratos de `seguranca.py`: `classificar`, `avaliar`, `admissibilidade` (estrutura, classe de risco, estados), `VERSAO = "0.4.0"`; regras ainda como esqueleto testável (depende de T201). Gate: G1. Evidência: `test_seguranca.py::test_classificacao`, `::test_admissibilidade` (quatro situações do critério 4).
  - File: `src/jarvis/seguranca.py`

**Checkpoint**: banco migra com segurança, interpretação congelada, casos gerados com proveniência, contratos de qualidade e segurança testados — blocos podem começar.

---

## Fase 1 — Bloco 1: casos e honestidade (US-01 a US-04, P1)

**Goal**: N1–N5 e REF-001-B percorridos com conclusões honestas.
**Independent Test**: `test_sessao.py::test_n1` a `::test_n5`, `::test_ref001b` (SC-201, SC-202).

- [x] JV-T214 [P] [US-02] — `vales_individuais` e `faixa_util` (FR-204). Gate: G1. Evidência: testes em `test_calculos.py`.
  - File: `src/jarvis/calculos.py`
- [x] JV-T215 [US-03] — `condicoes_comparaveis` (declarada) e `detector_mudanca_via` com três resultados (FR-207) (depende de T214). Gate: G1. Evidência: `test_calculos.py::test_detector_mudanca` (critério 7). **Divergência aberta (2026-10-15):** com a regra da spec, "só polaridade" dá ~8,7 % de falsos positivos a σ = 1,5 dB (1 000 sementes), contra "zero" no SC-208(b); teste marcado `xfail` estrito até decisão `JV-D`.
  - File: `src/jarvis/calculos.py`
- [x] JV-T216 [US-01] [US-02] — `regras` 1.1: I-3, reordenação, portão de qualidade (`reprovada`/`nao_estimavel`) (FR-203, FR-204) (depende de T209, T212, T214). Gate: G1. Evidência: `test_regras.py::test_i3_reordena_hipoteses`, `test_sessao.py::test_n1`, `::test_n2`, `::test_qualidade_limita_conclusao`.
  - File: `src/jarvis/regras.py`, `src/jarvis/sessao.py`
- [x] JV-T217 [US-01] — N4 (fase recusada sem referência declarada) e N5 (nada a alterar) no serviço (FR-205, FR-206) (depende de T203, T216). Gate: G1. Evidência: `test_sessao.py::test_n4`, `::test_n5`.
  - File: `src/jarvis/sessao.py`
- [x] JV-T218 [US-03] — `_medicoes()` e `importar_depois` com várias medições por via; recusa de cópia (hash/`aquisicao_id`); presunções só com proveniência verificada (INV-214) (depende de T211). Gate: G1. Evidência: `test_sessao.py::test_copia_nao_e_repeticao`, `::test_simulado_declarado_nao_presume`.
  - File: `src/jarvis/sessao.py`
- [x] JV-T219 [US-03] — `comprometida` com precedência E1 e repetição por aquisições independentes; `verificacao_variavel_unica` gravada (FR-207) (depende de T215, T218). Gate: G1. Evidência: `test_sessao.py::test_n3`, `::test_n3_so_declarada`, `::test_n3_so_medida`, `::test_n3_posicao_diferente_inconclusiva`, `::test_n3_sem_repeticao_inconclusiva`, `::test_reposicionamento_nao_compromete`, `::test_mudanca_reproduzida_nao_nomeia_parametro`, `::test_sem_dados_nao_e_sem_mudanca`, `::test_comprometida_nao_refuta`.
  - File: `src/jarvis/sessao.py`
- [x] JV-T220 [US-04] — REF-001-B: incerteza de σ̂ no veredito, aquisição comparável exigida para `confirmada` (FR-208) (depende de T219). Gate: G1. Evidência: `test_sessao.py::test_ref001b`, `::test_nao_estimavel_limita_veredito`, `::test_depois_outra_posicao_nao_confirma`.
  - File: `src/jarvis/sessao.py`
- [ ] JV-T221 [P] — Varredura SC-208 (a, b): σ̂ e detector; oráculos analíticos e testes metamórficos; relatório marcado "domínio simulado" (depende de T212, T215). Gate: G1/G2. Evidência: `tests/test_validacao_limiares.py`, `tests/test_oraculos.py`, `tests/test_metamorficos.py` → `08-qa/validacao-limiares.md` (parcial).
  - File: `tests/test_validacao_limiares.py`, `tests/test_oraculos.py`, `tests/test_metamorficos.py`
- [ ] JV-T222 [US-01..04] — Interface: seletor de caso, resultados novos (qualidade, detector com resolução, "ruído não estimável", "declarada compatível"), modo da sessão no Histórico (FR-209) (depende de T217, T220). Gate: G1. Evidência: `test_interface.py::test_seletor_casos`, `::test_textos_resultados`.
  - File: `src/jarvis/interface/janela.py`
- [ ] JV-T223 — **G3 do bloco 1**: roteiro no Windows, incluindo abrir o banco real (migração com backup) e reabrir as sessões (SC-206). Gate: G2 (roteiro) e G3. Evidência: seção do bloco 1 em `COMO-EXPERIMENTAR.md` e registro do desenvolvedor.
  - File: `COMO-EXPERIMENTAR.md`

**Checkpoint**: bloco 1 aprovado no Windows — bloco 2 pode começar (bloco 3 também, ver dependências).

---

## Fase 2 — Bloco 2: segurança (US-05, US-08, P2)

**Goal**: toda recomendação passa por SEG e admissibilidade; bloqueio e aprovação B exercitados.
**Independent Test**: `test_seguranca.py` completo, `test_sessao.py::test_s1_s2_s3` (SC-204, SC-209).

- [ ] JV-T224 [US-05] — Regras SEG-01/03/04/05/06/08/10/11/12/13 com casos permitido/limítrofe/proibido; SEG-02/07/09 sempre `não verificável` (FR-210 a FR-213) (depende de T213). Gate: G1. Evidência: `test_seguranca.py::test_seg01` … `::test_seg13`, `::test_seg02_07_09_nao_verificaveis`, `::test_seg12_planejado_nao_confirma`, `::test_provisorios_rotulados`.
  - File: `src/jarvis/seguranca.py`
- [ ] JV-T225 [US-05] — Teste de propriedade: 1 000 alterações, semente fixa, nenhuma bloqueada vira admissível (SC-204, INV-203) (depende de T224). Gate: G1. Evidência: `test_seguranca.py::test_propriedade_sem_violacao`.
  - File: `tests/test_seguranca.py`
- [ ] JV-T226 [US-05] — Integração: `propor_teste` passa por `seg.avaliar`/`admissibilidade` (sem bloco fixo); alteração bloqueada registrada sem receita; `registrar_aplicacao` recusa (FR-211) (depende de T224, T219). Gate: G1. Evidência: `test_sessao.py::test_polaridade_passa_por_seguranca`.
  - File: `src/jarvis/sessao.py`
- [ ] JV-T227 [US-05] — Aprovação de nível B: `Banco.nova_aprovacao`, `Servico.aprovar` com escopo, gatilho e integridade (FR-216) (depende de T207, T226). Gate: G1. Evidência: `test_seguranca.py::test_aprovacao_nao_verifica`, `test_persistencia.py::test_aprovacao_integridade[*]` (critério 6).
  - File: `src/jarvis/persistencia.py`, `src/jarvis/sessao.py`
- [ ] JV-T228 [US-08] — `avaliar_alteracao_candidata()` e percursos REF-003-S1 (bloqueado por SEG-07), S2 (SEG-12 e SEG-07), S3 (admitido, aprovação B) (FR-223) (depende de T211, T227). Gate: G1. Evidência: `test_sessao.py::test_s1_s2_s3`.
  - File: `src/jarvis/sessao.py`
- [ ] JV-T229 [P] — Varredura SC-208 (c): limites SEG (depende de T224). Gate: G1. Evidência: `test_validacao_limiares.py` ampliado.
  - File: `tests/test_validacao_limiares.py`
- [ ] JV-T230 [US-05] [US-08] — `seguranca_view.py`: "Verificação de segurança" em toda recomendação, provisórios visíveis, "Alteração bloqueada — não recomendada" sem aplicar, telas de aprovação (FR-214, FR-215) (depende de T228). Gate: G1. Evidência: `test_interface.py::test_provisorio_visivel`, `::test_verificacao_em_toda_recomendacao`, `::test_bloqueada_sem_aplicar`, `::test_casos_seguranca`.
  - File: `src/jarvis/interface/seguranca_view.py`, `src/jarvis/interface/janela.py`
- [ ] JV-T231 — **G3 do bloco 2**: S1, S2 e S3 no Windows (SC-206, SC-209). Gate: G2 e G3. Evidência: seção do bloco 2 em `COMO-EXPERIMENTAR.md` e registro do desenvolvedor.
  - File: `COMO-EXPERIMENTAR.md`

**Checkpoint**: segurança aprovada no Windows.

---

## Fase 3 — Bloco 3: calibração, configuração e fluxo completo (US-06, US-07, P2)

**Goal**: etapa simulada tipo ATM e reversão documentada.
**Independent Test**: `test_calibracao.py`, `test_configuracao.py` (SC-203, SC-205).

- [ ] JV-T232 [P] [US-06] — `calc.deficit_cruzamento` e `calibracao.resultado` com precedência e casos-limite; texto sem "alinhado"/"calibrado" (FR-217, FR-218, INV-206). Gate: G1. Evidência: `test_calibracao.py::test_variantes[*]`, `::test_casos_limite`, `::test_objetivo_ja_atendido`, `::test_nao_verificado_lista_origem`, `::test_sem_atribuicao_causal`.
  - File: `src/jarvis/calibracao.py`, `src/jarvis/calculos.py`
- [ ] JV-T233 [US-06] — Fluxo `etapa-simulada` no serviço: `propor_etapa`, `importar_depois_etapa`, `concluir_etapa`, recusas cruzadas, `estado()`/`resumo()` por fluxo (ADR-205) (depende de T232, T226). Gate: G1. Evidência: critério 2 do plano (`test_fluxo_etapa_completo`, `test_metodos_recusam_outro_fluxo`, `test_resumo_por_fluxo`, `test_modo_calibracao_ainda_nao_disponivel`).
  - File: `src/jarvis/sessao.py`
- [ ] JV-T234 [P] [US-07] — `configuracao.py`: `nome_sugerido` e `reversao` (arquivo/receita/nenhum, `confirmacao_fisica: false`) (FR-219, FR-221, INV-205). Gate: G1. Evidência: `test_configuracao.py::test_nome_sugerido`, `::test_reversao_tres_desfechos`, `::test_reversao_nao_documentada`, `::test_documentada_nao_e_fisica`, `::test_chave_garantida_v01_legivel`.
  - File: `src/jarvis/configuracao.py`
- [ ] JV-T235 [US-07] — Serviço e banco: `arquivar_ajuste` (opaco no cofre), `Banco.ultima_configuracao` entre sessões, `confirmar_configuracao_inicial`, `decidir("reverter")` com reversão documentada (FR-219 a FR-221) (depende de T234, T207). Gate: G1. Evidência: `test_configuracao.py::test_arquivo_opaco`, `::test_ultima_entre_sessoes`.
  - File: `src/jarvis/sessao.py`, `src/jarvis/persistencia.py`
- [ ] JV-T236 [US-07] — `configuracao_view.py` e a etapa no passo 4 (depende de T233, T235). Gate: G1. Evidência: `test_interface.py::test_confirmacao_inicial` e teste da etapa na interface.
  - File: `src/jarvis/interface/configuracao_view.py`, `src/jarvis/interface/janela.py`
- [ ] JV-T237 — Integridade estendida: uma inconsistência deliberada por verificação do data-model (FR-222) (depende de T227, T235). Gate: G1. Evidência: `tests/test_integridade.py::test_inconsistencia[*]` (critério 9).
  - File: `src/jarvis/persistencia.py`, `tests/test_integridade.py`
- [ ] JV-T238 — Fluxo completo dos dois tipos de sessão: criar, executar, encerrar, Histórico, reabrir sem recálculo (depende de T233, T236). Gate: G1. Evidência: `test_sessao.py::test_historico_lista_os_dois_fluxos`, `::test_reabrir_etapa`.
  - File: `tests/test_sessao.py`
- [ ] JV-T239 — **G3 do bloco 3**: quatro variantes REF-002-A, configuração e reversão; comparação de **esforço operacional** com dados sintéticos (2 ou 3 tarefas, Jarvis × REW + planilha), sem conclusão sobre utilidade real (A09; VP-10 fica fora). Gate: G2 e G3. Evidência: seção do bloco 3 em `COMO-EXPERIMENTAR.md`, registro de tempo e passos.
  - File: `COMO-EXPERIMENTAR.md`

**Checkpoint**: os três blocos aprovados no Windows.

---

## Fase N — Polish e QA

- [ ] JV-T240 [P] — Capturas de tela do V02. Gate: G2. Evidência: `docs/capturas/`.
  - File: `ferramentas/capturas.py`
- [ ] JV-T241 [P] — `08-qa/validacao-limiares.md` consolidado (a, b, c), domínio simulado declarado; nenhum limiar ajustado sem `JV-D`. Gate: G2. Evidência: o relatório.
  - File: `.arkan/features/lab-sq-jarvis/003-000-jv-v02-honestidade-e-seguranca/08-qa/validacao-limiares.md`
- [ ] JV-T242 — QA do incremento: suíte completa em Linux (SC-207); busca por escrita ao DSP (INV-207), por "reversão garantida", "alinhado", "calibrado" em texto exibido; `git diff` do Core (INV-209); registro de entregas no feature map (JV-D041); `status.md`. Gate: G1/G2. Evidência: `08-qa/qa-report.md`.
  - File: `.arkan/features/lab-sq-jarvis/003-000-jv-v02-honestidade-e-seguranca/08-qa/qa-report.md`

---

## Dependências e Ordem de Execução

| Fase | Bloqueia | Por quê |
| --- | --- | --- |
| 0 | 1, 2, 3 | migração, interpretação congelada, catálogo e contratos são usados por todos |
| 1 | 2 (parcial) | T226 depende de T219 (`sessao.py` com repetição e precedência) |
| 2 | 3 (parcial) | T233 depende de T226 (admissibilidade no serviço); T237 depende de T227 |
| 1, 2, 3 | N | QA depende dos três G3 |

**Caminho crítico**: T201 → T204 → T206 → T207 → T209 → T216 → T217/T219 → T220 → T222 → T223 → T226 → T227 → T228 → T230 → T231 → T233 → T236 → T238 → T239 → T242.

**Paralelismo real**:
- Fase 0: T203, T204, T205, T208, T210 começam juntas; T212 e T213 logo após T201.
- Fase 1: T214 e T221 em paralelo com o trabalho em `sessao.py`.
- Fase 3: T232 e T234 em paralelo (arquivos distintos).
- Fase N: T240 e T241.

**Riscos e mitigação** (Risk Analyzer):
1. **`sessao.py` é gargalo** (12 tasks tocam o arquivo) → tasks em sequência estrita nesse arquivo; nunca duas `[P]` nele.
2. **T207 (migração) toca o banco real do desenvolvedor** → fixture do V01 real e os sete testes do critério 1 antes do G3; o G3 do bloco 1 só depois de o backup ser conferido.
3. **T209 antes de T216** → se `regras.py` mudar antes da interpretação congelada, a interpretação histórica muda; T208 congela a cópia antes de qualquer edição.
4. **T205 depende de um checkout de `389e580`** → usar `git worktree` temporário; a fixture é gerada uma vez e nunca regenerada sem `JV-D`.
5. **Limiares ajustados para passar casos** → T221/T229/T241 só registram falsos positivos e negativos; mudança exige `JV-D` (P8).
6. **Tasks grandes**: T219 e T224 podem passar de 2 h → se passarem, dividir T219 em (precedência) + (repetição), e T224 em (SEG-01 a 06) + (SEG-08 a 13).

## Estratégia de Implementação

**MVP (P1 — bloco 1)**: Fase 0 + Fase 1, validado no G3 do bloco 1 (T223), com o banco real migrado. Os blocos 2 e 3 não alteram o que o bloco 1 entrega.

**Entrega incremental**: Fundação → bloco 1 (G3) → bloco 2 (G3) → bloco 3 (G3) → QA. Cada bloco termina com a suíte inteira verde (V01 + blocos anteriores); commit por task concluída, push só com autorização.
