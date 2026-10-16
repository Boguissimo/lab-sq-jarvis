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
