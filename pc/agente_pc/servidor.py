"""Servidor MCP local do PC (127.0.0.1) e guardião.

Só aceita chamadas assinadas pela Central de Controle (as mesmas assinaturas Ed25519 do celular, conferidas por
controle_ir.painel). O canal (controle_ir.canal) traz as chamadas da Central e as entrega aqui.

Guardião: desarmado, travado na Central ou travado pelo pc_travar → só pc_consultar e pc_travar. Armado (pelo
dono, com a digital, na Central) → todas as ferramentas.
"""
from __future__ import annotations

import hmac
import json
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from controle_ir import painel

from . import __version__
from .ferramentas import DEFINICOES, NOMES, Ferramentas

SEMPRE = {"pc_consultar", "pc_travar"}
CORPO_MAX = 32 * 2**20


class Guardiao:
    def __init__(self, pasta: Path, cfg_ler, cfg_gravar):
        self.pasta, self.cfg_ler, self.cfg_gravar = Path(pasta), cfg_ler, cfg_gravar
        self.trava = threading.Lock()

    def auditar(self, registro: dict):
        with self.trava:
            with open(self.pasta / "auditoria.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps({"quando": time.strftime("%Y-%m-%d %H:%M:%S"), **registro},
                                   ensure_ascii=False, default=str)[:4000] + "\n")

    def estado(self) -> dict:
        e = painel.estado_valido(self.pasta)
        cfg = self.cfg_ler()
        agora = time.time()
        r = {"pareado": bool(painel.ler(self.pasta)), "armado": False}
        if e:
            r.update(seq=e.get("seq"), travado_na_central=bool(e.get("travado")),
                     armado_ate=time.strftime("%d/%m %H:%M", time.localtime(e.get("armado_ate", 0)))
                     if e.get("armado_ate", 0) > agora else None)
            r["armado"] = not e.get("travado") and e.get("armado_ate", 0) > agora
        if cfg.get("travado_seq") is not None and (not e or int(e.get("seq", 0)) <= int(cfg["travado_seq"])):
            r["travado_local"] = cfg.get("travado_motivo") or True
            r["armado"] = False
        return r

    def motivo_bloqueio(self, nome: str) -> str | None:
        if nome in SEMPRE:
            return None
        s = self.estado()
        if s["armado"]:
            return None
        if s.get("travado_local"):
            return "o PC foi travado (pc_travar): o dono precisa armar de novo na Central de Controle, com a digital"
        if s.get("travado_na_central"):
            return "EMERGÊNCIA ativa na Central de Controle: só pc_consultar e pc_travar respondem"
        return (f"o PC está DESARMADO: “{nome}” precisa dele armado. O dono arma na Central de Controle, com a "
                "digital (Armar até a meia-noite / 2 h)")

    def travar(self, motivo: str):
        e = painel.estado_valido(self.pasta)
        cfg = self.cfg_ler()
        cfg["travado_seq"] = int(e.get("seq", 0)) if e else 0
        cfg["travado_motivo"] = str(motivo)[:200]
        self.cfg_gravar(cfg)
        self.auditar({"evento": "pc_travado", "motivo": motivo})


class ServidorMCP:
    def __init__(self, ferramentas: Ferramentas, guardiao: Guardiao):
        self.f, self.g = ferramentas, guardiao

    def tratar(self, msg) -> dict | list | None:
        if isinstance(msg, list):
            r = [x for x in (self._uma(m) for m in msg) if x is not None]
            return r or None
        return self._uma(msg)

    def _uma(self, m: dict) -> dict | None:
        if not isinstance(m, dict) or m.get("jsonrpc") != "2.0":
            return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "requisição inválida"}}
        ident, metodo, params = m.get("id"), m.get("method"), m.get("params") or {}
        if ident is None:  # notificação
            return None
        if metodo == "initialize":
            res = {"protocolVersion": params.get("protocolVersion") or "2025-06-18", "capabilities": {"tools": {}},
                   "serverInfo": {"name": "agente-pc", "title": "PC do dono", "version": __version__},
                   "instructions": "PC Windows do dono: ferramentas pc_*. Desarmado, só pc_consultar e pc_travar."}
        elif metodo == "ping":
            res = {}
        elif metodo == "tools/list":
            res = {"tools": DEFINICOES}
        elif metodo == "tools/call":
            res = self.chamar(str(params.get("name") or ""), params.get("arguments") or {})
        else:
            return {"jsonrpc": "2.0", "id": ident, "error": {"code": -32601, "message": f"método desconhecido: {metodo}"}}
        return {"jsonrpc": "2.0", "id": ident, "result": res}

    def chamar(self, nome: str, args: dict) -> dict:
        if nome not in NOMES:
            return _resultado({"erro": f"ferramenta desconhecida: {nome}"}, True)
        motivo = self.g.motivo_bloqueio(nome)
        if motivo:
            self.g.auditar({"evento": "pc_bloqueado", "ferramenta": nome})
            return _resultado({"erro": motivo, "bloqueado": True, "onde": "PC"}, True)
        t0 = time.time()
        try:
            dados, erro = self.f.chamar(nome, args), False
        except (ValueError, TypeError, OSError, RuntimeError, UnicodeDecodeError) as e:
            dados, erro = {"erro": str(e)[:1500]}, True
        except Exception as e:  # noqa: BLE001 — nunca derruba o servidor
            dados, erro = {"erro": f"{type(e).__name__}: {e}"[:600], "detalhe": traceback.format_exc()[-1500:]}, True
        if nome not in ("pc_consultar", "pc_tarefa", "pc_ler_arquivo", "pc_listar", "pc_tela"):
            self.g.auditar({"evento": "pc_chamada", "ferramenta": nome, "ok": not erro,
                            "ms": round((time.time() - t0) * 1000), "motivo": str(args.get("motivo") or "")[:200]})
        return _resultado(dados, erro)


def _resultado(dados: dict, erro: bool) -> dict:
    imagens = []

    def varrer(d, nivel=0):
        if not isinstance(d, dict) or nivel > 3:
            return
        i = d.pop("_imagem", None)
        if isinstance(i, dict) and i.get("base64"):
            imagens.append({"type": "image", "data": i["base64"], "mimeType": i.get("mime") or "image/jpeg"})
            d["imagem_anexada"] = True
        for v in list(d.values()):
            varrer(v, nivel + 1)

    varrer(dados)
    texto = json.dumps(dados, ensure_ascii=False, default=str)
    return {"content": [{"type": "text", "text": texto}, *imagens], "isError": bool(erro)}


def criar_servidor(pasta: Path, porta: int, segredo: str, mcp: ServidorMCP, guardiao: Guardiao,
                   exigir_assinatura: bool = True) -> ThreadingHTTPServer:
    class Manipulador(BaseHTTPRequestHandler):
        server_version = "agente-pc"

        def log_message(self, *a):  # sem registro de cada requisição (o histórico fica na auditoria)
            pass

        def _json(self, status: int, obj, extra: dict | None = None):
            corpo = json.dumps(obj, ensure_ascii=False).encode("utf-8") if obj is not None else b""
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(corpo)

        def do_GET(self):
            if self.path == "/saude":
                return self._json(200, {"ok": True, "versao": __version__, "pareado": bool(painel.ler(pasta))})
            return self._json(404, {"erro": "não encontrado"})

        def do_POST(self):
            partes = [p for p in self.path.split("?")[0].split("/") if p]
            if len(partes) != 2 or partes[0] != "mcp" or not hmac.compare_digest(partes[1], segredo):
                time.sleep(0.3)
                return self._json(404, {"erro": "não encontrado"})
            n = int(self.headers.get("Content-Length") or 0)
            if n > CORPO_MAX:
                return self._json(413, {"erro": "corpo grande demais"})
            bruto = self.rfile.read(n)
            if exigir_assinatura and not painel.verificar_requisicao(pasta, self.headers.get("X-Painel-Assinatura"), bruto):
                guardiao.auditar({"evento": "pc_assinatura_recusada"})
                return self._json(401, {"erro": "só a Central de Controle chama este PC (assinatura inválida ou repetida)"})
            try:
                msg = json.loads(bruto)
            except ValueError:
                return self._json(400, {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "JSON inválido"}})
            resp = mcp.tratar(msg)
            if resp is None:
                self.send_response(202)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            return self._json(200, resp)

    srv = ThreadingHTTPServer(("127.0.0.1", porta), Manipulador)
    srv.daemon_threads = True
    return srv
