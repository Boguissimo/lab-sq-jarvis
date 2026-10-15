# Spec (simplificada, peso Doc) — 001-000-fundacao-projeto

> **Status**: aprovada (G3, 2026-10-15 — JV-D042)

## Cenários de Usuário

- Como desenvolvedor, quero ler a base normativa ratificada e saber exatamente o que foi aprovado e o que continua provisório, antes de o primeiro incremento ser construído.

## Requirements

| ID | Entregável | Critério de aceitação |
| --- | --- | --- |
| FR-001 | Constituição v0.4.0 ratificada | estado “ratificada” com citação do desenvolvedor; P1 com decisão sem intervenção; P2 com reversão não garantida |
| FR-002 | Regras de segurança v0.4.0 | SEG-13 com valores acessíveis e origem; declaração de que provisórios continuam provisórios |
| FR-003 | Proposta consolidada aprovada | reversão (JV-D040), conferência (JV-D039), decisão sem intervenção (JV-D038) no texto e no modelo de dados |
| FR-004 | Feature map v4 | regras de entrega parcial, status `parcial (JV-Vxx)`, registro de entregas |
| FR-005 | Registro de decisões | JV-D038 a JV-D042 com estados; aprovações de JV-D011, JV-D015, JV-D016, JV-D032, JV-D034, JV-D037 |
| FR-006 | Projeto em `features-definidas` | `status.md` do projeto atualizado pelo script oficial |

## Invariantes

- INV-001: o Core do Arkan não é alterado. Teste: `diff -r` de `.arkan/scripts`, `.arkan/templates`, `.claude/commands`, `.arkan/agents` (exceto o agente de domínio) e `.arkan/memory/constitution.md` contra a cópia de referência.
- INV-002: nenhum valor marcado como provisório deixa de sê-lo. Teste: busca por “provisório” em `regras-de-seguranca.md` antes e depois mostra os mesmos itens.

## Critérios de sucesso

- SC-001: FR-001 a FR-006 atendidos. Instrumento: revisão do diff da feature.
