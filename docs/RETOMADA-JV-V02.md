# Retomada — JV-V02 pausado em 2026-10-16

Branch: `lab-sq-jarvis/003-000-jv-v02-honestidade-e-seguranca` · feature Arkan `003-000-jv-v02-honestidade-e-seguranca` · fase `04-architecture` (plano em **revisão**).
`main` contém o JV-V01 completo (commit `389e580`, QA aprovado, G3 cumprido no Windows). Esta branch parte dele.

## 1. Feito no JV-V02
| Fase | Artefato | Estado |
| --- | --- | --- |
| 01 Ideação | `01-discovery/ideacao.md` | **aprovada** (peso Code; superfície crítica: sim) |
| 03 Spec | `03-spec/spec.md` (FR-201 a FR-222, INV-201 a INV-210, SC-201 a SC-207) | **aprovada** (2026-10-16). Decisões: um incremento em três blocos; arquivo de ajuste do PC-Tool opaco; calibração simulada tipo ATM; SEG-02/07/09 só `não verificável`; `comprometida` por duas vias |
| 04 Plano | `04-architecture/plan.md`, `data-model.md`, `quickstart.md` (ADR-201 a ADR-210) | rascunho no commit `e2ab7ff`; **não aprovado**: revisão externa pede ajustes |
| 06 Tasks | — | não iniciada (esperar o plano aprovado) |

Nenhum código do V02 foi escrito. Testes do V01: 45 passando.

## 2. Revisão externa a aplicar (fonte: `docs/revisoes/jv-v02-revisao-tecnica-do-plano.md`)
Veredito: **aprovar com ajustes**; não refazer a arquitetura. Conferi no código do V01 e **confirmei** quatro afirmações: o V01 não grava `PRAGMA user_version` (banco legado = versão 0); `Banco.__init__` roda o esquema antes de qualquer migração; `Banco.configuracoes(sessao)` consulta só a sessão informada; a tabela `configuracao` não tem gatilho de só inserção (apenas `parametro_config` tem).

| # | Sev. | Ajuste | Onde mexe | Exige mudar a spec? |
| --- | --- | --- | --- | --- |
| 1 | Alta | Migração: reconhecer esquema legado (v0), migrar para 2; transacional, idempotente, com backup; teste com banco real do V01; recusar versão desconhecida sem modificar; reorganizar `Banco.__init__` | ADR-207, data-model | não |
| 2 | Alta | Adaptar `propor_teste`, `registrar_aplicacao`, `estado`, `resumo` aos dois fluxos (teste de polaridade e etapa de calibração); testar criar/executar/encerrar/histórico/reabrir | ADR-205 | não |
| 3 | Alta | Estimador de ruído mede irregularidade espectral, não ruído: pode reprovar cancelamentos e reflexões reais. Comparar com o ruído injetado em casos só-ruído, só-cancelamento e combinados | ADR-202 | **sim** (definição normativa de ruído, FR-202, limiar 1,5 dB) |
| 4 | Alta | Avaliação SEG participa da admissibilidade da recomendação; bloqueada nunca aparece como recomendada/segura; aplicar também às recomendações herdadas do V01 | ADR-204 | possível (FR-211/INV-203) |
| 5 | Alta | Persistir resultados de qualidade, versões, limiares usados e hashes das entradas; não reconstruir interpretação histórica reexecutando regras | ADR-210, data-model | possível |
| 6 | Média | Aprovação: reforçar integridade (recomendação existente, mesma sessão, nível, escopo, momento, alteração autorizada) | ADR-204 | não |
| 7 | Média | `comprometida`: aceitar medições "depois" de **ambas** as vias, faixas por alto-falante, distinguir "sem alteração comprovada" de "sem dados para verificar" | ADR-208 | **sim** (definição "depois comprometido", FR-207) |
| 8 | Média | Recuperar última configuração **entre sessões**; distinguir arquivo/receita disponíveis de restauração física confirmada | ADR-206 | possível (FR-220/221) |
| 9 | Média | Integridade estendida (aprovações, configurações, arquivos, resultados SEG, diário), testes com inconsistências deliberadas; gatilho de imutabilidade em `configuracao` | FR-222 | não |
| 10 | Média | Gerador: respostas fisicamente coerentes (filtros, atrasos, polaridade determinam juntos magnitude, fase, soma); ruído acrescentado depois | ADR-201 | não |
| 11 | Média | Quatro variantes de REF-002-A explícitas; déficit inicial nulo e divisão por zero; SC-204 a SC-207 | spec/plano | possível (definições de resultado) |
| 12 | Baixa | Cronologia das datas de aprovação; qualificar "reversão garantida" (documental × física) | spec, plano | texto |

Limiares: continuam provisórios; a revisão pede validação por varredura (valores logo acima/abaixo), registro de falsos positivos/negativos e **não ajustar critérios só para os casos de referência passarem**. Sequência: manter os três blocos; migração na fundação; contratos de qualidade e segurança antes de integrar recomendações; fluxo completo com histórico e reabertura no bloco 3. ADR-201, 203, 206, 209, 210 mantidas; 204 mantida com integridade reforçada; 205 e 208 ampliadas; 207 corrigida; 202 revista.

## 3. Diretriz de evolução (fontes de medição e REW)
Fonte: `docs/revisoes/diretriz-fontes-de-medicao-e-rew.md`. **Não entra no JV-V02.** Pendente: registrar no planejamento evolutivo (proposta: nova decisão `JV-D043`, e nota no feature map para F004/F013/F018) **com aprovação do desenvolvedor**, e identificar interfaces a preparar (por exemplo, campos de origem `SYNTHETIC`/`EXPERIMENTAL`/`CALIBRATED`, calibração de resposta e de SPL, referência temporal, equipamento, posição). Casa com o item 10 da revisão (gerador coerente).

## 4. Próximos passos (ordem sugerida)
1. Debater com o desenvolvedor os itens que exigem mudar a spec (3, 7 e, se for o caso, 4, 5, 8, 11). Aplicar via `/arkan.clarify` ou emenda na spec, **com nova aprovação**.
2. Revisar `plan.md` e `data-model.md` (ADR-202, 204, 205, 207, 208 revistas; 206, 210 ajustadas) e corrigir as datas (item 12).
3. Entregar: ADRs revisadas, **matriz de rastreabilidade** FR/INV/SC → módulo → teste, e critérios de teste de cada correção. Obter aprovação do plano.
4. `/arkan.tasks` (tasks `JV-T201…`, três blocos, ponto G3 por bloco), depois `/arkan.analyze`, implementação, QA.
5. Registrar a diretriz REW por decisão própria, se aprovado.

## 5. Como retomar (nova sessão)
- Repositório `Boguissimo/lab-sq-jarvis` (público). Clonar a branch: `git clone -b lab-sq-jarvis/003-000-jv-v02-honestidade-e-seguranca https://github.com/Boguissimo/lab-sq-jarvis`. Em sessão na nuvem, usar `add_repo` (push) antes.
- Ler: este arquivo, `docs/RETOMADA.md` (V01), `docs/revisoes/*`, e os artefatos da feature 003.
- Testes: `python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt`; no Linux, `apt-get install libegl1 libgl1 libxkbcommon0 libfontconfig1 libdbus-1-3` e `QT_QPA_PLATFORM=offscreen python -m pytest` (esperado: 45 passando).
- Convenções: Core do Arkan intacto; branches `lab-sq-jarvis/NNN-CCC-slug`; PT-BR; interface não calcula (ADR-03 do V01); limiares provisórios continuam provisórios; aprovação não verifica (JV-D032); status da feature só aceita `em-desenvolvimento`/`em-producao`/`arquivada`; `.sh` em LF; `.bat` em CRLF.
- Defeitos do Core já registrados (JV-D015): `qa-mecanico.sh` exige seções "N/A" em planos Doc e dá falso positivo para marcadores `[TODO]` (colchetes sem escape).
- Máquina do desenvolvedor (Windows): clone em `C:\Users\fabri\lab-sq-jarvis\lab-sq-jarvis` (pasta aninhada); banco do V01 em `%LOCALAPPDATA%\LabSQJarvis` com sessões que não podem ser perdidas.
- Decisões da spec já tomadas e **não** a reabrir sem motivo: um incremento em três blocos; arquivo do PC-Tool opaco; calibração = alinhamento de atrasos tipo ATM; SEG-02/07/09 só `não verificável`.
