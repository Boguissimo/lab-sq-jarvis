"""Serviço do percurso de uma sessão (JV-V01).

Conduz os cinco passos e monta a cadeia de conhecimento por trás (P1, P13). A interface só chama
estes métodos e mostra o que eles devolvem; nenhum número é calculado fora de ``calculos.py``.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jarvis import calculos, limiares, regras, regras_v1_0, rew_texto
from jarvis.referencia import casos
from jarvis.persistencia import Banco, agora

CRITERIO_ACEITE = {  # provisório (spec do JV-V01, “Limites declarados”)
    "faixa_hz": [1000.0, 10000.0],
    "rms_max_db": 1.0,
    "max_abs_db": 2.0,
    "aumento_vale_min_db": 10.0,
    "vale_persiste_abaixo_db": 3.0,
    "provisorio": True,
}

PROCEDIMENTO_SEG08 = [
    "Reduza o volume antes de mexer em qualquer coisa.",
    "Pare o sinal (pausa na música ou no gerador) antes de aplicar a alteração.",
]
RETOMADA_SEG08 = "Retome o volume aos poucos até o nível de medição declarado."

# @@T217 [FR-205] Recusa de fase sem referência temporal declarada compatível
AVISO_REFERENCIA = (
    "Sem referência temporal declarada compatível ({}): a fase entre as vias e a soma prevista não foram "
    "calculadas, nem o atraso. Só a magnitude e a soma de potências foram analisadas. Para comparar fase, meça "
    "todas as vias com a mesma referência temporal (loopback ou referência acústica), a mesma taxa de "
    "amostragem e a mesma posição de microfone, e declare esses dados.")

ORIGENS_PERCEPCAO = ("não aplicável", "simulada", "real")
AVISO_SIMULADO = ("Demonstração com dados simulados. As explicações vêm de regras implementadas, "
                  "não de IA, e não servem para orientar ajustes reais no carro.")


class ErroDoPercurso(Exception):
    """Ação fora de ordem ou impossível; a mensagem é para o usuário."""


def _fmt(x: float, casas: int = 1) -> str:
    if abs(x) < 0.5 * 10 ** -casas:
        x = 0.0  # evita “−0,0”
    return f"{x:.{casas}f}".replace(".", ",").replace("-", "−")


class Servico:
    def __init__(self, banco: Banco):
        self.b = banco
        self.sessao_id: int | None = None

    # ------------------------------------------------------------ utilidades
    def _exigir_sessao(self) -> int:
        if self.sessao_id is None:
            raise ErroDoPercurso("Comece ou abra uma sessão primeiro.")
        if self.b.sessao(self.sessao_id)["estado"] == "encerrada":
            raise ErroDoPercurso("Esta sessão já foi encerrada; ela pode ser consultada, não alterada.")
        return self.sessao_id

    def _ultimo(self, tipo: str, filtro=lambda d: True) -> dict | None:
        regs = [r for r in self.b.registros(self.sessao_id, tipo) if filtro(r["dados"])]
        return regs[-1] if regs else None

    def _calculo(self, nome: str) -> dict | None:
        return self._ultimo("calculo", lambda d: d.get("nome") == nome)

    # @@T218 [FR-207] Todas as medições de um papel e momento, não só a última (E3)
    def _medicoes(self, papel: str, momento: str = "antes") -> list[dict]:
        return [m for m in self.b.registros(self.sessao_id, "medicao")
                if m["dados"].get("papel") == papel and m["dados"].get("momento") == momento]

    def _registro_calculo(self, cid: str) -> dict:
        return next(r for r in self.b.registros(self.sessao_id, "calculo") if r["id"] == cid)

    def _medicao(self, papel: str, momento: str = "antes") -> dict | None:
        return self._ultimo("medicao", lambda d: d.get("papel") == papel and d.get("momento") == momento)

    def _resposta(self, medicao: dict) -> rew_texto.RespostaFrequencia:
        sha = medicao["dados"]["sha256"]
        if not self.b.verificar_original(sha):
            raise ErroDoPercurso(f"O arquivo original da medição {medicao['id']} não confere com o "
                                 "registrado. Ele pode ter sido alterado fora do programa.")
        return rew_texto.ler(self.b.caminho_original(sha))

    # @@T209 [INV-211] Todo cálculo grava entradas_sha256 (ADR-210)
    @staticmethod
    def _sha_entrada(entrada: dict) -> str:
        """Hash do arquivo, para medição; SHA-256 do JSON canônico de ``dados``, para os demais."""
        dados = entrada["dados"]
        if entrada["id"].startswith("M-") and dados.get("sha256"):
            return dados["sha256"]
        canonico = json.dumps(dados, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(canonico.encode("utf-8")).hexdigest()

    def _registrar_calculo(self, nome: str, titulo: str, resultado: dict, entradas: list[dict],
                           parametros: dict | None = None, limiares: dict | None = None) -> str:
        dados = {
            "nome": nome,
            "versao": calculos.VERSOES.get(nome, regras.VERSAO),
            "parametros": parametros or {},
            "limiares": limiares or {},
            "entradas": [e["id"] for e in entradas],
            "entradas_sha256": {e["id"]: self._sha_entrada(e) for e in entradas},
            "resultado": resultado,
        }
        return self.b.novo_registro(self.sessao_id, "calculo", titulo, dados,
                                    origens=[(e["id"], "entrada") for e in entradas])

    # ------------------------------------------------------------ passo 1
    def nova_sessao(self, modo: str = "investigacao") -> int:
        if modo == "calibracao":
            raise ErroDoPercurso("O modo calibração chega no incremento JV-V04. "
                                 "Neste incremento, use a investigação de queixa.")
        self.sessao_id = self.b.nova_sessao(modo, None)
        self.b.diario(self.sessao_id, "sessao", f"Sessão aberta no modo {modo}")
        return self.sessao_id

    def registrar_percepcao(self, momento: str, origem: str, descricao: str = "") -> str:
        sid = self._exigir_sessao()
        if origem not in ORIGENS_PERCEPCAO:
            raise ErroDoPercurso("Origem da percepção inválida.")
        if origem != "não aplicável" and not descricao.strip():
            raise ErroDoPercurso("Descreva a percepção ou marque “não aplicável”.")
        texto = descricao.strip() or "Não aplicável: caso simulado, sem escuta."
        rid = self.b.novo_registro(sid, "percepcao", f"Percepção {momento} ({origem})",
                                   {"momento": momento, "origem": origem, "descricao": texto},
                                   autor="usuário")
        self.b.diario(sid, "percepcao", f"Percepção {momento} registrada ({origem})")
        return rid

    # ------------------------------------------------------------ passo 2
    def importar_caso(self, pasta: str | Path) -> dict:
        sid = self._exigir_sessao()
        pasta = Path(pasta)
        try:
            manifesto = json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))
        except (OSError, ValueError) as erro:
            raise ErroDoPercurso("Esta pasta não tem um caso de referência válido "
                                 "(falta o arquivo manifesto.json).") from erro
        if self.b.registros(sid, "medicao"):
            raise ErroDoPercurso("As medições desta sessão já foram importadas.")

        prov = self._proveniencia(pasta, manifesto)
        importadas = []
        for meta in [m for m in manifesto["medicoes"] if m["momento"] == "antes"]:
            importadas.append(self._importar_medicao(pasta / meta["arquivo"], {**meta, "proveniencia": prov},
                                                     str(pasta)))

        conf = manifesto["configuracao_declarada"]
        origem = "caso simulado" if manifesto.get("simulado") else "declarado"
        self.b.nova_configuracao(sid, conf["nome"], "declarada",
                                 [{**p, "origem": origem} for p in conf["parametros"]])
        self.b.atualizar_sessao(sid, caso=manifesto["caso"], passo_atual=3)
        self.b.diario(sid, "importacao", f"Caso {manifesto['caso']} importado ({len(importadas)} medições)")
        return {"caso": manifesto["caso"], "simulado": manifesto.get("simulado", False),
                "descricao": manifesto.get("descricao", ""), "medicoes": importadas}

    # @@T216 [INV-214] Proveniência de catálogo conferida por hash (antecipada da JV-T218)
    @staticmethod
    def _proveniencia(pasta: Path, manifesto: dict) -> dict:
        """Confere se a pasta tem exatamente os arquivos que o catálogo gera para o caso declarado."""
        from jarvis.persistencia import sha256_de
        arquivos = ["manifesto.json"] + [m["arquivo"] for m in manifesto.get("medicoes", [])]
        try:
            shas = {a: sha256_de(pasta / a) for a in arquivos}
        except OSError:
            return {"catalogo": False, "caso": manifesto.get("caso"), "motivo": "arquivo do caso ausente"}
        return casos.proveniencia(manifesto.get("caso"), shas)

    @staticmethod
    def _suavizacao(dados: dict) -> str | None:
        """Suavização declarada; ausente vale "nenhuma" só em caso do catálogo com proveniência (INV-214)."""
        if dados.get("suavizacao") is not None:
            return dados["suavizacao"]
        return "nenhuma" if (dados.get("proveniencia") or {}).get("catalogo") else None

    def _importar_medicao(self, arquivo: Path, meta: dict, pasta_origem: str) -> dict:
        resposta = rew_texto.ler(arquivo)  # erro de formato sobe com mensagem simples
        sha = self.b.guardar_original(arquivo, "resposta em frequência (texto)")
        dados = {"sha256": sha, "arquivo": arquivo.name, "pasta_origem": pasta_origem,
                 **{k: v for k, v in meta.items() if k != "arquivo"}}
        mid = self.b.novo_registro(self.sessao_id, "medicao", meta.get("descricao", arquivo.name),
                                   dados, autor="usuário")
        med = {"id": mid, "dados": dados}
        qualidade = calculos.qualidade_basica(resposta)
        cid = self._registrar_calculo("qualidade_basica", f"Qualidade de {mid}", qualidade, [med])
        return {"id": mid, "arquivo": arquivo.name, "descricao": meta.get("descricao", ""),
                "qualidade": qualidade, "qualidade_id": cid}

    # ------------------------------------------------------------ passo 3
    @staticmethod
    def _conselho_do_portao(itens_falhos: set[str]) -> str:
        """O conselho depende da causa: frequências fora de ordem apontam leitura ruim do arquivo, não medição ruim."""
        if "frequências em ordem crescente" in itens_falhos:
            return (" As frequências do arquivo estão fora de ordem. Isso costuma indicar um arquivo que o Jarvis não "
                    "conseguiu ler direito (ou que está corrompido), e não uma medição ruim: confira se foi exportado "
                    "do REW como texto (frequência, nível e fase) e guarde o arquivo para análise.")
        if "valores numéricos válidos" in itens_falhos:
            return " O arquivo tem valores que não são números válidos; exporte-o de novo do REW como texto."
        return (f" Refaça a medição cobrindo {calculos.FAIXA_MINIMA_HZ[0]:.0f} Hz a "
                f"{calculos.FAIXA_MINIMA_HZ[1]:.0f} Hz com valores válidos.")

    def analisar(self) -> dict:
        sid = self._exigir_sessao()
        if self._calculo("referencia_temporal"):
            raise ErroDoPercurso("A análise desta sessão já foi feita.")
        ma, mb, ms = self._medicao("via_a"), self._medicao("via_b"), self._medicao("soma")
        if not (ma and mb and ms):
            raise ErroDoPercurso("Faltam medições: são necessárias as duas vias e a soma.")
        a, bb, s = self._resposta(ma), self._resposta(mb), self._resposta(ms)
        # @@T202 [FR-203] Portão básico obrigatório (ADR-212, A04)
        reprovadas, itens_falhos = [], set()
        for m, r in ((ma, a), (mb, bb), (ms, s)):
            q = calculos.qualidade_basica(r)
            if not q["aprovada"]:
                falhos = [i["item"] for i in q["itens"] if not i["ok"] and i["item"] != "contém fase"]
                itens_falhos.update(falhos)
                reprovadas.append(f"{m['dados'].get('descricao', m['id'])} ({m['id']}): falhou em {', '.join(falhos)}")
        if reprovadas:
            raise ErroDoPercurso("Não dá para analisar: a verificação básica de qualidade reprovou "
                                 + "; ".join(reprovadas) + "." + self._conselho_do_portao(itens_falhos))
        if not (calculos.mesma_grade(a, bb) and calculos.mesma_grade(a, s)):
            raise ErroDoPercurso("As medições não usam a mesma grade de frequências; "
                                 "exporte-as do REW com a mesma resolução.")
        ids: dict[str, str] = {}

        ref = calculos.referencia_temporal([ma["dados"], mb["dados"], ms["dados"]])
        ids["referencia"] = self._registrar_calculo(
            "referencia_temporal", "Compatibilidade de referência temporal", ref, [ma, mb, ms])

        lim = regras.LIMIARES["sobreposicao_max_diferenca_db"]
        sob = calculos.sobreposicao(a, bb, lim)
        ids["sobreposicao"] = self._registrar_calculo(
            "sobreposicao", "Faixa de sobreposição das vias", sob, [ma, mb], {"max_diferenca_db": lim})

        pot = calculos.soma_potencias(a, bb)
        ids["potencias"] = self._registrar_calculo(
            "soma_potencias", "Soma de energias das vias (sem interferência)", pot, [ma, mb])

        vale = None
        if sob["existe"]:
            vale = calculos.vale_relativo(s.nivel_db.tolist(), pot["nivel_db"], s.freq_hz.tolist(),
                                          sob["indices"])
            ids["vale"] = self._registrar_calculo(
                "vale_relativo", "Soma medida contra soma de energias", vale, [ms],
                {"usa": ids["potencias"]})
            self.b.con.execute("INSERT INTO derivacao VALUES (?, ?, ?)",
                               (ids["potencias"], ids["vale"], "entrada"))
            self.b.con.commit()

        fase = None
        if sob["existe"] and ref["compativel"] and a.tem_fase and bb.tem_fase:
            fase = calculos.diferenca_fase(a, bb, sob["indices"])
            ids["fase"] = self._registrar_calculo(
                "diferenca_fase", "Diferença de fase entre as vias", fase, [ma, mb])

        # @@T216 [FR-202] [FR-204] σ̂ de cada medição usada e vales individuais de cada via
        qualidade = {"medicoes": {}}
        ids_qualidade = {}
        for m, r in ((ma, a), (mb, bb), (ms, s)):
            irr = calculos.irregularidade(r, self._suavizacao(m["dados"]))
            ids_qualidade[m["id"]] = self._registrar_calculo(
                "irregularidade", f"Irregularidade ponto a ponto de {m['id']}", irr, [m],
                {"suavizacao": self._suavizacao(m["dados"])}, irr["limiares"])
            qualidade["medicoes"][m["id"]] = irr
        vales_ind = {}
        for via, m, r in (("via_a", ma, a), ("via_b", mb, bb)):
            vales_ind[via] = calculos.vales_individuais(r)
            ids[f"vales_individuais_{via}"] = self._registrar_calculo(
                "vales_individuais", f"Vales na via isolada ({m['id']})", vales_ind[via], [m],
                limiares=vales_ind[via]["limiares"])

        if fase is not None and not fase["calculavel"]:
            fase = None
        resultado = regras.avaliar(sob, vale, fase, ids, vales_individuais=vales_ind, qualidade=qualidade)
        if not ref["compativel"]:
            resultado["aviso_referencia"] = (
                AVISO_REFERENCIA.format("; ".join(ref["motivos"])))

        indicio_ids = []
        for ind in resultado["indicios"]:
            iid = self.b.novo_registro(sid, "indicio", ind["titulo"],
                                       {**ind, "versao_regras": regras.VERSAO,
                                        "limiares_provisorios": regras.LIMIARES_PROVISORIOS},
                                       origens=[(c, "evidência") for c in ind["calculos"]])
            indicio_ids.append(iid)
        hipotese_ids = [self.b.novo_registro(sid, "hipotese", h["enunciado"], h,
                                             origens=[(i, "apoio") for i in indicio_ids])
                        for h in resultado["hipoteses"]]

        # @@T209 [INV-211] Interpretação gravada: reabrir a sessão não reexecuta as regras (ADR-210)
        usados = [self._registro_calculo(c) for c in [*ids.values(), *ids_qualidade.values()]]
        avaliacao = {
            "versao_regras": regras.VERSAO,
            "portao": resultado["portao"], "falta": resultado.get("falta", []),
            "aviso_qualidade": resultado.get("aviso_qualidade"), "ids_qualidade": ids_qualidade,
            "sugestao": resultado["sugestao"], "motivo": resultado["motivo"],
            "hipoteses_ordem": hipotese_ids, "indicios": indicio_ids, "ids": ids,
            "aviso_referencia": resultado.get("aviso_referencia"),
        }
        self._registrar_calculo("avaliacao_regras", "Avaliação das regras de diagnóstico", avaliacao, usados,
                                limiares={"versao": regras.VERSAO, "provisorios": regras.LIMIARES_PROVISORIOS,
                                          "limiares": dict(regras.LIMIARES)})
        self.b.atualizar_sessao(sid, passo_atual=3)
        self.b.diario(sid, "analise", f"Análise concluída: {len(indicio_ids)} indício(s), "
                                      f"{len(resultado['hipoteses'])} hipótese(s); sugestão {resultado['sugestao']}")
        return self.estado()["analise"]

    # ------------------------------------------------------------ passo 4
    def propor_teste(self) -> dict:
        sid = self._exigir_sessao()
        analise = self.estado()["analise"]
        if analise is None:
            raise ErroDoPercurso("Analise as medições antes de propor um teste.")
        if analise["sugestao"] != "teste_polaridade":
            raise ErroDoPercurso("Estas medições não indicam um teste de polaridade. "
                                 "Use “nada a alterar” ou “solicitar dados adicionais”.")
        if self._ultimo("recomendacao"):
            return self.estado()["recomendacao"]
        ma, mb, ms = self._medicao("via_a"), self._medicao("via_b"), self._medicao("soma")
        a, bb, s = self._resposta(ma), self._resposta(mb), self._resposta(ms)

        prev = calculos.soma_complexa(a, bb, inverter_b=True)
        f_vale = analise["vale"]["freq_hz"]
        prev["nivel_no_vale_db"] = calculos.nivel_em(prev["freq_hz"], prev["nivel_db"], f_vale)
        prev_id = self._registrar_calculo("soma_complexa", "Previsão: soma com o tweeter invertido",
                                          prev, [ma, mb], {"inverter_b": True})

        configs = self.b.configuracoes(sid)
        anterior = next((p for p in configs[-1]["parametros"]
                         if p["canal"] == "tweeter_esq" and p["parametro"] == "polaridade"), None)
        para = "180°" if (anterior and anterior["valor"] == "0°") else "0°"
        receita = PROCEDIMENTO_SEG08 + [
            f"No PC-Tool, no canal do tweeter esquerdo, mude a polaridade de "
            f"{anterior['valor'] if anterior else 'atual'} para {para}. Não mude mais nada.",
            "Envie a configuração ao DSP e salve o ajuste com um nome novo.",
            RETOMADA_SEG08,
            "Meça de novo médio e tweeter juntos, na mesma posição e com a mesma referência temporal.",
        ]
        if anterior:
            inversa = PROCEDIMENTO_SEG08 + [
                f"No PC-Tool, no canal do tweeter esquerdo, volte a polaridade de {para} para "
                f"{anterior['valor']}.", "Envie ao DSP.", RETOMADA_SEG08]
            reversao = {"garantida": True, "receita_inversa": inversa,
                        "base": f"valor anterior registrado: {anterior['valor']} (origem: {anterior['origem']})"}
        else:
            reversao = {"garantida": False, "receita_inversa": None,
                        "base": "Reversão não garantida: o valor anterior da polaridade do tweeter não "
                                "está registrado."}
        h1 = self._ultimo("hipotese", lambda d: d.get("posicao") == 1)
        dados = {
            "tipo_intervencao": "teste de diagnóstico",
            "variavel": {"canal": "tweeter_esq", "parametro": "polaridade",
                         "de": anterior["valor"] if anterior else "desconhecido", "para": para},
            "hipotese": h1["id"],
            "previsao": prev_id,
            "previsao_resumo": (
                f"Com o tweeter invertido, a soma prevista em {_fmt(f_vale, 0)} Hz passa de "
                f"{_fmt(analise['vale']['soma_no_vale_db'])} dB para {_fmt(prev['nivel_no_vale_db'])} dB "
                f"[{prev_id}]."),
            "criterio": CRITERIO_ACEITE,
            "seguranca": {
                "classe": "não sensível",
                "motivo": "Polaridade não muda a potência elétrica, a excursão, a frequência de corte "
                          "nem o ganho de nenhum alto-falante (regras de segurança, seção 1).",
                "regras": [
                    {"regra": "SEG-08", "resultado": "aplicada: a receita começa com volume baixo e sinal parado"},
                    {"regra": "SEG-11", "resultado": "você aplica a alteração no PC-Tool; o Jarvis não escreve no DSP"},
                ],
            },
            "receita": receita,
            "reversao": reversao,
            "previsao_registrada_em": agora(),
        }
        rid = self.b.novo_registro(sid, "recomendacao",
                                   f"Teste: polaridade do tweeter esquerdo {dados['variavel']['de']} → {para}",
                                   dados, origens=[(h1["id"], "hipótese testada"), (prev_id, "previsão")])
        self.b.atualizar_sessao(sid, passo_atual=4)
        self.b.diario(sid, "recomendacao", f"Teste proposto ({rid}) com previsão {prev_id}")
        return self.estado()["recomendacao"]

    def registrar_aplicacao(self) -> str:
        sid = self._exigir_sessao()
        rec = self._ultimo("recomendacao")
        if rec is None:
            raise ErroDoPercurso("Não há teste proposto para registrar.")
        if self._ultimo("experimento"):
            raise ErroDoPercurso("O teste desta sessão já foi registrado.")
        percepcao = self._ultimo("percepcao", lambda d: d["momento"] == "antes")
        if percepcao is None:
            raise ErroDoPercurso("Registre a percepção “antes” (ou marque “não aplicável”) "
                                 "antes de aplicar o teste.")
        v = rec["dados"]["variavel"]
        xid = self.b.novo_registro(
            sid, "experimento", rec["titulo"],
            {"tipo_intervencao": "teste de diagnóstico", "variavel": v,
             "aplicado_em": agora(), "aplicacao": "declarada pelo usuário",
             "simulado": True},
            autor="usuário", origens=[(rec["id"], "recomendação"), (percepcao["id"], "percepção antes")])
        anterior = self.b.configuracoes(sid)[-1]
        params = [dict(p) for p in anterior["parametros"]]
        for p in params:
            if p["canal"] == v["canal"] and p["parametro"] == v["parametro"]:
                p["valor"], p["origem"] = v["para"], "declarado"
        self.b.nova_configuracao(sid, f"Após o teste {xid} (declarada)", "declarada", params,
                                 anterior=anterior["id"])
        self.b.atualizar_sessao(sid, passo_atual=5)
        self.b.diario(sid, "experimento", f"Aplicação do teste declarada ({xid})")
        return xid

    # ------------------------------------------------------------ passo 5
    def importar_depois(self, caminho: str | Path | None = None) -> dict:
        sid = self._exigir_sessao()
        exp = self._ultimo("experimento")
        rec = self._ultimo("recomendacao")
        if exp is None or rec is None or not rec["dados"].get("previsao_registrada_em"):
            raise ErroDoPercurso("A medição “depois” só pode entrar depois de o teste, com a previsão, "
                                 "estar registrado.")
        if self._medicao("soma", "depois"):
            raise ErroDoPercurso("A medição “depois” desta sessão já foi importada.")
        ms = self._medicao("soma")
        pasta = Path(ms["dados"]["pasta_origem"])
        meta = None
        if caminho is None:
            manifesto = json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))
            meta = next(m for m in manifesto["medicoes"] if m["momento"] == "depois")
            caminho = pasta / meta["arquivo"]
        caminho = Path(caminho)
        if meta is None:
            meta = {"momento": "depois", "papel": "soma", "canal": ms["dados"].get("canal"),
                    "descricao": f"Soma depois do teste ({caminho.name})",
                    "referencia_temporal": {"tipo": "nenhuma"}}
        prov_antes = ms["dados"].get("proveniencia") or {"catalogo": False}
        mesma_pasta = caminho.parent.resolve() == pasta.resolve()
        info = self._importar_medicao(caminho, {**meta, "proveniencia": prov_antes if mesma_pasta else
                                                {"catalogo": False, "motivo": "arquivo fora da pasta do caso"}},
                                      str(caminho.parent))
        recusadas = []
        if meta.get("arquivo") and mesma_pasta:  # vias individuais "depois" declaradas no manifesto
            manifesto = json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))
            for mv in manifesto["medicoes"]:
                if mv["momento"] == "depois" and mv.get("papel") in ("via_a", "via_b"):
                    try:
                        self.importar_via_depois(pasta / mv["arquivo"], mv)
                    except ErroDoPercurso as erro:
                        recusadas.append({"arquivo": mv["arquivo"], "motivo": str(erro)})
        conf_depois_id = None
        if meta.get("arquivo") and mesma_pasta:
            conf = (json.loads((pasta / "manifesto.json").read_text(encoding="utf-8")).get("depois") or {}) \
                .get("configuracao_declarada")
            if conf:
                anterior = self.b.configuracoes(sid)[-1]
                conf_depois_id = self.b.nova_configuracao(
                    sid, conf["nome"], "declarada", [{**p, "origem": "declarado"} for p in conf["parametros"]],
                    anterior=anterior["id"])
        md = self._medicao("soma", "depois")
        depois = self._resposta(md)
        prev = self.b.registros(sid, "calculo")
        prev = next(r for r in prev if r["id"] == rec["dados"]["previsao"])
        comp = calculos.comparacao(prev["dados"]["resultado"], depois, tuple(CRITERIO_ACEITE["faixa_hz"]))
        f_vale = self.estado()["analise"]["vale"]["freq_hz"]
        antes = self._resposta(ms)
        comp["vale_freq_hz"] = f_vale
        comp["nivel_vale_antes_db"] = calculos.nivel_em(antes.freq_hz.tolist(), antes.nivel_db.tolist(), f_vale)
        comp["nivel_vale_depois_db"] = calculos.nivel_em(depois.freq_hz.tolist(), depois.nivel_db.tolist(), f_vale)
        comp["aumento_vale_db"] = comp["nivel_vale_depois_db"] - comp["nivel_vale_antes_db"]
        comp["qualidade_depois_aprovada"] = info["qualidade"]["aprovada"]
        comp["configuracao_depois_id"] = conf_depois_id
        cid = self._registrar_calculo("comparacao", "Comparação previsto × medido depois", comp,
                                      [prev, md, ms], {"faixa_hz": CRITERIO_ACEITE["faixa_hz"]})
        self.b.diario(sid, "medicao", f"Medição depois importada ({md['id']}); comparação {cid}")
        resultado = self.estado()["comparacao"]
        if recusadas:
            resultado = {**resultado, "recusadas": recusadas}
        return resultado

    # @@T218 [FR-207] Aquisição individual "depois" de uma via; cópia não é repetição (E3)
    def importar_via_depois(self, caminho: str | Path, meta: dict | None = None) -> dict:
        """Importa uma aquisição individual “depois” de uma via (``meta['papel']`` = via_a ou via_b).

        Cada aquisição é uma medição própria. Uma cópia do mesmo arquivo (mesmo SHA-256) ou com o mesmo
        ``aquisicao_id`` de outra já importada é recusada: não conta como repetição.
        """
        from jarvis.persistencia import sha256_de
        sid = self._exigir_sessao()
        rec = self._ultimo("recomendacao")
        if self._ultimo("experimento") is None or rec is None or not rec["dados"].get("previsao_registrada_em"):
            raise ErroDoPercurso("As medições “depois” só podem entrar depois de o teste estar registrado.")
        caminho = Path(caminho)
        meta = dict(meta or {})
        papel = meta.get("papel")
        if papel not in ("via_a", "via_b"):
            raise ErroDoPercurso("Informe a via da medição “depois” (via_a ou via_b).")
        meta["momento"] = "depois"
        sha = sha256_de(caminho)
        anteriores = self._medicoes(papel, "depois")
        if any(m["dados"]["sha256"] == sha for m in anteriores):
            raise ErroDoPercurso(f"{caminho.name} é cópia de uma medição “depois” já importada desta via: "
                                 "cópia não conta como repetição.")
        aq = meta.get("aquisicao_id")
        if aq and any(m["dados"].get("aquisicao_id") == aq for m in anteriores):
            raise ErroDoPercurso(f"A aquisição “{aq}” já foi importada para esta via: a repetição exige "
                                 "outra aquisição, com o microfone retirado e recolocado.")
        meta.setdefault("repeticao", len(anteriores) + 1)
        ms = self._medicao("soma")
        pasta = Path(ms["dados"]["pasta_origem"])
        mesma_pasta = caminho.parent.resolve() == pasta.resolve()
        meta["proveniencia"] = (ms["dados"].get("proveniencia") or {"catalogo": False}) if mesma_pasta else             {"catalogo": False, "motivo": "arquivo fora da pasta do caso"}
        info = self._importar_medicao(caminho, meta, str(caminho.parent))
        self.b.diario(sid, "medicao", f"Medição individual depois importada ({info['id']}, {papel}, "
                                      f"aquisição {meta['repeticao']})")
        return info

    def concluir(self) -> dict:
        sid = self._exigir_sessao()
        exp = self._ultimo("experimento")
        comp = self._calculo("comparacao")
        if comp is None:
            raise ErroDoPercurso("Importe a medição “depois” antes de concluir.")
        if self._ultimo("conclusao"):
            raise ErroDoPercurso("O teste desta sessão já tem veredito.")
        pdepois = self._ultimo("percepcao", lambda d: d["momento"] == "depois")
        if pdepois is None:
            raise ErroDoPercurso("Registre a percepção “depois” (ou marque “não aplicável”).")
        r = comp["dados"]["resultado"]
        c = CRITERIO_ACEITE
        verif = self._verificacao_variavel_unica(exp, r)
        if not r["qualidade_depois_aprovada"]:
            veredito, motivo = "inconclusiva", "A medição “depois” não passou na verificação de qualidade."
        elif r["rms_db"] <= c["rms_max_db"] and r["max_abs_db"] <= c["max_abs_db"] \
                and r["aumento_vale_db"] >= c["aumento_vale_min_db"]:
            veredito = "confirmada"
            motivo = (f"A medição depois ficou a {_fmt(r['rms_db'], 3)} dB (RMS) da previsão entre 1 e 10 kHz "
                      f"(máximo {_fmt(r['max_abs_db'], 3)} dB) e o nível no antigo vale subiu "
                      f"{_fmt(r['aumento_vale_db'])} dB [{comp['id']}].")
        elif r["aumento_vale_db"] < c["vale_persiste_abaixo_db"]:
            veredito = "refutada"
            motivo = (f"O vale continuou: o nível subiu só {_fmt(r['aumento_vale_db'])} dB [{comp['id']}].")
        else:
            veredito = "inconclusiva"
            motivo = (f"O resultado não ficou perto o bastante da previsão (RMS {_fmt(r['rms_db'], 2)} dB, "
                      f"máximo {_fmt(r['max_abs_db'], 2)} dB) [{comp['id']}].")
        veredito, motivo, precedencia = self._precedencia(veredito, motivo, verif)
        incerteza = self._incerteza()
        md = self._medicao("soma", "depois")
        aid = self.b.novo_registro(
            sid, "conclusao", f"Veredito: hipótese {veredito}",
            {"veredito": veredito, "motivo": motivo, "tipo": "conclusão experimental",
             "precedencia_aplicada": precedencia, "verificacao_variavel_unica": verif,
             "incerteza": incerteza["texto"], "incerteza_declarada": incerteza,
             "limite": ("Este resultado vale para o caso simulado. No carro, reflexões, distâncias e a "
                        "resposta real dos alto-falantes mudam o quadro (JV-D025).")},
            origens=[(exp["id"], "experimento"), (comp["id"], "comparação"), (md["id"], "medição depois"),
                     (pdepois["id"], "percepção depois"),
                     *[(cid, "verificação da variável única") for cid in verif["calculos"]]])
        self.b.diario(sid, "conclusao", f"Veredito {veredito} ({aid})")
        return self.estado()["conclusao"]

    # @@T219 [FR-207] [INV-202] Verificação da variável única por via (ADR-208; spec E1/E3)
    def _verificacao_variavel_unica(self, exp: dict, comp: dict) -> dict:
        """(a) configuração declarada "depois" contra a proposta; (b) detector de mudança por via.

        Grava um cálculo ``detector_mudanca`` por via com medição individual "depois". A mudança só é
        **confirmada** quando reproduzida por duas aquisições independentes; mesmo assim, o parâmetro
        alterado não é identificado pela medição.
        """
        sid = self.sessao_id
        variavel = exp["dados"]["variavel"]
        configs = {c["id"]: c for c in self.b.configuracoes(sid)}
        conf_depois_id = comp.get("configuracao_depois_id")
        if conf_depois_id:
            declarada = configs[conf_depois_id]
            proposta = configs[declarada["anterior"]]
            pd = {(p["canal"], p["parametro"]): p["valor"] for p in proposta["parametros"]}
            dd = {(p["canal"], p["parametro"]): p["valor"] for p in declarada["parametros"]}
            diferencas = [{"canal": k[0], "parametro": k[1], "proposto": pd.get(k), "declarado": dd.get(k)}
                          for k in sorted(set(pd) | set(dd)) if pd.get(k) != dd.get(k)]
            situacao_conf = "diferente" if diferencas else "igual"
        else:
            diferencas, situacao_conf = [], "nao_declarada"
        vias, calcs = {}, []
        for via in ("via_a", "via_b"):
            antes = self._medicao(via)
            depois = self._medicoes(via, "depois")
            if not antes or not depois:
                vias[via] = {"resultado": "nao_verificada"}
                continue
            ra = self._resposta(antes)
            sa = calculos.irregularidade(ra, self._suavizacao(antes["dados"]))["sigma_db"]
            faixa = calculos.faixa_util(ra)
            dets = []
            for md in depois:
                rd = self._resposta(md)
                sd = calculos.irregularidade(rd, self._suavizacao(md["dados"]))["sigma_db"]
                cat = bool((antes["dados"].get("proveniencia") or {}).get("catalogo")
                           and (md["dados"].get("proveniencia") or {}).get("catalogo"))
                comparaveis = calculos.condicoes_comparaveis(antes["dados"], md["dados"], catalogo=cat)
                dets.append({"medicao": md["id"],
                             **calculos.detector_mudanca_via(ra, rd, sa, sd, faixa, comparaveis)})
            detectadas = [d for d in dets if d["resultado"] == "mudanca_detectada"]
            reproduzida, rep = False, None
            if len(detectadas) >= 2:
                rep = calculos.repeticao_confirma(detectadas[0], detectadas[1])  # E4: sentido, nível e faixa
                reproduzida = rep["reproduzida"]
            if any(d["resultado"] == "inconclusiva" for d in dets):
                resultado = "verificacao_inconclusiva"
            elif reproduzida:
                resultado = "mudanca_detectada_reproduzida"
            elif detectadas:
                resultado = "mudanca_detectada_indicativa"
            else:
                resultado = "mudanca_nao_detectada"
            faixa_mud = next((d["faixa_mudanca_hz"] for d in detectadas if d.get("faixa_mudanca_hz")), None)
            dados_det = {"via": via, "depois": [d["medicao"] for d in dets], "deteccoes": dets,
                         "reproduzida": reproduzida, "confirmacao": rep,
                         "faixa_compativel": rep["faixa_compativel"] if rep else None,
                         "parametro_identificado": False, "resultado": resultado, "faixa_mudanca_hz": faixa_mud}
            cid = self._registrar_calculo("detector_mudanca", f"Detector de mudança da via ({via})", dados_det,
                                          [antes, *depois], limiares=dets[0]["limiares"])
            calcs.append(cid)
            vias[via] = {"resultado": resultado, "detector": cid, "faixa_mudanca_hz": faixa_mud,
                         "resolucao": dets[0].get("resolucao")}
        verif = {"configuracao": situacao_conf, "diferencas": diferencas, "vias": vias, "calculos": calcs,
                 "variavel": variavel}
        if any(v["resultado"] in ("nao_verificada", "verificacao_inconclusiva") for v in vias.values()):
            verif["aviso"] = "outras alterações não foram verificadas"
        # somas "antes" e "depois" com condições de aquisição comparáveis declaradas (E3)
        ms, mdp = self._medicao("soma"), self._medicao("soma", "depois")
        cat = bool((ms["dados"].get("proveniencia") or {}).get("catalogo")
                   and (mdp["dados"].get("proveniencia") or {}).get("catalogo"))
        verif["somas_comparaveis"] = calculos.condicoes_comparaveis(ms["dados"], mdp["dados"], catalogo=cat)
        q = calculos.irregularidade(self._resposta(mdp), self._suavizacao(mdp["dados"]))
        verif["qualidade_depois"] = {"classificacao": q["classificacao"], "sigma_db": q["sigma_db"]}
        return verif

    # @@T220 [FR-208] Incerteza declarada calculada de σ̂ (spec E1)
    def _incerteza(self) -> dict:
        """Maior σ̂ entre as medições usadas no veredito (vias e somas); não estimável ⇒ "não quantificada"."""
        usadas = [m for m in (self._medicao("via_a"), self._medicao("via_b"), self._medicao("soma"),
                              self._medicao("soma", "depois")) if m]
        sigmas, nao_est = [], []
        for m in usadas:
            q = calculos.irregularidade(self._resposta(m), self._suavizacao(m["dados"]))
            (sigmas.append(q["sigma_db"]) if q["sigma_db"] is not None else nao_est.append(m["id"]))
        if nao_est:
            return {"sigma_max_db": None, "quantificada": False, "nao_estimaveis": nao_est,
                    "texto": "Incerteza não quantificada: ruído não estimável em " + ", ".join(nao_est)
                             + ". Limiares e critério de aceite provisórios."}
        smax = max(sigmas)
        if smax <= 0.05:
            texto = ("Caso simulado e ideal, sem ruído: a incerteza é só a do arredondamento dos arquivos "
                     f"(σ̂ máximo {_fmt(smax, 3)} dB). Limiares e critério de aceite provisórios.")
        else:
            texto = (f"Incerteza declarada: irregularidade ponto a ponto de até {_fmt(smax, 2)} dB (σ̂) nas medições "
                     "usadas; diferenças dessa ordem não são significativas. Limiares e critério de aceite provisórios.")
        return {"sigma_max_db": smax, "quantificada": True, "nao_estimaveis": [], "texto": texto}

    # @@T219 [FR-207] [FR-208] Precedência do veredito do teste (spec E1/E3)
    @staticmethod
    def _precedencia(veredito: str, motivo: str, verif: dict) -> tuple[str, str, int]:
        rotulos = {"via_a": "médio", "via_b": "tweeter"}
        if verif["configuracao"] == "diferente":
            outras = [d for d in verif["diferencas"] if not (d["canal"] == verif["variavel"]["canal"]
                                                             and d["parametro"] == verif["variavel"]["parametro"])]
            if outras:
                lista = "; ".join(f"{d['canal']} {d['parametro']}: proposto {d['proposto'] or '—'}, "
                                  f"declarado {d['declarado'] or '—'}" for d in outras)
                return ("comprometida", "A configuração declarada depois difere da proposta além da variável "
                        f"testada ({lista}). A hipótese não foi confirmada nem refutada: refaça o teste mudando "
                        "só uma variável.", 1)
        qd = verif.get("qualidade_depois", {}).get("classificacao")
        def teto(texto, nivel):
            if veredito == "inconclusiva":
                return veredito, motivo + " " + texto, nivel
            return "inconclusiva", texto, nivel
        if qd in ("reprovada", "nao_estimavel"):
            return teto("A qualidade da medição “depois” não permite concluir (irregularidade "
                        + ("acima do limite" if qd == "reprovada" else "não estimável") + "): no máximo inconclusiva.", 2)
        tipo_sem_magnitude = verif["variavel"].get("parametro") in ("polaridade", "atraso")
        reproduzidas = [v for v, d in verif["vias"].items() if d["resultado"] == "mudanca_detectada_reproduzida"]
        if reproduzidas and tipo_sem_magnitude:
            v = reproduzidas[0]
            fx = verif["vias"][v].get("faixa_mudanca_hz")
            faixa = f"{_fmt(fx[0], 0)} Hz a {_fmt(fx[1], 0)} Hz" if fx else "faixa útil"
            return ("comprometida", f"Mudança reproduzida no {rotulos[v]}, na faixa {faixa}; a medição não identifica "
                    "a causa e não comprova alteração no DSP (a causa pode ser acústica ou de aquisição). A variável testada não muda a magnitude da via isolada, então ela "
                    "não explica a mudança, e o teste não isola a variável: refaça o teste mudando só uma variável.", 3)
        if any(d["resultado"] == "mudanca_detectada_indicativa" for d in verif["vias"].values()):
            return teto("Mudança suspeita numa só aquisição “depois” (pode ser reposicionamento ou ruído; nenhuma alteração do DSP "
                        "é afirmada); repita a medição individual “depois” (retire e recoloque o microfone na mesma "
                        "posição).", 3)
        if not verif.get("somas_comparaveis", {}).get("ok", True):
            return teto("Melhora observada, sem confirmação causal: as somas “antes” e “depois” não têm "
                        "condições de aquisição comparáveis declaradas (posição, ganho de entrada, referência de nível).", 3)
        return veredito, motivo, 4

    def decidir(self, escolha: str) -> dict:
        sid = self._exigir_sessao()
        concl = self._ultimo("conclusao")
        if concl is None:
            raise ErroDoPercurso("Conclua o teste antes de decidir.")
        if escolha not in ("manter", "reverter"):
            raise ErroDoPercurso("Escolha manter ou reverter.")
        rec = self._ultimo("recomendacao")
        dados = {"escolha": escolha, "sem_intervencao": False}
        if escolha == "reverter":
            reversao = rec["dados"]["reversao"]
            dados["reversao"] = reversao
            if reversao["garantida"]:
                atual = self.b.configuracoes(sid)[-1]
                original = self.b.configuracoes(sid)[0]
                self.b.nova_configuracao(sid, "Revertida ao ajuste anterior (declarada)", "declarada",
                                         [{**p, "origem": "declarado"} for p in original["parametros"]],
                                         anterior=atual["id"])
        did = self.b.novo_registro(sid, "decisao",
                                   "Manter a alteração" if escolha == "manter" else "Reverter a alteração",
                                   dados, autor="usuário", origens=[(concl["id"], "conclusão")])
        self._encerrar(f"decisão {did}: {escolha}")
        return {"id": did, **dados}

    def decidir_sem_intervencao(self, tipo: str, fundamentacao: str) -> dict:
        sid = self._exigir_sessao()
        if tipo not in ("nada_a_alterar", "solicitar_dados"):
            raise ErroDoPercurso("Tipo de decisão inválido.")
        if not fundamentacao.strip():
            raise ErroDoPercurso("Escreva a fundamentação da decisão.")
        if self._ultimo("experimento"):
            raise ErroDoPercurso("Já existe um teste registrado nesta sessão; conclua-o.")
        apoio = (self.b.registros(sid, "hipotese") or self.b.registros(sid, "indicio")
                 or [r for r in self.b.registros(sid, "calculo")])
        dados = {"sem_intervencao": True, "tipo": tipo, "fundamentacao": fundamentacao.strip(),
                 "avaliacao": "" if apoio else "Decisão tomada antes de qualquer análise registrada."}
        titulo = "Nada a alterar" if tipo == "nada_a_alterar" else "Solicitar dados adicionais"
        did = self.b.novo_registro(sid, "decisao", titulo, dados, autor="usuário",
                                   origens=[(r["id"], "sustentação") for r in apoio])
        self._encerrar(f"decisão {did}: {titulo.lower()}")
        return {"id": did, **dados}

    def _encerrar(self, encerramento: str) -> None:
        sid = self.sessao_id
        self.b.atualizar_sessao(sid, estado="encerrada", encerramento=encerramento,
                                resumo=self.resumo(), passo_atual=5)
        self.b.diario(sid, "sessao", f"Sessão encerrada: {encerramento}")

    # ------------------------------------------------------------ histórico
    def listar_sessoes(self) -> list[dict]:
        return [dict(s) for s in self.b.sessoes()]

    def abrir_sessao(self, sessao: int) -> dict:
        if self.b.sessao(sessao) is None:
            raise ErroDoPercurso("Sessão não encontrada.")
        self.sessao_id = sessao
        return self.estado()

    def resumo(self) -> str:
        e = self.estado()
        partes = [f"Sessão {e['sessao']['id']} — {e['sessao']['caso'] or 'sem caso'} (dados simulados)."]
        if e["analise"]:
            partes.append(f"Sugestão das regras: {e['analise']['sugestao'].replace('_', ' ')}.")
        if e["recomendacao"]:
            partes.append(e["recomendacao"]["titulo"] + ".")
        if e["conclusao"]:
            partes.append(f"Veredito: {e['conclusao']['dados']['veredito']}.")
        for d in e["decisoes"]:
            partes.append(f"Decisão: {d['titulo'].lower()}.")
        if e["configuracoes"]:
            partes.append(f"Configuração vigente: {e['configuracoes'][-1]['nome']} "
                          f"(nível: {e['configuracoes'][-1]['nivel']}).")
        return " ".join(partes)

    def estado(self) -> dict:
        sid = self.sessao_id
        sessao = dict(self.b.sessao(sid))
        medicoes = self.b.registros(sid, "medicao")
        calcs = {r["dados"]["nome"]: r for r in self.b.registros(sid, "calculo")
                 if r["dados"]["nome"] != "qualidade_basica"}
        qualidades = {r["dados"]["entradas"][0]: r for r in self.b.registros(sid, "calculo")
                      if r["dados"]["nome"] == "qualidade_basica"}
        indicios = self.b.registros(sid, "indicio")
        hipoteses = self.b.registros(sid, "hipotese")
        analise = None
        if "referencia_temporal" in calcs:
            vale = calcs.get("vale_relativo")
            fase = calcs.get("diferenca_fase")
            if fase and not fase["dados"]["resultado"].get("calculavel", True):
                analise_fase_motivos = fase["dados"]["resultado"]["motivos"]
                fase = None
                ids_sem_fase = True
            else:
                analise_fase_motivos, ids_sem_fase = None, False
            sob = calcs["sobreposicao"]["dados"]["resultado"]
            ids = {k: calcs[n]["id"] for k, n in [("vale", "vale_relativo"), ("fase", "diferenca_fase"),
                                                   ("potencias", "soma_potencias"),
                                                   ("sobreposicao", "sobreposicao")]
                   if n in calcs and not (ids_sem_fase and n == "diferenca_fase")}
            registrada = calcs.get("avaliacao_regras")
            if registrada:
                avaliacao = registrada["dados"]["resultado"]
                ids = avaliacao["ids"]
                origem_interpretacao = f"registrada (regras {avaliacao['versao_regras']})"
            else:  # sessão do V01: reconstruída pelas regras 1.0 congeladas (INV-211)
                avaliacao = regras_v1_0.avaliar(sob, vale["dados"]["resultado"] if vale else None,
                                                fase["dados"]["resultado"] if fase else None, ids)
                origem_interpretacao = "reconstruída pelas regras 1.0"
            ref = calcs["referencia_temporal"]["dados"]["resultado"]
            analise = {
                "sugestao": avaliacao["sugestao"], "motivo": avaliacao["motivo"],
                "referencia": ref, "sobreposicao": sob,
                "vale": vale["dados"]["resultado"] if vale else None,
                "fase": fase["dados"]["resultado"] if fase else None,
                "ids": ids,
                "interpretacao": origem_interpretacao,
                "portao": avaliacao.get("portao"),
                "conclui": (avaliacao.get("portao") or {}).get("conclui", True),
                "falta": avaliacao.get("falta", []),
            }
            # @@T217 [FR-206] "Nada a alterar" com justificativa pré-preenchida e editável
            if avaliacao["sugestao"] == "nada_a_alterar":
                analise["justificativa_sugerida"] = (
                    "Sem indício de problema no cruzamento: " + avaliacao["motivo"]
                    + " Nenhum vale foi encontrado nas vias medidas sozinhas.")
            if avaliacao.get("aviso_qualidade"):
                analise["aviso_qualidade"] = avaliacao["aviso_qualidade"]
            if analise_fase_motivos:
                analise["aviso_fase"] = ("Fase e atraso entre as vias não calculáveis: "
                                         + "; ".join(analise_fase_motivos) + ".")
            if not ref["compativel"]:
                analise["aviso_referencia"] = (
                    AVISO_REFERENCIA.format("; ".join(ref["motivos"])))
        curvas = {}
        for m in medicoes:
            r = self._resposta(m)
            chave = f"{m['dados']['papel']}_{m['dados']['momento']}"
            curvas[chave] = {"freq_hz": r.freq_hz.tolist(), "nivel_db": r.nivel_db.tolist(),
                             "rotulo": m["dados"].get("descricao", m["id"])}
        rec = self._ultimo("recomendacao")
        if rec:
            prev = next(r for r in self.b.registros(sid, "calculo") if r["id"] == rec["dados"]["previsao"])
            curvas["previsao"] = {"freq_hz": prev["dados"]["resultado"]["freq_hz"],
                                  "nivel_db": prev["dados"]["resultado"]["nivel_db"],
                                  "rotulo": "Previsão com o tweeter invertido"}
        comp = calcs.get("comparacao")
        return {
            "aviso": AVISO_SIMULADO,
            "sessao": sessao,
            "medicoes": [{**m, "qualidade": qualidades.get(m["id"], {}).get("dados", {}).get("resultado")}
                         for m in medicoes],
            "curvas": curvas,
            "analise": analise,
            "indicios": indicios,
            "hipoteses": hipoteses,
            "recomendacao": rec,
            "experimento": self._ultimo("experimento"),
            "comparacao": comp,
            "conclusao": self._ultimo("conclusao"),
            "decisoes": self.b.registros(sid, "decisao"),
            "percepcoes": self.b.registros(sid, "percepcao"),
            "configuracoes": self.b.configuracoes(sid),
            "eventos": self.b.eventos(sid),
        }
