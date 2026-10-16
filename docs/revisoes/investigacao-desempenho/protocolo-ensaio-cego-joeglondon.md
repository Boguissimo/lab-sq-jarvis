# Protocolo do ensaio cego — conjunto `joeglondon/speakers-2026-filters` (PARA APROVAÇÃO; nada foi executado)

> Exploratório. Sem alteração de spec, limiares, algoritmos ou arquitetura; sem merge na `main`. **O Jarvis ainda não foi rodado sobre estes dados.** 2026-10-16.

## 1. Acesso e admissão (verificados)
- `github.com` e a API respondem 403 por proxy, mas `git clone` e `raw.githubusercontent.com` funcionam. Clonei o repositório **como dado**, fora do projeto (pasta temporária da sessão), no commit `799af5104e83d9b3af2e832e5bd1fb4db3dd352e` (`main`). **Nenhum código do repositório foi executado.** `Jamesits/eqx` (leitor de `.mdat`) respondeu a `ls-remote`; **não foi clonado nem usado**: as exportações de texto bastam.
- **Origem:** projeto pessoal de um único autor (12 commits), medições de 18/04/2026 com REW 5.31.3, UMIK-1, sweep log de 128k. **Sala doméstica, caixas L/R + subwoofer. Não é áudio automotivo.**
- **Licença: ausente** (nenhum `LICENSE`). Direitos não declarados ⇒ **não copiar os dados para este repositório**. Em `admissao-joeglondon.json` ficam só caminhos, tamanhos e SHA-256 dos 53 arquivos (50 exportações SPL/impulso, `.mdat`, calibração do microfone, distorção). Quem quiser reproduzir clona a fonte e confere os hashes.
- **Arquivos originais confirmados:** `SPL/` e `Impulse/` com `L`, `R`, `Sub Only`, `L + Sub`, `R + Sub`, **5 repetições cada**; `All Measurements (center).mdat` (38 MB); `Microphone Correction.txt`; `Distortion/`.
- **Formato SPL:** `Freq(Hz) SPL(dB) Phase(degrees)`, 54 628 pontos, **grade linear de 0,366 Hz**, sem suavização, cabeçalho com data, fonte e nota de atraso. Impulso: 48 kHz, 131 072 amostras, "IR sem janela, normalizado".
- **Referência de tempo (declarada nos cabeçalhos):** todas as medições usam *acoustic timing reference* tocada por L, sem offset. Atrasos estimados: L ≈ −0,05 ms; R ≈ −0,04 ms; L+Sub ≈ −0,05 ms (uma com −0,12 ms e "clock adjust"); **Sub Only ≈ −1,38 ms "pelo início do IR"** (método diferente das demais).
- **Ausente:** posição do microfone em cada repetição (o README não a documenta); ganho/nível de cada canal e a configuração do processador na hora da medição; **medição posterior à aplicação dos filtros** (os perfis são gerados e "preditos"; o README manda remedir depois de carregar). Logo **não há "depois" físico**.

## 2. Qualidade e classe da referência (avaliada antes de rodar, sem ler os relatórios)
- O que o autor publica é um **projeto de filtros (miniDSP) por otimização modelada**, não um diagnóstico de defeito por pessoa independente. Os números de "cancelamento previsto" e de "RMS depois" são **resultado modelado**, não verificado por medição.
- **Portanto este conjunto NÃO é benchmark real com referência independente.** Classe: **exploração com dado real** (dado bruto verificado, sem parecer externo e sem eficácia comprovada). Nada aqui será chamado "validação real".
- Opinião do autor não é tratada como verdade; o relatório dele só será lido **depois** da execução, para confronto, e rotulado "modelado".

## 3. O que o núcleo atual consegue (previsto pela leitura do código; a conferir na execução)
| Ponto | Previsão | Natureza se confirmado |
| --- | --- | --- |
| Papéis | via A = `L`, via B = `Sub Only`, soma = `L + Sub` (mesma repetição k); os rótulos do produto dizem "médio/tweeter" | limite de escopo (V02 = 2 vias médio/tweeter) |
| Cobertura mínima 200 Hz–10 kHz, mesma grade nas três | atendida | — |
| σ̂ (irregularidade) | **não estimável** (grade linear, não logarítmica; ≥ 24 pontos/oitava exigido): análise segue só descritiva | limite do algoritmo diante do formato de exportação |
| Vales individuais (200 Hz–10 kHz) | janelas de 1/3 de oitava calculadas em pontos podem ficar mal dimensionadas numa grade linear; ver na execução | possível falha de implementação ou limite; **a classificar com evidência** |
| Referência temporal | exige `tipo`, `id`, `taxa_amostragem` e `posicao_microfone` iguais; **posição não existe nos dados** | insuficiência do dado ⇒ fase e soma prevista recusadas (comportamento correto do Jarvis) |
| Faixa do cruzamento | main × sub em ~40–150 Hz; o detector de vales só olha ≥ 200 Hz | fora do escopo do detector |

## 4. Braços do ensaio (só o A é “sem presumir nada”)
- **A — como veio.** Metadados somente do que está nos arquivos; posição do microfone **não declarada**. Esperado pelo código: referência temporal "incompatível" ⇒ sem fase. Registra o comportamento real.
- **B — condicional (precisa do seu aceite).** Declarar posição igual para as três medições da **mesma repetição k**, sob a **hipótese não verificada** de que a repetição k de L, Sub e L+Sub foi feita no mesmo ponto. Todo resultado do B é rotulado "condicional a uma suposição".
- **C — conversão (precisa do seu aceite).** Reamostrar para grade logarítmica no harness (parâmetros e método registrados; transformação anotada) para exercitar σ̂ e vales; não substitui o A.
- **Referência física derivada dos dados (independente do Jarvis e de opiniões):** feita antes da execução, em código separado e simples (numpy): (i) soma complexa de `L` e `Sub Only` da repetição k contra a medida `L + Sub` k (consistência física); (ii) diferença de fase L–Sub e atraso equivalente por frequência; (iii) profundidade do cancelamento da soma medida contra a soma de potências. Dá a "verdade" mensurável; **não** diz qual ajuste é o melhor.

## 5. Registros e critérios (definidos antes)
- Saída bruta integral do `Servico` e de `calculos`, com proveniência (hashes, commit, versão do produto).
- Por braço e por repetição (5): sugestão, hipóteses, portão de qualidade, motivos de recusa, números citados; concordância com a referência física; abstenções corretas; falsos positivos/negativos; classificação de cada falha em **implementação / algoritmo / dado insuficiente**.
- Variabilidade entre as 5 repetições é resultado, não ruído a esconder. Resultado negativo tem o mesmo destaque.
- **Cegamento:** hash do arquivo de referência física e da lista de perguntas gravados antes; relatórios do autor lidos só depois.
- Sem ajuste de limiares, regras ou código para acomodar o resultado.

## 6. Decisões que preciso de você
1. Aprova a **classificação**: exploração com dado real, não benchmark real?
2. Aprova o **braço B** (supor mesma posição por repetição, rotulado condicional)?
3. Aprova o **braço C** (reamostragem logarítmica só no harness)?
4. Posso executar o braço A (e a referência física) já, sem esperar B e C?
5. Aprova guardar no repositório só o manifesto de hashes (sem dados, por falta de licença)?
