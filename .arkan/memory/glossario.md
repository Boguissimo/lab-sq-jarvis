# Glossário do Arkan

> Termos de domínio definidos de forma unívoca. Agentes usam este glossário para garantir consistência semântica entre artefatos.
> **Fonte canônica**: spec.md `## Key Entities` + ideacao.md `## Síntese`.

---

## Projeto

Container de desenvolvimento de um sistema complexo. Armazenado em `.arkan/projects/{slug}/`, abrange as fases 01-02 (Discovery + Proposta) e produz o `feature-map.md` como artefato central. Um repositório pode conter múltiplos projetos (multi-projeto). Ativado via `/arkan.projeto`. Mantém `projects/{slug}/status.md` com estados: `em-discovery` → `em-proposta` → `features-definidas`.

**Resolução de projeto ativo**: argumento explícito (`--project`) → branch git (`{projeto}/{NNN-CCC-slug}`) → campo `projeto-default` em `.arkan/config.md` → único projeto existente.

**Não confundir com**: Feature (unidade de entrega individual).

---

## Feature Map

Artefato obrigatório produzido pela fase 02 do Projeto (`projects/{projeto}/02-proposal/feature-map.md`). Lista todas as features derivadas do projeto com nome, descrição, prioridade, dependências e status. É o contrato de decomposição — sua aprovação é pré-condição para iniciar qualquer feature derivada.

**Não confundir com**: tasks.md (lista de implementação de uma feature individual).

---

## Feature

Unidade de trabalho do Arkan, identificada por `NNN-CCC-slug` (ex: `101-000-autenticacao`). Organizada em `.arkan/features/{projeto}/`. Tem ciclo de vida de 10 fases (ou menos, dependendo do peso) e `status.md` com estados: `em-desenvolvimento` → `em-producao` → `arquivada`.

**Hierarquia parent/child**:

- `NNN-000-slug` — feature principal (parent). Ex: `109-000-modulo-relatorios`
- `NNN-CCC-slug` (CCC > 000) — sub-feature (child). Ex: `109-001-modulo-relatorios-detalhe`

Pode ser criada de forma autônoma ou derivada de um Projeto via `feature-map.md`.

**Campos do status.md**: `status`, `fase-atual`, `projeto`, `pai` (se child), `peso`, `origem`, `atualizado-em`.

---

## Agente

Especialista Claude com escopo limitado a uma fase específica da pipeline. Cada agente tem: modo de operação declarado, técnica de prompting definida, PRÉ-CONDIÇÕES verificáveis e PÓS-CONDIÇÕES verificáveis. Definido em arquivo próprio em `.arkan/agents/[subdir]/[nome].md` — agentes exclusivos de uma fase ficam em `NN-fase/`; agentes reutilizados por múltiplos commands ficam em `transversal/`. Commands (`.claude/commands/arkan.*.md`) referenciam os agent files e injetam o contexto de runtime (FEATURE_DIR, paths de artefatos).

**Não confundir com**: Step (unidade estrutural da pipeline) ou Task (unidade de implementação).

---

## Artefato

Documento produzido por um agente em uma fase. Válido quando passa todas as verificações declaradas no `## PÓS-CONDIÇÕES` do agente produtor. Deve ser autocontido — o agente seguinte opera lendo apenas os arquivos do diretório da feature, sem consultas externas.

**Exemplos**: `ideacao.md`, `spec.md`, `plan.md`, `tasks.md`, `feature-map.md`.

---

## Gate

Checkpoint executável declarado no arquivo de definição do agente. Composto por `## PRÉ-CONDIÇÕES` (o que deve existir antes) e `## PÓS-CONDIÇÕES` (o que deve existir depois). Executado pelo `check-prerequisites.sh`. Tipos de verificação: `arquivo:` (existência) e `campo-obrigatorio:` (presença de seção markdown).

**Autoridade**: o `check-prerequisites.sh` é a autoridade do gate — não a intenção do agente.

---

## Step

Item atômico da pipeline completa. Steps distribuídos nas 10 fases definem o fluxo de trabalho do Arkan — o número exato de steps não é fixo e pode variar conforme o design da pipeline evolui. Steps são estruturais — existem no design da pipeline, não são criados por agentes.

**Não confundir com**: Task (criada pelo Task Decomposer para implementação de código).

---

## Task

Item atômico de implementação gerado pelo Task Decomposer em `06-planning/tasks.md`. Cada task tem arquivo-alvo, story associada e dependências explícitas. Pode ser marcada como paralela `[P]`.

**Não confundir com**: Step (estrutural) ou Artefato (output de um agente).

---

## Modo de Operação

Determina o comportamento do agente e a técnica de prompting:

| Modo | Fases | Comportamento | Técnica |
| --- | --- | --- | --- |
| **Assistência** | 01-02, 05 | Agente propõe, pausa e aguarda input humano | Socratic + ReAct |
| **Geração** | 03-04, 06-07 | Agente produz artefatos completos com gates | Few-Shot + Structured Output + Gates |
| **Verificação** | 03, 06, 08 | Agente analisa artefatos existentes sem gerar novos; produz relatórios de qualidade | Structured Output + Cross-Reference |
| **Orquestração** | 08-09 | Agente coordena processos externos com raciocínio explícito | ReAct + Chain-of-Thought |
| **Contínuo** | 10 | Agente monitora, ativado manualmente, sem artefato fixo | ReAct + FLARE |

**Verificação** — modo adicionado em v2.0.0. Agentes neste modo:

- Não produzem artefatos de design (spec, plan, tasks)
- Produzem relatórios de qualidade (checklists, análises de consistência, auditorias)
- Exemplos: checklist-writer (03-spec), consistency-analyzer (06-tasks), schema-auditor (08-qa)

---

## Constitution

Sistema de governança em dois níveis:

- **Global** (`.arkan/memory/constitution.md`): princípios Core (I-VIII) invariáveis que definem o comportamento operacional do Arkan. Não editável por projetos.
- **Projeto** (`.arkan/projects/{projeto}/constitution.md`): princípios específicos (P1, P2, ...) personalizáveis por projeto. Não podem contradizer o Core.

Constitution efetiva = Global + Projeto. Princípios I (Spec Governa Código) e II (Gate Obrigatório) nunca podem ser removidos. Autoridade máxima — supersede defaults, preferências e instruções de agentes. Modelo da constituição **de projeto** em `.arkan/templates/constitution-template.md`; o núcleo global não se copia nem se edita.

---

## Clarification

Correção ou esclarecimento aplicado a uma spec após aprovação explícita do desenvolvedor. Única forma legítima de alterar a spec sem violar o Princípio I (Spec Governa Código). Documentada na seção `## Clarifications` do `spec.md` com data e justificativa.

---

> **Última atualização**: 2026-03-25
