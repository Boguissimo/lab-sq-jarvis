# Candidato a segundo conjunto automotivo — `ayukhno/autosound-measurements` (triagem e protocolo PROPOSTO; nada executado)

> Exploração com medições reais. Sem alterar estimador, portão, limiares, spec ou `src/`. O Jarvis **não foi executado** sobre estes dados; o protocolo abaixo aguarda sua aprovação. 2026-10-16.

## 1. Admissão (verificada)
- **Fonte:** <https://github.com/ayukhno/autosound-measurements>, commit `7725d426745408b962ea1de4fab6e252bc6b89b6`; um autor (28 commits). Clonado como **dado** fora do projeto; **nenhum código do repositório foi executado** (`tools/check.py` e demais scripts não foram rodados).
- **Licença:** dados **CC BY 4.0** (texto em `LICENSE`), scripts MIT. A redistribuição é permitida **com atribuição** ("autosound-measurements (ayukhno), CC BY 4.0"); mesmo assim, mantenho só manifesto (`admissao-ayukhno.json`: 63 arquivos com SHA-256) por tamanho (≈ 358 MB).
- **Veículo e equipamento:** VW Passat B8 sedan LHD (carro real), Helix DSP Ultra S, Behringer ECM8000 (arquivos de calibração 0°/90° incluídos), Focusrite Scarlett 2i2, REW 5.40 β132; **loopback físico** como referência de tempo para todos os sweeps.
- **Conteúdo útil** (`cars/vw-passat-b8-sedan-lhd/`):
  | Sessão | O que tem | Para quê |
  | --- | --- | --- |
  | `2026-08-20_front-set-02` | 8 canais individuais (sub, woofers, mids, tweeters, centro) em IR (Resonalyze JSON v7, 96 kHz, **t = 0 no loopback**), microfone em **tripé**, DSP **zerado** (`dsp-state.json`: sem EQ, atraso 0, ganho 0 dB, polaridade normal, só HPF de proteção), **repetições** (`m_L` 3 capturas; `w_R` e `w_R-retake`), controles de deriva, near-field, coerência por canal (bloco A), duas programas independentes (REW × Resonalyze) | repetibilidade, coerência como referência de ruído, IR com referência física de tempo |
  | `2026-06-15_front-set-01` | 8 canais (microfone na mão), RTA espacial, 2 estados do DSP | menos controlado; apenas comparação |
  | `2026-08-24_mmm-rta-levels` | RTA de microfone móvel (150 médias, 1/48 oitava, **96 ppo, sem suavização, log**, texto `freq_Hz SPL_dB`), cada driver sozinho **e três somas medidas** (`sum_sw_w`, `sum_L`, `sum_R`, `sum_all`); **só magnitude** (a própria fonte diz que não serve a polaridade/atraso/cruzamento) | σ̂ em dado real automotivo com a grade que o produto exige; Regra 1 e 3 só em magnitude |
- **Metadados documentados (não inventados):** taxa 96 kHz, referência de tempo `SynchronizedLoopback` (físico), posição (ponto da cabeça do motorista, tripé), estado do DSP, suavização "nenhuma", `splOffset`, SNR por canal, hora das capturas, correção de deriva (não aplicada aos arquivos). Estão no `README`/`manifest.json`, não em cada arquivo: seriam transcritos para o manifesto do caso **com referência à origem**.
- **Limites da fonte (declarados pelo autor):** microfone móvel/ocupante pode mudar a interferência acima de 500 Hz (caso `w_R`); deriva por temperatura (≈ 0,43 amostra/°C); IR de bloco A (Resonalyze nativo, 95 MB) fora do repositório; calibração do microfone **não** aplicada às IRs; nenhum "defeito" diagnosticado, nem antes/depois de intervenção.

## 2. Valor e limites para o Jarvis
- **Mais próximo do que você pediu:** carro real, vias individuais, repetições e metadados bons. **Não tem** soma *medida* de duas vias com fase, nem diagnóstico de defeito de crossover publicado: **não é benchmark de diagnóstico**.
- **Serve a F-5 em carro** (repetibilidade, coerência, REW × Resonalyze) e a **casos reais com falha injetada** (ver §3-H), que dão verdade conhecida.
- O núcleo lê o texto do RTA direto (grade log de 96 ppo, sem fase); as IRs exigem a **conversão autorizada** (IR→resposta em frequência no harness).

## 3. Protocolo proposto (a executar só com sua aprovação)
Classes sempre separadas nos totais: **R** (real), **R-injetado** (real com falha injetada, verdade conhecida; **não** é problema de campo) e **S** (sintético).
- **Pré-registro e cegamento:** parâmetros de conversão, janelas, perguntas e critérios gravados e com SHA-256 **antes** de rodar; referência física derivada dos dados calculada por código separado do Jarvis; nada de ajuste de algoritmo ou limiar.
- **Conversão IR→FR (no harness):** registrar taxa (96 000 Hz), unidades (fração da escala cheia), t = 0 = amostra 0 (loopback), tratamento do tempo negativo (enrolado na cauda), janela, FFT, grade e interpolação, com hash do original e do derivado.
- **Arm F5-carro (sem diagnóstico):**
  1. σ̂ do produto (chamada direta) em cada canal e janela, em grade log 48 e 96 ppo;
  2. repetibilidade das 3 capturas de `m_L` (mesma posição, tripé) e de `w_R` × `w_R-retake`, no mesmo ponto de frequência;
  3. coerência (bloco A) como referência independente de ruído por banda;
  4. a mesma decomposição do F-5 (parte estável × variabilidade) e a pergunta "o portão rejeita medição repetível?";
  5. σ̂ nas curvas **RTA espacial** (96 ppo nativos) de cada driver e soma.
- **Arm D-real (Jarvis sobre dado real, com soma *calculada*):** vias `m_L` e `tw_L` (e `m_R`/`tw_R`), **soma = adição complexa das duas IRs** (classe "soma calculada", declarada; vale se o sistema é linear e invariante no tempo, com a deriva descrita acima), metadados transcritos da fonte; saída integral do `Servico`.
- **Arm H (real com falha injetada, verdade conhecida):** sobre as mesmas IRs reais, aplicar por código **polaridade invertida no tweeter** (multiplicar a IR por −1), **atraso conhecido** (deslocar a IR de N amostras) e controles sem injeção. É o único modo de ter verdade para polaridade/tempo em carro real. Rotulado **R-injetado**.
- **Registro por caso:** o de sempre (acertos, divergências, abstenções corretas, falsos positivos/negativos **só quando houver verdade**), separando falha de implementação, limitação de domínio, deficiência metodológica e dado insuficiente.

## 4. O que preciso de você (decisões de engenharia)
1. **Janela e tratamento na conversão IR→FR:** sugiro registrar duas — **30 ms a partir do primeiro som direto** (escala usual de medição em carro) e **IR inteira** (2,73 s) — reportadas separadas. Isso afeta σ̂ e vales; é escolha de metrologia. Qual prefere, ou outra?
2. **Soma calculada** no lugar de soma medida: aceita como *classe declarada* no Arm D-real?
3. **Falha injetada (Arm H):** autoriza essa classe híbrida, com o rótulo e os limites acima?
4. **Aprovação do protocolo** (e do pré-registro) para executar F5-carro, D-real e H.
