# Constituição do Projeto — [NOME DO PROJETO]

> **Versão**: 1.0.0 | **Projeto**: [NOME DO PROJETO] | **Data**: [AAAA-MM-DD]

## Arkan Core

Os princípios operacionais do Arkan (I a VIII) vivem em **`.arkan/memory/constitution.md`**
e valem para todos os projetos deste repositório. Eles **não são copiados aqui** e
**não se editam**: emendá-los exige aprovação explícita do mantenedor do Arkan e um registro
na tabela de emendas de lá — a maioria das emendas ao núcleo até hoje foi classificada como
versão menor (princípio novo ou seção nova); versão maior fica reservada à remoção ou
redefinição incompatível de um princípio existente.

Este arquivo contém apenas o que é seu.

> Por que não há cópia: até a versão 2.2.0 o núcleo era recopiado em cada modelo, e as
> duas versões divergiram sem que ninguém percebesse — o modelo perdeu dois dos oito
> princípios, entre eles o de idioma. Uma fonte só é o que impede isso de voltar.

---

## Princípios do Projeto

> Escreva aqui as decisões de design que valem para este projeto e que os agentes devem
> respeitar. Um princípio é uma regra que resolve uma discussão antes de ela acontecer.
> Numere-os P1, P2, P3… e marque como **NÃO-NEGOCIÁVEL** os que não admitem exceção.

### P1. [Título curto e afirmativo]

[Uma regra por princípio, em uma a três frases. Diga o que vale, não o que é bom.
Se houver exceção, escreva a exceção aqui, senão ela vira discussão depois.]

> **Critério de verificação**: [Como verificar que este princípio está sendo seguido? Um
> princípio sem critério checável vira boa intenção — quem revisa não tem como apontar violação.]

### P2. [Título]

[…]

> **Critério de verificação**: [Como verificar?]

---

## Decisões de contexto

Pontos que cada projeto resolve de um jeito. Preencha, mesmo que a resposta seja
"sem restrição": resposta em branco vira suposição do agente.

| Assunto | Decisão deste projeto |
| --- | --- |
| Idioma do código-fonte | [ex.: PT-BR / EN-US / sem restrição] |
| Idioma de artefatos e respostas | definido pelo Princípio V do núcleo |
| Estrutura de repositório | [monorepo / multirepo / repositório único] |
| Estratégia de testes | [ex.: TDD obrigatório / testes após implementação] |
| Política de publicação | [ex.: só por PR revisado / commit direto em branch de trabalho] |
| Dados sensíveis | [ex.: nenhum / dados pessoais sob a lei de proteção de dados] |
| Superfície(s) crítica(s) | [ex.: nenhuma / pagamentos e dados financeiros / dados de paciente / experiência de aprendizado do usuário — o que ativa `superficie-critica: sim` em `/arkan.ideacao` e exige a seção "Obrigações da Superfície Crítica"] |

---

## Histórico de Emendas

| Versão | Data | Tipo | Descrição |
| --- | --- | --- | --- |
| 1.0.0 | [AAAA-MM-DD] | — | Constituição inicial do projeto |
