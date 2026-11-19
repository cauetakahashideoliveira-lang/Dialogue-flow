"""Canal direto com a Central de Controle: o celular disca para a Central e mantém um WebSocket aberto.

Por que: antes, cada chamada do Claude ia Central → ngrok → celular (um túnel de terceiros, endereço que muda a
cada reinício, "Not Found" quando o ngrok fica preso). Com o canal, a Central repassa a chamada pela conexão que o
próprio celular abriu: sem túnel, sem abrir porta, funciona em dados móveis e roteado, e sem um aperto de mão TLS
por chamada. A Central também EMPURRA avisos por ele (ex.: "armado agora" → o celular sincroniza na hora, em vez
de esperar até 30 s).

Segurança: o canal é aberto com o token do aparelho (o mesmo da sincronização) e cada chamada que chega continua
ASSINADA pela Central (X-Painel-Assinatura, conferida pelo servidor local como sempre). O canal só entrega a
chamada ao servidor local (127.0.0.1); nada aqui decide o que pode ou não ser executado.

Só a biblioteca padrão (o Termux não precisa de pacote novo). Se a Central ainda não tiver o canal (versão
antiga), tenta de novo a cada 5 min e tudo segue pelo túnel como antes.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import socket
import ssl
import struct
import threading
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
BATIDA = 25  # s entre "ping" (a Central responde "pong" sem acordar o objeto: custo zero)
SILENCIO = 80  # s sem nada recebido = conexão morta
CABECALHOS_OK = ("x-painel-assinatura", "content-type", "accept", "mcp-session-id", "mcp-protocol-version")


def _mascarar(dados: bytes, mascara: bytes) -> bytes:
    n = len(dados)
    if not n:
        return dados
    rep = (mascara * (n // 4 + 1))[:n]
    return (int.from_bytes(dados, "big") ^ int.from_bytes(rep, "big")).to_bytes(n, "big")


class WebSocket:
    """Cliente WebSocket mínimo (RFC 6455): texto, ping/pong, fragmentos e fechamento."""

    def __init__(self, url: str, cabecalhos: dict, timeout: float = 20):
        u = urlparse(url)
        seguro = u.scheme == "wss"
        porta = u.port or (443 if seguro else 80)
        s = socket.create_connection((u.hostname, porta), timeout=timeout)
        if seguro:
            s = ssl.create_default_context().wrap_socket(s, server_hostname=u.hostname)
        chave = base64.b64encode(os.urandom(16)).decode()
        caminho = (u.path or "/") + (f"?{u.query}" if u.query else "")
        req = (f"GET {caminho} HTTP/1.1\r\nHost: {u.netloc}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
               f"Sec-WebSocket-Key: {chave}\r\nSec-WebSocket-Version: 13\r\nUser-Agent: controle-ir\r\n"
               + "".join(f"{k}: {v}\r\n" for k, v in cabecalhos.items()) + "\r\n")
        s.sendall(req.encode())
        resp = bytearray()
        while b"\r\n\r\n" not in resp:
            d = s.recv(4096)
            if not d:
                raise ConnectionError("a Central fechou a conexão no aperto de mão")
            resp += d
            if len(resp) > 65536:
                raise ConnectionError("resposta de aperto de mão grande demais")
        cab, _, resto = bytes(resp).partition(b"\r\n\r\n")
        status = cab.split(b"\r\n", 1)[0].decode(errors="replace")
        self.status = int(status.split()[1]) if len(status.split()) > 1 and status.split()[1].isdigit() else 0
        if self.status != 101:
            s.close()
            raise ConnectionError(f"a Central recusou o canal: {status}")
        aceite = base64.b64encode(hashlib.sha1((chave + GUID).encode()).digest()).decode().lower()
        if f"sec-websocket-accept: {aceite}".encode() not in cab.lower():
            s.close()
            raise ConnectionError("aceite do WebSocket inválido")
        self.s = s
        self.buf = bytearray(resto)
        self.trava = threading.Lock()

    def enviar(self, dados, op: int = 1):
        if isinstance(dados, str):
            dados = dados.encode()
        n = len(dados)
        cab = bytearray([0x80 | op])
        if n < 126:
            cab.append(0x80 | n)
        elif n < 65536:
            cab += bytes([0x80 | 126]) + struct.pack("!H", n)
        else:
            cab += bytes([0x80 | 127]) + struct.pack("!Q", n)
        mascara = os.urandom(4)
        with self.trava:
            self.s.sendall(bytes(cab) + mascara + _mascarar(dados, mascara))

    def _ler(self, n: int) -> bytes:
        while len(self.buf) < n:
            d = self.s.recv(65536)
            if not d:
                raise ConnectionError("conexão fechada")
            self.buf += d
        r = bytes(self.buf[:n])
        del self.buf[:n]
        return r

    def receber(self) -> tuple[int, bytes]:
        """Uma mensagem inteira (junta fragmentos; responde ping). Lança socket.timeout se nada chegar a tempo."""
        partes, op0 = [], 1
        while True:
            b1, b2 = self._ler(2)
            fim, op, n = b1 & 0x80, b1 & 0x0F, b2 & 0x7F
            if n == 126:
                n = struct.unpack("!H", self._ler(2))[0]
            elif n == 127:
                n = struct.unpack("!Q", self._ler(8))[0]
            mascara = self._ler(4) if b2 & 0x80 else None
            dados = self._ler(n)
            if mascara:
                dados = _mascarar(dados, mascara)
            if op == 9:
                self.enviar(dados, 10)
                continue
            if op == 10:
                continue
            if op == 8:
                raise ConnectionError("a Central fechou o canal")
            if op in (1, 2):
                op0, partes = op, [dados]
            elif op == 0:
                partes.append(dados)
            if fim:
                return op0, b"".join(partes)

    def fechar(self):
        try:
            self.enviar(b"", 8)
        except OSError:
            pass
        try:
            self.s.close()
        except OSError:
            pass


class Canal:
    """Mantém o canal aberto (reconecta sozinho) e atende o que a Central manda: chamadas do Claude (repassadas ao
    servidor local) e avisos ("sync": sincronizar agora)."""

    def __init__(self, pasta, porta: int, segredo: str, ao_sincronizar=None, log=None):
        self.pasta, self.porta, self.segredo = pasta, int(porta), segredo
        self.ao_sincronizar = ao_sincronizar
        self.log = log or (lambda *a: None)
        self.parar = threading.Event()
        self.despertar = threading.Event()
        self.ws: WebSocket | None = None
        self.conectado_desde = 0.0
        self.ultimo_erro = ""
        self.atendidas = 0

    @property
    def conectado(self) -> bool:
        return self.ws is not None

    def estado(self) -> dict:
        return {"conectado": self.conectado, "desde": int(self.conectado_desde) if self.conectado else None,
                "atendidas": self.atendidas, **({"erro": self.ultimo_erro} if self.ultimo_erro else {})}

    def iniciar(self):
        threading.Thread(target=self._laco, name="canal", daemon=True).start()
        return self

    def acordar(self):
        """A Central avisou (na sincronização) que tem canal: se estiver desconectado, tenta já, sem esperar."""
        if not self.conectado:
            self.despertar.set()

    def _endereco(self):
        from . import painel as painel_mod
        cfg = painel_mod.ler(self.pasta)
        if not cfg or cfg.get("revogado") or not cfg.get("url") or not cfg.get("token"):
            return None, None
        u = cfg["url"].rstrip("/")
        u = "wss://" + u[8:] if u.startswith("https://") else "ws://" + u.split("://", 1)[-1]
        return f"{u}/api/celular/canal", cfg["token"]

    def _laco(self):
        espera = 2.0
        while not self.parar.is_set():
            url, token = self._endereco()
            if not url:
                self.parar.wait(60)
                continue
            try:
                self.ws = WebSocket(url, {"Authorization": f"Bearer {token}"})
                self.conectado_desde, self.ultimo_erro, espera = time.time(), "", 2.0
                self.log("canal", "conectado à Central")
                if self.ao_sincronizar:  # acabou de conectar: sincroniza (a Central passa a saber que o canal existe)
                    self.ao_sincronizar()
                self._atender()
            except (OSError, ConnectionError, ValueError) as e:
                self.ultimo_erro = str(e)[:160]
                if "404" in self.ultimo_erro or "405" in self.ultimo_erro:
                    espera = 300.0  # Central sem canal (versão antiga): tenta de vez em quando
                elif "401" in self.ultimo_erro or "403" in self.ultimo_erro:
                    espera = 120.0
            finally:
                if self.ws:
                    self.ws.fechar()
                self.ws = None
            if self.despertar.wait(espera):  # espera (ou a Central avisou que o canal existe: tenta já)
                espera = 2.0
            self.despertar.clear()
            espera = min(espera * 2, 60.0) if espera < 120 else espera

    def _atender(self):
        ws = self.ws
        ws.s.settimeout(BATIDA)
        ultimo = time.time()
        while not self.parar.is_set():
            try:
                op, dados = ws.receber()
            except socket.timeout:
                if time.time() - ultimo > SILENCIO:
                    raise ConnectionError("canal mudo: reconectando")
                ws.enviar("ping")
                continue
            ultimo = time.time()
            if op != 1 or dados in (b"pong", b"ping"):
                continue
            try:
                m = json.loads(dados)
            except ValueError:
                continue
            if m.get("t") == "req":
                ws.enviar(json.dumps({"t": "ok", "id": m.get("id")}))  # recebido: a Central não cai para o túnel
                threading.Thread(target=self._repassar, args=(m,), name="canal-req", daemon=True).start()
            elif m.get("t") == "sync" and self.ao_sincronizar:
                self.ao_sincronizar()

    def _repassar(self, m: dict):
        """Entrega a chamada (já assinada pela Central) ao servidor local e devolve a resposta pelo canal."""
        cab = {k: v for k, v in (m.get("h") or {}).items() if k.lower() in CABECALHOS_OK}
        corpo = str(m.get("b") or "").encode()
        req = urllib.request.Request(f"http://127.0.0.1:{self.porta}/mcp/{self.segredo}", data=corpo, headers=cab,
                                     method="POST")
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                st, tipo, txt = r.status, r.headers.get("Content-Type", "application/json"), r.read()
        except urllib.error.HTTPError as e:
            st, tipo, txt = e.code, e.headers.get("Content-Type", "application/json"), e.read()
        except (urllib.error.URLError, OSError) as e:
            st, tipo, txt = 502, "application/json", json.dumps({"erro": f"servidor local: {e}"[:200]}).encode()
        self.atendidas += 1
        resp = {"t": "res", "id": m.get("id"), "s": st, "h": {"content-type": tipo},
                "b": txt.decode("utf-8", errors="replace")}
        try:
            if self.ws:
                self.ws.enviar(json.dumps(resp, ensure_ascii=False))
        except OSError as e:
            self.ultimo_erro = f"resposta perdida: {e}"[:160]
