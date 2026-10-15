# Registro de Decisões — Lab SQ Jarvis

> **Fonte canônica** dos identificadores `JV-D###` (constituição, P11).
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
| JV-D010 | MVP reduzido: ciclo de diagnóstico e experimento assistido com dados de referência | Escopo | aprovada (ajuste 3); detalhamento em `02-proposal/preparacao-mvp.md` proposto | 2026-10-15 |
| JV-D011 | Interface desktop em PySide6 (Qt) com gráficos pyqtgraph | Técnica | **proposta** | 2026-10-15 |
| JV-D012 | Ford Focus como primeiro veículo de referência; equipamentos só após confirmação | Escopo | aprovada | 2026-10-15 |
| JV-D013 | Competição SQ não é requisito inicial | Escopo | aprovada | 2026-10-15 |
| JV-D014 | Regras de segurança explícitas (`regras-de-seguranca.md`) | Segurança | aprovada como exigência (ajuste 4); conteúdo **proposto** | 2026-10-15 |
| JV-D015 | Instalação do Arkan: pacote reconstituído, sem o projeto de exemplo; branches `lab-sq-jarvis/…` | Método | **proposta** | 2026-10-15 |
| JV-D016 | Primeiro caso acústico de referência: polaridade invertida no cruzamento médio/tweeter | Método | **proposta** | 2026-10-15 |

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
do MVP. Estrutura proposta em `02-proposal/preparacao-mvp.md` e no feature map.

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
a partir das medições individuais. Detalhe em `02-proposal/preparacao-mvp.md`, seção 3.
