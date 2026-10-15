---
projeto-default:
agente-dominio:
---

# Arkan Config

Configurações globais do Arkan para este repositório.

| Campo | O que faz |
| --- | --- |
| `projeto-default` | projeto usado quando um comando não recebe `--project`. Troque por um projeto seu assim que criar o primeiro com `create-project.sh`. |
| `agente-dominio` | nome de um agente em `.arkan/agents/transversal/` que representa a especialidade do seu domínio. Quando preenchido, comandos que preveem reflexão de domínio o consultam; vazio, eles pulam essa etapa e registram isso no artefato. Veja `GUIA-DE-ADOCAO.md`. |
