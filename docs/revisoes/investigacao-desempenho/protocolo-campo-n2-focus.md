# Proposta de sessão N2 (v2) — Ford Focus: um par de vias, polaridade e atraso conhecidos, soma medida

> **PROPOSTA. NÃO EXECUTAR.** Aguarda (1) autorização expressa de Fabrício para a execução física, (2) o sistema instalado e (3) a instrumentação confirmada. Nada foi medido nem alterado. Não altera `src/`, spec, limiares nem arquitetura; margem e admissibilidade são **parâmetros experimentais do harness**. 2026-10-16.
> Substitui a v1 deste arquivo. A rodada 3 (margem derivada do controle) está **adiada** até haver dado físico independente; este protocolo não a executa.
> Convenção: **[CONFIRMAR]** = fato ainda não confirmado, não presumido; **[PROPOSTO]** = valor sugerido para Fabrício aprovar, sem efeito até aprovação.

## 1. Em uma página
**O que é:** um único par de vias (A, B) de baixa/média frequência. Mede-se A sozinha, B sozinha e A+B tocando juntas, **num estado de referência**; depois aplica-se **no DSP** uma alteração conhecida em B (polaridade invertida; atraso conhecido) e mede-se **de novo a soma real** (A+B pelo microfone). O protótipo recebe as vias isoladas do estado de referência e a soma do estado alterado e deve dizer o que mudou, ou abster-se.
**Por que é N2:** a observação é uma varredura física feita **depois** da alteração, com as duas vias soando juntas; não é soma calculada, não compartilha arquivos com a previsão e não passa por injeção em código.
**O que prova / não prova:** prova se a previsão física identifica uma alteração real aplicada ao hardware, em **um par, um carro, uma sessão**. Não prova defeito natural desconhecido, utilidade para o ouvinte, outros veículos nem validação acústica do V02. A verdade é conhecida por quem aplica a alteração.
**Duração estimada:** ~2 h de sessão + ~1 h de verificações pré-sessão (item 6).

## 2. De onde vem a independência da observação
Quadro de linhagem (o que entra na previsão e na observação):
| | Previsão | Observação |
| --- | --- | --- |
| Arquivos | **A_ref** e **B_ref**: varreduras das vias isoladas no bloco B0 (estado de referência), 3 repetições cada | **S_X**: varredura(s) com A e B tocando juntas **depois** da alteração X, mais cedo ou mais tarde que B0 (minutos), com o DSP em outro estado |
| Operação | hipóteses H aplicadas a B_ref: normal, inversão, atraso τ; soma prevista = A_ref + H(B_ref) | **nenhuma operação**: o arquivo exportado do REW é usado como está |
| Compartilhamento | nenhum arquivo, nenhum array, nenhuma varredura é comum às duas colunas | idem |
| O que liga as duas | apenas a física: superposição linear de dois alto-falantes no mesmo ambiente, **que é o objeto do teste** | idem |
**Por que não concorda "por construção":** (i) a soma não é calculada de A e B nem corrigida por álgebra (como era na rodada 1 e, em parte, na 2); (ii) a falha não é injetada em arrays: é aplicada ao hardware e passa por DAC, amplificador, alto-falante, cabine e microfone; (iii) a verdade (o que o DSP fez) é verificada **por outra medição** (B isolada com a alteração, item 9.3), não assumida do nominal.
**Dependências residuais declaradas (não eliminadas):** mesmo microfone, posição, interface, cabine e sessão (erros comuns a todas as varreduras); o experimentador conhece o desenho; o valor nominal do DSP pode diferir do efetivo; a banda operacional do par é declarada por nós.
**Sinal de alarme de dependência indevida:** no estado de referência, o custo da hipótese "normal" entre a soma prevista e a soma medida deve ser **> 0** (nas somas físicas da sala foi 0,13–0,22). Custo ≈ 0,000 (< 0,01) significa arquivo duplicado, soma calculada ou erro de exportação, e **invalida a sessão**.

## 3. Escolha do par (decidir depois de confirmar a instalação)
Critérios, todos obrigatórios: (a) A e B em **canais independentes do DSP**; (b) banda comum **≥ 1 oitava**, com HPF/LPF protetores declarados e dentro da banda útil dos dois alto-falantes; (c) **dados confirmados** de cada alto-falante (Fs, potência RMS, HPF mínimo do fabricante, Xmax) para aplicar SEG-01 a SEG-03; (d) **baixa/média frequência**, longe de tweeter.
Candidatos conforme a instalação [CONFIRMAR]: subwoofer + midbass (banda comum ≈ 40–150 Hz) ou midbass + médio (≈ 200–500 Hz). Evitar 2–10 kHz: na rodada 2 a deriva observada (origem ainda não identificada) derrubou a previsão nessa banda. **Um par só** nesta primeira sessão.

## 4. Instrumentação: mínima, pendente e opcional (sem recomendação de compra)
| Item | Função | Mínimo? | Estado | Verificação necessária |
| --- | --- | :-: | --- | --- |
| Ford Focus (veículo de referência, JV-D012) | sistema sob teste | sim | **disponível (informado)** | instalação do par confirmada: drivers (marca/modelo), posição, fiação, canal do DSP de cada via |
| Computador Windows do projeto | gerar varredura, medir, exportar | sim | **disponível (informado)** | — |
| REW | varredura, captura, exportação | sim | **[CONFIRMAR]** instalação e versão (sem registro neste repositório) | exporta texto com nível e fase e a resposta ao impulso; taxa de amostragem fixa |
| DSP HELIX PRO MK3 e PC-Tool | aplicar polaridade/atraso por canal; silenciar canais fora do par; HPF protetor | sim | **PENDENTE: informado como não instalado** | instalado e operante; resolução e unidade do atraso; leitura/gravação do arquivo de configuração; canais do par independentes |
| Alto-falantes do par: dados do fabricante | segurança (SEG-01 a SEG-03) | sim | **PENDENTE** | Fs, RMS, HPF mínimo, Xmax confirmados com fonte |
| Amplificação do par | segurança (clipping) | sim | **PENDENTE** | potência e ganho conhecidos; sem clipping/limitador ativo na varredura |
| Interface de áudio | saída da varredura; entrada do microfone **e** do loopback | sim | **PENDENTE: há notícia de uma interface Behringer com Fernando, modelo não confirmado** | nº de entradas (microfone + loopback), taxa de amostragem, alimentação do microfone, drivers, ausência de processamento/ganho automático, latência estável |
| Microfone de medição | captar a soma | sim | **PENDENTE: não confirmado** | tipo, alimentação necessária, arquivo de calibração, ruído próprio, orientação |
| Referência temporal | tempo de chegada comparável entre varreduras | **sim, obrigatória** | **PENDENTE** | cabo de loopback **físico independente do DSP**; teste de estabilidade (item 6, V3) |
| Tripé/suporte e marcações do microfone | posição fixa | sim | **PENDENTE** | sem contato com o assento/operador; posição marcada e fotografada |
| Câmera/celular | registrar posição, telas do DSP e do REW | recomendável | opcional | — |
| Termômetro/higrômetro da cabine | **apenas registrar**; permite, depois, testar hipóteses sobre a deriva; **não** presume causa | opcional | opcional | leitura em cada bloco, sem atribuir a deriva |
| Medidor de nível (SPL) | verificar o nível no microfone (SEG-09) | opcional | opcional | — |
| Fonte/carregador estável | tensão constante durante a sessão | opcional | opcional | — |
| Calibrador acústico, segundo microfone, osciloscópio | conferências adicionais | opcional | opcional | — |
**Sem o DSP instalado a sessão N2 como pedida não pode ser executada.** Alternativas de nível inferior, **não recomendadas e só com sua decisão expressa**: inverter fisicamente a fiação de B (polaridade) ou gerar o atraso fora do DSP; nenhuma passa pelo caminho real do HELIX.

## 5. Parâmetros experimentais (margem e admissibilidade)
Fixos antes da sessão, **sem ajuste posterior**: `C_ADM` = 1,0; margem constante `m` = 0,2 [PROPOSTO] (referência das rodadas 1–2; **não** derivada); portão por banda (banda declarada = interseção das bandas operacionais das duas vias, ≥ 1 oitava, ≥ 20 pontos); custo = mediana|dB| + mediana|fase|/10 na máscara −30 dB. Estes são parâmetros do **harness**, não limiares do produto (P8).

## 6. Verificações pré-sessão (nenhuma altera o DSP; critérios [PROPOSTOS])
| ID | Verificação | Critério proposto | Se falhar |
| --- | --- | --- | --- |
| V1 | **Cadeia e taxa:** mesma taxa de amostragem em interface, REW e DSP; sem processamento ou ganho automático | confirmado por escrito | não iniciar |
| V2 | **Ruído e nível:** ruído de fundo e resposta do par; menor nível com SNR suficiente | SNR ≥ 30 dB na banda do par | reduzir ruído ou rever o par |
| V3 | **Estabilidade da referência temporal:** 10 varreduras idênticas, microfone parado; posição do impulso do loopback e do sinal acústico | dispersão do tempo de chegada ≤ 0,1 amostra [PROPOSTO]; **a dispersão observada fica registrada como incerteza de tempo** | sem referência estável o N2 de atraso não é interpretável: não iniciar |
| V4 | **Linearidade:** A e B a dois níveis (−6 dB) | diferença ≤ 0,3 dB após remover o ganho | revisar nível/clipping |
| V5 | **Deriva observada em repouso:** repetir A a cada ~2 min por ~20 min, sem tocar em nada, registrando tempo de chegada, nível, horário e (se houver) temperatura | reportar; **sem atribuir causa**; se a deriva do tempo de chegada ao longo da sessão exceder o efeito de 0,10 ms [PROPOSTO], limitar a sessão a atrasos maiores | registrar e decidir |
| V6 | **Repetibilidade do sistema:** 3× A, 3× B, 3× A+B em B0 | custo entre repetições ≤ 0,5 [PROPOSTO] | investigar antes de seguir |
| V7 | **Controle de admissibilidade:** soma prevista de B0 × soma medida de B0 | custo da hipótese normal entre 0,01 e `C_ADM`; < 0,01 = alarme de dependência (item 2); > `C_ADM` = par inadmissível | encerrar sem alegar nada |
| V8 | **Atraso/polaridade aplicáveis:** resolução e unidade do atraso no DSP; polaridade por canal | valor 0,25 e 1,00 ms representáveis; se não, usar o mais próximo e registrar o efetivo | ajustar os valores do plano antes de começar |

## 7. Segurança de níveis e proteção dos alto-falantes (SEG-01 a SEG-03, SEG-08, SEG-09, SEG-11)
1. **Sem dados confirmados do fabricante não há varredura.** O passa-altas protetor de cada alto-falante fica **aplicado no DSP antes da primeira varredura**, não abaixo do mínimo do fabricante (SEG-01).
2. **Faixa da varredura limitada ao par:** do limite inferior seguro (≥ HPF mínimo e, como regra provisória do projeto, ≥ 2 × Fs; SEG-02) até um pouco acima da banda comum; **nunca** uma varredura de 20 Hz a 20 kHz.
3. **Nível:** começar no mínimo e subir em passos de 3 dB até o SNR da V2; interromper em qualquer sinal de distorção, ruído mecânico ou clipping. Teto: o menor entre (a) o que mantém a potência estimada ≤ RMS confirmada (SEG-03) e (b) um teto de SPL no microfone que **você definir** (SEG-09 ainda não tem valor; sugestão a confirmar: não acima de ~85 dB SPL).
4. **Só polaridade e atraso de B são alterados.** Proibido mexer em ganho, EQ, passa-altas ou crossover. Canais fora do par ficam **silenciados** (mute, registrando o estado anterior e restaurando ao fim).
5. **SEG-08 em cada alteração:** volume ao mínimo, alteração feita com o sinal parado, retorno gradual ao nível de medição. **SEG-11:** o Jarvis não escreve no DSP; quem aplica é Fabrício.
6. Proteção auditiva para quem estiver no carro durante as varreduras.
7. **Parada imediata** (volume mestre ao mínimo, sinal parado) por qualquer anomalia; registrar e só retomar após revisão.

## 8. Procedimento da sessão (fixo)
Posição do microfone e do operador **marcadas e idênticas** em todas as varreduras; o operador permanece na mesma posição (a fonte do Passat relata mudança de padrão acima de 500 Hz com o torso do operador; aqui fica como cuidado, não como regra demonstrada).
| Bloco | Estado do DSP | Medições | Varreduras |
| --- | --- | --- | ---: |
| B0 | referência (normal) | A×3, B×3, S×3 (S = A+B) | 9 |
| X1…X4 | **um estado por bloco, em ordem sorteada (item 9):** polaridade de B invertida · atraso de B = 1,00 ms · atraso de B = 0,25 ms · **simulacro** (nenhuma alteração, mesmo ritual no DSP) | S×3, B×1 (**retida**), A×1 | 5 por bloco |
| C1…C4 | **restaurado** após cada X (controle) | S×2, A×1, B×1 | 4 por bloco |
| (opcional X5) | atraso de B = 0,10 ms, só se V5/V8 permitirem | idem X | 5 |
Ordem: B0, X1, C1, X2, C2, X3, C3, X4, C4. Total ≈ 45 varreduras (50 com X5). Em cada bloco: registrar horário, nível, temperatura (se houver instrumento), estado informado pelo DSP e fotografar as telas relevantes.

## 9. Cegamento, restauração verificável e verdade efetiva
**9.1 Cegamento (compromisso com revelação posterior).** Antes da sessão, Fabrício gera com `ferramentas/investigacao/n2_sorteio_cego.py` a ordem sorteada dos estados de X1…X4, com um *nonce* aleatório; o script grava a tabela **só com ele** e imprime o **SHA-256** da tabela, que é enviado ao analista (Claude) **antes** de qualquer arquivo. A tabela só é revelada depois que o analista gravar as previsões e o hash delas. Arquivos com ids neutros por bloco; **B isolada dos blocos X (B_F) fica retida** até a revelação, porque revelaria a alteração. O cegamento é entre o protótipo e os rótulos; o analista conhece o desenho.
**9.2 Restauração verificável.** Antes de começar: salvar o arquivo de configuração do DSP, calcular o **SHA-256** e anotar/fotografar os valores de polaridade e atraso de **todos** os canais (JV-D040). Após cada X: restaurar **pelo valor registrado** (não de memória), conferir na tela e medir o controle C_k; critério de parada: C_k diferir do B0 além da repetibilidade da V6 (custo > 0,5 [PROPOSTO] ou nível > 1 dB na banda) → parar e investigar. Ao final: recarregar o arquivo salvo, confirmar o **mesmo SHA-256** e as telas, e medir um último controle.
**9.3 Verdade efetiva.** Depois da revelação, B_F (retida) é comparada a B_ref para estimar a polaridade e o atraso **efetivamente aplicados**; se o efetivo diferir do nominal além de ±max(0,02 ms; 10 %) a verdade usada na avaliação é o **efetivo**, e a diferença é reportada.

## 10. Referência temporal e incertezas
Referência temporal por **loopback físico independente do DSP** [CONFIRMAR topologia]; sem ela a comparação de fase/tempo entre varreduras separadas não é interpretável. Orçamento de incerteza **estimado na própria sessão** (nada presumido):
| Fonte | Como é estimada | Entra em |
| --- | --- | --- |
| Variabilidade entre varreduras | V6 e controles C_k (custo entre repetições) | margem experimental, portão |
| Estabilidade da referência temporal | V3 (10 varreduras) | incerteza de τ |
| Deriva observada no tempo de chegada (origem não identificada) | V5 e controles intercalados | incerteza de τ; limite do menor atraso interpretável |
| Discrepância do modelo (superposição linear) | custo de B0 (V7) e dos C_k | folga mínima de decisão |
| Nível/linearidade | V4 | verificação |
| Diferença nominal × efetivo do DSP | 9.3 | verdade usada |
| Ruído | V2 | portão |
A margem `m` = 0,2 é **parâmetro experimental fixo**; a derivação da margem a partir do controle fica na rodada 3, adiada.

## 11. Análise (pré-registro específico, a fechar antes da sessão)
`preregistro-n2-focus.RASCUNHO.json` define: entradas do protótipo (A_ref, B_ref de B0; S de cada bloco; sem B_F nem rótulos), portão por banda, `C_ADM`, `m`, verdade usada (efetiva), métricas (cobertura, certas, omissões, identificações erradas, falsos alarmes nos C_k e no simulacro, abstenções) e a regra **"nenhum critério é ajustado após ver os resultados"**. Análises secundárias, rotuladas: comparar a previsão feita a partir do controle imediatamente anterior em vez de B0; estimar (a) e (c) do orçamento com os dados desta sessão. O protótipo reusa `diagnostico_previsao2.py`; será escrito o leitor dos arquivos exportados do REW depois da confirmação do formato real.

## 12. Limites declarados
Um carro, um par, uma sessão; alterações provocadas e conhecidas; analista com conhecimento do desenho; sem defeito natural; sem avaliação perceptiva; resultado negativo ou abstenções são resultados válidos; **não valida o V02 nem autoriza mudar o produto**.

## 13. Portões para a execução (todos antes de começar)
- [ ] Autorização expressa de Fabrício para a execução física.
- [ ] DSP instalado e operante; PC-Tool com leitura/gravação do arquivo; resolução do atraso conhecida.
- [ ] Par escolhido, dados dos alto-falantes confirmados (Fs, RMS, HPF mínimo, Xmax) e HPF protetor aplicado.
- [ ] Interface, microfone (com calibração) e loopback confirmados; REW com versão registrada.
- [ ] V1–V8 aprovadas ou desvios aceitos por escrito.
- [ ] Pré-registro N2 fechado e commitado; hash da tabela de cegamento entregue ao analista.
- [ ] Teto de nível (SEG-09) definido por Fabrício.
Até lá: **nenhuma medição, nenhuma alteração de DSP.**

## Apêndice — Ficha de registro (um registro por varredura)
`id_neutro · bloco · tipo (A/B/S) · repetição · horário · nível (dBFS e SPL se houver) · taxa · versão do REW · calibração do microfone · estado informado do DSP (polaridade, atraso e unidade, mute) · foto/tela · temperatura (se houver) · SHA-256 do arquivo exportado · observações (ruído externo, qualquer interferência)`
