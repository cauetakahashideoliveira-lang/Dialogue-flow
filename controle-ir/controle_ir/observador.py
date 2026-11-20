"""Olhos da Central de Controle: o que está em uso agora no celular e quadros da tela ao vivo.

Só observa e relata ao painel (nada aqui pede aprovação nem muda a política):
* tarefas do terminal em execução (com os recursos que o comando toca: câmera, microfone, localização…);
* capacidades rodando em segundo plano (sono, sonar, termômetro…), lidas de /proc;
* câmera e microfone em uso por QUALQUER app, como o ponto verde do Android (AppOps "Running"), pelo Shizuku —
  só enquanto o painel está aberto, para não gastar bateria à toa;
* quadros JPEG da tela (screencap + ffmpeg da capacidade tela) enquanto o dono assiste no painel.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

CAPS = Path(__file__).resolve().parent.parent / "capacidades"
PALAVRAS = {
    "câmera": ("termux-camera", "camera-photo", "screenrecord --camera"),
    "microfone": ("termux-microphone", "microphone-record", "arecord", "ouvir_bipe"),
    "localização": ("termux-location",),
    "tela": ("screencap", "screenrecord", "uiautomator", "input tap", "input text", "input swipe"),
    "sms": ("termux-sms",),
    "contatos": ("termux-contact",),
    "chamadas": ("termux-telephony", "termux-call-log"),
}
RECURSOS_CAP = {"sono": ["microfone"], "sonar": ["microfone", "alto-falante"], "ouvir_bipe": ["microfone"],
                "foto": ["câmera"], "tela": ["tela"], "termometro": ["sensores"]}
_tela_mod = None


def recursos_do_comando(cmd: str) -> list[str]:
    c = (cmd or "").lower()
    return [r for r, ps in PALAVRAS.items() if any(p in c for p in ps)]


def _tela():
    """A capacidade tela (rish por arquivo, screencap + ffmpeg), importada uma vez."""
    global _tela_mod
    if _tela_mod is None:  # o mesmo módulo das chamadas do Claude: um só leitor rápido aberto
        from .capacidades import modulo_embutido
        _tela_mod = modulo_embutido(CAPS / "tela", "tela")
    return _tela_mod


def apps_usando(saida: str) -> dict[str, list[str]]:
    """Lê `dumpsys appops --op CAMERA; echo #####; dumpsys appops --op RECORD_AUDIO`: apps com a operação ativa."""
    res = {"câmera": [], "microfone": []}
    for chave, bloco in zip(("câmera", "microfone"), (saida or "").split("#####")):
        pacote = None
        for linha in bloco.splitlines():
            m = re.match(r"\s*Package (\S+):", linha)
            if m:
                pacote = m.group(1)
            elif "Running start at" in linha and pacote and pacote not in res[chave]:
                res[chave].append(pacote)
    return res


def _tarefas(pasta: Path) -> list[dict]:
    itens = []
    for f in (pasta / "tarefas").glob("*.json"):
        try:
            t = json.loads(f.read_text())
        except (OSError, ValueError):
            continue
        if t.get("status") == "executando":
            cmd = str(t.get("comando") or "")
            itens.append({"tipo": "terminal", "desc": cmd[:120], "desde": t.get("inicio"),
                          "recursos": ["terminal"] + recursos_do_comando(cmd)})
    return itens


def _capacidades_rodando() -> list[dict]:
    itens, vistos = [], set()
    for d in Path("/proc").glob("[0-9]*"):
        try:
            args = (d / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="ignore")
        except OSError:
            continue
        m = re.search(r"capacidades/([\w-]+)/principal\.py", args)
        if m and m.group(1) not in vistos:
            nome = m.group(1)
            vistos.add(nome)
            itens.append({"tipo": "capacidade", "desc": nome, "recursos": RECURSOS_CAP.get(nome, [])})
    return itens


def em_uso(pasta, android: bool = False, ao_vivo: bool = False) -> dict:
    """Resumo do que está em uso agora. `android` liga a checagem de câmera/microfone pelo Shizuku (painel aberto)."""
    pasta = Path(pasta)
    r = {"itens": _tarefas(pasta) + _capacidades_rodando(), "verificado_em": int(time.time())}
    if ao_vivo:
        r["itens"].append({"tipo": "tela", "desc": "tela transmitida para a Central de Controle", "recursos": ["tela"]})
    if android:
        try:
            out, _, codigo = _tela().rish("dumpsys appops --op CAMERA; echo '#####'; dumpsys appops --op RECORD_AUDIO",
                                     timeout=15)
            if codigo != 0:
                raise RuntimeError(f"consulta ao Android terminou com código {codigo}")
            r.update(apps_usando(out))
            r["shizuku"] = True
        except Exception as e:  # noqa: BLE001 — sem Shizuku o resto do relatório continua valendo
            r["shizuku"] = False
            r["shizuku_erro"] = str(e)[:120]
    return r


def quadro(largura: int = 540) -> str | None:
    """Um quadro JPEG da tela em base64 (None se o Shizuku não estiver ativo ou a tela for protegida)."""
    try:
        b64, _ = _tela().captura(largura)
        return b64
    except Exception:  # noqa: BLE001
        return None


if __name__ == "__main__":  # diagnóstico manual no Termux: python3 -m controle_ir.observador
    print(json.dumps(em_uso(os.path.expanduser("~/.controle-ir"), android=True), ensure_ascii=False, indent=1))
