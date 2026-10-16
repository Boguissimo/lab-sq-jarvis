# Revisão adversarial independente — Lab SQ Jarvis

> **Origem**: revisão externa (ChatGPT), recebida do desenvolvedor em 2026-10-15, a partir de `docs/revisoes/pedido-revisao-adversarial.md`. Base: commit `1f6b62d`. Transcrita como recebida; **ainda não aplicada**.
> **Conferência do agente** (2026-10-15), antes de qualquer aplicação:
> - **Lógica e textos:** A01 confirmado; o erro é da redação da E2, feita pelo agente. A09 confirmado nos dois deslizes de texto do `plan.md`. A08 é uma identidade matemática e não precisa de execução.
> - **Reproduzidos no código do V01:**
>   - A02: manifestos sem `id` nem taxa resultam "compatíveis".
>   - A04: `analisar` não consulta `qualidade_basica`, e a sobreposição de um ponto gera atraso 0 com `RankWarning`.
>   - A06: um arquivo órfão no cofre não entra no inventário, e a integridade não acusa nada.
> - **Coerentes com o código lido, sem execução:** A03, A05 e A07.

---

**Base:** commit `1f6b62d82980260fd7df0e2d663a255ae56b43ec`, branch `lab-sq-jarvis/003-000-jv-v02-honestidade-e-seguranca`.
**Natureza:** parecer anterior a `/arkan.tasks`; não constitui decisão JV-D, emenda normativa ou autorização de implementação.
**Método:** leitura estática da visão, briefing, proposta, feature map, constituição, decisões, regras SEG, artefatos do V01 e V02, código e testes existentes. Não houve execução independente dos testes nem medição real.

## Veredito

SEGUIR COM MUDANÇAS. Antes de decompor o V02 em tarefas, é preciso:
- resolver uma contradição normativa que torna impossível um critério de sucesso;
- corrigir rotas que permitem conclusões injustificadas no V01;
- separar a validação sintética da validade acústica real.

## Achados por gravidade

### A01 — CRÍTICO — REF-003-S1 exige o reforço que as regras proíbem
- **Onde:** `03-spec/spec.md`, linhas 28–32, 76, 100–105, 144 e 160–175; `regras-de-seguranca.md`, linhas 39–43 e 63–71; `04-architecture/plan.md`, linhas 169–181 e 340–345.
- **Problema:** FR-223 e SC-209 exigem que o REF-003-S1 (reforço positivo de EQ com equipamento sintético confirmado) seja admissível e aprovável em nível B. O FR-212, porém, deixa SEG-02, SEG-07 e SEG-09 sempre como "não verificável" e bloqueia os reforços que dependem delas. A SEG-07 se aplica expressamente a toda recomendação de reforço e, sem método de margem digital, determina bloqueio. A condição "equipamento confirmado" não verifica margem digital.
- **Cenário:** o S1 pede +1 dB de EQ, dentro dos limites de passo e de potência. O avaliador correto bloqueia por SEG-07, enquanto o teste obriga a admitir. Uma implementação que passe nesse teste estará descumprindo outra parte da spec.
- **Evidência:** incompatibilidade lógica direta dos textos canônicos, independente da implementação. S2 bloqueado e S3 com corte admitido não resolvem o S1.
- **Correção:** decidir formalmente entre duas opções, sem inventar exceção de simulação para liberar reforço:
  - (a) mudar o S1 para testar bloqueio e exercitar a aprovação B numa alteração sensível de risco decrescente;
  - (b) criar um caso admissível de risco crescente que não dependa das regras indisponíveis, justificando a aplicabilidade de cada SEG.
- **Muda spec ou regras?** Sim: FR-223/SC-209 ou regras canônicas, por escolha explícita. Não mudar a SEG-07 só para o teste passar.

### A02 — ALTO — Referência temporal declarada é tratada como sincronismo demonstrado
- **Onde:** `src/jarvis/calculos.py`, linhas 71–90; `src/jarvis/sessao.py`, linhas 161–196 e 223–230; `tests/test_calculos.py`, linhas 68–76; `proposta-consolidada.md`, linhas 212–220.
- **Problema:** `referencia_temporal` confere a igualdade dos rótulos de tipo, id, taxa e posição, mas aceita metadados ausentes quando estão ausentes em todos. Arquivos com `{"tipo":"loopback","id":"x"}` e posição textual igual podem passar sem uma referência física comum de verdade. A proposta também condiciona o cálculo ao mesmo sweep e ao mesmo estado do DSP, que essa função não verifica.
- **Cenário:** sweeps independentes, sem timing comum, recebem manifesto com o mesmo identificador copiado. O programa combina as fases, sugere polaridade invertida e apresenta uma soma prevista como se a referência tivesse sido conferida.
- **Evidência:** os conjuntos de comparação em `calculos.referencia_temporal` não exigem id nem taxa não nulos; o teste positivo só confere objetos de metadados idênticos.
- **Correção:**
  - distinguir "referência declarada" de "verificada";
  - exigir campos completos no primeiro filtro;
  - tratar arquivos externos sem protocolo verificável como insuficientes para conclusão de fase;
  - testar identificador ausente, taxa ausente, rótulo copiado, estados de DSP diferentes e aquisição incompatível.
- **Muda spec ou regras?** Possivelmente o FR-205 e o contrato de aquisição, se passar a exigir evidência adicional. Não requer afrouxar SEG.

### A03 — ALTO — Veredito do V01 não verifica comparabilidade acústica do "depois"
- **Onde:** `src/jarvis/sessao.py`, linhas 315–352 e 354–393; `tests/test_sessao.py`, linhas 17–36 e 54–66.
- **Problema:** `importar_depois(caminho)` com arquivo externo cria metadados mínimos, inclusive `referencia_temporal: {"tipo":"nenhuma"}` (linhas 332–335). `concluir()` pode emitir `confirmada` pela semelhança de magnitude com a previsão, sem conferir posição, ganho de aquisição e referência de nível. Para comparar só magnitude não é preciso referência temporal comum, mas as condições de nível e posição são necessárias. O plano do V02 reforça o detector de alteração, mas não deixa claro que a comparabilidade vale também para a decisão causal sobre a soma medida "depois".
- **Cenário:** o "depois" foi adquirido em outra posição do microfone ou com outro ganho, mas a curva coincide aproximadamente com a previsão. O programa pode confirmar uma causa que o protocolo não discriminou.
- **Evidência:** as condições de `concluir` usam RMS, diferença máxima, aumento do vale e `qualidade_depois_aprovada`, sem comparar posição, ganho ou nível do "depois". Os testes atuais não cobrem discrepâncias de aquisição posteriores.
- **Correção:**
  - exigir posição, ganho e nível comparáveis para confirmar causalidade;
  - distinguir melhora observada de confirmação causal;
  - incluir testes negativos com mudança desses metadados;
  - exigir referência temporal no "depois" só para conclusões que dependam de fase ou atraso.
- **Muda spec ou regras?** Sim, se introduzir precedência adicional no FR-207/208 e no INV-201.

### A04 — ALTO — O V01 registra reprovação básica, mas continua a analisar
- **Onde:** `src/jarvis/sessao.py`, linhas 134–158; `src/jarvis/calculos.py`, linhas 50–68 e 110–150; `tests/test_calculos.py`, linhas 79–84.
- **Problema:** `_importar_medicao` registra `qualidade_basica`, mas `Servico.analisar` só exige as três medições e a mesma grade, sem consultar o campo `aprovada` de cada medição. Assim, uma grade que não cubra de 200 Hz a 10 kHz pode chegar às hipóteses. Se a sobreposição tiver um único ponto, `diferenca_fase` faz uma regressão de primeiro grau sem amostras suficientes.
- **Cenário:** três arquivos com dez frequências só entre 2 995 e 3 005 Hz, com fase, têm a mesma grade. O motor avança, embora a verificação básica tenha reprovado a cobertura, e o ajuste de atraso pode ser degenerado.
- **Evidência:** `qualidade_basica` verifica cobertura; `analisar` não consulta o resultado; `np.polyfit(..., 1)` não tem pré-condição de amostras mínimas.
- **Correção:**
  - tornar obrigatório o gate básico;
  - exigir amostras suficientes para as estatísticas de fase e a regressão;
  - testar grades estreitas e sobreposição de um único ponto.
- **Muda spec ou regras?** Não: corrige uma implementação já coberta pelo FR-004 do V01 e pela honestidade do V02.

### A05 — ALTO — O simulador e o detector podem validar um ao outro sem testar a realidade
- **Onde:** `04-architecture/plan.md`, linhas 130–159, 235–249 e 275–281; `03-spec/spec.md`, linhas 54–68 e 145–158; `tests/test_calculos.py`, linhas 20–66; `tests/test_ref001.py`, linhas 8–25.
- **Problema:** o gerador fornece sinal e perturbação cuja "verdade" é conhecida pelo mesmo conjunto de hipóteses que orienta o detector. O estimador σ̂ supõe ruído aproximadamente independente entre bins. Ruído correlacionado, mudanças de janela, a resposta do habitáculo e o processamento do REW podem deixar σ̂ baixo mesmo com aquisição inadequada. O sucesso nos casos simulados mede coerência interna, não capacidade de acerto no Focus.
- **Cenário:** uma resposta medida com janela ou suavização desconhecida tem espectro pouco irregular e passa no portão. O erro importante de fase ou nível, causado por posicionamento ou reflexões, permanece, e o resultado `confirmada` é mais forte do que a evidência.
- **Evidência:** a ADR-202 reconhece que σ̂ não detecta ruído correlacionado; o SC-208 valida principalmente contra perturbações do próprio gerador; os testes do REF-001 usam o mesmo modelo LR4 da previsão.
- **Correção:**
  - manter os testes unitários e acrescentar oráculos independentes: vetores analíticos e casos construídos por outra implementação;
  - acrescentar testes metamórficos, ruído correlacionado, múltiplas reflexões, mudanças de janela e suavização, e medições reais quando disponíveis;
  - o SC-208 deve declarar que comprova só o desempenho no domínio simulado e registrar falsos positivos e negativos fora dele.
- **Muda spec ou regras?** Sim, para fortalecer o alcance e a redação do SC-208. Não autoriza adiantar medições reais para o V02.

### A06 — ALTO — Cofre por hash e banco não são uma operação atômica
- **Onde:** `src/jarvis/persistencia.py`, linhas 114–133 e 218–248; `tests/test_persistencia.py`, linhas 8–29; `04-architecture/data-model.md`, linhas 69–98.
- **Problema:** `guardar_original` copia para o cofre antes do INSERT no inventário. Se a operação falhar depois da cópia, a próxima chamada encontra o destino e devolve o hash na hora, sem inserir a linha que falta em `arquivo_original`. A rotina de integridade não varre o cofre físico em busca desses órfãos. `chmod` e gatilhos protegem contra alterações pelo caminho normal, não contra falha ou intervenção externa.
- **Cenário:** o processo cai entre `shutil.copyfile` e o INSERT; a próxima importação reutiliza o arquivo órfão e o inventário fica incompleto.
- **Evidência:** a ordem literal e o retorno antecipado em `persistencia.py:122–125`; os testes só cobrem a operação bem-sucedida e a adulteração posterior.
- **Correção:**
  - copiar para um temporário, conferir o hash do destino e mover de forma atômica;
  - reconciliar o inventário mesmo quando o arquivo já existe;
  - testar falha entre cada etapa;
  - detectar arquivos do cofre sem linha correspondente;
  - tratar "imutável" como política de preservação e detecção, não como impossibilidade física.
- **Muda spec ou regras?** Não; complementa o P2 e a integridade do V02.

### A07 — MÉDIO — Detector de mudança assume independência e confunde rótulo com posição real
- **Onde:** `03-spec/spec.md`, linhas 62–67 e 151–154; `04-architecture/plan.md`, linhas 235–249.
- **Problema:** o termo σΔ divide por `√n`, supondo amostras independentes dentro de cada banda. Pontos vizinhos de respostas acústicas costumam ser correlacionados, sobretudo com janela, suavização e reflexões. Dois manifestos com `posicao_microfone: "P1"` só declaram, sem verificar, que o microfone ficou no mesmo lugar.
- **Cenário:** o microfone é retirado e recolocado em P1, sem mexer no DSP. O novo posicionamento muda um nulo estreito, o detector interpreta a diferença como mudança extra e marca o teste de polaridade como `comprometida`.
- **Evidência:** a fórmula usa o n bruto, e o teste de comparabilidade se limita à igualdade literal dos metadados.
- **Correção:**
  - chamar a comparabilidade de "declarada";
  - exigir repetibilidade para conclusão causal;
  - testar reposicionamento sob o mesmo rótulo;
  - usar tamanho amostral efetivo ou repetição independente para estabelecer os limiares.
- **Muda spec ou regras?** Sim, nas definições do detector, se a classificação de comprometimento mudar.

### A08 — MÉDIO — O déficit de cruzamento não mede alinhamento ótimo
- **Onde:** `03-spec/spec.md`, linhas 68–75 e 112–113; `src/jarvis/calculos.py`, linhas 103–107 e 154–167.
- **Problema:** a métrica `max(0, soma de potências − soma medida)` usa a soma incoerente como referência, e não a máxima soma coerente nem uma curva-alvo. Duas fontes de mesma amplitude a 90° entre si podem dar déficit de 0 dB, mesmo desperdiçando soma potencial. O pior ponto de toda a região também pode amplificar uma nulidade isolada ou um erro de aquisição.
- **Cenário:** duas vias de amplitude A em quadratura: `|A + jA|² = 2A²`, exatamente a soma das potências. O déficit é 0, mas há diferença para a soma em fase, `|A+A|² = 4A²`.
- **Evidência:** identidade matemática, independente do simulador.
- **Correção:**
  - chamar o objetivo de "ausência de cancelamento abaixo da soma de potências", sem declarar alinhamento completo;
  - se a etapa pretende alinhar, exigir também uma métrica relativa ao máximo coerente ou a uma curva-alvo;
  - avaliar largura e persistência do vale.
- **Muda spec ou regras?** Sim, se o resultado da etapa continuar afirmando alinhamento ou calibração com base só nessa métrica.

### A09 — MÉDIO — A utilidade e o custo da governança não estão em disputa nos gates
- **Onde:** `01-discovery/vision.md`, linhas 14–39 e 43–54; `02-proposal/proposta-consolidada.md`, linhas 253–270; `02-proposal/feature-map.md`, linhas 28–53; `04-architecture/plan.md`, linhas 41–75.
- **Problema:** o VP-10 aceita a declaração positiva do desenvolvedor, e a comparação com REW + anotações simples é opcional. Assim, o método pode consumir mais trabalho do que poupa sem que nenhum gatilho objetivo reduza o escopo. O Constitution Check é majoritariamente documental. Há ainda dois deslizes no próprio commit:
  - `plan.md:54` ainda diz que E1 e R1 aguardam aprovação, embora o cabeçalho indique aprovação;
  - `plan.md:47` enumera uma matriz que omite os IDs acrescentados depois, FR-223 e SC-209.
- **Cenário:** preencher etapas, aprovações e rastreio consome mais tempo do que medir, testar e anotar no REW. Mesmo assim o VP-10 é dado como atendido pela satisfação do desenvolvedor, e nenhum gate detecta a perda de eficiência.
- **Evidência:** a comparação é opcional no VP-10; as divergências textuais do plano R1.1 são verificáveis.
- **Correção:**
  - cronometrar duas ou três tarefas representativas com o Jarvis e com REW + planilha ou notas;
  - comparar erros, esforço de entrada, retomada correta e manutenção;
  - definir um limite de complexidade para interromper funcionalidades que não melhorem o trabalho pessoal.
- **Muda spec ou regras?** Não para testar o valor; só se o VP-10 for reescrito formalmente.

## O que não consegui verificar

- Não executei o `pytest`, a aplicação PySide6 nem o REW. Os 45 testes do V01 estão relatados no QA, mas não foram reproduzidos nesta revisão.
- O V02 ainda não tem código no commit analisado. As falhas apontadas nele são contradições e riscos previstos, não erros observados em execução.
- Não examinei o banco verdadeiro no Windows, seu journal ou WAL, as permissões reais nem o backup de migração.
- Não examinei medições reais do Focus, arquivos reais do REW, configurações do HELIX nem fichas dos componentes instalados. O leitor do V01 admite que o formato do REW foi inferido de fontes secundárias (`src/jarvis/rew_texto.py:1–6`).
- Não fiz experimento de repetibilidade com reposicionamento do microfone, nem comparação controlada de produtividade contra REW + planilha.

## Pressupostos contestados

1. Metadados iguais não provam aquisição sincronizada nem alteração isolada no DSP.
2. Um teste sintético que recupera um defeito injetado não demonstra validade diagnóstica num veículo real.
3. Passar por um conjunto de regras sem modelos completos de potência, excursão, margem e exposição não garante segurança. Aplicar a alteração manualmente no DSP não elimina o risco da orientação.
4. Déficit zero em relação à soma de potências não significa alinhamento ótimo nem resposta desejável.
5. Hash e gatilhos protegem o fluxo normal e detectam adulteração; não tornam arquivos fisicamente indestrutíveis nem operações automaticamente atômicas.
6. Gates e documentação não demonstram valor pessoal. É possível formalizar muito bem um processo menos eficiente do que a alternativa simples.

## Encaminhamento, sem aplicação automática

- **Bloqueador antes de `/arkan.tasks`:** resolver o A01 por decisão explícita do desenvolvedor.
- **A02 a A04 e A06:** precisam de testes negativos e contratos de integridade.
- **A05:** deve impedir qualquer alegação de validação para o carro.
- **A07 e A08:** exigem decisão sobre a semântica normativa.

Este parecer não aprova alterações de spec, regras SEG, código ou limiares; qualquer aplicação deve passar pelo Princípio VIII do Arkan Core.
