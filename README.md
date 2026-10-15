# Arkan

Um pipeline de desenvolvimento guiado por especificação, operado por agentes, dentro do seu
editor. Dez fases, da ideia à operação. Nove seguem o mesmo contrato — pré-condições, artefato,
aprovação explícita — e têm portões que um agente não pode pular; a décima, Ops, roda em modo
contínuo e produz um relatório para leitura, não um portão para abrir.

## O que vem aqui

| Pasta ou arquivo | O que é |
| --- | --- |
| `.arkan/memory/` | a constituição-núcleo do Arkan (8 princípios), o glossário, os pesos de feature (`feature-weights.md`), o registro de bugs (`bugfixes.md`) e a ficha de stack que você preenche (`stack.md`) |
| `.arkan/config.md` | o projeto padrão do repositório e o gancho para o seu agente de domínio |
| `.arkan/agents/` | 29 agentes, um por papel do pipeline |
| `.arkan/templates/` | 16 modelos de artefato — a fase de implementação não tem modelo, e 4 são transversais (um de crítica de interface, dois de depuração, um de constituição de projeto), fora do eixo numerado |
| `.arkan/scripts/` | 8 scripts que checam pré-condições, criam projetos e features, e auditam consistência |
| `.claude/commands/` | os 24 comandos `arkan.*` que você digita |
| `arkan-kb/` | o indexador de código e specs do Arkan, em código-fonte (CLI + servidor de contexto/MCP) — opcional, você instala e compila antes de usar (`GUIA-DE-ADOCAO.md`, seção 3) |
| `.claude/skills/arkan-kb/` | as 6 skills que ensinam a usar o indexador, uma vez compilado |
| `MIGRATION-GUIDE.md` | como migrar features que já seguem o padrão de pastas de outra ferramenta de especificação para o formato do Arkan |
| `VERSAO.md` | de qual commit do repositório de origem este pacote foi gerado |

## Começar em cinco minutos

```bash
# 0. Pré-requisito: o repositório de destino já precisa ter `git init`.
#    Sem isso os scripts não acham a raiz do projeto — e o passo 3 morre
#    calado (ver GUIA-DE-ADOCAO.md, seção 2).

# 1. Copiar as pastas do framework e o .gitignore para a raiz do seu
#    repositório, e entrar nele — os passos daqui em diante usam caminho
#    relativo. arkan-kb/ (indexador de código) é opcional: inclua-o no
#    mesmo comando se quiser usá-lo agora, ou volte para ele depois
#    — ver GUIA-DE-ADOCAO.md, seção 3.
cp -r .arkan .claude /caminho/do/seu/projeto/
cp -r arkan-kb /caminho/do/seu/projeto/   # opcional — indexador de código
cp VERSAO.md /caminho/do/seu/projeto/     # registro de qual geração você instalou (seção 6)
cat .gitignore >> /caminho/do/seu/projeto/.gitignore   # anexe; não sobrescreva o seu
cd /caminho/do/seu/projeto/

# 2. Declarar a sua stack (os agentes leem daqui em vez de adivinhar)
$EDITOR .arkan/memory/stack.md

# 3. Criar o seu projeto
.arkan/scripts/create-project.sh --project meu-projeto --name "Meu Projeto"

# 4. Escrever os princípios do seu projeto, a partir do modelo
cp .arkan/templates/constitution-template.md .arkan/projects/meu-projeto/constitution.md
$EDITOR .arkan/projects/meu-projeto/constitution.md

# 5. Apontar o projeto padrão para ele
$EDITOR .arkan/config.md   # projeto-default: meu-projeto
```

Depois, no editor: `/arkan.ideacao` para a primeira feature. O caminho completo, com o que
cada fase produz e o que é opcional, está no `GUIA-DE-ADOCAO.md`.

## O que o Arkan garante

- **A especificação governa o código.** Divergência se resolve mudando o código, não a spec.
- **Portão obrigatório.** Nenhum agente avança sem as pré-condições satisfeitas, e quem decide
  isso é um script, não a intenção do agente.
- **O agente propõe, você decide.** Nenhuma decisão de escopo, prioridade ou arquitetura
  acontece sem aprovação explícita.

Os oito princípios completos estão em `.arkan/memory/constitution.md`, e não se editam.

## O que não vem aqui

A interface web é uma peça separada, publicada e mantida fora deste pacote.

O indexador de código (`arkan-kb/`) vem no pacote, mas em código-fonte — instalar as
dependências e compilar é passo seu (seção 3 do `GUIA-DE-ADOCAO.md`). Os comandos funcionam sem
ele; onde ele ajudaria, o comando diz isso e segue por leitura direta de arquivos.
