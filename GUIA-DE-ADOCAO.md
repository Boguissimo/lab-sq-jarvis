# Guia de adoção do Arkan

Este guia parte do princípio de que você acabou de copiar `.arkan/` e `.claude/` para o seu
repositório e ainda não rodou nenhum comando. As seis seções abaixo cobrem, nesta ordem: o
que o pipeline produz, como instalar sem tropeçar, o que é opcional, como devolver ao Arkan a
peça específica do seu domínio que este pacote não trouxe, como escrever a constituição do seu
projeto e como atualizar quando o Arkan de origem evoluir.

## 1. As dez fases e o que cada uma produz

Cada fase é um comando que você digita no editor. Nove das dez seguem o mesmo contrato: leem
pré-condições, produzem um artefato, e não avançam sem a sua aprovação explícita — o
Princípio VIII do núcleo ("o agente propõe, você decide"). A décima, Ops, é diferente por
natureza: roda em modo contínuo sobre uma feature que já está em produção, e o artefato é um
relatório para você ler, não um portão para você abrir.

| Fase | Comando | Artefato | Quem aprova |
| --- | --- | --- | --- |
| 01 — Ideação | `/arkan.ideacao` | `ideacao.md` (síntese do escopo) | você |
| 02 — Proposta | `/arkan.proposta` | `proposta.md` (escopo, estimativa, Go/No-Go) | você |
| 03 — Spec | `/arkan.spec` | `spec.md` (user stories, requisitos, invariantes) | você |
| 04 — Arquitetura | `/arkan.plan` | `plan.md` (ADRs, modelo de dados, contratos) | você |
| 05 — UX | `/arkan.ux` | `ux-spec.md` (fluxos, estados, interações) | você |
| 06 — Tasks | `/arkan.tasks` | `tasks.md` (lista ordenada e implementável) | você |
| 07 — Implementação | `/arkan.implement` | código + `tasks.md` marcado | você, tarefa a tarefa |
| 08 — QA | `/arkan.qa` | `qa-report.md` (decisão Go/No-Go para o deploy) | você |
| 09 — Deploy | `/arkan.deploy` | checklist de deploy executado + status em produção | você, confirmação por etapa |
| 10 — Ops | `/arkan.ops` | `ops-report.md` (erros, feedback, débito técnico) | leitura periódica sua, sem gate |

Nem toda feature passa pelas dez com o mesmo peso. `.arkan/memory/feature-weights.md` classifica
cada feature em **Code** (pipeline completo, 01→10), **Doc** (spec e QA simplificados,
arquitetura e UX puladas) ou **Config** (praticamente só tasks e implementação). Você confirma
o peso proposto na fase 01, e ele decide o que é obrigatório, simplificado ou pulado — leia
esse arquivo antes de estranhar uma fase "faltando".

Para sistemas grandes, `/arkan.projeto` decompõe a descrição num `feature-map.md` com várias
features antes do ciclo por feature começar — é a fase 01 em nível de projeto, não de feature.

Os outros 13 comandos não abrem uma fase nova: apoiam as dez de cima. `/arkan.clarify` e
`/arkan.checklist` reforçam a fase 03; `/arkan.analyze` reforça a fase 06; `/arkan.alinhamento`,
`/arkan.audit` e `/arkan.verificaissues` reforçam a fase 08; `/arkan.taskstoissues` leva a fase
06 para fora do repositório; `/arkan.critica-ui` e `/arkan.debate` são transversais, chamáveis
de qualquer fase; `/arkan.constituicao`, `/arkan.housekeeping` e `/arkan.debug` operam fora do
ciclo de uma feature específica; e `/arkan.pipeline` executa o ciclo 01→10 inteiro com os gates
de qualidade já embutidos.

## 2. Instalação e primeiro projeto

Os cinco passos são os do `README.md`. O que costuma dar errado em cada um:

1. **Esquecer de entrar no repositório de destino.** O passo 1 copia `.arkan/`, `.claude/` e o
   `.gitignore` para o seu projeto, mas se você não fizer `cd` para lá em seguida, os passos 2 a
   5 continuam rodando de dentro da pasta do pacote — você edita a cópia errada, e o seu
   repositório nunca vê a mudança. Confira com `pwd` antes de seguir para o passo 2.
2. **Rodar sem `git init` no repositório de destino.** Os scripts acham a raiz do projeto
   perguntando ao git onde fica o topo da árvore (`git rev-parse --show-toplevel`); sem
   repositório git, essa pergunta falha, e o efeito muda de script para script. O portão que os
   comandos do editor chamam (`check-prerequisites.sh`) não usa modo estrito: ele reporta
   `arquivo: ... — não encontrado` para cada pré-condição, uma mensagem incômoda mas visível. Já
   `create-project.sh` (passo 3) roda em modo estrito e **morre calado** — nenhuma saída, nem em
   texto normal nem em erro, só o código de saída 128. Se o passo 3 não imprimir nada e não
   criar a pasta do projeto, o motivo quase sempre é este: falta `git init` antes de tudo.
3. **Deixar o marcador de exemplo em `stack.md`.** A ficha já instrui deixar em branco o papel
   que não existe no seu projeto — isso está certo, um agente sabe ler ausência. O que não vale
   é deixar o texto do exemplo (`[ex.: src/, apps/]`) como se fosse o valor preenchido: um agente
   pode ler o que está entre colchetes como se fosse um caminho real. Ou você troca pelo caminho
   verdadeiro, ou apaga o conteúdo da célula — nunca deixa o exemplo como resposta.
4. **Projeto padrão apontando para um projeto que não existe.** Se `.arkan/config.md` declarar
   `projeto-default: meu-projeto` antes de você rodar `create-project.sh --project meu-projeto`,
   qualquer comando que resolva o projeto por esse campo vai procurar uma pasta que ainda não
   existe. Crie o projeto primeiro (passo 3), aponte o padrão depois (passo 5).
5. **Constituição do projeto não copiada.** `create-project.sh` cria a pasta e o `status.md` do
   projeto, mas **não** copia `constitution-template.md` — isso é passo manual (passo 4 do
   `README.md`). Pular esse `cp` deixa a lista de princípios do seu projeto (`P1..Pn`) sem
   arquivo para existir: só o núcleo global (`.arkan/memory/constitution.md`) é lido, e nenhuma
   regra sua entra na verificação até você criar o arquivo.
6. **`agente-dominio` esquecido em branco.** Não é erro — é o padrão, e sem ele a fase de
   reflexão de domínio é pulada e registrada no artefato, nunca fingida. Mas se você já tem um
   especialista de domínio em mente, escreva-o agora (seção 4) em vez de adiar: quanto mais
   crítica de interface você fizer sem ele, mais tela acumula sem revisão de domínio — parecer
   nenhum se acumula, porque a etapa simplesmente não roda.

**Crescer o projeto: criar uma feature nova.** O caminho normal é digitar `/arkan.ideacao` no
editor — o comando decide o próximo número e roda `.arkan/scripts/create-feature.sh` por você,
nos bastidores. Se preferir rodar o script direto (por exemplo, para automatizar a criação de
várias features de uma vez, fora do editor), a sintaxe **não** é `--name`: é `--short-name` mais
a descrição como argumento posicional solto.

```bash
.arkan/scripts/create-feature.sh --short-name "exportar-relatorio" "Exportar relatório em CSV"
```

Tentar `--name` no lugar de `--short-name` produz `Opção desconhecida: --name` e sai — mensagem
clara, não trava ninguém, mas só aparece depois da tentativa errada. Outras opções do script:
`--json` (saída estruturada, para automação), `--number N` (força o número em vez de calcular o
próximo disponível), `--parent NNN-000-slug` (declara como sub-feature de uma feature principal)
e `--project slug` (se o repositório tiver mais de um projeto e você não quiser depender do
`projeto-default` de `.arkan/config.md`).

## 3. Dependências opcionais

Nenhuma dependência de fora bloqueia o pipeline inteiro. Cada uma abre uma capacidade a mais em
alguns comandos específicos; sem ela, esses comandos seguem por um caminho mais lento (leitura
direta de arquivo) ou registram no próprio artefato que aquela parte não foi feita — nunca
fingem que passou.

### 3.1 Indexador de código (`arkan-kb`)

O indexador tem nome: `arkan-kb`, chamado nos comandos como `mcp__arkan-kb__query` e afins. Ele
**vem neste pacote**, na pasta `arkan-kb/` da raiz — mas em código-fonte. `node_modules/` e
`dist/` não vêm: instalar as dependências e compilar é passo seu, uma vez, antes do primeiro
uso. Todo comando que o cita funciona sem ele; os **20 dos 24 comandos** que o citam continuam
funcionando por leitura direta de arquivo enquanto você não compila — nenhum passo fica
bloqueado, só muda o custo de achar a informação.

**A fricção que você precisa saber antes de tentar, não depois.** Das seis dependências de
`arkan-kb`, uma — `better-sqlite3` — é módulo nativo: compila C++ durante a instalação e exige
ferramentas de build na máquina (em Linux/macOS, um compilador C++ e Python; no Windows, as
Build Tools do Visual Studio). Num ambiente sem essas ferramentas, a instalação **falha**, não
o indexador — os comandos continuam funcionando sem ele, pela mesma leitura direta de arquivo de
sempre. Se a instalação falhar e você não precisar do indexador agora, siga sem ele; volte a
esta seção quando (e se) a máquina tiver as ferramentas de build.

**Instalar e compilar:**

```bash
cd arkan-kb
<seu gerenciador de pacotes> install   # npm install / pnpm install / yarn / bun install
<seu gerenciador de pacotes> run build # roda o script "build" do package.json (tsc)
```

Isso produz `arkan-kb/dist/`. Nenhum gerenciador é exigido — o `package.json` não fixa um; use o
que já está disponível no seu ambiente.

**Ligar o indexador depois de compilado.** `arkan-kb/dist/cli/index.js` expõe duas superfícies,
ambas lidas do `package.json` do pacote:

- **Um servidor de contexto (MCP)**, iniciado com o subcomando `mcp`. É o que os comandos citam
  como `mcp__arkan-kb__query`, `mcp__arkan-kb__context` etc. — registre-o na configuração MCP do
  seu editor apontando `command: node` e `args: ["arkan-kb/dist/cli/index.js", "mcp"]`
  (caminho relativo à raiz do seu projeto).
- **Um executável de linha de comando**, `arkan-kb` (o campo `bin` do `package.json`) — use-o
  direto com `node arkan-kb/dist/cli/index.js <comando>`, ou linke o pacote (`npm link` dentro de
  `arkan-kb/`, ou equivalente do seu gerenciador) para chamar só `arkan-kb <comando>`.

Em qualquer caso, o primeiro comando a rodar é sempre `analyze` — ele constrói o índice em
`.arkan-kb/index.db`, na raiz do seu projeto; os demais comandos (`query`, `status`,
`export-graph`, `suggest-annotations`, `audit-coverage`) leem esse índice. Detalhe de cada um na
skill `arkan-kb-cli`, abaixo.

**As 6 skills.** Ensinam a usar o indexador uma vez compilado, uma por tipo de tarefa, em
`.claude/skills/arkan-kb/`:

| Skill | Quando usar |
| --- | --- |
| `arkan-kb-guide` | Referência rápida de todas as ferramentas MCP, do recurso `arkan-kb://status` e do schema do grafo — comece por aqui se não souber qual das outras cinco usar |
| `arkan-kb-cli` | Rodar os comandos de terminal (`analyze`, `query`, `export-graph` etc.) |
| `arkan-kb-exploring` | Entender como um código ou uma spec funciona, algo que você ainda não conhece |
| `arkan-kb-debugging` | Rastrear um bug, um erro, um comportamento inesperado |
| `arkan-kb-impact-analysis` | Medir o que quebra antes de mudar algo não trivial |
| `arkan-kb-auditing` | Auditar cobertura spec↔código e validar as constraints da constituição |

### 3.2 Demais dependências

| Dependência | Quem usa | Sem ela | Como declarar em `stack.md` |
| --- | --- | --- | --- |
| Banco de dados | 3 comandos: `/arkan.constituicao`, `/arkan.housekeeping`, `/arkan.audit` | a rota que não toca banco é a padrão nos três. Em `/arkan.housekeeping` a área de banco é pulada e registrada; em `/arkan.audit` a nota do relatório passa a ser sobre nove em vez de sobre dez, e a dimensão de banco fica declarada como "não avaliável" — nunca aprovada por omissão | linha "Banco via MCP" |
| GitHub | 2 comandos: `/arkan.taskstoissues` e `/arkan.verificaissues` — **os únicos onde a dependência é obrigatória, não opcional** | sem GitHub configurado de um jeito ou de outro, esses dois comandos não servem. Os outros 22 funcionam normalmente | linha "GitHub via MCP". Os dois comandos preferem GitHub via servidor de contexto (`mcp__github__*`); se indisponível, aceitam a CLI `gh` como alternativa (`gh auth login` necessário) — e registram no relatório final qual das duas foi usada |
| Observabilidade | 1 comando: `/arkan.ops` | o relatório operacional é montado só com os arquivos em `10-ops/` e o feedback que você registrou manualmente | linha "Observabilidade" — qualquer texto identificando o que há, ou em branco se não houver nenhuma |

## 4. Como escrever um agente de domínio

Esta é a seção mais importante do guia, porque é ela que devolve ao seu projeto a peça que
ficou de fora do pacote.

O repositório de onde o Arkan foi extraído tinha um agente especialista no domínio daquele
produto. Ele não veio para cá — cada produto tem o seu, e um agente escrito para o domínio de
origem seria ruído (ou pior, um viés escondido) em qualquer outro. No lugar dele ficou um
**gancho**: o campo `agente-dominio` em `.arkan/config.md`, hoje vazio.

```yaml
agente-dominio:
```

Quando você preenche esse campo com o nome de um agente seu (o nome do arquivo, sem a
extensão, salvo em `.arkan/agents/transversal/`), um comando passa a consultá-lo diretamente:
`/arkan.critica-ui` — depois que a crítica de usabilidade termina, seu agente entra como segunda
opinião, e recebe os achados dela como contexto. Quando o campo está vazio, essa etapa é
**pulada e registrada no artefato** ("nenhum agente de domínio declarado"), nunca fingida.

`/arkan.ux` não lê o campo — ele só *sugere*, ao final da fase, rodar
`/arkan.critica-ui --alvo=$FEATURE_DIR/05-ux/ux-spec.md` como próximo passo (obrigatório apenas
se a constituição do seu projeto exigir revisão heurística; opcional nos demais casos). É por
esse caminho indireto, não por leitura própria do campo, que o agente de domínio chega à fase de
experiência: quem escreve o agente esperando que ele entre sozinho na fase 05 não vê nada
acontecer — só vê algo quando alguém roda a crítica de interface depois.

Um terceiro caminho, `/arkan.debate`, também não lê o campo sozinho, mas como o arquivo do seu
agente mora no mesmo lugar de onde o debate escolhe as vozes do painel, basta convocá-lo pelo
nome (`--roles=<nome-do-arquivo>`) para trazer a voz do domínio a uma decisão que envolve
trade-offs, não só uma tela.

**O caso real que deu origem ao gancho.** No projeto onde o Arkan nasceu, esse agente era um
especialista em desenho de aprendizagem: julgava se uma tela respeitava os princípios
pedagógicos daquele produto, e os invariantes dele venciam os de usabilidade sempre que os dois
entravam em conflito — uma tela podia ser perfeitamente usável e ainda assim ser reprovada, se
ensinasse errado. O seu agente é outra coisa. Pode ser um especialista em conformidade
regulatória, em risco de crédito, em acessibilidade ou em segurança — o domínio muda, mas a
forma não: ele declara **invariantes verificáveis**, não preferências de estilo, e **recusa
qualquer recomendação que não consiga rastrear a um documento do seu domínio**. Um agente que
recomenda por instinto é decoração; um que aponta a cláusula, a política ou a norma interna que
sustenta cada achado é o que este gancho existe para trazer de volta.

**Esqueleto de arquivo.** Salve como `.arkan/agents/transversal/<nome-do-arquivo>.md`. O campo
`modo` não é schema imposto por nenhum script — é convenção; a lista abaixo são os seis valores
que os 29 agentes do pacote de fato usam, escolha o que descrever melhor o seu:

```markdown
---
nome: [Nome do seu agente — ex.: Especialista em Conformidade]
modo: [Geração | Orquestração | Assistência | Verificação | Contínuo | Adversarial + Reflexão]
tecnica: [ex.: Chain-of-Thought + Verificação Contra Documento-Fonte]
fase: transversal
usado-em: [.claude/commands/arkan.critica-ui.md]
---

## AGENTE

[Quem ele é, o que julga, e — decisivo — o que ele NÃO é. Se o seu domínio também tem um
agente de conformidade e um de segurança, declare aqui onde a fronteira entre os dois fica.]

## MODO

[Ele gera artefato novo ou só reage a um artefato existente? Tem veto do desenvolvedor sobre
cada recomendação (Princípio VIII), ou o parecer dele é consultivo?]

## TÉCNICA

[A técnica de raciocínio, passo a passo, na ordem em que precisa ser seguida. Se a ordem
importa — por exemplo, "leia o artefato inteiro antes de nomear o invariante violado, nunca o
contrário" — declare isso aqui: é o que evita virar checklist burocrático.]

## PRÉ-CONDIÇÕES

O comando que o invoca deve ter carregado:
- [o artefato a analisar]
- [o documento do domínio que fundamenta os invariantes — sem ele o agente não tem contra o
  que verificar]

## PÓS-CONDIÇÕES

[O formato do parecer: quantos achados, no mínimo e no máximo; o que cada achado precisa ter
(evidência, invariante violado, severidade, recomendação); e o que fazer quando não há
documento do domínio para rastrear uma recomendação — declarar a ausência, nunca inventar o
invariante.]

## PROMPT

Você é [nome] — [uma frase sobre a razão de existir]. Você não é [outro papel do painel, para
não duplicar escopo]. Em nenhum caso você recomenda algo que não consiga apontar a um trecho
do documento do domínio que o sustente.
```

## 5. Como escrever a constituição do seu projeto

O núcleo do Arkan (`.arkan/memory/constitution.md`, os oito princípios operacionais) **não se
copia** para a constituição do seu projeto — ele já vale para todos os projetos do repositório,
e é lido de um lugar só. `.arkan/templates/constitution-template.md` conta o motivo: até uma
versão antiga do Arkan, o núcleo era recopiado em cada modelo de projeto, e as duas cópias
divergiram sem que ninguém percebesse — o modelo chegou a perder dois dos oito princípios,
entre eles o que obriga a escrever em um idioma consistente. Fonte única é o que impede isso de
se repetir. O arquivo do seu projeto contém só o que é seu.

**O que é um bom princípio.** É uma regra que encerra uma discussão antes de ela acontecer —
não uma boa intenção. "Priorizar a segurança" não é um princípio: ninguém discorda disso, e
ninguém sabe o que fazer com isso na hora de revisar um código. "Toda rota que recebe dado de
fora do sistema valida o formato antes de persistir, e a validação que falha nunca é
silenciosa" é um princípio: alguém pode abrir um arquivo, checar se a rota valida, e dizer sim
ou não. Um princípio sem critério de verificação vira intenção; quem revisa não tem como
apontar violação.

Três exemplos, de domínios diferentes entre si, no formato que o modelo pede — inclusive a
marcação **NÃO-NEGOCIÁVEL**, para o princípio que não admite exceção:

**P1. Estoque reservado se libera sozinho.** Todo pedido cancelado ou expirado libera
automaticamente o estoque que havia reservado, em até 5 minutos, sem exigir ação manual de
ninguém.
*Critério de verificação*: nenhuma consulta ao estoque reservado retorna item de pedido
cancelado ou expirado há mais de 5 minutos.

**P2. Nenhum agendamento se sobrepõe.** Um profissional nunca tem dois agendamentos com
intervalos de horário que se cruzam, mesmo que criados por caminhos diferentes do sistema.
*Critério de verificação*: para qualquer profissional, a lista de agendamentos ordenada por
horário não tem dois itens consecutivos com intervalos sobrepostos.

**P3. Toda decisão automatizada é explicável.** NÃO-NEGOCIÁVEL. Nenhuma decisão de risco tomada
sem intervenção humana é registrada só com o resultado; o registro sempre inclui as variáveis
que a explicam, sem exceção — inclusive sob prazo apertado ou volume alto.
*Critério de verificação*: todo registro de decisão automatizada tem ao menos uma variável
nomeada associada — nunca apenas um resultado sem motivo.

Preencha também a tabela **Decisões de contexto** do modelo, mesmo quando a resposta for "sem
restrição": resposta em branco vira suposição do agente, e suposição errada custa mais do que
uma linha preenchida.

## 6. Atualizar o Arkan

Nem tudo debaixo de `.arkan/` é do framework. A maior parte do que você vai acumular usando o
Arkan mora nas mesmas pastas que ele ocupa, e uma atualização que não souber separar os dois
sobrescreve o seu próprio trabalho. Antes de atualizar, confira as duas listas.

**O que é seu — uma atualização nunca pode sobrescrever:**

- `.arkan/memory/stack.md` e `.arkan/config.md` — você preenche os dois na adoção (seção 2).
- `.arkan/projects/` — a constituição (seção 5) e o status de cada projeto seu.
- `.arkan/features/` — **todos os artefatos de todas as suas features**: ideação, spec, plano,
  tasks, qa, deploy, ops. É o grosso do que o Arkan produz para você — a razão de ele existir.
- `.arkan/memory/bugfixes.md` — log só de acréscimo; cada entrada é um bug que `/arkan.debug`
  corrigiu.
- `.arkan/memory/glossario.md` — a fonte canônica dele é a sua spec e a sua ideação; o arquivo
  acumula o que os agentes extraem delas ao longo do uso.
- `.arkan/debug/` — bugs órfãos que o comando de depuração registra quando nenhuma feature é
  identificável.
- o agente de domínio que você escreveu na seção 4, dentro de `.arkan/agents/transversal/` —
  mesmo estando numa pasta do framework, o conteúdo é seu.

**O que é do framework — pode ser substituído por uma versão nova sem perda:**

- `.arkan/agents/` (exceto o arquivo do seu agente de domínio, acima)
- `.arkan/templates/`
- `.arkan/scripts/`
- `.claude/commands/`
- `.arkan/memory/constitution.md` (o núcleo — não se edita, nem antes nem depois de atualizar) e
  `.arkan/memory/feature-weights.md`
- `MIGRATION-GUIDE.md`
- `arkan-kb/src/`, `arkan-kb/test/`, `arkan-kb/scripts/`, `arkan-kb/package.json`,
  `arkan-kb/tsconfig.json` e `arkan-kb/vitest.config.ts` — a fonte do indexador. `arkan-kb/dist/`
  e `.arkan-kb/` não fazem parte disto: são gerados por você (seção 3) e recriados com um novo
  build, não substituídos pela atualização.
- `.claude/skills/arkan-kb/` — as 6 skills do indexador.

**Como atualizar, com honestidade sobre o que dá para saber.** `VERSAO.md` diz de qual geração
este pacote veio — data, commit de origem, contagem de arquivos — o suficiente para responder
"isto é o que eu tenho, é o mais recente?". Ele **não** diz o que mudou entre uma geração e
outra: não há changelog aqui dentro, e este pacote não é um clone do repositório de origem — é
só o resultado de uma extração, sem histórico de commits para você puxar sozinho. Atualizar não
é algo que se faça a partir deste pacote isolado: é quem distribui o Arkan para você que precisa
gerar e entregar a geração nova. Do seu lado, o trabalho é substituir apenas os itens da lista
"framework" pela versão nova recebida, e conferir depois que nada da lista "seu" foi tocado.
