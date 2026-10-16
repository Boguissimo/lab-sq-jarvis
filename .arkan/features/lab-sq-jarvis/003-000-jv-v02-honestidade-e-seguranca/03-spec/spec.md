# Spec — 003-000-jv-v02-honestidade-e-seguranca (JV-V02)

> **Status**: aprovada pelo desenvolvedor em 2026-10-15 · **Emenda E1** (revisão externa do plano): **aprovada pelo desenvolvedor em 2026-10-15 (nível B)** | **Data**: 2026-10-15
> **Entrada**: [ideacao.md](../01-discovery/ideacao.md) (aprovada). Complementa a spec do JV-V01; o que não é dito aqui continua valendo como no V01.
> **Emenda E1** (2026-10-15): origem `docs/revisoes/jv-v02-revisao-tecnica-do-plano.md`, itens 3, 4, 5, 7, 8, 11 e 12; decisões do desenvolvedor em Clarifications. Seções alteradas: Edge Cases, Definições normativas, FR-201, 202, 207, 208, 211, 217, 220, 221; INV-201, 203, 205; INV-211 e 212 novos; SC-203; SC-208 novo; Limites declarados. Datas: a aprovação registrada como "2026-10-16" vinha do relógio UTC dos commits; a data local é 2026-10-15.
> Siglas: **REW** — Room EQ Wizard; **DSP** — processador digital de sinais; **SEG** — regra de segurança; **ATM** — alinhamento automático de atrasos da ferramenta do DSP; **T/S** — parâmetros Thiele-Small; **Fs** — frequência de ressonância; **G1/G2/G3** — gates.

## Cenários de Usuário

**US-01 — Aceitar que não dá para concluir (P1).** Como desenvolvedor, quero que o Jarvis recuse concluir quando a medição não presta, para não ser enganado por um resultado bonito.

- Dado o caso REF-001-N2 (ruído alto), quando analiso, então vejo "não dá para concluir", o motivo (ruído acima do limite) e o que falta (nova medição com menos ruído); nenhuma hipótese é ordenada e nenhum teste é proposto.
- Dado o caso REF-001-N4 (sem referência temporal comum), quando analiso, então fase e soma prevista são recusadas com explicação, e vejo só magnitude e soma de potências.

**US-02 — Não ser conduzido à hipótese errada (P1).** Como desenvolvedor, quero que um vale que já existe nas vias individuais não vire "polaridade invertida".

- Dado o caso REF-001-N1, quando analiso, então o Jarvis aponta o vale presente numa via, ordena a interferência/reflexão antes da polaridade, não propõe teste de polaridade como primeiro passo e não sugere reforço de EQ.
- Dado o caso REF-001-N5 (sem problema), quando analiso, então o Jarvis diz que não há indício de problema no cruzamento e sugere "nada a alterar" com justificativa que eu posso editar e registrar.

**US-03 — Ver o resultado de um teste mal feito como mal feito (P1).** Como desenvolvedor, quero que um "depois" com mais de uma mudança não confirme nem refute a hipótese.

- Dado o caso REF-001-N3, quando importo o "depois", então o veredito é `comprometida`, a hipótese não é marcada como refutada, e o Jarvis explica o que mudou além da polaridade e propõe refazer com uma variável.

**US-04 — Ver a incerteza num caso realista (P1).** Como desenvolvedor, quero o REF-001-B (alto-falantes reais, pequena diferença de distância, ruído moderado) com veredito e incerteza declarada maior que a do REF-001-A.

**US-05 — Saber o que é seguro e o que não é (P2).** Como desenvolvedor, quero que toda recomendação mostre o resultado de cada regra SEG (`aprovada`, `bloqueada`, `não verificável`), os valores provisórios como tal e as limitações, sem nunca chamar de seguro o que não foi verificado.

**US-06 — Percorrer uma etapa de calibração simulada (P2).** Como desenvolvedor, quero registrar um conjunto de ajustes de atraso (tipo ATM) antes e depois, e ver se o objetivo foi atingido, sem que o Jarvis atribua a melhora a um ajuste isolado.

**US-07 — Reverter só quando dá (P2).** Como desenvolvedor, quero guardar o arquivo de ajuste "antes" e "depois" e, ao pedir reversão, receber o arquivo a carregar, a receita inversa completa, ou o aviso "reversão não documentada" com o que falta — sabendo que nenhum dos dois confirma a restauração física (E1).

### Edge Cases

- Medição "depois" importada antes da previsão registrada: recusada (INV-004 do V01).
- Caso importado com `manifesto.json` sem campo de referência temporal: tratado como incompatível (recusa de fase).
- Caso com vale em uma via **e** ruído alto: prevalece "não dá para concluir".
- Etapa de calibração sem objetivo registrado antes: o "depois" é recusado.
- Reversão pedida numa etapa de calibração cujo arquivo "antes" não foi guardado e com parâmetros incompletos: "reversão não documentada".
- (E1) Medição com suavização declarada, desconhecida, grade não logarítmica uniforme ou densidade insuficiente: "ruído não estimável" — **não** é qualidade aprovada (INV-212).
- (E1) Cancelamento profundo ou reflexão forte **sem** ruído (ex.: soma "antes" do REF-001-A): não reprova a qualidade; o defeito acústico não é confundido com ruído.
- (E1) "Depois" com medições individuais tiradas em outra posição de microfone, outro ganho de entrada ou outra referência de nível: verificação da variável única `inconclusiva`; a diferença não é atribuída ao DSP.
- (E1) "Depois" sem medições individuais: avaliação só pela configuração declarada, com o aviso "outras alterações não foram verificadas".
- (E1) Etapa de calibração com deficit "antes" ≤ 3 dB: o objetivo de deficit já está atendido; nenhuma alteração é proposta para atingi-lo (uma etapa com outro objetivo continua possível).
- (E1) Recomendação de risco crescente com regra aplicável sem dado confirmado: aparece como "alteração bloqueada — não recomendada", sem receita executável.

## Definições normativas

| Termo | Definição verificável | Estado |
| --- | --- | --- |
| Irregularidade ponto a ponto estimada (σ̂) — *substitui "ruído estimado" (E1)* | em cada medição usada na análise, **inclusive as somas**: σ̂ = 1,4826 × MAD(Δ²L) / √6, onde Δ²L é a segunda diferença do nível em dB, na grade logarítmica uniforme, entre 200 Hz e 10 kHz, e MAD é a mediana dos desvios absolutos em torno da mediana. O fator converte a MAD em desvio padrão **sob a hipótese** de ruído aditivo gaussiano independente entre pontos. σ̂ é uma estimativa normalizada de irregularidade fina, **não** uma medição direta de ruído nem um indicador geral de qualidade acústica | método fixo (E1); limiares abaixo provisórios |
| Condições de aplicação do estimador | (i) grade logarítmica uniforme: razão entre frequências vizinhas constante em ±0,5 %; (ii) densidade ≥ **24 pontos por oitava**; (iii) suavização declarada `nenhuma`. A suavização vem do manifesto (`suavizacao`). Ausente num caso do catálogo do Jarvis (`simulado: true`), vale `nenhuma`, porque o gerador não suaviza. Ausente em arquivo externo, é `desconhecida` | (ii) **provisório** |
| Ruído não estimável | falha em qualquer condição de aplicação. **Não é qualidade aprovada**: a incerteza fica "não quantificada" e o veredito do teste fica limitado a `inconclusiva` (INV-212) | regra fixa |
| Qualidade reprovada por irregularidade | σ̂ > **1,5 dB** em qualquer medição usada na análise | **provisório — limite candidato**, sujeito à validação (SC-208) |
| Aviso de irregularidade | σ̂ entre **0,5 dB** e 1,5 dB: análise permitida, incerteza declarada maior | **provisório — limite candidato**, sujeito à validação (SC-208) |
| Vale individual | numa via, entre 200 Hz e 10 kHz, nível ≥ **10 dB** abaixo da média móvel de 1/3 de oitava, com largura ≤ 1/3 de oitava | **provisório** |
| Condições de aquisição comparáveis (E1) | para cada via, as medições "antes" e "depois" têm a mesma posição de microfone (`posicao_microfone`), o mesmo ganho de entrada (`ganho_entrada_db`) e a mesma referência de nível (`referencia_nivel`), todos declarados no manifesto. Campo ausente ou diferente ⇒ não comparáveis | regra fixa |
| Faixa útil da via (E1) | pontos entre 200 Hz e 10 kHz em que o nível "antes" da via é ≥ (máximo da via nessa faixa − **20 dB**) | **provisório** |
| Detector de mudança da via (E1) — *substitui "mudança de nível da via"* | aplicado a **cada via** que tenha medição individual "antes" e "depois", na faixa útil da via, sobre Δ = nível "depois" − nível "antes": **mudança geral** se \|média de Δ\| > **1,0 dB**; **mudança localizada** se, em alguma banda de 1/3 de oitava (janela deslizante sobre a grade), \|média de Δ na banda\| > max(**1,5 dB**; **3**·σΔ), onde σΔ = √(σ̂²antes + σ̂²depois) / √n e n é o número de pontos da banda | limiares e fator 3 **provisórios** |
| Resultado do detector, por via (E1) | `mudança detectada`: mudança geral ou localizada. `mudança não detectada (resolução: média 1,0 dB; bandas X dB)`: nenhuma das duas, com condições comparáveis e σ̂ estimável nas duas medições; X é o limiar efetivo das bandas, sempre declarado. `verificação inconclusiva`: condições de aquisição não comparáveis, ou σ̂ não estimável sem mudança geral detectada. Nesse caso nenhuma diferença é atribuída a alteração do DSP. Sem medição individual "depois", o detector não roda e a via fica "não verificada" | regra fixa |
| Depois comprometido | (a) a configuração declarada "depois" difere da proposta em algum parâmetro além da variável testada, **ou** (b) o detector dá `mudança detectada` em alguma via, sendo a variável testada de um tipo que não altera a magnitude da via isolada (polaridade, atraso). Neste incremento, todo teste de diagnóstico é de polaridade | regra fixa; limiares de (b) provisórios |
| Precedência do veredito do teste (E1) | 1º (a) ⇒ `comprometida`, qualquer que seja a qualidade da medição; 2º qualidade "depois" reprovada ou ruído não estimável ⇒ no máximo `inconclusiva`; 3º (b) ⇒ `comprometida`; 4º veredito normal do V01 (`confirmada`/`refutada`/`inconclusiva`). `verificação inconclusiva` ou via "não verificada" não elevam nem rebaixam o veredito, mas aparecem como limitação ("outras alterações não foram verificadas") | regra fixa |
| Deficit no cruzamento (E1) | max(0; maior valor de (soma de potências − soma medida) na região de sobreposição), em dB | regra fixa |
| Objetivo da etapa de calibração | deficit ≤ **3 dB**. Com deficit "antes" ≤ 3 dB, o objetivo já está atendido e nenhuma alteração é proposta para atingi-lo (E1) | **provisório** |
| Resultado da etapa — precedência (E1) | avaliado nesta ordem; vale o primeiro que se aplica: | — |
| 1. `inconclusivo` | qualidade reprovada ou ruído não estimável em medição da etapa, referência temporal incompatível ou "depois" ausente | — |
| 2. `objetivo atingido` | deficit "depois" ≤ 3 dB | — |
| 3. `parcial` | redução do deficit, (antes − depois) / antes, ≥ **50 %**. O denominador é > 3 dB pela pré-condição: sem divisão por zero | **provisório** |
| 4. `não atingido` | redução < 50 %, inclusive piora | — |
| Reversão documentada — *substitui "reversão garantida" (E1)* | existe arquivo "antes" arquivado **ou** todos os valores anteriores dos parâmetros alterados estão registrados. Quer dizer que existe um **procedimento** de restauração, **não** que a restauração física foi executada ou confirmada; a confirmação física exige nova medição comparada ao "antes" e fica fora deste incremento. Arquivar um arquivo não garante que ele seja compatível com o DSP nem que seja aplicado corretamente | — |
| Admissibilidade da recomendação (E1) | decidida pelos resultados SEG e pela classe (regras de segurança, seção 1). **Risco crescente**: qualquer regra aplicável `bloqueada` ou sem dado confirmado ⇒ `alteração bloqueada — não recomendada`. **Risco decrescente**: regra aplicável `bloqueada` ⇒ bloqueada; `não verificável` **não bloqueia** e a recomendação sai com a lista do que não foi verificado e o aviso de efeitos colaterais. **Não sensível**: admitida com SEG-08 e SEG-11. Alteração bloqueada nunca aparece como recomendação executável: não tem receita aplicável nem aprovação disponível | regra fixa |
| Valor acessível (SEG-13) | valor que o desenvolvedor lê na ferramenta e informa (origem `declarado`) ou efeito observado em medição (origem `medição`) | — |

## Requirements

### Bloco 1 — Casos e honestidade

| ID | Requisito | Teste |
| --- | --- | --- |
| FR-201 | Gerar de forma determinística REF-001-B, REF-001-N1 a N5 e as quatro variantes da etapa de calibração `REF-002-A-atingido`, `-parcial`, `-nao-atingido` e `-inconclusivo`, com a mesma cadeia de arquivos do REF-001-A (`medio`, `tweeter`, `soma-antes`, `soma-depois`, manifesto). (E1) Magnitude, fase e soma saem do mesmo modelo físico (filtros, atrasos, polaridades, reflexões); ruído e erros de aquisição entram **depois**, como perturbação de cada medição, com `ruido_sigma_db` e semente registrados no manifesto. O manifesto aceita medições individuais "depois" das **duas** vias e, por medição, `suavizacao`, `ganho_entrada_db` e `referencia_nivel`. REF-001-A continua byte a byte | `test_casos.py` |
| FR-202 | Calcular a irregularidade ponto a ponto σ̂ de cada medição usada na análise, inclusive as somas, conforme a definição normativa. Registrar como cálculo (algoritmo, versão, condições de aplicação, entradas por hash). Reprovar a qualidade acima do limite, declarar o aviso e declarar "ruído não estimável" quando as condições falham | `test_calculos.py` |
| FR-203 | Com qualidade reprovada: responder "não dá para concluir", com o motivo e o que falta; não ordenar hipóteses; não propor teste; permitir "solicitar dados adicionais" | `test_sessao.py::test_n2` |
| FR-204 | Detectar vale individual e registrá-lo como indício I-3; com I-3 e sem oposição de fase constante (I-2), ordenar "interferência ou reflexão na via" antes de "polaridade invertida" e não propor teste de polaridade como primeiro passo | `test_regras.py`, `test_sessao.py::test_n1` |
| FR-205 | Sem referência temporal comum: recusar diferença de fase, atraso e soma prevista; mostrar magnitude e soma de potências; dizer o que falta (medir com a mesma referência) | `test_sessao.py::test_n4` |
| FR-206 | Sem I-1 nem I-2 e sem vale individual: informar "sem indício de problema no cruzamento" e oferecer a decisão "nada a alterar" com justificativa pré-preenchida e editável; nada é registrado sem confirmação | `test_sessao.py::test_n5` |
| FR-207 | (E1) Aceitar medições individuais "depois" das duas vias. Aplicar o detector de mudança a cada via e a regra de precedência do veredito. Emitir `comprometida` quando o "depois" é comprometido; a hipótese não vira `refutada` nem `confirmada`. Indicar o que mudou (parâmetro declarado ou via e faixa da mudança detectada) e propor refazer com uma variável. Mostrar por via o resultado do detector, com a resolução quando for `mudança não detectada`. Sem medições individuais "depois", avaliar só pela configuração declarada e dizer "outras alterações não foram verificadas" | `test_sessao.py::test_n3`, `test_calculos.py::test_detector_mudanca` |
| FR-208 | No REF-001-B, emitir `confirmada` com incerteza declarada calculada de σ̂ e maior que a do REF-001-A. No "depois" com qualidade reprovada ou ruído não estimável, no máximo `inconclusiva` | `test_sessao.py::test_ref001b` |
| FR-209 | Seletor de caso na interface (lista dos casos distribuídos) e, para cada resultado dos FR-203 a FR-208, texto em linguagem simples com origem dos números e aviso de dados simulados | `test_interface.py` |

### Bloco 2 — Regras de segurança

| ID | Requisito | Teste |
| --- | --- | --- |
| FR-210 | Classificar toda recomendação em `sensível — risco crescente`, `sensível — risco decrescente` ou `não sensível` (regras de segurança v0.4.0, seção 1) | `test_seguranca.py` |
| FR-211 | Avaliar SEG-01, 03, 04, 05, 06, 08, 10, 11, 12 e 13 e registrar o resultado de cada regra aplicável (`aprovada`, `bloqueada`, `não verificável`) com a limitação da seção 0; regra sem dado confirmado segue a coluna "sem dado confirmado" das regras. (E1) A avaliação **decide a admissibilidade** (definição normativa) **antes** de a recomendação ser registrada ou exibida, inclusive no teste de polaridade herdado do V01, cujo bloco de segurança passa a vir dessa avaliação. Alteração bloqueada fica registrada como "alteração bloqueada — não recomendada", com motivo e o que falta, sem receita executável | `test_seguranca.py`, `test_seguranca.py::test_admissibilidade` |
| FR-212 | SEG-02, SEG-07 e SEG-09 não têm fonte para valor ou método: o contrato das regras existe, mas o resultado é sempre `não verificável` e qualquer reforço que dependa delas é **bloqueado**; nenhum modelo de excursão, margem digital ou exposição é calculado neste incremento; a tela diz o que falta (T/S confirmados e Fs; atenuação a montante documentada; critério de exposição com fonte) | `test_seguranca.py` |
| FR-213 | Dados de equipamento `planejado` ou `informado` nunca alimentam regra como confirmados (SEG-12) | `test_seguranca.py` |
| FR-214 | Mostrar os valores provisórios como provisórios na própria recomendação (ex.: "limite provisório de +1,5 dB") | `test_seguranca.py`, `test_interface.py` |
| FR-215 | Mostrar a "Verificação de segurança" em toda recomendação exibida na interface, inclusive a de polaridade (SEG-08, 10, 11 e 12 aplicáveis; as demais, "não se aplica") | `test_interface.py` |
| FR-216 | Aprovação de nível B registrada para recomendação sensível, sem alterar o resultado das regras (aprovação não verifica) | `test_seguranca.py` |

### Bloco 3 — Calibração simulada e configuração

| ID | Requisito | Teste |
| --- | --- | --- |
| FR-217 | Etapa de calibração simulada (variantes REF-002-A): registrar objetivo e limites informados (SEG-13) antes; conjunto de parâmetros antes/depois; resultado conforme a definição normativa e sua precedência; texto sem atribuir a melhora a um ajuste isolado. (E1) Com deficit "antes" ≤ 3 dB, informar "objetivo de deficit já atendido" e não propor alteração para atingi-lo | `test_calibracao.py` |
| FR-218 | Na etapa de calibração, parâmetros sensíveis não acessíveis ficam `não verificado`, com a lista do que não foi conferido e a origem de cada valor conferido | `test_calibracao.py` |
| FR-219 | Arquivar arquivo de ajuste ("antes"/"depois") como arquivo opaco por hash, ligado à configuração (nível `arquivada`), sem ler o conteúdo; sugerir o nome `JV-AAAA-MM-DD-S<sessão>-antes` / `-depois` | `test_configuracao.py` |
| FR-220 | No início da sessão, mostrar a última configuração registrada **em qualquer sessão anterior** (a mais recente, com a sessão de origem) e pedir confirmação ou outra configuração (`declarada`); o nível `coerente` não existe neste incremento | `test_configuracao.py`, `test_interface.py` |
| FR-221 | Reversão: arquivo "antes" arquivado → indicar qual arquivo carregar; senão, receita inversa só se todos os valores anteriores estiverem registrados; senão, "reversão não documentada" e o que falta. (E1) Os dois primeiros desfechos aparecem como "reversão documentada", com o aviso de que a restauração física não está confirmada até nova medição; arquivo arquivado não garante compatibilidade com o DSP. A chave `garantida` dos registros do V01 continua legível | `test_configuracao.py` |
| FR-222 | Estender a rotina de integridade às novas relações (etapa, arquivo de ajuste, resultado de regras) e ao diário | `test_persistencia.py` |

## Invariantes

- INV-201: um resultado nunca é mais conclusivo que a qualidade das medições: qualidade reprovada ⇒ nenhum veredito acima de `inconclusiva` e nenhuma hipótese ordenada. (E1) Defeito acústico sem ruído (cancelamento, reflexão) não reprova a qualidade. **Teste:** `test_sessao.py::test_qualidade_limita_conclusao`, `test_calculos.py::test_irregularidade_nao_confunde_vale`.
- INV-202: `comprometida` nunca é registrada como `refutada` nem `confirmada` da hipótese. **Teste:** `test_sessao.py::test_comprometida_nao_refuta`.
- INV-203: nenhuma recomendação sensível aparece como segura, nem sem a lista de resultados das regras e das limitações; regra `bloqueada` ou `não verificável` nunca vira "segura" por aprovação. (E1) Alteração bloqueada nunca aparece como recomendação executável (sem receita aplicável, sem aprovação disponível); toda recomendação exibida, inclusive o teste de polaridade, passou pela avaliação de admissibilidade antes de ser registrada. **Teste:** `test_seguranca.py::test_aprovacao_nao_verifica`, `test_seguranca.py::test_admissibilidade`, `test_seguranca.py::test_propriedade_sem_violacao` (recomendações aleatórias com semente fixa: zero violações nas exibidas).
- INV-204: reforço de EQ nunca é recomendado para vale classificado como cancelamento ou interferência (SEG-06). **Teste:** `test_seguranca.py::test_seg06`, `test_sessao.py::test_n1`.
- INV-205: reversão só mostra receita quando o valor anterior de todos os parâmetros alterados está registrado ou há arquivo "antes"; (E1) "reversão documentada" nunca é apresentada como restauração física confirmada. **Teste:** `test_configuracao.py::test_reversao_nao_documentada`, `test_configuracao.py::test_documentada_nao_e_fisica`.
- INV-206: etapa de calibração não produz conclusão causal sobre ajuste isolado. **Teste:** `test_calibracao.py::test_sem_atribuicao_causal`.
- INV-207: arquivo de ajuste guardado não é lido nem alterado; o programa nunca escreve no DSP (SEG-11). **Teste:** `test_configuracao.py::test_arquivo_opaco`, busca no código por escrita ao DSP no QA.
- INV-208: mesmas entradas, mesmos resultados, inclusive nos casos com ruído (semente fixa). **Teste:** `test_casos.py::test_deterministico`.
- INV-209: Core do Arkan intacto. **Teste:** `git diff` das pastas do Core contra a fundação, registrado no QA.
- INV-210: o INV-001 a INV-006 do V01 continuam valendo. **Teste:** suíte do V01 passando sem alteração de asserções.
- INV-211 (E1): a interpretação registrada não muda ao reabrir a sessão. Indícios, hipóteses, sugestão, controles de qualidade, resultados SEG, admissibilidade e vereditos são lidos do registro, que guarda a versão do algoritmo ou das regras, os limiares usados e os hashes das entradas; nada é recalculado silenciosamente com regras novas. Sessões legadas do V01 continuam abrindo e mostrando o que foi registrado, sem exigir metadados que não existiam; o que o V01 não gravou aparece reconstruído pelas regras **na versão com que a sessão foi feita** (1.0), identificado como tal. **Teste:** `test_sessao.py::test_reabrir_nao_recalcula`, `test_persistencia.py::test_sessao_v01_legivel`.
- INV-212 (E1): incerteza desconhecida nunca vira aprovação. "Ruído não estimável" não é qualidade aprovada; `verificação inconclusiva` e via "não verificada" não são "sem mudança"; `mudança não detectada` sempre declara a resolução. **Teste:** `test_calculos.py::test_nao_estimavel_nao_aprova`, `test_sessao.py::test_sem_dados_nao_e_sem_mudanca`.

## Critérios de Sucesso

- **SC-201** — REF-001-N1 a N5 produzem o comportamento da tabela da proposta (seção 7.1) nos cinco casos. **Instrumento:** `test_sessao.py::test_n1` a `test_n5`. **Baseline:** N/A — funcionalidade nova.
- **SC-202** — REF-001-B fecha o percurso com `confirmada` e incerteza declarada maior que a do REF-001-A. **Instrumento:** `test_sessao.py::test_ref001b`. **Baseline:** N/A.
- **SC-203** — Etapa de calibração com os quatro resultados nas variantes `REF-002-A-atingido`, `-parcial`, `-nao-atingido` e `-inconclusivo`, mais os casos-limite: deficit "antes" ≤ 3 dB (nada proposto), deficit negativo limitado a zero, piora e redução de exatamente 50 %. **Instrumento:** `test_calibracao.py`. **Baseline:** N/A.
- **SC-204** — Zero violações em 1 000 recomendações aleatórias (semente fixa) pelas regras SEG implementadas. **Instrumento:** `test_seguranca.py::test_propriedade_sem_violacao`. **Baseline:** N/A.
- **SC-205** — Reversão nos três desfechos (documentada por arquivo, documentada por receita, não documentada), sempre sem afirmar restauração física. **Instrumento:** `test_configuracao.py`. **Baseline:** N/A.
- **SC-206** — O desenvolvedor percorre os casos pelo programa no Windows e reconhece a explicação de cada um (G3). **Instrumento:** roteiro `COMO-EXPERIMENTAR.md` atualizado. **Baseline:** JV-V01 no Windows aprovado.
- **SC-207** — Suíte completa (V01 + V02) passando em Linux, sem alterar asserções do V01. **Instrumento:** `python -m pytest`. **Baseline:** 45 testes passando no JV-V01.
- **SC-208** (E1) — Validação dos limiares provisórios por varredura, com falsos positivos e falsos negativos registrados em `08-qa/validacao-limiares.md`. **(a) σ̂:**
  - Casos sem ruído (os quatro arquivos do REF-001-A, reflexões e cancelamentos): σ̂ ≤ 0,05 dB.
  - Ruído conhecido, isolado ou combinado com vales: \|σ̂ − σ injetado\| ≤ 15 % de σ + 0,05 dB.
  - Varredura de σ logo abaixo e logo acima de 0,5 e 1,5 dB.
  - Curvas suavizadas: "não estimável", nunca aprovadas.

  **(b) Detector de mudança:**
  - Zero falsos positivos em "só polaridade" até σ = 1,5 dB.
  - Detecção registrada para mudança global (ganho ±1,5 e ±3 dB, deslocamento de corte) e para filtros estreitos (Q 2 a 4, ±3 dB).
  - Mudança de posição simulada ⇒ `verificação inconclusiva`.

  **(c) Vale individual, deficit e limites SEG:** valores logo acima e logo abaixo de cada limite.

  Os limiares **não são ajustados para os casos de referência passarem**: mudança de limiar exige `JV-D`. **Instrumento:** `test_validacao_limiares.py` (gera a tabela). **Baseline:** N/A.

## Limites declarados

- Casos simulados ideais ou levemente realistas: não representam o carro (JV-D025).
- Limiares marcados como provisórios nas definições normativas e nos valores SEG: validados só em casos simulados.
- SEG-02, SEG-07 e SEG-09: sem modelo de cálculo (falta fonte); ficam `não verificável` e bloqueiam reforço até haver cadastro do equipamento e fonte.
- Arquivo de ajuste do PC-Tool tratado como opaco; leitura é F019.
- IA continua fora (JV-V03).
- (E1) σ̂ só enxerga irregularidade fina e independente entre pontos. Ruído correlacionado, de baixa frequência ou removido por suavização não aparece nele. Por isso suavização desconhecida ⇒ "não estimável".
- (E1) O detector de mudança só prova ausência de mudança **acima da resolução declarada**; mudanças estreitas abaixo dela passam despercebidas.
- (E1) "Reversão documentada" é um procedimento disponível, não uma restauração física confirmada.

## Clarifications

### Sessão 2026-10-15

- **SEG-02, SEG-07 e SEG-09 sem fundamentação.** Decisão do desenvolvedor (opção A, depois de esclarecer): sem modelos simplificados no V02; as três regras resultam sempre `não verificável` e bloqueiam reforço (FR-212). O cálculo entra com o cadastro do equipamento e uma fonte.
- **Detecção de `comprometida`.** Decisão do desenvolvedor: duas vias, qualquer uma basta — configuração declarada "depois" diferente da proposta ou mudança de nível de via acima de 1,0 dB (definição normativa). *Substituída na emenda E1 (abaixo).*

### Sessão 2026-10-15 — Emenda E1 (revisão externa do plano)

Origem: `docs/revisoes/jv-v02-revisao-tecnica-do-plano.md`. A evidência numérica foi apresentada ao desenvolvedor antes de cada decisão. As decisões seguem o Princípio VIII: o desenvolvedor nomeou o ato (registrar as alterações normativas na spec e no plano) e o escopo (itens abaixo).

- **Ruído (item 3).** *Evidência:* o método anterior (resíduo × média móvel de 7 pontos) dá 2,27 dB na soma "antes" do REF-001-A e reprovaria o caso do V01. Ele também dá 0,62 dB numa reflexão forte sem ruído: mede curvatura espectral, não ruído. A segunda diferença robusta dá 0,00 nesses casos e acompanha o ruído injetado (0,28 / 0,91 / 2,23 dB para σ = 0,3 / 1,0 / 2,0). *Decisão:*
  - Irregularidade ponto a ponto por MAD da segunda diferença, em grade logarítmica uniforme, de 200 Hz a 10 kHz, com fator 1,4826/√6 e em todas as medições, inclusive as somas.
  - "Ruído não estimável" quando o estimador não se aplica; isso não é qualidade aprovada.
  - 0,5 e 1,5 dB ficam como limites candidatos provisórios.
  - Validação com ruído conhecido, vales sem ruído e combinações, com falsos positivos e falsos negativos registrados.
  - A estimativa não é medição direta de ruído nem indicador universal de qualidade.
  - *Complemento do agente, a aprovar:* a suavização é **declarada**, não inferida. O teste mostrou que suavizar 3 pontos reduz σ̂ em cerca de 3,5× e que a autocorrelação da segunda diferença não separa os casos com segurança. Ausência de declaração vale `nenhuma` em caso do catálogo do Jarvis e `desconhecida` em arquivo externo. Com ruído não estimável, o veredito fica limitado a `inconclusiva`; os testes do V01 só usam casos do catálogo, então o INV-210 não é afetado.
- **`comprometida` (item 7).** *Evidência:* a regra anterior (média entre 1 e 10 kHz) não gera falso positivo com ruído, mas não detectou EQ estreita (PEQ de −3 dB em 6 kHz no tweeter e de −4 dB em 800 Hz no médio: 0 %). O detector híbrido detectou o N3 em 100 % dos casos e não deu falso positivo em "só polaridade" até σ = 1,5 (200 sementes). *Decisão:*
  - Detector híbrido por via, nas duas vias, cada uma na sua faixa útil.
  - Média > 1,0 dB para mudanças gerais; bandas de 1/3 de oitava > max(1,5 dB; 3σΔ) para mudanças localizadas.
  - σΔ a partir de σ̂ das duas medições, quando estimável.
  - Condições de aquisição comparáveis exigidas (posição, ganho, referência de nível). Sem elas, a verificação é `inconclusiva` e a diferença não é atribuída ao DSP.
  - Três resultados: detectada, não detectada dentro da resolução e inconclusiva.
  - Sem medições individuais "depois", vale a avaliação pela configuração declarada, com o aviso explícito.
  - Validação com mudanças globais, filtros estreitos, ruído conhecido e mudança de posição simulada.
  - Limiares provisórios.
- **Admissibilidade SEG (item 4).** Alteração bloqueada nunca aparece como recomendação executável. `não verificável` só bloqueia onde as regras canônicas mandam, ou seja, em risco crescente sem dado confirmado; em risco decrescente não bloqueia. Vale também para o teste de polaridade herdado.
- **Rastreabilidade histórica (item 5).** Novo INV-211: preservar a interpretação registrada (versões, limiares, hashes), sem recalcular resultados antigos com regras novas. Sessões do V01 continuam acessíveis sem exigir metadados retroativos.
- **Configuração e reversão (item 8).** A última configuração vem de qualquer sessão. "Reversão garantida" passa a ser "reversão documentada", que distingue procedimento de restauração e execução física confirmada.
- **Limites e critérios (itens 11 e 12).**
  - Deficit limitado a zero por baixo.
  - Com o objetivo já atendido, nada é proposto para atingi-lo; uma etapa com outro objetivo continua possível.
  - Precedência explícita dos resultados.
  - Quatro variantes nomeadas e testadas.
  - Datas de aprovação corrigidas para a data local (2026-10-15).
