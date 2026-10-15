# Plano de Implementação: [NOME DA FEATURE]

**Branch**: `[NNN-short-name]` | **Data**: [DATA] | **Spec**: `03-spec/spec.md`

---

## Sumário

[Extraído da spec: requisito principal + abordagem técnica escolhida. Máximo 3 linhas.]

---

## Contexto Técnico

**Linguagem/Runtime**: [ex: TypeScript 5.x, Python 3.12, Bash]
**Dependências Principais**: [ex.: framework web do projeto, banco de dados, ferramenta de IA usada — o que o projeto realmente usa]
**Storage**: [ex: sistema de arquivos, PostgreSQL, N/A]
**Testes**: [ex: execução dos commands em feature de teste, pytest, N/A]
**Plataforma**: [ex: Claude Code CLI (Windows/Git Bash + Unix/zsh)]
**Tipo de Projeto**: [ex: meta-ferramenta, SaaS, API, CLI]
**Metas de Performance**: [ex: N/A — I/O de arquivos é o gargalo]
**Restrições**: [ex: sem dependências externas além de git + bash]
**Escala**: [ex: single-developer, até centenas de features]

---

## Constitution Check

**Arquivos**: `.arkan/memory/constitution.md` (core) + `.arkan/projects/<projeto>/constitution.md` (princípios do projeto)

### Core (I–VIII)

| Princípio | Verificação |
| --- | --- |
| I. Spec Governa Código | [PASS/FAIL — justificativa] |
| II. Gate Obrigatório | [PASS/FAIL — justificativa] |
| III. Conclusividade | [PASS/FAIL — justificativa] |
| IV. Modo Declarado | [PASS/FAIL — justificativa] |
| V. PT-BR First | [PASS/FAIL — justificativa] |
| VI. Especialização por Modo | [PASS/FAIL — justificativa] |
| VII. Independência Estrutural | [PASS/FAIL — justificativa] |
| VIII. Agente Propõe, Humano Decide | [PASS/FAIL — justificativa] |

### Projeto (P1..Pn)

<!--
  Ler os princípios VIGENTES da constituição do projeto e listar TODOS —
  não copiar uma lista fixa: princípios emendados/novos entram automaticamente.
  Princípio não aplicável a esta feature: marcar N/A com justificativa de uma linha.
-->

| Princípio | Verificação |
| --- | --- |
| P1. [Nome] | [PASS/FAIL/N/A — justificativa] |
| P2. [Nome] | [PASS/FAIL/N/A — justificativa] |
| Pn. [Nome] | [PASS/FAIL/N/A — justificativa] |

**Resultado**: PASS / FAIL

---

## Estrutura do Projeto

### Documentação (esta feature)

```text
.arkan/features/[NNN-nome]/
├── 01-discovery/
│   └── ideacao.md
├── 03-spec/
│   └── spec.md
├── 04-architecture/
│   ├── plan.md              # Este arquivo
│   ├── research.md
│   ├── data-model.md
│   ├── contracts/
│   └── quickstart.md
├── 06-planning/
│   └── tasks.md
└── status.md
```

### Código-fonte (raiz do repositório)

```text
[Estrutura real de arquivos a criar/modificar — caminhos concretos]
```

---

## ADRs — Decisões de Arquitetura

### ADR-001: [Título da decisão]

**Status**: Aceito / Proposto / Deprecado
**Contexto**: [Por que esta decisão foi necessária.]
**Decisão**: [O que foi decidido.]
**Alternativas descartadas**: [A — por que não; B — por que não] OU "Nenhuma considerada — [por quê]"
**Consequências**: [O que muda. Limitações conhecidas.]

---

## Dependências e Interfaces

### Dependências (esta feature CONSOME)

| Recurso | Feature de origem | Contrato | Impacto se mudar |
| --- | --- | --- | --- |
| [Recurso] | [Feature ou sistema externo] | [Contrato de uso] | [O que quebra] |

*Se nenhuma dependência externa: "Nenhuma dependência externa."*

### Interfaces Expostas (outras features CONSOMEM)

| Recurso | Consumidores | Contrato que NÃO mudar |
| --- | --- | --- |
| [Recurso exposto] | [Quem consome] | [Garantia de compatibilidade] |

*Se nenhuma interface exposta: "Nenhuma interface exposta."*

---

## Mapa de Agentes por Fase

| Fase | Modo | Command | Agente(s) | Técnica(s) | Artefato de Saída |
| --- | --- | --- | --- | --- | --- |
| [NN — Nome] | [Assistência/Geração/Orquestração/Contínuo] | `arkan.[cmd]` | [Agente] | [Técnica] | `[caminho/artefato.md]` |

---

## Sequência de Implementação Recomendada

### Fase 0 — Fundação

1. [Item bloqueante 1]
2. [Item bloqueante 2]

### Fase 1 — [User Story P1]

1. [Task principal 1]
2. [Task principal 2]

### Fase N — Polish

1. [Validação final]
2. [Testes de integração]
