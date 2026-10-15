#!/usr/bin/env bash
# Arkan — qa-mecanico.sh
# Verificação mecânica de artefatos de uma feature: contagem de arquivos,
# presença de seções obrigatórias, placeholders abertos e referências cruzadas.
#
# Uso: qa-mecanico.sh [--json] [FEATURE_ID]
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
# 1. Verificar existência de artefatos por fase
# ---------------------------------------------------------------------------
check_file() {
    local path="$1"
    local label="$2"
    local required="$3"  # "required" ou "optional"

    if [ -f "$path" ]; then
        check_pass "Arquivo existe: ${label}"
    elif [ "$required" = "required" ]; then
        check_fail "Arquivo obrigatório ausente: ${label}"
    else
        check_warn "Arquivo opcional ausente: ${label}"
    fi
}

# Fase 01
check_file "${FEATURE_DIR}/01-discovery/ideacao.md" "01-discovery/ideacao.md" "required"

# Fase 03
check_file "${FEATURE_DIR}/03-spec/spec.md" "03-spec/spec.md" "optional"

# Fase 04
check_file "${FEATURE_DIR}/04-architecture/plan.md" "04-architecture/plan.md" "optional"
check_file "${FEATURE_DIR}/04-architecture/data-model.md" "04-architecture/data-model.md" "optional"
check_file "${FEATURE_DIR}/04-architecture/quickstart.md" "04-architecture/quickstart.md" "optional"

# Fase 06
check_file "${FEATURE_DIR}/06-planning/tasks.md" "06-planning/tasks.md" "optional"

# Fase 08
check_file "${FEATURE_DIR}/08-qa/qa-report.md" "08-qa/qa-report.md" "optional"
check_file "${FEATURE_DIR}/08-qa/alinhamento-report.md" "08-qa/alinhamento-report.md" "optional"

# status.md
check_file "${FEATURE_DIR}/status.md" "status.md" "required"

# ---------------------------------------------------------------------------
# 2. Verificar seções obrigatórias em artefatos existentes
# ---------------------------------------------------------------------------
check_section() {
    local file="$1"
    local section="$2"
    local label="$3"

    if [ ! -f "$file" ]; then
        return  # arquivo não existe — já reportado acima
    fi

    if grep -q "^${section}" "$file" 2>/dev/null; then
        check_pass "Seção presente: ${label}"
    else
        check_fail "Seção ausente: ${label}"
    fi
}

# ideacao.md
check_section "${FEATURE_DIR}/01-discovery/ideacao.md" "## Síntese" "## Síntese em ideacao.md"
check_section "${FEATURE_DIR}/01-discovery/ideacao.md" "## Decisões Tomadas" "## Decisões Tomadas em ideacao.md"

# spec.md
if [ -f "${FEATURE_DIR}/03-spec/spec.md" ]; then
    check_section "${FEATURE_DIR}/03-spec/spec.md" "## Requirements" "## Requirements em spec.md"
    check_section "${FEATURE_DIR}/03-spec/spec.md" "## Invariantes" "## Invariantes em spec.md"
    check_section "${FEATURE_DIR}/03-spec/spec.md" "## Cenários de Usuário" "## Cenários de Usuário em spec.md"
fi

# plan.md
if [ -f "${FEATURE_DIR}/04-architecture/plan.md" ]; then
    check_section "${FEATURE_DIR}/04-architecture/plan.md" "## ADRs" "## ADRs em plan.md"
    check_section "${FEATURE_DIR}/04-architecture/plan.md" "## Dependências e Interfaces" "## Dependências e Interfaces em plan.md"
    check_section "${FEATURE_DIR}/04-architecture/plan.md" "## Sequência de Implementação" "## Sequência de Implementação em plan.md"
fi

# tasks.md
if [ -f "${FEATURE_DIR}/06-planning/tasks.md" ]; then
    check_section "${FEATURE_DIR}/06-planning/tasks.md" "## Fase 1" "## Fase 1 em tasks.md"
fi

# qa-report.md
if [ -f "${FEATURE_DIR}/08-qa/qa-report.md" ]; then
    check_section "${FEATURE_DIR}/08-qa/qa-report.md" "## Resultado do QA" "## Resultado do QA em qa-report.md"
fi

# ---------------------------------------------------------------------------
# 3. Verificar placeholders abertos
# ---------------------------------------------------------------------------
PLACEHOLDERS=("[NEEDS CLARIFICATION]" "[TODO]" "[PLACEHOLDER]" "[A DEFINIR]" "[NEEDS PATH]" "[REQUER DECISÃO]" "[REQUER CONTEXTO]")

for ph in "${PLACEHOLDERS[@]}"; do
    matches=$(grep -rl "$ph" "${FEATURE_DIR}" 2>/dev/null | grep -v '/10-ops/' || true)
    if [ -n "$matches" ]; then
        count=$(echo "$matches" | wc -l | tr -d ' ')
        files=$(echo "$matches" | sed "s|${FEATURE_DIR}/||g" | tr '\n' ', ' | sed 's/,$//')
        check_warn "Placeholder aberto '${ph}' em ${count} arquivo(s): ${files}"
    fi
done

# ---------------------------------------------------------------------------
# 4. Verificar tasks — progresso
# ---------------------------------------------------------------------------
if [ -f "${FEATURE_DIR}/06-planning/tasks.md" ]; then
    TOTAL_TASKS=$(grep -cE '^\s*- \[[ x]\]' "${FEATURE_DIR}/06-planning/tasks.md" 2>/dev/null || true)
    DONE_TASKS=$(grep -cE '^\s*- \[x\]' "${FEATURE_DIR}/06-planning/tasks.md" 2>/dev/null || true)
    # 'grep -c' imprime "0" E sai com status 1 quando não casa nada. Com
    # '|| echo "0"' as duas saídas se somavam, a variável virava a string de
    # duas linhas "0\n0", a aritmética abaixo estourava e a checagem de tasks
    # sumia inteira — nem pass, nem warn — em 11 features. Use '|| true'.
    TOTAL_TASKS=${TOTAL_TASKS:-0}
    DONE_TASKS=${DONE_TASKS:-0}
    OPEN_TASKS=$((TOTAL_TASKS - DONE_TASKS))

    if [ "$TOTAL_TASKS" -gt 0 ]; then
        check_pass "Tasks: ${DONE_TASKS}/${TOTAL_TASKS} concluídas (${OPEN_TASKS} abertas)"
    else
        check_warn "tasks.md existe mas nenhuma task encontrada"
    fi
fi

# ---------------------------------------------------------------------------
# 5. Verificar arquivos vazios (artefatos com 0 bytes)
# ---------------------------------------------------------------------------
while IFS= read -r f; do
    [ -z "$f" ] && continue
    if [ ! -s "$f" ]; then
        rel=$(echo "$f" | sed "s|${FEATURE_DIR}/||")
        check_warn "Arquivo vazio: ${rel}"
    fi
done < <(find "${FEATURE_DIR}" -name "*.md" -type f 2>/dev/null)

# ---------------------------------------------------------------------------
# 6. Verificar consistência status.md
# ---------------------------------------------------------------------------
if [ -f "${FEATURE_DIR}/status.md" ]; then
    status_val=$(parse_yaml_field "${FEATURE_DIR}/status.md" "status")
    fase_val=$(parse_yaml_field "${FEATURE_DIR}/status.md" "fase-atual")

    if [ -n "$status_val" ]; then
        check_pass "status.md campo 'status': ${status_val}"
    else
        check_fail "status.md campo 'status' vazio ou ausente"
    fi

    if [ -n "$fase_val" ]; then
        check_pass "status.md campo 'fase-atual': ${fase_val}"
    else
        check_fail "status.md campo 'fase-atual' vazio ou ausente"
    fi
fi

# ---------------------------------------------------------------------------
# 6a. Superfície crítica — obrigações extras (BLOQUEANTE)
# ---------------------------------------------------------------------------
# Feature com superficie-critica: sim exige a seção ## Obrigações da Superfície
# Crítica na ideação. O que conta como "crítico" para este projeto, e a política
# para cada superfície, é decisão de cada projeto — declarada em
# .arkan/projects/<projeto>/constitution.md, tabela "Decisões de contexto"
# ("se não houver resposta clara → feature não entra").
# Só dispara em features novas — antigas não têm o campo no status.md.
if [ -f "${FEATURE_DIR}/status.md" ]; then
    superficie=$(parse_yaml_field "${FEATURE_DIR}/status.md" "superficie-critica")
    if [ "$superficie" = "sim" ]; then
        if grep -q "^## Obrigações da Superfície Crítica" "${FEATURE_DIR}/01-discovery/ideacao.md" 2>/dev/null; then
            check_pass "Obrigações da Superfície Crítica presentes na ideação (superficie-critica: sim)"
        else
            check_fail "Obrigações da Superfície Crítica AUSENTES na ideação — obrigatório com superficie-critica: sim"
        fi
    fi
fi

# ---------------------------------------------------------------------------
# 6b. Conteúdo interno da spec (S-02/S-03 — modo WARN)
# ---------------------------------------------------------------------------
# Invariante (linha INV-) sem "Teste:" é decoração; SC sem "Instrumento:" é
# imensurável. Modo WARN pela mesma razão da S-01: specs antigas usam os mesmos
# formatos e o corpus não é retrofitado. Endurecer junto com a S-01.
# Referência: docs/investigacoes/templates-legados-vs-arkan.md (S-02, S-03).
SPEC_FILE="${FEATURE_DIR}/03-spec/spec.md"
if [ -f "$SPEC_FILE" ]; then
    inv_sem_teste=$(awk '/^## Invariantes/{f=1;next} /^## /{f=0} f && /INV-/ && !/Teste:/' "$SPEC_FILE" | grep -c "INV-" 2>/dev/null)
    if [ "${inv_sem_teste:-0}" -gt 0 ]; then
        check_warn "Spec: ${inv_sem_teste} invariante(s) INV- sem 'Teste:' em ## Invariantes"
    fi

    sc_sem_instrumento=$(grep -E '^\s*- \*\*SC-[0-9]+\*\*' "$SPEC_FILE" 2>/dev/null | grep -cv "Instrumento" 2>/dev/null)
    if [ "${sc_sem_instrumento:-0}" -gt 0 ]; then
        check_warn "Spec: ${sc_sem_instrumento} critério(s) de sucesso SC- sem 'Instrumento:'"
    fi
fi

# ---------------------------------------------------------------------------
# 7. Coerência status × artefatos (S-01 — modo WARN)
# ---------------------------------------------------------------------------
# Regra: o que o status.md declara precisa existir em disco.
# Modo WARN (decisão do dono, 2026-08-05): não bloqueia; endurecer para FAIL
# quando o backlog inconsistente for saneado.
# Referência: docs/investigacoes/templates-legados-vs-arkan.md (S-01).
if [ -f "${FEATURE_DIR}/status.md" ]; then
    DEPLOY_CL="${FEATURE_DIR}/09-deploy/deploy-checklist.md"
    DEPLOY_NA=false
    # Exceção: deploy formalmente registrado como N/A em artefato da feature
    # (ex.: feature de código que já está em produção antes deste gate existir)
    if grep -rqi '09-deploy.*N/A' "${FEATURE_DIR}" --include="*.md" 2>/dev/null; then
        DEPLOY_NA=true
    fi

    case "$fase_val" in
        08-qa)
            if [ ! -f "${FEATURE_DIR}/08-qa/qa-report.md" ]; then
                check_warn "Coerência: fase-atual=08-qa sem 08-qa/qa-report.md"
            fi
            ;;
        10-ops)
            if [ ! -d "${FEATURE_DIR}/10-ops" ] || [ -z "$(ls -A "${FEATURE_DIR}/10-ops" 2>/dev/null)" ]; then
                check_warn "Coerência: fase-atual=10-ops sem artefatos em 10-ops/"
            fi
            if [ ! -f "$DEPLOY_CL" ] && [ "$DEPLOY_NA" = false ]; then
                check_warn "Coerência: fase-atual=10-ops sem 09-deploy/deploy-checklist.md (nem registro de deploy N/A)"
            fi
            ;;
    esac

    case "$status_val" in
        em-producao|em-operacao)
            if [ ! -f "$DEPLOY_CL" ]; then
                if [ "$DEPLOY_NA" = false ]; then
                    check_warn "Coerência: status=${status_val} sem 09-deploy/deploy-checklist.md (nem registro de deploy N/A)"
                fi
            else
                if ! grep -q "^## Resultado do Deploy" "$DEPLOY_CL"; then
                    check_warn "Coerência: deploy-checklist.md sem seção '## Resultado do Deploy'"
                fi
                bloq_abertos=$(grep -cE '^\s*- \[ \].*\[BLOQUEANTE\]' "$DEPLOY_CL" 2>/dev/null)
                if [ "${bloq_abertos:-0}" -gt 0 ]; then
                    check_warn "Coerência: status=${status_val} com ${bloq_abertos} item(ns) [BLOQUEANTE] não verificado(s) no deploy-checklist"
                fi
            fi
            if [ ! -f "${FEATURE_DIR}/08-qa/qa-report.md" ]; then
                check_warn "Coerência: status=${status_val} sem 08-qa/qa-report.md"
            fi
            ;;
    esac
fi

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
STATUS="PASS"
[ "$WARNINGS" -gt 0 ] && STATUS="PASS_WITH_WARNINGS"
[ "$FAILURES" -gt 0 ] && STATUS="FAIL"

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
    echo "ARKAN — QA Mecânico"
    echo "Feature: ${FEATURE_NAME}"
    echo "Status : ${STATUS}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Resultado: ${PASSED} pass | ${WARNINGS} warn | ${FAILURES} fail (${TOTAL_CHECKS} checks)"

    if [ ${#RESULTS_FAIL[@]} -gt 0 ]; then
        echo ""
        echo "❌ Falhas:"
        for f in "${RESULTS_FAIL[@]}"; do [ -n "$f" ] && echo "  - $f"; done
    fi

    if [ ${#RESULTS_WARN[@]} -gt 0 ]; then
        echo ""
        echo "⚠️  Avisos:"
        for w in "${RESULTS_WARN[@]}"; do [ -n "$w" ] && echo "  - $w"; done
    fi

    if [ ${#RESULTS_PASS[@]} -gt 0 ]; then
        echo ""
        echo "✓ Passou:"
        for p in "${RESULTS_PASS[@]}"; do [ -n "$p" ] && echo "  - $p"; done
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

[ "$FAILURES" -eq 0 ] && exit 0 || exit 1
