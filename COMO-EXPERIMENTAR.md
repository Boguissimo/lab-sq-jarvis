# Como experimentar o JV-V02 (Lab SQ Jarvis)

> Demonstração com **dados simulados**. As explicações vêm de regras, não de IA, e **não servem para
> orientar ajustes reais** no carro (JV-D025). Este é o roteiro dos seus testes G3 no Windows (SC-206),
> um por bloco. A suíte automática já passou no Windows (211 passando, 1 `xfail` esperado, 16/10/2026); falta concluir este roteiro manual.

## Antes de começar
- Windows com **Python 3.11 a 3.14** (o ambiente do V01 é reaproveitado; não há dependências novas).
- **Seu banco do V01 será migrado na primeira abertura.** Antes de mexer, o programa faz uma cópia de
  segurança `jarvis.antes-v02-<data>.db` na pasta de dados (`%LOCALAPPDATA%\LabSQJarvis`). Se quiser,
  copie essa pasta inteira para outro lugar antes de começar.
- Se algo falhar, a janela preta ou o aviso explicam em linguagem simples; mostre-os ao Claude.

## Bloco 1 — casos e honestidade (cerca de 20 minutos)
1. **Dois cliques em `INICIAR-JARVIS.bat`.** Esperado: janela "Lab SQ Jarvis — JV-V02 (demonstração
   com dados simulados)" e o aviso de dados simulados sempre visível.
2. **Migração do seu banco.** Na pasta de dados deve aparecer `jarvis.antes-v02-<data>.db`. Em
   **Histórico**, as sessões antigas continuam lá (coluna **Modo** nova). Abra uma: a análise aparece
   marcada como **"reconstruída pelas regras 1.0"** e nada do que ela disse mudou.
3. **Os casos.** Para cada caso abaixo: **Começar uma nova sessão** → em **2. O que preciso medir**,
   escolha o caso na lista (a descrição aparece embaixo) → **Importar o caso escolhido** →
   **Analisar as medições**. Esperado:
   - **REF-001-A**: como no V01; qualidade **aprovada**; teste de polaridade; veredito **confirmada**.
   - **REF-001-B** (realista): mesmo percurso; veredito **confirmada** com **incerteza declarada maior**
     (σ̂ de alguns décimos de dB).
   - Só **REF-001-A, B e N3** têm o teste de polaridade e o percurso até o veredito. Em **N1, N2, N4 e N5** o programa
     recusa propor o teste de polaridade (é o esperado): confira só a análise e o texto de cada um.
   - **REF-001-N1**: indício **"vale numa via isolada"**; **interferência ou reflexão** em primeiro;
     nenhum teste de polaridade; aviso para **não reforçar a EQ**.
   - **REF-001-N2**: **"Não dá para concluir"**, com o motivo (σ̂ acima do limite provisório) e o que falta.
   - **REF-001-N3**: siga até o veredito (**Ver o teste proposto** → **Registrar** → **Importar a medição
     "depois"** → percepção). Esperado: **comprometida**, "mudança detectada e reproduzida" no tweeter,
     com a faixa, e os textos **"a medição não identifica a causa"** e **"não comprova alteração no DSP"**.
   - **REF-001-N4**: fase e soma prevista **recusadas** ("Sem referência temporal declarada compatível"),
     só magnitude e soma de potências.
   - **REF-001-N5**: "Sem indício de problema no cruzamento"; em **4. Qual passo dar**, **Nada a alterar**
     abre com a justificativa **pré-preenchida**, que você pode editar.
4. **Feche e abra de novo.** Reabra algumas sessões no **Histórico**: o que cada uma disse não muda.

## G3 do bloco 1 — roteiro humano mínimo (17/10/2026)
O que já foi conferido por outros (Codex/Work no Windows, relatado; testes automatizados) está em `08-qa/g3-bloco1-parcial.md`. **Só o seu aceite fecha o G3.** Cerca de 15 minutos, na versão atual (`git pull` na branch `claude/busy-bohr-25s6e5`; depois, `INICIAR-JARVIS.bat`).
1. **Abrir:** a janela "JV-V02 (demonstração com dados simulados)" e o aviso de simulação aparecem.
2. **Backup:** na pasta `%LOCALAPPDATA%\LabSQJarvis` existe `jarvis.antes-v02-<data>.db`.
3. **Sessão antiga (V01):** em **Histórico**, abra uma sessão antiga → passo **3**: aparece a frase **"Sessão anterior ao JV-V02: a análise foi reconstruída pelas regras 1.0 … o que ela disse não mudou"**.
4. **REF-001-A até o veredito (versão atual):** **Começar uma nova sessão** → **REF-001-A** → importar → analisar → **Ver o teste proposto** → aplicar → **Importar a medição "depois" do caso REF-001-A** → percepção → veredito. Esperado: **confirmada**. Nesta sessão **nova**, o passo 3 **não** mostra "reconstruída" nem "regras 1.1".
5. **Rótulos do N3:** nova sessão → **REF-001-N3** até o veredito. Esperado: o botão diz **"…do caso REF-001-N3"** (não REF-001-A), nenhum texto cita REF-001-A, veredito **comprometida**.
6. **Fechar e reabrir:** reabra o N3 no Histórico: o veredito não muda; abra uma sessão nova qualquer: nada de linha técnica de interpretação.
7. **Mensagem de erro:** em "Escolher outra pasta de caso…", escolha uma pasta sem `manifesto.json` (qualquer pasta comum): aparece mensagem em português e a janela continua utilizável.
8. **Seu aceite:** diga se **aceita o G3 do bloco 1** (sim/não, com observações) e se **aceita como suficientes** as verificações do Work para B, N1, N2, N4 e N5 e a integridade do backup (ou prefere vê-las). Isso também vale como validação operacional do pacote **T250 + T251** no Windows.

## Blocos 2 e 3
Roteiros acrescentados quando os blocos estiverem prontos (segurança e casos REF-003-S; etapa de
calibração REF-002-A, configuração e reversão documentada).

## O que me contar
- Em que passo você travou ou ficou em dúvida? Algum texto confuso?
- A migração do seu banco funcionou? A cópia de segurança apareceu?
- As explicações de cada caso fizeram sentido?

## Limites
Casos simulados (não representam o carro); limiares provisórios, validados só no domínio simulado
(`08-qa/validacao-limiares.md`); posição, ganho, nível e referência temporal são **declarados**, não
verificados fisicamente; formato de texto do REW a confirmar com arquivo real (JV-V04). Dados em
`%LOCALAPPDATA%\LabSQJarvis` (ou na pasta indicada em `JARVIS_DADOS`).
