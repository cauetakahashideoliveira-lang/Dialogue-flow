"""Retrato do PC para o pc_consultar: sistema, CPU, memória, discos, placa de vídeo e programas instalados.

Só biblioteca padrão (ctypes no Windows). O que é caro de medir (placa de vídeo pelo Windows, programas) fica em
cache por alguns minutos; uso de CPU, memória e placa NVIDIA são medidos a cada consulta.
"""
from __future__ import annotations

import ctypes
import glob
import os
import platform
import shutil
import string
import subprocess
import time

WINDOWS = os.name == "nt"
_cache: dict = {}
PROGRAMAS = ("git", "gh", "python", "py", "node", "npm", "claude", "rokit", "rojo", "lune", "stylua", "ollama", "wsl",
             "docker", "nvidia-smi", "winget", "pwsh", "code")


def _rodar(args, timeout=15) -> str:
    try:
        r = subprocess.run(args, capture_output=True, timeout=timeout,
                           creationflags=subprocess.CREATE_NO_WINDOW if WINDOWS else 0)
        return r.stdout.decode("utf-8", errors="replace").strip() if r.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _em_cache(chave, segundos, fn):
    v = _cache.get(chave)
    if v and time.time() - v[0] < segundos:
        return v[1]
    r = fn()
    _cache[chave] = (time.time(), r)
    return r


def memoria() -> dict:
    if WINDOWS:
        class MEM(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        m = MEM()
        m.dwLength = ctypes.sizeof(MEM)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return {"total_gb": round(m.ullTotalPhys / 2**30, 1), "livre_gb": round(m.ullAvailPhys / 2**30, 1),
                "uso_pct": int(m.dwMemoryLoad)}
    try:
        with open("/proc/meminfo") as f:
            info = dict(linha.split(":", 1) for linha in f)
        total = int(info["MemTotal"].split()[0]) * 1024
        livre = int(info["MemAvailable"].split()[0]) * 1024
        return {"total_gb": round(total / 2**30, 1), "livre_gb": round(livre / 2**30, 1),
                "uso_pct": round(100 * (1 - livre / total))}
    except (OSError, KeyError, ValueError):
        return {}


def cpu_uso(janela: float = 0.25) -> float | None:
    """Uso total da CPU (%) numa janela curta."""
    if WINDOWS:
        def tempos():
            ocioso, kernel, usuario = ctypes.c_ulonglong(), ctypes.c_ulonglong(), ctypes.c_ulonglong()
            ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(ocioso), ctypes.byref(kernel), ctypes.byref(usuario))
            return ocioso.value, kernel.value + usuario.value  # kernel já inclui o ocioso
        o1, t1 = tempos()
        time.sleep(janela)
        o2, t2 = tempos()
        return round(100 * (1 - (o2 - o1) / max(1, t2 - t1)), 1)
    try:
        def tempos():
            with open("/proc/stat") as f:
                v = [int(x) for x in f.readline().split()[1:]]
            return v[3] + v[4], sum(v)
        o1, t1 = tempos()
        time.sleep(janela)
        o2, t2 = tempos()
        return round(100 * (1 - (o2 - o1) / max(1, t2 - t1)), 1)
    except (OSError, ValueError):
        return None


def ligado_ha() -> str:
    if WINDOWS:
        ctypes.windll.kernel32.GetTickCount64.restype = ctypes.c_ulonglong
        s = ctypes.windll.kernel32.GetTickCount64() / 1000
    else:
        with open("/proc/uptime") as f:
            s = float(f.read().split()[0])
    d, r = divmod(int(s), 86400)
    return f"{d}d {r // 3600}h{(r % 3600) // 60:02d}"


def discos() -> list:
    letras = [f"{c}:\\" for c in string.ascii_uppercase if os.path.exists(f"{c}:\\")] if WINDOWS else ["/"]
    r = []
    for d in letras:
        try:
            u = shutil.disk_usage(d)
            r.append({"disco": d, "total_gb": round(u.total / 2**30), "livre_gb": round(u.free / 2**30)})
        except OSError:
            pass
    return r


def nvidia() -> list:
    campos = "name,memory.total,memory.used,utilization.gpu,temperature.gpu,power.draw,driver_version"
    txt = _rodar(["nvidia-smi", f"--query-gpu={campos}", "--format=csv,noheader,nounits"], 10)
    gpus = []
    for linha in txt.splitlines():
        v = [x.strip() for x in linha.split(",")]
        if len(v) == 7:
            gpus.append({"nome": v[0], "vram_total_mb": v[1], "vram_usada_mb": v[2], "uso_pct": v[3],
                         "temperatura_c": v[4], "energia_w": v[5], "driver": v[6]})
    if gpus:
        cab = _em_cache("cuda", 3600, lambda: _rodar(["nvidia-smi"], 10))
        if "CUDA Version:" in cab:
            gpus[0]["cuda"] = cab.split("CUDA Version:")[1].split()[0]
    return gpus


def placas_windows() -> list:
    if not WINDOWS:
        return []
    ps = ("Get-CimInstance Win32_VideoController | ForEach-Object { \"$($_.Name)|$($_.DriverVersion)|"
          "$($_.CurrentHorizontalResolution)x$($_.CurrentVerticalResolution)\" }")
    txt = _rodar(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], 20)
    return [dict(zip(("nome", "driver", "resolucao"), linha.split("|"))) for linha in txt.splitlines() if "|" in linha]


def processador() -> str:
    if WINDOWS:
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as k:
                return winreg.QueryValueEx(k, "ProcessorNameString")[0].strip()
        except OSError:
            pass
    try:
        with open("/proc/cpuinfo") as f:
            for linha in f:
                if linha.lower().startswith("model name"):
                    return linha.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor()


def programas() -> dict:
    r = {p: bool(shutil.which(p)) for p in PROGRAMAS}
    if WINDOWS and os.environ.get("LOCALAPPDATA"):
        studio = glob.glob(os.path.join(os.environ["LOCALAPPDATA"], "Roblox", "Versions", "*", "RobloxStudioBeta.exe"))
        r["roblox_studio"] = studio[0] if studio else False
    return r


def retrato() -> dict:
    estatico = _em_cache("estatico", 600, lambda: {
        "nome": platform.node(), "sistema": f"{platform.system()} {platform.release()} ({platform.version()})",
        "processador": processador(), "nucleos": os.cpu_count(), "placas": placas_windows(),
        "usuario": os.environ.get("USERNAME") or os.environ.get("USER")})
    return {**estatico, "ligado_ha": ligado_ha(), "cpu_uso_pct": cpu_uso(), "memoria": memoria(), "discos": discos(),
            "nvidia": nvidia(), "programas": _em_cache("programas", 300, programas)}
