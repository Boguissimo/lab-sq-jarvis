# Spec — 003-000-jv-v02-honestidade-e-seguranca (JV-V02)

> **Status**: aprovada pelo desenvolvedor em 2026-10-15 · **Emenda E1** (revisão externa do plano): **aprovada pelo desenvolvedor em 2026-10-15 (nível B)** · **Emenda E2** (decisões sobre os pontos de aprovação da R1): **aprovada pelo desenvolvedor em 2026-10-15 (nível B)** · **Emenda E3** (revisão adversarial `docs/revisoes/revisao-adversarial-projeto.md`, A01 a A09): **aprovada pelo desenvolvedor em 2026-10-15 (nível B)** | **Data**: 2026-10-15
> **Emenda E4** (2026-10-16; decisões do desenvolvedor sobre as duas divergências de `08-qa/validacao-limiares.md`): **decisões do desenvolvedor registradas em 2026-10-16 (aprovação parcial, com correções); a redação final aguarda conferência e aprovação expressa antes do commit (Princípio VIII)**. Altera o **critério de aceite** do SC-208(a) e (b) e a redação da confirmação de mudança (definições normativas, FR-207, FR-209, INV-215 novo); **não altera o estimador σ̂, nem os limiares técnicos, nem o detector além da exigência de faixa compatível (JV-T222A)**. O SC-208(b) **não é declarado validado** quanto a falsos positivos confirmados. Resultados anteriores em `08-qa/validacao-limiares.md`; ensaio complementar em `08-qa/validacao-limiares-e4.md`.
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

**US-08 — Exercitar recomendações sensíveis (P2, E2).** Como desenvolvedor, quero casos sintéticos próprios em que o Jarvis avalia alterações sensíveis, para ver na prática a aprovação de nível B, o bloqueio pelas regras SEG e a apresentação correta de cada situação na interface.

- (E3) Dado o REF-003-S1 (reforço de EQ de +1 dB, equipamento sintético **confirmado**, dentro dos limites de passo e potência), quando avalio, então vejo "alteração bloqueada — não recomendada" **por SEG-07** (margem digital sem método, FR-212): dado confirmado não libera o que não tem método de verificação. Não há receita nem opção de aprovar.
- (E3) Dado o REF-003-S2 (o mesmo reforço com equipamento `planejado`), quando avalio, então vejo "alteração bloqueada — não recomendada" **por SEG-12** (além da SEG-07), com o que falta, sem receita nem opção de aprovar.
- Dado o REF-003-S3 (corte de EQ com regra sem dado confirmado), quando avalio, então a alteração é admitida como "sensível — risco decrescente", com a lista do que não foi verificado e o aviso de efeitos colaterais, e exige aprovação de nível B.

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
| Condições de aplicação do estimador | (i) grade logarítmica uniforme: razão entre frequências vizinhas constante em ±0,5 %; (ii) densidade ≥ **24 pontos por oitava**; (iii) suavização declarada `nenhuma`. A suavização vem do manifesto (`suavizacao`). (E3) Ausente num **caso do catálogo interno com proveniência verificada** (definição abaixo), vale `nenhuma`, porque o gerador não suaviza. Em qualquer outro arquivo, inclusive um que só declare `simulado: true`, é `desconhecida` | (ii) **provisório** |
| Ruído não estimável | falha em qualquer condição de aplicação. **Não é qualidade aprovada** (INV-212). (E2) **Preserva** as observações descritivas admissíveis com os dados disponíveis: curvas, níveis, sobreposição, soma de potências, vales e indícios, marcados "qualidade não estimada". **Limita** só o que depende da estimativa de qualidade: a incerteza fica "não quantificada"; o veredito do teste fica no máximo `inconclusiva` e o resultado da etapa no máximo `inconclusivo`; as bandas do detector de mudança ficam inconclusivas; nenhuma hipótese é apresentada como confirmada | regra fixa |
| Qualidade reprovada por irregularidade | σ̂ > **1,5 dB** em qualquer medição usada na análise | **provisório — limite candidato**, sujeito à validação (SC-208) |
| Aviso de irregularidade | σ̂ entre **0,5 dB** e 1,5 dB: análise permitida, incerteza declarada maior | **provisório — limite candidato**, sujeito à validação (SC-208) |
| Vale individual | numa via, entre 200 Hz e 10 kHz, nível ≥ **10 dB** abaixo da média móvel de 1/3 de oitava, com largura ≤ 1/3 de oitava | **provisório** |
| Condições de aquisição comparáveis **declaradas** (E1; E3) | para duas medições a comparar (vias no detector; somas "antes" e "depois" no veredito), mesma posição de microfone (`posicao_microfone`), mesmo ganho de entrada (`ganho_entrada_db`) e mesma referência de nível (`referencia_nivel`), todos declarados no manifesto. Campo ausente ou diferente ⇒ não comparáveis. (E3) É **igualdade declarada**, não verificação física: o programa nunca diz que a posição foi conferida. Só nos **casos do catálogo interno com proveniência verificada**, campo ausente vale "idêntico por construção", porque o gerador usa uma única aquisição. Em qualquer outro arquivo, inclusive um que só declare `simulado: true`, ausente ⇒ não comparáveis | regra fixa |
| Caso do catálogo interno com proveniência verificada (E3) | o caso consta em `casos.listar()` **e** o SHA-256 de cada arquivo importado (medições e manifesto) é igual ao do arquivo que o próprio catálogo gera para esse caso. A declaração `simulado: true` sozinha **não** dá essa condição: ela só faz o programa tratar os dados como simulação (aviso e limites), nunca concede presunções. Falha na conferência ⇒ o caso é tratado como arquivo externo | regra fixa |
| Referência temporal declarada compatível (E3) | todas as medições usadas para fase têm `referencia_temporal.tipo` ≠ `nenhuma`, `referencia_temporal.id`, `taxa_amostragem` e `posicao_microfone` **presentes e não vazios** e iguais entre si. Campo ausente ⇒ incompatível (antes, ausência igual em todas passava). A tela diz "referência temporal **declarada** compatível", nunca "verificada". Arquivo importado sem manifesto ⇒ incompatível | regra fixa |
| Repetição do "depois" (E3) | segunda **aquisição independente** individual "depois" da mesma via: outro arquivo, outro registro de medição com identificador próprio e `aquisicao_id` diferente, feita com o microfone retirado e recolocado na mesma posição declarada. Duas cópias do mesmo arquivo (mesmo SHA-256) ou o mesmo `aquisicao_id` não contam como repetição. Serve para separar mudança do DSP de variação de reposicionamento | regra fixa |
| Faixa útil da via (E1) | pontos entre 200 Hz e 10 kHz em que o nível "antes" da via é ≥ (máximo da via nessa faixa − **20 dB**) | **provisório** |
| Detector de mudança da via (E1) — *substitui "mudança de nível da via"* | aplicado a **cada via** que tenha medição individual "antes" e "depois", na faixa útil da via, sobre Δ = nível "depois" − nível "antes": **mudança geral** se \|média de Δ\| > **1,0 dB**; **mudança localizada** se, em alguma banda de 1/3 de oitava (janela deslizante sobre a grade), \|média de Δ na banda\| > max(**1,5 dB**; **3**·σΔ), onde σΔ = √(σ̂²antes + σ̂²depois) / √n e n é o número de pontos da banda | limiares e fator 3 **provisórios** |
| Resultado do detector, por via (E1) | `mudança detectada`: mudança geral ou localizada. `mudança não detectada (resolução: média 1,0 dB; bandas X dB)`: nenhuma das duas, com condições comparáveis e σ̂ estimável nas duas medições; X é o limiar efetivo das bandas, sempre declarado. `verificação inconclusiva`: condições de aquisição não comparáveis, ou σ̂ não estimável sem mudança geral detectada. Nesse caso nenhuma diferença é atribuída a alteração do DSP. Sem medição individual "depois", o detector não roda e a via fica "não verificada". (E3) Com **uma só** medição "depois", `mudança detectada` vale como **indicativa** (pode ser reposicionamento). Ela só vira **confirmada** quando há repetição do "depois" e as duas medições "depois" mostram a mudança, no mesmo sentido, e concordam entre si dentro do limiar das bandas. O σΔ supõe pontos independentes e é usado só como margem provisória; o limiar não é tratado como estatisticamente calibrado. (E3) Mudança **reproduzida** comprova que algo mudou na via, na faixa indicada; **não** comprova qual parâmetro do DSP foi alterado. O programa nunca nomeia o parâmetro a partir da medição; só a configuração declarada nomeia parâmetros | regra fixa |
| Depois comprometido | (a) a configuração declarada "depois" difere da proposta em algum parâmetro além da variável testada, **ou** (b) o detector dá `mudança detectada` **confirmada por repetição** (E3) em alguma via, sendo a variável testada de um tipo que não altera a magnitude da via isolada (polaridade, atraso). Neste incremento, todo teste de diagnóstico é de polaridade | regra fixa; limiares de (b) provisórios |
| Precedência do veredito do teste (E1) | 1º (a) ⇒ `comprometida`, qualquer que seja a qualidade da medição; 2º qualidade "depois" reprovada ou ruído não estimável ⇒ no máximo `inconclusiva`; 3º (b) ⇒ `comprometida`; 3º-A (E3) `mudança detectada` indicativa (sem repetição) ⇒ no máximo `inconclusiva`, com "mudança suspeita; repetir a medição individual 'depois'" (E4: sem afirmar alteração do DSP); 3º-B (E3) somas "antes" e "depois" sem condições de aquisição comparáveis declaradas ⇒ no máximo `inconclusiva`, com "melhora observada, sem confirmação causal"; 4º veredito normal do V01 (`confirmada`/`refutada`/`inconclusiva`). `verificação inconclusiva` ou via "não verificada" não elevam nem rebaixam o veredito, mas aparecem como limitação ("outras alterações não foram verificadas") | regra fixa |
| Quatro afirmações distintas (E4) | O programa e a interface **não tratam como equivalentes**: (1) **mudança acústica suspeita** (indicativa, uma só aquisição); (2) **mudança acústica reproduzida** (confirmada, definição abaixo); (3) **teste comprometido** (`comprometida`: a variável única não está garantida, seja por configuração declarada diferente, seja por mudança reproduzida que a variável testada não explica); (4) **alteração adicional declarada pelo usuário** na configuração. **Nenhuma delas comprova o estado físico do equipamento.** Uma declaração do usuário **registra o que ele afirma**; não prova o que está gravado no DSP (o programa não lê nem escreve no DSP). A medição, por si só, nunca comprova uma alteração no DSP nem identifica a causa. `comprometida` pela via medida significa que o teste não isola a variável, não que o usuário alterou outro parâmetro; `comprometida` pela configuração declarada significa que a **declaração** difere da proposta, não que a diferença foi verificada | regra fixa |
| Mudança indicativa e confirmada (E4) — *explicita e endurece a E3* | **Mudança indicativa**: `mudança detectada` numa só aquisição "depois"; não permite concluir que o teste foi comprometido nem que o DSP foi alterado, e na interface aparece como "mudança suspeita; repetir a medição". **Mudança confirmada**: exige uma **nova aquisição independente** do "depois", com identificação própria (`aquisicao_id` distinto e conteúdo distinto — cópia, reimportação ou nova análise dos mesmos dados nunca confirmam), com condições de aquisição comparáveis declaradas, a mudança **reproduzida no mesmo sentido, dentro do limiar das bandas e em região de frequência compatível** (as faixas de frequência da mudança das duas aquisições têm interseção não vazia). A confirmação comprova que algo mudou na via, na faixa indicada; não identifica o parâmetro. O programa não afirma "alteração adicional do DSP" em nenhuma das duas situações | regra fixa; sem limiar novo |
| Deficit no cruzamento (E1) | max(0; maior valor de (soma de potências − soma medida) na região de sobreposição), em dB | regra fixa |
| Objetivo da etapa de calibração | (E3) nome exibido: **"sem cancelamento acima de 3 dB em relação à soma de potências"**. O deficit não mede alinhamento ótimo: duas vias em quadratura dão deficit 0 sem somar em fase. O programa nunca chama esse resultado de "alinhado" nem de "calibrado". Critério: deficit ≤ **3 dB**. Com deficit "antes" ≤ 3 dB, o objetivo já está atendido e nenhuma alteração é proposta para atingi-lo (E1) | **provisório** |
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
| FR-205 | Sem referência temporal comum: recusar diferença de fase, atraso e soma prevista; mostrar magnitude e soma de potências; dizer o que falta (medir com a mesma referência). (E3) A compatibilidade segue a "referência temporal declarada compatível": campos ausentes ⇒ incompatível; a tela diz "declarada", nunca "verificada" | `test_sessao.py::test_n4`, `test_calculos.py::test_referencia_campos_ausentes` |
| FR-206 | Sem I-1 nem I-2 e sem vale individual: informar "sem indício de problema no cruzamento" e oferecer a decisão "nada a alterar" com justificativa pré-preenchida e editável; nada é registrado sem confirmação | `test_sessao.py::test_n5` |
| FR-207 | (E1) Aceitar medições individuais "depois" das duas vias. Aplicar o detector de mudança a cada via e a regra de precedência do veredito. Emitir `comprometida` quando o "depois" é comprometido; a hipótese não vira `refutada` nem `confirmada`. Indicar o que mudou (parâmetro declarado ou via e faixa da mudança detectada) e propor refazer com uma variável. Mostrar por via o resultado do detector, com a resolução quando for `mudança não detectada`. Sem medições individuais "depois", avaliar só pela configuração declarada e dizer "outras alterações não foram verificadas". (E3) O REF-001-N3 traz o ganho do tweeter +3 dB **não declarado** e duas aquisições independentes "depois" do tweeter, identificadas individualmente (repetição); deve produzir `comprometida`, com o texto "mudança reproduzida no tweeter, na faixa X; a medição não identifica a causa e não comprova alteração no DSP". Mudança só medida e sem repetição dá no máximo `inconclusiva`. (E4) A repetição só confirma com aquisição independente identificada, condições comparáveis e **região de frequência compatível** (definição "Mudança indicativa e confirmada"). O serviço guarda e usa **todas** as medições "depois" de cada via, não só a última | `test_sessao.py::test_n3`, `::test_n3_sem_repeticao_inconclusiva`, `::test_reposicionamento_nao_compromete`, `::test_copia_nao_e_repeticao`, `::test_mudanca_reproduzida_nao_nomeia_parametro`, `::test_repeticao_exige_faixa_compativel`, `test_calculos.py::test_detector_mudanca` |
| FR-208 | No REF-001-B, emitir `confirmada` com incerteza declarada calculada de σ̂ e maior que a do REF-001-A. No "depois" com qualidade reprovada ou ruído não estimável, no máximo `inconclusiva`. (E3) `confirmada` exige somas "antes" e "depois" com condições de aquisição comparáveis declaradas; sem elas, "melhora observada, sem confirmação causal" e no máximo `inconclusiva` | `test_sessao.py::test_ref001b`, `::test_depois_outra_posicao_nao_confirma` |
| FR-209 | Seletor de caso na interface (lista dos casos distribuídos) e, para cada resultado dos FR-203 a FR-208, texto em linguagem simples com origem dos números e aviso de dados simulados. (E4) A mudança indicativa aparece como "mudança suspeita; repetir a medição", sem afirmar alteração adicional do DSP; só a confirmada diz "mudança reproduzida" | `test_interface.py::test_textos_resultados`, `::test_mudanca_suspeita_sem_afirmar_dsp` |

### Bloco 2 — Regras de segurança

| ID | Requisito | Teste |
| --- | --- | --- |
| FR-210 | Classificar toda recomendação em `sensível — risco crescente`, `sensível — risco decrescente` ou `não sensível` (regras de segurança v0.4.0, seção 1) | `test_seguranca.py` |
| FR-211 | Avaliar SEG-01, 03, 04, 05, 06, 08, 10, 11, 12 e 13 e registrar o resultado de cada regra aplicável (`aprovada`, `bloqueada`, `não verificável`) com a limitação da seção 0; regra sem dado confirmado segue a coluna "sem dado confirmado" das regras. (E1) A avaliação **decide a admissibilidade** (definição normativa) **antes** de a recomendação ser registrada ou exibida, inclusive no teste de polaridade herdado do V01, cujo bloco de segurança passa a vir dessa avaliação. Alteração bloqueada fica registrada como "alteração bloqueada — não recomendada", com motivo e o que falta, sem receita executável | `test_seguranca.py`, `test_seguranca.py::test_admissibilidade` |
| FR-212 | SEG-02, SEG-07 e SEG-09 não têm fonte para valor ou método: o contrato das regras existe, mas o resultado é sempre `não verificável` e qualquer reforço que dependa delas é **bloqueado**; nenhum modelo de excursão, margem digital ou exposição é calculado neste incremento; a tela diz o que falta (T/S confirmados e Fs; atenuação a montante documentada; critério de exposição com fonte) | `test_seguranca.py` |
| FR-213 | Dados de equipamento `planejado` ou `informado` nunca alimentam regra como confirmados (SEG-12) | `test_seguranca.py` |
| FR-214 | Mostrar os valores provisórios como provisórios na própria recomendação (ex.: "limite provisório de +1,5 dB") | `test_seguranca.py`, `test_interface.py` |
| FR-215 | Mostrar a "Verificação de segurança" em toda recomendação exibida na interface, inclusive a de polaridade (SEG-08, 10, 11 e 12 aplicáveis; as demais, "não se aplica") | `test_interface.py` |
| FR-223 | (E2) Gerar de forma determinística os casos de segurança: `REF-003-S1` (E3: reforço de EQ +1 dB, equipamento sintético confirmado, dentro dos limites de passo e potência ⇒ **bloqueada por SEG-07**, sem exceção por simulação); `REF-003-S2` (mesmo reforço, equipamento `planejado` ⇒ bloqueada por SEG-12 e SEG-07); `REF-003-S3` (corte de EQ com regra sem dado confirmado ⇒ risco decrescente admitido com aviso, exige aprovação B). O manifesto traz o **equipamento sintético** (com `estado`) e a **alteração candidata**. O serviço submete a alteração à classificação, às regras SEG e à admissibilidade; registra a recomendação ou a alteração bloqueada; exige aprovação B antes de registrar a aplicação. Os casos são identificados como simulação, não alteram os casos de referência existentes e entram no roteiro G3 do bloco 2 | `test_casos.py`, `test_sessao.py::test_s1_s2_s3`, `test_interface.py::test_casos_seguranca` |
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
- INV-214 (E3): presunções que dispensam declaração (suavização `nenhuma`, aquisição idêntica por construção) só valem para caso do catálogo interno com proveniência verificada; `simulado: true` sozinho nunca as concede. **Teste:** `test_casos.py::test_proveniencia_catalogo`, `test_sessao.py::test_simulado_declarado_nao_presume`.
- INV-215 (E4): uma mudança indicativa nunca é tratada como confirmada nem leva a `comprometida`; a confirmação exige aquisição independente identificada, condições comparáveis e região de frequência compatível; a taxa de falsos positivos observada na validação é um registro do domínio simulado, não uma garantia. **Teste:** `test_sessao.py::test_repeticao_exige_faixa_compativel`, `::test_copia_nao_e_repeticao`.
- INV-213 (E2): os casos de referência existentes (REF-001-A e B, N1 a N5, variantes REF-002-A) não mudam por causa dos casos de segurança; o REF-001-A continua byte a byte. **Teste:** `test_casos.py::test_deterministico`, `::test_ref001a_intacto`.
- INV-212 (E1): incerteza desconhecida nunca vira aprovação. "Ruído não estimável" não é qualidade aprovada; `verificação inconclusiva` e via "não verificada" não são "sem mudança"; `mudança não detectada` sempre declara a resolução. **Teste:** `test_calculos.py::test_nao_estimavel_nao_aprova`, `test_sessao.py::test_sem_dados_nao_e_sem_mudanca`.

## Critérios de Sucesso

- **SC-201** — REF-001-N1 a N5 produzem o comportamento da tabela da proposta (seção 7.1) nos cinco casos. **Instrumento:** `test_sessao.py::test_n1` a `test_n5`. **Baseline:** N/A — funcionalidade nova.
- **SC-202** — REF-001-B fecha o percurso com `confirmada` e incerteza declarada maior que a do REF-001-A. **Instrumento:** `test_sessao.py::test_ref001b`. **Baseline:** N/A.
- **SC-203** — Etapa de calibração com os quatro resultados nas variantes `REF-002-A-atingido`, `-parcial`, `-nao-atingido` e `-inconclusivo`, mais os casos-limite: deficit "antes" ≤ 3 dB (nada proposto), deficit negativo limitado a zero, piora e redução de exatamente 50 %. **Instrumento:** `test_calibracao.py`. **Baseline:** N/A.
- **SC-204** — Zero violações em 1 000 recomendações aleatórias (semente fixa) pelas regras SEG implementadas. **Instrumento:** `test_seguranca.py::test_propriedade_sem_violacao`. **Baseline:** N/A.
- **SC-205** — Reversão nos três desfechos (documentada por arquivo, documentada por receita, não documentada), sempre sem afirmar restauração física. **Instrumento:** `test_configuracao.py`. **Baseline:** N/A.
- **SC-206** — O desenvolvedor percorre os casos pelo programa no Windows e reconhece a explicação de cada um (G3). **Instrumento:** roteiro `COMO-EXPERIMENTAR.md` atualizado. **Baseline:** JV-V01 no Windows aprovado.
- **SC-207** — Suíte completa (V01 + V02) passando em Linux, sem alterar asserções do V01. **Instrumento:** `python -m pytest`. **Baseline:** 45 testes passando no JV-V01.
- **SC-209** (E2) — Os três casos REF-003-S produzem bloqueio por SEG-07 com equipamento confirmado (S1, E3), bloqueio por SEG-12 e SEG-07 (S2) e admissão de risco decrescente com aviso e aprovação B (S3), cada bloqueio com a regra e o que falta, nos testes automatizados e no programa no Windows. **Instrumento:** `test_sessao.py::test_s1_s2_s3`, `test_interface.py::test_casos_seguranca`, roteiro G3 do bloco 2 em `COMO-EXPERIMENTAR.md`. **Baseline:** N/A.
- **SC-208** (E1; E3) — **Alcance (E3): comprova só o desempenho no domínio simulado; não é validação acústica para o carro**, e nenhum texto do programa ou do QA pode afirmar o contrário. Além das perturbações do próprio gerador, inclui oráculos independentes do gerador (vetores analíticos calculados à mão: identidade de quadratura, LR4 no cruzamento, atraso puro), testes metamórficos (ganho global não muda σ̂ nem o detector; trocar as vias não muda o deficit), ruído correlacionado entre pontos, múltiplas reflexões e suavização. Fora do domínio, registra falsos positivos e falsos negativos sem ajustar limiar. Validação dos limiares provisórios por varredura, com falsos positivos e falsos negativos registrados em `08-qa/validacao-limiares.md`.

  **(a) σ̂ — critério de aceite revisto pela E4.** O critério anterior (por realização) era ambíguo e, medido, não é atendido por 22 de 1 400 realizações (1,6 %); a tolerância original **não é ampliada**. O critério passa a ser estatístico:
  - Sem ruído (os quatro arquivos do REF-001-A, reflexões e cancelamentos): σ̂ ≤ 0,05 dB (inalterado).
  - Com ruído conhecido, isolado ou combinado com vales: o **viés médio assinado** de cada cenário × nível de σ fica dentro de 15 % de σ + 0,05 dB. O relatório apresenta também erro absoluto médio, desvio-padrão, percentis (1, 5, 25, 50, 75, 95, 99) e a **proporção de realizações fora da tolerância original**, com a lista dessas realizações, sua distribuição por nível de σ e por cenário e a análise de erro sistemático. A proporção e a dispersão são **declaradas e avaliadas, não são critério de aprovação**: não se fixa agora limite numérico de dispersão com base nesta amostra, e o resultado **não** é apresentado como aprovação automática da precisão individual do estimador (E4).
  - Varredura de σ logo abaixo e logo acima de 0,5 e 1,5 dB, registrando **falsas aprovações e falsas reprovações de qualidade** (classe pelo σ̂ contra classe pelo σ injetado). A classificação perto dos limites é declarada como probabilística.
  - Curvas suavizadas: "não estimável", nunca aprovadas (inalterado).
  - *Texto anterior (E1/E3), substituído:* "Ruído conhecido, isolado ou combinado com vales: |σ̂ − σ injetado| ≤ 15 % de σ + 0,05 dB." Resultado da validação anterior preservado em `validacao-limiares.md`.

  **(b) Detector de mudança — revisto pela E4.** O critério original ("zero falsos positivos em 'só polaridade' até σ = 1,5 dB") **não é atendido** e **não é declarado validado**. A E4 separa três planos; nenhum limiar foi alterado:

  *Desempenho observado (domínio simulado; N = 1 000 sementes por linha, em `validacao-limiares-e4.md`; ensaio original: 20/200 indicativas em σ = 1,5 dB):*
  - "Só polaridade" com σ = 0,5 e 1,0 dB: 0/1 000 indicativas e 0/1 000 confirmadas.
  - σ = 1,5 dB: **87/1 000 indicativas, 12/1 000 confirmadas e 10/1 000 confirmadas com faixa compatível**.
  - σ = 2,0 dB: 105/1 000, 14/1 000 e 12/1 000.
  - Falsos negativos e custo: confirmadas em 300/300 nos cenários de ganho (±1,5 e ±3 dB), no N3 e no PEQ +3 dB Q 2; 293/300 no PEQ −3 dB Q 4 com σ = 1,5 dB. Com σ = 1,5 dB cerca de 17 % das sessões teriam ao menos um alarme indicativo.

  *Critério de aceitação (o que o V02 exige):*
  - Separar **indicativa** de **confirmada** (definição normativa "Mudança indicativa e confirmada"); só a confirmada pode levar a `comprometida`.
  - A confirmação exige aquisição independente identificada, condições comparáveis declaradas, mesmo sentido, concordância dentro do limiar das bandas e faixa de frequência compatível (JV-T222A); a interface diz "mudança suspeita; repetir a medição" para a indicativa (JV-T222B).
  - Os números acima (com N, contagens e limitações) permanecem registrados; detecção confirmada registrada para mudanças reais (ganho ±1,5 e ±3 dB, deslocamento de corte, filtros estreitos Q 2 a 4 de ±3 dB, N3); posição diferente ⇒ `verificação inconclusiva`.
  - Registrar no G3 e no uso real quantas repetições o detector pede em condições normais.
  - **Nenhum limite de taxa de falsos positivos é adotado como critério de aprovação nesta emenda.**

  *Limitação conhecida, não resolvida:*
  - Em σ = 1,5 dB **permanecem falsos positivos confirmados** (12/1 000; 10/1 000 com faixa compatível). O detector **não está validado** nesse ponto.
  - Causa: as aquisições "depois" são comparadas com o **mesmo "antes"**, que compartilha o erro da medição de referência; a repetição **não** fornece confirmações estatisticamente independentes.
  - **Limitação técnica da confirmação (E4; algoritmo não redesenhado neste incremento):** a "faixa compatível" exige apenas **interseção não vazia** entre as faixas de frequência da mudança das duas aquisições (qualquer sobreposição, ainda que mínima; uma "mudança geral" usa a faixa útil inteira e cruza com qualquer outra). O serviço avalia **somente as duas primeiras detecções positivas** de cada via, na ordem de importação, e não todos os pares. Isso **não demonstra**, por si só, que a diferença ocorreu na mesma região fisicamente relevante.
  - Um futuro limite admissível de falsos positivos deverá ser **justificado e testado independentemente**, nunca escolhido para acomodar esta bateria. Redesenhar o detector (por exemplo, repetir também o "antes") **fica fora do V02**, para validação posterior. σ̂, fator 3 e os demais limiares permanecem até haver decisão normativa fundamentada.
  - *Texto anterior (E1/E3), substituído:* "Zero falsos positivos em 'só polaridade' até σ = 1,5 dB." Resultado da validação anterior preservado em `validacao-limiares.md`.

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
- (E3) Posição, ganho, nível e referência temporal são **declarados** pelo usuário ou pelo manifesto; o programa não os verifica fisicamente.
- (E3) O deficit no cruzamento mede cancelamento em relação à soma de potências, não alinhamento ótimo nem resposta desejável.
- (E3) Toda validação do V02 vale no domínio simulado; não é validação diagnóstica no veículo. A comparação de esforço no G3 usa dados sintéticos e não indica vantagem na calibração do carro.
- (E4) **Limitação técnica da confirmação de faixa:** só interseção não vazia, e só as duas primeiras detecções positivas por via; não demonstra que a diferença ocorreu na mesma região fisicamente relevante.
- (E4) **Limitação conhecida:** o detector mantém falsos positivos confirmados em σ = 1,5 dB (12/1 000) e as confirmações compartilham o mesmo "antes"; o SC-208(b) não está validado quanto a isso.
- (E4) As taxas de falso positivo e de falso negativo do detector, e as taxas de falsa aprovação e falsa reprovação de qualidade, são medidas num domínio simulado com ruído gaussiano independente e amostras finitas (1 000 e 300 sementes); "0 em 1 000" não é "zero". Nenhuma taxa é garantia nem vale para o carro. O estimador σ̂ tem viés positivo leve na presença de estrutura espectral.
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

### Sessão 2026-10-15 — Emenda E2 (pontos para aprovação da R1)

Decisões do desenvolvedor sobre os encaminhamentos listados no fim do plano R1, todos aceitos:

- **Ruído não estimável.** Preservar as observações descritivas admissíveis; limitar só as conclusões que dependem da estimativa de qualidade (definição normativa revista).
- **Fixture do banco V01.** Gerada pelo V01 original (`main@389e580`), só com dados sintéticos, versionada e mantida como teste de regressão permanente da migração (plano, ADR-207).
- **Lacuna de segurança.** Acrescentar casos sintéticos específicos (REF-003-S1 a S3; US-08, FR-223, SC-209) que exercitam recomendação sensível com aprovação de nível B, bloqueio pelas regras SEG e apresentação na interface, nos testes automatizados e no roteiro G3 do Windows.
- **Casos de referência existentes** permanecem inalterados (INV-213).

### Sessão 2026-10-15 — Emenda E3 (revisão adversarial do projeto)

Origem: `docs/revisoes/revisao-adversarial-projeto.md`. O agente conferiu os achados: A02, A04 e A06 reproduzidos no código do V01; A01 e A09 confirmados nos textos; A08 é identidade matemática. O desenvolvedor aceitou as posições propostas para A01 a A09.

- **A01 (crítico).** O REF-003-S1 da E2 exigia admitir um reforço que a SEG-07 bloqueia; foi um erro de redação do agente. Opção (a): S1 passa a ser reforço **bloqueado por SEG-07** mesmo com equipamento confirmado; S2 bloqueado por SEG-12; S3 continua como corte admitido com aprovação B. Nenhuma exceção de simulação; as regras canônicas não mudam.
- **A02.** "Referência temporal declarada compatível": campos obrigatórios presentes e iguais; sempre dita como declarada, nunca verificada.
- **A03.** `confirmada` exige somas "antes" e "depois" com aquisição comparável declarada; senão, "melhora observada, sem confirmação causal" e no máximo `inconclusiva`. Só nos casos do catálogo interno com proveniência verificada (caso listado e hashes iguais aos gerados), ausência vale "idêntico por construção"; `simulado: true` sozinho não basta (ajuste do desenvolvedor). INV-210 preservado.
- **A04 e A06.** Defeitos de implementação do V01, sem mudança de spec. São corrigidos na fundação do V02 (plano, ADR-212).
- **A05.** O SC-208 declara que vale só no domínio simulado e ganha oráculos independentes, testes metamórficos e ruído correlacionado. Nenhuma alegação de validade para o carro.
- **A07.** A comparabilidade é declarada. Mudança detectada com uma só medição "depois" é indicativa e leva no máximo a `inconclusiva`; `comprometida` por medição exige repetição. O N3 passa a trazer a repetição como aquisições independentes e identificadas, e o serviço suporta várias medições "depois" da mesma via. Mudança reproduzida não comprova qual parâmetro foi alterado (ajuste do desenvolvedor).
- **A08.** O objetivo da etapa passa a se chamar "sem cancelamento acima de 3 dB em relação à soma de potências"; nunca "alinhado" nem "calibrado".
- **A09.** Deslizes de texto do plano corrigidos. Ajuste do desenvolvedor: duas avaliações separadas.
  - **(i) Esforço operacional no G3 do V02**, com dados sintéticos: tempo e passos de 2 ou 3 tarefas, Jarvis contra REW + planilha. Mede só o custo do fluxo, não a utilidade.
  - **(ii) Utilidade real (VP-10)**, em incremento com medições reais, fora do V02.

  Nenhum resultado do V02 é apresentado como vantagem na calibração do carro. A spec não muda por isso.

### Sessão 2026-10-16 — Emenda E4 (divergências do SC-208 antes do G3 do bloco 1) — *decisões do desenvolvedor; redação final aguarda conferência*

Origem: `08-qa/validacao-limiares.md` (JV-T221) e `08-qa/validacao-limiares-e4.md`. Decisões do desenvolvedor sobre os resultados complementares:

- **SC-208(a) — aprovado.** Viés médio, erro absoluto, dispersão, percentis e proporção fora da tolerância original; 22/1 400 e demais dados preservados. **Sem limite numérico adicional de dispersão** com base nesta amostra; a dispersão é declarada e avaliada, sem valer como aprovação automática da precisão individual.
- **SC-208(b) — aprovado parcialmente, com correção.** Aprovadas a separação indicativa × confirmada, as aquisições independentes e a faixa de frequência compatível. **Não aprovada** a troca da meta "zero até σ = 1,5 dB" por "zero até σ = 1,0 dB" como solução: os resultados em σ = 1,5 dB (87/1 000, 12/1 000, 10/1 000) ficam como **limitação conhecida**, sem declarar validado o que mantém falsos positivos confirmados. O SC distingue desempenho observado, critério de aceitação e limitação não resolvida. Um futuro limite de falsos positivos será justificado e testado de forma independente.
- **JV-T222A e JV-T222B — implementação aprovada.** Verificação da faixa compatível e apresentação da indicativa, mantendo a distinção entre alteração acústica observada, alteração declarada pelo usuário e alteração comprovada no DSP (que o programa nunca estabelece). O V02 **não** é ampliado para redesenhar o detector.
- **Não alterado:** σ̂, fator 3, limiares 1,0/1,5/0,5, precedência do veredito (exceto o texto da indicativa), N3 ⇒ `comprometida`.

### Sessão 2026-10-17 — Patch do P1 (origem declarada; JV-D046) — *aprovado por Fabrício, Nível B*

Alternativa A: a origem declarada do manifesto é um registro primário `declaracao` (prefixo `L`), um por manifesto, com snapshot de `equipamento` e `alteracao_candidata` e hash do manifesto no cofre. **Só `calculo` deriva dele.** Reflexo estritamente necessário em FR-223 e INV-216; nada mais da spec muda.

- **FR-223 (nota):** a avaliação de segurança dos casos REF-003-S, quando implementada pela JV-T228, deriva da `declaracao` da sessão e **nunca** de uma medição que não usou.
- **INV-216 (P1 0.5.0):** a `declaracao` não tem origens, tem a marca `declarado`, referencia o manifesto no cofre com hash conferido, tem snapshot igual ao conteúdo desse manifesto, fonte coerente com o caso da sessão, e só `calculo` aponta para ela. Declaração não é medição nem confirma o estado físico do equipamento. **Teste:** `test_persistencia.py::test_declaracao_*`, `test_sessao.py::test_importar_caso_com_campos_declarados_gera_uma_declaracao`.
- **Preservados:** INV-211 (sem reavaliação nem declaração retroativa) e INV-213 (casos existentes inalterados).

### Sessão 2026-10-17 — JV-T228: alteração candidata (JV-D047) — *aprovado por Fabrício, Nível B*

- **D1:** SC-209 é lido pela `seguranca.admissibilidade` existente (crescente sem dado confirmado ou `não verificável` ⇒ bloqueada; decrescente `não verificável` ⇒ admitida com aviso e aprovação B; `bloqueada` sempre bloqueia).
- **D2/D3/D4:** rótulo `alteração candidata`; percurso do S3 termina na aplicação declarada, sessão aberta, sem veredito e sem passo 5; EQ ausente só entra com a premissa declarada `de = 0 dB`, senão recusa; `estado()` com `avaliacao_seguranca` e `aprovacao` aditivos e sem curva de previsão.
- **D5 (FR-223):** a potência não é verificada pelas regras disponíveis; **nunca** "dentro do limite" por manifesto, simulação ou aprovação.
- **Teste:** `test_sessao.py::test_s1_s2_s3` e `test_candidata_*`, `test_s3_*`.
