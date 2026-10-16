"""Sorteio cego (compromisso com revelação posterior) da ordem dos estados da sessão N2 no Focus.
Quem aplica as alterações (Fabrício) roda UMA vez antes da sessão: o script grava a tabela SECRETA (estados em ordem + nonce)
e imprime o SHA-256 dela. Envie ao analista SÓ o hash; a tabela é revelada depois que as previsões forem gravadas.
  python n2_sorteio_cego.py sortear [--com-0_10] [--saida n2_tabela_secreta.json]
  python n2_sorteio_cego.py verificar <tabela.json> <sha256>
Não faz parte do produto. Não toca em DSP."""
import argparse, hashlib, json, secrets, sys
from datetime import date
from pathlib import Path

ESTADOS = ["polaridade_B_invertida", "atraso_B_1.00_ms", "atraso_B_0.25_ms", "simulacro_sem_alteracao"]
OPCIONAL = "atraso_B_0.10_ms"


def canonico(tabela: dict) -> bytes:
    return json.dumps(tabela, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(tabela: dict) -> str:
    return hashlib.sha256(canonico(tabela)).hexdigest()


def sortear(com_010: bool, saida: Path):
    estados = ESTADOS + ([OPCIONAL] if com_010 else [])
    sr = secrets.SystemRandom()
    sr.shuffle(estados)
    tabela = {"versao": 1, "data": date.today().isoformat(), "nonce": secrets.token_hex(16), "estados_em_ordem": estados}
    saida.write_text(json.dumps(tabela, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Tabela SECRETA gravada em: {saida}  (NÃO enviar; guardar)")
    print(f"SHA-256 (enviar ao analista ANTES da sessão): {sha256(tabela)}")
    print("\nRoteiro para o operador (cada X é seguido do controle C com o DSP restaurado):")
    for k, e in enumerate(estados, 1):
        print(f"  X{k}: {e}   ->  C{k}: restaurar pelo valor registrado e medir o controle")


def verificar(caminho: Path, esperado: str):
    tabela = json.loads(caminho.read_text(encoding="utf-8"))
    ok = sha256(tabela) == esperado.strip().lower()
    print("CONFERE" if ok else "NÃO CONFERE")
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sortear"); s.add_argument("--com-0_10", action="store_true"); s.add_argument("--saida", default="n2_tabela_secreta.json")
    v = sub.add_parser("verificar"); v.add_argument("tabela"); v.add_argument("sha256")
    a = ap.parse_args()
    if a.cmd == "sortear":
        sortear(a.com_0_10, Path(a.saida))
    else:
        sys.exit(verificar(Path(a.tabela), a.sha256))
