# Plano — 002-000-jv-v01-primeiro-percurso (JV-V01)

> **Status**: aprovado no escopo autorizado (JV-D042) | **Data**: 2026-10-15

## Visão geral

```
INICIAR-JARVIS.bat ─→ python -m jarvis
                         │
              interface/ (PySide6 + pyqtgraph)  ── só apresenta; não calcula
                         │
                 sessao.py (serviço do percurso)  ── orquestra os cinco passos
          ┌──────────────┼──────────────┬───────────────┐
   rew_texto.py     calculos.py     regras.py      persistencia.py
   (importa)        (determinístico) (indícios,     (SQLite + cofre por hash,
                                      hipóteses)     cadeia, diário, integridade)
                         │
            referencia/ref001.py (gera o caso REF-001-A) → dados/referencia/REF-001-A/
```

## ADRs

| ADR | Decisão | Motivo | Consequência |
| --- | --- | --- | --- |
| ADR-01 | Python 3.11–3.13; PySide6 6.8.2.1, pyqtgraph 0.13.7, numpy 2.2.3, versões fixadas em `requirements.txt` | JV-D002, JV-D011; versões com pacotes prontos para Windows | atualização de versão é decisão explícita |
| ADR-02 | Código em `src/jarvis/`; identificadores em português | regra de idioma do projeto; o desenvolvedor lê os nomes nos relatórios | consistência com os documentos |
| ADR-03 | Interface não calcula: toda grandeza mostrada vem de `calculos.py` via `sessao.py` | P3 | a interface pode ser trocada sem tocar nos cálculos |
| ADR-04 | Banco SQLite e cofre em `%LOCALAPPDATA%\LabSQJarvis\` (ou na pasta definida por `JARVIS_DADOS`) | dados locais, fora da pasta do programa; testes usam pasta temporária | reinstalar o programa não apaga o histórico |
| ADR-05 | Resultados de cálculo guardados em JSON no banco, com hash das entradas | retomada sem recalcular; auditoria | arquivos de algumas dezenas de KB por sessão |
| ADR-06 | Diário e originais protegidos por gatilhos SQLite contra `UPDATE`/`DELETE` | P2; INV-001, INV-002 | correções viram novos registros |
| ADR-07 | Metadados do caso (canal, posição, referência temporal, configuração declarada) em `manifesto.json` ao lado dos arquivos de texto | o texto do REW não traz a referência temporal | nas medições reais, esses dados virão do protocolo de medição (F012) |
| ADR-08 | Lançador `.bat` cria `.venv` na primeira execução e instala `requirements.txt` | não é possível gerar executável Windows a partir deste ambiente | exige Python instalado e internet na primeira vez |

## Modelo de dados (mínimo do JV-V01)

| Tabela | Campos principais | Regras |
| --- | --- | --- |
| `arquivo_original` | sha256 (chave), nome, tipo, tamanho, importado_em | só inserção (gatilho) |
| `sessao` | id, modo, criada_em, estado (`aberta`/`encerrada`), passo_atual, encerramento, resumo, caso | — |
| `configuracao` | id, sessao, nome, nivel (`declarada`/`arquivada`/`coerente`), criada_em, anterior | nunca sobrescrita |
| `parametro_config` | configuracao, canal, parametro, valor, origem (`declarado`/`medição`/`caso simulado`) | base da receita inversa (JV-D040) |
| `registro` | id (`M-`, `C-`, `I-`, `H-`, `R-`, `X-`, `A-`, `D-`, `P-`), sessao, tipo, autor, criado_em, titulo, dados (JSON) | tipos de P1 |
| `derivacao` | origem, destino, papel | conferida pela rotina de integridade |
| `diario` | id, momento, sessao, evento, descricao | só inserção (gatilho) |

**Derivações permitidas** (P1, JV-D038): cálculo ← medição | cálculo; indício ← cálculo; hipótese ←
indício; recomendação ← hipótese | cálculo; experimento ← recomendação | medição | percepção;
conclusão experimental ← experimento; decisão ← conclusão | experimento; **decisão sem
intervenção** ← cálculo | indício | hipótese (nunca experimento); medição ← arquivo original
(referência por hash); percepção: lateral, ligada à sessão.

## Contratos internos

- `rew_texto.ler(caminho) -> RespostaFrequencia(freq_hz, nivel_db, fase_graus)`; erro
  `FormatoInvalido` com mensagem simples.
- `calculos.*` funções puras com `VERSAO` por função; retornam dicionários serializáveis.
- `regras.avaliar(resultados) -> (indicios, hipoteses)`; limiares em `regras.LIMIARES` marcados como
  provisórios.
- `sessao.Servico` — `nova_sessao`, `registrar_percepcao`, `importar_caso`, `analisar`,
  `propor_teste`, `registrar_aplicacao`, `importar_depois`, `decidir`, `decidir_sem_intervencao`,
  `listar_sessoes`, `abrir_sessao`, `integridade`.

## Dependências e Interfaces

| Depende de | Como | Observação |
| --- | --- | --- |
| Constituição v0.4.0, regras de segurança v0.4.0 | requisitos e invariantes | — |
| Partes de F002, F003, F004, F005, F006, F007, F008 | entregues neste incremento | registro de entregas no feature map (JV-D041) |
| PySide6, pyqtgraph, numpy | `requirements.txt` | instalados pelo lançador |
| REW | nenhuma no V01 (caso simulado) | formato de texto a confirmar no JV-V04 |
| Nenhuma outra feature | — | P VII do núcleo: sem importação de código de outras features |

## Sequência de Implementação

1. Estrutura do pacote, `requirements.txt`, configuração de testes.
2. `rew_texto.py` (ler/escrever) e testes.
3. `calculos.py` e testes analíticos.
4. `referencia/ref001.py`, geração de `dados/referencia/REF-001-A/` e teste de determinismo.
5. `regras.py` e testes.
6. `persistencia.py` (schema, cofre, gatilhos, integridade) e testes.
7. `sessao.py` (percurso completo, decisões, retomada) e testes.
8. Interface (`interface/`) e teste com pytest-qt.
9. `INICIAR-JARVIS.bat`, `COMO-EXPERIMENTAR.md`, capturas de tela.
10. QA e registro de entregas.
