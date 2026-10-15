---
name: arkan-kb-guide
description: "Use when the user asks about Arkan-KB itself — available tools, how to query the knowledge graph, MCP resource, graph schema, or workflow reference. Examples: \"What Arkan-KB tools are available?\", \"How do I use Arkan-KB?\""
---

# Arkan-KB Guide

Quick reference for all Arkan-KB MCP tools, resource, and the unified knowledge graph schema (specs + code).

## Always Start Here

For any task involving code understanding, spec traceability, debugging, impact analysis, or auditing:

1. **Read `arkan-kb://status`** — index stats, node counts, check freshness
2. **Match your task to a skill below** and **read that skill file**
3. **Follow the skill's workflow and checklist**

> If step 1 warns the index is missing, run `node arkan-kb/dist/cli/index.js analyze` in terminal.

## Skills

| Task                                              | Skill to read              |
| ------------------------------------------------- | --------------------------- |
| Understand architecture / "How does X work?"       | `arkan-kb-exploring`       |
| Blast radius / "What breaks if I change X?"        | `arkan-kb-impact-analysis` |
| Trace bugs / "Why is X failing?"                   | `arkan-kb-debugging`       |
| Spec coverage / "What's missing?"                  | `arkan-kb-auditing`        |
| Tools, resource, schema reference                  | `arkan-kb-guide` (this file) |
| Index, CLI commands                                | `arkan-kb-cli`             |

## Tools Reference

| Tool              | What it gives you                                                          |
| ----------------- | ---------------------------------------------------------------------------- |
| `query`           | Ranked search across specs + code — nodes grouped by relevance             |
| `context`         | 360-degree view — definition, callers, callees, and features involved      |
| `impact`          | Blast radius — what breaks at depth 1/2/3 with risk level                  |
| `detect_changes`  | Git-diff impact — maps changed files to affected symbols and features      |
| `audit_coverage`  | Spec-code coverage gaps — tasks without File:, unannotated symbols, orphans |
| `annotate`        | Suggest or apply `@@TXXX` traceability annotations in source code          |
| `validate`        | Check Constitution constraints (P1, P5, P9) for violations                 |

## Resource

| Resource            | Content                              |
| -------------------- | ------------------------------------- |
| `arkan-kb://status` | Index stats, node counts by label    |

## Graph Schema

**Node labels:** SpecElement, CodeSymbol, SQLObject, Feature, Task, File
**Edge types:** IMPLEMENTS_FR, VALIDATES_INV, CALLS, IMPORTS, DEFINES, BELONGS_TO, DEPENDS_ON, COVERS

Nodes have properties: `name`, `filePath`, `label`, `type`, `feature`

## Cascading Discovery

When a tool returns empty or the index is unavailable, fall back:

```
1. mcp__arkan-kb__* (preferred)
2. Grep/Glob directly over the project's code directories (fallback — no dependency graph, no spec traceability)
```

## Refactoring Note

Arkan-KB does not include a `rename` tool. For safe multi-file renames, use the **IDE Rename
Symbol** (AST-aware) and validate with `mcp__arkan-kb__query` (or a Grep) before and after to
confirm caller parity.
