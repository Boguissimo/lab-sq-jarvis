# Spec — 003-000-jv-v02-honestidade-e-seguranca (JV-V02)

> **Status**: rascunho — aguardando aprovação do desenvolvedor | **Data**: 2026-10-15
> **Entrada**: [ideacao.md](../01-discovery/ideacao.md) (aprovada). Complementa a spec do JV-V01; o que não é dito aqui continua valendo como no V01.
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

**US-07 — Reverter só quando dá (P2).** Como desenvolvedor, quero guardar o arquivo de ajuste "antes" e "depois" e, ao pedir reversão, receber o arquivo a carregar, a receita inversa completa, ou o aviso "reversão não garantida" com o que falta.

### Edge Cases

- Medição "depois" importada antes da previsão registrada: recusada (INV-004 do V01).
- Caso importado com `manifesto.json` sem campo de referência temporal: tratado como incompatível (recusa de fase).
- Caso com vale em uma via **e** ruído alto: prevalece "não dá para concluir".
- Etapa de calibração sem objetivo registrado antes: o "depois" é recusado.
- Reversão pedida numa etapa de calibração cujo arquivo "antes" não foi guardado e com parâmetros incompletos: "reversão não garantida".

## Definições normativas

| Termo | Definição verificável | Estado |
| --- | --- | --- |
| Ruído estimado | desvio padrão (dB) do resíduo entre o nível medido e sua média móvel de 7 pontos da grade, entre 200 Hz e 10 kHz, calculado em cada medição do caso | método fixo; limiares abaixo provisórios |
| Qualidade reprovada por ruído | ruído estimado > **1,5 dB** em qualquer medição usada na análise | **provisório** |
| Aviso de ruído | ruído estimado entre **0,5 dB** e 1,5 dB: análise permitida, incerteza declarada maior | **provisório** |
| Vale individual | numa via, entre 200 Hz e 10 kHz, nível ≥ **10 dB** abaixo da média móvel de 1/3 de oitava, com largura ≤ 1/3 de oitava | **provisório** |
| Mudança de nível da via | diferença > **1,0 dB** entre o nível médio de uma via no "antes" e no "depois", entre 1 e 10 kHz | **provisório** |
| Depois comprometido | (a) a configuração declarada "depois" difere da proposta em algum parâmetro além da variável testada, **ou** (b) há medição individual "depois" e uma via mudou de nível (definição acima) | regra fixa; limiar de (b) provisório |
| Objetivo da etapa de calibração | deficit no cruzamento (soma medida abaixo da soma de potências, no pior ponto da região de sobreposição) ≤ **3 dB** | **provisório** |
| Resultado `objetivo atingido` | deficit "depois" ≤ 3 dB | — |
| Resultado `parcial` | deficit "depois" > 3 dB e redução do deficit ≥ 50 % em relação ao "antes" | — |
| Resultado `não atingido` | redução < 50 % ou piora | — |
| Resultado `inconclusivo` | qualidade reprovada, referência temporal incompatível ou "depois" ausente | — |
| Reversão garantida | existe arquivo "antes" arquivado **ou** todos os valores anteriores dos parâmetros alterados estão registrados | — |
| Valor acessível (SEG-13) | valor que o desenvolvedor lê na ferramenta e informa (origem `declarado`) ou efeito observado em medição (origem `medição`) | — |

## Requirements

### Bloco 1 — Casos e honestidade

| ID | Requisito | Teste |
| --- | --- | --- |
| FR-201 | Gerar de forma determinística REF-001-B e REF-001-N1 a N5, e REF-002-A (etapa de calibração), com a mesma cadeia de arquivos do REF-001-A (`medio`, `tweeter`, `soma-antes`, `soma-depois`, manifesto); semente de ruído fixa e registrada no manifesto | `test_casos.py` |
| FR-202 | Calcular o ruído estimado de cada medição e registrá-lo como cálculo (algoritmo, versão, entradas por hash); reprovar a qualidade acima do limite; declarar o aviso de ruído | `test_calculos.py` |
| FR-203 | Com qualidade reprovada: responder "não dá para concluir", com o motivo e o que falta; não ordenar hipóteses; não propor teste; permitir "solicitar dados adicionais" | `test_sessao.py::test_n2` |
| FR-204 | Detectar vale individual e registrá-lo como indício I-3; com I-3 e sem oposição de fase constante (I-2), ordenar "interferência ou reflexão na via" antes de "polaridade invertida" e não propor teste de polaridade como primeiro passo | `test_regras.py`, `test_sessao.py::test_n1` |
| FR-205 | Sem referência temporal comum: recusar diferença de fase, atraso e soma prevista; mostrar magnitude e soma de potências; dizer o que falta (medir com a mesma referência) | `test_sessao.py::test_n4` |
| FR-206 | Sem I-1 nem I-2 e sem vale individual: informar "sem indício de problema no cruzamento" e oferecer a decisão "nada a alterar" com justificativa pré-preenchida e editável; nada é registrado sem confirmação | `test_sessao.py::test_n5` |
| FR-207 | Emitir `comprometida` quando o "depois" é comprometido (definição normativa); a hipótese não vira `refutada`; indicar o que mudou e propor refazer com uma variável | `test_sessao.py::test_n3` |
| FR-208 | No REF-001-B, emitir `confirmada` com incerteza declarada calculada do ruído estimado e maior que a do REF-001-A; no "depois" com qualidade reprovada, no máximo `inconclusiva` | `test_sessao.py::test_ref001b` |
| FR-209 | Seletor de caso na interface (lista dos casos distribuídos) e, para cada resultado dos FR-203 a FR-208, texto em linguagem simples com origem dos números e aviso de dados simulados | `test_interface.py` |

### Bloco 2 — Regras de segurança

| ID | Requisito | Teste |
| --- | --- | --- |
| FR-210 | Classificar toda recomendação em `sensível — risco crescente`, `sensível — risco decrescente` ou `não sensível` (regras de segurança v0.4.0, seção 1) | `test_seguranca.py` |
| FR-211 | Avaliar SEG-01, 03, 04, 05, 06, 08, 10, 11, 12 e 13 e registrar o resultado de cada regra aplicável (`aprovada`, `bloqueada`, `não verificável`) com a limitação da seção 0; regra sem dado confirmado segue a coluna "sem dado confirmado" das regras | `test_seguranca.py` |
| FR-212 | SEG-02, SEG-07 e SEG-09 não têm fonte para valor ou método: o contrato das regras existe, mas o resultado é sempre `não verificável` e qualquer reforço que dependa delas é **bloqueado**; nenhum modelo de excursão, margem digital ou exposição é calculado neste incremento; a tela diz o que falta (T/S confirmados e Fs; atenuação a montante documentada; critério de exposição com fonte) | `test_seguranca.py` |
| FR-213 | Dados de equipamento `planejado` ou `informado` nunca alimentam regra como confirmados (SEG-12) | `test_seguranca.py` |
| FR-214 | Mostrar os valores provisórios como provisórios na própria recomendação (ex.: "limite provisório de +1,5 dB") | `test_seguranca.py`, `test_interface.py` |
| FR-215 | Mostrar a "Verificação de segurança" em toda recomendação exibida na interface, inclusive a de polaridade (SEG-08, 10, 11 e 12 aplicáveis; as demais, "não se aplica") | `test_interface.py` |
| FR-216 | Aprovação de nível B registrada para recomendação sensível, sem alterar o resultado das regras (aprovação não verifica) | `test_seguranca.py` |

### Bloco 3 — Calibração simulada e configuração

| ID | Requisito | Teste |
| --- | --- | --- |
| FR-217 | Etapa de calibração simulada (REF-002-A): registrar objetivo e limites informados (SEG-13) antes; conjunto de parâmetros antes/depois; resultado conforme a definição normativa; texto sem atribuir a melhora a um ajuste isolado | `test_calibracao.py` |
| FR-218 | Na etapa de calibração, parâmetros sensíveis não acessíveis ficam `não verificado`, com a lista do que não foi conferido e a origem de cada valor conferido | `test_calibracao.py` |
| FR-219 | Arquivar arquivo de ajuste ("antes"/"depois") como arquivo opaco por hash, ligado à configuração (nível `arquivada`), sem ler o conteúdo; sugerir o nome `JV-AAAA-MM-DD-S<sessão>-antes` / `-depois` | `test_configuracao.py` |
| FR-220 | No início da sessão, mostrar a última configuração registrada e pedir confirmação ou outra configuração (`declarada`); o nível `coerente` não existe neste incremento | `test_configuracao.py`, `test_interface.py` |
| FR-221 | Reversão: arquivo "antes" arquivado → indicar qual arquivo carregar; senão, receita inversa só se todos os valores anteriores estiverem registrados; senão, "reversão não garantida" e o que falta | `test_configuracao.py` |
| FR-222 | Estender a rotina de integridade às novas relações (etapa, arquivo de ajuste, resultado de regras) e ao diário | `test_persistencia.py` |

## Invariantes

- INV-201: um resultado nunca é mais conclusivo que a qualidade das medições: qualidade reprovada ⇒ nenhum veredito acima de `inconclusiva` e nenhuma hipótese ordenada. **Teste:** `test_sessao.py::test_qualidade_limita_conclusao`.
- INV-202: `comprometida` nunca é registrada como `refutada` nem `confirmada` da hipótese. **Teste:** `test_sessao.py::test_comprometida_nao_refuta`.
- INV-203: nenhuma recomendação sensível aparece como segura, nem sem a lista de resultados das regras e das limitações; regra `bloqueada` ou `não verificável` nunca vira "segura" por aprovação. **Teste:** `test_seguranca.py::test_aprovacao_nao_verifica`, `test_seguranca.py::test_propriedade_sem_violacao` (recomendações aleatórias com semente fixa: zero violações nas exibidas).
- INV-204: reforço de EQ nunca é recomendado para vale classificado como cancelamento ou interferência (SEG-06). **Teste:** `test_seguranca.py::test_seg06`, `test_sessao.py::test_n1`.
- INV-205: reversão só mostra receita quando o valor anterior de todos os parâmetros alterados está registrado ou há arquivo "antes". **Teste:** `test_configuracao.py::test_reversao_nao_garantida`.
- INV-206: etapa de calibração não produz conclusão causal sobre ajuste isolado. **Teste:** `test_calibracao.py::test_sem_atribuicao_causal`.
- INV-207: arquivo de ajuste guardado não é lido nem alterado; o programa nunca escreve no DSP (SEG-11). **Teste:** `test_configuracao.py::test_arquivo_opaco`, busca no código por escrita ao DSP no QA.
- INV-208: mesmas entradas, mesmos resultados, inclusive nos casos com ruído (semente fixa). **Teste:** `test_casos.py::test_deterministico`.
- INV-209: Core do Arkan intacto. **Teste:** `git diff` das pastas do Core contra a fundação, registrado no QA.
- INV-210: o INV-001 a INV-006 do V01 continuam valendo. **Teste:** suíte do V01 passando sem alteração de asserções.

## Critérios de Sucesso

- **SC-201** — REF-001-N1 a N5 produzem o comportamento da tabela da proposta (seção 7.1) nos cinco casos. **Instrumento:** `test_sessao.py::test_n1` a `test_n5`. **Baseline:** N/A — funcionalidade nova.
- **SC-202** — REF-001-B fecha o percurso com `confirmada` e incerteza declarada maior que a do REF-001-A. **Instrumento:** `test_sessao.py::test_ref001b`. **Baseline:** N/A.
- **SC-203** — Etapa de calibração com os quatro resultados em variantes geradas de REF-002-A. **Instrumento:** `test_calibracao.py`. **Baseline:** N/A.
- **SC-204** — Zero violações em 1 000 recomendações aleatórias (semente fixa) pelas regras SEG implementadas. **Instrumento:** `test_seguranca.py::test_propriedade_sem_violacao`. **Baseline:** N/A.
- **SC-205** — Reversão nos três desfechos (arquivo, receita, não garantida). **Instrumento:** `test_configuracao.py`. **Baseline:** N/A.
- **SC-206** — O desenvolvedor percorre os casos pelo programa no Windows e reconhece a explicação de cada um (G3). **Instrumento:** roteiro `COMO-EXPERIMENTAR.md` atualizado. **Baseline:** JV-V01 no Windows aprovado.
- **SC-207** — Suíte completa (V01 + V02) passando em Linux. **Instrumento:** `python -m pytest`. **Baseline:** 45 testes passando no JV-V01.

## Limites declarados

- Casos simulados ideais ou levemente realistas: não representam o carro (JV-D025).
- Limiares marcados como provisórios nas definições normativas e nos valores SEG: validados só em casos simulados.
- SEG-02, SEG-07 e SEG-09: sem modelo de cálculo (falta fonte); ficam `não verificável` e bloqueiam reforço até haver cadastro do equipamento e fonte.
- Arquivo de ajuste do PC-Tool tratado como opaco; leitura é F019.
- IA continua fora (JV-V03).

## Clarifications

### Sessão 2026-10-15

- **SEG-02, SEG-07 e SEG-09 sem fundamentação.** Decisão do desenvolvedor (opção A, depois de esclarecer): sem modelos simplificados no V02; as três regras resultam sempre `não verificável` e bloqueiam reforço (FR-212). O cálculo entra com o cadastro do equipamento e uma fonte.
- **Detecção de `comprometida`.** Decisão do desenvolvedor: duas vias, qualquer uma basta — configuração declarada "depois" diferente da proposta ou mudança de nível de via acima de 1,0 dB (definição normativa).
