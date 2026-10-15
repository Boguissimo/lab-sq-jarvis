#!/usr/bin/env bash
# Arkan — create-feature.sh
# Cria uma nova feature: branch git + estrutura de diretórios + status.md inicial
#
# Uso: create-feature.sh [--json] [--number N] [--parent NNN-000-slug] [--project slug] --short-name "nome" "Descrição"
# Output JSON: { "FEATURE_DIR": "...", "BRANCH": "...", "NUMBER": "NNN", "PROJECT": "..." }

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# ---------------------------------------------------------------------------
# Argumentos
# ---------------------------------------------------------------------------
JSON_OUTPUT=false
NUMBER=""
SHORT_NAME=""
DESCRIPTION=""
PARENT=""
PROJECT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --json)        JSON_OUTPUT=true; shift ;;
        --number)      NUMBER="$2"; shift 2 ;;
        --short-name)  SHORT_NAME="$2"; shift 2 ;;
        --parent)      PARENT="$2"; shift 2 ;;
        --project)     PROJECT="$2"; shift 2 ;;
        -*)            echo "Opção desconhecida: $1" >&2; exit 1 ;;
        *)             DESCRIPTION="$1"; shift ;;
    esac
done

if [ -z "$SHORT_NAME" ]; then
    echo "Erro: --short-name é obrigatório." >&2
    echo "Uso: create-feature.sh [--json] [--number N] [--parent NNN-000-slug] [--project slug] --short-name \"nome\" \"Descrição\"" >&2
    exit 1
fi

[ -z "$DESCRIPTION" ] && DESCRIPTION="$SHORT_NAME"

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

# Garantir que o diretório do projeto existe
mkdir -p ".arkan/features/${PROJECT}" ".arkan/projects/${PROJECT}"

# ---------------------------------------------------------------------------
# Determinar número e nome (parent vs child)
# ---------------------------------------------------------------------------
if [ -n "$PARENT" ]; then
    # Sub-feature: extrair parent_id e gerar child_number
    parse_feature_hierarchy "$(basename "$PARENT")"
    PARENT_NUM="$PARENT_ID"
    PARENT_DIR=$(find_parent_dir "$PARENT_NUM" "$PROJECT")
    if [ -z "$PARENT_DIR" ]; then
        echo "Erro: feature-pai '${PARENT}' não encontrada no projeto '${PROJECT}'." >&2
        exit 1
    fi
    PARENT_BASENAME=$(basename "$PARENT_DIR")
    CHILD_NUM=$(next_child_number "$PARENT_NUM" "$PROJECT")
    NNN="${PARENT_NUM}"
    FEATURE_NAME="${PARENT_NUM}-${CHILD_NUM}-${SHORT_NAME}"
    BRANCH_NAME="${PROJECT}/${FEATURE_NAME}"
    PAI_FIELD="$PARENT_BASENAME"
else
    # Feature principal: NNN-000-slug
    if [ -z "$NUMBER" ]; then
        NUMBER=$(next_feature_number "$PROJECT")
    fi
    NNN=$(printf "%03d" "$((10#$NUMBER))")
    FEATURE_NAME="${NNN}-000-${SHORT_NAME}"
    BRANCH_NAME="${PROJECT}/${FEATURE_NAME}"
    PAI_FIELD=""
fi

ROOT=$(arkan_root)
FEATURE_DIR="${ROOT}/.arkan/features/${PROJECT}/${FEATURE_NAME}"
FEATURE_DIR_REL=".arkan/features/${PROJECT}/${FEATURE_NAME}"
TODAY=$(today_iso)

# ---------------------------------------------------------------------------
# Verificar se já existe
# ---------------------------------------------------------------------------
if [ -d "$FEATURE_DIR" ]; then
    echo "Erro: diretório ${FEATURE_DIR_REL} já existe." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Criar branch git (só cria se não existir)
# ---------------------------------------------------------------------------
if ! git show-ref --quiet "refs/heads/${BRANCH_NAME}" 2>/dev/null; then
    git checkout -b "$BRANCH_NAME" 2>/dev/null
else
    git checkout "$BRANCH_NAME" 2>/dev/null
fi

# ---------------------------------------------------------------------------
# Criar estrutura de diretórios
# ---------------------------------------------------------------------------
mkdir -p \
    "${FEATURE_DIR}/01-discovery" \
    "${FEATURE_DIR}/02-proposta" \
    "${FEATURE_DIR}/03-spec" \
    "${FEATURE_DIR}/04-architecture/contracts" \
    "${FEATURE_DIR}/05-ux" \
    "${FEATURE_DIR}/06-planning" \
    "${FEATURE_DIR}/07-development" \
    "${FEATURE_DIR}/08-qa/checklists" \
    "${FEATURE_DIR}/09-deploy" \
    "${FEATURE_DIR}/10-ops"

# ---------------------------------------------------------------------------
# Criar status.md
# ---------------------------------------------------------------------------
if [ -n "$PAI_FIELD" ]; then
cat > "${FEATURE_DIR}/status.md" << STATUSEOF
---
status: em-desenvolvimento
fase-atual: 01-discovery
pai: ${PAI_FIELD}
projeto: ${PROJECT}
atualizado-em: ${TODAY}
---

# ${FEATURE_NAME}

Sub-feature de ${PAI_FIELD}.

${DESCRIPTION}
STATUSEOF
else
cat > "${FEATURE_DIR}/status.md" << STATUSEOF
---
status: em-desenvolvimento
fase-atual: 01-discovery
projeto: ${PROJECT}
atualizado-em: ${TODAY}
---

# ${FEATURE_NAME}

${DESCRIPTION}
STATUSEOF
fi

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
if [ "$JSON_OUTPUT" = true ]; then
    printf '{"FEATURE_DIR":"%s","BRANCH":"%s","NUMBER":"%s","PROJECT":"%s"}\n' \
        "$FEATURE_DIR_REL" "$BRANCH_NAME" "$NNN" "$PROJECT"
else
    echo "Feature criada: ${FEATURE_NAME}"
    echo "Projeto: ${PROJECT}"
    echo "Diretório: ${FEATURE_DIR_REL}"
    echo "Branch: ${BRANCH_NAME}"
fi
