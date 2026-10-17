# Revisão técnica do plano de implementação JV-V02

> **Origem**: revisão externa (ChatGPT), recebida do desenvolvedor em 2026-10-16, sobre o `plan.md` e o `data-model.md` do commit `e2ab7ff`. Transcrita como recebida. **Ainda não aplicada ao plano.** Estado de cada item: ver `docs/RETOMADA-JV-V02.md`.

**Projeto**: Lab SQ Jarvis
**Veredito**: APROVAR COM AJUSTES.

O plano está bem estruturado e contempla conceitualmente os 22 requisitos funcionais (FR-201 a FR-222), os 10 invariantes (INV-201 a INV-210) e os 7 critérios de sucesso (SC-201 a SC-207). Entretanto, a revisão cruzada com o código do JV-V01 identificou problemas que precisam ser corrigidos antes da implementação.

Não é necessário refazer a arquitetura. Solicito incorporar as correções abaixo, respeitando o processo de decisões e aprovações do Arkan Core.

## Problemas identificados

1. **[ALTA] Migração SQLite (ADR-207).** O V01 não configura `PRAGMA user_version = 1`. Portanto, o banco existente normalmente apresenta versão 0. Corrigir a estratégia para reconhecer o esquema legado, migrar para a versão 2 e preservar integralmente as sessões. A migração deve ser transacional, idempotente, precedida de backup consistente e acompanhada de testes com um banco efetivamente produzido pelo V01. Reorganizar `Banco.__init__`, que atualmente executa o esquema antes de qualquer migração. Recusar versões desconhecidas sem modificar o banco.

2. **[ALTA] Reutilização dos registros na calibração (ADR-205).** Manter os tipos `recomendacao`, `experimento` e `conclusao`, sem modificar `DERIVACOES_PERMITIDAS`. Entretanto, métodos como `propor_teste`, `registrar_aplicacao`, `estado` e `resumo` pressupõem testes de polaridade, campos como `variavel` e `previsao`, e conclusões com `veredito`. Adaptar explicitamente o serviço para os dois fluxos. Testar criação, execução, encerramento, histórico e reabertura de sessões de investigação e calibração.

3. **[ALTA] Estimativa de ruído (ADR-202).** O desvio padrão do resíduo contra uma média móvel de sete pontos mede irregularidade espectral, não necessariamente ruído de medição. Cancelamentos e reflexões acústicas reais também podem produzir resíduos elevados. Isso pode fazer o Jarvis rejeitar justamente os problemas que deveria diagnosticar. Revisar a interpretação do indicador. Comparar os resultados com o ruído efetivamente introduzido nos cenários sintéticos, incluindo casos de ruído isolado, cancelamento sem ruído e combinação dos dois. Caso o método normativo precise mudar, revisar formalmente a spec.

4. **[ALTA] Segurança das recomendações (ADR-204).** A avaliação das regras SEG deve participar obrigatoriamente da decisão de admissibilidade da recomendação. Uma condição bloqueada não pode aparecer como alteração recomendada ou segura. A aprovação de nível B não transforma uma condição desconhecida em verificada. Manter SEG-02, SEG-07 e SEG-09 como `não verificável`, sem inventar modelos de excursão, margem digital ou exposição acústica. Reforços dependentes dessas verificações continuam bloqueados. Aplicar a avaliação de segurança também às recomendações herdadas do V01.

5. **[ALTA] Qualidade e rastreabilidade.** Persistir resultados dos controles de qualidade, versões dos algoritmos, limiares utilizados e identificadores ou hashes das entradas. O V01 reconstrói parte da análise executando novamente as regras, o que pode modificar a interpretação histórica quando elas evoluírem. Resultados registrados devem permanecer associados à versão que os produziu. A ausência de referência temporal compatível impede inferências sobre fase relativa, atraso e soma complexa prevista.

6. **[MÉDIA] Aprovação em tabela própria (ADR-204).** Manter essa solução, pois aprovação representa autorização do usuário, não derivação técnica de conhecimento. Reforçar a integridade: a aprovação precisa identificar uma recomendação existente, pertencente à mesma sessão, com nível, escopo, momento e alteração autorizada. A aprovação não modifica o resultado das regras SEG.

7. **[MÉDIA] Teste comprometido (ADR-208).** A comparação da configuração declarada e da variação média de nível é insuficiente para detectar todas as mudanças indevidas. Permitir medições posteriores de ambas as vias, analisar faixas relevantes para cada alto-falante e distinguir ausência comprovada de alteração de ausência de dados para verificá-la. Garantir que REF-001-N3 produza `comprometida`, sem confirmar ou refutar a hipótese.

8. **[MÉDIA] Configuração e reversão (ADR-206).** Preservar arquivos de ajuste opacos e imutáveis, vinculados por hash. Implementar recuperação da última configuração entre sessões, pois o V01 consulta configurações apenas da sessão informada. Distinguir disponibilidade de arquivo ou receita inversa de restauração física efetivamente confirmada. Arquivar um arquivo não garante sua compatibilidade ou aplicação correta no DSP.

9. **[MÉDIA] Integridade (FR-222).** Estender as verificações para aprovações, configurações, arquivos de ajuste, resultados SEG e diário. Criar testes com inconsistências deliberadamente introduzidas. Verificar a imutabilidade das configurações, que não possuem no V01 a mesma proteção por gatilhos aplicada a outros registros.

10. **[MÉDIA] Gerador acústico (ADR-201).** Preservar REF-001-A sem alterações. Nos novos casos, gerar respostas fisicamente coerentes. Filtros, atrasos, polaridades e efeitos acústicos devem determinar conjuntamente magnitude, fase e soma. Acrescentar posteriormente ruído e erros de aquisição. Não gerar essas grandezas independentemente. Determinismo não garante plausibilidade acústica.

11. **[MÉDIA] Critérios de aceitação.** Explicitar as quatro variantes de REF-002-A: `objetivo atingido`, `parcial`, `não atingido` e `inconclusivo`. Tratar déficit inicial nulo e divisões por zero. Garantir os 1.000 casos aleatórios com semente fixa do SC-204, os três desfechos de reversão do SC-205, a execução no Windows do SC-206 e toda a suíte V01 + V02 do SC-207, sem alterar as asserções anteriores.

12. **[BAIXA] Documentação.** Conferir a cronologia das aprovações, pois alguns arquivos apresentam data de aprovação de 16/10/2026. Qualificar a expressão `reversão garantida` para evitar confusão entre reversão documental e restauração física.

## Avaliação dos limiares provisórios

Os limiares podem permanecer como parâmetros experimentais, mas não devem ser considerados critérios validados para o equipamento real.

- O limite de ruído de 1,5 dB depende da revisão metodológica do estimador.
- O vale individual de 10 dB serve como referência inicial, mas pode deixar de reconhecer anomalias menores.
- A mudança média de nível superior a 1 dB não detecta todas as alterações relevantes.
- O déficit máximo de 3 dB no cruzamento e a redução de 50% para resultado parcial são critérios operacionais razoáveis, desde que seus casos-limite sejam tratados.
- Os limites SEG de +1,5 dB por experimento, +3 dB por filtro e +6 dB acumulados podem permanecer provisoriamente para testar o motor de regras, sem pressupor segurança para hardware real.
- Validar os limiares mediante varreduras de amplitudes, atrasos, ruídos, ressonâncias e cancelamentos, incluindo valores imediatamente acima e abaixo dos limites.
- Comparar as decisões com os defeitos conhecidos dos cenários sintéticos, registrando falsos positivos e falsos negativos. Evitar ajustar os critérios apenas para fazer os casos de referência passarem.

## Sequência de implementação

Manter os três blocos:

1. Casos sintéticos, qualidade e honestidade diagnóstica.
2. Regras de segurança, bloqueios e aprovações.
3. Calibração simulada, configurações, reversão e integridade.

Corrigir a migração SQLite na fundação. Definir os contratos de qualidade e segurança antes de integrar recomendações. Validar o fluxo completo, incluindo histórico e reabertura, no terceiro bloco.

## Decisões que devem ser preservadas

Manter a separação entre cálculos, regras, persistência, serviço e interface; a imutabilidade dos registros; o versionamento dos algoritmos; os arquivos opacos; a ausência de escrita automática no DSP; e a distinção entre verificação técnica e aprovação do usuário.

As ADR-201, 203, 206, 209 e 210 têm direção arquitetural adequada. A ADR-204 pode ser mantida com integridade reforçada. A ADR-205 precisa de adaptações explícitas no serviço. A ADR-208 necessita ampliar a detecção. A ADR-207 exige correção e a ADR-202 merece revisão metodológica na spec.

## Encaminhamento

Revisar `plan.md` e `data-model.md`, corrigindo os problemas identificados e conferindo a aderência aos FR-201 a FR-222, INV-201 a INV-210 e SC-201 a SC-207.

Preservar as decisões válidas. Quando uma correção exigir mudança normativa da spec ou das regras canônicas, seguir o processo formal do Arkan Core.

Apresentar as ADRs revisadas, a matriz de rastreabilidade atualizada e os critérios de teste correspondentes antes de iniciar a implementação.


---

## Adendo de revisão — teste de comunicação ChatGPT → Claude (2026-10-17)

> **Nota técnica não normativa, distinta da revisão original acima.** Registrada pelo ChatGPT no papel de gerência/revisão previsto na JV-D045. Não constitui decisão do desenvolvedor, autorização Arkan Nível A/B, aceite G3 ou instrução para alterar código, requisitos ou spec.

**JV-T228 — pendência P1:** a avaliação de segurança dos casos S1/S2/S3 usa a alteração candidata e os dados de equipamento declarados no manifesto, e não valores das medições. Atribuir sua derivação a uma medição apenas por compartilhar o canal criaria proveniência artificial. É preciso decidir como representar a entrada documental verificável no modelo de proveniência antes de implementar a cadeia; o hash preserva a integridade do arquivo, mas, isoladamente, não estabelece a relação entre registros. Decisão normativa reservada ao desenvolvedor.

**Teste do canal:** Claude, quando consultar este documento no fluxo normal de trabalho, confirme que leu o adendo. A publicação desta nota não notifica nem executa automaticamente a sessão do Claude. Não iniciar T228 ou T230 com base nela.
