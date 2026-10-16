# Proposta de correção pontual — três defeitos de implementação (NÃO APLICADA)

> **Proposta para aprovação expressa antes de qualquer alteração em `src/`.** Nenhum arquivo de `src/` foi modificado no repositório. Não mexe em σ̂, portão de qualidade nem limiares (a decisão metodológica do F-5 segue aberta e separada). 2026-10-16.
> Validação feita **numa cópia temporária** do commit `65b2898` (já removida): patch aplicado, suíte completa rodada.
> Arquivos desta pasta: `correcao-pontual.patch` (3 arquivos de `src/`, +26 −7), `test_regressao_formato_rew.py` (6 testes; ao aprovar, vai para `tests/`).

## Defeitos, causas e correções

### D-1 — Leitura do separador de milhar do REW (erro de implementação, gravidade alta)
- **Evidência real:** em REW 5.31.3 (en-US) toda frequência ≥ 1 kHz sai como `1,000.1222`. `rew_texto._campos` trata a vírgula como separador de campos; a linha `1,000.1222 73.647 -169.22` vira `[1, 000.1222, 73.647, -169.22]` e `ler_texto` guarda os três primeiros: frequência 1,0, nível 0,12, fase 73,6. Resultado: 51 884 de 54 614 pontos (95 %) lidos errado, em silêncio; só o portão básico, adiante, acusa.
- **Correção:** um número en-US com milhar e decimal (`[+-]?\d{1,3}(,\d{3})+\.\d+`) numa linha separada por espaço/tabulação tem as vírgulas removidas. **Exige o ponto decimal** para não confundir com vírgula decimal. Nada muda para os demais formatos (vírgula como separador, ponto e vírgula, tabulação).
- **Não coberto (declarado):** arquivo com vírgula decimal separado por espaço (localidades pt-BR do REW, **não verificado**) continua sem suporte; inteiros agrupados sem decimal (`1,000`) continuam como antes.
- **Ponto de spec que precisa de você:** o FR-002 do JV-V01 diz "tolerando … separadores espaço, tabulação, vírgula ou ponto e vírgula". A correção é coerente com a intenção (ler o REW) mas **acrescenta comportamento**; pelo Princípio I, convém uma **Clarification de nível B** no FR-002: "números en-US com separador de milhar e parte decimal são lidos como um só valor".

### D-2 — Mensagem de recusa incorreta (erro de implementação, gravidade média)
- **Evidência:** com frequências fora de ordem a recusa dizia "Refaça a medição cobrindo 200 Hz a 10 000 Hz", embora a medição estivesse boa e o problema fosse a leitura do arquivo.
- **Correção:** o conselho depende da causa (`Servico._conselho_do_portao`): fora de ordem → "costuma indicar um arquivo que o Jarvis não conseguiu ler direito (ou corrompido), e não uma medição ruim: confira a exportação do REW e guarde o arquivo"; valores inválidos → "exporte de novo como texto"; só faixa curta → o texto atual, sem mudança. A primeira parte da mensagem (itens que falharam) fica **igual**, e o teste existente `test_sessao.py:149` continua válido.

### D-3 — Borda de 24 pontos/oitava (erro de implementação, gravidade baixa)
- **Evidência:** uma grade com exatamente 24,0 ppo dá `densidade_suficiente = False` ("24.0 … mínimo 24") por ponto flutuante (23,9999…).
- **Correção:** `ppo` arredondado a 6 casas antes da comparação. O **limiar continua 24**; muda só o resultado em diferenças menores que 10⁻⁶.

## Impacto
- **Em dados reais:** os 10 pares de arquivos originais do conjunto joeglondon passam a ser lidos corretamente (0 pontos errados) e o braço A1 reproduz o A2 (mesma sugestão e mesmo portão em 10/10).
- **No produto:** casos simulados e V01 não têm vírgula de milhar; comportamento idêntico. Suíte na cópia temporária: **217 passando (211 + 6 novos), 1 xfail esperado**; antes do patch, 4 dos 6 novos falham como deve (os outros 2 protegem comportamento antigo).
- **Riscos:** (1) localidade com vírgula decimal e separação por espaço, não coberta; (2) a mensagem nova é texto, sem efeito em lógica; (3) nenhum limiar, regra ou resultado de diagnóstico muda além de destravar a leitura.

## Testes de regressão (arquivo desta pasta)
1. milhar en-US não corrompe as frequências (linhas sintéticas no formato do REW; nenhum dado de terceiros copiado);
2. exportação linear completa (≈ 54 600 pontos) lê inteira e passa no portão básico;
3. separadores antigos continuam valendo;
4. frequências fora de ordem: a mensagem lista o que falhou, explica a causa provável e **não** manda refazer a medição;
5. faixa curta: continua pedindo "Refaça a medição cobrindo 200 Hz a 10 000 Hz";
6. 24,0 ppo exatos contam como suficientes; 23 ppo, não.

## O que preciso de você
Aprovação expressa (Nível B) para: (a) aplicar o patch em `src/` e adicionar os testes, numa **branch própria** (sugestão: `claude/correcao-pontual-formato-rew`, a partir de `claude/busy-bohr-25s6e5`); (b) a Clarification do FR-002 (spec do JV-V01). Sem merge na `main`; o G3 do bloco 1 segue separado.
