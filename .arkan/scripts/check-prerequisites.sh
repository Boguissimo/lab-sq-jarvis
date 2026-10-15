#!/usr/bin/env bash
# Arkan — check-prerequisites.sh
# Valida PRÉ-CONDIÇÕES e PÓS-CONDIÇÕES de um command Arkan
# Suporta nível Feature (.arkan/features/{projeto}/NNN-nome/) e nível Projeto (.arkan/projects/{projeto}/)
#
# Uso: check-prerequisites.sh [--json] [--command PATH] [--pos] [--require-tasks] [--include-tasks] [--project slug] [--report-file PATH] [--debug-dir PATH]

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# ---------------------------------------------------------------------------
# Argumentos
# ---------------------------------------------------------------------------
JSON_OUTPUT=false
REQUIRE_TASKS=false
INCLUDE_TASKS=false
COMMAND_FILE=""
CHECK_TYPE="pre"   # "pre" = PRÉ-CONDIÇÕES | "pos" = PÓS-CONDIÇÕES
PROJECT=""
REPORT_FILE_ARG=""
DEBUG_DIR_ARG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --json)          JSON_OUTPUT=true; shift ;;
        --require-tasks) REQUIRE_TASKS=true; shift ;;
        --include-tasks) INCLUDE_TASKS=true; shift ;;
        --pos)           CHECK_TYPE="pos"; shift ;;
        --command)       COMMAND_FILE="$2"; shift 2 ;;
        --project)       PROJECT="$2"; shift 2 ;;
        --report-file)   REPORT_FILE_ARG="$2"; shift 2 ;;
        --debug-dir)     DEBUG_DIR_ARG="$2"; shift 2 ;;
        *)               shift ;;
    esac
done

ROOT=$(arkan_root)

normalize_path_value() {
    local value="${1:-}"
    if [[ "$value" =~ ^[A-Za-z]:[\\/].* ]]; then
        if command -v cygpath >/dev/null 2>&1; then
            cygpath -u "$value"
        else
            printf '%s' "$value" | sed 's|\\|/|g'
        fi
    else
        printf '%s' "$value"
    fi
}

# ---------------------------------------------------------------------------
# Resolver projeto
# ---------------------------------------------------------------------------
if [ -z "$PROJECT" ]; then
    PROJECT=$(resolve_project)
fi

# ---------------------------------------------------------------------------
# Contexto — Feature
# ---------------------------------------------------------------------------
FEATURE_DIR=$(find_feature_dir "" "$PROJECT")
FEATURE_STATUS=""
FASE_ATUAL=""
FEATURE_SLUG=""
FEATURE_NAME=""
FEATURE_NUMBER=""

if [ -n "$FEATURE_DIR" ]; then
    FEATURE_SLUG=$(basename "$FEATURE_DIR")
    FEATURE_NAME=$(printf '%s' "$FEATURE_SLUG" | sed -E 's/^[0-9]{3}-([0-9]{3}-)?//')
    FEATURE_NUMBER=$(printf '%s' "$FEATURE_SLUG" | grep -oE '^[0-9]+' || echo "")

    if [ -f "${ROOT}/${FEATURE_DIR}/status.md" ]; then
        FEATURE_STATUS=$(parse_yaml_field "${ROOT}/${FEATURE_DIR}/status.md" "status")
        FASE_ATUAL=$(parse_yaml_field "${ROOT}/${FEATURE_DIR}/status.md" "fase-atual")
    fi
fi

# ---------------------------------------------------------------------------
# Contexto — Projeto (multi-projeto)
# ---------------------------------------------------------------------------
PROJECT_STATUS=""
PROJECT_FASE=""
PROJECT_DIR=""
PROJECT_STATUS_FILE=""
if [ -n "$PROJECT" ]; then
    PROJECT_DIR=$(project_dir "$PROJECT")
    PROJECT_STATUS_FILE="${ROOT}/${PROJECT_DIR}/status.md"
fi
if [ -n "$PROJECT_STATUS_FILE" ] && [ -f "$PROJECT_STATUS_FILE" ]; then
    PROJECT_STATUS=$(parse_yaml_field "$PROJECT_STATUS_FILE" "status")
    PROJECT_FASE=$(parse_yaml_field "$PROJECT_STATUS_FILE" "fase-atual")
fi

# ---------------------------------------------------------------------------
# Verificação de pré/pós-condições do command file
# ---------------------------------------------------------------------------
PASSED=()
FAILED=()
GATE_RESULT="PASS"
COMMAND_PATH=""

if [ -n "$COMMAND_FILE" ]; then
    COMMAND_CANDIDATE=$(normalize_path_value "$COMMAND_FILE")
    if [ -f "$COMMAND_CANDIDATE" ]; then
        COMMAND_PATH="$COMMAND_CANDIDATE"
    elif [ -f "${ROOT}/${COMMAND_CANDIDATE}" ]; then
        COMMAND_PATH="${ROOT}/${COMMAND_CANDIDATE}"
    else
        FAILED+=("command: ${COMMAND_FILE} - arquivo não encontrado")
        GATE_RESULT="FAIL"
    fi
fi

if [ -n "$COMMAND_PATH" ]; then

    if [ "$CHECK_TYPE" = "pre" ]; then
        SECTION_MARKER="PRÉ-CONDIÇÕES"
        SECTION_MARKER_ASCII="PRE-CONDICOES"
    else
        SECTION_MARKER="PÓS-CONDIÇÕES"
        SECTION_MARKER_ASCII="POS-CONDICOES"
    fi

    # Extrai linhas de verificação do bloco da seção até a próxima seção ##
    SECTION_FOUND=true
    if ! grep -Eq "^## (${SECTION_MARKER}|${SECTION_MARKER_ASCII})[[:space:]]*$" "$COMMAND_PATH"; then
        FAILED+=("seção: ${SECTION_MARKER} - não encontrada em ${COMMAND_FILE}")
        GATE_RESULT="FAIL"
        SECTION_FOUND=false
        BLOCK=""
    else
        BLOCK=$(awk -v accented="$SECTION_MARKER" -v ascii="$SECTION_MARKER_ASCII" '
            /^## / {
                heading = $0
                sub(/\r$/, "", heading)
                if (capture) exit
                if (heading == "## " accented || heading == "## " ascii) capture = 1
                next
            }
            capture {
                sub(/\r$/, "")
                print
            }
        ' "$COMMAND_PATH" | grep -E '^(arquivo|campo-obrigatorio|comando-disponivel):[[:space:]]*' || true)
    fi

    CONDITION_COUNT=0

    while IFS= read -r line; do
        [ -z "$line" ] && continue
        CONDITION_COUNT=$((CONDITION_COUNT + 1))

        TYPE="${line%%:*}"
        VALUE=$(printf '%s' "${line#*:}" | sed 's/^[[:space:]]*//')

        # Substitui apenas variáveis de contexto conhecidas pelo gate.
        DEBUG_DIR_VALUE="${DEBUG_DIR_ARG:-${DEBUG_DIR:-}}"
        REPORT_FILE_VALUE="${REPORT_FILE_ARG:-${REPORT_FILE:-}}"
        if [ -z "$DEBUG_DIR_VALUE" ] && [ -n "$FEATURE_DIR" ]; then
            DEBUG_DIR_VALUE="${FEATURE_DIR}/debug"
        fi
        DEBUG_DIR_VALUE=$(normalize_path_value "$DEBUG_DIR_VALUE")
        REPORT_FILE_VALUE=$(normalize_path_value "$REPORT_FILE_VALUE")
        VALUE=$(printf '%s' "$VALUE" | sed \
            -e "s|\\\$FEATURE_DIR|${FEATURE_DIR}|g" \
            -e "s|\\\$FEATURE_SLUG|${FEATURE_SLUG}|g" \
            -e "s|\\\$FEATURE_NAME|${FEATURE_NAME}|g" \
            -e "s|\\\$FEATURE|${FEATURE_DIR}|g" \
            -e "s|\\\$PROJECT_DIR|${PROJECT_DIR}|g" \
            -e "s|\\\$DEBUG_DIR|${DEBUG_DIR_VALUE}|g" \
            -e "s|\\\$REPORT_FILE|${REPORT_FILE_VALUE}|g" \
            -e "s|\\\$ROOT|${ROOT}|g")

        if [ "$TYPE" = "arquivo" ]; then
            if [[ "$VALUE" = /* || "$VALUE" =~ ^[A-Za-z]:/ ]]; then
                TARGET="$VALUE"
            else
                TARGET="${ROOT}/${VALUE}"
            fi

            if [ -n "$VALUE" ] && [ -f "$TARGET" ]; then
                PASSED+=("arquivo: ${VALUE}")
            else
                FAILED+=("arquivo: ${VALUE} — não encontrado")
                GATE_RESULT="FAIL"
            fi

        elif [ "$TYPE" = "campo-obrigatorio" ]; then
            # Formato esperado: "## Nome da Seção in caminho/para/arquivo.md"
            SECTION_NAME=$(printf '%s' "$VALUE" | sed 's/ in .*//')
            FILE_REL=$(printf '%s' "$VALUE" | sed 's/.* in //')
            if [[ "$FILE_REL" = /* || "$FILE_REL" =~ ^[A-Za-z]:/ ]]; then
                TARGET="$FILE_REL"
            else
                TARGET="${ROOT}/${FILE_REL}"
            fi

            if [[ "$VALUE" == *" in "* ]] && [ -f "$TARGET" ] && awk -v expected="$SECTION_NAME" '
                {
                    line = $0
                    sub(/\r$/, "", line)
                    if (index(line, expected) == 1) found = 1
                }
                END { exit(found ? 0 : 1) }
            ' "$TARGET" 2>/dev/null; then
                PASSED+=("campo-obrigatorio: ${SECTION_NAME} em ${FILE_REL}")
            else
                FAILED+=("campo-obrigatorio: ${SECTION_NAME} em ${FILE_REL} — não encontrado")
                GATE_RESULT="FAIL"
            fi

        elif [ "$TYPE" = "comando-disponivel" ]; then
            COMMAND_NAME=$(printf '%s' "$VALUE" | awk '{print $1}')
            AVAILABLE_TOOLS=",${ARKAN_AVAILABLE_TOOLS:-},"
            AVAILABLE_TOOLS="${AVAILABLE_TOOLS// /,}"

            if [ -n "$COMMAND_NAME" ] && { command -v "$COMMAND_NAME" >/dev/null 2>&1 || [[ "$AVAILABLE_TOOLS" == *",${COMMAND_NAME},"* ]]; }; then
                PASSED+=("comando-disponivel: ${COMMAND_NAME}")
            else
                FAILED+=("comando-disponivel: ${COMMAND_NAME} — não encontrado")
                GATE_RESULT="FAIL"
            fi
        fi

    done <<< "$BLOCK"

    if [ "$SECTION_FOUND" = true ] && [ "$CONDITION_COUNT" -eq 0 ]; then
        FAILED+=("seção: ${SECTION_MARKER} - nenhuma condição estruturada")
        GATE_RESULT="FAIL"
    fi
fi

# ---------------------------------------------------------------------------
# Verificação de tasks.md
# ---------------------------------------------------------------------------
TASKS_FILE=""
if [ -n "$FEATURE_DIR" ]; then
    TASKS_CANDIDATE="${ROOT}/${FEATURE_DIR}/06-planning/tasks.md"
    [ -f "$TASKS_CANDIDATE" ] && TASKS_FILE="./${FEATURE_DIR}/06-planning/tasks.md"
fi

if [ "$REQUIRE_TASKS" = true ] && [ -z "$TASKS_FILE" ]; then
    FAILED+=("arquivo: ${FEATURE_DIR}/06-planning/tasks.md — obrigatório (--require-tasks)")
    GATE_RESULT="FAIL"
fi

# ---------------------------------------------------------------------------
# Verificação de constitution (global + projeto)
# ---------------------------------------------------------------------------
CONSTITUTION_OK="false"
CONSTITUTION_PATHS=$(load_constitution "$PROJECT")
if [ -n "$CONSTITUTION_PATHS" ]; then
    CONSTITUTION_OK="true"
fi

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
json_escape() {
    local value="${1:-}"
    value="${value//\\/\\\\}"
    value="${value//\"/\\\"}"
    value="${value//$'\t'/\\t}"
    value="${value//$'\r'/\\r}"
    value="${value//$'\n'/\\n}"
    printf '%s' "$value"
}

if [ "$JSON_OUTPUT" = true ]; then
    # Serializa arrays como strings JSON
    passed_json=""
    for p in "${PASSED[@]:-}"; do
        [ -n "$p" ] && passed_json="${passed_json}\"$(json_escape "$p")\","
    done
    passed_json="[${passed_json%,}]"

    failed_json=""
    for f in "${FAILED[@]:-}"; do
        [ -n "$f" ] && failed_json="${failed_json}\"$(json_escape "$f")\","
    done
    failed_json="[${failed_json%,}]"

    printf '{\n'
    printf '  "PROJECT": "%s",\n'          "$(json_escape "$PROJECT")"
    printf '  "FEATURE_DIR": "%s",\n'      "$(json_escape "$FEATURE_DIR")"
    printf '  "FEATURE_SLUG": "%s",\n'     "$(json_escape "$FEATURE_SLUG")"
    printf '  "FEATURE_NAME": "%s",\n'     "$(json_escape "$FEATURE_NAME")"
    printf '  "FEATURE_NUMBER": "%s",\n'   "$(json_escape "$FEATURE_NUMBER")"
    printf '  "STATUS": "%s",\n'           "$(json_escape "$FEATURE_STATUS")"
    printf '  "FASE_ATUAL": "%s",\n'       "$(json_escape "$FASE_ATUAL")"
    printf '  "PROJECT_STATUS": "%s",\n'   "$(json_escape "$PROJECT_STATUS")"
    printf '  "PROJECT_FASE": "%s",\n'     "$(json_escape "$PROJECT_FASE")"
    printf '  "CONSTITUTION_OK": %s,\n'    "${CONSTITUTION_OK}"
    printf '  "GATE_RESULT": "%s",\n'      "${GATE_RESULT}"
    printf '  "PASSED": %s,\n'             "${passed_json}"
    printf '  "FAILED": %s,\n'             "${failed_json}"
    printf '  "failures": %s,\n'           "${failed_json}"
    printf '  "TASKS_FILE": "%s"\n'        "$(json_escape "$TASKS_FILE")"
    printf '}\n'

else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "ARKAN — check-prerequisites"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Projeto : ${PROJECT:-não detectado} (${PROJECT_STATUS:-não iniciado})"
    echo "Feature : ${FEATURE_DIR:-não detectada}"
    echo "Status  : ${FEATURE_STATUS:-—} | Fase: ${FASE_ATUAL:-—}"
    echo "Gate    : ${GATE_RESULT}"

    if [ ${#FAILED[@]} -gt 0 ]; then
        echo ""
        echo "❌ Falhas:"
        for f in "${FAILED[@]}"; do [ -n "$f" ] && echo "  - $f"; done
    fi

    if [ ${#PASSED[@]} -gt 0 ]; then
        echo ""
        echo "✓ Passou:"
        for p in "${PASSED[@]}"; do [ -n "$p" ] && echo "  - $p"; done
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

# Exit code reflete resultado do gate
[ "$GATE_RESULT" = "PASS" ] && exit 0 || exit 1
