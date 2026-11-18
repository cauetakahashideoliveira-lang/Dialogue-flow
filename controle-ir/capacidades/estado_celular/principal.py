"""Estado do celular pelo Termux (sem root). Saída: JSON."""
import json
import os
import shutil
import subprocess


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


home = os.path.expanduser("~")
du = shutil.disk_usage(home)
up = ler("/proc/uptime")
api = ["termux-" + n for n in ("infrared-transmit", "battery-status", "wifi-connectioninfo", "wifi-scaninfo",
                               "camera-photo", "microphone-record", "sensor", "location", "nfc", "usb",
                               "speech-to-text", "tts-speak", "notification", "dialog", "job-scheduler", "toast")]
print(json.dumps({
    "modelo": rodar(["getprop", "ro.product.model"]),
    "android": rodar(["getprop", "ro.build.version.release"]),
    "bateria": js(["termux-battery-status"]),
    "wifi": js(["termux-wifi-connectioninfo"]),
    "armazenamento_livre_gb": round(du.free / 1e9, 1),
    "ligado_ha_horas": round(float(up[0]) / 3600, 1) if up else None,
    "carga_cpu_1min": float((ler("/proc/loadavg") or [0])[0]),
    "termux_api_disponivel": [c for c in api if shutil.which(c)],
}, ensure_ascii=False))
