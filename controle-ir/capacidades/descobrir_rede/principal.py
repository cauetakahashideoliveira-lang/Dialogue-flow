"""Inventário da rede local, só leitura, em Python puro. Entrada: JSON no stdin. Saída: JSON."""
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

PORTAS = [22, 53, 80, 443, 554, 1900, 5000, 6668, 8001, 8002, 8008, 8009, 8080, 8443, 9000, 9100, 9197, 55000]
ARQUIVO = os.path.join(os.path.expanduser("~"), ".controle-ir", "medicoes", "inventario.json")


def classificar(portas, upnp=None, gree=False, midea=False, e_gateway=False, e_este=False):
    """Palpite do tipo de aparelho. Devolve (tipo, motivo)."""
    p = set(portas)
    if e_este:
        return "este celular", "IP do próprio celular"
    if e_gateway or (upnp or {}).get("tipo", "").endswith("InternetGatewayDevice:1"):
        return "roteador", (upnp or {}).get("modelo") or "gateway da rede"
    if gree:
        return "ar-condicionado (Gree)", "respondeu ao scan UDP 7000"
    if midea:
        return "ar-condicionado (Midea/Carrier)", "respondeu ao UDP 6445"
    if p & {8001, 8002, 55000}:
        return "TV (Samsung/Tizen provável)", "portas 8001/8002/55000"
    if p & {8008, 8009}:
        return "Chromecast/Google TV provável", "portas 8008/8009"
    if 9100 in p:
        return "impressora provável", "porta 9100"
    if 554 in p:
        return "câmera IP provável", "RTSP (554) aberto"
    if 6668 in p:
        return "aparelho Tuya provável", "porta 6668"
    if p & {80, 443, 8080, 8443}:
        return "aparelho com página web", "HTTP/HTTPS aberto"
    if 22 in p:
        return "computador/servidor provável", "SSH aberto"
    return "não identificado", "nenhuma porta comum aberta"


def tcp(ip, porta, t=0.6):
    try:
        with socket.create_connection((ip, porta), timeout=t):
            return True
    except OSError:
        return False


def udp(ip, porta, dados, t=1.2):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(t)
    try:
        s.sendto(dados, (ip, porta))
        return s.recvfrom(4096)[0]
    except OSError:
        return None
    finally:
        s.close()


def ip_do_wifi():
    try:
        r = subprocess.run(["termux-wifi-connectioninfo"], capture_output=True, text=True, timeout=10)
        return json.loads(r.stdout).get("ip")
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def ssdp():
    """{ip: {'location': url}} dos que respondem ao anúncio geral."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1)
    achados = {}
    try:
        s.sendto(b'M-SEARCH * HTTP/1.1\r\nHOST:239.255.255.250:1900\r\nMAN:"ssdp:discover"\r\nMX:2\r\nST:ssdp:all\r\n\r\n',
                 ("239.255.255.250", 1900))
        fim = time.time() + 3
        while time.time() < fim:
            d, a = s.recvfrom(2048)
            m = re.search(r"LOCATION:\s*(\S+)", d.decode(errors="ignore"), re.I)
            achados.setdefault(a[0], {"location": m.group(1) if m else None})
    except OSError:
        pass
    finally:
        s.close()
    return achados


def ficha_upnp(url):
    try:
        with urllib.request.urlopen(url, timeout=4) as r:
            x = r.read(60000).decode(errors="ignore")
    except (OSError, ValueError):
        return {}
    def tag(n):
        m = re.search(r"<%s>([^<]*)" % n, x)
        return m.group(1).strip() if m else ""
    return {"tipo": tag("deviceType"), "modelo": " ".join(filter(None, [tag("manufacturer"), tag("modelName")]))}


def sondar(ip, com_udp):
    abertas = [p for p in PORTAS if tcp(ip, p)]
    gree = bool(com_udp and udp(ip, 7000, b'{"t":"scan"}'))
    midea = bool(com_udp and udp(ip, 6445, b"\x5a\x5a\x01\x11\x48\x00\x92\x00"))
    return ip, abertas, gree, midea


def vivos(base):
    """Hosts que aceitam conexão em alguma porta comum ou respondem UDP (sem root, sem ping)."""
    def vivo(ip):
        return ip if any(tcp(ip, p, 0.35) for p in (80, 443, 554, 53, 22, 8080, 8001, 9000, 5000, 62078)) else None
    with ThreadPoolExecutor(64) as ex:
        return sorted(filter(None, ex.map(vivo, ["%s.%d" % (base, i) for i in range(1, 255)])),
                      key=lambda i: int(i.rsplit(".", 1)[1]))


def main():
    arg = json.loads(sys.stdin.read() or "{}")
    meu = ip_do_wifi()
    base = arg.get("sub_rede") or (meu.rsplit(".", 1)[0] if meu else None)
    if not base:
        print(json.dumps({"erro": "sem Wi-Fi: informe sub_rede (ex.: 192.168.5)"}, ensure_ascii=False))
        return
    com_udp = arg.get("udp", True)
    gateway = base + ".1"
    candidatos = set(vivos(base)) | {gateway}
    if meu:
        candidatos.add(meu)
    anuncios = ssdp()
    candidatos |= set(a for a in anuncios if a.startswith(base + "."))
    with ThreadPoolExecutor(16) as ex:
        sondas = list(ex.map(lambda i: sondar(i, com_udp), sorted(candidatos)))
    rotulos = arg.get("rotulo") or {}
    inventario = {}
    for ip, abertas, gree, midea in sondas:
        up = ficha_upnp(anuncios[ip]["location"]) if anuncios.get(ip, {}).get("location") else {}
        tipo, motivo = classificar(abertas, up, gree, midea, ip == gateway, ip == meu)
        inventario[ip] = {"tipo": tipo, "motivo": motivo, "portas": abertas, "upnp": up or None}
    anterior = {}
    try:
        with open(ARQUIVO) as f:
            anterior = json.load(f).get("aparelhos", {})
    except (OSError, ValueError):
        pass
    for ip, nome in rotulos.items():
        if ip in inventario:
            inventario[ip]["nome"] = nome
    for ip in inventario:
        if "nome" not in inventario[ip] and anterior.get(ip, {}).get("nome"):
            inventario[ip]["nome"] = anterior[ip]["nome"]
    novos = sorted(set(inventario) - set(anterior)) if anterior else []
    sumidos = sorted(set(anterior) - set(inventario))
    try:
        os.makedirs(os.path.dirname(ARQUIVO), exist_ok=True)
        with open(ARQUIVO, "w") as f:
            json.dump({"quando": time.strftime("%Y-%m-%d %H:%M:%S"), "sub_rede": base, "aparelhos": inventario},
                      f, ensure_ascii=False, indent=1)
    except OSError:
        pass
    print(json.dumps({"sub_rede": base, "total": len(inventario), "aparelhos": inventario,
                      "novos": novos, "sumidos": sumidos,
                      "nota": "palpites por portas; confirme com quem é dono do aparelho"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
