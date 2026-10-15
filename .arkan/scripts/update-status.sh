#!/usr/bin/env bash
# Arkan — update-status.sh
# Atualiza campos do YAML front matter em status.md (feature ou projeto)
# Não sobrescreve campos não mencionados.
#
# Uso: update-status.sh --file PATH --field CAMPO --value VALOR

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# ---------------------------------------------------------------------------
# Argumentos
# ---------------------------------------------------------------------------
FILE=""
FIELD=""
VALUE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --file)  FILE="$2";  shift 2 ;;
        --field) FIELD="$2"; shift 2 ;;
        --value) VALUE="$2"; shift 2 ;;
        *)       echo "Opção desconhecida: $1" >&2; exit 1 ;;
    esac
done

if [ -z "$FILE" ] || [ -z "$FIELD" ] || [ -z "$VALUE" ]; then
    echo "Erro: --file, --field e --value são obrigatórios." >&2
    echo "Uso: update-status.sh --file PATH --field CAMPO --value VALOR" >&2
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "Erro: arquivo não encontrado: $FILE" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Atualizar campo e registrar data
# ---------------------------------------------------------------------------
update_yaml_field "$FILE" "$FIELD" "$VALUE"

# Atualiza atualizado-em automaticamente (exceto se o próprio campo for atualizado-em)
if [ "$FIELD" != "atualizado-em" ]; then
    update_yaml_field "$FILE" "atualizado-em" "$(today_iso)"
fi

echo "Atualizado: ${FIELD} = ${VALUE} em ${FILE}"
