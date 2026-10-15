# Briefing: Lab SQ Jarvis

> **Projeto**: lab-sq-jarvis
> **Status**: **Proposta — aguardando aprovação do desenvolvedor** (documento vivo)
> **Data**: 2026-10-15
> **Participantes**: Fabrício (desenvolvedor, engenheiro mecânico) + Claude (agente, Arkan)
> **Insumos**: [`diagnostico-inicial.md`](diagnostico-inicial.md) · decisões [`../decisoes.md`](../decisoes.md)

---

## 1. Problema

Calibrar um sistema de som automotivo de qualidade sonora (SQ/SQPL) exige relacionar medições
acústicas, configuração do DSP, geometria do veículo, limites dos equipamentos e percepção
auditiva. As ferramentas existentes fazem bem partes isoladas — o REW mede e analisa; o HELIX DSP
PC-Tool configura e oferece EQ automático —, mas nenhuma faz o raciocínio de engenharia que liga
essas partes: diagnosticar a causa, formular hipóteses, planejar uma alteração controlada,
prever seu efeito e verificar se ele ocorreu.

**Contexto atual**:

O ajuste é feito por tentativa: mede-se no REW, altera-se o PC-Tool, mede-se de novo e
compara-se de memória. Nenhuma ferramenta registra com qual ajuste do DSP cada medição foi feita;
o EQ automático corrige a curva de magnitude sem distinguir problemas equalizáveis de
cancelamentos e interferências, que exigem outra intervenção (polaridade, atraso, crossover) e que,
quando “corrigidos” com reforço de EQ, gastam margem e arriscam o equipamento. Percepções
subjetivas (“palco puxado para a esquerda”, “voz metálica”) não viram testes objetivos.

**Impacto**:

Tempo perdido, decisões sem rastreabilidade, regressões que ninguém sabe explicar, risco de dano
(tweeter com corte baixo demais, reforços excessivos) e aprendizado que não se acumula entre
sessões. Afeta quem calibra o próprio sistema e precisa de método, não só de gráficos.

---

## 2. Público-alvo

| Perfil | Descrição | Necessidade principal |
| --- | --- | --- |
| Calibrador técnico (usuário primário) | Engenheiro ou entusiasta avançado que domina sistemas de som automotivo, usa REW e PC-Tool, não programa | Diagnóstico fundamentado, experimentos controlados e registro confiável do que foi feito e por quê |
| Revisor técnico (futuro) | Outra pessoa que analisa o histórico de calibração | Reconstruir decisões a partir do registro, sem a conversa original |

**Usuário primário**: calibrador técnico — o próprio desenvolvedor, com o Ford Focus como primeiro
veículo de referência.

---

## 3. Objetivos de Negócio

1. Demonstrar, com dados de referência de verdade conhecida, um ciclo completo
   medição → cálculo → indício → hipótese → recomendação → experimento → conclusão → decisão, com
   100% dos registros rastreáveis.
2. Garantir que nenhuma recomendação exibida viole as regras de segurança do equipamento (zero
   violações na suíte de testes de segurança).
3. Construir o conjunto de casos de teste e as métricas de diagnóstico antes de qualquer meta de
   acerto (JV-D008).
4. Incorporar progressivamente medições reais do Focus, depois de confirmado o cadastro dos
   equipamentos.

**Fora do escopo desta versão**:

- Medir, gerar sinais de teste ou equalizar automaticamente — pertence ao REW e ao PC-Tool (P10).
- Escrever parâmetros no DSP (JV-D004, SEG-11).
- Ler o arquivo de ajuste do HELIX antes de inspecionar um arquivo real.
- Disparo automático de varreduras pela API do REW (exige Pro).
- Projeto de filtros FIR.
- Competição SQ como requisito (JV-D013).
- Metas numéricas de acerto diagnóstico (JV-D008).

---

## 4. Restrições

| Tipo | Restrição | Impacto |
| --- | --- | --- |
| Tecnológica | Python, SQLite, desktop Windows, uso local (JV-D002) | Sem servidor; empacotamento para dois cliques |
| Tecnológica | HELIX sem API pública nem formato de arquivo documentado | Integração assistida pelo humano (JV-D004) |
| Tecnológica | API do REW: leitura livre; varredura exige Pro | Leitura e importação no escopo; automação de medição fora |
| Metodológica | Cálculo de validação e recomendação só determinístico (P3) | IA restrita a interpretação, planejamento, conversa e estimativas marcadas |
| Segurança | Regras SEG-01 a SEG-12 (proposta) | Recomendações sensíveis bloqueadas sem dado confirmado; aprovação de nível B |
| Dados | Equipamentos do Focus ainda não confirmados; itens planejados não presumidos (JV-D012) | MVP usa dados de referência construídos |
| IA | Independência de fornecedor; envio conforme necessidade técnica, com transparência e controle (JV-D005) | Camada de adaptação e registro de envios |
| Operacional | Desenvolvedor não programa (P13) | Operação por interface; erros em linguagem simples |
| Método | Arkan Core sem modificação | Defeitos encontrados no Core são registrados, não corrigidos aqui |

---

## 5. Stakeholders

| Nome / Papel | Interesse | Nível de envolvimento |
| --- | --- | --- |
| Fabrício — desenvolvedor e usuário primário | Calibração com método e rastreabilidade; decisões de engenharia | Alto |
| Mantenedor do Arkan | Integridade do Core; recebe as observações de defeito registradas em JV-D015 | Baixo |

**Decisor final**: Fabrício.

---

## 6. Contexto Adicional

### Decisões tomadas

| Decisão | Fundamentação | Alternativas descartadas |
| --- | --- | --- |
| JV-D001 a JV-D004, JV-D007 | aprovadas pelo desenvolvedor em 2026-10-15 a partir do diagnóstico inicial | ver `decisoes.md` |
| JV-D005 | independência de IA; dados conforme necessidade técnica, com transparência e controle | regra fixa “só dados derivados” |
| JV-D006 | IA pode estimar de forma identificada; validação e recomendação por rotina determinística | IA proibida de qualquer número |
| JV-D008 | métricas antes de metas | meta de 90% no início |
| JV-D010 | MVP com dados de referência | MVP com medições reais do carro |

### Dúvidas resolvidas

| Pergunta | Resolução |
| --- | --- |
| O Jarvis compete com REW ou PC-Tool? | Não; complementa (P10). |
| Usa-se equipamento planejado nas análises? | Não, só confirmado (P5, SEG-12). |
| Competição é requisito? | Não (JV-D013). |
| A questão do Arkan Fiscal entra no projeto? | Não; pendência independente (JV-D009). |

### Pendências de informação (só o desenvolvedor pode fornecer)

1. Versão e licença do REW instalado.
2. Cadastro real do Focus: DSP, amplificadores, alto-falantes, posições — com fichas técnicas.
3. Microfone e interface de medição efetivamente disponíveis.
4. Um arquivo de ajuste do PC-Tool, para inspeção do formato (quando houver DSP).
5. Provedores de IA aceitos.

### Síntese (aguardando validação)

- **Nome canônico**: Lab SQ Jarvis (`lab-sq-jarvis`).
- **Definição**: assistente desktop de calibração de áudio automotivo que transforma medições,
  configuração e percepção em diagnóstico fundamentado, experimentos controlados e registro
  rastreável, trabalhando com o REW e o HELIX DSP PC-Tool.
- **Escopo do MVP**: ciclo de diagnóstico e experimento assistido sobre dados de referência
  (ver `../02-proposal/preparacao-mvp.md`).
- **Fora do escopo**: lista da seção 3.
