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
def detectar_bipes(amostras, taxa=TAXA, fmin=1000.0, fmax=6000.0, quadro=0.032, salto=0.016, concentracao_min=0.5,
                   acima_fundo_db=5.0, nivel_min_dbfs=-50.0, dur_min=0.04, dur_max=1.2):
    """Procura tons curtos e puros. Um quadro é "tonal" quando (1) o pico da faixa fmin–fmax concentra pelo menos
    `concentracao_min` da energia da faixa (tom puro, não fala, clique ou ruído) e (2) a energia da faixa fica
    `acima_fundo_db` acima da mediana da gravação (mais alto que o ambiente) e (3) o nível da faixa passa de
    `nivel_min_dbfs` (descarta tons fraquíssimos e artefatos da compressão AAC em trechos quietos). Quadros vizinhos
    com a mesma frequência (±4 %) formam um evento.
    Devolve [{inicio_s, duracao_s, freq_hz, forca_db, nivel_dbfs, concentracao}], do mais forte para o mais fraco;
    forca_db = quanto o bipe ficou acima do fundo; nivel_dbfs = nível absoluto (seno de amplitude 1 = −3 dBFS)."""
    import numpy as np
    x = np.asarray(amostras, dtype=np.float32)
    n = int(quadro * taxa)
    passo = int(salto * taxa)
    if x.size < n:
        return []
    janela = np.hanning(n).astype(np.float32)
    freqs = np.fft.rfftfreq(n, 1.0 / taxa)
    faixa = (freqs >= fmin) & (freqs <= fmax)
    fq_faixa = freqs[faixa]
    escala = 2.0 / (n * float(np.sum(janela ** 2)))  # energia da faixa → média quadrática do sinal (Parseval)
    linhas = []
    for i in range(0, x.size - n + 1, passo):
        pot = np.abs(np.fft.rfft(x[i:i + n] * janela)) ** 2
        b = pot[faixa]
        total = float(b.sum()) + 1e-20
        k = int(np.argmax(b))
        borda = k in (0, b.size - 1)
        conc = 0.0 if borda else float(b[max(k - 2, 0):k + 3].sum()) / total
        linhas.append((i / taxa, float(fq_faixa[k]), conc, 10 * np.log10(total), 10 * np.log10(total * escala)))
    fundo = float(np.median([l[3] for l in linhas]))
    eventos, atual = [], None
    for t, f, conc, edb, nivel in linhas:
        tonal = conc >= concentracao_min and edb >= fundo + acima_fundo_db and nivel >= nivel_min_dbfs
        if tonal and atual and abs(f - atual["f"]) <= 0.04 * atual["f"]:
            atual["fim"] = t + quadro
            atual["fs"].append(f)
            atual["dbs"].append(edb - fundo)
            atual["ns"].append(nivel)
            atual["cs"].append(conc)
        else:
            if atual:
                eventos.append(atual)
            atual = ({"ini": t, "fim": t + quadro, "f": f, "fs": [f], "dbs": [edb - fundo], "ns": [nivel],
                      "cs": [conc]} if tonal else None)
    if atual:
        eventos.append(atual)
    out = []
    for e in eventos:
        dur = e["fim"] - e["ini"]
        if dur_min <= dur <= dur_max:
            out.append({"inicio_s": round(e["ini"], 2), "duracao_s": round(dur, 2),
                        "freq_hz": round(float(np.median(e["fs"]))), "forca_db": round(float(np.max(e["dbs"])), 1),
                        "nivel_dbfs": round(float(np.max(e["ns"])), 1), "concentracao": round(float(np.mean(e["cs"])), 2)})
    return sorted(out, key=lambda e: -e["forca_db"])


def filtrar_janela(bipes, envio_s, antes=0.6, depois=3.5):
    """Só os bipes que começam perto do envio (de `antes` s antes até `depois` s depois); acrescenta atraso_s.
    A folga antes do envio cobre o atraso entre pedir a gravação e o microfone começar de fato."""
    if envio_s is None:
        return bipes
    out = []
    for b in bipes:
        atraso = b["inicio_s"] - envio_s
        if -antes <= atraso <= depois:
            out.append(dict(b, atraso_s=round(atraso, 2)))
    return out


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


def analisar(aparelho=None, salvar_referencia=False, manter_audio=False, envio_em=None):
    est = ler_json(ESTADO, {})
    if envio_em:
        est["envio_em"] = float(envio_em)
        gravar_json(ESTADO, est)
    envio_s = (est["envio_em"] - est["inicio"]) if est.get("envio_em") and est.get("inicio") else None
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
    todos = detectar_bipes(x)
    bipes = filtrar_janela(todos, envio_s)
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
            "envio_no_audio_s": round(envio_s, 2) if envio_s is not None else None,
            "sons_fora_da_janela": len(todos) - len(bipes),
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
        out = analisar(a.get("aparelho"), bool(a.get("salvar_referencia")), bool(a.get("manter_audio")),
                       a.get("envio_em"))
    else:
        out = {"erro": "acao deve ser gravar ou analisar"}
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
