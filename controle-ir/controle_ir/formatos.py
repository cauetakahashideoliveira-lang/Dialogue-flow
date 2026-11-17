"""Importação e exportação de perfis e sinais.

Formatos aceitos na importação (detectados automaticamente):

* arquivo ``.ir`` do Flipper Zero (sinais ``parsed`` e ``raw``);
* JSON do SmartIR (climate, fan, media_player, light);
* JSON de perfil do controle-ir (``"formato": "controle-ir/perfil@1"``);
* Pronto hex (``0000 006D ...``), Broadlink base64 (``JgB...``);
* sinal bruto: ``38000: 9000 4500 560 ...``, listas com sinal (+/−) ou JSON.

Exportação: perfil JSON, ``.ir`` do Flipper e Pronto.
"""
from __future__ import annotations

import json
import re

from . import protocolos, vocabulario
from .sinais import ErroSinal, Sinal

FORMATO_PERFIL = "controle-ir/perfil@1"


class ErroFormato(ValueError):
    pass


# ------------------------------------------------------------- perfis (base)

def comando(nome: str, sinal: dict, termo: vocabulario.Termo | None = None) -> dict:
    t = termo or vocabulario.interpretar(nome)
    c = {"chave": t.chave, "rotulo": t.rotulo, "nome_original": str(nome), "tipo": t.tipo}
    if t.parametro:
        c["parametro"] = t.parametro
    if t.tipo == "ajustar":
        c["passo"] = t.passo
    if t.efeitos:
        c["efeitos"] = t.efeitos_dict()
    if t.risco:
        c["risco"] = True
    c["sinal"] = Sinal(sinal).dados
    return c


def novo_perfil(chave: str, nome: str, categoria=None, marca=None, modelo=None, fonte="usuario",
                licenca="do usuário") -> dict:
    return {"formato": FORMATO_PERFIL, "chave": chave, "nome": nome,
            "categoria": vocabulario.categoria_canonica(categoria) or categoria,
            "marca": marca, "modelo": modelo, "fonte": fonte, "licenca": licenca,
            "comandos": [], "estado_completo": None}


def adicionar_comando(perfil: dict, cmd: dict, indice: dict | None = None) -> dict:
    """Adiciona sem perder duplicatas: a segunda 'Power' vira energia_alternar_2.

    ``indice`` (opcional) acelera importações grandes; é mantido pelo chamador.
    """
    if indice is None:
        indice = indice_comandos(perfil)
    imp = Sinal(cmd["sinal"]).impressao()
    base = cmd["chave"]
    if (base, imp) in indice["pares"]:
        return cmd  # mesma tecla com o mesmo sinal: ignora
    if base in indice["chaves"]:
        n = indice["n"].get(base, 1)
        while True:
            n += 1
            nova = f"{base}_{n}"
            if nova not in indice["chaves"]:
                break
        indice["n"][base] = n
        cmd = dict(cmd, chave=nova, rotulo=f"{cmd['rotulo']} ({n})", base=base)
    indice["chaves"].add(cmd["chave"])
    indice["pares"].add((base, imp))
    perfil["comandos"].append(cmd)
    return cmd


def indice_comandos(perfil: dict) -> dict:
    ind = {"chaves": set(), "pares": set(), "n": {}}
    for c in perfil["comandos"]:
        ind["chaves"].add(c["chave"])
        ind["pares"].add((c.get("base", c["chave"]), Sinal(c["sinal"]).impressao()))
    return ind


# ---------------------------------------------------------------- Flipper .ir

def _hex_le(texto: str) -> int:
    bs = bytes(int(x, 16) for x in texto.split())
    return int.from_bytes(bs, "little")


def ler_flipper(texto: str, chave="importado", nome=None, categoria=None, marca=None, modelo=None,
                fonte="usuario", licenca="do usuário") -> dict:
    perfil = novo_perfil(chave, nome or chave, categoria, marca, modelo, fonte, licenca)
    blocos, atual = [], {}
    comentarios = []
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha:
            continue
        if linha.startswith("#"):
            if not atual and not blocos:
                c = linha.lstrip("#").strip()
                if c:
                    comentarios.append(c)
            if atual:
                blocos.append(atual)
                atual = {}
            continue
        if ":" not in linha:
            continue
        k, v = linha.split(":", 1)
        k, v = k.strip().lower(), v.strip()
        if k == "name":
            if atual:
                blocos.append(atual)
            atual = {"name": v}
        elif atual is not None:
            atual[k] = v
    if atual:
        blocos.append(atual)
    erros = 0
    indice = indice_comandos(perfil)
    for b in blocos:
        if "name" not in b:
            continue
        try:
            if b.get("type") == "parsed":
                sinal = {"protocolo": b["protocol"], "endereco": _hex_le(b["address"]),
                         "comando": _hex_le(b["command"])}
            elif b.get("type") == "raw":
                vals = [int(x) for x in b["data"].split()]
                sinal = Sinal({"frequencia": int(float(b.get("frequency", 38000))), "pulsos": vals}).compacto()
            else:
                continue
            adicionar_comando(perfil, comando(b["name"], sinal), indice)
        except (KeyError, ValueError, ErroSinal, protocolos.ErroProtocolo):
            erros += 1
    if comentarios and not nome:
        perfil["nome"] = comentarios[0][:80]
    perfil["descartados"] = erros
    if not perfil["comandos"]:
        raise ErroFormato("nenhum sinal válido no arquivo .ir")
    return perfil


def escrever_flipper(perfil: dict) -> str:
    linhas = ["Filetype: IR signals file", "Version: 1", "#", f"# {perfil.get('nome', '')}", "#"]
    for c in perfil.get("comandos", []):
        s = Sinal(c["sinal"])
        nome = c.get("nome_original") or c.get("rotulo") or c["chave"]
        linhas.append(f"name: {nome.replace(' ', '_')}")
        d = s.dados
        if "protocolo" in d:
            na, nc = protocolos.TAMANHOS[d["protocolo"]]
            linhas += ["type: parsed", f"protocol: {d['protocolo']}",
                       "address: " + " ".join(f"{b:02X}" for b in d["endereco"].to_bytes(4, "little")),
                       "command: " + " ".join(f"{b:02X}" for b in d["comando"].to_bytes(4, "little"))]
        else:
            f, p = s.transmissao()
            linhas += ["type: raw", f"frequency: {f}", "duty_cycle: 0.330000", "data: " + " ".join(map(str, p))]
        linhas.append("#")
    return "\n".join(linhas) + "\n"


# ------------------------------------------------------------------- SmartIR

_MODOS_AR = {"cool": "frio", "heat": "calor", "dry": "desumidificar", "fan_only": "ventilar", "fan": "ventilar",
             "heat_cool": "automatico", "auto": "automatico"}
_VENT_AR = {"auto": "automatica", "low": "baixa", "mid": "media", "medium": "media", "med": "media",
            "middle": "media", "high": "alta", "quiet": "silenciosa", "silent": "silenciosa", "turbo": "turbo",
            "powerful": "turbo", "highest": "maxima", "max": "maxima", "lowest": "minima", "min": "minima",
            "mediumhigh": "media_alta", "medium_high": "media_alta", "mediumlow": "media_baixa",
            "medium_low": "media_baixa", "focus": "foco", "diffuse": "difusa"}
_OSC_AR = {"off": "desligada", "stop": "desligada", "static": "desligada", "fixed": "desligada",
           "on": "ligada", "swing": "ligada", "auto": "automatica", "both": "ambas", "vertical": "vertical",
           "horizontal": "horizontal"}


def _traduz(mapa: dict, valor: str) -> str:
    v = str(valor)
    chave = vocabulario.normalizar(v).replace(" ", "_")
    if chave in mapa:
        return mapa[chave]
    m = re.fullmatch(r"level_?(\d+)", chave)
    if m:
        return f"nivel{m.group(1)}"
    return chave


def _sinal_smartir(codigo, controlador: str, codificacao: str) -> dict | None:
    if codigo is None or codigo == "":
        return None
    if isinstance(codigo, list):
        if codigo and isinstance(codigo[0], str):  # lista de códigos enviados em sequência
            codigo = codigo[0]
        else:
            return {"frequencia": 38000, "pulsos": codigo}
    ctrl = (controlador or "").lower()
    enc = (codificacao or "").lower()
    if ctrl == "xiaomi":
        return None  # formato comprimido proprietário
    if enc == "pronto":
        return {"pronto": codigo}
    if enc == "raw":
        nums = [int(x) for x in re.findall(r"-?\d+", str(codigo))]
        return {"frequencia": 38000, "pulsos": nums} if nums else None
    if enc in ("base64", "") or ctrl == "broadlink":
        return {"broadlink": str(codigo)}
    return None


def ler_smartir(dados: dict, tipo: str, chave: str, fonte="smartir", licenca="MIT") -> dict:
    marca = str(dados.get("manufacturer", "")).strip() or None
    modelos = [str(m) for m in dados.get("supportedModels", []) if m]
    modelo = ", ".join(modelos)[:200] or None
    categoria = {"climate": "ar_condicionado", "fan": "ventilador", "media_player": None,
                 "light": "iluminacao"}.get(tipo)
    nome = f"{marca or 'Desconhecido'} {modelos[0] if modelos else ''}".strip()
    perfil = novo_perfil(chave, nome, categoria, marca, modelo, fonte, licenca)
    ctrl, enc = dados.get("supportedController", ""), dados.get("commandsEncoding", "")
    cmds = dados.get("commands") or {}

    def sinal(c):
        try:
            s = _sinal_smartir(c, ctrl, enc)
            if not s:
                return None
            obj = Sinal(s)
            obj.transmissao()  # valida (descarta códigos de RF e corrompidos)
            return obj.dados
        except (ErroSinal, ValueError, TypeError):
            return None

    if tipo == "climate":
        modos = [m for m in cmds if m != "off" and isinstance(cmds[m], dict)]
        tmin, tmax = dados.get("minTemperature", 16), dados.get("maxTemperature", 30)
        passo = dados.get("precision", 1) or 1
        estados = []
        tem_osc = bool(dados.get("swingModes"))
        valores_vent, valores_osc, temps = [], [], set()
        for m in modos:
            for vent, sub in cmds[m].items():
                if not isinstance(sub, dict):
                    continue
                pares = []
                if tem_osc and sub and all(isinstance(x, dict) for x in sub.values()):
                    for osc, temps_d in sub.items():
                        pares.append((osc, temps_d))
                else:
                    pares.append((None, sub))
                for osc, temps_d in pares:
                    for temp, cod in temps_d.items():
                        s = sinal(cod)
                        if not s:
                            continue
                        try:
                            t = float(temp)
                        except ValueError:
                            continue
                        t = int(t) if t.is_integer() else t
                        e = {"modo": _traduz(_MODOS_AR, m), "ventilacao": _traduz(_VENT_AR, vent), "temperatura": t,
                             "sinal": s}
                        if osc is not None:
                            e["oscilacao"] = _traduz(_OSC_AR, osc)
                            if e["oscilacao"] not in valores_osc:
                                valores_osc.append(e["oscilacao"])
                        if e["ventilacao"] not in valores_vent:
                            valores_vent.append(e["ventilacao"])
                        temps.add(t)
                        estados.append(e)
        if not estados:
            raise ErroFormato("perfil SmartIR sem estados utilizáveis")
        params = {"modo": [], "temperatura": {"min": min(temps), "max": max(temps), "passo": passo,
                                              "valores": sorted(temps)},
                  "ventilacao": valores_vent}
        for e in estados:
            if e["modo"] not in params["modo"]:
                params["modo"].append(e["modo"])
        if valores_osc:
            params["oscilacao"] = valores_osc
        perfil["estado_completo"] = {"parametros": params, "desligar": sinal(cmds.get("off")),
                                     "estados": estados, "faixa_declarada": [tmin, tmax]}
        if perfil["estado_completo"]["desligar"]:
            adicionar_comando(perfil, comando("off", perfil["estado_completo"]["desligar"]))
        return perfil

    if tipo == "fan":
        if sinal(cmds.get("off")):
            adicionar_comando(perfil, comando("off", sinal(cmds.get("off"))))
        if sinal(cmds.get("oscillate")):
            adicionar_comando(perfil, comando("oscillate", sinal(cmds.get("oscillate"))))
        velocidades = [str(v) for v in dados.get("speed", [])]
        for direcao, sub in cmds.items():
            if direcao in ("off", "oscillate") or not isinstance(sub, dict):
                continue
            for i, vel in enumerate(velocidades or list(sub)):
                s = sinal(sub.get(vel))
                if not s:
                    continue
                valor = str(i + 1)
                if direcao in ("default", "forward"):
                    t = vocabulario.Termo(f"velocidade_{valor}", f"Velocidade {valor} ({vel})", "definir",
                                          efeitos=(("energia", "ligado"), ("velocidade", valor)), teste=6)
                    adicionar_comando(perfil, comando(vel, s, t))
                else:
                    t = vocabulario.Termo(f"x_{direcao}_{valor}", f"{direcao} velocidade {valor}", "definir",
                                          efeitos=(("energia", "ligado"), ("velocidade", valor),
                                                   ("direcao", direcao)))
                    adicionar_comando(perfil, comando(f"{direcao} {vel}", s, t))
        if not perfil["comandos"]:
            raise ErroFormato("perfil de ventilador vazio")
        return perfil

    for nome_cmd, cod in cmds.items():
        if nome_cmd == "sources" and isinstance(cod, dict):
            for fonte_nome, c2 in cod.items():
                s = sinal(c2)
                if not s:
                    continue
                t = vocabulario.interpretar(f"input {fonte_nome}")
                if not t.chave.startswith("entrada_"):
                    t2 = vocabulario.interpretar(fonte_nome)
                    if t2.chave.startswith("entrada_"):
                        t = t2
                    else:
                        v = vocabulario.slug(fonte_nome)
                        t = vocabulario.Termo(f"entrada_{v}", f"Entrada {fonte_nome}", "definir",
                                              efeitos=(("entrada", v),), teste=1)
                adicionar_comando(perfil, comando(f"source {fonte_nome}", s, t))
            continue
        s = sinal(cod)
        if s:
            adicionar_comando(perfil, comando(nome_cmd, s))
    if not perfil["comandos"]:
        raise ErroFormato("perfil SmartIR vazio")
    return perfil


# ------------------------------------------------------------- sinais soltos

_RE_B64 = re.compile(r"^[A-Za-z0-9+/=\s]{16,}$")


def ler_sinal_texto(texto: str) -> dict:
    """Interpreta um sinal isolado colado pelo usuário."""
    t = texto.strip()
    if not t:
        raise ErroFormato("texto vazio")
    if t.startswith("{") or t.startswith("["):
        try:
            obj = json.loads(t)
        except json.JSONDecodeError as e:
            raise ErroFormato(f"JSON inválido: {e}") from e
        if isinstance(obj, list):
            return Sinal({"frequencia": 38000, "pulsos": obj}).compacto()
        if isinstance(obj, dict):
            return Sinal(obj).compacto()
    if re.fullmatch(r"(?:[0-9A-Fa-f]{4}\s+){5,}[0-9A-Fa-f]{4}", t):
        return Sinal({"pronto": t}).dados
    if _RE_B64.match(t) and not re.fullmatch(r"[\d\s]+", t):
        return Sinal({"broadlink": "".join(t.split())}).dados
    m = re.match(r"^\s*(?:f(?:req(?:uency|uencia)?)?\s*[=:]?\s*)?(\d{5})\s*(?:hz)?\s*[:;,|]\s*(.*)$", t, re.I | re.S)
    freq = 38000
    corpo = t
    if m and 20000 <= int(m.group(1)) <= 60000:
        freq, corpo = int(m.group(1)), m.group(2)
    else:
        fm = re.search(r"frequenc\w*\s*[:=]\s*(\d+)", t, re.I)
        dm = re.search(r"data\s*[:=]\s*([-\d\s,]+)", t, re.I)
        if fm and dm:
            freq, corpo = int(fm.group(1)), dm.group(1)
    nums = [int(x) for x in re.findall(r"[-+]?\d+", corpo)]
    if len(nums) < 3:
        raise ErroFormato("não reconheci o formato do sinal")
    return Sinal({"frequencia": freq, "pulsos": nums}).compacto()


def importar_texto(texto: str, nome=None, categoria=None, marca=None, modelo=None, chave=None) -> dict:
    """Detecta o formato e devolve um perfil (ou um perfil de um comando só)."""
    t = texto.strip()
    chave = chave or f"usuario:{vocabulario.slug(nome or marca or 'importado')}"
    if t.lower().startswith("filetype: ir signals file") or re.search(r"^name:\s*\S+", t, re.M):
        return ler_flipper(t, chave, nome, categoria, marca, modelo)
    if t.startswith("{"):
        try:
            obj = json.loads(t)
        except json.JSONDecodeError:
            obj = None
        if isinstance(obj, dict):
            if obj.get("formato") == FORMATO_PERFIL:
                validar_perfil(obj)
                if nome:
                    obj["nome"] = nome
                obj["chave"] = obj.get("chave") or chave
                return obj
            if "commands" in obj and ("manufacturer" in obj or "supportedController" in obj):
                if "operationModes" in obj:
                    tipo = "climate"
                elif "speed" in obj:
                    tipo = "fan"
                elif any(k in obj["commands"] for k in ("brighten", "dim")):
                    tipo = "light"
                else:
                    tipo = "media_player"
                p = ler_smartir(obj, tipo, chave, fonte="usuario", licenca="do usuário")
                if nome:
                    p["nome"] = nome
                if categoria:
                    p["categoria"] = vocabulario.categoria_canonica(categoria) or categoria
                return p
    sinal = ler_sinal_texto(t)
    perfil = novo_perfil(chave, nome or "Sinal importado", categoria, marca, modelo)
    adicionar_comando(perfil, comando(nome or "sinal importado", sinal))
    return perfil


def validar_perfil(p: dict) -> None:
    if not isinstance(p.get("comandos"), list):
        raise ErroFormato("perfil sem lista de comandos")
    for c in p["comandos"]:
        if "chave" not in c or "sinal" not in c:
            raise ErroFormato("comando sem chave ou sinal")
        c["sinal"] = Sinal(c["sinal"]).dados
        c.setdefault("tipo", "tecla")
        c.setdefault("rotulo", c["chave"])
    ec = p.get("estado_completo")
    if ec:
        for e in ec.get("estados", []):
            e["sinal"] = Sinal(e["sinal"]).dados


def exportar(perfil: dict, formato: str = "json") -> str:
    f = (formato or "json").lower()
    if f in ("flipper", "ir", ".ir"):
        return escrever_flipper(perfil)
    if f == "pronto":
        linhas = []
        for c in perfil.get("comandos", []):
            fr, p = Sinal(c["sinal"]).transmissao()
            linhas.append(f"{c['rotulo']}: {sinais_pronto(fr, p)}")
        return "\n".join(linhas)
    limpo = {k: v for k, v in perfil.items() if k != "descartados"}
    limpo["formato"] = FORMATO_PERFIL
    return json.dumps(limpo, ensure_ascii=False, indent=1)


def sinais_pronto(freq, pulsos):
    from .sinais import pulsos_para_pronto
    return pulsos_para_pronto(freq, pulsos)
