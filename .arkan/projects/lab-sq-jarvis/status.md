---
status: features-definidas
fase-atual: 02-proposal
projeto: lab-sq-jarvis
atualizado-em: 2026-10-16
---

# Projeto: Lab SQ Jarvis

Assistente inteligente de calibração de áudio automotivo SQ/SQPL: diagnóstico, hipóteses, experimentos controlados e registro rastreável, integrado ao REW e ao HELIX DSP PC-Tool.

## Estado corrente — 2026-10-16 (nota não normativa)

- **Jarvis 1.0: sem prazo artificial.** A liberação depende de **evidências** e de **validação humana** (Fabrício), não de data. Primeiro um candidato interno; nenhuma demonstração ou teste externo antes de maturidade funcional, técnica e de apresentação (candidata UC-01 no `02-proposal/feature-map.md`, vinculada à F017; ainda **não** é requisito).
- **Estado operacional detalhado** (branches, testes, pendências, autorizações): `docs/RETOMADA-JV-V02.md` (seção "Estado atual") e o `status.md` da feature `003-000-jv-v02-honestidade-e-seguranca`.
- As seções abaixo são **histórico do planejamento** (2026-10-15). Onde dizem "nenhuma implementação autorizada" ou "aguardando aprovação", o registro é **daquela data**: o JV-V01 está concluído e em `main`, e o JV-V02 está em implementação.

## Histórico preservado — estado em 2026-10-15, revisão 3

- Revisão 3 do desenvolvedor: sete pontos específicos, sem reabrir o planejamento. Decisões JV-D030
  a JV-D037; revisões marcadas em `decisoes.md` (JV-D018 → JV-D036; JV-D024 restrita por JV-D031;
  JV-D026 ampliada por JV-D033; SEG-07 corrigida por JV-D032).
- Documentos atualizados: constituição v0.3.0, regras de segurança v0.3.0, proposta consolidada
  (revisão 3), feature map v3 (incrementos JV-V01 a JV-V06, sem features novas), comparação de
  ferramentas, fontes (JV-S028, JV-S029), briefing e visão.
- Fase do projeto permanece `01-discovery`. Nenhuma implementação autorizada.

**Próxima ação válida:** aprovação do conjunto para implementar. Depois: `/arkan.ideacao` para F001
(fundação) e, em seguida, para o incremento JV-V01.

## Histórico preservado — estado da revisão 2

- O desenvolvedor revisou a proposta inicial (seis pontos). Decisões JV-D017 a JV-D029 registradas;
  substituições marcadas em `decisoes.md` (JV-D010 → JV-D019; conteúdo de JV-D014 → JV-D022).
- Documentos revisados e **aguardando aprovação do conjunto**: briefing, visão, constituição v0.2.0,
  regras de segurança v0.2.0, feature map v2 (dois marcos, 22 features), proposta consolidada
  (antes `preparacao-mvp.md`) e nova comparação de ferramentas.
- Fase do projeto permanece `01-discovery`. Nenhuma implementação autorizada.

**Próxima ação válida:** aprovação do conjunto revisado e das propostas pendentes (JV-D011, JV-D015,
JV-D016, JV-D018, JV-D029, quantidades dos critérios VP). Depois: `/arkan.ideacao` para F001.

## Histórico preservado — estado anterior à revisão 2

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
