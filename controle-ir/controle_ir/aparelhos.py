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
    out = {
        "nome": a["nome"], "categoria": a.get("categoria"),
        "perfil": a["perfil"].get("nome"), "tipo_controle": cap["tipo_controle"],
        "comandos": len(a["perfil"].get("comandos", [])),
        # teclas avulsas primeiro, depois o que só o estado completo controla (sem repetir: um perfil misto
        # pode ter "modo" nos dois, como o Gree do quarto com o turbo)
        "parametros": sorted(cap["parametros"]) + [p for p in sorted((cap.get("estado_completo") or {})
                                                                     .get("parametros", {}))
                                                   if p not in cap["parametros"]],
        "macros": sorted(a.get("macros", {})),
    }
    if a.get("observacao"):
        out["observacao"] = a["observacao"]
    return out


# ------------------------------------------------------------- resumo para o Claude
LIMITE_TECLAS_RESUMO = 60
LIMITE_RESUMO = 9000


def _curto(texto, n: int) -> str:
    t = " ".join(str(texto or "").split())
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


def _faixa_txt(f) -> str:
    if isinstance(f, dict):
        if "min" in f and "max" in f:
            return f"{f['min']}–{f['max']}" + (f" (passo {f['passo']})" if f.get("passo") not in (None, 1) else "")
        if f.get("valores"):
            return "|".join(str(v) for v in f["valores"])
    if isinstance(f, (list, tuple)):
        return "|".join(str(v) for v in f)
    return str(f)


def _linhas_aparelho(a: dict, mesmos_codigos: list[str], limite_teclas: int) -> list[str]:
    cap = capacidades(a["perfil"], a.get("faixas"))
    cat = a.get("categoria")
    cat_txt = vocabulario.CATEGORIAS.get(cat, (cat or "sem categoria",))[0]
    tipo = {"estado_completo": "estado completo", "misto": "estado completo + teclas",
            "teclas": "teclas"}.get(cap["tipo_controle"], cap["tipo_controle"])
    linhas = [f"- \"{a['nome']}\" — {cat_txt}; perfil {a['perfil'].get('nome') or '?'}; {tipo}"]
    ec = cap.get("estado_completo")
    if ec:
        partes = [f"{par} {_faixa_txt(v)}" for par, v in ec["parametros"].items()]
        if ec.get("desligar") and "energia" not in cap["parametros"]:
            partes.append("desligar direto")
        linhas.append("  config. completa (definir={...}, um envio): " + "; ".join(partes))
    extras = [c for c in a["perfil"].get("comandos", []) if c.get("adicionado_pelo_usuario") and not c.get("risco")]
    partes = []
    for par, d in cap["parametros"].items():
        if ec and par in ec["parametros"] and "direto" not in d:
            continue
        modos = []
        if d.get("valores"):
            modos.append("|".join(d["valores"]))
        if "alternar" in d:
            modos.append("alterna (precisa do estado)")
        if "mais" in d or "menos" in d:
            modos.append("+/−" + (f" {_faixa_txt(d['faixa'])}" if d.get("faixa") else ""))
        if "ciclo" in d:
            modos.append("próximo")
        if d.get("digitos"):
            modos.append("número 0–9")
        partes.append(f"{par}: {', '.join(modos) or '?'}")
    if partes:
        linhas.append("  parâmetros: " + " · ".join(partes))
    if extras:
        linhas.append("  botões criados pelo usuário (teclas=[chave]): " + "; ".join(
            f"{c['chave']} ({_curto(c.get('rotulo'), 90)})" for c in extras))
    ja = {c["chave"] for c in extras}
    if (cap["parametros"].get("canal") or {}).get("digitos"):
        ja |= {f"numero_{i}" for i in range(10)}  # já descritas como "número 0–9"
    teclas = []
    for t in cap["teclas"]:
        if t["chave"] in ja:
            continue
        rot = t.get("rotulo") or ""
        mesma = normalizar(rot) == normalizar(t["chave"].replace("_", " "))
        teclas.append(t["chave"] if not rot or mesma else f"{t['chave']} ({_curto(rot, 60)})")
    if teclas:
        extra = len(teclas) - limite_teclas
        txt = ", ".join(teclas[:limite_teclas])
        if extra > 0:
            txt += f", … (+{extra}: veja opcoes)"
        linhas.append("  teclas=[chave]: " + txt)
    macros = a.get("macros") or {}
    if macros:
        linhas.append("  macros: " + "; ".join(
            f"{k}" + (f" ({_curto(m.get('descricao'), 90)})" if m.get("descricao") else "") for k, m in macros.items()))
    if mesmos_codigos:
        linhas.append(f"  mesmos códigos de: {', '.join(mesmos_codigos)} — um envio pode acionar os dois se "
                      "estiverem ao alcance")
    if a.get("observacao"):
        linhas.append(f"  observação: {_curto(a['observacao'], 400)}")
    return linhas


def resumo_compacto(aparelhos: list[dict], limite: int) -> str:
    """Versão curta para caber no trecho das instruções que o cliente lê: todos os nomes SEMPRE aparecem.
    Nível 1: nome, categoria, valores da configuração completa e parâmetros; nível 2: só os nomes."""
    if not aparelhos:
        return resumo_para_instrucoes(aparelhos)
    cab = (f"Aparelhos salvos ({len(aparelhos)}; use o nome exato entre aspas; definir={{parâmetro: valor}}, "
           "ajustar={parâmetro: passos}; teclas e macros em opcoes):")
    linhas = []
    for a in sorted(aparelhos, key=lambda x: normalizar(x["nome"])):
        try:
            completas = _linhas_aparelho(a, [], 0)
            manter = [l.replace("config. completa (definir={...}, um envio): ", "definir: ")
                      for l in completas[1:] if l.lstrip().startswith(("config.", "parâmetros"))]
            extras = [c for c in a["perfil"].get("comandos", [])
                      if c.get("adicionado_pelo_usuario") and not c.get("risco")]
            if extras:  # botões que o usuário criou (ex.: visor do ar): chave + rótulo curto
                manter.append("  teclas=[chave] criadas por você: " + "; ".join(
                    f"{c['chave']} ({str(c.get('rotulo') or '').split(' (')[0][:30]})" for c in extras))
            if a.get("macros"):
                manter.append("  macros: " + "; ".join(a["macros"]))
            linhas.append("\n".join([completas[0]] + [_curto(l, 200) for l in manter]))
        except (KeyError, TypeError, ValueError, AttributeError):
            linhas.append(f"- \"{a.get('nome')}\" — use opcoes")
    texto = cab + "\n" + "\n".join(linhas)
    if len(texto) <= limite:
        return texto
    return (f"Aparelhos salvos ({len(aparelhos)}; nome exato entre aspas; valores aceitos em opcoes): "
            + "; ".join(f"\"{a.get('nome')}\"" for a in sorted(aparelhos, key=lambda x: normalizar(x["nome"]))))


def resumo_para_instrucoes(aparelhos: list[dict], limite_teclas: int = LIMITE_TECLAS_RESUMO,
                           limite: int = LIMITE_RESUMO) -> str:
    """Texto compacto com os aparelhos salvos, para as instruções do servidor MCP.

    Lista, por aparelho, o nome exato, os valores aceitos (configuração completa
    e parâmetros), as teclas avulsas, as macros, os aparelhos que compartilham
    os mesmos códigos e a observação do usuário. Não inclui o último estado,
    que muda a cada envio e ficaria velho durante a conversa."""
    if not aparelhos:
        return ("Aparelhos salvos: nenhum ainda. Para cadastrar, use buscar (descoberta por testes) e "
                "salvar_aparelho.")
    por_perfil: dict[str, list[str]] = {}
    for a in aparelhos:
        chave = (a.get("perfil") or {}).get("chave")
        if chave and not str(chave).startswith("usuario:"):
            por_perfil.setdefault(chave, []).append(a["nome"])
    blocos = []
    for a in sorted(aparelhos, key=lambda x: normalizar(x["nome"])):
        chave = (a.get("perfil") or {}).get("chave")
        mesmos = [n for n in por_perfil.get(chave, []) if n != a["nome"]]
        try:
            blocos.append("\n".join(_linhas_aparelho(a, mesmos, limite_teclas)))
        except (KeyError, TypeError, ValueError, AttributeError):
            blocos.append(f"- \"{a.get('nome')}\" — use opcoes para ver as capacidades")
    cab = (f"Aparelhos salvos ({len(aparelhos)}; resumo gerado ao conectar — use o nome exato entre aspas). "
           "Valores com | vão em definir={parâmetro: valor}; +/− vai em ajustar={parâmetro: passos}; "
           "\"alterna\" só sai sabendo o estado atual; teclas avulsas vão em teclas=[chave]; macros em macro=nome.")
    texto = cab + "\n" + "\n".join(blocos)
    if len(texto) > limite:
        corte = texto.rfind("\n", 0, limite - 80)
        texto = texto[: corte if corte > 0 else limite - 80] + \
            "\n… (resumo cortado por tamanho; use consultar e opcoes para os demais)"
    return texto
