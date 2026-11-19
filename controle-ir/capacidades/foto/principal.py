"""Foto pela câmera do celular (Termux:API), reduzida com ffmpeg e devolvida como imagem. Entrada/saída: JSON."""
import base64
import json
import os
import shutil
import subprocess
import sys
import time

PASTA = os.path.join(os.environ.get("CONTROLE_IR_DIR") or os.path.expanduser("~/.controle-ir"), "fotos")
LIMITE_BYTES = 110_000  # o base64 (~150 mil caracteres) precisa caber na resposta da capacidade
CAMERAS = {"traseira": "0", "frontal": "1"}


def reduzir(origem, destino, largura):
    """Reduz até caber em LIMITE_BYTES, piorando a qualidade (e depois a largura) aos poucos."""
    for w in (largura, int(largura * 0.75), int(largura * 0.5)):
        for q in (5, 8, 12, 18):
            r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", origem, "-vf", f"scale='min({w},iw)':-2",
                                "-q:v", str(q), destino], capture_output=True, timeout=30)
            if r.returncode != 0:
                raise RuntimeError("ffmpeg falhou: " + r.stderr.decode(errors="ignore")[-300:])
            if os.path.getsize(destino) <= LIMITE_BYTES:
                return w, q
    return w, q


def main():
    a = json.loads(sys.stdin.read() or "{}")
    cam = CAMERAS.get(str(a.get("camera", "traseira")).lower())
    if cam is None:
        print(json.dumps({"erro": "camera deve ser traseira ou frontal"}, ensure_ascii=False))
        return
    largura = max(320, min(int(a.get("largura", 960)), 1600))
    for prog in ("termux-camera-photo", "ffmpeg"):
        if not shutil.which(prog):
            print(json.dumps({"erro": f"{prog} ausente"}, ensure_ascii=False))
            return
    os.makedirs(PASTA, exist_ok=True)
    nome = time.strftime("foto-%Y%m%d-%H%M%S")
    original = os.path.join(PASTA, nome + ".jpg")
    reduzida = os.path.join(PASTA, nome + "-r.jpg")
    r = subprocess.run(["termux-camera-photo", "-c", cam, original], capture_output=True, text=True, timeout=30)
    saida = (r.stdout + r.stderr).strip()
    if not os.path.exists(original) or os.path.getsize(original) < 1000:
        dica = " (dê ao Termux:API a permissão de câmera nas configurações do Android)" if "permission" in saida.lower() else ""
        print(json.dumps({"erro": f"a câmera não tirou a foto: {saida[:300]}{dica}"}, ensure_ascii=False))
        return
    try:
        w, q = reduzir(original, reduzida, largura)
        with open(reduzida, "rb") as f:
            dados = f.read()
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as e:
        print(json.dumps({"erro": str(e)}, ensure_ascii=False))
        return
    finally:
        if os.path.exists(reduzida):
            os.remove(reduzida)
        if not a.get("salvar") and os.path.exists(original):
            os.remove(original)
    print(json.dumps({"camera": a.get("camera", "traseira"), "largura_max": w, "qualidade_ffmpeg": q,
                      "bytes": len(dados), "quando": time.strftime("%H:%M:%S"),
                      "salva_em": original if a.get("salvar") else None,
                      "_imagem": {"mime": "image/jpeg", "base64": base64.b64encode(dados).decode()}},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
