# Como experimentar o JV-V01 (Lab SQ Jarvis)

> Demonstração com **dados simulados** (caso REF-001-A). As explicações vêm de regras, não de IA, e
> **não servem para orientar ajustes reais** no carro. Este é o seu teste G3 no Windows (SC-004):
> o programa ainda não foi executado no Windows por quem o escreveu.

## Antes de começar
- Windows com **Python 3.11 a 3.14** instalado (marque "Add Python to PATH") e internet na primeira vez.
- Se algo falhar, a janela preta explica em linguagem simples; mostre-a ao Claude.

## Roteiro (cerca de 10 minutos)
1. **Dois cliques em `INICIAR-JARVIS.bat`.** Na primeira vez ele prepara o ambiente (alguns minutos).
   Esperado: abre a janela "Lab SQ Jarvis — JV-V01 (demonstração com dados simulados)" com o aviso
   de dados simulados sempre visível.
2. **1. O que estou percebendo** — deixe a percepção como "não aplicável" (ou escolha "simulada" e
   escreva algo) e clique **Começar a sessão**.
3. **2. O que preciso medir** — clique **Importar o caso REF-001-A**. Esperado: três medições "antes",
   verificação de qualidade e de referência temporal, gráficos de magnitude e fase. Clique **Analisar as medições**.
4. **3. O que os dados sugerem** — leia indícios (cancelamento entre vias; fase em oposição) e a
   hipótese de **polaridade invertida** em primeiro lugar, cada número com sua origem. Abra
   **Ver a cadeia por trás desta análise**.
5. **4. Qual passo dar** — **Ver o teste proposto** (previsão e critério gravados antes de medir;
   receita; reversão). Clique em **Registrar: apliquei o teste**.
   (Para testar a alternativa: em outra sessão, use **Nada a alterar** ou **Solicitar dados adicionais** com justificativa.)
6. **5. O que mudou** — **Importar a medição "depois"**, registre a percepção e veja o veredito
   (esperado: **confirmada**) com antes, previsto e depois no mesmo gráfico. Decida **Manter** ou **Reverter**.
7. **Feche o programa e abra de novo.** Em **Histórico**, a sessão deve estar lá; **Abrir a sessão selecionada**
   mostra tudo o que foi feito.

## O que me contar
- Em que passo você travou ou ficou em dúvida? Algum texto confuso?
- O `.bat` funcionou de primeira? Qual mensagem apareceu se não?
- Os gráficos e o veredito fizeram sentido?

## Limites
Caso simulado ideal (não representa o carro); limiares provisórios; formato de texto do REW a confirmar
com arquivo real (JV-V04). Dados em `%LOCALAPPDATA%\LabSQJarvis` (ou pasta em `JARVIS_DADOS`).
