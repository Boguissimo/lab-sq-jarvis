# Retomada — JV-V01 pausado em 2026-10-15

Branch: `lab-sq-jarvis/002-000-jv-v01-primeiro-percurso` · feature Arkan `002-000-jv-v01-primeiro-percurso` · fase `07-implement`.

## 1. Feito no JV-V01
- Arkan: ideação, spec, plano e tasks da feature (portões `check-prerequisites` PASS).
- `src/jarvis/`: `rew_texto.py` (texto estilo REW), `calculos.py` (determinístico, versionado), `referencia/ref001.py` + dados REF-001-A, `regras.py` (Regras 1 e 2, hipóteses), `persistencia.py` (SQLite, cofre por SHA-256, gatilhos só-inserção, integridade), `sessao.py` (percurso, decisões, retomada), `interface/janela.py` (PySide6 + pyqtgraph, 5 passos + histórico, aviso fixo de dados simulados).
- 45 testes `pytest`/`pytest-qt` passando em Linux (inclui interface com fechar/reabrir). Capturas em `docs/capturas/`; gerador em `ferramentas/capturas.py`.
- Tasks JV-T101 a JV-T108 implementadas, mas ainda **não marcadas** em `06-planning/tasks.md`.

## 2. Falta
- `INICIAR-JARVIS.bat` (cria `.venv`, instala `requirements.txt`, roda `python -m jarvis` com `PYTHONPATH=src`; mensagens simples como o `JOGAR.bat` do Rygar) — JV-T109.
- `COMO-EXPERIMENTAR.md` (roteiro G3 para o desenvolvedor) — JV-T109.
- Marcar tasks; `08-qa/qa-report.md` (`## Resultado do QA`) e `qa-mecanico.sh` — JV-T111.
- Registro de entregas no `feature-map.md` (JV-V01 e features `parcial (JV-V01)`) — JV-T111.
- Pacote final (zip com programa, instruções, testes, limitações); integração em `main` só com aprovação.

## 3. Windows
- Requer Python 3.11–3.14. Versões fixadas: PySide6 6.10.2, numpy 2.4.6, pyqtgraph 0.14.0 (pacotes prontos para Windows até 3.14).
- O programa **ainda não foi executado no Windows**; o `.bat` não existe e não foi testado.

## 4. Defeitos do Core (registrados em JV-D015, Core não alterado)
- `qa-mecanico.sh` exige `## ADRs`, `## Dependências e Interfaces` e `## Sequência de Implementação` no plano mesmo para peso Doc; atendido com seções “N/A”.
- A checagem de marcadores (`[TODO]` etc.) usa `grep` sem escapar colchetes: falso positivo em quase todo arquivo.

## 5. Convenções e decisões
- Arkan: Core intacto; branches `lab-sq-jarvis/NNN-CCC-slug` (branch `claude/...` resolve projeto errado); `.gitattributes` mantém `.sh` em LF.
- Fontes canônicas em `.arkan/projects/lab-sq-jarvis/`: constituição v0.4.0, `regras-de-seguranca.md` v0.4.0, `decisoes.md` (JV-D001–D042), `feature-map.md` v4, `proposta-consolidada.md`.
- JV-V01 é demonstração simulada; explicações por regras, sem IA (IA no JV-V03); não orienta ajustes reais (JV-D025, JV-D042).
- Limiares e valores SEG provisórios continuam provisórios. Aprovação não verifica (JV-D032).
- Decisão sem intervenção ≠ conclusão experimental (JV-D038); reversão só com valor anterior registrado (JV-D040); entregas parciais por incremento (JV-D041).
- Código e textos em PT-BR; interface não calcula (ADR-03); dados em `%LOCALAPPDATA%\LabSQJarvis` ou `JARVIS_DADOS`.
- Uso pessoal primeiro; comercial depois (JV-D017). GitHub: usar o mínimo (git direto).

## 6. Atualização (conclusão do JV-V01)
- Feitos: `INICIAR-JARVIS.bat`, `COMO-EXPERIMENTAR.md`, tasks marcadas, `08-qa/qa-report.md` (aprovado com ressalvas), registro de entregas e F002–F008 `parcial (JV-V01)`, pacote `dist/jarvis-jv-v01.zip`.
- Falta: G3 — o desenvolvedor executar no Windows (SC-004); só então integrar em `main`.
