"""Aparelhos Bluetooth ao redor (só escuta os anúncios; nunca conecta nem pareia). Entrada/saída: JSON.

O Termux:API não tem Bluetooth e o bluetoothctl não acha o adaptador no Android. Aqui um leitor em Java
(java/controleir/Bluetooth.java) roda como usuário "shell" pelo Shizuku (o mesmo caminho do agente de tela),
escuta a busca BLE por alguns segundos e lista os pareados. O Python classifica cada aparelho pelo nome, pelo
fabricante (identificador da Bluetooth SIG) e pelos serviços anunciados.
"""
import hashlib
import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("CONTROLE_IR_DIR") or os.path.expanduser("~/.controle-ir")
TMP = os.path.join(BASE, "bluetooth")
JAVA_FONTE = os.path.join(AQUI, "java", "controleir", "Bluetooth.java")
ULTIMA = os.path.join(BASE, "medicoes", "bluetooth.json")

# --------------------------------------------------------------------------- classificação (funções puras, testadas)
FABRICANTES = {  # identificadores de empresa da Bluetooth SIG mais comuns por aqui
    0x004C: "Apple", 0x0006: "Microsoft", 0x0075: "Samsung", 0x00E0: "Google", 0x0087: "Garmin",
    0x0157: "Huami (Amazfit/Mi Band)", 0x038F: "Xiaomi", 0x027D: "Huawei", 0x0059: "Nordic (genérico)",
    0x000F: "Broadcom", 0x000A: "Qualcomm/CSR", 0x001D: "Qualcomm", 0x0171: "Amazon", 0x00C4: "LG",
    0x02E5: "Espressif (ESP32)", 0x0057: "Harman (JBL)", 0x012D: "Sony", 0x009E: "Bose", 0x005D: "Realtek",
    0x0046: "MediaTek", 0x0499: "Ruuvi", 0x0002: "Intel",
}
SERVICOS = {  # UUIDs de 16 bits → (tipo, descrição)
    "fd6f": ("celular", "notificação de exposição (celular)"),
    "fe2c": ("fone ou caixa de som", "Google Fast Pair"),
    "fe9f": ("aparelho Google/Android", "serviço Google"),
    "feaa": ("beacon", "Eddystone"),
    "180d": ("relógio ou pulseira", "frequência cardíaca"),
    "1812": ("teclado, mouse ou controle", "HID"),
    "1826": ("equipamento de academia", "aparelho de ginástica"),
    "fd5a": ("rastreador", "Samsung SmartTag"),
    "feed": ("rastreador", "Tile"), "feec": ("rastreador", "Tile"),
    "fe95": ("aparelho Xiaomi/Mi Home", "MiBeacon"),
    "fe03": ("aparelho Amazon/Alexa", "Amazon"),
    "184e": ("fone ou caixa de som", "LE Audio"), "1844": ("fone ou caixa de som", "LE Audio"),
}
APPLE = {  # 1º byte do anúncio "Continuity" da Apple
    0x02: ("beacon", "iBeacon"), 0x05: ("celular ou computador", "AirDrop"),
    0x07: ("fone ou caixa de som", "AirPods/Beats"), 0x09: ("TV ou computador", "AirPlay (Apple TV/Mac)"),
    0x0A: ("celular ou computador", "AirPlay"), 0x0C: ("celular ou computador", "Handoff"),
    0x0F: ("celular", "iPhone (ação próxima)"), 0x10: ("celular", "iPhone/iPad/Watch por perto"),
    0x12: ("rastreador", "rede Buscar (AirTag ou aparelho Apple longe do dono)"),
}
NOMES = [  # (regex no nome, tipo)
    (r"\btv\b|bravia|\[tv\]|webos|android ?tv|fire ?tv|chromecast|roku|\btcl\b|\baoc\b|\bphilco\b|\bsemp\b", "TV ou streaming"),
    (r"buds|airpods|beats|fone|headset|headphone|earbud|\bjbl\b|bose|sony wh|wf-|wh-|qcy|tws|soundcore|"
     r"edifier|soundbar|speaker|caixa|\bboom\b|xtreme|flip ?\d|charge ?\d|go ?\d|harman|marshall|baseus", "fone ou caixa de som"),
    (r"watch|\bband\b|amazfit|mi smart band|fitbit|garmin|\bgear\b|pulseira|forerunner|venu|huawei band|xiaomi band",
     "relógio ou pulseira"),
    (r"carplay|\bcar\b|honda|toyota|\bvw\b|volkswagen|hyundai|\bfiat\b|chevrolet|chevy|mylink|\bbmw\b|\bjeep\b|\bford\b|"
     r"renault|nissan|peugeot|citro[eë]n|\bkia\b|mitsubishi|multim[ií]dia|uconnect|android auto", "carro"),
    (r"iphone|ipad|galaxy|redmi|\bpoco\b|\bmoto|xiaomi|samsung sm-|pixel|oneplus|realme|\boppo\b|\bvivo\b|zenfone|celular",
     "celular"),
    (r"macbook|laptop|notebook|desktop-|\bpc\b|thinkpad|ideapad|vivobook|dell", "computador"),
    (r"keyboard|teclado|mouse|controller|controle|dualsense|dualshock|xbox|joy-?con|gamepad", "teclado, mouse ou controle"),
    (r"printer|impressora|\bhp\b|epson|canon|brother", "impressora"),
    (r"tag\b|tile\b|smarttag|airtag|chaveiro", "rastreador"),
    (r"lamp|l[âa]mpada|bulb|govee|\bled\b|yeelight|tuya|smart ?life|tomada|plug", "casa inteligente"),
    (r"scale|balan[çc]a|mi_scale", "balança"),
    (r"esp32|\bble_|arduino|hm-?10|nrf", "placa eletrônica (DIY)"),
]


def classificar(d):
    """d: um aparelho visto ({nome, fabricante:[{id,dados}], servicos:[...], classe_maior}). → (tipo, fabricante, pista)."""
    nome = (d.get("nome") or "").strip()
    baixo = nome.lower()
    fab_ids = [f.get("id") for f in d.get("fabricante") or [] if isinstance(f, dict)]
    fabricante = next((FABRICANTES[i] for i in fab_ids if i in FABRICANTES), None)
    for padrao, tipo in NOMES:
        if baixo and re.search(padrao, baixo):
            return tipo, fabricante, f"nome “{nome}”"
    for s in d.get("servicos") or []:
        if s in SERVICOS:
            return SERVICOS[s][0], fabricante, SERVICOS[s][1]
    for f in d.get("fabricante") or []:
        if f.get("id") == 0x004C and len(f.get("dados") or "") >= 2:
            sub = int(f["dados"][:2], 16)
            if sub in APPLE:
                return APPLE[sub][0], "Apple", APPLE[sub][1]
            return "aparelho Apple", "Apple", "anúncio da Apple"
        if f.get("id") == 0x0006 and (f.get("dados") or "").startswith("01"):
            return "computador", "Microsoft", "Windows por perto (CDP)"
    classe = d.get("classe_maior")
    if classe is not None:
        tipo = {0x0100: "computador", 0x0200: "celular", 0x0400: "fone ou caixa de som", 0x0500: "teclado, mouse ou controle",
                0x0600: "impressora ou câmera", 0x0700: "relógio ou pulseira", 0x0900: "saúde"}.get(classe)
        if tipo:
            return tipo, fabricante, "classe Bluetooth"
    if fabricante:
        return f"aparelho {fabricante.split(' (')[0]}", fabricante, "fabricante no anúncio"
    return "desconhecido", None, None


def distancia(rssi):
    """Faixa grosseira pela força do sinal (paredes, corpo e bolso mudam muito)."""
    if rssi is None:
        return None
    if rssi >= -60:
        return "muito perto (até ~1 m)"
    if rssi >= -72:
        return "perto (~1–4 m)"
    if rssi >= -85:
        return "no ambiente (~4–10 m)"
    return "longe ou atrás de parede"


def resumir(bruto, limite=40):
    """Junta pareados e vistos, classifica e ordena pelo sinal."""
    if "erro" in bruto:
        return bruto
    vistos = []
    pareados = {p.get("endereco"): p for p in bruto.get("pareados") or [] if p.get("endereco")}
    for d in bruto.get("proximos") or []:
        tipo, fab, pista = classificar({**pareados.get(d.get("endereco"), {}), **d})
        rssi = d.get("rssi_max") if isinstance(d.get("rssi_max"), int) and d["rssi_max"] > -999 else d.get("rssi")
        vistos.append({"nome": d.get("nome") or pareados.get(d.get("endereco"), {}).get("nome"), "tipo": tipo,
                       "fabricante": fab, "pista": pista, "rssi": rssi, "distancia": distancia(rssi),
                       "pareado": d.get("endereco") in pareados, "endereco": d.get("endereco"),
                       "vezes": d.get("vezes")})
    vistos.sort(key=lambda v: -(v["rssi"] if isinstance(v["rssi"], int) else -999))
    por_tipo = {}
    for v in vistos:
        por_tipo[v["tipo"]] = por_tipo.get(v["tipo"], 0) + 1
    lista_pareados = []
    for p in pareados.values():
        tipo, fab, _ = classificar(p)
        lista_pareados.append({"nome": p.get("nome"), "tipo": tipo, "endereco": p.get("endereco"),
                               "por_perto": any(v["endereco"] == p.get("endereco") for v in vistos)})
    out = {"bluetooth_ligado": bruto.get("bluetooth_ligado"), "modo_so_ble": bruto.get("modo_so_ble"),
           "busca": bruto.get("busca"), "total_vistos": len(vistos),
           "por_tipo": dict(sorted(por_tipo.items(), key=lambda kv: -kv[1])),
           "aparelhos": vistos[:limite], "pareados": lista_pareados,
           "nota": ("só escuta anúncios BLE (não conecta); celulares e fones trocam de endereço de tempos em tempos, "
                    "então um mesmo aparelho pode aparecer duas vezes; aparelhos só clássicos e calados não aparecem")}
    if len(vistos) > limite:
        out["omitidos"] = len(vistos) - limite
    for k in ("codigo_falha", "detalhe", "avisos", "ligado_para_buscar"):
        if bruto.get(k):
            out[k] = bruto[k]
    if bruto.get("busca") == "bluetooth_desligado":
        out["dica"] = ("o Bluetooth está desligado e o modo só BLE não subiu: ligue o Bluetooth ou chame de novo com "
                       "ligar=true (ele liga só durante a busca e desliga no fim)")
    if bruto.get("busca") == "falhou":
        out["dica"] = {2: "o Android recusou o registro da busca (tente de novo em alguns segundos)",
                       6: "buscas demais em pouco tempo: espere ~30 s"}.get(bruto.get("codigo_falha"),
                                                                            "a busca BLE falhou no Android")
    return out


def ler_pareados_dumpsys(texto):
    """Pareados pelo `dumpsys bluetooth_manager` (sem o leitor Java). Linhas do tipo
    '  AA:BB:CC:DD:EE:FF [ DUAL ] Nome' depois de 'Bonded devices:'."""
    out, dentro = [], False
    for linha in (texto or "").splitlines():
        if re.match(r"\s*Bonded devices:", linha):
            dentro = True
            continue
        if dentro:
            m = re.match(r"\s+([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})\s*(?:\[\s*(\w+)\s*\])?\s*(.*)$", linha)
            if not m:
                if linha.strip():
                    break
                continue
            nome = re.sub(r"\s+\(.*$", "", m.group(3)).strip() or None
            out.append({"endereco": m.group(1).upper(), "nome": nome,
                        "tipo_radio": {"DUAL": "duplo", "LE": "ble", "CLASSIC": "classico"}.get((m.group(2) or "").upper())})
    return out


# --------------------------------------------------------------------------- celular
def _tela():
    """O módulo do agente de tela: reaproveita o rish (Shizuku) e a pasta de troca com o shell."""
    caminho = os.path.join(os.path.dirname(AQUI), "tela", "principal.py")
    spec = importlib.util.spec_from_file_location("cap_tela_para_bluetooth", caminho)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def compilar():
    """Bluetooth.java → jar dex (ecj + dx do Termux), refeito só quando o fonte muda. Devolve o caminho ou erro."""
    with open(JAVA_FONTE, "rb") as f:
        fonte = f.read()
    os.makedirs(TMP, exist_ok=True)
    jar = os.path.join(TMP, f"controle-bt-{hashlib.sha256(fonte).hexdigest()[:12]}.jar")
    if os.path.exists(jar):
        return jar, None
    if not (shutil.which("ecj") and shutil.which("dx")) and shutil.which("pkg"):
        subprocess.run(["pkg", "install", "-y", "ecj", "dx"], capture_output=True, timeout=300, check=False)
    if not (shutil.which("ecj") and shutil.which("dx")):
        return None, "faltam ecj e dx (pkg install ecj dx)"
    trab = os.path.join(TMP, f"compilar-{os.getpid()}")
    shutil.rmtree(trab, ignore_errors=True)
    try:
        src = os.path.join(trab, "src", "controleir")
        os.makedirs(src)
        shutil.copy(JAVA_FONTE, src)
        c = subprocess.run(["ecj", "-d", os.path.join(trab, "cls"), os.path.join(src, "Bluetooth.java")],
                           capture_output=True, text=True, timeout=180, check=False)
        cls = os.path.join(trab, "cls", "controleir")
        if not os.path.isdir(cls) or not any(n.endswith(".class") for n in os.listdir(cls)):
            return None, "não compilou: " + (c.stderr or c.stdout)[-600:]
        dex = os.path.join(trab, "dex", "controleir")
        os.makedirs(dex)
        for n in os.listdir(cls):
            shutil.copy(os.path.join(cls, n), dex)
        parcial = jar[:-4] + ".parcial.jar"
        d = subprocess.run(["dx", "--dex", f"--output={parcial}", os.path.join(trab, "dex")],
                           capture_output=True, text=True, timeout=180, check=False)
        if not os.path.exists(parcial):
            return None, "dx falhou: " + (d.stderr or d.stdout)[-600:]
        for velho in os.listdir(TMP):
            # o recém-compilado (.parcial.jar) também termina em .jar: apagá-lo foi o 1º erro no POCO (21/11)
            if velho.startswith("controle-bt-") and velho.endswith(".jar") and velho != os.path.basename(parcial):
                os.remove(os.path.join(TMP, velho))
        os.replace(parcial, jar)
        return jar, None
    finally:
        shutil.rmtree(trab, ignore_errors=True)


def ultima_linha_json(texto):
    for linha in reversed((texto or "").strip().splitlines()):
        linha = linha.strip()
        if linha.startswith("{"):
            try:
                return json.loads(linha)
            except ValueError:
                continue
    return None


def buscar(segundos, ligar=False, tela=None):
    tela = tela or _tela()
    jar, erro = compilar()
    if not jar:
        return {"erro": erro}
    pasta = tela._pasta_troca()
    copia = os.path.join(pasta, os.path.basename(jar))
    shutil.copy(jar, copia)
    destino = f"{tela.TMP_SHELL}/controle-bt.jar"
    ligou = False
    try:
        if ligar:
            estado, _, _ = tela.rish("settings get global bluetooth_on", timeout=10)
            if estado.strip() == "0":
                tela.rish("cmd bluetooth_manager enable; cmd bluetooth_manager wait-for-state:STATE_ON", timeout=20)
                ligou = True
                time.sleep(1)
        cmd = (f"cp {shlex.quote(copia)} {destino} && CLASSPATH={destino} app_process /system/bin "
               f"controleir.Bluetooth {int(segundos * 1000)} ble")
        out, err, cod = tela.rish(cmd, timeout=segundos + 25)
    finally:
        if ligou:
            tela.rish("cmd bluetooth_manager disable", timeout=15)
        try:
            os.remove(copia)
        except OSError:
            pass
    bruto = ultima_linha_json(out)
    if bruto is None:
        return {"erro": "o leitor Bluetooth não respondeu", "codigo": cod, "detalhe": (err or out or "")[-800:]}
    if ligou:
        bruto["ligado_para_buscar"] = True
    return bruto


def pareados_rapido(tela=None):
    tela = tela or _tela()
    out, err, _ = tela.rish("dumpsys bluetooth_manager", timeout=20)
    return ler_pareados_dumpsys(out)


def guardar(r):
    try:
        os.makedirs(os.path.dirname(ULTIMA), exist_ok=True)
        with open(ULTIMA, "w") as f:
            json.dump({"quando": time.strftime("%Y-%m-%d %H:%M:%S"), **r}, f, ensure_ascii=False)
    except OSError:
        pass


def main():
    a = json.loads(sys.stdin.read() or "{}")
    acao = a.get("acao", "buscar")
    try:
        if acao == "buscar":
            segundos = max(3, min(int(a.get("segundos", 10)), 30))
            bruto = buscar(segundos, bool(a.get("ligar")))
            if "erro" not in bruto and not bruto.get("pareados"):
                try:  # o leitor não teve permissão para os pareados: tenta pelo dumpsys
                    bruto["pareados"] = pareados_rapido()
                except Exception:  # noqa: BLE001
                    pass
            out = resumir(bruto, max(5, min(int(a.get("limite", 40)), 200)))
            if "erro" not in out:
                guardar(out)
        elif acao == "pareados":
            out = {"pareados": [{**p, "tipo": classificar(p)[0]} for p in pareados_rapido()]}
        elif acao == "ultima":
            try:
                with open(ULTIMA) as f:
                    out = json.load(f)
            except (OSError, ValueError):
                out = {"erro": "nenhuma busca guardada ainda"}
        else:
            out = {"erro": "acao deve ser buscar, pareados ou ultima"}
    except Exception as e:  # noqa: BLE001 — SemShizuku e afins viram resposta clara
        out = {"erro": str(e)[:400]}
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
