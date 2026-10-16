"""Braço A: Jarvis sobre os dados originais de joeglondon/speakers-2026-filters, sem preencher metadados ausentes.

Uso: python ferramentas/investigacao/braco_a.py <pasta-clone> <pasta-trabalho> <saida.json>
Copia os arquivos para a pasta de trabalho (fora do repositório do Jarvis; sem redistribuição), monta o
manifesto só com o que é verificável nos arquivos, roda Servico.nova_sessao/importar_caso/analisar e grava a
saída integral. Não altera o produto.
"""
import json, re, shutil, sys, tempfile, traceback
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import verificar_origem, ler_spl, sha256
from jarvis import rew_texto
from jarvis.persistencia import Banco
from jarvis.sessao import Servico, ErroDoPercurso


def taxa_do_impulso(fonte: Path, nome: str, spl_cab: list[str]) -> int | None:
    """Taxa de amostragem do arquivo de impulso exportado da MESMA medição (mesmo nome e mesma data)."""
    cab = (fonte / "Impulse" / f"{nome}.txt").read_text(encoding="utf-8", errors="replace").splitlines()[:30]
    data_spl = next(l for l in spl_cab if l.startswith("* Dated"))
    data_imp = next(l for l in cab if l.startswith("* Dated"))
    medicao = next(l for l in cab if l.startswith("* Measurement")).split(":", 1)[1].strip()
    if data_spl != data_imp or medicao != nome:
        return None
    intervalo = next(float(l.split("//")[0]) for l in cab if "Sample interval" in l)
    return int(round(1.0 / intervalo))


def meta(fonte, nome, papel, canal, descricao, momento="antes"):
    f, n, p, cab = ler_spl(fonte / "SPL" / f"{nome}.txt")
    suav = next(l for l in cab if l.startswith("* Smoothing")).split(":", 1)[1].strip()
    ref = next(l for l in cab if "acoustic timing reference" in l.lower() or "Acoustic reference" in l)
    return {
        "arquivo": f"{nome}.txt", "momento": momento, "papel": papel, "canal": canal, "descricao": descricao,
        # só o verificável: tipo (cabeçalho: referência acústica), taxa (arquivo de impulso pareado), suavização.
        # NÃO preenchidos: id da referência temporal e posição do microfone (ausentes nos dados).
        "referencia_temporal": {"tipo": "acústica (tocada por L, declarada no cabeçalho REW)"},
        "taxa_amostragem": taxa_do_impulso(fonte, nome, cab),
        "suavizacao": "nenhuma" if suav.lower() == "none" else suav,
        "simulado": False,
    }


NORMALIZAR = False  # A2: só remove o separador de milhar da frequência (valores idênticos); ver transformacao


def copiar(origem: Path, destino: Path) -> None:
    if not NORMALIZAR:
        shutil.copy(origem, destino)
        return
    linhas = []
    for linha in origem.read_text(encoding="utf-8").splitlines():
        if linha.startswith("*") or not linha.strip():
            linhas.append(linha)
        else:
            c = linha.split()
            linhas.append(" ".join([c[0].replace(",", ""), *c[1:]]))
    destino.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def montar(fonte: Path, lado: str, k: int, destino: Path) -> Path:
    destino.mkdir(parents=True)
    itens = [(f"{lado} {k}", "via_a", f"{lado}", f"{lado} sozinho (repetição {k})"),
             (f"Sub Only {k}", "via_b", "Sub", f"Subwoofer sozinho (repetição {k})"),
             (f"{lado} + Sub {k}", "soma", f"{lado}+Sub", f"{lado} e Sub juntos (repetição {k})")]
    meds = []
    for nome, papel, canal, desc in itens:
        copiar(fonte / "SPL" / f"{nome}.txt", destino / f"{nome}.txt")
        meds.append(meta(fonte, nome, papel, canal, desc))
    man = {"caso": f"JOEGLONDON-{lado}-{k}", "simulado": False,
           "descricao": "Medições reais de terceiros (joeglondon/speakers-2026-filters); metadados só os verificáveis.",
           "tipo_sessao": "investigacao",
           "configuracao_declarada": {"nome": "Sem configuração declarada (dados de terceiros)", "parametros": []},
           "medicoes": meds}
    (destino / "manifesto.json").write_text(json.dumps(man, indent=1, ensure_ascii=False), encoding="utf-8")
    return destino


def leitura_do_produto(fonte: Path, nome: str, base: Path | None = None) -> dict:
    """Compara o que o leitor do produto entende com a leitura independente (checagem do formato)."""
    f, n, p, _ = ler_spl(fonte / "SPL" / f"{nome}.txt")
    try:
        r = rew_texto.ler((base or fonte / "SPL") / f"{nome}.txt")
    except Exception as e:
        return {"erro": f"{type(e).__name__}: {e}"}
    out = {"pontos_independente": int(f.size), "pontos_produto": int(r.freq_hz.size)}
    if r.freq_hz.size == f.size:
        out["frequencias_iguais"] = bool(np.allclose(r.freq_hz, f))
        out["pontos_com_frequencia_errada"] = int(np.sum(~np.isclose(r.freq_hz, f)))
    out["freq_produto_min_max"] = [float(r.freq_hz.min()), float(r.freq_hz.max())]
    out["freq_produto_crescente"] = bool(np.all(np.diff(r.freq_hz) > 0))
    return out


def rodar(pasta: Path, banco: Path) -> dict:
    s = Servico(Banco(banco))
    out = {"caso": pasta.name, "etapas": []}
    try:
        s.nova_sessao("investigacao")
        imp = s.importar_caso(pasta)
        out["importacao"] = {"medicoes": [{"arquivo": m["arquivo"], "qualidade_basica": m["qualidade"]} for m in imp["medicoes"]]}
        try:
            out["analise"] = s.analisar()
            out["resultado"] = "analisou"
        except ErroDoPercurso as e:
            out["resultado"] = "recusou"
            out["mensagem_recusa"] = str(e)
        sid = s.sessao_id
        out["calculos"] = [{"titulo": r["titulo"], "dados": r["dados"]} for r in s.b.registros(sid, "calculo")]
        out["indicios"] = [{"titulo": r["titulo"], "dados": r["dados"]} for r in s.b.registros(sid, "indicio")]
        out["hipoteses"] = [{"titulo": r["titulo"], "dados": r["dados"]} for r in s.b.registros(sid, "hipotese")]
    except Exception:
        out["resultado"] = "erro_inesperado"
        out["traceback"] = traceback.format_exc()
    finally:
        s.b.fechar()
    return out


def main():
    global NORMALIZAR
    fonte, trab, saida = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    NORMALIZAR = "--normalizar" in sys.argv
    adm = verificar_origem(fonte)
    if trab.exists():
        shutil.rmtree(trab)
    res = {"fonte_commit": adm["commit"], "braco": "A2 (separador de milhar removido; valores idênticos)" if NORMALIZAR else "A1 (arquivos originais)",
           "pares": []}
    for lado in ("L", "R"):
        for k in range(1, 6):
            pasta = montar(fonte, lado, k, trab / f"{lado}-{k}")
            r = rodar(pasta, trab / f"banco-{lado}-{k}")
            r["leitura_produto"] = {n: leitura_do_produto(fonte, n, pasta) for n in (f"{lado} {k}", f"Sub Only {k}", f"{lado} + Sub {k}")}
            res["pares"].append(r)
            print(lado, k, r["resultado"], (r.get("mensagem_recusa") or r.get("analise", {}).get("sugestao") or "")[:200])
    saida.write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
