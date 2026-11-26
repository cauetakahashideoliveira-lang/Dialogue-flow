"""Pastas e configuração local do agente (fora do repositório: o segredo local nunca vai para o Git)."""
from __future__ import annotations

import json
import os
import secrets
from pathlib import Path

WINDOWS = os.name == "nt"
REPO = Path(__file__).resolve().parents[2]  # raiz do dialogue-flow (pc/agente_pc/ -> ../..)
PORTA_PADRAO = 47630


def pasta() -> Path:
    base = os.environ.get("AGENTE_PC_DIR")
    if base:
        p = Path(base)
    elif WINDOWS and os.environ.get("LOCALAPPDATA"):
        p = Path(os.environ["LOCALAPPDATA"]) / "agente-pc"
    else:
        p = Path.home() / ".agente-pc"
    p.mkdir(parents=True, exist_ok=True)
    return p


def ler(p: Path | None = None) -> dict:
    """config.json: porta e segredo da rota local (a Central não o conhece; só o canal, na mesma máquina)."""
    p = p or pasta()
    arq = p / "config.json"
    try:
        cfg = json.loads(arq.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cfg = {}
    mudou = False
    if not cfg.get("segredo"):
        cfg["segredo"], mudou = secrets.token_urlsafe(24), True
    if not cfg.get("porta"):
        cfg["porta"], mudou = int(os.environ.get("AGENTE_PC_PORTA") or PORTA_PADRAO), True
    if mudou:
        gravar(cfg, p)
    return cfg


def gravar(cfg: dict, p: Path | None = None) -> None:
    p = p or pasta()
    arq = p / "config.json"
    tmp = arq.with_suffix(".novo")
    tmp.write_text(json.dumps(cfg, indent=1), encoding="utf-8")
    os.replace(tmp, arq)
