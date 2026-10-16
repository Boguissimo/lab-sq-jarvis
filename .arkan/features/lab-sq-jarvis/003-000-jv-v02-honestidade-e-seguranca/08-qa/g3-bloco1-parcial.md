# G3 do bloco 1 (JV-T223) — registro parcial

> **Parcial: o G3 do bloco 1 NÃO está concluído.** Execução do desenvolvedor no Windows em 16/10/2026, mais conferência por código no Linux.

## Evidências recebidas do Windows (commit `6bf4ea7`, branch `claude/busy-bohr-25s6e5`)
- Python 3.13.7, PySide6 6.10.2; 212 testes coletados: **211 passando, 1 `xfail` esperado**, 31,64 s, interface incluída. Não precisa repetir sem mudança relevante de código.
- `INICIAR-JARVIS.bat` abriu a janela JV-V02; aviso de dados simulados visível; três sessões anteriores no Histórico; uma sessão V01 encerrada reaberta com gráfico, diagnóstico, veredito e decisão preservados.
- REF-001-N3, análise inicial: qualidade aprovada (σ̂ máx. 0,23 dB); déficit da soma de 63,5 dB perto de 3 kHz; fase média 179,8°; hipótese prioritária polaridade invertida; atraso e crossover como alternativas; teste reversível de uma variável proposto. Interface compreensível.

## Ainda não conferido (manual)
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
