# Spec — 002-000-jv-v01-primeiro-percurso (JV-V01)

> **Status**: aprovada no escopo autorizado (JV-D042) | **Data**: 2026-10-15
> Siglas: **REW** — Room EQ Wizard; **DSP** — processador digital de sinais; **SEG** — regra de
> segurança; **LR4** — filtro Linkwitz-Riley de 4ª ordem; **G1/G2/G3** — gates.

## Cenários de Usuário

**US-01 — Percorrer uma investigação simulada.** Como desenvolvedor, quero abrir o Jarvis, iniciar
uma sessão de investigação, importar o caso REF-001-A, ver os gráficos e entender por que o Jarvis
suspeita de polaridade invertida, para aprender o mecanismo com dados de verdade conhecida.

- Dado o programa aberto, quando inicio uma sessão e importo o caso, então vejo as três medições
  “antes”, o resultado da verificação de qualidade e de referência temporal, e os gráficos de
  magnitude e fase.
- Dado o caso importado, quando abro “O que os dados sugerem”, então leio indícios e hipóteses em
  linguagem simples, cada número com a origem (cálculo) e o aviso de que a explicação vem de regras.

**US-02 — Registrar o teste e ver o resultado.** Como desenvolvedor, quero registrar o teste
proposto, ver a previsão antes, importar a medição “depois” e receber um veredito comparado.

- Dado o teste proposto, quando o registro, então a previsão e o critério ficam gravados antes de
  qualquer medição “depois”.
- Dada a medição “depois” importada, então vejo antes, previsto e depois no mesmo gráfico e o
  veredito com a incerteza declarada.

**US-03 — Decidir sem intervir.** Como desenvolvedor, quero poder encerrar com “nada a alterar” ou
“solicitar dados adicionais”, com a minha justificativa, sem criar experimento.

**US-04 — Retomar.** Como desenvolvedor, quero fechar o programa e, ao abrir de novo, encontrar a
sessão no histórico com tudo o que foi feito.

## Requirements

| ID | Requisito | Teste |
| --- | --- | --- |
| FR-001 | Gerar o caso REF-001-A de forma determinística: LR4 em 3 000 Hz, alto-falantes ideais, 1,00 m, tweeter com polaridade invertida na fiação, grade de 1/48 de oitava de 20 Hz a 20 kHz; arquivos `medio`, `tweeter`, `soma-antes`, `soma-depois` e manifesto | `test_ref001.py` |
| FR-002 | Importar texto de resposta em frequência (frequência, nível em dB, fase em graus), tolerando comentários com `*` e separadores espaço, tabulação, vírgula ou ponto e vírgula; recusar arquivo sem dados válidos com mensagem simples | `test_rew_texto.py` |
| FR-003 | Guardar cada arquivo importado no cofre pelo hash SHA-256, sem alterar nem substituir | `test_persistencia.py` |
| FR-004 | Verificar qualidade básica (frequências crescentes, faixa coberta, valores finitos, mesma grade) e compatibilidade de referência temporal pelo manifesto; sem referência compatível, recusar fase, atraso e soma prevista | `test_calculos.py`, `test_sessao.py` |
| FR-005 | Calcular: resposta complexa, soma complexa prevista, soma de potências, região de sobreposição, diferença de fase (média e dispersão circulares), atraso equivalente, comparação previsto × medido; cada cálculo registrado com algoritmo, versão, parâmetros e entradas por hash | `test_calculos.py` |
| FR-006 | Regras de indício: I-1 cancelamento entre vias; I-2 oposição de fase constante. Regras de hipótese ordenadas: polaridade invertida; desalinhamento temporal; filtros com fases diferentes — cada uma com o que a confirmaria ou refutaria | `test_regras.py` |
| FR-007 | Propor teste de diagnóstico de uma variável (polaridade do tweeter no DSP), com previsão calculada, critério de aceite provisório, classe de segurança, receita com SEG-08 e disponibilidade da receita inversa (JV-D040) | `test_sessao.py` |
| FR-008 | Aceitar a medição “depois” só após a previsão registrada; emitir veredito `confirmada`, `refutada` ou `inconclusiva` com incerteza | `test_sessao.py` |
| FR-009 | Registrar decisão manter/reverter; reverter mostra a receita inversa só se o valor anterior estiver registrado, senão “reversão não garantida” | `test_sessao.py` |
| FR-010 | Registrar decisão sem intervenção (`nada a alterar`, `solicitar dados adicionais`) com fundamentação obrigatória, sem experimento | `test_sessao.py`, `test_persistencia.py` |
| FR-011 | Percepção com origem `não aplicável` (padrão no caso simulado), `simulada` ou `real` | `test_sessao.py` |
| FR-012 | Persistir sessão, cadeia, configurações e diário em SQLite; reabrir o programa e recuperar a sessão com seu estado | `test_sessao.py`, `test_interface.py` |
| FR-013 | Interface com aviso fixo de demonstração simulada e explicações por regras; cinco passos e histórico; modo calibração visível e desativado | `test_interface.py` |
| FR-014 | Lançador `INICIAR-JARVIS.bat` que prepara o ambiente na primeira vez e explica cada falha conhecida em linguagem simples | revisão (G2) + roteiro no Windows (G3) |

## Invariantes

- INV-001: arquivo original nunca é alterado nem substituído. Teste: `test_persistencia.py::test_original_imutavel`.
- INV-002: diário só aceita inserção. Teste: `test_persistencia.py::test_diario_so_insercao`.
- INV-003: toda conclusão experimental aponta para experimento; toda decisão sem intervenção tem fundamentação e não aponta para experimento. Teste: `test_persistencia.py::test_integridade_*`.
- INV-004: previsão gravada antes da medição “depois”. Teste: `test_sessao.py::test_depois_sem_previsao_recusado`.
- INV-005: sem referência temporal compatível, nenhum cálculo de fase, atraso ou soma prevista é produzido. Teste: `test_sessao.py::test_sem_referencia_temporal`.
- INV-006: mesmas entradas, mesmos resultados. Teste: `test_ref001.py::test_deterministico`, `test_calculos.py::test_reprodutivel`.
- INV-007: o Core do Arkan não é alterado. Teste: `diff -r` registrado no QA.

## Critérios de Sucesso

- SC-001: percurso completo REF-001-A → veredito `confirmada`, com a cadeia íntegra. Instrumento: `test_sessao.py::test_percurso_completo`.
- SC-002: o mesmo percurso pela interface, fechando e reabrindo. Instrumento: `test_interface.py`.
- SC-003: cálculos analíticos: LR4 vale −6,02 dB em 3 kHz por via; soma correta plana (desvio ≤ 0,01 dB); soma invertida com vale ≥ 30 dB na grade. Instrumento: `test_calculos.py`.
- SC-004: o desenvolvedor abre no Windows com dois cliques e percorre a sessão (G3). Instrumento: roteiro em `COMO-EXPERIMENTAR.md`.

## Limites declarados

- Caso simulado ideal: não representa o carro (JV-D025).
- Limiares provisórios: I-1 (soma ≥ 6 dB abaixo da soma de potências na sobreposição), I-2 (média
  circular ≥ 160° e dispersão ≤ 15°), sobreposição (vias a até 6 dB uma da outra), critério de aceite
  (RMS previsto × medido ≤ 1 dB e máximo ≤ 2 dB entre 1 e 10 kHz; nível no vale sobe ≥ 10 dB).
- Formato de texto do REW: estrutura de fontes secundárias, a confirmar com arquivo real (JV-V04).
