# Lab SQ Jarvis — Diagnóstico inicial

> **Natureza**: insumo pré-Arkan para `/arkan.projeto` (fases 01–02 em nível de projeto).
> **Não é** artefato aprovado: nenhum briefing, visão, feature map ou constituição foi ratificado.
> **Nenhuma implementação foi iniciada.**
> **Data**: 2026-10-15

> **Registro histórico preservado (2026-10-15).** Este é o diagnóstico entregue antes da criação do
> repositório, mantido como recebido pelo desenvolvedor. O estado decisório vigente está em
> [`../decisoes.md`](../decisoes.md): DA-01 a DA-04 e DA-07 aprovadas; DA-05/DA-06 aprovadas com
> ressalva (JV-D005); meta de 90% retirada (JV-D008); MVP reduzido (JV-D010); “sinal” passou a
> chamar-se “indício” (JV-D006); competição SQ não é requisito (JV-D013); equipamentos não
> confirmados não são presumidos (JV-D012).

---

## 1. Como o Arkan Core está disponível

### 1.1 O que existe

| Item | Achado |
| --- | --- |
| Forma de distribuição | Pacote extraído (não é clone do repositório de origem). `VERSAO.md`: gerado em 2026-09-30, commit de origem `281e98d39`, 143 arquivos. |
| Onde está instalado | Uma cópia por repositório: `Boguissimo/jogo-arcade` (Rygar) e `Boguissimo/arkan-fiscal`. Não há repositório do Arkan de origem acessível nesta sessão. |
| Integridade do Core | Agentes, scripts, templates, comandos e constituição-núcleo são **idênticos** nos dois repositórios. A única diferença é o fim de linha (ver 1.3). |
| Núcleo | `.arkan/memory/constitution.md` v2.3.0, princípios I–VIII (spec governa código, gate obrigatório, artefatos conclusivos, modo declarado, PT-BR, especialização por modo, independência estrutural, agente propõe/humano decide — com aprovação nível A e nível B). |
| Ponto de entrada de um sistema novo | `/arkan.projeto` → `briefing.md`, `vision.md`, `feature-map.md` aprovados. Depois, `/arkan.ideacao` para cada feature (fases 01→10, com peso Code/Doc/Config). |

### 1.2 Procedimento correto de início (conforme `README.md` e `GUIA-DE-ADOCAO.md`)

1. Repositório próprio com `git init`.
2. Copiar `.arkan/`, `.claude/`, `VERSAO.md` e anexar o `.gitignore` do pacote.
3. Preencher `.arkan/memory/stack.md` (sem deixar marcadores de exemplo).
4. `.arkan/scripts/create-project.sh --project lab-sq-jarvis --name "Lab SQ Jarvis"`.
5. Copiar `constitution-template.md` para `.arkan/projects/lab-sq-jarvis/constitution.md` e escrever os princípios do projeto (o núcleo não é copiado).
6. Apontar `projeto-default: lab-sq-jarvis` em `.arkan/config.md` (só depois do passo 4).
7. Opcional e recomendado: escrever o agente de domínio em `.arkan/agents/transversal/` e declará-lo em `agente-dominio`.
8. `/arkan.projeto` com a descrição do sistema.

### 1.3 Convenções herdadas dos projetos existentes

| Convenção | Rygar | Arkan Fiscal | Proposta para o Jarvis |
| --- | --- | --- | --- |
| Namespace de IDs | `RG-D/F/T/S/H/E/A` | `F001`, `D1…D78` | `JV-D/F/T/S/H/E/A` (governança do desenvolvimento) |
| Uma fonte canônica por tipo de estado | P11 | registro de decisões em `fiscal-profile/` | adotar (decisões, hipóteses de projeto, fontes, feature map) |
| Gates G1/G2/G3 | determinístico / analítico / humano | idem | adotar — encaixa exatamente em cálculo / interpretação / audição |
| Separação de categorias epistêmicas | fonte → hipótese → evidência → achado | detector → sinal → hipótese → achado | medição → cálculo → sinal → hipótese → recomendação → experimento → conclusão |
| Feature 001 de incorporação | — | `001-000-incorporar-arkan` | `001-000-fundacao-arkan` (peso Doc/Config) |
| Agente de domínio | não declarado | `auditoria-fiscal` | `engenharia-acustica-sq` |
| Operação por não programador | P14 (`JOGAR.bat`) | — | adotar |

### 1.4 Problemas encontrados (sem alteração do Core)

1. **No Arkan Fiscal, os portões não executam.** Os `.sh` estão gravados no repositório com CRLF; `check-prerequisites.sh` falha com `$'\r': command not found` e `set: pipefail: invalid option name`. O Rygar evitou isso com `.gitattributes` (`*.sh text eol=lf`). O Jarvis deve nascer com esse arquivo.
2. **Branch com barra muda o projeto resolvido.** `resolve_project` usa o prefixo da branch antes de `config.md`. Nesta sessão, a branch `claude/serene-curie-8e9li4` faz o Arkan resolver o projeto como `claude`. No Jarvis: branches `lab-sq-jarvis/NNN-CCC-slug` ou `--project lab-sq-jarvis` sempre.
3. **Não consigo criar um repositório novo a partir desta sessão** — só opero nos repositórios já anexados. Também não convém instalar o Jarvis dentro do repositório do Rygar: o Jarvis é independente.

---

## 2. Panorama das ferramentas existentes

> Limitação: o acesso direto aos sites dos fabricantes está bloqueado pela política de rede deste ambiente. Os dados abaixo vêm de pesquisa por mecanismo de busca (páginas oficiais, fórum do autor do REW, prêmio EISA, fóruns técnicos). O que não pôde ser confirmado em fonte primária está marcado **[a confirmar]**.

### 2.1 REW (Room EQ Wizard)

| Capacidade | Situação |
| --- | --- |
| Medição por varredura, RTA, resposta ao impulso, ETC, fase, atraso de grupo, distorção, cascata/espectrograma, médias, ferramenta de alinhamento, módulo de EQ com exportação de filtros em texto, importação/exportação em texto e WAV | consolidado |
| **API REST local** (porta 4735; documentação Swagger em `localhost:4735`; especificação OpenAPI em `/doc.json`) | linha 5.40 (betas até pelo menos o beta 108) [a confirmar: versão estável atual] |
| Leitura via API (todos os GET) | disponível **sem** licença Pro |
| Disparar varreduras via API (`POST /measure/...`) | exige **REW Pro**; RTA via API sem Pro |
| Resposta em frequência pela API | `/measurements/{id}/frequency-response`, valores em Base64 |
| Ecossistema | servidores MCP de terceiros para REW (46 e 27 ferramentas), `rew-iqc` (aprovação/reprovação), `qrew` (medição automatizada) |

**Implicação**: o Jarvis pode ler medições direto do REW (sem exportar arquivo à mão), com a importação de arquivo como caminho garantido. Automação de varreduras é opcional e depende de licença Pro.

### 2.2 HELIX DSP PC-Tool (Audiotec Fischer)

| Capacidade | Situação |
| --- | --- |
| PC-Tool 5 (5.00.08 em 2023; 5.05.01 revisou o RTA e acrescentou automação de alinhamento de curvas) | estável conhecida |
| **PC-Tool 6** — interface por fluxo de sinal; AISA (detecção e compensação de EQ, all-pass e atraso de fábrica); TuneEQ multibanda na entrada e na saída; **Tune To Target** (ajuste automático a curva-alvo, inclusive ganho); controle dinâmico de loudness; RTA integrado; cerca de 30 modelos BRAX/HELIX/MATCH desde 2018 | prêmio EISA 2025–2026 |
| AMI (interface de medição): entrada de microfone com phantom, entrada de linha, **loopback** (permite medir fase com referência elétrica), ATM (medição automática de tempo) | acessório oficial |
| Filtros de crossover: Butterworth, Bessel, Linkwitz-Riley, 6 a 42 dB/oitava | FAQ do fabricante [a confirmar no PC-Tool 6] |
| Importação de filtros do REW (“REW Generic EQ .txt”) via importação avançada | desde a v4.x [a confirmar no PC-Tool 6] |
| Arquivos de ajuste `.afpx` (v4/v5); compatibilidade v5→v6 | relatos contraditórios em fórum [a confirmar] |
| API, SDK ou protocolo público para controle por terceiros | **não encontrado** |
| Formato do arquivo de ajuste documentado | **não encontrado** |

**Implicação**: o Jarvis não deve escrever no DSP. O fluxo é “humano no circuito”: o Jarvis gera uma **receita de alteração** (o quê, onde, quanto, em que ordem, com que proteção), o usuário aplica no PC-Tool e salva o arquivo de ajuste, que o Jarvis arquiva com hash. Ler o arquivo de ajuste é possível **somente depois de inspecionar um arquivo real** (estrutura desconhecida).

### 2.3 Ferramentas complementares e concorrentes

| Ferramenta | O que faz | Relação com o Jarvis |
| --- | --- | --- |
| TuneEQ / Tune To Target (HELIX) | EQ automático rumo a uma curva-alvo | corrige magnitude; não explica causa |
| Audison bit Tune / ACCORDO | EQ, alinhamento temporal e nível automáticos (Audison) | idem, ecossistema fechado |
| Dirac Live (ex.: miniDSP C-DSP) | correção automática de sala | idem |
| Tuning Labs | software de ajuste com “IA”; a própria página trata o copiloto como plano | concorrente conceitual, sem rastreabilidade declarada |
| rePhase | projeto de filtros FIR | fora do MVP |
| Servidores MCP do REW | ligam um modelo de IA ao REW | genéricos; sem modelo do veículo, sem experimento, sem registro |
| Critérios de julgamento SQ (EMMA): imagem, palco (distância, largura, altura), precisão tonal, equilíbrio espectral, prazer auditivo, ruído | vocabulário de percepção | base do mapeamento subjetivo → objetivo [regulamento oficial a obter] |

---

## 3. Lacunas concretas — o que ninguém integra

| # | Lacuna | Por que importa | O que o Jarvis faz |
| --- | --- | --- | --- |
| O1 | Nenhuma ferramenta liga **a medição ao estado do DSP** que a produziu | sem isso, “antes e depois” é memória | cada medição referencia o snapshot do ajuste (hash) e a alteração aplicada |
| O2 | O EQ automático trata **magnitude**, não **causa** | um vale de cancelamento no crossover (atraso/polaridade) não se corrige com reforço de EQ — gasta headroom e arrisca o equipamento | separar problemas equalizáveis (fase mínima, estáveis no espaço) de não equalizáveis (excesso de fase, interferência, modos variáveis entre posições) |
| O3 | Não há **experimento controlado** | ajuste por tentativa mistura variáveis | uma variável por vez, previsão quantitativa antes, critério de aceite, veredito considerando a incerteza |
| O4 | Não há ponte **percepção ↔ medição** | queixas como “palco puxado para a esquerda” ou “voz metálica” não viram teste | mapear a queixa para regiões de frequência, mecanismos candidatos e medições que discriminam entre eles |
| O5 | Não há verificação de **coerência geometria ↔ DSP ↔ medição** | atrasos configurados vs. diferença de percurso vs. chegada medida; crossover vs. limites do alto-falante | conferências determinísticas cruzadas |
| O6 | Não há **qualidade da medição** antes do diagnóstico | relação sinal-ruído baixa, saturação, microfone mal posicionado ou sem calibração produzem falsos diagnósticos | sinalizar e bloquear conclusões sobre medição inválida |
| O7 | Não há **memória do sistema** | cada sessão recomeça do zero | histórico de experimentos, observações recorrentes e preferências, separados dos critérios técnicos |
| O8 | Não há **guarda de segurança** explícita | reforço excessivo, passa-altas de tweeter baixo demais, volume durante troca de polaridade | regras de segurança verificáveis aplicadas a toda recomendação |
| O9 | Assistentes de IA atuais ficam presos a um fornecedor | risco de dependência e custo | camada de IA substituível |

---

## 4. Arquitetura proposta

### 4.1 Visão em camadas

```text
┌───────────────────────────────────────────────────────────────┐
│ Interface (janela desktop Windows): painéis + gráficos + chat  │
└───────────────────────────┬───────────────────────────────────┘
                            │ API local (só na própria máquina)
┌───────────────────────────┴───────────────────────────────────┐
│ Orquestração da aplicação                                     │
│  ├─ Modelo do sistema (veículo, posições, canais, equipamentos,│
│  │  limites de fabricante)                                    │
│  ├─ Ingestão: REW arquivo │ REW API (leitura) │ HELIX arquivo* │
│  ├─ Motor de cálculo determinístico (funções puras, versionadas)│
│  ├─ Detectores (regras → Sinais com evidência)                │
│  ├─ Base de conhecimento de engenharia (critérios, limites,   │
│  │  percepção→mecanismo; versionada; cada item com fonte)     │
│  ├─ Gerenciador de experimentos (previsão, critério, veredito)│
│  ├─ Guardas de segurança (aplicadas a toda recomendação)      │
│  └─ Assistente de IA (adaptador de provedor + ferramentas)    │
└───────────────────────────┬───────────────────────────────────┘
┌───────────────────────────┴───────────────────────────────────┐
│ Persistência: arquivos originais imutáveis (por hash SHA-256) │
│ + banco local (metadados, registro epistêmico, diário só de   │
│ acréscimo)                                                    │
└───────────────────────────────────────────────────────────────┘
* condicionado à inspeção de um arquivo real
```

### 4.2 Modelo epistêmico (o coração do sistema)

| Tipo | Quem produz | Exemplo | Regra |
| --- | --- | --- | --- |
| **Medição (M)** | REW, importada | varredura do médio esquerdo na posição do motorista | original nunca é alterado; metadados obrigatórios (canal, posição do microfone, calibração, snapshot do DSP) |
| **Cálculo (C)** | motor determinístico | atraso relativo L–R de 0,21 ms; diferença tonal de 3,1 dB em 2–4 kHz | registra algoritmo + versão + entradas (por hash); reprodutível |
| **Sinal (S)** | detector determinístico | “vale de 12 dB em 1,9 kHz, coincidente com o crossover médio/tweeter” | sempre aponta para cálculos |
| **Hipótese (H)** | IA ou usuário | “cancelamento por diferença de fase no crossover” | cita sinais; declara o que a confirmaria ou refutaria |
| **Recomendação (R)** | IA, filtrada pelas guardas | “inverter polaridade do tweeter esquerdo, com volume reduzido” | uma variável; previsão quantitativa; passos de segurança |
| **Experimento (X)** | usuário executa | medições antes/depois + snapshot | veredito: confirmada / refutada / inconclusiva (incerteza considerada) |
| **Conclusão (A)** | Jarvis propõe, usuário ratifica | “polaridade invertida resolveu o vale; ganho de 9 dB” | só a partir de experimento |
| **Decisão (D)** | usuário | adotar a alteração no ajuste vigente; mudar um critério | critérios técnicos só mudam por decisão explícita e versionada |

A IA **não calcula**: toda grandeza numérica que aparece numa resposta precisa ter origem num cálculo registrado. Um verificador automático confere isso antes de mostrar a resposta.

### 4.3 Aprendizado sem alterar critérios em silêncio

- **Critérios** (curvas-alvo, tolerâncias, limites de segurança): dados versionados; mudam somente por decisão explícita, com versão e justificativa.
- **Contexto aprendido** (modos recorrentes do habitáculo, preferências de audição, efeitos de experimentos anteriores): registrado como observação com proveniência; pode influenciar a **ordem** das hipóteses, nunca o critério de aceite.

### 4.4 Princípios candidatos para a constituição do projeto (rascunho)

| # | Princípio | Critério de verificação |
| --- | --- | --- |
| P1 | Medição original é imutável (NÃO-NEGOCIÁVEL) | hash de cada arquivo importado confere em qualquer momento |
| P2 | Separação epistêmica (NÃO-NEGOCIÁVEL) | todo registro tem tipo M/C/S/H/R/X/A/D e referências válidas |
| P3 | Nenhum número sem origem (NÃO-NEGOCIÁVEL) | verificador rejeita resposta da IA com grandeza não rastreada |
| P4 | Cálculo determinístico, testado e versionado | mesmas entradas ⇒ mesmo resultado; suíte G1 passa |
| P5 | Segurança do equipamento antes do resultado (NÃO-NEGOCIÁVEL) | toda recomendação passa pelas guardas; teste de propriedade sem violações |
| P6 | Uma variável por experimento, com previsão prévia | todo X tem previsão e critério registrados antes da medição “depois” |
| P7 | Incerteza declarada | todo veredito informa repetibilidade/limitação instrumental |
| P8 | Critérios só mudam por decisão explícita | histórico de versões dos critérios; nenhuma alteração sem D |
| P9 | IA substituível | trocar provedor não altera cálculos nem registros; suíte de avaliação roda em mais de um provedor |
| P10 | Não reinventar REW nem PC-Tool | nenhuma feature duplica medição, EQ automático ou controle do DSP |
| P11 | Operação simples (como P14 do Rygar) | abre com dois cliques; erros em linguagem simples |
| P12 | Gates G1/G2/G3 | cada task cita gate e evidência |

### 4.5 Pilha tecnológica recomendada

| Camada | Recomendação | Motivo | Alternativas |
| --- | --- | --- | --- |
| Cálculo e servidor local | **Python** (NumPy/SciPy) | melhor ecossistema para processamento de sinais e para validação numérica | TypeScript (numérica fraca); C# (bom no Windows, ecossistema numérico menor) |
| Interface | página web local exibida em janela desktop (ex.: pywebview), gráficos interativos | bom para gráficos e chat; um só código | Qt/PySide6 (nativo, mais trabalho de UI); Electron (pesado) |
| Dados | SQLite + pasta de arquivos imutáveis | local, sem servidor, auditável | — |
| IA | adaptador comum para Claude, OpenAI e modelos locais (API compatível) | evita dependência | um único fornecedor |
| Execução | `.bat` de dois cliques no início; instalador depois | P11 | — |

---

## 5. MVP de utilidade comprovável

### 5.1 Definição

**Um ciclo de diagnóstico verificável, ponta a ponta, no carro do usuário:**

1. Cadastro do sistema (veículo, posições dos alto-falantes e do ouvinte, canais do DSP, equipamentos, limites de fabricante).
2. Importação de medições do REW (arquivo exportado; leitura pela API quando disponível), com metadados e snapshot do ajuste.
3. Verificação de qualidade das medições.
4. Análise determinística: suavização fracionária, médias, diferença tonal L/R, desvio em relação à curva-alvo, tempo de chegada e atraso relativo, estimativa de polaridade, previsão vs. medição da soma no crossover, variação espacial entre posições.
5. Diagnóstico: detectores → sinais; IA formula hipóteses a partir dos sinais e da queixa subjetiva.
6. Recomendação de um experimento controlado, com previsão e passos de segurança.
7. Comparação antes/depois com veredito.
8. Diário completo, retomável.

**Fora do MVP**: escrever no DSP; ler arquivo de ajuste do HELIX (antes da inspeção); projeto de FIR; automação de varreduras; EQ automático.

### 5.2 Critérios de utilidade (propostos — a ratificar)

| Critério | Meta |
| --- | --- |
| Cálculos | 100% da suíte G1; concordância com o REW dentro das tolerâncias da seção 6 |
| Diagnóstico em falhas injetadas | hipótese correta entre as três primeiras em ≥ 90% dos cenários |
| Campo | ≥ 5 experimentos reais com previsão quantitativa e veredito inequívoco registrados |
| Segurança | zero recomendações que violem guardas, em teste e em campo |
| Rastreabilidade | qualquer alteração do ajuste vigente é explicada pelo diário sem a conversa original |
| Julgamento humano (G3) | o usuário avalia se o ciclo encurtou o caminho até o resultado |

---

## 6. Plano de validação

| Nível | O que valida | Como | Exemplos de tolerância (a ratificar) |
| --- | --- | --- | --- |
| **L1 — Cálculo com resposta analítica** | cada função do motor | sinais sintéticos com resposta conhecida: atraso puro, polaridade invertida, biquads (fórmulas fechadas), soma de duas fontes, ruído conhecido | atraso: ±1 amostra; magnitude de biquad: ±0,01 dB |
| **L2 — Concordância com o REW** | importação e cálculos sobre dados reais | mesma resposta ao impulso → comparar magnitude, fase, atraso do REW com os do Jarvis | ±0,1 dB; ±2°; ±10 µs |
| **L3 — Regressão com dados de referência** | estabilidade ao longo do desenvolvimento | medições reais do carro congeladas por hash; resultados de referência | identidade numérica |
| **L4 — Diagnóstico com falha injetada** | detectores e hipóteses | cenários sintéticos e semissintéticos: polaridade invertida, atraso errado de 0,3 ms, cancelamento no crossover, desequilíbrio L/R de 2 dB, passa-altas de tweeter abaixo do limite | top-3 ≥ 90% |
| **L5 — Segurança** | guardas | testes de propriedade com milhares de recomendações geradas: nenhuma viola limites | zero violações |
| **L6 — IA** | interpretação e conversa | conjunto fixo de casos; verificação automática “nenhum número sem origem”; rubrica de qualidade; execução em mais de um provedor | 100% rastreabilidade numérica |
| **L7 — Campo (G3)** | utilidade real | experimentos no carro: previsão vs. resultado; audição do usuário | seção 5.2 |

---

## 7. Organização no Arkan

### 7.1 Sequência

1. **Repositório** `Boguissimo/lab-sq-jarvis` (privado, vazio) — criado pelo usuário.
2. **Fundação** (feature `001-000-fundacao-arkan`, peso Doc/Config): pacote Arkan da geração `281e98d39` sem alterações; `.gitattributes`; `stack.md`; `create-project.sh`; constituição do projeto a partir da seção 4.4; `config.md`; agente de domínio `engenharia-acustica-sq`.
3. **`/arkan.projeto`**: briefing e visão a partir deste diagnóstico; feature map aprovado.
4. **Por feature**: `/arkan.ideacao` → … → `/arkan.qa`, com `/arkan.analyze` antes de implementar e gates G1/G2/G3.

### 7.2 Feature map candidato (a decompor formalmente em `/arkan.projeto`)

| # | Feature | Prioridade | Peso | Depende de |
| --- | --- | --- | --- | --- |
| F001 | fundação Arkan e constituição | P1 | Doc | — |
| F002 | modelo do sistema (veículo, geometria, canais, equipamentos, limites) | P1 | Code | F001 |
| F003 | ingestão de medições REW e armazenamento imutável | P1 | Code | F001 |
| F004 | motor de cálculo determinístico + suíte de validação L1–L3 | P1 | Code | F003 |
| F005 | detectores, base de conhecimento e registro epistêmico | P1 | Code | F002, F004 |
| F006 | assistente de IA independente de fornecedor, com verificador e guardas | P1 | Code | F005 |
| F007 | experimentos e comparação antes/depois | P1 | Code | F005 |
| F008 | interface gráfica (janela, gráficos, chat, diário) | P1 | Code | F003 |
| F009 | piloto no veículo (validação L7) | P1 | Doc | F006, F007, F008 |
| F010 | leitura do arquivo de ajuste HELIX | P2 | Code | inspeção de arquivo real |
| F011 | exportação de filtros no formato “REW Generic EQ” para o PC-Tool | P2 | Code | F007 |
| F012 | medição automatizada via API do REW (Pro) | P2 | Code | F003 |
| F013 | sessões de audição estruturadas (nível igualado, comparação cega A/B) | P3 | Code | F007 |

---

## 8. Decisões que exigem aprovação

| ID | Decisão | Recomendação | Alternativas |
| --- | --- | --- | --- |
| DA-01 | Onde o projeto vive | repositório próprio `lab-sq-jarvis`, com cópia própria do pacote Arkan | segundo projeto dentro de um repositório existente (fere a independência) |
| DA-02 | Pilha | Python + interface web local em janela desktop + SQLite | C#/.NET; Qt; Electron/TypeScript |
| DA-03 | Integração com o REW | importação de arquivo (garantida) + leitura pela API; sem varredura automática no MVP | só arquivo; automação completa (exige Pro) |
| DA-04 | Integração com o HELIX | humano no circuito: receita de alteração + arquivo de ajuste arquivado por hash; leitura do arquivo só após inspeção | tentar engenharia reversa do protocolo (risco, sem suporte) |
| DA-05 | IA | adaptador para vários provedores; IA nunca calcula; verificador de números | provedor único |
| DA-06 | Privacidade | enviar à IA só dados derivados (cálculos, sinais), não arquivos brutos; chaves no cofre do Windows | enviar tudo; só modelo local |
| DA-07 | Modelo epistêmico e governança de critérios | seções 4.2 e 4.3 | — |
| DA-08 | Escopo do MVP e critérios de utilidade | seções 5.1 e 5.2 | — |

## 9. Informações que só o usuário pode fornecer

1. Criar o repositório `Boguissimo/lab-sq-jarvis` e anexá-lo à sessão.
2. REW: versão instalada e se tem licença Pro.
3. Microfone (modelo; tem arquivo de calibração?) e interface de áudio (tem AMI ou loopback?).
4. DSP HELIX: modelo e versão do PC-Tool (5 ou 6).
5. Veículo e topologia do sistema (vias, sub, central, amplificadores, alto-falantes).
6. Arquivos de exemplo: um arquivo de ajuste do PC-Tool e algumas medições do REW (`.mdat` e exportações) do carro.
7. Provedores de IA que aceita usar e se aceita enviar dados derivados para a nuvem.
8. Se compete (EMMA, IASCA, MECA…) e qual regulamento serve de vocabulário de percepção.

---

## 10. Fontes consultadas

- REW — API: https://www.roomeqwizard.com/help/help_en-GB/html/api.html
- REW — versões beta: https://www.roomeqwizard.com/beta.html
- Fórum do autor do REW (API, Pro): https://www.avnirvana.com/threads/rew-api-beta-releases.12981/
- room-eq-wizard-mcp: https://glama.ai/mcp/servers/mgg64z6a6z
- rew-iqc: https://github.com/audiomacgyver/rew-iqc
- qrew: https://pypi.org/project/qrew/
- Audiotec Fischer — downloads do PC-Tool: https://www.audiotec-fischer.de/en/tools/dsp-pc-tool/downloads/
- Audiotec Fischer — DSP PC-Tool 6: https://www.audiotec-fischer.de/en/tools/dsp-pc-tool-6/
- Audiotec Fischer — TuneEQ: https://www.audiotec-fischer.de/en/knowledge-base/dsp-pc-tool/tuneeq/
- Audiotec Fischer — AMI: https://www.audiotec-fischer.de/en/accessories/ami
- EISA — DSP PC-Tool 6: https://eisa.eu/awards/dsp-pc-tool-6/
- EMMA — DSP PC-Tool 6: https://www.emmanet.info/audiotec-fischer-dsp-pc-tool6/
- DIYMA — PC-Tool 6 lançado: https://www.diymobileaudio.com/threads/dsp-pc-tool-6-live-and-ready-for-download.476476/
- DIYMA — PC-Tool 5.05.01: https://www.diymobileaudio.com/threads/helix-brax-match-dsp-tool-5-05-01-big-software-update-brax-dsp-goes-virtual.467701/
- DIYMA — importação de filtros REW no PC-Tool: https://www.diymobileaudio.com/threads/how-to-import-rew-filter-sets-into-the-helix-v4-20-software.359418/page-2
- Audison ACCORDO: https://audison.com/accordo/
- Tuning Labs: https://tuninglabs.net/
- EMMA — regulamento 2024: https://www.emmanet.info/wp-content/uploads/2024/03/EMMARulebook2024.pdf
