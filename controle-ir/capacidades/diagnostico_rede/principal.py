"""Diagnóstico de rede para o Termux (sem root, só biblioteca padrão).

Entrada: JSON na entrada padrão. Saída: JSON. Cada medição falha de forma
isolada (ferramenta ausente, permissão): o resto continua.
"""
import json
import os
import re
import shutil
import socket
import statistics
import subprocess
import sys
import time
import urllib.request


def rodar(cmd, t=15):
    if not shutil.which(cmd[0]):
        return None
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=t)
        return r.stdout if r.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def wifi():
    s = rodar(["termux-wifi-connectioninfo"], 12)
    try:
        d = json.loads(s) if s else None
    except ValueError:
        d = None
    if not d:
        return None
    return {k: d.get(k) for k in ("ssid", "rssi", "link_speed_mbps", "frequency_mhz", "ip", "supplicant_state")}


def gateway(ip):
    s = rodar(["ip", "route"], 5) or ""
    m = re.search(r"default via (\d+\.\d+\.\d+\.\d+)", s)
    if m:
        return m.group(1), "rota"
    if ip and re.match(r"\d+\.\d+\.\d+\.\d+$", ip):
        return ".".join(ip.split(".")[:3] + ["1"]), "suposto (x.x.x.1)"
    return None, None


def ping(host, n=10):
    s = rodar(["ping", "-c", str(n), "-i", "0.3", "-W", "2", host], 8 + n)
    if s:
        perda = re.search(r"([\d.]+)% packet loss", s)
        rtt = re.search(r"= ([\d.]+)/([\d.]+)/([\d.]+)", s)
        return {"metodo": "icmp", "perda_pct": float(perda.group(1)) if perda else None,
                "ms_min": float(rtt.group(1)) if rtt else None, "ms_med": float(rtt.group(2)) if rtt else None,
                "ms_max": float(rtt.group(3)) if rtt else None}
    tempos, falhas = [], 0  # sem ping: tempo de conexão TCP
    for porta in (443, 80, 53):
        try:
            t0 = time.monotonic()
            socket.create_connection((host, porta), timeout=2).close()
            tempos.append((time.monotonic() - t0) * 1000)
            for _ in range(4):
                t0 = time.monotonic()
                try:
                    socket.create_connection((host, porta), timeout=2).close()
                    tempos.append((time.monotonic() - t0) * 1000)
                except OSError:
                    falhas += 1
            break
        except OSError:
            continue
    if not tempos:
        return {"metodo": "tcp", "erro": "sem resposta (ICMP indisponível e portas 443/80/53 fechadas)"}
    return {"metodo": f"tcp:{porta}", "perda_pct": round(100 * falhas / (len(tempos) + falhas), 1),
            "ms_min": round(min(tempos), 1), "ms_med": round(statistics.mean(tempos), 1), "ms_max": round(max(tempos), 1)}


def dns():
    out = {}
    for d in ("www.google.com", "claude.ai", "github.com"):
        t0 = time.monotonic()
        try:
            socket.getaddrinfo(d, 443)
            out[d] = round((time.monotonic() - t0) * 1000, 1)
        except OSError as e:
            out[d] = f"falhou: {e}"
    return out


def download(mb):
    url = f"https://speed.cloudflare.com/__down?bytes={mb * 1_000_000}"
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            n = 0
            while True:
                b = r.read(65536)
                if not b:
                    break
                n += len(b)
        s = time.monotonic() - t0
        return {"mbps": round(n * 8 / s / 1e6, 1), "bytes": n, "segundos": round(s, 1)}
    except OSError as e:
        return {"erro": str(e)[:200]}


def analisar(r):
    achados, sugestoes = [], []
    w = r.get("wifi") or {}
    rssi = w.get("rssi")
    if isinstance(rssi, int) and rssi > -127:
        if rssi < -75:
            achados.append(f"sinal Wi-Fi fraco ({rssi} dBm)")
            sugestoes.append("aproxime o celular do roteador ou teste outro cômodo; se houver rede 5 GHz e 2,4 GHz, "
                             "compare as duas (5 GHz é mais rápida e alcança menos)")
        elif rssi < -67:
            achados.append(f"sinal Wi-Fi médio ({rssi} dBm)")
    gw, net = r.get("ping", {}).get("roteador") or {}, r.get("ping", {}).get("1.1.1.1") or {}
    pg, pn = gw.get("perda_pct"), net.get("perda_pct")
    if isinstance(pg, (int, float)) and pg >= 5:
        achados.append(f"perda de {pg}% até o roteador: o problema está no Wi-Fi/roteador, não no provedor")
        sugestoes.append("reinicie o roteador (reversível) e troque o canal do Wi-Fi se houver muitas redes vizinhas")
    elif isinstance(pn, (int, float)) and pn >= 5:
        achados.append(f"roteador ok, mas perda de {pn}% até a internet: provável problema do provedor/ONT")
        sugestoes.append("reinicie a ONT/modem da operadora; se persistir, registre estas medições e acione o provedor")
    if (gw.get("ms_med") or 0) > 30:
        achados.append(f"latência alta até o roteador ({gw['ms_med']} ms): Wi-Fi congestionado ou economia de energia")
    if (net.get("ms_med") or 0) > 120:
        achados.append(f"latência alta até a internet ({net['ms_med']} ms)")
    tempos = [v for v in (r.get("dns") or {}).values() if isinstance(v, (int, float))]
    if tempos and max(tempos) > 300:
        achados.append(f"DNS lento (até {max(tempos)} ms)")
        sugestoes.append("teste o DNS privado do Android (Configurações → Conexão → DNS privado: one.one.one.one); "
                         "para voltar, escolha Automático")
    dl = (r.get("download") or {}).get("mbps")
    link = w.get("link_speed_mbps")
    if isinstance(dl, (int, float)) and isinstance(link, int) and link > 0 and dl < link * 0.15:
        achados.append(f"download ({dl} Mbps) bem abaixo do enlace Wi-Fi ({link} Mbps): gargalo depois do Wi-Fi "
                       "(plano, roteador ou provedor)")
    if not achados:
        achados.append("nenhum problema evidente nesta medição")
    return achados, sugestoes


def main():
    a = json.loads(sys.stdin.read() or "{}")
    r = {"quando": time.strftime("%Y-%m-%d %H:%M:%S"), "rotulo": a.get("rotulo")}
    r["wifi"] = wifi()
    gw, origem = gateway((r["wifi"] or {}).get("ip"))
    r["roteador"] = {"ip": gw, "origem": origem}
    alvos = ([("roteador", gw)] if gw else []) + [("1.1.1.1", "1.1.1.1"), ("8.8.8.8", "8.8.8.8")]
    alvos += [(h, h) for h in a.get("alvos", [])[:5]]
    r["ping"] = {nome: ping(h) for nome, h in alvos}
    r["dns"] = dns()
    if not a.get("rapido"):
        r["download"] = download(max(1, min(int(a.get("megabytes", 10)), 50)))
    r["achados"], r["sugestoes"] = analisar(r)
    pasta = os.path.join(os.environ.get("CONTROLE_IR_DIR", os.path.expanduser("~/.controle-ir")), "medicoes")
    hist = os.path.join(pasta, "rede.jsonl")
    anteriores = []
    try:
        with open(hist) as f:
            anteriores = [json.loads(x) for x in f.readlines()[-3:]]
    except (OSError, ValueError):
        pass
    resumo = lambda m: {"quando": m.get("quando"), "rotulo": m.get("rotulo"),  # noqa: E731
                        "rssi": (m.get("wifi") or {}).get("rssi"),
                        "roteador_ms": ((m.get("ping") or {}).get("roteador") or {}).get("ms_med"),
                        "internet_ms": ((m.get("ping") or {}).get("1.1.1.1") or {}).get("ms_med"),
                        "download_mbps": (m.get("download") or {}).get("mbps")}
    r["anteriores"] = [resumo(m) for m in anteriores]
    try:
        os.makedirs(pasta, exist_ok=True)
        with open(hist, "a") as f:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    except OSError:
        pass
    print(json.dumps(r, ensure_ascii=False))


main()
