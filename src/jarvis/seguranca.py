"""Regras de segurança do equipamento e admissibilidade das recomendações (ADR-204; FR-210 a FR-216).

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
(inclinação), ``freq_hz`` e ``q`` (EQ).
"""

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
        g = alteracao.get("ganho_db")
        if g is None:
            return CRESCENTE
        return CRESCENTE if g > 0 else DECRESCENTE
    if tipo == "passa_altas":
        de, para = alteracao.get("de_hz"), alteracao.get("para_hz")
        if de is None or para is None:
            return CRESCENTE
        return CRESCENTE if para < de else DECRESCENTE
    de, para = alteracao.get("de_db_oit"), alteracao.get("para_db_oit")  # inclinação
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


def avaliar(alteracao: dict, equipamento: list[dict] | None = None) -> list[dict]:
    """Resultado de cada regra SEG para a alteração, na ordem SEG-01 … SEG-13.

    Contrato da fase 0 (JV-T213): SEG-08, SEG-10, SEG-11 e SEG-12 já seguem as regras; as demais regras
    aplicáveis a uma alteração sensível ficam ``não verificável`` até a JV-T224 implementá-las.
    """
    classe = classificar(alteracao)
    sensivel = classe != NAO_SENSIVEL
    equip = _equipamento_do_canal(equipamento, alteracao.get("canal", ""))
    saida = []
    for regra in REGRAS:
        if regra == "SEG-08":
            saida.append(resultado(regra, APROVADA, "A receita começa com o volume reduzido e o sinal parado, "
                                                    "e termina retomando o volume aos poucos."))
        elif regra == "SEG-11":
            saida.append(resultado(regra, APROVADA, "O Jarvis não escreve no DSP; quem aplica é você, no PC-Tool."))
        elif regra == "SEG-10":
            saida.append(resultado(regra, APROVADA, "Exige aprovação de nível B (o quê, em qual canal, quanto) "
                                                    "antes de aplicar; a aprovação não supre dado ausente.")
                         if sensivel else resultado(regra, NAO_SE_APLICA, "Alteração não sensível."))
        elif regra == "SEG-12":
            if not sensivel:
                saida.append(resultado(regra, NAO_SE_APLICA, "Alteração não sensível."))
            elif equip is None:
                saida.append(resultado(regra, NAO_VERIFICAVEL, "Não há equipamento cadastrado para o canal.",
                                       falta="cadastro confirmado do alto-falante do canal"))
            elif equip.get("estado") != "confirmado":
                saida.append(resultado(regra, NAO_VERIFICAVEL,
                                       f"O equipamento do canal está como “{equip.get('estado')}”: não alimenta "
                                       "nenhuma regra como confirmado.",
                                       falta="equipamento instalado e confirmado"))
            else:
                saida.append(resultado(regra, APROVADA, "Equipamento do canal cadastrado como confirmado."))
        elif not sensivel or regra == "SEG-13":
            saida.append(resultado(regra, NAO_SE_APLICA, "Não se aplica a esta alteração."))
        else:
            saida.append(resultado(regra, NAO_VERIFICAVEL, "Regra ainda não avaliada nesta versão (JV-T224).",
                                   falta="avaliação da regra"))
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
