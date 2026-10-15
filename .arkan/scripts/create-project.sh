#!/usr/bin/env bash
# Arkan — create-project.sh
# Cria .arkan/projects/{slug}/ + status.md inicial (multi-projeto)
# Idempotente: se o projeto já existir, reporta o status atual sem modificar.
#
# Uso: create-project.sh [--json] [--project slug] [--name "nome-do-projeto"] ["Descrição"]
# Output JSON: { "PROJECT_DIR": ".arkan/projects/{slug}", "PROJECT": "...", "NAME": "...", "STATUS": "...", "ALREADY_EXISTS": bool }

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# ---------------------------------------------------------------------------
# Argumentos
# ---------------------------------------------------------------------------
JSON_OUTPUT=false
PROJECT=""
PROJECT_NAME=""
DESCRIPTION=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --json)     JSON_OUTPUT=true; shift ;;
        --project)  PROJECT="$2"; shift 2 ;;
        --name)     PROJECT_NAME="$2"; shift 2 ;;
        -*)         echo "Opção desconhecida: $1" >&2; exit 1 ;;
        *)          DESCRIPTION="$1"; shift ;;
    esac
done

ROOT=$(arkan_root)
TODAY=$(today_iso)

# ---------------------------------------------------------------------------
# Resolver slug do projeto
# ---------------------------------------------------------------------------
if [ -z "$PROJECT" ]; then
    PROJECT=$(resolve_project)
fi
if [ -z "$PROJECT" ] && [ -n "$PROJECT_NAME" ]; then
    # Derivar slug do nome: lowercase, espaços → hífens, remover caracteres inválidos
    PROJECT=$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g')
fi
if [ -z "$PROJECT" ]; then
    echo "Erro: projeto não especificado. Use --project slug ou --name \"Nome\"." >&2
    exit 1
fi

PROJECT_DIR_REL="$(project_dir "$PROJECT")"
PROJECT_DIR="${ROOT}/${PROJECT_DIR_REL}"

[ -z "$PROJECT_NAME" ] && PROJECT_NAME="$PROJECT"
[ -z "$DESCRIPTION" ]  && DESCRIPTION="Projeto Arkan"

# ---------------------------------------------------------------------------
# Idempotência: projeto já existe
# ---------------------------------------------------------------------------
if [ -f "${PROJECT_DIR}/status.md" ]; then
    CURRENT_STATUS=$(parse_yaml_field "${PROJECT_DIR}/status.md" "status")
    CURRENT_FASE=$(parse_yaml_field "${PROJECT_DIR}/status.md" "fase-atual")

    if [ "$JSON_OUTPUT" = true ]; then
        printf '{"PROJECT_DIR":"%s","PROJECT":"%s","NAME":"%s","STATUS":"%s","FASE_ATUAL":"%s","ALREADY_EXISTS":true}\n' \
            "$PROJECT_DIR_REL" "$PROJECT" "$PROJECT_NAME" "$CURRENT_STATUS" "$CURRENT_FASE"
    else
        echo "Projeto já existe: ${PROJECT}"
        echo "Status: ${CURRENT_STATUS} | Fase: ${CURRENT_FASE}"
        echo "Diretório: ${PROJECT_DIR_REL}"
    fi
    exit 0
fi

# ---------------------------------------------------------------------------
# Criar estrutura de diretórios
# ---------------------------------------------------------------------------
mkdir -p \
    "${PROJECT_DIR}/01-discovery" \
    "${PROJECT_DIR}/02-proposal"

# Garantir diretório de features do projeto
mkdir -p "${ROOT}/.arkan/features/${PROJECT}"

# ---------------------------------------------------------------------------
# Criar status.md
# ---------------------------------------------------------------------------
cat > "${PROJECT_DIR}/status.md" << STATUSEOF
---
status: em-discovery
fase-atual: 01-discovery
projeto: ${PROJECT}
atualizado-em: ${TODAY}
---

# Projeto: ${PROJECT_NAME}

${DESCRIPTION}
STATUSEOF

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
if [ "$JSON_OUTPUT" = true ]; then
    printf '{"PROJECT_DIR":"%s","PROJECT":"%s","NAME":"%s","STATUS":"em-discovery","FASE_ATUAL":"01-discovery","ALREADY_EXISTS":false}\n' \
        "$PROJECT_DIR_REL" "$PROJECT" "$PROJECT_NAME"
else
    echo "Projeto criado: ${PROJECT} (${PROJECT_DIR_REL})"
    echo "Nome: ${PROJECT_NAME}"
    echo "Features: .arkan/features/${PROJECT}/"
    echo "Status inicial: em-discovery"
fi
