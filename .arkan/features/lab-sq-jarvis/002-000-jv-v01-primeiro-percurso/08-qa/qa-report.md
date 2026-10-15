# Relatório de QA — 002-000-jv-v01-primeiro-percurso (JV-V01)

> **Peso**: Code | **Data**: 2026-10-15 | **Ambiente de QA**: Linux, Python 3.13, `QT_QPA_PLATFORM=offscreen`

## Resultado do QA

**APROVADO COM RESSALVAS** — requisitos e invariantes verificados por teste automatizado (45 testes
passando). Ressalvas: o G3 (SC-004, teste no Windows) e a execução do `.bat` ainda não ocorreram.

**Bloqueadores abertos**: 0 | **Divergências spec↔código**: 0 conhecidas | **Itens de UAT pendentes**: 1 (SC-004)

## 1. Requisitos

| Item | Resultado | Evidência |
| --- | --- | --- |
| FR-001 a FR-013 | PASS | `tests/test_ref001.py`, `test_rew_texto.py`, `test_persistencia.py`, `test_calculos.py`, `test_regras.py`, `test_sessao.py`, `test_interface.py` — 45 passed |
| FR-014 lançador | PENDENTE | `INICIAR-JARVIS.bat` revisado (G2): detecta Python 3.11–3.14, cria `.venv`, instala `requirements.txt`, mensagens simples. **Não executado no Windows** (G3) |

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
| SC-004 | PENDENTE (G3) | roteiro em `COMO-EXPERIMENTAR.md` |

## 4. Verificação mecânica

`qa-mecanico.sh`: 18 pass, 11 warn, 0 fail. Os avisos são arquivos opcionais ausentes (`data-model.md`,
`quickstart.md`, `alinhamento-report.md`) e falsos positivos de marcadores `[TODO]` etc. (defeito do Core,
JV-D015: `grep` sem escapar colchetes).

## 5. Ressalvas

| # | Descrição | Prioridade | Quando |
| --- | --- | --- | --- |
| R01 | Executar no Windows e percorrer `COMO-EXPERIMENTAR.md` (G3) | Alta | Antes de integrar em `main` |
| R02 | Task JV-T109 marcada com G3 pendente | Alta | Junto com R01 |
| R03 | Limiares e formato de texto do REW continuam provisórios | Média | JV-V02 / JV-V04 |

## 6. Decisão Final

**APROVADO COM RESSALVAS** (2026-10-15). Integração em `main` somente com aprovação do desenvolvedor.
