# Como verificar o JV-V02 (resumo)

1. `git pull` na branch da feature; `INICIAR-JARVIS.bat` (o ambiente do V01 é reaproveitado; não há dependências novas).
2. **Bloco 1**: em "2. O que preciso medir", escolha cada caso na lista e siga os passos:
   REF-001-B (confirmada, incerteza maior); N1 (vale numa via, sem teste de polaridade); N2 ("não dá para concluir");
   N3 (`comprometida`); N4 (só magnitude, fase recusada); N5 ("nada a alterar" sugerido).
3. **Bloco 2**: em qualquer recomendação, conferir a "Verificação de segurança" (regras, provisórios, limitações).
4. **Bloco 3**: caso REF-002-A (etapa de calibração tipo ATM): objetivo, limites, antes/depois, resultado;
   guardar arquivos de ajuste de exemplo; pedir reversão e conferir os três desfechos.
5. Fechar e reabrir: as sessões do V01 e do V02 aparecem no Histórico.
6. Máquina de QA: `QT_QPA_PLATFORM=offscreen python -m pytest` (esperado: suíte do V01 + V02 passando).
