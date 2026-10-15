# Bug Report: [BUG-ID]

> **Feature**: [NNN-slug ou "orfao"]
> **Classificacao**: [Logica | UI/UX | Integracao | Dependencia | Dados | Ambiente]
> **Modo**: [Desenvolvimento | Producao]
> **Severidade**: [Critica | Alta | Media | Baixa]
> **Data**: [YYYY-MM-DD]
> **Status**: [Aberto | Corrigido | Nao-reproduzivel]

---

## 1. Sintoma

### Descricao

[O que foi observado. Comportamento esperado vs comportamento real.]

### Evidencias

- **Erro/Stack trace**: [se disponivel]
- **Logs relevantes**: [se disponivel]
- **Screenshot/URL**: [se disponivel]

### Contexto de descoberta

- **Onde**: [app/pagina/endpoint/job onde o bug foi observado]
- **Quando**: [momento — durante teste, em producao, apos deploy]
- **Quem reportou**: [dev/usuario/monitoramento]

---

## 2. Reproducao

### Passos para reproduzir

1. [Passo 1]
2. [Passo 2]
3. [Resultado observado]

### Reproduzivel?

- [ ] Sim — 100% das vezes
- [ ] Sim — intermitente (frequencia: ~X%)
- [ ] Nao reproduzido ainda

### Ambiente de reproducao

- **Branch**: [branch git]
- **Node**: [versao]
- **SO**: [Windows/Linux/Mac]
- **Banco**: [local/cloud/branch]

---

## 3. Isolamento

### Camada afetada

- [ ] Frontend (web/admin/app)
- [ ] Backend (API routes/RPC)
- [ ] Banco de dados (migrations/RLS/data)
- [ ] Worker / processamento assíncrono (fila, jobs agendados, execução durável)
- [ ] Infra/Config (env vars, deploy, CI)

### Escopo do impacto

- **Arquivos envolvidos**: [lista]
- **Features afetadas**: [lista se cross-feature]
- **Usuarios afetados**: [N/estimativa — apenas modo producao]

---

## 4. Causa Raiz

### Hipoteses investigadas

| # | Hipotese | Status | Evidencia |
|---|----------|--------|-----------|
| 1 | [Hipotese A] | Confirmada / Descartada | [onde no codigo] |
| 2 | [Hipotese B] | Confirmada / Descartada | [onde no codigo] |

### Causa raiz confirmada

[Descricao precisa da causa raiz. Referenciar arquivo:linha.]

### Ferramentas usadas na investigacao

- [ ] arkan-kb (query/context/detect_changes)
- [ ] Indexador de código declarado em `.arkan/memory/stack.md`
- [ ] grep/glob (fallback)
- [ ] Leitura direta de codigo

---

## 5. Correcao

### Fix aplicado

[Descricao do fix. Referenciar arquivo:linha modificado.]

### Arquivos modificados

| Arquivo | Tipo de mudanca |
|---------|----------------|
| [caminho] | [novo/modificado/removido] |

### Alternativas consideradas

[Se houve alternativa descartada, justificar brevemente.]

---

## 6. Verificacao

### Aligner (spec↔codigo)

- **Executado**: [Sim/Nao/N/A — sem spec.md]
- **Resultado**: [Alinhado / Divergencia encontrada: detalhe]

### Checklist de nao-regressao

- [ ] Fix resolve o sintoma original
- [ ] Fix nao introduz novos erros visuais
- [ ] Fix nao quebra fluxos adjacentes
- [ ] Invariantes da feature respeitados
- [ ] Tipos TypeScript compilam sem erro (se aplicavel)

---

## 7. Registro

### Prevenção

<!--
  O que impediria esta CLASSE de bug de voltar — não este bug específico.
  Preencher sempre: prevenção não aplicada vira tech debt rastreado, nunca omissão.
-->

- **O que impediria esta classe**: [teste automatizado / constraint no banco / regra de lint / gate no pipeline / N/A — justificar]
- **Aplicado nesta correção?** [Sim — onde] / [Não — registrado como TD-NNN em `10-ops/`]

### Resumo (para bugfixes.md)

- **ID**: [BUG-YYYYMMDD-NNN]
- **Feature**: [NNN-slug ou "orfao"]
- **Classificacao**: [tipo]
- **Causa raiz**: [1 linha]
- **Fix**: [1 linha]
- **Data**: [YYYY-MM-DD]

### Retroalimentacao

- [ ] Entrada adicionada em `.arkan/memory/bugfixes.md`
- [ ] Bug-report salvo em `[feature]/debug/` ou `.arkan/debug/`
- [ ] Referenciado em `10-ops/` (apenas modo producao)
