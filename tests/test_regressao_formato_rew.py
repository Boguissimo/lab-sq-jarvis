"""Regressão do formato real do REW (en-US) e das mensagens/bordas do portão básico.

Origem: investigação de desempenho com medições reais (joeglondon/speakers-2026-filters, REW 5.31.3): frequências a
partir de 1 kHz saem com separador de milhar ("1,000.1222"). Linhas de exemplo abaixo são SINTÉTICAS no mesmo formato
(nenhum dado de terceiros é copiado).
"""
import numpy as np
import pytest

from jarvis import calculos, rew_texto
from jarvis.persistencia import Banco
from jarvis.referencia import casos
from jarvis.sessao import ErroDoPercurso, Servico

CABECALHO_REW = "* Measurement data measured by REW V5.31.3\n* Freq(Hz) SPL(dB) Phase(degrees)\n"


def _texto_rew(freqs, nivel=80.0):
    return CABECALHO_REW + "\n".join(f"{f:,.4f} {nivel + 0.001 * i:.3f} {-170 + 0.01 * i:.2f}" for i, f in enumerate(freqs))


def test_milhar_en_us_nao_corrompe_as_frequencias():
    freqs = np.array([998.2, 999.0, 1000.1222, 1000.4884, 1500.5, 12345.6789, 20000.2458] + list(np.linspace(1001, 1100, 8)))
    freqs.sort()
    r = rew_texto.ler_texto(_texto_rew(freqs))
    assert np.allclose(r.freq_hz, np.round(freqs, 4))
    assert np.all(np.diff(r.freq_hz) > 0)
    assert r.nivel_db[0] == pytest.approx(80.0) and r.fase_graus[0] == pytest.approx(-170.0)


def test_exportacao_linear_completa_passa_no_portao_basico():
    f = np.arange(0.3662, 20000.3, 0.36621097)  # grade linear do REW (≈ 54 600 pontos)
    r = rew_texto.ler_texto(_texto_rew(f))
    assert r.freq_hz.size == f.size
    q = calculos.qualidade_basica(r)
    assert q["aprovada"], q


def test_separadores_antigos_continuam_valendo():
    r = rew_texto.ler_texto("\n".join(f"{100 * (i + 1)},{80 + i},{-i}" for i in range(15)))
    assert r.freq_hz[-1] == 1500 and r.freq_hz.size == 15
    r = rew_texto.ler_texto("\n".join(f"{100 * (i + 1)}\t{80 + i}" for i in range(15)))
    assert not r.tem_fase and r.freq_hz.size == 15


def _servico_com_arquivo_alterado(tmp_path, alterar):
    pasta = casos.gerar("REF-001-A", tmp_path / "caso")
    linhas = (pasta / "medio.txt").read_text(encoding="utf-8").splitlines()
    cab = [l for l in linhas if l.startswith("*")]
    dados = [l for l in linhas if not l.startswith("*") and l.strip()]
    (pasta / "medio.txt").write_text("\n".join(cab + alterar(dados)) + "\n", encoding="utf-8")
    s = Servico(Banco(tmp_path / "dados"))
    s.nova_sessao("investigacao")
    s.importar_caso(pasta)
    return s


def test_mensagem_de_frequencias_fora_de_ordem_nao_manda_refazer_a_medicao(tmp_path):
    s = _servico_com_arquivo_alterado(tmp_path, lambda d: d[::-1])
    with pytest.raises(ErroDoPercurso) as e:
        s.analisar()
    msg = str(e.value)
    assert "frequências em ordem crescente" in msg           # continua listando o que falhou
    assert "fora de ordem" in msg and "ler" in msg           # explica a causa provável
    assert "Refaça a medição cobrindo" not in msg            # não culpa a medição
    s.b.fechar()


def test_mensagem_de_faixa_curta_continua_pedindo_nova_medicao(tmp_path):
    s = _servico_com_arquivo_alterado(tmp_path, lambda d: d[: len(d) // 3])
    with pytest.raises(ErroDoPercurso, match="reprovou.*cobre 200 Hz a 10000 Hz.*Refaça a medição cobrindo"):
        s.analisar()
    s.b.fechar()


def test_densidade_exatamente_no_minimo_conta_como_suficiente():
    minimo = 24
    f = 20.0 * 2.0 ** (np.arange(int(np.log2(1000) * minimo) + 1) / minimo)
    ok = calculos.irregularidade(rew_texto.RespostaFrequencia(f, np.full(f.size, 80.0), np.zeros(f.size)), "nenhuma")
    assert ok["condicoes"]["densidade_suficiente"] is True
    f2 = 20.0 * 2.0 ** (np.arange(int(np.log2(1000) * 23) + 1) / 23.0)
    no = calculos.irregularidade(rew_texto.RespostaFrequencia(f2, np.full(f2.size, 80.0), np.zeros(f2.size)), "nenhuma")
    assert no["condicoes"]["densidade_suficiente"] is False
