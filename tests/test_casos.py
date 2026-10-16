"""Catálogo de casos do V02 (JV-T211; FR-201, FR-223, INV-208, INV-213, INV-214)."""

import hashlib
import json

import pytest

from jarvis import rew_texto
from jarvis.referencia import casos, ref001

DISTRIBUIDOS = [c.nome for c in casos.listar(somente_distribuidos=True)]
NOVOS = [n for n in DISTRIBUIDOS if n != "REF-001-A"]


def _manifesto(nome):
    return json.loads(casos.conteudo(nome)["manifesto.json"].decode("utf-8"))


@pytest.mark.parametrize("nome", NOVOS)
def test_deterministico(nome):
    """Regerar dá os mesmos bytes que estão na pasta de dados distribuída."""
    pasta = casos.PASTA_DADOS / nome
    gerados = casos.conteudo(nome)
    assert sorted(p.name for p in pasta.iterdir()) == sorted(gerados)
    for arq, b in gerados.items():
        assert (pasta / arq).read_bytes() == b, f"{nome}/{arq}"
    assert casos.conteudo(nome) == gerados


def test_ref001a_intacto(tmp_path):
    ref001.gerar(tmp_path)
    no_catalogo = casos.conteudo("REF-001-A")
    for arq, b in no_catalogo.items():
        assert (ref001.PASTA_PADRAO / arq).read_bytes() == b == (tmp_path / arq).read_bytes()


@pytest.mark.parametrize("nome", [c.nome for c in casos.listar()])
def test_conteudo_esperado(nome):
    m = _manifesto(nome)
    arquivos = casos.conteudo(nome)
    assert m["caso"] == nome and m["simulado"] is True
    assert {"medio.txt", "tweeter.txt", "soma-antes.txt", "soma-depois.txt"} <= set(arquivos)
    for med in m["medicoes"]:
        assert med["simulado"] is True and med["arquivo"] in arquivos
        r = rew_texto.ler_texto(arquivos[med["arquivo"]].decode("utf-8"))
        assert r.tem_fase
    if nome == "REF-001-A":
        return
    depois = [med for med in m["medicoes"] if med["momento"] == "depois"]
    assert depois[0]["papel"] == "soma"  # o V01 lê a primeira medição "depois" como a soma
    for med in m["medicoes"]:
        for campo in ("taxa_amostragem", "posicao_microfone", "suavizacao", "ganho_entrada_db",
                      "referencia_nivel", "aquisicao_id"):
            assert campo in med, (nome, campo)
    if nome.startswith("REF-002-A"):
        assert m["tipo_sessao"] == "etapa-simulada" and m["etapa"]["conjunto"]
    if nome.startswith("REF-003-S"):
        assert m["equipamento"] and all(e["simulado"] for e in m["equipamento"])
        assert m["alteracao_candidata"]["tipo"] in ("reforco_eq", "corte_eq")


def test_n3_duas_aquisicoes_independentes():
    m = _manifesto("REF-001-N3")
    arquivos = casos.conteudo("REF-001-N3")
    tw = [med for med in m["medicoes"] if med["papel"] == "via_b" and med["momento"] == "depois"]
    assert [t["repeticao"] for t in tw] == [1, 2]
    assert len({t["aquisicao_id"] for t in tw}) == 2
    assert len({hashlib.sha256(arquivos[t["arquivo"]]).hexdigest() for t in tw}) == 2
    assert len({t["posicao_microfone"] for t in tw}) == 1
    # o ganho de +3 dB não é declarado na configuração "depois"
    assert not any(p["parametro"] == "ganho" for p in m["depois"]["configuracao_declarada"]["parametros"])


def test_casos_de_seguranca():
    s1, s2, s3 = (_manifesto(f"REF-003-S{i}") for i in (1, 2, 3))
    est = lambda m, canal: next(e["estado"] for e in m["equipamento"] if e["canal"] == canal)
    assert s1["alteracao_candidata"] == s2["alteracao_candidata"]
    assert s1["alteracao_candidata"]["tipo"] == "reforco_eq"
    assert est(s1, "tweeter_esq") == "confirmado" and est(s2, "tweeter_esq") == "planejado"
    assert s3["alteracao_candidata"]["tipo"] == "corte_eq" and est(s3, "medio_esq") == "informado"


def test_ruido_registrado():
    for c in casos.listar():
        if c.nome == "REF-001-A":
            continue
        for med in _manifesto(c.nome)["medicoes"]:
            if med["ruido_sigma_db"]:
                assert isinstance(med["semente"], int), (c.nome, med["arquivo"])
            else:
                assert med["semente"] is None
    assert all(med["ruido_sigma_db"] == 2.0 for med in _manifesto("REF-001-N2")["medicoes"])
    assert all(med["ruido_sigma_db"] == 0.3 for med in _manifesto("REF-001-B")["medicoes"])


def test_proveniencia_catalogo(tmp_path):
    shas = casos.sha_esperados("REF-001-N5")
    assert casos.proveniencia("REF-001-N5", shas)["catalogo"] is True
    alterado = bytearray(casos.conteudo("REF-001-N5")["tweeter.txt"])
    alterado[-2] = ord("9") if alterado[-2] != ord("9") else ord("8")  # 1 byte
    shas_alt = {**shas, "tweeter.txt": hashlib.sha256(bytes(alterado)).hexdigest()}
    r = casos.proveniencia("REF-001-N5", shas_alt)
    assert r["catalogo"] is False and "tweeter.txt" in r["motivo"]
    sem_manifesto = {k: v for k, v in shas.items() if k != "manifesto.json"}
    assert casos.proveniencia("REF-001-N5", sem_manifesto)["catalogo"] is False
    assert casos.proveniencia("CASO-EXTERNO", shas)["catalogo"] is False
    assert casos.proveniencia(None, shas)["catalogo"] is False
    # outro caso do catálogo com os arquivos deste não confere
    assert casos.proveniencia("REF-001-N1", shas)["catalogo"] is False


def test_variantes_nao_distribuidas():
    variantes = [c for c in casos.listar() if not c.distribuido]
    assert variantes and all(c.nome.startswith("REF-001-N3-") for c in variantes)
    assert not any((casos.PASTA_DADOS / c.nome).exists() for c in variantes)
