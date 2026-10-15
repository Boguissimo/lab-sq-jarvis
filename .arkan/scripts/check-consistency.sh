#!/usr/bin/env bash
# Arkan — check-consistency.sh
# Verificação de consistência cruzada entre artefatos de uma feature:
# spec↔plan, plan↔tasks, tasks↔status, referências de agentes em commands.
#
# Uso: check-consistency.sh [--json] [FEATURE_ID]
# Sem FEATURE_ID: infere da branch git atual.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# ---------------------------------------------------------------------------
# Argumentos
# ---------------------------------------------------------------------------
JSON_OUTPUT=false
FEATURE_ARG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --json) JSON_OUTPUT=true; shift ;;
        *)      FEATURE_ARG="$1"; shift ;;
    esac
done

ROOT=$(arkan_root)
cd "$ROOT" || exit 1

# ---------------------------------------------------------------------------
# Detectar feature
# ---------------------------------------------------------------------------
if [ -n "$FEATURE_ARG" ]; then
    FEATURE_DIR=$(find_feature_dir "$FEATURE_ARG")
else
    FEATURE_DIR=$(find_feature_dir)
fi

if [ -z "$FEATURE_DIR" ] || [ ! -d "$FEATURE_DIR" ]; then
    echo "ERRO: Feature não encontrada. Forneça o ID ou esteja em uma branch de feature." >&2
    exit 1
fi

FEATURE_NAME=$(basename "$FEATURE_DIR")

# ---------------------------------------------------------------------------
# Contadores
# ---------------------------------------------------------------------------
TOTAL_CHECKS=0
PASSED=0
WARNINGS=0
FAILURES=0

RESULTS_PASS=()
RESULTS_WARN=()
RESULTS_FAIL=()

check_pass() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    PASSED=$((PASSED + 1))
    RESULTS_PASS+=("$1")
}

check_warn() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    WARNINGS=$((WARNINGS + 1))
    RESULTS_WARN+=("$1")
}

check_fail() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    FAILURES=$((FAILURES + 1))
    RESULTS_FAIL+=("$1")
}

# ---------------------------------------------------------------------------
# 1. Spec ↔ Plan: user stories referenciadas
# ---------------------------------------------------------------------------
SPEC="${FEATURE_DIR}/03-spec/spec.md"
PLAN="${FEATURE_DIR}/04-architecture/plan.md"

if [ -f "$SPEC" ] && [ -f "$PLAN" ]; then
    # Extrair user stories da spec (linhas que começam com ### US ou contêm US[0-9])
    spec_stories=$(grep -oE 'US[0-9]+' "$SPEC" 2>/dev/null | sort -u || true)

    if [ -n "$spec_stories" ]; then
        while IFS= read -r us; do
            [ -z "$us" ] && continue
            if grep -q "$us" "$PLAN" 2>/dev/null; then
                check_pass "spec→plan: ${us} referenciada no plan"
            else
                check_warn "spec→plan: ${us} na spec mas não referenciada no plan"
            fi
        done <<< "$spec_stories"
    else
        check_warn "spec→plan: nenhuma user story (US[N]) encontrada na spec"
    fi
else
    [ ! -f "$SPEC" ] && check_warn "spec↔plan: spec.md não existe — verificação pulada"
    [ ! -f "$PLAN" ] && check_warn "spec↔plan: plan.md não existe — verificação pulada"
fi

# ---------------------------------------------------------------------------
# 2. Plan ↔ Tasks: arquivos do plan referenciados em tasks
# ---------------------------------------------------------------------------
TASKS="${FEATURE_DIR}/06-planning/tasks.md"

if [ -f "$PLAN" ] && [ -f "$TASKS" ]; then
    # Extrair arquivos mencionados na Estrutura do Projeto do plan
    # Procura por linhas com extensão de arquivo comuns
    plan_files=$(grep -oE '[a-zA-Z0-9_./-]+\.(ts|tsx|js|jsx|py|sh|md|json|yaml|yml|sql|css|html|vue|svelte)' "$PLAN" 2>/dev/null | sort -u || true)

    if [ -n "$plan_files" ]; then
        plan_file_count=$(echo "$plan_files" | wc -l | tr -d ' ')
        tasks_file_refs=$(grep -oE 'File:\s*.*' "$TASKS" 2>/dev/null | sed 's/File:[[:space:]]*//' || true)

        if [ -n "$tasks_file_refs" ]; then
            check_pass "plan→tasks: plan referencia ${plan_file_count} arquivo(s), tasks tem campos File:"
        else
            check_warn "plan→tasks: plan referencia ${plan_file_count} arquivo(s) mas tasks.md não tem campos File:"
        fi
    fi
else
    [ ! -f "$TASKS" ] && [ -f "$PLAN" ] && check_warn "plan↔tasks: tasks.md não existe — verificação pulada"
fi

# ---------------------------------------------------------------------------
# 3. Tasks ↔ Status: progresso coerente com fase-atual
# ---------------------------------------------------------------------------
if [ -f "$TASKS" ] && [ -f "${FEATURE_DIR}/status.md" ]; then
    fase_atual=$(parse_yaml_field "${FEATURE_DIR}/status.md" "fase-atual")
    total_tasks=$(grep -cE '^\s*- \[[ x]\]' "$TASKS" 2>/dev/null || echo "0")
    done_tasks=$(grep -cE '^\s*- \[x\]' "$TASKS" 2>/dev/null || echo "0")

    if [ "$total_tasks" -gt 0 ]; then
        # Se fase-atual é 07 (implementação) ou posterior, deve haver tasks concluídas
        fase_num=$(echo "$fase_atual" | grep -oE '^[0-9]+' || echo "0")

        if [ "$fase_num" -ge 7 ] && [ "$done_tasks" -eq 0 ]; then
            check_warn "tasks↔status: fase-atual=${fase_atual} mas 0 tasks concluídas"
        elif [ "$fase_num" -ge 8 ] && [ "$done_tasks" -lt "$total_tasks" ]; then
            open=$((total_tasks - done_tasks))
            check_warn "tasks↔status: fase-atual=${fase_atual} (QA+) mas ${open} tasks ainda abertas"
        else
            check_pass "tasks↔status: ${done_tasks}/${total_tasks} tasks concluídas, fase-atual=${fase_atual}"
        fi
    fi
fi

# ---------------------------------------------------------------------------
# 4. Referências de agentes em commands apontam para arquivos existentes
# ---------------------------------------------------------------------------
AGENTS_DIR=".arkan/agents"
COMMANDS_DIR=".claude/commands"

if [ -d "$COMMANDS_DIR" ]; then
    # Encontrar todas as referências a arquivos de agente nos commands
    agent_refs=$(grep -ohE '\.arkan/agents/[a-zA-Z0-9_/-]+\.md' "${COMMANDS_DIR}"/arkan.*.md 2>/dev/null | sort -u || true)

    if [ -n "$agent_refs" ]; then
        while IFS= read -r ref; do
            [ -z "$ref" ] && continue
            if [ -f "$ref" ]; then
                check_pass "agent ref: ${ref} existe"
            else
                check_fail "agent ref: ${ref} referenciado em command mas arquivo não existe"
            fi
        done <<< "$agent_refs"
    else
        check_warn "agent refs: nenhuma referência a agentes encontrada nos commands"
    fi
fi

# ---------------------------------------------------------------------------
# 5. Agentes com ## PROMPT obrigatório
# ---------------------------------------------------------------------------
if [ -d "$AGENTS_DIR" ]; then
    while IFS= read -r agent_file; do
        [ -z "$agent_file" ] && continue
        rel=$(echo "$agent_file" | sed 's|^\./||')

        if grep -q "^## PROMPT" "$agent_file" 2>/dev/null; then
            check_pass "agent struct: ${rel} tem ## PROMPT"
        else
            check_fail "agent struct: ${rel} falta ## PROMPT"
        fi
    done < <(find "$AGENTS_DIR" -name "*.md" -type f 2>/dev/null)
fi

# ---------------------------------------------------------------------------
# 6. Spec invariantes ↔ plan Constitution Check
# ---------------------------------------------------------------------------
if [ -f "$SPEC" ] && [ -f "$PLAN" ]; then
    spec_invariants=$(grep -cE '^\s*[0-9]+\.' "${SPEC}" 2>/dev/null || echo "0")
    # Verificar se plan tem Constitution Check
    if grep -q "Constitution Check" "$PLAN" 2>/dev/null; then
        check_pass "spec↔plan: plan.md contém Constitution Check"
    else
        check_warn "spec↔plan: plan.md não contém Constitution Check"
    fi
fi

# ---------------------------------------------------------------------------
# 7. Spec Key Entities ↔ data-model.md
# ---------------------------------------------------------------------------
DATA_MODEL="${FEATURE_DIR}/04-architecture/data-model.md"

if [ -f "$SPEC" ] && [ -f "$DATA_MODEL" ]; then
    # Verificar que data-model existe quando spec tem Key Entities
    if grep -q "Key Entities" "$SPEC" 2>/dev/null; then
        check_pass "spec↔data-model: spec tem Key Entities e data-model.md existe"
    fi
elif [ -f "$SPEC" ] && grep -q "Key Entities" "$SPEC" 2>/dev/null && [ ! -f "$DATA_MODEL" ]; then
    check_warn "spec↔data-model: spec tem Key Entities mas data-model.md não existe"
fi

# ---------------------------------------------------------------------------
# 7b. Entidade com status ⇒ máquina de estados no data-model (S-05)
# ---------------------------------------------------------------------------
# O data-modeler exige state machine (tabela De|Para|Guard|Efeito|Ator + transições
# proibidas) para entidade com campo status — este check garante que a exigência
# não foi descartada. Referência: docs/investigacoes/templates-legados-vs-arkan.md (S-05).
if [ -f "$DATA_MODEL" ]; then
    if grep -qiE '\bstatus\b|status_[a-z]+|ciclo de vida' "$DATA_MODEL" 2>/dev/null; then
        if grep -qE '\|\s*De\s*\|\s*Para\s*\|' "$DATA_MODEL" 2>/dev/null; then
            check_pass "data-model: entidade com status tem tabela de transições (De|Para)"
            if ! grep -qi "transições proibidas\|transicoes proibidas" "$DATA_MODEL" 2>/dev/null; then
                check_warn "data-model: tabela de transições sem lista de transições proibidas"
            fi
        else
            check_warn "data-model: menciona campo status/ciclo de vida mas não tem tabela de transições (| De | Para |) — exigida pelo data-modeler"
        fi
    fi
fi

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
STATUS="CONSISTENT"
[ "$WARNINGS" -gt 0 ] && STATUS="MINOR_INCONSISTENCIES"
[ "$FAILURES" -gt 0 ] && STATUS="INCONSISTENT"

if [ "$JSON_OUTPUT" = true ]; then
    pass_json=""
    for p in "${RESULTS_PASS[@]:-}"; do
        [ -n "$p" ] && pass_json="${pass_json}\"${p}\","
    done
    pass_json="[${pass_json%,}]"

    warn_json=""
    for w in "${RESULTS_WARN[@]:-}"; do
        [ -n "$w" ] && warn_json="${warn_json}\"${w}\","
    done
    warn_json="[${warn_json%,}]"

    fail_json=""
    for f in "${RESULTS_FAIL[@]:-}"; do
        [ -n "$f" ] && fail_json="${fail_json}\"${f}\","
    done
    fail_json="[${fail_json%,}]"

    printf '{\n'
    printf '  "FEATURE_DIR": "%s",\n'   "${FEATURE_DIR}"
    printf '  "FEATURE_NAME": "%s",\n'  "${FEATURE_NAME}"
    printf '  "STATUS": "%s",\n'        "${STATUS}"
    printf '  "TOTAL_CHECKS": %d,\n'    "${TOTAL_CHECKS}"
    printf '  "PASSED": %d,\n'          "${PASSED}"
    printf '  "WARNINGS": %d,\n'        "${WARNINGS}"
    printf '  "FAILURES": %d,\n'        "${FAILURES}"
    printf '  "RESULTS_PASS": %s,\n'    "${pass_json}"
    printf '  "RESULTS_WARN": %s,\n'    "${warn_json}"
    printf '  "RESULTS_FAIL": %s\n'     "${fail_json}"
    printf '}\n'

else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "ARKAN — Verificação de Consistência"
    echo "Feature: ${FEATURE_NAME}"
    echo "Status : ${STATUS}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Resultado: ${PASSED} pass | ${WARNINGS} warn | ${FAILURES} fail (${TOTAL_CHECKS} checks)"

    if [ ${#RESULTS_FAIL[@]} -gt 0 ]; then
        echo ""
        echo "❌ Inconsistências:"
        for f in "${RESULTS_FAIL[@]}"; do [ -n "$f" ] && echo "  - $f"; done
    fi

    if [ ${#RESULTS_WARN[@]} -gt 0 ]; then
        echo ""
        echo "⚠️  Avisos:"
        for w in "${RESULTS_WARN[@]}"; do [ -n "$w" ] && echo "  - $w"; done
    fi

    if [ ${#RESULTS_PASS[@]} -gt 0 ]; then
        echo ""
        echo "✓ Consistente:"
        for p in "${RESULTS_PASS[@]}"; do [ -n "$p" ] && echo "  - $p"; done
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

[ "$FAILURES" -eq 0 ] && exit 0 || exit 1
