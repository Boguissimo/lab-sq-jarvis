# Modelo de dados — JV-V02

> Complementa o modelo do JV-V01 (`002-000-jv-v01-primeiro-percurso/04-architecture/plan.md`). Nada do V01 é removido ou renomeado.

## Esquema

`PRAGMA user_version`: **1** (V01) → **2** (V02). A migração é idempotente e não toca em dados existentes (ADR-207).

| Tabela | Mudança | Campos | Regras |
| --- | --- | --- | --- |
| `aprovacao` | **nova** | id, sessao, recomendacao (id em `registro`), nivel (`B`), escopo (texto: o quê, canal, quanto), momento | só inserção (gatilho); integridade confere que `recomendacao` existe e é do tipo `recomendacao` |
| `arquivo_original` | uso novo | `tipo = 'ajuste-pctool'` para arquivos de ajuste | já é só inserção |
| `configuracao` | uso novo | `arquivo_sha256` preenchido quando o nível é `arquivada` | nunca sobrescrita |
| `registro` | uso novo | `dados` da `recomendacao` ganha `tipo_intervencao` (`teste de diagnóstico` \| `etapa de calibração`), `seguranca.regras[]` com resultado por regra; `dados` da `conclusao` ganha `resultado` (etapa) e `comprometida` como veredito | tipos e derivações do V01 inalterados |

## Estruturas em `dados` (JSON)

- **Resultado de regra SEG**: `{regra, resultado: aprovada|bloqueada|não verificável, motivo, provisorio: bool, limite?}`.
- **Etapa de calibração (recomendação)**: `{tipo_intervencao, objetivo: {deficit_max_db, provisorio}, limites_informados: [...], conjunto: [{canal, parametro, de, para}], previsao?, seguranca}`.
- **Resultado da etapa (conclusão)**: `{resultado: objetivo atingido|parcial|não atingido|inconclusivo, deficit_antes_db, deficit_depois_db, reducao_percentual, nao_verificado: [...], texto}`; nunca contém atribuição a um ajuste isolado.
- **Manifesto de caso (extensões, todas opcionais)**: `semente`, `ruido_sigma_db`, `tipo_sessao` (`investigacao` \| `etapa_calibracao`), `depois.configuracao_declarada`, medição individual `via_b` com `momento: "depois"`, `referencia_temporal` por medição.

## Integridade (FR-222)

Além das verificações do V01: toda `aprovacao` aponta para uma `recomendacao` existente; toda `conclusao` de etapa aponta para um `experimento` de etapa; toda `configuracao` `arquivada` aponta para um arquivo existente no cofre com hash conferido; nenhum registro de `etapa de calibração` contém veredito de teste, e vice-versa.
