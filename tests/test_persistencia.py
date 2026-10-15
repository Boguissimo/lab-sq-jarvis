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
