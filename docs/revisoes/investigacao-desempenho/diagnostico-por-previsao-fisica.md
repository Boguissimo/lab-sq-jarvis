# Diagnóstico por previsão física (soma prevista × soma observada) — resultados

> **Exploração com falhas injetadas; protótipo do experimento, não o Jarvis.** Não altera `src/`, spec, limiares nem algoritmos; não valida o V02 acusticamente; **não alcança diagnóstico independente (N2)**. 2026-10-16.
> Fontes: `joeglondon/speakers-2026-filters` @ `799af51` (sem licença; só números derivados) e `ayukhno/autosound-measurements` @ `7725d42` (CC BY 4.0); SHA-256 conferidos antes de gerar os casos.
> Pré-registro: `preregistro-previsao-fisica.json` (SHA-256 `5eab623c…32d4`, commit `24683b8`), commitado **antes** de gerar casos ou rodar o diagnóstico. Código: `gerar_casos_previsao.py` → `diagnostico_previsao.py` → `avaliar_previsao.py` (commit `fb351b8` antes da execução). Números: `previsao-fisica-previsoes.json` (SHA-256 `8fec50f8…27b3`), `previsao-fisica-avaliacao.json`, `previsao-fisica-rotulos.json`, `previsao-fisica-manifesto-casos.json`.
> Baseline que **não** foi refeito: a Regra 2 do produto (assinatura de fase constante) acertou 0/80 falhas injetadas no Passat (`resultados-passat-ayukhno.md`).

## 1. O que cada nível prova (e o que não prova)
| Nível | Definição neste experimento | O que prova | O que NÃO prova |
| --- | --- | --- | --- |
| **N0 — consistência matemática** | previsão e "soma observada" vêm das mesmas capturas; falha injetada por código | a hipótese é **identificável** (teto ideal) | nada sobre diagnóstico real |
| **N1 — robustez à variação de captura** | a previsão usa outra repetição/captura; na sala a soma observada contém a **soma física medida** (lado + Sub), com a falha só na parcela do Sub; no carro a soma segue computada | resiste a ruído e deriva reais entre capturas | diagnóstico independente: a falha continua **injetada** por código, ideal (−1 exato, atraso exato) |
| **N2 — diagnóstico independente** | defeito **real** documentado, antes/depois, parecer externo | — | **não existe em nenhum conjunto; não é alegado** |
Os **controles** da sala (somas físicas sem alteração) já eram evidência independente de que a previsão descreve a física em 30–150 Hz (`resultados-braco-a-joeglondon.md`); aqui só funcionam como controles.

## 2. Método (fixado antes)
Protótipo com 3 hipóteses sobre a via B: **normal** (hA + hB), **polaridade invertida** (hA − hB) e **atraso** τ ∈ ±3 ms (melhor ajuste). Custo = mediana |erro de nível dB| + mediana |erro de fase|/10, na **banda operacional do par** (interseção das bandas úteis), máscara −30 dB. Decisão: `nao_conclui` se o melhor custo > 1,0 (o mesmo limite de mediana da admissibilidade já pré-registrada); `normal` se o custo da normal não supera o melhor alternativo em ≥ 0,2; senão, a de menor custo. Falhas: controle, polaridade, atrasos 0,05/0,10/0,25/1,00 ms e **ganho +3 dB (fora do espaço de hipóteses, para medir falsa confiança)**. 189 casos: sala 140 (N1 70 + N0 70), carro 49.
**Cegamento (estrutural, não epistêmico):** o protótipo só lê `f, hA, hB, hS` e a banda; ids embaralhados (semente 20261016); os rótulos estavam **fora do alcance** (diretório movido) durante a execução; a assinatura é `diagnosticar(f, hA, hB, hS, banda_hz, margem)`; o código não contém referências a rótulo ou falha. Quem escreveu o gerador (Claude) conhece o desenho dos casos; o que se garante é que o algoritmo não recebe a resposta e que `C_ADM` e `MARGEM` foram fixados antes de qualquer execução.

## 3. Resultados (banda operacional; acerto / abstenção / erro)
| Falha | Sala N1 (n=10) | Sala N0 (n=10) | Carro N1 (n=5) | Carro N0 (n=2) |
| --- | --- | --- | --- | --- |
| Controle (→ normal) | 10 / 0 / 0 | 10 / 0 / 0 | 3 / 2 / 0 | 2 / 0 / 0 |
| **Polaridade** (→ inversão) | **10 / 0 / 0** | 10 / 0 / 0 | 3 / 2 / 0 | 2 / 0 / 0 |
| Atraso 0,05 ms | 0 / 0 / 10 | 0 / 0 / 10 | 3 / 2 / 0 | 2 / 0 / 0 |
| Atraso 0,10 ms | 4 / 0 / 6 | 3 / 0 / 7 | 3 / 2 / 0 | 2 / 0 / 0 |
| Atraso 0,25 ms | 9 / 0 / 1 | 9 / 0 / 1 | 3 / 2 / 0 | 2 / 0 / 0 |
| Atraso 1,00 ms | 10 / 0 / 0 | 10 / 0 / 0 | 3 / 2 / 0 | 2 / 0 / 0 |
| Ganho +3 dB (fora do espaço → nao_conclui) | 10 / 0 / 0 | 10 / 0 / 0 | 5 / 0 / 0 | 2 / 0 / 0 |
**Falsa confiança (banda operacional): 0.** Nenhum controle foi acusado de falha e nenhuma falha fora do espaço recebeu hipótese.
Contraste com o baseline: a Regra 2 do produto acertou **0 de 20** polaridades invertidas (e 0 de 60 atrasos) no Passat; o protótipo conclui polaridade corretamente em todos os casos em que conclui, nos dois conjuntos.

### Leitura honesta
1. **Polaridade e atrasos ≥ 0,25 ms são identificáveis** com a banda operacional do par, nos dois conjuntos. N0 ≈ N1 na sala: a repetibilidade da sala é tão alta que a variação de captura quase não pesa; **boa parte do resultado da sala é consistência matemática**, e deve ser lida assim.
2. **O limite de detecção de atraso é imposto pela MARGEM, não pelo dado.** Na sala, 0,05 ms não é detectado (0/10) e 0,10 ms é detectado em 4/10; a incerteza de fase da sala (≈ 0,3–0,6°) permitiria resolver ~0,02–0,05 ms. Sensibilidade (post hoc, rotulada): acertos de tipo da decisão em 162 casos (falhas dentro do espaço + controles) — MARGEM 0,1: 130; 0,2: 120; 0,5: 104; 1,0: 87. **Nada foi escolhido com base nisso.**
3. **No carro, a previsão é pouco confiável em alta frequência e o protótipo abstém-se (certo).** Em P2 (médio + tweeter, 2–10 kHz) a soma formada com capturas derivadas (`m_L-ctl1/ctl3`) já dá custo 1,46 no **controle** (> 1,0): a deriva de 0,3–0,6 amostra (≈ 12° a 5 kHz) invalida a previsão, e o protótipo responde `nao_conclui` em vez de errar. É o comportamento seguro, mas significa **sem diagnóstico** onde a deriva domina.
4. **A banda operacional é essencial.** Ablação (pré-registrada), banda cheia 20 Hz–20 kHz: 2 controles acusados de falha (falsa confiança 2), mais abstenções no carro (3 de 5 em vez de 2), embora ajude a detectar 0,10 ms na sala (9/10). Banda por via **como dado declarado** muda o resultado — sustenta a diretriz de faixa operacional por via do mapa técnico.

## 4. Limitações
Uma sala, um carro, uma sessão cada; falhas injetadas e ideais; somas do carro computadas; sala com soma física mas falha injetada na parcela do Sub; n por célula 2–10 (intervalos de Wilson amplos, no JSON); o protótipo sabe quais são as vias A/B e a banda do par (premissas de entrada); não usa `referencia/modelo.py` (prevê a soma a partir das vias **medidas**, não de um modelo de alto-falante + DSP); nenhuma parte foi integrada ao produto.

## 5. Decisões de engenharia (para Fabrício; nada implementado)
1. **Direção de diagnóstico:** a evidência favorece substituir/complementar a "assinatura de fase constante" por **comparação soma observada × soma prevista com hipóteses físicas e abstenção**, condicionada a (a) vias medidas isoladamente + em conjunto, (b) **banda operacional por par declarada**. Isto reforça as decisões 1 e 2 do mapa técnico (faixa operacional por via; previsão). Decidir se entra como direção do V04. **Sem alteração do V02.**
2. **Limiar de decisão (P8):** `C_ADM` e `MARGEM` determinam o que se detecta. Proposta: derivar a margem da **incerteza medida por repetição** (custo de controle entre capturas), em vez de constante; exige nova rodada pré-registrada. Escolha do valor é sua.
3. **Abstenção por deriva:** onde a previsão não reproduz nem o controle (custo de controle > C_ADM), o produto deve declarar "sem previsão confiável" — não forçar hipótese. Em HF de carro isso será frequente (deriva de temperatura); mitigação possível: capturas próximas no tempo, referência temporal por loopback.
4. **Único passo que fecha a validação (N2):** um caso **real** com defeito físico documentado. Proposta de baixo custo no Focus: medir vias isoladas e em conjunto com a polaridade correta, depois **inverter a polaridade no DSP** (falha real, não computada) e medir a soma de novo; repetir com um atraso conhecido no DSP. Pede sessão de campo; é decisão de prioridade sua.
5. Sem mudança de algoritmo, limiar, spec ou `src/`; `Regra 2` permanece como está.
