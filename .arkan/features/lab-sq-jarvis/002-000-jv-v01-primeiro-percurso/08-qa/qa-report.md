# Relatório de QA — 002-000-jv-v01-primeiro-percurso (JV-V01)

> **Peso**: Code | **Data**: 2026-10-15 | **Ambiente de QA**: Linux, Python 3.13, `QT_QPA_PLATFORM=offscreen`

## Resultado do QA

**APROVADO COM RESSALVAS** — requisitos e invariantes verificados por teste automatizado (45 testes
passando) e G3 (SC-004) cumprido pelo desenvolvedor no Windows em 2026-10-15. Ressalva restante: confirmar visualmente a correção de contraste do veredito (R04).

**Bloqueadores abertos**: 0 | **Divergências spec↔código**: 0 conhecidas | **Itens de UAT pendentes**: 0

## 1. Requisitos

| Item | Resultado | Evidência |
| --- | --- | --- |
| FR-001 a FR-013 | PASS | `tests/test_ref001.py`, `test_rew_texto.py`, `test_persistencia.py`, `test_calculos.py`, `test_regras.py`, `test_sessao.py`, `test_interface.py` — 45 passed |
| FR-014 lançador | PASS | `INICIAR-JARVIS.bat` revisado (G2) e executado pelo desenvolvedor no Windows (G3): criou o ambiente, instalou e abriu o programa |

## 2. Invariantes

| Invariante | Status | Evidência |
| --- | --- | --- |
| INV-001 a INV-006 | PASS | testes em `test_persistencia.py`, `test_sessao.py`, `test_ref001.py`, `test_calculos.py` |
| INV-007 Core intacto | PASS | `git diff c4b6042 HEAD` em `.arkan/agents`, `.arkan/templates`, `.arkan/scripts`, `.claude/commands`, `.arkan/memory/constitution.md`: sem diferenças |

## 3. Critérios de sucesso

| SC | Status | Evidência |
| --- | --- | --- |
| SC-001 | PASS | `test_sessao.py::test_percurso_completo` |
| SC-002 | PASS | `test_interface.py` (fechar e reabrir) |
| SC-003 | PASS | `test_calculos.py` |
| SC-004 | PASS (G3) | desenvolvedor percorreu o roteiro no Windows: percurso até o passo 5 e sessão reencontrada no Histórico após fechar e reabrir |

## 4. Verificação mecânica

`qa-mecanico.sh`: 18 pass, 11 warn, 0 fail. Os avisos são arquivos opcionais ausentes (`data-model.md`,
`quickstart.md`, `alinhamento-report.md`) e falsos positivos de marcadores `[TODO]` etc. (defeito do Core,
JV-D015: `grep` sem escapar colchetes).

## 5. Ressalvas

| # | Descrição | Prioridade | Quando |
| --- | --- | --- | --- |
| R01 | G3 no Windows executado (ver SC-004) | — | Resolvida |
| R02 | Defeito achado no G3: texto do veredito ilegível no tema escuro; corrigido no commit `4544876` (texto escuro fixo nas caixas claras) | Alta | Resolvida no código; R04 |
| R03 | Limiares e formato de texto do REW continuam provisórios | Média | JV-V02 / JV-V04 |
| R04 | Confirmar visualmente o veredito legível após a correção | Média | Antes de integrar em `main` |

## 6. Decisão Final

**APROVADO COM RESSALVAS** (2026-10-15). Integração em `main` somente com aprovação do desenvolvedor.
