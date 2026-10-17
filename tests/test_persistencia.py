import sqlite3

import pytest

from jarvis.persistencia import OriginalImutavel, sha256_de


def test_original_imutavel(banco, pasta_caso):
    sha = banco.guardar_original(pasta_caso / "medio.txt", "texto")
    assert banco.verificar_original(sha)
    assert sha == sha256_de(pasta_caso / "medio.txt")
    with pytest.raises(OriginalImutavel):
        banco.substituir_original(sha, b"outro conteudo")
    with pytest.raises(sqlite3.DatabaseError, match="não pode ser alterado"):
        banco.con.execute("UPDATE arquivo_original SET nome = 'x' WHERE sha256 = ?", (sha,))
    with pytest.raises(sqlite3.DatabaseError):
        banco.con.execute("DELETE FROM arquivo_original WHERE sha256 = ?", (sha,))
    # guardar de novo o mesmo arquivo não duplica nem altera
    assert banco.guardar_original(pasta_caso / "medio.txt", "texto") == sha
    assert any("recusada" in e["descricao"] for e in banco.con.execute("SELECT * FROM diario"))


def test_original_alterado_fora_do_programa_e_detectado(banco, pasta_caso):
    sha = banco.guardar_original(pasta_caso / "medio.txt", "texto")
    caminho = banco.caminho_original(sha)
    caminho.chmod(0o644)
    caminho.write_text("adulterado")
    assert not banco.verificar_original(sha)


def test_diario_so_insercao(banco):
    banco.diario(None, "teste", "evento")
    with pytest.raises(sqlite3.DatabaseError, match="só aceita"):
        banco.con.execute("UPDATE diario SET descricao = 'x'")
    with pytest.raises(sqlite3.DatabaseError):
        banco.con.execute("DELETE FROM diario")


def test_registro_nao_pode_ser_alterado(banco):
    sid = banco.nova_sessao("investigacao", None)
    rid = banco.novo_registro(sid, "percepcao", "p", {"momento": "antes"})
    with pytest.raises(sqlite3.DatabaseError):
        banco.con.execute("UPDATE registro SET titulo = 'x' WHERE id = ?", (rid,))


def test_integridade_detecta_derivacao_proibida(banco):
    sid = banco.nova_sessao("investigacao", None)
    c = banco.novo_registro(sid, "calculo", "c", {"nome": "x"})  # cálculo sem origem
    banco.novo_registro(sid, "hipotese", "h", {}, origens=[(c, "apoio")])  # hipótese ← cálculo: proibido
    problemas = banco.integridade()
    assert any("sem origem" in p for p in problemas)
    assert any("não pode derivar de calculo" in p for p in problemas)


def test_integridade_conclusao_exige_experimento(banco):
    sid = banco.nova_sessao("investigacao", None)
    p = banco.novo_registro(sid, "percepcao", "p", {"momento": "depois"})
    banco.novo_registro(sid, "conclusao", "a", {"veredito": "confirmada"}, origens=[(p, "x")])
    assert any("conclusão experimental sem experimento" in x for x in banco.integridade())


def test_integridade_decisao_sem_intervencao(banco):
    sid = banco.nova_sessao("investigacao", None)
    banco.novo_registro(sid, "decisao", "d", {"sem_intervencao": True, "fundamentacao": ""})
    problemas = banco.integridade()
    assert any("sem fundamentação" in p for p in problemas)
    assert any("sem registros que a sustentem" in p for p in problemas)


# --- JV-T204 (ADR-212, A06): cofre atômico, reconciliado e varrido pela integridade ---

def test_falha_entre_copia_e_insert_reconcilia(banco, pasta_caso, monkeypatch):
    def falha(*a, **k):
        raise RuntimeError("queda simulada entre a cópia e o INSERT")
    monkeypatch.setattr(banco, "_inserir_inventario", falha)
    with pytest.raises(RuntimeError):
        banco.guardar_original(pasta_caso / "medio.txt", "texto")
    sha = sha256_de(pasta_caso / "medio.txt")
    assert banco.caminho_original(sha).exists()
    assert any("órfão" in p for p in banco.integridade())
    monkeypatch.undo()
    assert banco.guardar_original(pasta_caso / "medio.txt", "texto") == sha  # reconcilia
    assert banco.con.execute("SELECT COUNT(*) FROM arquivo_original WHERE sha256 = ?", (sha,)).fetchone()[0] == 1
    assert banco.integridade() == []


def test_orfao_no_cofre_detectado(banco, pasta_caso):
    sha = sha256_de(pasta_caso / "tweeter.txt")
    destino = banco.caminho_original(sha)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes((pasta_caso / "tweeter.txt").read_bytes())
    problemas = banco.integridade()
    assert any(sha[:12] in p and "órfão" in p for p in problemas)


def test_linha_sem_arquivo_e_hash_divergente_detectados(banco, pasta_caso):
    sha = banco.guardar_original(pasta_caso / "medio.txt", "texto")
    caminho = banco.caminho_original(sha)
    caminho.chmod(0o644)
    caminho.write_text("adulterado")
    assert any("hash divergente" in p for p in banco.integridade())
    caminho.unlink()
    assert any("sem arquivo no cofre" in p for p in banco.integridade())


def test_tmp_residual_detectado(banco):
    tmp = banco.cofre / ".tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / "resto").write_bytes(b"x")
    assert any(".tmp/resto" in p for p in banco.integridade())


def test_guardar_nao_deixa_tmp(banco, pasta_caso):
    banco.guardar_original(pasta_caso / "soma-antes.txt", "texto")
    assert not any((banco.cofre / ".tmp").iterdir())


def test_sessao_v01_legivel(tmp_path, monkeypatch):
    """Sessão gravada pelo V01 abre com a análise reconstruída pelas regras 1.0 (INV-211)."""
    import shutil
    from pathlib import Path
    from jarvis import regras
    from jarvis.persistencia import Banco
    from jarvis.sessao import Servico
    pasta = tmp_path / "dados"
    shutil.copytree(Path(__file__).parent / "dados" / "banco-v01", pasta)
    for p in pasta.rglob("*"):
        if p.is_file():
            p.chmod(0o644)
    monkeypatch.setattr(regras, "avaliar", lambda *a, **k: (_ for _ in ()).throw(AssertionError("regras atuais")))
    b = Banco(pasta)
    try:
        s = Servico(b)
        s.sessao_id = 1
        analise = s.estado()["analise"]
        assert analise["interpretacao"] == "reconstruída pelas regras 1.0"
        assert analise["sugestao"] == "teste_polaridade"
    finally:
        b.fechar()


# ---- JV-T227: aprovação de nível B do Jarvis (FR-216; critério 6 do plano) ----------------------------------

ESCOPO = {"canal": "medio_esq", "parametro": "EQ 1 kHz", "de": "0 dB", "para": "−2 dB"}


def _com_recomendacao(servico, cria_recomendacao, **campos):
    servico.nova_sessao()
    return cria_recomendacao(servico, **campos)


def test_cenario_sensivel_admissivel_existe(servico, cria_recomendacao):
    rid = _com_recomendacao(servico, cria_recomendacao)
    adm = servico.b.registros(servico.sessao_id, "recomendacao")[0]["dados"]["seguranca"]["admissibilidade"]
    assert adm["admissivel"] is True and adm["exige_aprovacao_b"] is True and adm["nao_verificadas"]
    ap = servico.aprovar(rid, ESCOPO)
    assert ap["nivel"] == "B" and ap["recomendacao"] == rid and ap["escopo"] == ESCOPO and ap["autor"] == "usuário"
    assert servico.b.aprovacao_de(rid) == ap
    assert not [p for p in servico.b.integridade() if "aprovação" in p]


def _inexistente(s, c):
    return "R-9999", ESCOPO


def _outra_sessao(s, c):
    rid = c(s)
    s.nova_sessao()
    return rid, ESCOPO


def _outro_tipo(s, c):
    c(s)
    return s.b.registros(s.sessao_id, "hipotese")[0]["id"], ESCOPO


def _bloqueada(s, c):
    return c(s, tipo="reforco_eq", ganho_db=1.0, para="+1 dB"), {**ESCOPO, "para": "+1 dB"}


def _nao_sensivel(s, c):
    return (c(s, tipo="polaridade", de="0°", para="180°", parametro="polaridade"),
            {"canal": "medio_esq", "parametro": "polaridade", "de": "0°", "para": "180°"})


def _escopo_diferente(s, c):
    return c(s), {**ESCOPO, "para": "−6 dB"}


def _escopo_incompleto(s, c):
    return c(s), {"canal": "medio_esq", "parametro": "EQ 1 kHz"}


def _duplicada(s, c):
    rid = c(s)
    s.aprovar(rid, ESCOPO)
    return rid, ESCOPO


@pytest.mark.parametrize("montar", [_inexistente, _outra_sessao, _outro_tipo, _bloqueada, _nao_sensivel,
                                    _escopo_diferente, _escopo_incompleto, _duplicada],
                         ids=lambda f: f.__name__.strip("_"))
def test_aprovacao_integridade_servico_recusa(servico, cria_recomendacao, montar):
    from jarvis.sessao import ErroDoPercurso
    servico.nova_sessao()
    rid, escopo = montar(servico, cria_recomendacao)
    antes = len(servico.b.aprovacoes())
    with pytest.raises(ErroDoPercurso):
        servico.aprovar(rid, escopo)
    assert len(servico.b.aprovacoes()) == antes  # nada foi gravado pela recusa


@pytest.mark.parametrize("montar", [_inexistente, _outra_sessao, _outro_tipo], ids=lambda f: f.__name__.strip("_"))
def test_aprovacao_integridade_gatilho_recusa(servico, cria_recomendacao, montar):
    servico.nova_sessao()
    rid, escopo = montar(servico, cria_recomendacao)
    with pytest.raises(sqlite3.DatabaseError, match="recomendação existente"):
        servico.b.nova_aprovacao(servico.sessao_id, rid, escopo)


def test_aprovacao_integridade_nivel_e_so_insercao(servico, cria_recomendacao):
    rid = _com_recomendacao(servico, cria_recomendacao)
    with pytest.raises(sqlite3.DatabaseError):
        servico.b.nova_aprovacao(servico.sessao_id, rid, ESCOPO, nivel="A")  # CHECK (nivel = 'B')
    servico.aprovar(rid, ESCOPO)
    with pytest.raises(sqlite3.DatabaseError):
        servico.b.nova_aprovacao(servico.sessao_id, rid, ESCOPO)  # UNIQUE: uma aprovação por recomendação
    with pytest.raises(sqlite3.DatabaseError, match="Aprovação registrada"):
        servico.b.con.execute("UPDATE aprovacao SET autor = 'x'")
    with pytest.raises(sqlite3.DatabaseError, match="Aprovação registrada"):
        servico.b.con.execute("DELETE FROM aprovacao")


@pytest.mark.parametrize("caso,esperado", [
    ("inexistente", "não aponta para uma recomendação existente"),
    ("outra_sessao", "recomendação de outra sessão"),
    ("outro_tipo", "não aponta para uma recomendação existente"),
    ("bloqueada", "bloqueada ou sem admissibilidade"),
    ("nao_sensivel", "não sensível não recebe aprovação"),
    ("escopo", "escopo diferente da alteração"),
    ("momento", "momento anterior à recomendação"),
])
def test_aprovacao_integridade_acusa_insercao_direta(servico, cria_recomendacao, caso, esperado):
    """Aprovação inserida por SQL direto, com o gatilho de entrada removido, é acusada por ``integridade()``."""
    servico.nova_sessao()
    b = servico.b
    b.con.execute("DROP TRIGGER aprovacao_recomendacao_valida")
    sessao, ok = servico.sessao_id, cria_recomendacao(servico)
    rid, escopo, momento = ok, ESCOPO, "9999-12-31T00:00:00+00:00"
    if caso == "inexistente":
        rid = "R-9999"
    elif caso == "outra_sessao":
        sessao = servico.nova_sessao()
    elif caso == "outro_tipo":
        rid = b.registros(sessao, "hipotese")[0]["id"]
    elif caso == "bloqueada":
        rid = cria_recomendacao(servico, tipo="reforco_eq", ganho_db=1.0, para="+1 dB")
        escopo = {**ESCOPO, "para": "+1 dB"}
    elif caso == "nao_sensivel":
        rid = cria_recomendacao(servico, tipo="polaridade", de="0°", para="180°", parametro="polaridade")
        escopo = {"canal": "medio_esq", "parametro": "polaridade", "de": "0°", "para": "180°"}
    elif caso == "escopo":
        escopo = {**ESCOPO, "para": "−6 dB"}
    elif caso == "momento":
        momento = "2000-01-01T00:00:00+00:00"
    if caso != "momento":
        momento = "9999-12-31T00:00:00+00:00"
    b.con.execute("PRAGMA foreign_keys = OFF")
    b.nova_aprovacao(sessao, rid, escopo, momento=momento)
    assert any(esperado in p for p in b.integridade()), b.integridade()


# ---- P1 0.5.0: declaração, origem declarada do manifesto (tipo primário; sem T228) -------------------------

import json  # noqa: E402

MANIFESTO = {"caso": "REF-X", "simulado": True,
             "equipamento": [{"canal": "medio_esq", "estado": "informado"}],
             "alteracao_candidata": {"canal": "medio_esq", "tipo": "corte_eq", "ganho_db": -2.0}}


def _declaracao(banco, tmp_path, manifesto=None, **mudar):
    """Declaração montada à mão: manifesto no cofre, snapshot fiel e registro primário (sem usar a T228)."""
    manifesto = MANIFESTO if manifesto is None else manifesto
    arq = tmp_path / "manifesto.json"
    arq.write_text(json.dumps(manifesto), encoding="utf-8")
    sha = banco.guardar_original(arq, "manifesto do caso (declarado)")
    sid = banco.nova_sessao("investigacao", manifesto.get("caso"))
    dados = {"marca": "declarado", "sha256": sha, "arquivo": "manifesto.json",
             "fonte": {"caso": manifesto.get("caso"), "simulado": True, "catalogo": False},
             **{k: manifesto[k] for k in banco.CAMPOS_DECLARADOS if k in manifesto}}
    dados.update(mudar)
    return sid, banco.novo_registro(sid, "declaracao", "declaração", dados, autor="usuário"), sha


def test_declaracao_integra_e_prefixo(banco, tmp_path):
    _, rid, _ = _declaracao(banco, tmp_path)
    assert rid == "L-0001"
    assert banco.integridade() == []


def test_declaracao_deriva_so_para_calculo(banco, tmp_path):
    sid, rid, _ = _declaracao(banco, tmp_path)
    banco.novo_registro(sid, "calculo", "avaliação", {}, origens=[(rid, "declaração")])
    assert banco.integridade() == []
    for tipo in ("indicio", "hipotese", "recomendacao", "experimento", "conclusao", "decisao"):
        banco.novo_registro(sid, tipo, "x", {"sem_intervencao": True, "fundamentacao": "x"}, origens=[(rid, "x")])
    problemas = banco.integridade()
    for tipo in ("indicio", "hipotese", "recomendacao", "experimento", "conclusao", "decisao"):
        assert any(f"{tipo} não pode derivar de declaracao" in p for p in problemas), tipo


def test_declaracao_nao_tem_origem(banco, tmp_path):
    sid, rid, _ = _declaracao(banco, tmp_path)
    m = banco.novo_registro(sid, "calculo", "c", {}, origens=[(rid, "declaração")])
    banco.con.execute("INSERT INTO derivacao VALUES (?, ?, ?)", (m, rid, "origem indevida"))
    assert any("declaração não pode ter origem" in p for p in banco.integridade())


def test_calculo_continua_exigindo_origem(banco, tmp_path):
    sid, _, _ = _declaracao(banco, tmp_path)
    banco.novo_registro(sid, "calculo", "sem origem", {})
    assert any("calculo sem origem na cadeia" in p for p in banco.integridade())


def test_declaracao_nao_e_medicao(banco, tmp_path):
    sid, rid, _ = _declaracao(banco, tmp_path)
    c = banco.novo_registro(sid, "calculo", "c", {}, origens=[(rid, "declaração")])
    assert [o["tipo"] for o in banco.origens_de(c)] == ["declaracao"]


def test_declaracao_sem_marca_ou_com_marca_errada(banco, tmp_path):
    _declaracao(banco, tmp_path, marca="medido")
    assert any("sem a marca “declarado”" in p for p in banco.integridade())


def test_declaracao_manifesto_adulterado_no_cofre(banco, tmp_path):
    _, _, sha = _declaracao(banco, tmp_path)
    caminho = banco.caminho_original(sha)
    caminho.chmod(0o644)
    caminho.write_text("{}")
    assert any("manifesto ausente ou alterado no cofre" in p for p in banco.integridade())


def test_declaracao_manifesto_ausente_do_cofre(banco, tmp_path):
    _, _, sha = _declaracao(banco, tmp_path)
    caminho = banco.caminho_original(sha)
    caminho.chmod(0o644)
    caminho.unlink()
    assert any("manifesto ausente ou alterado no cofre" in p for p in banco.integridade())


@pytest.mark.parametrize("campo,novo", [
    ("alteracao_candidata", {"canal": "tweeter_esq", "tipo": "corte_eq", "ganho_db": -2.0}),
    ("equipamento", [{"canal": "medio_esq", "estado": "confirmado"}]),
])
def test_declaracao_snapshot_adulterado_com_hash_intacto(banco, tmp_path, campo, novo):
    _declaracao(banco, tmp_path, **{campo: novo})
    assert banco.integridade() == [f"L-0001: declaração: “{campo}” diverge do manifesto preservado"]


def test_declaracao_campo_a_mais_ou_a_menos_no_snapshot(banco, tmp_path):
    _declaracao(banco, tmp_path, manifesto={"caso": "REF-X", "equipamento": MANIFESTO["equipamento"]},
                alteracao_candidata={"tipo": "corte_eq"})
    assert any("“alteracao_candidata” diverge" in p for p in banco.integridade())


def test_declaracao_fonte_e_sessao_coerentes(banco, tmp_path):
    _declaracao(banco, tmp_path, fonte={"caso": "OUTRO", "simulado": True, "catalogo": False})
    assert any("fonte não identifica o caso do manifesto" in p for p in banco.integridade())


def test_declaracao_caso_da_sessao_diferente_da_fonte(banco, tmp_path):
    sid, _, _ = _declaracao(banco, tmp_path)
    banco.con.execute("UPDATE sessao SET caso = 'REF-Y' WHERE id = ?", (sid,))
    assert any("caso da fonte diferente do caso da sessão" in p for p in banco.integridade())


def test_declaracao_sem_campos_declarados(banco, tmp_path):
    _declaracao(banco, tmp_path, manifesto={"caso": "REF-X"})
    assert any("sem equipamento nem alteração candidata" in p for p in banco.integridade())


def test_sessao_v01_integridade_inalterada_com_declaracao_nova(tmp_path):
    """Histórico (fixture do V01): a integridade não muda e nenhuma declaração é criada retroativamente (INV-211)."""
    import shutil
    from pathlib import Path
    from jarvis.persistencia import Banco
    pasta = tmp_path / "dados"
    shutil.copytree(Path(__file__).parent / "dados" / "banco-v01", pasta)
    for p in pasta.rglob("*"):
        if p.is_file():
            p.chmod(0o644)
    b = Banco(pasta)
    try:
        assert b.integridade() == []
        assert b.con.execute("SELECT COUNT(*) FROM registro WHERE tipo = 'declaracao'").fetchone()[0] == 0
    finally:
        b.fechar()
