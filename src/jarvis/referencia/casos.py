"""Catálogo dos casos simulados do JV-V02 (ADR-201; FR-201, FR-223, INV-208, INV-213, INV-214).

Cada caso é descrito por parâmetros do modelo físico (``modelo.py``) e da aquisição. Os arquivos
saem do mesmo H(f); ruído e erros entram só na aquisição, com σ e semente no manifesto.

- ``listar()`` devolve todos os casos do catálogo; ``distribuido`` indica os que vão na pasta de dados e
  aparecem no seletor da interface. Os demais são **variantes de teste** (SC-208, ADR-208), geradas sob
  demanda.
- ``conteudo(nome)`` devolve os bytes exatos de cada arquivo; ``gerar(nome, pasta)`` grava esses bytes.
  Os casos novos usam fim de linha LF em todas as plataformas (`.gitattributes` marca as pastas como
  ``-text``). O REF-001-A continua gerado por ``ref001.py``, byte a byte (INV-213).
- ``proveniencia(nome, shas)`` confere se os arquivos importados são exatamente os que o catálogo gera
  (INV-214). Só então valem as presunções de catálogo; ``simulado: true`` sozinho não concede nada.

Todos os casos são simulações: não representam o carro (JV-D025).
"""

# @@T211 [FR-201] [FR-223] [INV-213] [INV-214] Catálogo de casos com proveniência verificável

from __future__ import annotations

import copy
import functools
import hashlib
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from jarvis.referencia import modelo, ref001
from jarvis.rew_texto import formatar

VERSAO = "1.0"
PASTA_DADOS = Path(__file__).resolve().parent / "dados"
TAXA = 48000
POSICAO = "P1 — posição de escuta do motorista (simulada)"
REFERENCIA_NIVEL = "calibrador 94 dB em 1 kHz (simulado)"
FC = 3000.0


@dataclass(frozen=True)
class Caso:
    nome: str
    titulo: str
    distribuido: bool
    construir: Callable[[], dict]


# ----------------------------------------------------------------- vias de base

def _medio(**extra) -> dict:
    return {"filtros": [{"tipo": "lr4_pb", "fc_hz": FC}], "distancia_m": 1.0, "nivel_db": 85.0, **extra}


def _tweeter(**extra) -> dict:
    return {"filtros": [{"tipo": "lr4_pa", "fc_hz": FC}], "distancia_m": 1.0, "nivel_db": 85.0, **extra}


def _config_base(nome: str, polar_tweeter: str = "0°", extra: list[dict] | None = None) -> dict:
    return {"nome": nome, "parametros": [
        {"canal": "medio_esq", "parametro": "polaridade", "valor": "0°"},
        {"canal": "tweeter_esq", "parametro": "polaridade", "valor": polar_tweeter},
        {"canal": "medio_esq", "parametro": "passa-baixas", "valor": "LR 24 dB/oit em 3000 Hz"},
        {"canal": "tweeter_esq", "parametro": "passa-altas", "valor": "LR 24 dB/oit em 3000 Hz"},
        *(extra or []),
    ]}


def _aplicar_dsp(via: dict, mudancas: dict) -> dict:
    """Nova via com mudanças de DSP (polaridade, atraso, filtros extras)."""
    v = copy.deepcopy(via)
    if "polaridade_dsp_graus" in mudancas:
        v["polaridade_dsp_graus"] = mudancas["polaridade_dsp_graus"]
    if "atraso_dsp_ms" in mudancas:
        v["atraso_dsp_ms"] = mudancas["atraso_dsp_ms"]
    v["filtros"] = v.get("filtros", []) + mudancas.get("filtros_extra", [])
    return v


# ----------------------------------------------------------------- montagem de um caso

def _medicao(arquivo, momento, papel, canal, descricao, *, ref_id, sigma, semente, ref_tipo="loopback",
             posicao=POSICAO, ganho=0.0, aquisicao_id=None, repeticao=None, extra_posicao=None) -> dict:
    m = {
        "arquivo": arquivo, "momento": momento, "papel": papel, "canal": canal, "descricao": descricao,
        "referencia_temporal": {"tipo": ref_tipo, "id": ref_id} if ref_tipo != "nenhuma" else {"tipo": "nenhuma"},
        "taxa_amostragem": TAXA, "posicao_microfone": posicao, "simulado": True,
        "suavizacao": "nenhuma", "ganho_entrada_db": ganho, "referencia_nivel": REFERENCIA_NIVEL,
        "aquisicao_id": aquisicao_id or f"{arquivo.rsplit('.', 1)[0]}", "ruido_sigma_db": sigma,
        "semente": semente,
    }
    if repeticao is not None:
        m["repeticao"] = repeticao
    if extra_posicao:
        m["posicao_simulada"] = extra_posicao  # só para auditoria: efeito acústico da posição
    return m


def _caso(nome: str, descricao: str, vias: dict, depois: dict | None, sigma: float, semente: int, *,
          configuracao: dict, configuracao_depois: dict | None = None, ref_tipo: str = "loopback",
          extras_manifesto: dict | None = None, depois_vias: list[dict] | None = None,
          sigma_por_arquivo: dict | None = None, tipo_sessao: str = "investigacao") -> dict:
    """Monta arquivos e manifesto. ``depois``: vias depois da mudança de DSP (None = sem mudança).

    ``depois_vias``: aquisições individuais "depois" (``{papel, arquivo, semente, posicao?}``).
    """
    f = modelo.grade_log()
    va, vb = vias["via_a"], vias["via_b"]
    ha, hb = modelo.resposta_via(va, f), modelo.resposta_via(vb, f)
    dep = depois or vias
    ha2, hb2 = modelo.resposta_via(dep["via_a"], f), modelo.resposta_via(dep["via_b"], f)
    sig = dict(sigma_por_arquivo or {})
    ref_id = f"{nome}-loopback-simulado"

    def _s(arq):
        return sig.get(arq, sigma)

    planos = [
        ("medio.txt", ha, "antes", "via_a", "medio_esq", "Médio esquerdo sozinho", None),
        ("tweeter.txt", hb, "antes", "via_b", "tweeter_esq", "Tweeter esquerdo sozinho", None),
        ("soma-antes.txt", modelo.soma(ha, hb), "antes", "soma", "medio_esq+tweeter_esq",
         "Médio e tweeter juntos", None),
        ("soma-depois.txt", modelo.soma(ha2, hb2), "depois", "soma", "medio_esq+tweeter_esq",
         "Médio e tweeter juntos, depois da alteração", None),
    ]
    for i, d in enumerate(depois_vias or []):
        h = ha2 if d["papel"] == "via_a" else hb2
        rotulo = "Médio" if d["papel"] == "via_a" else "Tweeter"
        planos.append((d["arquivo"], h, "depois", d["papel"],
                       "medio_esq" if d["papel"] == "via_a" else "tweeter_esq",
                       f"{rotulo} esquerdo sozinho, depois (aquisição {d.get('repeticao', i + 1)})", d))

    arquivos: dict[str, bytes] = {}
    medicoes = []
    for k, (arq, h, momento, papel, canal, desc, d) in enumerate(planos):
        d = d or {}
        sem = d.get("semente", semente + k)
        pos = d.get("posicao")
        aq = {"ruido_sigma_db": _s(arq), "ganho_entrada_db": d.get("ganho_entrada_db", 0.0),
              "posicao": pos or {}}
        r = modelo.adquirir(h, f, aq, semente=sem if aq["ruido_sigma_db"] else None)
        cab = [f"Lab SQ Jarvis — caso {nome} (DADOS SIMULADOS, não é medição real)",
               "Formato: frequência (Hz), nível (dB), fase (graus), no estilo da exportação em texto do REW",
               f"Medição simulada: {arq.rsplit('.', 1)[0]}"]
        arquivos[arq] = formatar(r, cab).encode("utf-8")
        medicoes.append(_medicao(
            arq, momento, papel, canal, desc, ref_id=ref_id,
            sigma=aq["ruido_sigma_db"], semente=sem if aq["ruido_sigma_db"] else None, ref_tipo=ref_tipo,
            posicao=d.get("posicao_declarada", POSICAO), ganho=aq["ganho_entrada_db"],
            aquisicao_id=d.get("aquisicao_id"), repeticao=d.get("repeticao"), extra_posicao=pos))
    # o V01 lê a primeira medição "depois" como a soma: a soma-depois vem antes das vias "depois"
    manifesto = {
        "caso": nome, "simulado": True, "descricao": descricao, "versao_catalogo": VERSAO,
        "tipo_sessao": tipo_sessao, "semente": semente, "ruido_sigma_db": sigma,
        "modelo": {"versao": modelo.VERSAO, "antes": vias, "depois": dep},
        "configuracao_declarada": configuracao,
        "medicoes": medicoes,
    }
    if configuracao_depois:
        manifesto["depois"] = {"configuracao_declarada": configuracao_depois}
    manifesto.update(extras_manifesto or {})
    arquivos["manifesto.json"] = (json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return arquivos


# ----------------------------------------------------------------- família REF-001 (bloco 1)

def _ab_polaridade(tweeter_extra: dict | None = None, medio_extra: dict | None = None,
                   depois_extra_tweeter: list | None = None) -> tuple[dict, dict]:
    va = _medio(**(medio_extra or {}))
    vb = _tweeter(polaridade_fiacao=-1, **(tweeter_extra or {}))
    vias = {"via_a": va, "via_b": vb}
    vb2 = _aplicar_dsp(vb, {"polaridade_dsp_graus": 180, "filtros_extra": depois_extra_tweeter or []})
    return vias, {"via_a": va, "via_b": vb2}


CONFIG_DEPOIS_POLARIDADE = _config_base("Depois: tweeter com polaridade 180° (declarado)", "180°")


def _ref001b() -> dict:
    vias, depois = _ab_polaridade(
        medio_extra={"alto_falante": {"tipo": "ressonante", "fs_hz": 70.0, "q": 0.7, "rolagem_hz": 15000.0}},
        tweeter_extra={"alto_falante": {"tipo": "ressonante", "fs_hz": 600.0, "q": 0.7},
                       "distancia_m": 1.0086})
    return _caso("REF-001-B", "Caso simulado realista: alto-falantes com ressonância e queda natural, tweeter "
                 "0,86 cm mais longe, ruído moderado (σ = 0,3 dB). Fiação do tweeter invertida. Não representa o carro.",
                 vias, depois, 0.3, 1100, configuracao=_config_base("Ajuste inicial do caso REF-001-B (declarado)"),
                 configuracao_depois=CONFIG_DEPOIS_POLARIDADE)


def _n1() -> dict:
    va = _medio()
    vb = _tweeter(reflexoes=[{"g": 0.8, "tau_ms": 0.5}])  # vales estreitos (≈ 5, 7 e 9 kHz) só no tweeter
    vias = {"via_a": va, "via_b": vb}
    return _caso("REF-001-N1", "Polaridade correta; vales estreitos causados por reflexão (interferência), presentes na "
                 "medição individual do tweeter (≈ 5, 7 e 9 kHz). Não são de polaridade nem equalizáveis. Simulado.",
                 vias, None, 0.0, 1200, configuracao=_config_base("Ajuste inicial do caso REF-001-N1 (declarado)"))


def _n2() -> dict:
    vias, depois = _ab_polaridade()
    return _caso("REF-001-N2", "Fiação do tweeter invertida, com ruído alto (σ = 2,0 dB) em todas as medições: "
                 "a qualidade não permite concluir. Simulado.", vias, depois, 2.0, 1300,
                 configuracao=_config_base("Ajuste inicial do caso REF-001-N2 (declarado)"),
                 configuracao_depois=CONFIG_DEPOIS_POLARIDADE)


def _n3(variante: str = "padrao") -> dict:
    """REF-001-N3 e variantes de teste do detector (ADR-208)."""
    ganho = [{"tipo": "ganho", "ganho_db": 3.0}]
    declarada = CONFIG_DEPOIS_POLARIDADE
    medida = True
    if variante == "so-declarada":
        ganho, medida = [], False
        declarada = _config_base("Depois: polaridade 180° e ganho do tweeter +3 dB (declarado)", "180°",
                                 [{"canal": "tweeter_esq", "parametro": "ganho", "valor": "+3 dB"}])
    vias, depois = _ab_polaridade(depois_extra_tweeter=ganho)
    rep = [{"papel": "via_b", "arquivo": "tweeter-depois-1.txt", "semente": 1391, "repeticao": 1,
            "aquisicao_id": "N3-tweeter-depois-aq1"},
           {"papel": "via_b", "arquivo": "tweeter-depois-2.txt", "semente": 1392, "repeticao": 2,
            "aquisicao_id": "N3-tweeter-depois-aq2"}]
    if variante == "sem-repeticao":
        rep = rep[:1]
    elif variante == "posicao-diferente":
        for r in rep:
            r["posicao_declarada"] = "P2 — outra posição (simulada)"
            r["posicao"] = {"delta_distancia_m": 0.05}
    elif variante == "reposicionamento":
        # sem ganho no DSP: o microfone recolocado desloca um nulo estreito (efeito acústico, não DSP)
        vias, depois = _ab_polaridade()
        rep = rep[:1]
        rep[0]["posicao"] = {"reflexoes": [{"g": 0.7, "tau_ms": 0.2}]}
    elif variante == "so-medida":
        pass
    elif variante == "ruido-alto":
        pass
    if not medida:
        rep = []
    sigma_arq = {}
    if variante == "ruido-alto":
        sigma_arq = {r["arquivo"]: 1.2 for r in rep} | {"tweeter.txt": 1.2}
    nome = "REF-001-N3" if variante == "padrao" else f"REF-001-N3-{variante}"
    desc = {"padrao": "No “depois”, além da polaridade, o ganho do tweeter subiu 3 dB sem ser declarado; duas "
                      "aquisições independentes do tweeter “depois” (repetição). Simulado.",
            }.get(variante, f"Variante de teste do REF-001-N3: {variante}. Simulado.")
    return _caso(nome, desc, vias, depois, 0.2, 1390, configuracao=_config_base(f"Ajuste inicial do caso {nome} (declarado)"),
                 configuracao_depois=declarada, depois_vias=rep, sigma_por_arquivo=sigma_arq)


def _n4() -> dict:
    vias, depois = _ab_polaridade()
    return _caso("REF-001-N4", "Fiação do tweeter invertida, mas medições separadas sem referência temporal comum: "
                 "fase e soma prevista não podem ser calculadas. Simulado.", vias, depois, 0.0, 1400,
                 configuracao=_config_base("Ajuste inicial do caso REF-001-N4 (declarado)"),
                 configuracao_depois=CONFIG_DEPOIS_POLARIDADE, ref_tipo="nenhuma")


def _n5() -> dict:
    vias = {"via_a": _medio(), "via_b": _tweeter()}
    return _caso("REF-001-N5", "Sistema sem problema no cruzamento: polaridade correta, soma plana. Simulado.",
                 vias, None, 0.0, 1500, configuracao=_config_base("Ajuste inicial do caso REF-001-N5 (declarado)"))


# ----------------------------------------------------------------- família REF-002-A (bloco 3: etapa tipo ATM)

ATRASO_ANTES_MS = 0.14   # tweeter atrasado: cancelamento de ~10,8 dB no cruzamento
ATRASOS_DEPOIS_MS = {"atingido": 0.0, "parcial": 0.11, "nao-atingido": 0.13, "inconclusivo": 0.0}


def _ref002(variante: str) -> dict:
    va = _medio()
    vb = _tweeter(atraso_dsp_ms=ATRASO_ANTES_MS)
    vias = {"via_a": va, "via_b": vb}
    novo = ATRASOS_DEPOIS_MS[variante]
    depois = {"via_a": va, "via_b": _aplicar_dsp(vb, {"atraso_dsp_ms": novo})}
    conjunto = [{"canal": "tweeter_esq", "parametro": "atraso", "de": f"{ATRASO_ANTES_MS:.2f} ms",
                 "para": f"{novo:.2f} ms"},
                {"canal": "medio_esq", "parametro": "atraso", "de": "0,00 ms", "para": "0,00 ms"}]
    extra = [{"canal": "tweeter_esq", "parametro": "atraso", "valor": f"{ATRASO_ANTES_MS:.2f} ms"},
             {"canal": "medio_esq", "parametro": "atraso", "valor": "0,00 ms"}]
    extra_depois = [{"canal": "tweeter_esq", "parametro": "atraso", "valor": f"{novo:.2f} ms"},
                    {"canal": "medio_esq", "parametro": "atraso", "valor": "0,00 ms"}]
    nome = f"REF-002-A-{variante}"
    sig = {"soma-depois.txt": 2.0} if variante == "inconclusivo" else {}
    return _caso(nome, f"Etapa de calibração simulada tipo ATM (alinhamento de atrasos), variante “{variante}”. "
                 "O objetivo é “sem cancelamento acima de 3 dB em relação à soma de potências”. Simulado.",
                 vias, depois, 0.0, 2000 + list(ATRASOS_DEPOIS_MS).index(variante) * 10,
                 configuracao=_config_base(f"Ajuste inicial do caso {nome} (declarado)", extra=extra),
                 configuracao_depois=_config_base(f"Depois da etapa {nome} (declarado)", extra=extra_depois),
                 sigma_por_arquivo=sig, tipo_sessao="etapa-simulada",
                 extras_manifesto={"etapa": {"ferramenta": "ATM (simulada)", "conjunto": conjunto,
                                             "limites_informados": [
                                                 {"canal": "tweeter_esq", "parametro": "atraso",
                                                  "limite": "0 a 1 ms", "origem": "declarado"}]}})


# ----------------------------------------------------------------- família REF-003-S (bloco 2: segurança, E2/E3)

def _equipamento(estado_tweeter: str, estado_medio: str = "confirmado") -> list[dict]:
    return [
        {"canal": "medio_esq", "alto_falante": "médio sintético M-165", "estado": estado_medio,
         "potencia_rms_w": 60, "fs_hz": 70.0, "passa_altas_min_hz": 80.0, "inclinacao_min_db_oit": 12,
         "simulado": True},
        {"canal": "tweeter_esq", "alto_falante": "tweeter sintético T-25", "estado": estado_tweeter,
         "potencia_rms_w": 30, "fs_hz": 900.0, "passa_altas_min_hz": 2000.0, "inclinacao_min_db_oit": 24,
         "simulado": True},
    ]


def _ref003(variante: str) -> dict:
    vias = {"via_a": _medio(), "via_b": _tweeter()}
    if variante in ("S1", "S2"):
        alteracao = {"canal": "tweeter_esq", "parametro": "EQ 8 kHz", "de": "0 dB", "para": "+1 dB",
                     "tipo": "reforco_eq", "freq_hz": 8000.0, "q": 1.0, "ganho_db": 1.0}
        equipamento = _equipamento("confirmado" if variante == "S1" else "planejado")
        desc = ("Reforço de EQ de +1 dB no tweeter, equipamento sintético "
                + ("confirmado: bloqueado por SEG-07 (margem digital sem método)." if variante == "S1"
                   else "planejado: bloqueado por SEG-12 e SEG-07."))
    else:
        alteracao = {"canal": "medio_esq", "parametro": "EQ 1 kHz", "de": "0 dB", "para": "−2 dB",
                     "tipo": "corte_eq", "freq_hz": 1000.0, "q": 2.0, "ganho_db": -2.0}
        equipamento = _equipamento("confirmado", estado_medio="informado")
        desc = ("Corte de EQ de −2 dB no médio, com dado do médio só informado: sensível de risco decrescente, "
                "admitido com aviso e aprovação de nível B.")
    nome = f"REF-003-{variante}"
    return _caso(nome, desc + " Caso de segurança sintético (simulado); não altera os casos de referência.",
                 vias, None, 0.0, 3000 + int(variante[1]) * 10,
                 configuracao=_config_base(f"Ajuste inicial do caso {nome} (declarado)"),
                 extras_manifesto={"equipamento": equipamento, "alteracao_candidata": alteracao})


# ----------------------------------------------------------------- catálogo

def _ref001a() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        pasta = ref001.gerar(Path(tmp) / "REF-001-A")
        return {p.name: p.read_bytes() for p in sorted(pasta.iterdir())}


_CATALOGO: list[Caso] = [
    Caso("REF-001-A", "REF-001-A — polaridade invertida (ideal)", True, _ref001a),
    Caso("REF-001-B", "REF-001-B — polaridade invertida (realista)", True, _ref001b),
    Caso("REF-001-N1", "REF-001-N1 — vale numa via (reflexão)", True, _n1),
    Caso("REF-001-N2", "REF-001-N2 — ruído alto", True, _n2),
    Caso("REF-001-N3", "REF-001-N3 — “depois” com outra mudança", True, _n3),
    Caso("REF-001-N4", "REF-001-N4 — sem referência temporal comum", True, _n4),
    Caso("REF-001-N5", "REF-001-N5 — sem problema no cruzamento", True, _n5),
    *[Caso(f"REF-002-A-{v}", f"REF-002-A — etapa de calibração ({v})", True, (lambda v=v: _ref002(v)))
      for v in ATRASOS_DEPOIS_MS],
    *[Caso(f"REF-003-{v}", f"REF-003-{v} — caso de segurança", True, (lambda v=v: _ref003(v)))
      for v in ("S1", "S2", "S3")],
    *[Caso(f"REF-001-N3-{v}", f"Variante de teste do N3: {v}", False, (lambda v=v: _n3(v)))
      for v in ("so-declarada", "so-medida", "sem-repeticao", "posicao-diferente", "reposicionamento",
                "ruido-alto")],
]


def listar(somente_distribuidos: bool = False) -> list[Caso]:
    return [c for c in _CATALOGO if c.distribuido or not somente_distribuidos]


def caso(nome: str) -> Caso:
    for c in _CATALOGO:
        if c.nome == nome:
            return c
    raise KeyError(f"caso fora do catálogo: {nome}")


def conteudo(nome: str) -> dict[str, bytes]:
    """Bytes exatos de cada arquivo do caso (medições e manifesto)."""
    return caso(nome).construir()


@functools.lru_cache(maxsize=64)
def _sha_esperados(nome: str) -> tuple:
    return tuple(sorted((arq, hashlib.sha256(b).hexdigest()) for arq, b in conteudo(nome).items()))


def sha_esperados(nome: str) -> dict[str, str]:
    return dict(_sha_esperados(nome))


def gerar(nome: str, pasta: str | Path | None = None) -> Path:
    pasta = Path(pasta) if pasta else PASTA_DADOS / nome
    pasta.mkdir(parents=True, exist_ok=True)
    for arq, b in conteudo(nome).items():
        (pasta / arq).write_bytes(b)
    return pasta


def proveniencia(nome: str | None, shas: dict[str, str]) -> dict:
    """Confere a proveniência de catálogo (INV-214).

    ``shas``: SHA-256 de cada arquivo importado, pelo nome do arquivo (inclui ``manifesto.json``).
    ``catalogo`` só é verdadeiro quando o caso consta do catálogo e **todos** os hashes conferem.
    """
    if not nome or nome not in {c.nome for c in _CATALOGO}:
        return {"catalogo": False, "caso": nome, "motivo": "caso fora do catálogo interno"}
    esperados = sha_esperados(nome)
    if "manifesto.json" not in shas:
        return {"catalogo": False, "caso": nome, "motivo": "manifesto não conferido"}
    divergentes = sorted(a for a, s in shas.items() if esperados.get(a) != s)
    if divergentes:
        return {"catalogo": False, "caso": nome, "motivo": "arquivos diferentes dos do catálogo: "
                + ", ".join(divergentes)}
    return {"catalogo": True, "caso": nome, "sha256_esperado": {a: esperados[a] for a in shas}}


def gerar_distribuidos() -> list[Path]:
    """Regrava as pastas dos casos distribuídos (exceto REF-001-A, gerado por ``ref001.py``)."""
    return [gerar(c.nome) for c in listar(somente_distribuidos=True) if c.nome != "REF-001-A"]


if __name__ == "__main__":
    for p in gerar_distribuidos():
        print(p)
    sys.exit(0)
