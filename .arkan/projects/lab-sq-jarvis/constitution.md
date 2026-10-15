# Constituição do Projeto — lab-sq-jarvis (Lab SQ Jarvis)

> **Versão**: 0.2.0 | **Projeto**: lab-sq-jarvis | **Namespace**: `JV` | **Data**: 2026-10-15 (revisão 2)
> **Estado**: **proposta — aguardando ratificação do desenvolvedor (G3)**. Enquanto não ratificada,
> nenhuma feature passa de `/arkan.ideacao`.

## Arkan Core

Os princípios operacionais do Arkan (I a VIII) vivem em **`.arkan/memory/constitution.md`**
e valem para todos os projetos deste repositório. Eles **não são copiados aqui** e
**não se editam**: emendá-los exige aprovação explícita do mantenedor do Arkan e um registro
na tabela de emendas de lá.

Este arquivo contém apenas o que é do projeto.

---

## Propósito

O Lab SQ Jarvis é um **assistente inteligente de calibração** de áudio automotivo SQ/SQPL. Ele usa
medições acústicas, informações dos equipamentos e fundamentos de engenharia para diagnosticar
problemas, formular hipóteses, recomendar experimentos de ajuste controlados e verificar os
resultados — trabalhando junto com o REW e o HELIX DSP PC-Tool.

**Não é um novo REW** e não substitui o PC-Tool: não mede, não equaliza automaticamente e não
controla o DSP. Sua inteligência está no diagnóstico, no método experimental e no registro.

**Primeiro, uma ferramenta pessoal** (JV-D017): servir ao desenvolvedor para ajustar o próprio
sistema, entender o que está fazendo e acumular aprendizado entre sessões — fazendo, até onde
possível, o que faria um calibrador experiente, sabendo que a referência sonora é individual. O
potencial comercial só é avaliado depois da versão pessoal pronta.

Siglas usadas neste arquivo: **REW** — Room EQ Wizard (programa de medição acústica); **DSP** —
processador digital de sinais; **EQ** — equalização; **IA** — inteligência artificial;
**SEG** — regra de segurança do projeto; **G1/G2/G3** — gates determinístico, analítico e humano
(P12).

---

## Princípios do Projeto

### P1. Cadeia de conhecimento explícita (NÃO-NEGOCIÁVEL)

Todo registro produzido ou guardado pelo sistema pertence a exatamente um tipo da cadeia
**medição → cálculo → indício → hipótese → recomendação → experimento → conclusão → decisão**
e aponta para os registros de que deriva. Dois tipos laterais completam a cadeia: a **percepção**
do desenvolvedor, registrada antes e depois de cada teste (JV-D021), que motiva a sessão e
integra o experimento; e as **estimativas exploratórias** da IA (P3), fora da cadeia de validação. Nenhum tipo é promovido a outro sem passar pelos elos intermediários:
indício não vira conclusão, hipótese não vira recomendação sem indício, conclusão não existe sem
experimento.

> **Critério de verificação**: uma rotina de integridade percorre o banco e confirma que 100% dos
> registros têm tipo válido e referências para registros existentes do tipo anterior permitido.

### P2. Medições e configurações originais são imutáveis (NÃO-NEGOCIÁVEL)

Arquivos importados (medições do REW, arquivos de ajuste do PC-Tool, calibrações de microfone)
são guardados como recebidos e identificados pelo hash SHA-256. O sistema nunca os altera nem os
substitui; correções e reprocessamentos geram registros novos que apontam para o original.
Configurações anteriores do DSP nunca se perdem: cada estado é um snapshot próprio.

> **Critério de verificação**: o hash de cada original confere a qualquer momento; um teste
> automatizado tenta sobrescrever um original e verifica que a operação é recusada e registrada.

### P3. Cálculo determinístico para validar e recomendar; IA estima só de forma identificada (NÃO-NEGOCIÁVEL)

Grandezas físicas e processamento de sinais usados em validação, previsão de efeito,
veredito de experimento ou recomendação técnica são produzidos ou conferidos por rotinas
determinísticas, versionadas e rastreáveis (algoritmo, versão, parâmetros e entradas por hash).
A IA pode fazer **estimativas exploratórias**, desde que identificadas como tais; uma estimativa
exploratória só sustenta recomendação depois de conferida por cálculo determinístico.

Um número correto pode sustentar uma explicação errada: a explicação da IA é sempre
interpretação, e decisões de diagnóstico se apoiam nos indícios determinísticos (JV-D026).

> **Critério de verificação**: um verificador automático classifica cada valor numérico de cada
> resposta da IA como (a) referência a um cálculo registrado **e coerente com ele em grandeza,
> unidade, canal, medição e faixa de frequência** ou (b) estimativa exploratória marcada; resposta
> com valor fora de (a) ou (b) é recusada. Nenhuma recomendação tem previsão cuja origem seja
> estimativa não conferida.

### P4. Reduzir o risco ao equipamento antes de buscar o resultado (NÃO-NEGOCIÁVEL)

Toda recomendação passa pelas regras de `regras-de-seguranca.md` antes de ser mostrada. As regras
**reduzem o risco dentro das condições conhecidas e dos dados cadastrados; não garantem segurança
absoluta** (JV-D022). Toda recomendação que afete **potência, excursão, frequência de corte ou
ganho** é sensível — inclusive reduções — e só é aplicada após aprovação de nível B do
desenvolvedor (ato nomeado). As que aumentam o risco exigem, além disso, dados confirmados; sem
eles, são bloqueadas. Nada é presumido seguro por falta de informação.

> **Critério de verificação**: suíte de testes de segurança com recomendações proibidas e limítrofes
> bloqueia 100% das proibidas; nenhuma recomendação sensível é exibida sem a marcação e o pedido
> de aprovação.

### P5. Nada é inventado: equipamentos e características só com fonte

Características técnicas (potência, Fs, Xmax, limites de corte, sensibilidade, posições) entram no
sistema com fonte e estado: `planejado`, `informado` ou `confirmado`. Só dados `confirmados`
alimentam análises e regras de segurança. Componentes planejados ou ainda não adquiridos nunca são
tratados como instalados.

> **Critério de verificação**: toda especificação de equipamento tem fonte e estado; teste
> automatizado confirma que análise ou regra que dependa de dado não confirmado é recusada ou
> marcada.

### P6. Um experimento, uma variável, previsão antes

Toda recomendação de ajuste é um experimento: altera uma única variável, registra antes da medição
“depois” a previsão quantitativa (por cálculo), o critério de aceite e a percepção “antes”, e termina
em veredito `confirmada`, `refutada`, `inconclusiva` ou `comprometida`. **Comprometida** significa
que o protocolo foi violado (por exemplo, mais de uma variável mudou): o resultado não confirma nem
refuta a hipótese, e o teste é refeito (JV-D024).

> **Critério de verificação**: todo experimento tem previsão, critério e percepção “antes” com data
> anterior à da primeira medição “depois”; experimento com mais de uma variável alterada recebe
> veredito `comprometida`.

### P7. Incerteza e limitação instrumental declaradas

Todo veredito e toda conclusão informam a incerteza considerada (repetibilidade, relação
sinal-ruído, calibração do microfone, posição) e as limitações conhecidas. Medição que não passa na
verificação de qualidade não sustenta conclusão.

Comparar fase, estimar atraso relativo ou prever a soma de medições separadas exige **referência
temporal compatível** entre elas (JV-D023); sem isso, só análises de magnitude são feitas e o
sistema diz o que falta. Resultados validados em casos simulados não se generalizam
automaticamente para o carro (JV-D025).

> **Critério de verificação**: todo veredito tem campo de incerteza preenchido; teste com medição
> degradada confirma que o veredito vira `inconclusiva`; teste com medições sem referência temporal
> comum confirma que fase e soma prevista são recusadas.

### P8. Critérios técnicos só mudam por decisão explícita; o histórico ensina sem alterar critérios

Curvas-alvo, tolerâncias, limites e regras de segurança são dados versionados. Só mudam por
decisão registrada do desenvolvedor, com versão e justificativa. O contexto aprendido com o
histórico (comportamentos recorrentes do veículo, preferências, efeitos de experimentos) é guardado
como observação com proveniência e pode influenciar a ordem das hipóteses, nunca o critério de
aceite.

> **Critério de verificação**: toda alteração de critério tem uma decisão associada; teste confirma
> que o histórico não altera nenhum valor de critério.

### P9. IA substituível, com transparência e controle sobre os dados enviados

Nenhuma função depende de um fornecedor específico de IA. A quantidade e o tipo de dados enviados a
um modelo são determinados pela necessidade técnica de cada tarefa, declarados antes do envio e
controláveis pelo desenvolvedor; por padrão, envia-se o mínimo necessário. Todo envio é registrado
(provedor, finalidade, categorias de dado, volume).

> **Critério de verificação**: trocar o provedor não altera cálculos nem registros (testes com
> provedor simulado e com ao menos um provedor real); 100% dos envios constam do registro de
> transparência.

### P10. Não reinventar REW nem PC-Tool

Medição, equalização automática e controle do DSP pertencem às ferramentas existentes. O Jarvis
lê, interpreta, planeja e registra. A integração com o HELIX é assistida: o sistema gera a receita
de alteração e o desenvolvedor a aplica no PC-Tool.

> **Critério de verificação**: nenhuma feature do feature map gera sinal de medição, escreve
> parâmetros no DSP ou implementa EQ automático sem decisão `JV-D` que o autorize.

### P11. Uma fonte canônica por tipo de estado do projeto

| Estado | Fonte canônica |
| --- | --- |
| Princípios | este arquivo |
| Decisões (`JV-D`) | `decisoes.md` |
| Fontes (`JV-S`) | `01-discovery/fontes.md` |
| Regras de segurança (`SEG-`) | `regras-de-seguranca.md` |
| Escopo e estado das features | `02-proposal/feature-map.md` |
| Critérios de aceitação dos marcos (`PT`, `VP`) | `02-proposal/proposta-consolidada.md` |
| Pendências executáveis (`JV-T`) | `06-planning/tasks.md` da feature ativa |

> **Critério de verificação**: nenhum outro documento mantém lista própria desses estados; os demais
> apenas apontam.

### P12. Três gates

| Gate | Natureza | Autoridade |
| --- | --- | --- |
| **G1 — determinístico** | cálculos, integridade da cadeia, segurança, imutabilidade | testes automatizados |
| **G2 — analítico** | coerência técnica de diagnóstico e recomendação | agente, com o agente de domínio `engenharia-acustica-sq` |
| **G3 — humano** | utilidade, escuta, aprovação de alteração e de critério | desenvolvedor |

> **Critério de verificação**: cada task concluída cita o gate e a evidência.

### P13. Sessão guiada; rastreabilidade por trás

O desenvolvedor não programa. Abrir com dois cliques é necessário, mas não basta: o uso acontece
num fluxo guiado — **o que estou percebendo → o que preciso medir → o que os dados sugerem → qual
teste fazer → o que mudou** (JV-D020). A cadeia de conhecimento é montada pelo sistema por trás do
fluxo; o usuário não preenche registros à mão nem navega por telas avulsas. Erros aparecem em
linguagem simples; termos técnicos e siglas são explicados na primeira ocorrência.

> **Critério de verificação**: roteiro G3 em que o desenvolvedor faz uma sessão completa sem
> terminal e sem sair do fluxo, exceto para usar o REW e o PC-Tool; a rotina de integridade (P1)
> passa sobre os registros gerados.

### P14. Pessoal primeiro

Até a versão pessoal estar pronta (Marco 2), nenhuma feature trata de assinatura, cobrança,
múltiplos usuários, oficinas ou nuvem obrigatória (JV-D017).

> **Critério de verificação**: nenhuma feature anterior ao fim do Marco 2 no `feature-map.md` tem
> esse escopo.

---

## Decisões de contexto

| Assunto | Decisão deste projeto |
| --- | --- |
| Idioma do código-fonte | identificadores em inglês ou português a definir no primeiro `/arkan.plan`; textos para o usuário em PT-BR |
| Idioma de artefatos e respostas | definido pelo Princípio V do núcleo |
| Estrutura de repositório | repositório único, independente |
| Estratégia de testes | testes de cálculo com resposta conhecida escritos antes ou junto da implementação; casos acústicos de referência com verdade construída |
| Política de publicação | branch de trabalho `lab-sq-jarvis/<feature>`; integração em `main` só com aprovação do desenvolvedor |
| Dados sensíveis | nenhum dado pessoal relevante; chaves de API de IA guardadas no cofre de credenciais do Windows, nunca no repositório |
| Superfície(s) crítica(s) | **segurança do equipamento** (potência, excursão, frequência de corte, ganho) e **integridade da cadeia de conhecimento** (medição original, cálculo, recomendação) |

---

## Identificadores do projeto (governança do desenvolvimento)

| Prefixo | Significado |
| --- | --- |
| `JV-D###` | decisão |
| `JV-S###` | fonte |
| `JV-T###` | task |
| `SEG-##` | regra de segurança |

Os registros que a **aplicação** produz em uso (medições, cálculos, indícios etc.) têm
identificadores próprios, definidos no modelo de dados — não se confundem com estes.

---

## Histórico de Emendas

| Versão | Data | Tipo | Descrição |
| --- | --- | --- | --- |
| 0.1.0 | 2026-10-15 | — | Proposta inicial, derivada do diagnóstico e das decisões de 2026-10-15; aguardando ratificação |
| 0.2.0 | 2026-10-15 | Minor | Revisão 2: propósito pessoal (JV-D017); percepção na cadeia (JV-D021); P3 com conferência de grandeza, unidade e canal (JV-D026); P4 como redução de risco, sem garantia (JV-D022); P6 com veredito `comprometida` (JV-D024); P7 com referência temporal e limite de generalização (JV-D023, JV-D025); P13 reescrito como sessão guiada (JV-D020); P14 novo. Aguardando ratificação |
