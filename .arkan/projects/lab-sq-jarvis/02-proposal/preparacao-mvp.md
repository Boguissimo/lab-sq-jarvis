# Preparação do MVP — Lab SQ Jarvis

> **Projeto**: lab-sq-jarvis
> **Status**: **Proposta — aguardando aprovação do desenvolvedor**
> **Data**: 2026-10-15
> **Natureza**: anexo do [`feature-map.md`](feature-map.md), pedido pelo desenvolvedor antes de qualquer
> implementação. Não substitui as fases do Arkan: o modelo de dados formal nasce no `plan.md` da
> F003; o caso de teste formal, na `spec.md` da F002; os critérios de aceitação de cada feature, na
> respectiva spec. Aqui ficam as propostas que essas fases vão detalhar.

---

## 1. Estrutura do MVP revisado (JV-D010)

**Objetivo**: demonstrar, sobre dados de referência de verdade conhecida, um ciclo de diagnóstico e
experimento assistido completo e rastreável. Medições reais do Focus entram depois, de forma
progressiva (F012, F013).

### Fluxo do usuário no MVP

| Passo | O que acontece | Tipo de registro | Feature |
| --- | --- | --- | --- |
| 1 | Abrir o caso de referência REF-001 (sistema virtual já cadastrado, dados confirmados por construção) | cadastro | F002, F003 |
| 2 | Importar as medições “antes” (arquivos no formato de exportação do REW) | medição | F004 |
| 3 | Verificar qualidade das medições | cálculo | F005 |
| 4 | Calcular respostas, soma prevista, diferença de fase | cálculo | F005 |
| 5 | Gerar indícios a partir dos cálculos | indício | F006 |
| 6 | Formular e ordenar hipóteses (regras + IA), com o que confirmaria ou refutaria cada uma | hipótese | F006, F008 |
| 7 | Recomendar um experimento de uma variável, com previsão calculada, critério de aceite e verificação de segurança | recomendação | F007 |
| 8 | Registrar a aplicação (simulada no caso de referência) e importar a medição “depois” | experimento | F004, F007 |
| 9 | Comparar previsão × resultado e emitir veredito com incerteza | experimento | F005, F007 |
| 10 | Usuário ratifica conclusão e decide | conclusão, decisão | F007, F009 |
| — | Conversar com o assistente sobre qualquer passo; consultar diário e registro de envios à IA | — | F008, F009 |

### O que o MVP não faz

Medições reais do Focus; API do REW; arquivo do HELIX; exportação de filtros; medição automatizada;
FIR; EQ automático.

---

## 2. Tecnologia da interface desktop (JV-D011, proposta)

**Proposta**: **PySide6** (Qt 6, licença LGPL) com **pyqtgraph** para gráficos; empacotamento com
PyInstaller para abrir com dois cliques.

| Por que | Detalhe |
| --- | --- |
| Uma só linguagem | Interface, cálculo e testes em Python; o desenvolvedor não precisa de cadeia JavaScript |
| Gráficos de engenharia | eixo de frequência logarítmico, dezenas de curvas sobrepostas, fase, resposta ao impulso, zoom e cursor com bom desempenho |
| Nativo no Windows | não depende de navegador nem de serviço local exposto |
| Testável | `pytest-qt` permite testes automatizados da interface (G1) |
| Maduro | Qt é padrão em software técnico desktop |

**Desvantagem aceita**: o chat do assistente terá formatação mais simples que numa página web
(Markdown básico).
**Alternativa**: NiceGUI em janela nativa (aparência web, mais fácil para chat, gráficos mais lentos
com muitas curvas).

### Telas mínimas do MVP

| Tela | Conteúdo |
| --- | --- |
| Sistema | veículo/sistema, canais, equipamentos com estado (planejado/informado/confirmado) |
| Medições | lista, metadados, gráficos de magnitude, fase e impulso, resultado da verificação de qualidade |
| Diagnóstico | indícios → hipóteses, cada item clicável até o cálculo e a medição de origem |
| Experimento | recomendação, resultado de cada regra de segurança, previsão, gráfico antes/previsto/depois, veredito |
| Assistente | conversa; cada número mostra a origem (cálculo) ou o selo “estimativa exploratória” |
| Diário | eventos em ordem, só leitura |
| Envios à IA | o que foi enviado, a quem, para quê; controle do nível de envio |

---

## 3. Primeiro caso de teste acústico — REF-001 (JV-D016, proposta)

### 3.1 Por que este caso

- **Verdade conhecida por construção**: a causa é posta pelo gerador do caso.
- **Clássico e discriminante**: o cancelamento por polaridade invertida no cruzamento é um problema
  real que o EQ automático não resolve e que diferencia o Jarvis.
- **Experimento seguro**: inverter polaridade não altera potência, excursão, corte nem ganho — não é
  recomendação sensível; vale só o procedimento seguro (SEG-08).
- **Previsão calculável**: a soma esperada após a correção é calculada a partir das medições
  individuais “antes”, sem nova medição.

### 3.2 Construção (variante ideal REF-001-A)

| Item | Valor |
| --- | --- |
| Sistema virtual | um lado (esquerdo): médio e tweeter, mesmo canal de DSP por via |
| Crossover | Linkwitz-Riley 4ª ordem (24 dB/oitava) em **3 000 Hz**, passa-baixas no médio, passa-altas no tweeter |
| Resposta dos alto-falantes | plana (variante ideal: só o crossover molda a resposta) |
| Distância ao microfone | 1,00 m para ambos (mesmo tempo de chegada) |
| Falha injetada | tweeter com **polaridade invertida** |
| Taxa de amostragem | 48 kHz; resposta ao impulso de 65 536 amostras |
| Arquivos gerados | por medição: resposta ao impulso (WAV) e resposta em frequência em texto no formato de exportação do REW |

**Medições “antes”**: M-médio (só o médio), M-tweeter (só o tweeter), M-soma (os dois).
**Medição “depois”** (gerada com a polaridade correta): M-soma-depois.

### 3.3 O que é fisicamente esperado (fundamento)

- Os dois filtros LR4 estão **em fase** em todas as frequências (diferença de 360°, equivalente a 0°)
  e valem −6 dB cada em 3 kHz; com polaridade correta, a soma tem magnitude plana (0 dB).
- Com o tweeter invertido, as duas contribuições ficam em **oposição de fase (180°)** em toda a
  região de sobreposição; em 3 kHz têm a mesma amplitude, e a soma teórica vai a zero (vale
  profundo, limitado na prática pelo ruído).
- Um **atraso** produziria diferença de fase que **varia com a frequência** (por exemplo, 0,167 ms
  dá 180° em 3 kHz, mas 120° em 2 kHz e 270° em 4,5 kHz); a diferença **constante** de 180°
  distingue polaridade de atraso.

### 3.4 Cadeia esperada (verdade de referência)

| Elo | Esperado |
| --- | --- |
| Qualidade | todas as medições aprovadas |
| Cálculos | respostas em frequência; soma prevista (M-médio + M-tweeter, complexa) concorda com M-soma; diferença de fase médio–tweeter ≈ 180°, constante entre 1,5 e 6 kHz |
| Indícios | I-1: vale na soma, próximo de 3 kHz, que não existe em nenhuma medição individual (a soma fica abaixo da soma de potências das individuais); I-2: diferença de fase constante ≈ 180° na sobreposição |
| Hipóteses (ordem) | 1ª: polaridade invertida de uma das vias; descartada ou rebaixada: desalinhamento temporal (fase não constante); crossover assimétrico |
| Recomendação | inverter a polaridade do tweeter esquerdo — uma variável; não sensível; com os passos de SEG-08 |
| Previsão | soma calculada com o tweeter invertido: magnitude plana; nível em 3 kHz sobe de forma acentuada |
| Veredito | **confirmada** |

### 3.5 Controles negativos e variantes (mesma família)

| Caso | Construção | Comportamento correto do sistema |
| --- | --- | --- |
| REF-001-N1 | polaridade correta; vale causado por reflexão presente nas medições individuais | **não** propor inversão de polaridade como primeira hipótese; reconhecer que o vale existe nas individuais; não recomendar reforço de EQ sem saber se o vale é equalizável (pedir mais posições) |
| REF-001-N2 | polaridade invertida, medições com ruído alto (relação sinal-ruído insuficiente) | verificação de qualidade reprova; nenhuma conclusão; veredito no máximo `inconclusiva` |
| REF-001-N3 | experimento em que, além da polaridade, o ganho do tweeter mudou +3 dB | resultado diverge da previsão; veredito `refutada` ou `inconclusiva`, com a divergência apontada |
| REF-001-B | variante realista: queda natural dos alto-falantes, pequena diferença de distância, ruído moderado | mesma cadeia que REF-001-A, com incerteza maior declarada |

Tolerâncias numéricas (diferença aceitável entre previsto e medido, limiar do indício de vale,
critério de “fase constante”) **não são fixadas aqui**: são definidas e justificadas na spec da F002,
junto com as métricas do conjunto de casos (JV-D008).

---

## 4. Modelo de dados mínimo (conceitual — formalizado no `plan.md` da F003)

### 4.1 Cadastro

| Entidade | Campos principais |
| --- | --- |
| Veículo/sistema | nome, descrição, estado do cadastro |
| Equipamento | tipo (alto-falante, amplificador, DSP, microfone, interface), fabricante, modelo, **estado** (`planejado`, `informado`, `confirmado`), fonte |
| Especificação | equipamento, grandeza (potência RMS, Fs, Xmax, impedância, corte mínimo recomendado…), valor, unidade, fonte, estado |
| Canal | nome, lado, via, alto-falante, amplificador, saída do DSP |
| Posição | nome (ouvinte, microfone, alto-falante), coordenadas, referência, estado |
| Snapshot de ajuste | origem (arquivo do PC-Tool ou descrição estruturada), arquivo original, data |

### 4.2 Originais

| Entidade | Campos principais |
| --- | --- |
| Arquivo original | hash SHA-256, nome original, tipo, tamanho, data de importação, local no cofre — **somente inserção** |

### 4.3 Cadeia de conhecimento

Uma tabela comum **Registro** (identificador, tipo, data, autor `sistema`/`ia`/`usuário`, estado,
resumo) e uma tabela **Derivação** (registro de origem → registro derivado, papel). Cada tipo tem
seus campos próprios:

| Tipo | Campos próprios |
| --- | --- |
| Medição | arquivo original, canais excitados, posição, microfone, calibração, snapshot de ajuste, nível, resultado de qualidade |
| Cálculo | algoritmo, versão, parâmetros, hash das entradas, resultado |
| Estimativa exploratória (lateral) | provedor, modelo, texto, cálculo que a conferiu (se houver) |
| Indício | detector, versão, descrição |
| Hipótese | enunciado, o que a confirmaria, o que a refutaria, estado |
| Recomendação | alteração (uma variável), sensível sim/não, cálculo da previsão, critério de aceite, resultado de cada regra SEG, aprovação de nível B |
| Experimento | recomendação, snapshots antes/depois, data de registro da previsão, veredito, incerteza |
| Conclusão | texto, data de ratificação |
| Decisão | texto, tipo (adotar ajuste, mudar critério…) |

**Regras de derivação permitidas**: medição → cálculo → indício → hipótese → recomendação →
experimento → conclusão → decisão. Uma estimativa exploratória pode inspirar uma hipótese, mas a
previsão de uma recomendação sempre aponta para um cálculo.

### 4.4 Critérios, transparência e diário

| Entidade | Campos principais |
| --- | --- |
| Critério | nome, versão, valor, decisão que o instituiu, vigência |
| Envio à IA | data, provedor, modelo, finalidade, categorias de dado, volume, hash do conteúdo, nível de autorização |
| Evento do diário | data, tipo, registro relacionado, descrição — **somente inserção** |

---

## 5. Critérios objetivos de aceitação do MVP (propostos)

| ID | Critério | Verificação |
| --- | --- | --- |
| CA-01 | Originais imutáveis: os hashes de todos os arquivos importados conferem ao fim do ciclo; tentativa de sobrescrever é recusada e registrada | teste automatizado (G1) |
| CA-02 | Cadeia íntegra: 100% dos registros com tipo válido e derivações permitidas; nenhuma recomendação sem hipótese, nenhuma hipótese sem indício, nenhum indício sem cálculo, nenhum cálculo sem entrada rastreável | rotina de integridade (G1) |
| CA-03 | Reprodutibilidade: recalcular com as mesmas entradas dá o mesmo resultado | teste automatizado (G1) |
| CA-04 | Cálculos com resposta analítica: cada rotina do MVP passa nos testes com sinais de resposta conhecida, nas tolerâncias fixadas na spec da F005 | suíte L1 (G1) |
| CA-05 | REF-001-A: a cadeia produzida é a da seção 3.4, com veredito `confirmada` | teste de caso (G1) |
| CA-06 | Controles negativos N1, N2, N3: o comportamento é o da seção 3.5 | testes de caso (G1) |
| CA-07 | Segurança: a suíte SEG bloqueia 100% das recomendações proibidas; recomendação sensível nunca é exibida sem marcação e pedido de nível B; dado não confirmado nunca é tratado como confirmado | suíte de segurança (G1) |
| CA-08 | Números da IA: 100% dos valores numéricos das respostas do assistente apontam para um cálculo ou têm o selo de estimativa exploratória; resposta fora disso é recusada | testes com provedor simulado (G1) e demonstração com ao menos um provedor real (G2) |
| CA-09 | Transparência: 100% dos envios à IA constam do registro; o usuário vê e controla o nível de envio | teste automatizado (G1) |
| CA-10 | Retomada: fechar e reabrir a aplicação restaura o estado; o diário explica o estado sem a conversa original | teste automatizado + roteiro (G1, G3) |
| CA-11 | Operação: abre com dois cliques no Windows; erros previstos aparecem em linguagem simples | roteiro executado pelo desenvolvedor (G3) |
| CA-12 | Utilidade: o desenvolvedor percorre o ciclo REF-001 pela interface e julga o raciocínio compreensível e útil | avaliação G3 |

Não há meta de acerto diagnóstico (JV-D008): o MVP define as métricas e mede o conjunto inicial; a
meta é decisão posterior.

---

## 6. Dependências entre features

Ver [`feature-map.md`](feature-map.md), seções “Features Propostas” e “Mapa de Dependências”.
