# Mapa técnico de evolução do Lab SQ Jarvis (produto completo) — PROPOSTA para decisão

> Visão técnica de todo o produto, **sem arquitetura nova desnecessária e sem implementar nada fora do escopo aprovado**. O domínio operacional do V02 (200 Hz–10 kHz, vias médio/tweeter) **permanece inalterado** durante a validação; este mapa só garante que não o impeça de crescer. Calibração automatizada fica para depois, mas os **modelos físicos e interfaces** que ela exigirá são previstos desde já. Base: código atual (`src/jarvis`, 3,3 mil linhas), feature map F001–F022 (JV-D042), ADRs do V02 e as evidências da investigação (F-1 a F-10, joeglondon, Passat). 2026-10-16.

## 1. O que existe hoje (e é reaproveitável)
| Módulo | O que faz | Reuso futuro |
| --- | --- | --- |
| `rew_texto` | lê/escreve resposta em frequência em texto (freq, nível, fase) | base da aquisição; **precisa** de IR, RTA e dos defeitos F-1..F-3 (correção em `claude/correcao-pontual-formato-rew`) |
| `calculos` | qualidade básica, referência temporal declarada, soma complexa/de potências, sobreposição, diferença de fase, vale relativo, σ̂, vales individuais, detector de mudança, comparação previsto × medido | núcleo determinístico (P3); funções puras, sem estado |
| `referencia/modelo.py` | **modelo físico direto**: H = alto-falante × filtros DSP (LR4, PEQ, ganho) × polaridade × atraso × reflexões, soma complexa, camada de aquisição (ruído, posição) | **candidato natural a motor de previsão** da calibração futura (hoje só gera casos de teste) |
| `regras`, `regras_v1_0`, `limiares` | indícios, hipóteses, portão, limiares versionados e provisórios | diagnóstico (precisa de contexto acústico, ver §3) |
| `seguranca` | classificação de risco, regras SEG, admissibilidade | indispensável a qualquer recomendação ou otimizador |
| `sessao` (`Servico`) + `persistencia` + `migracao` | fluxo guiado, cadeia de conhecimento, originais imutáveis, configurações, diário | espinha dorsal; já independente da interface |
| `interface` (PySide6) | sessão guiada, histórico | camada fina sobre `Servico` |
| `ferramentas/investigacao` | harness cego, conversão IR→frequência, σ̂, injeção de falhas | base da bancada de validação; **fora do produto** |

## 2. Módulos necessários por assunto (sub, midbass, mid, tweeter)
Convenção: ✔ existe · ◐ parcial/limitado · ✖ falta. "Via" = sub, midbass (porta), midrange, tweeter, centro.
| Capacidade | Estado | Observações e evidência |
| --- | --- | --- |
| **Aquisição**: texto REW de resposta em frequência | ◐ | milhar en-US corrigido na branch de correção; grade log/linear; suavização declarada |
| Aquisição: **resposta ao impulso** (janela, FFT, referência de tempo) | ✖ | feita só no harness (30 ms e 1,7 s, bin mais próximo); precisa de janela declarada e registrada |
| Aquisição: RTA espacial (magnitude) | ◐ | lê como texto; sem fase; σ̂ saudável (0,05–0,12 dB no Passat) |
| Aquisição: repetibilidade e coerência | ✖ | no Passat: variabilidade 0,2–0,4 dB é deriva suave, ruído aleatório ≤ 0,2 dB; hoje nada disso é medido |
| **Admissibilidade** (portão): formato, faixa, ordem | ✔ | com mensagem a corrigir (F-2) |
| Admissibilidade: ruído/irregularidade (σ̂) | ◐ | depende de grade e janela; mistura estrutura e ruído (F-5) → decisão metodológica aberta |
| **Papel e faixa operacional da via** (sub/midbass/mid/tweeter, HPF/LPF declarados, banda útil) | ✖ | **lacuna central**: sobreposição, fase e vales hoje valem de 0,4 Hz a 19 kHz; tweeters/sub fora da banda geram vales e cancelamentos espúrios (F-3, F-6, Passat) |
| **Magnitude**: nível, balanço L/R, picos e vales, soma de potências | ◐ | vales só 200 Hz–10 kHz; sem balanço L/R nem alvos |
| **Fase e atraso**: diferença de fase, atraso equivalente, alinhamento | ◐ | exige referência temporal **declarada**; atraso equivalente instável sem faixa por via |
| **Crossover**: sobreposição, soma medida × prevista | ◐ | assume vias de crossover projetado em fase (REF-001); em drivers reais não alinhados a "oposição constante" não existe |
| **Polaridade e tempo em vias reais** | ✖ | Passat: 0/48 acertos em falhas injetadas; a fase vê os 180°, a regra não usa; precisa de **previsão/estado anterior** em vez de assinatura |
| **Interferências** (comb, reflexões, SBIR) | ◐ | Regra 3 centenas de "vales" em grade fina; falta noção de escala (largura em Hz/oitava) e de via fora de banda |
| **Acústica da cabine** (modos, assimetria L/R, boundary) | ✖ | o Passat mostra assimetria entre portas de 10–19 dB; nenhum módulo trata; útil como contexto das hipóteses |
| **Segurança** (SEG, cadastro `confirmado`) | ✔ | funções puras; depende de cadastro (F011) |
| **Diagnóstico**: indícios → hipóteses ordenadas | ◐ | cobre polaridade/vale/ruído; falta atraso, nível L/R, corte inadequado (F014) |
| **Previsão de resultados**: antes/depois | ◐ | previsão da inversão de polaridade existe (`soma_complexa`, comparação); falta previsão para atraso, ganho, corte, PEQ — o `modelo.py` já calcula |
| **Experimento** (uma variável, veredito) | ✔ | polaridade; precisa estender a atraso/ganho |
| **Registro/rastreabilidade** | ✔ | cadeia e originais imutáveis |
| **Interface e IA** | ◐ | sessão guiada ✔; assistente (F009) pendente |
| **Calibração automatizada** | ✖ (futuro) | ver §4 |

## 3. Lacunas que as evidências tornam prioritárias (sem expandir o V02)
1. **Contexto acústico da via**: toda análise (sobreposição, fase, vales, σ̂) deve receber a **faixa operacional da via** (cadastro F011 + DSP declarado). Resolve F-3/F-6 e a falta de detecção no Passat; é dado, não algoritmo novo.
2. **Diagnóstico por previsão e por comparação**: usar a **soma prevista** (modelo) e o **estado anterior** em vez de "assinatura de 180° constante".
3. **Aquisição como cidadã de primeira classe**: IR com janela declarada, repetições, coerência, grade, suavização e hash — e a decisão sobre o papel do σ̂.
4. **Escala espectral explícita**: σ̂, vales e densidade dependem da grade (3,8 → 1,6 dB de 24 a 192 ppo); a escala deve ser parâmetro declarado.

## 4. Interfaces a reservar para a calibração futura (não implementar)
| Interface | Função | Reaproveita |
| --- | --- | --- |
| `Via` / `Sistema` (papel, faixa operacional, filtros, polaridade, atraso, ganho) | descrição física declarada do que está instalado | cadastro F011, `configuracao` do banco |
| `Previsor(sistema, alteração) → resposta prevista` | prevê a soma após uma alteração | `referencia/modelo.py` + `calculos.soma_complexa` |
| `Objetivo` (curva-alvo/critério versionado) | define "melhor" (P8: só muda por decisão) | `limiares` versionados |
| `Restrições` | limites SEG e do cadastro | `seguranca.avaliar/admissibilidade` |
| `Busca` (futuro) | propõe alterações dentro de restrições e objetivo | — (etapa posterior) |
| `Exportador` / receita | gera receita para o PC-Tool; **não escreve no DSP** (P10) | F015, F019 |
O critério: nada disso exige mudar o V02; exige apenas que os resultados do V02 sejam **dados estruturados e reutilizáveis** (já são, na cadeia).

## 5. Dependências entre funcionalidades
`Cadastro de equipamento (F011)` → `faixa operacional por via` → `sobreposição/fase/vales por via` → `diagnóstico (F014)`.
`Modelo direto (modelo.py)` → `Previsor` → `experimento com previsão (F007)` → `calibração assistida (F015)` → `Busca` (futuro).
`Aquisição robusta (IR, repetição, coerência, grade)` → `portão com ruído medido` → qualquer conclusão de campo.
`Seguranca` bloqueia todas as saídas que recomendam alterações.

## 6. Sequência recomendada (curta; cada passo com decisão de Fabrício quando afetar escopo)
1. **Feito:** correção pontual dos três defeitos (branch própria).
2. **Decidir F-5** (papel do σ̂ e do portão) — sem isso, a admissão de medições reais fica instável.
3. **Faixa operacional por via** como entrada declarada das análises (spec do V02/V04): maior ganho prático.
4. **IR e repetição** na aquisição (F004/F012), com janela e coerência registradas.
5. **Diagnóstico por previsão** de polaridade/tempo/nível, reutilizando `modelo.py` como motor, antes de qualquer otimizador.
6. **Um caso real com defeito documentado e antes/depois** (a única validação que falta); só então avançar a F014/F017.
7. Calibração automatizada **depois** do Marco 2.

## 7. O que NÃO construir agora
Otimizador/automação de ajuste; modelo completo de cabine; leitura/escrita de arquivos do DSP; novas camadas genéricas "para o futuro". Nada disso é pré-requisito do que a evidência pede.

## 8. Decisões que precisam de Fabrício
1. **Faixa operacional por via** como dado de entrada (cadastro + DSP declarado): aprova como direção para o V02/V04 (afeta spec)?
2. **Promover `modelo.py` a motor de previsão** do produto (hoje é gerador de casos): aprova como direção?
3. **Prioridade**: F-5 (portão) antes ou depois da faixa operacional?
4. **IR na aquisição**: entra no V04 (medições reais) ou fica para depois?
