# Resultados do braço A — `joeglondon/speakers-2026-filters` (exploração com medições reais)

> **Exploração com medições reais. Não é benchmark com diagnóstico independente nem validação acústica do Jarvis.** Sem alteração de spec, limiares, algoritmos ou arquitetura. Dados de terceiros **não redistribuídos** (sem licença): aqui só números derivados, hashes e o código do harness. 2026-10-16.
> Fonte: commit `799af5104e83d9b3af2e832e5bd1fb4db3dd352e`; 53 arquivos conferidos por SHA-256 contra `admissao-joeglondon.json` antes de cada execução.
> Reprodução: clonar a fonte, depois `python ferramentas/investigacao/{admissibilidade,braco_a,descritivo_fisico}.py` (ver cabeçalhos). Números por par: `resultados-braco-a-joeglondon.json`.

## 0. Ordem real dos passos (honestidade de cegamento)
1. Critérios de admissibilidade **pré-registrados** (`ferramentas/investigacao/preregistro-braco-a.json`, SHA-256 `538ce86a…c294`), definidos antes de qualquer cálculo; ainda **não commitado** (o registro prova o conteúdo, não a data).
2. Admissibilidade calculada (sem o Jarvis). 3. Jarvis rodado (A1 e A2). 4. **Só depois** calculei o descritivo físico (`descritivo_fisico.py`): ele é **post hoc**, feito vendo a saída do Jarvis, e **não** conta como referência cega. 5. O relatório do autor foi lido por último.

## 1. As medições são compatíveis? (pré-registrado) — sim, na faixa 30–150 Hz
Para cada um dos 10 pares (L e R × 5 repetições), a soma complexa `lado + Sub Only` reproduz a medição `lado + Sub`: erro mediano de nível **0,06–0,14 dB** (p95 0,28–0,54 dB) e de fase **0,4–3,2°**, nos 311–324 pontos válidos; critério (≤ 1,0 dB, ≤ 3,0 dB p95, ≤ 10°) atendido em **10/10**. Varredura do atraso do Sub: melhor valor entre −0,04 e +0,02 ms (≈ 0), polaridade invertida piora (3–5 dB). **Conclusão:** nessa faixa, posição, nível e referência temporal são **empiricamente consistentes** entre as três medições de cada repetição; a diferença de método de atraso do `Sub Only` não afeta a fase. **Limites:** vale só para 30–150 Hz (comprimentos de onda de metros são insensíveis a pequenas mudanças de posição); não prova a posição nem autoriza usar fase acima disso. Repetibilidade entre as 5 repetições: desvio-padrão médio 0,13 dB (L, R), 0,07 dB (Sub), 0,06 dB (somas).

## 2. A1 — Jarvis sobre os arquivos originais: recusou 10/10, pelo motivo errado
- O leitor de texto do produto **interpretou errado 51 884 de 54 614 pontos (95 %) de cada arquivo**: o REW (en-US) escreve frequências ≥ 1 000 Hz com separador de milhar (`1,000.1222`), e o produto trata a vírgula como separador de campos. A frequência máxima lida caiu para 999,76 Hz e a ordem deixou de ser crescente.
- O portão básico reprovou e **nada foi diagnosticado** (comportamento seguro), mas a mensagem diz "Refaça a medição cobrindo 200 Hz a 10 000 Hz com valores válidos": **engana**, pois a medição está boa e o problema é o formato.
- **Classe: falha de implementação (leitor) + mensagem enganosa.** É exatamente o risco que o projeto já anotava ("formato de texto do REW a confirmar com arquivo real, JV-V04"), agora confirmado com arquivo real. Não é insuficiência do dado nem limite do algoritmo. A dependência de localidade do REW (outras localidades podem usar outro separador) é **hipótese não verificada**.

## 3. A2 — mesmos dados com só o separador de milhar removido (valores idênticos; harness)
Metadados **não preenchidos**: id da referência temporal e posição do microfone ausentes; tipo, taxa (48 kHz, do arquivo de impulso pareado de mesma data) e suavização ("nenhuma") vieram dos arquivos.

| Item | Resultado (10/10 pares, salvo indicação) | Avaliação |
| --- | --- | --- |
| Portão básico | aprovado | correto |
| σ̂ (irregularidade) | **não estimável** (grade linear de 0,366 Hz; 18 928 pontos/oitava), incerteza "não quantificada" | recusa correta; limite do algoritmo diante do formato de exportação |
| Referência temporal | **incompatível** (sem id e sem posição); fase, soma prevista e atraso **não calculados** | recusa correta por dado insuficiente (não preenchi) |
| Sugestão | `solicitar_dados` ("meça em outras posições… não reforce a EQ") | prudente |
| Regra 1 (cancelamento): onde | vale a 44,3 Hz (L4, L5) e 88,6–89,0 Hz (R1–R5) = **7/10 coincidem** com o ponto de maior cancelamento físico em 30–150 Hz (23–25 dB abaixo da soma de potências; ±2 Hz). **3/10 espúrios**: 7,3 Hz (L1), 1 091 Hz (L2), 7,0 Hz (L3) | **limitação de domínio** (os cancelamentos reais estão abaixo de 200 Hz, fora do domínio do V02): não serve para reprovar o algoritmo; só registra que a sobreposição não impõe faixa e pode reportar pontos subsônicos (< 20 Hz) |
| "Cruzamento" (níveis iguais) | coincide com o físico (±2 Hz) em **4/10**; nos demais aponta de 1,5 Hz a 1 227 Hz | mesma limitação de domínio (sem faixa operacional) |
| Regra 3 (vales em via isolada) | 86–109 "vales" no L/R e **780–821 no Sub** (acima de ~200 Hz o Sub está fora da sua faixa); largura 0,001–0,006 oitava (pontos isolados); hipótese "interferência ou reflexão" como **mais provável** em **10/10**, apesar do portão "nenhuma hipótese pode ser confirmada" | **interpretação inadequada / não sustentada**: detector calibrado para grade log; o produto não barra resolução fina nem via fora de banda. Falso positivo estrutural **provável**, mas sem verdade independente não dá para provar |
| Polaridade | "pouco provável" em 10/10 | só porque a fase não foi calculada; coincide com o físico (diferença de fase **não é constante**: dispersão 85–98° em 60–120 Hz), mas sem fundamento no Jarvis |

## 4. O que os dados mostram (post hoc, descritivo) e o confronto com o autor
- Cancelamento real do `L + Sub` perto de **44 Hz** e do `R + Sub` perto de **89 Hz**, com fase L–Sub próxima de 180° **só nesse ponto**. Não é inversão constante de polaridade (a fase varia com a frequência).
- O autor entrega um **projeto de filtros** por otimização modelada (cruzamento LR4 em 140 Hz; atraso relativo do Sub de −1,8 ms; vários PEQ), **não um diagnóstico do defeito medido**; não remediu depois de aplicar. Ele é *compatível* com um problema de tempo/fase na região do cruzamento, mas isso é **modelado**, não verificado, e não é referência independente.
- O Jarvis (V02) **não chegou** a "tempo/fase na região do cruzamento" porque, sem metadados, recusa a fase; e **apontou uma hipótese (reflexão) não sustentada**.

## 5. Falha × limite × dado (classes: erro de implementação, limitação de domínio, deficiência metodológica, dado insuficiente)
| Achado | Classe |
| --- | --- |
| Leitor interpreta mal 95 % dos pontos (vírgula de milhar) e a mensagem culpa a medição | **Erro de implementação** (+ explicação ao usuário incorreta) |
| σ̂ não estimável em grade linear | Limitação de domínio/formato (comportamento honesto) |
| Sem faixa operacional: cancelamento e "cruzamento" espúrios em 3/10 e 6/10 | Limitação de domínio (cancelamentos < 200 Hz); o V02 não impõe faixa operacional à sobreposição |
| Regra 3 gera centenas de "vales" e hipótese "mais provável" em dado de resolução fina e via fora de banda | **Possível deficiência metodológica** (contextualização acústica: via fora de banda e resolução fina), a investigar; falsos positivos **não contados** sem referência independente |
| Fase/soma recusadas por falta de id e posição | **Dado insuficiente**; recusa correta |
| Ausência de "depois" e de diagnóstico independente | **Dado insuficiente** (impede benchmark) |

## 6. O que NÃO se pode concluir
Que o Jarvis acerta ou erra diagnósticos de crossover (não há diagnóstico independente); que vale para áudio automotivo (é sala doméstica com subwoofer); que os filtros do autor funcionam; que a posição foi constante; que a reamostragem (braço C) é inócua (não executada).

## 7. Próximos passos e decisões
- **Braço B** exige **duas** presunções, não uma: posição constante **e** identificador único de referência temporal por repetição (o núcleo exige os dois). A admissibilidade (§1) sustenta isso só em 30–150 Hz. **Posso rodar o B com essas duas presunções rotuladas?**
- **Braço C** (grade log) está autorizado: executo em seguida, com registro do método e do efeito sobre σ̂ e vales, se aceitar a ordem.
- **Para os mantenedores (sem agir):** os achados da §5 (leitor e faixa operacional) seriam candidatos a registro como achados de investigação; **nenhuma alteração do produto sem sua aprovação.**
- Posso fazer o commit e o push de `ferramentas/investigacao/` (código do harness e pré-registro), `resultados-braco-a-joeglondon.{md,json}`? Os dados originais não vão.

## 8. Classificação formal dos achados (decisão do desenvolvedor, 2026-10-16)
**F-1 — Erro de implementação: leitor de texto não trata separador de milhar.** Confirmado com dados reais (REW 5.31.3, en-US): 95 % dos pontos de cada exportação são lidos com frequência errada. **Gravidade: alta** para o uso real (bloqueia qualquer exportação REW em banda larga com valores ≥ 1 kHz); mitigada porque o portão barra a análise (nada é diagnosticado em cima de dado corrompido). **Correção proposta (não aplicada):** em `rew_texto`, reconhecer a vírgula como milhar quando o mesmo token tem ponto decimal depois (padrão `\d{1,3}(,\d{3})+\.\d+`) e validar monotonicidade da frequência; decidir a regra para locais com vírgula decimal. Testes de regressão com linhas sintéticas no formato observado (sem copiar dados de terceiros) e um teste de que o arquivo completo não degrada para "frequências fora de ordem". **Alteração pontual a preparar depois, sob sua aprovação; não corrigida nesta investigação.**
**F-2 — Explicação incorreta ao usuário.** O Jarvis disse para refazer uma medição que estava correta. Um bloqueio seguro não torna correta a explicação. **Proposta:** distinguir "arquivo ilegível/ordem de frequências inválida" de "faixa não coberta" na mensagem do portão.
**F-3 — Possível deficiência metodológica: vales e hipótese de reflexão sem contexto acústico.** Centenas de vales de 1 ponto em subwoofer fora da faixa e hipótese "reflexão" recorrente (10/10). Examinar relevância e segurança diagnóstica (limite de largura em pontos/Hz, faixa operacional da via, resolução da grade). **Sem contagem de falsos positivos** (sem referência independente).
**F-4 — Limitação de domínio (não reprovação):** cancelamentos em 44 Hz e 89 Hz estão fora do domínio de 200 Hz a 10 kHz do V02.
