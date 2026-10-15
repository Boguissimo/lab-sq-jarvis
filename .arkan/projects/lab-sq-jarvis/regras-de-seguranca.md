# Regras de Segurança do Equipamento — Lab SQ Jarvis

> **Fonte canônica** dos identificadores `SEG-##` (constituição, P4 e P11).
> **Versão**: 0.1.0 | **Data**: 2026-10-15 | **Estado**: **proposta — aguardando ratificação (G3)**
> Estas regras são **critérios técnicos**: só mudam por decisão `JV-D` registrada (constituição, P8).

---

## 1. Conceitos

- **Recomendação sensível**: qualquer recomendação que altere, direta ou indiretamente, **potência**
  entregue, **excursão** do cone, **frequência de corte** ou **ganho** de um canal. Inclui reforço
  de EQ (ganho positivo em banda), mudança de passa-altas ou passa-baixas, mudança de ganho de canal
  ou de entrada, troca de inclinação de filtro e mudanças de nível do subwoofer.
- **Recomendação não sensível**: polaridade, atraso, corte de EQ (ganho negativo) e redução de
  ganho — ainda sujeitas ao procedimento seguro (SEG-08).
- **Dado confirmado**: especificação com fonte e estado `confirmado` (constituição, P5).
- **Não verificável**: a regra não pode ser avaliada por falta de dado confirmado. Resultado
  possível de qualquer regra; nunca equivale a “aprovada”.

## 2. Regras

| ID | Grandeza | Regra | Sem dado confirmado |
| --- | --- | --- | --- |
| SEG-01 | Frequência de corte | O passa-altas de cada alto-falante nunca fica abaixo da frequência mínima recomendada pelo fabricante, nem com inclinação menor que a recomendada. | Recomendação que **baixe** a frequência ou **suavize** a inclinação é **bloqueada**. |
| SEG-02 | Excursão | Toda recomendação que aumente conteúdo abaixo de 2 × Fs do alto-falante (baixar passa-altas, reforço de graves, aumento de ganho do subwoofer) exige verificação de excursão por cálculo determinístico com parâmetros Thiele-Small confirmados e potência no nível de teste. | **Bloqueada**. |
| SEG-03 | Potência | A potência elétrica estimada no canal, no nível de uso declarado, não ultrapassa a potência RMS confirmada do alto-falante, considerando o ganho total (entrada + EQ + canal). Quando a potência do amplificador no canal excede a RMS do alto-falante, todo aumento de ganho ou reforço exige essa verificação. | Aumento de ganho ou reforço é **bloqueado**; reduções seguem permitidas. |
| SEG-04 | Ganho — passo | Aumentos de ganho e reforços de EQ são feitos em passos de no máximo **+1,5 dB** por experimento. | — |
| SEG-05 | Ganho — reforço de EQ | Um filtro de EQ nunca reforça mais que **+3 dB**; a soma dos reforços que se sobrepõem numa banda de um canal nunca passa de **+6 dB**. Preferir corte a reforço. | — |
| SEG-06 | Ganho — cancelamento | Nunca recomendar reforço de EQ para preencher um vale classificado como cancelamento, interferência ou variação espacial (não equalizável). | — |
| SEG-07 | Margem digital | Toda recomendação de reforço informa o efeito sobre a margem até a saturação digital do DSP; recomendação que reduza a margem abaixo do critério vigente é bloqueada. | Marcada **não verificável**; exige aprovação de nível B com aviso explícito. |
| SEG-08 | Procedimento seguro | Antes de qualquer alteração de polaridade, crossover, atraso ou ganho: reduzir o volume; aplicar a alteração com o sinal parado; retomar o volume gradualmente até o nível de medição declarado. A receita de alteração sempre inclui esses passos. | — |
| SEG-09 | Nível de medição e audição | Toda receita declara o nível de medição; nunca recomendar nível acima do critério vigente de exposição sonora do usuário. | Usar o nível mais baixo que garanta a relação sinal-ruído mínima. |
| SEG-10 | Aprovação | Toda recomendação sensível exige aprovação de nível B (ato nomeado: o quê, em qual canal, quanto) antes de ser aplicada. | — |
| SEG-11 | Escrita no DSP | O Jarvis nunca escreve parâmetros no DSP; quem aplica é o desenvolvedor, no PC-Tool. | — |
| SEG-12 | Dados planejados | Equipamento `planejado` ou `informado` não alimenta nenhuma regra como se fosse instalado e confirmado. | Regra resulta **não verificável**. |

> Os valores numéricos de SEG-04 e SEG-05 (+1,5 dB, +3 dB, +6 dB) e o fator 2 × Fs de SEG-02 são
> **propostas conservadoras do agente, sem fonte normativa** — valores de partida para ratificação,
> não verdades técnicas. Os critérios de margem digital (SEG-07) e de exposição sonora (SEG-09)
> ainda **não têm valor**: serão propostos na spec da feature de experimentos, com fonte.

## 3. Como as regras são verificadas (G1)

- Cada regra tem testes com casos permitidos, limítrofes e proibidos.
- Testes de propriedade geram recomendações aleatórias e confirmam zero violações nas exibidas.
- Toda recomendação registra o resultado de cada regra aplicável: `aprovada`, `bloqueada` ou
  `não verificável`.

## Histórico

| Versão | Data | Descrição |
| --- | --- | --- |
| 0.1.0 | 2026-10-15 | Proposta inicial (pedido do desenvolvedor: regras explícitas para potência, excursão, frequência de corte e ganho) |
