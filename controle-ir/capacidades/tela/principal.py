"""Agente de tela pelo Shizuku (rish): ver a tela e tocar/digitar, sem root. Entrada/saída: JSON.

O rish roda comandos com o usuário "shell" do adb (uid 2000): screencap, uiautomator, input e monkey.
Arquivos: ~/.controle-ir/rish/{rish, rish_shizuku.dex} (exportados pelo app Shizuku).
"""
import base64
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
import unicodedata
import xml.etree.ElementTree as ET

BASE = os.environ.get("CONTROLE_IR_DIR") or os.path.expanduser("~/.controle-ir")
RISH = os.path.join(BASE, "rish", "rish")
TMP = os.path.join(BASE, "tela")
BLOQUEADOS_ARQ = os.path.join(BASE, "tela_bloqueados.json")
# Apps em que a ferramenta não toca nem digita (bancos, pagamentos, senhas, autenticadores). Editável no arquivo acima.
BLOQUEADOS_PADRAO = [
    "br.com.bb", "com.itau", "br.com.itau", "br.com.bradesco", "com.bradesco", "com.nu.production",
    "br.com.intermedium", "com.santander", "br.com.santander", "br.com.caixa", "br.gov.caixa", "com.mercadopago",
    "com.picpay", "com.c6bank", "br.com.original", "com.btg", "br.com.sicredi", "br.com.sicoob", "com.sicoob",
    "br.com.uol.ps", "com.paypal", "com.google.android.apps.walletnfcrel", "com.samsung.android.spay",
    "com.x8bit.bitwarden", "com.lastpass", "com.onepassword", "com.agilebits", "com.dashlane", "com.keepassdroid",
    "com.azure.authenticator", "com.google.android.apps.authenticator2", "com.authy", "br.gov.meugovbr",
]
TECLAS = {"voltar": 4, "inicio": 3, "recentes": 187, "enter": 66, "apagar": 67}


# --------------------------------------------------------------------------- funções puras (testadas)
def normalizar(t):
    t = unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t).strip()


def ler_bounds(b):
    m = re.match(r"\[(-?\d+),(-?\d+)\]\[(-?\d+),(-?\d+)\]", b or "")
    return tuple(int(v) for v in m.groups()) if m else None


def elementos(xml_texto, limite=120):
    """Elementos úteis do dump do uiautomator: com texto, descrição ou clicáveis, com o centro para tocar."""
    try:
        raiz = ET.fromstring(xml_texto)
    except ET.ParseError:
        return []
    out = []
    for n in raiz.iter("node"):
        a = n.attrib
        texto, desc = a.get("text", ""), a.get("content-desc", "")
        clicavel = a.get("clickable") == "true" or a.get("long-clickable") == "true"
        editavel = a.get("class", "").endswith("EditText")
        b = ler_bounds(a.get("bounds"))
        if not b or b[2] <= b[0] or b[3] <= b[1] or not (texto or desc or clicavel or editavel):
            continue
        out.append({"texto": texto[:80], "desc": desc[:80], "id": a.get("resource-id", "").split("/")[-1],
                    "classe": a.get("class", "").split(".")[-1], "clicavel": clicavel, "editavel": editavel,
                    "x": (b[0] + b[2]) // 2, "y": (b[1] + b[3]) // 2, "pacote": a.get("package", "")})
        if len(out) >= limite:
            break
    return out


def achar(els, texto):
    """Elemento cujo texto/descrição/id contém `texto` (sem acento, sem caixa). Prefere igual > clicável > primeiro."""
    alvo = normalizar(texto)
    if not alvo:
        return None
    cands = [e for e in els if alvo in normalizar(e["texto"]) or alvo in normalizar(e["desc"])
             or alvo == normalizar(e["id"])]
    if not cands:
        return None
    iguais = [e for e in cands if alvo in (normalizar(e["texto"]), normalizar(e["desc"]))]
    for grupo in (iguais, cands):
        clic = [e for e in grupo if e["clicavel"]]
        if clic:
            return clic[0]
        if grupo:
            return grupo[0]
    return None


def bloqueado(pacote, lista):
    p = (pacote or "").lower()
    return any(p == b.lower() or p.startswith(b.lower() + ".") or p.startswith(b.lower()) for b in lista)


def escapar_input_text(texto):
    """Prepara o texto para `input text`: só ASCII imprimível; espaço vira %s. Devolve (texto, aviso)."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    aviso = "acentos e emojis não passam pelo input text; enviado sem acento" if sem_acento != texto else None
    sem_acento = "".join(c for c in sem_acento if 32 <= ord(c) < 127)
    return sem_acento.replace("%", r"\%").replace(" ", "%s"), aviso


def app_em_foco(dumpsys):
    m = re.search(r"mCurrentFocus=Window\{\S+ \S+ ([\w.]+)/", dumpsys or "") or \
        re.search(r"mFocusedApp=.*?([\w.]+)/", dumpsys or "")
    return m.group(1) if m else None


# --------------------------------------------------------------------------- celular
class SemShizuku(RuntimeError):
    pass


def rish(cmd, timeout=20, binario=False):
    if not os.path.exists(RISH):
        raise SemShizuku("rish não instalado: exporte os arquivos no app Shizuku (Usar o Shizuku em aplicativos de "
                         "terminal → Exportar) e peça ao Claude para copiá-los")
    env = dict(os.environ, RISH_APPLICATION_ID="com.termux")
    r = subprocess.run(["sh", RISH, "-c", cmd], capture_output=True, timeout=timeout, env=env,
                       text=not binario)
    erro = r.stderr if not binario else r.stderr.decode(errors="ignore")
    if r.returncode != 0 and ("Shizuku" in erro or "not running" in erro.lower() or "permission" in erro.lower()):
        raise SemShizuku("o Shizuku não respondeu: abra o app Shizuku e toque em Iniciar (depois de reiniciar o "
                         f"celular ele precisa ser iniciado de novo). Detalhe: {erro.strip()[:200]}")
    return r.stdout, erro, r.returncode


def foco():
    out, _, _ = rish("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'")
    return app_em_foco(out)


def tela_acesa():
    out, _, _ = rish("dumpsys power | grep -m1 mWakefulness=")
    return "Awake" in out if out else None


def bloqueados():
    try:
        with open(BLOQUEADOS_ARQ) as f:
            return json.load(f)
    except (OSError, ValueError):
        return BLOQUEADOS_PADRAO


def dump_ui():
    for _ in range(2):
        out, _, _ = rish("uiautomator dump /data/local/tmp/cir_ui.xml >/dev/null 2>&1; cat /data/local/tmp/cir_ui.xml",
                         timeout=25)
        if out.strip().startswith("<?xml"):
            return out
        time.sleep(0.8)
    return ""


def captura(largura):
    png, _, _ = rish("screencap -p", timeout=20, binario=True)
    if not png.startswith(b"\x89PNG"):
        return None, None
    os.makedirs(TMP, exist_ok=True)
    origem, destino = os.path.join(TMP, "tela.png"), os.path.join(TMP, "tela.jpg")
    with open(origem, "wb") as f:
        f.write(png)
    try:
        for q in (6, 10, 16):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", origem, "-vf", f"scale='min({largura},iw)':-2",
                            "-q:v", str(q), destino], capture_output=True, timeout=30)
            if os.path.exists(destino) and os.path.getsize(destino) <= 110_000:
                break
        with open(destino, "rb") as f:
            return base64.b64encode(f.read()).decode(), largura
    finally:
        for p in (origem, destino):
            if os.path.exists(p):
                os.remove(p)


def ver(imagem=True, largura=720):
    out = {"app": foco(), "tela_acesa": tela_acesa()}
    tam, _, _ = rish("wm size")
    m = re.search(r"(\d+)x(\d+)", tam.splitlines()[-1] if tam else "")
    out["resolucao"] = f"{m.group(1)}x{m.group(2)}" if m else None
    els = elementos(dump_ui())
    out["elementos"] = els
    out["nota"] = "coordenadas x,y em pixels da tela real (use-as em tocar); a imagem é reduzida"
    if imagem:
        b64, w = captura(largura)
        if b64:
            out["_imagem"] = {"mime": "image/jpeg", "base64": b64}
            out["largura_imagem"] = w
        else:
            out["imagem_erro"] = "screencap não devolveu imagem (app com proteção de tela mostra preto)"
    return out


def agir(a):
    acao = a["acao"]
    app = foco()
    if acao in ("tocar", "digitar", "deslizar") and bloqueado(app, bloqueados()):
        return {"erro": f"recusado: o app em foco ({app}) está na lista de bloqueados (banco/pagamento/senha). "
                        "Edite ~/.controle-ir/tela_bloqueados.json no celular se quiser mudar isso."}
    if acao == "tocar":
        x, y, alvo = a.get("x"), a.get("y"), None
        if a.get("texto"):
            alvo = achar(elementos(dump_ui()), a["texto"])
            if not alvo:
                return {"erro": f"nenhum elemento com “{a['texto']}” na tela", "app": app}
            x, y = alvo["x"], alvo["y"]
        if x is None or y is None:
            return {"erro": "informe x e y, ou texto"}
        rish(f"input tap {int(x)} {int(y)}")
        res = {"feito": f"toque em {int(x)},{int(y)}", "elemento": alvo}
    elif acao == "digitar":
        texto, aviso = escapar_input_text(a.get("texto", ""))
        if not texto:
            return {"erro": "nada para digitar"}
        rish("input text " + shlex.quote(texto))
        res = {"feito": f"digitado ({len(a.get('texto', ''))} caracteres)", "aviso": aviso}
    elif acao == "tecla":
        cod = TECLAS.get(normalizar(a.get("tecla")))
        if cod is None:
            return {"erro": f"tecla deve ser uma de: {', '.join(TECLAS)}"}
        rish(f"input keyevent {cod}")
        res = {"feito": f"tecla {a['tecla']}"}
    elif acao == "deslizar":
        if None in (a.get("x"), a.get("y"), a.get("x2"), a.get("y2")):
            return {"erro": "informe x, y, x2, y2"}
        rish(f"input swipe {int(a['x'])} {int(a['y'])} {int(a['x2'])} {int(a['y2'])} 350")
        res = {"feito": "deslizou"}
    elif acao == "abrir":
        pac = a.get("pacote") or ""
        if not re.match(r"^[A-Za-z][\w.]{2,120}$", pac):
            return {"erro": "pacote inválido (ex.: com.android.settings)"}
        _, erro, cod = rish(f"monkey -p {pac} -c android.intent.category.LAUNCHER 1")
        if cod != 0 or "No activities found" in erro:
            return {"erro": f"não consegui abrir {pac}: {erro.strip()[:200]}"}
        res = {"feito": f"abriu {pac}"}
    else:
        return {"erro": "acao deve ser ver, tocar, digitar, tecla, deslizar, abrir ou estado"}
    espera = float(a.get("esperar") or 0)
    if espera > 0:
        time.sleep(min(espera, 10))
        res["tela"] = ver(bool(a.get("imagem", True)), int(a.get("largura", 720)))
    else:
        res["app"] = foco()
    return res


def main():
    a = json.loads(sys.stdin.read() or "{}")
    acao = a.get("acao")
    try:
        if acao == "estado":
            out, _, _ = rish("id")
            r = {"rish": "ok" if "uid=2000" in out or "uid=0" in out else out.strip()[:120],
                 "app": foco(), "tela_acesa": tela_acesa(), "ffmpeg": bool(shutil.which("ffmpeg"))}
        elif acao == "ver":
            largura = max(320, min(int(a.get("largura", 720)), 1080))
            r = ver(bool(a.get("imagem", True)), largura)
        else:
            r = agir(a)
    except SemShizuku as e:
        r = {"erro": str(e), "precisa": "shizuku"}
    except subprocess.TimeoutExpired:
        r = {"erro": "o comando na tela demorou demais (o celular pode estar travado ou com a tela apagada)"}
    print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    main()
