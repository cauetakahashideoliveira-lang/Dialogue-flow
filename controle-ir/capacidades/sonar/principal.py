"""Sonar de presença por ultrassom (Doppler) com o alto-falante e o microfone do celular. Entrada/saída: JSON."""
import json
import os
import shutil
import subprocess
import sys
import time
import wave

TAXA = 48000
BASE = os.environ.get("CONTROLE_IR_DIR") or os.path.expanduser("~/.controle-ir")
TMP = os.path.join(BASE, "sonar")


# --------------------------------------------------------------------------- funções puras (testadas)
def gerar_tom(freq, segundos, taxa=TAXA, amplitude=0.6, rampa=0.2):
    """Seno em int16 com subida/descida suaves (sem estalo audível no começo e no fim)."""
    import numpy as np
    t = np.arange(int(segundos * taxa)) / taxa
    env = np.ones_like(t)
    r = int(rampa * taxa)
    env[:r] = np.linspace(0, 1, r)
    env[-r:] = np.linspace(1, 0, r)
    return (amplitude * env * np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)


def analisar_sonar(x, freq, taxa=TAXA, n=8192, faixa_doppler=(12.0, 160.0), limiar_db=6.0):
    """Suporte (o tom aparece acima do ruído da faixa alta?) e linha do tempo de movimento: energia nas laterais
    do tom (desvio Doppler de 12–160 Hz ≈ 0,1–1,4 m/s) relativa ao próprio tom, quadro a quadro."""
    import numpy as np
    x = np.asarray(x, dtype=np.float32)
    if x.size < n * 4:
        return {"erro": "áudio curto demais"}
    f = np.fft.rfftfreq(n, 1.0 / taxa)
    janela = np.hanning(n).astype(np.float32)
    passo = n // 2
    quadros = [np.abs(np.fft.rfft(x[i:i + n] * janela)) ** 2 for i in range(0, x.size - n + 1, passo)]
    medio = np.mean(quadros, axis=0)
    k = int(np.argmin(np.abs(f - freq)))
    perto = (np.abs(f - freq) <= 3 * taxa / n)
    alta = (f >= 16500) & (f <= min(22000, taxa / 2 - 100)) & ~(np.abs(f - freq) <= faixa_doppler[1] + 50)
    tom_db = 10 * np.log10(float(medio[perto].sum()) + 1e-20)
    ruido_db = 10 * np.log10(float(np.median(medio[alta])) * perto.sum() + 1e-20) if alta.any() else tom_db - 99
    suporte = (tom_db - ruido_db) >= 15
    desvio = np.abs(f - freq)
    lat = (desvio >= faixa_doppler[0]) & (desvio <= faixa_doppler[1])
    razoes = np.array([10 * np.log10((q[lat].sum() + 1e-20) / (q[perto].sum() + 1e-20)) for q in quadros])
    base = float(np.median(razoes))
    mov = razoes > base + limiar_db
    seg_quadro = passo / taxa
    linha, por_meio = [], max(1, int(round(0.5 / seg_quadro)))
    for i in range(0, mov.size, por_meio):
        linha.append(int(bool(mov[i:i + por_meio].any())))
    return {"suporte": bool(suporte), "tom_acima_do_ruido_db": round(float(tom_db - ruido_db), 1),
            "movimento_pct": round(100.0 * float(mov.mean()), 1),
            "linha_do_tempo_meio_s": linha, "frequencia_hz": freq,
            "leitura": "1 = movimento naquele meio segundo" if suporte else sugestao_sem_tom(freq)}


def sugestao_sem_tom(freq):
    if freq > MINIMA:
        return (f"o tom não chegou ao microfone: alto-falante ou gravação cortam essa frequência; "
                f"tente {max(MINIMA, freq - 1000)} Hz")
    return "o tom não chegou ao microfone nem na frequência mínima (17000 Hz): este aparelho não serve para o sonar"


# Sem frequência pedida: a última que funcionou neste celular; sem ela, a padrão e depois a mínima (no POCO X8 Pro
# Max, 19 e 18 kHz não chegam ao microfone e 17 kHz chega com folga — medido em 21/11).
PADRAO, MINIMA = 19000, 17000
MEMORIA = os.path.join(BASE, "medicoes", "sonar.json")


def frequencia_lembrada():
    try:
        with open(MEMORIA) as f:
            v = int(json.load(f)["frequencia"])
        return v if MINIMA <= v <= 20500 else None
    except (OSError, ValueError, KeyError, TypeError):
        return None


def lembrar(freq):
    try:
        os.makedirs(os.path.dirname(MEMORIA), exist_ok=True)
        with open(MEMORIA, "w") as f:
            json.dump({"frequencia": freq, "quando": time.strftime("%Y-%m-%d %H:%M")}, f)
    except OSError:
        pass


def escolher_e_testar(a, testar_fn):
    """Frequência pedida: testa só ela. Sem pedido: a lembrada; se não houver (ou falhar), 19000 e então 17000.
    A que funcionar fica lembrada para as próximas vezes."""
    segundos = max(4, min(int(a.get("segundos", 10)), 20))
    volume = max(1, min(int(a.get("volume", 10)), 15))
    if "frequencia" in a:
        fila = [max(MINIMA, min(int(a["frequencia"]), 20500))]
    else:
        fila = [f for f in dict.fromkeys([frequencia_lembrada(), PADRAO, MINIMA]) if f]
    tentativas = []
    for freq in fila:
        out = testar_fn(freq, segundos, volume)
        if "erro" in out:
            return out
        tentativas.append({"frequencia_hz": freq, "suporte": out.get("suporte"),
                           "tom_acima_do_ruido_db": out.get("tom_acima_do_ruido_db")})
        if out.get("suporte"):
            lembrar(freq)
            break
    if len(tentativas) > 1:
        out["tentativas"] = tentativas
    return out


# --------------------------------------------------------------------------- celular
def volume_musica():
    try:
        v = json.loads(subprocess.run(["termux-volume"], capture_output=True, text=True, timeout=10).stdout)
        return next((s["volume"] for s in v if s.get("stream") == "music"), None)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def testar(freq, segundos, volume):
    import numpy as np
    faltam = [p for p in ("termux-microphone-record", "termux-media-player", "termux-volume", "ffmpeg")
              if not shutil.which(p)]
    if faltam:
        return {"erro": "faltam: " + ", ".join(faltam)}
    os.makedirs(TMP, exist_ok=True)
    tom, rec = os.path.join(TMP, "tom.wav"), os.path.join(TMP, "eco.m4a")
    with wave.open(tom, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TAXA)
        w.writeframes(gerar_tom(freq, segundos + 1.5).tobytes())
    antes = volume_musica()
    try:
        subprocess.run(["termux-volume", "music", str(volume)], capture_output=True, timeout=10)
        subprocess.run(["termux-microphone-record", "-q"], capture_output=True, timeout=10)
        if os.path.exists(rec):
            os.remove(rec)
        subprocess.run(["termux-microphone-record", "-f", rec, "-l", str(segundos), "-e", "aac", "-r", str(TAXA),
                        "-b", "256000"], capture_output=True, timeout=15)
        time.sleep(0.4)
        subprocess.run(["termux-media-player", "play", tom], capture_output=True, timeout=10)
        time.sleep(segundos + 1.2)
        subprocess.run(["termux-microphone-record", "-q"], capture_output=True, timeout=10)
        subprocess.run(["termux-media-player", "stop"], capture_output=True, timeout=10)
        r = subprocess.run(["ffmpeg", "-v", "error", "-i", rec, "-ac", "1", "-ar", str(TAXA), "-f", "s16le", "-"],
                           capture_output=True, timeout=60)
        x = np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    finally:
        if antes is not None:
            subprocess.run(["termux-volume", "music", str(antes)], capture_output=True, timeout=10)
        for p in (tom, rec):
            if os.path.exists(p):
                os.remove(p)
    out = analisar_sonar(x, freq)
    out["volume_restaurado"] = antes
    return out


def main():
    a = json.loads(sys.stdin.read() or "{}")
    if a.get("acao") != "testar":
        print(json.dumps({"erro": "acao deve ser testar"}, ensure_ascii=False))
        return
    print(json.dumps(escolher_e_testar(a, testar), ensure_ascii=False))


if __name__ == "__main__":
    main()
