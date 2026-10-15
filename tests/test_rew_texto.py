import numpy as np
import pytest

from jarvis import rew_texto


def _linhas(n=20, sep=" "):
    return "\n".join(sep.join([f"{100 * (i + 1)}", f"{80 + i * 0.1:.2f}", f"{-i:.1f}"]) for i in range(n))


def test_le_texto_com_comentarios():
    r = rew_texto.ler_texto("* cabeçalho\n* Freq(Hz) SPL(dB) Phase(degrees)\n" + _linhas())
    assert r.freq_hz.size == 20 and r.tem_fase
    assert r.freq_hz[0] == 100 and r.nivel_db[1] == pytest.approx(80.1)


@pytest.mark.parametrize("sep", ["\t", ",", " ; "])
def test_separadores(sep):
    texto = _linhas(sep=sep)
    if ";" in sep:
        texto = texto.replace(".", ",")  # vírgula decimal com ponto e vírgula
    r = rew_texto.ler_texto(texto)
    assert r.freq_hz.size == 20 and r.nivel_db[3] == pytest.approx(80.3)


def test_sem_fase():
    texto = "\n".join(f"{100 * (i + 1)} {80 + i}" for i in range(15))
    r = rew_texto.ler_texto(texto)
    assert not r.tem_fase


def test_arquivo_invalido_tem_mensagem_simples():
    with pytest.raises(rew_texto.FormatoInvalido, match="Não encontrei dados"):
        rew_texto.ler_texto("isto não é uma medição", "x.txt")


def test_escrever_e_ler_de_volta(tmp_path):
    f = np.geomspace(20, 20000, 50)
    r = rew_texto.RespostaFrequencia(f, np.linspace(70, 90, 50), np.linspace(-170, 170, 50))
    rew_texto.escrever(tmp_path / "a.txt", r, ["teste"])
    lido = rew_texto.ler(tmp_path / "a.txt")
    assert np.allclose(lido.freq_hz, f, rtol=1e-6)
    assert np.allclose(lido.nivel_db, r.nivel_db, atol=1e-4)
    assert np.allclose(lido.fase_graus, r.fase_graus, atol=1e-3)
