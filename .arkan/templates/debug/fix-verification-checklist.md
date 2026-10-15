# Checklist de Verificacao de Fix

> Usar apos aplicar correcao de bug. Preencher antes de registrar o bug-report como "Corrigido".

---

## Alinhamento Spec↔Codigo (Aligner)

- [ ] Aligner invocado com spec.md + codigo corrigido
- [ ] Nenhuma divergencia spec→codigo introduzida pelo fix
- [ ] Se divergencia encontrada: justificada como Clarification ou corrigida

> Se feature nao possui spec.md: marcar como N/A e registrar limitacao no bug-report.

---

## Nao-Regressao Funcional

- [ ] Fix resolve o sintoma original (reproduzir e confirmar)
- [ ] Fluxos adjacentes ao ponto do fix continuam funcionando
- [ ] Edge cases da spec (se existem) nao foram quebrados
- [ ] Invariantes da feature permanecem validos

---

## Nao-Regressao Tecnica

- [ ] TypeScript compila sem erros (comando de type-check do projeto, no diretório de código afetado — ambos declarados em `.arkan/memory/stack.md`)
- [ ] Lint passa (comando de lint do projeto, declarado em `.arkan/memory/stack.md`)
- [ ] Nenhum import quebrado ou dependencia circular introduzida
- [ ] Migrations (se alteradas) aplicam sem erro

---

## Impacto Cross-Feature (se aplicavel)

- [ ] Análise de impacto executada no símbolo modificado (arkan-kb, ou indexador de código declarado em `.arkan/memory/stack.md`, ou leitura direta — o que estiver disponível)
- [ ] Nenhum caller direto (d=1) quebrado
- [ ] Features dependentes notificadas se impacto d=2+

---

## Prevenção da Classe

- [ ] O que impediria esta classe de bug foi identificado (teste/constraint/lint/gate) — registrado no bug-report, seção Prevenção
- [ ] Prevenção aplicada nesta correção, OU registrada como tech debt (TD-NNN) em `10-ops/`

---

## Resultado

- [ ] **APROVADO** — fix verificado, pronto para registro
- [ ] **REPROVADO** — motivo: [descrever o que falhou]
