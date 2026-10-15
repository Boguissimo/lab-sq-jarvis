# Ideação — 003-000-jv-v02-honestidade-e-seguranca (incremento JV-V02)

> **Projeto**: lab-sq-jarvis | **Peso**: Code | **Superfície crítica**: sim | **Data**: 2026-10-15
> **Status**: aprovada pelo desenvolvedor em 2026-10-15 (peso Code; superfície crítica: sim)
> **Marco**: 1 (Protótipo técnico). **Features atravessadas**: F002, F005, F006, F007 completas; F003 (configurações e critérios) — feature map v4.

## Contexto

O JV-V01 mostrou o caminho feliz: o Jarvis acerta quando os dados são bons e a hipótese é correta. O
JV-V02 mostra o que torna a ferramenta confiável: **saber quando não concluir**. Entrega os casos de
controle que exigem recusa, ressalva ou "nada a alterar", as regras de segurança do equipamento, uma
etapa de calibração simulada e o histórico de configurações com reversão honesta.

## Decisões Tomadas

| Decisão | Fundamentação | Alternativas descartadas |
| --- | --- | --- |
| Um único incremento, organizado em **três blocos testáveis separadamente**: (1) casos e honestidade, (2) regras SEG, (3) calibração simulada e configuração/reversão | mantém o JV-V02 do feature map; cada bloco tem teste e roteiro G3 próprios | dividir em V02a/V02b; reduzir escopo |
| Arquivo de ajuste do PC-Tool (antes/depois) guardado como **arquivo opaco** por hash, sem ler o conteúdo; nos casos simulados, arquivos de exemplo | JV-D039: o arquivo é registro e restauração, não conferência; leitura é F019 | só registro por valores |
| Etapa de calibração simulada = **alinhamento de atrasos tipo ATM**: conjunto de ajustes de atraso avaliado contra um objetivo, sem atribuição causal a um ajuste isolado | exemplo da proposta (seção 4); JV-D031; PT-11 | conjunto genérico de filtros de EQ |
| Casos de controle conforme a tabela da seção 7.1 da proposta: REF-001-B (realista) e N1 a N5 | JV-D016, D023, D024, D030, D035 | — |
| Resultado `comprometida` só para teste de diagnóstico (uma variável); etapa de calibração tem resultado próprio (`objetivo atingido`, `parcial`, `não atingido`, `inconclusivo`) | JV-D024 restrita por JV-D031 | mesmo vocabulário para os dois |
| Regras SEG-01 a SEG-13 implementadas como funções testáveis; resultado por regra `aprovada`, `bloqueada` ou `não verificável`; valores provisórios exibidos como provisórios | `regras-de-seguranca.md` v0.4.0; JV-D032 (aprovação não verifica) | só as regras do teste de polaridade |
| Configuração com níveis `declarada` e `arquivada` no V02; `coerente` (medição de controle) só quando houver medição real, no JV-V04 | JV-D034; caso simulado não tem DSP | implementar `coerente` com dados simulados |
| Reversão: receita inversa só com todos os valores anteriores registrados; conjunto exige arquivo "antes" ou todos os parâmetros; senão "reversão não garantida" e o que falta | JV-D040 | sempre mostrar receita |
| Modo calibração passa a existir apenas como **etapa simulada** dentro de uma sessão de investigação; o modo calibração completo continua para o JV-V04 | evita antecipar o ciclo do calibrador real | ativar o modo calibração completo |
| Aviso fixo de dados simulados, explicações por regras (sem IA) e limiares provisórios mantidos | JV-D025, JV-D042 | — |

## Dúvidas Resolvidas

| Pergunta | Resolução |
| --- | --- |
| O V02 precisa do formato real do REW? | Não. Continua o formato de texto do V01; confirmação com arquivo real fica para o JV-V04 |
| Os novos casos reaproveitam o gerador do V01? | Sim: o gerador determinístico ganha variantes (ruído, reflexão, atraso, ganho, ausência de referência temporal), mantendo INV-006 (mesmas entradas, mesmos resultados) |

## Síntese

- **Nome canônico**: JV-V02 — Honestidade e segurança.
- **Definição**: o Jarvis passa a recusar, ressalvar ou dizer "nada a alterar" quando os dados não
  sustentam uma conclusão, a aplicar as regras de segurança do equipamento e a registrar
  configurações com reversão honesta.
- **Escopo**:
  - *Bloco 1 — casos e honestidade*: REF-001-B (incerteza maior declarada); N1 (vale por reflexão:
    não propor polaridade primeiro, não recomendar reforço); N2 (ruído alto: "não dá para concluir",
    no máximo `inconclusiva`); N3 (ganho extra no "depois": `comprometida`, hipótese não refutada);
    N4 (sem referência temporal comum: recusar fase e soma prevista, trabalhar só com magnitude);
    N5 (sem problema: "nada a alterar" com justificativa); interface mostrando cada resultado com
    explicação do que falta.
  - *Bloco 2 — regras SEG*: classificação sensível/não sensível; SEG-01 a SEG-13 com resultado por
    regra; recomendação nunca apresentada como segura quando há regra bloqueada ou não verificável;
    limitações da seção 0 junto de cada recomendação sensível.
  - *Bloco 3 — calibração simulada e configuração*: etapa de calibração tipo ATM com objetivo,
    limites informados (SEG-13), resultado sem atribuição causal; configuração declarada/arquivada
    com arquivo opaco por hash; sugestão de nome para o arquivo; reversão por arquivo "antes" ou
    receita inversa completa, senão "reversão não garantida".
- **Fora do escopo**: IA (JV-V03); aceite do Marco 1 PT-01 a PT-11 completo (JV-V03); medições reais,
  formato real do REW e nível `coerente` (JV-V04); leitura do arquivo do PC-Tool (F019); modo
  calibração completo (JV-V04); receita real para o PC-Tool (JV-V05).

## Obrigações da Superfície Crítica

| Pergunta | Resposta |
| --- | --- |
| Política aplicável | P1 a P7 da constituição v0.4.0; `regras-de-seguranca.md` v0.4.0 (SEG-01 a SEG-13) |
| O incremento recomenda algo que afete potência, excursão, corte ou ganho? | Pode simular recomendações sensíveis nos casos de teste das regras SEG, sempre marcadas como simuladas; sem dado confirmado do equipamento, a recomendação fica **bloqueada** ou **não verificável** (SEG-12) |
| Como se evita parecer orientação real? | aviso fixo na janela; rótulo "simulado"; texto lembrando o limite de generalização (JV-D025); nenhuma receita sensível exibida como segura |
| Como se protege a cadeia? | originais e arquivos por hash; só inserção; previsão antes do "depois"; rotina de integridade estendida às novas tabelas |
| Valores provisórios | fator 2 × Fs, +1,5 dB, +3/+6 dB e demais valores `provisório` aparecem como tal na própria recomendação |
| Aprovação verifica? | Não (JV-D032): aprovação de nível B autoriza o ato; não transforma condição desconhecida em verificada |
