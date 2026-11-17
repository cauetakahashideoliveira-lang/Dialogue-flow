"""Túnel HTTPS público até o servidor local.

Modos:
* ``rapido``     — Cloudflare Quick Tunnel (``*.trycloudflare.com``), sem conta;
                   a URL muda sempre que o túnel reinicia.
* ``cloudflare`` — túnel nomeado com token e domínio próprio: URL fixa.
* ``ngrok``      — domínio estático gratuito do ngrok: URL fixa.
* ``nenhum``     — sem túnel (uso local/testes).
"""
from __future__ import annotations

import re
import shutil
import subprocess
import threading
import time

RE_URL = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")


class Tunel:
    def __init__(self, porta: int, config: dict, ao_mudar_url=None, log=None):
        self.porta = porta
        self.cfg = config or {}
        self.modo = self.cfg.get("modo", "rapido")
        self.ao_mudar_url = ao_mudar_url or (lambda url: None)
        self.log = log or (lambda *a: None)
        self.url: str | None = None
        self.proc: subprocess.Popen | None = None
        self.parar_evento = threading.Event()
        self.thread: threading.Thread | None = None
        self.ultimo_erro: str | None = None

    def comando(self) -> list[str] | None:
        alvo = f"http://127.0.0.1:{self.porta}"
        if self.modo == "rapido":
            return ["cloudflared", "tunnel", "--no-autoupdate", "--url", alvo]
        if self.modo == "cloudflare":
            return ["cloudflared", "tunnel", "--no-autoupdate", "run", "--token", self.cfg["token"]]
        if self.modo == "ngrok":
            cmd = ["ngrok", "http", f"--url={self.cfg['dominio']}", alvo, "--log", "stdout"]
            # no Android o ngrok não acha o DNS; termux-chroot expõe um /etc/resolv.conf
            if self.cfg.get("chroot", True) and shutil.which("termux-chroot"):
                cmd = ["termux-chroot"] + cmd
            return cmd
        return None

    def iniciar(self):
        if self.modo == "nenhum":
            return
        self.thread = threading.Thread(target=self._laco, name="tunel", daemon=True)
        self.thread.start()

    def _definir_url(self, url: str):
        if url != self.url:
            self.url = url
            self.ao_mudar_url(url)

    def _laco(self):
        espera = 3
        while not self.parar_evento.is_set():
            cmd = self.comando()
            prog = next((c for c in (cmd or []) if c != "termux-chroot"), None)
            if not cmd or not shutil.which(prog):
                self.ultimo_erro = f"{prog or 'túnel'} não está instalado"
                self.log(self.ultimo_erro)
                return
            if self.modo in ("cloudflare", "ngrok"):
                fixa = self.cfg.get("url") or f"https://{self.cfg.get('dominio')}"
                self._definir_url(fixa.rstrip("/"))
            try:
                self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                             bufsize=1)
            except OSError as e:
                self.ultimo_erro = str(e)
                return
            inicio = time.monotonic()
            for linha in self.proc.stdout:
                if self.parar_evento.is_set():
                    break
                m = RE_URL.search(linha)
                if m and self.modo == "rapido":
                    self._definir_url(m.group(0))
                if "ERR" in linha or "error" in linha.lower():
                    self.ultimo_erro = linha.strip()[:200]
            self.proc.wait()
            if self.parar_evento.is_set():
                return
            # caiu: reinicia com espera crescente
            if time.monotonic() - inicio > 120:
                espera = 3
            self.log(f"túnel encerrou (código {self.proc.returncode}); reiniciando em {espera} s")
            self.parar_evento.wait(espera)
            espera = min(espera * 2, 60)

    def parar(self):
        self.parar_evento.set()
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
