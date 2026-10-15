# Visão do Projeto: Lab SQ Jarvis

> **Projeto**: lab-sq-jarvis
> **Input**: [briefing.md](briefing.md)
> **Status**: **Proposta — aguardando aprovação do desenvolvedor**
> **Data**: 2026-10-15

---

## 1. Vision Statement

> Para quem calibra sistemas de som automotivo de qualidade sonora e precisa de método, o Lab SQ
> Jarvis é um engenheiro de áudio virtual que transforma medições, configuração e percepção em
> diagnóstico fundamentado, experimentos controlados e registro rastreável. Diferente do EQ
> automático e dos analisadores, ele explica a causa, prevê o efeito de cada alteração antes de
> aplicá-la, verifica o resultado e nunca arrisca o equipamento.

**Proposta de valor**: a inteligência de diagnóstico e o método experimental que faltam entre o
REW (que mede) e o PC-Tool (que configura), com segurança e rastreabilidade verificáveis.

---

## 2. KPIs de Sucesso

| KPI | Baseline | Meta | Prazo |
| --- | --- | --- | --- |
| Rastreabilidade da cadeia (registros com tipo e referências válidas) | inexistente | 100% | MVP |
| Recomendações exibidas que violam regras de segurança | não controlado | 0 | MVP |
| Reprodutibilidade dos cálculos (mesmas entradas ⇒ mesmo resultado) | — | 100% dos casos de referência | MVP |
| Ciclo completo demonstrado no primeiro caso de referência, com veredito correto | — | demonstrado e aprovado em G3 | MVP |
| Conjunto de casos de referência com verdade definida e métricas escolhidas | inexistente | conjunto inicial publicado; métricas definidas, **sem meta numérica** (JV-D008) | MVP |
| Experimentos com medições reais do Focus | 0 | a definir após confirmação do cadastro | pós-MVP |

**KPI primário (MVP)**: ciclo completo demonstrado no primeiro caso de referência, com 100% de
rastreabilidade e zero violações de segurança.

---

## 3. Riscos

| Risco | Probabilidade | Impacto | Mitigação |
| --- | --- | --- | --- |
| IA apresentar número sem origem como fato | Média | Alto | verificador de números (P3); provedor simulado nos testes |
| Recomendação danificar equipamento | Baixa | Crítico | regras SEG; aprovação de nível B; bloqueio sem dado confirmado |
| Dados de referência sintéticos não representarem o habitáculo real | Alta | Médio | casos com ruído, reflexões e controles negativos; medições reais incorporadas progressivamente |
| Formato do arquivo do PC-Tool inacessível | Média | Médio | integração assistida; receita de alteração manual |
| Mudanças na API do REW | Baixa | Médio | importação de arquivo como caminho garantido |
| Escopo derivar para “novo REW” | Média | Alto | P10; revisão do agente de domínio |
| Defeitos do Core do Arkan travarem gates | Média | Baixo | registrar (JV-D015) e verificar manualmente o equivalente |

**Risco crítico**: recomendação que danifique o equipamento.

---

## 4. Prioridades Acordadas

### P1 — Essencial (MVP)

- Fundação do projeto no Arkan (constituição, decisões, regras de segurança, agente de domínio).
- Casos acústicos de referência com verdade conhecida e métricas definidas.
- Registro da cadeia de conhecimento com originais imutáveis e diário.
- Importação de arquivos do REW.
- Cálculos determinísticos validados para o primeiro caso.
- Indícios e hipóteses a partir dos cálculos.
- Experimento assistido com previsão, verificação de segurança e veredito.
- Assistente conversacional com IA substituível, verificador de números e registro de envios.
- Interface desktop mínima que conduz o ciclo.

### P2 — Importante (v1.0)

- Leitura direta pela API do REW.
- Cadastro real do Focus e incorporação progressiva de medições reais.
- Receita de alteração e exportação de filtros no formato aceito pelo PC-Tool.
- Ampliação do conjunto de casos e das métricas de diagnóstico.
- Leitura do arquivo de ajuste do HELIX (após inspeção).

### P3 — Desejável (roadmap)

- Medição automatizada pela API do REW (Pro).
- Sessões de audição estruturadas (nível igualado, comparação cega).

### Fora do Escopo (decisão explícita)

- Escrever no DSP — segurança e ausência de API (JV-D004).
- EQ automático e geração de sinais de medição — já existem (P10).
- Competição SQ como requisito (JV-D013).

---

## 5. Próximos Passos

- [ ] Aprovar briefing, visão, constituição e regras de segurança
- [ ] Aprovar decomposição em features (`feature-map.md`) e dependências
- [ ] Aprovar JV-D011 (interface), JV-D015 (instalação) e JV-D016 (primeiro caso)
- [ ] Iniciar F001 via `/arkan.ideacao`
