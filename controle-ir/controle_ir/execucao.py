"""Execução governada de comandos no aparelho (o "nó").

O Claude pede, o aparelho concede: a política só muda no próprio aparelho
(linha de comando ou botões da notificação), nunca pelo MCP.

Classes de ação e modo padrão:
* ``leitura``  — programas que só leem (ls, cat, getprop, termux-battery-status…)  → permitir
* ``rede``     — ping, curl, nmap, dig, iperf3…                                   → perguntar
* ``pacotes``  — pkg, apt, pip, npm                                                → perguntar
* ``sistema``  — atualizar o próprio controle-ir                                   → perguntar
* ``livre``    — todo o resto, ou qualquer linha com ; | & $ ` < > ( ) { }        → perguntar
Modos: ``permitir`` | ``perguntar`` (notificação Executar/Negar/Liberar 30 min) | ``negar``.
``liberado_ate`` transforma "perguntar" em "permitir" até a hora marcada (exceto sistema);
``travado`` nega tudo e encerra o que estiver rodando.

Cada pedido vira uma tarefa com número, registro em disco e saída em arquivo, e
entra no histórico de auditoria (``auditoria.jsonl``).
"""
from __future__ import annotations

import json
import os
import shlex
import shutil
import signal
import subprocess
import threading
import time
from pathlib import Path

CLASSES = ("leitura", "rede", "pacotes", "sistema", "livre")
PADRAO = {"leitura": "permitir", "rede": "perguntar", "pacotes": "perguntar", "sistema": "perguntar",
          "livre": "perguntar"}
LEITURA = {"ls", "cat", "head", "tail", "wc", "pwd", "whoami", "id", "uname", "uptime", "date", "df", "du",
           "free", "ps", "which", "file", "stat", "grep", "getprop", "ip", "termux-info", "termux-battery-status",
           "termux-wifi-connectioninfo", "termux-wifi-scaninfo", "termux-sensor", "termux-infrared-frequencies",
           "termux-telephony-cellinfo", "termux-audio-info", "termux-volume", "nproc", "lscpu", "getconf"}
REDE = {"ping", "traceroute", "tracepath", "mtr", "nmap", "dig", "nslookup", "host", "curl", "wget", "iperf3",
        "nc", "ncat", "whois", "speedtest-cli", "arp", "ss", "netstat"}
PACOTES = {"pkg", "apt", "apt-get", "pip", "pip3", "npm", "dpkg"}
LEITURA_PACOTES = {("pkg", "list-installed"), ("pkg", "search"), ("pkg", "show"), ("pip", "list"),
                   ("pip3", "list"), ("pip", "show"), ("apt", "list"), ("dpkg", "-l")}
META = set(";|&$`<>(){}\n\\")
LIMITE_SAIDA = 1_000_000
MAX_TEMPO = 3600


def classificar(comando: str) -> str:
    if any(c in META for c in comando):
        return "livre"
    try:
        partes = shlex.split(comando)
    except ValueError:
        return "livre"
    if not partes:
        return "livre"
    prog = os.path.basename(partes[0])
    if prog in LEITURA and not (prog == "grep" and any(a in ("-r", "-R") for a in partes)):
        return "leitura"
    if prog in PACOTES:
        return "leitura" if tuple(partes[:2]) in LEITURA_PACOTES else "pacotes"
    if prog in REDE:
        return "rede"
    return "livre"


class Politica:
    def __init__(self, pasta: Path):
        self.arq = Path(pasta) / "politica.json"

    def ler(self) -> dict:
        try:
            p = json.loads(self.arq.read_text())
        except (OSError, ValueError):
            p = {}
        p["classes"] = {**PADRAO, **{k: v for k, v in (p.get("classes") or {}).items() if k in CLASSES}}
        p.setdefault("travado", False)
        p.setdefault("liberado_ate", 0)
        return p

    def gravar(self, p: dict):
        self.arq.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.arq.with_suffix(".novo")
        tmp.write_text(json.dumps(p, indent=1))
        os.chmod(tmp, 0o600)
        os.replace(tmp, self.arq)

    def decidir(self, classe: str) -> str:
        p = self.ler()
        if p["travado"]:
            return "negar"
        modo = p["classes"].get(classe, "perguntar")
        if modo == "perguntar" and classe != "sistema" and time.time() < float(p["liberado_ate"] or 0):
            return "permitir"
        return modo

    def resumo(self) -> dict:
        p = self.ler()
        lib = float(p["liberado_ate"] or 0)
        return {"travado": p["travado"], "classes": p["classes"],
                "liberado_ate": time.strftime("%H:%M", time.localtime(lib)) if lib > time.time() else None,
                "como_mudar": "só no celular: controle-ir exec classe <classe> permitir|perguntar|negar · "
                              "controle-ir exec liberar <minutos> · controle-ir exec travar|destravar"}


class Execucao:
    def __init__(self, pasta: Path, notificar=None):
        self.pasta = Path(pasta)
        self.dir = self.pasta / "tarefas"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.politica = Politica(self.pasta)
        self.notificar = notificar or (lambda ev: None)
        self.trava = threading.Lock()
        self.eventos: dict[str, threading.Event] = {}
        self.procs: dict[str, subprocess.Popen] = {}
        for f in self.dir.glob("*.json"):  # o serviço reiniciou: o que rodava foi interrompido
            try:
                t = json.loads(f.read_text())
                if t.get("status") in ("executando", "aguardando_aprovacao"):
                    t["status"] = "interrompida"
                    f.write_text(json.dumps(t, ensure_ascii=False))
            except (OSError, ValueError):
                pass

    # ------------------------------------------------------------- registro
    def _salvar(self, t: dict):
        (self.dir / f"{t['id']}.json").write_text(json.dumps(t, ensure_ascii=False))

    def _ler(self, ident: str) -> dict:
        try:
            return json.loads((self.dir / f"{ident}.json").read_text())
        except (OSError, ValueError):
            raise KeyError(f"tarefa {ident} não encontrada") from None

    def auditar(self, registro: dict):
        with self.trava:
            with open(self.pasta / "auditoria.jsonl", "a") as f:
                f.write(json.dumps({"quando": time.strftime("%Y-%m-%d %H:%M:%S"), **registro},
                                   ensure_ascii=False, default=str)[:4000] + "\n")

    def _novo_id(self) -> str:
        with self.trava:
            n = 1 + max([int(f.stem) for f in self.dir.glob("*.json") if f.stem.isdigit()] or [0])
            (self.dir / f"{n}.json").write_text("{}")
            return str(n)

    # ------------------------------------------------------------- pedido
    def pedir(self, comando: str, aguardar: float = 30, tempo_limite: float = 120, pasta: str | None = None,
              classe: str | None = None, motivo: str | None = None) -> dict:
        comando = str(comando or "").strip()
        if not comando:
            raise ValueError("comando vazio")
        classe = classe or classificar(comando)
        decisao = self.politica.decidir(classe)
        t = {"id": self._novo_id(), "comando": comando, "classe": classe, "motivo": motivo,
             "pasta": pasta or str(Path.home()), "tempo_limite": max(1, min(float(tempo_limite or 120), MAX_TEMPO)),
             "criada": time.time(), "decisao": decisao}
        self.auditar({"evento": "pedido", "tarefa": t["id"], "classe": classe, "decisao": decisao,
                      "comando": comando[:500]})
        if decisao == "negar":
            t["status"] = "negada"
            self._salvar(t)
            return self._publico(t, extra={"orientacao": "A política do celular nega esta classe agora."})
        ev = threading.Event()
        self.eventos[t["id"]] = ev
        if decisao == "permitir":
            t["status"] = "executando"
            self._salvar(t)
            self._iniciar(t)
        else:
            t["status"] = "aguardando_aprovacao"
            self._salvar(t)
            self.notificar({"tipo": "exec_aprovacao", "id": t["id"], "classe": classe, "comando": comando,
                            "motivo": motivo})
        ev.wait(max(0.0, min(float(aguardar or 0), 55)))
        return self.estado(t["id"])

    def decidir(self, ident: str, aprovar: bool) -> dict:
        t = self._ler(ident)
        if t.get("status") != "aguardando_aprovacao":
            return self._publico(t)
        t["decisao"] = "aprovada" if aprovar else "negada_no_celular"
        self.auditar({"evento": "decisao", "tarefa": ident, "decisao": t["decisao"]})
        if aprovar:
            t["status"] = "executando"
            self._salvar(t)
            self._iniciar(t)
        else:
            t["status"] = "negada"
            self._salvar(t)
            self.eventos.get(ident, threading.Event()).set()
        return self._publico(t)

    # ------------------------------------------------------------- execução
    def _iniciar(self, t: dict):
        threading.Thread(target=self._rodar, args=(t,), name=f"tarefa-{t['id']}", daemon=True).start()

    def _rodar(self, t: dict):
        saida = self.dir / f"{t['id']}.log"
        shell = shutil.which("bash") or shutil.which("sh") or "/bin/sh"
        t["inicio"] = time.time()
        try:
            with open(saida, "wb") as f:
                p = subprocess.Popen([shell, "-c", t["comando"]], stdout=f, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL, cwd=t["pasta"], start_new_session=True)
                self.procs[t["id"]] = p
                try:
                    t["codigo"] = p.wait(timeout=t["tempo_limite"])
                    t["status"] = "concluida" if t["codigo"] == 0 else "falhou"
                except subprocess.TimeoutExpired:
                    self._matar(p)
                    t["status"] = "tempo_esgotado"
        except OSError as e:
            t["status"], t["erro"] = "falhou", str(e)
        finally:
            self.procs.pop(t["id"], None)
        atual = self._ler(t["id"])
        if atual.get("status") == "parada":
            t["status"] = "parada"
        t["fim"] = time.time()
        self._salvar(t)
        self.auditar({"evento": "fim", "tarefa": t["id"], "status": t["status"], "codigo": t.get("codigo"),
                      "segundos": round(t["fim"] - t["inicio"], 1)})
        self.eventos.get(t["id"], threading.Event()).set()

    @staticmethod
    def _matar(p: subprocess.Popen):
        try:
            os.killpg(p.pid, signal.SIGTERM)
            p.wait(timeout=3)
        except (OSError, subprocess.TimeoutExpired):
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except OSError:
                pass

    def parar(self, ident: str) -> dict:
        t = self._ler(ident)
        p = self.procs.get(ident)
        if t.get("status") == "aguardando_aprovacao":
            return self.decidir(ident, False)
        if p:
            t["status"] = "parada"
            self._salvar(t)
            self._matar(p)
            self.auditar({"evento": "parada", "tarefa": ident})
        return self.estado(ident)

    def parar_todas(self) -> int:
        n = 0
        for ident in list(self.procs):
            self.parar(ident)
            n += 1
        for f in self.dir.glob("*.json"):
            try:
                if json.loads(f.read_text()).get("status") == "aguardando_aprovacao":
                    self.decidir(f.stem, False)
            except (OSError, ValueError):
                pass
        return n

    # ------------------------------------------------------------- consulta
    def _publico(self, t: dict, linhas: int = 60, extra: dict | None = None) -> dict:
        out = {k: t.get(k) for k in ("id", "comando", "classe", "status", "codigo", "decisao", "erro") if t.get(k)
               is not None}
        if t.get("inicio"):
            out["segundos"] = round((t.get("fim") or time.time()) - t["inicio"], 1)
        log = self.dir / f"{t.get('id')}.log"
        if log.exists():
            with open(log, "rb") as f:
                f.seek(max(0, log.stat().st_size - 16000))
                txt = f.read().decode("utf-8", "replace")
            out["saida"] = "\n".join(txt.splitlines()[-max(1, int(linhas)):])
            out["saida_bytes"] = log.stat().st_size
        if t.get("status") == "aguardando_aprovacao":
            out["orientacao"] = ("Aguardando o usuário tocar em Executar na notificação do celular. Consulte de novo "
                                 f"com tarefa(id='{t['id']}').")
        elif t.get("status") == "executando":
            out["orientacao"] = f"Ainda rodando; acompanhe com tarefa(id='{t['id']}') ou pare com parar=true."
        return {**out, **(extra or {})}

    def estado(self, ident: str, linhas: int = 60) -> dict:
        return self._publico(self._ler(str(ident)), linhas)

    def listar(self, n: int = 10) -> list[dict]:
        ts = []
        for f in self.dir.glob("*.json"):
            try:
                t = json.loads(f.read_text())
                if t.get("id"):
                    ts.append(t)
            except (OSError, ValueError):
                pass
        ts.sort(key=lambda t: -int(t["id"]))
        return [{k: t.get(k) for k in ("id", "comando", "classe", "status", "codigo")} for t in ts[:n]]
