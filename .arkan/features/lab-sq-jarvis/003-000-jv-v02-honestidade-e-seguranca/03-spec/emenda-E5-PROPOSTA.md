# Emenda E5 — PROPOSTA de redação (NÃO APROVADA; não altera `spec.md`; nada foi implementado)

> **Estado:** rascunho para decisão de Fabrício (Nível A). Até a aprovação, `spec.md`, o código e os testes não mudam e as tasks T253–T259 não começam. 2026-10-16.
> **Origem:** avaliação do estado do produto (`status.md`), investigação de desempenho (F-1 a F-10) e entrega de T250/T251. A emenda **não define o escopo do Jarvis 1.0** e **não rebaixa os blocos 2 e 3** do V02. **F-5 (papel do σ̂ e do portão) permanece em aberto**; esta emenda não o decide.
> **Não muda:** σ̂, portão, limiares, regras SEG, precedência do veredito, detector de mudança.

## E5-a — Importação guiada de medições reais
**FR-224 (proposto).** O usuário pode importar medições reais do REW (texto) **sem escrever `manifesto.json`**: escolhe os arquivos de via A, via B e soma, e declara, por medição, o tipo e a identificação da referência temporal, a taxa de amostragem, a posição do microfone, a suavização e o canal; e declara a configuração do DSP (origem `declarado`). O programa grava essa declaração na **mesma estrutura** que o T251 valida, guarda os originais por hash (FR-003) e executa o portão básico (FR-004) antes de aceitar.
**FR-225 (proposto).** **Nenhum metadado é preenchido por presunção.** Campo não informado fica ausente e as consequências já previstas se mantêm (sem referência temporal: fase, atraso e soma prevista recusados, FR-205). Nenhum cálculo novo: reutiliza FR-004/FR-005.
**FR-226 (proposto).** Uma importação que falha não deixa a sessão com medições pela metade; mensagens em linguagem simples (T251).
*Testes previstos:* `test_sessao.py` (importação real, recusas, atomicidade), `test_interface.py` (diálogo guiado sem JSON). *Critério:* uma sessão real é criada, analisada e reaberta sem editar arquivo à mão.

## E5-b — Proveniência real × simulada
**FR-227 (proposto; altera FR-013 do V01).** O aviso fixo da interface passa a depender da **proveniência declarada** das medições da sessão: só casos simulados → aviso atual; ao menos uma medição real → aviso de dado real ("regras provisórias, testadas só em casos simulados; resultado exploratório; não substitui o julgamento"), com o mesmo destaque; sessão mista → rotulada como mista. **O aviso nunca desaparece.** Título da janela, títulos dos gráficos e tabela de medições acompanham. A origem vem da declaração, nunca de inferência pelo nome do arquivo.
**INV-216 (proposta).** Dado real nunca é rotulado como simulado, nem o inverso.
**INV-217 (proposta).** O programa não preenche por presunção nenhum metadado de aquisição.
*Testes previstos:* `test_interface.py` (aviso, título e gráficos por proveniência).

## E5-c — Hipóteses quando o portão restringe — **CONDICIONADO à revisão da F-5; sem texto final**
Fato registrado na investigação: com σ̂ "não estimável" (grade linear de exportação do REW) a sugestão é "solicitar dados", mas as hipóteses continuam listadas e a de "interferência/reflexão" aparece como "mais provável"; o FR-203 só proíbe ordenar hipóteses com qualidade **reprovada**. Opções para decidir **depois** da revisão metodológica da F-5:
- **A.** manter como está;
- **B.** apresentar as hipóteses como "indícios não confirmados", sem "mais provável", quando σ̂ for não estimável;
- **C.** aguardar a revisão da F-5 (recomendação), sem alterar nada antes.

## E5-d — Canal e lado derivados do declarado
**FR-228 (proposto).** O teste de polaridade, a receita e a reversão usam o **canal e o lado declarados da via B** e o valor anterior da configuração declarada. Sem essa informação o programa **não propõe** o teste (pede o canal) ou declara "reversão não garantida" (JV-D040). Nunca assume "tweeter esquerdo".
*Testes previstos:* `test_sessao.py` (lado direito, nomes de canal diferentes, canal ausente).

## E5-e — Orientação de exportação do REW
**FR-229 (proposto).** Texto de ajuda na importação: exportar como texto com frequência, nível e fase; as três medições com a mesma grade e a mesma referência temporal; grade e suavização declaradas. **Sem afirmar** opções do REW não verificadas: o texto é conferido no REW do desenvolvedor antes de entrar (`[confirmar]`).

## Rastreabilidade e perguntas
Tasks: T252 (esta emenda) → T253 (E5-a), T254 (E5-b), T255 (E5-d), T256 (E5-c, só após F-5), T257 (E5-e e polimento). Nenhuma inicia sem sua ordem.
Decisões pedidas: (1) E5 dentro do V02 ou feature própria; (2) aprovação item a item (a, b, c, d, e); (3) opção do E5-c; (4) texto do aviso de dado real.
