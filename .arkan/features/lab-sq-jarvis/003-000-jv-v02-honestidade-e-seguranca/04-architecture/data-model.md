# Modelo de dados — JV-V02

> Complementa o modelo do JV-V01 (`002-000-jv-v01-primeiro-percurso/04-architecture/plan.md`). Nada do V01 é removido, renomeado ou alterado; **nenhum `ALTER TABLE`** em tabelas do V01.
> **Revisão R1** (2026-10-15): versão legada 0, migração transacional com backup, `aprovacao` com integridade reforçada, gatilho em `configuracao`, interpretação gravada (INV-211) e estruturas da emenda E1.

## Versões do esquema

| `user_version` | Significado | Ao abrir (ADR-207) |
| --- | --- | --- |
| 0, sem tabelas | arquivo novo/vazio | cria o esquema 2 numa transação |
| 0, impressão digital = V01 | **banco legado do JV-V01** (o V01 não grava `user_version`) | backup consistente → `integrity_check` do backup → migração 0 → 2 em `BEGIN IMMEDIATE … COMMIT` |
| 2, impressão digital = V02 | atual | abre; nada é alterado (idempotência) |
| qualquer outro (1, > 2, impressão desconhecida) | não reconhecido | `ErroVersaoBanco`; o arquivo **não** é modificado |

**Impressão digital**: o conjunto (tipo, nome, SQL normalizado) de tabelas e gatilhos em `sqlite_master`, comparado às constantes `ESQUEMA_V01` (cópia literal do V01) e `ESQUEMA_V02`. A leitura é feita numa conexão `mode=ro`.

**Backup**: `jarvis.antes-v02-<AAAAMMDD-HHMMSS>.db` na pasta de dados, gerado por `sqlite3.Connection.backup`. O cofre não é copiado, porque a migração não o toca.

## Tabelas

| Tabela | Mudança | Campos | Regras |
| --- | --- | --- | --- |
| `aprovacao` | **nova** | `id` INTEGER PK; `sessao` INTEGER NOT NULL → `sessao(id)`; `recomendacao` TEXT NOT NULL UNIQUE → `registro(id)`; `nivel` TEXT NOT NULL CHECK (`nivel = 'B'`); `escopo` TEXT NOT NULL (JSON `{canal, parametro, de, para}`); `momento` TEXT NOT NULL; `autor` TEXT NOT NULL DEFAULT 'usuário' | **Só inserção:** gatilhos que recusam UPDATE e DELETE. **Gatilho `BEFORE INSERT`:** recusa se não existe `registro` com `id = NEW.recomendacao`, `tipo = 'recomendacao'` e `sessao = NEW.sessao`. **Serviço:** recusa recomendação não sensível, não admissível ou com escopo diferente da alteração, e `momento` anterior ao `criado_em` da recomendação. **Integridade:** confere tudo isso de novo |
| `configuracao` | **gatilhos novos** | — | só inserção: gatilhos `so_insercao_configuracao_update`/`_delete`, criados na migração (o V01 nunca altera essa tabela) |
| `arquivo_original` | uso novo | `tipo = 'ajuste-pctool'` para arquivos de ajuste | já é só inserção |
| `configuracao` | uso novo | `arquivo_sha256` preenchido quando o nível é `arquivada` | — |
| `sessao` | uso novo | `modo` ganha o valor `etapa-simulada`; `calibracao` continua recusado (V04) | — |
| `registro` | uso novo | ver estruturas abaixo | tipos e `DERIVACOES_PERMITIDAS` do V01 inalterados |

## Estruturas em `registro.dados` (JSON)

**Comum a todo `calculo` novo** (ADR-210): `{nome, versao, parametros, limiares: {<nome>: {valor, provisorio}}, entradas: [ids], entradas_sha256: {id: sha256}, resultado}`. Para medição, `entradas_sha256` é o hash do arquivo no cofre; para outros registros, é o SHA-256 do JSON canônico (`sort_keys`, sem espaços) de `dados`.

| Cálculo (`nome`) | `resultado` |
| --- | --- |
| `irregularidade` (uma por medição) | `{sigma_db: float \| null, aplicavel, condicoes: {grade_log_uniforme, pontos_por_oitava, suavizacao: nenhuma\|declarada\|desconhecida}, classificacao: aprovada\|aviso\|reprovada\|nao_estimavel}` |
| `vales_individuais` (por via) | `{vales: [{freq_hz, profundidade_db, largura_oitava}]}` |
| `avaliacao_regras` (**INV-211**) | `{versao_regras, portao: {classificacao, conclui: bool, motivo, falta}, sugestao, motivo, hipoteses_ordem: [ids], aviso_referencia?}`; deriva de todos os cálculos que usou |
| `detector_mudanca` (por via, no "depois") | `{via, condicoes_comparaveis: {ok, diferencas: [...]}, faixa_util_hz: [min, max], media_db, pior_banda: {freq_hz, delta_db}, limiar_bandas_db, resultado: mudanca_detectada\|nao_detectada\|inconclusiva, resolucao: {media_db: 1.0, bandas_db}}` |
| `deficit_cruzamento` | `{deficit_db (≥ 0), freq_hz, indices}` |

**`recomendacao`**:
- **Comum:** `{tipo_intervencao: teste de diagnóstico | etapa de calibração, seguranca: {versao_regras_seg: "0.4.0", classe, regras: [ResultadoRegra], admissibilidade: {admissivel, estado: recomendada|bloqueada, motivo, falta: [], nao_verificadas: []}, limitacoes: [...]}, receita: [...] | null, reversao}`.
- **Alteração bloqueada:** `admissivel: false`, `receita: null`, título "Alteração bloqueada — não recomendada".
- **Teste:** `variavel`, `hipotese`, `previsao`, `previsao_resumo`, `criterio`, `previsao_registrada_em`. São os mesmos campos do V01; muda só a origem do bloco `seguranca`.
- **Etapa:** `{objetivo: {deficit_max_db, provisorio}, limites_informados: [...], conjunto: [{canal, parametro, de, para}], deficit_antes: id}`.

**ResultadoRegra**: `{regra, resultado: aprovada|bloqueada|não verificável|não se aplica, motivo, provisorio: bool, limite?, falta?}`.

**`reversao`** (na recomendação e na decisão): `{documentada: bool, modo: arquivo|receita|nenhum, arquivo_sha256?, receita_inversa?, falta: [], confirmacao_fisica: false, aviso}`. Registros do V01 têm `{garantida, receita_inversa, base}`; `garantida: true` é lido como `documentada: true, modo: receita`.

**`conclusao`**:
- **De teste:** `{veredito: confirmada|refutada|inconclusiva|comprometida, motivo, precedencia_aplicada: 1..4, verificacao_variavel_unica: {configuracao: igual|diferente|nao_declarada, diferencas: [...], vias: {via_a: {resultado | "nao_verificada", detector?: id}, via_b: {...}}, aviso?: "outras alterações não foram verificadas"}, incerteza: {sigma_max_db | "não quantificada"}, limite}`.
- **De etapa:** `{resultado: objetivo atingido|parcial|não atingido|inconclusivo, precedencia_aplicada: 1..4, deficit_antes_db, deficit_depois_db, reducao_percentual | null, nao_verificado: [{canal, parametro}], verificado: [{canal, parametro, valor, origem: declarado|medição}], texto}`. Nunca contém atribuição a um ajuste isolado nem campo `veredito`.

**`aprovacao.escopo`**: `{canal, parametro, de, para}`, igual à alteração da recomendação.

## Manifesto de caso (extensões, todas opcionais)

- **Caso:** `semente`, `ruido_sigma_db`, `tipo_sessao` (`investigacao` | `etapa-simulada`), `modelo` (parâmetros físicos usados, para auditoria), `depois.configuracao_declarada`.
- **Por medição:** `suavizacao` (`nenhuma` | texto da suavização declarada), `ganho_entrada_db`, `referencia_nivel`, `posicao_microfone` (já existe), `referencia_temporal` (já existe).
- **Casos de segurança REF-003-S (E2, FR-223):** `equipamento` (sintético: `[{canal, alto_falante, estado: confirmado|planejado|informado, potencia_rms_w?, fs_hz?, passa_altas_min_hz?, inclinacao_min_db_oit?}]`, sempre com `simulado: true`) e `alteracao_candidata` (`{canal, parametro, de, para, tipo: reforco_eq|corte_eq|ganho|passa_altas, freq_hz?, q?}`). A alteração passa por `seguranca.classificar`/`avaliar`/`admissibilidade` e é registrada como `recomendacao` (admitida ou bloqueada), com as mesmas estruturas acima.
- **Repetição do "depois" (E3):** cada aquisição individual "depois" é um registro `medicao` próprio (id `M-…`), com arquivo próprio no cofre (SHA-256 distinto), `aquisicao_id` único e `repeticao` (1, 2, …). Todas têm a mesma `posicao_microfone` declarada. Não há limite de uma medição por via e momento: o serviço lê todas (`_medicoes`). Mesmo SHA-256 ou mesmo `aquisicao_id` ⇒ recusada como repetição. O REF-001-N3 traz duas para o tweeter. O cálculo `detector_mudanca` passa a guardar `depois: [ids]`, `reproduzida: bool` e `parametro_identificado: false`. **(E4)** Também guarda `confirmacao: {reproduzida, mesmo_sentido, concordam, faixa_compativel}` e `faixa_compativel: bool` (interseção não vazia entre as faixas de mudança das aquisições); `reproduzida` exige `faixa_compativel`. Resultado por via: `mudanca_detectada_indicativa` ou `mudanca_detectada_reproduzida` (já existentes); nenhum campo novo de tabela, só chaves em `dados` do cálculo.
- **Referência temporal (E3):** `referencia_temporal.tipo`, `referencia_temporal.id`, `taxa_amostragem` e `posicao_microfone` são obrigatórios para uma referência declarada compatível; o cálculo grava `declarada: true`.
- **Medições "depois":** `via_a` e `via_b` com `momento: "depois"`.

Regra de ausência:
- `suavizacao` ausente vale `nenhuma` **só** num caso do catálogo interno com proveniência verificada. Em qualquer outro arquivo, inclusive com `simulado: true`, vale `desconhecida` (INV-214).
- **Proveniência:** ao importar, o serviço grava em `dados` da medição `proveniencia: {catalogo: bool, caso, sha256_esperado}`; `catalogo: true` só quando o caso está em `casos.listar()` e o SHA-256 confere com o gerado.
- `ganho_entrada_db` ou `referencia_nivel` ausentes ⇒ condições não comparáveis para o detector.

## Integridade (FR-222; revisão, item 9)

Além das verificações do V01, `integridade()` confere:

1. **Aprovação**:
   - aponta para um `registro` existente do tipo `recomendacao`, da mesma sessão, sensível e admissível;
   - o escopo é igual à alteração da recomendação;
   - o momento é posterior à recomendação;
   - não há duas aprovações para a mesma recomendação.
2. **Configuração**:
   - `anterior` aponta para uma configuração existente, sem ciclo;
   - nível `arquivada` ⇒ `arquivo_sha256` existe em `arquivo_original` e confere no cofre;
   - toda configuração tem ao menos um parâmetro.
3. **Arquivo de ajuste**: `tipo = 'ajuste-pctool'` existe no cofre com o hash conferido e está ligado a uma configuração.
4. **Resultados SEG**:
   - toda `recomendacao` do V02 tem `seguranca.regras` e `admissibilidade`;
   - recomendação bloqueada não tem receita, nem `experimento` derivado, nem aprovação;
   - recomendação sensível com `experimento` tem aprovação.
5. **Etapa × teste**:
   - nenhum registro de `etapa de calibração` contém `veredito`, e nenhum de teste contém `resultado`;
   - toda `conclusao` de etapa aponta para um `experimento` de etapa.
6. **Interpretação**:
   - toda sessão do V02 com análise tem `avaliacao_regras`;
   - todo cálculo do V02 tem `entradas_sha256`, e os hashes de medição conferem com o cofre.
7. **Diário**:
   - eventos com `sessao` apontam para uma sessão existente;
   - `id` e `momento` são não decrescentes;
   - toda sessão `encerrada` tem evento de encerramento.

8. **Cofre físico (E3, A06; ADR-212)**:
   - todo arquivo em `cofre/` tem linha em `arquivo_original`, e toda linha tem arquivo;
   - o hash de cada arquivo confere com o nome;
   - não restam arquivos em `cofre/.tmp/`.

"Imutável" é política de preservação e detecção, não impossibilidade física.

Cada verificação tem um teste com inconsistência deliberada em `test_integridade.py`. A inconsistência é inserida por SQL direto, com gatilhos ou `foreign_keys` desligados só dentro do teste.

## Fixture de regressão da migração (E2)

`tests/dados/banco-v01/` (`jarvis.db` + `cofre/`) é gerada uma única vez pelo V01 original (`main@389e580`) com `ferramentas/gerar_banco_v01.py`, só com sessões sintéticas do REF-001-A, e versionada como teste de regressão permanente. Não é regenerada sem `JV-D`. Os testes trabalham sempre numa cópia temporária.

## Legado do V01 (INV-211)

Sessões sem `avaliacao_regras` são do V01. `estado()` reconstrói a análise com `regras_v1_0.py` (cópia congelada), marca "reconstruída pelas regras 1.0" e não exige `entradas_sha256`, `irregularidade` nem `seguranca.admissibilidade`.
