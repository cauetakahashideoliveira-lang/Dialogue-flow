"""Comandos no PC como tarefas numeradas: rodam em segundo plano, a saída fica num arquivo e o Claude acompanha.

- PowerShell (padrão no Windows), cmd, pwsh ou bash. O script do PowerShell vai para um .ps1 (UTF-8 com BOM) e
  roda com -File: sem limite de tamanho da linha de comando e sem problema de aspas.
- Saída em UTF-8 sempre que o programa permitir (PowerShell e Python forçados); o resto é decodificado com
  a página de código do console como reserva.
- Parar encerra a árvore inteira de processos (taskkill /T no Windows, grupo de processos no Linux).
"""
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import threading
import time
from pathlib import Path

WINDOWS = os.name == "nt"
SAIDA_MAX = 12000  # bytes de saída devolvidos por chamada (o resto: tarefa(desde=...))
GUARDAR = 300  # tarefas mantidas no histórico
PREFIXO_PS = ("$ProgressPreference='SilentlyContinue'\n"
              "try { [Console]::OutputEncoding = [Text.Encoding]::UTF8; $OutputEncoding = [Text.Encoding]::UTF8 } catch {}\n")


def _sem_janela() -> int:
    return (subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP) if WINDOWS else 0


def preparar(comando: str, shell: str | None, script_ps: Path):
    """Devolve (argumentos, usa_texto) para o Popen. Lança ValueError se o shell não existir."""
    shell = (shell or ("powershell" if WINDOWS else "sh")).lower()
    if shell in ("powershell", "pwsh"):
        exe = shutil.which("pwsh") if shell == "pwsh" else (shutil.which("powershell") or shutil.which("pwsh"))
        if not exe:
            raise ValueError(f"{shell} não encontrado neste PC")
        script_ps.write_text(PREFIXO_PS + comando, encoding="utf-8-sig")
        return [exe, "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(script_ps)]
    if shell == "cmd":
        if not WINDOWS:
            raise ValueError("cmd só existe no Windows")
        # string, não lista: o cmd não entende as aspas escapadas com \ do list2cmdline
        return f'cmd.exe /d /s /c "chcp 65001>nul & {comando}"'
    if shell == "bash":
        exe = shutil.which("bash")
        if not exe:
            raise ValueError("bash não encontrado (instale o Git for Windows ou o WSL)")
        return [exe, "-lc", comando]
    if shell == "sh" and not WINDOWS:
        return ["/bin/sh", "-c", comando]
    raise ValueError(f"shell desconhecido: {shell} (use powershell, pwsh, cmd ou bash)")


def decodificar(dados: bytes) -> str:
    try:
        return dados.decode("utf-8")
    except UnicodeDecodeError:
        return dados.decode("cp850" if WINDOWS else "latin-1", errors="replace")


def matar_arvore(pid: int) -> None:
    if WINDOWS:
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)
        return
    try:
        os.killpg(pid, signal.SIGTERM)
        time.sleep(1)
        os.killpg(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


class Tarefas:
    def __init__(self, pasta: Path, auditar=None):
        self.dir = Path(pasta) / "tarefas"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.auditar = auditar or (lambda r: None)
        self.trava = threading.Lock()
        self.tarefas: dict[str, dict] = {}
        self.procs: dict[str, subprocess.Popen] = {}
        self.fim: dict[str, threading.Event] = {}
        self._carregar()

    def _carregar(self):
        for f in sorted(self.dir.glob("*.json"), key=lambda x: int(x.stem) if x.stem.isdigit() else 0):
            try:
                t = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if t.get("status") == "rodando":  # o agente reiniciou com ela rodando: o processo ficou órfão
                t["status"] = "perdida"
            self.tarefas[t["id"]] = t
        self.proximo = 1 + max([int(i) for i in self.tarefas if i.isdigit()] or [0])
        for i in sorted(self.tarefas, key=int)[:-GUARDAR]:
            self._apagar(i)

    def _apagar(self, ident):
        self.tarefas.pop(ident, None)
        for ext in (".json", ".log", ".ps1"):
            (self.dir / f"{ident}{ext}").unlink(missing_ok=True)

    def _salvar(self, t: dict):
        (self.dir / f"{t['id']}.json").write_text(json.dumps(t, ensure_ascii=False), encoding="utf-8")

    # ------------------------------------------------------------- execução
    def pedir(self, comando: str, shell: str | None = None, pasta: str | None = None, aguardar: float = 30,
              tempo_limite: float = 600, motivo: str | None = None, env: dict | None = None) -> dict:
        comando = str(comando or "").strip()
        if not comando:
            raise ValueError("comando vazio")
        pasta = os.path.expandvars(os.path.expanduser(pasta)) if pasta else str(Path.home())
        if not os.path.isdir(pasta):
            raise ValueError(f"pasta não existe: {pasta}")
        tempo_limite = max(1.0, min(float(tempo_limite or 600), 86400.0))
        with self.trava:
            ident = str(self.proximo)
            self.proximo += 1
        args = preparar(comando, shell, self.dir / f"{ident}.ps1")
        t = {"id": ident, "comando": comando[:2000], "shell": shell or ("powershell" if WINDOWS else "sh"),
             "pasta": pasta, "motivo": (motivo or "")[:200], "inicio": time.time(), "status": "rodando",
             "tempo_limite": tempo_limite}
        ambiente = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1", **(env or {})}
        log = open(self.dir / f"{ident}.log", "wb")
        try:
            p = subprocess.Popen(args, cwd=pasta, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                 env=ambiente, creationflags=_sem_janela(), start_new_session=not WINDOWS)
        except OSError as e:
            log.close()
            t.update(status="erro", erro=str(e)[:300], fim=time.time())
            self.tarefas[ident] = t
            self._salvar(t)
            return self.resumo(t)
        t["pid"] = p.pid
        with self.trava:
            self.tarefas[ident], self.procs[ident], self.fim[ident] = t, p, threading.Event()
        self._salvar(t)
        self.auditar({"evento": "pc_comando", "id": ident, "comando": comando[:300], "motivo": t["motivo"]})
        threading.Thread(target=self._vigiar, args=(ident, p, log, tempo_limite), name=f"tarefa-{ident}",
                         daemon=True).start()
        self.fim[ident].wait(max(0.0, min(float(aguardar if aguardar is not None else 30), 55.0)))
        return self.resumo(t)

    def _vigiar(self, ident: str, p: subprocess.Popen, log, tempo_limite: float):
        t = self.tarefas[ident]
        try:
            codigo = p.wait(timeout=tempo_limite)
            if t["status"] == "rodando":
                t["status"] = "concluida" if codigo == 0 else "falhou"
        except subprocess.TimeoutExpired:
            matar_arvore(p.pid)
            codigo = p.wait()
            t["status"] = "tempo_esgotado"
        finally:
            log.close()
        t.update(codigo=codigo, fim=time.time())
        self._salvar(t)
        with self.trava:
            self.procs.pop(ident, None)
            ev = self.fim.pop(ident, None)
        (self.dir / f"{ident}.ps1").unlink(missing_ok=True)
        if ev:
            ev.set()

    # ------------------------------------------------------------- consulta e controle
    def saida(self, ident: str, desde: int | None = None, maximo: int = SAIDA_MAX) -> dict:
        arq = self.dir / f"{ident}.log"
        try:
            tam = arq.stat().st_size
        except OSError:
            return {"texto": "", "total_bytes": 0, "ate": 0}
        inicio = max(0, tam - maximo) if desde is None else max(0, min(int(desde), tam))
        with open(arq, "rb") as f:
            f.seek(inicio)
            dados = f.read(maximo)
        corte = 0
        while corte < min(4, len(dados)) and dados[corte] & 0xC0 == 0x80:  # não começa no meio de um caractere
            corte += 1
        r = {"texto": decodificar(dados[corte:]), "total_bytes": tam, "ate": inicio + len(dados)}
        if inicio > 0:
            r["cortado_inicio"] = inicio
        if inicio + len(dados) < tam:
            r["mais"] = f"há mais saída: pc_tarefa(id='{ident}', desde={inicio + len(dados)})"
        return r

    def resumo(self, t: dict, desde: int | None = None) -> dict:
        r = {k: t.get(k) for k in ("id", "status", "codigo", "pid", "shell", "pasta", "erro") if t.get(k) is not None}
        fim = t.get("fim") or time.time()
        r["duracao_s"] = round(fim - t["inicio"], 1)
        r["comando"] = t["comando"][:300]
        r["saida"] = self.saida(t["id"], desde)
        if t["status"] == "rodando":
            r["dica"] = f"continua rodando: pc_tarefa(id='{t['id']}', aguardar=55) para acompanhar"
        return r

    def ver(self, ident: str, desde: int | None = None, aguardar: float = 0) -> dict:
        t = self.tarefas.get(str(ident))
        if not t:
            raise ValueError(f"tarefa {ident} não existe")
        ev = self.fim.get(str(ident))
        if ev and aguardar:
            ev.wait(max(0.0, min(float(aguardar), 55.0)))
        return self.resumo(t, desde)

    def listar(self, maximo: int = 20) -> list:
        ids = sorted(self.tarefas, key=int)[-maximo:]
        return [{"id": i, "status": self.tarefas[i]["status"], "comando": self.tarefas[i]["comando"][:120],
                 "inicio": time.strftime("%d/%m %H:%M:%S", time.localtime(self.tarefas[i]["inicio"]))}
                for i in reversed(ids)]

    def ativas(self) -> list:
        return [t for t in self.tarefas.values() if t["status"] == "rodando"]

    def parar(self, ident: str) -> dict:
        ident = str(ident)
        p = self.procs.get(ident)
        t = self.tarefas.get(ident)
        if not t:
            raise ValueError(f"tarefa {ident} não existe")
        if p:
            t["status"] = "parada"
            matar_arvore(p.pid)
            ev = self.fim.get(ident)
            if ev:
                ev.wait(10)
            self.auditar({"evento": "pc_tarefa_parada", "id": ident})
        return self.resumo(t)

    def parar_todas(self) -> int:
        ids = list(self.procs)
        for i in ids:
            try:
                self.parar(i)
            except ValueError:
                pass
        return len(ids)
