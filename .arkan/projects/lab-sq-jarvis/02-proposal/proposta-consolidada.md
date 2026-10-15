# Proposta Consolidada — Lab SQ Jarvis

> **Projeto**: lab-sq-jarvis
> **Status**: **Proposta (revisão 3) — aguardando aprovação do desenvolvedor para implementar**
> **Data**: 2026-10-15
> **Substitui**: `preparacao-mvp.md` (v1, mesmo arquivo renomeado; histórico no git) e a versão da
> revisão 2 deste arquivo. Anexo do [`feature-map.md`](feature-map.md), fonte canônica de features,
> dependências, incrementos e sequência. Nada aqui substitui as fases do Arkan: o modelo de dados
> formal nasce no `plan.md` da F003; os casos de teste formais, na `spec.md` da F002; os critérios
> de cada feature, na respectiva spec.

## Siglas

| Sigla | Significado |
| --- | --- |
| REW | Room EQ Wizard — programa gratuito de medição acústica |
| DSP | processador digital de sinais (aqui, o HELIX) |
| PC-Tool | DSP PC-Tool — programa da Audiotec Fischer que configura o HELIX |
| EQ | equalização |
| IA | inteligência artificial |
| API | interface de programação — permite que um programa converse com outro |
| SEG | regra de segurança do projeto (`regras-de-seguranca.md`) |
| TuneEQ / ATM | automações do PC-Tool: EQ automático e medição automática de atraso |
| G1 / G2 / G3 | gates: verificação por teste automático / análise técnica do agente / decisão sua |
| PT / VP | critérios do Protótipo Técnico (Marco 1) e da Versão Pessoal (Marco 2) |
| JV-V | incremento executável (fatia vertical) |
| Nível B | aprovação que nomeia o ato: o quê, onde, quanto (núcleo do Arkan, princípio VIII) |

---

## 1. Para quem e para quê

O Jarvis é, primeiro, uma ferramenta **para o desenvolvedor**: ajustar o próprio sistema no Ford
Focus, entender o que está fazendo e acumular aprendizado entre sessões (JV-D017). Ele deve se
comportar, até onde possível, como um calibrador experiente (seção 3), respeitando que a referência
sonora é individual.

Não se pretende provar que a ideia é inédita: Flat Liner, Tuning Labs, TuneEQ/ATM e ACCORDO já
automatizam e guiam partes do trabalho (ver `../01-discovery/comparacao-ferramentas.md`). O Jarvis se
justifica pelo que acrescenta ao uso do desenvolvedor: explicar o porquê, testar em vez de tentar,
lembrar entre sessões e conferir contra o próprio equipamento — e aproveitar as automações dessas
ferramentas quando fizer sentido.

## 2. Escopo

**Dentro (até a versão pessoal)**

- Sessão guiada em dois modos (calibração e investigação de queixa), com a cadeia de conhecimento
  montada por trás.
- Teste de diagnóstico (uma variável) e etapa de calibração (conjunto documentado, inclusive
  TuneEQ/ATM).
- Percepção registrada antes e depois.
- Importação de arquivos do REW; protocolo de medição para o carro real.
- Cálculos determinísticos verificáveis; indícios e hipóteses.
- Regras de segurança que reduzem o risco, com limites provisórios identificados.
- Receita passo a passo para aplicar no PC-Tool, à mão.
- Histórico de sessões e de configurações, com estado declarado, arquivado ou coerente.
- Assistente de IA substituível, com números conferidos pela natureza da informação.

**Fora (por decisão)**

- Assinatura, SaaS (software como serviço), multiusuário, oficinas (JV-D017).
- Escrita automática no DSP (JV-D004, JV-D028).
- Leitura pela API do REW, leitura do arquivo do HELIX, comparação cega, medição automatizada:
  depois da versão pessoal (F018–F021).
- Medição, EQ automático e controle do DSP: continuam no REW e no PC-Tool (P10).

## 3. Como o Jarvis conduz uma sessão (JV-D020, JV-D021, JV-D030)

### 3.1 Dois modos

| Modo | Quando | Como começa |
| --- | --- | --- |
| **Calibração** | sistema novo, mudança de equipamento, retomada de um ajuste em andamento ou quando não há queixa clara | pela avaliação do estado do sistema |
| **Investigação de queixa** | você percebe algo específico | pela sua percepção |

### 3.2 O ciclo do calibrador (igual nos dois modos)

1. **Avaliar o estado**: o que já se sabe do sistema (cadastro, última configuração, últimas medições,
   etapas já concluídas, testes anteriores).
2. **Listar o que falta**: dados de equipamento não confirmados, medições ausentes ou sem referência
   temporal, configuração não declarada. Cada falta vem com o impacto (“sem a frequência mínima do
   tweeter, não recomendo baixar o passa-altas”).
3. **Explicar prioridades**: por que tratar primeiro isto e não aquilo (por exemplo, proteção e
   crossovers antes de EQ; problema de fase antes de corrigir magnitude).
4. **Escolher o próximo passo**: uma medição, um teste de diagnóstico, uma etapa de calibração — ou
   **nada a alterar**, quando os dados e a sua percepção não justificam mudança. Encerrar uma sessão
   sem ajuste é um resultado válido e fica registrado com a justificativa.
5. **Voltar quando o resultado exigir**: se uma etapa revela problema de uma etapa anterior (por
   exemplo, o EQ não resolve porque há cancelamento no cruzamento), o Jarvis propõe voltar a ela.

### 3.3 Sequência de referência

Guia de ordem, não roteiro rígido: estrutura de ganho e proteção → crossovers → níveis →
alinhamento temporal e polaridade → EQ → ajuste fino por escuta. Antes de virar critério, cada etapa
precisa de fonte registrada (JV-D029; spec das features F012 e F014). Até lá, a sequência aparece
como **proposta do agente**.

### 3.4 Três camadas de critério, em ordem de precedência

| Camada | Exemplos | Quem define | Pode ser flexibilizada por preferência? |
| --- | --- | --- | --- |
| 1. Segurança | regras SEG | decisão `JV-D` | não |
| 2. Limites técnicos | referência temporal para fase, qualidade mínima de medição, uma variável por teste de diagnóstico | constituição e specs | não |
| 3. Preferências pessoais | curva-alvo, equilíbrio de graves, apresentação do palco | você, versionadas | é a própria camada de preferência |

### 3.5 Os cinco passos na tela

| Passo | O que você faz | O que o Jarvis faz por trás |
| --- | --- | --- |
| **1. O que estou percebendo** (ou, no modo calibração, **onde estamos**) | descreve o que ouve — ou só confirma o estado do sistema | avalia o estado, lista o que falta, traduz percepções em mecanismos candidatos |
| **2. O que preciso medir** | segue o passo a passo no REW e importa os arquivos | confere qualidade e referência temporal; registra a configuração vigente (seção 5) |
| **3. O que os dados sugerem** | lê a explicação; pode perguntar ao assistente | calcula, gera indícios, ordena hipóteses e prioridades |
| **4. Qual passo dar** | aprova (nível B quando sensível) e aplica no PC-Tool — ou aceita “nada a alterar” | escolhe teste de diagnóstico ou etapa de calibração (seção 4), calcula a previsão, aplica as regras SEG, gera a receita |
| **5. O que mudou** | mede de novo, registra a percepção “depois” e decide manter ou reverter | compara, emite o veredito, atualiza o histórico e escreve o resumo da sessão |

A qualquer momento: **assistente** (conversa) e **histórico**.

## 4. Dois tipos de intervenção (JV-D031)

| | Teste de diagnóstico | Etapa de calibração |
| --- | --- | --- |
| Para quê | descobrir uma causa | levar o sistema a um objetivo (por exemplo, atrasos ajustados, curva próxima da preferência) |
| O que muda | **uma** variável | um **conjunto documentado** de alterações, inclusive automações (TuneEQ, ATM) |
| Antes | previsão quantitativa por cálculo; critério; percepção | objetivo da etapa; medições e percepção; limites informados para a automação (SEG-13) |
| Depois | veredito `confirmada`, `refutada`, `inconclusiva` ou `comprometida` | resultado `objetivo atingido`, `parcial`, `não atingido` ou `inconclusivo` |
| Atribuição causal | sim, à variável testada | **não**: a melhora é do conjunto, nunca de uma alteração isolada |
| Se várias coisas mudaram | `comprometida`; refazer com uma variável | normal: é o próprio conjunto |

Exemplo: o ATM ajusta todos os atrasos de uma vez (etapa de calibração). Se depois sobrar um vale
suspeito no cruzamento, um teste de diagnóstico inverte só a polaridade do tweeter para verificar a
causa.

## 5. Configuração do DSP e histórico com ajustes manuais (JV-D034)

O Jarvis não lê o HELIX. Por isso, distingue três níveis de confiança sobre a configuração usada em
cada medição, sem fingir uma verificação que não consegue fazer:

| Nível | O que significa | O que não prova |
| --- | --- | --- |
| **Declarada** | você informa qual configuração está ativa | nada além da sua declaração |
| **Arquivada** | o arquivo de ajuste do PC-Tool foi guardado no Jarvis (identificado por hash) | que esse arquivo estava aplicado no DSP durante a medição |
| **Coerente** | uma medição de controle rápida bate com a medição anterior da mesma configuração, dentro da tolerância | que o DSP está exatamente naquela configuração (é indício, não prova) |
| Verificada | leitura do estado do DSP | **indisponível** nesta fase |

**Procedimento (simples)**

1. **Início da sessão**: o Jarvis mostra a última configuração registrada e pergunta se é a que está
   no DSP. Você confirma ou informa outra (declarada).
2. **Medição de controle (recomendada)**: um canal de referência medido rapidamente; o Jarvis
   compara com a última medição dessa configuração e marca “coerente” ou “diferente — confira o
   DSP”.
3. **Antes de alterar**: salve o ajuste atual no PC-Tool com o nome que o Jarvis sugere (por exemplo,
   `JV-2026-10-20-S03-antes`) e entregue o arquivo ao Jarvis (arquivada).
4. **Depois de aplicar**: salve de novo (`…-depois`), entregue o arquivo e confirme que enviou ao DSP.
5. **Reverter**: o Jarvis indica qual arquivo carregar no PC-Tool; sem arquivo, mostra a receita
   inversa.

Cada medição guarda a configuração declarada, o arquivo associado (se houver) e o resultado da
medição de controle (se feita). O histórico mostra sempre o nível de confiança.

## 6. Interface (JV-D011, proposta)

**Tecnologia proposta**: PySide6 (Qt 6, licença LGPL) com gráficos pyqtgraph, empacotada para abrir
com dois cliques. Justificativa em `../decisoes.md`, JV-D011. Alternativa: NiceGUI.

**Organização**: duas áreas — **Sessão** (os cinco passos, com o assistente ao lado) e **Histórico**
(sessões, linha do tempo das configurações com o nível de confiança, resumo para retomar). Detalhes
da cadeia ficam em “ver detalhes”, nunca como etapa obrigatória.

## 7. Casos de referência e seus limites

Os casos simulados verificam os cálculos e o fluxo. **Passar neles demonstra funcionamento técnico,
não utilidade no Focus** (JV-D019, JV-D025). Nos casos simulados, a percepção é marcada
**`simulada`** ou **`não aplicável`** — você não precisa inventar uma experiência auditiva (JV-D035).

### 7.1 Família REF-001 — polaridade no cruzamento médio/tweeter (JV-D016)

Construção ideal (REF-001-A): crossover Linkwitz-Riley de 4ª ordem (24 dB/oitava) em 3 000 Hz;
alto-falantes de resposta plana; mesma distância de 1,00 m; tweeter com polaridade invertida;
48 kHz; arquivos no formato de exportação do REW; **todas as medições com a mesma referência
temporal**. Física esperada: as duas vias, em fase quando corretas, valem −6 dB cada em 3 kHz e
somam plano; invertidas, ficam em oposição (180° constante) e se anulam em 3 kHz.

| Caso | Construção | Comportamento correto |
| --- | --- | --- |
| REF-001-A | ideal, como acima | cadeia completa; hipótese de polaridade em primeiro; teste de diagnóstico de inversão; previsão plana; veredito `confirmada` |
| REF-001-B | realista: queda natural dos alto-falantes, pequena diferença de distância, ruído moderado | mesma cadeia, com incerteza maior declarada |
| REF-001-N1 | polaridade correta; vale causado por reflexão presente nas medições individuais | **não** propor polaridade em primeiro; reconhecer que o vale existe nas individuais; não recomendar reforço sem saber se é equalizável (pedir mais posições) |
| REF-001-N2 | polaridade invertida, ruído alto | qualidade reprova; **“não dá para concluir”** com explicação do que falta; no máximo `inconclusiva` |
| REF-001-N3 | no “depois”, além da polaridade, o ganho do tweeter subiu 3 dB | veredito `comprometida`; a hipótese **não** é refutada; propor refazer com uma variável (JV-D024) |
| REF-001-N4 | medições separadas **sem referência temporal comum** | **recusar** comparar fase e prever a soma; trabalhar só com magnitude e explicar o que falta (JV-D023) |
| REF-001-N5 | sistema sem problema no cruzamento (polaridade correta, soma plana) | **“nada a alterar”** nesse ponto, com justificativa (JV-D030) |

**Limite de generalização** (JV-D025): no carro, reflexões, distâncias, resposta real dos
alto-falantes e posição de escuta tornam a diferença de fase variável com a frequência, e um vale
pode ter várias causas. Lá, o diagnóstico se apoia em testes que discriminam; limiares ajustados em
casos simulados só valem no carro depois de conferidos em sessões reais (F014, F017).

### 7.2 Referência temporal compatível (JV-D023, condições propostas)

Comparar fase, estimar atraso relativo ou prever a soma de medições separadas só é permitido quando
todas as medições envolvidas têm: (1) o mesmo tipo de referência temporal, configurado igual —
loopback elétrico ou referência acústica de tempo do REW [recurso a confirmar na documentação oficial
e registrar como fonte na spec da F005]; (2) a mesma taxa de amostragem e as mesmas configurações de
varredura; (3) a mesma posição de microfone (tolerância a definir na spec da F005); (4) o mesmo
estado do DSP, exceto a variável em teste. Faltando qualquer condição: só magnitude; fase marcada
“não comparável”; o sistema sugere medir a soma diretamente ou repetir com referência.

## 8. Modelo de dados mínimo (conceitual — formalizado no `plan.md` da F003)

| Grupo | Entidades e campos principais |
| --- | --- |
| Cadastro | Veículo; Equipamento (tipo, fabricante, modelo, estado `planejado`/`informado`/`confirmado`, fonte); Especificação (grandeza, valor, unidade, fonte, estado); Canal; Posição |
| Configurações | Configuração (nome, origem, **nível de confiança** `declarada`/`arquivada`/`coerente`); arquivo do PC-Tool por hash, quando houver; medição de controle associada |
| Originais | Arquivo original (hash SHA-256, nome, tipo, data) — só inserção |
| Sessão | Sessão (modo `calibração`/`queixa`, data, estado, resumo, encerramento: com ou sem ajuste e justificativa); **Percepção** (antes/depois, descrição, faixa, música, posição, volume, nota opcional, origem `real`/`simulada`/`não aplicável`) |
| Cadeia | Registro (tipo, autor `sistema`/`ia`/`usuário`, data) + Derivação; tipos: medição (configuração vigente, tipo de referência temporal), cálculo, estimativa exploratória, indício, hipótese, recomendação (classe de sensibilidade, resultado de cada SEG, aprovação), **teste de diagnóstico** (variável, previsão, critério, veredito, incerteza), **etapa de calibração** (objetivo, conjunto de alterações, ferramenta usada, resultado, incerteza), conclusão, decisão (inclusive “decisão do usuário — condição não verificada”) |
| Critérios e preferências | Critério técnico versionado; Preferência pessoal versionada; Observação aprendida (com proveniência; ordena hipóteses, não altera critérios) |
| Transparência | Envio à IA (provedor, finalidade, categorias de dado, volume, autorização) |
| Diário | Evento (só inserção) |

## 9. Marco 1 — Protótipo técnico: critérios de aceitação

| ID | Critério | Gate |
| --- | --- | --- |
| PT-01 | Originais imutáveis: hashes conferem; sobrescrita é recusada e registrada | G1 |
| PT-02 | Cadeia íntegra (inclusive percepção, testes e etapas): 100% dos registros com tipo e derivações válidos | G1 |
| PT-03 | Reprodutibilidade: mesmas entradas, mesmo resultado | G1 |
| PT-04 | Cálculos com resposta analítica nas tolerâncias fixadas na spec da F005 | G1 |
| PT-05 | REF-001-A e REF-001-B produzem a cadeia e o veredito esperados (seção 7.1) | G1 |
| PT-06 | REF-001-N1 a N5 produzem o comportamento esperado: não propor polaridade (N1), “não dá para concluir” (N2), `comprometida` (N3), recusa por falta de referência temporal (N4), “nada a alterar” (N5) | G1 |
| PT-07 | Suíte SEG: 100% das proibidas bloqueadas; nenhuma bloqueada liberada por aprovação; sensíveis sempre com nível B; provisórios exibidos como provisórios | G1 |
| PT-08 | Números da IA: 100% associados a uma origem legítima e coerentes com ela (JV-D033), com provedor simulado; demonstração com um provedor real | G1, G2 |
| PT-09 | Transparência: 100% dos envios à IA registrados e controláveis | G1 |
| PT-10 | Fluxo guiado: você percorre o REF-001 pelos cinco passos, com percepção marcada `simulada`, sem preencher a cadeia à mão; fecha o programa e retoma | G3 |
| PT-11 | Etapa de calibração simulada: um conjunto de alterações registrado antes/depois é avaliado contra o objetivo, sem conclusão causal sobre alteração isolada | G1 |

**O Marco 1 não demonstra utilidade no Focus.**

## 10. Marco 2 — Versão pessoal utilizável: quando está pronta

A versão pessoal está pronta quando **todos** os critérios abaixo forem atendidos. Quantidades são
roteiro mínimo: **não provam, sozinhas, utilidade nem confiabilidade** (JV-D035) — quem decide é o
critério VP-10.

| ID | Critério | Como se verifica |
| --- | --- | --- |
| VP-01 | Cadastro do Focus confirmado: todos os equipamentos instalados com estado e fonte; nenhum item planejado tratado como instalado | revisão + teste (G1, G3) |
| VP-02 | Roteiro mínimo: pelo menos 3 sessões reais completas no Focus, em pelo menos 2 dias, incluindo ao menos uma em modo calibração e uma investigação de queixa, se houver queixa. Sessão encerrada sem ajuste, com justificativa, conta como completa | histórico (G1) |
| VP-03 | Nas sessões, você só descreveu percepções, seguiu o protocolo no REW, importou arquivos, aplicou receitas ou automações no PC-Tool e decidiu; a rotina de integridade passou | integridade (G1) + roteiro (G3) |
| VP-04 | Compreensão: cada orientação que levou a teste, etapa ou “nada a alterar” recebe sua marcação “entendi / em parte / não entendi”; nas duas últimas sessões, todas ficaram “entendi” (com ou sem perguntas ao assistente) | registro na sessão (G3) |
| VP-05 | Retomada: ao menos uma sessão retomada em outro dia só pelo resumo do Jarvis; você confirma que soube onde parou, o que já foi testado e qual é a configuração vigente e o nível de confiança dela | G3 |
| VP-06 | Percepção antes e depois registrada em 100% dos testes de diagnóstico e etapas de calibração reais | G1 |
| VP-07 | Honestidade: todo teste termina num dos quatro vereditos e toda etapa num dos quatro resultados; nenhuma conclusão sai de teste comprometido, de medição reprovada ou de atribuição causal dentro de uma etapa. (O “não dá para concluir” já foi demonstrado no Marco 1, PT-06; não é exigido no carro) | G1 |
| VP-08 | Segurança: nenhuma recomendação exibida viola regra SEG; todas as sensíveis passaram por nível B; alterações por decisão sua sem verificação aparecem como tal | G1 |
| VP-09 | Configurações: toda alteração aplicada tem configuração antes e depois com nível de confiança e pode ser revertida a partir do histórico | G1, G3 |
| VP-10 | Utilidade: você declara, por escrito e com justificativa, que o Jarvis o ajudou a ajustar o Focus e a entender o que fez. Comparar com outra ferramenta é **opcional** (JV-D036) | G3 |

## 11. Incrementos executáveis

O primeiro percurso completo que você poderá experimentar é o **JV-V01** — sessão guiada sobre o
REF-001-A, do arquivo importado ao veredito, com gráficos e histórico, aberta com dois cliques. Os
incrementos seguintes e o que entra em cada um estão no [`feature-map.md`](feature-map.md), seção
“Incrementos executáveis” (JV-D037).

## 12. O que mudou

### Revisão 3 (em relação à revisão 2)

| Revisão 2 | Revisão 3 | Decisão |
| --- | --- | --- |
| “calibrador experiente” como intenção | dois modos de sessão, ciclo de cinco ações, “nada a alterar”, retorno a etapas, três camadas de critério | JV-D030 |
| qualquer alteração múltipla = `comprometida` | teste de diagnóstico (uma variável) × etapa de calibração (conjunto, inclusive TuneEQ/ATM) | JV-D031 |
| SEG-07 permitia margem desconhecida com aprovação | aprovação não verifica; reforço sem margem verificada não é recomendado | JV-D032 |
| números da IA: cálculo ou estimativa | oito origens legítimas, conferidas pela natureza e pelo contexto | JV-D033 |
| arquivo de ajuste guardado = configuração usada | declarada, arquivada, coerente; “verificada” indisponível | JV-D034 |
| “não dá para concluir” exigido no carro; percepção exigida nos simulados | demonstrado em caso controlado (N2); percepção `simulada`; sessão sem ajuste vale; quantidades são roteiro mínimo | JV-D035 |
| relatórios do Flat Liner e conexões do Tuning Labs “não encontrados” | corrigidos; teste de outra ferramenta opcional | JV-D036 |
| marcos sem entregas intermediárias | seis incrementos executáveis | JV-D037 |

### Revisão 2 (em relação à v1)

| v1 | Revisão 2 | Decisão |
| --- | --- | --- |
| MVP único com dados de referência | dois marcos: protótipo técnico e versão pessoal | JV-D019 (substitui JV-D010) |
| sete telas mínimas | sessão guiada em cinco passos + histórico | JV-D020 |
| percepção não prevista no MVP | percepção antes e depois desde o Marco 1 | JV-D021 |
| “nenhuma ferramenta integra…” | comparação com fontes; sem pretensão de ineditismo | JV-D018 |
| reduções de ganho “não sensíveis” | toda mudança de ganho é sensível; exigência por direção do risco | JV-D022 |
| segurança apresentada como garantia | redução de risco nas condições conhecidas; limites provisórios identificados | JV-D022 |
| fase e soma prevista sem condição explícita | exigem referência temporal compatível | JV-D023 |
| N3 levava a `refutada` ou `inconclusiva` | N3 leva a `comprometida` | JV-D024 |
| REF-001 sem limite declarado | demonstra mecanismo; não generaliza para o carro | JV-D025 |
| números da IA conferidos só pela origem | origem, grandeza, unidade, canal | JV-D026 |
| medições reais dependiam da API do REW | dependem só da importação de arquivos | JV-D027 |
