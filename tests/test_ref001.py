import filecmp
import json

from jarvis import rew_texto
from jarvis.referencia import ref001


def test_deterministico(tmp_path):
    ref001.gerar(tmp_path)
    for nome in ["medio.txt", "tweeter.txt", "soma-antes.txt", "soma-depois.txt", "manifesto.json"]:
        assert filecmp.cmp(tmp_path / nome, ref001.PASTA_PADRAO / nome, shallow=False), nome


def test_manifesto_identifica_dados_simulados():
    m = json.loads((ref001.PASTA_PADRAO / "manifesto.json").read_text(encoding="utf-8"))
    assert m["simulado"] is True
    assert all(med["simulado"] for med in m["medicoes"])
    assert {med["momento"] for med in m["medicoes"]} == {"antes", "depois"}


def test_arquivos_marcados_como_simulados():
    texto = (ref001.PASTA_PADRAO / "soma-antes.txt").read_text(encoding="utf-8")
    assert "SIMULADOS" in texto.splitlines()[0]
    r = rew_texto.ler(ref001.PASTA_PADRAO / "soma-antes.txt")
    assert r.freq_hz.size == 479 and r.tem_fase
