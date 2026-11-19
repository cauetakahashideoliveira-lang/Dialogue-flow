"""Ligação do celular com o Painel da Casa (Etapa 1 de docs/seguranca.md).

Pareado, o celular só fica ARMADO se o painel disser, num estado assinado (Ed25519) que o celular confere a cada
leitura com a chave pública fixada no pareamento. A cada ~30 s ele busca o estado, confirma o que aplicou (o painel
só mostra "aplicado" depois disso) e envia o histórico local (auditoria.jsonl) para o painel, onde o agente não
escreve. Sem resposta do painel, vale o último estado assinado até o prazo dele (no máximo 24 h).
"""
from __future__ import annotations

import base64
import json
import os
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

INTERVALO = 30
ARQUIVO = "painel.json"


def _b64(txt: str) -> bytes:
    return base64.urlsafe_b64decode(txt + "=" * (-len(txt) % 4))


def ler(pasta) -> dict | None:
    try:
        return json.loads((Path(pasta) / ARQUIVO).read_text())
    except (OSError, ValueError):
        return None


def gravar(pasta, dados: dict) -> None:
    arq = Path(pasta) / ARQUIVO
    tmp = arq.with_suffix(".novo")
    tmp.write_text(json.dumps(dados, indent=1))
    os.chmod(tmp, 0o600)
    os.replace(tmp, arq)


def verificar(cfg: dict, estado_txt: str, assinatura: str) -> dict:
    """Confere a assinatura do painel e devolve o estado. Lança ValueError se não servir."""
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError as e:  # sem a biblioteca, falha fechada
        raise ValueError("instale a biblioteca: pkg install python-cryptography") from e
    try:
        Ed25519PublicKey.from_public_bytes(_b64(cfg["chave_publica"])).verify(_b64(assinatura), estado_txt.encode())
    except (InvalidSignature, ValueError, KeyError) as e:
        raise ValueError("assinatura do painel inválida") from e
    e = json.loads(estado_txt)
    if e.get("v") != 1 or e.get("aparelho") != cfg.get("aparelho"):
        raise ValueError("estado de outro aparelho")
    return e


def estado_valido(pasta) -> dict | None:
    """Estado vigente (re-verificado agora). None = sem estado válido: o guardião trata como desarmado."""
    cfg = ler(pasta)
    if not cfg or cfg.get("revogado") or not cfg.get("estado"):
        return None
    try:
        e = verificar(cfg, cfg["estado"], cfg.get("assinatura", ""))
    except ValueError:
        return None
    if int(e.get("seq", -1)) < int(cfg.get("seq_max", 0)):  # estado antigo reapresentado
        return None
    return e


def _http(metodo: str, url: str, token: str | None = None, corpo=None, timeout: float = 10):
    cab = {"Accept": "application/json", "User-Agent": "controle-ir"}
    dados = None
    if corpo is not None:
        dados = json.dumps(corpo).encode()
        cab["Content-Type"] = "application/json"
    if token:
        cab["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=dados, headers=cab, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except ValueError:
            return e.code, {}


def parear(pasta, url: str, codigo: str, nome: str, versao: str) -> dict:
    url = url.rstrip("/")
    if not url.startswith("https://") and not url.startswith("http://localhost") and not url.startswith("http://127."):
        raise ValueError("o endereço do painel precisa ser https://")
    st, r = _http("POST", f"{url}/api/celular/parear", corpo={"codigo": codigo, "nome": nome, "versao": versao})
    if st != 200:
        raise ValueError(r.get("erro") or f"o painel respondeu HTTP {st}")
    cfg = {"url": url, "aparelho": r["aparelho"], "token": r["token"], "chave_publica": r["chave_publica"],
           "seq_max": 0, "offset": 0, "pareado_em": time.time()}
    gravar(pasta, cfg)
    return cfg


def sincronizar(pasta, versao: str, ao_reduzir=None) -> dict:
    """Uma rodada: busca o estado assinado, aplica, confirma e envia o histórico novo."""
    cfg = ler(pasta)
    if not cfg:
        return {"pareado": False}
    antes = estado_valido(pasta)
    st, r = _http("GET", f"{cfg['url']}/api/celular/estado", cfg["token"])
    if st == 401:  # revogado no painel: falha fechada
        cfg["revogado"] = True
        gravar(pasta, cfg)
        if ao_reduzir:
            ao_reduzir("celular revogado no painel")
        return {"pareado": True, "revogado": True}
    if st != 200:
        return {"pareado": True, "erro": f"HTTP {st}", "offline": True}
    e = verificar(cfg, r["estado"], r["assinatura"])
    if int(e["seq"]) < int(cfg.get("seq_max", 0)):
        raise ValueError("o painel devolveu um estado mais antigo que o já aplicado")
    cfg.update(estado=r["estado"], assinatura=r["assinatura"], seq_max=int(e["seq"]), verificado_em=time.time(),
               revogado=False)
    gravar(pasta, cfg)
    agora = time.time()
    armado_antes = bool(antes and not antes.get("travado") and antes.get("armado_ate", 0) > agora)
    armado_agora = not e.get("travado") and e.get("armado_ate", 0) > agora
    if ao_reduzir and (e.get("travado") or (armado_antes and not armado_agora)):
        ao_reduzir("emergência no painel" if e.get("travado") else "desarmado pelo painel")
    eventos, novo_offset = _eventos_novos(pasta, int(cfg.get("offset", 0)))
    st2, _ = _http("POST", f"{cfg['url']}/api/celular/ack", cfg["token"],
                   {"seq": e["seq"], "versao": versao, "eventos": eventos})
    if st2 == 200:
        cfg = ler(pasta) or cfg
        cfg["offset"] = novo_offset
        gravar(pasta, cfg)
    return {"pareado": True, "seq": e["seq"], "armado_ate": e["armado_ate"], "travado": e["travado"],
            "eventos_enviados": len(eventos) if st2 == 200 else 0}


def _eventos_novos(pasta, offset: int, maximo: int = 100) -> tuple[list, int]:
    arq = Path(pasta) / "auditoria.jsonl"
    try:
        with open(arq, "rb") as f:
            f.seek(0, 2)
            if offset > f.tell():  # arquivo encolheu: alguém apagou linhas — o painel registra
                return [{"evento": "auditoria_local_encolheu", "antes": offset, "agora": f.tell()}], f.tell()
            f.seek(offset)
            linhas, pos = [], offset
            for linha in f:
                if len(linhas) >= maximo:
                    break
                pos += len(linha)
                try:
                    d = json.loads(linha)
                except ValueError:
                    continue
                linhas.append({k: (str(v)[:200] if isinstance(v, str) else v) for k, v in d.items()})
            return linhas, pos
    except OSError:
        return [], offset


class Sincronizador:
    """Laço em segundo plano do serviço: busca o estado do painel a cada INTERVALO segundos."""

    def __init__(self, pasta, versao: str, ao_reduzir=None, log=None):
        self.pasta, self.versao, self.ao_reduzir = Path(pasta), versao, ao_reduzir
        self.log = log or (lambda *a: None)
        self.parar = threading.Event()
        self.ultimo: dict = {}

    def iniciar(self):
        threading.Thread(target=self._laco, name="painel", daemon=True).start()

    def _laco(self):
        while not self.parar.is_set():
            try:
                self.ultimo = sincronizar(self.pasta, self.versao, self.ao_reduzir)
            except Exception as e:  # noqa: BLE001 — erro de rede ou assinatura: mantém falha fechada
                self.ultimo = {"erro": str(e)[:200]}
                self.log("painel", self.ultimo["erro"])
            self.parar.wait(INTERVALO)
