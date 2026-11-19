"""Laboratório do sono: roncos, barulhos, ruído e temperatura do quarto durante a noite. Entrada/saída: JSON.

Privacidade: cada trecho de áudio é analisado e apagado na hora; só números vão para o histórico.
Roncos (heurística, sem aprendizado de máquina): rajadas graves (80–800 Hz) de 0,25–2,5 s, com o "peso" do
espectro abaixo de ~900 Hz, que se repetem no ritmo da respiração (2–8 s entre uma e outra, ao menos 3 seguidas).
"""
import json
import os
import signal
import subprocess
import sys
import time

TAXA = 16000
BASE = os.environ.get("CONTROLE_IR_DIR") or os.path.expanduser("~/.controle-ir")
MED = os.path.join(BASE, "medicoes")
TMP = os.path.join(BASE, "sono")
ESTADO = os.path.join(TMP, "sessao.json")


# --------------------------------------------------------------------------- análise (pura, testada)
def _quadros_db(x, taxa, banda, quadro=0.05):
    import numpy as np
    n = int(quadro * taxa)
    if x.size < n * 4:
        return np.array([]), np.array([])
    q = x[: (x.size // n) * n].reshape(-1, n)
    esp = np.abs(np.fft.rfft(q * np.hanning(n), axis=1)) ** 2
    f = np.fft.rfftfreq(n, 1.0 / taxa)
    m = (f >= banda[0]) & (f <= banda[1])
    energia = esp[:, m].sum(axis=1) + 1e-20
    centroide = (esp[:, (f >= 80) & (f <= 4000)] * f[(f >= 80) & (f <= 4000)]).sum(axis=1) / \
        (esp[:, (f >= 80) & (f <= 4000)].sum(axis=1) + 1e-20)
    return 10 * np.log10(energia), centroide


def _rajadas(ativo, quadro):
    out, ini = [], None
    for i, a in enumerate(list(ativo) + [False]):
        if a and ini is None:
            ini = i
        elif not a and ini is not None:
            out.append((ini, i))
            ini = None
    return [(a * quadro, (b - a) * quadro, a, b) for a, b in out]


def analisar_trecho(x, taxa=TAXA, quadro=0.05):
    """Devolve {roncos, ronco_s, barulhos, nivel_db, pico_db, ritmo_s} de um trecho (float32, −1..1)."""
    import numpy as np
    x = np.asarray(x, dtype=np.float32)
    grave, centroide = _quadros_db(x, taxa, (80, 800), quadro)
    total, _ = _quadros_db(x, taxa, (80, 7900), quadro)
    if grave.size == 0:
        return {"roncos": 0, "ronco_s": 0.0, "barulhos": 0, "nivel_db": None, "pico_db": None, "ritmo_s": None}
    fundo = float(np.percentile(grave, 20))
    rajadas = [r for r in _rajadas(grave > fundo + 8, quadro) if 0.25 <= r[1] <= 2.5]
    graves = [r for r in rajadas if float(np.median(centroide[r[2]:r[3]])) < 900]
    # sequências no ritmo da respiração
    roncos, seq = [], [graves[0]] if graves else []
    for anterior, atual in zip(graves, graves[1:]):
        if 2.0 <= atual[0] - anterior[0] <= 8.0:
            seq.append(atual)
        else:
            if len(seq) >= 3:
                roncos.extend(seq)
            seq = [atual]
    if len(seq) >= 3:
        roncos.extend(seq)
    fundo_total = float(np.percentile(total, 20))
    barulhos = [r for r in _rajadas(total > fundo_total + 20, quadro) if r[1] < 0.3]
    intervalos = [b[0] - a[0] for a, b in zip(roncos, roncos[1:]) if b[0] - a[0] <= 8.0]
    nivel = 20 * np.log10(float(np.sqrt(np.mean(x ** 2))) + 1e-9)
    n = int(quadro * taxa)
    rms_quadros = np.sqrt(np.mean(x[: (x.size // n) * n].reshape(-1, n) ** 2, axis=1))
    pico = 20 * np.log10(float(rms_quadros.max()) + 1e-9)
    return {"roncos": len(roncos), "ronco_s": round(sum(r[1] for r in roncos), 1), "barulhos": len(barulhos),
            "nivel_db": round(float(nivel), 1), "pico_db": round(float(pico), 1),
            "ritmo_s": round(float(np.median(intervalos)), 1) if intervalos else None}


def resumir(linhas):
    """Resumo da noite e por hora a partir das linhas do histórico."""
    if not linhas:
        return {"erro": "nenhum trecho medido nesta noite"}
    horas = {}
    for l in linhas:
        h = time.strftime("%H:00", time.localtime(l["t"]))
        d = horas.setdefault(h, {"hora": h, "trechos": 0, "roncos": 0, "ronco_s": 0.0, "barulhos": 0,
                                 "nivel": [], "temp": []})
        d["trechos"] += 1
        d["roncos"] += l.get("roncos", 0)
        d["ronco_s"] += l.get("ronco_s", 0.0)
        d["barulhos"] += l.get("barulhos", 0)
        if l.get("nivel_db") is not None:
            d["nivel"].append(l["nivel_db"])
        if l.get("ar_estimado_c") is not None:
            d["temp"].append(l["ar_estimado_c"])
    por_hora = []
    for d in horas.values():
        por_hora.append({"hora": d["hora"], "trechos": d["trechos"], "roncos": d["roncos"],
                         "ronco_s": round(d["ronco_s"], 1), "barulhos": d["barulhos"],
                         "nivel_db": round(sum(d["nivel"]) / len(d["nivel"]), 1) if d["nivel"] else None,
                         "ar_c": round(sum(d["temp"]) / len(d["temp"]), 1) if d["temp"] else None})
    ouvido_s = sum(l.get("duracao_s", 0) for l in linhas)
    ronco_s = sum(l.get("ronco_s", 0) for l in linhas)
    com_ronco = [h for h in por_hora if h["roncos"]]
    return {"inicio": time.strftime("%d/%m %H:%M", time.localtime(linhas[0]["t"])),
            "fim": time.strftime("%d/%m %H:%M", time.localtime(linhas[-1]["t"])),
            "trechos": len(linhas), "minutos_ouvidos": round(ouvido_s / 60, 1),
            "roncos": sum(l.get("roncos", 0) for l in linhas), "ronco_pct_do_ouvido": round(100 * ronco_s / ouvido_s, 1)
            if ouvido_s else 0, "barulhos": sum(l.get("barulhos", 0) for l in linhas),
            "hora_com_mais_ronco": max(com_ronco, key=lambda h: h["ronco_s"])["hora"] if com_ronco else None,
            "por_hora": por_hora,
            "nota": "estimativa por heurística de som (não é exame médico); ronco frequente com pausas vale avaliação"}


# --------------------------------------------------------------------------- celular
def ler_json(caminho, padrao):
    try:
        with open(caminho) as f:
            return json.load(f)
    except (OSError, ValueError):
        return padrao


def gravar_json(caminho, dados):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)


def trecho_do_microfone(segundos):
    """Grava, decodifica e apaga. Devolve as amostras ou None."""
    import numpy as np
    os.makedirs(TMP, exist_ok=True)
    arq = os.path.join(TMP, "trecho.m4a")
    subprocess.run(["termux-microphone-record", "-q"], capture_output=True, timeout=10)
    if os.path.exists(arq):
        os.remove(arq)
    subprocess.run(["termux-microphone-record", "-f", arq, "-l", str(segundos), "-e", "aac"],
                   capture_output=True, timeout=15)
    time.sleep(segundos + 1.5)
    subprocess.run(["termux-microphone-record", "-q"], capture_output=True, timeout=10)
    try:
        r = subprocess.run(["ffmpeg", "-v", "error", "-i", arq, "-ac", "1", "-ar", str(TAXA), "-f", "s16le", "-"],
                           capture_output=True, timeout=60)
        return np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768.0 if r.stdout else None
    finally:
        if os.path.exists(arq):
            os.remove(arq)


def temperatura():
    try:
        b = json.loads(subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=15).stdout)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None, None
    conf = ler_json(os.path.join(MED, "termometro.json"), {"diferenca": 2.0})
    t = b.get("temperature")
    carregando = str(b.get("plugged", "UNPLUGGED")).upper() != "UNPLUGGED"
    return (round(float(t) - conf.get("diferenca", 2.0), 1) if t is not None else None), carregando


def comandar_ar(aparelho, temperatura_c):
    """Envia pelo servidor local (o segredo não sai do celular)."""
    import urllib.request
    c = ler_json(os.path.join(BASE, "config.json"), {})
    porta = ler_json(os.path.join(BASE, "servidor.json"), {}).get("porta", 8765)
    corpo = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
             "params": {"name": "controlar", "arguments": {"aparelho": aparelho, "definir": {"temperatura": temperatura_c}}}}
    req = urllib.request.Request(f"http://127.0.0.1:{porta}/mcp/{c.get('segredo', '')}", data=json.dumps(corpo).encode(),
                                 headers={"Content-Type": "application/json", "Accept": "application/json"})
    try:
        r = json.load(urllib.request.urlopen(req, timeout=40))
        return json.loads(r["result"]["content"][0]["text"]).get("status")
    except Exception as e:  # noqa: BLE001
        return f"falhou: {e}"


def laco(sessao):
    s = ler_json(ESTADO, {})
    arq = os.path.join(MED, f"sono-{sessao}.jsonl")
    ajuste = s.get("ajuste_ar") or {}
    if ajuste.get("aparelho") and ajuste.get("dormir_c") is not None:
        s["eventos_ar"] = [{"hora": time.strftime("%H:%M"), "temperatura": ajuste["dormir_c"],
                            "status": comandar_ar(ajuste["aparelho"], ajuste["dormir_c"])}]
        gravar_json(ESTADO, s)
    madrugada_feita = False
    while time.time() < s["fim"] and not os.path.exists(os.path.join(TMP, "parar")) and not os.path.exists(os.path.join(BASE, "PARAR")):
        t0 = time.time()
        x = trecho_do_microfone(s["duracao_s"])
        linha = {"t": round(t0), "duracao_s": s["duracao_s"]}
        if x is not None and x.size:
            linha.update(analisar_trecho(x))
        else:
            linha["erro"] = "microfone não gravou"
        linha["ar_estimado_c"], linha["carregando"] = temperatura()
        with open(arq, "a") as f:
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")
        if (ajuste.get("aparelho") and ajuste.get("madrugada_c") is not None and not madrugada_feita
                and time.strftime("%H:%M") >= ajuste.get("hora_madrugada", "03:00")
                and time.strftime("%H:%M") < "12:00"):
            s = ler_json(ESTADO, s)
            s.setdefault("eventos_ar", []).append({"hora": time.strftime("%H:%M"), "temperatura": ajuste["madrugada_c"],
                                                   "status": comandar_ar(ajuste["aparelho"], ajuste["madrugada_c"])})
            gravar_json(ESTADO, s)
            madrugada_feita = True
        espera = s["intervalo_min"] * 60 - (time.time() - t0)
        while espera > 0 and not os.path.exists(os.path.join(TMP, "parar")) and not os.path.exists(os.path.join(BASE, "PARAR")):
            time.sleep(min(espera, 15))
            espera -= 15
    s = ler_json(ESTADO, s)
    s["ativo"] = False
    gravar_json(ESTADO, s)


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--laco":
        laco(sys.argv[2])
        return
    a = json.loads(sys.stdin.read() or "{}")
    acao = a.get("acao")
    s = ler_json(ESTADO, {})
    if acao == "iniciar":
        if s.get("ativo") and s.get("fim", 0) > time.time():
            print(json.dumps({"erro": "já há uma noite em andamento", "sessao": s.get("sessao")}, ensure_ascii=False))
            return
        horas = max(1.0, min(float(a.get("horas", 8)), 12.0))
        sessao = time.strftime("%Y%m%d-%H%M")
        s = {"sessao": sessao, "ativo": True, "inicio": time.time(), "fim": time.time() + horas * 3600,
             "intervalo_min": max(2, min(int(a.get("intervalo_min", 5)), 30)),
             "duracao_s": max(20, min(int(a.get("duracao_s", 60)), 120)), "ajuste_ar": a.get("ajuste_ar")}
        os.makedirs(TMP, exist_ok=True)
        if os.path.exists(os.path.join(TMP, "parar")):
            os.remove(os.path.join(TMP, "parar"))
        p = subprocess.Popen([sys.executable, os.path.abspath(__file__), "--laco", sessao], start_new_session=True,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        s["pid"] = p.pid
        gravar_json(ESTADO, s)
        out = {"iniciado": True, "sessao": sessao, "ate": time.strftime("%H:%M", time.localtime(s["fim"])),
               "trechos": f"{s['duracao_s']} s a cada {s['intervalo_min']} min",
               "ajuste_ar": s["ajuste_ar"] or "desligado",
               "dica": "deixe o celular perto da cama; fora da tomada a temperatura sai mais certa"}
    elif acao == "parar":
        os.makedirs(TMP, exist_ok=True)
        open(os.path.join(TMP, "parar"), "w").close()
        try:
            os.killpg(s.get("pid", -1), signal.SIGTERM)
        except (OSError, TypeError):
            pass
        subprocess.run(["termux-microphone-record", "-q"], capture_output=True, timeout=10)
        s["ativo"] = False
        gravar_json(ESTADO, s)
        out = {"parado": True, "sessao": s.get("sessao")}
    elif acao == "estado":
        linhas = _linhas(s.get("sessao"))
        out = {"sessao": s.get("sessao"), "ativo": bool(s.get("ativo")) and s.get("fim", 0) > time.time(),
               "trechos_medidos": len(linhas), "ultimo": linhas[-1] if linhas else None,
               "eventos_ar": s.get("eventos_ar", [])}
    elif acao == "relatorio":
        sessao = a.get("sessao") or s.get("sessao")
        out = dict(resumir(_linhas(sessao)), sessao=sessao, eventos_ar=s.get("eventos_ar", []))
    else:
        out = {"erro": "acao deve ser iniciar, estado, parar ou relatorio"}
    print(json.dumps(out, ensure_ascii=False))


def _linhas(sessao):
    if not sessao:
        return []
    try:
        with open(os.path.join(MED, f"sono-{sessao}.jsonl")) as f:
            return [json.loads(l) for l in f if l.strip()]
    except OSError:
        return []


if __name__ == "__main__":
    main()
