# Tasks: [NOME DA FEATURE]

**Input**: [spec.md](../03-spec/spec.md) | [plan.md](../04-architecture/plan.md)
**Pré-requisitos**: spec.md ✓ | plan.md ✓

## Formato: `[ID] [P?] [Story] Descrição`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência)
- **[Story]**: user story que a task implementa (US1, US2, ...)
- Cada task DEVE especificar `File: caminho/para/arquivo`

---

## Fase 1: Setup (Infraestrutura Compartilhada)

**Propósito**: inicialização do projeto e estrutura base.

- [ ] T001 [Descrição da task de setup]
  - File: `caminho/para/arquivo`
- [ ] T002 [P] [Descrição de task paralela de setup]
  - File: `caminho/para/arquivo`

**Checkpoint**: fundação pronta — user stories podem começar.

---

## Fase 2: Fundação (Pré-requisitos Bloqueantes)

**Propósito**: infraestrutura que DEVE estar completa antes de qualquer user story.

**⚠️ CRÍTICO**: nenhuma implementação de user story antes desta fase.

- [ ] T003 [Descrição do pré-requisito bloqueante]
  - File: `caminho/para/arquivo`

**Checkpoint**: fundação completa — user stories podem prosseguir.

---

## Fase 3: User Story 1 — [Título] (Prioridade: P1)

**Goal**: [O que esta story entrega.]

**Independent Test**: [Como verificar que a story funciona de forma isolada.]

- [ ] T004 [P] [US1] [Descrição da task]
  - File: `caminho/para/arquivo`
- [ ] T005 [US1] [Descrição da task] (depende de T004)
  - File: `caminho/para/arquivo`

**Checkpoint**: US1 completa e testável independentemente.

---

## Fase 4: User Story 2 — [Título] (Prioridade: P2)

**Goal**: [O que esta story entrega.]

**Independent Test**: [Como verificar de forma isolada.]

- [ ] T006 [US2] [Descrição da task]
  - File: `caminho/para/arquivo`

**Checkpoint**: US2 completa e testável independentemente.

---

## Fase N: Polish e Aspectos Transversais

**Propósito**: melhorias que afetam múltiplas user stories.

- [ ] TXXX [P] Validar ciclo completo contra critérios de aceitação da spec
- [ ] TXXX Verificar conformidade com Constitution (invariantes 1-5+)

---

## Dependências e Ordem de Execução

### Dependências entre Fases

- **Fase 1 (Setup)**: sem dependências — iniciar imediatamente
- **Fase 2 (Fundação)**: depende da Fase 1 — BLOQUEANTE para todas as user stories
- **Fases 3+ (User Stories)**: dependem da Fase 2; podem prosseguir em paralelo após fundação
- **Polish**: depende das user stories desejadas completas

### Oportunidades de Paralelismo

- Tasks marcadas `[P]` dentro de uma fase: podem rodar simultaneamente
- User stories diferentes: podem ser desenvolvidas em paralelo após fundação

---

## Estratégia de Implementação

### MVP (Apenas P1)

1. Completar Fase 1 + Fase 2
2. Completar Fase 3 (US1)
3. **PARAR e VALIDAR**: testar US1 de forma isolada
4. Deploy/demo se pronto

### Entrega Incremental

1. Setup + Fundação → base pronta
2. US1 → testar → demo (MVP)
3. US2 → testar → demo
4. Cada story adiciona valor sem quebrar as anteriores
