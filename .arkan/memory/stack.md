# Stack do Projeto

> Preencha este arquivo no primeiro dia de adoção do Arkan. Os agentes leem daqui
> os diretórios onde procurar código, migrações e testes, em vez de adivinhar.

---

## Identificação

- **Projeto**: [nome]
- **Repositório**: [monorepo | repositório único | vários repositórios]
- **Linguagens principais**: [ex.: TypeScript, Python]

## Diretórios que os agentes usam

| Papel | Caminho neste repositório | Usado por |
| --- | --- | --- |
| Código de aplicação | `[ex.: src/, apps/]` | investigador de bugs, auditor, alinhamento |
| Bibliotecas internas | `[ex.: packages/, lib/]` | investigador de bugs, análise de impacto |
| Migrações de banco | `[ex.: migrations/, db/migrations/]` | auditor de esquema, housekeeping |
| Testes | `[ex.: tests/, __tests__/]` | agente de qualidade |
| Documentação de domínio | `[ex.: docs/]` | spec, glossário, alinhamento |

> Deixe em branco o papel que não existe no projeto. Agente que precisa de um
> caminho ausente **declara isso no artefato** em vez de inventar um caminho.

## Ferramentas

| Ferramenta | Há no projeto? | Observação |
| --- | --- | --- |
| Controle de versão | git | obrigatório |
| GitHub via MCP | [sim/não] | necessário para `/arkan.taskstoissues` e `/arkan.verificaissues` |
| Banco via MCP | [sim/não] | opcional; habilita a parte de banco do `/arkan.housekeeping` |
| Indexador de código | [sim/não] | opcional; os comandos funcionam sem, lendo arquivos direto |
| Observabilidade | [qual, se houver] | opcional; usada pelo `/arkan.ops` |

## Comandos de verificação

| O que | Comando |
| --- | --- |
| Testes | `[comando de teste do projeto]` |
| Lint | `[comando de lint do projeto]` |
| Tipos | `[comando de checagem de tipos do projeto]` |
| Build | `[comando de build do projeto]` |
