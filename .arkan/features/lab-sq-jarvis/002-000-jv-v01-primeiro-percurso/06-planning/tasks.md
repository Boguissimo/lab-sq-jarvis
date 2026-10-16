# Tasks — 002-000-jv-v01-primeiro-percurso (JV-V01)

> Gate de cada task: G1 = teste automatizado; G2 = revisão técnica; G3 = desenvolvedor.

## Fase 1 — Base e cálculo

- [x] JV-T101 — Estrutura `src/jarvis/`, `requirements.txt`, `pyproject.toml` (pytest). Gate: G1. Evidência: `python -m pytest` executa.
- [x] JV-T102 — `rew_texto.py`: leitura tolerante e escrita; erro em linguagem simples (FR-002). Gate: G1. Evidência: `tests/test_rew_texto.py`.
- [x] JV-T103 — `calculos.py`: resposta complexa, somas, sobreposição, fase, atraso equivalente, comparação, qualidade, referência temporal (FR-004, FR-005). Gate: G1. Evidência: `tests/test_calculos.py`.
- [x] JV-T104 — `referencia/ref001.py` e dados `REF-001-A` (FR-001). Gate: G1. Evidência: `tests/test_ref001.py`.

## Fase 2 — Diagnóstico e registro

- [x] JV-T105 — `regras.py`: indícios I-1, I-2 e hipóteses ordenadas (FR-006). Gate: G1. Evidência: `tests/test_regras.py`.
- [x] JV-T106 — `persistencia.py`: cofre, banco, gatilhos, integridade (FR-003, INV-001 a INV-003). Gate: G1. Evidência: `tests/test_persistencia.py`.
- [x] JV-T107 — `sessao.py`: percurso, teste de diagnóstico, veredito, decisões, retomada (FR-007 a FR-012). Gate: G1. Evidência: `tests/test_sessao.py`.

## Fase 3 — Interface e entrega

- [x] JV-T108 — Interface: aviso fixo, cinco passos, gráficos, histórico (FR-013). Gate: G1. Evidência: `tests/test_interface.py`.
- [x] JV-T109 (G3 cumprido em 2026-10-15) — `INICIAR-JARVIS.bat` e `COMO-EXPERIMENTAR.md` (FR-014). Gate: G2 (revisão) e G3 (seu teste no Windows). Evidência: arquivos e roteiro.
- [x] JV-T110 — Capturas de tela do percurso para a entrega. Gate: G2. Evidência: `docs/capturas/`.
- [x] JV-T111 — QA do incremento e registro de entregas no feature map (JV-D041). Gate: G1/G2. Evidência: `08-qa/qa-report.md`.
