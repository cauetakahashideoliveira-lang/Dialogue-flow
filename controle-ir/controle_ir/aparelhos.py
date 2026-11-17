"""Aparelhos salvos e capacidades derivadas dos perfis.

As capacidades nunca são fixas no código: são recalculadas a partir dos
comandos do perfil (tipo, parâmetro, efeitos) e da tabela de estado completo.
Um perfil importado depois da instalação ganha capacidades na mesma hora.
"""
from __future__ import annotations

import copy
import json
import os
import tempfile
import threading
import time
from pathlib import Path

from . import vocabulario
from .vocabulario import normalizar

BINARIOS = {"energia", "mudo", "oscilacao"}


def agora() -> float:
    return round(time.time(), 1)


def hora_legivel(ts: float | None) -> str | None:
    if not ts:
        return None
    return time.strftime("%d/%m %H:%M:%S", time.localtime(ts))


def capacidades(perfil: dict, faixas: dict | None = None, incluir_risco: bool = False) -> dict:
    faixas = faixas or {}
    params: dict[str, dict] = {}
    teclas = []
    comandos = []

    def p(nome):
        return params.setdefault(nome, {"rotulo": vocabulario.PARAMETROS.get(nome, nome.replace("_", " ").title())})

    for c in perfil.get("comandos", []):
        if c.get("risco") and not incluir_risco:
            continue
        tipo = c.get("tipo", "tecla")
        item = {"chave": c["chave"], "rotulo": c.get("rotulo"), "tipo": tipo}
        if c.get("risco"):
            item["risco"] = True
        comandos.append(item)
        if tipo == "definir":
            for par, val in (c.get("efeitos") or {}).items():
                if par == "energia" and len(c.get("efeitos") or {}) > 1:
                    continue  # "frio forte" liga o aparelho, mas não é um comando de energia
                d = p(par)
                d.setdefault("direto", {}).setdefault(str(val), []).append(c["chave"])
        elif tipo == "alternar" and c.get("parametro"):
            p(c["parametro"]).setdefault("alternar", []).append(c["chave"])
        elif tipo == "ajustar" and c.get("parametro"):
            d = p(c["parametro"])
            passo = c.get("passo", 0)
            chave = "mais" if passo > 0 else ("menos" if passo < 0 else "ciclo")
            d.setdefault(chave, []).append(c["chave"])
        else:
            teclas.append(item)
    for nome, d in params.items():
        modos = []
        if "direto" in d:
            d["valores"] = sorted(d["direto"], key=lambda v: (len(v), v))
            modos.append("valor direto")
        if "alternar" in d:
            modos.append("alternância (precisa saber o estado atual)")
        if "mais" in d or "menos" in d:
            modos.append("passos relativos")
        if "ciclo" in d:
            modos.append("ciclo (próximo valor)")
        if nome in faixas:
            d["faixa"] = faixas[nome]
        d["como"] = modos
    numeros = {f"numero_{i}" for i in range(10)}
    if numeros <= {c["chave"] for c in perfil.get("comandos", [])}:
        p("canal").setdefault("como", []).append("número do canal pelas teclas 0–9")
        params["canal"]["digitos"] = True
    out = {"parametros": params, "teclas": teclas, "comandos": comandos,
           "tipo_controle": "teclas"}
    ec = perfil.get("estado_completo")
    if ec:
        out["tipo_controle"] = "estado_completo" if not params or set(params) <= {"energia"} else "misto"
        par = copy.deepcopy(ec.get("parametros", {}))
        if isinstance(par.get("temperatura"), dict):
            par["temperatura"].pop("valores", None)
        out["estado_completo"] = {
            "parametros": par,
            "desligar": bool(ec.get("desligar")),
            "combinacoes": len(ec.get("estados", [])),
            "oscilacao": "oscilacao" in par,
            "explicacao": "Cada transmissão envia modo, temperatura e ventilação juntos. Para mudar um só "
                          "valor, envie o nome do aparelho e o novo valor; os demais vêm do último envio.",
        }
    return out


class ErroAparelho(LookupError):
    pass


class Aparelhos:
    def __init__(self, caminho: str | os.PathLike):
        self.caminho = Path(caminho)
        self.trava = threading.RLock()
        self.dados = {"aparelhos": {}}
        if self.caminho.exists():
            try:
                self.dados = json.loads(self.caminho.read_text())
            except json.JSONDecodeError:
                backup = self.caminho.with_suffix(".corrompido.json")
                self.caminho.rename(backup)
        self.dados.setdefault("aparelhos", {})

    def gravar(self):
        with self.trava:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=str(self.caminho.parent), prefix=".aparelhos")
            with os.fdopen(fd, "w") as f:
                json.dump(self.dados, f, ensure_ascii=False, separators=(",", ":"))
            os.replace(tmp, self.caminho)

    def listar(self) -> list[dict]:
        with self.trava:
            return list(self.dados["aparelhos"].values())

    def obter(self, nome: str) -> dict:
        with self.trava:
            todos = self.dados["aparelhos"]
            if not todos:
                raise ErroAparelho("nenhum aparelho salvo ainda — use buscar e salvar_aparelho")
            n = normalizar(nome)
            ident = vocabulario.slug(nome)
            if ident in todos:
                return todos[ident]
            for a in todos.values():
                if normalizar(a["nome"]) == n:
                    return a
            contem = [a for a in todos.values() if n and (n in normalizar(a["nome"]) or normalizar(a["nome"]) in n)]
            if len(contem) == 1:
                return contem[0]
            palavras = set(n.split()) - {"o", "a", "do", "da", "de", "no", "na"}
            pont = []
            for a in todos.values():
                pa = set(normalizar(a["nome"]).split())
                s = len(palavras & pa)
                if s:
                    pont.append((s, a))
            pont.sort(key=lambda x: -x[0])
            if pont and (len(pont) == 1 or pont[0][0] > pont[1][0]):
                return pont[0][1]
            opcoes = [a["nome"] for a in (contem or [x[1] for x in pont] or todos.values())]
            raise ErroAparelho(f"não encontrei um único aparelho chamado “{nome}”. Opções: {', '.join(opcoes)}")

    def salvar(self, aparelho: dict) -> dict:
        with self.trava:
            self.dados["aparelhos"][aparelho["id"]] = aparelho
            self.gravar()
            return aparelho

    def remover(self, nome: str) -> dict:
        with self.trava:
            a = self.obter(nome)
            del self.dados["aparelhos"][a["id"]]
            self.gravar()
            return a

    def novo(self, nome: str, perfil: dict, categoria: str | None = None, origem: dict | None = None,
             substituir: bool = False) -> dict:
        ident = vocabulario.slug(nome)
        with self.trava:
            if ident in self.dados["aparelhos"] and not substituir:
                raise ErroAparelho(f"já existe um aparelho chamado “{nome}”. Use outro nome ou substituir=true.")
            perfil = copy.deepcopy(perfil)
            for c in perfil.get("comandos", []):
                c.pop("sinal_id", None)
            ap = {
                "id": ident, "nome": nome.strip(),
                "categoria": vocabulario.categoria_canonica(categoria) or perfil.get("categoria"),
                "perfil": perfil, "origem": origem or {}, "faixas": {}, "macros": {},
                "config": {"intervalo_teclas": 0.45, "espera_apos_ligar": 1.2},
                "estado": {"ultimo_envio": {}, "confirmado": {}, "controle_original_em": None,
                           "estado_completo": None},
                "historico": [], "criado": agora(),
            }
            return self.salvar(ap)


def resumo_aparelho(a: dict) -> dict:
    cap = capacidades(a["perfil"], a.get("faixas"))
    return {
        "nome": a["nome"], "categoria": a.get("categoria"),
        "perfil": a["perfil"].get("nome"), "tipo_controle": cap["tipo_controle"],
        "comandos": len(a["perfil"].get("comandos", [])),
        "parametros": sorted(cap["parametros"]) + (sorted(cap["estado_completo"]["parametros"])
                                                   if "estado_completo" in cap else []),
        "macros": sorted(a.get("macros", {})),
    }
