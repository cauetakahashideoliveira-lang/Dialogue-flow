"""Linha de comando do agente do PC.

  python -m agente_pc parear <URL-da-Central> <CÓDIGO> [--nome NOME]
  python -m agente_pc ligar          (o serviço: a tarefa agendada roda isto no logon)
  python -m agente_pc estado
  python -m agente_pc desligar       (encerra o serviço sem que a tarefa o reabra)
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import threading
import time
import urllib.request

from controle_ir import painel
from controle_ir.canal import Canal

from . import __version__, config
from .ferramentas import Ferramentas
from .servidor import Guardiao, ServidorMCP, criar_servidor


class CanalPC(Canal):
    """O canal do celular, com o laço blindado: uma falha inesperada reinicia o laço em vez de matar a conexão."""

    def _laco(self):
        while not self.parar.is_set():
            try:
                super()._laco()
            except Exception as e:  # noqa: BLE001
                self.ultimo_erro = f"{type(e).__name__}: {e}"[:160]
                self.log("canal: laço reiniciado depois de", self.ultimo_erro)
                self.parar.wait(5)


def log(*a):
    print(time.strftime("%Y-%m-%d %H:%M:%S"), *a, flush=True)


def parear(a) -> int:
    pasta = config.pasta()
    try:
        painel.parear(pasta, a.url, a.codigo, a.nome or platform.node() or "PC", __version__)
    except ValueError as e:
        print(f"✘ {e}")
        return 1
    print("✔ PC pareado com a Central de Controle (desarmado). Arme pela Central, com a digital, para usar.")
    try:
        print("  estado:", json.dumps(painel.sincronizar(pasta, __version__), ensure_ascii=False))
    except Exception as e:  # noqa: BLE001
        print(f"  aviso: primeira sincronização falhou ({e}); o serviço tenta de novo a cada 30 s")
    return 0


def estado(_a) -> int:
    pasta = config.pasta()
    cfg = config.ler(pasta)
    g = Guardiao(pasta, lambda: config.ler(pasta), lambda c: config.gravar(c, pasta))
    saude = None
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{cfg['porta']}/saude", timeout=3) as r:
            saude = json.loads(r.read())
    except OSError:
        pass
    p = painel.ler(pasta) or {}
    print(json.dumps({"versao": __version__, "pasta": str(pasta), "porta": cfg["porta"], "servico": saude,
                      "central": p.get("url"), "aparelho": p.get("aparelho"), "seguranca": g.estado()},
                     ensure_ascii=False, indent=1))
    return 0


def desligar(_a) -> int:
    pasta = config.pasta()
    (pasta / "DESLIGAR").write_text(str(time.time()))
    print("pedido de desligar registrado: o serviço encerra em até 5 s e não volta até o próximo 'ligar'")
    return 0


def manter_acordado() -> bool:
    """Windows: impede a suspensão enquanto o agente roda (como um player de vídeo); a tela ainda pode apagar."""
    if os.name != "nt":
        return False
    import ctypes
    ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
    return bool(ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED))


def ligar(_a) -> int:
    pasta = config.pasta()
    (pasta / "DESLIGAR").unlink(missing_ok=True)
    cfg = config.ler(pasta)
    g = Guardiao(pasta, lambda: config.ler(pasta), lambda c: config.gravar(c, pasta))
    canal_ref = {}

    class CanalPreguicoso:  # a ferramenta consulta o canal que só existe depois do servidor
        def estado(self):
            c = canal_ref.get("c")
            return c.estado() if c else {"conectado": False, "nota": "PC não pareado"}

    def canal_resumo():  # leve (sem medir ida e volta): é o que o /saude mostra
        c = canal_ref.get("c")
        if not c:
            return {"conectado": False, "erro": "PC não pareado"}
        return {"conectado": bool(c.conectado), **({"erro": c.ultimo_erro} if c.ultimo_erro and not c.conectado else {})}

    ferramentas = Ferramentas(pasta, g.auditar, g.estado, g.travar, canal=CanalPreguicoso())
    srv = criar_servidor(pasta, int(cfg["porta"]), cfg["segredo"], ServidorMCP(ferramentas, g), g, canal=canal_resumo)
    threading.Thread(target=srv.serve_forever, name="http", daemon=True).start()
    log(f"agente {__version__} em 127.0.0.1:{cfg['porta']} (pasta {pasta})"
        + ("; PC mantido acordado enquanto o agente roda" if manter_acordado() else ""))
    g.auditar({"evento": "pc_agente_ligado", "versao": __version__})

    def reduzir(motivo):
        n = ferramentas.tarefas.parar_todas()
        g.auditar({"evento": "reduzido_pelo_painel", "motivo": motivo, "tarefas_encerradas": n})
        log("Central:", motivo, f"({n} tarefas encerradas)")

    def em_uso(_observar, _ao_vivo):
        return {"itens": [{"tipo": "terminal", "desc": t["comando"][:80]} for t in ferramentas.tarefas.ativas()]}

    if painel.ler(pasta):
        sinc = painel.Sincronizador(pasta, __version__, reduzir, log=log, em_uso=em_uso).iniciar()
        canal_ref["c"] = CanalPC(pasta, int(cfg["porta"]), cfg["segredo"], ao_sincronizar=sinc.acordar, log=log).iniciar()
        sinc.ao_ver_canal = canal_ref["c"].acordar
    else:
        log("PC ainda não pareado: rode 'python -m agente_pc parear <URL> <CÓDIGO>' e reinicie")
    ultimo_relato, ultimo_erro, fora_desde = 0.0, "", None
    while not (pasta / "DESLIGAR").exists():
        time.sleep(5)
        c = canal_ref.get("c")
        if not c:
            continue
        if c.conectado:
            if fora_desde:
                log(f"canal de volta depois de {int(time.time() - fora_desde)} s fora")
            fora_desde = None
            continue
        fora_desde = fora_desde or time.time()
        if c.ultimo_erro and c.ultimo_erro != ultimo_erro:  # cada motivo novo de queda vai para o registro
            ultimo_erro = c.ultimo_erro
            log("canal caiu:", ultimo_erro)
        if time.time() - fora_desde > 60:  # fora há mais de 1 min: tenta de novo agora (pula a espera longa)
            c.acordar()
        if time.time() - ultimo_relato > 300:
            ultimo_relato = time.time()
            log(f"canal desconectado da Central há {int(time.time() - fora_desde)} s:", c.ultimo_erro or "tentando")
    ferramentas.tarefas.parar_todas()
    log("desligado a pedido")
    return 0


def main(argv=None) -> int:
    if os.environ.get("AGENTE_PC_LOG"):  # serviço sem console (iniciar.ps1): registro em UTF-8 num arquivo
        sys.stdout = sys.stderr = open(os.environ["AGENTE_PC_LOG"], "a", encoding="utf-8", buffering=1)
    elif hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(prog="agente_pc", description="Agente do PC para a Central de Controle")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("parear")
    p.add_argument("url")
    p.add_argument("codigo")
    p.add_argument("--nome")
    sub.add_parser("ligar")
    sub.add_parser("estado")
    sub.add_parser("desligar")
    a = ap.parse_args(argv)
    return {"parear": parear, "ligar": ligar, "estado": estado, "desligar": desligar}[a.cmd](a)

