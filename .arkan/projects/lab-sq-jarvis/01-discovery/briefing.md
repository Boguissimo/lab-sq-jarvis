# Briefing: Lab SQ Jarvis

> **Projeto**: lab-sq-jarvis
> **Status**: **Proposta (revisão 2) — aguardando aprovação do desenvolvedor** (documento vivo)
> **Data**: 2026-10-15
> **Participantes**: Fabrício (desenvolvedor e usuário, engenheiro mecânico) + Claude (agente, Arkan)
> **Insumos**: [`diagnostico-inicial.md`](diagnostico-inicial.md) (histórico) ·
> [`comparacao-ferramentas.md`](comparacao-ferramentas.md) · decisões [`../decisoes.md`](../decisoes.md)

Siglas: **SQ/SQPL** — qualidade sonora / qualidade sonora com pressão sonora alta; **REW** — Room EQ
Wizard; **DSP** — processador digital de sinais; **PC-Tool** — programa que configura o HELIX;
**EQ** — equalização; **IA** — inteligência artificial; **SaaS** — software como serviço.

---

## 1. Problema

Calibrar um sistema de som automotivo de qualidade sonora exige relacionar medições, configuração do
DSP, geometria do carro, limites dos equipamentos e o que se ouve. As ferramentas existentes já
ajudam bastante: o REW mede e calcula EQ; o PC-Tool automatiza EQ e atrasos (TuneEQ, ATM); o Flat
Liner guia um fluxo sobre o REW; o Tuning Labs anuncia orientação com IA (ver
[`comparacao-ferramentas.md`](comparacao-ferramentas.md)).

O que falta **ao desenvolvedor**, que ainda está aprendendo, é um assistente que, no carro dele,
explique por que algo soa como soa, proponha um teste de cada vez com o resultado esperado, registre
o que ele ouviu antes e depois, e lembre de tudo na sessão seguinte.

**Contexto atual**:

O ajuste é feito por tentativa: mede no REW, altera no PC-Tool, mede de novo e compara de memória.
Não fica registrado com qual configuração cada medição foi feita, nem o que foi ouvido. Correções
automáticas de curva não distinguem problemas equalizáveis de cancelamentos e interferências, que
pedem outra intervenção (polaridade, atraso, crossover).

**Impacto**:

Tempo perdido, decisões que não se explicam depois, regressões sem causa conhecida, risco evitável ao
equipamento e aprendizado que não se acumula entre sessões.

---

## 2. Público-alvo

| Perfil | Descrição | Necessidade principal |
| --- | --- | --- |
| Desenvolvedor (único usuário até a versão pessoal) | Engenheiro mecânico, conhece sistemas de som automotivo, usa REW e PC-Tool, não programa, ainda aprendendo calibração | Ajustar o próprio Focus, entender o que faz e acumular aprendizado entre sessões |

**Usuário primário**: o desenvolvedor, com o Ford Focus como veículo de referência (JV-D012).
Outros perfis só serão considerados na avaliação comercial, depois da versão pessoal (JV-D017).

---

## 3. Objetivos

1. **Marco 1 — Protótipo técnico**: o ciclo completo funciona com casos conhecidos, com cálculos
   verificáveis, cadeia íntegra e regras de segurança testadas (critérios PT-01 a PT-10).
2. **Marco 2 — Versão pessoal utilizável**: o desenvolvedor faz sessões reais no Focus, entende a
   orientação e retoma o trabalho em outro dia (critérios VP-01 a VP-10).
3. Construir o conjunto de casos de teste e as métricas de diagnóstico antes de qualquer meta de
   acerto (JV-D008).

**Fora do escopo desta versão**:

- Assinatura, SaaS, multiusuário, requisitos de oficina (JV-D017).
- Medir, gerar sinais de teste ou equalizar automaticamente — continuam no REW e no PC-Tool (P10).
- Escrever parâmetros no DSP (JV-D004, JV-D028).
- API do REW, arquivo do HELIX, comparação cega, medição automatizada — depois da versão pessoal.
- Projeto de filtros FIR (resposta ao impulso finita).
- Competição SQ como requisito (JV-D013).

---

## 4. Restrições

| Tipo | Restrição | Impacto |
| --- | --- | --- |
| Tecnológica | Python, SQLite, desktop Windows, uso local (JV-D002, JV-D028) | sem servidor; abrir com dois cliques |
| Tecnológica | HELIX sem API pública nem formato de arquivo documentado | ajustes aplicados à mão pelo desenvolvedor (JV-D004) |
| Metodológica | cálculos de validação e recomendação determinísticos (P3) | IA explica, planeja e conversa; estimativas marcadas |
| Medição | fase e soma prevista exigem referência temporal compatível (JV-D023) | protocolo de medição precisa garantir isso |
| Segurança | regras SEG reduzem risco, não garantem segurança (JV-D022) | recomendações sensíveis com aprovação nominal |
| Dados | equipamentos do Focus ainda não confirmados; itens planejados não presumidos (JV-D012) | Marco 1 usa casos simulados |
| IA | independência de fornecedor; envio conforme necessidade, com transparência e controle (JV-D005) | adaptador e registro de envios |
| Operacional | desenvolvedor não programa; quer fluxo guiado, não telas avulsas (P13) | sessão em cinco passos |
| Método | Arkan Core sem modificação | defeitos do Core registrados (JV-D015), não corrigidos aqui |

---

## 5. Stakeholders

| Nome / Papel | Interesse | Nível de envolvimento |
| --- | --- | --- |
| Fabrício — desenvolvedor e usuário | ajustar o Focus com método; decisões de engenharia | Alto |
| Mantenedor do Arkan | integridade do Core; recebe as observações de JV-D015 | Baixo |

**Decisor final**: Fabrício.

---

## 6. Contexto Adicional

### Decisões tomadas

| Decisão | Fundamentação |
| --- | --- |
| JV-D001 a JV-D004, JV-D007 | aprovadas a partir do diagnóstico inicial |
| JV-D005, JV-D006 | IA independente; dados por necessidade técnica; estimativas identificadas |
| JV-D008 | métricas antes de metas |
| JV-D017 | pessoal primeiro, comercial depois |
| JV-D018 | comparação refeita; sem pretensão de ineditismo |
| JV-D019 | dois marcos (substitui JV-D010) |
| JV-D020, JV-D021 | sessão guiada; percepção antes/depois |
| JV-D022 a JV-D026 | limites técnicos e de segurança corrigidos |
| JV-D027, JV-D028 | medições reais por arquivo; preservações reafirmadas |

### Dúvidas resolvidas

| Pergunta | Resolução |
| --- | --- |
| O Jarvis precisa ser inédito? | Não; justifica-se pelo que acrescenta ao uso do desenvolvedor (JV-D018). |
| Passar no REF-001 prova utilidade? | Não; prova funcionamento técnico. Utilidade só no Marco 2 (JV-D019). |
| Medições reais esperam a API do REW? | Não; usam importação de arquivos (JV-D027). |
| As regras garantem a segurança do equipamento? | Não; reduzem o risco nas condições conhecidas (JV-D022). |

### Pendências de informação (só o desenvolvedor pode fornecer)

1. Versão e licença do REW instalado.
2. Cadastro real do Focus: DSP, amplificadores, alto-falantes, posições — com fichas técnicas.
3. Microfone e interface de medição efetivamente disponíveis (e se permitem referência temporal).
4. Um arquivo de ajuste do PC-Tool, quando houver DSP (para a F019).
5. Provedores de IA aceitos.

### Síntese (aguardando validação)

- **Nome canônico**: Lab SQ Jarvis (`lab-sq-jarvis`).
- **Definição**: assistente pessoal de calibração de áudio automotivo que guia uma sessão — do que se
  percebe ao que mudou —, explicando, testando e lembrando, junto com o REW e o PC-Tool.
- **Escopo**: Marco 1 e Marco 2 (ver `../02-proposal/proposta-consolidada.md`).
- **Fora do escopo**: lista da seção 3.

### Histórico de revisões

| Data | Mudança |
| --- | --- |
| 2026-10-15 | Versão inicial |
| 2026-10-15 | Revisão 2: foco pessoal; problema reescrito reconhecendo o que as ferramentas já fazem; objetivos por marco; público reduzido ao desenvolvedor |
