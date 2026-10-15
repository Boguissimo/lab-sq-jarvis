---
description: "Arkan — Constituição: visualizar, validar, emendar ou ingerir princípios na constituição do projeto."
mode: assistencia
fase: transversal
nivel: projeto
tecnica: "Socratic Prompting + ReAct"
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/memory/constitution.md

## PÓS-CONDIÇÕES

arquivo: .arkan/memory/constitution.md

## User Input

```text
$ARGUMENTS
```

## Outline

Gerenciar a constituição do projeto — o documento de princípios, quality gates e restrições em `.arkan/memory/constitution.md`. A constituição é a autoridade máxima do Arkan, supersedendo defaults e preferências de agentes.

### Fase 0 — Setup

1. Ler `.arkan/memory/constitution.md` (núcleo global do Arkan — princípios I-VIII)
   - Se não existir: **parar** e avisar o desenvolvedor que o pacote está incompleto. O núcleo **não se recria** a partir de `.arkan/templates/constitution-template.md` — esse arquivo é o modelo de constituição de *projeto* e só aponta para o núcleo global; ele não contém os princípios I-VIII. Copiar dele produziria uma constituição vazia apontando para si mesma.
2. Extrair versão atual e data do cabeçalho

### Fase 1 — Determinar Ação

**Exibir cabeçalho**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  CONSTITUIÇÃO  ·  MODO: ASSISTÊNCIA
Agente: Constituição  ·  Step: Determinação de ação
Ação esperada: aguardar — identificando ação solicitada
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Determinar ação a partir de `$ARGUMENTS`:

| Primeiro token | Ação | Descrição |
| --- | --- | --- |
| (vazio) ou `view` | **View** | Exibir constituição com metadata |
| `validate` | **Validate** | Verificar compliance do codebase contra princípios |
| `amend` | **Amend** | Propor emenda à constituição |
| `check` | **Check** | Verificar arquivo ou feature contra princípios |
| `ingest` | **Ingest** | Extrair princípios de documento fonte e propor como emendas |

### Fase 2 — Execução

#### Se ação = View

Exibir a constituição formatada com:
- Versão e data
- Lista de princípios Core (I-VIII) — apenas nomes
- Lista de princípios do Projeto (P1-PN) — nomes + critérios de verificação
- Restrições de operação
- Quality gates

Sem interação adicional. Ir para Fase 4.

#### Se ação = Validate

**Exibir cabeçalho**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  CONSTITUIÇÃO  ·  MODO: ASSISTÊNCIA
Agente: Constituição  ·  Step: Validação de compliance
Ação esperada: aguardar — verificando codebase contra princípios
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Para cada princípio do projeto, verificar compliance. **A lista canônica é a do arquivo `.arkan/projects/<projeto>/constitution.md` (P1..Pn vigentes) — ler de lá; os itens abaixo são exemplos do formato de verificação, não princípios reais nem a lista completa:**

- **P1 — [nome do princípio do projeto]**: [pergunta objetiva — ex.: "Versionamento semântico obrigatório: todo pacote publicado segue SemVer, e breaking change sem major bump é violação?"]
- **P2 — [nome do princípio do projeto]**: [pergunta objetiva — ex.: "Acessibilidade WCAG AA: todo componente interativo tem rótulo acessível e contraste mínimo 4.5:1?"]
- **P3 — [nome do princípio do projeto]**: [pergunta objetiva — ex.: "Teste unitário isolado: nenhum teste unitário abre socket de rede; dependências externas são mockadas?"]

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

**Validação assistida por indexador** (quando disponível):
- `mcp__arkan-kb__query({query: "<termo-chave do princípio>"})` — encontrar símbolos e flows relacionados ao princípio em verificação (ou busca por texto, se não houver indexador)
- Consultas estruturais sobre o grafo de código no indexador, quando o princípio depender de relação entre símbolos (ex.: "X nunca referencia Y sem passar por Z") — usar consultas sobre nós e relações indexados pelo indexador de código declarado em `.arkan/memory/stack.md` (ou busca por texto, se não houver indexador)
- `git diff main...HEAD` — verificar se a branch respeita a constituição (cruzar com busca por referências no indexador nos símbolos alterados, quando disponível)

> **Dependência opcional — banco.** Esta parte só roda se `.arkan/memory/stack.md` declarar um banco acessível por servidor de contexto. Sem isso, o comando segue pelo caminho que não toca banco e **declara no artefato** que a verificação de banco não foi feita, em vez de fingir que passou.

Se o projeto declarar um princípio sobre gestão de schema (ex.: "toda mudança de schema é uma migration versionada"): verificar que as migrations aplicadas no banco batem com o diretório de migrações declarado em `.arkan/memory/stack.md`, com a versão registrada no controle de migrações do banco.

Para princípios Core (I-VIII), verificar compliance estrutural:
- **I — Spec Governa Código**: Features ativas têm `spec.md`? Código diverge de specs?
- **II — Gate Obrigatório**: `check-prerequisites.sh` existe e é executável?
- **III — Conclusividade**: Artefatos de features ativas têm `[PLACEHOLDER]` ou `[NEEDS CLARIFICATION]` abertos?
- **IV — Modo Declarado**: Comandos Arkan têm cabeçalho padronizado?

**Output**: Tabela com resultado por princípio:

| Princípio | Status | Detalhes |
| --- | --- | --- |
| P1 — [nome do princípio] | PASS / WARN / FAIL | [evidência] |
| ... | ... | ... |

#### Se ação = Amend

**Exibir cabeçalho**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  CONSTITUIÇÃO  ·  MODO: ASSISTÊNCIA
Agente: Constituição  ·  Step: Proposta de emenda
Ação esperada: revisar proposta e aprovar/rejeitar
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

1. Extrair descrição da emenda de `$ARGUMENTS` (texto após `amend`)
2. Identificar seção afetada na constituição
3. Mostrar seção **atual** (antes)
4. Mostrar seção **proposta** (depois) com diff claro
5. Determinar bump de versão:
   - **MAJOR**: Remoção ou redefinição incompatível de princípio Core
   - **MINOR**: Novo princípio ou seção adicionada
   - **PATCH**: Clarificação, correção de redação, ajuste factual
6. Apresentar ao desenvolvedor: diff + bump proposto
7. **Princípio VIII**: Aguardar aprovação explícita antes de aplicar
8. Se aprovado: aplicar emenda, atualizar `Versão` e `Data`, adicionar linha no `## Histórico de Emendas`
9. Ir para Fase 3 (Sync Impact Report)

**Regras de emenda**:
- Seção `## Arkan Core [NÃO EDITAR]` — NUNCA modificar sem aprovação explícita do mantenedor do Arkan + bump MAJOR
- Princípios I e II — NUNCA podem ser removidos (Governança)
- Princípios do projeto marcados **NÃO-NEGOCIÁVEL** em `.arkan/projects/<projeto>/constitution.md` — remoção requer justificativa excepcional (Governança)
- Toda emenda deve ter justificativa documentada

#### Se ação = Check

**Exibir cabeçalho**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  CONSTITUIÇÃO  ·  MODO: ASSISTÊNCIA
Agente: Constituição  ·  Step: Verificação pontual
Ação esperada: aguardar — analisando arquivo/feature contra princípios
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

1. Extrair alvo de `$ARGUMENTS` (texto após `check`) — pode ser path de arquivo ou nome de feature
2. Se for feature: ler artefatos em `.arkan/features/<feature>/`
3. Se for arquivo: ler o arquivo
4. Verificar contra cada princípio aplicável (Core + Projeto)
5. **Output**: Tabela com resultado por princípio (mesmo formato do Validate, mas escopo reduzido)

#### Se ação = Ingest

**Exibir cabeçalho**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  CONSTITUIÇÃO  ·  MODO: ASSISTÊNCIA
Agente: Constituição  ·  Step: Ingestão de princípios
Ação esperada: revisar propostas extraídas e aprovar/rejeitar individualmente
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

1. Extrair path do documento fonte de `$ARGUMENTS` (texto após `ingest`)
2. Ler o documento fonte
3. Ler a constituição atual
4. **Comparar**: Identificar informações no fonte que:
   - **Não estão na constituição** E têm natureza de princípio, restrição ou gate
   - **Expandem** um princípio existente com detalhes relevantes
   - Descartar informações puramente operacionais (pipelines, métricas de performance, stack detalhado)
5. Para cada candidato, classificar como:
   - **Novo princípio** (P[N+1]) — com nome, descrição e critério de verificação
   - **Expansão de princípio existente** — seção ou critério adicional
   - **Nova restrição de operação** — item na lista de restrições
   - **Novo quality gate** — linha na tabela de gates
6. Apresentar todas as propostas ao desenvolvedor em lista numerada:
   ```
   ## Propostas de Ingestão

   Fonte: [path do documento]
   Propostas: N candidatos identificados

   ### Proposta 1 — [Novo Princípio / Expansão / Restrição / Gate]

   **Tipo**: Novo princípio P7
   **Nome**: [Nome proposto]
   **Conteúdo proposto**:
   > [Texto do princípio]
   > **Critério de verificação**: [Como verificar]

   **Justificativa**: [Por que extrair isso do fonte]

   **Aceitar?** [aguardar resposta]
   ```
7. **Princípio VIII**: Aguardar aprovação **individual** de cada proposta
8. Aplicar propostas aceitas como um único amend (bump MINOR se novos princípios, PATCH se apenas expansões)
9. Ir para Fase 3 (Sync Impact Report)

**Critérios de filtragem para ingest**:
- **Incluir**: Decisões de design, invariantes, restrições arquiteturais, princípios de domínio específicos do projeto, regras de negócio invioláveis
- **Excluir**: Detalhes de implementação, métricas de performance, lista de pipelines, stack tecnológico (já em `stack.md`), FAQs, diagramas operacionais

### Fase 3 — Sync Impact Report (apenas para Amend e Ingest)

Após aplicar emendas, verificar impacto nos templates e agentes:

1. Verificar templates Arkan:
   - `.arkan/templates/03-spec/spec-template.md` — princípios afetam requisitos?
   - `.arkan/templates/04-architecture/plan-template.md` — princípios afetam arquitetura?
   - `.arkan/templates/06-planning/tasks-template.md` — princípios afetam categorização de tasks?
   - `.arkan/templates/08-qa/qa-report-template.md` — novos gates afetam QA?

2. Verificar agentes que referenciam princípios:
   - Buscar referências a princípios alterados em `.arkan/agents/**/*.md`
   - Identificar agentes que precisam de atualização

3. Reportar:
   ```
   ## Sync Impact Report

   | Artefato | Impacto | Ação necessária |
   | --- | --- | --- |
   | spec-template.md | Nenhum / Atualizar | [descrição] |
   | plan-template.md | Nenhum / Atualizar | [descrição] |
   | ... | ... | ... |
   ```

### Fase 4 — Finalização

1. Reportar ao desenvolvedor:
   - Versão atual da constituição (nova se houve emenda)
   - Ações tomadas
   - Commit message sugerido (se houve alteração):
     ```
     chore(arkan): [amend|ingest] constituição vN.N.N — [resumo]
     ```
2. Se houve Sync Impact Report: lembrar desenvolvedor de revisar templates afetados

## Guidelines

- Constituição é a **autoridade máxima** — supersede defaults, preferências e instruções de agentes
- Seção `## Arkan Core` é **intocável** sem aprovação do mantenedor do Arkan + bump MAJOR
- Princípios I (Spec Governa) e II (Gate Obrigatório) **nunca podem ser removidos**
- Princípios do projeto marcados **NÃO-NEGOCIÁVEL** na constituição do projeto são fundamentais — remoção requer justificativa excepcional
- Emendas DEVEM ser explícitas: seção alterada, justificativa, bump de versão e data
- **Princípio VIII**: agente propõe, humano decide — nunca aplicar emenda sem aprovação
- Documentação em **PT-BR**
- Princípios devem ser declarativos e testáveis (usar DEVE/NÃO DEVE, não linguagem vaga)
- Sem `[PLACEHOLDER]` remanescentes após emenda
- Datas em formato ISO YYYY-MM-DD
