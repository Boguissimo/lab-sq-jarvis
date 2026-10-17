# PROPOSTA — Pacote Nível B: JV-T228 `avaliar_alteracao_candidata()` e percursos REF-003-S1/S2/S3

> **Estado: PROPOSTA, não aprovada. Nada foi implementado.** Não reabre o P1 (JV-D046) nem altera SEG, limiares ou interface.
> Origem: fechamento favorável da revisão do patch P1 ([comentário](https://github.com/Boguissimo/lab-sq-jarvis/issues/1#issuecomment-6236937310)), que pede levar a Fabrício só o escopo da T228 e as decisões ainda não resolvidas.
> Autoridade: Nível B por ato e escopo nomeados (JV-D045). Esta proposta e comentários de IA não autorizam nada.
> Base: `83c3c0f`. Suíte: 355 + 1 xfail.

## 1. O que a T228 faz (escopo mínimo)

`Servico.avaliar_alteracao_candidata()`:

1. Exige sessão com importação feita e uma `declaracao` com `alteracao_candidata` (senão `ErroDoPercurso` claro; sem declaração retroativa, sem origem fabricada).
2. Lê `equipamento` e `alteracao_candidata` **do manifesto preservado no cofre** (conferido pelo hash e pelo snapshot, como na integridade), não da pasta externa.
3. Chama `seguranca.classificar`, `avaliar(alteracao, equipamento)` e `admissibilidade`, sem alterar regras nem limiares.
4. Registra um `calculo` `avaliacao_seguranca` com **origem única = a `declaracao`** (`entradas`, `entradas_sha256`, `versao_regras_seg`, `limitacoes`). Nenhuma aresta para `medicao`.
5. Registra a `recomendacao` derivada desse cálculo (`recomendacao ← calculo` já é permitido): bloqueada ⇒ "Alteração bloqueada — não recomendada", sem receita; admitida ⇒ receita com PROCEDIMENTO/RETOMADA SEG-08, reversão pelo valor declarado, `exige_aprovacao_b` quando sensível.
6. Idempotente (devolve a recomendação existente), como `propor_teste`.

A aprovação (`aprovar`) e a `registrar_aplicacao` **já existem** (T227) e não mudam.

**Percursos (SC-209):** S1 (reforço, equipamento confirmado) ⇒ bloqueada por SEG-07; S2 (equipamento planejado) ⇒ SEG-12 e SEG-07; S3 (corte de EQ, médio só informado) ⇒ admitida com aviso, aprovação B, aplicação declarada.

## 2. Arquivos e atos pedidos

| Arquivo | Ato |
| --- | --- |
| `src/jarvis/sessao.py` | `avaliar_alteracao_candidata()` e o que ela precisa em `estado()` (ver D4) |
| `tests/test_sessao.py` | `test_s1_s2_s3` e os falsificadores (seção 4) |
| `.arkan/.../spec.md`, `plan.md`, `data-model.md` | só os reflexos das decisões D1–D5 (Clarification) |
| `.arkan/.../tasks.md`, `status.md`, `docs/RETOMADA-JV-V02.md` | conclusão da T228 |
| `.arkan/projects/lab-sq-jarvis/decisoes.md` | decisão `JV-D…` se D1–D5 forem aprovadas |

**Fora (continua vedado):** interface e T230 (`seguranca_view.py`, `test_interface.py`), regras SEG, limiares, calibração, esquema, reavaliação de histórico, merge na `main`.

## 3. Decisões ainda abertas (as já tomadas ficam preservadas)

- **D1 — leitura do SC-209 pela admissibilidade:** "bloqueada" = `admissibilidade.admissivel = false` (risco crescente sem dado confirmado ou regra `não verificável` bloqueia; risco decrescente não verificável é admitido com aviso). *Proposta:* adotar assim, é o que `seguranca.admissibilidade` já faz.
- **D2 — `tipo_intervencao`:** "alteração candidata" (novo rótulo) no cálculo, na recomendação e no experimento, em vez de "teste de diagnóstico", para não parecer diagnóstico. *Proposta:* rótulo novo, só texto em `dados`; sem tipo novo na cadeia.
- **D3 — S3 após a aplicação:** a sessão fica aberta com configuração declarada nova e **sem** análise/veredito (a alteração é só exercício de segurança, não diagnóstico). *Proposta:* encerrar no registro da aplicação, sem importar "depois" nem concluir.
- **D4 — `estado()["aprovacao"]`:** expor aprovação e `avaliacao_seguranca` em `estado()` para a T230 consumir. *Proposta:* acrescentar chaves de leitura em `estado()`, sem tocar na interface.
- **D5 — potência (Clarification opcional do FR-223):** potência é `não verificável` e nunca aparece como "dentro do limite" (já é o comportamento de SEG). *Proposta:* registrar como Clarification para impedir leitura contrária futura.

## 4. Testes de falsificação (devem falhar sem a mudança)

1. `test_s1_s2_s3`: S1 bloqueada por SEG-07; S2 por SEG-12 e SEG-07; S3 admitida com aviso e exige aprovação B; bloqueadas sem receita e sem aplicação.
2. `origens_de(avaliacao_seguranca) == [declaracao]`; nenhuma aresta para `medicao`; `integridade() == []`.
3. Avaliação lê do cofre: pasta externa apagada ou alterada depois da importação não muda o resultado.
4. Snapshot da declaração adulterado no banco ⇒ a avaliação recusa (e a integridade acusa).
5. Sessão sem declaração (REF-001-A) ⇒ recusa clara, sem registro criado.
6. Idempotência; segunda chamada não duplica.
7. S3 sem aprovação ⇒ `registrar_aplicacao` recusa; com aprovação de escopo igual ⇒ aplica; escopo diferente ⇒ recusa.
8. Regressão: INV-211 (histórico sem reavaliação), INV-213 (catálogo inalterado), suíte atual intacta.

## 5. Riscos

- A avaliação de segurança é **simulada** (equipamento sintético): não valida o estado físico nem a utilidade (limite declarado).
- Aprovação B autoriza o ato, não verifica nada (JV-D032); a interface (T230) deve dizê-lo e fica fora deste pacote.

## 6. Texto sugerido para a autorização

> "Autorizo, em Nível B, o pacote `PROPOSTA-pacote-nivel-b-t228-avaliar-alteracao-candidata.md`, seções 1, 2 e 4, com D1 = …, D2 = …, D3 = …, D4 = …, D5 = …. Não autorizo T230, interface, SEG, limiares, merge ou qualquer item fora do pacote."
