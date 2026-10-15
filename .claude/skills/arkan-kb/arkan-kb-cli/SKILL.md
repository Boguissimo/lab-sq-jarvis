---
name: arkan-kb-cli
description: "Use when the user needs to run Arkan-KB CLI commands like analyze/index the project, query from terminal, audit coverage, or export the graph. Examples: \"Index this repo\", \"Reanalyze the codebase\", \"Export the knowledge graph\""
---

# Arkan-KB CLI Commands

The CLI is available via the local package binary, once `arkan-kb/` is installed and built
(`cd arkan-kb && <gerenciador de pacotes> install && <gerenciador de pacotes> run build`).

## Commands

### analyze — Build or refresh the index

```bash
node arkan-kb/dist/cli/index.js analyze
```

Run from the project root. Parses all spec files (`.arkan/features/`), source code, and SQL migrations. Builds the unified knowledge graph and writes it to `.arkan-kb/index.db`.

**When to run:** First time in a project, after major code or spec changes, or when `arkan-kb://status` reports missing index. Full indexation time and database size scale with repository size.

### query — Search from terminal

```bash
node arkan-kb/dist/cli/index.js query "auth validation"
```

Returns ranked results across specs and code. Useful for quick lookups outside of MCP context.

### suggest-annotations — Propose @@TXXX annotations

```bash
node arkan-kb/dist/cli/index.js suggest-annotations
```

Scans source files and proposes `// @@TXXX` traceability annotations linking code to spec tasks. Review suggestions before applying.

### audit-coverage — Spec-code coverage report

```bash
node arkan-kb/dist/cli/index.js audit-coverage
```

Reports tasks without `File:` references, unannotated code symbols, and orphan files not linked to any feature.

### export-graph — Export for visualization

```bash
node arkan-kb/dist/cli/index.js export-graph
```

Exports the graph to `grafo-data.json`. No bundled viewer ships with this package — bring your own visualization tool for the JSON, or open an issue if you'd like one contributed.

## After Indexing

1. **Read `arkan-kb://status`** to verify the index loaded
2. Use the other Arkan-KB skills (`exploring`, `debugging`, `impact-analysis`, `auditing`) for your task

## Troubleshooting

- **"Indice Arkan-KB nao encontrado"**: Run `analyze` from the project root
- **Index is stale after code changes**: Re-run `analyze` — it does incremental updates
- **Large codebase slow**: Indexing time scales with the number of code, spec, and SQL files — it is normally a matter of seconds, not minutes
