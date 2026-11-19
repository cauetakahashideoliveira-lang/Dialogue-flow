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
RECORTES = os.path.join(os.environ.get("CONTROLE_IR_DIR") or os.path.expanduser("~/.controle-ir"), "medicoes",
                        "recortes.json")


def validar_recorte(r):
    """[x0, y0, x1, y1] em frações da foto (0–1, origem no canto superior esquerdo). Devolve a lista ou erro."""
    if not isinstance(r, list) or len(r) != 4 or not all(isinstance(v, (int, float)) for v in r):
        raise ValueError("recorte deve ser [x0, y0, x1, y1] com frações de 0 a 1")
    x0, y0, x1, y1 = (float(v) for v in r)
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1) or (x1 - x0) < 0.02 or (y1 - y0) < 0.02:
        raise ValueError("recorte inválido: precisa de 0 ≤ x0 < x1 ≤ 1, 0 ≤ y0 < y1 ≤ 1 e pelo menos 2 % de cada lado")
    return [round(x0, 4), round(y0, 4), round(x1, 4), round(y1, 4)]


def filtro(largura, recorte=None):
    """Filtro do ffmpeg: recorta (em frações) e reduz para no máximo `largura` px."""
    partes = []
    if recorte:
        x0, y0, x1, y1 = recorte
        partes.append(f"crop=iw*{x1 - x0:.4f}:ih*{y1 - y0:.4f}:iw*{x0:.4f}:ih*{y0:.4f}")
    partes.append(f"scale='min({largura},iw)':-2")
    return ",".join(partes)


def ler_recortes():
    try:
        with open(RECORTES) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def reduzir(origem, destino, largura, recorte=None):
    """Reduz até caber em LIMITE_BYTES, piorando a qualidade (e depois a largura) aos poucos."""
    for w in (largura, int(largura * 0.75), int(largura * 0.5)):
        for q in (5, 8, 12, 18):
            r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", origem, "-vf", filtro(w, recorte),
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
    alvo = (a.get("alvo") or "").strip() or None
    recortes = ler_recortes()
    try:
        recorte = validar_recorte(a["recorte"]) if a.get("recorte") is not None else None
    except ValueError as e:
        print(json.dumps({"erro": str(e)}, ensure_ascii=False))
        return
    if recorte and alvo:  # guarda para as próximas fotos do mesmo alvo
        recortes[alvo] = recorte
        os.makedirs(os.path.dirname(RECORTES), exist_ok=True)
        with open(RECORTES, "w") as f:
            json.dump(recortes, f, ensure_ascii=False, indent=1)
    elif alvo and not recorte:
        recorte = recortes.get(alvo)
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
        w, q = reduzir(original, reduzida, largura, recorte)
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
                      "salva_em": original if a.get("salvar") else None, "alvo": alvo, "recorte": recorte,
                      "_imagem": {"mime": "image/jpeg", "base64": base64.b64encode(dados).decode()}},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
