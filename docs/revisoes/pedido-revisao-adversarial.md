# Pedido de revisão adversarial — Lab SQ Jarvis (para colar no ChatGPT)

> Preparado em 2026-10-15, antes de `/arkan.tasks` do JV-V02. Estado: commit `1f6b62d` da branch `lab-sq-jarvis/003-000-jv-v02-honestidade-e-seguranca`. A resposta deve ser salva em `docs/revisoes/` e aplicada só por decisão do desenvolvedor (Princípio VIII).

---

Você vai fazer uma **revisão adversarial** de um projeto pessoal de software. O papel não é aprovar: é **tentar derrubar** o projeto. Procure o que está errado, o que é frágil, o que é desonesto sem querer e o que vai falhar na prática. Não repita elogios nem resuma o que o projeto já diz de si mesmo.

## O projeto

O Lab SQ Jarvis é um aplicativo desktop pessoal (Python, PySide6, SQLite) que ajuda o desenvolvedor a ajustar o som do carro (DSP HELIX, medições no Room EQ Wizard). Ele analisa medições, levanta hipóteses, propõe **um teste de cada vez** com previsão registrada antes e verifica o resultado. Nunca escreve no DSP, e regras de segurança (SEG-01 a SEG-13) protegem o equipamento. O processo de desenvolvimento segue o "Arkan Core", com spec, plano, ADRs, gates e aprovações registradas.

- O **JV-V01** está pronto (em `main`): um percurso completo com um caso simulado (REF-001-A, polaridade do tweeter invertida).
- O **JV-V02** está especificado e planejado, ainda sem código: honestidade diagnóstica (casos negativos N1 a N5), regras de segurança, calibração simulada e reversão.
- O plano do V02 já passou por uma revisão sua (`docs/revisoes/jv-v02-revisao-tecnica-do-plano.md`), aplicada nas emendas E1 e E2.

## O que ler

Repositório público: https://github.com/Boguissimo/lab-sq-jarvis. Leia na branch `lab-sq-jarvis/003-000-jv-v02-honestidade-e-seguranca`, que contém o V01 completo:

1. **Visão e proposta:**
   - `.arkan/projects/lab-sq-jarvis/01-discovery/vision.md` e `briefing.md`;
   - `.arkan/projects/lab-sq-jarvis/02-proposal/proposta-consolidada.md` e `feature-map.md`.
2. **Regras do projeto:**
   - `.arkan/projects/lab-sq-jarvis/constitution.md`, `regras-de-seguranca.md` e `decisoes.md`.
3. **JV-V01:**
   - artefatos em `.arkan/features/lab-sq-jarvis/002-000-jv-v01-primeiro-percurso/`;
   - código em `src/jarvis/` e testes em `tests/`.
4. **JV-V02:**
   - `.arkan/features/lab-sq-jarvis/003-000-jv-v02-honestidade-e-seguranca/03-spec/spec.md`;
   - `04-architecture/plan.md` e `data-model.md`, na mesma pasta.
5. **Contexto:** `docs/RETOMADA-JV-V02.md` e `docs/revisoes/*`.

## Ataque estas frentes

1. **Premissa e valor.** O projeto resolve um problema real melhor do que REW + ouvido + planilha? Onde a disciplina (spec, gates, aprovações) custa mais do que entrega para um único desenvolvedor?
2. **Validade acústica.** Os modelos, métricas e limiares fazem sentido físico? Pontos de atenção:
   - o estimador σ̂ por segunda diferença;
   - o detector de mudança por via;
   - o deficit no cruzamento;
   - o critério de aceite do V01.

   Que fenômenos reais de carro (reflexões, posição, janela temporal, suavização do REW, fase mínima versus excesso de fase) quebram as conclusões?
3. **Honestidade epistêmica.** Em que pontos o programa pode **parecer** mais confiável do que é? Pense em casos simulados que validam o próprio gerador, circularidade entre gerador e detector, e limiares escolhidos pelo agente.
4. **Segurança do equipamento.** As regras SEG protegem de verdade? Que alteração perigosa passaria? A distinção entre "não verificável" e "bloqueada" e a aprovação de nível B se sustentam?
5. **Arquitetura e código do V01.** Procure bugs reais e riscos de integridade:
   - persistência e migração;
   - imutabilidade e gatilhos;
   - cofre por hash;
   - `estado()` recalculando regras;
   - acoplamento da interface;
   - testes que passam sem provar nada.
6. **Plano do V02.** Contradições entre spec, plano e data-model; requisitos sem teste real; testes que não detectariam a falha; escopo grande demais para um incremento.
7. **Processo.** O processo Arkan está sendo seguido de verdade ou só formalmente? Há decisões tomadas por inércia?

## Formato da resposta

- **Veredito geral** em uma frase: seguir, seguir com mudanças ou parar e repensar.
- **Achados**, ordenados por gravidade (crítico, alto, médio, baixo). Cada achado traz:
  - **onde:** arquivo e trecho;
  - **o problema;**
  - **cenário concreto** em que falha;
  - **evidência:** citação do arquivo ou raciocínio verificável;
  - **correção sugerida;**
  - se exige mudar a spec ou as regras canônicas.
- **O que você não conseguiu verificar** (arquivos não lidos, suposições).
- **Pressupostos que você contesta** e que o projeto trata como certos.

Seja específico. Um achado sem arquivo e sem cenário concreto não ajuda. Prefira poucos achados sólidos a muitos genéricos. Se algo estiver bem feito, não comente.
