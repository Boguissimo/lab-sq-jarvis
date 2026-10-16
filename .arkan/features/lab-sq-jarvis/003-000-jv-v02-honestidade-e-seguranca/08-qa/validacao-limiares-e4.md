# Validação dos limiares provisórios — complemento da emenda E4 (SC-208)

> **Domínio simulado apenas.** Complementa `validacao-limiares.md`, que **permanece como foi gerado** (inclui os 22/1 400 resultados fora da tolerância e os falsos positivos indicativos originais). Nenhum limiar foi ajustado (P8). Gerado por `ferramentas/medir_e4.py` (sementes fixas).

## (a) σ̂ — viés, dispersão e distribuição do erro

Mesma bateria de `validacao-limiares.md` (4 cenários × 7 níveis de σ × 50 sementes = 1 400 realizações). Erro = σ̂ − σ injetado.

- **Global (N = 1400):** viés médio assinado +0.019 dB (2.8 % de σ); erro absoluto médio 0.067 dB; desvio-padrão 0.093 dB. Erro relativo (erro/σ), percentis 1/5/25/50/75/95/99: -18.6 % / -11.6 % / -2.6 % / +2.3 % / +8.3 % / +17.3 % / +23.0 %.
- **Fora da tolerância original** (|σ̂ − σ| > 15 % de σ + 0,05 dB): **22 de 1400** (1.6 %). Mantida a tolerância original; nada foi ampliado.

| σ injetado | N | viés (dB) | erro abs. médio | desvio-padrão | p5 | p95 | fora da tolerância (+/−) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.30 | 200 | +0.019 | 0.028 | 0.030 | -0.030 | +0.069 | 1 (1+/0−) |
| 0.45 | 200 | +0.019 | 0.035 | 0.040 | -0.045 | +0.084 | 1 (1+/0−) |
| 0.55 | 200 | +0.020 | 0.041 | 0.048 | -0.055 | +0.107 | 0 (0+/0−) |
| 1.00 | 200 | +0.019 | 0.063 | 0.078 | -0.127 | +0.157 | 1 (1+/0−) |
| 1.40 | 200 | +0.019 | 0.087 | 0.109 | -0.179 | +0.199 | 5 (2+/3−) |
| 1.60 | 200 | +0.018 | 0.097 | 0.124 | -0.205 | +0.225 | 6 (2+/4−) |
| 2.00 | 200 | +0.019 | 0.118 | 0.152 | -0.256 | +0.270 | 8 (3+/5−) |

| cenário | viés relativo | fora da tolerância | dos quais positivos |
| --- | --- | --- | --- |
| via plana LR4 | -0.2 % | 5/350 | 0 |
| reflexão g=0,9 | 4.3 % | 1/350 | 0 |
| reflexões múltiplas | 5.3 % | 9/350 | 6 |
| cancelamento | 1.9 % | 7/350 | 4 |

**Leitura (sem ajuste):** o desvio-padrão do erro cresce com σ (o erro relativo é aproximadamente constante), de modo que as realizações fora da tolerância se concentram nos σ altos (19 das 22 em σ ≥ 1,4 dB). Há um viés positivo pequeno (≈ +2 % de σ no conjunto) que vem sobretudo dos cenários com estrutura espectral real (reflexões múltiplas: viés relativo maior e 6 de 9 fora da tolerância positivas); na via plana o viés é ≈ 0. Isso é um erro **sistemático leve** do estimador na presença de estrutura, coerente com o limite declarado na E1 (σ̂ é irregularidade fina, não ruído direto).

### Classificação perto de 0,5 dB e 1,5 dB (200 sementes por linha)

Classe teórica pelo σ injetado: aprovada (< 0,5), aviso (0,5 a 1,5), reprovada (> 1,5). **Falsa aprovação** = classificada menos grave que a teórica; **falsa reprovação** = mais grave.

| cenário | σ injetado | classe teórica | aprovada | aviso | reprovada | falsas aprovações | falsas reprovações |
| --- | --- | --- | --- | --- | --- | --- | --- |
| via plana LR4 | 0.40 | aprovada | 200 | 0 | 0 | 0 | 0 |
| via plana LR4 | 0.45 | aprovada | 182 | 18 | 0 | 0 | 18 |
| via plana LR4 | 0.48 | aprovada | 134 | 66 | 0 | 0 | 66 |
| via plana LR4 | 0.50 | no limite | 97 | 103 | 0 | — | — |
| via plana LR4 | 0.52 | aviso | 58 | 142 | 0 | 58 | 0 |
| via plana LR4 | 0.55 | aviso | 25 | 175 | 0 | 25 | 0 |
| via plana LR4 | 0.60 | aviso | 4 | 196 | 0 | 4 | 0 |
| via plana LR4 | 1.30 | aviso | 0 | 193 | 7 | 0 | 7 |
| via plana LR4 | 1.40 | aviso | 0 | 152 | 48 | 0 | 48 |
| via plana LR4 | 1.45 | aviso | 0 | 128 | 72 | 0 | 72 |
| via plana LR4 | 1.50 | no limite | 0 | 97 | 103 | — | — |
| via plana LR4 | 1.55 | reprovada | 0 | 62 | 138 | 62 | 0 |
| via plana LR4 | 1.60 | reprovada | 0 | 39 | 161 | 39 | 0 |
| via plana LR4 | 1.70 | reprovada | 0 | 15 | 185 | 15 | 0 |
| reflexões múltiplas | 0.40 | aprovada | 182 | 18 | 0 | 0 | 18 |
| reflexões múltiplas | 0.45 | aprovada | 110 | 90 | 0 | 0 | 90 |
| reflexões múltiplas | 0.48 | aprovada | 58 | 142 | 0 | 0 | 142 |
| reflexões múltiplas | 0.50 | no limite | 32 | 168 | 0 | — | — |
| reflexões múltiplas | 0.52 | aviso | 18 | 182 | 0 | 18 | 0 |
| reflexões múltiplas | 0.55 | aviso | 4 | 196 | 0 | 4 | 0 |
| reflexões múltiplas | 0.60 | aviso | 1 | 199 | 0 | 1 | 0 |
| reflexões múltiplas | 1.30 | aviso | 0 | 183 | 17 | 0 | 17 |
| reflexões múltiplas | 1.40 | aviso | 0 | 144 | 56 | 0 | 56 |
| reflexões múltiplas | 1.45 | aviso | 0 | 113 | 87 | 0 | 87 |
| reflexões múltiplas | 1.50 | no limite | 0 | 73 | 127 | — | — |
| reflexões múltiplas | 1.55 | reprovada | 0 | 49 | 151 | 49 | 0 |
| reflexões múltiplas | 1.60 | reprovada | 0 | 31 | 169 | 31 | 0 |
| reflexões múltiplas | 1.70 | reprovada | 0 | 9 | 191 | 9 | 0 |

**Leitura:** a transição entre classes é gradual, com largura de cerca de ±0,1 a ±0,15 dB em torno de cada limite; a classificação nessa vizinhança é **probabilística**, não determinística. Nenhuma realização com σ ≥ 1,0 dB foi classificada `aprovada` nas duas famílias testadas. Com a reflexão múltipla, σ̂ tende a ficar acima de σ e a classificação antecipa o aviso (σ = 0,45: 45 % `aviso`).

## (b) Detector — indicativas, confirmadas e falsos negativos

Fluxo fiel ao serviço: **um** "antes" (semente k) e duas aquisições "depois" independentes (sementes k + 50 000 e k + 100 000). *Indicativa* = a primeira aquisição "depois" dá `mudança detectada`. *Confirmada (regra atual)* = as duas dão `mudança detectada`, mesmo sentido e concordância dentro do limiar das bandas (`sessao.py`). *Confirmada com faixa compatível (E4)* = a regra atual **e** interseção não vazia das faixas de frequência da mudança.

### Falsos positivos (só polaridade, sem mudança de magnitude; N = 1 000 por linha)

| σ | indicativas | confirmadas (regra atual) | confirmadas com faixa compatível (E4) | limite superior ≈95 % se 0 (regra dos três) |
| --- | --- | --- | --- | --- |
| 0.5 | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0.3 % |
| 1.0 | 0 (0.0 %) | 0 (0.0 %) | 0 (0.0 %) | 0.3 % |
| 1.5 | 87 (8.7 %) | 12 (1.2 %) | 10 (1.0 %) | — |
| 2.0 | 105 (10.5 %) | 14 (1.4 %) | 12 (1.2 %) | — |

**Leitura:** com σ ≤ 1,0 dB não houve alarme algum em 1 000 sementes. Com σ = 1,5 dB há alarmes indicativos e **também confirmações falsas**: a repetição reduz muito a taxa, mas **não a zera**, porque as duas comparações "depois × antes" compartilham o mesmo "antes" (o ruído do "antes" é comum às duas e não é repetido). A exigência de faixa compatível elimina só parte delas. O critério "zero falso positivo confirmado até σ = 1,5 dB" **não é atendido** pelo detector atual nesta bateria. É uma **limitação conhecida, não resolvida**: o detector não está validado quanto a falsos positivos confirmados, e qualquer limite futuro deve ser justificado e testado de forma independente. A região σ ≥ 1,5 dB coincide com o limite de reprovação da qualidade (`aviso`/`reprovada`).

**Custo operacional.** Com duas vias independentes e σ = 1,5 dB, a chance de pelo menos um alarme indicativo numa sessão é ≈ 16.6 % (cada alarme pede uma repetição). Com σ ≤ 1,0 dB foi 0 na bateria. Medir, no G3 e nas sessões reais, quantas repetições o detector pede em condições normais; se forem frequentes, revisar o detector em incremento posterior.

### Falsos negativos (mudança real; N = 300 por linha)

| cenário | σ | indicativas | confirmadas (regra atual) | confirmadas com faixa compatível (E4) |
| --- | --- | --- | --- | --- |
| N3 ganho +3 dB | 1.5 | 300/300 | 300/300 | 300/300 |
| ganho +1,5 dB | 0.5 | 300/300 | 300/300 | 300/300 |
| ganho +1,5 dB | 1.5 | 300/300 | 300/300 | 300/300 |
| ganho −1,5 dB | 1.5 | 300/300 | 300/300 | 300/300 |
| PEQ −3 dB Q4 6 kHz | 0.5 | 300/300 | 300/300 | 300/300 |
| PEQ −3 dB Q4 6 kHz | 1.5 | 296/300 | 293/300 | 293/300 |
| PEQ +3 dB Q2 6 kHz | 1.5 | 300/300 | 300/300 | 300/300 |

**Leitura:** a exigência de repetição não reduziu a detecção nos cenários de ganho (±1,5 e ±3 dB) nem no N3; a perda aparece no filtro estreito com ruído alto (PEQ −3 dB Q 4 em 6 kHz, σ = 1,5: 293/300 confirmadas). A faixa compatível não custou detecção em nenhum cenário medido.

## Reconciliação com `test_detector_validacao_200_sementes`

Esse teste codifica o critério **original** do SC-208(b) (zero alarme em 'só polaridade' a σ = 1,5 dB em 200 sementes) e está marcado `xfail` estrito: ele **falha de propósito**, o que coincide com este relatório e não o contradiz. Não há divergência de algoritmo nem de dados: o detector é o mesmo. Diferem só (i) as sementes do "depois" (teste: semente + 10 000; validação: + 50 000), o que dá 16/200 contra 20/200 — variação amostral da mesma taxa; com 1 000 sementes ambos dão 87/1 000; (ii) o critério de contagem (o teste para no primeiro alarme e também exige N3 detectado; a validação conta todos); (iii) a quantização não altera o resultado. A asserção e os limiares não foram alterados; só o texto do motivo do `xfail`, que estava desatualizado.

## Limitações estatísticas

- Domínio simulado; ruído gaussiano independente entre pontos (a mesma hipótese do estimador).
- N = 1 000 (falsos positivos) e 300 (falsos negativos) sementes por linha: taxas abaixo de ≈ 0,3 % não são resolvidas; "0 em 1 000" não é "zero".
- Poucas famílias de cenário; não há ruído correlacionado nem reposicionamento nesta bateria.
- A bateria varia σ de modo uniforme entre antes e depois; diferenças de σ entre aquisições não foram varridas.
