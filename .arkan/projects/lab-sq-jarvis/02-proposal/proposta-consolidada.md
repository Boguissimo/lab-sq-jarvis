# Proposta Consolidada — Lab SQ Jarvis

> **Projeto**: lab-sq-jarvis
> **Status**: **Proposta (revisão 2) — aguardando aprovação do desenvolvedor**
> **Data**: 2026-10-15
> **Substitui**: `preparacao-mvp.md` (v1, mesmo arquivo renomeado; histórico no git). Anexo do
> [`feature-map.md`](feature-map.md), que é a fonte canônica de features, dependências e sequência.
> Nada aqui substitui as fases do Arkan: o modelo de dados formal nasce no `plan.md` da F003; os
> casos de teste formais, na `spec.md` da F002; os critérios de cada feature, na respectiva spec.

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
| Nível B | aprovação que nomeia o ato: o quê, onde, quanto (núcleo do Arkan, princípio VIII) |

---

## 1. Para quem e para quê

O Jarvis é, primeiro, uma ferramenta **para o desenvolvedor**: ajustar o próprio sistema no Ford
Focus, entender o que está fazendo e acumular aprendizado entre sessões (JV-D017). A ideia é fazer,
até onde possível, o que faria um calibrador experiente — sabendo que a referência sonora é
individual, e que as preferências do desenvolvedor são critérios dele, não verdades técnicas
(JV-D029).

Não se pretende provar que a ideia é inédita: Flat Liner, Tuning Labs, TuneEQ/ATM e ACCORDO já
automatizam e guiam partes do trabalho (ver `../01-discovery/comparacao-ferramentas.md`). O Jarvis se
justifica pelo que acrescenta ao uso do desenvolvedor: explicar o porquê, testar em vez de tentar,
lembrar entre sessões e conferir contra o próprio equipamento.

## 2. Escopo

**Dentro (até a versão pessoal)**

- Sessão guiada em cinco passos, com a cadeia de conhecimento montada por trás.
- Percepção registrada antes e depois de cada teste.
- Importação de arquivos do REW; protocolo de medição para o carro real.
- Cálculos determinísticos verificáveis; indícios e hipóteses; experimentos de uma variável.
- Regras de segurança que reduzem o risco, com limites provisórios identificados.
- Receita passo a passo para aplicar no PC-Tool, à mão.
- Histórico de sessões e de configurações; retomada pelo resumo.
- Assistente de IA substituível, com números conferidos.

**Fora (por decisão)**

- Assinatura, SaaS (software como serviço), multiusuário, oficinas (JV-D017).
- Escrita automática no DSP (JV-D004, JV-D028).
- Leitura pela API do REW, leitura do arquivo do HELIX, comparação cega, medição automatizada:
  depois da versão pessoal (F018–F021).
- Medição, EQ automático e controle do DSP: continuam no REW e no PC-Tool (P10).

## 3. A sessão guiada (JV-D020, JV-D021)

| Passo | O que você faz | O que o Jarvis faz por trás | Registros criados automaticamente |
| --- | --- | --- | --- |
| **1. O que estou percebendo** | descreve o que ouve, com apoio de vocabulário (palco, imagem, tonalidade, graves, clareza, aspereza…), a música de referência, a posição e o volume | traduz a percepção em regiões de frequência e mecanismos candidatos; consulta o histórico do carro | percepção “antes”; sessão |
| **2. O que preciso medir** | segue o passo a passo no REW (canais, posição do microfone, referência temporal, nível) e importa os arquivos | confere qualidade e referência temporal; avisa se algo impede a análise | medições; cálculos de qualidade |
| **3. O que os dados sugerem** | lê a explicação; pode perguntar ao assistente | calcula, gera indícios e ordena hipóteses, dizendo o que confirmaria ou refutaria cada uma | cálculos; indícios; hipóteses |
| **4. Qual teste fazer** | aprova o teste (nível B quando sensível) e aplica a receita no PC-Tool | escolhe um teste de uma variável, calcula a previsão, aplica as regras SEG, gera a receita com os passos seguros | recomendação; experimento; snapshot “antes” |
| **5. O que mudou** | mede de novo, registra a percepção “depois” (mesma música, posição e volume) e decide manter ou reverter | compara previsto × medido, emite o veredito com incerteza e escreve o resumo da sessão | medição “depois”; percepção “depois”; veredito; conclusão; decisão; snapshot “depois” |

A qualquer momento: **assistente** (conversa) e **histórico** (sessões, configurações, o que já foi
testado). A ordem dos assuntos ao longo das sessões segue a sequência de um calibrador experiente
(estrutura de ganho e proteção → crossovers → níveis → alinhamento temporal e polaridade → EQ →
ajuste fino por escuta), a ser fundamentada com fontes na F014 (JV-D029).

## 4. Interface (JV-D011, proposta; JV-D020)

**Tecnologia proposta**: PySide6 (Qt 6, licença LGPL) com gráficos pyqtgraph, empacotada para abrir
com dois cliques. Justificativa em `../decisoes.md`, JV-D011: tudo em Python, gráficos técnicos
rápidos, aplicativo nativo do Windows, testes automatizados da interface. Alternativa: NiceGUI.

**Organização**: duas áreas, não sete telas.

- **Sessão** — os cinco passos, um de cada vez, com o assistente ao lado.
- **Histórico** — sessões anteriores, linha do tempo das configurações, resumo para retomar.

A cadeia completa (cálculos, indícios, registro de envios à IA) fica acessível por “ver detalhes”,
nunca como etapa obrigatória.

## 5. Casos de referência e seus limites

Os casos simulados verificam os cálculos e o fluxo. **Passar neles demonstra funcionamento
técnico, não utilidade no Focus** (JV-D019, JV-D025).

### 5.1 Família REF-001 — polaridade no cruzamento médio/tweeter (JV-D016)

Construção ideal (REF-001-A): crossover Linkwitz-Riley de 4ª ordem (24 dB/oitava) em 3 000 Hz;
alto-falantes de resposta plana; mesma distância de 1,00 m; tweeter com polaridade invertida;
48 kHz; arquivos no formato de exportação do REW; **todas as medições com a mesma referência
temporal**. Física esperada: as duas vias, em fase quando corretas, valem −6 dB cada em 3 kHz e
somam plano; invertidas, ficam em oposição (180° constante) e se anulam em 3 kHz.

| Caso | Construção | Comportamento correto |
| --- | --- | --- |
| REF-001-A | ideal, como acima | cadeia completa; hipótese de polaridade em primeiro; teste de inversão; previsão plana; veredito `confirmada` |
| REF-001-B | realista: queda natural dos alto-falantes, pequena diferença de distância, ruído moderado | mesma cadeia, com incerteza maior declarada |
| REF-001-N1 | polaridade correta; vale causado por reflexão presente nas medições individuais | **não** propor polaridade em primeiro; reconhecer que o vale existe nas individuais; não recomendar reforço sem saber se é equalizável (pedir mais posições) |
| REF-001-N2 | polaridade invertida, ruído alto | qualidade reprova; nenhuma conclusão; no máximo `inconclusiva` |
| REF-001-N3 | no “depois”, além da polaridade, o ganho do tweeter subiu 3 dB | veredito **`comprometida`**: o protocolo foi violado; a hipótese **não** é refutada; o sistema propõe refazer com uma variável (JV-D024) |
| REF-001-N4 | medições separadas **sem referência temporal comum** | o sistema **recusa** comparar fase e prever a soma; trabalha só com magnitude e explica o que falta (JV-D023) |

**Limite de generalização** (JV-D025): no carro, reflexões, distâncias, resposta real dos
alto-falantes e posição de escuta tornam a diferença de fase variável com a frequência, e um vale
pode ter várias causas. Lá, o diagnóstico se apoia em testes que discriminam (inverter e medir de
novo, por exemplo); limiares ajustados em casos simulados só valem no carro depois de conferidos em
sessões reais (F014, F017).

### 5.2 Referência temporal compatível (JV-D023, condições propostas)

Comparar fase, estimar atraso relativo ou prever a soma de medições separadas só é permitido quando
todas as medições envolvidas têm:

1. o mesmo tipo de referência temporal, configurado igual — loopback elétrico ou referência
   acústica de tempo do REW [recurso do REW a confirmar na documentação oficial e registrar como
   fonte na spec da F005];
2. a mesma taxa de amostragem e as mesmas configurações de varredura;
3. a mesma posição de microfone (tolerância a definir na spec da F005);
4. o mesmo estado do DSP, exceto a variável em teste.

Faltando qualquer condição: só análises de magnitude; resultados de fase marcados “não comparável”;
o sistema sugere medir a soma diretamente ou repetir com referência.

## 6. Modelo de dados mínimo (conceitual — formalizado no `plan.md` da F003)

| Grupo | Entidades e campos principais |
| --- | --- |
| Cadastro | Veículo; Equipamento (tipo, fabricante, modelo, estado `planejado`/`informado`/`confirmado`, fonte); Especificação (grandeza, valor, unidade, fonte, estado); Canal; Posição |
| Configurações | Snapshot de ajuste (arquivo do PC-Tool guardado por hash, ou descrição estruturada; data; sessão) |
| Originais | Arquivo original (hash SHA-256, nome, tipo, data) — só inserção |
| Sessão | Sessão (data, objetivo, estado, resumo); **Percepção** (sessão, experimento, antes/depois, descrição, faixa, música, posição, volume, nota opcional) |
| Cadeia | Registro (tipo, autor `sistema`/`ia`/`usuário`, data) + Derivação; tipos: medição (com **tipo de referência temporal** e parâmetros), cálculo (algoritmo, versão, parâmetros, entradas por hash), estimativa exploratória, indício, hipótese, recomendação (classe de sensibilidade, resultado de cada SEG, aprovação nível B), experimento (previsão, critério, veredito `confirmada`/`refutada`/`inconclusiva`/`comprometida`, incerteza), conclusão, decisão |
| Critérios e preferências | Critério técnico versionado (decisão que o instituiu); **Preferência pessoal** versionada (curva-alvo e gostos do desenvolvedor); Observação aprendida (com proveniência; ordena hipóteses, não altera critérios) |
| Transparência | Envio à IA (provedor, finalidade, categorias de dado, volume, autorização) |
| Diário | Evento (só inserção) |

## 7. Marco 1 — Protótipo técnico: critérios de aceitação

| ID | Critério | Gate |
| --- | --- | --- |
| PT-01 | Originais imutáveis: hashes conferem; sobrescrita é recusada e registrada | G1 |
| PT-02 | Cadeia íntegra (inclusive percepção): 100% dos registros com tipo e derivações válidos | G1 |
| PT-03 | Reprodutibilidade: mesmas entradas, mesmo resultado | G1 |
| PT-04 | Cálculos com resposta analítica nas tolerâncias fixadas na spec da F005 | G1 |
| PT-05 | REF-001-A e REF-001-B produzem a cadeia e o veredito esperados (seção 5.1) | G1 |
| PT-06 | REF-001-N1 a N4 produzem o comportamento esperado, inclusive `comprometida` (N3) e recusa por falta de referência temporal (N4) | G1 |
| PT-07 | Suíte SEG: 100% das proibidas bloqueadas; sensíveis sempre com nível B; provisórios exibidos como provisórios | G1 |
| PT-08 | Números da IA: 100% conferidos por origem, grandeza, unidade e canal com provedor simulado; demonstração com um provedor real | G1, G2 |
| PT-09 | Transparência: 100% dos envios à IA registrados e controláveis | G1 |
| PT-10 | Fluxo guiado: o desenvolvedor percorre o REF-001 pelos cinco passos, sem preencher a cadeia à mão, com percepção antes/depois, fecha o programa e retoma | G3 |

**O Marco 1 não demonstra utilidade no Focus.**

## 8. Marco 2 — Versão pessoal utilizável: quando está pronta

A versão pessoal está pronta quando **todos** os critérios abaixo forem atendidos. As quantidades são
propostas, para sua aprovação.

| ID | Critério | Como se verifica |
| --- | --- | --- |
| VP-01 | Cadastro do Focus confirmado: todos os equipamentos instalados com estado e fonte; nenhum item planejado tratado como instalado | revisão + teste (G1, G3) |
| VP-02 | Pelo menos **3 sessões reais completas** no Focus (passos 1 a 5), em pelo menos **2 dias diferentes** | histórico (G1) |
| VP-03 | Nas sessões, você só descreveu percepções, seguiu o protocolo no REW, importou arquivos, aplicou receitas no PC-Tool e decidiu; a rotina de integridade passou sobre todos os registros | integridade (G1) + roteiro (G3) |
| VP-04 | Compreensão: cada orientação que levou a teste recebe sua marcação “entendi / em parte / não entendi”; nas **duas últimas sessões**, todas ficaram “entendi” (com ou sem perguntas ao assistente) | registro na sessão (G3) |
| VP-05 | Retomada: ao menos uma sessão retomada em outro dia só pelo resumo do Jarvis, e você confirma que soube onde parou, o que já foi testado e qual é a configuração vigente | G3 |
| VP-06 | Percepção antes e depois registrada em 100% dos experimentos | G1 |
| VP-07 | Honestidade: todo experimento termina num dos quatro vereditos; nenhuma conclusão sai de experimento comprometido ou de medição reprovada; ao menos uma vez o Jarvis disse “não dá para concluir” e explicou o que faltava | G1, G3 |
| VP-08 | Segurança: nenhuma recomendação exibida viola regra SEG; todas as sensíveis passaram por nível B | G1 |
| VP-09 | Configurações: toda alteração aplicada tem snapshot antes e depois e pode ser revertida a partir do histórico | G1, G3 |
| VP-10 | Utilidade: você declara, por escrito e com justificativa, que o Jarvis o ajudou a ajustar o Focus e a entender o que fez; se a sessão de referência com Flat Liner ou TuneEQ/ATM for feita (JV-D018), a declaração compara as duas experiências | G3 |

## 9. Sequência

Ver [`feature-map.md`](feature-map.md): Marco 1 (F001–F010), Marco 2 (F011–F017), depois (F018–F022).
Os dados do Focus podem ser reunidos em paralelo desde o início.

## 10. O que mudou em relação à v1

| v1 | Revisão 2 | Decisão |
| --- | --- | --- |
| MVP único com dados de referência | dois marcos: protótipo técnico e versão pessoal | JV-D019 (substitui JV-D010) |
| sete telas mínimas | sessão guiada em cinco passos + histórico | JV-D020 |
| percepção não prevista no MVP | percepção antes e depois desde o Marco 1 | JV-D021 |
| “nenhuma ferramenta integra…” | comparação com fontes; sem pretensão de ineditismo | JV-D018 |
| reduções de ganho “não sensíveis” | toda mudança de ganho é sensível; exigência por direção do risco | JV-D022 |
| segurança apresentada como garantia | redução de risco nas condições conhecidas; limites provisórios identificados | JV-D022 |
| fase e soma prevista sem condição explícita | exigem referência temporal compatível (novo caso N4) | JV-D023 |
| N3 levava a `refutada` ou `inconclusiva` | N3 leva a `comprometida`; a hipótese não é refutada | JV-D024 |
| REF-001 sem limite declarado | demonstra mecanismo; não generaliza para o carro | JV-D025 |
| números da IA conferidos só pela origem | origem, grandeza, unidade, canal; explicação segue sendo interpretação | JV-D026 |
| medições reais dependiam da API do REW | dependem só da importação de arquivos | JV-D027 |
| critério de utilidade dentro do MVP | utilidade só se mede no Marco 2 (VP-10) | JV-D019 |
