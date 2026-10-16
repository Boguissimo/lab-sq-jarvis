# Esclarecimento metodológico — diagnóstico por previsão física (antes da rodada 2)

> Responde aos três pontos pedidos por Fabrício em 2026-10-16, **antes de executar a rodada 2**. Usa só arquivos já gravados da rodada 1 (`previsao-fisica-*.json`); nada novo foi calculado além de tabelas derivadas (`matriz_previsao.py`, `piso_construcao_previsao.py`). Não altera `src/`, spec, limiares nem arquitetura.

## Correção de uma formulação anterior
O resumo da rodada 1 dizia que o protótipo "acerta polaridade em todos os casos em que conclui". **Sem a cobertura isso induz a erro**: no carro N1 só 51 % dos casos concluem, e na sala as falhas de atraso pequeno são, em sua maioria, *não detectadas* (o protótipo respondeu "normal"). A matriz abaixo substitui essa formulação.

## 1. Matriz de resultados (rodada 1, banda operacional, margem 0,2)
`concluiu` = decisão ≠ `nao_conclui` (cobertura). `certas`/`erradas` valem só entre as que concluíram. Na classe *fora do espaço* (ganho +3 dB) a resposta certa é **não concluir**, por isso `não concluiu (corretas)`.

| Nível | Classe | n | concluiu | certas | erradas | não concluiu (corretas) | cobertura | certas entre as que concluíram |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| N0-sala | controle | 10 | 10 | 10 | 0 | 0 | 100 % | 100 % |
| N0-sala | polaridade | 10 | 10 | 10 | 0 | 0 | 100 % | 100 % |
| N0-sala | atraso (0,05/0,10/0,25/1,00 ms) | 40 | 40 | 22 | 18 | 0 | 100 % | **55 %** |
| N0-sala | fora do espaço | 10 | 0 | 0 | 0 | 10 (10) | 0 % | — |
| N1-sala | controle | 10 | 10 | 10 | 0 | 0 | 100 % | 100 % |
| N1-sala | polaridade | 10 | 10 | 10 | 0 | 0 | 100 % | 100 % |
| N1-sala | atraso | 40 | 40 | 23 | 17 | 0 | 100 % | **57 %** |
| N1-sala | fora do espaço | 10 | 0 | 0 | 0 | 10 (10) | 0 % | — |
| N0-carro | controle | 2 | 2 | 2 | 0 | 0 | 100 % | 100 % |
| N0-carro | polaridade | 2 | 2 | 2 | 0 | 0 | 100 % | 100 % |
| N0-carro | atraso | 8 | 8 | 8 | 0 | 0 | 100 % | 100 % |
| N0-carro | fora do espaço | 2 | 0 | 0 | 0 | 2 (2) | 0 % | — |
| N1-carro | controle | 5 | 3 | 3 | 0 | 2 (0) | **60 %** | 100 % |
| N1-carro | polaridade | 5 | 3 | 3 | 0 | 2 (0) | **60 %** | 100 % |
| N1-carro | atraso | 20 | 12 | 12 | 0 | 8 (0) | **60 %** | 100 % |
| N1-carro | fora do espaço | 5 | 0 | 0 | 0 | 5 (5) | 0 % | — |
| **Total** | todas | 189 | 150 | 115 | 35 | 39 (27) | 79 % | 77 % |

- **Sala, atraso por tamanho (N1):** 0,05 ms → 0/10 certas (todas "normal"); 0,10 ms → 4/10; 0,25 ms → 9/10 (1 com τ errado); 1,00 ms → 10/10. Os 35 erros da matriz são de **omissão** (atraso não acusado) ou τ estimado fora da tolerância; **nenhum controle foi acusado de falha** e **nenhuma falha fora do espaço recebeu hipótese**.
- **Carro N1:** as 5 variantes viram 3 conclusivas (P1 ×2, P3) e 2 abstenções (P2 ×2, tweeter 2–10 kHz, onde a deriva derruba o próprio controle). Os 12 + 3 + 3 "certos" vêm das mesmas 3 variantes; **n efetivo = 3 configurações**, não 15.
- **Carro N0 (n = 14):** é identidade algébrica (ver ponto 2), sem valor de diagnóstico.
- Arquivos: `previsao-fisica-matriz-banda_operacional.json` (com Wilson 95 %).

## 2. O que entra na previsão, o que entra na observação, o que foi alterado, e onde há concordância por construção
Notação: A, B = vias; H(·) = hipótese sobre B (normal, B → −B, B → B·e^{−j2πfτ}); F(·) = falha injetada.

**Sala (joeglondon), banda 30–150 Hz, lado ∈ {L, R}, repetição k:**
| | Arquivos |
| --- | --- |
| **Previsão** | A = `lado k`; B = `Sub Only k′` (N0: k′ = k; N1: k′ = k mod 5 + 1). Soma prevista = A + H(B) |
| **Observação** | hS = `lado + Sub k` (**soma física medida**) − `Sub Only k` + F(`Sub Only k`) |
| **Alterado artificialmente** | (i) subtração de `Sub Only k` da soma medida e reinserção transformada por F; (ii) reamostragem para 48 ppo (pontual) |
| **Como identifica a falha** | se `lado+Sub k ≈ lado k + Sub k` (verificado: 0,06–0,14 dB, 0,4–3,2°), então hS ≈ `lado k` + ε + F(Sub k). A hipótese certa deixa resíduo ≈ ε (e η = diferença entre repetições do Sub, em N1); as erradas deixam resíduo da ordem de \|B\|·\|1 − T\| (≈ 2B na polaridade) |
| **Dado compartilhado** | **N0: `Sub Only k` está dos dois lados** (em B da previsão e dentro da observação, subtraído e reinserido): a concordância é algébrica, limitada só por ε. **N1: o Sub vem de outra repetição**, mas `lado k` (previsão) e `lado + Sub k` (observação) são da **mesma época** (repetição k); não são disjuntos no tempo. |
| **Parte genuinamente física** | **somente o controle** (F = identidade): hS é o arquivo medido `lado + Sub k` sem alteração |

**Carro (Passat):**
| | N0 (P4: m_R+tw_R; P5: sw+w_L) | N1 (P1, P2, P3) |
| --- | --- | --- |
| Previsão | A e B das capturas únicas | A, B das capturas base |
| Observação | **A + F(B) computado dos mesmos arrays** | A + F(B), com uma das vias de **outra captura** (P1: B = `m_L-ctl1/3`; P2: A = `m_L-ctl1/3`; P3: A = `w_R-retake`) |
| Dado compartilhado | tudo: identidade algébrica | P1: A idêntico, B de outra captura (**a via que recebe a falha é disjunta**). **P2 e P3: a via que recebe a falha (tw_L, m_R) é o MESMO array na previsão e na observação**; só a outra via difere |
| Parte física | **nenhuma**: não existe soma medida no conjunto | **nenhuma** |

**Evidência numérica do piso por construção** (custo da hipótese **verdadeira**, rodada 1; `piso_construcao_previsao.py`):
| Nível | Par | Mediana | Máx | Leitura |
| --- | --- | ---: | ---: | --- |
| N0-carro | P4, P5 | **0,000** | 0,005 | a observação **é** a previsão (identidade) |
| N0-sala | L+Sub / R+Sub | 0,215 / 0,134 | 0,384 | piso = ε, discrepância física do modelo |
| N1-sala | L+Sub / R+Sub | 0,221 / 0,144 | 0,387 | igual a N0 → a variação entre repetições é desprezível na sala; o piso é ε |
| N1-carro | P1 | 0,131 | 0,190 | discrepância entre capturas da via faltosa |
| N1-carro | P3 | 0,491 | 0,569 | deriva/torso |
| N1-carro | P2 | **1,592** | 1,815 | acima de C_ADM = 1,0 → o protótipo se abstém |

**Conclusão do ponto 2:** *há* concordância por construção, e ela é **total em N0**, **parcial em N1** (carro P2/P3: a via faltosa é o mesmo array; sala: mesma época) e **ausente apenas no controle da sala**. A rodada 1 prova identificabilidade e abstenção sob discrepância; **não** prova diagnóstico. A rodada 2 corrige o que for corrigível: via faltosa sempre de aquisição disjunta (e, na sala, previsão e observação em repetições disjuntas para **todas** as vias); o que não for corrigível (carro sem soma física; só m_L e w_R têm capturas repetidas) fica **declarado como limite**.

## 3. Componentes da margem: o que é e o que não é estimável
A margem decide entre "normal" e "falha" comparando `custo(normal) − min(custo(inversão), custo(atraso*))` (a "folga") com um limiar m. Para o limiar derivar de incerteza, é preciso separar:
| Componente | Definição | Sala (30–150 Hz) | Carro (por par/banda) |
| --- | --- | --- | --- |
| **(a) Variabilidade entre aquisições** | custo entre somas previstas de repetições diferentes (`lado k + Sub k` × `lado k′ + Sub k′`) | **Estimável** (5 repetições; 20 pares ordenados por lado) | **Estimável com fraqueza**: `m_L` 3 capturas (6 pares ordenados), `w_R` 2 (2 pares); demais vias sem repetição |
| **(b) Erro de referência temporal** | desvio de τ* (melhor atraso) nos controles; deriva do tempo de chegada | **Parcial**: só a estabilidade **relativa** entre arquivos (dispersão de τ* nos controles); não há `id` de referência/loopback, então o erro **absoluto** de referência **não é estimável** | **Estimável em parte**: deriva medida pelo autor (0 / −0,291 / −0,636 amostra) → efeito de fase 360·f·Δt calculado; jitter do loopback **não estimável** |
| **(c) Discrepância do modelo** (linearidade, acoplamento, interação ao tocar juntas) | custo entre a soma prevista e a soma **medida** da mesma repetição (`lado k + Sub k` × `lado + Sub k`) | **Estimável só em 30–150 Hz e só nesta sala**; inclui qualquer deslocamento de tempo entre arquivos da mesma repetição (não separável de (b) intra-repetição) | **NÃO estimável**: não há soma medida no conjunto. A margem do carro seria, no máximo, um **limite inferior** |
| **(d) Incerteza efetiva da decisão** | distribuição empírica da folga em controles com previsão e observação disjuntas | **Estimável empiricamente** (40 controles = 2 lados × 20 pares), sem garantia de cobertura probabilística: uma sala, uma sessão, lados L e R dependentes (mesmo Sub, mesma época) | **NÃO estimável com confiança**: n ≤ 8 pares e sem (c) |
**Consequência (declarada antes de executar):** a rodada 2 **deriva margens apenas para a sala**, por calibração cruzada (margem do lado L avalia o lado R, e vice-versa; nenhum caso é julgado por margem calculada com ele). Para o **carro, nenhuma margem derivada é emitida**: ele entra só como teste de estresse com a margem fixa de referência e as abstenções, e **a viabilidade no carro fica explicitamente "não demonstrada"**.
**Admissibilidade (nova condição):** o par só é analisado se (i) a banda declarada for a **interseção das bandas operacionais das duas vias**, (ii) tiver ≥ 1 oitava e ≥ 20 pontos válidos na máscara, e (iii) a previsão reproduzir o controle (custo ≤ C_ADM). **Fora disso o resultado é `inadmissivel`/`nao_conclui`; nada é generalizado fora da banda.**
