# Lab SQ Jarvis | Feedback estratégico e diretrizes de evolução

> **Origem**: feedback do desenvolvedor, registrado em 2026-10-16 durante a aplicação da revisão externa ao plano do JV-V02. Transcrito como recebido. **Não altera o escopo do JV-V02, não cria feature, requisito obrigatório nem task.** Registro de orientação para a arquitetura futura. Registrada como `JV-D044` em `decisoes.md`, **aprovada pelo desenvolvedor em 2026-10-16**. A `JV-D043` (diretriz do REW) segue pendente de decisão própria.

Claude, tivemos uma discussão sobre o potencial do Lab SQ Jarvis, tanto como ferramenta pessoal quanto como possível produto comercial.
Quero registrar algumas conclusões para orientar a arquitetura futura, sem alterar o escopo aprovado do JV-V02.

## 1. O usuário de referência
O desenvolvedor é também o primeiro cliente-alvo do produto.
O perfil é o entusiasta de áudio automotivo que investe em equipamentos de qualidade, possui conhecimento técnico geral, mas não domina profissionalmente a calibração acústica.
Ele deseja aprender, compreender os ajustes e conquistar autonomia, sem precisar se tornar especialista em REW, processamento digital de sinais e acústica automotiva.
Princípio de produto: o Jarvis deve ensinar enquanto ajuda a resolver problemas reais, reduzindo a necessidade de consultar especialistas ou outras IAs para compreender suas orientações.

## 2. Potencial comercial
Identificamos dois públicos principais:
Consumidores entusiastas: querem melhorar o próprio sistema com autonomia, orientação e segurança.
Profissionais de instalação e calibração: querem aumentar produtividade, melhorar diagnósticos, padronizar procedimentos e preservar conhecimento técnico.
O primeiro segmento profissional a investigar é o instalador que domina equipamentos e instalação, mas depende de conhecimentos especializados para oferecer calibração acústica de maior qualidade.
A hipótese de diferenciação não é substituir REW, PC-Tool ou o ajustador experiente. É oferecer investigação causal assistida, experimentos controlados, verificação de evidências e memória técnica por veículo.
Essas são hipóteses comerciais, ainda não demonstradas.

## 3. Instrumentação e acessibilidade
A necessidade de equipamentos de medição pode representar uma barreira de entrada.
A arquitetura futura deve permitir diferentes níveis de instrumentação:

* Sem microfone: orientação baseada em informações declaradas, sem inventar diagnósticos acústicos.
* Celular: experimentação limitada e explicitamente identificada como não calibrada.
* Microfone USB calibrado: diagnósticos compatíveis com as medições e referências disponíveis.
* Microfone e interface de áudio: recursos adicionais, incluindo possibilidade de referência temporal por loopback.

O sistema não deve tratar a ausência de instrumentação como impossibilidade de uso, mas deve impedir conclusões não sustentadas pelos dados disponíveis.
Não implementar esses diferentes níveis agora. Preservar a possibilidade arquitetural e detalhar futuramente os protocolos necessários.

## 4. Integração com engines de IA
A integração está prevista para a F009/JV-V03.
Queremos independência de provedores, permitindo futuramente GPT, Claude, Gemini e modelos locais, mediante adaptadores.
Separação essencial:

* Núcleo determinístico: cálculos acústicos, critérios, segurança, integridade e admissibilidade.
* IA: interpretação, explicação, interação conversacional, formulação de hipóteses e solicitação de novos cálculos ou dados.
* Usuário: aprovação e execução física dos ajustes.

A IA não altera critérios técnicos, não contorna bloqueios SEG e não escreve no DSP.
Considerar desde o desenho da F009: contexto estruturado da sessão; ferramentas de consulta e cálculo com permissões; validação das respostas; identificação do modelo e provedor; controle de dados enviados; armazenamento seguro das credenciais; e preservação do histórico independentemente da engine.
A eventual utilização de várias IAs numa mesma investigação fica para avaliação posterior.
Não antecipar a implementação da F009 para o V02.

## 5. Validação do produto
O desenvolvimento continua orientado ao uso pessoal.
Nossa sequência de validação será:

1. Fazer o Jarvis funcionar tecnicamente.
2. Utilizá-lo no Focus com medições reais.
3. Verificar se o processo melhora a qualidade das decisões e reduz dificuldades práticas.
4. Experimentar com outros entusiastas.
5. Experimentar com instaladores e ajustadores profissionais.
6. Avaliar o potencial de comercialização.

Nos testes com profissionais, observar especialmente tempo de diagnóstico, quantidade de intervenções, qualidade dos resultados, facilidade de compreensão e capacidade de recuperar o histórico.
Não confundir aprovação dos testes sintéticos com validação de utilidade ou de eficácia acústica em campo.

## 6. Prioridade imediata
Nada disso deve ampliar o JV-V02.
A prioridade continua sendo fechar corretamente a emenda E3 e a revisão R1.2 do plano, com suas ressalvas, verificar a consistência entre spec, ADRs, data-model e testes, obter a aprovação formal necessária e seguir para `/arkan.tasks`.
Manter o Princípio VIII: o agente propõe, o desenvolvedor decide.
Registrar este feedback como diretriz estratégica futura, preferencialmente nos artefatos existentes, sem criar novas features, requisitos obrigatórios ou tarefas de implementação para o V02.
Objetivo central: primeiro construir uma ferramenta que realmente resolva o problema do desenvolvedor. O potencial comercial será consequência de resultados demonstrados, não uma premissa de desenvolvimento.

---

## Nota do agente (2026-10-16)

- **Relação com o estado real:** a E3/R1.2 já estava aprovada (2026-10-15) e o `/arkan.tasks` já foi executado (tasks JV-T201 a T242, com T201 a T222 concluídas). O que restava antes do G3 do bloco 1 eram as duas divergências do SC-208, tratadas na emenda E4 (decisões registradas; redação final em conferência).
- **Onde esta diretriz fica refletida (sem requisito novo):** este arquivo; seção 3 de `docs/RETOMADA-JV-V02.md`; `decisoes.md` (JV-D044); nota "Diretrizes estratégicas futuras" em `feature-map.md` (F009, F013, F017). Nenhuma alteração em spec, FR, INV, SC ou tasks do V02 por causa deste feedback.
- **Pontos de contato com decisões já tomadas (para o desenho futuro):** a distinção entre níveis de instrumentação já aparece, em forma mínima, na referência temporal e na aquisição **declaradas** (E3, A02/A03) e na separação SYNTHETIC/EXPERIMENTAL/CALIBRATED da diretriz REW; a separação núcleo determinístico / IA / usuário é a mesma de JV-D (F009: ferramentas só de leitura) e do Princípio VIII. Nada disso exige código no V02.

---

## Complemento consolidado (2026-10-16) — somente o que é novo

> Texto "Orientações consolidadas para continuidade", transcrito pelo agente **apenas nos pontos que acrescentam algo**. O restante (usuário de referência, os dois segmentos e o instalador como primeiro público profissional, níveis de instrumentação, separação núcleo determinístico / IA / usuário na F009, escopo do V02 intocado, JV-D043 pendente, "sem commit antes da autorização") já está acima ou em `JV-D044` e **não foi duplicado**. Não cria decisão nova nem requisito; vale como fundamentação complementar da `JV-D044`.

### A. Benchmark de mercado (validação futura; sem requisito no V02)
A aceitabilidade da imprecisão do Jarvis será avaliada **também em comparação com referências de mercado**, sem exigir desempenho perfeito nem metas arbitrárias desconectadas do que instrumentos, algoritmos e profissionais entregam em condições reais. Três dimensões, que não se misturam:
1. **Precisão da medição:** repetibilidade, ruído, incerteza instrumental, posicionamento, confiabilidade dos dados acústicos.
2. **Precisão do diagnóstico:** acertos, falsos positivos, falsos negativos, inconclusivos corretamente identificados, capacidade de formular hipóteses úteis.
3. **Eficácia do ajuste:** melhoria acústica efetiva, número de intervenções, repetibilidade do resultado, tempo necessário, qualidade percebida.

Referências a considerar no futuro: REW (medição e processamento), Flat Liner e Tuning Labs (fluxos de ajuste e funcionalidades comparáveis), ajustadores profissionais experientes (diagnóstico e intervenção prática) e o método simples REW + planilha + anotações.
- As comparações usam **condições equivalentes**, os **mesmos dados** sempre que possível e **verdade de referência independente**; métricas diferentes não se confundem e alegações comerciais não contam como comprovação independente.
- **Segurança não é relativizada pelo benchmark:** uma recomendação perigosa não se torna aceitável porque outra ferramenta também a produz.
- Relaciona-se com a limitação do detector em σ = 1,5 dB (`spec.md`, SC-208(b)): qualquer limite futuro de falsos positivos será justificado e testado de forma independente, e esse benchmark é um dos insumos.

### B. Acréscimos pontuais
- **Perfil de referência ≠ mercado:** o perfil do desenvolvedor é referência inicial, não demonstração de representatividade estatística.
- **Hipóteses de diferenciação (não validadas) além das já listadas:** ensino integrado ao trabalho; maior consistência de procedimentos entre profissionais; redução de intervenções desnecessárias. O Jarvis não é posicionado como substituto obrigatório do especialista nem se presume superior a soluções existentes.
- **Instrumentação:** o equipamento exigido depende da **análise pretendida**, não do acesso ao aplicativo; **falta de dados não significa sistema aprovado nem ausência de problema**; loopback elétrico só quando corretamente configurado.
- **F009:** além do já previsto, selecionar o que realmente precisa ser enviado ao provedor e **validar as afirmações técnicas e suas fontes**.
- **Sequência de validação, versão consolidada:** (1) funcionamento técnico; (2) medições reais no Focus; (3) **comparar decisões e resultados com ferramentas e procedimentos de referência**; (4) **avaliar esforço operacional e curva de aprendizado**; (5) outros entusiastas; (6) instaladores e ajustadores; (7) potencial comercial. Observar qualidade do diagnóstico, segurança, eficácia do ajuste, tempo, custo, repetibilidade e facilidade de uso. Casos sintéticos demonstram funcionamento dentro de um modelo, não desempenho acústico real nem utilidade comercial.
- **Diretriz central:** primeiro funcionar, depois compreender e quantificar as limitações, comparar com alternativas reais e só então avaliar expansão comercial. Buscar resultados úteis e competitivos, não perfeição estatística artificial; honestidade diagnóstica, rastreabilidade e segurança permanecem obrigatórias.
