# Regras de Segurança do Equipamento — Lab SQ Jarvis

> **Fonte canônica** dos identificadores `SEG-##` (constituição, P4 e P11).
> **Versão**: 0.2.0 | **Data**: 2026-10-15 (revisão 2) | **Estado**: **proposta — aguardando ratificação (G3)**
> Estas regras são **critérios técnicos**: só mudam por decisão `JV-D` registrada (constituição, P8).
> Siglas: **SEG** — regra de segurança deste projeto; **EQ** — equalização; **DSP** — processador
> digital de sinais; **Fs** — frequência de ressonância do alto-falante; **Xmax** — excursão linear
> máxima do cone; **RMS** — potência média contínua declarada pelo fabricante; **T/S** — parâmetros
> Thiele-Small do alto-falante.

---

## 0. Alcance e limites (JV-D022)

Estas regras **reduzem o risco** de dano ao equipamento **dentro das condições conhecidas e dos dados
cadastrados**. Elas **não garantem segurança absoluta**. Ficam fora do que o Jarvis consegue
controlar, entre outros:

- dados de fabricante errados ou otimistas;
- saturação (clipping) do amplificador ou do DSP fora do que foi medido ou declarado;
- defeitos de instalação, fiação e componentes;
- volume de uso acima do declarado na sessão;
- alterações feitas no PC-Tool diferentes da receita.

O Jarvis declara essas limitações junto de cada recomendação sensível.

## 1. Classificação das recomendações

Toda alteração que muda **potência** entregue, **excursão** do cone, **frequência de corte** ou
**ganho** é **sensível — inclusive as reduções**. A exigência depende da direção do risco:

| Classe | Exemplos | Exigências |
| --- | --- | --- |
| **Sensível — risco crescente** | aumentar ganho de canal ou de entrada; reforço de EQ (ganho positivo); baixar passa-altas; suavizar inclinação de filtro; aumentar nível do subwoofer | dados **confirmados** para as regras aplicáveis; todas as regras SEG; aprovação de nível B. Sem dado confirmado: **bloqueada** |
| **Sensível — risco decrescente** | reduzir ganho; corte de EQ (ganho negativo); subir passa-altas; inclinação mais íngreme | aprovação de nível B e **aviso de efeitos colaterais** (abaixo); regras sem dado ficam “não verificáveis”, sem bloquear |
| **Não sensível** | polaridade; atraso | não mudam a energia elétrica entregue a cada alto-falante; seguem o procedimento seguro (SEG-08) e a aprovação normal do usuário |

**Por que reduções também são sensíveis** (resolve a contradição da v0.1.0): reduzir o ganho de um
canal costuma levar o usuário a subir o volume geral para compensar, o que aumenta a potência nos
demais canais; subir um passa-altas muda a soma no cruzamento e pode criar um vale que o usuário
tente “corrigir” com reforço. A redução diminui o risco no canal alterado, mas não no sistema.

**Sobre polaridade e atraso**: corrigir um cancelamento pode aumentar vários decibéis o nível
**acústico** numa faixa sem aumentar a potência **elétrica** de nenhum alto-falante. Por isso não
são sensíveis, mas a receita sempre começa com o volume reduzido (SEG-08).

## 2. Regras

Coluna **Fundamentação**: `fabricante` = depende do dado confirmado do equipamento; `fonte` = valor
com fonte registrada; **`provisório`** = valor conservador proposto pelo agente, **sem fundamentação
normativa**, a ser revisto com fontes — não é verdade técnica.

| ID | Grandeza | Regra | Sem dado confirmado | Fundamentação |
| --- | --- | --- | --- | --- |
| SEG-01 | Frequência de corte | O passa-altas de cada alto-falante nunca fica abaixo da frequência mínima recomendada pelo fabricante, nem com inclinação menor que a recomendada. | baixar a frequência ou suavizar a inclinação: **bloqueado** | fabricante |
| SEG-02 | Excursão | Toda recomendação que aumente conteúdo abaixo de **2 × Fs** do alto-falante exige verificação de excursão por cálculo determinístico com parâmetros T/S confirmados e potência no nível declarado. | **bloqueada** | fator 2 × Fs: **provisório**; cálculo: fabricante |
| SEG-03 | Potência | A potência elétrica estimada no canal, no nível de uso declarado, não ultrapassa a potência RMS confirmada do alto-falante, considerando o ganho total (entrada + EQ + canal). | aumento de ganho ou reforço: **bloqueado** | fabricante |
| SEG-04 | Ganho — passo | Aumentos de ganho e reforços de EQ: no máximo **+1,5 dB** por experimento. | — | **provisório** |
| SEG-05 | Ganho — reforço de EQ | Um filtro não reforça mais que **+3 dB**; a soma dos reforços sobrepostos numa banda de um canal não passa de **+6 dB**. Preferir corte a reforço. | — | **provisório**; o guia do fabricante do HELIX alerta para reforços acima de ≈ 4 dB (JV-S017), o que é coerente com a ordem de grandeza, mas não fundamenta os valores exatos |
| SEG-06 | Ganho — vales | Nunca recomendar reforço de EQ para preencher um vale classificado como cancelamento, interferência ou variação espacial (não equalizável). | — | fonte: guia do fabricante (JV-S017) desaconselha “encher” vales estreitos por distorção e ruído |
| SEG-07 | Margem digital | Toda recomendação de reforço informa o efeito sobre a margem até a saturação digital do DSP; abaixo do critério vigente, é bloqueada. | marcada **não verificável**; exige nível B com aviso | critério **sem valor** ainda: a definir com fonte na spec da feature F007 |
| SEG-08 | Procedimento seguro | Antes de alterar polaridade, crossover, atraso ou ganho: reduzir o volume; aplicar com o sinal parado; retomar o volume gradualmente até o nível de medição declarado. A receita sempre inclui esses passos. | — | prática de trabalho (prudência) |
| SEG-09 | Nível de medição e audição | Toda receita declara o nível de medição; nunca recomendar nível acima do critério vigente de exposição sonora. | usar o nível mais baixo que garanta a relação sinal-ruído mínima | critério **sem valor** ainda: a definir com fonte na spec da F012 |
| SEG-10 | Aprovação | Toda recomendação **sensível** (crescente ou decrescente) exige aprovação de nível B: o quê, em qual canal, quanto. | — | constituição, P4 |
| SEG-11 | Escrita no DSP | O Jarvis nunca escreve parâmetros no DSP; quem aplica é o desenvolvedor, no PC-Tool. | — | JV-D004, JV-D028 |
| SEG-12 | Dados planejados | Equipamento `planejado` ou `informado` não alimenta nenhuma regra como se fosse instalado e confirmado. | a regra resulta **não verificável** | constituição, P5 |

## 3. Como as regras são verificadas (G1 — testes automatizados)

- Cada regra tem testes com casos permitidos, limítrofes e proibidos.
- Testes de propriedade geram recomendações aleatórias e confirmam zero violações nas exibidas.
- Toda recomendação registra o resultado de cada regra aplicável: `aprovada`, `bloqueada` ou
  `não verificável`, e as limitações da seção 0.
- Valores **provisórios** aparecem como tal na própria recomendação (“limite provisório de +1,5 dB”).

## Histórico

| Versão | Data | Descrição |
| --- | --- | --- |
| 0.1.0 | 2026-10-15 | Proposta inicial (pedido do desenvolvedor: regras explícitas para potência, excursão, frequência de corte e ganho) |
| 0.2.0 | 2026-10-15 | Revisão 2 (JV-D022): alcance e limites declarados, sem promessa de segurança absoluta; reduções passam a ser sensíveis (classe de risco decrescente), resolvendo a contradição da v0.1.0; coluna de fundamentação com valores provisórios identificados; SEG-05 e SEG-06 ligadas ao guia do fabricante (JV-S017) |
