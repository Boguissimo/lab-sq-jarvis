# Planejamento — bancada automatizada de validação (proposta, fora do JV-V02)

> **Status: proposta para decisão do desenvolvedor (Princípio VIII).** Não altera spec, limiares nem arquitetura do JV-V02; não cria requisito nem tarefa. Se aprovada, vira feature/incremento próprio com spec própria.

## 1. Objetivo
Executar por código, sem a interface, um conjunto de casos e comparar a saída do Jarvis (hipótese prioritária, qualidade, veredito, textos) com um **parecer de referência** de cada caso, produzindo um relatório reproduzível.

## 2. Regra de honestidade: três classes de caso, nunca misturadas
| Classe | Origem dos dados | O que o resultado prova |
| --- | --- | --- |
| **S — sintético** | gerado por código (REF-001, REF-003…) | só que o código se comporta como projetado (regressão); já existe |
| **I — inspirado em caso real** | sintético, escrito a partir de um relato/parecer real | cobertura de cenários plausíveis; **não é validação sobre medição real** |
| **R — medição real** | arquivo de medição (ex. REW) de carro/sala reais, com parecer externo | única classe que sustenta alegação de acerto com dados reais |

O relatório mostra a classe de cada linha e totais **por classe**; nunca soma S/I com R. Enquanto não houver casos R, o relatório diz "sem validação sobre medições reais".

## 3. Estrutura proposta (para discussão)
- `ferramentas/bancada/` (código) + `validacao/casos/<id>/` com: `medicoes/`, `declarado.json` (config, posição, referência temporal), `parecer.json` (parecer de referência), `origem.md` (fonte, data, autor do parecer, consentimento/anonimização).
- Execução pelo serviço (`Servico`), não pela janela; saída em JSON + Markdown em `08-qa/`.
- Parecer de referência **estruturado e versionado**: hipótese correta aceita (lista), hipóteses descartáveis, resposta esperada à pergunta "dá para concluir?", ação **proibida** (segurança), grau de certeza do parecerista.
- Mais de um parecerista por caso R quando possível; divergência entre pareceristas é registrada, não resolvida por média.

## 4. Métricas (três dimensões separadas, como na JV-D044)
1. **Precisão da medição:** qualidade/σ̂ e estimativas contra a referência quando houver verdade conhecida (só classes S/I, ou R com instrumento de referência).
2. **Precisão do diagnóstico:** hipótese prioritária ∈ aceitas; abstenção correta ("não dá para concluir") separada de erro; falsa confiança como métrica própria.
3. **Eficácia do ajuste:** só com antes/depois reais (classe R); fora do alcance inicial.
**Segurança nunca é relativizada:** qualquer ação proibida sugerida = falha, independente da média.

## 5. O que preciso de você (decisões, não urgentes)
1. Aprovar ou não abrir esta frente e em que incremento (sugestão: depois do G3 e do bloco 2, como feature própria).
2. Origem dos casos R: você tem medições reais exportadas (formato, quantas)? Os pareceres externos virão de quem e com que consentimento?
3. Formato do parecer de referência (item 3) e se a abstenção conta como acerto parcial.
4. Onde guardar dados reais (fora do repositório público? anonimização).

## 6. Passos que posso fazer sem decisão
- Esboçar o esquema JSON do caso e do parecer e rodar os casos S atuais pela bancada (sem dados reais), como protótipo descartável.
- Não vou criar casos "I" sem sua indicação da fonte, para não passarem por validação.
