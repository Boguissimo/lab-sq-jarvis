"""Regras de segurança do equipamento e admissibilidade das recomendações (ADR-204; FR-210 a FR-216). Regras SEG-01/03/04/05/06/13 (JV-T224).

Três funções puras:

- ``classificar(alteracao)`` → classe de risco (regras de segurança v0.4.0, seção 1);
- ``avaliar(alteracao, equipamento)`` → resultado de cada regra SEG (``aprovada``, ``bloqueada``,
  ``não verificável`` ou ``não se aplica``);
- ``admissibilidade(classe, resultados)`` → se a alteração pode ser recomendada (definição normativa
  da spec, E1).

Estas regras **reduzem o risco** dentro das condições conhecidas; não garantem segurança absoluta
(seção 0). **Aprovação não é verificação** (JV-D032): ela não altera nenhum resultado daqui.

``alteracao``: ``{canal, parametro, de, para, tipo}`` com ``tipo`` em ``TIPOS`` e, conforme o tipo,
``ganho_db`` (EQ e ganho), ``de_hz``/``para_hz`` (passa-altas), ``de_db_oit``/``para_db_oit``
(inclinação), ``freq_hz`` e ``q`` (EQ). Dados opcionais das regras (ausentes ⇒ ``não verificável``, nunca
aprovação presumida): ``potencia_estimada_w`` (SEG-03), ``reforcos_na_banda_db`` (SEG-05),
``vale_classificacao`` (SEG-06), ``etapa_automatizada``, ``limites_informados`` e ``valores_conferencia``
(``[{valor, origem}]``, SEG-13). ``equipamento``: ``[{canal, estado, potencia_rms_w, fs_hz,
passa_altas_min_hz, inclinacao_min_db_oit}]``; só ``estado == "confirmado"`` alimenta regra (SEG-12).
"""

# @@T224 [FR-211] [FR-212] [FR-213] [FR-214] Regras SEG-01/03/04/05/06/13 e não verificáveis SEG-02/07/09
# @@T213 [FR-210] [FR-211] Contratos de classificação, avaliação e admissibilidade (ADR-204)

from __future__ import annotations

VERSAO = "0.4.0"  # versão canônica das regras de segurança

CRESCENTE = "sensível — risco crescente"
DECRESCENTE = "sensível — risco decrescente"
NAO_SENSIVEL = "não sensível"

APROVADA, BLOQUEADA, NAO_VERIFICAVEL, NAO_SE_APLICA = "aprovada", "bloqueada", "não verificável", "não se aplica"

TIPOS = ("reforco_eq", "corte_eq", "ganho", "passa_altas", "inclinacao", "polaridade", "atraso")

REGRAS = tuple(f"SEG-{i:02d}" for i in range(1, 14))

LIMITACOES = [
    "As regras reduzem o risco dentro das condições conhecidas e dos dados cadastrados; não garantem "
    "segurança absoluta.",
    "Ficam fora do controle do Jarvis: dados de fabricante errados, saturação do amplificador ou do DSP "
    "fora do medido, defeitos de instalação, volume de uso acima do declarado e alterações no PC-Tool "
    "diferentes da receita.",
    "Aprovação não é verificação: aprovar não transforma uma condição desconhecida em verificada.",
]

# Limites das regras v0.4.0. PROVISÓRIOS (sem fundamentação normativa): SEG-04 e SEG-05; só mudam por JV-D (P8).
PASSO_MAX_DB = 1.5
REFORCO_FILTRO_MAX_DB = 3.0
REFORCO_BANDA_MAX_DB = 6.0
LIMITE_PASSO = "+1,5 dB por experimento (limite provisório)"
LIMITE_REFORCO = "+3 dB por filtro e +6 dB somados na banda do canal (limites provisórios)"
CLASSES_VALE_NAO_EQUALIZAVEL = ("cancelamento", "interferencia", "variacao_espacial")
CLASSES_SEM_VALE_NAO_EQUALIZAVEL = ("equalizavel", "nao_e_vale")
ORIGENS_ACESSIVEIS = ("declarado", "medição")
_TOL = 1e-9

AVISO_EFEITOS_COLATERAIS = (
    "Reduzir um canal costuma levar a subir o volume geral para compensar, o que aumenta a potência nos "
    "demais canais; mudar um passa-altas altera a soma no cruzamento. Não compense com reforço sem nova "
    "avaliação.")


class AlteracaoInvalida(ValueError):
    """Alteração sem os campos necessários para ser classificada."""


def classificar(alteracao: dict) -> str:
    """Classe de risco da alteração (seção 1). Na dúvida sobre a direção, trata como risco crescente."""
    tipo = alteracao.get("tipo")
    if tipo not in TIPOS:
        raise AlteracaoInvalida(f"tipo de alteração desconhecido: {tipo!r}")
    if tipo in ("polaridade", "atraso"):
        return NAO_SENSIVEL
    if tipo == "reforco_eq":
        return CRESCENTE
    if tipo == "corte_eq":
        return DECRESCENTE
    if tipo == "ganho":
        g = _numero(alteracao.get("ganho_db"))
        if g is None:
            return CRESCENTE
        return CRESCENTE if g > 0 else DECRESCENTE
    if tipo == "passa_altas":
        de, para = _numero(alteracao.get("de_hz")), _numero(alteracao.get("para_hz"))
        if de is None or para is None:
            return CRESCENTE
        return CRESCENTE if para < de else DECRESCENTE
    de, para = _numero(alteracao.get("de_db_oit")), _numero(alteracao.get("para_db_oit"))  # inclinação
    if de is None or para is None:
        return CRESCENTE
    return CRESCENTE if para < de else DECRESCENTE


def resultado(regra: str, estado: str, motivo: str, *, provisorio: bool = False, limite: str | None = None,
              falta: str | None = None) -> dict:
    """ResultadoRegra (data-model): ``{regra, resultado, motivo, provisorio, limite?, falta?}``."""
    r = {"regra": regra, "resultado": estado, "motivo": motivo, "provisorio": provisorio}
    if limite is not None:
        r["limite"] = limite
    if falta is not None:
        r["falta"] = falta
    return r


def _equipamento_do_canal(equipamento: list[dict] | None, canal: str) -> dict | None:
    return next((e for e in (equipamento or []) if e.get("canal") == canal), None)


def _numero(valor) -> float | None:
    """Número finito e não booleano; qualquer outra coisa conta como dado ausente."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor != valor or abs(valor) == float("inf"):
        return None
    return float(valor)


def _dado_confirmado(equip: dict | None, campo: str) -> float | None:
    """Dado do equipamento só vale se o canal está ``confirmado`` e o campo é um número positivo (SEG-12)."""
    if equip is None or equip.get("estado") != "confirmado":
        return None
    v = _numero(equip.get(campo))
    return v if v is not None and v > 0 else None


def _falta_equip(equip: dict | None, campo: str, descricao: str) -> str:
    if equip is None:
        return f"{descricao} de equipamento cadastrado e confirmado para o canal"
    if equip.get("estado") != "confirmado":
        return f"{descricao} de equipamento confirmado (hoje “{equip.get('estado')}”)"
    return f"{descricao} cadastrado e confirmado ({campo})"


def _seg01(alt: dict, equip: dict | None) -> dict:
    """SEG-01 — passa-altas e inclinação nunca abaixo do mínimo recomendado pelo fabricante."""
    tipo = alt["tipo"]
    if tipo == "passa_altas":
        campo, valor, un = "passa_altas_min_hz", _numero(alt.get("para_hz")), "Hz"
    elif tipo == "inclinacao":
        campo, valor, un = "inclinacao_min_db_oit", _numero(alt.get("para_db_oit")), "dB/oit"
    else:
        return resultado("SEG-01", NAO_SE_APLICA, "A alteração não muda frequência de corte nem inclinação.")
    minimo = _dado_confirmado(equip, campo)
    if minimo is None:
        return resultado("SEG-01", NAO_VERIFICAVEL, "Sem o mínimo do fabricante confirmado para o canal.",
                         falta=_falta_equip(equip, campo, "mínimo do fabricante"))
    if valor is None:
        return resultado("SEG-01", NAO_VERIFICAVEL, "A alteração não informa o valor de destino.",
                         falta="valor de destino da alteração")
    lim = f"{minimo:g} {un} (fabricante)"
    if valor < minimo - _TOL:
        return resultado("SEG-01", BLOQUEADA, f"Destino {valor:g} {un} abaixo do mínimo do fabricante.", limite=lim)
    return resultado("SEG-01", APROVADA, f"Destino {valor:g} {un} dentro do mínimo do fabricante.", limite=lim)


def _seg03(alt: dict, equip: dict | None, classe: str) -> dict:
    """SEG-03 — potência estimada (nível de uso declarado, ganho total) não passa da RMS confirmada."""
    if alt["tipo"] not in ("ganho", "reforco_eq", "corte_eq") and classe != CRESCENTE:
        return resultado("SEG-03", NAO_SE_APLICA, "A alteração não muda a potência entregue ao canal.")
    rms = _dado_confirmado(equip, "potencia_rms_w")
    if rms is None:
        return resultado("SEG-03", NAO_VERIFICAVEL, "Sem a potência RMS confirmada do alto-falante.",
                         falta=_falta_equip(equip, "potencia_rms_w", "potência RMS"))
    est = _numero(alt.get("potencia_estimada_w"))
    if est is None or est < 0:
        return resultado("SEG-03", NAO_VERIFICAVEL, "Sem a potência estimada no canal após a alteração.",
                         falta="potência estimada no canal, no nível de uso declarado, com o ganho total")
    lim = f"{rms:g} W RMS (fabricante)"
    if est > rms + _TOL:
        return resultado("SEG-03", BLOQUEADA, f"Potência estimada de {est:g} W acima da RMS confirmada.", limite=lim)
    return resultado("SEG-03", APROVADA, f"Potência estimada de {est:g} W dentro da RMS confirmada.", limite=lim)


def _seg04(alt: dict) -> dict:
    """SEG-04 — aumento de ganho ou reforço de EQ: no máximo +1,5 dB por experimento (provisório)."""
    if alt["tipo"] not in ("ganho", "reforco_eq"):
        return resultado("SEG-04", NAO_SE_APLICA, "Não é aumento de ganho nem reforço de EQ.")
    g = _numero(alt.get("ganho_db"))
    if g is None:
        return resultado("SEG-04", NAO_VERIFICAVEL, "A alteração não informa o valor do ganho.",
                         provisorio=True, limite=LIMITE_PASSO, falta="valor do ganho em dB")
    if alt["tipo"] == "ganho" and g <= 0:
        return resultado("SEG-04", NAO_SE_APLICA, "Redução de ganho.", provisorio=True)
    if g > PASSO_MAX_DB + _TOL:
        return resultado("SEG-04", BLOQUEADA, f"Aumento de {g:g} dB acima do passo máximo.",
                         provisorio=True, limite=LIMITE_PASSO)
    return resultado("SEG-04", APROVADA, f"Aumento de {g:g} dB dentro do passo máximo.",
                     provisorio=True, limite=LIMITE_PASSO)


def _seg05(alt: dict) -> dict:
    """SEG-05 — reforço de EQ: +3 dB por filtro e +6 dB somados numa banda do canal (provisório)."""
    if alt["tipo"] != "reforco_eq":
        return resultado("SEG-05", NAO_SE_APLICA, "Não é reforço de EQ.")
    g = _numero(alt.get("ganho_db"))
    if g is None:
        return resultado("SEG-05", NAO_VERIFICAVEL, "A alteração não informa o valor do reforço.",
                         provisorio=True, limite=LIMITE_REFORCO, falta="valor do reforço em dB")
    if g > REFORCO_FILTRO_MAX_DB + _TOL:
        return resultado("SEG-05", BLOQUEADA, f"Reforço de {g:g} dB acima do máximo por filtro.",
                         provisorio=True, limite=LIMITE_REFORCO)
    outros = alt.get("reforcos_na_banda_db")
    if not isinstance(outros, (list, tuple)) or any(_numero(x) is None for x in outros):
        return resultado("SEG-05", NAO_VERIFICAVEL, "Reforços já presentes na banda do canal não informados.",
                         provisorio=True, limite=LIMITE_REFORCO,
                         falta="reforços de EQ sobrepostos na mesma banda do canal (lista vazia se não houver)")
    soma = g + sum(max(float(x), 0.0) for x in outros)
    if soma > REFORCO_BANDA_MAX_DB + _TOL:
        return resultado("SEG-05", BLOQUEADA, f"Soma de reforços na banda de {soma:g} dB acima do máximo.",
                         provisorio=True, limite=LIMITE_REFORCO)
    return resultado("SEG-05", APROVADA, f"Reforço de {g:g} dB e soma na banda de {soma:g} dB dentro dos máximos.",
                     provisorio=True, limite=LIMITE_REFORCO)


def _seg06(alt: dict) -> dict:
    """SEG-06 — nunca reforçar para preencher vale não equalizável (cancelamento, interferência, espacial)."""
    if alt["tipo"] != "reforco_eq":
        return resultado("SEG-06", NAO_SE_APLICA, "Não é reforço de EQ.")
    c = alt.get("vale_classificacao")
    if c in CLASSES_VALE_NAO_EQUALIZAVEL:
        return resultado("SEG-06", BLOQUEADA, f"O reforço preencheria um vale classificado como {c}.",
                         limite="vale de cancelamento, interferência ou variação espacial não é equalizável")
    if c in CLASSES_SEM_VALE_NAO_EQUALIZAVEL:
        return resultado("SEG-06", APROVADA, "O reforço não preenche vale não equalizável.")
    return resultado("SEG-06", NAO_VERIFICAVEL, "A classificação do vale ou região reforçada não foi informada.",
                     falta="classificação do vale reforçado (cancelamento, interferência, variação espacial, "
                           "equalizável ou não é vale)")


def _seg13(alt: dict) -> dict:
    """SEG-13 — etapa automatizada: limites informados e conferência só com valores de origem acessível."""
    if not alt.get("etapa_automatizada"):
        return resultado("SEG-13", NAO_SE_APLICA, "Não é etapa de calibração automatizada.")
    if not alt.get("limites_informados"):
        return resultado("SEG-13", NAO_VERIFICAVEL, "Os limites aplicáveis não foram informados para configurar na ferramenta.",
                         falta="limites aplicáveis (reforço máximo, passa-altas mínimo) informados antes da etapa")
    valores = alt.get("valores_conferencia")
    if not isinstance(valores, (list, tuple)) or not valores:
        return resultado("SEG-13", NAO_VERIFICAVEL, "Não há valores efetivamente acessíveis para a conferência.",
                         falta="valores lidos na ferramenta (declarado) ou efeito medido (medição), com a origem")
    origens = [v.get("origem") if isinstance(v, dict) else None for v in valores]
    if any(o is None or o == "" for o in origens):
        return resultado("SEG-13", NAO_VERIFICAVEL, "Há valor de conferência sem a origem identificada.",
                         falta="origem (declarado ou medição) de cada valor de conferência")
    ruins = sorted({o for o in origens if o not in ORIGENS_ACESSIVEIS})
    if ruins:
        return resultado("SEG-13", BLOQUEADA, "Origem não acessível para conferência: " + ", ".join(map(str, ruins))
                         + ". O arquivo do PC-Tool é registro e restauração, não conferência.",
                         falta="valores de origem declarado ou medição")
    return resultado("SEG-13", APROVADA, "Conferência só com valores de origem declarada ou medida.")


def avaliar(alteracao: dict, equipamento: list[dict] | None = None) -> list[dict]:
    """Resultado de cada regra SEG para a alteração, na ordem SEG-01 … SEG-13.

    ``aprovada`` só com dado confirmado e dentro do limite; dado ausente, não confirmado (SEG-12) ou
    valor não informado ⇒ ``não verificável`` (nunca aprovação presumida); violação ⇒ ``bloqueada``.
    SEG-02, SEG-07 e SEG-09 não têm fonte de valor ou método: sempre ``não verificável`` para alteração
    sensível (FR-212), o que bloqueia o risco crescente em ``admissibilidade``.
    """
    classe = classificar(alteracao)
    sensivel = classe != NAO_SENSIVEL
    equip = _equipamento_do_canal(equipamento, alteracao.get("canal", ""))
    saida = []
    for regra in REGRAS:
        if regra == "SEG-13":
            saida.append(_seg13(alteracao))
        elif regra == "SEG-08":
            saida.append(resultado(regra, APROVADA, "A receita começa com o volume reduzido e o sinal parado, "
                                                    "e termina retomando o volume aos poucos."))
        elif regra == "SEG-11":
            saida.append(resultado(regra, APROVADA, "O Jarvis não escreve no DSP; quem aplica é você, no PC-Tool."))
        elif not sensivel:
            saida.append(resultado(regra, NAO_SE_APLICA, "Alteração não sensível." if regra == "SEG-10"
                                   else "Não se aplica a esta alteração."))
        elif regra == "SEG-01":
            saida.append(_seg01(alteracao, equip))
        elif regra == "SEG-02":
            saida.append(resultado(regra, NAO_VERIFICAVEL, "Sem modelo de excursão com parâmetros T/S confirmados.",
                                   provisorio=True, limite="2 × Fs (fator provisório)",
                                   falta="cálculo de excursão com parâmetros T/S confirmados e fonte"))
        elif regra == "SEG-03":
            saida.append(_seg03(alteracao, equip, classe))
        elif regra == "SEG-04":
            saida.append(_seg04(alteracao))
        elif regra == "SEG-05":
            saida.append(_seg05(alteracao))
        elif regra == "SEG-06":
            saida.append(_seg06(alteracao))
        elif regra == "SEG-07":
            saida.append(resultado(regra, NAO_VERIFICAVEL, "Sem método para a margem digital do DSP.",
                                   provisorio=True, limite="critério de margem digital (provisório)",
                                   falta="método e critério de margem até a saturação digital, com fonte"))
        elif regra == "SEG-09":
            saida.append(resultado(regra, NAO_VERIFICAVEL, "Sem critério de exposição sonora definido.",
                                   limite="critério ainda sem valor definido",
                                   falta="critério de exposição sonora com fonte"))
        elif regra == "SEG-10":
            saida.append(resultado(regra, APROVADA, "Exige aprovação de nível B (o quê, em qual canal, quanto) "
                                                    "antes de aplicar; a aprovação não supre dado ausente."))
        else:  # SEG-12
            if equip is None:
                saida.append(resultado(regra, NAO_VERIFICAVEL, "Não há equipamento cadastrado para o canal.",
                                       falta="cadastro confirmado do alto-falante do canal"))
            elif equip.get("estado") != "confirmado":
                saida.append(resultado(regra, NAO_VERIFICAVEL,
                                       f"O equipamento do canal está como “{equip.get('estado')}”: não alimenta "
                                       "nenhuma regra como confirmado.",
                                       falta="equipamento instalado e confirmado"))
            else:
                saida.append(resultado(regra, APROVADA, "Equipamento do canal cadastrado como confirmado."))
    return saida


def admissibilidade(classe: str, resultados: list[dict]) -> dict:
    """Admissibilidade pela classe de risco e pelos resultados SEG (definição normativa, E1).

    - Risco crescente: qualquer regra aplicável ``bloqueada`` ou sem dado confirmado ⇒ bloqueada.
    - Risco decrescente: ``bloqueada`` ⇒ bloqueada; ``não verificável`` não bloqueia e sai listada,
      com o aviso de efeitos colaterais.
    - Não sensível: admitida com SEG-08 e SEG-11.

    Alteração bloqueada nunca é executável: sem receita e sem aprovação disponível.
    """
    if classe not in (CRESCENTE, DECRESCENTE, NAO_SENSIVEL):
        raise AlteracaoInvalida(f"classe desconhecida: {classe!r}")
    bloqueadas = [r for r in resultados if r["resultado"] == BLOQUEADA]
    nao_verif = [r for r in resultados if r["resultado"] == NAO_VERIFICAVEL]
    falta = [r["falta"] for r in bloqueadas + nao_verif if r.get("falta")]
    if classe == CRESCENTE and (bloqueadas or nao_verif):
        regras = ", ".join(r["regra"] for r in bloqueadas + nao_verif)
        return {"admissivel": False, "estado": "bloqueada",
                "motivo": f"Risco crescente com regra bloqueada ou sem dado confirmado ({regras}); "
                          "alteração bloqueada — não recomendada. A aprovação não a libera.",
                "falta": falta, "nao_verificadas": [r["regra"] for r in nao_verif],
                "exige_aprovacao_b": False}
    if bloqueadas:
        return {"admissivel": False, "estado": "bloqueada",
                "motivo": "Regra bloqueada (" + ", ".join(r["regra"] for r in bloqueadas)
                          + "); alteração bloqueada — não recomendada.",
                "falta": falta, "nao_verificadas": [r["regra"] for r in nao_verif],
                "exige_aprovacao_b": False}
    saida = {"admissivel": True, "estado": "recomendada", "falta": falta,
             "nao_verificadas": [r["regra"] for r in nao_verif], "exige_aprovacao_b": classe != NAO_SENSIVEL}
    if classe == DECRESCENTE:
        saida["motivo"] = ("Risco decrescente: admitida com aprovação de nível B"
                           + (", sem verificar " + ", ".join(saida["nao_verificadas"]) if nao_verif else "")
                           + ".")
        saida["aviso"] = AVISO_EFEITOS_COLATERAIS
    elif classe == CRESCENTE:
        saida["motivo"] = "Risco crescente com todas as regras aplicáveis aprovadas; exige aprovação de nível B."
    else:
        saida["motivo"] = "Não sensível: segue o procedimento seguro (SEG-08) e a aprovação normal."
    return saida
