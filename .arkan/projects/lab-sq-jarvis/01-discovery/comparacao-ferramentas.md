# Comparação com Ferramentas Existentes — Lab SQ Jarvis

> **Data**: 2026-10-15 | **Estado**: revisão pedida pelo desenvolvedor (JV-D018); substitui as seções
> 2 e 3 do [`diagnostico-inicial.md`](diagnostico-inicial.md), que afirmavam que “nenhuma ferramenta
> conecta medições, ajustes, orientação e histórico” — afirmação **retirada** por não se sustentar.
> **Pergunta central**: quanto essas ferramentas ajudam quem ainda está aprendendo, e o que o Jarvis
> acrescentaria ao uso do desenvolvedor? O projeto **não** depende de ser inédito.

## Como ler as tabelas

| Rótulo | Significado |
| --- | --- |
| **Documentado** | descrito em manual, ajuda ou base de conhecimento oficial do fabricante |
| **Anunciado** | descrito em página comercial, blog ou vídeo do próprio fabricante, sem detalhe técnico verificável |
| **Relato** | descrito por usuários em fórum; não é fonte oficial |
| **Testado** | executado por nós. **Nenhuma** função foi testada: os programas não estão disponíveis neste ambiente |

**Limitação da pesquisa**: os sites dos fabricantes estavam bloqueados pela rede do ambiente de
desenvolvimento; o conteúdo veio de mecanismo de busca, que resume as páginas. Antes de qualquer
decisão que dependa de um detalhe, o desenvolvedor deve conferir a página citada. As fontes estão em
[`fontes.md`](fontes.md) (`JV-S014` a `JV-S027`).

Siglas: **REW** — Room EQ Wizard; **DSP** — processador digital de sinais; **EQ** — equalização;
**RTA** — analisador em tempo real; **API** — interface de programação; **ATM** — medição automática
de tempo (Audiotec Fischer); **TA** — alinhamento temporal.

---

## 1. REW (Room EQ Wizard)

| Capacidade | Classificação | Observação |
| --- | --- | --- |
| Medição por varredura, RTA, fase, atraso de grupo, impulso, distorção | Documentado | núcleo do programa |
| Cálculo de filtros paramétricos para aproximar a resposta de uma curva-alvo (“Match response to target”), com faixa de ajuste e filtros que podem ser travados | Documentado (JV-S014) | o próprio manual recomenda limitar os filtros a baixas frequências (≈ abaixo de 200 Hz), salvo compensação de característica geral do alto-falante |
| Ferramenta de alinhamento (soma de duas medições, atraso e polaridade) | Documentado | disponibilidade por versão/licença com relatos divergentes [dúvida] |
| API local (porta 4735) para ler medições e, com licença Pro, disparar medições | Documentado (JV-S001, JV-S003) | — |
| Testado por nós | — | não |

**Para quem aprende**: muito poderoso e muito exigente. Calcula, mas não diz o que medir, em que
ordem ajustar, nem por que uma curva está como está. Não conhece o carro, os alto-falantes nem o
estado do DSP. O histórico são arquivos e anotações.

## 2. HELIX DSP PC-Tool (Audiotec Fischer)

| Capacidade | Classificação | Observação |
| --- | --- | --- |
| **TuneEQ**: correção automática da resposta a partir de uma medição com média espacial (resolução ≥ 1/6 de oitava) por canal ou par de canais, rumo a uma curva de referência livre | Documentado (JV-S005, JV-S016) | PC-Tool 5 em diante |
| **Tune To Target**: ajuste automático a qualquer curva-alvo, inclusive ganho; TuneEQ multibanda também na entrada | Anunciado (JV-S008) | PC-Tool 6; detalhes técnicos não encontrados |
| **ATM**: mede automaticamente o atraso necessário por canal, considerando sistemas passivos | Documentado (JV-S015) | “funciona com todos os aparelhos configuráveis pelo PC-Tool”; exige microfone e interface de medição (por exemplo, AMI); **qual hardware de medição é obrigatório por versão** ficou sem resposta [dúvida] |
| AISA: detecção e compensação de EQ, all-pass e atraso de fábrica na entrada | Anunciado (JV-S008) | PC-Tool 6 |
| Guia de ajuste do fabricante: processo iterativo; não “encher” vales estreitos (distorção e ruído); cuidado com reforços acima de ≈ 4 dB | Documentado (JV-S017) | guia escrito para versões antigas; pode estar desatualizado |
| Importar arquivos de ajuste antigos (v5) no PC-Tool 6 | Relato (JV-S010) | relatos contraditórios [dúvida] |
| Testado por nós | — | não |

**Para quem aprende**: automatiza bem EQ e atrasos **dentro** do HELIX e dá conselhos gerais. Não
explica a causa de um problema específico, não registra experimentos nem liga a percepção às
medições. O histórico são os arquivos de ajuste salvos.

## 3. Flat Liner Tuning

| Capacidade | Classificação | Observação |
| --- | --- | --- |
| Fluxo guiado sobre o REW: descrever o sistema → medir → gerar ajuste → carregar no DSP | Anunciado (JV-S018, JV-S019) | é a ferramenta **mais próxima** do que o Jarvis propõe |
| Usa a API local do REW para capturar medições | Anunciado | — |
| Crossovers (passa-altas, passa-baixas, passa-faixa) para 2 vias, 3 vias, traseiro e subwoofer | Anunciado | — |
| EQ à curva-alvo a partir de medição RTA | Anunciado | — |
| Alinhamento temporal calculado pela **distância física** de cada alto-falante | Anunciado | não por medição acústica |
| Varredura de verificação final comparada à curva-alvo, com sugestão de ajustes | Anunciado | o pedido do desenvolvedor menciona “relatórios”; não encontrei descrição oficial do relatório [dúvida] |
| Carregar o EQ gerado no HELIX (EQ, não a configuração completa); copiar e colar filtros | Anunciado (JV-S019) | escrita no DSP **[dúvida: mecanismo não documentado]** |
| Dados locais, sem nuvem | Anunciado | — |
| Plataforma | **Divergência**: a página do produto cita Windows e macOS; a página de download só oferece instalador Windows | [dúvida registrada] |
| Licença | US$ 39,99 (perpétua, um assento); versão Pro anual US$ 299,99; sessão remota com pessoa | Anunciado | preços via busca, a confirmar |
| Testado por nós | — | não |

**Para quem aprende**: provavelmente a que mais ajuda, porque dá **ordem** ao trabalho. Pelo que é
anunciado, o foco é chegar à curva-alvo; não encontrei descrição de explicação de causas, de
experimentos de uma variável ou de registro de percepção. É barata o bastante para ser **testada
pelo desenvolvedor** como referência de comparação (ver JV-D018).

## 4. Tuning Labs

| Capacidade | Classificação | Observação |
| --- | --- | --- |
| “Auto-Tune” em 6 fases: recebe arquivo de RTA (do REW ou do celular) e gera EQ paramétrico em ≈ 60 s; modos automático e semiautomático; checagem de risco de clipping, limites de ganho e artefatos de fase antes de aplicar | Anunciado (JV-S021, JV-S022) | blog e guias do fabricante |
| 11 ferramentas com IA, incluindo recomendação de crossover | Anunciado | — |
| Biblioteca de mais de 19 000 produtos; ferramentas no navegador; IA exige internet; uso offline por 30 dias | Anunciado (JV-S020) | — |
| Edições Enthusiast, Shop Small, Shop Large; gestão de oficina, histórico de cliente e veículo nas edições de oficina | Anunciado (JV-S020) | foco declarado em oficinas |
| **Divergência entre páginas**: uma página apresenta o copiloto de IA como futuro (“imagine um copiloto de IA posicionando cada filtro”), outras descrevem o Auto-Tune como existente | — | [dúvida registrada] |
| Quais DSPs são suportados e como os filtros chegam ao DSP | não encontrado | [dúvida] |
| Testado por nós | — | não |

**Para quem aprende**: promete exatamente “orientação com IA”. Não encontrei documentação sobre
como a IA chega às recomendações, nem sobre a separação entre cálculo e interpretação.

## 5. Audison ACCORDO (bit Drive)

| Capacidade | Classificação | Observação |
| --- | --- | --- |
| Ajuste automático de EQ de saída, atrasos e níveis, buscando a resposta-alvo “com bom desempenho de fase” | Documentado (JV-S023, JV-S024) | algoritmo proprietário |
| ACCORDO 2.0 (bit Drive 3.0/3.1): mede o ruído de fundo e ajusta o nível do sinal de teste por alto-falante | Anunciado (JV-S025) | — |
| Microfone USB de medição (até 24 bits) ou sistema bit Tune | Documentado (JV-S024) | — |
| Compatível só com processadores e amplificadores Audison “bit” listados | Documentado (JV-S024) | **não se aplica a um HELIX** |
| **Divergência**: o FAQ do ACCORDO para bit Drive 2.0 descreve um “Nível Três” (dianteiro esquerdo, direito e sub separados); outras páginas descrevem só dois níveis | — | [dúvida registrada] |
| Testado por nós | — | não |

**Para quem aprende**: útil para quem tem Audison; fora do ecossistema do desenvolvedor.

---

## 6. Síntese

| Necessidade de quem aprende | REW | PC-Tool | Flat Liner | Tuning Labs | ACCORDO |
| --- | --- | --- | --- | --- | --- |
| Medir com qualidade | sim | parcial (RTA, AMI) | via REW | via arquivo | sim |
| Calcular EQ / atrasos | sim | sim (TuneEQ, ATM) | sim | sim | sim |
| Ordem de trabalho guiada | não | parcial | **sim** | sim (anunciado) | sim (níveis) |
| Explicar a causa de um problema específico | não | não | não encontrado | não encontrado | não encontrado |
| Experimento de uma variável com previsão e veredito | não | não | não encontrado | não encontrado | não |
| Registrar percepção antes/depois | não | não | não encontrado | não encontrado | não |
| Histórico de sessões e aprendizado sobre o próprio carro | arquivos | arquivos de ajuste | não encontrado | sim, nas edições de oficina | não encontrado |
| Funciona com HELIX | sim (manual) | sim | sim (EQ) | [dúvida] | não |

“Não encontrado” significa que a documentação acessível não descreve a função — **não** que ela não
exista.

## 7. O que o Jarvis acrescentaria ao uso do desenvolvedor

Sem pretensão de ineditismo, o Jarvis se justifica pelo conjunto, aplicado a um carro e a uma
pessoa:

1. **Explicar o porquê**: ligar o que se percebe e o que se mede a mecanismos físicos (cancelamento,
   atraso, reflexão, modo do habitáculo, corte inadequado), ensinando durante o ajuste.
2. **Testar em vez de tentar**: uma alteração por vez, com previsão antes e veredito depois,
   inclusive “inconclusivo” e “comprometido”.
3. **Lembrar entre sessões**: o que foi tentado, o que funcionou, quais configurações existiram e o
   que o desenvolvedor ouviu antes e depois.
4. **Conferir contra o próprio equipamento**: limites e fichas técnicas do Focus, com dados
   confirmados.
5. **Conviver com as ferramentas atuais**: o REW mede, o PC-Tool aplica (inclusive TuneEQ e ATM,
   quando fizer sentido), o Jarvis orienta e registra.

**Recomendação**: antes ou durante o Marco 2, o desenvolvedor faz uma sessão com o Flat Liner (ou
com TuneEQ/ATM) como referência. Isso preenche a coluna “Testado” e mostra, na prática, o que o
Jarvis precisa fazer melhor para valer o esforço.
