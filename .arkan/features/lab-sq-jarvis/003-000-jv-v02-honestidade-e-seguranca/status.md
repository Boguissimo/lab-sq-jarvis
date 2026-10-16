---
status: em-desenvolvimento
fase-atual: 07-implementation
projeto: lab-sq-jarvis
atualizado-em: 2026-10-15
peso: Code
superficie-critica: sim
---

# 003-000-jv-v02-honestidade-e-seguranca

JV-V02 — Honestidade e segurança: casos N1 a N5 e REF-001-B, recusa sem referência temporal, regras SEG, etapa de calibração simulada, configuração arquivada e reversão

## Candidato interno 1.0 (2026-10-16) — estado e proposta

**Prioridade definida por Fabrício:** consolidar um Jarvis utilizável por ele antes de qualquer participação externa (sem beta, sem Fernando/carro, sem merge na `main`). Investigação acústica preservada e suspensa.
**Estado real (verificado):** 211 testes passando + 1 xfail na branch de trabalho; blocos 2 e 3 do V02 não implementados; G3 do bloco 1 parcial. A interface entrega o percurso completo **só com casos simulados**; não existe importação de medição real (exige `manifesto.json` escrito à mão), o aviso/título/gráficos dizem "simulado" sempre, o leitor do REW lê errado 95 % dos pontos de exportações reais (correção pronta na branch `claude/correcao-pontual-formato-rew`, não integrada), a receita de polaridade é fixa em "tweeter esquerdo" e manifestos incompletos geram exceção sem tratamento.
**Proposta:** Fase 5 do `tasks.md` (T250–T259), por dependência: T250 → T251 → E5 (T252, Nível A) → T253–T256 → T257 → T258 → G3 (T259). Primeiro pacote com autorização Nível B: T250 + T251. Nada foi alterado em `src/` ou na spec.

