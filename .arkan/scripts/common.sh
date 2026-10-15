#!/usr/bin/env bash
# Arkan — common.sh
# Funções compartilhadas entre todos os scripts Arkan
# Compatível com: bash/zsh (Unix) e Git Bash (Windows) — NFR-005

# Garantir UTF-8 para sed/grep com caracteres acentuados (PT-BR)
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

# ---------------------------------------------------------------------------
# parse_yaml_field FILE FIELD
# Extrai o valor de um campo do YAML front matter (entre --- e ---)
# ---------------------------------------------------------------------------
parse_yaml_field() {
    local file="$1"
    local field="$2"
    sed -n '/^---$/,/^---$/p' "$file" \
        | grep "^${field}:" \
        | head -1 \
        | sed "s/^${field}:[[:space:]]*//" \
        | tr -d '\r'
}

# ---------------------------------------------------------------------------
# update_yaml_field FILE FIELD VALUE
# Atualiza um campo no YAML front matter.
# Se o campo não existir, adiciona antes do segundo ---.
# Não sobrescreve campos não mencionados.
# ---------------------------------------------------------------------------
update_yaml_field() {
    local file="$1"
    local field="$2"
    local value="$3"
    local tmpfile
    tmpfile=$(mktemp)

    if grep -q "^${field}:" "$file"; then
        sed "s|^${field}:.*|${field}: ${value}|" "$file" > "$tmpfile"
    else
        awk -v f="$field" -v v="$value" '
            /^---$/ && ++count == 2 { print f ": " v }
            { print }
        ' "$file" > "$tmpfile"
    fi
    mv "$tmpfile" "$file"
}

# ---------------------------------------------------------------------------
# resolve_project [PROJECT_SLUG]
# Resolve o projeto ativo. Ordem de prioridade:
# 1. Argumento explícito
# 2. Branch git (prefixo antes do /)
# 3. Campo projeto-default em .arkan/config.md
# 4. Único projeto em .arkan/features/ (se só 1 existir)
# Retorna o slug do projeto ou string vazia.
# ---------------------------------------------------------------------------
resolve_project() {
    local explicit="${1:-}"

    # 1. Argumento explícito
    if [ -n "$explicit" ]; then
        echo "$explicit"
        return
    fi

    # 2. Branch git: {projeto}/{NNN-CCC-slug}
    local branch
    branch=$(git branch --show-current 2>/dev/null | tr -d '\r')
    if [ -n "$branch" ] && [[ "$branch" == */* ]]; then
        echo "${branch%%/*}"
        return
    fi

    # 3. Config default
    if [ -f ".arkan/config.md" ]; then
        local default_proj
        default_proj=$(parse_yaml_field ".arkan/config.md" "projeto-default")
        if [ -n "$default_proj" ]; then
            echo "$default_proj"
            return
        fi
    fi

    # 4. Único projeto em features/
    if [ -d ".arkan/features" ]; then
        local count
        count=$(find ".arkan/features" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l)
        if [ "$count" -eq 1 ]; then
            basename "$(find ".arkan/features" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | head -1)"
            return
        fi
    fi

    echo ""
}

# ---------------------------------------------------------------------------
# features_base [PROJECT_SLUG]
# Retorna o caminho base das features para um projeto.
# ---------------------------------------------------------------------------
features_base() {
    local project="${1:-}"
    if [ -z "$project" ]; then
        project=$(resolve_project)
    fi
    if [ -n "$project" ]; then
        echo ".arkan/features/${project}"
    else
        echo ".arkan/features"
    fi
}

# ---------------------------------------------------------------------------
# project_dir [PROJECT_SLUG]
# Retorna o caminho do diretório de metadata do projeto.
# ---------------------------------------------------------------------------
project_dir() {
    local project="${1:-}"
    if [ -z "$project" ]; then
        project=$(resolve_project)
    fi
    echo ".arkan/projects/${project}"
}

# ---------------------------------------------------------------------------
# find_feature_dir [FEATURE_ID] [PROJECT_SLUG]
# Encontra o diretório da feature.
# Sem argumento: infere da branch git atual.
# Com argumento: busca por prefixo no projeto.
# Retorna caminho relativo à raiz do repositório, ou string vazia.
# ---------------------------------------------------------------------------
find_feature_dir() {
    local target="${1:-}"
    local project="${2:-}"
    local base
    base=$(features_base "$project")

    if [ -n "$target" ]; then
        local dir
        dir=$(find "$base" -maxdepth 1 -type d -name "${target}*" 2>/dev/null | head -1)
        echo "$dir"
        return
    fi

    local branch
    branch=$(git branch --show-current 2>/dev/null | tr -d '\r')
    [ -z "$branch" ] && echo "" && return

    # Branch format: {projeto}/{NNN-CCC-slug} ou {NNN-CCC-slug}
    local feature_id
    if [[ "$branch" == */* ]]; then
        feature_id="${branch#*/}"
    else
        feature_id=$(echo "$branch" | grep -E '^[0-9]+-')
    fi
    [ -z "$feature_id" ] && echo "" && return

    local dir="${base}/${feature_id}"
    [ -d "$dir" ] && echo "$dir" || echo ""
}

# ---------------------------------------------------------------------------
# next_feature_number [PROJECT_SLUG]
# Retorna o próximo número NNN disponível com zero-padding (001, 002, ...).
# Consulta diretórios de features do projeto.
# ---------------------------------------------------------------------------
next_feature_number() {
    local project="${1:-}"
    local base
    base=$(features_base "$project")
    local max=0
    local num

    if [ -d "$base" ]; then
        while IFS= read -r dir; do
            dir=$(basename "$dir")
            num=$(echo "$dir" | grep -oE '^[0-9]+' | head -1)
            if [ -n "$num" ] && [ $((10#$num)) -gt $((10#$max)) ]; then max=$((10#$num)); fi
        done < <(find "$base" -maxdepth 1 -mindepth 1 -type d 2>/dev/null)
    fi

    printf "%03d" $((10#$max + 1))
}

# ---------------------------------------------------------------------------
# parse_feature_hierarchy NAME
# Extrai parent_id, child_id e slug de um nome de feature.
# Padrão: NNN-000-slug (parent) ou NNN-CCC-slug (child, CCC > 000)
# Seta variáveis: PARENT_ID, CHILD_ID, FEATURE_SLUG, IS_CHILD
# ---------------------------------------------------------------------------
parse_feature_hierarchy() {
    local name="$1"
    if [[ "$name" =~ ^([0-9]{3})-([0-9]{3})-(.+)$ ]]; then
        PARENT_ID="${BASH_REMATCH[1]}"
        CHILD_ID="${BASH_REMATCH[2]}"
        FEATURE_SLUG="${BASH_REMATCH[3]}"
        if [ "$CHILD_ID" = "000" ]; then
            IS_CHILD=false
        else
            IS_CHILD=true
        fi
    else
        PARENT_ID=""
        CHILD_ID=""
        FEATURE_SLUG="$name"
        IS_CHILD=false
    fi
}

# ---------------------------------------------------------------------------
# find_parent_dir PARENT_ID [PROJECT_SLUG]
# Encontra o diretório da feature-pai pelo ID numérico (ex: "002").
# Retorna caminho relativo ou string vazia.
# ---------------------------------------------------------------------------
find_parent_dir() {
    local parent_id="$1"
    local project="${2:-}"
    local base
    base=$(features_base "$project")
    local dir
    dir=$(find "$base" -maxdepth 1 -type d -name "${parent_id}-000-*" 2>/dev/null | head -1)
    echo "$dir"
}

# ---------------------------------------------------------------------------
# next_child_number PARENT_ID [PROJECT_SLUG]
# Retorna o próximo número CCC disponível para sub-features de um parent.
# ---------------------------------------------------------------------------
next_child_number() {
    local parent_id="$1"
    local project="${2:-}"
    local base
    base=$(features_base "$project")
    local max=0
    local num

    if [ -d "$base" ]; then
        while IFS= read -r dir; do
            dir=$(basename "$dir")
            if [[ "$dir" =~ ^${parent_id}-([0-9]{3})- ]]; then
                num="${BASH_REMATCH[1]}"
                if [ $((10#$num)) -gt $((10#$max)) ]; then max=$((10#$num)); fi
            fi
        done < <(find "$base" -maxdepth 1 -mindepth 1 -type d 2>/dev/null)
    fi

    printf "%03d" $((10#$max + 1))
}

# ---------------------------------------------------------------------------
# load_constitution [PROJECT_SLUG]
# Retorna os caminhos das constitutions a carregar (global + projeto).
# ---------------------------------------------------------------------------
load_constitution() {
    local project="${1:-}"
    local global=".arkan/memory/constitution.md"
    local proj_const
    if [ -n "$project" ]; then
        proj_const=".arkan/projects/${project}/constitution.md"
    fi

    if [ -f "$global" ]; then
        echo "$global"
    fi
    if [ -n "$proj_const" ] && [ -f "$proj_const" ]; then
        echo "$proj_const"
    fi
}

# ---------------------------------------------------------------------------
# arkan_root
# Retorna o caminho absoluto da raiz do repositório git.
# ---------------------------------------------------------------------------
arkan_root() {
    git rev-parse --show-toplevel 2>/dev/null
}

# ---------------------------------------------------------------------------
# today_iso
# Retorna a data de hoje no formato ISO 8601 (YYYY-MM-DD).
# ---------------------------------------------------------------------------
today_iso() {
    date +%Y-%m-%d
}
