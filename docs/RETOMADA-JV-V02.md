# Retomada — JV-V02 (atualizada em 2026-10-15)

Branch: `lab-sq-jarvis/003-000-jv-v02-honestidade-e-seguranca` · feature Arkan `003-000-jv-v02-honestidade-e-seguranca` · fase `04-architecture` **concluída** (spec e plano aprovados). Próximo: `/arkan.tasks`.
`main` contém o JV-V01 completo (commit `389e580`, QA aprovado, G3 cumprido no Windows). Esta branch parte dele.

## 1. Estado do JV-V02
| Fase | Artefato | Estado |
| --- | --- | --- |
| 01 Ideação | `01-discovery/ideacao.md` | aprovada (peso Code; superfície crítica: sim) |
| 03 Spec | `03-spec/spec.md` (FR-201 a FR-223, INV-201 a INV-214, SC-201 a SC-209) | aprovada em 2026-10-15, com as emendas **E1**, **E2** e **E3**, todas aprovadas em nível B; decisões nas Clarifications |
| 04 Plano | `04-architecture/plan.md` (ADR-201 a ADR-212), `data-model.md`, `quickstart.md` | revisão **R1** e complementos **R1.1** e **R1.2** aprovados em nível B; inclui a matriz de rastreabilidade (46 IDs, conferida por script) e os critérios de teste |
| 06 Tasks | — | **próximo passo** |

Nenhum código do V02 foi escrito. Testes do V01: 45 passando.

Commits: `2f0e8f1` (E1/R1), `1f6b62d` (E2/R1.1), `45f6401` (E3/R1.2 + revisão adversarial).

## 2. O que cada emenda decidiu (resumo; detalhe nas Clarifications da spec)
- **E1 — revisão técnica externa** (`docs/revisoes/jv-v02-revisao-tecnica-do-plano.md`):
  - irregularidade σ̂ por MAD da segunda diferença; o método antigo reprovava o próprio REF-001-A;
  - detector de mudança por via, nas duas vias, com três resultados;
  - admissibilidade SEG pela classe de risco;
  - INV-211 (interpretação lida do registro, sem recálculo) e INV-212 (incerteza desconhecida não vira aprovação);
  - "reversão documentada";
  - precedência e casos-limite da etapa de calibração;
  - SC-208 (varredura de limiares);
  - datas corrigidas para a data local.
- **E2 — decisões sobre a R1:**
  - "ruído não estimável" preserva as observações descritivas;
  - fixture do banco V01 gerada pelo V01 original, só sintética e permanente;
  - casos de segurança REF-003-S1 a S3 (FR-223, SC-209);
  - casos de referência inalterados (INV-213).
- **E3 — revisão adversarial** (`docs/revisoes/revisao-adversarial-projeto.md`, A01 a A09):
  - REF-003-S1 **bloqueado por SEG-07**, sem exceção para simulação;
  - referência temporal e aquisição comparável **declaradas**; `confirmada` exige aquisição comparável;
  - mudança só medida exige repetição por **aquisições independentes**, e mudança reproduzida não identifica o parâmetro;
  - presunções só para catálogo interno com **proveniência verificada** por hash (INV-214);
  - SC-208 restrito ao domínio simulado, com oráculos e testes metamórficos;
  - objetivo da etapa sem alegar alinhamento;
  - **ADR-212**: correções do V01 na fundação (portão básico obrigatório, cofre atômico, referência com campos obrigatórios);
  - esforço no G3 (dados sintéticos) separado da utilidade real (VP-10).

## 3. Pendências fora do V02
- **Diretriz REW** (`docs/revisoes/diretriz-fontes-de-medicao-e-rew.md`): registrar no planejamento evolutivo (proposta `JV-D043` e nota no feature map para F004/F013/F018) **com aprovação do desenvolvedor**.
- **VP-10 (utilidade real):** avaliar em incremento com medições reais.

## 4. Próximos passos
1. `/arkan.tasks`: tasks `JV-T201…`, nos três blocos com ponto G3 por bloco, mais a fase 0. A fase 0 traz as correções do V01 (ADR-212), a migração (ADR-207), a interpretação congelada, o modelo físico e o catálogo, e os contratos de qualidade e segurança.
2. `/arkan.analyze`, implementação, QA.

## 5. Como retomar (nova sessão)
- Repositório `Boguissimo/lab-sq-jarvis` (público). Na máquina do desenvolvedor, o **clone de trabalho** é `C:\Users\fabri\src-jv\repo`. A pasta `C:\Users\fabri\lab-sq-jarvis` é um pacote extraído em 2026-09-30, **sem `.git`**, e não deve ser editada.
- Para clonar em outro lugar: `git clone -b lab-sq-jarvis/003-000-jv-v02-honestidade-e-seguranca https://github.com/Boguissimo/lab-sq-jarvis`. No Windows, use um caminho curto: o clone em pasta muito longa falhou com "`$GIT_DIR` too big".
- Leia este arquivo, `docs/RETOMADA.md` (V01), `docs/revisoes/*` e os artefatos da feature 003.
- **Testes:** `python -m venv .venv` e `pip install -r requirements-dev.txt`. No Linux, instale `libegl1 libgl1 libxkbcommon0 libfontconfig1 libdbus-1-3` e rode `QT_QPA_PLATFORM=offscreen python -m pytest` (esperado: 45 passando). Há uma venv pronta em `C:\Users\fabri\lab-sq-jarvis\.venv`; o `python` do PATH no Windows é o atalho da Microsoft Store e trava.
- **Git neste clone:** sem identidade configurada; os commits usam `-c user.name=Claude -c user.email=noreply@anthropic.com`, como os anteriores da branch.
- **Convenções:**
  - Core do Arkan intacto; PT-BR; branches `lab-sq-jarvis/NNN-CCC-slug`.
  - A interface não calcula (ADR-03 do V01); limiares provisórios continuam provisórios; aprovação não verifica (JV-D032).
  - Emendas normativas exigem aprovação de nível B (ato e escopo nomeados).
  - O status da feature só aceita `em-desenvolvimento`, `em-producao` ou `arquivada`.
  - `.sh` em LF; `.bat` em CRLF.
- **Defeitos do Core já registrados (JV-D015):** `qa-mecanico.sh` exige seções "N/A" em planos Doc e dá falso positivo para marcadores `[TODO]` (colchetes sem escape).
- **Banco do V01** em `%LOCALAPPDATA%\LabSQJarvis`, com sessões que não podem ser perdidas. A migração (ADR-207) faz backup antes de mexer.
- **Decisões a não reabrir sem motivo:**
  - um incremento em três blocos; arquivo do PC-Tool opaco; calibração = alinhamento de atrasos tipo ATM;
  - SEG-02/07/09 só `não verificável`, e nenhum reforço é admitido;
  - presunções só para catálogo com proveniência verificada.
