"""Modos do celular: guarda o estado atual, aplica um modo (ex.: reunião = toque no vibrar) e restaura tudo ao sair.

Direto no Android, sem tela:
- toque (normal/vibrar/silencioso): `cmd audio set-ringer-mode` pelo shell do Shizuku (provado no POCO, Android 16);
- volumes por fluxo (ring, notification, music, alarm, system, call): leitura pelo shell (`cmd media_session volume
  --get`) e escrita pelo Termux:API (`termux-volume`); no HyperOS o `--set` do shell é ignorado (provado em 22/11).

Aprende com o uso (~/.controle-ir/modos/aprendido.json): guarda o método que funcionou em cada tipo de ajuste e
as condições (versão do Android, Shizuku); no pedido seguinte usa direto o que já foi confirmado e só revalida se
uma condição mudou. Um método que falhou sob as mesmas condições não é tentado de novo. Cada falha vem com o
teste que separa as causas prováveis (Shizuku parado, comando ausente, sistema recusou, Termux:API ausente).

Entrada (JSON): acao = entrar | sair | alternar | estado | listar | definir | testar | remover | atalho.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("CONTROLE_IR_DIR") or os.path.expanduser("~/.controle-ir")
PREFIXO = os.environ.get("PREFIX") or "/data/data/com.termux/files/usr"

FLUXOS = {"call": 0, "system": 1, "ring": 2, "music": 3, "alarm": 4, "notification": 5}
APELIDOS = {"chamada": "call", "sistema": "system", "toque": "ring", "campainha": "ring", "musica": "music",
            "midia": "music", "alarme": "alarm", "notificacao": "notification", "notificacoes": "notification"}
TOQUES = {"normal": ("NORMAL", 2), "vibrar": ("VIBRATE", 1), "silencioso": ("SILENT", 0)}
DE_RINGER = {v[1]: k for k, v in TOQUES.items()}
# fluxos que o toque afeta: guardados sempre, para a volta deixar tudo como estava
FLUXOS_DO_TOQUE = ("ring", "notification")

PADRAO = {
    "reuniao": {"nome": "Modo reunião", "toque": "vibrar", "volumes": {},
                "descricao": "toque e notificações no vibrar; ao sair volta o toque e os volumes de antes"},
}

METODOS = {"toque": ["shell"], "volume": ["termux", "shell"]}
# sobe quando o jeito de aplicar/conferir muda: o que foi aprendido com o código antigo é revalidado
VERSAO_METODOS = 2


class SemShell(RuntimeError):
    """Shizuku/rish indisponível (condição, não defeito do método)."""


# --------------------------------------------------------------------------- arquivos
def _pasta():
    p = os.path.join(BASE, "modos")
    os.makedirs(p, exist_ok=True)
    return p


def _ler_json(nome, padrao):
    try:
        with open(os.path.join(_pasta(), nome), encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, type(padrao)) else padrao
    except (OSError, ValueError):
        return padrao


def _gravar_json(nome, dados):
    arq = os.path.join(_pasta(), nome)
    tmp = arq + ".novo"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)
    os.replace(tmp, arq)


def modos_definidos():
    d = {k: dict(v, padrao=True) for k, v in PADRAO.items()}
    for k, v in _ler_json("modos.json", {}).items():
        if isinstance(v, dict):
            d[k] = dict(v, padrao=False)
    return d


def _chave(nome):
    import unicodedata
    s = unicodedata.normalize("NFKD", str(nome or "")).encode("ascii", "ignore").decode().lower().strip()
    for p in ("modo ", "modo_"):
        if s.startswith(p):
            s = s[len(p):]
    return "_".join(s.replace("-", " ").split())


def _fluxo(nome):
    n = _chave(nome)
    n = APELIDOS.get(n, n)
    if n not in FLUXOS:
        raise ValueError(f"fluxo de volume desconhecido: {nome} (use {', '.join(FLUXOS)})")
    return n


# --------------------------------------------------------------------------- Android
def _tela():
    """O agente de tela já tem o rish (Shizuku). Dentro do serviço reaproveita o leitor rápido aberto."""
    try:
        from controle_ir.capacidades import modulo_embutido  # dentro do serviço: a mesma instância (leitor aberto)
        from pathlib import Path
        return modulo_embutido(Path(AQUI).parent / "tela", "tela")
    except Exception:  # noqa: BLE001 — fora do serviço (atalho do widget, testes)
        spec = importlib.util.spec_from_file_location("cap_tela_para_modos", os.path.join(AQUI, "..", "tela",
                                                                                         "principal.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m


class Android:
    """Primitivas do aparelho. `shell(cmd, timeout)` → (out, err, rc) e levanta SemShell; `termux(args)` →
    (out, rc) e levanta FileNotFoundError sem o Termux:API. Os testes trocam as duas."""

    def __init__(self, shell=None, termux=None):
        self._shell = shell
        self._termux = termux
        self.chamadas = 0

    def shell(self, cmd, timeout=20):
        self.chamadas += 1
        if self._shell:
            return self._shell(cmd, timeout)
        t = _tela()
        try:
            return t.rish(cmd, timeout=timeout)
        except t.SemShizuku as e:
            raise SemShell(str(e)) from e

    def termux(self, args, timeout=20):
        self.chamadas += 1
        if self._termux:
            return self._termux(args, timeout)
        exe = shutil.which(args[0])
        if not exe:
            raise FileNotFoundError(args[0])
        r = subprocess.run([exe] + list(args[1:]), capture_output=True, text=True, timeout=timeout, check=False)
        return r.stdout, r.returncode

    # leitura -----------------------------------------------------------------------------------
    def ler(self, fluxos):
        """{toque, volumes{fluxo: n}, sdk, via}. Um só comando no shell; sem Shizuku, volumes pelo Termux:API."""
        fluxos = list(dict.fromkeys(fluxos))
        try:
            partes = ["echo R=$(settings get global mode_ringer)", "echo SDK=$(getprop ro.build.version.sdk)"]
            partes += [f"echo V{f}=$(cmd media_session volume --stream {FLUXOS[f]} --get 2>&1 | "
                       "grep -o 'volume is [0-9]*' | grep -o '[0-9]*$')" for f in fluxos]
            out, _err, _rc = self.shell("; ".join(partes), timeout=20)
            kv = dict(l.split("=", 1) for l in out.splitlines() if "=" in l)
            toque = DE_RINGER.get(int(kv["R"])) if kv.get("R", "").strip().isdigit() else None
            vols = {f: int(kv[f"V{f}"]) for f in fluxos if kv.get(f"V{f}", "").strip().isdigit()}
            if toque is not None and len(vols) == len(fluxos):
                return {"toque": toque, "volumes": vols, "sdk": kv.get("SDK", "").strip() or None, "via": "shell"}
        except SemShell:
            pass
        vols = self.volumes_termux()
        return {"toque": None, "volumes": {f: vols[f] for f in fluxos if f in vols}, "sdk": _sdk_local(),
                "via": "termux"}

    def volumes_termux(self):
        out, rc = self.termux(["termux-volume"])
        if rc != 0:
            raise RuntimeError("termux-volume falhou")
        return {s["stream"]: int(s["volume"]) for s in json.loads(out or "[]") if "stream" in s}

    # escrita -----------------------------------------------------------------------------------
    def definir_toque(self, toque):
        """Muda e confere no mesmo comando. Devolve o modo lido depois."""
        nome, n = TOQUES[toque]
        # o Android grava o mode_ringer nas configurações com atraso (0,3 s ainda lia o antigo no POCO, 22/11):
        # relê até ~2,5 s antes de concluir que o sistema recusou
        out, err, rc = self.shell(f"cmd audio set-ringer-mode {nome} 2>&1; for i in 1 2 3 4 5 6 7 8 9 10 11 12; do "
                                  f"r=$(settings get global mode_ringer); [ \"$r\" = \"{n}\" ] && break; sleep 0.2; "
                                  "done; echo R=$r", timeout=15)
        lido = None
        for l in out.splitlines():
            if l.startswith("R=") and l[2:].strip().isdigit():
                lido = DE_RINGER.get(int(l[2:].strip()))
        texto = "\n".join(l for l in (out + "\n" + err).splitlines() if not l.startswith("R=")).strip()
        return lido, texto, rc

    def definir_volume(self, fluxo, valor, metodo):
        if metodo == "termux":
            _out, rc = self.termux(["termux-volume", fluxo, str(int(valor))])
            return rc == 0
        out, err, rc = self.shell(f"cmd media_session volume --stream {FLUXOS[fluxo]} --set {int(valor)}", 15)
        return rc == 0


def _sdk_local():
    try:
        r = subprocess.run(["getprop", "ro.build.version.sdk"], capture_output=True, text=True, timeout=5)
        return r.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


# --------------------------------------------------------------------------- aprendizado
class Memoria:
    """Métodos confirmados e que falharam, por tipo de ajuste, com as condições em que valeram."""

    def __init__(self):
        self.d = _ler_json("aprendido.json", {})
        self.d.setdefault("metodos", {})
        self.d.setdefault("validacoes", {})
        self.d.setdefault("correcoes", [])
        self.notas = []

    def gravar(self):
        _gravar_json("aprendido.json", self.d)

    def ordem(self, tipo, cond):
        """Métodos a tentar: o confirmado sob as mesmas condições primeiro; os que falharam sob as mesmas
        condições ficam de fora; condição diferente → tudo de novo (revalidar)."""
        reg = self.d["metodos"].get(tipo) or {}
        todos = list(METODOS[tipo])
        if reg.get("condicoes") and reg["condicoes"] != cond:
            self.notas.append(f"{tipo}: condição mudou ({reg['condicoes']} → {cond}); revalidando os métodos")
            return todos
        falhos = set((reg.get("falhou") or {}).keys())
        ok = reg.get("ok")
        ordem = ([ok] if ok in todos else []) + [m for m in todos if m != ok and m not in falhos]
        return ordem or todos

    def ok(self, tipo, metodo, cond):
        reg = self.d["metodos"].setdefault(tipo, {})
        if reg.get("condicoes") != cond:
            reg["falhou"] = {}
        reg.update(ok=metodo, condicoes=cond, confirmado_em=time.strftime("%d/%m %H:%M"))
        reg.setdefault("falhou", {}).pop(metodo, None)

    def falhou(self, tipo, metodo, cond, causa):
        reg = self.d["metodos"].setdefault(tipo, {})
        if reg.get("condicoes") != cond:
            reg.update(condicoes=cond, falhou={})
            reg.pop("ok", None)
        reg.setdefault("falhou", {})[metodo] = {"causa": causa, "em": time.strftime("%d/%m %H:%M")}
        if reg.get("ok") == metodo:
            reg.pop("ok", None)


def _cond(leitura, shell_ok):
    return {"android_sdk": leitura.get("sdk"), "shizuku": bool(shell_ok), "versao_metodos": VERSAO_METODOS}


# --------------------------------------------------------------------------- ajustes com diagnóstico
def aplicar_toque(cel, mem, toque, cond, diag):
    """Muda o toque. Falhou → diagnóstico com o teste que separa as causas. Devolve o método ou None."""
    for metodo in mem.ordem("toque", cond):
        if metodo != "shell":
            continue
        try:
            lido, texto, rc = cel.definir_toque(toque)
        except SemShell as e:
            diag.append({"teste": "o Shizuku responde?", "resultado": "não",
                         "conclusao": "Shizuku parado: abra o app Shizuku e toque em Iniciar (condição, não defeito; "
                                      "nada foi marcado como falho)", "detalhe": str(e)[:160]})
            return None
        if lido == toque:
            mem.ok("toque", metodo, cond)
            return metodo
        if rc != 0 or any(p in texto.lower() for p in ("unknown", "error", "invalid")):
            causa = "comando set-ringer-mode ausente ou recusado nesta versão"
            diag.append({"teste": "o comando existe?", "resultado": texto[:160] or f"código {rc}",
                         "conclusao": causa})
        else:
            causa = f"o sistema não mudou o toque (continua {lido} após ~2,5 s): Não perturbe ou regra do fabricante"
            diag.append({"teste": "o valor mudou em até ~2,5 s?", "resultado": f"não (lido: {lido})",
                         "conclusao": causa})
        mem.falhou("toque", metodo, cond, causa)
    return None


def aplicar_volume(cel, mem, fluxo, valor, cond, diag):
    """Escreve e confere pela leitura. Método que não muda o valor vira falha aprendida (com a causa)."""
    for metodo in mem.ordem("volume", cond):
        if metodo == "shell" and not cond.get("shizuku"):
            continue
        try:
            cel.definir_volume(fluxo, valor, metodo)
            lido = cel.ler([fluxo])["volumes"].get(fluxo)
        except FileNotFoundError:
            diag.append({"teste": "termux-volume existe?", "resultado": "não",
                         "conclusao": "falta o Termux:API (pkg install termux-api e o app Termux:API)"})
            mem.falhou("volume", metodo, cond, "Termux:API ausente")
            continue
        except SemShell:
            continue
        if lido == int(valor):
            mem.ok("volume", metodo, cond)
            return metodo
        causa = f"pedido {valor}, ficou {lido}: o sistema ignorou este caminho"
        diag.append({"teste": f"{fluxo} mudou via {metodo}?", "resultado": f"não (lido {lido})", "conclusao": causa})
        mem.falhou("volume", metodo, cond, causa)
    return None


def _ler_ou_diagnosticar(cel, fluxos):
    """Leitura do estado; se nem o shell nem o Termux:API respondem, devolve o diagnóstico das duas vias."""
    try:
        return cel.ler(fluxos)
    except FileNotFoundError:
        causa = "falta o Termux:API (pkg install termux-api e o app Termux:API)"
    except (RuntimeError, ValueError, OSError) as e:
        causa = f"termux-volume não respondeu: {str(e)[:120]}"
    return {"diagnostico": [
        {"teste": "o Shizuku responde?", "resultado": "não",
         "conclusao": "Shizuku parado: abra o app Shizuku e toque em Iniciar"},
        {"teste": "termux-volume responde?", "resultado": "não", "conclusao": causa}],
        "dica": "sem nenhuma das duas vias o celular não pode ser lido nem ajustado; nada foi mudado"}


# --------------------------------------------------------------------------- ações
def _fluxos_do_modo(m):
    fl = list(FLUXOS_DO_TOQUE) if m.get("toque") else []
    return list(dict.fromkeys(fl + [_fluxo(f) for f in (m.get("volumes") or {})]))


def entrar(cel, nome_modo, avisar=False):
    t0 = time.monotonic()
    modos = modos_definidos()
    chave = _chave(nome_modo or "reuniao")
    if chave not in modos:
        return {"erro": f"modo “{nome_modo}” não existe", "modos": sorted(modos)}
    m = modos[chave]
    est = _ler_json("estado.json", {})
    ativo = est.get("ativo")
    if ativo and ativo.get("modo") == chave:
        return {"status": "ja_ativo", "modo": chave, "desde": ativo.get("desde"), "antes": ativo.get("antes")}
    mem = Memoria()
    fluxos = _fluxos_do_modo(m)
    if ativo:  # troca de modo: o "antes" continua sendo o original, para a volta deixar tudo como era
        fluxos = list(dict.fromkeys(fluxos + list((ativo.get("antes") or {}).get("volumes", {}))))
    leitura = _ler_ou_diagnosticar(cel, fluxos)
    if "diagnostico" in leitura:
        return {"status": "falhou", "modo": chave, **leitura}
    shell_ok = leitura["via"] == "shell"
    cond = _cond(leitura, shell_ok)
    antes = ativo["antes"] if ativo else {"toque": leitura["toque"], "volumes": leitura["volumes"]}
    if ativo:
        for f, v in leitura["volumes"].items():
            antes["volumes"].setdefault(f, v)
    # grava ANTES de mexer: se algo cair no meio, sair ainda sabe para onde voltar
    _gravar_json("estado.json", {"ativo": {"modo": chave, "desde": time.strftime("%d/%m %H:%M:%S"),
                                           "antes": antes, "completo": False}})
    diag, feito, metodos = [], {}, {}
    if m.get("toque"):
        metodo = aplicar_toque(cel, mem, m["toque"], cond, diag)
        if metodo:
            feito["toque"], metodos["toque"] = m["toque"], metodo
        else:  # plano B: silencia pelos volumes (sem vibrar), e diz isso
            for f in FLUXOS_DO_TOQUE:
                if aplicar_volume(cel, mem, f, 0, cond, diag):
                    feito.setdefault("volumes", {})[f] = 0
            if feito.get("volumes"):
                feito["plano_b"] = "toque silenciado pelos volumes (sem vibração): o modo de toque não pôde mudar"
    for f, v in (m.get("volumes") or {}).items():
        f = _fluxo(f)
        metodo = aplicar_volume(cel, mem, f, v, cond, diag)
        if metodo:
            feito.setdefault("volumes", {})[f] = int(v)
            metodos["volume"] = metodo
    mem.gravar()
    ok = bool(feito) and not (m.get("toque") and "toque" not in feito and "plano_b" not in feito)
    est = {"ativo": {"modo": chave, "desde": time.strftime("%d/%m %H:%M:%S"), "antes": antes, "completo": ok,
                     "aplicado": feito}}
    _gravar_json("estado.json", est)
    r = {"status": "ativo" if ok else "falhou", "modo": chave, "nome": m.get("nome"), "antes": antes,
         "aplicado": feito, "metodos": metodos, "segundos": round(time.monotonic() - t0, 2),
         "chamadas_android": cel.chamadas}
    if diag:
        r["diagnostico"] = diag
    if mem.notas:
        r["revalidacao"] = mem.notas
    if not ok:
        r["dica"] = "nada mudou de fato; veja o diagnóstico. acao=sair desfaz o que tiver sido aplicado"
    if avisar:
        _avisar(f"{m.get('nome', chave)}: ligado" + (" (vibrar)" if feito.get("toque") == "vibrar" else "")
                if ok else f"{m.get('nome', chave)}: não consegui aplicar")
    return r


def sair(cel, nome_modo=None, avisar=False):
    t0 = time.monotonic()
    est = _ler_json("estado.json", {})
    ativo = est.get("ativo")
    if not ativo:
        return {"status": "nenhum_ativo"}
    if nome_modo and _chave(nome_modo) != ativo.get("modo"):
        return {"status": "outro_ativo", "ativo": ativo.get("modo")}
    antes = ativo.get("antes") or {}
    mem = Memoria()
    diag = []
    leitura = _ler_ou_diagnosticar(cel, list(antes.get("volumes", {})) or list(FLUXOS_DO_TOQUE))
    if "diagnostico" in leitura:
        return {"status": "falhou", "modo": ativo["modo"], "antes": antes, **leitura}
    cond = _cond(leitura, leitura["via"] == "shell")
    if antes.get("toque") and leitura.get("toque") != antes["toque"]:
        aplicar_toque(cel, mem, antes["toque"], cond, diag)
    # volta o toque primeiro (o Android devolve o volume do toque sozinho); depois confere fluxo a fluxo
    agora = cel.ler(list(antes.get("volumes", {}))) if antes.get("volumes") else {"volumes": {}}
    for f, v in (antes.get("volumes") or {}).items():
        if agora["volumes"].get(f) != v:
            aplicar_volume(cel, mem, f, v, cond, diag)
    mem.gravar()
    final = cel.ler(list(antes.get("volumes", {})) or list(FLUXOS_DO_TOQUE))
    restaurado = (not antes.get("toque") or final.get("toque") in (None, antes["toque"])) and all(
        final["volumes"].get(f) == v for f, v in (antes.get("volumes") or {}).items())
    if restaurado:
        _gravar_json("estado.json", {})
    nome = modos_definidos().get(ativo["modo"], {}).get("nome", ativo["modo"])
    r = {"status": "restaurado" if restaurado else "incompleto", "modo": ativo["modo"], "antes": antes,
         "agora": {"toque": final.get("toque"), "volumes": final["volumes"]},
         "segundos": round(time.monotonic() - t0, 2), "chamadas_android": cel.chamadas}
    if diag:
        r["diagnostico"] = diag
    if avisar:
        _avisar(f"{nome}: desligado, tudo como antes" if restaurado else f"{nome}: não consegui restaurar tudo")
    return r


def testar(cel, nome_modo, criar_atalho=True):
    """Ciclo completo: entrar → conferir → sair → conferir que voltou igual. Registra a validação."""
    chave = _chave(nome_modo or "reuniao")
    if _ler_json("estado.json", {}).get("ativo"):
        return {"erro": "há um modo ativo; saia dele antes de testar (o teste precisa do estado normal)"}
    e = entrar(cel, chave)
    if e.get("erro"):
        return e
    s = sair(cel, chave)
    ok = e.get("status") == "ativo" and s.get("status") == "restaurado" and s.get("agora", {}).get("volumes") == \
        e.get("antes", {}).get("volumes")
    mem = Memoria()
    m = modos_definidos()[chave]
    mem.d["validacoes"][chave] = {
        "ok": ok, "quando": time.strftime("%d/%m %H:%M"), "definicao": {"toque": m.get("toque"),
                                                                       "volumes": m.get("volumes") or {}},
        "condicoes": {"metodos": e.get("metodos"), "plano_b": e.get("aplicado", {}).get("plano_b"),
                      **{k: v for k, v in (mem.d["metodos"].get("toque") or {}).get("condicoes", {}).items()}},
        "entrar_s": e.get("segundos"), "sair_s": s.get("segundos")}
    mem.gravar()
    r = {"status": "validado" if ok else "falhou", "modo": chave, "entrar": e, "sair": s}
    if ok and criar_atalho:
        r["atalho"] = atalho(chave)
    return r


def definir(a):
    chave = _chave(a.get("modo") or a.get("nome"))
    if not chave:
        return {"erro": "informe modo (nome curto, ex.: cinema)"}
    modos = modos_definidos()
    antigo = modos.get(chave)
    novo = {"nome": a.get("nome") or (antigo or {}).get("nome") or f"Modo {chave}",
            "toque": (antigo or {}).get("toque"), "volumes": dict((antigo or {}).get("volumes") or {}),
            "descricao": a.get("descricao") or (antigo or {}).get("descricao") or ""}
    if "toque" in a:
        if a["toque"] not in (None, "", *TOQUES):
            return {"erro": f"toque: {' | '.join(TOQUES)} (ou vazio para não mexer)"}
        novo["toque"] = a["toque"] or None
    if isinstance(a.get("volumes"), dict):
        try:
            for f, v in a["volumes"].items():
                f = _fluxo(f)
                if v is None:
                    novo["volumes"].pop(f, None)
                else:
                    novo["volumes"][f] = max(0, int(v))
        except (ValueError, TypeError) as e:
            return {"erro": str(e)}
    if not novo["toque"] and not novo["volumes"]:
        return {"erro": "o modo precisa mudar o toque ou algum volume"}
    salvos = _ler_json("modos.json", {})
    salvos[chave] = {k: v for k, v in novo.items() if k != "padrao"}
    _gravar_json("modos.json", salvos)
    mem = Memoria()
    if antigo:  # correção do usuário: guarda o antes/depois e invalida a validação antiga
        mem.d["correcoes"].append({"quando": time.strftime("%d/%m %H:%M"), "modo": chave,
                                   "de": {"toque": antigo.get("toque"), "volumes": antigo.get("volumes") or {}},
                                   "para": {"toque": novo["toque"], "volumes": novo["volumes"]}})
        mem.d["correcoes"] = mem.d["correcoes"][-50:]
    if chave in mem.d["validacoes"]:
        mem.d["validacoes"][chave]["ok"] = False
        mem.d["validacoes"][chave]["motivo"] = "definição mudou: rode acao=testar"
    mem.gravar()
    return {"status": "salvo", "modo": chave, "definicao": salvos[chave], "corrigido": bool(antigo),
            "proximo": "acao=testar para validar o ciclo completo"}


def atalho(chave):
    """Atalho do Termux:Widget que entra/sai do modo com um toque (pasta tasks: roda sem abrir o terminal)."""
    m = modos_definidos().get(chave) or {}
    nome = "Modo " + _chave(m.get("nome") or chave).replace("_", " ")
    pasta = os.path.join(os.path.expanduser("~"), ".shortcuts", "tasks")
    try:
        os.makedirs(pasta, exist_ok=True)
        for d in (os.path.dirname(pasta), pasta):
            os.chmod(d, 0o700)  # o Termux:Widget recusa pastas graváveis por outros apps
        arq = os.path.join(pasta, f"{nome} (liga-desliga)")
        args = json.dumps({"acao": "alternar", "modo": chave, "avisar": True})
        corpo = (f"#!{PREFIXO}/bin/sh\n# Atalho criado pela capacidade modos (Controle IR)\n"
                 f"exec \"{PREFIXO}/bin/controle-ir\" capacidade executar modos --args '{args}'\n")
        with open(arq + ".novo", "w") as f:
            f.write(corpo)
        os.chmod(arq + ".novo", 0o700)
        os.replace(arq + ".novo", arq)
        return {"arquivo": arq, "como_usar": "Termux:Widget na tela inicial → escolha o atalho; 1 toque liga, "
                                             "outro desliga (aparece um aviso)"}
    except OSError as e:
        return {"erro": str(e)}


def _avisar(texto):
    try:
        subprocess.run(["termux-toast", texto], capture_output=True, timeout=8, check=False)
    except (OSError, subprocess.SubprocessError):
        pass


def listar():
    mem = Memoria()
    est = _ler_json("estado.json", {})
    return {"modos": {k: {**v, "validacao": mem.d["validacoes"].get(k)} for k, v in modos_definidos().items()},
            "ativo": est.get("ativo"), "aprendido": mem.d["metodos"], "correcoes": mem.d["correcoes"][-10:]}


def resumo_curto():
    """Linha das instruções do conector: modos, se validados e qual está ativo (sem tocar no Android)."""
    val = Memoria().d["validacoes"]
    itens = []
    for k, m in sorted(modos_definidos().items()):
        o = [f"toque {m['toque']}"] if m.get("toque") else []
        o += [f"{f} {v}" for f, v in (m.get("volumes") or {}).items()]
        v = val.get(k) or {}
        o.append(f"validado {v['quando']}" if v.get("ok") else "não validado: rode acao=testar")
        itens.append(f"{k} ({m.get('nome', k)}: {', '.join(o)})")
    ativo = (_ler_json("estado.json", {}).get("ativo") or {}).get("modo")
    return ("Modos do celular (executar_capacidade modos, argumentos {acao: entrar|sair|alternar, modo}; guarda e "
            "restaura toque e volumes): " + "; ".join(itens) + f". Ativo agora: {ativo or 'nenhum'}.")


def executar(a, cel=None):
    cel = cel or Android()
    acao = a.get("acao", "estado")
    try:
        if acao == "entrar":
            return entrar(cel, a.get("modo"), bool(a.get("avisar")))
        if acao == "sair":
            return sair(cel, a.get("modo"), bool(a.get("avisar")))
        if acao == "alternar":
            ativo = (_ler_json("estado.json", {}).get("ativo") or {}).get("modo")
            if ativo == _chave(a.get("modo") or "reuniao"):
                return sair(cel, a.get("modo"), bool(a.get("avisar")))
            return entrar(cel, a.get("modo"), bool(a.get("avisar")))
        if acao == "estado":
            est = _ler_json("estado.json", {})
            return {"ativo": est.get("ativo"), "agora": _ler_ou_diagnosticar(cel, list(FLUXOS))}
        if acao == "listar":
            return listar()
        if acao == "definir":
            return definir(a)
        if acao == "testar":
            return testar(cel, a.get("modo"), a.get("criar_atalho", True) is not False)
        if acao == "atalho":
            return atalho(_chave(a.get("modo") or "reuniao"))
        if acao == "remover":
            chave = _chave(a.get("modo"))
            if (_ler_json("estado.json", {}).get("ativo") or {}).get("modo") == chave:
                return {"erro": "o modo está ativo; saia dele primeiro"}
            salvos = _ler_json("modos.json", {})
            if chave not in salvos:
                return {"erro": "só os modos criados por você podem ser removidos" if chave in PADRAO
                        else f"modo “{chave}” não existe"}
            salvos.pop(chave)
            _gravar_json("modos.json", salvos)
            return {"status": "removido", "modo": chave}
        return {"erro": f"acao desconhecida: {acao}"}
    except ValueError as e:
        return {"erro": str(e)}


def main():
    a = json.loads(sys.stdin.read() or "{}")
    print(json.dumps(executar(a), ensure_ascii=False))


if __name__ == "__main__":
    main()
