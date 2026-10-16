# Fixture do banco do JV-V01 (permanente)

Banco (`jarvis.db`, `user_version` 0) e cofre produzidos pelo **código original do V01**
(`main@389e580`) com `ferramentas/gerar_banco_v01.py`, em 2026-10-15. Usada pelos testes de migração
(ADR-207, `tests/test_migracao.py`).

- Conteúdo só sintético: duas sessões do REF-001-A (uma completa, com decisão "manter"; outra aberta
  depois da análise). Nenhum dado do desenvolvedor.
- O cofre guarda os quatro arquivos do REF-001-A, com os bytes do checkout em que foi gerada (fim de
  linha CRLF, Windows). `.gitattributes` marca a pasta como `-text`, para o Git não alterar os bytes.
- **Não regenerar sem uma decisão `JV-D`** (emenda E2): esta é a regressão permanente da migração.
  O gerador recusa sobrescrever sem `--forcar`.
- Os testes copiam a pasta para um diretório temporário antes de abrir; nunca abrem esta cópia direto.
