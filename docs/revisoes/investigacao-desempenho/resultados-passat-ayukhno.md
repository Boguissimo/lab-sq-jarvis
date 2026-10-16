# Resultados — VW Passat B8 (`ayukhno/autosound-measurements`): F-5 em carro, janelas e falhas injetadas

> **Exploração com medições reais de um carro, uma sessão (20/08/2026), um veículo.** Falhas **injetadas** por código em IRs reais (classe R-injetado, **não** são problemas de campo). Somas **calculadas** (adição complexa), não medidas. **Não** altera estimador, portão, limiares, spec ou `src/`; **não** valida nem reprova o V02. 2026-10-16.
> Fonte: commit `7725d42…` (CC BY 4.0, atribuição: *autosound-measurements (ayukhno), CC BY 4.0*); 63 arquivos conferidos por SHA-256 antes de cada execução. Pré-registro: `ferramentas/investigacao/preregistro-passat.json` (SHA-256 `ae6ce1f2…bd1fe`), commitado em `0da59fc` **antes** de qualquer cálculo. Código: `passat_{comum,f5,jarvis,faixa}.py`. Números: `passat-f5.json`, `passat-jarvis.json` (80 casos), `passat-faixa-posthoc.json`.
> Ordem real: pré-registro → F-5 → Jarvis → **só então** o descritivo por faixa (post hoc, rotulado). Desempate de pontuação fixado no código antes de ver resultados.

## 1. Cinco conceitos separados (o que cada medida diz)
| Conceito | Medida usada | Resultado no Passat (200 Hz–10 kHz, mids) |
| --- | --- | --- |
| **Integridade da aquisição** | SNR do REW, coerência (Resonalyze, bloco A), loopback físico, hash | SNR 44–55 dB nos canais de médios/woofers (sub 33 dB); coerência ≈ 1 na banda útil; arquivos íntegros |
| **Repetibilidade** | desvio entre capturas no mesmo ponto de frequência (microfone em tripé) | `m_L` (3 capturas): **0,39–0,43 dB** mediano; deslocamentos de nível ≤ 0,13 dB. `w_R` × retake: **0,20–0,24 dB (40–500 Hz)** e **1,5–1,6 dB (200 Hz–10 kHz)** |
| **Estrutura espectral** | σ̂ da média das capturas | ≈ σ̂ de cada captura (m_L 48 ppo: 0,75 × 0,61–0,85; 96 ppo: 0,24 × 0,23–0,26): o σ̂ vem da estrutura estável |
| **Incerteza de medição (ruído aleatório)** | ruído esperado pela coerência: σ ≈ 8,686·√((1−γ²)/(2γ²·4)) | **0,03–0,20 dB** na banda útil (aproximação; bloco A, outro programa) |
| **Admissibilidade para a análise** | classe do portão do produto (σ̂ 200 Hz–10 kHz) | depende da grade e da janela (§2) |
Observações: a **variabilidade entre capturas (0,2–0,4 dB) é muito maior que o ruído aleatório esperado (≤ 0,2 dB)** e é **suave em frequência** (σ̂ do resíduo entre capturas só 0,06–0,33 dB): é deriva observada de origem ainda não identificada (posição, operador e outros fatores não foram separados), não ruído branco. Os números de `w_R` reproduzem, por pipeline independente, o que o autor relata (0,19 dB abaixo de 150 Hz; 1,3–3,0 dB acima de 500 Hz), o que dá confiança na conversão IR→frequência.

## 2. F-5: σ̂ sob grade e janela (produto, chamada direta)
| Curva | Grade | σ̂ (W30) | σ̂ (Wfull) | Classe (W30 / Wfull) |
| --- | --- | --- | --- | --- |
| `m_L` (3 capturas) | 48 ppo | 0,61–0,82 | 0,67–0,85 | aviso / aviso |
| `m_L` (3 capturas) | 96 ppo | 0,23–0,26 | 0,23–0,26 | aprovada / aprovada |
| `w_R`, `w_R-retake` | 48 / 96 ppo | 0,90–1,05 / 0,36 | 1,05–1,07 / 0,38–0,47 | aviso / aprovada |
| `tw_L`, `tw_R` (banda do produto, abaixo da passagem do HPF de 1 kHz) | 48 ppo | 0,63–0,85 | **2,02–2,18** | aviso / **reprovada** |
| `sw` | 48 ppo | 1,21 | **2,53** | aviso / **reprovada** |
| **RTA espacial** (11 curvas, 96 ppo nativos, 150 médias) | nativa | 0,05–0,12 | — | **aprovada 11/11** |

- **Grade:** dobrar a densidade (48 → 96 ppo) leva o mesmo `m_L` de "aviso" para "aprovada". O desvio entre capturas (≈ 0,4 dB) fica **entre** os dois σ̂ (0,75 e 0,24): **o σ̂ superestima a variabilidade numa grade e a subestima na outra.**
- **Janela:** para os médios (dentro da banda), W30 e Wfull dão σ̂ quase iguais; para canais **fora da própria banda** (tweeters abaixo de 1 kHz, sub acima de 150 Hz), a IR inteira inclui cauda e ruído e o σ̂ salta (até "reprovada"). A janela importa sobretudo onde a via não toca.
- **Contraste com a sala do joeglondon:** lá, 25/25 aquisições "reprovada" (2,4–4,6 dB); aqui, médios em carro 0,2–0,8 dB e RTA espacial 0,05–0,12 dB. **O portão não rejeitou medição repetível do carro** na faixa útil dos médios; só a rejeitou fora de banda (esperado). Uma sala, um carro: não generalizar.

## 3. D-real e H: Jarvis sobre vias reais, soma calculada, falhas injetadas (80 execuções)
Cinco pares (`w_L+m_L`, `m_L+tw_L`, `w_R+m_R`, `m_R+tw_R`, `sw+w_L`) × janelas (W30, Wfull) × 48/96 ppo × {controle, polaridade invertida, atraso 0,25 ms, atraso 1,0 ms} na via B. Metadados transcritos do README/manifesto da fonte (loopback físico, 96 kHz, tripé), DSP declarado "normal".

| Injeção | Acertos | Erros | Abstenções (nao_da_para_concluir) |
| --- | --- | --- | --- |
| Polaridade invertida | **0** | 16 | 4 |
| Atraso 0,25 ms | **0** | 16 | 4 |
| Atraso 1,0 ms | **0** | 16 | 4 |
| Controle (sem pontuação de falso positivo) | — | — | — |

- **Nenhuma falha injetada foi reconhecida.** Os "erros" são a mesma hipótese de **reflexão/interferência** dada também no **controle**: a saída do Jarvis **não muda** com a injeção. As abstenções vêm do portão ("reprovada": tweeter fora de banda, sub fora de banda).
- **A fase vê a inversão, a regra não a usa:** a média da diferença de fase desloca **exatamente 180°** entre controle e polaridade (ex.: 93,9° → −86,1°), mas a Regra 2 exige dispersão ≤ 15° e o par real tem 54–150° (faixa de sobreposição de banda larga, 20 Hz–20 kHz).
- **Post hoc, restrito a uma faixa operacional do par** (chamada direta de `calculos.diferenca_fase`; faixas 150–400 Hz, 2–4 kHz, 60–150 Hz escolhidas pelas faixas úteis, não ajustadas): a dispersão **continua grande (39–130°)**. Em drivers reais **sem crossover projetado**, a diferença de fase natural não é constante; "oposição constante de 180°" não é assinatura utilizável. A **inversão desloca a média em 180° e inverte o sinal do ganho previsto da inversão** (ex.: `w_L+m_L` +7,6 → −7,6 dB), mas o **controle natural já tem valores não nulos** (−1,1 a +7,6 dB): sem referência, não há limiar óbvio; a inferência exige comparar com uma previsão ou com um estado anterior.
- **Atraso:** o `atraso_equivalente` do produto muda com a injeção (ex.: `w_L+m_L` 0,54 → 0,79 → 1,54 ms), mas a hipótese "diferença de tempo" só é considerada dentro do ramo de polaridade; sem oposição constante ela nunca aparece.

## 4. Classificação
| Achado | Classe |
| --- | --- |
| Regra 2 (oposição constante ≤ 15°) não detecta polaridade em drivers reais sem crossover | **Limitação de domínio** (a regra supõe vias com crossover projetado em fase) e **deficiência metodológica** para o uso real (a "assinatura" não existe em sistemas não alinhados) |
| Sobreposição/fase de banda larga, sem faixa operacional da via | Limitação de domínio (F-6) |
| Regra 3/hipótese de reflexão idêntica com e sem injeção | Deficiência metodológica (F-3); **sem contar falsos positivos** |
| σ̂ dependente de grade e janela; super e subestima | Questão metodológica (F-5) |
| Sucesso nos casos sintéticos (REF-001) não se transfere a vias reais sem crossover | Resultado central desta rodada: **os testes sintéticos não validam o uso real** |
| Soma calculada, injeção ideal, um carro, uma sessão | Limites desta evidência |

## 5. Limitações obrigatórias
Um veículo e uma sessão (tripé; deriva ±0,6 amostra não corrigida); somas calculadas pressupõem linearidade e invariância no tempo; injeções ideais (exatamente −1 ou N amostras); estado do DSP "cru" (sem crossover), que **não é o estado de uma calibração**; escolhas do harness (bin FFT mais próximo, janelas de 30 ms e 1,7 s, 48/96 ppo); o ruído esperado pela coerência vem de outro programa; nada disso mede utilidade para o ouvinte.

## 6. Conclusões e alternativas (para decisão humana; nada implementado)
1. **σ̂ (F-5):** três coisas diferentes — rugosidade espectral (σ̂), repetibilidade (desvio entre capturas, suave em frequência) e ruído aleatório (≈ 0,03–0,2 dB, coerência) — **não são equivalentes e variam com grade e janela**. Evidência a favor de: (a) declarar a escala (grade) em que σ̂ vale; (b) estimar repetibilidade por capturas repetidas, separada da rugosidade; (c) usar coerência quando houver. Para o portão, a leitura segura é "σ̂ pequeno = qualidade confirmada; σ̂ grande ≠ ruído".
2. **Diagnóstico de polaridade/tempo em vias reais:** pede **comparar com previsão ou com estado anterior** (ganho previsto da inversão, soma medida × soma prevista, antes/depois) e **faixa operacional por par**, em vez de oposição constante; é o caminho já presente em `propor_teste` (a previsão da inversão).
3. **Evitar expandir:** esta rodada fecha com 1 carro e 1 sala; o próximo ganho vem de **um caso em que a falha seja real e documentada** (antes/depois), não de mais injeções.
