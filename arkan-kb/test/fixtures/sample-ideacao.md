# Ideacao: Teste

> **Feature**: 001-teste
> **Data**: 2026-03-24

---

## Registro de Decisoes

### D1 — Formato de persistencia

**Contexto**: Precisamos escolher como armazenar o grafo.

**Alternativas consideradas**:
- A) SQLite embarcado
- B) PostgreSQL

**Decisao**: Opcao A — SQLite embarcado

**Fundamentacao**: Zero dependencia externa. Funciona offline. Performance adequada para grafos de ate 50K nos.

---

### D2 — Parser de specs

**Contexto**: Como extrair informacao estruturada de Markdown.

**Alternativas consideradas**:
- A) Regex puro
- B) remark AST + regex

**Decisao**: Opcao B — remark AST + regex

**Fundamentacao**: AST fornece estrutura robusta. Regex complementa para patterns inline como FR-001, INV-001.

---

## Sintese

O sistema usa SQLite embarcado para persistencia e remark+regex para parsing de Markdown.
