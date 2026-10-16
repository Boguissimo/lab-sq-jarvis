# Protocolo de campo N2 — Ford Focus: polaridade e atraso conhecidos, antes/depois

> **PROPOSTA. NÃO EXECUTAR sem autorização expressa de Fabrício.** Nada neste documento foi iniciado. Não altera `src/`, spec, limiares nem arquitetura. 2026-10-16.
> **O que é N2 aqui:** a falha é **aplicada fisicamente no DSP** (verdade conhecida por Fabrício) e a soma é **medida**, não calculada. É o primeiro passo que separa diagnóstico de consistência matemática. **O que ainda não é:** defeito natural desconhecido; um único carro/uma sessão; falha provocada por quem conhece a resposta.
> **Equipamento:** `JV-D012` exige confirmar o equipamento real antes de qualquer análise. Este protocolo **não presume** microfone, interface, DSP ou software; as lacunas estão marcadas **[CONFIRMAR]**.

## 1. Pergunta e hipóteses (fixadas antes)
Dado um par de vias admissível (banda operacional ≥ 1 oitava), o protótipo `diagnostico_previsao2.py` (com `C_ADM` = 1,0 e a margem escolhida **antes** da sessão) identifica, a partir das vias medidas isoladamente e da soma medida: (H1) a inversão de polaridade da via B; (H2) um atraso conhecido de B (1,00 ms e 0,25 ms; 0,10 ms opcional); e (H3) o estado normal nos controles. Resultado negativo (abstenção ou erro) é resultado válido e será reportado.

## 2. Instrumentação necessária [CONFIRMAR cada item]
| Item | Requisito | Estado |
| --- | --- | --- |
| Microfone de medição | calibrado, em tripé fixo, posição marcada e fotografada (altura, distância, ângulo) | [CONFIRMAR modelo e arquivo de calibração; o projeto proíbe presumir o UMIK-1] |
| Interface de áudio | com **referência temporal por loopback físico** independente do DSP (ou referência acústica do REW); mesma taxa de amostragem em todas as medições | [CONFIRMAR topologia: o loopback não pode passar pelo DSP que terá o atraso alterado] |
| Software de medição | REW (versão registrada); varredura, nível e duração fixos; exportar **texto com fase** e, se possível, a resposta ao impulso; guardar os `.mdat` | [CONFIRMAR versão e configurações] |
| DSP e software de ajuste | acesso à **polaridade** e ao **atraso** do canal da via B; resolução e unidade do atraso conhecidas | [CONFIRMAR modelo; o projeto menciona HELIX/PC-Tool sem confirmação de aquisição] |
| Termômetro da cabine | registrar a temperatura a cada bloco (a deriva do tempo de chegada acompanha a temperatura: ~0,43 amostra/°C a 96 kHz em 0,9 m, medido no Passat) | [CONFIRMAR] |
| Ruído e condições | motor desligado (ou condição constante registrada), portas/janelas fixas, ocupantes nas mesmas posições, sem ar-condicionado variando | registrar |

## 3. Escolha do par (portão de admissibilidade)
Escolher **um par com banda operacional comum ≥ 1 oitava, em baixa/média frequência**, por exemplo subwoofer + midbass/woofer (≈ 40–150 Hz) ou woofer + médio (≈ 200–500 Hz) **conforme o cadastro confirmado**. **Evitar par tweeter + médio (2–10 kHz) nesta primeira sessão:** nos dados do Passat a deriva já derruba a previsão nessa banda. Declarar a banda do par e as bandas operacionais das duas vias **antes** de medir (entram no portão).

## 4. Segurança e restauração da configuração (SEG-08, SEG-11, JV-D040)
1. **Só polaridade e atraso** de uma única via são alterados (classe "não sensível"). **Proibido** mexer em ganho, EQ, passa-altas/crossover ou qualquer outro parâmetro; **uma mudança por vez**.
2. **Antes de começar:** salvar o arquivo de configuração do DSP, calcular o **SHA-256** e anotar (ou fotografar) os valores atuais de polaridade e atraso de todos os canais (JV-D040: sem valor anterior registrado a reversão não é garantida). O Jarvis **não escreve no DSP** (SEG-11): quem aplica é Fabrício.
3. **SEG-08 em cada mudança:** reduzir o volume ao mínimo, aplicar a mudança com o sinal parado, retomar o volume gradualmente até o **nível de medição declarado**; usar o menor nível que dê relação sinal-ruído suficiente (SEG-09: o critério de exposição ainda não tem valor).
4. **Restaurar pelo valor registrado**, não de memória: após cada bloco de falha, voltar polaridade/atraso ao valor anotado, conferir na tela e **medir um controle** (bloco B). Critério de parada: se um controle diferir do controle anterior além do previsto pela repetibilidade (níveis > 1 dB ou fase > 10° na banda do par) ou se algo soar anormal, **parar, restaurar e investigar** (microfone movido, ganho alterado, deriva).
5. **Ao final:** recarregar o arquivo salvo, confirmar o **mesmo SHA-256** e as telas; fazer um último controle. A configuração original deve estar restaurada e comprovada **antes** de encerrar.
6. Nada é automático e nada vira recomendação do Jarvis: é um experimento de medição com verdade conhecida.

## 5. Sequência de medição (fixa; controles intercalados para medir a deriva)
Cada ponto = medir **A isolada, B isolada e A+B** (3 varreduras cada, microfone sem tocar), mesma referência temporal, mesmo nível, registrando horário e temperatura.
| Bloco | Estado do DSP (verdade; só Fabrício conhece o registro até a análise) |
| --- | --- |
| B0 | normal (controle inicial) |
| F1 | polaridade de B invertida |
| B1 | normal (restaurado) |
| F2 | atraso de B = 1,00 ms |
| B2 | normal |
| F3 | atraso de B = 0,25 ms |
| B3 | normal |
| (F4 opcional) | atraso de B = 0,10 ms, seguido de B4 normal |
- Para o **ensaio cego**: os arquivos recebem **ids neutros** (sem nomes como "polaridade"); Fabrício guarda a tabela id → estado e o **SHA-256 dessa tabela é registrado antes** de qualquer arquivo ser entregue ao analista; a tabela só é revelada após a gravação das previsões. (O cegamento é entre protótipo e rótulos; Claude conhece o desenho.)
- Registrar para cada arquivo: id, bloco, horário, temperatura, nível, configuração do REW, valor de atraso e unidade/resolução do DSP, estado da polaridade.

## 6. Análise (pré-registro específico antes da sessão)
Será escrito um pré-registro N2 **antes** da sessão, fixando: `C_ADM` = 1,0; a margem (constante 0,2 **ou** a regra do controle do próprio sistema, se a rodada 3 for aprovada e executada antes); o portão por banda; as métricas (cobertura, certas, omissões, identificações erradas, falsos alarmes nos controles B0–B3, abstenções); e a regra de que **nenhum critério é ajustado após ver os resultados**. As componentes de incerteza (a) variabilidade e (c) discrepância do modelo serão **estimadas com este mesmo conjunto** (3 repetições + soma física), o que também destrava a margem do carro.

## 7. Limites declarados
Um carro, uma sessão, uma via B; falhas provocadas e ideais (inversão exata; atraso na resolução do DSP); o analista conhece o desenho; não testa defeitos naturais nem a utilidade para o ouvinte; não valida o V02.

## 8. Autorização
Este protocolo **só será executado depois de aprovação expressa de Fabrício** e da confirmação do equipamento. Até lá: nenhuma medição, nenhuma alteração de DSP.
