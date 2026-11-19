"""Termômetro do cômodo pela bateria (técnica "battery as thermometer"). Entrada/saída: JSON.

Parado, fora da tomada e com pouco consumo, a bateria entra em equilíbrio térmico e fica um pouco acima do ar
(em geral 1–3 °C). Estimativa = temperatura da bateria − diferença calibrada. Uso, carga e tela acesa aquecem a
bateria: nesses casos a confiança cai e a leitura é marcada como "aquecida".
"""
import json
import os
import subprocess
import sys
import time

BASE = os.environ.get("CONTROLE_IR_DIR") or os.path.expanduser("~/.controle-ir")
HIST = os.path.join(BASE, "medicoes", "temperatura.jsonl")
CONF = os.path.join(BASE, "medicoes", "termometro.json")
DIFERENCA_PADRAO = 2.0  # bateria parada fica ~2 °C acima do ar até calibrar


def bateria():
    r = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=15)
    return json.loads(r.stdout)


def ler_conf():
    try:
        with open(CONF) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"diferenca": DIFERENCA_PADRAO, "calibrado": False}


def gravar(caminho, dados, anexar=False):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "a" if anexar else "w") as f:
        f.write(json.dumps(dados, ensure_ascii=False) + ("\n" if anexar else ""))


def historico(n=30):
    try:
        with open(HIST) as f:
            linhas = f.readlines()[-n:]
        return [json.loads(l) for l in linhas if l.strip()]
    except OSError:
        return []


# --------------------------------------------------------------------------- funções puras (testadas)
def avaliar(amostras, diferenca):
    """amostras: [{temperature, plugged, current(µA)}]. Devolve estimativa, confiança e motivos."""
    temps = [float(a["temperature"]) for a in amostras if a.get("temperature") is not None]
    if not temps:
        return {"erro": "a bateria não informou temperatura"}
    media = sum(temps) / len(temps)
    variacao = max(temps) - min(temps)
    carregando = any(str(a.get("plugged", "UNPLUGGED")).upper() != "UNPLUGGED" for a in amostras)
    # "current" (instantânea, µA) é mais confiável que current_average, que muitos aparelhos não preenchem
    correntes = [abs(float(a.get("current", a.get("current_average")))) for a in amostras
                 if a.get("current", a.get("current_average")) not in (None, "")]
    corrente_ma = (sum(correntes) / len(correntes) / 1000) if correntes else None
    motivos = []
    if carregando:
        motivos.append("na tomada (a carga aquece a bateria)")
    if corrente_ma is not None and corrente_ma > 250:
        motivos.append(f"consumo alto ({corrente_ma:.0f} mA: tela acesa ou uso)")
    if variacao > 0.6:
        motivos.append(f"temperatura variando {variacao:.1f} °C durante a medição")
    confianca = "alta" if not motivos else ("media" if len(motivos) == 1 and not carregando else "baixa")
    return {"ar_estimado_c": round(media - diferenca, 1), "bateria_c": round(media, 1),
            "confianca": confianca, "motivos": motivos, "corrente_ma": round(corrente_ma) if corrente_ma else None}


def tendencia(hist, minutos=60):
    """°C/h das estimativas confiáveis da última hora (regressão linear simples)."""
    agora = time.time()
    pts = [(h["t"], h["ar_estimado_c"]) for h in hist
           if h.get("confianca") in ("alta", "media") and agora - h.get("t", 0) <= minutos * 60]
    if len(pts) < 3 or pts[-1][0] - pts[0][0] < 300:
        return None
    mx = sum(p[0] for p in pts) / len(pts)
    my = sum(p[1] for p in pts) / len(pts)
    den = sum((p[0] - mx) ** 2 for p in pts)
    return round(sum((p[0] - mx) * (p[1] - my) for p in pts) / den * 3600, 2) if den else None


# --------------------------------------------------------------------------- ações
def medir(segundos):
    amostras = []
    fim = time.time() + segundos
    while True:
        amostras.append(bateria())
        if time.time() >= fim:
            break
        time.sleep(min(5, max(0.0, fim - time.time())))
    conf = ler_conf()
    r = avaliar(amostras, conf["diferenca"])
    if "erro" not in r:
        r.update({"t": round(time.time()), "quando": time.strftime("%Y-%m-%d %H:%M"), "calibrado": conf["calibrado"]})
        gravar(HIST, r, anexar=True)
        r["tendencia_c_por_hora"] = tendencia(historico(60))
    return r


def main():
    a = json.loads(sys.stdin.read() or "{}")
    acao = a.get("acao")
    if acao == "ler":
        out = medir(max(5, min(int(a.get("segundos", 15)), 40)))
    elif acao == "calibrar":
        real = a.get("temperatura_real")
        if real is None:
            out = {"erro": "informe temperatura_real (°C)"}
        else:
            r = medir(15)
            if r.get("confianca") == "baixa":
                out = {"erro": "celular aquecido agora (" + "; ".join(r["motivos"]) + "): calibre com ele parado, "
                               "fora da tomada e com a tela apagada", "leitura": r}
            else:
                dif = round(r["bateria_c"] - float(real), 2)
                gravar(CONF, {"diferenca": dif, "calibrado": True, "quando": time.strftime("%Y-%m-%d %H:%M"),
                              "bateria_c": r["bateria_c"], "real_c": float(real)})
                out = {"calibrado": True, "diferenca_bateria_ar": dif, "leitura": r}
    elif acao == "monitorar":
        minutos = max(5, min(int(a.get("minutos", 60)), 720))
        voltas = max(1, minutos // 2)
        parar = os.path.join(BASE, "PARAR")  # travar cria este arquivo: o laço termina na volta seguinte
        cmd = (f"for i in $(seq {voltas}); do [ -e '{parar}' ] && break; "
               f"echo '{{\"acao\":\"ler\",\"segundos\":10}}' | "
               f"python3 {os.path.abspath(__file__)} >/dev/null 2>&1; sleep 110; done")
        subprocess.Popen(["sh", "-c", cmd], start_new_session=True, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=os.environ.copy())
        out = {"monitorando": True, "minutos": minutos, "leituras_previstas": voltas,
               "dica": "deixe o celular parado, fora da tomada e com a tela apagada; veja com acao=historico"}
    elif acao == "historico":
        h = historico(max(1, min(int(a.get("n", 30)), 500)))
        out = {"leituras": h, "tendencia_c_por_hora": tendencia(h), "calibracao": ler_conf()}
    else:
        out = {"erro": "acao deve ser ler, calibrar, monitorar ou historico"}
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
