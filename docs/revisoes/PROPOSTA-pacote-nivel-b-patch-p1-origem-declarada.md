# PROPOSTA — Pacote Nível B: patch do P1 para origem declarada (alternativa A) e JV-T228

> **Estado: PROPOSTA, não aprovada.** Nada deste pacote foi aplicado. Não altera constituição, spec, plano, código, esquema nem testes.
> Origem: decisão de Fabrício registrada na [issue #1](https://github.com/Boguissimo/lab-sq-jarvis/issues/1#issuecomment-6236529076) (alternativa **A** aprovada; opção B descartada). Análise de base: [comentário 6236457007](https://github.com/Boguissimo/lab-sq-jarvis/issues/1#issuecomment-6236457007).
> Autoridade: Nível B exige **ato e escopo nomeados** de Fabrício (JV-D045). Comentário de IA não autoriza.
> Data: 2026-10-17.

## 1. Escopo pedido (um único pacote)

| # | Ato | Arquivo(s) | Natureza |
| --- | --- | --- | --- |
| 1 | Patch do P1: admitir um tipo primário de **declaração** | `.arkan/projects/lab-sq-jarvis/constitution.md` (P1 e histórico de versões), `decisoes.md` (nova `JV-D…`) | normativo |
| 2 | Reflexo na spec e no modelo de dados | `03-spec/spec.md` (Clarification, FR-223, invariante novo), `04-architecture/data-model.md`, `plan.md` (ADR-213) | normativo |
| 3 | Tipo e derivações | `src/jarvis/persistencia.py` (`PREFIXOS`, `DERIVACOES_PERMITIDAS`) | código |
| 4 | Importação da declaração no cofre | `src/jarvis/sessao.py` (`importar_caso`) | código |
| 5 | Integridade | `persistencia.py` (`integridade()`) | código |
| 6 | Testes de falsificação (seção 5) | `tests/test_persistencia.py`, `tests/test_sessao.py` | testes |
| 7 | Ajuste de `tasks.md` | `06-planning/tasks.md` (T228 passa a citar o tipo; nova task de patch) | planejamento |

**Fora do pacote (permanece vedado):** implementar `avaliar_alteracao_candidata()` e os percursos S1–S3 (T228 propriamente dita, exige autorização própria depois do patch); T230 e interface; regras e limites SEG; reavaliar histórico (INV-211); migração de esquema; merge na `main`.

## 2. Texto proposto para o P1 (patch)

Acrescentar ao parágrafo da cadeia, depois da frase dos tipos laterais:

> Um terceiro tipo primário, a **declaração**, guarda uma afirmação do desenvolvedor ou do manifesto de um caso sobre o equipamento ou a alteração candidata (por exemplo, `equipamento` e `alteracao_candidata`). Como a medição, ela **não deriva de outro registro**; ao contrário dela, **não é dado medido**: carrega a marca `declarado` e o hash do documento preservado no cofre. Só um **cálculo** pode derivar de uma declaração. Nenhuma declaração é promovida a medição, e nenhum cálculo deriva de uma medição que não usou.

Critério de verificação (acréscimo): a rotina de integridade confirma que toda declaração tem o documento no cofre com hash conferido e que só `calculo` aponta para declaração.

Classificação da mudança: **patch do P1** (altera a enumeração fechada de tipos e o significado literal de "aponta para os registros de que deriva" apenas para o novo tipo primário). **Não** é Clarification. Versão da constituição: **0.4.1 → 0.5.0 (Minor)** ou 0.4.2 (Patch) — a classificação é de Fabrício. *Atenção:* o rascunho 0.4.1 da JV-D045 segue não aprovado e não commitado; o patch deste pacote deve ser aplicado **depois** dele ou numerado sem colidir com ele (decisão aberta D2).

## 3. Delta mínimo no código

1. `PREFIXOS["declaracao"]`: prefixo livre (proposta: `"L"`; `M C I H R X A D P E` já estão em uso).
2. `DERIVACOES_PERMITIDAS["calculo"] = {"medicao", "calculo", "declaracao"}`. `declaracao` fica **sem** entrada de destino (é raiz, como `medicao`). Nenhum outro destino aceita `declaracao`.
3. `integridade()`: para `declaracao`, (a) `verificar_original(dados["sha256"])`, como na medição; (b) `dados["marca"] == "declarado"`; (c) não pode ter origens. Mensagem própria por falha.
4. `importar_caso`: guardar `manifesto.json` no cofre (`guardar_original`) e criar a(s) `declaracao` (`equipamento`, `alteracao_candidata`) com autor `usuário`, `sha256` do manifesto e o conteúdo declarado em `dados`. Só quando o manifesto traz essas chaves.
5. Sem migração: `registro.tipo` não tem CHECK (conferido). Banco V01 e sessões antigas intactos.

## 4. Dados históricos

Efeito **aditivo**. Registros e sessões existentes (inclusive o fixture do V01) não são reescritos nem reavaliados (INV-211); `integridade()` deles continua idêntica. Só sessões **novas** de caso com `equipamento`/`alteracao_candidata` (REF-003-S) ganham declaração. Sessões antigas do mesmo caso, importadas antes do patch, não ganham declaração retroativa e não podem usar `avaliar_alteracao_candidata()` (ficam como "sem declaração", sem fabricar origem).

## 5. Testes de falsificação (devem falhar sem a mudança)

1. `avaliacao_seguranca` sem declaração de origem é acusada pela integridade.
2. Hash da declaração ausente do cofre ou alterado é acusado.
3. Declaração só origina `calculo`: derivação direta para `indicio`, `recomendacao` etc. é acusada.
4. `origens_de(avaliacao_seguranca)` não contém `medicao`.
5. Conteúdo avaliado idêntico ao snapshot da declaração (mesmo hash).
6. Pasta de origem apagada após a importação: a avaliação lê do cofre.
7. Declaração com origens, ou sem `marca == "declarado"`, é acusada.
8. Regressão histórica: fixture do V01 e sessões anteriores com `integridade()` idêntica e reabertura sem recálculo (INV-211); casos de referência inalterados (INV-213).
9. Nenhum outro `calculo` sem origem passa a ser aceito (a exigência de origem não foi afrouxada).

Meta de suíte: 328 + 1 xfail hoje; deve continuar passando, mais os novos testes (que falham sem o patch).

## 6. Riscos e limites declarados

- Introduz um **segundo tipo-raiz**; mitigado por: só `calculo` deriva dele, hash conferido, marca `declarado`, sem origens.
- Declaração **não prova o estado físico** do equipamento (afirmação, não medição); a interface e o relatório devem dizê-lo quando T230 for tratada.
- Não resolve a qualidade do conteúdo declarado; isso segue nas regras SEG (inalteradas).

## 7. Decisões ainda genuinamente abertas (para Fabrício)

- **D1 — nome e prefixo do tipo:** `declaracao` / `L` (proposta) ou outro.
- **D2 — classificação e numeração:** Minor 0.5.0 ou Patch; ordem em relação ao rascunho 0.4.1 (JV-D045) ainda não aprovado.
- **D3 — conteúdo:** uma declaração por manifesto (agrupa `equipamento` e `alteracao_candidata`) ou uma por item. Proposta: **uma por manifesto**, menor delta e um só hash.

Tudo o mais permanece como aprovado (alternativa A, sem exceção para cálculo sem origem, sem origem fabricada, sem reavaliar histórico, sem antecipar T230).

## 8. Texto sugerido para a autorização (Nível B)

> "Autorizo, em Nível B, o pacote `PROPOSTA-pacote-nivel-b-patch-p1-origem-declarada.md`, itens 1 a 7, com D1 = …, D2 = …, D3 = …. Não autorizo a implementação de JV-T228 (`avaliar_alteracao_candidata`), JV-T230, merge ou qualquer item fora do pacote."
