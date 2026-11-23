"""Conexão com o PS4 pelo Remote Play (biblioteca pyremoteplay, base no Chiaki).

O celular vira um DualShock 4 virtual na rede: todos os botões, os dois analógicos e a imagem do jogo
(quadros decodificados). A pyremoteplay está parada desde 2022 (0.7.6); funciona com pyee<9 e async_timeout.
Instalação no Termux: veja `DEPENDENCIAS`.
"""
import asyncio
import base64
import collections
import logging
import os
import threading
import time

LOG = collections.deque(maxlen=400)  # últimas linhas do log da pyremoteplay (para diagnosticar no celular)


class _Memoria(logging.Handler):
    def emit(self, r):
        try:
            LOG.append(f"{time.strftime('%H:%M:%S')} {r.levelname[0]} {r.name.split('.')[-1]}: {r.getMessage()}"[:300])
        except Exception:  # noqa: BLE001
            pass


def _ligar_log(nivel=logging.DEBUG):
    lg = logging.getLogger("pyremoteplay")
    if not any(isinstance(h, _Memoria) for h in lg.handlers):
        lg.addHandler(_Memoria())
    lg.setLevel(nivel)
    lg.propagate = False


def ultimas_linhas(n=60, filtro=None):
    linhas = [l for l in LOG if not filtro or filtro.lower() in l.lower()]
    return linhas[-max(1, int(n)):]

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


def compat_av():
    """A pyremoteplay 0.7.6 foi escrita para o PyAV antigo (Flags.LOW_DELAY, Flags2.FAST); no PyAV 14+ os nomes
    são minúsculos e a abertura do decodificador quebrava em silêncio (sessão autentica, vídeo nunca começa).
    Troca o video_codec da biblioteca por um que aceita os dois jeitos. Idempotente."""
    import av
    from pyremoteplay.receiver import AVReceiver
    if getattr(AVReceiver, "_compat_controle_ir", False):
        return
    if not hasattr(av.error, "ValueError"):
        av.error.ValueError = ValueError
    ctxmod = av.codec.context

    def _flag(enum, *nomes):
        for n in nomes:
            if hasattr(enum, n):
                return getattr(enum, n)
        return None

    def video_codec(codec_name):
        try:
            cc = av.codec.Codec(codec_name, "r").create()
        except Exception as e:  # noqa: BLE001
            LOG.append(f"{time.strftime('%H:%M:%S')} E ps4: decodificador {codec_name} indisponível: {e}")
            raise
        LOG.append(f"{time.strftime('%H:%M:%S')} I ps4: decodificador {codec_name} (compat PyAV {av.__version__})")
        if codec_name.startswith("h264"):
            cc.options = AVReceiver.AV_CODEC_OPTIONS_H264
        elif codec_name.startswith("hevc"):
            cc.options = AVReceiver.AV_CODEC_OPTIONS_HEVC
        cc.pix_fmt = "yuv420p"
        f1 = _flag(ctxmod.Flags, "low_delay", "LOW_DELAY")
        f2 = _flag(ctxmod.Flags2, "fast", "FAST")
        tt = _flag(getattr(ctxmod, "ThreadType", None), "AUTO", "auto", "SLICE")
        if f1 is not None:
            cc.flags = f1
        if f2 is not None:
            cc.flags2 = f2
        if tt is not None:
            cc.thread_type = tt
        return cc

    AVReceiver.video_codec = staticmethod(video_codec)
    AVReceiver._compat_controle_ir = True


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
        _ligar_log()
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
        self.loop.set_exception_handler(
            lambda _l, ctx: LOG.append(f"{time.strftime('%H:%M:%S')} E asyncio: {ctx.get('message')} "
                                       f"{repr(ctx.get('exception'))[:200]}"))
        self.th = threading.Thread(target=self.loop.run_forever, name="ps4-remoteplay", daemon=True)
        self.th.start()
        return self.loop

    def _rodar(self, coro, timeout=40):
        return asyncio.run_coroutine_threadsafe(coro, self._laco()).result(timeout)

    def _sync(self, fn, *a, timeout=30, **kw):
        """Roda uma função síncrona da biblioteca DENTRO do laço: ela chama asyncio.get_event_loop() ao ler o
        estado do PS4 (busca a capa do jogo aberto) e quebra numa thread sem laço, como as do serviço."""
        async def _c():
            return fn(*a, **kw)
        return self._rodar(_c(), timeout)

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
        for d in self._sync(RPDevice.search):
            st = d.status or {}
            out.append({"ip": d.host, "nome": d.host_name, "tipo": d.host_type, "ligado": d.is_on,
                        "estado": d.status_name, "jogo": d.app_name, "sistema": d.system_version,
                        "mac": d.mac_address, "contas_pareadas": d.get_users(perfis) if st else []})
        return out

    def _dispositivo(self, ip):
        self._rp()
        from pyremoteplay.device import RPDevice
        d = RPDevice(ip)
        if not self._sync(d.get_status):
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
        r = self._sync(d.register, u, str(pin), timeout=6.0, profiles=perfis, save=False)
        if not r:
            raise RuntimeError("o PS4 recusou o PIN (ele muda a cada abertura da tela de vincular)")
        perfis.save(self.perfis_arq)
        return {"conta": u, "console": d.host_name}

    def ligar(self, ip, usuario=None):
        d = self._dispositivo(ip)
        if d.is_on:
            return {"ja_ligado": True}
        self._sync(d.wakeup, self._usuario(d, usuario), profiles=self._perfis())
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
        if self.device:  # sessão anterior que não ficou pronta
            self.desconectar()
        from pyremoteplay.receiver import QueueReceiver
        compat_av()
        d = self._dispositivo(ip)
        if not d.is_on:
            self._sync(d.wakeup, self._usuario(d, usuario), profiles=self._perfis())
            raise RuntimeError("o PS4 estava em repouso: mandei acordar, tente conectar de novo em ~20 s")
        self.receptor = QueueReceiver(max_frames=4)
        loop = self._laco()
        s = d.create_session(self._usuario(d, usuario), profiles=self._perfis(), loop=loop,
                             receiver=self.receptor, resolution=resolucao, fps=fps)
        if not s:
            raise RuntimeError("não consegui criar a sessão (conta pareada?)")
        self.device = d  # guarda já: se não ficar pronta, estado/log mostram onde parou e desconectar limpa
        LOG.append(f"{time.strftime('%H:%M:%S')} I ps4: conectando {ip} {resolucao}/{fps}")
        if not self._rodar(d.connect(), espera + 10):
            raise RuntimeError(f"sessão recusada: {getattr(s, 'error', '') or 'sem detalhe'} | "
                               + " / ".join(ultimas_linhas(8)))
        if not self._rodar(s.async_wait(espera), espera + 10):
            raise RuntimeError(f"o vídeo não começou a tempo (sessão: {self._estado_sessao()}) | "
                               + " / ".join(ultimas_linhas(12)))
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

    def _estado_sessao(self):
        s = self.device.session if self.device else None
        if not s:
            return None
        st = getattr(s, "state", None)
        return {"estado": getattr(st, "name", str(st)), "erro": getattr(s, "error", None),
                "stream": type(getattr(s, "_stream", None)).__name__}

    def estado(self):
        d = self.device
        return {"conectado": self.conectado, "sessao": self._estado_sessao(), "console": d.host_name if d else None,
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
