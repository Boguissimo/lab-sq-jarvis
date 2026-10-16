# Como verificar o JV-V02 (resumo)

1. `git pull` na branch da feature; `INICIAR-JARVIS.bat` (o ambiente do V01 é reaproveitado; não há dependências novas).
2. **Primeira abertura** (ADR-207): o banco do V01 é reconhecido e migrado. Confira que surgiu `jarvis.antes-v02-<data>.db` na pasta de dados e que as sessões antigas continuam no Histórico, com a análise marcada "reconstruída pelas regras 1.0".
3. **Bloco 1**: em "2. O que preciso medir", escolha cada caso na lista e siga os passos:
   - REF-001-B: `confirmada`, incerteza maior.
   - N1: vale numa via, sem teste de polaridade.
   - N2: "não dá para concluir".
   - N3: `comprometida`, com a via e a faixa da mudança.
   - N4: só magnitude, fase recusada.
   - N5: "nada a alterar" sugerido.

   Reabra cada sessão e confira que nada mudou.
4. **Bloco 2**: em qualquer recomendação, confira a "Verificação de segurança": regras, provisórios, limitações e admissibilidade.
5. **Bloco 3**: as quatro variantes REF-002-A (etapa de calibração tipo ATM): objetivo, limites, antes/depois e resultado. Depois:
   - guarde arquivos de ajuste de exemplo;
   - abra uma sessão nova e confira a última configuração da sessão anterior;
   - peça a reversão e confira os três desfechos, sempre como "reversão documentada" (restauração física não confirmada).
6. Feche e reabra: as sessões do V01 e do V02 (investigação e etapa) aparecem no Histórico.
7. Máquina de QA: `QT_QPA_PLATFORM=offscreen python -m pytest` (esperado: suíte do V01 + V02 passando). `08-qa/validacao-limiares.md` sai da varredura do SC-208.
