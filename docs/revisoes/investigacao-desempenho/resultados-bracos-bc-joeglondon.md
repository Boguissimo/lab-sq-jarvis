# Resultados dos braços B, C e D — `joeglondon/speakers-2026-filters` (exploração com medições reais)

> **Exploração com medições reais; ensaio contrafactual nos braços B e D. Não é benchmark com diagnóstico independente nem validação acústica do Jarvis.** Sem alteração de spec, limiares, algoritmos ou arquitetura; produto não corrigido. Dados originais não redistribuídos; só números derivados. 2026-10-16. Fonte: commit `799af51…`, 53 arquivos conferidos por SHA-256 antes de cada execução.
> Código: `ferramentas/investigacao/{bracos_bc,repetibilidade_sigma}.py`. Números por par: `resultados-bracos-bc-joeglondon.json`, `repetibilidade-sigma-joeglondon.json`. Resultados do braço A em `resultados-braco-a-joeglondon.md` (separados).

## 0. O que cada braço é (e o que não é)
| Braço | Transformação sobre os arquivos originais | Natureza |
| --- | --- | --- |
| A1 | nenhuma | dado como veio |
| A2 | só remove o separador de milhar da frequência (valores idênticos) | correção de **formato** |
| B | A2 + **metadados hipotéticos**: posição do microfone constante e id temporal por repetição | **contrafactual**. Os ids (`HARNESS-PRESUMIDO-<lado>-<k>`) são **sintéticos do harness**, **não vêm dos arquivos REW** e **não comprovam sincronização física**. O acordo soma complexa × medida em 30–150 Hz (±0,1 dB, ≤ 3°) é evidência favorável **só nessa faixa** |
| C | A2 reamostrado para grade logarítmica (24, 48, 96, 192 pontos/oitava), por dois métodos: **pontual** (interpolação linear em log f do nível e da fase desenrolada; mantém a rugosidade) e **janela** (média de potência e fase da média complexa em ±½ passo; suaviza, declarada como suavização) | **dado derivado**; não é nova medição, não é independente |
| D | C + B | contrafactual completo |

## 1. Tabela comparativa (10 pares cada: L e R × 5 repetições)
| Item | A1 originais | A2 só formato | B + metadados hipotéticos | C pontual (24–192 ppo) | C janela (24–192 ppo) | D = C + B |
| --- | --- | --- | --- | --- | --- | --- |
| Executou a análise | **0/10** (recusa) | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 |
| Portão de qualidade | reprovou (pontos mal lidos) | σ̂ **não estimável** (grade linear) | idem A2 | **σ̂ reprovada 10/10** em todas as densidades (mediana 3,89 / 3,53 / 2,33 / 1,57 dB) | σ̂ não estimável (suavização declarada) | pontual: reprovada; janela: não estimável |
| Sugestão | — | `solicitar_dados` | `solicitar_dados` | **`nao_da_para_concluir`** | `solicitar_dados` | pontual: `nao_da_para_concluir`; janela: `solicitar_dados` |
| Ref. temporal / fase | — | incompatível; **fase não calculada** | compatível (hipotética); **fase calculada 10/10** | incompatível; sem fase | incompatível; sem fase | compatível (hipotética); fase calculada 10/10 |
| Fase calculada (média; dispersão; atraso eq.) | — | — | L −6…+1°, R −62…−69°; dispersão 102–108°; atraso −0,07…+1,9 ms (faixa útil = banda inteira, 0,4 Hz–19 kHz) | — | — | pontual 48 ppo: média 7–45°, disp. 113–137°, atraso −2,6…+0,07 ms; janela 48 ppo: disp. 120–143°, atraso L −3,75 / R −1,0 ms (faixa ≈ 41–1 157 Hz) |
| Regra 2 (oposição constante) | — | não | **não** (dispersão ≫ 15°) | não | não | não |
| Regra 1 (cancelamento) | — | 10/10 | 10/10 | — (portão barra) | 10/10 | pontual: — ; janela: 10/10 |
| Frequência do cancelamento apontada | — | 7,3 / 1 091 / 7,0 Hz (3 espúrios) e 44,3 e 88,6–89 Hz | idem A2 | 44,3 e 88,5–88,8 Hz (≥ 48 ppo); 24 ppo: 44,9 e 73–87 Hz | 43,6–44,9 e 87–89 Hz | idem C |
| Regra 3 (vales em via isolada) | — | **86–109** (L/R) e **780–821** (Sub) | idem A2 | 4–29 (L/R) e 5–52 (Sub), **cresce com a densidade** | 0–15 e 1–16 | idem C |
| Hipótese "mais provável" | — | reflexão/interferência 10/10 | idem A2 | nenhuma (portão) | reflexão 10/10 | pontual: nenhuma; janela: reflexão 10/10 |
| "Cruzamento" (níveis iguais) | — | 4/10 coincidem com o físico (±2 Hz); outros 1,5…1 227 Hz | idem A2 | instável (56 Hz … 1 092 Hz) | instável (39 … 376 Hz) | idem C |

## 2. Impacto de cada transformação
- **Correção do formato (A1→A2):** é a que destrava tudo (de 0/10 para 10/10 análises). Sem ela, o produto não lê nenhuma exportação REW com ≥ 1 kHz.
- **Metadados hipotéticos (A2→B):** liga **só** a fase e a soma prevista. Não muda sugestão, hipótese, vales nem portão. A fase calculada mostra **dispersão ≈ 105°**: não é inversão constante de polaridade, e o Jarvis, agora com base medida e não por ausência, mantém "polaridade pouco provável". O atraso equivalente calculado numa faixa de 0,4 Hz a 19 kHz tem pouco significado físico (faixa útil sem limite operacional).
- **Reamostragem (A2→C):**
  - **σ̂ muda de "não estimável" para "reprovada"** (pontual) e depende da densidade da grade (3,9 → 1,6 dB de 24 a 192 ppo): a mesma medição fica "inconclusiva" ou "analisável" conforme a resolução exportada.
  - **Número de vales** muda de centenas para unidades/dezenas e cresce com a densidade: não é uma quantidade estável da medição.
  - **Cancelamento real (30–150 Hz):** com ≥ 96 ppo a posição fica a ≤ 0,2 Hz e a profundidade muda ≤ 1–2 dB (pontual); a **24 ppo** desloca (R: 88,6 → 73,4 Hz) e subestima em ~10 dB (−24 → −11…−13 dB). Janela suaviza o fundo (−18 dB a 48 ppo; ≈ igual a ≥ 96 ppo em L).
  - **Fase:** erro mediano soma complexa × medida praticamente inalterado (0,6–0,9°); a interpolação da fase desenrolada preservou a coerência. O **atraso equivalente** varia com o método (L: −2,5 ms pontual × −3,75 ms janela; R: ≈ 0 × −1,0 ms).
  - O cancelamento e o "cruzamento" continuam sem faixa operacional, mesmo na grade log.
- **D:** soma os efeitos; o portão decide (pontual barra, janela segue).

## 3. σ̂ × variabilidade entre repetições (referência empírica independente)
O desvio-padrão ponto a ponto **entre as 5 repetições** (200 Hz–10 kHz, 48 ppo, mesmo método) tem mediana de **0,12 dB** (L), **0,24** (R), **0,37** (L+Sub), **0,10** (R+Sub) e **0,66** (Sub, que está fora da sua faixa), com p90 de 0,3–1,2 dB (Sub: 6 dB). O σ̂ do produto (chamado diretamente) dá **2,4–4,6 dB** na mesma grade. Ou seja: em dado real **sem suavização**, σ̂ é **uma ordem de grandeza maior** que a variabilidade entre repetições (limite superior do ruído de medição). Interpretação: σ̂ mede a **irregularidade fina real** (estrutura acústica da sala, resolução fina), **não ruído**; ao tratar isso como ruído e barrar com "com este ruído, a medição não permite concluir", o portão descarta medições repetíveis. Cuidados: uma sala doméstica; a variabilidade entre repetições também embute qualquer mudança de posição; o σ̂ foi validado só no domínio simulado (limite já declarado).

## 4. Classificação dos achados (implementação / domínio / metodologia / dado)
| # | Achado | Classe | Gravidade / nota |
| --- | --- | --- | --- |
| F-1 | Leitor não trata separador de milhar (95 % dos pontos) | Erro de implementação | alta; correção pontual proposta (relatório do braço A, §8) |
| F-2 | Mensagem "refaça a medição" com medição boa | Erro de implementação (explicação incorreta) | média; barreira segura, explicação errada |
| F-3 | Centenas de vales em Sub fora de faixa; hipótese de reflexão 10/10 mesmo com portão "não estimável" | Possível deficiência metodológica (contextualização acústica) | a investigar; **sem contar falsos positivos** (sem referência independente) |
| F-4 | Cancelamentos em 44 e 89 Hz | Limitação de domínio (V02 vai de 200 Hz a 10 kHz) | não reprova o algoritmo |
| **F-5** | **σ̂ ≫ variabilidade entre repetições; "reprovada" em 10/10 com grade log sem suavização; depende da densidade** | **Possível deficiência metodológica no domínio do algoritmo** | **alta: o portão pode barrar medições boas**; precisa de validação adicional (mais conjuntos, incluindo carro) |
| F-6 | Sobreposição/cruzamento/vale/fase sem faixa operacional (subsônico até 19 kHz) | Limitação de domínio + ausência de barreira | média |
| F-7 | Número de vales e atraso equivalente dependem da resolução e do método de reamostragem | Deficiência metodológica (estabilidade) | média |
| F-8 | 24 ppo (mínimo aceito) desloca/subestima cancelamentos de baixa frequência | Limitação (densidade mínima vs. objetivo) | baixa para o V02 (domínio ≥ 200 Hz) |
| F-9 | Fase/soma recusadas sem id e posição; ausência de "depois" | Dado insuficiente (recusa correta) | — |

**Recusas corretas:** formato ilegível (barra, embora com explicação errada); σ̂ não estimável em grade linear; fase sem metadados; "nada confirmado" quando σ̂ não estimável (porém a hipótese continuou a ser exibida).
**Erros:** F-1, F-2. **Conclusões potencialmente inadequadas** (sem verdade independente, não contadas como falso positivo): hipótese de reflexão como "mais provável" (A2, B, C-janela, D-janela); "não dá para concluir" por σ̂ em medição repetível (C-pontual, D-pontual).

## 5. Lista priorizada
**Problemas superáveis (correção pontual provável, sob sua aprovação):**
1. F-1 leitor do separador de milhar, com testes de regressão no formato observado.
2. F-2 mensagem do portão: distinguir arquivo ilegível de faixa não coberta.
3. F-6 aplicar a análise (sobreposição, vale, fase) somente à faixa operacional da via/ao domínio declarado (decisão de spec; não é só código).
4. Avisar o usuário quando a grade for linear/fina e orientar a exportação (ex.: 1/48 de oitava, sem suavização), em vez de só "não estimável".

**Limitações aceitáveis (documentar, não corrigir agora):** domínio de 200 Hz a 10 kHz (F-4); σ̂ não estimável em grade linear (comportamento honesto); recusa de fase sem metadados (F-9); 24 ppo insuficiente para baixa frequência (F-8).

**Questões que exigem validação adicional antes de decidir:** F-5 (papel do σ̂ como portão com dado real; talvez σ̂ deva medir ruído por repetição/coerência e não por rugosidade); F-3 (regra de vales e hipótese de reflexão com contexto acústico; limite de largura em pontos/Hz e de via fora de banda); F-7 (estabilidade de vales e de atraso equivalente frente à resolução); conjunto em **áudio automotivo** com vias individuais, soma e "depois" (inexistente até agora).

## 6. O que não se pode concluir
Que o Jarvis acerta diagnósticos de crossover; que vale para carro; que a posição ou a sincronização foram constantes (B/D são contrafactuais); que a reamostragem é medição independente; que as taxas de alarme sejam falsos positivos.
