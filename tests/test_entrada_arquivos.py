"""JV-T251 (FR-002, FR-004): entrada de arquivos sem exceção solta e com mensagem em português.

Todo defeito de manifesto ou de arquivo de medição vira `ErroDoPercurso`/`FormatoInvalido` em linguagem simples, sem
texto do sistema em inglês, e uma falha não deixa a sessão com medições pela metade.
"""
import json
import shutil

import pytest

from jarvis import rew_texto
from jarvis.sessao import ErroDoPercurso


def _copia(pasta_caso, tmp_path, alterar=None):
    copia = tmp_path / "caso"
    shutil.copytree(pasta_caso, copia)
    if alterar:
        m = json.loads((copia / "manifesto.json").read_text(encoding="utf-8"))
        alterar(m)
        (copia / "manifesto.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    return copia


def _sem(chave):
    return lambda m: m.pop(chave)


DEFEITOS = {
    "sem medicoes": (_sem("medicoes"), "falta a lista “medicoes”"),
    "sem configuracao_declarada": (_sem("configuracao_declarada"), "falta o campo “configuracao_declarada”"),
    "sem caso": (_sem("caso"), "falta o campo “caso”"),
    "medição sem arquivo": (lambda m: m["medicoes"][0].pop("arquivo"), "falta o “arquivo” na medição 1"),
    "momento inválido": (lambda m: m["medicoes"][0].update(momento="agora"), "“momento” da medição 1"),
    "papel inválido": (lambda m: m["medicoes"][0].update(papel="tweeter"), "“papel” da medição 1"),
    "nenhuma medição antes": (lambda m: [x.update(momento="depois") for x in m["medicoes"]], "nenhuma medição “antes”"),
    "referencia_temporal não objeto": (lambda m: m["medicoes"][0].update(referencia_temporal="loopback"),
                                       "“referencia_temporal” da medição 1 deve ser um objeto"),
    "id da referência em lista": (lambda m: m["medicoes"][0]["referencia_temporal"].update(id=[1]), "devem ser texto"),
    "taxa em texto": (lambda m: m["medicoes"][0].update(taxa_amostragem="abc"), "“taxa_amostragem” da medição 1"),
    "taxa negativa": (lambda m: m["medicoes"][0].update(taxa_amostragem=-1), "número positivo"),
    "posição do microfone numérica": (lambda m: m["medicoes"][0].update(posicao_microfone=3), "“posicao_microfone”"),
    "suavização numérica": (lambda m: m["medicoes"][0].update(suavizacao=3), "“suavizacao”"),
    "parâmetro sem texto": (lambda m: m["configuracao_declarada"]["parametros"][0].update(valor=0), "o parâmetro 1"),
    "simulado em texto": (lambda m: m.update(simulado="sim"), "“simulado” deve ser verdadeiro ou falso"),
    "depois não objeto": (lambda m: m.update(depois="x"), "“depois” deve ser um objeto"),
}


@pytest.mark.parametrize("nome", list(DEFEITOS))
def test_manifesto_com_defeito_vira_mensagem_simples_e_nao_registra_nada(servico, pasta_caso, tmp_path, nome):
    alterar, trecho = DEFEITOS[nome]
    sid = servico.nova_sessao("investigacao")
    with pytest.raises(ErroDoPercurso, match="manifesto.json.*(incompleto ou inválido)") as e:
        servico.importar_caso(_copia(pasta_caso, tmp_path, alterar))
    assert trecho in str(e.value)
    assert not servico.b.registros(sid, "medicao")          # nada pela metade


def test_manifesto_que_nao_e_json_nem_objeto_nem_utf8(servico, pasta_caso, tmp_path):
    servico.nova_sessao("investigacao")
    copia = _copia(pasta_caso, tmp_path)
    (copia / "manifesto.json").write_text("{não é json", encoding="utf-8")
    with pytest.raises(ErroDoPercurso, match="não está em formato JSON válido"):
        servico.importar_caso(copia)
    (copia / "manifesto.json").write_text("[1, 2]", encoding="utf-8")
    with pytest.raises(ErroDoPercurso, match="não descreve um caso"):
        servico.importar_caso(copia)
    (copia / "manifesto.json").write_bytes(b"\xff\xfe\x00\x80 lixo")
    with pytest.raises(ErroDoPercurso, match="não é um texto legível"):
        servico.importar_caso(copia)


def test_pasta_sem_manifesto_mantem_a_mensagem_de_antes(servico, tmp_path):
    servico.nova_sessao("investigacao")
    with pytest.raises(ErroDoPercurso, match="falta o arquivo manifesto.json"):
        servico.importar_caso(tmp_path)


def test_arquivo_de_medicao_ausente_ou_pasta_em_portugues_sem_texto_do_sistema(servico, pasta_caso, tmp_path):
    servico.nova_sessao("investigacao")
    copia = _copia(pasta_caso, tmp_path)
    (copia / "tweeter.txt").unlink()
    with pytest.raises(rew_texto.FormatoInvalido) as e:
        servico.importar_caso(copia)
    assert "não existe" in str(e.value) and "No such file" not in str(e.value)
    with pytest.raises(rew_texto.FormatoInvalido, match="é uma pasta"):
        rew_texto.ler(tmp_path)


def test_falha_no_terceiro_arquivo_nao_deixa_a_sessao_pela_metade(servico, pasta_caso, tmp_path):
    sid = servico.nova_sessao("investigacao")
    copia = _copia(pasta_caso, tmp_path)
    original = (copia / "soma-antes.txt").read_text(encoding="utf-8")
    (copia / "soma-antes.txt").write_text("lixo\nlixo\n", encoding="utf-8")
    with pytest.raises(rew_texto.FormatoInvalido, match="Não encontrei dados"):
        servico.importar_caso(copia)
    assert not servico.b.registros(sid, "medicao")
    (copia / "soma-antes.txt").write_text(original, encoding="utf-8")       # corrige o arquivo e tenta de novo
    assert len(servico.importar_caso(copia)["medicoes"]) == 3


def _ate_aplicacao(servico, pasta):
    servico.nova_sessao("investigacao")
    servico.registrar_percepcao("antes", "não aplicável")
    servico.importar_caso(pasta)
    servico.analisar()
    servico.propor_teste()
    servico.registrar_aplicacao()


def test_importar_depois_sem_depois_no_caso_pede_o_arquivo_em_vez_de_quebrar(servico, pasta_caso, tmp_path):
    def sem_depois(m):
        m["medicoes"] = [x for x in m["medicoes"] if x["momento"] == "antes"]
        m.pop("depois", None)
    _ate_aplicacao(servico, _copia(pasta_caso, tmp_path, sem_depois))
    with pytest.raises(ErroDoPercurso, match="não traz a medição “depois”"):
        servico.importar_depois()


def test_importar_depois_com_arquivo_inexistente_e_via_depois_inexistente(servico, pasta_caso, tmp_path):
    _ate_aplicacao(servico, _copia(pasta_caso, tmp_path))
    with pytest.raises(rew_texto.FormatoInvalido, match="não existe"):
        servico.importar_depois(tmp_path / "nao-existe.txt")
    with pytest.raises(ErroDoPercurso, match="Não consegui abrir.*não existe"):
        servico.importar_via_depois(tmp_path / "nao-existe.txt", {"papel": "via_a"})


def test_manifesto_apagado_depois_de_importar_nao_quebra_o_depois(servico, pasta_caso, tmp_path):
    copia = _copia(pasta_caso, tmp_path)
    _ate_aplicacao(servico, copia)
    (copia / "manifesto.json").unlink()
    with pytest.raises(ErroDoPercurso, match="falta o arquivo manifesto.json"):
        servico.importar_depois()


# --- Pacote pós-G2: a identificação de pasta fica dentro do tratamento de erros (Python 3.11 a 3.14) ---

from pathlib import Path  # noqa: E402


def _levanta(erro):
    def f(self, *a, **k):
        raise erro
    return f


@pytest.mark.parametrize("erro, trecho", [(PermissionError(13, "Permission denied"), "sem permissão"),
                                          (OSError(5, "Input/output error"), "não deixou ler")])
def test_is_dir_que_propaga_erro_do_sistema_nao_escapa(monkeypatch, tmp_path, erro, trecho):
    """Em Python 3.11 `Path.is_dir()` pode propagar erro de permissão; o usuário recebe mensagem simples."""
    monkeypatch.setattr(Path, "is_dir", _levanta(erro))
    with pytest.raises(rew_texto.FormatoInvalido, match=trecho) as e:
        rew_texto.ler(tmp_path / "medicao.txt")
    assert "Permission denied" not in str(e.value) and "Input/output" not in str(e.value)


def test_pasta_como_no_windows_nao_chega_a_ser_lida(monkeypatch, tmp_path):
    """No Windows, ler uma pasta gera PermissionError; a pasta é identificada antes e a leitura nem é tentada."""
    chamadas = []

    def read_text_windows(self, *a, **k):
        chamadas.append(self)
        raise PermissionError(13, "Permission denied")
    monkeypatch.setattr(Path, "read_text", read_text_windows)
    with pytest.raises(rew_texto.FormatoInvalido, match="isto é uma pasta, não um arquivo"):
        rew_texto.ler(tmp_path)
    assert chamadas == []


def test_arquivo_comum_continua_sendo_lido(tmp_path):
    arq = tmp_path / "m.txt"
    arq.write_text("\n".join(f"{100 * (i + 1)} {80 + i} {-i}" for i in range(15)), encoding="utf-8")
    assert rew_texto.ler(arq).freq_hz.size == 15
