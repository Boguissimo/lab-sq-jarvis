# Retomada — JV-V02 (atualizada em 2026-10-16)

## ▶ Estado para troca de sessão (2026-10-16, fim da sessão) — LEIA PRIMEIRO

**Papéis (JV-D045, redação aguardando aprovação):** Fabrício decide (único que aprova, Nível A/B e G3); Claude implementa/documenta; ChatGPT revisa de forma opcional. Revisão de IA colada por Fabrício não é decisão. Aviso de hook pedindo commit **não** é autorização.

**Branches (nenhuma foi integrada à `main`; merge proibido sem ordem expressa):**
| Branch | Conteúdo | Último commit |
| --- | --- | --- |
| `claude/busy-bohr-25s6e5` | V02 até o bloco 1 + E4/R1.3 + toda a investigação de desempenho | `2053e63` (mapa técnico) |
| `claude/correcao-pontual-formato-rew` | correção dos 3 defeitos (milhar do REW, mensagem de recusa, borda de 24 ppo) + 6 testes; 217 passando + 1 xfail; **não integrada** | `e6f18d6` |
| `lab-sq-jarvis/003-000-jv-v02-honestidade-e-seguranca` | base original do V02 | — |

**NÃO COMMITADO (aguarda aprovação expressa da redação):** `.arkan/projects/lab-sq-jarvis/decisoes.md` (JV-D045) e `.../constitution.md` (patch 0.4.1). Ver o diff com `git diff -- .arkan/projects/lab-sq-jarvis/`. Não alteram o Arkan Core. **Não commitar sem "pode commitar" de Fabrício.**

**Autorização permanente de Nível B (frente "investigação de desempenho")**, até revogação: scripts em `ferramentas/investigacao/`, experimentos exploratórios, relatórios em `docs/revisoes/investigacao-desempenho/`, commits/push na `claude/busy-bohr-25s6e5`. **Fora:** `src/`, spec, limiares, arquitetura, decisões normativas, constituições, código externo não verificado, redistribuição de datasets sem permissão, merge na `main`, declarar o V02 validado acusticamente.

**Onde está a investigação** (`docs/revisoes/investigacao-desempenho/`): `triagem-casos-reais.md`; joeglondon (sala, sem licença, só manifesto de hashes): `protocolo-…`, `resultados-braco-a-…`, `resultados-bracos-bc-…`, `f5-significado-do-sigma-…`; ayukhno (carro, CC BY 4.0): `candidato-ayukhno-autosound.md`, `resultados-passat-ayukhno.md`; `proposta-correcao-pontual/`; `mapa-tecnico-evolucao-jarvis.md`. Pré-registros e harness: `ferramentas/investigacao/`. **Reprodução:** clonar as fontes (`github.com/joeglondon/speakers-2026-filters` @ `799af51`; `github.com/ayukhno/autosound-measurements` @ `7725d42`) fora do repositório, conferir os SHA-256 de `admissao-*.json` (o harness aborta se divergir) e rodar os scripts. Só `git clone` e `raw.githubusercontent.com` são alcançáveis do ambiente de nuvem.

**Resultados-chave:** (1) defeito de leitura do milhar do REW confirmado com dado real (95 % dos pontos); (2) F-5: σ̂ mistura estrutura espectral com ruído e depende da grade; rejeitou 25/25 aquisições da sala, mas no carro (mids) ficou em 0,2–0,8 dB e a RTA espacial 11/11 aprovada; (3) no Passat com falhas injetadas, **0 acertos** (polaridade/atraso): a fase vê os 180°, a Regra 2 não dispara em drivers reais sem crossover; (4) sucesso nos casos sintéticos **não** valida o uso real; V02 **não** está validado acusticamente.

**Decisões pendentes de Fabrício (consolidadas):**
1. Aprovar a redação da JV-D045 e do patch 0.4.1 (e então commitar).
2. Clarification do FR-002 (JV-V01) para o separador de milhar (texto proposto no relatório da sessão; nível B). Só então integrar a correção pontual.
3. F-5: papel do σ̂ e do portão (alternativas 1–5 em `f5-significado-do-sigma-joeglondon.md`); nada foi alterado.
4. Mapa técnico: faixa operacional por via como dado de entrada; promover `referencia/modelo.py` a motor de previsão; prioridade F-5 × faixa operacional; IR na aquisição (§8 do mapa).
5. Buscar um caso real com defeito documentado e antes/depois (única validação que falta).

**Pendência operacional:** G3 do bloco 1 (JV-T223) no Windows segue **parcial** (`COMO-EXPERIMENTAR.md`, `08-qa/g3-bloco1-parcial.md`); não invalida os testes aprovados.

**Ambiente:** `.venv` na raiz; para a suíte: `PYTHONPATH=src QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest` (libs Qt: `apt-get install libegl1 libgl1 libxkbcommon0 libfontconfig1 libdbus-1-3`).

### Complemento de fechamento da sessão (2026-10-16) — decisões e backup

**Backup do rascunho normativo:** `docs/revisoes/RASCUNHO-NORMATIVO-NAO-APROVADO-jv-d045-constituicao-0.4.1.patch` (verificado: `git apply` num checkout limpo de `03aa6a5` reproduz exatamente os dois arquivos). **É rascunho, não aprovação.** Os arquivos `decisoes.md` e `constitution.md` seguem fora do commit; recuperá-los com `git apply` se o working tree for perdido. Não commitar sem aprovação expressa da redação.

**Decisões de Fabrício a registrar (2026-10-16):**
- O **ChatGPT exerce também a gerência do projeto** (coordenação de prioridades, pendências, integração das frentes, revisão crítica). **Fabrício mantém exclusivamente a autoridade humana decisória.** A JV-D045 precisa **incorporar esse papel antes da aprovação definitiva** (o rascunho atual ainda descreve o ChatGPT só como revisor opcional e sem gate).
- Clarification do FR-002 (milhar REW): redação proposta no relatório da sessão (acréscimo ao FR-002: números en-US com milhar e decimal são um só valor; demais separadores como antes; vírgula decimal separada por espaço não coberta), **pendente de formalização** (nível B). Só depois integrar a correção pontual.
- O diagnóstico deve **evoluir para previsão e comparação física**, sem depender só de assinaturas de fase constante.
- A avaliação metrológica distingue **integridade, repetibilidade, estrutura acústica, incerteza e admissibilidade por análise**.
- O experimento **rigor × facilidade de uso** (aquisição simplificada × repetida × adaptativa) continua entre as próximas entregas.
- **Faixa operacional por via**, avaliação de `referencia/modelo.py` como motor de previsão e **IR como dado de primeira classe no V04** são **diretrizes de evolução, não implementações autorizadas**.
- O domínio atual dos algoritmos não pode limitar a futura análise do sistema automotivo completo. Calibração automatizada fica para depois, mas seus modelos físicos e dependências são considerados desde já.
- G3 Windows (JV-T223) segue **parcialmente concluído**.

**Estado técnico a preservar (sem extrapolar):** correção pontual em `claude/correcao-pontual-formato-rew` @ `e6f18d6` (217 passando + 1 xfail, sem merge); joeglondon e Passat com relatórios e limitações documentadas; **Passat: 0/80 detecções corretas nas falhas injetadas — resultado limitado a esse ensaio, sem extrapolar para desempenho geral**; F-5: σ̂ **não** é estimativa confiável de ruído da aquisição quando tomado isoladamente; mapa técnico concluído.

**Hashes remotos conferidos no fechamento** (`git ls-remote`, antes do commit deste complemento): `claude/busy-bohr-25s6e5` = `03aa6a5d5e0d2d94c83a668d29b220225bf37ef9`; `claude/correcao-pontual-formato-rew` = `e6f18d6054423ff21cbd275c8b3883515fa7e486`; base do V02 `lab-sq-jarvis/003-…` = `d56e0ad1f75a03f53936a70a60490e85d8a6d8d8`; `main` = `389e58083c0a74492e4111b7b19f72ea71839633` (intacta). O hash do commit deste complemento é informado na entrega da sessão (um arquivo não pode conter o próprio hash).

**Próxima sessão — frentes (continuidade operacional, sem reiniciar o planejamento):** (1) fechar pendências normativas (JV-D045 com o papel de gerência; patch 0.4.1; Clarification FR-002); (2) correções pontuais e integração controlada (só após a Clarification e ordem expressa); (3) investigação metrológica e experimento rigor × usabilidade; (4) evolução dos métodos de diagnóstico e previsão; (5) conclusão posterior do G3. Não abrir frentes adicionais sem necessidade. Fonte canônica: este arquivo (seção "LEIA PRIMEIRO"), `decisoes.md`, `.arkan/projects/lab-sq-jarvis/constitution.md` e `docs/revisoes/investigacao-desempenho/`.

### Atualização (2026-10-16, após aprovações de Fabrício)
- **Aprovados e commitados** (`392ea6c`): JV-D045 (com a gerência do ChatGPT; Fabrício mantém a autoridade decisória exclusiva) e constituição 0.4.1. Os arquivos `decisoes.md`/`constitution.md` já não estão pendentes; o `LEIA-ME-rascunhos-normativos.md` registra o histórico.
- **Clarification C-1 do FR-002 incorporada** à spec do JV-V01, com rastreio em `tasks.md` e teste do limite declarado, na branch `claude/correcao-pontual-formato-rew` (`bae3c3e`; 218 passando + 1 xfail). **A integração do código segue separada** (sem merge; aguarda ordem expressa).
- **Investigação concluída nesta fase** (`docs/revisoes/investigacao-desempenho/`): `metrologia-e-rigor-usabilidade-joeglondon.md`, `deriva-passat-gatilho-adaptativo.md`, `diagnostico-por-previsao-fisica.md`. Fabrício **não aprovou limiar adaptativo definitivo**: a necessidade de repetição deve ser avaliada na faixa e para a decisão pretendida. Diagnóstico por previsão: N0/N1 apenas; **N2 (diagnóstico independente) não alcançado**.

### Atualização (2026-10-16, previsão física)
- Fabrício aprovou **conceitualmente** o diagnóstico por previsão física como direção do V04 (**sem autorizar mudanças no produto**) e autorizou a rodada 2 no harness. Feita e documentada: `esclarecimento-metodologico-previsao-fisica.md`, `previsao-fisica-rodada2.md` (viabilidade e o que falta). Conclusão: viável como direção para polaridade/atraso em banda baixa/média de par admissível, com abstenção; **ainda não utilizável com confiança** (sem N2; carro sem soma física; margem do carro não estimável).
- **Protocolo de campo N2 no Focus preparado e NÃO iniciado** (`protocolo-campo-n2-focus.md`); depende de autorização expressa de Fabrício e da confirmação do equipamento (JV-D012).
- Pendente de decisão: autorizar o N2; autorizar a rodada 3 (margem derivada do controle do próprio sistema); `C_ADM`/margem seguem como parâmetros do harness (limiar de produto = P8).

---


> **Correção de estado (2026-10-16, sessão de aplicação da revisão externa):** as seções 1 e 4 abaixo, escritas antes do `/arkan.tasks`, ficaram desatualizadas. Valem: fase `07-implementation`; `tasks.md` aprovado (JV-T201 a T242); T201 a T222 concluídas. As revisões externas (técnica e adversarial) **já foram aplicadas** nas emendas E1, E2 e E3 / R1, R1.1 e R1.2. O que restava antes do G3 do bloco 1 eram as duas divergências do SC-208, tratadas na **emenda E4 (abaixo)**.
>
> **Emenda E4 — decisões do desenvolvedor registradas em 2026-10-16; redação final aguarda conferência e aprovação expressa; NADA COMMITADO ainda.** Muda o **critério de aceite** do SC-208. **(a) σ̂:** viés médio, erro absoluto, dispersão, percentis e proporção fora da tolerância original; 22/1 400 preservados; tolerância de 15 % σ + 0,05 **não** ampliada; **sem limite numérico de dispersão** e sem tratar o resultado como aprovação da precisão individual. **(b) detector:** separa mudança **indicativa** de **confirmada** (aquisição independente identificada, condições comparáveis, mesmo sentido, concordância e **faixa de frequência compatível**); o SC distingue desempenho observado, critério de aceitação e **limitação não resolvida**. **Limitação conhecida (não validado):** em σ = 1,5 dB há falsos positivos confirmados — 87/1 000 indicativos, 12/1 000 confirmados, 10/1 000 com faixa compatível — porque as aquisições "depois" compartilham o mesmo "antes" e não dão confirmações estatisticamente independentes. A meta de zero **não** foi reduzida para σ ≤ 1,0 dB; nenhum limite de falsos positivos é adotado; redesenho do detector (p. ex. repetir o "antes") fica **fora do V02**, para validação posterior; um limite futuro exige justificativa e teste independentes. σ̂, fator 3 e limiares **não mudam**. **Implementadas (não commitadas):** JV-T222A (`calculos.repeticao_confirma`, `faixa_compativel` no detector) e JV-T222B ("mudança suspeita; repetir a medição", sem afirmar alteração do DSP). Ensaio complementar: `08-qa/validacao-limiares-e4.md` (`ferramentas/medir_e4.py`); `validacao-limiares.md` mantém os números originais (só o texto de enquadramento mudou). **Verificação:** suíte completa em Linux com as libs de Qt (instaladas por `apt`), interface incluída: **211 passando e 1 `xfail`** (208 anteriores + 3 testes da E4), em 2026-10-16; falta repetir no Windows. **Limitação técnica da confirmação de faixa:** só interseção não vazia (a "mudança geral" cruza com qualquer faixa) e só as duas primeiras detecções positivas por via; não demonstra que a diferença ocorreu na mesma região fisicamente relevante; algoritmo não redesenhado. **Teste `xfail` do SC-208(b) original:** `test_calculos.py::test_detector_validacao_200_sementes` codifica o critério original e continua `xfail` estrito (16/200 com as sementes dele; 20/200 com as da validação; 87/1 000 nos dois): mesma taxa, sementes e critério de contagem diferentes — não há divergência de algoritmo. **Vereditos (conferência):** a indicativa é "mudança suspeita" (no máximo `inconclusiva`); a reproduzida é "mudança acústica reproduzida"; `comprometida` por via medida significa que o teste não isola a variável; a interface diz "a medição não identifica a causa" e **não comprova alteração no DSP**. Uma alteração adicional só aparece como **declarada** pelo usuário (afirmação, não prova do estado físico). O G3 do bloco 1 (JV-T223) vem depois.

> **Estado em 2026-10-16:** fase `07-implementation`. Tasks JV-T201 a T222 concluídas (fase 0 e bloco 1);
> suíte com 208 testes passando e 1 `xfail` estrito. Roteiro do G3 do bloco 1 pronto em `COMO-EXPERIMENTAR.md`
> (JV-T223 aguarda o desenvolvedor). **Antes do G3**, decidir duas divergências registradas em
> `08-qa/validacao-limiares.md`, sem ajustar limiar (P8):
> 1. o detector de mudança dá ~10 % de falsos positivos em "só polaridade" a σ = 1,5 dB (SC-208(b) pede zero); com fator 3,5 cai para 2 % e com fator 4 para 0,6 %, e o N3 continua detectado em 100 %;
> 2. o σ̂ tem 22 de 1 400 realizações fora de "15 % de σ + 0,05 dB", com a média sempre dentro (o SC-208 não diz se o critério vale por realização).
>
> Próximo: proposta de emenda (`JV-D`) para essas divergências → G3 do bloco 1 → bloco 2 (JV-T224…).
> Venv de testes do clone: `.venv` na raiz (criada em 2026-10-15).


Branch: `lab-sq-jarvis/003-000-jv-v02-honestidade-e-seguranca` · feature Arkan `003-000-jv-v02-honestidade-e-seguranca` · fase `04-architecture` **concluída** (spec e plano aprovados). Próximo: `/arkan.tasks`.
`main` contém o JV-V01 completo (commit `389e580`, QA aprovado, G3 cumprido no Windows). Esta branch parte dele.

## 1. Estado do JV-V02
| Fase | Artefato | Estado |
| --- | --- | --- |
| 01 Ideação | `01-discovery/ideacao.md` | aprovada (peso Code; superfície crítica: sim) |
| 03 Spec | `03-spec/spec.md` (FR-201 a FR-223, INV-201 a INV-214, SC-201 a SC-209) | aprovada em 2026-10-15, com as emendas **E1**, **E2** e **E3**, todas aprovadas em nível B; decisões nas Clarifications |
| 04 Plano | `04-architecture/plan.md` (ADR-201 a ADR-212), `data-model.md`, `quickstart.md` | revisão **R1** e complementos **R1.1** e **R1.2** aprovados em nível B; inclui a matriz de rastreabilidade (46 IDs; 47 com o INV-215 da E4, conferida por script) e os critérios de teste |
| 06 Tasks | `06-planning/tasks.md` (JV-T201 a T242) | aprovado em 2026-10-15; T201–T222 concluídas; T222A/B implementadas (E4), não commitadas |

~~Nenhum código do V02 foi escrito.~~ *(Desatualizado: ver a correção de estado no topo; 208 testes passando e 1 `xfail` estrito até a JV-T222.)* Testes do V01: 45 passando.

Commits: `2f0e8f1` (E1/R1), `1f6b62d` (E2/R1.1), `45f6401` (E3/R1.2 + revisão adversarial).

## 2. O que cada emenda decidiu (resumo; detalhe nas Clarifications da spec)
- **E1 — revisão técnica externa** (`docs/revisoes/jv-v02-revisao-tecnica-do-plano.md`):
  - irregularidade σ̂ por MAD da segunda diferença; o método antigo reprovava o próprio REF-001-A;
  - detector de mudança por via, nas duas vias, com três resultados;
  - admissibilidade SEG pela classe de risco;
  - INV-211 (interpretação lida do registro, sem recálculo) e INV-212 (incerteza desconhecida não vira aprovação);
  - "reversão documentada";
  - precedência e casos-limite da etapa de calibração;
  - SC-208 (varredura de limiares);
  - datas corrigidas para a data local.
- **E2 — decisões sobre a R1:**
  - "ruído não estimável" preserva as observações descritivas;
  - fixture do banco V01 gerada pelo V01 original, só sintética e permanente;
  - casos de segurança REF-003-S1 a S3 (FR-223, SC-209);
  - casos de referência inalterados (INV-213).
- **E3 — revisão adversarial** (`docs/revisoes/revisao-adversarial-projeto.md`, A01 a A09):
  - REF-003-S1 **bloqueado por SEG-07**, sem exceção para simulação;
  - referência temporal e aquisição comparável **declaradas**; `confirmada` exige aquisição comparável;
  - mudança só medida exige repetição por **aquisições independentes**, e mudança reproduzida não identifica o parâmetro;
  - presunções só para catálogo interno com **proveniência verificada** por hash (INV-214);
  - SC-208 restrito ao domínio simulado, com oráculos e testes metamórficos;
  - objetivo da etapa sem alegar alinhamento;
  - **ADR-212**: correções do V01 na fundação (portão básico obrigatório, cofre atômico, referência com campos obrigatórios);
  - esforço no G3 (dados sintéticos) separado da utilidade real (VP-10).

## 3. Pendências fora do V02
- **Diretriz REW** (`docs/revisoes/diretriz-fontes-de-medicao-e-rew.md`): registrar no planejamento evolutivo (proposta `JV-D043` e nota no feature map para F004/F013/F018) **com aprovação do desenvolvedor**.
- **VP-10 (utilidade real):** avaliar em incremento com medições reais.
- **Diretrizes estratégicas de produto** (`docs/revisoes/diretriz-estrategica-usuario-e-produto.md`; **`JV-D044` aprovada em 2026-10-16**, registrada em `decisoes.md`, com complemento de benchmark de mercado — três dimensões separadas, segurança não relativizada): usuário de referência (entusiasta que quer autonomia e aprender), públicos entusiasta e instalador (hipóteses comerciais **não demonstradas**), níveis de instrumentação (sem microfone, celular, USB calibrado, microfone com interface) a preservar arquiteturalmente, F009 com engines de IA por adaptadores e separação núcleo determinístico / IA / usuário, e sequência de validação (Focus → entusiastas → profissionais → comercialização). **Não amplia o JV-V02**: nenhuma feature, requisito ou task nova; reflexo apenas em nota no `feature-map.md` (F009, F013, F017). A `JV-D043` (diretriz do REW) continua pendente de decisão própria. Teste sintético não valida utilidade nem eficácia acústica em campo.

## 4. Próximos passos
> *(Atualizado em 2026-10-16: itens 1 e 2 já foram feitos até a JV-T222. Próximo: conferir a redação final da E4 e rodar a suíte completa → commit aprovado → G3 do bloco 1 (JV-T223) → bloco 2 (JV-T224…).)*

1. *(feito)* `/arkan.tasks`: tasks `JV-T201…`, nos três blocos com ponto G3 por bloco, mais a fase 0. A fase 0 traz as correções do V01 (ADR-212), a migração (ADR-207), a interpretação congelada, o modelo físico e o catálogo, e os contratos de qualidade e segurança.
2. `/arkan.analyze`, implementação, QA.

## 5. Como retomar (nova sessão)
- Repositório `Boguissimo/lab-sq-jarvis` (público). Na máquina do desenvolvedor, o **clone de trabalho** é `C:\Users\fabri\src-jv\repo`. A pasta `C:\Users\fabri\lab-sq-jarvis` é um pacote extraído em 2026-09-30, **sem `.git`**, e não deve ser editada.
- Para clonar em outro lugar: `git clone -b lab-sq-jarvis/003-000-jv-v02-honestidade-e-seguranca https://github.com/Boguissimo/lab-sq-jarvis`. No Windows, use um caminho curto: o clone em pasta muito longa falhou com "`$GIT_DIR` too big".
- Leia este arquivo, `docs/RETOMADA.md` (V01), `docs/revisoes/*` e os artefatos da feature 003.
- **Testes:** `python -m venv .venv` e `pip install -r requirements-dev.txt`. No Linux, instale `libegl1 libgl1 libxkbcommon0 libfontconfig1 libdbus-1-3` e rode `QT_QPA_PLATFORM=offscreen python -m pytest` (esperado: 45 passando). Há uma venv pronta em `C:\Users\fabri\lab-sq-jarvis\.venv`; o `python` do PATH no Windows é o atalho da Microsoft Store e trava.
- **Git neste clone:** sem identidade configurada; os commits usam `-c user.name=Claude -c user.email=noreply@anthropic.com`, como os anteriores da branch.
- **Convenções:**
  - Core do Arkan intacto; PT-BR; branches `lab-sq-jarvis/NNN-CCC-slug`.
  - A interface não calcula (ADR-03 do V01); limiares provisórios continuam provisórios; aprovação não verifica (JV-D032).
  - Emendas normativas exigem aprovação de nível B (ato e escopo nomeados).
  - O status da feature só aceita `em-desenvolvimento`, `em-producao` ou `arquivada`.
  - `.sh` em LF; `.bat` em CRLF.
- **Defeitos do Core já registrados (JV-D015):** `qa-mecanico.sh` exige seções "N/A" em planos Doc e dá falso positivo para marcadores `[TODO]` (colchetes sem escape).
- **Banco do V01** em `%LOCALAPPDATA%\LabSQJarvis`, com sessões que não podem ser perdidas. A migração (ADR-207) faz backup antes de mexer.
- **Decisões a não reabrir sem motivo:**
  - um incremento em três blocos; arquivo do PC-Tool opaco; calibração = alinhamento de atrasos tipo ATM;
  - SEG-02/07/09 só `não verificável`, e nenhum reforço é admitido;
  - presunções só para catálogo com proveniência verificada.

## G3 do bloco 1 — andamento (16/10/2026)
Parcial, **não concluído**: suíte Windows 211 + 1 `xfail`, abertura, sessão V01 e N3 (análise) OK. Faltam backup/migração, N3 até o veredito, demais casos e reabertura: ver `COMO-EXPERIMENTAR.md` e `08-qa/g3-bloco1-parcial.md`. Proposta da bancada automatizada (não decidida): `docs/revisoes/planejamento-bancada-validacao.md`.
