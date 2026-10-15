# Tasks: Teste

**Input**: spec.md | plan.md
**Pre-requisitos**: spec.md ✓ | plan.md ✓

---

## Fase 1: Setup

**Proposito**: inicializacao do projeto.

- [ ] T001 Criar package.json
  - File: `packages/teste/package.json`
- [ ] T002 [P] Criar tsconfig.json
  - File: `packages/teste/tsconfig.json`

**Checkpoint**: build passa.

---

## Fase 2: Core (US1)

**Goal**: funcionalidade principal de busca.

- [ ] T003 [US1] Implementar parser de specs
  - File: `packages/teste/src/parsers/spec-parser.ts`
- [x] T004 [P] [US1] Implementar busca full-text
  - File: `packages/teste/src/analysis/search.ts`
- [ ] T005 [US2] Implementar validacao de invariantes
  - File: `packages/teste/src/analysis/constraints.ts`

---

## Fase 3: Polish

**Proposito**: validacao final.

- [ ] T006 [P] Validar criterios de aceitacao
- [ ] T007 Verificar conformidade com invariantes
