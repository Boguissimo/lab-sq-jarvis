# Deriva e refazer entre capturas (Passat B8) e utilidade do gatilho adaptativo

> **Exploração com medições reais de um carro, uma sessão.** Complementa `metrologia-e-rigor-usabilidade-joeglondon.md` (limite nº 4). Não valida nem reprova o V02; não altera `src/`, spec, limiares nem arquitetura. 2026-10-16.
> Fonte: `ayukhno/autosound-measurements` @ `7725d42` (CC BY 4.0; 63 arquivos conferidos por SHA-256). Pré-registro: `preregistro-deriva-passat.json` (SHA-256 `a2d4b356…457f`), commitado em `baa363c` **antes** do cálculo. Código: `deriva_passat.py`. Números: `deriva-passat.json`.

## O que estes dados são (e não são)
**Não há deslocamento deliberado do microfone.** `m_L`, `m_L-ctl1`, `m_L-ctl3` são o mesmo ponto em tripé em t+0, +91 e +277 s (deriva de temperatura da cabine: 0 / −0,291 / −0,636 amostras a 96 kHz). `w_R` e `w_R-retake` são a mesma via 12 min depois, com o torso do operador em outra posição. O ensaio mede sensibilidade à **deriva temporal e ao refazer pelo operador**, não a reposicionamento deliberado.

## Estabilidade de decisões de balanço L/R (efeito a resolver: 1 dB; estável se amplitude ≤ 0,5 dB)
| Decisão | Valores por captura (dB) | Amplitude | Classe |
| --- | --- | --- | --- |
| D1 balanço L−R dos médios, 200 Hz–10 kHz | 3,39 / 3,74 / 3,36 | 0,38 dB | **estável** |
| D2 balanço L−R dos woofers, 40–500 Hz | −0,08 / −0,50 | 0,42 dB | **estável** |
| D3 balanço L−R dos woofers, 500–2000 Hz | 1,88 / 0,79 | **1,09 dB** | **instável** |
Uma decisão de balanço L/R acima de 500 Hz com os woofers **pode inverter de sentido ou sumir só por refazer a captura** (o efeito é maior que o próprio dado). Abaixo de 500 Hz e nos médios em tripé ela se sustenta.

## O gatilho adaptativo (τ = 0,3 dB, mediana de |Δ nível| entre capturas consecutivas, na banda útil do canal)
| Par | Banda | Gatilho | Pediria nova captura? |
| --- | --- | --- | --- |
| m_L × ctl1 | 200 Hz–10 kHz | 0,40 dB | sim |
| m_L × ctl3 | idem | 0,26 dB | não |
| ctl1 × ctl3 | idem | 0,53 dB | sim |
| w_R × retake | 40–500 Hz | 0,34 dB | sim |
| *w_R × retake, 500–2000 Hz (complemento rotulado)* | banda da decisão D3 | **2,23 dB** | sim |
- **Nos médios (D1) e nos woofers abaixo de 500 Hz (D2) o gatilho dispara em 3 de 4 pares embora a decisão seja estável**: com τ = 0,3 dB o gatilho é **mais sensível que a decisão** em carro (a deriva de tripé já dá 0,26–0,53 dB). Os alarmes seriam desnecessários para essas decisões.
- **Para D3 o gatilho "acertou", mas por margem mínima** (0,34 dB contra 0,30 na banda útil, 40–500 Hz, que não é a banda da decisão). Calculado **na banda da decisão** ele separa claramente (2,23 dB). Leitura: o gatilho deve ser medido **na banda em que a decisão será tomada**, não na banda útil do canal.
- O τ não foi ajustado após ver os números (regra fixada antes). Com 4 pares o ensaio é só descritivo: **não estima** taxas de falso alarme ou acerto.

## Fase e deriva (descritivo, 200–2000 Hz)
Mediana de |Δfase| entre capturas: 0,85°, 1,17° e 1,88°; esperado só pela deriva de tempo do manifesto: 0,69°, 0,82° e 1,50° (razão ≈ 1,2–1,4). A deriva de fase entre capturas é **compatível com o deslocamento de tempo medido** e **minúscula frente a 0,25 ms** (que valeriam ~127° a 1,4 kHz): decisões de tempo/polaridade não são sensíveis a ela nestes dados. Atenção: a referência temporal por loopback preserva a fase; sem ela, isso não vale.

## Conclusões (com limites)
1. A repetição adaptativa em carro precisa de gatilho **por decisão e por banda da decisão**, com τ coerente com a deriva esperada (aqui ~0,3–0,5 dB em tripé). Um τ único sobre a banda útil gera alarmes sobre decisões estáveis e pode não ver instabilidade fora da banda. **Escolher τ é decisão de Fabrício** (limiar do produto, P8); aqui só se mostra o efeito.
2. O ganho de repetir em carro está em **sinalizar decisões frágeis** (D3), não em baixar o erro das estáveis; combina com o achado da sala, onde repetir não mudou nenhuma decisão.
3. Limites: um carro, uma sessão, 3 + 2 capturas, sem verdade independente, sem reposicionamento deliberado, só balanço de nível (não há soma medida no conjunto).

## Pendência que só um dado novo resolve
Reposicionamento **deliberado** (deslocar o microfone N cm e refazer) não existe em nenhum dos dois conjuntos. Se Fabrício quiser fechar esse ponto, uma sessão curta de campo com o Focus (mesma via, 3 posições deliberadas) responderia; é uma decisão de prioridade dele, não bloqueia nada.
