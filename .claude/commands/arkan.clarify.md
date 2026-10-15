---
description: Arkan fase 03 — Clarificação: detecta ambiguidades em 9 categorias e resolve com opções baseadas em evidências do codebase.
---

## PRÉ-CONDIÇÕES

arquivo: .arkan/scripts/common.sh
arquivo: .arkan/scripts/check-prerequisites.sh
arquivo: .arkan/memory/constitution.md
campo-obrigatorio: ## Requirements in $FEATURE_DIR/03-spec/spec.md

## PÓS-CONDIÇÕES

campo-obrigatorio: ## Clarifications in $FEATURE_DIR/03-spec/spec.md

## Outline

O texto após `/arkan.clarify` é opcional — especifica foco (ex: "apenas domain/data", "edge cases"). A feature é inferida da branch atual.

### Fase 0 — Setup (automático)

1. Verificar pré-condições: `.arkan/scripts/check-prerequisites.sh --json --command .claude/commands/arkan.clarify.md`
   - Se falhar: exibir lista de falhas e **parar**
2. Definir `FEATURE_DIR` a partir do JSON retornado

### Fase 1 — Carregamento

**Exibir cabeçalho**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARKAN  ·  FASE 03 — SPEC  ·  MODO: ASSISTÊNCIA
Agente: Clarifier  ·  Step: Scan de ambiguidades
Feature: [FEATURE_SLUG]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

> **Dependência opcional — indexador de código.** Se o projeto tiver um indexador de código e specs configurado como servidor de contexto, os passos que citam o indexador abaixo o usam. Sem ele, o comando **funciona igual**: onde diria "consulte o indexador", leia os arquivos direto com busca por texto nos diretórios declarados em `.arkan/memory/stack.md`. Nenhum passo deste comando fica bloqueado por falta do indexador; o que muda é o custo de achar a informação.

Carregar:
- `$FEATURE_DIR/03-spec/spec.md`
- `.arkan/memory/constitution.md`
- Consultas ao indexador de código declarado em `.arkan/memory/stack.md` para entidades existentes (se disponível)

### Fase 2 — Scan estruturado de ambiguidades

Escanear spec.md em 9 categorias:

| # | Categoria | O que verificar |
|---|----------|-----------------|
| 1 | Escopo Funcional | Funcionalidades ausentes, requisitos vagos, limites indefinidos |
| 2 | Domínio/Dados | Entidades indefinidas, relações faltantes, fluxos de dados vagos |
| 3 | Interação/UX | Fluxos de usuário vagos, estados indefinidos, feedback ausente |
| 4 | Não-Funcional | Performance, segurança, acessibilidade ausentes |
| 5 | Integração | APIs indefinidas, dependências externas, limites de sistema |
| 6 | Edge Cases | Erros sem tratamento, condições de contorno, modos de falha |
| 7 | Constraints | Limites indefinidos, restrições de recurso, compliance |
| 8 | Terminologia | Termos inconsistentes, jargão indefinido, linguagem ambígua |
| 9 | Sinais de Conclusão | Critérios de sucesso ausentes, condições de "pronto" indefinidas |

Também buscar:
- Marcadores `[NEEDS CLARIFICATION]`
- Requisitos vagos ("adequadamente", "de forma eficiente")
- Cenários de aceitação ausentes
- Requisitos conflitantes

### Fase 3 — Gerar até 5 questões priorizadas

Para cada ambiguidade (máx. 5, por impacto):

```markdown
## Issue [N]: [Tópico]
**Categoria**: [Nome da categoria]
**Localização**: [Trecho da spec]
**Problema**: [O que está ambíguo]
**Evidência Codebase**: [achados do indexador de código declarado em `.arkan/memory/stack.md` ou "N/A"]

**Opções**:
| Opção | Descrição | Impacto |
|-------|-----------|---------|
| A | [Opção A] | [Consequência] |
| B | [Opção B] | [Consequência] |
| C | [Opção C] | [Consequência] |

**Sugestão**: [Opção recomendada com justificativa]
```

Apresentar uma questão por vez. Aguardar resposta do dev.

### Fase 4 — Aplicar clarificações

Após cada resposta:
1. Registrar em `## Clarifications` → `### Session YYYY-MM-DD`
2. Aplicar incrementalmente nas seções relevantes da spec
3. Avançar para próxima questão

### Fase 5 — Resumo de cobertura

| Categoria | Status |
|-----------|--------|
| Escopo Funcional | Resolvido / Diferido / Limpo / Pendente |
| ... | ... |

## Guidelines

- Documentação em **PT-BR**
- Máximo 5 questões por sessão — priorizar por impacto
- Enriquecer com evidências do indexador de código declarado em `.arkan/memory/stack.md` quando entidades existem no código
- Se o dev responde "diferir": registrar como DIFERIDO, não insistir
- Cada clarificação é permanente — faz parte da spec formal
- Princípio VIII: dev decide, agente propõe opções
