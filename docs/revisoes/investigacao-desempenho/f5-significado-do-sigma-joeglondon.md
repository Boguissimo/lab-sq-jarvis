# F-5 — O que o σ̂ mede em medições acústicas reais (investigação prioritária)

> **Exploração com medições reais (uma sala doméstica, um conjunto, 5 repetições).** Não altera o estimador nem os limiares; produz alternativas para decisão humana. Não valida nem reprova o V02. 2026-10-16. Fonte: `joeglondon/speakers-2026-filters` @ `799af51` (hashes conferidos). Código: `ferramentas/investigacao/{sigma_f5,compat_hf,repetibilidade_sigma}.py`; números: `sigma-f5-joeglondon.json`, `compat-hf-joeglondon.json`.

## 1. O que cada estatística mede (exatamente)
| | σ̂ do produto (`calculos.irregularidade`) | Desvio entre repetições |
| --- | --- | --- |
| Fórmula | 1,4826 · MAD(Δ²L) / √6, com Δ² = segunda diferença do **nível em dB entre pontos vizinhos da grade** | desvio-padrão (n−1) das 5 repetições **no mesmo ponto de frequência**, depois mediana na faixa |
| Faixa | 200 Hz a 10 kHz | 200 Hz a 10 kHz |
| Grade | exige grade logarítmica uniforme, ≥ 24 pontos/oitava, sem suavização; **o resultado depende do espaçamento** | independe da grade (usa o mesmo ponto em cada repetição) |
| Agregação | **mediana robusta** sobre toda a curva (uma só aquisição) | mediana sobre a faixa de um desvio por frequência (5 aquisições) |
| Mede | rugosidade **ponto a ponto na escala da grade**; igual a σ do ruído se este for branco e a curva for lisa | variabilidade do **processo de aquisição** naquela frequência; ignora qualquer estrutura que se repita |
| Não são equivalentes | uma estrutura estável e fina (comb, modos, interferência) entra em σ̂ **e não** no desvio | ruído e deriva entram nos dois |

## 2. As cinco repetições são comparáveis? (verificado antes de decompor)
- **Nível:** deslocamento médio de cada repetição em relação à média, 200 Hz–10 kHz: |≤ 0,12 dB| em L, R e somas; até 0,39 dB no Sub.
- **Estrutura da variabilidade:** desvio entre repetições pequeno em todas as bandas de oitava (L: 0,06–0,34 dB; R: 0,19–0,32 dB). Com o microfone fora de lugar, a estrutura fina acima de 2 kHz variaria vários dB; **não varia**, o que sugere microfone fixo entre as repetições de uma mesma configuração (inferência, não documentada pelo autor).
- **Posição e tempo entre medições diferentes (teste físico em alta frequência):** acima de 2 kHz o Sub não contribui; `(L|R)+Sub k` deveria igualar `(L|R) k`. Resultado: erro mediano de **0,4–0,8 dB e 2–10°**, quase constante em 2–10 kHz (não cresce com a frequência, então não é atraso/posição). **Exceção: L-3**, com 31–150° e cabeçalho que declara outro atraso (−0,1236 ms, contra ≈ −0,049 ms nas demais) e "Clock adjustment: −85,8 ppm" para `L + Sub 3`: **a hipótese de referência temporal compatível do braço B é contrariada por evidência dos arquivos nesse par**; no LF o efeito é pequeno (≈ 3°), por isso passou na admissibilidade de 30–150 Hz. R-1 mostra 5–10° crescentes com a frequência (≈ 3 µs, cerca de 1 mm de caminho).
- **Conclusão:** nível, e na prática posição, são compatíveis entre as repetições (9 dos 10 pares também na referência temporal em alta frequência); L-3 fica ressalvado.

## 3. Componente estável × variabilidade entre aquisições (σ̂ do produto, 48 pontos/oitava, método pontual)
Para cada curva: x_k = repetição k; m = média das 5; r_k = (x_k − média das outras 4)/√1,25 (variabilidade entre aquisições, escalonada para ter a escala do ruído por aquisição).

| Curva | σ̂ de x_k (5 repetições) | σ̂ de m (estável) | σ̂ do resíduo r_k | desvio entre rep. | autocorrelação lag-1 do resíduo |
| --- | --- | --- | --- | --- | --- |
| L | 3,52–3,57 | **3,50** | 0,12–0,18 | 0,12 | −0,19…0,06 |
| R | 2,58–2,77 | **2,70** | 0,27–0,47 | 0,24 | ≈ 0 |
| Sub Only | 3,94–4,64 | 3,54 | 0,65–0,78 | 0,66 | −0,09…0,23 |
| L + Sub | 3,00–3,53 | **3,20** | 0,26–0,53 | 0,37 | ≈ 0 |
| R + Sub | 2,39–2,50 | **2,47** | 0,08–0,11 | 0,10 | ≈ 0 |

- **O σ̂ de uma aquisição é praticamente igual ao σ̂ da média das cinco:** o valor vem da estrutura **estável**, não da variabilidade.
- **Aplicado só à variabilidade, o estimador funciona:** σ̂ do resíduo (0,1–0,8 dB) concorda com o desvio entre repetições (0,1–0,7 dB) e o resíduo é aproximadamente branco (lag-1 ≈ 0). Ou seja, a matemática do σ̂ está correta **quando a curva é lisa**; o que falha é a premissa "curva lisa + ruído branco".
- **Piso de estrutura (ruído branco de σ conhecido somado à média estável):** σ̂ de L passa de 3,50 para 3,50 / 3,60 / 3,50 / 3,82 / 4,09 dB com σ = 0,25 / 0,5 / 1,0 / 1,5 / 2,0 dB. **Com essa estrutura, ruído de até ~1 dB é invisível para o σ̂**: o estimador só reage quando o ruído se aproxima da própria estrutura. Em outras palavras, σ̂² ≈ estrutura² + ruído², e numa única aquisição não dá para separar os dois.

## 4. Sensibilidade à grade e à interpolação
Mediana de 5 repetições de L (R é semelhante). Em 24,0 ppo exatos o produto devolve "densidade insuficiente" (comparação em ponto flutuante com o mínimo 24: 23,9999…); nessa coluna foi usada a **réplica da fórmula**.

| Grade | σ̂ de x | σ̂ de m | σ̂ do resíduo | desvio entre rep. |
| --- | --- | --- | --- | --- |
| 24 ppo pontual | 3,76 | 3,81 | 0,18 | 0,12 |
| 48 ppo pontual | 3,55 | 3,50 | 0,15 | 0,12 |
| 96 ppo pontual | 2,30 | 2,34 | 0,15 | 0,12 |
| 192 ppo pontual | 1,56 | 1,56 | 0,12 | 0,12 |
| 48 ppo janela | 1,96 | 1,95 | 0,05 | 0,05 |
| 192 ppo janela | 1,08 | 1,07 | 0,08 | 0,09 |
| **nativa linear (0,37 Hz; réplica)** | **0,03** | 0,03 | 0,01 | 0,18 |

- σ̂ da mesma medição vai de **0,03 dB (grade nativa) a 3,8 dB (24 ppo)**; o desvio entre repetições fica em 0,12 dB em todas as grades pontuais. σ̂ é função do **espaçamento da grade**, não só da qualidade da medição.
- **Na grade nativa o estimador também falha, no sentido oposto:** o resíduo dá 0,01 dB contra 0,18 dB de desvio, porque pontos vizinhos a 0,37 Hz são correlacionados (o ruído não é independente entre pontos). Só numa faixa intermediária (≈ 48 ppo pontual) o σ̂ do resíduo acompanha o desvio.
- O produto já barra a grade linear (σ̂ "não estimável"), o que é coerente com esse achado.

## 5. O portão rejeita medições repetíveis por estrutura acústica legítima?
Sim, **nesta amostra**: das 25 aquisições (5 curvas × 5 repetições) em 48 ppo pontual sem suavização, **25 ficam "reprovada"** (σ̂ > 1,5 dB). Se o critério medisse só a variabilidade entre aquisições (mesmos limiares, ilustração), **19 seriam "aprovada" e 6 "aviso"**, nenhuma "reprovada" (os avisos são o Sub e L+Sub). O texto exibido ao usuário nesse caso é "com este ruído, a medição não permite concluir": **atribui a estrutura acústica ao ruído**.
A leitura segura que o σ̂ permite é um **limite superior do ruído** (σ̂ ≤ x ⇒ ruído ≤ x): "aprovada" é confiável; "reprovada" **não** prova ruído alto.

## 6. Limitações (obrigatórias)
Uma sala doméstica com caixas de dois canais e subwoofer, um microfone, uma sessão de 18/04/2026, 5 repetições, posição não documentada pelo autor, sweep único de 128 k; a variabilidade entre repetições inclui qualquer deriva real e **não captura erros sistemáticos** (ruído correlacionado entre repetições, calibração, posição fixa porém errada); a estrutura fina de uma sala doméstica não representa um carro (que pode ter menos ou mais estrutura); o σ̂ foi validado no domínio simulado (ruído branco + vales), onde sua premissa vale; ruído **não branco** ou ambiental não foi testado aqui.

## 7. Alternativas fundamentadas (para decisão humana; nada implementado)
| Alt. | Descrição | A favor (evidência daqui) | Contra / depende de |
| --- | --- | --- | --- |
| 1 | **Reinterpretar a classe "reprovada"** como "ruído não distinguível da estrutura" (equivalente a "não estimável", INV-212), mantendo "aprovada" e "aviso" como limites superiores do ruído | muda pouco; evita rejeitar medições boas; a mensagem passa a ser verdadeira | afeta o N2 e o SC-208 (spec); com uma só aquisição, ruído alto fica "não estimável" em vez de "não dá para concluir" |
| 2 | **Estimar ruído por repetição** (≥ 2 aquisições do mesmo arranjo; resíduo entre aquisições com os mesmos limiares) | mede o que a spec diz medir; independe da grade (desvio 0,12 em todas); concorda com σ̂ do resíduo; reaproveita o conceito de repetição da E4 | exige mais medições do usuário; inclui deriva de posição; muda spec/UX |
| 3 | Remover a estrutura por filtragem antes do Δ² | — | **não resolve**: numa só aquisição ruído e estrutura fina não são separáveis (σ=1 dB passa despercebido) |
| 4 | **Declarar a escala espectral** do σ̂ (ex.: exigir 48 ppo) e orientar a exportação | σ̂ varia 3,8→1,6 dB de 24 a 192 ppo; hoje o aviso é só "não estimável" | não corrige a mistura estrutura × ruído; limiares passam a ser por escala |
| 5 | **Manter e documentar** o limite (domínio simulado) com aviso ao usuário de que "reprovada" pode ser estrutura | nenhuma mudança de produto | rejeita 25/25 aquisições desta sala; a mensagem continua errada |

Tendência sugerida pelas evidências (decisão sua): combinar **1** (honestidade da mensagem, mudança pequena) com **2** como evolução (ruído medido por repetição); descartar 3. Antes de qualquer mudança, convém um **segundo conjunto** de preferência em carro, com repetições, e um caso com ruído real conhecido (para checar que o estimador ainda barra ruído de verdade).

## 8. Achado paralelo
**F-10 (baixa gravidade):** em exatamente 24,0 pontos/oitava a verificação de densidade mínima falha por arredondamento de ponto flutuante (23,9999…), embora a regra diga "mínimo 24". Depende do arredondamento do arquivo (ocorreu em memória, não nos arquivos gravados).
