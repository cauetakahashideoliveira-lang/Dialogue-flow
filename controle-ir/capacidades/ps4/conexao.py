"""Conexão com o PS4 pelo Remote Play (biblioteca pyremoteplay, base no Chiaki).

O celular vira um DualShock 4 virtual na rede: todos os botões, os dois analógicos e a imagem do jogo
(quadros decodificados). A pyremoteplay está parada desde 2022 (0.7.6); funciona com pyee<9 e async_timeout.
Instalação no Termux: veja `DEPENDENCIAS`.
"""
import asyncio
import base64
import os
import threading
import time

DEPENDENCIAS = ("pkg install -y python-cryptography ffmpeg clang && "
                "pip install 'pyee<9' async_timeout netifaces av pyremoteplay==0.7.6")


def disponivel():
    faltam = []
    for mod in ("pyremoteplay", "av", "numpy"):
        try:
            __import__(mod)
        except Exception as e:  # noqa: BLE001
            faltam.append(f"{mod} ({type(e).__name__}: {str(e)[:80]})")
    return faltam


class Conexao:
    def __init__(self, pasta):
        self.pasta = pasta
        os.makedirs(pasta, exist_ok=True)
        self.perfis_arq = os.path.join(pasta, "perfis.json")
        self.device = None
        self.receptor = None
        self.loop = None
        self.th = None
        self.desde = None
        self.ultimo_erro = None
        self._botoes_presos = set()

    # ------------------------------------------------------------ bibliotecas
    def _rp(self):
        import pyremoteplay  # noqa: F401
        from pyremoteplay.profile import Profiles
        Profiles.set_default_path(self.perfis_arq)
        return pyremoteplay

    def _perfis(self):
        self._rp()
        from pyremoteplay.profile import Profiles
        return Profiles.load(self.perfis_arq)

    def _laco(self):
        if self.loop and self.th and self.th.is_alive():
            return self.loop
        self.loop = asyncio.new_event_loop()
        self.th = threading.Thread(target=self.loop.run_forever, name="ps4-remoteplay", daemon=True)
        self.th.start()
        return self.loop

    def _rodar(self, coro, timeout=40):
        return asyncio.run_coroutine_threadsafe(coro, self._laco()).result(timeout)

    # ------------------------------------------------------------ conta PSN e pareamento
    def link_login(self):
        self._rp()
        from pyremoteplay.oauth import get_login_url
        return get_login_url()

    def contas(self):
        p = self._perfis()
        return [{"nome": u.name, "consoles": [h.name for h in u.hosts]} for u in p.users]

    def adicionar_conta(self, url=None, conta_id=None, nome=None):
        perfis = self._perfis()
        if url:
            u = perfis.new_user(url, save=False)
            if not u:
                raise RuntimeError("a Sony não aceitou o link (ele vale poucos minutos: gere outro e cole logo)")
            perfis.save(self.perfis_arq)
            return u.name
        if not conta_id or not nome:
            raise RuntimeError("informe url (depois do login) ou conta_id + nome")
        from pyremoteplay.profile import format_user_account
        cid = str(conta_id).strip()
        rpid = base64.b64encode(int(cid).to_bytes(8, "little")).decode() if cid.isdigit() else cid
        u = format_user_account({"user_rpid": rpid, "online_id": str(nome)})
        perfis.update_user(u)
        perfis.save(self.perfis_arq)
        return u.name

    def procurar(self):
        self._rp()
        from pyremoteplay.device import RPDevice
        out, perfis = [], self._perfis()
        for d in RPDevice.search():
            st = d.status or {}
            out.append({"ip": d.host, "nome": d.host_name, "tipo": d.host_type, "ligado": d.is_on,
                        "estado": d.status_name, "jogo": d.app_name, "sistema": d.system_version,
                        "mac": d.mac_address, "contas_pareadas": d.get_users(perfis) if st else []})
        return out

    def _dispositivo(self, ip):
        self._rp()
        from pyremoteplay.device import RPDevice
        d = RPDevice(ip)
        if not d.get_status():
            raise RuntimeError(f"PS4 não respondeu em {ip} (mesmo Wi-Fi? Remote Play ativado?)")
        return d

    def _usuario(self, d, usuario=None):
        perfis = self._perfis()
        nomes = d.get_users(perfis) if d.status else []
        if usuario:
            if usuario not in perfis.usernames:
                raise RuntimeError(f"conta {usuario!r} não cadastrada (acao=conta)")
            return usuario
        if nomes:
            return nomes[0]
        if len(perfis.usernames) == 1:
            return perfis.usernames[0]
        raise RuntimeError("nenhuma conta pareada com este PS4 (acao=parear com o PIN)")

    def parear(self, ip, pin, usuario=None):
        d = self._dispositivo(ip)
        perfis = self._perfis()
        u = usuario or (perfis.usernames[0] if perfis.usernames else None)
        if not u:
            raise RuntimeError("cadastre a conta PSN antes (acao=conta)")
        r = d.register(u, str(pin), timeout=6.0, profiles=perfis, save=False)
        if not r:
            raise RuntimeError("o PS4 recusou o PIN (ele muda a cada abertura da tela de vincular)")
        perfis.save(self.perfis_arq)
        return {"conta": u, "console": d.host_name}

    def ligar(self, ip, usuario=None):
        d = self._dispositivo(ip)
        if d.is_on:
            return {"ja_ligado": True}
        d.wakeup(self._usuario(d, usuario), profiles=self._perfis())
        return {"acordando": True}

    def repouso(self, ip=None, usuario=None):
        if self.device and self.device.session and self.device.connected:
            ok = self._rodar(self.device.session.async_standby())
            self.desconectar()
            return {"repouso": bool(ok)}
        d = self._dispositivo(ip)
        return {"repouso": bool(self._rodar(d.standby(self._usuario(d, usuario), self._perfis()), 60))}

    # ------------------------------------------------------------ sessão
    @property
    def conectado(self):
        try:
            return bool(self.device and self.device.session and self.device.session.is_ready)
        except Exception:  # noqa: BLE001
            return False

    def conectar(self, ip, usuario=None, resolucao="720p", fps="high", espera=30):
        if self.conectado:
            return {"ja_conectado": True}
        from pyremoteplay.receiver import QueueReceiver
        d = self._dispositivo(ip)
        if not d.is_on:
            d.wakeup(self._usuario(d, usuario), profiles=self._perfis())
            raise RuntimeError("o PS4 estava em repouso: mandei acordar, tente conectar de novo em ~20 s")
        self.receptor = QueueReceiver(max_frames=4)
        loop = self._laco()
        s = d.create_session(self._usuario(d, usuario), profiles=self._perfis(), loop=loop,
                             receiver=self.receptor, resolution=resolucao, fps=fps)
        if not s:
            raise RuntimeError("não consegui criar a sessão (conta pareada?)")
        if not self._rodar(d.connect(), espera + 10):
            raise RuntimeError(f"sessão recusada: {getattr(s, 'error', '') or 'sem detalhe'}")
        if not self._rodar(s.async_wait(espera), espera + 10):
            raise RuntimeError("o vídeo não começou a tempo")
        d.controller.start()
        self.device, self.desde = d, time.time()
        return {"conectado": True, "console": d.host_name, "resolucao": resolucao, "fps": fps}

    def desconectar(self):
        if self.device:
            try:
                for b in list(self._botoes_presos):
                    self.soltar(b)
                self.device.controller.stop()
                self.device.disconnect()
            except Exception:  # noqa: BLE001
                pass
        self.device, self.receptor, self.desde = None, None, None
        return {"desconectado": True}

    def estado(self):
        d = self.device
        return {"conectado": self.conectado, "console": d.host_name if d else None,
                "jogo": d.app_name if d else None,
                "conectado_ha_s": int(time.time() - self.desde) if self.desde else None}

    # ------------------------------------------------------------ controle (interface de controle.executar)
    def _ctrl(self):
        if not self.conectado:
            raise RuntimeError("PS4 não conectado (acao=conectar)")
        return self.device.controller

    def apertar(self, b):
        self._ctrl().button(b, "press")
        self._botoes_presos.add(b)

    def soltar(self, b):
        self._ctrl().button(b, "release")
        self._botoes_presos.discard(b)

    def analogico(self, lado, x, y):
        self._ctrl().stick(lado, point=(float(x), float(y)))

    # ------------------------------------------------------------ imagem
    def quadro(self):
        """Último quadro do jogo como array RGB (ou None)."""
        if not self.receptor:
            return None
        f = self.receptor.get_latest_video_frame()
        if f is None:
            return None
        return f.to_ndarray(format="rgb24")
