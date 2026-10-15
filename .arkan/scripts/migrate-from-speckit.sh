#!/usr/bin/env bash
# Arkan — migrate-from-speckit.sh
# Migra uma feature do Speckit (.specify/features/) para o Arkan (.arkan/features/{projeto}/).
# Copia artefatos para as fases corretas, gera status.md e stub de ideacao.md.
# Inclui fase de cleanup para remover o Speckit após migração confirmada.
#
# Uso:
#   migrate-from-speckit.sh --short-name <nome> [--project slug] [--force] [--dry-run] [--confirm-remove] [--json]
#   migrate-from-speckit.sh --remove-speckit-system --confirm-remove
#
# Flags:
#   --short-name <nome>       Sufixo do nome da feature Speckit (ex: arkan-framework)
#   --force                   Sobrescreve feature Arkan existente com o mesmo nome
#   --dry-run                 Exibe o que seria removido sem executar remoção
#   --confirm-remove          Autoriza remoção de .specify/features/NNN-nome/
#   --remove-speckit-system   Com --confirm-remove: remove .specify/ e speckit.*.md completos
#   --json                    Saída JSON com resultado da migração

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# ---------------------------------------------------------------------------
# Argumentos
# ---------------------------------------------------------------------------
SHORT_NAME=""
FORCE=false
DRY_RUN=false
CONFIRM_REMOVE=false
REMOVE_SPECKIT_SYSTEM=false
JSON_OUTPUT=false
PROJECT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --short-name)           SHORT_NAME="$2"; shift 2 ;;
        --project)              PROJECT="$2"; shift 2 ;;
        --force)                FORCE=true; shift ;;
        --dry-run)              DRY_RUN=true; shift ;;
        --confirm-remove)       CONFIRM_REMOVE=true; shift ;;
        --remove-speckit-system) REMOVE_SPECKIT_SYSTEM=true; shift ;;
        --json)                 JSON_OUTPUT=true; shift ;;
        -*)                     echo "Opção desconhecida: $1" >&2; exit 1 ;;
        *)                      echo "Argumento inesperado: $1" >&2; exit 1 ;;
    esac
done

# ---------------------------------------------------------------------------
# Validação de argumentos
# ---------------------------------------------------------------------------

# --remove-speckit-system não requer --short-name, mas exige --confirm-remove
if $REMOVE_SPECKIT_SYSTEM; then
    if ! $CONFIRM_REMOVE; then
        echo "Erro: --remove-speckit-system requer --confirm-remove." >&2
        echo "Uso: migrate-from-speckit.sh --remove-speckit-system --confirm-remove" >&2
        exit 1
    fi
else
    # Todas as outras operações requerem --short-name
    if [ -z "$SHORT_NAME" ]; then
        echo "Erro: --short-name é obrigatório." >&2
        echo "Uso: migrate-from-speckit.sh --short-name <nome> [opções]" >&2
        exit 1
    fi
    # Validar formato kebab-case (letras minúsculas, dígitos e hífens; não começa com hífen)
    if [[ ! "$SHORT_NAME" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
        echo "Erro: --short-name deve estar em kebab-case (letras minúsculas, dígitos e hífens)." >&2
        echo "Exemplo válido: arkan-framework" >&2
        exit 1
    fi
fi

# ---------------------------------------------------------------------------
# Resolver projeto
# ---------------------------------------------------------------------------
if [ -z "$PROJECT" ]; then
    PROJECT=$(resolve_project)
fi
if [ -z "$PROJECT" ]; then
    echo "Erro: projeto não especificado e não inferido. Use --project slug." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Variáveis de ambiente
# ---------------------------------------------------------------------------
ROOT="$(arkan_root)"
SPECKIT_BASE="${ROOT}/.specify/features"
ARKAN_BASE="${ROOT}/$(features_base "$PROJECT")"
TODAY="$(today_iso)"

# ---------------------------------------------------------------------------
# Modo: remover sistema Speckit completo (sem migração)
# ---------------------------------------------------------------------------
if $REMOVE_SPECKIT_SYSTEM; then
    # Tratado na Fase 3 (US2) — pular detecção de feature
    : # placeholder; lógica implementada em T012
    # Chegando aqui: --confirm-remove já validado acima
fi

# ---------------------------------------------------------------------------
# Detecção da feature Speckit por sufixo (ADR-002)
# ---------------------------------------------------------------------------
if ! $REMOVE_SPECKIT_SYSTEM; then

    if [ ! -d "$SPECKIT_BASE" ]; then
        echo "Erro: diretório .specify/features/ não encontrado em ${ROOT}." >&2
        echo "Este repositório não possui features Speckit para migrar." >&2
        exit 1
    fi

    # Buscar diretório pelo sufixo do nome
    mapfile -t RESULTADOS < <(find "$SPECKIT_BASE" -maxdepth 1 -type d -name "*-${SHORT_NAME}" 2>/dev/null | sort)

    if [ "${#RESULTADOS[@]}" -eq 0 ]; then
        echo "Erro: feature '${SHORT_NAME}' não encontrada em .specify/features/." >&2
        echo "Features disponíveis:" >&2
        find "$SPECKIT_BASE" -maxdepth 1 -mindepth 1 -type d 2>/dev/null \
            | sort | sed 's|.*/||' | sed 's/^/  /' >&2
        exit 1
    fi

    if [ "${#RESULTADOS[@]}" -gt 1 ]; then
        echo "Erro: múltiplas features encontradas com sufixo '${SHORT_NAME}':" >&2
        printf '  %s\n' "${RESULTADOS[@]}" >&2
        echo "Informe o nome completo via --short-name com o NNN incluído." >&2
        exit 1
    fi

    SPECKIT_DIR="${RESULTADOS[0]}"
    SPECKIT_NOME="$(basename "$SPECKIT_DIR")"

    # ---------------------------------------------------------------------------
    # Criar estrutura Arkan via create-feature.sh (ADR-004 — usa NNN automático)
    # ---------------------------------------------------------------------------
    echo "Migrando '${SHORT_NAME}' do Speckit para o Arkan..."

    CREATE_SCRIPT="${ROOT}/.arkan/scripts/create-feature.sh"

    # Verificar se já existe feature Arkan com o mesmo short-name
    ARKAN_EXISTENTE=""
    ARKAN_EXISTENTE="$(find "$ARKAN_BASE" -maxdepth 1 -type d -name "*-${SHORT_NAME}" 2>/dev/null | head -1)"

    if [ -n "$ARKAN_EXISTENTE" ] && ! $FORCE; then
        echo "Erro: feature Arkan '$(basename "$ARKAN_EXISTENTE")' já existe." >&2
        echo "Use --force para sobrescrever." >&2
        exit 1
    fi

    if [ -n "$ARKAN_EXISTENTE" ] && $FORCE; then
        echo "  Aviso: sobrescrevendo '$(basename "$ARKAN_EXISTENTE")' (--force ativo)."
        rm -rf "$ARKAN_EXISTENTE"
    fi

    # Invocar create-feature.sh e capturar JSON de saída
    CREATE_JSON="$("$CREATE_SCRIPT" --json --project "$PROJECT" --short-name "$SHORT_NAME" "Migrado do Speckit: ${SPECKIT_NOME}" 2>&1)"
    CREATE_EXIT=$?

    if [ $CREATE_EXIT -ne 0 ]; then
        echo "Erro ao criar estrutura Arkan:" >&2
        echo "$CREATE_JSON" >&2
        exit 1
    fi

    # Extrair FEATURE_DIR do JSON retornado
    FEATURE_DIR="$(echo "$CREATE_JSON" | grep -o '"FEATURE_DIR":"[^"]*"' | sed 's/"FEATURE_DIR":"//;s/"//')"
    FEATURE_DIR_ABS="${ROOT}/${FEATURE_DIR}"

    if [ -z "$FEATURE_DIR" ] || [ ! -d "$FEATURE_DIR_ABS" ]; then
        echo "Erro: create-feature.sh não retornou FEATURE_DIR válido." >&2
        echo "Saída recebida: ${CREATE_JSON}" >&2
        exit 1
    fi

    echo "  Estrutura Arkan criada: ${FEATURE_DIR}"

    # ---------------------------------------------------------------------------
    # Copiar artefatos Speckit → Arkan (FR-003)
    # Mapeamento: origem (relativo a SPECKIT_DIR) → destino (relativo a FEATURE_DIR_ABS)
    # ---------------------------------------------------------------------------
    ARTEFATOS_COPIADOS=0

    # Função auxiliar: copiar arquivo se existir na origem
    copiar_arquivo() {
        local origem="${SPECKIT_DIR}/$1"
        local destino="${FEATURE_DIR_ABS}/$2"
        if [ -f "$origem" ]; then
            mkdir -p "$(dirname "$destino")"
            cp "$origem" "$destino"
            echo "  Copiando $1 → $2"
            ARTEFATOS_COPIADOS=$((ARTEFATOS_COPIADOS + 1))
        fi
    }

    # Função auxiliar: copiar diretório se existir na origem
    copiar_diretorio() {
        local origem="${SPECKIT_DIR}/$1"
        local destino="${FEATURE_DIR_ABS}/$2"
        if [ -d "$origem" ]; then
            mkdir -p "$(dirname "$destino")"
            cp -r "$origem" "$destino"
            echo "  Copiando $1/ → $2/"
            ARTEFATOS_COPIADOS=$((ARTEFATOS_COPIADOS + 1))
        fi
    }

    # Mapeamento FR-003
    copiar_arquivo "spec.md"                "03-spec/spec.md"
    copiar_arquivo "plan.md"                "04-architecture/plan.md"
    copiar_arquivo "tasks.md"               "06-planning/tasks.md"
    copiar_arquivo "data-model.md"          "04-architecture/data-model.md"
    copiar_diretorio "contracts"            "04-architecture/contracts"
    copiar_arquivo "quickstart.md"          "04-architecture/quickstart.md"
    copiar_arquivo "research.md"            "04-architecture/research.md"
    copiar_arquivo "inventario-existente.md" "04-architecture/inventario-existente.md"
    copiar_diretorio "checklists"           "08-qa/checklists"

    echo "  ${ARTEFATOS_COPIADOS} artefato(s) copiado(s)."

    # ---------------------------------------------------------------------------
    # Gerar status.md com metadados de migração (FR-004)
    # ---------------------------------------------------------------------------
    UPDATE_SCRIPT="${ROOT}/.arkan/scripts/update-status.sh"
    STATUS_FILE="${FEATURE_DIR_ABS}/status.md"

    # status.md já criado pelo create-feature.sh — atualizar campos de migração
    bash "$UPDATE_SCRIPT" --file "$STATUS_FILE" --field origem  --value speckit
    bash "$UPDATE_SCRIPT" --file "$STATUS_FILE" --field fase-atual --value 03-spec

    # Registrar projeto no status.md da feature migrada
    bash "$UPDATE_SCRIPT" --file "$STATUS_FILE" --field projeto --value "$PROJECT"

    echo "  Gerando status.md (origem: speckit, fase-atual: 03-spec)"

    # ---------------------------------------------------------------------------
    # Gerar stub de ideacao.md (FR-005, ADR-004 — heredoc)
    # ---------------------------------------------------------------------------
    IDEACAO_DIR="${FEATURE_DIR_ABS}/01-discovery"
    mkdir -p "$IDEACAO_DIR"

    cat > "${IDEACAO_DIR}/ideacao.md" << IDEACAO_EOF
# Ideação: ${SHORT_NAME}

> **Feature**: migrada do Speckit em ${TODAY}
> **Status**: Stub de migração — preencher conforme necessário
> **Origem**: \`${SPECKIT_NOME}\` em \`.specify/features/\`
> **Propósito**: Este arquivo foi gerado automaticamente pelo script de migração Speckit → Arkan.
> Para uma ideação completa, consulte o \`spec.md\` migrado e execute \`/arkan.spec\` se necessário.

---

## Contexto Inicial

### O problema que a feature resolve

Migrado do Speckit. Consultar \`03-spec/spec.md\` para o contexto completo.

### O que já existe

- \`03-spec/spec.md\` — especificação migrada de \`.specify/features/${SPECKIT_NOME}/spec.md\`
- Demais artefatos migrados disponíveis em \`04-architecture/\` e \`06-planning/\`

### O que este debate precisa resolver

Nenhum debate pendente — feature migrada com artefatos existentes.

---

## Decisões Tomadas

| # | Decisão | Data |
| --- | --- | --- |
| D1 | Feature migrada estruturalmente do Speckit para o Arkan via \`migrate-from-speckit.sh\` | ${TODAY} |

---

## Síntese

**Nome**: ${SHORT_NAME}

**Definição**: Feature migrada do Speckit. Consultar \`03-spec/spec.md\` para definição completa.

**Escopo — o que entra**:

1. Artefatos migrados de \`.specify/features/${SPECKIT_NOME}/\`

**Fora do escopo**:

- Redefinição de escopo — já documentado na spec migrada

---

## Próximos Passos

- [x] Migrar artefatos do Speckit para o Arkan
- [ ] Revisar \`03-spec/spec.md\` e adaptar ao formato Arkan se necessário
- [ ] Revisar \`06-planning/tasks.md\` e reorganizar em fases Arkan (ver MIGRATION-GUIDE.md)
- [ ] Atualizar feature-map em \`$(project_dir "$PROJECT")/02-proposal/feature-map.md\`
- [ ] Executar \`/arkan.implement\` para continuar o desenvolvimento
IDEACAO_EOF

    echo "  Gerando ideacao.md (stub de migração)"

    # ---------------------------------------------------------------------------
    # Saída final de migração (FR-009, FR-010)
    # ---------------------------------------------------------------------------
    if $JSON_OUTPUT; then
        printf '{"FEATURE_DIR":"%s","SPECKIT_DIR":"%s","ARTEFATOS_COPIADOS":%d,"STATUS":"SUCESSO"}\n' \
            "$FEATURE_DIR" "$SPECKIT_NOME" "$ARTEFATOS_COPIADOS"
    else
        echo ""
        echo "✓ Migração concluída: ${FEATURE_DIR}"
        echo ""
        echo "Próximos passos:"
        echo "  1. Adicionar a feature ao feature-map:"
        echo "     $(project_dir "$PROJECT")/02-proposal/feature-map.md"
        printf '     Linha sugerida: | FNNN | %s | [descrição] | P? | [depende de] | pendente |\n' \
            "$(basename "$FEATURE_DIR")"
        echo "  2. Revisar tasks.md e reorganizar em fases Arkan (ver .arkan/MIGRATION-GUIDE.md)"
        echo "  3. Executar /arkan.implement para continuar o desenvolvimento"
        echo ""
        if $DRY_RUN || $CONFIRM_REMOVE; then
            : # cleanup tratado abaixo (T010-T012)
        fi
    fi

fi  # fim do bloco principal de migração (! REMOVE_SPECKIT_SYSTEM)

# ---------------------------------------------------------------------------
# Fase de cleanup — dry-run (T010)
# Exibe arquivos que seriam removidos sem executar nenhuma deleção.
# Executado quando --dry-run está presente (com ou sem --confirm-remove).
# ---------------------------------------------------------------------------
listar_remocao_feature() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        echo "  Diretório não encontrado: $dir" >&2
        return 1
    fi
    find "$dir" -type f | sort | sed "s|${ROOT}/||"
}

if $DRY_RUN && ! $REMOVE_SPECKIT_SYSTEM; then
    echo ""
    echo "[DRY-RUN] Arquivos que seriam removidos de .specify/features/${SPECKIT_NOME}/:"
    listar_remocao_feature "$SPECKIT_DIR"
    echo ""
    echo "Execute com --confirm-remove para remover."
fi

# ---------------------------------------------------------------------------
# Fase de cleanup — remoção da feature Speckit (T011, ADR-005)
# Executado com --confirm-remove (sem --remove-speckit-system).
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Fase de cleanup — remoção do sistema Speckit completo (T012)
# Executado com --remove-speckit-system --confirm-remove.
# Remove: .specify/ inteiro + .claude/commands/speckit.*.md
# ---------------------------------------------------------------------------
if $REMOVE_SPECKIT_SYSTEM; then
    # --confirm-remove já validado no topo do script
    ESPECIFY_DIR="${ROOT}/.specify"
    COMMANDS_DIR="${ROOT}/.claude/commands"

    echo "Arquivos que serão removidos:"
    echo ""

    # Listar .specify/
    if [ -d "$ESPECIFY_DIR" ]; then
        echo "  Diretório: .specify/"
        find "$ESPECIFY_DIR" -type f | sort | sed "s|${ROOT}/||" | sed 's/^/    /'
    else
        echo "  .specify/ não encontrado (já removido?)"
    fi

    # Listar speckit.*.md em .claude/commands/
    COMMANDS_SPECKIT=()
    if [ -d "$COMMANDS_DIR" ]; then
        mapfile -t COMMANDS_SPECKIT < <(find "$COMMANDS_DIR" -maxdepth 1 -name "speckit.*.md" 2>/dev/null | sort)
    fi

    if [ "${#COMMANDS_SPECKIT[@]}" -gt 0 ]; then
        echo ""
        echo "  Commands Speckit (.claude/commands/):"
        printf '    %s\n' "${COMMANDS_SPECKIT[@]}" | sed "s|${ROOT}/||"
    fi

    echo ""
    read -r -p "Confirma remoção COMPLETA do sistema Speckit? Esta ação é irreversível. (s/N): " RESPOSTA
    if [[ "${RESPOSTA,,}" != "s" ]]; then
        echo "Remoção cancelada."
        exit 0
    fi

    # Executar remoção
    if [ -d "$ESPECIFY_DIR" ]; then
        rm -rf "$ESPECIFY_DIR"
        echo "✓ Removido: .specify/"
    fi

    if [ "${#COMMANDS_SPECKIT[@]}" -gt 0 ]; then
        rm -f "${COMMANDS_SPECKIT[@]}"
        echo "✓ Removidos: ${#COMMANDS_SPECKIT[@]} command(s) Speckit"
    fi

    echo ""
    echo "✓ Sistema Speckit removido. Período de coexistência encerrado."
    exit 0
fi

if $CONFIRM_REMOVE && ! $REMOVE_SPECKIT_SYSTEM; then
    if [ ! -d "$SPECKIT_DIR" ]; then
        echo "Aviso: diretório Speckit não encontrado (já removido?): ${SPECKIT_NOME}" >&2
    else
        echo ""
        echo "Arquivos a remover de .specify/features/${SPECKIT_NOME}/:"
        listar_remocao_feature "$SPECKIT_DIR"
        echo ""

        # Se --dry-run não foi passado na mesma invocação: solicitar confirmação interativa
        PODE_REMOVER=true
        if ! $DRY_RUN; then
            read -r -p "Confirma remoção de .specify/features/${SPECKIT_NOME}/? (s/N): " RESPOSTA
            if [[ "${RESPOSTA,,}" != "s" ]]; then
                echo "Remoção cancelada."
                PODE_REMOVER=false
            fi
        fi

        if $PODE_REMOVER; then
            rm -rf "$SPECKIT_DIR"
            echo "✓ Removido: .specify/features/${SPECKIT_NOME}/"
        fi
    fi
fi
