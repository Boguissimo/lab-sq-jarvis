# Tasks — 003-000-jv-v02-honestidade-e-seguranca (JV-V02)

**Input**: [spec.md](../03-spec/spec.md) (E1–E3) | [plan.md](../04-architecture/plan.md) (R1–R1.2) | [data-model.md](../04-architecture/data-model.md) | [quickstart.md](../04-architecture/quickstart.md)
**Status**: aprovado pelo desenvolvedor em 2026-10-15 (Princípio VIII). **JV-T222A e JV-T222B** (emenda E4): implementação aprovada pelo desenvolvedor em 2026-10-16; commit aguarda a conferência da redação final. JV-T223 (G3 do bloco 1) vem depois delas.

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
- [x] JV-T221 [P] — Varredura SC-208 (a, b): σ̂ e detector; oráculos analíticos e testes metamórficos; relatório marcado "domínio simulado" (depende de T212, T215). Gate: G1/G2. Evidência: `tests/test_validacao_limiares.py`, `tests/test_oraculos.py`, `tests/test_metamorficos.py` → `08-qa/validacao-limiares.md` (parcial).
  - File: `tests/test_validacao_limiares.py`, `tests/test_oraculos.py`, `tests/test_metamorficos.py`
- [x] JV-T222 [US-01..04] — Interface: seletor de caso, resultados novos (qualidade, detector com resolução, "ruído não estimável", "declarada compatível"), modo da sessão no Histórico (FR-209) (depende de T217, T220). Gate: G1. Evidência: `test_interface.py::test_seletor_casos`, `::test_textos_resultados`.
  - File: `src/jarvis/interface/janela.py`
- [x] JV-T222A [US-03] — **(E4)** Confirmação de mudança exige faixa de frequência compatível entre as duas aquisições (`calculos.repeticao_confirma`; `faixa_compativel` em `detector_mudanca`); cópia, reimportação ou nova análise dos mesmos dados nunca confirmam (depende de T219). Gate: G1. Evidência: `test_calculos.py::test_repeticao_exige_faixa_compativel_calculo`, `test_sessao.py::test_repeticao_exige_faixa_compativel`, `::test_copia_nao_e_repeticao` (INV-215). Sem mudar limiares. Limitação registrada: só interseção não vazia de faixas e só as duas primeiras detecções positivas por via; algoritmo não redesenhado.

- [x] JV-T222B [US-03] — **(E4)** Texto da indicativa "mudança suspeita; repetir a medição", sem afirmar alteração do DSP (`janela.py`, `sessao.py`, FR-209); framing de `tests/test_validacao_limiares.py` atualizado sem alterar números nem tabelas; ensaio complementar em `ferramentas/medir_e4.py` (depende de T222A). Gate: G1. Evidência: `test_interface.py::test_mudanca_suspeita_sem_afirmar_dsp` (passando; suíte completa em 2026-10-16: 211 passando e 1 `xfail`, com interface, em Linux com as libs), `08-qa/validacao-limiares.md` e `-e4.md`.

- [x] JV-T223 — **G3 do bloco 1** — **CONCLUÍDA por aprovação humana expressa de Fabrício em 2026-10-17** (alcance: funcionamento operacional do Bloco 1, histórico, persistência e compatibilidade observada com o V01; **não** é validação acústica com medições reais, nem aprovação dos algoritmos experimentais, nem conclusão dos Blocos 2 e 3; ressalvas de apresentação e a conferência só visual do backup em `08-qa/g3-bloco1-parcial.md`). Texto original e andamento preservados a seguir como histórico: roteiro no Windows, incluindo abrir o banco real (migração com backup) e reabrir as sessões (SC-206). Gate: G2 (roteiro) e G3. Evidência: seção do bloco 1 em `COMO-EXPERIMENTAR.md` e registro do desenvolvedor. **PARCIAL (16/10/2026, não concluída):** suíte Windows 211 + 1 `xfail`, abertura, sessão V01 reaberta e N3 até a análise OK; faltam backup/marcação da migração, N3 até o veredito, demais casos e reabertura. Registro em `08-qa/g3-bloco1-parcial.md`. **Atualização 17/10/2026 — continua PARCIAL, não marcada `[x]`:** evidências **do Codex no Windows** (execução do agente; commit `7c3104a`, que corrige a identificação de pasta no Windows e a marcação "reconstruída pelas regras 1.0") cobrem backup V01 e base íntegros, marcação confirmada na instalação operacional, A, B, N1, N2, N4 e N5 pela interface, B e N3 até o veredito e reabertura do N3 (cópia isolada); **evidência automatizada:** suíte 243 + 1 `xfail` (Windows, relatada; Linux, reproduzida). **Não houve aceite humano inequívoco do G3 completo:** falta Fabrício executar ou presenciar o roteiro e declarar o aceite. Distinção das três classes de evidência em `08-qa/g3-bloco1-parcial.md`.
  - File: `COMO-EXPERIMENTAR.md`

**Checkpoint**: bloco 1 aprovado no Windows — bloco 2 pode começar (bloco 3 também, ver dependências).

---

## Fase 2 — Bloco 2: segurança (US-05, US-08, P2)

**Goal**: toda recomendação passa por SEG e admissibilidade; bloqueio e aprovação B exercitados.
**Independent Test**: `test_seguranca.py` completo, `test_sessao.py::test_s1_s2_s3` (SC-204, SC-209).

- [x] JV-T224 [US-05] **CONCLUÍDA (2026-10-17, Nível B autorizado por Fabrício; commit na branch de trabalho).** Só `seguranca.py` e `test_seguranca.py`; limites da v0.4.0 inalterados (SEG-04 e SEG-05 rotulados provisórios); dado ausente, não confirmado ou ilegível ⇒ `não verificável`, nunca aprovação presumida; SEG-02/07/09 sempre `não verificável` para alteração sensível (risco crescente fica bloqueado). Dados novos da alteração (opcionais): `potencia_estimada_w`, `reforcos_na_banda_db`, `vale_classificacao`, `etapa_automatizada`/`limites_informados`/`valores_conferencia`. `classificar` passou a tratar valor não numérico como desconhecido (risco crescente). Descrição original: — Regras SEG-01/03/04/05/06/08/10/11/12/13 com casos permitido/limítrofe/proibido; SEG-02/07/09 sempre `não verificável` (FR-210 a FR-213) (depende de T213). Gate: G1. Evidência: `test_seguranca.py::test_seg01` … `::test_seg13`, `::test_seg02_07_09_nao_verificaveis`, `::test_seg12_planejado_nao_confirma`, `::test_provisorios_rotulados`.
  - File: `src/jarvis/seguranca.py`
- [x] JV-T225 [US-05] **CONCLUÍDA (2026-10-17, Nível B autorizado por Fabrício; commit na branch de trabalho).** Propriedade com 1 000 alterações e semente fixa, que complementa os testes determinísticos de limite e combinação (T224). Descrição original: — Teste de propriedade: 1 000 alterações, semente fixa, nenhuma bloqueada vira admissível (SC-204, INV-203) (depende de T224). Gate: G1. Evidência: `test_seguranca.py::test_propriedade_sem_violacao`.
  - File: `tests/test_seguranca.py`
- [x] JV-T226 [US-05] — **CONCLUÍDA (2026-10-17, Nível B autorizado por Fabrício).** `propor_teste` grava o bloco `seguranca` vindo de `seg.classificar`/`avaliar`/`admissibilidade` (13 regras, `admissibilidade`, `versao_regras_seg`, `limitacoes`; resultados e motivos preservados); alteração bloqueada vira "Alteração bloqueada — não recomendada", sem receita; `registrar_aplicacao` recusa. Nenhum dado de equipamento inventado (polaridade não sensível; `avaliar(…, None)`). Registro anterior sem `admissibilidade` não é reavaliado (INV-211): vale a classe que ele guardou, e só `não sensível` segue aplicável; qualquer outra, ou sem `seguranca`, é recusada. Interface inalterada (T230). Suíte 296 + 1 xfail; 4 testes novos falham sem a mudança. Descrição original: — Integração: `propor_teste` passa por `seg.avaliar`/`admissibilidade` (sem bloco fixo); alteração bloqueada registrada sem receita; `registrar_aplicacao` recusa (FR-211) (depende de T224, T219). Gate: G1. Evidência: `test_sessao.py::test_polaridade_passa_por_seguranca`.
  - File: `src/jarvis/sessao.py`
- [x] JV-T227 [US-05] — **CONCLUÍDA (2026-10-17, Nível B autorizado por Fabrício; escolhas 1–3 aprovadas).** `Banco.nova_aprovacao`/`aprovacoes`/`aprovacao_de`; `Servico.aprovar(recomendacao, escopo)` (só por pedido expresso; recusa inexistente, outra sessão, outro tipo, bloqueada, não sensível, registro sem admissibilidade, escopo diferente ou incompleto, duplicada); `registrar_aplicacao` exige aprovação de escopo igual para recomendação sensível (registro histórico sem `admissibilidade` não é reavaliado, INV-211); `integridade()` confere as aprovações (item 1 do data-model; `momento >= criado_em`). O restante da integridade estendida fica na T237. A aprovação não altera `seguranca.regras` nem libera bloqueada. Esquema, regras SEG e interface inalterados. Testes com recomendação sensível admissível real pelas regras atuais (corte de EQ, risco decrescente) montada pela fábrica `cria_recomendacao` (o produto só a gera na T228). Suíte 322 + 1 xfail; 26 testes novos falham sem a mudança. Descrição original: — Aprovação de nível B: `Banco.nova_aprovacao`, `Servico.aprovar` com escopo, gatilho e integridade (FR-216) (depende de T207, T226). Gate: G1. Evidência: `test_seguranca.py::test_aprovacao_nao_verifica`, `test_persistencia.py::test_aprovacao_integridade[*]` (critério 6).
  - File: `src/jarvis/persistencia.py`, `src/jarvis/sessao.py`
- [ ] JV-T228 [US-08] — `avaliar_alteracao_candidata()` e percursos REF-003-S1 (bloqueado por SEG-07), S2 (SEG-12 e SEG-07), S3 (admitido, aprovação B) (FR-223) (depende de T211, T227). Gate: G1. Evidência: `test_sessao.py::test_s1_s2_s3`.
  - File: `src/jarvis/sessao.py`
- [x] JV-T229 [P] — **CONCLUÍDA (2026-10-17, Nível B autorizado por Fabrício).** Seis testes novos `test_c_*` em `tests/test_validacao_limiares.py` varrem, com `classificar`/`avaliar`/`admissibilidade` reais, SEG-01 (80 Hz e 12 dB/oit fictícios, passo até 0,001), SEG-03 (50 W, passo até 0,0005), SEG-04 (+1,5 dB), SEG-05 (+3 por filtro, +6 na banda, grade 10 × 17), SEG-06, SEG-13 e equipamento não confirmado: zero falsos aprovados e zero falsos bloqueados por regra nas fronteiras; dado ausente, inválido ou não confirmado nunca aprova. Registrado, sem alterar limite: reforço de EQ dentro de todos os limites segue bloqueado por SEG-02/07/09 sem método (por desenho, FR-212); SEG-01 bloqueia destino abaixo do mínimo mesmo ao subir a frequência; tolerância absoluta de 1e-9. Só acrescentou testes; `validacao-limiares.md` não foi regravado (seções a/b intactas). Suíte 328 + 1 xfail. Descrição original: — Varredura SC-208 (c): limites SEG (depende de T224). Gate: G1. Evidência: `test_validacao_limiares.py` ampliado.
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

---

## Fase 5 — Candidato interno 1.0 (referência de planejamento de 2026-10-16)

**Objetivo (Fabrício):** amadurecer progressivamente um produto sólido e utilizável por ele, antes de qualquer participação externa; não é versão comercial nem beta; **sem prazo artificial** e sem comprometer capacidades futuras. A investigação acústica está **preservada**; sua suspensão é prioridade operacional temporária. **O escopo mínimo abaixo é referência, não decisão sobre o Jarvis 1.0. Os blocos 2 e 3 do V02 permanecem no planejamento original (T224–T242), sem rebaixamento. F-5 (papel do σ̂ e do portão) segue em aberto. Só T250 e T251 foram autorizados; T253–T259 não iniciam sem nova ordem.** Prioridades: **P0** impede uso confiável · **P1** prejudica a apresentação · **P2** pode esperar. **Esclarecimento:** os rótulos P0/P1/P2 desta fase são de planejamento da Fase 5 e **não alteram** as prioridades de user story (P1/P2) nem o escopo anteriormente aprovados da V02; as Fases 2 e 3 (blocos 2 e 3, T224–T242) continuam como aprovadas.

- [x] JV-T250 [P0] — Integrar à branch do V02 a correção pontual (leitor do REW com milhar; mensagem de recusa por causa; borda de 24 ppo) e a Clarification C-1 do FR-002. **Nível B (autorizado em 2026-10-16).** Evidência: merge `7dfa2b2` (sem `main`); `src/` muda só em `rew_texto.py`, `sessao.py` (conselho do portão) e 1 linha de `calculos.py` (arredondamento de `ppo`, limiar 24 inalterado); 25/25 arquivos REW reais lidos idênticos ao leitor independente e aprovados no portão básico (antes: recusa).
- [x] JV-T251 [P0] — Entrada de arquivos sem exceção solta (FR-002, FR-004): `Servico._ler_manifesto` valida o manifesto e devolve mensagens em português; erros do sistema traduzidos (`rew_texto.motivo_do_sistema`); `importar_depois` sem "depois" no caso e `importar_via_depois` com arquivo ausente deixam de gerar exceção; **importação tudo-ou-nada** (falha no 3º arquivo não deixa a sessão pela metade). **Nível B (autorizado em 2026-10-16).** Evidência: `tests/test_entrada_arquivos.py` (23 testes; 22 falham sem a mudança), 1 teste de interface; suíte 242 passando + 1 xfail; nenhuma asserção anterior alterada (INV-210). **Seguimento (2026-10-17):** as duas correções do commit `7c3104a` (identificação de pasta no Windows e marcação das sessões V01), feitas pelo Work, foram **ratificadas por Fabrício em Nível B**, conforme o diff revisado (G2); este registro documenta a ratificação atual e **não** presume nem reescreve a autorização histórica do Work.
- [x] JV-T251A [P1] — **Pacote corretivo pós-G2 (Nível B, autorizado por Fabrício em 2026-10-17):** (1) rótulos fixos "REF-001-A" trocados por texto do caso selecionado (passos 1 e 2 e botão da medição "depois"); (2) "reconstruída pelas regras 1.0" só em sessões V01 efetivamente reconstruídas, em linguagem simples, via indicador derivado `analise.reconstruida` (sem metadado técnico em sessões novas; a interpretação continua registrada); (3) `is_dir()` dentro do tratamento de erros, compatível com Python 3.11 a 3.14. Arquivos: `src/jarvis/interface/janela.py`, `src/jarvis/sessao.py` (1 linha), `src/jarvis/rew_texto.py`, `tests/test_interface.py`, `tests/test_entrada_arquivos.py`. Sem alteração de cálculos, diagnóstico, σ̂, portão, limiares ou spec. Gate: G1. Evidência: suíte 253 passando + 1 `xfail` (3.13); testes sensíveis a versão (sessão, persistência, REW, entrada) 91 passando em 3.11, 3.12 e 3.14; nenhuma asserção anterior alterada; 8 dos 10 testes novos falham sem a mudança.

- [ ] JV-T252 [P0] — **Emenda E5 à spec do V02 (Nível A):** redação proposta em `03-spec/emenda-E5-PROPOSTA.md` (a importação guiada; b proveniência real × simulada, altera FR-013; c hipóteses sob portão restritivo, **condicionada à F-5**; d canal e lado declarados; e orientação de exportação). **Não aprovada; spec inalterada.** Gate: G2 e aprovação de Fabrício antes de T253–T256.
- [ ] JV-T253 [P0] — Importação guiada de medições reais: escolher 3 arquivos (via A, via B, A+B) e declarar tipo/id da referência temporal, taxa, posição do microfone, suavização e configuração do DSP; sem editar JSON. **Nível B (após T252).** Arquivos: `src/jarvis/sessao.py` (`importar_medicoes_reais`), `src/jarvis/interface/janela.py`, `tests/test_sessao.py`, `tests/test_interface.py`. Gate: G1. Evidência: sessão real importada sem manifesto escrito à mão; originais no cofre por hash.
- [ ] JV-T254 [P0] — Proveniência na interface: aviso fixo, título da janela e gráficos conforme a sessão (simulada, real ou mista); nunca "simulado" sobre dado real nem o inverso. **Nível B (após T252).** Arquivos: `janela.py`, `sessao.py`, `tests/test_interface.py`.
- [ ] JV-T255 [P0] — `propor_teste` e receita usam o canal e o lado declarados (hoje fixo em "tweeter esquerdo"). **Nível B (após T252).** Arquivos: `sessao.py`, `tests/test_sessao.py`. Evidência: lado direito e nomes de canal diferentes geram receita e reversão corretas.
- [ ] JV-T256 [P0] — (**condicionado à F-5, ainda em aberto**) Sem "hipótese mais provável" quando o portão barra ou σ̂ não é estimável; texto diz o que falta e **como reexportar do REW** (grade, suavização declarada). **Nível B (após T252).** Arquivos: `sessao.py`, `regras.py` (apresentação, sem mudar limiares), `janela.py`, testes. Decisão de Fabrício pendente: papel do σ̂ e do portão (F-5).
- [ ] JV-T257 [P1] — Interface: histórico legível (proveniência, modo, data completa), próximo passo concreto em resultado inconclusivo, nome e versão do candidato, guia curto de exportação do REW. Arquivos: `janela.py`, `COMO-EXPERIMENTAR.md`.
- [ ] JV-T258 [P0] — Três cenários reproduzíveis (importar e analisar arquivo REW real; medição problemática/inconclusiva; salvar, reabrir e preservar o histórico), com roteiro e capturas; declarar o que é demonstrável com dado real e o que é só sintético.
- [ ] JV-T259 — **G3 do candidato** no Windows de Fabrício (fecha T223 junto): backup e marcação "reconstruída pelas regras 1.0", N3 até o veredito, cenários C1–C3 com dado real, fechar e reabrir. Os testes na nuvem não substituem. Gate: G2 e G3.

