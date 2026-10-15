# Constituição do Projeto — lab-sq-jarvis (Lab SQ Jarvis)

> **Versão**: 0.1.0 | **Projeto**: lab-sq-jarvis | **Namespace**: `JV` | **Data**: 2026-10-15
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

---

## Princípios do Projeto

### P1. Cadeia de conhecimento explícita (NÃO-NEGOCIÁVEL)

Todo registro produzido ou guardado pelo sistema pertence a exatamente um tipo da cadeia
**medição → cálculo → indício → hipótese → recomendação → experimento → conclusão → decisão**
e aponta para os registros de que deriva. Estimativas exploratórias (P3) são um tipo lateral,
fora da cadeia de validação. Nenhum tipo é promovido a outro sem passar pelos elos intermediários:
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

> **Critério de verificação**: um verificador automático classifica cada valor numérico de cada
> resposta da IA como (a) referência a um cálculo registrado ou (b) estimativa exploratória
> marcada; resposta com valor que não se enquadra em (a) ou (b) é recusada. Nenhuma recomendação
> tem previsão cuja origem seja estimativa não conferida.

### P4. Segurança do equipamento antes do resultado (NÃO-NEGOCIÁVEL)

Toda recomendação passa pelas regras de `regras-de-seguranca.md` antes de ser mostrada. Recomendação
que afete **potência, excursão, frequência de corte ou ganho** é classificada como sensível e só
pode ser aplicada após aprovação de nível B do desenvolvedor (ato nomeado). Quando faltam dados
confirmados para verificar uma regra, a recomendação é bloqueada ou marcada “não verificável” —
nunca presumida segura.

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
“depois” a previsão quantitativa (por cálculo) e o critério de aceite, e termina em veredito
`confirmada`, `refutada` ou `inconclusiva`.

> **Critério de verificação**: todo experimento tem previsão e critério com data anterior à da
> primeira medição “depois”; nenhum experimento altera mais de uma variável.

### P7. Incerteza e limitação instrumental declaradas

Todo veredito e toda conclusão informam a incerteza considerada (repetibilidade, relação
sinal-ruído, calibração do microfone, posição) e as limitações conhecidas. Medição que não passa na
verificação de qualidade não sustenta conclusão.

> **Critério de verificação**: todo veredito tem campo de incerteza preenchido; teste com medição
> degradada confirma que o veredito vira `inconclusiva`.

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

### P13. Operação simples

O desenvolvedor não programa. A aplicação abre com dois cliques no Windows; erros aparecem em
linguagem simples; termos técnicos são explicados na primeira ocorrência.

> **Critério de verificação**: roteiro G3 de abertura e uso executado pelo desenvolvedor sem
> terminal.

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
