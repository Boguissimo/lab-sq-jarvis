# Validação dos limiares provisórios — JV-V02 (SC-208)

> **Domínio simulado apenas** (E3): estes números saem do gerador e de oráculos analíticos; não validam nada no carro. Limiares não foram ajustados (P8). Gerado por `tests/test_validacao_limiares.py`.

## (a) Irregularidade σ̂

| cenário | σ injetado | σ̂ médio | erro máx. | fora de 15 % σ + 0,05 | classificações (aprov/aviso/reprov) |
| --- | --- | --- | --- | --- | --- |
| via plana LR4 | 0.30 | 0.299 | 0.056 | 0/50 | 50/0/0 |
| via plana LR4 | 0.45 | 0.449 | 0.085 | 0/50 | 47/3/0 |
| via plana LR4 | 0.55 | 0.549 | 0.105 | 0/50 | 5/45/0 |
| via plana LR4 | 1.00 | 0.998 | 0.193 | 0/50 | 0/50/0 |
| via plana LR4 | 1.40 | 1.397 | 0.269 | 1/50 | 0/41/9 |
| via plana LR4 | 1.60 | 1.596 | 0.306 | 2/50 | 0/8/42 |
| via plana LR4 | 2.00 | 1.995 | 0.382 | 2/50 | 0/0/50 |
| reflexão g=0,9 | 0.30 | 0.327 | 0.073 | 0/50 | 50/0/0 |
| reflexão g=0,9 | 0.45 | 0.477 | 0.099 | 0/50 | 35/15/0 |
| reflexão g=0,9 | 0.55 | 0.578 | 0.120 | 0/50 | 2/48/0 |
| reflexão g=0,9 | 1.00 | 1.032 | 0.188 | 0/50 | 0/50/0 |
| reflexão g=0,9 | 1.40 | 1.436 | 0.259 | 0/50 | 0/38/12 |
| reflexão g=0,9 | 1.60 | 1.637 | 0.283 | 0/50 | 0/7/43 |
| reflexão g=0,9 | 2.00 | 2.033 | 0.365 | 1/50 | 0/0/50 |
| reflexões múltiplas | 0.30 | 0.341 | 0.101 | 1/50 | 50/0/0 |
| reflexões múltiplas | 0.45 | 0.489 | 0.129 | 1/50 | 34/16/0 |
| reflexões múltiplas | 0.55 | 0.591 | 0.131 | 0/50 | 1/49/0 |
| reflexões múltiplas | 1.00 | 1.032 | 0.179 | 0/50 | 0/50/0 |
| reflexões múltiplas | 1.40 | 1.425 | 0.294 | 2/50 | 0/40/10 |
| reflexões múltiplas | 1.60 | 1.620 | 0.327 | 2/50 | 0/6/44 |
| reflexões múltiplas | 2.00 | 2.026 | 0.401 | 3/50 | 0/0/50 |
| cancelamento | 0.30 | 0.310 | 0.062 | 0/50 | 50/0/0 |
| cancelamento | 0.45 | 0.461 | 0.094 | 0/50 | 44/6/0 |
| cancelamento | 0.55 | 0.563 | 0.115 | 0/50 | 3/47/0 |
| cancelamento | 1.00 | 1.016 | 0.203 | 1/50 | 0/50/0 |
| cancelamento | 1.40 | 1.420 | 0.282 | 2/50 | 0/40/10 |
| cancelamento | 1.60 | 1.620 | 0.321 | 2/50 | 0/7/43 |
| cancelamento | 2.00 | 2.024 | 0.396 | 2/50 | 0/0/50 |

- **Critério por realização** (|σ̂ − σ| ≤ 15 % de σ + 0,05 dB): 22 de 1400 realizações fora. A média fica dentro em todos os cenários; a dispersão de uma realização isolada pode passar do critério com σ alto. Critério revisto pela E4 (viés médio + dispersão declarada, sem ampliar a tolerância); as realizações fora ficam registradas aqui e analisadas em `validacao-limiares-e4.md`.
- Fora do domínio: ruído correlacionado (janela de 8 pontos, σ = 1,0 dB) dá σ̂ médio **0.290 dB** — o estimador subestima ruído correlacionado (limite declarado E1).
- Suavização declarada: `nao_estimavel`, nunca aprovada.

## (b) Detector de mudança

| cenário | σ | detectada | não detectada | inconclusiva |
| --- | --- | --- | --- | --- |
| só polaridade (sem mudança de magnitude) | 0.5 | 0 | 200 | 0 |
| só polaridade (sem mudança de magnitude) | 1.0 | 0 | 200 | 0 |
| só polaridade (sem mudança de magnitude) | 1.5 | 20 | 180 | 0 |
| N3: ganho +3 dB | 1.5 | 200 | 0 | 0 |
| ganho +1,5 dB | 0.5 | 200 | 0 | 0 |
| ganho −1,5 dB | 0.5 | 200 | 0 | 0 |
| ganho +3 dB | 0.5 | 200 | 0 | 0 |
| PEQ +3 dB Q 2 em 6 kHz | 0.5 | 200 | 0 | 0 |
| PEQ −3 dB Q 4 em 6 kHz | 0.5 | 200 | 0 | 0 |
| corte 3,0 → 3,5 kHz | 0.5 | 200 | 0 | 0 |

- Posição de microfone diferente: `inconclusiva` (nenhuma diferença atribuída ao DSP).
- **Falsos positivos em “só polaridade”**: σ 0,5 → 0/200; σ 1,0 → 0/200; σ 1,5 → 20/200. O critério original do SC-208(b) (zero até σ = 1,5 dB) **não é atendido**: limitação conhecida, registrada pela E4 (indicativa × confirmada; ensaio ampliado em `validacao-limiares-e4.md`). Limiar não ajustado (P8).
- Limiares usados: média 1.0 dB; bandas max(1.5 dB; 3.0·σΔ).

## (c) Limites SEG

Valores de cadastro fictícios (80 Hz, 12 dB/oit, 50 W, estado confirmado), só para exercitar as fronteiras; limites da v0.4.0 não ajustados (P8; SEG-04 e SEG-05 provisórios). Falso aprovado = limite violado e regra aprovada; falso bloqueado = limite respeitado e regra bloqueada.

- SEG-01 passa-altas 70–90 Hz, passo 0,5: 41 pontos, falsos aprovados 0, falsos bloqueados 0
- SEG-01 passa-altas 79,99–80,01, passo 0,001: 21 pontos, falsos aprovados 0, falsos bloqueados 0
- SEG-01 inclinação 6–18 dB/oit, passo 0,25: 49 pontos, falsos aprovados 0, falsos bloqueados 0
- SEG-01 inclinação 11,99–12,01, passo 0,001: 21 pontos, falsos aprovados 0, falsos bloqueados 0
- SEG-01: sem cadastro confirmado, mínimo inválido ou destino ausente ⇒ nunca aprovada
- SEG-03 ganho 40–60 W, passo 0,5: 41 pontos, falsos aprovados 0, falsos bloqueados 0
- SEG-03 reforco_eq 40–60 W, passo 0,5: 41 pontos, falsos aprovados 0, falsos bloqueados 0
- SEG-03 49,999–50,001 W, passo 0,0005: 5 pontos, falsos aprovados 0, falsos bloqueados 0
- SEG-03: fronteira em 50 W (tolerância absoluta 1e-9 W); dado ausente/inválido ⇒ não verificável
- SEG-04 ganho 0,05–2 dB, passo 0,05: 40 pontos, falsos aprovados 0, falsos bloqueados 0
- SEG-04 reforco_eq 0,05–2 dB, passo 0,05: 40 pontos, falsos aprovados 0, falsos bloqueados 0
- SEG-04 vizinhança 1,499–1,501, passo 0,0005: 5 pontos, falsos aprovados 0, falsos bloqueados 0
- SEG-04: fronteira em +1,5 dB (provisório); redução e corte não se aplicam
- SEG-05 por filtro 2,5–3,5 dB, passo 0,05: 21 pontos, falsos aprovados 0, falsos bloqueados 0
- SEG-05 grade filtro × banda: 187 pontos, falsos aprovados 0, falsos bloqueados 0
- SEG-05: +3 dB por filtro e +6 dB na banda (provisório); banda não informada ⇒ não verificável
- SEG-06/13: categóricos; equipamento não confirmado nunca aprova SEG-01/03
- Admissibilidade: 36 reforços de 0 a 3,5 dB, todos bloqueados por SEG-02/07/09 (falso bloqueio por desenho); decrescentes dentro dos limites recomendados
