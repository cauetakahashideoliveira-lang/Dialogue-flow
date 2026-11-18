"""Servidor HTTP local: MCP para o Claude, painel do celular e API do painel.

Rotas:
* ``POST /mcp/<segredo>``      — MCP (o túnel publica só esta URL);
* ``POST /mcp`` + ``Authorization: Bearer <segredo>`` — alternativa por cabeçalho;
* ``GET  /painel?t=<segredo>`` — painel para o navegador do celular;
* ``GET/POST /api/...?t=<segredo>`` — ações do painel e da linha de comando;
* ``GET  /saude``               — verificação sem dados.

Escuta apenas em 127.0.0.1; o acesso externo passa pelo túnel HTTPS.
"""
from __future__ import annotations

import hmac
import json
import shutil
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .mcp import ServidorMCP
from .servico import ErroUso, Servico

PAINEL = Path(__file__).with_name("painel.html")
ORIGENS_OK = ("claude.ai", "claude.com", "anthropic.com")
LIMITE_CORPO = 2_000_000


class Notificador:
    """Anuncia cada envio no celular: número falado em voz alta, linha grande no
    Termux e notificação persistente com o botão “Reagiu — pausar”."""

    def __init__(self, comando_cli: str = "controle-ir", voz: bool = True, console: bool = True):
        self.ok = bool(shutil.which("termux-notification"))
        self.voz = voz and bool(shutil.which("termux-tts-speak"))
        self.console = console
        self.cli = comando_cli
        self.ultimo = 0.0
        self.trava = threading.Lock()

    def _rodar(self, args, sempre=False):
        if not (self.ok or sempre):
            return
        try:
            subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            if not sempre:
                self.ok = False

    def falar(self, texto: str):
        if self.voz:
            self._rodar(["termux-tts-speak", "-l", "pt", "-r", "1.2", texto], sempre=True)

    def __call__(self, ev: dict):
        tipo = ev.get("tipo")
        if tipo in ("teste", "reteste", "distincao"):
            n = ev["n"]
            if tipo == "teste":
                marcas = ", ".join(ev.get("marcas") or [])[:60]
                txt = f"Nº {n} · candidato {ev['posicao']}/{ev['total']}"
                if ev.get("funcao"):
                    txt += f" · {ev['funcao']}"
                if marcas:
                    txt += f" · {marcas}"
                if ev.get("status") == "erro":
                    txt += " · ERRO no envio"
                fala = str(n) if ev.get("status") != "erro" else f"{n}, erro"
            elif tipo == "reteste":
                txt = f"Nº {n} · reteste do nº {ev['repete']}"
                fala = f"{n}, reteste do {ev['repete']}"
            else:
                txt = f"Nº {n} · distinção {ev.get('teste')} — variante {ev.get('variante')}"
                fala = f"{n}, variante {ev.get('variante')}"
            self.falar(fala)
            if self.console:
                print(f"  ▶ {n:>3}   {txt}", flush=True)
            with self.trava:
                agora = time.monotonic()
                if tipo == "teste" and agora - self.ultimo < 0.8:
                    return
                self.ultimo = agora
            self._rodar(["termux-notification", "--id", "controle-ir-busca", "--title", f"Controle IR — nº {n}",
                         "--content", txt, "--ongoing", "--alert-once", "--priority", "high",
                         "--button1", "Reagiu — pausar", "--button1-action", f"{self.cli} pausar",
                         "--button2", "Painel", "--button2-action", f"{self.cli} painel"])
        elif tipo in ("pausado", "lote", "concluido"):
            txt = {"pausado": "Busca pausada. Diga ao Claude qual número funcionou.",
                   "lote": f"Lote concluído ({ev.get('testados')}/{ev.get('total')}). Nada reagiu?",
                   "concluido": "Todos os candidatos foram testados."}[tipo]
            self.falar({"pausado": "pausado", "lote": "fim do lote", "concluido": "fim dos testes"}[tipo])
            if self.console:
                print(f"  ■ {txt}", flush=True)
            self._rodar(["termux-notification", "--id", "controle-ir-busca", "--title", "Controle IR",
                         "--content", txt, "--button1", "Continuar", "--button1-action", f"{self.cli} retomar",
                         "--button2", "Painel", "--button2-action", f"{self.cli} painel"])

    def limpar(self):
        if shutil.which("termux-notification-remove"):
            self._rodar(["termux-notification-remove", "controle-ir-busca"])

    def servico_ativo(self, url: str | None, encerrar: bool = False):
        """Notificação fixa enquanto o serviço roda em segundo plano (sem console no Termux)."""
        if encerrar:
            if shutil.which("termux-notification-remove"):
                self._rodar(["termux-notification-remove", "controle-ir-servico"])
            return
        host = urlparse(url).hostname if url else None
        txt = f"Conector pronto ({host})" if host else "Servidor local ativo (sem túnel)"
        self._rodar(["termux-notification", "--id", "controle-ir-servico", "--title", "Controle IR ativo",
                     "--content", f"{txt} · em segundo plano", "--ongoing", "--alert-once", "--priority", "low",
                     "--button1", "Painel", "--button1-action", f"{self.cli} painel",
                     "--button2", "Copiar URL", "--button2-action", f"{self.cli} copiar",
                     "--button3", "Desligar", "--button3-action", f"{self.cli} desligar"])


def criar_servidor(servico: Servico, segredo: str, porta: int = 8765, host: str = "127.0.0.1", log=None):
    log = log or (lambda *a: None)
    mcp = ServidorMCP(servico, log)

    def token_ok(t: str | None) -> bool:
        return bool(t) and hmac.compare_digest(str(t).encode(), segredo.encode())

    acoes = {
        "pausar": lambda d: servico.pausar(origem=d.get("origem", "painel")),
        "retomar": lambda d: servico.retomar(d.get("intervalo"), d.get("a_partir_de")),
        "retestar": lambda d: servico.retestar([int(d["numero"])], d.get("intervalo")),
        "confirmar": lambda d: servico.confirmar(int(d["numero"]), bool(d.get("funcionou", True))),
        "intervalo": lambda d: servico.desc.ajustar_intervalo(float(d["intervalo"])),
        "tecla": lambda d: servico.controlar(d["aparelho"], teclas=[d["tecla"]]),
        "importar": lambda d: servico.importar(d["conteudo"], d.get("nome"), d.get("categoria"), d.get("marca")),
    }

    class Manipulador(BaseHTTPRequestHandler):
        server_version = "controle-ir"
        protocol_version = "HTTP/1.1"

        def log_message(self, fmt, *args):  # silencioso: não registra URLs com segredo
            return

        def _json(self, status: int, obj=None, extra: dict | None = None):
            corpo = b"" if obj is None else json.dumps(obj, ensure_ascii=False, default=str).encode()
            self.send_response(status)
            if obj is not None:
                self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.send_header("Cache-Control", "no-store")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            if corpo:
                self.wfile.write(corpo)

        def _origem_ok(self) -> bool:
            o = self.headers.get("Origin")
            if not o or o == "null":
                return True
            host = urlparse(o).hostname or ""
            if host in ("127.0.0.1", "localhost"):
                return True
            return any(host == d or host.endswith("." + d) for d in ORIGENS_OK)

        def _corpo(self):
            n = int(self.headers.get("Content-Length") or 0)
            if n > LIMITE_CORPO:
                raise ValueError("corpo grande demais")
            dados = self.rfile.read(n) if n else b""
            return json.loads(dados.decode() or "null") if dados else None

        def _rota(self):
            u = urlparse(self.path)
            partes = [p for p in u.path.split("/") if p]
            q = parse_qs(u.query)
            return u, partes, q

        def _token_req(self, q) -> str | None:
            auth = self.headers.get("Authorization", "")
            if auth.lower().startswith("bearer "):
                return auth[7:].strip()
            return (q.get("t") or [None])[0] or self.headers.get("X-Token")

        def do_GET(self):
            u, partes, q = self._rota()
            if not self._origem_ok():
                return self._json(403, {"erro": "origem não permitida"})
            if u.path in ("/", "/saude"):
                return self._json(200, {"servico": "controle-ir", "ok": True})
            if partes and partes[0] == "mcp":
                return self._json(405, {"erro": "use POST"}, {"Allow": "POST"})
            if partes == ["painel"]:
                if not token_ok(self._token_req(q)):
                    return self._json(401, {"erro": "segredo inválido"})
                html = PAINEL.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("Referrer-Policy", "no-referrer")
                self.end_headers()
                self.wfile.write(html)
                return
            if partes == ["api", "estado"]:
                if not token_ok(self._token_req(q)):
                    return self._json(401, {"erro": "segredo inválido"})
                return self._json(200, servico.estado_painel())
            return self._json(404, {"erro": "não encontrado"})

        def do_DELETE(self):
            return self._json(405, {"erro": "sem sessões para encerrar"}, {"Allow": "POST"})

        def do_OPTIONS(self):
            return self._json(204, None, {"Allow": "GET, POST"})

        def do_POST(self):
            u, partes, q = self._rota()
            if not self._origem_ok():
                return self._json(403, {"erro": "origem não permitida"})
            try:
                corpo = self._corpo()
            except (ValueError, json.JSONDecodeError):
                return self._json(400, {"jsonrpc": "2.0", "id": None,
                                        "error": {"code": -32700, "message": "JSON inválido"}})
            if partes and partes[0] == "mcp":
                t = partes[1] if len(partes) > 1 else self._token_req(q)
                if not token_ok(t):
                    time.sleep(0.5)
                    return self._json(401, {"erro": "segredo inválido"},
                                      {"WWW-Authenticate": 'Bearer realm="controle-ir"'})
                servico.ultima_requisicao_claude = time.time()
                status, resp = mcp.tratar(corpo)
                return self._json(status, resp)
            if len(partes) == 2 and partes[0] == "api" and partes[1] in acoes:
                if not token_ok(self._token_req(q)):
                    return self._json(401, {"erro": "segredo inválido"})
                try:
                    return self._json(200, acoes[partes[1]](corpo or {}))
                except ErroUso as e:
                    return self._json(400, {"erro": str(e)})
                except (KeyError, TypeError, ValueError) as e:
                    return self._json(400, {"erro": f"parâmetros inválidos: {e}"})
            return self._json(404, {"erro": "não encontrado"})

    srv = ThreadingHTTPServer((host, porta), Manipulador)
    srv.daemon_threads = True
    return srv
