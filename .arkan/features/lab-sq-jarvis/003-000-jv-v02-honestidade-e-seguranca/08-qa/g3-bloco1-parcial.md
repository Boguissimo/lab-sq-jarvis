# G3 do bloco 1 (JV-T223) — registro parcial

> **Parcial: o G3 do bloco 1 NÃO está concluído.** Execução do desenvolvedor no Windows em 16/10/2026, mais conferência por código no Linux.
> **Atualizado em 17/10/2026:** novas evidências **do Codex** no Windows e suíte automatizada (seção abaixo). **Continua parcial: não houve aceite humano inequívoco do G3 completo.**

> **Três classes de evidência neste registro, nunca somadas como aceite:** (1) **execução do Codex** (agente rodando no Windows real; relatada a este registro); (2) **evidência automatizada** (suítes de testes); (3) **validação humana** (Fabrício, no Windows). Só a classe 3 pode fechar o G3.

## Evidências recebidas do Windows (commit `6bf4ea7`, branch `claude/busy-bohr-25s6e5`)
- Python 3.13.7, PySide6 6.10.2; 212 testes coletados: **211 passando, 1 `xfail` esperado**, 31,64 s, interface incluída. Não precisa repetir sem mudança relevante de código.
- `INICIAR-JARVIS.bat` abriu a janela JV-V02; aviso de dados simulados visível; três sessões anteriores no Histórico; uma sessão V01 encerrada reaberta com gráfico, diagnóstico, veredito e decisão preservados.
- REF-001-N3, análise inicial: qualidade aprovada (σ̂ máx. 0,23 dB); déficit da soma de 63,5 dB perto de 3 kHz; fase média 179,8°; hipótese prioritária polaridade invertida; atraso e crossover como alternativas; teste reversível de uma variável proposto. Interface compreensível.

## Atualização de 17/10/2026 — evidências do Codex no Windows (execução do agente; não é aceite humano)

**Commit publicado: `7c3104a`** (autor Codex), em `claude/busy-bohr-25s6e5`; conferido no remoto antes deste registro. Duas correções, ambas em código (`src/jarvis/rew_texto.py` +3 linhas; `src/jarvis/interface/janela.py` +2 linhas; `tests/test_interface.py` +1 teste), **sem alterar métodos ou limiares** (segundo a mensagem do commit, autorizadas por Fabrício na conversa com o Codex; esta autorização não foi verificada por este registro):
1. **Identificação de pasta no Windows:** abrir uma pasta como se fosse arquivo gerava `PermissionError` no Windows; agora a pasta é identificada antes da leitura e a mensagem diz "isto é uma pasta, não um arquivo". (Achado só possível na execução real no Windows; no Linux o caso já era tratado.)
2. **Marcação "reconstruída pelas regras 1.0":** a origem da interpretação passa a aparecer na análise de sessões V01, sem alterar registros históricos (teste `test_sessao_v01_mostra_interpretacao_reconstruida_sem_alterar_registros`).

### 1) Execução do Codex no Windows real (relatada; sem artefato de evidência no repositório)
- Suíte completa da versão corrigida: **243 passando e 1 `xfail` esperado**. Clone operacional atualizado; **32 testes de entrada e interface passaram nele**.
- **Backup V01 e base operacional íntegros**, com hashes preservados; registros antigos e cofre conferidos. *(Os valores dos hashes não foram fornecidos a este registro.)*
- **Na cópia isolada dos dados**, pela interface: análises de **A, B, N1, N2, N4 e N5** conferidas; **B e N3 até o veredito**; **N3 preservado após fechar e reabrir**; justificativa pré-preenchida de N5 conferida.
- **Na instalação operacional atualizada:** sessão V01 reaberta e **marcação de reconstrução confirmada**.

### 2) Evidência automatizada
- Windows (relatada pelo Codex): 243 + 1 `xfail`. **Linux/nuvem (reproduzida neste registro em `7c3104a`): 243 passando e 1 `xfail`.** Aumento de 242 para 243 = o teste novo da marcação V01.
- Conferência por código (Linux) dos vereditos por caso: tabela já registrada abaixo; **não substitui** o Windows.

### 3) Validação humana
- **Somente a de 16/10/2026** (Fabrício, commit `6bf4ea7`): suíte no Windows (211 + 1), `INICIAR-JARVIS.bat`, aviso de simulação, três sessões no Histórico, sessão V01 reaberta com gráfico, diagnóstico, veredito e decisão preservados, N3 até a análise inicial. **Nenhuma** das verificações do Codex acima foi presenciada ou aceita por Fabrício neste registro.

### Cobertura do roteiro curto (`COMO-EXPERIMENTAR.md`, "G3 do bloco 1 — o que falta")
| Item do roteiro | Codex (Windows, relatado) | Automatizado | Humano (Fabrício) |
| --- | --- | --- | --- |
| 1a. Backup `jarvis.antes-v02-<data>.db` | backup V01 e base operacional íntegros, hashes preservados | testes de migração (nuvem) | **pendente** |
| 1b. Marcação "reconstruída pelas regras 1.0" | confirmada na instalação operacional atualizada | teste novo (Linux e Windows) | **pendente** |
| 2. N3 até o veredito | conferido na cópia isolada | conferência por código (Linux) | **pendente** (só a análise inicial, em 16/10) |
| 3. A, B, N1, N2, N4, N5 | análises conferidas pela interface (cópia isolada); B até o veredito; justificativa de N5 conferida | conferência por código (Linux) | **pendente** |
| 4. Fechar e reabrir | N3 preservado (cópia isolada); V01 reaberta (instalação operacional) | testes de persistência | V01 reaberta em 16/10; o resto **pendente** |

### O que resta para o aceite humano do G3 do bloco 1
Fabrício, no Windows dele, executar ou presenciar o roteiro curto (itens 1 a 4 acima) **e declarar o aceite**; em particular: ver o backup `jarvis.antes-v02-<data>.db` na pasta de dados; ver a marcação "reconstruída pelas regras 1.0" numa sessão V01; levar o N3 ao veredito; abrir A, B, N1, N2, N4 e N5; fechar e reabrir. Enquanto isso, **JV-T223 permanece parcial**. Fica também como marco da validação operacional o pacote **T250 + T251** (testes de entrada de arquivos), ainda sem aceite humano no Windows.

## Ainda não conferido (manual) — situação em 16/10/2026; veja a atualização de 17/10/2026 acima
Backup `jarvis.antes-v02-<data>.db` e marcação "reconstruída pelas regras 1.0"; N3 até o veredito; A, B, N1, N2, N4, N5; fechar e reabrir. Roteiro curto em `COMO-EXPERIMENTAR.md`.

## Conferido por código (Linux, serviço + `_texto_verificacao`, não substitui o Windows)
| Caso | Mudança por via | Veredito | Pede repetição? |
| --- | --- | --- | --- |
| REF-001-A, B | sem medição individual "depois" | confirmada | não |
| REF-001-N3 (duas aquisições) | reproduzida | comprometida | não |
| N3-sem-repeticao | indicativa | **inconclusiva** | **sim (1)** |
| N3-reposicionamento | indicativa | inconclusiva | sim (1) |
| N3-posicao-diferente | verificação inconclusiva | inconclusiva | não |
| N3-so-declarada / so-medida / ruido-alto | — / reproduzida / reproduzida | comprometida | não |
N1, N2, N4, N5: o programa recusa o teste de polaridade (esperado). **Contagem em condições normais:** 0 repetições pedidas nos casos distribuídos; 1 só nas variantes de teste que simulam uma única aquisição. Em uso real o custo continua a medir (SC-208(b)).

## Correção documental
`COMO-EXPERIMENTAR.md` ainda dizia "o parâmetro alterado não é identificado pela medição"; trocado por "a medição não identifica a causa" e "não comprova alteração no DSP" (E4).
