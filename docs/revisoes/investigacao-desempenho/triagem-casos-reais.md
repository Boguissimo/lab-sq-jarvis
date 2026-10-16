# Investigação de desempenho — triagem de casos reais (1ª entrega)

> **Exploratória.** Sem alteração de spec, limiares, algoritmos ou arquitetura; sem merge na `main`. Nada aqui é validação do Jarvis: nenhum caso foi processado ainda.
> Data: 2026-10-16. Autor: agente (Princípio VIII: o agente propõe, o desenvolvedor decide).

## 1. Limite desta triagem (leia primeiro)
- Este ambiente só alcança o repositório do GitHub da sessão. Fóruns, Zenodo e o site do REW são **bloqueados** (`connect_rejected`). Só consegui **resumos de buscas**; **não abri nenhuma página nem baixei nenhum arquivo**.
- Por isso, "arquivos disponíveis" abaixo é o que os resumos sugerem, marcado como **não verificado**. Nenhum diagnóstico foi lido na fonte original, e nenhuma autoridade de autor foi checada além do que o resumo mostra.
- Não achei, nem sei se existe publicamente, um caso de áudio automotivo com **exportação REW em texto + diagnóstico fundamentado + antes/depois**. Os resumos das buscas não mostraram nenhum. Isto é um achado: o material público mais comum é guia de método e discussão com imagens de gráficos, não dado bruto.

## 2. Candidatos (5), sem inflar o que não foi verificado
Classes: **R** = medição real com dado bruto verificado; **E** = estudo exploratório (real, mas sem dado ou sem diagnóstico confiável); **Q** = só referência qualitativa (não serve de benchmark).

| # | Candidato (fonte) | Contexto | Arquivos (não verificado) | Diagnóstico documentado | Evidência / autoridade | Núcleo atual processa? | Classe proposta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [Gearspace — "initial rew measurements for basement studio"](https://gearspace.com/threads/initial-rew-measurements-for-basement-studio.1374577/) | sala de estúdio, UMIK-1 | `.mdat` do REW anexado (segundo o resumo) | nulo em 125 Hz atribuído a reflexão do piso; pico modal+SBIR em 70–80 Hz; nulo em 1 kHz perguntado | resposta de um usuário; autoridade desconhecida; sem intervenção nem "depois" | **Parcial.** Uma só resposta (sem vias individuais): o `.mdat` não é lido; após exportar texto, só `vales_individuais` (200 Hz–10 kHz) se aplicaria, e o nulo de 125 Hz fica fora dessa faixa | **E** |
| 2 | [DIYMobileAudio — "REW offline measurement - timing reference help"](https://www.diymobileaudio.com/threads/rew-offline-measurement-timing-reference-help.466053/) | **automotivo**, REW | possíveis anexos (não verificado) | distâncias "a pés" de diferença entre medições; sugestão de usar loopback/sinal direto no DSP | discussão técnica de usuários; sem "antes/depois" confirmado | **Não pelos dados.** O Jarvis trata a referência temporal como **declarada**, não a infere do arquivo; não detectaria esse erro | **E** (interessa ao SC de referência temporal) |
| 3 | [Audioholics — "Fluance Signature Series Speakers Preview"](https://forums.audioholics.com/forums/goto/post?id=1123676) | caixa doméstica 3 vias | gráficos (imagens, provável) | gráfico com polaridade invertida mostra dip ≈ 1 300 Hz; um moderador **discorda** da causa e aponta o cruzamento woofer–médio | **disputado**: exemplo de por que não presumir o especialista correto | Não: sem dado numérico verificado | **Q** (descartado como benchmark) |
| 4 | [Audioholics — "MBOWI 3-Way Phase and Measurement Question"](https://forums.audioholics.com/forums/threads/mbowi-3-way-phase-and-measurement-question.103723/post-1354651) | caixa doméstica 3 vias | gráficos (provável) | driver fora de fase gera nulos nos cruzamentos | opiniões de usuários; sem dado | Não | **Q** (descartado) |
| 5 | [Zenodo 12806684](https://zenodo.org/records/12806684) — respostas ao impulso de **6 alto-falantes de um carro** (2024) | **automotivo real**, dado bruto público (segundo o resumo) | respostas ao impulso (não verificado) | **nenhum** (é um conjunto de dados, sem problema diagnosticado) | fonte acadêmica/depósito; licença não confirmada | **Sim, com conversão fora do produto:** resposta ao impulso → resposta em frequência (FFT), feita só no harness | **E** (controle negativo em dado real: qualidade e falsos positivos) |

Menções sem uso como caso: CAVEMOVE (gravado com REW; [arXiv 2508.19691](https://arxiv.org/pdf/2508.19691)), IR64-CAR (microfone esférico; sem diagnóstico) e os guias de método ([BestCarAudio](https://www.bestcaraudio.com/question-of-the-month-main-speaker-to-subwoofer-polarity/), [Deer Creek](https://deercreekaudio.com/blogs/tech-blogs/subwoofer-integration-take-your-stereo-to-the-next-level), [miniDSP](https://www.minidsp.com/applications/subwoofer-tuning/sub-integration-rew)). Guias descrevem o procedimento correto (inverter a polaridade e manter a que dá soma aditiva; atraso e polaridade juntos): servem de **expectativa de método**, não de caso.

## 3. Conclusão da triagem
- **Nenhum candidato atinge a classe R** (medição real + dado bruto verificado + diagnóstico fundamentado + antes/depois) com o que consegui ver daqui.
- Os melhores usos honestos são: (5) como **controle negativo em dado automotivo real**; (1) como **estudo exploratório** de reflexão/nulo em dado real, se o `.mdat` for exportado; (2) para discutir o limite "referência temporal é declarada".
- Obstáculos que podem ser de **dados**, não do Jarvis: falta de dado bruto, de "depois" e de diagnóstico verificado.
- Obstáculos que seriam do **Jarvis** (previstos pela leitura do código, ainda não medidos): o núcleo exige três arquivos (via A, via B e soma) e foca em polaridade/atraso/cruzamento entre duas vias; casos de uma única resposta, de sub ou de sala só exercitam parte das regras. Isso é um **escopo declarado do V02**, não uma falha.

## 4. Plano experimental (para quando houver dados)
1. **Cegamento:** o diagnóstico de referência vai para `referencias/<caso>.json` e seu SHA-256 é gravado **antes** da execução; o executor não abre esse arquivo.
2. **Execução independente da interface**, pelo `Servico` (mesmo caminho do produto) e pelas funções de `calculos`, com a conversão de formato (ex.: `.mdat`→texto, impulso→frequência) feita **só no harness**, sem alterar o produto.
3. **Registro por caso:** origem e confiabilidade; dados presentes e ausentes; diagnóstico de referência × produzido; acertos, divergências, falsos positivos/negativos; abstenções corretas; e separação **falha de implementação × limite do algoritmo × insuficiência do dado**.
4. **Benchmark:** só quando a métrica for equivalente (medição, diagnóstico, eficácia do ajuste). O REW não emite diagnóstico; um comparador por busca de polaridade/atraso (conceito da ferramenta de alinhamento) seria **meu código**, não o REW, e será rotulado assim.
5. **Classes nunca misturadas** nos totais: R (real), I (sintético inspirado em caso real, p. ex. nulo de reflexão por c/(2Δd)) e S (puramente sintético). Nada de I ou S entra como "validação real".

## 5. O que preciso de você (decisões / ações)
1. **Acesso aos dados.** Escolha uma:
   - (a) liberar domínios no ambiente (Network access → Allowed domains): `zenodo.org`, `gearspace.com`, `www.diymobileaudio.com`, `forums.audioholics.com`, `www.avnirvana.com`; ou
   - (b) você baixar os anexos que quiser e colocá-los em `validacao/casos/<id>/` no repositório (pasta que eu criaria).
2. **Casos 1 e 5:** autoriza usar exportações de texto/conversão de impulso no harness (sem mexer no produto)?
3. Se nenhum caso R aparecer, aceita fechar a primeira fase com **estudos exploratórios + controles negativos**, declarando que ainda não há validação real?

Nada foi executado nem commitado deste arquivo; aguardo sua decisão para commit.
