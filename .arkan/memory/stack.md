# Stack do Projeto

> Preencha este arquivo no primeiro dia de adoção do Arkan. Os agentes leem daqui
> os diretórios onde procurar código, migrações e testes, em vez de adivinhar.

---

## Identificação

- **Projeto**: lab-sq-jarvis (Lab SQ Jarvis)
- **Repositório**: repositório único (`Boguissimo/lab-sq-jarvis`), independente do Arkan Personal, do Rygar e do Arkan Fiscal (JV-D001)
- **Linguagens principais**: Python 3 (cálculo determinístico, aplicação e interface); SQLite como banco local (JV-D002). Interface desktop Windows: tecnologia proposta em JV-D011 (PySide6), **pendente de aprovação**.
- **Plataforma-alvo**: Windows 10/11, uso local (sem servidor)

## Diretórios que os agentes usam

| Papel | Caminho neste repositório | Usado por |
| --- | --- | --- |
| Código de aplicação | `src/jarvis/` — **planejado**, ainda não existe; caminho a confirmar no `/arkan.plan` da primeira feature Code | investigador de bugs, auditor, alinhamento |
| Bibliotecas internas |  | investigador de bugs, análise de impacto |
| Migrações de banco | `src/jarvis/persistencia/migracoes/` — **planejado**, a confirmar no `/arkan.plan` | auditor de esquema, housekeeping |
| Testes | `tests/` (pytest) — **planejado**; casos acústicos de referência em `tests/referencia/` | agente de qualidade |
| Documentação de domínio | `.arkan/projects/lab-sq-jarvis/` (constituição, decisões `JV-D`, fontes `JV-S`, regras de segurança, diagnóstico inicial, feature map) | spec, glossário, alinhamento |

> Deixe em branco o papel que não existe no projeto. Agente que precisa de um
> caminho ausente **declara isso no artefato** em vez de inventar um caminho.

## Ferramentas

| Ferramenta | Há no projeto? | Observação |
| --- | --- | --- |
| Controle de versão | git | obrigatório |
| GitHub via MCP | sim, com uso mínimo (pedido do desenvolvedor: consome muitos tokens) — preferir git direto | necessário para `/arkan.taskstoissues` e `/arkan.verificaissues` |
| Banco via MCP | não | opcional; habilita a parte de banco do `/arkan.housekeeping` |
| Indexador de código | não (fonte em `arkan-kb/`, não compilado) | opcional; os comandos funcionam sem, lendo arquivos direto |
| REW (Room EQ Wizard) | externo | instalado no Windows do desenvolvedor; versão e licença **a confirmar**. Integração por API local (porta 4735) e importação de arquivos (JV-D003) |
| HELIX DSP PC-Tool | externo | versão **a confirmar**; integração assistida, sem escrita no DSP (JV-D004) |
| Observabilidade | diário de eventos só de acréscimo da própria aplicação (planejado) | opcional; usada pelo `/arkan.ops` |

## Comandos de verificação

| O que | Comando |
| --- | --- |
| Testes | `python -m pytest` — **planejado** |
| Lint | (a definir no `/arkan.plan`) |
| Tipos | (a definir no `/arkan.plan`) |
| Build | (a definir no `/arkan.plan`) |
