# Comparação com Ferramentas Existentes — Lab SQ Jarvis

> **Data**: 2026-10-15 | **Estado**: revisão pedida pelo desenvolvedor (JV-D018); substitui as seções
> 2 e 3 do [`diagnostico-inicial.md`](diagnostico-inicial.md), que afirmavam que “nenhuma ferramenta
> conecta medições, ajustes, orientação e histórico” — afirmação **retirada** por não se sustentar.
> **Revisão 3 (JV-D036)**: relatórios do Flat Liner e FAQ do Tuning Labs incluídos; “não encontrado” ou
> “não verificado” onde a pesquisa foi limitada — nunca afirmação de ausência; testar outra ferramenta
> é opcional.
> **Pergunta central**: quanto essas ferramentas ajudam quem ainda está aprendendo, e o que o Jarvis
> acrescentaria ao uso do desenvolvedor? O projeto **não** depende de ser inédito.

## Como ler as tabelas

| Rótulo | Significado |
| --- | --- |
| **Documentado** | descrito em manual, ajuda ou base de conhecimento oficial do fabricante |
| **Anunciado** | descrito em página comercial, blog ou vídeo do próprio fabricante, sem detalhe técnico verificável |
| **Relato** | descrito por usuários em fórum; não é fonte oficial |
| **Testado** | executado por nós. **Nenhuma** função foi testada: os programas não estão disponíveis neste ambiente |
| **Não encontrado** | a documentação acessível não descreve a função — **não** significa que ela não exista |
| **Não verificado** | há indício, mas não foi possível confirmar |

**Limitação da pesquisa**: os sites dos fabricantes estavam bloqueados pela rede do ambiente de
desenvolvimento; o conteúdo veio de mecanismo de busca, que resume as páginas. Antes de qualquer
decisão que dependa de um detalhe, o desenvolvedor deve conferir a página citada. As fontes estão em
[`fontes.md`](fontes.md) (`JV-S014` a `JV-S029`).

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

**Para quem aprende**: muito poderoso e muito exigente. Calcula; na documentação consultada não
encontrei orientação sobre o que medir, em que ordem ajustar ou por que uma curva está como está, nem
cadastro do carro, dos alto-falantes ou do estado do DSP. O histórico são arquivos de medição e
anotações.

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

**Para quem aprende**: automatiza EQ e atrasos **dentro** do HELIX e dá conselhos gerais. Na
documentação consultada não encontrei explicação de causas de problemas específicos, registro de
experimentos nem ligação entre percepção e medições. O histórico são os arquivos de ajuste salvos.

## 3. Flat Liner Tuning

| Capacidade | Classificação | Observação |
| --- | --- | --- |
| Fluxo guiado sobre o REW: descrever o sistema → medir → gerar ajuste → carregar no DSP | Anunciado (JV-S018, JV-S019) | é a ferramenta **mais próxima** do que o Jarvis propõe |
| Usa a API local do REW para capturar medições | Anunciado | — |
| Crossovers (passa-altas, passa-baixas, passa-faixa) para 2 vias, 3 vias, traseiro e subwoofer | Anunciado | — |
| EQ à curva-alvo a partir de medição RTA | Anunciado | — |
| Alinhamento temporal calculado pela **distância física** de cada alto-falante | Anunciado | não por medição acústica |
| Varredura de verificação final comparada à curva-alvo, com sugestão de ajustes | Anunciado | — |
| **Relatório final** de cada ajuste: medições iniciais, curva-alvo, EQ aplicado, níveis e alinhamento temporal, com **exemplo em PDF** na página do produto | Anunciado (JV-S028) | corrigido na revisão 3; o exemplo não pôde ser aberto neste ambiente |
| Carregar o EQ gerado no HELIX (EQ, não a configuração completa); copiar e colar filtros | Anunciado (JV-S019) | escrita no DSP **[dúvida: mecanismo não documentado]** |
| Dados locais, sem nuvem | Anunciado | — |
| Plataforma | **Divergência**: a página do produto cita Windows e macOS; a página de download só oferece instalador Windows | [dúvida registrada] |
| Licença | US$ 39,99 (perpétua, um assento); versão Pro anual US$ 299,99; sessão remota com pessoa | Anunciado | preços via busca, a confirmar |
| Testado por nós | — | não |

**Para quem aprende**: provavelmente a que mais ajuda, porque dá **ordem** ao trabalho e documenta
cada ajuste num relatório. Pelo que é anunciado, o foco é chegar à curva-alvo; não encontrei
descrição de explicação de causas, de testes de uma variável ou de registro de percepção. Testá-la
pode ser útil, mas é **opcional** (JV-D036).

## 4. Tuning Labs

| Capacidade | Classificação | Observação |
| --- | --- | --- |
| “Auto-Tune” em 6 fases: recebe arquivo de RTA (do REW ou do celular) e gera EQ paramétrico em ≈ 60 s; modos automático e semiautomático; checagem de risco de clipping, limites de ganho e artefatos de fase antes de aplicar | Anunciado (JV-S021, JV-S022) | blog e guias do fabricante |
| 11 ferramentas com IA, incluindo recomendação de crossover | Anunciado | — |
| Biblioteca de mais de 19 000 produtos; ferramentas no navegador; IA exige internet; uso offline por 30 dias | Anunciado (JV-S020) | — |
| Edições Enthusiast, Shop Small, Shop Large; gestão de oficina, histórico de cliente e veículo nas edições de oficina | Anunciado (JV-S020) | foco declarado em oficinas |
| **Divergência entre páginas**: uma página apresenta o copiloto de IA como futuro (“imagine um copiloto de IA posicionando cada filtro”), outras descrevem o Auto-Tune como existente | — | [dúvida registrada] |
| Processadores suportados citados no FAQ: EDSP31-610, EDSP31-68, Dayton Audio DSP-408, BLAM LA808 e outros da família YDW; conexões por WebHID, ponte nativa e BLE (Bluetooth de baixo consumo) | Anunciado (JV-S029) | o FAQ não diz qual conexão serve a qual processador |
| Lista de marcas da página principal (Audison, Helix, Arc Audio, JL Audio, Audiofrog, AudioControl, Focal, Morel, Hertz) | Anunciado | é o **catálogo** de produtos, não lista de compatibilidade |
| Suporte ao HELIX | **não verificado** | nenhuma fonte acessível afirma compatibilidade |
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
| Ordem de trabalho guiada | não encontrado | parcial | **sim** (anunciado) | sim (anunciado) | sim (níveis) |
| Explicar a causa de um problema específico | não encontrado | não encontrado | não encontrado | não encontrado | não encontrado |
| Teste de uma variável com previsão e veredito | não encontrado | não encontrado | não encontrado | não encontrado | não encontrado |
| Registrar percepção antes/depois | não encontrado | não encontrado | não encontrado | não encontrado | não encontrado |
| Registro do que foi feito | arquivos de medição | arquivos de ajuste | relatório por ajuste (anunciado) | histórico de cliente e veículo nas edições de oficina (anunciado) | não encontrado |
| Funciona com HELIX | sim (filtros digitados ou importados) | sim | EQ (anunciado; mecanismo não verificado) | não verificado | não: compatibilidade oficial só com Audison |

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

**Opcional**: uma sessão com o Flat Liner, com TuneEQ/ATM ou com outra ferramenta pode servir de
referência prática e preencher a coluna “Testado”. Não é obrigação de compra nem condição para
concluir o projeto (JV-D036). TuneEQ e ATM, por já fazerem parte do PC-Tool, podem ser usados
normalmente como etapas de calibração dentro do Jarvis (JV-D031).
