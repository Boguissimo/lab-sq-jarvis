import numpy as np
import pytest

from jarvis import calculos, rew_texto
from jarvis.referencia import ref001
from jarvis.rew_texto import RespostaFrequencia


def _vias():
    f = ref001.grade_frequencias()
    lp, hp = ref001.linkwitz_riley_4(f, 3000.0)
    return f, lp, hp


def _resp(f, h, atraso_s=0.0):
    h = h * np.exp(-2j * np.pi * f * atraso_s)
    return RespostaFrequencia(f, 20 * np.log10(np.abs(h) + 1e-15), np.rad2deg(np.angle(h)))


def test_lr4_vale_menos_6_db_no_cruzamento():
    lp, hp = ref001.linkwitz_riley_4(np.array([3000.0]), 3000.0)
    assert 20 * np.log10(abs(lp[0])) == pytest.approx(-6.0206, abs=1e-3)
    assert 20 * np.log10(abs(hp[0])) == pytest.approx(-6.0206, abs=1e-3)


def test_soma_lr4_correta_e_plana():
    f, lp, hp = _vias()
    s = calculos.soma_complexa(_resp(f, lp), _resp(f, hp))
    assert np.max(np.abs(s["nivel_db"])) <= 0.01


def test_soma_lr4_invertida_tem_vale_profundo():
    f, lp, hp = _vias()
    s = calculos.soma_complexa(_resp(f, lp), _resp(f, hp), inverter_b=True)
    assert min(s["nivel_db"]) <= -30


def test_diferenca_fase_polaridade_constante():
    f, lp, hp = _vias()
    a, b = _resp(f, lp), _resp(f, -hp)
    sob = calculos.sobreposicao(a, b, 6.0)
    d = calculos.diferenca_fase(a, b, sob["indices"])
    assert abs(d["media_graus"]) == pytest.approx(180.0, abs=0.01)
    assert d["dispersao_graus"] < 0.01
    assert abs(d["atraso_equivalente_ms"]) < 1e-6


def test_atraso_aparece_como_inclinacao():
    f, lp, hp = _vias()
    a, b = _resp(f, lp), _resp(f, hp, atraso_s=0.0002)  # tweeter 0,2 ms atrasado
    sob = calculos.sobreposicao(a, b, 6.0)
    d = calculos.diferenca_fase(a, b, sob["indices"])
    assert d["atraso_equivalente_ms"] == pytest.approx(0.2, abs=0.005)
    assert d["dispersao_graus"] > 15  # diferença não é constante


def test_soma_potencias_e_vale_relativo():
    f, lp, hp = _vias()
    a, b = _resp(f, lp), _resp(f, -hp)
    soma = calculos.soma_complexa(a, b)
    pot = calculos.soma_potencias(a, b)
    sob = calculos.sobreposicao(a, b, 6.0)
    v = calculos.vale_relativo(soma["nivel_db"], pot["nivel_db"], soma["freq_hz"], sob["indices"])
    assert v["min_relativo_db"] < -30
    assert v["freq_hz"] == pytest.approx(3000, rel=0.01)


def test_referencia_temporal():
    ok = {"referencia_temporal": {"tipo": "loopback", "id": "x"}, "taxa_amostragem": 48000,
          "posicao_microfone": "P1"}
    assert calculos.referencia_temporal([ok, ok])["compativel"]
    sem = {**ok, "referencia_temporal": {"tipo": "nenhuma"}}
    r = calculos.referencia_temporal([ok, sem])
    assert not r["compativel"] and r["motivos"]
    outra_pos = {**ok, "posicao_microfone": "P2"}
    assert not calculos.referencia_temporal([ok, outra_pos])["compativel"]


def test_qualidade_basica():
    f, lp, _ = _vias()
    assert calculos.qualidade_basica(_resp(f, lp))["aprovada"]
    estreita = RespostaFrequencia(f[200:260], np.zeros(60), np.zeros(60))
    assert not calculos.qualidade_basica(estreita)["aprovada"]


def test_comparacao_interpola_grades_diferentes():
    f, lp, hp = _vias()
    prev = calculos.soma_complexa(_resp(f, lp), _resp(f, hp))
    f2 = np.geomspace(20, 20000, 300)
    plano = RespostaFrequencia(f2, np.zeros(300), np.zeros(300))
    c = calculos.comparacao(prev, plano, (1000.0, 10000.0))
    assert c["rms_db"] < 0.02 and c["pontos"] > 0


def test_reprodutivel():
    f, lp, hp = _vias()
    a, b = _resp(f, lp), _resp(f, -hp)
    assert calculos.soma_complexa(a, b) == calculos.soma_complexa(a, b)


# --- JV-T202 (ADR-212, A04): amostras mínimas para fase e atraso ---

def test_sobreposicao_insuficiente():
    import warnings
    f, lp, hp = _vias()
    a, b = _resp(f, lp), _resp(f, hp, atraso_s=1e-4)
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # nenhum RankWarning nem outro aviso numérico
        um_ponto = calculos.diferenca_fase(a, b, [int(np.argmin(np.abs(f - 3000.0)))])
        assert um_ponto["calculavel"] is False
        assert "atraso_equivalente_ms" not in um_ponto
        i = int(np.argmin(np.abs(f - 3000.0)))
        estreita = calculos.diferenca_fase(a, b, list(range(i, i + 9)))  # 9 pontos, < 1/3 de oitava
        assert estreita["calculavel"] is False
        assert any("oitava" in m for m in estreita["motivos"])


def test_sobreposicao_suficiente_calcula():
    f, lp, hp = _vias()
    sob = calculos.sobreposicao(_resp(f, lp), _resp(f, hp), 6.0)
    assert sob["pontos"] >= 8 and sob["largura_oitavas"] >= 1 / 3
    d = calculos.diferenca_fase(_resp(f, lp), _resp(f, hp), sob["indices"])
    assert d["calculavel"] is True


# --- JV-T203 (ADR-212, A02): referência temporal declarada com campos obrigatórios ---

@pytest.mark.parametrize("remover", ["tipo", "id", "taxa_amostragem", "posicao_microfone"])
def test_referencia_campos_ausentes(remover):
    base = {"referencia_temporal": {"tipo": "loopback", "id": "x"}, "taxa_amostragem": 48000,
            "posicao_microfone": "P1"}
    falho = {**base, "referencia_temporal": dict(base["referencia_temporal"])}
    if remover in ("tipo", "id"):
        del falho["referencia_temporal"][remover]
    else:
        del falho[remover]
    for medicoes in ([base, falho], [falho, falho]):  # ausência igual em todas também não passa
        r = calculos.referencia_temporal(medicoes)
        assert r["compativel"] is False
        assert r["declarada"] is True
        assert r["motivos"]


def test_referencia_vazia_e_sem_manifesto():
    assert not calculos.referencia_temporal([{}, {}])["compativel"]
    base = {"referencia_temporal": {"tipo": "loopback", "id": " "}, "taxa_amostragem": 48000,
            "posicao_microfone": "P1"}
    assert not calculos.referencia_temporal([base, base])["compativel"]
    ok = {**base, "referencia_temporal": {"tipo": "loopback", "id": "x"}}
    r = calculos.referencia_temporal([ok, ok])
    assert r == {"compativel": True, "declarada": True, "motivos": []}


# --- JV-T212 (ADR-202; critério 3 do plano): irregularidade σ̂ ---

from jarvis.referencia import modelo  # noqa: E402

_F = modelo.grade_log()
_BASE_A = {"filtros": [{"tipo": "lr4_pb", "fc_hz": 3000.0}]}
_BASE_B = {"filtros": [{"tipo": "lr4_pa", "fc_hz": 3000.0}], "polaridade_fiacao": -1}


def _cenarios_sem_ruido():
    ha, hb = modelo.resposta_via(_BASE_A, _F), modelo.resposta_via(_BASE_B, _F)
    yield "REF-001-A medio", ha
    yield "REF-001-A tweeter", hb
    yield "REF-001-A soma (cancelamento)", ha + hb
    yield "REF-001-A soma corrigida", ha - hb
    for g in (0.3, 0.6, 0.9):
        yield f"reflexão g={g}", modelo.resposta_via({**_BASE_A, "reflexoes": [{"g": g, "tau_ms": 0.4}]}, _F)


def test_irregularidade_sem_ruido_quase_zero():
    for nome, h in _cenarios_sem_ruido():
        r = calculos.irregularidade(modelo.adquirir(h, _F), "nenhuma")
        assert r["aplicavel"] and r["sigma_db"] <= 0.05, (nome, r["sigma_db"])
        assert r["classificacao"] == "aprovada"


def test_ref001a_distribuido_aprovado():
    for nome in ("medio.txt", "tweeter.txt", "soma-antes.txt", "soma-depois.txt"):
        r = calculos.irregularidade(rew_texto.ler(ref001.PASTA_PADRAO / nome), "nenhuma")
        assert r["sigma_db"] <= 0.05, nome


@pytest.mark.parametrize("sigma", [0.3, 0.5, 1.0, 1.5, 2.0])
def test_irregularidade_ruido_conhecido(sigma):
    for semente, (nome, h) in enumerate(_cenarios_sem_ruido()):
        r = calculos.irregularidade(modelo.adquirir(h, _F, {"ruido_sigma_db": sigma}, semente=100 + semente),
                                    "nenhuma")
        assert abs(r["sigma_db"] - sigma) <= 0.15 * sigma + 0.05, (nome, sigma, r["sigma_db"])


def test_irregularidade_nao_confunde_vale():
    """Vale estreito ou cancelamento profundo sem ruído não reprova; com ruído, σ̂ mede o ruído."""
    vale = modelo.resposta_via({**_BASE_B, "reflexoes": [{"g": 0.9, "tau_ms": 0.125}]}, _F)
    assert calculos.irregularidade(modelo.adquirir(vale, _F), "nenhuma")["classificacao"] == "aprovada"
    r = calculos.irregularidade(modelo.adquirir(vale, _F, {"ruido_sigma_db": 0.3}, semente=5), "nenhuma")
    assert r["classificacao"] == "aprovada"


def test_classificacao_pelos_limiares():
    h = modelo.resposta_via(_BASE_A, _F)
    classes = {s: calculos.irregularidade(modelo.adquirir(h, _F, {"ruido_sigma_db": s}, semente=9), "nenhuma")
               ["classificacao"] for s in (0.2, 1.0, 2.5)}
    assert classes == {0.2: "aprovada", 1.0: "aviso", 2.5: "reprovada"}


def test_condicoes_aplicacao():
    h = modelo.resposta_via(_BASE_A, _F)
    r = modelo.adquirir(h, _F)
    assert calculos.irregularidade(r, "nenhuma")["condicoes"]["pontos_por_oitava"] == pytest.approx(48, abs=0.01)
    # grade linear
    f_lin = np.linspace(20, 20000, 1000)
    lin = modelo.adquirir(modelo.resposta_via(_BASE_A, f_lin), f_lin)
    assert not calculos.irregularidade(lin, "nenhuma")["condicoes"]["grade_log_uniforme"]
    # menos de 24 pontos por oitava
    f_12 = modelo.grade_log(pontos_por_oitava=12)
    esparsa = modelo.adquirir(modelo.resposta_via(_BASE_A, f_12), f_12)
    assert not calculos.irregularidade(esparsa, "nenhuma")["condicoes"]["densidade_suficiente"]
    for res in (lin, esparsa):
        assert calculos.irregularidade(res, "nenhuma")["classificacao"] == "nao_estimavel"


@pytest.mark.parametrize("suavizacao", [None, "", "1/6 oitava", "psicoacústica"])
def test_nao_estimavel_nao_aprova(suavizacao):
    h = modelo.resposta_via(_BASE_A, _F)
    r = calculos.irregularidade(modelo.adquirir(h, _F), suavizacao)
    assert r["classificacao"] == "nao_estimavel" and r["sigma_db"] is None and not r["aplicavel"]
    assert r["motivos"]


# --- JV-T214 (FR-204, FR-207): vale individual e faixa útil ---

def test_vale_individual_na_via_com_reflexao():
    from jarvis.referencia import casos
    tw = rew_texto.ler_texto(casos.conteudo("REF-001-N1")["tweeter.txt"].decode("utf-8"))
    v = calculos.vales_individuais(tw)
    assert v["existe"]
    for vale in v["vales"]:
        assert 200 <= vale["freq_hz"] <= 10000
        assert vale["profundidade_db"] >= 10.0 and vale["largura_oitava"] <= 1 / 3


@pytest.mark.parametrize("arquivo", ["medio.txt", "tweeter.txt", "soma-depois.txt"])
def test_sem_vale_individual_nas_vias_limpas(arquivo):
    assert not calculos.vales_individuais(rew_texto.ler(ref001.PASTA_PADRAO / arquivo))["existe"]


def test_vale_largo_nao_e_individual():
    """Um vale largo (reflexão curta, notch de mais de 1/3 de oitava) não conta como vale individual."""
    h = modelo.resposta_via({**_BASE_B, "reflexoes": [{"g": 0.8, "tau_ms": 0.125}]}, _F)
    assert not calculos.vales_individuais(modelo.adquirir(h, _F))["existe"]


def test_faixa_util():
    medio = rew_texto.ler(ref001.PASTA_PADRAO / "medio.txt")
    idx = calculos.faixa_util(medio)
    f = medio.freq_hz[idx]
    assert f.min() >= 200 and f.max() <= 10000
    teto = medio.nivel_db[(medio.freq_hz >= 200) & (medio.freq_hz <= 10000)].max()
    assert np.all(medio.nivel_db[idx] >= teto - 20)
    # o médio cai 24 dB/oitava acima de 3 kHz: a faixa útil termina antes de 10 kHz
    assert f.max() < 10000


# --- JV-T215 (FR-207; critério 7 do plano): comparabilidade e detector de mudança ---

_META = {"posicao_microfone": "P1", "ganho_entrada_db": 0.0, "referencia_nivel": "94 dB"}


def test_condicoes_comparaveis():
    assert calculos.condicoes_comparaveis(_META, dict(_META))["ok"]
    outra = calculos.condicoes_comparaveis(_META, {**_META, "posicao_microfone": "P2"})
    assert not outra["ok"] and outra["diferencas"][0]["campo"] == "posicao_microfone"
    sem = {k: v for k, v in _META.items() if k != "referencia_nivel"}
    assert calculos.condicoes_comparaveis(_META, sem)["ausentes"] == ["referencia_nivel"]
    assert calculos.condicoes_comparaveis(sem, sem, catalogo=True)["ok"]  # presunção só do catálogo
    assert not calculos.condicoes_comparaveis(sem, sem)["ok"]


def _via(ganho=0.0, filtros=(), fc=3000.0):
    p = {"filtros": [{"tipo": "lr4_pa", "fc_hz": fc}, *filtros]}
    if ganho:
        p["filtros"].append({"tipo": "ganho", "ganho_db": ganho})
    return modelo.resposta_via(p, _F)


def _detectar(h_antes, h_depois, sigma=0.0, semente=0, comparaveis=None):
    a = modelo.adquirir(h_antes, _F, {"ruido_sigma_db": sigma}, semente=semente if sigma else None)
    d = modelo.adquirir(h_depois, _F, {"ruido_sigma_db": sigma}, semente=semente + 10_000 if sigma else None)
    sa = calculos.irregularidade(a, "nenhuma")["sigma_db"]
    sd = calculos.irregularidade(d, "nenhuma")["sigma_db"]
    return calculos.detector_mudanca_via(a, d, sa, sd, calculos.faixa_util(a), comparaveis)


def test_detector_mudanca():
    base = _via()
    for h in (_via(1.5), _via(-1.5), _via(fc=3500.0),
              _via(filtros=[{"tipo": "peq", "f0_hz": 6000.0, "ganho_db": 3.0, "q": 4.0}])):
        assert _detectar(base, h)["resultado"] == "mudanca_detectada"
    r = _detectar(base, base)
    assert r["resultado"] == "nao_detectada" and r["resolucao"]["media_db"] == 1.0
    assert r["resolucao"]["bandas_db"] == 1.5 and r["parametro_identificado"] is False
    nc = calculos.condicoes_comparaveis(_META, {**_META, "posicao_microfone": "P2"})
    assert _detectar(base, _via(3.0), comparaveis=nc)["resultado"] == "inconclusiva"
    a = modelo.adquirir(base, _F)
    assert calculos.detector_mudanca_via(a, a, None, 0.1, calculos.faixa_util(a))["resultado"] == "inconclusiva"
    d = modelo.adquirir(_via(3.0), _F)
    assert calculos.detector_mudanca_via(a, d, None, None, calculos.faixa_util(a))["resultado"] == "mudanca_detectada"


def test_detector_n3_detectado_200_sementes():
    base, n3 = _via(), -_via(3.0)
    assert all(_detectar(base, n3, 1.5, s)["resultado"] == "mudanca_detectada" for s in range(200))


@pytest.mark.xfail(strict=True, reason="Divergência com o SC-208(b) em aberto: com a regra da spec (fator 3, "
                   "bandas deslizantes), 'só polaridade' dá ~8,7 % de falsos positivos a σ = 1,5 dB "
                   "(1 000 sementes). Aguarda decisão do desenvolvedor (JV-D); limiar não ajustado (P8).")
def test_detector_validacao_200_sementes():
    """Zero falsos positivos em "só polaridade" até σ = 1,5 dB; N3 (+3 dB) detectado em 100 %."""
    base = _via()
    so_polaridade = -base  # inverter a polaridade não muda a magnitude da via isolada
    n3 = -_via(3.0)
    for s in range(200):
        assert _detectar(base, so_polaridade, 1.5, s)["resultado"] != "mudanca_detectada", s
        assert _detectar(base, n3, 1.5, s)["resultado"] == "mudanca_detectada", s
