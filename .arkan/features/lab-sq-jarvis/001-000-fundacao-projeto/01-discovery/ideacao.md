# Ideação — 001-000-fundacao-projeto (F001)

> **Projeto**: lab-sq-jarvis | **Peso**: Doc | **Superfície crítica**: sim (segurança do equipamento;
> integridade da cadeia de conhecimento) | **Data**: 2026-10-15
> **Status**: aprovada (G3, 2026-10-15 — JV-D042)

## Contexto

O planejamento de projeto passou por três revisões e foi ratificado pelo desenvolvedor, que
autorizou “a fundação necessária e o primeiro incremento executável JV-V01” e pediu quatro ajustes
pontuais antes de consolidar o modelo de dados do primeiro incremento.

## Decisões Tomadas

| Decisão | Fundamentação | Alternativas descartadas |
| --- | --- | --- |
| JV-D038 — decisão sem intervenção na cadeia (emenda P1) | pedido do desenvolvedor: “nada a alterar” sem experimento fictício | exigir experimento em toda sessão |
| JV-D039 — SEG-13 confere só valores acessíveis | o Jarvis ainda não lê o arquivo do PC-Tool | tratar o arquivo arquivado como conferência |
| JV-D040 — reversão só com valores anteriores registrados (emenda P2) | não prometer o que não se pode restaurar | receita inversa sempre |
| JV-D041 — execução por incrementos com registro de entregas | entregar partes de features sem esperar a feature inteira | dependências só entre features completas |
| JV-D042 — ratificação do conjunto | palavras do desenvolvedor registradas em `decisoes.md` | nova rodada de revisão completa (dispensada) |

## Síntese

- **Nome**: Fundação do projeto.
- **Definição**: deixar a base normativa ratificada e coerente com os ajustes de 2026-10-15, para
  que o JV-V01 seja especificado e verificado contra ela.
- **Escopo**: constituição v0.4.0; regras de segurança v0.4.0; proposta consolidada aprovada; feature
  map v4 com registro de entregas; decisões JV-D038 a JV-D042; status do projeto
  `features-definidas`; integração em `main`.
- **Fora do escopo**: código; validação dos valores provisórios; fontes da sequência de ajuste
  (JV-D029).

## Obrigações da Superfície Crítica

| Pergunta | Resposta |
| --- | --- |
| Que política da constituição rege a superfície? | P4 (redução de risco; aprovação não verifica) e `regras-de-seguranca.md`; P1/P2 para a cadeia |
| Esta feature altera regras de segurança? | sim: SEG-13 (JV-D039) — torna a conferência mais restritiva, não mais permissiva |
| Algum valor provisório passa a definitivo? | não; a aprovação declara expressamente que continuam provisórios |
| A cadeia perde alguma garantia? | não: a decisão sem intervenção é um tipo novo e não substitui conclusão experimental |
| Como se verifica? | revisão de texto (G2) e aceite do desenvolvedor (G3); verificações G1 entram com o código no JV-V01 |
