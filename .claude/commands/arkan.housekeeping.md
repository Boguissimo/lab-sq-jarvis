---
description: "Arkan transversal — Housekeeping: diagnostico recorrente de debito tecnico e organizacional. MVP: git (branches) + banco (orfas + migrations). Sempre propoe, nunca aplica."
mode: continuo
fase: transversal
nivel: projeto
tecnica: "Schema Reflection + Diff Temporal + Classification-First"
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/memory/constitution.md
comando-disponivel: git

A disponibilidade do MCP de banco declarado em `.arkan/memory/stack.md` é obrigatória somente quando o escopo inclui Banco; no modo `apenas git`, não bloquear a execução por ausência do MCP.

> **Dependência opcional — banco.** Esta parte só roda se `.arkan/memory/stack.md` declarar um banco acessível por servidor de contexto. Sem isso, o comando segue pelo caminho que não toca banco e **declara no artefato** que a verificação de banco não foi feita, em vez de fingir que passou. A rota padrão deste command é a que não usa banco — a área Banco (Fase 2) só roda quando essa dependência está satisfeita.

## PÓS-CONDIÇÕES

arquivo: $REPORT_FILE
campo-obrigatorio: ## Classificacao in $REPORT_FILE
campo-obrigatorio: ## Acoes Propostas in $REPORT_FILE

## Outline

O texto apos `/arkan.housekeeping` e opcional — pode especificar area ou escopo (ex: "apenas git", "apenas orfas", "--area banco"). Se vazio, roda Git sempre; a area Banco entra tambem, mas somente se `.arkan/memory/stack.md` declarar um banco acessivel por servidor de contexto — sem isso, a Fase 2 e pulada (ver `## PRÉ-CONDIÇÕES`).

**Modo Continuo**: este command roda periodicamente (semanal sugerido) e produz um relatorio classificado de debito. Nao altera nada automaticamente — todas as acoes exigem confirmacao explicita do dev (Constitution VIII).

**Principio inviolavel**: `nunca deletar, nunca fechar, nunca pushar`. Housekeeping propoe, humano decide.

### Fase 0 — Setup (automatico)

1. Verificar pre-condicoes: git disponivel; se o escopo incluir Banco, MCP de banco declarado em `.arkan/memory/stack.md` conectado
2. Definir `REPORT_DATE = YYYY-MM-DD` (data de hoje)
3. Definir `REPORT_FILE = .arkan/housekeeping/${REPORT_DATE}-relatorio.md`
4. Criar `.arkan/housekeeping/` se nao existe
5. Verificar se existe relatorio anterior para diff temporal:
   ```bash
   ls .arkan/housekeeping/*.md | sort | tail -2 | head -1
   ```
   - Se existe: modo **comparativo** (destacar novos/resolvidos/persistentes)
   - Se nao existe: modo **inicial** (primeira execucao)

6. **Exibir cabecalho**:
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ARKAN  ·  HOUSEKEEPING  ·  MODO: CONTINUO
   Data: [REPORT_DATE]
   Areas: Git [+ Banco, se `.arkan/memory/stack.md` declarar banco — senao so Git]
   Relatorio anterior: [caminho ou "N/A — primeira execucao"]
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

### Fase 1 — Area Git

> Agente: Investigador silencioso (sem agente dedicado — execucao direta)

Coletar diagnosticos via `git` CLI:

**1.1 — Branches locais orfas**:
```bash
git fetch --prune --dry-run 2>&1 | grep "\\[gone\\]"
```
Classificacao: 🟢 **Auto-safe** (branches ja deletadas no remoto)

**1.2 — Branches com commits nao-pushed**:
```bash
git branch -vv | grep -v "origin/"
```
Para cada uma, contar commits locais:
```bash
git log --oneline origin/main..${branch} 2>/dev/null | wc -l
```
Classificacao: 🟡 **Revisao** (risco de perda se deletar)

**1.3 — Branches abandonadas** (ultimo commit > 30 dias):
```bash
for b in $(git branch --format='%(refname:short)'); do
  last=$(git log -1 --format='%ct' $b)
  age=$(( ($(date +%s) - last) / 86400 ))
  [ $age -gt 30 ] && echo "$b: $age dias"
done
```
Classificacao: 🟡 **Revisao**

**1.4 — Branches com nome de feature concluida**:
- Ler `.arkan/features/*/status.md` para features com `status: em-producao`
- Grep branches locais com slug da feature
- Classificacao: 🟡 **Revisao** (provavel candidata a delete)

**Saida da area Git**: lista de itens com classificacao.

### Fase 2 — Area Banco (Schema Reflection)

Se `.arkan/memory/stack.md` não declarar um banco acessível por servidor de contexto: pular esta fase inteira e registrar no relatório, na seção "Area: Banco", "verificação de banco não realizada — nenhum banco declarado em `.arkan/memory/stack.md`".

> Tool: MCP de banco declarado em `.arkan/memory/stack.md` (leitura apenas)

**2.1 — Divergencia migrations banco vs repo**:

```sql
-- Migrations aplicadas no banco
SELECT name, version FROM schema_migrations ORDER BY version
```

Comparar com o conteudo do diretório de migrações declarado em `.arkan/memory/stack.md` (`ls $DIR_MIGRACOES/*.sql`, onde `$DIR_MIGRACOES` e esse diretorio). Gerar 3 sets:

| Set | Significado | Classificacao |
|-----|-------------|---------------|
| `banco - repo` | Migration aplicada no banco sem arquivo no git | 🔴 **Investigar** |
| `repo - banco` | Arquivo no git nao aplicado no banco | 🟡 **Revisao** (aplicar ou descartar) |
| `banco ∩ repo` | Sincronizadas | 🟢 OK |

**2.2 — Orfas via FK nao-cascata**:

Detectar automaticamente tabelas com `delete_rule = 'NO ACTION'` e contar orfas:

```sql
-- Lista dinamica de FKs NO ACTION
SELECT tc.table_name, kcu.column_name, ccu.table_name AS parent_table, ccu.column_name AS parent_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu USING (constraint_name)
JOIN information_schema.constraint_column_usage ccu USING (constraint_name)
JOIN information_schema.referential_constraints rc USING (constraint_name)
WHERE tc.constraint_type = 'FOREIGN KEY' AND rc.delete_rule = 'NO ACTION'
```

Para cada FK retornada, executar:
```sql
SELECT COUNT(*) FROM {table} f
LEFT JOIN {parent_table} p ON f.{column} = p.{parent_column}
WHERE f.{column} IS NOT NULL AND p.{parent_column} IS NULL
```

Classificacao: 🔴 **Investigar** se `count > 0`, 🟢 OK se zero.

**2.3 — Tabelas nao referenciadas no codigo**:

Para cada tabela em `information_schema.tables`, fazer grep no codebase:
```bash
# $DIRS_CODIGO e $DIR_MIGRACOES vem dos diretórios de código e de migrações
# declarados em .arkan/memory/stack.md
grep -r "\.from(['\"]${tabela}['\"]" $DIRS_CODIGO 2>/dev/null | wc -l
grep -r "\"${tabela}\"" $DIR_MIGRACOES 2>/dev/null | wc -l
```

Classificacao: 🟡 **Revisao** se zero referencias no codigo E > 0 rows (pode ser tabela ativa mas acessada via RPC que nao detectamos). 🟢 OK caso contrario.

**Saida da area Banco**: lista de itens classificados.

### Fase 3 — Consolidacao & Diff Temporal

**3.1 — Montar relatorio bruto** com todos os itens das fases 1 e 2.

**3.2 — Se existe relatorio anterior**, computar diff:

- 🆕 **Novos**: itens no relatorio atual mas nao no anterior
- ✅ **Resolvidos**: itens no anterior mas nao no atual
- 🔁 **Persistentes**: itens em ambos (contar quantas execucoes persistem)

Itens persistentes por 3+ execucoes viram 🔴 **Investigar** (problema cronico).

**3.3 — Exibir resumo ao dev**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  HOUSEKEEPING  ·  RESUMO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Git:
  🟢 Auto-safe:     [N] itens
  🟡 Revisao:       [N] itens
  🔴 Investigar:    [N] itens

Banco:
  🟢 OK:            [N] itens
  🟡 Revisao:       [N] itens
  🔴 Investigar:    [N] itens

Diff desde [data_anterior]:
  🆕 Novos:         [N] itens
  ✅ Resolvidos:    [N] itens
  🔁 Persistentes:  [N] itens ([X] ha 3+ execucoes)

Relatorio completo: [REPORT_FILE]

Deseja revisar item-por-item? (sim / nao / apenas-vermelho)
```

### Fase 4 — Aprovacao Item-Por-Item

Apenas se dev aceita revisar.

Para cada item (em ordem de severidade: 🔴 → 🟡 → 🟢):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ITEM [N/total]  ·  [area]  ·  [classificacao]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Descricao: [o que foi encontrado]
Evidencia: [comando/query que detectou]
Historico: [primeira vez detectado / persiste ha X execucoes]

Acao sugerida: [o que o dev poderia fazer]
  Comando: [comando exato — dev copia e executa se quiser]

(A) Aceitar sugestao (registrar no log como "aceito")
(I) Ignorar item (marcar como "nao aplicavel")
(P) Pular para proximo sem classificar
(Q) Sair e salvar relatorio parcial
```

**Importante**: o skill **nunca executa** o comando automaticamente. Apenas exibe para o dev copiar/colar. Aceitar apenas registra a decisao no log.

### Fase 5 — Salvar Relatorio

Salvar `REPORT_FILE` com formato:

```markdown
# Housekeeping Report — YYYY-MM-DD

> **Modo**: comparativo / inicial
> **Areas**: Git [+ Banco, se declarado em `.arkan/memory/stack.md` / apenas Git — banco nao declarado]
> **Total de itens**: N
> **Relatorio anterior**: [caminho ou "N/A"]

---

## Classificacao

| Severidade | Git | Banco | Total |
|------------|-----|-------|-------|
| 🔴 Investigar | N | N | N |
| 🟡 Revisao | N | N | N |
| 🟢 OK | N | N | N |

---

## Area: Git

### 🔴 Investigar

(nenhum)

### 🟡 Revisao

#### Item 1 — Branch abandonada: `feat/old-feature`
- **Evidencia**: ultimo commit ha 45 dias
- **Comando sugerido**: `git branch -D feat/old-feature` (apenas se confirmado merged)
- **Decisao do dev**: [aceito / ignorado / pendente]

### 🟢 Auto-safe

#### Item N — Branch local orfa: `feat/xyz`
- **Evidencia**: `git fetch --prune --dry-run` retorna `[gone]`
- **Comando sugerido**: `git branch -d feat/xyz`
- **Decisao do dev**: [aceito / ignorado / pendente]

---

## Area: Banco

### 🔴 Investigar

#### Item 1 — Migration aplicada no banco sem arquivo no repo
- **Evidência**: `fix_rpcs_tabela_renomeada` (20260408184607) está aplicada no banco mas não existe no diretório de migrações declarado em `.arkan/memory/stack.md`
- **Acao sugerida**: investigar com o dev que aplicou (git blame do deploy) + criar migration equivalente no repo
- **Decisao do dev**: [aceito / ignorado / pendente]

### 🟡 Revisao

#### Item N — Orfa em `pedidos.categoria_id`
- **Evidencia**: 3 rows referenciam `categorias.id` que nao existe mais
- **Comando sugerido**:
  ```sql
  SELECT id, categoria_id FROM pedidos
  WHERE categoria_id NOT IN (SELECT id FROM categorias);
  ```
- **Decisao do dev**: [aceito / ignorado / pendente]

---

## Acoes Propostas

(lista consolidada das acoes aceitas pelo dev nesta execucao)

1. `git fetch --prune` — limpar 3 branches gone
2. Investigar migration `fix_rpcs_tabela_renomeada` (divergencia banco↔repo)

---

## Diff Temporal

### 🆕 Novos itens (N)

- Item X da area Y

### ✅ Resolvidos desde [data_anterior] (N)

- Item W que nao aparece mais

### 🔁 Persistentes (N)

- Item Z — 3 execucoes consecutivas → escalar para 🔴 Investigar
```

### Fase 6 — Sugestao de Periodicidade

Ao final, sugerir ao dev:

```
Sugestao de periodicidade:
  - Se total de itens 🔴 > 0: proxima execucao em 3 dias
  - Se total de itens 🟡 > 10: proxima execucao em 7 dias
  - Caso contrario: proxima execucao em 14 dias

Para agendar: /schedule /arkan.housekeeping weekly
```

## Guidelines

- Documentacao em **PT-BR**
- **Constitution VIII inviolavel**: nunca aplicar acao sem confirmacao explicita
- **Principio inviolavel**: `nunca deletar, nunca fechar, nunca pushar` automaticamente
- **Schema reflection**: nunca hardcodar nomes de tabelas — sempre ler `information_schema`
> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.
- **Cascata de confianca**: arkan-kb (ou busca por texto, se não houver indexador) → grep (registrar qual foi usada)
- **Falsos positivos**: marcar como "provavel" quando nao-confirmado
- **Relatorio append-only**: cada execucao e um novo arquivo (nao sobrescrever)
- **Threshold configuravel**: valores default (30 dias branch, 14 dias feature) podem ser tunados em `.arkan/housekeeping.config.md`
- **Tempo maximo**: 15 minutos de execucao total — se exceder, parar e reportar parcial
- **MVP atual**: Git sempre; Banco quando `.arkan/memory/stack.md` declarar banco acessivel por servidor de contexto (sem isso, so Git). Futuras areas (Artefatos, Codigo Morto, Infraestrutura de Jobs, GitHub) em execucoes posteriores
- **Separacao de responsabilidades**:
  - `arkan.audit` → profundo, por feature, sob demanda
  - `arkan.ops` → por feature em producao
  - `arkan.housekeeping` → transversal, recorrente, raso mas amplo
