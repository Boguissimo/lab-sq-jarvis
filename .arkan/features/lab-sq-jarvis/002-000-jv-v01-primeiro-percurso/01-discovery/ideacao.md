# Ideação — 002-000-jv-v01-primeiro-percurso (incremento JV-V01)

> **Projeto**: lab-sq-jarvis | **Peso**: Code | **Superfície crítica**: sim | **Data**: 2026-10-15
> **Status**: aprovada — escopo autorizado pelo desenvolvedor em 2026-10-15 (JV-D042): “Autorizo a
> fundação necessária e o primeiro incremento executável JV-V01, usando PySide6 com pyqtgraph”.
> **Marco**: 1 (Protótipo técnico). **Features atravessadas**: partes de F002 a F008 (feature map v4).

## Contexto

Primeiro percurso executável do Jarvis. O desenvolvedor quer, no Windows: abrir o programa,
importar o caso simulado REF-001-A, ver os gráficos, receber a explicação da hipótese com base nos
cálculos, registrar o teste simulado, comparar o resultado e recuperar a sessão depois de fechar o
programa. A conversa com IA fica para o JV-V03.

## Decisões Tomadas

| Decisão | Fundamentação | Alternativas descartadas |
| --- | --- | --- |
| Interface em PySide6 + pyqtgraph | JV-D011 aprovada | NiceGUI |
| Explicações geradas por regras implementadas, sem IA | IA entra no JV-V03; o desenvolvedor pediu que isso fique claro | IA já no V01 |
| Aviso permanente: demonstração com dados simulados, não orienta ajustes reais no carro | pedido do desenvolvedor; JV-D025 | — |
| Importação do formato texto de resposta em frequência no estilo do REW (frequência, nível, fase), com um manifesto do caso para metadados | o formato de texto é o caminho mais simples e cobre magnitude e fase; o REW não grava no texto a referência temporal, por isso o manifesto | WAV de resposta ao impulso já no V01 (fica para completar a F004) |
| Percepção marcada `não aplicável` por padrão no caso simulado, com opção `simulada` | JV-D035: não exigir experiência auditiva inventada | percepção obrigatória |
| Modo calibração visível, mas desativado até o JV-V04 | o V01 cobre só a investigação; mostrar o que vem depois sem fingir que existe | esconder o modo |
| Decisão sem intervenção (“nada a alterar”, “solicitar dados adicionais”) disponível desde o V01 | JV-D038; custo baixo e evita experimento fictício | só no V02 |
| Lançamento por arquivo `.bat` que prepara um ambiente Python na primeira vez | executável único não pode ser gerado a partir deste ambiente Linux; padrão já usado no Rygar (`JOGAR.bat`) | instalador |
| Limiares das regras de diagnóstico **provisórios** e validados só em casos simulados | JV-D025, JV-D042 | tratá-los como critérios |

## Dúvidas Resolvidas

| Pergunta | Resolução |
| --- | --- |
| O formato de texto do REW é conhecido com certeza? | Não: a estrutura vem de fontes secundárias. O importador é tolerante (linhas de comentário com `*`, separadores espaço, tabulação, vírgula ou ponto e vírgula) e a confirmação com um arquivo real do REW fica para o JV-V04 |
| O teste simulado pode ser “aplicado”? | Sim, como registro: no caso simulado, o desenvolvedor marca a alteração como aplicada e importa a medição “depois” fornecida pelo caso |

## Síntese

- **Nome canônico**: JV-V01 — Primeiro percurso.
- **Definição**: aplicativo desktop que conduz uma sessão de investigação sobre o caso simulado
  REF-001-A, do arquivo importado ao veredito, guardando tudo para retomar depois.
- **Escopo**: gerador determinístico do REF-001-A; importação de texto de resposta em frequência com
  manifesto; cálculos do caso (resposta complexa, soma prevista, soma de potências, diferença de
  fase, atraso equivalente, comparação previsto × medido); verificação básica de qualidade e de
  referência temporal; regras de indício e hipótese para cancelamento no cruzamento; teste de
  diagnóstico de polaridade com previsão, critério, classificação de segurança, receita com SEG-08 e
  receita inversa quando houver valor anterior registrado; veredito; decisão manter/reverter;
  decisão sem intervenção; percepção `não aplicável`/`simulada`; banco SQLite com originais por
  hash, cadeia, configurações declaradas com parâmetros, diário só de acréscimo e rotina de
  integridade; interface com os cinco passos e histórico; lançador `.bat`.
- **Fora do escopo**: IA (JV-V03); casos N1–N5 e REF-001-B (JV-V02); suíte SEG completa (JV-V02);
  modo calibração e medições reais (JV-V04); etapas de calibração (JV-V02/V05); arquivo do PC-Tool
  (JV-V02 arquiva, F019 lê); WAV de resposta ao impulso.

## Obrigações da Superfície Crítica

| Pergunta | Resposta |
| --- | --- |
| Política aplicável | P1, P2, P3, P4, P6, P7 da constituição v0.4.0; `regras-de-seguranca.md` v0.4.0 |
| O incremento recomenda algo que afete potência, excursão, corte ou ganho? | Não. A única recomendação é inversão de polaridade (classe “não sensível”), com o procedimento SEG-08 |
| Como se evita parecer orientação real? | aviso fixo na janela, rótulo “simulado” em medições e percepção, texto do resultado lembrando que o caso não se generaliza ao carro (JV-D025) |
| Como se protege a cadeia? | originais por hash e só inserção; previsão registrada antes da medição “depois”; rotina de integridade testada |
| Valores provisórios | os limiares do diagnóstico e do critério de aceite aparecem como provisórios na própria tela |
