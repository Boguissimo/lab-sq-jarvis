# Registro de Decisões — Lab SQ Jarvis

> **Fonte canônica** dos identificadores `JV-D###` (constituição, P11).
> **Revisão 2 (2026-10-15)**: o desenvolvedor revisou a proposta inicial; decisões JV-D017 a JV-D029.
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
| JV-D011 | Interface desktop em PySide6 (Qt) com gráficos pyqtgraph | Técnica | **proposta**; lista de telas substituída pelo fluxo guiado (JV-D020) | 2026-10-15 |
| JV-D012 | Ford Focus como primeiro veículo de referência; equipamentos só após confirmação | Escopo | aprovada | 2026-10-15 |
| JV-D013 | Competição SQ não é requisito inicial | Escopo | aprovada | 2026-10-15 |
| JV-D014 | Regras de segurança explícitas (`regras-de-seguranca.md`) | Segurança | aprovada como exigência; conteúdo v0.1.0 **substituído por JV-D022** (v0.2.0, proposta) | 2026-10-15 |
| JV-D015 | Instalação do Arkan: pacote reconstituído, sem o projeto de exemplo; branches `lab-sq-jarvis/…` | Método | **proposta** | 2026-10-15 |
| JV-D016 | Primeiro caso acústico de referência: polaridade invertida no cruzamento médio/tweeter | Método | **proposta**; controle N3 revisto por JV-D024; limite de generalização em JV-D025 | 2026-10-15 |
| JV-D017 | Ferramenta pessoal primeiro; potencial comercial avaliado depois de pronta | Escopo | aprovada (revisão 2) | 2026-10-15 |
| JV-D018 | Comparação com ferramentas refeita com fontes oficiais; afirmação de ineditismo retirada | Método | aprovada (revisão 2); teste de referência com Flat Liner ou TuneEQ/ATM **proposto** | 2026-10-15 |
| JV-D019 | Dois marcos: Protótipo técnico e Versão pessoal utilizável | Escopo | aprovada (revisão 2); substitui JV-D010 | 2026-10-15 |
| JV-D020 | Fluxo guiado de sessão como experiência principal; rastreabilidade por trás | Escopo | aprovada (revisão 2); desenho detalhado **proposto** | 2026-10-15 |
| JV-D021 | Percepção registrada antes e depois desde o Marco 1; comparação cega depois | Escopo | aprovada (revisão 2); complementa JV-D006 | 2026-10-15 |
| JV-D022 | Segurança como redução de risco, sem garantia; limites provisórios identificados; sensibilidade por direção de risco | Segurança | aprovada (revisão 2) quanto aos princípios; classificação **proposta**; substitui o conteúdo v0.1.0 de JV-D014 | 2026-10-15 |
| JV-D023 | Fase e soma prevista só com referência temporal compatível | Técnica | aprovada (revisão 2); condições **propostas** | 2026-10-15 |
| JV-D024 | Veredito “comprometido” quando o protocolo do experimento é violado | Método | aprovada (revisão 2); revisa o controle N3 de JV-D016 | 2026-10-15 |
| JV-D025 | Casos ideais demonstram mecanismo, não generalizam o diagnóstico para o carro | Método | aprovada (revisão 2); complementa JV-D016 | 2026-10-15 |
| JV-D026 | Números da IA conferidos por origem, grandeza, unidade e canal; explicação segue sendo interpretação | Técnica | aprovada (revisão 2); revisa o critério de P3 da constituição v0.1.0 | 2026-10-15 |
| JV-D027 | Medições reais por importação de arquivos, sem esperar a API do REW | Escopo | aprovada (revisão 2); revisa dependência do feature map v1 | 2026-10-15 |
| JV-D028 | Reafirmados: local no Windows, cálculos verificáveis, originais preservados, histórico de configurações, IA substituível, ajustes aplicados à mão no HELIX | Método | aprovada (revisão 2) | 2026-10-15 |
| JV-D029 | Sequência de ajuste de referência (o que um profissional faria) com fontes; referência sonora pessoal como critério do usuário | Método | **proposta** | 2026-10-15 |

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
vazio, `common.sh` emite `proj_const: unbound variable`, embora o portão retorne PASS. Registradas
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
