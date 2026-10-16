# Metrologia em cinco dimensões e experimento rigor × facilidade de uso — sala (joeglondon)

> **Exploração com medições reais de uma sala, 5 repetições de uma sessão.** Não valida nem reprova o V02; não altera `src/`, spec, limiares nem arquitetura. Dados de terceiros não redistribuídos (só números derivados). 2026-10-16.
> Fonte: `joeglondon/speakers-2026-filters` @ `799af51` (53 arquivos conferidos por SHA-256 antes de cada execução). Pré-registro: `ferramentas/investigacao/preregistro-metrologia-rigor.json` (SHA-256 `21087a4f…3f63`), commitado em `15b26ee` **antes** de qualquer cálculo. Código: `metrologia_cinco_dimensoes.py`, `rigor_usabilidade.py`. Números: `metrologia-cinco-dimensoes-joeglondon.json`, `rigor-usabilidade-joeglondon.json`.
> Não repete: σ̂ por repetição e repetibilidade em 30–150 Hz (já em `repetibilidade-sigma-joeglondon.json` e `resultados-braco-a-joeglondon.*`).

## Parte M — as cinco dimensões (mediana por ponto entre as 5 repetições)
| Via | Integridade | Repetib. nível 30–150 Hz | Repetib. nível 200 Hz–10 kHz | Fase 200 Hz–10 kHz | Parte suave × rápida do resíduo (48 ppo, RMS dB, 200–10 k) | σ̂(média) ÷ σ̂(captura) |
| --- | --- | --- | --- | --- | --- | --- |
| L | íntegra | 0,09 dB | 0,18 dB | 1,2° | 0,05 × 0,08 | 0,99 |
| R | íntegra | 0,11 dB | 0,26 dB | 2,8° | 0,13 × 0,19 | 1,02 |
| Sub Only | íntegra | 0,06 dB | **3,75 dB** | **59,7°** | 0,40 × 0,37 | 0,87 |
| L + Sub | íntegra | 0,04 dB | 0,39 dB | 30,3° | 0,12 × 0,36 | 1,03 |
| R + Sub | íntegra | 0,05 dB | 0,16 dB | 1,9° | 0,03 × 0,04 | 1,00 |
Integridade: 54 614 pontos, finitos, frequência crescente, mesma grade (passo 0,366 Hz) nas 5 repetições e nos 5 arquivos.

- **Repetibilidade:** na banda do subwoofer (30–150 Hz) é muito boa (≤ 0,11 dB). Na banda do V02 é boa para L e R (0,2–0,3 dB) e **ruim para o Sub Only** (3,7 dB; fase 60°), que está fora da sua própria banda (ruído, não repetibilidade da via).
- **Suave × rápida:** no 30–150 Hz as duas partes são parecidas; em 200 Hz–10 kHz a parte rápida (ruído) domina em L, R e L+Sub, e no Sub Only as duas são grandes. **Não apareceu deriva suave dominante nesta sala** (ao contrário do Passat). Isso é compatível com repetições feitas sem mover o microfone; os dados não dizem se houve reposicionamento.
- **Estrutura:** σ̂ da média ≈ σ̂ da captura (razão 0,87–1,03): a rugosidade vem da estrutura estável da sala, não do ruído, de modo que repetir não melhora σ̂ (consistente com F-5). A razão 0,87 do Sub Only é o único efeito do ruído.
- **Incerteza (tipo A):** `u(n) = s/√n`; tipo B (calibração do microfone, posição) **não estimada**.

### Admissibilidade por análise (regra pré-registrada: admissível se 2·√2·u ≤ ½ efeito; marginal se ≤ efeito)
Efeitos: 1 dB (nível/balanço), 0,25 ms (tempo; convertido em graus em cada banda), 180° (polaridade; admissível se ≤ 90°).
| Via (200 Hz–10 kHz) | n=1 | n=3 | n=5 |
| --- | --- | --- | --- |
| L, R | nível **marginal**; tempo e polaridade admissíveis | tudo admissível | tudo admissível |
| R + Sub | tudo admissível | tudo admissível | tudo admissível |
| L + Sub | nível **não admissível**; tempo marginal | nível marginal | admissível |
| Sub Only | nível e tempo **não admissíveis**; polaridade marginal | nível não adm.; tempo marginal | nível não adm.; tempo marginal |
Na banda 30–150 Hz tudo é admissível já com n=1 (exceto L+Sub, tempo marginal com n=1).
**Nota de honestidade:** a regra registrada resumia a banda pela mediana entre L, R e Sub Only (resumo no JSON), o que **esconde o Sub Only**. A tabela acima é por via e é **complemento post hoc**, rotulado; o pré-registro não foi alterado. Lição de método: a admissibilidade por análise precisa ser **por via e por banda operacional da via**, nunca um resumo único. É o mesmo argumento da faixa operacional por via do mapa técnico.

## Parte E — rigor × facilidade de uso (custo em varreduras por via)
| Modo | Varreduras/via | Q1 soma prevista (P95 do erro) | Q3 atraso (P95) | Q4 ganho da inversão (P95) | Q5 balanço L/R (P95) | Q6 σ̂ (P95) | Q2 admissível (concordância) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S (simplificada) | 1 | 0,046 dB | 0,036 ms | 0,18 dB | 0,048 dB | 0,11 dB | 100 % |
| R2 (2 repetições) | 2 | 0,028 dB | 0,042 ms | 0,10 dB | 0,040 dB | 0,10 dB | 100 % |
| R3 (3 repetições) | 3 | idêntico ao R2 (ver abaixo) | | | | | 100 % |
| A (adaptativo, τ = 0,3 dB) | 2,0 (parou em 2 nas 240 ordens) | idêntico ao R2 | | | | | 100 % |
Critério pré-registrado: P95 do erro ≤ ½ efeito (1 dB, 0,25 ms, 1 dB, 1 dB, 0,5 dB). **Todos os modos, inclusive a aquisição simplificada de 1 varredura, atendem a todos os critérios nesta sala.**

### Leitura e limites (sem extrapolar)
1. **Resultado:** nesta sala, em 30–150 Hz (soma, atraso, inversão) e para balanço L/R e σ̂ em 200 Hz–10 kHz, **uma única varredura reproduz a decisão** do conjunto das demais repetições com erro muito abaixo do que a decisão exige. Repetir não traz ganho de decisão aqui; o adaptativo nunca pediu a 3ª repetição.
2. **R3 = R2 por construção, não por coincidência:** com N = 5, o complemento de um subconjunto de 3 é um par; as diferenças |Q(3) − Q(2)| são as mesmas dos pares. O desenho não distingue R2 de R3. Distinguir exigiria mais repetições por ponto.
3. **A referência é o complemento (ruidoso):** o erro está **superestimado** (conservador). Não há verdade independente.
4. **Isto é um limite superior do que repetir traz, não prova de que repetir seja desnecessário.** As cinco repetições parecem do mesmo ponto, sem reposicionamento. O Passat (carro) mostrou variabilidade entre capturas 0,2–0,4 dB, suave em frequência (deriva observada de origem ainda não identificada; posição e outros fatores não foram separados), que repetições sem mover o microfone **não** capturam. A pergunta "quanta repetição detecta mudança de posição" **não é respondida** aqui.
5. **O custo é só contagem de varreduras.** Não mede tempo, esforço nem experiência de usuário; para isso é preciso estudo com pessoas.
6. A banda do Sub Only acima da sua faixa é inadmissível independentemente de n: **mais varreduras não corrigem via fora de banda.** O que corrige é declarar a faixa operacional da via.

## Classificação dos achados
| Achado | Classe |
| --- | --- |
| Uma varredura basta para as decisões testadas na sala, nas bandas úteis das vias | Resultado limitado a 1 sala/1 sessão/posição fixa |
| Admissibilidade por análise tem de ser por via e por banda operacional (o resumo mediano esconde o Sub Only) | Deficiência de método do próprio pré-registro, corrigida em complemento rotulado; reforça a diretriz de faixa operacional |
| σ̂ não melhora com repetição (rugosidade estrutural) | Confirma F-5; repetibilidade e σ̂ são grandezas diferentes |
| Repetições do mesmo ponto não medem deriva de posição | Limite do desenho; precisa de repetições com reposicionamento deliberado |

## Próximo passo sugerido (dentro da frente, sem decisão normativa)
Medir a **sensibilidade a reposicionamento** com dados que já existem: no Passat, as capturas `m_L`, `m_L-ctl1`, `m_L-ctl3` e `w_R`/retake permitem comparar "mesma posição" × "microfone refeito" por decisão (Q1–Q5) e dizer se a repetição adaptativa teria detectado a deriva. Exige clonar `ayukhno/autosound-measurements` (~0,5 GB) e conferir os SHA-256; não exige decisão.
