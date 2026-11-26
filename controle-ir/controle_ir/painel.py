"""Ligação do celular com a Central de Controle (Etapa 1 de docs/seguranca.md).

Pareado, o celular só fica ARMADO se o painel disser, num estado assinado (Ed25519) que o celular confere a cada
leitura com a chave pública fixada no pareamento. A cada ~30 s ele busca o estado, confirma o que aplicou (o painel
só mostra "aplicado" depois disso) e envia o histórico local (auditoria.jsonl) para o painel, onde o agente não
escreve. Sem resposta do painel, vale o último estado assinado até o prazo dele (no máximo 24 h).
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

INTERVALO = 30
QUADRO = 2.0  # segundos entre quadros da tela ao vivo
MAX_EVENTOS = 30  # por envio: cabe numa transação do painel (limite de consultas do plano grátis)
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


# Etapa 1b: o painel (gateway OAuth na borda) assina cada chamada MCP que repassa ao celular:
# cabeçalho X-Painel-Assinatura = "<unix>.<nonce>.<Ed25519 de '<unix>.<nonce>.<sha256 hex do corpo>'>", com a mesma
# chave do estado. O nonce (aleatório) torna cada assinatura única: a mesma não é aceita duas vezes.
JANELA_ASSINATURA = 90
_vistas: dict[str, float] = {}
_vistas_trava = threading.Lock()


def verificar_requisicao(pasta, cabecalho: str | None, corpo: bytes, agora: float | None = None) -> bool:
    """A chamada veio da Central de Controle? Confere assinatura, horário (±90 s) e repetição (cada uma vale uma vez)."""
    cfg = ler(pasta)
    if not cfg or cfg.get("revogado") or not cabecalho or cabecalho.count(".") != 2:
        return False
    agora = time.time() if agora is None else agora
    ts, nonce, sig = cabecalho.split(".")
    try:
        if abs(agora - int(ts)) > JANELA_ASSINATURA or not 8 <= len(nonce) <= 64:
            return False
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        msg = f"{int(ts)}.{nonce}.{hashlib.sha256(corpo).hexdigest()}".encode()
        Ed25519PublicKey.from_public_bytes(_b64(cfg["chave_publica"])).verify(_b64(sig), msg)
    except (ValueError, KeyError, ImportError, InvalidSignature):
        return False
    with _vistas_trava:
        for k in [k for k, t in _vistas.items() if agora - t > 2 * JANELA_ASSINATURA]:
            del _vistas[k]
        if nonce in _vistas:  # repetição de uma chamada já atendida
            return False
        _vistas[nonce] = agora
    return True


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
    except (urllib.error.URLError, OSError) as e:  # sem rede ou tempo esgotado: tratado como offline
        return 0, {"erro": str(getattr(e, "reason", e))[:200]}


def parear(pasta, url: str, codigo: str, nome: str, versao: str) -> dict:
    url = url.rstrip("/")
    if not url.startswith("https://") and not url.startswith("http://localhost") and not url.startswith("http://127."):
        raise ValueError("o endereço do painel precisa ser https://")
    st, r = _http("POST", f"{url}/api/celular/parear", corpo={"codigo": codigo, "nome": nome, "versao": versao})
    if st != 200:
        raise ValueError(r.get("erro") or f"o painel respondeu HTTP {st}")
    try:  # o histórico de antes do pareamento fica só no celular; o painel recebe daqui em diante
        offset = (Path(pasta) / "auditoria.jsonl").stat().st_size
    except OSError:
        offset = 0
    cfg = {"url": url, "aparelho": r["aparelho"], "token": r["token"], "chave_publica": r["chave_publica"],
           "seq_max": 0, "offset": offset, "pareado_em": time.time()}
    gravar(pasta, cfg)
    return cfg


def sincronizar(pasta, versao: str, ao_reduzir=None, url_mcp=None, em_uso=None) -> dict:
    """Uma rodada: busca o estado assinado, aplica, confirma e envia o histórico novo."""
    cfg = ler(pasta)
    if not cfg:
        return {"pareado": False}
    # celular (tem politica.json): a trava local acompanha a seq do painel. O agente do PC usa este mesmo módulo
    # com a trava dele (travado_seq na config própria) e não ganha politica.json por isso.
    pol = None
    if (Path(pasta) / "politica.json").exists():
        from .execucao import Politica
        pol = Politica(pasta)
        pol.efetiva()  # migra trava antiga (sem travado_seq) para a seq aplicada ANTES deste estado novo
    antes = estado_valido(pasta)
    st, r = _http("GET", f"{cfg['url']}/api/celular/estado", cfg["token"])
    if st == 401:  # revogado no painel: falha fechada
        cfg["revogado"] = True
        gravar(pasta, cfg)
        if ao_reduzir:
            ao_reduzir("celular revogado no painel")
        return {"pareado": True, "revogado": True}
    if st != 200:
        motivo = r.get("erro") if isinstance(r, dict) else None
        return {"pareado": True, "erro": f"HTTP {st}" + (f": {str(motivo)[:160]}" if motivo else ""),
                "offline": True}
    e = verificar(cfg, r["estado"], r["assinatura"])
    if int(e["seq"]) < int(cfg.get("seq_max", 0)):
        raise ValueError("o painel devolveu um estado mais antigo que o já aplicado")
    cfg.update(estado=r["estado"], assinatura=r["assinatura"], seq_max=int(e["seq"]), verificado_em=time.time(),
               revogado=False, so_pelo_painel=int(e.get("so_pelo_painel") or 0))
    gravar(pasta, cfg)
    if pol:  # estado assinado mais novo que a trava local (o dono armou de novo, com a digital): solta a trava
        pol.soltar_pelo_painel(int(e["seq"]), emergencia=bool(e.get("travado")))
    agora = time.time()
    armado_antes = bool(antes and not antes.get("travado") and antes.get("armado_ate", 0) > agora)
    armado_agora = not e.get("travado") and e.get("armado_ate", 0) > agora
    if ao_reduzir and (e.get("travado") or (armado_antes and not armado_agora)):
        ao_reduzir("emergência no painel" if e.get("travado") else "desarmado pelo painel")
    desde = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cfg["pareado_em"])) if cfg.get("pareado_em") else ""
    eventos, novo_offset, arquivo = _eventos_novos(pasta, int(cfg.get("offset", 0)), desde)
    corpo = {"seq": e["seq"], "versao": versao, "eventos": eventos, "arquivo": arquivo}
    if pol:  # o que vale de fato no celular: a Central não mostra "aplicado" com o celular ainda travado
        from .seguranca import armado
        ef = pol.efetiva()
        corpo["efetivo"] = {"armado": armado(ef), "travado": bool(ef["travado"]),
                            "trava_local": bool(ef.get("trava_local")),
                            "vetado": int(ef.get("veto_seq", -1)) >= int(e["seq"])}
    observar = float(r.get("observar_ate") or 0) > agora  # painel aberto: relatório completo (com Shizuku)
    ao_vivo = float(r.get("ao_vivo_ate") or 0) > agora
    if em_uso:
        try:
            corpo["em_uso"] = em_uso(observar, ao_vivo)
        except Exception as erro:  # noqa: BLE001 — o relatório nunca derruba a sincronização
            corpo["em_uso"] = {"itens": [], "erro": str(erro)[:120]}
    url = url_mcp() if url_mcp else None
    if url:  # endereço do MCP do celular, para o painel repassar as chamadas do Claude (assinadas)
        corpo["mcp_url"] = url
    st2, r2 = _http("POST", f"{cfg['url']}/api/celular/ack", cfg["token"], corpo, timeout=20)
    if st2 == 200:
        cfg = ler(pasta) or cfg
        cfg["offset"] = novo_offset
        gravar(pasta, cfg)
    erro_ack = {}
    if st2 != 200:  # o estado valeu, mas a Central não soube: continua mostrando "pendente"
        motivo = r2.get("erro") if isinstance(r2, dict) else None
        erro_ack = {"erro_ack": f"HTTP {st2}" + (f": {str(motivo)[:160]}" if motivo else "")}
    return {"pareado": True, "seq": e["seq"], "armado_ate": e["armado_ate"], "travado": e["travado"], **erro_ack,
            "eventos_enviados": len(eventos) if st2 == 200 else 0,
            "eventos_aceitos": r2.get("recebidos", 0) if st2 == 200 else 0,
            "ao_vivo_ate": float(r.get("ao_vivo_ate") or 0), "observar_ate": float(r.get("observar_ate") or 0),
            "canal_na_central": bool(r.get("canal"))}


def _eventos_novos(pasta, offset: int, desde: str = "", maximo: int = MAX_EVENTOS) -> tuple[list, int, str]:
    """Linhas novas da auditoria local a partir de `offset` (no máximo `maximo` por envio, para o painel gravar
    tudo numa só transação). Cada evento leva `_fim` (posição no arquivo) para o painel ignorar repetidos, e
    `arquivo` identifica o arquivo (se ele for trocado, as posições recomeçam)."""
    arq = Path(pasta) / "auditoria.jsonl"
    try:
        with open(arq, "rb") as f:
            arquivo = str(os.fstat(f.fileno()).st_ino)
            f.seek(0, 2)
            if offset > f.tell():  # arquivo encolheu: alguém apagou linhas — o painel registra
                return [{"evento": "auditoria_local_encolheu", "antes": offset, "agora": f.tell()}], f.tell(), arquivo
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
                if desde and str(d.get("quando", "9")) < desde:  # anterior ao pareamento: fica só no celular
                    continue
                linhas.append({**{k: (str(v)[:200] if isinstance(v, str) else v) for k, v in d.items()}, "_fim": pos})
            return linhas, pos, arquivo
    except OSError:
        return [], offset, ""


class Sincronizador:
    """Laço em segundo plano do serviço: busca o estado do painel a cada INTERVALO segundos."""

    def __init__(self, pasta, versao: str, ao_reduzir=None, log=None, url_mcp=None, em_uso=None, quadro=None):
        self.pasta, self.versao, self.ao_reduzir, self.url_mcp = Path(pasta), versao, ao_reduzir, url_mcp
        self.em_uso, self.quadro = em_uso, quadro
        self.log = log or _log_padrao  # falha de sincronização nunca é muda: sem log próprio, vai para a saída
        self.parar = threading.Event()
        self.despertar = threading.Event()
        self.ultimo: dict = {}
        self.resultado: dict = {}  # último resultado (ok/erro, quando, seq), mostrado em consultar
        self.thread: threading.Thread | None = None
        self.ao_ver_canal = None  # a Central passou a ter canal direto: o canal do celular tenta conectar já

    def iniciar(self):
        self.thread = threading.Thread(target=self._laco, name="painel", daemon=True)
        self.thread.start()
        return self

    def acordar(self):
        """Sincroniza agora (a Central avisou pelo canal: armado, desarmado, painel aberto…), sem esperar 30 s."""
        self.despertar.set()

    def resumo(self) -> dict:
        return dict(self.resultado) if self.resultado else {"ok": None, "quando": None}

    def _registrar(self, r: dict):
        """Guarda o resultado da rodada; erro (HTTP, motivo, exceção, ack recusado) vai para o log do serviço."""
        erro = r.get("erro") or r.get("erro_ack") or ("celular revogado no painel" if r.get("revogado") else None) \
            or (None if r.get("pareado", True) else "não pareado")
        falhava = self.resultado.get("ok") is False
        self.resultado = {"ok": not erro, "quando": time.strftime("%d/%m %H:%M:%S"),
                          "seq": r.get("seq", self.resultado.get("seq")), **({"erro": str(erro)[:200]} if erro else {})}
        if erro:
            self.log("painel", f"sincronização falhou: {erro}")
        elif falhava:
            self.log("painel", f"sincronização voltou ao normal (seq {r.get('seq')})")

    def _laco(self):
        while not self.parar.is_set():
            try:
                self.ultimo = self._rodada()
                self._registrar(self.ultimo)
                if self.ao_ver_canal and self.ultimo.get("canal_na_central"):
                    self.ao_ver_canal()
                if self.quadro and self.ultimo.get("ao_vivo_ate", 0) > time.time():
                    self._transmitir()
            except Exception as e:  # noqa: BLE001 — erro de rede ou assinatura: mantém falha fechada
                self.ultimo = {"erro": f"{type(e).__name__}: {e}"[:200]}
                self._registrar(self.ultimo)
            self.despertar.wait(INTERVALO)  # 30 s, ou na hora se a Central avisar pelo canal
            self.despertar.clear()

    def _rodada(self) -> dict:
        return sincronizar(self.pasta, self.versao, self.ao_reduzir, self.url_mcp, self.em_uso)

    def _transmitir(self):
        """Tela ao vivo: um quadro a cada ~2 s enquanto o painel pedir (o pedido vence em 2 min sem renovação)."""
        cfg = ler(self.pasta)
        proxima = time.time() + 10
        while cfg and not self.parar.is_set() and self.ultimo.get("ao_vivo_ate", 0) > time.time():
            t0 = time.time()
            b64 = self.quadro()
            if b64:
                st, _ = _http("POST", f"{cfg['url']}/api/celular/quadro", cfg["token"], {"jpeg": b64}, timeout=15)
                if st in (401, 409):  # revogado, ou o dono parou de assistir
                    break
            if time.time() >= proxima:  # confirma com o painel se ainda é para transmitir
                self.ultimo = self._rodada()
                self._registrar(self.ultimo)
                proxima = time.time() + 10
            self.parar.wait(max(0.3, QUADRO - (time.time() - t0)))


class CaoDeGuarda:
    """Confere a cada `intervalo` s se as threads vigiadas (canal, painel) estão vivas e reinicia a que morreu.

    `vigiados`: nome → objeto com `thread`, `parar` (Event) e `iniciar()` (Canal e Sincronizador). Quem foi parado
    de propósito (`parar` ligado) não é reiniciado."""

    def __init__(self, vigiados: dict, log=None, intervalo: float = 30.0):
        self.vigiados, self.intervalo = dict(vigiados), float(intervalo)
        self.log = log or _log_padrao
        self.parar = threading.Event()
        self.reinicios: dict[str, int] = {}

    def iniciar(self):
        threading.Thread(target=self._laco, name="cao-de-guarda", daemon=True).start()
        return self

    def conferir(self):
        for nome, obj in self.vigiados.items():
            t = getattr(obj, "thread", None)
            if obj.parar.is_set() or (t is not None and t.is_alive()):
                continue
            try:
                obj.iniciar()
                self.reinicios[nome] = self.reinicios.get(nome, 0) + 1
                self.log(f"cão de guarda: reiniciei {nome}")
            except Exception as e:  # noqa: BLE001 — tenta de novo na próxima volta
                self.log(f"cão de guarda: não consegui reiniciar {nome}: {type(e).__name__}: {e}"[:200])

    def _laco(self):
        while not self.parar.wait(self.intervalo):
            try:
                self.conferir()
            except Exception as e:  # noqa: BLE001 — o cão de guarda também não morre
                self.log(f"cão de guarda: {type(e).__name__}: {e}"[:200])


def _log_padrao(*a):
    """Registro do serviço: no modo --fundo a saída vai para ~/.controle-ir/servico.log."""
    print(time.strftime("%H:%M:%S"), *a, flush=True)
