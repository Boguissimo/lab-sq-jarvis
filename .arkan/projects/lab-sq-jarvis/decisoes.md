# Registro de Decisões — Lab SQ Jarvis

> **Fonte canônica** dos identificadores `JV-D###` (constituição, P11).
> **Revisão 2 (2026-10-15)**: o desenvolvedor revisou a proposta inicial; decisões JV-D017 a JV-D029.
> **Revisão 3 (2026-10-15)**: fechamento de pontos específicos, sem reabrir o planejamento; decisões JV-D030 a JV-D037.
> **Estados**: `proposta` (agente propôs; aguarda o desenvolvedor) · `aprovada` (desenvolvedor) ·
> `aprovada com ressalva` · `registrada` (pendência ou fato fora do escopo) · `substituída por JV-D###`.
> **Classe**: Método · Técnica · Escopo · Segurança.

| ID | Título | Classe | Estado | Data |
| --- | --- | --- | --- | --- |
| JV-D001 | Repositório independente `lab-sq-jarvis` com cópia própria do pacote Arkan | Método | aprovada (DA-01) | 2026-10-15 |
| JV-D002 | Python, SQLite e interface desktop para Windows | Técnica | aprovada (DA-02); tecnologia da interface em JV-D011 | 2026-10-15 |
| JV-D003 | Integração com o REW por API local e importação de arquivos | Técnica | aprovada (DA-03) | 2026-10-15 |
| JV-D004 | Integração com o HELIX assistida, sem alteração automática do DSP | Técnica | aprovada (DA-04) | 2026-10-15 |
| JV-D005 | IA independente de fornecedor; dados enviados conforme necessidade técnica, com transparência e controle | Técnica | aprovada com ressalva (DA-05/DA-06) | 2026-10-15 |
| JV-D006 | Cadeia de conhecimento e estimativas exploratórias da IA | Método | aprovada com ajuste (DA-07; ajustes 1 e 5) | 2026-10-15 |
| JV-D007 | Critérios técnicos só mudam por decisão explícita | Método | aprovada (DA-07) | 2026-10-15 |
| JV-D008 | Sem meta de acerto diagnóstico antes de existir conjunto de teste e verdade de referência | Método | aprovada (ajuste 2) | 2026-10-15 |
| JV-D009 | Scripts CRLF do Arkan Fiscal: pendência independente | Método | registrada (ajuste 6) | 2026-10-15 |
| JV-D010 | MVP reduzido: ciclo de diagnóstico e experimento assistido com dados de referência | Escopo | **substituída por JV-D019** (dois marcos) | 2026-10-15 |
| JV-D011 | Interface desktop em PySide6 (Qt) com gráficos pyqtgraph | Técnica | **aprovada** (G3, 2026-10-15: “usando PySide6 com pyqtgraph conforme proposto”) | 2026-10-15 |
| JV-D012 | Ford Focus como primeiro veículo de referência; equipamentos só após confirmação | Escopo | aprovada | 2026-10-15 |
| JV-D013 | Competição SQ não é requisito inicial | Escopo | aprovada | 2026-10-15 |
| JV-D014 | Regras de segurança explícitas (`regras-de-seguranca.md`) | Segurança | aprovada como exigência; conteúdo v0.1.0 **substituído por JV-D022** (v0.2.0, proposta) | 2026-10-15 |
| JV-D015 | Instalação do Arkan: pacote reconstituído, sem o projeto de exemplo; branches `lab-sq-jarvis/…` | Método | aprovada (G3, 2026-10-15: “siga o Arkan, preserve as decisões e mantenha o Core sem alterações”) | 2026-10-15 |
| JV-D016 | Primeiro caso acústico de referência: polaridade invertida no cruzamento médio/tweeter | Método | aprovada (G3, 2026-10-15, autorização do JV-V01 sobre o REF-001-A); N3 por JV-D024, limite em JV-D025, N5 em JV-D035 | 2026-10-15 |
| JV-D017 | Ferramenta pessoal primeiro; potencial comercial avaliado depois de pronta | Escopo | aprovada (revisão 2) | 2026-10-15 |
| JV-D018 | Comparação com ferramentas refeita com fontes oficiais; afirmação de ineditismo retirada | Método | aprovada (revisão 2); lacunas corrigidas e teste de outra ferramenta tornado **opcional** por JV-D036 | 2026-10-15 |
| JV-D019 | Dois marcos: Protótipo técnico e Versão pessoal utilizável | Escopo | aprovada (revisão 2); substitui JV-D010 | 2026-10-15 |
| JV-D020 | Fluxo guiado de sessão como experiência principal; rastreabilidade por trás | Escopo | aprovada (revisão 2); desenho detalhado **proposto** | 2026-10-15 |
| JV-D021 | Percepção registrada antes e depois desde o Marco 1; comparação cega depois | Escopo | aprovada (revisão 2); complementa JV-D006 | 2026-10-15 |
| JV-D022 | Segurança como redução de risco, sem garantia; limites provisórios identificados; sensibilidade por direção de risco | Segurança | aprovada (revisão 2) quanto aos princípios; classificação **proposta**; substitui o conteúdo v0.1.0 de JV-D014; SEG-07 corrigida por JV-D032 | 2026-10-15 |
| JV-D023 | Fase e soma prevista só com referência temporal compatível | Técnica | aprovada (revisão 2); condições **propostas** | 2026-10-15 |
| JV-D024 | Veredito “comprometido” quando o protocolo do experimento é violado | Método | aprovada (revisão 2); revisa o controle N3 de JV-D016; alcance restrito ao teste de diagnóstico por JV-D031 | 2026-10-15 |
| JV-D025 | Casos ideais demonstram mecanismo, não generalizam o diagnóstico para o carro | Método | aprovada (revisão 2); complementa JV-D016 | 2026-10-15 |
| JV-D026 | Números da IA conferidos por origem, grandeza, unidade e canal; explicação segue sendo interpretação | Técnica | aprovada (revisão 2); categorias de origem ampliadas por JV-D033 | 2026-10-15 |
| JV-D027 | Medições reais por importação de arquivos, sem esperar a API do REW | Escopo | aprovada (revisão 2); revisa dependência do feature map v1 | 2026-10-15 |
| JV-D028 | Reafirmados: local no Windows, cálculos verificáveis, originais preservados, histórico de configurações, IA substituível, ajustes aplicados à mão no HELIX | Método | aprovada (revisão 2) | 2026-10-15 |
| JV-D029 | Sequência de ajuste de referência (o que um profissional faria) com fontes; referência sonora pessoal como critério do usuário | Método | **proposta**; comportamento concreto em JV-D030 | 2026-10-15 |
| JV-D030 | Comportamento do calibrador: dois modos de sessão, avaliação do estado, prioridades, próximo passo, “nada a alterar” e retorno a etapas | Método | aprovada (revisão 3) quanto ao comportamento; sequência de referência continua dependendo de fontes (JV-D029) | 2026-10-15 |
| JV-D031 | Teste de diagnóstico (uma variável) × etapa de calibração (conjunto documentado, inclusive TuneEQ/ATM) | Método | aprovada (revisão 3); restringe JV-D024 ao teste de diagnóstico | 2026-10-15 |
| JV-D032 | Aprovação não transforma condição desconhecida em verificada; SEG-07 alinhada à regra geral | Segurança | aprovada (G3, 2026-10-15); método de margem digital segue **provisório** | 2026-10-15 |
| JV-D033 | Verificador de números por natureza da informação: cálculo, especificação com fonte, cadastro, declaração, critério, identificador, estimativa | Técnica | aprovada (revisão 3); amplia JV-D026 | 2026-10-15 |
| JV-D034 | Estado da configuração em três níveis: declarada, arquivada, coerente com medição de controle; “verificada” indisponível sem leitura do DSP | Técnica | aprovada (G3, 2026-10-15) com ajustes JV-D039 e JV-D040 | 2026-10-15 |
| JV-D035 | Critérios de aceite ajustados ao uso real | Escopo | aprovada (revisão 3); revisa critérios PT/VP da revisão 2 | 2026-10-15 |
| JV-D036 | Comparação: relatórios do Flat Liner e FAQ do Tuning Labs; “não encontrado/não verificado” em vez de ausência; teste de outra ferramenta opcional | Método | aprovada (revisão 3); revisa JV-D018 | 2026-10-15 |
| JV-D037 | Incrementos executáveis (fatias verticais JV-V01 a JV-V06) dentro dos dois marcos | Escopo | aprovada (G3, 2026-10-15); rastreio de entregas parciais em JV-D041 | 2026-10-15 |
| JV-D038 | Decisão sem intervenção (“nada a alterar”, “solicitar dados adicionais”), distinta de conclusão experimental | Método | aprovada (pedido do desenvolvedor, 2026-10-15); emenda P1 | 2026-10-15 |
| JV-D039 | Conferência de parâmetros só com valores efetivamente acessíveis e origem identificada; arquivo arquivado = registro e restauração | Segurança | aprovada (pedido, 2026-10-15); revisa SEG-13 | 2026-10-15 |
| JV-D040 | Reversão só com valores anteriores registrados; conjunto exige arquivo “antes” ou todos os parâmetros; senão, “reversão não garantida” | Técnica | aprovada (pedido, 2026-10-15); emenda P2 | 2026-10-15 |
| JV-D041 | Execução por incrementos: dependências para concluir feature, não para entrega parcial; status `parcial (JV-Vxx)`; registro de entregas | Método | aprovada (pedido, 2026-10-15) | 2026-10-15 |
| JV-D042 | Ratificação do conjunto e autorização da fundação e do JV-V01 | Método | **aprovada** (G3, 2026-10-15) | 2026-10-15 |
| JV-D044 | Diretrizes estratégicas de produto (orientação futura, sem ampliar o JV-V02) | Escopo | **aprovada** (2026-10-16) | 2026-10-16 |
| JV-D045 | Colaboração Fabrício–ChatGPT–Claude e autorização operacional da investigação de desempenho | Método | **aprovada** (redação final aprovada expressamente por Fabrício, 2026-10-16); emenda de 2026-10-17: regras 8 e 9 | 2026-10-16 |

---

### JV-D001 — Repositório independente

O Lab SQ Jarvis é independente do Arkan Personal, do Rygar e do Arkan Fiscal. Vive em
`Boguissimo/lab-sq-jarvis`, com cópia própria do pacote Arkan. O Core não é modificado.

### JV-D002 — Python, SQLite, desktop Windows

Python para cálculo, aplicação e interface; SQLite como banco local; uso local no Windows. A
tecnologia específica da interface foi pedida como proposta justificada: JV-D011.

### JV-D003 — REW: API local e arquivos

Leitura por API local do REW (linha 5.40+, porta 4735) e importação de arquivos exportados.
Disparo de varreduras pela API exige REW Pro: fora do escopo inicial.

### JV-D004 — HELIX: integração assistida

O Jarvis gera a receita de alteração; o desenvolvedor aplica no PC-Tool. Nenhuma alteração
automática de parâmetros do DSP (constituição, P10; SEG-11). Leitura do arquivo de ajuste só depois
de inspecionar um arquivo real.

### JV-D005 — IA e dados enviados

Aprovada a independência de fornecedor e a privacidade por padrão. **Ressalva do desenvolvedor**: a
quantidade e o tipo de dados enviados aos modelos são determinados pela necessidade técnica de cada
tarefa, com transparência e controle — não por uma regra fixa de “só dados derivados”. Consequência:
cada tarefa de IA declara as categorias de dado que precisa; o envio é registrado e controlável
(constituição, P9).

### JV-D006 — Cadeia de conhecimento e estimativas exploratórias

Cadeia preservada: medição → cálculo → indício → hipótese → recomendação → experimento →
conclusão → decisão (o termo “indício” substitui “sinal” do diagnóstico inicial). **Ajuste do
desenvolvedor**: a IA pode fazer estimativas exploratórias identificadas; cálculos usados para
validação e recomendação são produzidos ou conferidos por rotinas determinísticas rastreáveis
(constituição, P1 e P3).

### JV-D007 — Governança de critérios

Critérios (curvas-alvo, tolerâncias, limites, regras de segurança) são versionados e só mudam por
decisão. O histórico gera observações que podem ordenar hipóteses, nunca alterar critérios
(constituição, P8).

### JV-D008 — Métricas de diagnóstico antes de metas

A meta de 90% de acerto proposta no diagnóstico inicial foi retirada. Primeiro: construir o conjunto
de casos de teste, definir a verdade de referência de cada caso e escolher métricas adequadas. Metas
numéricas só depois, por nova decisão.

### JV-D009 — Pendência externa: CRLF no Arkan Fiscal

No repositório `Boguissimo/arkan-fiscal`, os scripts `.arkan/scripts/*.sh` estão gravados com fim de
linha CRLF; `check-prerequisites.sh` falha no bash (`$'\r': command not found`). O Rygar evita o
problema com `.gitattributes` (`*.sh text eol=lf`), adotado também aqui. **Decisão do
desenvolvedor**: registrar como pendência independente; **não alterar aquele repositório durante
este projeto**.

### JV-D010 — MVP reduzido

O MVP demonstra um ciclo de diagnóstico e experimento assistido, inicialmente com dados de
referência (casos construídos com verdade conhecida). Medições reais entram progressivamente, depois
do MVP. Estrutura proposta, na época, em `02-proposal/preparacao-mvp.md` (hoje `proposta-consolidada.md`).

### JV-D011 — Tecnologia da interface (proposta)

**Proposta**: PySide6 (Qt 6, licença LGPL) com pyqtgraph para gráficos.

| Critério | PySide6 + pyqtgraph | NiceGUI / pywebview (web local em janela) | Dear PyGui |
| --- | --- | --- | --- |
| Uma só linguagem (Python) | sim | sim (NiceGUI) / não (pywebview pede HTML/JS) | sim |
| Gráficos técnicos (eixo log, muitas curvas, fase, impulso, zoom) | muito bom, rápido | bom (Plotly/ECharts), mais lento com muitas curvas | rápido, recursos limitados |
| Aplicativo desktop nativo no Windows, sem navegador | sim | depende do WebView2 do Edge | sim |
| Maturidade e documentação | alta (Qt) | média | média-baixa |
| Testes automatizados de interface | pytest-qt | Playwright | limitado |
| Chat com texto formatado | adequado (Markdown básico) | excelente | fraco |
| Empacotamento (instalador/dois cliques) | PyInstaller, conhecido | PyInstaller, mais peças | PyInstaller |

**Justificativa**: o núcleo do produto é técnico (gráficos de resposta, fase, impulso, comparações
antes/depois); Qt é o padrão de aplicativos desktop de engenharia, roda nativo no Windows, mantém
todo o código em Python (um único conjunto de ferramentas de teste) e não depende de navegador. A
desvantagem — chat menos rico que numa página web — é aceitável. **Alternativa** se preferir
aparência de aplicativo web: NiceGUI em janela nativa.

### JV-D012 — Veículo e equipamentos

O Ford Focus é o primeiro veículo de referência. O cadastro real dos equipamentos será confirmado
antes de qualquer análise. Não presumir aquisição do microfone UMIK-1, do DSP HELIX PRO MK3 nem de
outros componentes planejados (constituição, P5; SEG-12).

### JV-D013 — Competição

Competição SQ não é requisito inicial. Vocabulário de percepção não depende de regulamento de
competição.

### JV-D014 — Regras de segurança

Exigência aprovada: regras explícitas para potência, excursão, frequência de corte e ganho. Conteúdo
proposto em `regras-de-seguranca.md` (v0.1.0), aguardando ratificação.

### JV-D015 — Instalação do Arkan (proposta)

Nenhum repositório acessível guarda o pacote Arkan em estado original (os dois começam já com o
projeto instalado). O pacote foi reconstituído: framework copiado do Rygar e conferido arquivo a
arquivo contra o Arkan Fiscal (idênticos, salvo fim de linha); `stack.md` no estado de modelo,
tirado do Fiscal; `arkan-kb/` e suas skills tirados do Fiscal. Contagem: 135 arquivos + 8 do
projeto de exemplo = 143, igual a `VERSAO.md`. O projeto de exemplo (demonstração) **não** foi
incluído, como no Rygar. Branches seguem `lab-sq-jarvis/<feature>`, porque o Arkan resolve o projeto
pelo prefixo da branch (uma branch `claude/...` seria lida como projeto `claude`).

Observações sobre o Core, **sem alteração**: (a) `arkan.projeto.md` declara pós-condições em
`.arkan/project/…` (singular), enquanto o script cria `.arkan/projects/<slug>/` — confirmado em
2026-10-15: `check-prerequisites.sh --pos` para `arkan.projeto.md` retorna FAIL procurando
`.arkan/project/status.md`; a verificação equivalente é feita sobre `.arkan/projects/lab-sq-jarvis/`
e registrada no `status.md` do projeto; (b) com projeto
vazio, `common.sh` emite `proj_const: unbound variable`, embora o portão retorne PASS. (c) `qa-mecanico.sh` exige `## ADRs`, `## Dependências e
Interfaces` e `## Sequência de Implementação` no plano mesmo para peso Doc, em que a fase 04 é
pulada; atendido com seções “N/A”; (d) a checagem de marcadores pendentes (`[TODO]`, `[A DEFINIR]`
etc.) usa `grep` sem escapar os colchetes, que viram classe de caracteres: acusa marcador em quase
todo arquivo (falso positivo).  Registradas
para o mantenedor do Arkan.

### JV-D016 — Primeiro caso acústico (proposta)

Caso de referência construído: médio e tweeter com crossover Linkwitz-Riley de 4ª ordem, tweeter com
polaridade invertida, gerando cancelamento no cruzamento. Verdade conhecida por construção;
experimento seguro (polaridade não altera potência, excursão, corte nem ganho); previsão calculável
a partir das medições individuais. Detalhe em `02-proposal/proposta-consolidada.md` (antes `preparacao-mvp.md`), seção 5.

---

## Revisão 2 — 2026-10-15

Origem: revisão do desenvolvedor sobre a proposta inicial (seis pontos: uso pessoal primeiro,
comparação com ferramentas, marcos, experiência de uso, limites técnicos e de segurança,
preservações). “Aprovada (revisão 2)” significa que a **direção** foi definida pelo desenvolvedor;
o texto que a detalha nos documentos continua aguardando a aprovação do conjunto.

### JV-D017 — Pessoal primeiro

O Jarvis existe primeiro para o desenvolvedor ajustar o próprio sistema, entender o que está
fazendo e acumular aprendizado entre sessões. Assinatura, estrutura de SaaS (software como
serviço) e requisitos de oficina ficam fora do escopo. A avaliação comercial acontece depois da
versão pessoal pronta (feature F022, sem data).

### JV-D018 — Comparação refeita

As seções 2 e 3 do diagnóstico inicial afirmavam que nenhuma ferramenta conectava medições,
ajustes, orientação e histórico. A afirmação foi retirada. A nova comparação está em
`01-discovery/comparacao-ferramentas.md`, separando capacidade documentada, anunciada, relatada e
testada (nenhuma testada até agora), com as divergências entre páginas registradas como dúvida.
**Proposta**: o desenvolvedor faz uma sessão com o Flat Liner (licença perpétua anunciada a
US$ 39,99) ou com TuneEQ/ATM como referência prática, antes da validação do Marco 2.

### JV-D019 — Dois marcos (substitui JV-D010)

- **Marco 1 — Protótipo técnico**: ciclo completo funcionando com casos conhecidos (simulados).
  Demonstra funcionamento técnico, não utilidade no Focus.
- **Marco 2 — Versão pessoal utilizável**: o desenvolvedor faz sessões reais no Focus, entende a
  orientação e retoma o trabalho depois. Critérios em `02-proposal/proposta-consolidada.md`.

### JV-D020 — Fluxo guiado

A experiência principal é uma sessão guiada em cinco passos: **o que estou percebendo → o que
preciso medir → o que os dados sugerem → qual teste fazer → o que mudou**. A cadeia de
conhecimento é montada por trás; o usuário não preenche registros à mão nem navega por telas
avulsas. Abrir com dois cliques continua necessário, mas não basta.

### JV-D021 — Percepção antes e depois

A percepção do desenvolvedor (o que ouve, em que faixa, com que música, posição e volume) é
registrada antes e depois de cada teste desde o Marco 1, como registro próprio da cadeia. A
comparação cega fica para depois (feature F020).

### JV-D022 — Segurança (substitui o conteúdo v0.1.0)

As regras reduzem o risco dentro das condições conhecidas e dos dados cadastrados; não garantem
segurança absoluta. A promessa “nunca arrisca o equipamento” foi retirada. Valores numéricos sem
fundamentação ficam marcados como **provisórios**. A contradição sobre ganho foi resolvida: toda
mudança que afeta potência, excursão, frequência de corte ou ganho é sensível, inclusive reduções;
o que muda é a exigência conforme a direção do risco. Detalhe em `regras-de-seguranca.md` v0.2.0.

### JV-D023 — Referência temporal

Comparar fase entre medições, estimar atraso relativo e prever a soma complexa de medições
separadas só é permitido quando as medições têm referência temporal compatível (por exemplo,
loopback ou referência acústica de tempo do REW, mesma taxa de amostragem, mesma posição de
microfone). Sem isso, o sistema trabalha só com magnitude e diz o que falta.

### JV-D024 — Veredito “comprometido” (revisa N3 de JV-D016)

Quando o experimento viola o próprio protocolo (por exemplo, mudar polaridade **e** ganho), o
resultado não refuta a hipótese: o veredito é `comprometido` e o sistema propõe repetir o teste
com uma variável.

### JV-D025 — Limite de generalização (complementa JV-D016)

O REF-001 ideal demonstra o mecanismo e testa o código. No carro, reflexões, distâncias
diferentes, resposta real dos alto-falantes e posição de escuta mudam o quadro: a diferença de fase
deixa de ser constante e o vale pode ter outras causas. Diagnóstico no carro se apoia em testes
discriminantes (por exemplo, inverter e medir de novo), e limiares validados em casos simulados
não valem para o carro até serem conferidos em sessões reais.

### JV-D026 — Números da IA (revisa critério de P3)

Além da origem, o verificador confere se o número citado corresponde à mesma grandeza, unidade,
canal, medição e faixa de frequência do cálculo de origem. Um número certo pode sustentar uma
explicação errada: a explicação da IA é sempre interpretação, e decisões de diagnóstico se apoiam
nos indícios determinísticos.

### JV-D027 — Medições reais sem API

A incorporação de medições reais (F013) depende da importação de arquivos, do cadastro do Focus e
do protocolo de medição — não da leitura pela API do REW, que passa a ser conveniência posterior
(F018).

### JV-D028 — Preservações

Mantidos: aplicação local no Windows; cálculos verificáveis; originais preservados; histórico das
configurações do DSP; IA substituível; ajustes aplicados manualmente no HELIX nesta fase.

### JV-D029 — Sequência de referência e preferência pessoal (proposta)

O fluxo guiado segue, até onde possível, a ordem de trabalho de um calibrador experiente
(estrutura de ganho e proteção, crossovers, níveis, alinhamento temporal, polaridade, EQ, ajuste
fino por escuta). Essa sequência precisa de fontes registradas antes de virar critério (spec das
features F012 e F014). A referência sonora é individual: a curva-alvo e as preferências do
desenvolvedor são critérios dele, versionados (P8), não verdades técnicas.

---

## Revisão 3 — 2026-10-15

Origem: revisão do desenvolvedor sobre a revisão 2 — sete pontos específicos, sem reabrir o
planejamento e sem aumentar o escopo. “Aprovada (revisão 3)” = direção definida pelo desenvolvedor;
o detalhamento nos documentos aguarda a aprovação do conjunto.

### JV-D030 — Comportamento do calibrador (concretiza JV-D029)

Dois modos de sessão: **calibração** (do estado atual do sistema, sem precisar de queixa) e
**investigação de queixa** (parte do que o desenvolvedor percebe). Em ambos, o Jarvis segue o mesmo
ciclo: avaliar o estado do sistema; listar o que falta saber; explicar prioridades; escolher e
justificar o próximo passo; reconhecer quando **não há motivo para alterar** nada. A sequência de
referência é um guia com retorno a etapas anteriores quando o resultado exige. Três camadas de
critério, em ordem de precedência: segurança (SEG) > limites técnicos > preferências pessoais. O
conteúdo da sequência depende de fontes (JV-D029). Detalhe: `02-proposal/proposta-consolidada.md`,
seção 3.

### JV-D031 — Teste de diagnóstico × etapa de calibração (restringe JV-D024)

- **Teste de diagnóstico**: investiga uma causa; uma variável controlada; previsão antes; veredito
  `confirmada`, `refutada`, `inconclusiva` ou `comprometida` (protocolo violado).
- **Etapa de calibração**: aplica um conjunto documentado de alterações, inclusive automações do
  PC-Tool (TuneEQ, ATM); registra o conjunto e as medições antes e depois; avalia o resultado contra
  o objetivo da etapa (`objetivo atingido`, `parcial`, `não atingido`, `inconclusivo`), **sem atribuir
  a melhora a uma alteração isolada**. O veredito `comprometida` não se aplica a etapas.

As regras de segurança valem para os dois tipos; numa etapa automatizada, o conjunto resultante é
conferido quando seus valores são informados ou arquivados, e o que não puder ser conferido fica
`não verificado`.

### JV-D032 — Aprovação não verifica (corrige SEG-07)

A aprovação do desenvolvedor autoriza um ato; não transforma uma condição desconhecida em condição
tecnicamente verificada. Regra única: se falta dado para verificar uma alteração de risco crescente,
o Jarvis **não a recomenda**. O desenvolvedor continua livre para alterar o próprio DSP; nesse caso,
o Jarvis registra “decisão do usuário — condição não verificada”, sem apresentá-la como segura nem
como recomendação. A SEG-07 (margem digital) passa a seguir essa regra. Caminho proposto para
verificar a margem: reforços compensados por atenuação documentada a montante (valor provisório, a
fundamentar na spec da F007).

### JV-D033 — Natureza dos números (amplia JV-D026)

Origens legítimas de um número numa resposta da IA: cálculo registrado; especificação com fonte;
valor do cadastro (com o estado: só `confirmado` é tratado como fato); configuração declarada pelo
usuário (tratada como declaração); critério ou preferência versionados; identificador ou rótulo
(canal 3, banda 5, JV-D031 — não são grandezas); constante física com fonte; estimativa exploratória
marcada. Cada número é conferido conforme a natureza e o contexto (grandeza, unidade, canal ou
equipamento, faixa, estado).

### JV-D034 — Estado da configuração do DSP

Três níveis, sem fingir verificação: **declarada** (o desenvolvedor informa qual configuração está
ativa), **arquivada** (arquivo do PC-Tool guardado por hash — prova o conteúdo do arquivo, não que
estava no DSP) e **coerente** (uma medição de controle rápida bate com a medição anterior dessa
configuração — indício, não prova). “Verificada” fica indisponível enquanto o Jarvis não ler o
DSP. Procedimento em `02-proposal/proposta-consolidada.md`, seção 5.

### JV-D035 — Critérios de aceite ajustados

- “Não dá para concluir” é demonstrado em caso controlado (Marco 1), não exigido no carro.
- Sessão encerrada sem ajuste conta como sessão completa quando essa é a decisão justificada.
- Nos casos simulados, a percepção é marcada `simulada` ou `não aplicável`.
- Três sessões em dois dias são um **roteiro mínimo**, não prova de utilidade nem de confiabilidade.

### JV-D036 — Comparação corrigida (revisa JV-D018)

Flat Liner: relatório final anunciado (medições iniciais, curva-alvo, EQ aplicado, níveis, alinhamento
temporal), com exemplo em PDF na página do produto. Tuning Labs: o FAQ cita processadores suportados
(EDSP31-610, EDSP31-68, Dayton Audio DSP-408, BLAM LA808 e outros da família YDW) e conexões por
WebHID, ponte nativa e BLE; a lista de marcas da página principal é do catálogo, não de
compatibilidade; suporte ao HELIX **não verificado**. Onde a pesquisa foi limitada, usa-se “não
encontrado” ou “não verificado”, nunca ausência. Testar outra ferramenta é **opcional**: nem compra
nem condição para concluir o projeto.

### JV-D037 — Incrementos executáveis

Os dois marcos são entregues em seis fatias verticais (JV-V01 a JV-V06), cada uma executável no
Windows e atravessando várias features, como no Rygar (RG-V01). A primeira, JV-V01, é o primeiro
percurso completo que o desenvolvedor pode experimentar. Nenhuma feature nova: as fatias reordenam
o trabalho já previsto. Composição em `02-proposal/feature-map.md`.

---

## Autorização de construção — 2026-10-15

### JV-D042 — Ratificação e autorização

Palavras do desenvolvedor: “a revisão 3 está alinhada com o que quero. Podemos sair do planejamento
geral e começar a construir. Autorizo a fundação necessária e o primeiro incremento executável
JV-V01, usando PySide6 com pyqtgraph conforme proposto.”

Ratificados, com os ajustes JV-D038 a JV-D041: constituição (v0.4.0), regras de segurança (v0.4.0,
como base do protótipo), briefing, visão, feature map (v4) e proposta consolidada. Aprovadas:
JV-D011, JV-D015, JV-D016, JV-D032, JV-D034, JV-D037.

**Não** muda com esta autorização: os limites técnicos provisórios continuam provisórios e não
validados para o equipamento do desenvolvedor; JV-D029 (sequência de referência) continua dependendo
de fontes; o JV-V01 é demonstração com dados simulados e explicações geradas por regras
implementadas — **não** está pronto para orientar ajustes reais no carro. A conversa com IA entra no
JV-V03.

### JV-D038 — Decisão sem intervenção (emenda P1)

A cadeia pode terminar numa decisão fundamentada de “nada a alterar” ou de “solicitar dados
adicionais”, derivada da avaliação do estado, de cálculos, indícios ou hipóteses, sem criar
experimento fictício. É distinta de uma conclusão experimental, que exige experimento.

### JV-D039 — Conferência por valores acessíveis (revisa SEG-13)

Enquanto o arquivo do PC-Tool não puder ser lido (F019), a conferência usa só valores efetivamente
acessíveis — declarados por você ou observados em medição —, sempre com a origem identificada. O
arquivo arquivado continua sendo registro e recurso de restauração.

### JV-D040 — Reversão (emenda P2)

Receita inversa só quando os valores anteriores necessários estão registrados. Em alterações em
conjunto, preserva-se o ajuste anterior (arquivo “antes”) ou todos os parâmetros necessários. Se
faltar informação, o Jarvis diz que a reversão não está garantida e o que falta.

### JV-D041 — Execução por incrementos

Dependências entre features valem para concluí-las, não para entregar partes. Uma feature fica
`parcial (JV-Vxx)` quando a parte prevista no incremento é entregue e testada. O feature map mantém
um registro de entregas que aponta para a evidência de teste de cada incremento.

## Diretrizes estratégicas — 2026-10-16

### JV-D044 — Diretrizes estratégicas de produto

Orientação para a arquitetura futura, **sem ampliar o JV-V02** e sem criar feature, requisito obrigatório
ou task. Texto integral em `docs/revisoes/diretriz-estrategica-usuario-e-produto.md`.

- **Usuário de referência:** o próprio desenvolvedor, entusiasta de áudio automotivo com conhecimento técnico geral, sem domínio profissional de calibração acústica; quer aprender e ter autonomia. O Jarvis ensina enquanto ajuda a resolver problemas reais.
- **Hipóteses comerciais (não demonstradas):** públicos entusiasta e profissional (primeiro, o instalador que domina equipamentos e instalação, mas depende de conhecimento especializado para calibrar); diferencial = investigação causal assistida, experimentos controlados, verificação de evidências e memória técnica por veículo, sem substituir REW, PC-Tool nem o ajustador experiente.
- **Níveis de instrumentação (preservar a possibilidade arquitetural; não implementar agora):** sem microfone (orientação declarada, sem inventar diagnóstico), celular (experimental, não calibrado), microfone USB calibrado, microfone com interface de áudio (referência temporal por loopback). A ausência de instrumento não impede o uso, mas impede conclusão não sustentada pelos dados.
- **IA (F009/JV-V03):** independência de provedores por adaptadores; núcleo determinístico (cálculo, critérios, segurança, integridade, admissibilidade) / IA (interpretação, explicação, hipóteses, pedidos de cálculo ou dados) / usuário (aprovação e execução física). A IA não altera critérios, não contorna bloqueios SEG e não escreve no DSP. Vários modelos numa investigação: avaliação posterior.
- **Sequência de validação:** funcionar tecnicamente → uso no Focus com medições reais → verificar ganho nas decisões → outros entusiastas → instaladores e ajustadores → avaliar comercialização. Teste sintético não valida utilidade nem eficácia acústica em campo. O potencial comercial é consequência de resultados demonstrados, não premissa.
- **Complemento de fundamentação (2026-10-16, sem decisão nova):** a aceitabilidade da imprecisão será avaliada também por **benchmark de mercado** (REW, Flat Liner, Tuning Labs, ajustadores experientes, REW + planilha), em três dimensões separadas — precisão da medição, precisão do diagnóstico, eficácia do ajuste —, com condições equivalentes, mesmos dados e verdade de referência independente; alegações comerciais não valem como prova; **segurança não é relativizada pelo benchmark**. Validação futura, sem requisito no V02. Detalhe em `docs/revisoes/diretriz-estrategica-usuario-e-produto.md`.
- A JV-D043 (diretriz de fontes de medição e REW) **permanece pendente** de decisão própria.

## Colaboração e investigação — 2026-10-16

### JV-D045 — Colaboração Fabrício–ChatGPT–Claude e autorização operacional da investigação de desempenho

Aprovada pelo desenvolvedor em 2026-10-16, incluindo o papel de gerência do ChatGPT; a redação final deste texto foi aprovada expressamente por ele na mesma data, junto com a autorização operacional de Nível B abaixo. Não altera os princípios I a VIII do Arkan Core nem os requisitos técnicos aprovados.

**Emenda de 2026-10-17** (aprovada expressamente por Fabrício; Nível B): acrescentadas as regras 8 e 9. Regras 1 a 7, papéis e autorização operacional preservados.

**Papéis.**
- **Fabrício** é o desenvolvedor do Princípio VIII: autoridade humana de decisão e responsável pela direção técnica do produto, em especial engenharia física, metrologia, metodologia experimental, validação, prioridades e finalidade. É o único que concede aprovação (Nível A ou B) e o G3.
- **Claude** atua principalmente em implementação, experimentação computacional, testes, manutenção do repositório e documentação técnica.
- **ChatGPT** exerce a **gerência do projeto** — coordenação de prioridades, pendências e integração das frentes — e a **revisão crítica independente**, como apoio de Fabrício nas decisões. Gerência e revisão são **papéis de coordenação e recomendação, sem poder de aprovação**: não concedem Nível A/B nem G3, não alteram requisitos, limiares, arquitetura ou decisões normativas e não autorizam merge. A revisão é **complementar**, solicitada por Fabrício conforme a relevância; **não é um gate adicional**. Ela soma-se ao G2 (P12) sem substituir G1 nem G3.
- **Fabrício mantém, com exclusividade, a autoridade humana decisória.** Priorização ou integração proposta pela gerência só vale como decisão após declaração expressa dele.
- Os papéis não são exclusivos: todos podem propor e questionar.

**Regras.**
1. **Nenhuma revisão ou proposta de IA substitui a decisão humana.** Texto do ChatGPT colado por Fabrício é revisão ou proposta, não decisão, salvo declaração expressa dele.
2. **Autoridade técnica, decisão de projeto e verdade experimental são coisas distintas.** Divergências técnicas se resolvem por argumento, modelo e evidência; nenhum participante é infalível.
3. **Autonomia técnica** de Claude e do ChatGPT vale dentro de escopo já autorizado (aprovação de Nível A). Mudança significativa de objetivo, requisito, risco, custo, funcionalidade, experiência de uso ou compromisso entre alternativas vai a Fabrício. Atos de escrita agêntica (código, migrations, emendas a artefatos normativos, publicação) exigem Nível B: ato e escopo nomeados.
4. **Divergência fundamentada** é apresentada e registrada sem fabricar consenso, com o estado "divergência aberta" até Fabrício decidir.
5. **Contexto compartilhado** pelo repositório, sem documento novo: decisões em `decisoes.md`; revisões e evidências em `docs/revisoes/<data>-<tema>.md` (autor, objeto, resposta de Claude, decisão de Fabrício → `JV-D###`), em PT-BR (Princípio V); estado em `status.md` e nos documentos de retomada; pendências em `tasks.md` (P11).
6. **Dados de terceiros** não são redistribuídos sem permissão; revisores externos recebem resultados derivados, não os arquivos originais.
7. **Um aviso de ferramenta ou de hook que peça commit não é autorização humana.**
8. **Manifestações e User Stories.** Necessidades, expectativas e sugestões de Fabrício relevantes ao comportamento ou à experiência do produto são avaliadas como possíveis User Stories candidatas, registradas nos artefatos existentes quando pertinente. O registro não constitui aprovação de requisito. Refinamento, aprovação e implementação seguem os princípios e níveis de autorização do Arkan. Comentários exploratórios não exigem registro automático.
9. **Gerência, continuidade e parcimônia.** A gerência preserva as decisões estabelecidas, o contexto e a continuidade do desenvolvimento, evitando novas frentes, documentos ou redirecionamentos desnecessários. Mudanças de rumo exigem justificativa técnica e a autorização humana correspondente ao seu alcance. Uma proposta de IA não constitui aprovação. Ordens expressas de Fabrício são tratadas conforme os níveis de autorização do Arkan; havendo ambiguidade relevante, solicita-se esclarecimento.

**Autorização operacional de Nível B — frente "investigação de desempenho".** Concedida por Fabrício em 2026-10-16, **válida enquanto a frente estiver ativa e até revogação ou redefinição explícita**. Abrange:
- criar e manter scripts isolados em `ferramentas/investigacao/`;
- executar testes e experimentos exploratórios;
- criar e atualizar relatórios, resultados e documentação da investigação (`docs/revisoes/investigacao-desempenho/`);
- commits e pushes desses materiais na branch `claude/busy-bohr-25s6e5`, sem pedido individual por commit.

**Limites (não abrange):** alterações no núcleo do Jarvis (`src/`), spec, limiares, arquitetura, decisões normativas, constituições e regras de segurança; instalação ou execução de código externo não verificado; redistribuição de datasets sem permissão; **merge na `main`**; declarar o V02 validado acusticamente. O G3 do bloco 1 (JV-T223) permanece parcial.

## Patch do P1 — 2026-10-17

### JV-D046 — Origem declarada como registro primário `declaracao` (patch do P1, constituição 0.5.0)

Aprovada expressamente por Fabrício em 2026-10-17 (alternativa **A**; opção B, exceção para cálculo sem origem em registro, **não** escolhida) e transmitida pela [issue #1](https://github.com/Boguissimo/lab-sq-jarvis/issues/1) (decisão e autorização Nível B). A issue é só canal de transmissão. Não reabre a JV-D045 nem altera o Arkan Core.

**Problema.** O cálculo `avaliacao_seguranca` usa dados declarados no manifesto (equipamento e alteração candidata), não dados de medição. Derivá-lo de uma medição não utilizada falsearia a proveniência, e o P1 só admitia `calculo ← medicao | calculo`.

**Decisão.**
- **Tipo primário `declaracao`, prefixo `L`** (D1). Sem origens, como a `medicao`; marca `declarado`; não é medição nem confirmação física do equipamento.
- **Uma declaração por manifesto** (D3), com o snapshot dos campos `equipamento` e `alteracao_candidata` e o SHA-256 do manifesto guardado no cofre. É a granularidade deste fluxo, não uma regra para declarações futuras.
- **Só `calculo` deriva de `declaracao`**; `DERIVACOES_PERMITIDAS["calculo"]` passa a `{medicao, calculo, declaracao}`; cálculo sem origem continua acusado.
- **Integridade:** além do hash no cofre, o snapshot é conferido **contra o conteúdo do manifesto preservado** (adulterar só o banco é acusado); ausência de origens; marca; fonte coerente com o manifesto e com o caso da sessão.
- **Constituição 0.5.0 (Minor)** sobre a 0.4.1 vigente (D2).
- **Sem migração de esquema** (`registro.tipo` não tem CHECK). Sem reavaliar o histórico (INV-211) e sem declaração retroativa; casos de referência anteriores inalterados (INV-213).

**Fora desta decisão:** `avaliar_alteracao_candidata` e os percursos S1–S3 (JV-T228), a interface (JV-T230), regras e limites SEG, calibração e merge na `main`. Cada um segue exigindo autorização própria.
