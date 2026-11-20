"""Túnel HTTPS público até o servidor local.

Modos:
* ``rapido``     — Cloudflare Quick Tunnel (``*.trycloudflare.com``), sem conta;
                   a URL muda sempre que o túnel reinicia.
* ``cloudflare`` — túnel nomeado com token e domínio próprio: URL fixa.
* ``ngrok``      — domínio estático gratuito do ngrok: URL fixa.
* ``nenhum``     — sem túnel (uso local/testes).
"""
from __future__ import annotations

import os
import re
import shutil
import signal
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
            return ["cloudflared", "tunnel", "--no-autoupdate", "run"]  # token pelo ambiente: fora do `ps`
        if self.modo == "ngrok":
            # sem o inspetor local (127.0.0.1:4040), que mostraria o caminho com o segredo e as respostas
            cmd = ["ngrok", "http", f"--url={self.cfg['dominio']}", alvo, "--log", "stdout", "--inspect=false"]
            # no Android o ngrok não acha o DNS; termux-chroot expõe um /etc/resolv.conf
            if self.cfg.get("chroot", True) and shutil.which("termux-chroot"):
                cmd = ["termux-chroot"] + cmd
            return cmd
        return None

    def limpar_orfaos(self) -> bool:
        """Encerra agentes ngrok que sobraram de um serviço anterior (ex.: depois de uma atualização).
        O plano grátis aceita um agente por domínio: um órfão faz o novo sair com código 1 em laço e o conector
        responde "Not Found". Só age no modo ngrok e só em processos chamados exatamente ``ngrok``."""
        if self.modo != "ngrok" or not shutil.which("pkill"):
            return False
        try:
            r = subprocess.run(["pkill", "-x", "ngrok"], capture_output=True, timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            return False
        if r.returncode == 0:
            self.log("ngrok antigo encerrado antes de abrir o túnel")
            time.sleep(1)
            return True
        return False

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
            self.limpar_orfaos()
            try:
                # grupo próprio: ao parar, encerra também o ngrok filho do termux-chroot (senão ele fica órfão)
                env = dict(os.environ, TUNNEL_TOKEN=self.cfg["token"]) if self.modo == "cloudflare" else None
                self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                             bufsize=1, start_new_session=True, env=env)
            except OSError as e:
                self.ultimo_erro = str(e)
                self.log(f"falha ao iniciar o túnel; nova tentativa em {espera} s")
                self.parar_evento.wait(espera)
                espera = min(espera * 2, 60)
                continue
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
            self.log(f"túnel encerrou (código {self.proc.returncode}); reiniciando em {espera} s" +
                     (f" — último erro: {self.ultimo_erro}" if self.ultimo_erro else ""))
            self.parar_evento.wait(espera)
            espera = min(espera * 2, 60)

    def parar(self):
        self.parar_evento.set()
        if self.proc and self.proc.poll() is None:
            self._sinal(signal.SIGTERM)
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._sinal(signal.SIGKILL)
        self.limpar_orfaos()

    def _sinal(self, sig):
        try:
            os.killpg(self.proc.pid, sig)
        except (OSError, AttributeError):
            try:
                self.proc.send_signal(sig)
            except OSError:
                pass
