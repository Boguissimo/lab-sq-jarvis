import json
import shutil

import pytest

from jarvis.persistencia import Banco
from jarvis.sessao import ErroDoPercurso, Servico


def _ate_analise(servico, pasta_caso):
    servico.nova_sessao("investigacao")
    servico.registrar_percepcao("antes", "não aplicável")
    servico.importar_caso(pasta_caso)
    return servico.analisar()


def test_percurso_completo(servico, pasta_caso, banco):
    analise = _ate_analise(servico, pasta_caso)
    assert analise["referencia"]["compativel"]
    assert analise["sugestao"] == "teste_polaridade"
    rec = servico.propor_teste()
    assert rec["dados"]["seguranca"]["classe"] == "não sensível"
    assert rec["dados"]["receita"][0].startswith("Reduza o volume")
    assert rec["dados"]["reversao"]["garantida"]
    servico.registrar_aplicacao()
    comp = servico.importar_depois()
    assert comp["dados"]["resultado"]["rms_db"] < 0.01
    servico.registrar_percepcao("depois", "não aplicável")
    concl = servico.concluir()
    assert concl["dados"]["veredito"] == "confirmada"
    assert "JV-D025" in concl["dados"]["limite"]
    servico.decidir("manter")
    estado = servico.estado()
    assert estado["sessao"]["estado"] == "encerrada"
    assert estado["configuracoes"][-1]["parametros"][1]["valor"] == "180°"
    assert banco.integridade() == []


def test_depois_sem_previsao_recusado(servico, pasta_caso):
    _ate_analise(servico, pasta_caso)
    with pytest.raises(ErroDoPercurso, match="previsão"):
        servico.importar_depois()


def test_aplicacao_exige_percepcao_antes(servico, pasta_caso):
    servico.nova_sessao("investigacao")
    servico.importar_caso(pasta_caso)
    servico.analisar()
    servico.propor_teste()
    with pytest.raises(ErroDoPercurso, match="percepção"):
        servico.registrar_aplicacao()


def test_sem_referencia_temporal(servico, pasta_caso, tmp_path):
    copia = tmp_path / "caso"
    shutil.copytree(pasta_caso, copia)
    m = json.loads((copia / "manifesto.json").read_text(encoding="utf-8"))
    m["medicoes"][1]["referencia_temporal"] = {"tipo": "nenhuma"}
    (copia / "manifesto.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    analise = _ate_analise(servico, copia)
    assert not analise["referencia"]["compativel"]
    assert analise["fase"] is None
    assert analise["sugestao"] == "solicitar_dados"
    assert "não foram calculadas" in analise["aviso_referencia"]
    with pytest.raises(ErroDoPercurso):
        servico.propor_teste()


def test_nada_a_alterar_sem_experimento(servico, pasta_caso, banco):
    _ate_analise(servico, pasta_caso)
    with pytest.raises(ErroDoPercurso, match="fundamentação"):
        servico.decidir_sem_intervencao("nada_a_alterar", "  ")
    d = servico.decidir_sem_intervencao("solicitar_dados", "Quero medir em mais posições antes.")
    assert d["sem_intervencao"]
    assert not banco.registros(servico.sessao_id, "experimento")
    assert banco.integridade() == []
    assert servico.estado()["sessao"]["estado"] == "encerrada"


def test_reverter_mostra_receita_inversa(servico, pasta_caso):
    _ate_analise(servico, pasta_caso)
    servico.propor_teste()
    servico.registrar_aplicacao()
    servico.importar_depois()
    servico.registrar_percepcao("depois", "simulada", "Exercício: imaginei a voz mais cheia.")
    servico.concluir()
    d = servico.decidir("reverter")
    assert d["reversao"]["garantida"]
    assert any("volte a polaridade" in passo for passo in d["reversao"]["receita_inversa"])
    assert servico.estado()["configuracoes"][-1]["parametros"][1]["valor"] == "0°"


def test_reversao_nao_garantida_sem_valor_anterior(servico, pasta_caso, tmp_path):
    copia = tmp_path / "caso"
    shutil.copytree(pasta_caso, copia)
    m = json.loads((copia / "manifesto.json").read_text(encoding="utf-8"))
    m["configuracao_declarada"]["parametros"] = [p for p in m["configuracao_declarada"]["parametros"]
                                                 if p["canal"] != "tweeter_esq" or p["parametro"] != "polaridade"]
    (copia / "manifesto.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    _ate_analise(servico, copia)
    rec = servico.propor_teste()
    assert not rec["dados"]["reversao"]["garantida"]
    assert "não garantida" in rec["dados"]["reversao"]["base"]


def test_recuperar_sessao_apos_fechar(tmp_path, pasta_caso):
    pasta = tmp_path / "dados"
    b1 = Banco(pasta)
    s1 = Servico(b1)
    _ate_analise(s1, pasta_caso)
    s1.propor_teste()
    sid = s1.sessao_id
    b1.fechar()

    b2 = Banco(pasta)  # programa reaberto
    s2 = Servico(b2)
    assert [s["id"] for s in s2.listar_sessoes()] == [sid]
    estado = s2.abrir_sessao(sid)
    assert estado["recomendacao"] is not None
    assert estado["sessao"]["passo_atual"] == 4
    assert "previsao" in estado["curvas"]
    s2.registrar_aplicacao()  # continua de onde parou
    b2.fechar()


def test_sessao_encerrada_nao_aceita_alteracao(servico, pasta_caso):
    _ate_analise(servico, pasta_caso)
    servico.decidir_sem_intervencao("nada_a_alterar", "Teste de encerramento.")
    with pytest.raises(ErroDoPercurso, match="encerrada"):
        servico.propor_teste()


def test_modo_calibracao_ainda_nao_disponivel(servico):
    with pytest.raises(ErroDoPercurso, match="JV-V04"):
        servico.nova_sessao("calibracao")
