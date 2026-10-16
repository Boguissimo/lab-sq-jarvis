# Previsão física — rodada 2: margens derivadas da incerteza, aquisições disjuntas e portão de admissibilidade

> **Nota de redação (2026-10-16):** onde estes relatórios falam em *deriva*, trata-se de **deriva observada de origem ainda não identificada**. A atribuição à temperatura vem do autor da fonte (Passat), não de medição nossa; o estudo de causa (se houver) depende de registros ainda inexistentes (ver `protocolo-campo-n2-focus.md`, teste de repouso).

> **Exploração no harness; protótipo, não o Jarvis.** Não altera `src/`, spec, limiares nem algoritmos; não valida o V02; **sem N2**. 2026-10-16.
> Pré-registro: `preregistro-previsao-fisica-r2.json` (SHA-256 `817af766…dd4`, commit `c0bca8f`), antes de gerar casos. Margens estimadas **antes** de qualquer avaliação diagnóstica (`previsao-fisica-r2-margens.json`, commit `20d031a`). Execução cega com rótulos fora do alcance; `previsoes` SHA-256 `3ff1514f…4a08`. Código: `gerar_casos_previsao2.py`, `estimar_margem_previsao.py`, `diagnostico_previsao2.py`, `avaliar_previsao2.py`. Números: `previsao-fisica-r2-*.json`.
> Premissas lidas em `esclarecimento-metodologico-previsao-fisica.md` (matriz da rodada 1, dados compartilhados, estimabilidade das componentes).

## 1. Componentes da margem (estimadas antes de avaliar; custo = mediana|dB| + mediana|fase|/10)
| Componente | Sala L (30–150 Hz) | Sala R | Carro |
| --- | --- | --- | --- |
| (a) variabilidade entre aquisições, P95 | 0,158 (20 pares) | 0,167 | C1 máx 0,229 (6 pares); C2 máx 2,197 (6); C3 0,465 (2) |
| (b) referência temporal | dispersão **relativa** de τ\* nos controles: −0,02…+0,12 ms; erro **absoluto não estimável** (sem id/loopback) | −0,02…+0,01 ms | efeito da deriva **conhecida** (manifesto): C1 máx 0,175; C2 máx **1,053** (≈ metade da variabilidade observada em C2) |
| (c) discrepância do modelo, P95 | 0,331 | 0,154 | **não estimável** (sem soma medida) |
| (d) folga efetiva em controles disjuntos, P95 | 0,103 (20) | **0,0056** (20) | **não estimável** (n ≤ 6 e sem c) |
| margem por componentes `M_C` = √(a² + c²) | 0,367 | 0,227 | **não emitida** |
| margem empírica `M_B` = P95 de (d) | 0,103 | 0,0056 | **não emitida** |
**Duas leituras que o pré-registro obrigava a declarar:** (1) **a discrepância do modelo (c) é diferente entre L e R** (0,331 × 0,154) mesmo no mesmo ambiente; (2) **nada de margem para o carro**: faltam (c) e (d).

## 2. Resultados — sala (banda 30–150 Hz), aquisições disjuntas (N1s), 280 casos; margem do lado **oposto**
Cobertura de conclusões das falhas dentro do espaço: 100 % (o protótipo nunca se absteve nelas); fora do espaço: 0 % de conclusões (correto).
| Falha (n = 40) | M_A (0,2) certas/omissão/ident. | M_B (empírica) | M_C (componentes) |
| --- | --- | --- | --- |
| Controle (→ normal) | 40 / 0 / **0 falso alarme** | 32 / 0 / **8 falsos alarmes** | 40 / 0 / 0 |
| Polaridade | 40 / 0 / 0 | 40 / 0 / 0 | 40 / 0 / 0 |
| Atraso 0,05 ms | 0 / 40 / 0 | 16 / 20 / 4 | 0 / 40 / 0 |
| Atraso 0,10 ms | 5 / 31 / 4 | 36 / 0 / 4 | 0 / 36 / 4 |
| Atraso 0,25 ms | 36 / 0 / 4 | 36 / 0 / 4 | 36 / 0 / 4 |
| Atraso 1,00 ms | 40 / 0 / 0 | 40 / 0 / 0 | 40 / 0 / 0 |
| Fora do espaço (ganho +3 dB → não concluir) | 40 / 40 abstenções | 40 | 40 |
- **Detecção × identificação:** com 0,25 ms o atraso foi **acusado em 40/40**; em 4 casos o τ estimado ficou fora da tolerância (|τ̂ − τ| > máx(0,05; 20 %)): erro de identificação, não de detecção.
- **Critério fixado (≤ 2/40 falsos alarmes; polaridade ≥ 36/40; fora do espaço ≥ 36/40):** `M_A` **aceitável**, `M_C` **aceitável**, `M_B` **não aceitável** (8/40 falsos alarmes). Menor atraso com ≥ 90 % de acertos: **0,25 ms** para as duas aceitáveis.
- **Por que `M_B` falhou:** o lado L usou a margem estimada em R (0,0056) e acusou falha em 8 dos 20 controles; o lado R, com a margem de L (0,103), teve 0/20 falsos alarmes e detectou **0,10 ms em 20/20**. A margem empírica **não se transfere entre lados**, porque a discrepância do modelo difere (item 1). Observação *post hoc*, não pré-registrada: **a margem útil parece ser a do próprio sistema** (medida num controle dele), não uma constante nem uma margem emprestada.
- **Margem derivada de componentes não superou a constante 0,2** (mesmo limite de detecção, 0,25 ms): nesta sala, derivar a margem de incerteza não "comprou" sensibilidade; comprou **justificativa** e mostrou que a constante estava dentro da faixa plausível (0,23–0,37).
- N0 (mesma repetição) deu números praticamente idênticos aos de N1s (piso: custo da hipótese verdadeira 0,13–0,22 nos dois): a variação entre repetições é desprezível na sala; o piso é a discrepância do modelo (c).

## 3. Resultados — carro (sem margem derivada; só `M_A` = 0,2 como teste de estresse)
| Nível | Casos | Concluiu | Certas | Erradas | Não concluiu | Observação |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| N0 (mesma captura) | 70 | 60 | 60 | 0 | 10 (todas fora do espaço, corretas) | piso da hipótese verdadeira ≈ **0,000**: identidade algébrica, sem valor de diagnóstico |
| N1s (captura disjunta da via faltosa) | 98 | 48 | 48 | 0 | 50 (14 fora do espaço, corretas; **36 dentro do espaço**) | C1 (200–500 Hz) e C3 (200–500 Hz): 100 % concluíram e acertaram, **inclusive 0,05 ms**; **C2 (2–10 kHz): 0 % de cobertura** |
- **n efetivo no carro N1s = 8 variantes conclusivas** (C1 ×6, C3 ×2) de **3 pares**; o piso do C2 (mediana 1,74) excede `C_ADM` = 1,0 e o protótipo se abstém em todas (a deriva observada de origem ainda não identificada derruba até o controle).
- O carro continua com **A compartilhado, soma computada e nenhuma soma física**: 100 % em C1/C3 é **identificabilidade sob variação de captura**, não diagnóstico. Em 200–500 Hz o atraso de 0,05 ms é detectável porque 0,05 ms vale ≈ 6° a 350 Hz, acima do piso (0,13–0,40).

## 4. Portão de admissibilidade
- Os 80 controles com banda declarada fora da interseção das bandas operacionais (200–10000 Hz e 20–20000 Hz) foram **80/80 `inadmissivel`**, sem diagnóstico.
- **Custo de ignorar o portão** (rotulado, não é diagnóstico): com o portão desligado, os mesmos controles seriam acusados de falha em **3/80** (`M_A`, `M_C`) e **19/80** (`M_B`), e 4/80 cairiam em "não concluir". Um resultado válido em 30–150 Hz **não** vale fora da banda; o portão por banda é condição de uso, não detalhe.

## 5. Limitações desta rodada
Uma sala (L e R não são independentes: mesmo Sub, mesma época), um carro, uma sessão cada; falhas injetadas e ideais; soma do carro computada; `A` compartilhado no carro; n efetivo pequeno (Wilson no JSON); calibração cruzada entre lados é mais fraca que entre sessões; `C_ADM` fixo em 1,0 (não derivado); erro absoluto de referência temporal não estimável na sala; **nenhum N2**.

## 6. Conclusão objetiva: viabilidade do método e o que falta
**Veredito:** o método é **viável como direção de evolução (V04) para polaridade e atraso em banda baixa/média de um par admissível, com abstenção**; **ainda não é utilizável com confiança**, porque nada foi demonstrado fora de falhas injetadas.
| Tema | O que os dados sustentam | O que não sustentam |
| --- | --- | --- |
| Polaridade | identificada em 40/40 casos disjuntos da sala (soma física), 0 falso alarme, também com margens diferentes | defeito real; outro sistema; carro com soma física |
| Atraso | **detectado** (acusado) em 40/40 com 0,25 ms na sala; τ dentro da tolerância em 36/40; em 200–500 Hz do carro, 0,05 ms detectável (soma computada) | atrasos < 0,25 ms na sala dependem da margem e do sistema; ruído/deriva reais de campo |
| Alta frequência no carro (2–10 kHz) | o método **se abstém** (custo do controle 1,7 > 1,0): comportamento seguro | utilidade: com capturas separadas por minutos a deriva observada de origem ainda não identificada inviabiliza a previsão |
| Margem | `0,2` constante e `√(a²+c²)` por componentes deram o mesmo desempenho na sala; margem empírica emprestada de outro lado **falhou** (8/40 falsos alarmes) | margem para o carro (faltam (c), (d)); transferência entre sistemas |
| Portão por banda | 80/80 casos fora da banda barrados; ignorá-lo geraria até 19/80 falsos alarmes | — |
**O que ainda falta para usar com confiança (em ordem de ganho):**
1. **N2:** defeito físico aplicado no DSP com soma **medida** antes/depois (protocolo preparado, não iniciado).
2. **Soma física medida em carro** para estimar a discrepância do modelo (c) e permitir margem do carro.
3. **Margem do próprio sistema:** a evidência *post hoc* sugere margem derivada do controle (baseline) medido no mesmo par; exige **nova rodada pré-registrada** e deve ser validada no N2. Nada foi ajustado nesta rodada.
4. **Um segundo sistema** (outra sala/outro carro) para testar transferência; hoje L e R compartilham sala, Sub e época.
5. **Referência temporal absoluta** no fluxo (id/loopback): na sala o erro absoluto não é estimável.
6. **Banda operacional por par declarada e confirmada** (cadastro): é dado de entrada obrigatório do portão.
7. **Alta frequência:** capturas próximas no tempo ou abstenção declarada.
8. Nada disso entra no produto sem decisão normativa (limiares são P8; SEG continua valendo; o método não recomenda alteração).

## 7. Decisões de engenharia para Fabrício
1. **Autorizar (ou não) o N2 no Focus** com o protocolo `protocolo-campo-n2-focus.md`; confirmar o equipamento real (JV-D012 exige confirmação antes de qualquer análise).
2. **Autorizar a rodada 3 (pré-registrada)** de margem derivada do controle do próprio sistema, em dados já existentes; ou aguardar o N2 para calibrá-la com dado físico.
3. Manter `C_ADM` e a margem como **parâmetros do harness**; a promoção a limiares do produto é decisão P8 futura.
