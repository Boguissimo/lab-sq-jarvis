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


# --- JV-T202 (ADR-212, A04): portão básico obrigatório ---

def test_qualidade_basica_reprovada_bloqueia(servico, pasta_caso, tmp_path, banco):
    copia = tmp_path / "caso"
    shutil.copytree(pasta_caso, copia)
    arq = copia / "tweeter.txt"
    linhas = arq.read_text(encoding="utf-8").splitlines()
    mantidas = [l for l in linhas if l.startswith("*") or float(l.split()[0]) <= 5000.0]
    arq.write_text("\n".join(mantidas) + "\n", encoding="utf-8")
    servico.nova_sessao("investigacao")
    servico.importar_caso(copia)
    with pytest.raises(ErroDoPercurso, match="verificação básica de qualidade reprovou.*cobre 200 Hz a 10000 Hz"):
        servico.analisar()
    assert servico.estado()["analise"] is None


# --- JV-T209 (ADR-210, INV-211): interpretação congelada ---

def test_reabrir_nao_recalcula(servico, pasta_caso, banco, monkeypatch):
    from jarvis import regras, regras_v1_0
    _ate_analise(servico, pasta_caso)
    antes = servico.estado()["analise"]
    assert antes["interpretacao"] == f"registrada (regras {regras.VERSAO})"

    def proibido(*a, **k):
        raise AssertionError("estado() não pode reexecutar as regras")
    monkeypatch.setattr(regras, "avaliar", proibido)
    monkeypatch.setattr(regras_v1_0, "avaliar", proibido)
    monkeypatch.setattr(regras, "VERSAO", "9.9")
    monkeypatch.setitem(regras.LIMIARES, "cancelamento_min_db", 99.0)
    reaberto = Servico(banco)
    reaberto.sessao_id = servico.sessao_id
    assert reaberto.estado()["analise"] == antes


def test_calculos_gravam_entradas_sha256(servico, pasta_caso, banco):
    _ate_analise(servico, pasta_caso)
    calcs = banco.registros(servico.sessao_id, "calculo")
    medicoes = {m["id"]: m for m in banco.registros(servico.sessao_id, "medicao")}
    for c in calcs:
        assert set(c["dados"]["entradas_sha256"]) == set(c["dados"]["entradas"]), c["id"]
        assert "limiares" in c["dados"]
        for eid, sha in c["dados"]["entradas_sha256"].items():
            if eid in medicoes:
                assert sha == medicoes[eid]["dados"]["sha256"]
                assert banco.verificar_original(sha)
    av = next(c for c in calcs if c["dados"]["nome"] == "avaliacao_regras")
    assert av["dados"]["resultado"]["sugestao"] == "teste_polaridade"
    assert av["dados"]["limiares"]["limiares"]["cancelamento_min_db"] == 6.0
    assert banco.integridade() == []


# --- JV-T216 (FR-203, FR-204, INV-201, INV-212): portão de qualidade, I-3 e reordenação ---

from jarvis.referencia import casos as _casos  # noqa: E402


def _analisar_caso(servico, nome):
    servico.nova_sessao("investigacao")
    servico.registrar_percepcao("antes", "não aplicável")
    servico.importar_caso(_casos.PASTA_DADOS / nome if nome != "REF-001-A" else _casos.ref001.PASTA_PADRAO)
    return servico.analisar()


def test_ref001a_catalogo_com_qualidade_aprovada(servico, banco):
    analise = _analisar_caso(servico, "REF-001-A")
    assert analise["portao"]["classificacao"] == "aprovada" and analise["conclui"]
    assert analise["sugestao"] == "teste_polaridade"
    meds = banco.registros(servico.sessao_id, "medicao")
    assert all(m["dados"]["proveniencia"]["catalogo"] for m in meds)


def test_n2(servico):
    analise = _analisar_caso(servico, "REF-001-N2")
    assert analise["sugestao"] == "nao_da_para_concluir" and analise["conclui"] is False
    assert "σ̂" in analise["motivo"] and "limite provisório" in analise["motivo"]
    assert analise["falta"] and "menos ruído" in analise["falta"][0]
    assert servico.b.registros(servico.sessao_id, "hipotese") == []
    with pytest.raises(ErroDoPercurso):
        servico.propor_teste()
    # "solicitar dados adicionais" continua disponível
    assert servico.decidir_sem_intervencao("solicitar_dados", "Refazer com menos ruído.")["tipo"] == "solicitar_dados"


def test_n1(servico, banco):
    analise = _analisar_caso(servico, "REF-001-N1")
    assert analise["sugestao"] == "solicitar_dados"
    hip = banco.registros(servico.sessao_id, "hipotese")
    assert hip[0]["dados"]["enunciado"].startswith("Interferência ou reflexão")
    assert not any("Polaridade" in h["dados"]["enunciado"] and h["dados"]["posicao"] == 1 for h in hip)
    ind = banco.registros(servico.sessao_id, "indicio")
    assert any(i["dados"]["regra"].startswith("Regra 3") for i in ind)
    assert "Não reforce a EQ" in analise["motivo"]
    with pytest.raises(ErroDoPercurso):
        servico.propor_teste()


def test_qualidade_limita_conclusao(servico, banco):
    """Com vale numa via e ruído alto, prevalece "não dá para concluir" (edge case da spec)."""
    _analisar_caso(servico, "REF-001-N2")
    assert banco.registros(servico.sessao_id, "indicio") == []
    assert banco.registros(servico.sessao_id, "hipotese") == []


def test_nao_estimavel_preserva_descritivo(servico, banco, tmp_path):
    """Fora do catálogo (cópia alterada), suavização ausente ⇒ não estimável; o descritivo continua."""
    copia = tmp_path / "caso"
    shutil.copytree(_casos.ref001.PASTA_PADRAO, copia)
    m = json.loads((copia / "manifesto.json").read_text(encoding="utf-8"))
    m["descricao"] += " (cópia externa)"
    (copia / "manifesto.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    servico.nova_sessao("investigacao")
    servico.importar_caso(copia)
    analise = servico.analisar()
    assert analise["portao"]["classificacao"] == "nao_estimavel" and analise["conclui"] is True
    assert analise["vale"] is not None and analise["sobreposicao"]["existe"]
    assert "não quantificada" in analise["aviso_qualidade"]
    ind = banco.registros(servico.sessao_id, "indicio")
    assert ind and all(i["dados"]["qualidade"] == "não estimada" for i in ind)


# --- JV-T217 (FR-205, FR-206): N4 e N5 ---

def test_n4(servico, banco):
    analise = _analisar_caso(servico, "REF-001-N4")
    assert not analise["referencia"]["compativel"] and analise["referencia"]["declarada"]
    assert analise["fase"] is None and analise["vale"] is not None
    assert "declarada compatível" in analise["aviso_referencia"]
    assert "mesma referência temporal" in analise["aviso_referencia"]
    nomes = {c["dados"]["nome"] for c in banco.registros(servico.sessao_id, "calculo")}
    assert "diferenca_fase" not in nomes and "soma_potencias" in nomes
    with pytest.raises(ErroDoPercurso):
        servico.propor_teste()


def test_n5(servico, banco):
    analise = _analisar_caso(servico, "REF-001-N5")
    assert analise["sugestao"] == "nada_a_alterar"
    assert analise["justificativa_sugerida"].startswith("Sem indício de problema no cruzamento")
    assert not banco.registros(servico.sessao_id, "decisao")  # nada é registrado sem confirmação
    editada = analise["justificativa_sugerida"] + " Conferi a soma no programa."
    d = servico.decidir_sem_intervencao("nada_a_alterar", editada)
    assert d["fundamentacao"] == editada
    assert servico.estado()["sessao"]["estado"] == "encerrada"
    assert banco.integridade() == []


# --- JV-T218 (FR-207, INV-214): várias aquisições "depois" por via; cópia não é repetição ---

def _ate_depois(servico, nome):
    _analisar_caso(servico, nome)
    servico.propor_teste()
    servico.registrar_aplicacao()
    return servico.importar_depois()


def test_n3_importa_todas_as_aquisicoes_depois(servico):
    _ate_depois(servico, "REF-001-N3")
    tw = servico._medicoes("via_b", "depois")
    assert [m["dados"]["repeticao"] for m in tw] == [1, 2]
    assert len({m["dados"]["aquisicao_id"] for m in tw}) == 2
    assert all(m["dados"]["proveniencia"]["catalogo"] for m in tw)


def test_copia_nao_e_repeticao(servico, tmp_path):
    _ate_depois(servico, "REF-001-N3")
    pasta = _casos.PASTA_DADOS / "REF-001-N3"
    copia = tmp_path / "tweeter-depois-3.txt"
    shutil.copyfile(pasta / "tweeter-depois-1.txt", copia)
    with pytest.raises(ErroDoPercurso, match="cópia"):
        servico.importar_via_depois(copia, {"papel": "via_b", "aquisicao_id": "outra"})
    # bytes diferentes, mesmo aquisicao_id: também não é repetição
    texto = copia.read_text(encoding="utf-8").replace("* Medição simulada", "* Medição simulada (editada)")
    copia.write_text(texto, encoding="utf-8")
    with pytest.raises(ErroDoPercurso, match="já foi importada"):
        servico.importar_via_depois(copia, {"papel": "via_b", "aquisicao_id": "N3-tweeter-depois-aq1"})
    assert len(servico._medicoes("via_b", "depois")) == 2


def test_via_depois_fora_da_pasta_nao_tem_proveniencia(servico, tmp_path):
    _ate_depois(servico, "REF-001-N3")
    origem = _casos.PASTA_DADOS / "REF-001-N3" / "tweeter-depois-2.txt"
    nova = tmp_path / "tweeter-depois-extra.txt"
    nova.write_text(origem.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    info = servico.importar_via_depois(nova, {"papel": "via_b", "aquisicao_id": "aq-extra"})
    m = next(x for x in servico._medicoes("via_b", "depois") if x["id"] == info["id"])
    assert m["dados"]["proveniencia"]["catalogo"] is False and m["dados"]["repeticao"] == 3


def test_simulado_declarado_nao_presume(servico, tmp_path):
    """`simulado: true` sem proveniência de catálogo não concede presunção de suavização (INV-214)."""
    copia = tmp_path / "caso"
    shutil.copytree(_casos.ref001.PASTA_PADRAO, copia)
    m = json.loads((copia / "manifesto.json").read_text(encoding="utf-8"))
    assert m["simulado"] is True and "suavizacao" not in m["medicoes"][0]
    m["caso"] = "REF-001-A"  # nome do catálogo, mas bytes diferentes
    m["descricao"] += " "
    (copia / "manifesto.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    servico.nova_sessao("investigacao")
    servico.importar_caso(copia)
    meds = servico.b.registros(servico.sessao_id, "medicao")
    assert all(md["dados"]["proveniencia"]["catalogo"] is False for md in meds)
    assert servico.analisar()["portao"]["classificacao"] == "nao_estimavel"


# --- JV-T219 (FR-207, INV-202; ADR-208): comprometida com precedência e repetição ---

def _percurso_ate_veredito(servico, pasta):
    servico.nova_sessao("investigacao")
    servico.registrar_percepcao("antes", "não aplicável")
    servico.importar_caso(pasta)
    analise = servico.analisar()
    assert analise["sugestao"] == "teste_polaridade", analise["motivo"]
    servico.propor_teste()
    servico.registrar_aplicacao()
    servico.importar_depois()
    servico.registrar_percepcao("depois", "não aplicável")
    return servico.concluir()["dados"]


def _variante(tmp_path, nome):
    return _casos.gerar(nome, tmp_path / nome)


def test_n3(servico, banco):
    c = _percurso_ate_veredito(servico, _casos.PASTA_DADOS / "REF-001-N3")
    assert c["veredito"] == "comprometida" and c["precedencia_aplicada"] == 3
    assert "Mudança reproduzida no tweeter" in c["motivo"]
    assert "não comprova alteração no DSP" in c["motivo"]  # E4: comprometida não é prova de alteração do DSP
    assert c["verificacao_variavel_unica"]["vias"]["via_b"]["resultado"] == "mudanca_detectada_reproduzida"
    assert c["verificacao_variavel_unica"]["vias"]["via_a"]["resultado"] == "nao_verificada"
    assert banco.integridade() == []


def test_mudanca_reproduzida_nao_nomeia_parametro(servico, banco):
    c = _percurso_ate_veredito(servico, _casos.PASTA_DADOS / "REF-001-N3")
    assert "a medição não identifica a causa" in c["motivo"]
    assert "ganho" not in c["motivo"].lower()
    det = next(x for x in banco.registros(servico.sessao_id, "calculo") if x["dados"]["nome"] == "detector_mudanca")
    assert det["dados"]["resultado"]["parametro_identificado"] is False
    assert len(det["dados"]["resultado"]["depois"]) == 2


def test_repeticao_exige_faixa_compativel(servico, banco, monkeypatch):
    """E4/INV-215: duas aquisições com mudança no mesmo sentido, mas em faixas disjuntas, não confirmam."""
    from jarvis import calculos
    real = calculos.detector_mudanca_via
    chamadas = {"n": 0}

    def disjunto(*a, **k):
        r = real(*a, **k)
        chamadas["n"] += 1
        if r["resultado"] == "mudanca_detectada":  # alterna faixas sem tocar em nível nem sentido
            r = {**r, "faixa_mudanca_hz": [2000.0, 3000.0] if chamadas["n"] % 2 else [6000.0, 7000.0]}
        return r

    monkeypatch.setattr(calculos, "detector_mudanca_via", disjunto)
    c = _percurso_ate_veredito(servico, _casos.PASTA_DADOS / "REF-001-N3")
    assert c["veredito"] == "inconclusiva" and c["veredito"] != "comprometida"
    assert c["verificacao_variavel_unica"]["vias"]["via_b"]["resultado"] == "mudanca_detectada_indicativa"
    assert "Mudança suspeita" in c["motivo"] and "nenhuma alteração do DSP é afirmada" in c["motivo"]
    det = next(x for x in banco.registros(servico.sessao_id, "calculo")
               if x["dados"]["nome"] == "detector_mudanca" and x["dados"]["resultado"]["via"] == "via_b")
    assert det["dados"]["resultado"]["faixa_compativel"] is False
    assert det["dados"]["resultado"]["reproduzida"] is False


def test_comprometida_nao_refuta(servico, banco):
    c = _percurso_ate_veredito(servico, _casos.PASTA_DADOS / "REF-001-N3")
    assert c["veredito"] == "comprometida"
    assert "refutada" not in json.dumps(c, ensure_ascii=False)
    assert "refaça o teste mudando só uma variável" in c["motivo"]


def test_n3_so_declarada(servico, tmp_path):
    c = _percurso_ate_veredito(servico, _variante(tmp_path, "REF-001-N3-so-declarada"))
    assert c["veredito"] == "comprometida" and c["precedencia_aplicada"] == 1
    assert "tweeter_esq ganho" in c["motivo"]
    assert c["verificacao_variavel_unica"]["aviso"] == "outras alterações não foram verificadas"


def test_n3_so_medida(servico, tmp_path):
    c = _percurso_ate_veredito(servico, _variante(tmp_path, "REF-001-N3-so-medida"))
    assert c["veredito"] == "comprometida" and c["verificacao_variavel_unica"]["configuracao"] == "igual"


def test_n3_sem_repeticao_inconclusiva(servico, tmp_path):
    c = _percurso_ate_veredito(servico, _variante(tmp_path, "REF-001-N3-sem-repeticao"))
    assert c["veredito"] == "inconclusiva"
    assert "repita a medição individual" in c["motivo"]


def test_n3_posicao_diferente_inconclusiva(servico, tmp_path):
    c = _percurso_ate_veredito(servico, _variante(tmp_path, "REF-001-N3-posicao-diferente"))
    assert c["veredito"] != "comprometida" or c["precedencia_aplicada"] == 1
    assert c["verificacao_variavel_unica"]["vias"]["via_b"]["resultado"] == "verificacao_inconclusiva"
    assert c["verificacao_variavel_unica"]["aviso"] == "outras alterações não foram verificadas"


def test_reposicionamento_nao_compromete(servico, tmp_path):
    c = _percurso_ate_veredito(servico, _variante(tmp_path, "REF-001-N3-reposicionamento"))
    assert c["veredito"] != "comprometida"


def test_sem_dados_nao_e_sem_mudanca(servico, pasta_caso):
    c = _percurso_ate_veredito(servico, pasta_caso)
    assert c["veredito"] == "confirmada"  # REF-001-A continua confirmada (INV-210)
    v = c["verificacao_variavel_unica"]
    assert v["vias"] == {"via_a": {"resultado": "nao_verificada"}, "via_b": {"resultado": "nao_verificada"}}
    assert v["aviso"] == "outras alterações não foram verificadas"


# --- JV-T220 (FR-208, SC-202): REF-001-B, incerteza e aquisição comparável ---

def test_ref001b(servico):
    b = _percurso_ate_veredito(servico, _casos.PASTA_DADOS / "REF-001-B")
    assert b["veredito"] == "confirmada" and b["precedencia_aplicada"] == 4
    servico2 = Servico(servico.b)
    a = _percurso_ate_veredito(servico2, _casos.ref001.PASTA_PADRAO)
    assert b["incerteza_declarada"]["quantificada"] and a["incerteza_declarada"]["quantificada"]
    assert b["incerteza_declarada"]["sigma_max_db"] > a["incerteza_declarada"]["sigma_max_db"]
    assert "Incerteza declarada" in b["incerteza"]


def _copia_ref001a(tmp_path, alterar):
    copia = tmp_path / "caso"
    shutil.copytree(_casos.ref001.PASTA_PADRAO, copia)
    m = json.loads((copia / "manifesto.json").read_text(encoding="utf-8"))
    for med in m["medicoes"]:
        med["suavizacao"] = "nenhuma"
    alterar(m)
    (copia / "manifesto.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    return copia


def test_nao_estimavel_limita_veredito(servico, tmp_path):
    def sem_suavizacao_no_depois(m):
        del m["medicoes"][3]["suavizacao"]
        for med in m["medicoes"]:
            med.update(ganho_entrada_db=0.0, referencia_nivel="94 dB")
    c = _percurso_ate_veredito(servico, _copia_ref001a(tmp_path, sem_suavizacao_no_depois))
    assert c["veredito"] == "inconclusiva" and c["precedencia_aplicada"] == 2
    assert c["incerteza_declarada"]["quantificada"] is False


def test_depois_outra_posicao_nao_confirma(servico, tmp_path):
    def outra_posicao(m):
        for med in m["medicoes"]:
            med.update(ganho_entrada_db=0.0, referencia_nivel="94 dB")
        m["medicoes"][3]["posicao_microfone"] = "P2 — outra posição"
    c = _percurso_ate_veredito(servico, _copia_ref001a(tmp_path, outra_posicao))
    assert c["veredito"] == "inconclusiva"
    assert "Melhora observada, sem confirmação causal" in c["motivo"]
    # com tudo declarado igual, a mesma cópia externa confirma
    servico2 = Servico(servico.b)
    c2 = _percurso_ate_veredito(servico2, _copia_ref001a(tmp_path / "b", lambda m: [
        med.update(ganho_entrada_db=0.0, referencia_nivel="94 dB") for med in m["medicoes"]]))
    assert c2["veredito"] == "confirmada"


# ---- JV-T226: a recomendação passa pelo módulo de segurança (FR-211, ADR-204) ---------------------------

def test_polaridade_passa_por_seguranca(servico, pasta_caso):
    from jarvis import seguranca as seg
    _ate_analise(servico, pasta_caso)
    d = servico.propor_teste()["dados"]
    s = d["seguranca"]
    alt = {"canal": "tweeter_esq", "parametro": "polaridade", "tipo": "polaridade",
           "de": d["variavel"]["de"], "para": d["variavel"]["para"]}
    esperado = seg.avaliar(alt, None)
    assert s["regras"] == esperado  # resultados e motivos do módulo, sem reescrever
    assert [r["regra"] for r in s["regras"]] == list(seg.REGRAS)
    assert s["admissibilidade"] == seg.admissibilidade(seg.classificar(alt), esperado)
    assert s["classe"] == seg.NAO_SENSIVEL and s["versao_regras_seg"] == seg.VERSAO == "0.4.0"
    assert s["motivo"] == s["admissibilidade"]["motivo"] and s["limitacoes"] == seg.LIMITACOES
    por = {r["regra"]: r["resultado"] for r in s["regras"]}
    assert por["SEG-08"] == por["SEG-11"] == seg.APROVADA
    assert d["receita"] and s["admissibilidade"]["admissivel"] is True


def test_bloqueada_sem_receita_e_sem_aplicacao(servico, pasta_caso, monkeypatch):
    from jarvis import seguranca as seg
    _ate_analise(servico, pasta_caso)
    original = seg.avaliar

    def com_bloqueio(alteracao, equipamento=None):
        res = original(alteracao, equipamento)
        res[0] = seg.resultado("SEG-01", seg.BLOQUEADA, "bloqueio de teste", falta="dado de teste")
        res[1] = seg.resultado("SEG-02", seg.NAO_VERIFICAVEL, "sem fonte", falta="fonte de teste")
        return res
    monkeypatch.setattr(seg, "avaliar", com_bloqueio)
    rec = servico.propor_teste()
    d = rec["dados"]
    assert rec["titulo"] == "Alteração bloqueada — não recomendada"
    assert d["receita"] is None and d["seguranca"]["admissibilidade"]["admissivel"] is False
    assert d["seguranca"]["admissibilidade"]["estado"] == "bloqueada"
    por = {r["regra"]: r for r in d["seguranca"]["regras"]}  # os três estados permanecem distintos
    assert por["SEG-01"]["resultado"] == seg.BLOQUEADA and por["SEG-02"]["resultado"] == seg.NAO_VERIFICAVEL
    assert por["SEG-08"]["resultado"] == seg.APROVADA
    assert "SEG-02" in d["seguranca"]["admissibilidade"]["nao_verificadas"]
    with pytest.raises(ErroDoPercurso, match="bloqueada"):
        servico.registrar_aplicacao()
    assert servico._ultimo("experimento") is None
    with pytest.raises(ErroDoPercurso):
        servico.importar_depois()


def test_nao_verificavel_nao_vira_aprovado(servico, pasta_caso, monkeypatch):
    from jarvis import seguranca as seg
    _ate_analise(servico, pasta_caso)
    original = seg.avaliar

    def com_nao_verificavel(alteracao, equipamento=None):
        res = original(alteracao, equipamento)
        res[2] = seg.resultado("SEG-03", seg.NAO_VERIFICAVEL, "sem dado", falta="potência")
        return res
    monkeypatch.setattr(seg, "avaliar", com_nao_verificavel)
    d = servico.propor_teste()["dados"]
    assert {r["regra"]: r["resultado"] for r in d["seguranca"]["regras"]}["SEG-03"] == seg.NAO_VERIFICAVEL
    assert d["seguranca"]["admissibilidade"]["nao_verificadas"] == ["SEG-03"]
    assert d["seguranca"]["admissibilidade"]["admissivel"] is True  # não sensível: admitida, com a lista


def test_registro_anterior_a_admissibilidade_nao_contorna_restricao():
    exigir = Servico._exigir_admissivel
    v01 = {"seguranca": {"classe": "não sensível", "regras": []}, "receita": ["passo"]}
    exigir({"dados": v01})  # registro histórico não sensível segue aplicável, sem reavaliação (INV-211)
    for dados in ({"seguranca": {"classe": "sensível — risco crescente"}, "receita": ["passo"]},
                  {"seguranca": {"classe": "sensível — risco decrescente"}, "receita": ["passo"]},
                  {"receita": ["passo"]},
                  {"seguranca": {"classe": "não sensível", "admissibilidade": {"admissivel": False}},
                   "receita": ["passo"]},
                  {"seguranca": {"classe": "não sensível"}, "receita": None}):
        with pytest.raises(ErroDoPercurso):
            exigir({"dados": dados})


# ---- JV-T227: aplicar exige a aprovação, sem substituir a avaliação de segurança --------------------------

def _preparar(servico, cria_recomendacao, **campos):
    servico.nova_sessao()
    servico.registrar_percepcao("antes", "não aplicável")
    servico.b.nova_configuracao(servico.sessao_id, "base", "declarada",
                                [{"canal": "medio_esq", "parametro": "EQ 1 kHz", "valor": "0 dB",
                                  "origem": "declarado"}])
    return cria_recomendacao(servico, **campos)


ESC = {"canal": "medio_esq", "parametro": "EQ 1 kHz", "de": "0 dB", "para": "−2 dB"}


def test_sensivel_sem_aprovacao_nao_e_aplicada(servico, cria_recomendacao):
    _preparar(servico, cria_recomendacao)
    with pytest.raises(ErroDoPercurso, match="aprovação de nível B"):
        servico.registrar_aplicacao()
    assert servico._ultimo("experimento") is None
    assert servico.b.aprovacoes() == []  # nenhuma aprovação automática


def test_sensivel_com_aprovacao_exata_e_aplicada(servico, cria_recomendacao):
    rid = _preparar(servico, cria_recomendacao)
    servico.aprovar(rid, ESC)
    assert servico.registrar_aplicacao().startswith("X-")


def test_aprovacao_de_outro_escopo_nao_vale(servico, cria_recomendacao):
    rid = _preparar(servico, cria_recomendacao)
    servico.b.nova_aprovacao(servico.sessao_id, rid, {**ESC, "para": "−6 dB"})  # inserida por fora do serviço
    with pytest.raises(ErroDoPercurso, match="escopo é outro"):
        servico.registrar_aplicacao()
    assert servico._ultimo("experimento") is None


def test_aprovacao_nao_libera_bloqueada(servico, cria_recomendacao):
    rid = _preparar(servico, cria_recomendacao, tipo="reforco_eq", ganho_db=1.0, para="+1 dB")
    with pytest.raises(ErroDoPercurso, match="não a libera"):
        servico.aprovar(rid, {**ESC, "para": "+1 dB"})
    servico.b.nova_aprovacao(servico.sessao_id, rid, {**ESC, "para": "+1 dB"})  # aprovação forçada por fora
    with pytest.raises(ErroDoPercurso, match="bloqueada"):
        servico.registrar_aplicacao()
    assert servico._ultimo("experimento") is None


def test_polaridade_nao_sensivel_segue_sem_aprovacao(servico, pasta_caso):
    _ate_analise(servico, pasta_caso)
    servico.propor_teste()
    assert servico.registrar_aplicacao().startswith("X-")  # histórico e polaridade não exigem aprovação
    assert servico.b.aprovacoes() == []
