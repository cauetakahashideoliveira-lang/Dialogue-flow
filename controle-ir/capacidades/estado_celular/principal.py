"""Estado do celular pelo Termux (sem root). Saída: JSON."""
import json
import os
import shutil
import subprocess
import time


def rodar(cmd, t=12):
    if not shutil.which(cmd[0]):
        return None
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=t)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def js(cmd):
    try:
        return json.loads(rodar(cmd) or "null")
    except ValueError:
        return None


def ler(caminho):
    try:
        with open(caminho) as f:
            return f.read().split()
    except OSError:
        return None


def ligado_ha_horas():
    """Horas desde que o celular ligou. No Android 16 o app não lê /proc/uptime; o relógio CLOCK_BOOTTIME
    (conta também o tempo em repouso) dá o mesmo número sem passar pelo /proc."""
    up = ler("/proc/uptime")
    if up:
        return round(float(up[0]) / 3600, 1)
    try:
        return round(time.clock_gettime(time.CLOCK_BOOTTIME) / 3600, 1)
    except (AttributeError, OSError, ValueError):
        return None


def carga_cpu_1min():
    """Carga média de 1 minuto. Sem /proc/loadavg, tenta getloadavg(); sem leitura devolve None (antes saía 0,
    que parecia um processador ocioso)."""
    la = ler("/proc/loadavg")
    if la:
        return float(la[0])
    try:
        return round(os.getloadavg()[0], 2)
    except (AttributeError, OSError):
        return None


def main():
    home = os.path.expanduser("~")
    du = shutil.disk_usage(home)
    api = ["termux-" + n for n in ("infrared-transmit", "battery-status", "wifi-connectioninfo", "wifi-scaninfo",
                                   "camera-photo", "microphone-record", "sensor", "location", "nfc", "usb",
                                   "speech-to-text", "tts-speak", "notification", "dialog", "job-scheduler",
                                   "toast")]
    print(json.dumps({
        "modelo": rodar(["getprop", "ro.product.model"]),
        "android": rodar(["getprop", "ro.build.version.release"]),
        "bateria": js(["termux-battery-status"]),
        "wifi": js(["termux-wifi-connectioninfo"]),
        "armazenamento_livre_gb": round(du.free / 1e9, 1),
        "ligado_ha_horas": ligado_ha_horas(),
        "carga_cpu_1min": carga_cpu_1min(),
        "termux_api_disponivel": [c for c in api if shutil.which(c)],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
