"""Ouve o bipe de um aparelho pelo microfone do celular (Termux:API + ffmpeg + numpy). Entrada/saída: JSON."""
import json
import os
import shutil
import subprocess
import sys
import time

TAXA = 16000
PASTA = os.path.join(os.environ.get("CONTROLE_IR_DIR") or os.path.expanduser("~/.controle-ir"))
AUDIO = os.path.join(PASTA, "audio", "bipe.m4a")
ESTADO = os.path.join(PASTA, "audio", "gravacao.json")
REFS = os.path.join(PASTA, "medicoes", "bipes.json")


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


# --------------------------------------------------------------------------- análise (pura, testável)
def detectar_bipes(amostras, taxa=TAXA, fmin=1000.0, fmax=6000.0, quadro=0.032, salto=0.016, min_db=14.0,
                   dur_min=0.04, dur_max=1.2):
    """Procura tons curtos e puros: em cada quadro, o pico da faixa fmin–fmax precisa ficar min_db acima da
    mediana do espectro daquele quadro (tom, não ruído). Quadros vizinhos com a mesma frequência (±4 %) formam um
    evento. Devolve [{inicio_s, duracao_s, freq_hz, forca_db}], do mais forte para o mais fraco."""
    import numpy as np
    x = np.asarray(amostras, dtype=np.float32)
    if x.size == 0:
        return []
    n = int(quadro * taxa)
    passo = int(salto * taxa)
    if x.size < n:
        return []
    janela = np.hanning(n).astype(np.float32)
    freqs = np.fft.rfftfreq(n, 1.0 / taxa)
    faixa = (freqs >= fmin) & (freqs <= fmax)
    idx_faixa = np.nonzero(faixa)[0]
    quadros = []
    for i in range(0, x.size - n + 1, passo):
        esp = np.abs(np.fft.rfft(x[i:i + n] * janela)) + 1e-9
        k = idx_faixa[np.argmax(esp[faixa])]
        forca = 20 * np.log10(esp[k] / np.median(esp))
        quadros.append((i / taxa, float(freqs[k]), float(forca)))
    eventos, atual = [], None
    for t, f, db in quadros:
        tonal = db >= min_db
        if tonal and atual and abs(f - atual["f"]) <= 0.04 * atual["f"]:
            atual["fim"] = t + quadro
            atual["fs"].append(f)
            atual["dbs"].append(db)
        else:
            if atual:
                eventos.append(atual)
            atual = {"ini": t, "fim": t + quadro, "f": f, "fs": [f], "dbs": [db]} if tonal else None
    if atual:
        eventos.append(atual)
    out = []
    for e in eventos:
        dur = e["fim"] - e["ini"]
        if dur_min <= dur <= dur_max:
            out.append({"inicio_s": round(e["ini"], 2), "duracao_s": round(dur, 2),
                        "freq_hz": round(float(np.median(e["fs"]))), "forca_db": round(float(np.max(e["dbs"])), 1)})
    return sorted(out, key=lambda e: -e["forca_db"])


def comparar(bipes, ref, tolerancia=0.05):
    """Bipes que batem com a frequência de referência (±5 %)."""
    if not ref:
        return []
    return [b for b in bipes if abs(b["freq_hz"] - ref["freq_hz"]) <= tolerancia * ref["freq_hz"]]


# --------------------------------------------------------------------------- celular
def gravar(segundos):
    if not shutil.which("termux-microphone-record"):
        return {"erro": "termux-microphone-record ausente (instale o app Termux:API e o pacote termux-api)"}
    os.makedirs(os.path.dirname(AUDIO), exist_ok=True)
    subprocess.run(["termux-microphone-record", "-q"], capture_output=True, timeout=10)  # encerra gravação velha
    if os.path.exists(AUDIO):
        os.remove(AUDIO)
    r = subprocess.run(["termux-microphone-record", "-f", AUDIO, "-l", str(segundos), "-e", "aac"],
                       capture_output=True, text=True, timeout=15)
    saida = (r.stdout + r.stderr).strip()
    if r.returncode != 0 or "error" in saida.lower():
        return {"erro": f"o microfone não começou a gravar: {saida[:300]}"}
    fim = time.time() + segundos
    gravar_json(ESTADO, {"inicio": time.time(), "fim": fim, "segundos": segundos})
    return {"status": "gravando", "segundos": segundos,
            "proximo_passo": "envie o comando agora (controlar) e depois chame acao=analisar"}


def decodificar():
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg ausente: pkg install ffmpeg")
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", AUDIO, "-ac", "1", "-ar", str(TAXA), "-f", "s16le", "-"],
                       capture_output=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg não conseguiu ler o áudio: " + r.stderr.decode(errors="ignore")[-300:])
    import numpy as np
    return np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768.0


def analisar(aparelho=None, salvar_referencia=False, manter_audio=False):
    est = ler_json(ESTADO, {})
    falta = est.get("fim", 0) - time.time()
    if falta > 0:
        time.sleep(min(falta + 1.0, 25))
    else:
        time.sleep(1.0)
    subprocess.run(["termux-microphone-record", "-q"], capture_output=True, timeout=10)
    for _ in range(10):  # o Termux:API fecha o arquivo um pouco depois do fim
        if os.path.exists(AUDIO) and os.path.getsize(AUDIO) > 1000:
            break
        time.sleep(0.5)
    if not os.path.exists(AUDIO):
        return {"erro": "nenhuma gravação encontrada: chame acao=gravar antes de enviar o comando"}
    import numpy as np
    try:
        x = decodificar()
    except RuntimeError as e:
        return {"erro": str(e)}
    nivel = float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)) if x.size else None
    bipes = detectar_bipes(x)
    refs = ler_json(REFS, {})
    ref = refs.get(aparelho) if aparelho else None
    batem = comparar(bipes, ref)
    if salvar_referencia and aparelho and bipes:
        refs[aparelho] = {"freq_hz": bipes[0]["freq_hz"], "duracao_s": bipes[0]["duracao_s"],
                          "forca_db": bipes[0]["forca_db"], "quando": time.strftime("%Y-%m-%d %H:%M")}
        gravar_json(REFS, refs)
        ref = refs[aparelho]
        batem = [bipes[0]]
    if not manter_audio:
        try:
            os.remove(AUDIO)
        except OSError:
            pass
    if ref:
        veredito = "confirmado" if batem else "nao_confirmado"
    else:
        veredito = "bipe_ouvido_sem_referencia" if bipes else "nada_ouvido"
    return {"veredito": veredito, "aparelho": aparelho, "referencia": ref, "bipes": bipes[:5],
            "batem_com_referencia": batem[:3], "duracao_audio_s": round(x.size / TAXA, 1),
            "nivel_medio_db": round(nivel, 1) if nivel is not None else None,
            "dica": None if bipes or (nivel or -99) > -70 else
            "áudio quase mudo: o microfone pode estar bloqueado com a tela apagada ou sem permissão do Termux:API"}


def main():
    a = json.loads(sys.stdin.read() or "{}")
    acao = a.get("acao")
    if acao == "gravar":
        out = gravar(max(2, min(int(a.get("segundos", 7)), 20)))
    elif acao == "analisar":
        out = analisar(a.get("aparelho"), bool(a.get("salvar_referencia")), bool(a.get("manter_audio")))
    else:
        out = {"erro": "acao deve ser gravar ou analisar"}
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
