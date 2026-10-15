# Deploy Checklist: [NOME DA FEATURE]

> **Feature**: [NNN-short-name]
> **Input**: [qa-report.md](../08-qa/qa-report.md)
> **Data**: [DATA]
> **Executado por**: [Nome / Agente]

<!--
  IMPORTANTE: Cada item requer confirmação explícita do desenvolvedor.
  Nenhuma etapa é executada automaticamente sem confirmação.
  Marcar [x] apenas após verificação real — não marcar preventivamente.

  CLASSIFICAÇÃO DE ITENS:
  - [BLOQUEANTE]: deploy NÃO prossegue sem este item verificado. Sem exceções.
  - [AVISO]: registrar justificativa se não verificado e prosseguir com aprovação explícita.

  Se qualquer item BLOQUEANTE permanecer [ ], o resultado final NÃO pode ser SUCESSO.
-->

---

## Pré-requisitos para iniciar

Verificar antes de começar qualquer etapa de deploy:

- [ ] **[BLOQUEANTE]** QA aprovado (`08-qa/qa-report.md` com status APROVADO ou APROVADO COM RESSALVAS)
- [ ] **[BLOQUEANTE]** Todos os bloqueadores do QA resolvidos
- [ ] **[BLOQUEANTE]** Branch atual é a branch da feature (`[NNN-short-name]`)
- [ ] **[AVISO]** Código commitado e sem mudanças não commitadas (`git status` limpo)
- [ ] **[BLOQUEANTE]** Desenvolvedor confirmou que pode prosseguir com o deploy

**Confirmação do desenvolvedor**: ☐ SIM, prosseguir com o deploy

---

## Fase 1 — Pré-Deploy

<!--
  Verificações e preparações antes de qualquer mudança no ambiente de produção.
-->

- [ ] **[AVISO]** **Backup**: estado atual do ambiente de produção documentado ou backup criado
  - Observação: [como foi feito o backup]
- [ ] **[AVISO]** **Dependências**: todas as dependências necessárias estão disponíveis em produção
  - Dependências verificadas: [listar]
- [ ] **[AVISO]** **Variáveis de ambiente**: variáveis necessárias configuradas em produção
  - Variáveis verificadas: [listar sem valores]
- [ ] **[AVISO]** **Migrações**: migrações de dados (se houver) testadas em ambiente de staging
- [ ] **[BLOQUEANTE]** **Rollback plan**: plano de rollback documentado abaixo
  - Plano de rollback: [descrever como reverter se algo der errado]
- [ ] **[BLOQUEANTE — apenas se `superficie-critica: sim`]** **Gatilho de rollback de produto**: regra escrita ANTES do deploy (ex.: "se a métrica-alvo piora junto com o risco monitorado → rollback")
  - Métrica monitorada: [a métrica das Obrigações da Superfície Crítica da ideação / SC correspondente da spec]
  - Limiar e janela: [ex.: métrica do público afetado piora mais que X em N dias → reverter]
  - Como será lido: [instrumento do SC — query/evento/procedimento]

**Confirmação do desenvolvedor antes de prosseguir para deploy**: ☐ SIM

---

## Fase 2 — Deploy

<!--
  Execução do deploy. Cada comando deve ser confirmado antes de executar.
  Registrar o que foi executado e o resultado.
-->

- [ ] **[BLOQUEANTE]** **Build**: build de produção gerado sem erros
  - Comando: `[comando de build]`
  - Resultado: ☐ Sucesso  /  ☐ Falha — [descrição]
- [ ] **[BLOQUEANTE]** **Deploy executado**: código publicado em produção
  - Comando / método: `[comando ou processo]`
  - Resultado: ☐ Sucesso  /  ☐ Falha — [descrição]
- [ ] **[AVISO]** **Migrações executadas** (se houver): mudanças de dados aplicadas
  - Resultado: ☐ Sucesso  /  ☐ N/A

**Se qualquer etapa BLOQUEANTE falhar**: PARAR imediatamente — não prosseguir; executar rollback.

---

## Fase 3 — Pós-Deploy (Verificação)

<!--
  Verificar que a feature está funcionando corretamente em produção.
  Testar os cenários críticos da spec.
-->

- [ ] **[BLOQUEANTE]** **Smoke test**: funcionalidade principal funciona em produção
  - Cenário testado: [descrição do teste mínimo]
  - Resultado: ☐ PASS  /  ☐ FAIL
- [ ] **[AVISO]** **Cenários P1 verificados**: user stories P1 funcionam em produção
  - US1 — [título]: ☐ PASS  /  ☐ FAIL
  - US2 — [título]: ☐ PASS  /  ☐ FAIL (se aplicável)
- [ ] **[AVISO]** **Sem regressões**: funcionalidades existentes não foram quebradas
  - Verificado: [o que foi testado]
- [ ] **[AVISO]** **Monitoramento**: erros imediatos verificados (logs disponíveis localmente)

**Confirmação final do desenvolvedor**: ☐ Deploy concluído e verificado

---

## Resultado do Deploy

<!--
  REGRA DE STATUS:
  - SUCESSO: todos os itens BLOQUEANTE são [x] E desenvolvedor confirmou
  - COM DESVIOS: todos os BLOQUEANTE são [x] mas há AVISO não verificados (listar justificativas)
  - FALHA: algum BLOQUEANTE permaneceu [ ] ou rollback foi executado
  - PARCIAL: deploy interrompido antes de concluir todas as fases
-->

**Status**: ☐ SUCESSO  /  ☐ COM DESVIOS  /  ☐ FALHA  /  ☐ PARCIAL

**Itens BLOQUEANTE verificados**: [N/N]

**Itens AVISO não verificados** (se houver):

- [Item]: [justificativa para prosseguir sem verificação]

**Data/hora de conclusão**: [DATA HORA]

**Observações**: [Qualquer informação relevante sobre o processo]

---

## Rollback (se necessário)

**Decisão de rollback**: ☐ SIM — executar rollback  /  ☐ NÃO — manter e corrigir

Se rollback:

- [ ] Código revertido para versão anterior
- [ ] Migrações revertidas (se possível e necessário)
- [ ] Ambiente restaurado ao estado pré-deploy
- [ ] Confirmado que sistema está estável após rollback

**Status após rollback**: [descrever estado final]
