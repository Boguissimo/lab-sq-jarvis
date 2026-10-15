# Classificação de Features por Peso

O Arkan classifica cada feature por peso na ideação (fase 01). O peso determina quais fases do pipeline são obrigatórias, simplificadas ou puladas.

---

## Pesos

### Code — Pipeline completo

Features que envolvem lógica executável: scripts, APIs, integrações, código de aplicação.

**Fases obrigatórias**: todas (01 → 10)

**Quando usar**: a feature produz ou modifica arquivos que são executados (`.sh`, `.ts`, `.py`, etc.) ou configuram comportamento de runtime.

### Doc — Pipeline simplificado

Features puramente documentais: markdown, templates, definições, reorganização de arquivos de texto.

**Fases obrigatórias**:

| Fase | Status | Adaptação |
| --- | --- | --- |
| 01 — Ideação | Obrigatória | Normal |
| 02 — Proposta | Opcional | Pular se feature interna (sem cliente) |
| 03 — Spec | Simplificada | Lista de entregáveis + critérios de aceitação. Sem Given/When/Then formal. Invariantes apenas se aplicável. |
| 04 — Arquitetura | Pulada | Não há arquitetura — são arquivos de texto. Registrar "N/A — feature documental" |
| 05 — UX | Pulada | Sem UI |
| 06 — Tasks | Obrigatória | Normal |
| 07 — Implementação | Obrigatória | Normal |
| 08 — QA | Simplificada | Checklist mecânico (qa-mecanico.sh) + revisão rápida. Sem orquestração multi-agente. |
| 09 — Deploy | Obrigatória | Normal (com template BLOQUEANTE/AVISO) |
| 10 — Ops | Opcional | Apenas se feature terá ciclo de vida longo |

### Config — Pipeline mínimo

Ajustes pontuais: edição de configuração, correção de campo, renomeação.

**Fases obrigatórias**:

| Fase | Status | Adaptação |
| --- | --- | --- |
| 01 — Ideação | Mínima | Registro inline da mudança e justificativa — sem debate formal |
| 02-05 | Puladas | Sem necessidade |
| 06 — Tasks | Mínima | Lista simples de arquivos a editar |
| 07 — Implementação | Obrigatória | Normal |
| 08 — QA | Mínima | Verificação mecânica apenas (qa-mecanico.sh) |
| 09 — Deploy | Simplificada | Commit + merge, sem checklist completo |
| 10 — Ops | Pulada | Sem necessidade |

---

## Como classificar

Na ideação (fase 01), após a síntese, o agente propõe o peso com justificativa:

> **Peso proposto**: [Code/Doc/Config]
> **Justificativa**: [por que este peso — quais artefatos serão produzidos]

O desenvolvedor confirma ou ajusta. O peso é registrado no `status.md` da feature:

```yaml
peso: Code  # ou Doc, Config
```

Se o peso mudar durante o desenvolvimento (ex: feature Doc que revelou necessidade de script), o desenvolvedor pode reclassificar executando:

```bash
.arkan/scripts/update-status.sh --file $FEATURE_DIR/status.md --field peso --value Code
```

---

## Referência rápida

| Peso | Fases | Overhead estimado | Quando usar |
| --- | --- | --- | --- |
| **Code** | 01-10 (completo) | Alto | Código executável, integrações, APIs |
| **Doc** | 01, 03*, 06, 07, 08*, 09 | Médio | Markdown, templates, reorganização |
| **Config** | 01*, 06*, 07, 08*, 09* | Baixo | Edição pontual, correção, renomeação |

`*` = fase simplificada ou mínima
