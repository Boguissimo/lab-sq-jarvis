---
status: em-desenvolvimento
fase-atual: 07-implementation
projeto: lab-sq-jarvis
atualizado-em: 2026-10-17
peso: Code
superficie-critica: sim
---

# 003-000-jv-v02-honestidade-e-seguranca

JV-V02 — Honestidade e segurança: casos N1 a N5 e REF-001-B, recusa sem referência temporal, regras SEG, etapa de calibração simulada, configuração arquivada e reversão

## Candidato interno 1.0 (2026-10-16) — estado

**Diretriz de Fabrício:** amadurecer um produto sólido, **sem prazo artificial; a liberação do Jarvis 1.0 depende de evidências e validação humana**; investigação preservada (suspensão operacional temporária); escopo mínimo é só referência; blocos 2 e 3 do V02 permanecem no plano original; F-5 em aberto; sem contato externo, sem beta, sem merge na `main`.
**Feito (Nível B, T250 + T251):** correção pontual do REW e Clarification C-1 integradas à branch de trabalho (`7dfa2b2`) e entrada de arquivos sem exceção solta e com mensagens em português. Suíte: **242 passando + 1 xfail**. Nenhuma mudança em diagnóstico, σ̂, portão ou limiares.
**Proposto, não aprovado:** emenda E5 (`03-spec/emenda-E5-PROPOSTA.md`). **Não iniciado:** T253–T259 (aguardam avaliação conjunta). **G3 do bloco 1 (T223): ACEITO por Fabrício em 2026-10-17** (operacional no Windows; ressalvas de apresentação em `08-qa/g3-bloco1-parcial.md`; não é validação acústica). Blocos 2 e 3 (T224–T242) permanecem no planejamento original, não iniciados.

## Bloco 2 (segurança) — andamento (2026-10-17)
**T224 e T225 concluídas** (Nível B autorizado por Fabrício; só `seguranca.py` e `test_seguranca.py`): regras SEG-01/03/04/05/06/13 e SEG-02/07/09 `não verificável`, limites da v0.4.0 preservados e provisórios identificados; propriedade de 1 000 casos. Suíte: 292 passando + 1 xfail (Linux). **T226 e T227 concluídas** (Nível B; aprovação B do Jarvis em `persistencia.py` e `sessao.py`; suíte 322 + 1 xfail). **T229 concluída** (Nível B; varredura SC-208(c) dos limites SEG em `test_validacao_limiares.py`, só testes; suíte 328 + 1 xfail; `validacao-limiares.md` não regravado — registro de (c) no relatório fica pendente de decisão). **Não iniciadas:** T228 e T230 em diante; Bloco 3. Sem merge na `main`. Sem validação acústica.

## Patch do P1 — origem declarada (2026-10-17)
**JV-T228P concluída** (Nível B; JV-D046; constituição 0.5.0): tipo primário `declaracao` (`L`) na cadeia, criado na importação do manifesto, integridade com snapshot conferido contra o manifesto do cofre. Suíte: 355 passando + 1 xfail. **T228 e T230 continuam sem autorização de implementação.** Sem merge na `main`.

## JV-T228 — alteração candidata (2026-10-17)
**JV-T228 concluída** (Nível B; JV-D047, D1–D5): REF-003-S1/S2 bloqueadas, S3 admitida com aviso e aprovação B; percurso do S3 termina na aplicação declarada, sessão aberta. Extensão pontual (Nível B, issue #1): `registrar_aplicacao()` recusa, antes de gravar, parâmetro existente cujo valor difere do `de` declarado (2 testes). Suíte: 369 + 1 xfail. **JV-T230 (interface) segue sem autorização.** Sem merge na `main`. Sem validação acústica (caso simulado).
