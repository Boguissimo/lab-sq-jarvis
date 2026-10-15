---
status: em-discovery
fase-atual: 01-discovery
projeto: lab-sq-jarvis
atualizado-em: 2026-10-15
---

# Projeto: Lab SQ Jarvis

Assistente inteligente de calibração de áudio automotivo SQ/SQPL: diagnóstico, hipóteses, experimentos controlados e registro rastreável, integrado ao REW e ao HELIX DSP PC-Tool.

## Estado corrente — 2026-10-15

- Pacote Arkan instalado sem alteração no Core (JV-D015); projeto criado por `create-project.sh`.
- `/arkan.projeto` executado até a proposta: briefing, visão, constituição v0.1.0, regras de
  segurança v0.1.0, feature map e preparação do MVP **redigidos e aguardando aprovação**.
- Fase do projeto permanece `01-discovery` até a aprovação do briefing e da visão; passa a
  `02-proposal` / `features-definidas` só com a aprovação do feature map.
- Pós-condição do `/arkan.projeto`: o portão procura `.arkan/project/` (defeito do Core, JV-D015);
  verificação equivalente manual sobre `.arkan/projects/lab-sq-jarvis/`: `status.md` presente;
  `## Features Propostas` presente em `02-proposal/feature-map.md`.

**Próxima ação válida:** aprovação do desenvolvedor (briefing, visão, constituição, regras de
segurança, feature map, JV-D011, JV-D015, JV-D016). Depois: `/arkan.ideacao` para F001. Nenhuma
implementação autorizada.
