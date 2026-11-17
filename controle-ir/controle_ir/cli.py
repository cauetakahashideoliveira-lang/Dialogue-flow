"""Linha de comando ``controle-ir``.

    controle-ir                  inicia o serviço (servidor + túnel) e mostra a URL
    controle-ir copiar           copia a URL privada do conector
    controle-ir pausar|retomar   controla a busca em andamento
    controle-ir painel           abre o painel no navegador do celular
    controle-ir status           mostra o estado
    controle-ir catalogo reconstruir|ampliar|info
    controle-ir importar ARQUIVO [--aparelho NOME | --nome NOME]
    controle-ir tunel rapido | cloudflare --token T --url URL | ngrok --dominio D
    controle-ir novo-segredo     invalida a URL antiga e gera outra
    controle-ir parar            encerra o serviço em segundo plano
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.request
import zipfile
from pathlib import Path

from . import __version__, catalogo as cat_mod
from .emissor import EmissorSimulado, EmissorTermux

PASTA = Path(os.environ.get("CONTROLE_IR_DIR", Path.home() / ".controle-ir"))
PACOTE = Path(__file__).resolve().parent.parent
DADOS = PACOTE / "dados"
URL_FLIPPER = "https://codeload.github.com/Lucaslhm/Flipper-IRDB/zip/refs/heads/main"


def _cfg_caminho():
    return PASTA / "config.json"


def carregar_config() -> dict:
    PASTA.mkdir(parents=True, exist_ok=True)
    c = {}
    if _cfg_caminho().exists():
        try:
            c = json.loads(_cfg_caminho().read_text())
        except json.JSONDecodeError:
            c = {}
    mudou = False
    if not c.get("segredo"):
        c["segredo"] = secrets.token_urlsafe(32)
        mudou = True
    c.setdefault("porta", 8765)
    c.setdefault("tunel", {"modo": "rapido"})
    if mudou or not _cfg_caminho().exists():
        salvar_config(c)
    return c


def salvar_config(c: dict):
    PASTA.mkdir(parents=True, exist_ok=True)
    _cfg_caminho().write_text(json.dumps(c, indent=1))
    os.chmod(_cfg_caminho(), 0o600)


def estado_servidor() -> dict:
    f = PASTA / "servidor.json"
    try:
        return json.loads(f.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _api(acao: str, dados: dict | None = None, metodo="POST") -> dict:
    c = carregar_config()
    url = f"http://127.0.0.1:{c['porta']}/api/{acao}?t={c['segredo']}"
    req = urllib.request.Request(url, data=json.dumps(dados or {}).encode() if metodo == "POST" else None,
                                 headers={"Content-Type": "application/json"}, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode() or "{}")
    except OSError:
        print("O serviço não está rodando. Abra o Termux e digite: controle-ir")
        sys.exit(1)


def _termux(*args) -> bool:
    if shutil.which(args[0]):
        try:
            subprocess.run(list(args), timeout=15)
            return True
        except (OSError, subprocess.TimeoutExpired):
            return False
    return False


def progresso_txt(prefixo):
    def f(i, n):
        if n:
            print(f"\r{prefixo}: {i}/{n}", end="", flush=True)
        else:
            print(f"\r{prefixo}: {i}", end="", flush=True)
    return f


# ----------------------------------------------------------------- catálogo
def reconstruir_catalogo(silencioso=False) -> dict:
    destino = PASTA / "catalogo.sqlite"
    tmp = PASTA / "catalogo.novo.sqlite"
    for f in (tmp, Path(str(tmp) + "-wal"), Path(str(tmp) + "-shm")):
        f.unlink(missing_ok=True)
    c = cat_mod.Catalogo(tmp)
    r = {}
    base = DADOS / "base.jsonl.gz"
    if base.exists():
        r["base"] = cat_mod.importar_jsonl(c, str(base), None if silencioso else progresso_txt("catálogo base"))
        if not silencioso:
            print()
    fl = PASTA / "fontes" / "Flipper-IRDB-main"
    if fl.exists():
        r["flipper"] = cat_mod.importar_flipper(c, str(fl), progresso=None if silencioso else
                                                progresso_txt("Flipper-IRDB"))
        if not silencioso:
            print()
    imp = PASTA / "importados"
    if imp.exists():
        from . import formatos
        n = 0
        for f in sorted(imp.glob("*.json")):
            try:
                p = json.loads(f.read_text())
                formatos.validar_perfil(p)
                c.adicionar_perfil(p)
                n += 1
            except (ValueError, KeyError, formatos.ErroFormato):
                pass
        c.commit()
        c.registrar_fonte("usuario")
        r["importados"] = n
    c.db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    c.fechar()
    for suf in ("-wal", "-shm"):
        Path(str(tmp) + suf).unlink(missing_ok=True)
        Path(str(destino) + suf).unlink(missing_ok=True)
    os.replace(tmp, destino)
    (PASTA / "catalogo.versao").write_text(__version__ + ":" + str(base.stat().st_mtime if base.exists() else 0))
    return r


def catalogo_atual() -> bool:
    base = DADOS / "base.jsonl.gz"
    v = PASTA / "catalogo.versao"
    esperado = __version__ + ":" + str(base.stat().st_mtime if base.exists() else 0)
    return (PASTA / "catalogo.sqlite").exists() and v.exists() and v.read_text() == esperado


def ampliar_catalogo(confirmado=False, incluir_convertidos=True):
    print("A Flipper-IRDB completa tem cerca de 9 mil controles de dezenas de categorias.")
    print("Aviso de licença: o repositório adota CC0 só para contribuições a partir de agosto de 2025;")
    print("os arquivos anteriores não declaram licença. O download é feito por você, para uso pessoal.")
    if not confirmado:
        r = input("Baixar agora (~40 MB)? [S/n] ").strip().lower()
        if r not in ("", "s", "sim", "y"):
            print("Mantido apenas o catálogo base.")
            return
    fontes = PASTA / "fontes"
    fontes.mkdir(parents=True, exist_ok=True)
    zipf = fontes / "flipper-irdb.zip"
    print("Baixando Flipper-IRDB…")
    ok = False
    if shutil.which("curl"):
        ok = subprocess.run(["curl", "-fL", "--retry", "3", "-o", str(zipf), URL_FLIPPER]).returncode == 0
    if not ok:
        try:
            urllib.request.urlretrieve(URL_FLIPPER, zipf)
            ok = True
        except OSError as e:
            print(f"Falha no download: {e}")
            return
    destino = fontes / "Flipper-IRDB-main"
    if destino.exists():
        shutil.rmtree(destino)
    print("Extraindo…")
    with zipfile.ZipFile(zipf) as z:
        membros = [m for m in z.namelist() if m.endswith(".ir") or m.endswith("LICENSE")]
        if not incluir_convertidos:
            membros = [m for m in membros if "/_Converted_/" not in m]
        z.extractall(fontes, membros)
    zipf.unlink(missing_ok=True)
    print("Convertendo para o catálogo (alguns minutos no celular)…")
    r = reconstruir_catalogo()
    print(f"Pronto: {json.dumps(r, ensure_ascii=False)}")


# ----------------------------------------------------------------- serviço
def iniciar(args):
    from .servico import Servico
    from .servidor import Notificador, criar_servidor
    from .tunel import Tunel

    c = carregar_config()
    porta = int(args.porta or c["porta"])
    if not catalogo_atual():
        print("Preparando o catálogo de controles…")
        reconstruir_catalogo()
    emissor = EmissorSimulado() if args.simulado else EmissorTermux()
    disp = emissor.disponivel()
    if disp.get("disponivel"):
        faixas = ", ".join(f"{f['min'] // 1000} kHz" for f in disp["faixas_hz"])
        print(f"Emissor infravermelho encontrado ({faixas}).")
    else:
        print(f"ATENÇÃO: emissor indisponível — {disp.get('motivo')}")
    notificar = Notificador(voz=c.get("voz", True))
    servico = Servico(str(PASTA), emissor, cat_mod.Catalogo(PASTA / "catalogo.sqlite"), notificar)
    try:
        srv = criar_servidor(servico, c["segredo"], porta)
    except OSError:
        print(f"A porta {porta} já está em uso: o serviço provavelmente já está aberto em outra sessão do Termux.")
        print("Use  controle-ir parar  e tente de novo.")
        sys.exit(1)
    threading.Thread(target=srv.serve_forever, name="http", daemon=True).start()
    _termux("termux-wake-lock")

    def gravar_estado(url=None):
        d = {"pid": os.getpid(), "porta": porta, "url": url, "iniciado": time.time()}
        f = PASTA / "servidor.json"
        f.write_text(json.dumps(d))
        os.chmod(f, 0o600)

    def ao_mudar_url(url):
        servico.url_publica = url
        gravar_estado(url)
        mostrar_url(url + f"/mcp/{c['segredo']}", mudou=bool(estado_anterior.get("url")) and
                    estado_anterior.get("url") != url)
        estado_anterior["url"] = url

    estado_anterior = {"url": estado_servidor().get("url")}
    gravar_estado(None)
    tunel_cfg = {"modo": "nenhum"} if args.sem_tunel else c["tunel"]
    tunel = Tunel(porta, tunel_cfg, ao_mudar_url, log=lambda *a: print(*a))
    tunel.iniciar()
    if tunel_cfg.get("modo") == "nenhum":
        print(f"Servidor local em http://127.0.0.1:{porta}/mcp/<segredo> (sem túnel).")
    else:
        print("Abrindo o túnel seguro… (pode levar até 30 s)")

    def encerrar(*_):
        tunel.parar()
        notificar.limpar()
        _termux("termux-wake-unlock")
        (PASTA / "servidor.json").unlink(missing_ok=True)
        os._exit(0)

    signal.signal(signal.SIGTERM, encerrar)
    signal.signal(signal.SIGINT, encerrar)
    if not sys.stdin or not sys.stdin.isatty():
        while True:
            time.sleep(3600)
    while True:
        try:
            linha = input().strip().lower()
        except EOFError:
            while True:
                time.sleep(3600)
        if linha == "":
            if servico.desc.s and servico.desc.s.get("estado") == "executando":
                r = servico.pausar("Enter no Termux")
                print("⏸  Busca pausada.")
                for s in r.get("suspeitos", []):
                    print(f"   suspeito nº {s['numero']} ({s.get('segundos_antes_da_pausa')} s antes da pausa)")
                print("   Conte ao Claude o que aconteceu (ex.: “ligou”).")
            else:
                print("(nenhuma busca em andamento — Enter pausa durante os testes)")
        elif linha in ("copiar", "copy"):
            url = servico.url_publica
            if url and _termux("termux-clipboard-set", url + f"/mcp/{c['segredo']}"):
                print("✔ URL copiada. Cole direto no cadastro do conector no Claude.")
            else:
                print("A URL ainda não está pronta ou o Termux:API não respondeu.")
        elif linha in ("c", "continuar"):
            try:
                servico.retomar()
                print("▶  Busca retomada.")
            except Exception as e:  # noqa: BLE001
                print(e)
        elif linha in ("painel", "p"):
            _termux("termux-open-url", f"http://127.0.0.1:{porta}/painel?t={c['segredo']}")
        elif linha in ("url",):
            if servico.url_publica:
                mostrar_url(servico.url_publica + f"/mcp/{c['segredo']}")
        elif linha in ("sair", "q", "parar"):
            encerrar()
        elif linha in ("ajuda", "?", "h"):
            print("Enter = pausar · c = continuar · copiar · url · painel · sair")


def mostrar_url(url_mcp: str, mudou: bool = False):
    linha = "═" * 46
    print(f"\n{linha}")
    if mudou:
        print(" A URL DO TÚNEL MUDOU — atualize o conector no Claude")
    print(" Controle IR pronto")
    print(" URL privada do conector (não compartilhe; cubra em capturas):")
    print(f" {url_mcp}")
    print("")
    print(" Digite  copiar  e Enter para copiar a URL.")
    print(" Enter sozinho = pausar a busca · c = continuar")
    print(" painel = abrir o painel · sair = encerrar")
    print(f"{linha}\n")


# ----------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(prog="controle-ir", description="Controle infravermelho universal + Claude (MCP)")
    ap.add_argument("--versao", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("iniciar")
    p.add_argument("--porta", type=int)
    p.add_argument("--simulado", action="store_true", help="sem emissor real (testes)")
    p.add_argument("--sem-tunel", action="store_true")
    for n in ("copiar", "pausar", "retomar", "painel", "status", "url", "parar", "novo-segredo", "testar-emissor"):
        sub.add_parser(n)
    pv = sub.add_parser("voz", help="liga/desliga o número falado a cada teste")
    pv.add_argument("estado", choices=["sim", "nao"])
    pc = sub.add_parser("catalogo")
    pc.add_argument("acao", choices=["reconstruir", "ampliar", "info"])
    pc.add_argument("--sim", action="store_true")
    pc.add_argument("--sem-convertidos", action="store_true")
    pi = sub.add_parser("importar")
    pi.add_argument("arquivo")
    pi.add_argument("--aparelho")
    pi.add_argument("--nome")
    pi.add_argument("--categoria")
    pt = sub.add_parser("tunel")
    pt.add_argument("modo", choices=["rapido", "cloudflare", "ngrok", "nenhum"])
    pt.add_argument("--token")
    pt.add_argument("--url")
    pt.add_argument("--dominio")
    a = ap.parse_args(argv)
    cmd = a.cmd or "iniciar"
    if cmd == "iniciar":
        if not a.cmd:
            a = ap.parse_args(["iniciar"])
        return iniciar(a)
    c = carregar_config()
    if cmd == "copiar":
        url = estado_servidor().get("url")
        if not url:
            print("O túnel ainda não está ativo. Abra o serviço com: controle-ir")
            return 1
        if _termux("termux-clipboard-set", f"{url}/mcp/{c['segredo']}"):
            print("✔ URL copiada.")
        return 0
    if cmd == "url":
        url = estado_servidor().get("url")
        print(f"{url}/mcp/{c['segredo']}" if url else "túnel inativo")
        return 0
    if cmd == "pausar":
        r = _api("pausar", {"origem": "notificação"})
        print("⏸  Pausado." if "erro" not in r else r["erro"])
        _termux("termux-toast", "Busca pausada")
        return 0
    if cmd == "retomar":
        r = _api("retomar")
        print("▶  Retomado." if "erro" not in r else r["erro"])
        return 0
    if cmd == "painel":
        _termux("termux-open-url", f"http://127.0.0.1:{c['porta']}/painel?t={c['segredo']}")
        return 0
    if cmd == "status":
        print(json.dumps(_api("estado", metodo="GET"), ensure_ascii=False, indent=1)[:4000])
        return 0
    if cmd == "parar":
        pid = estado_servidor().get("pid")
        if pid:
            try:
                os.kill(int(pid), signal.SIGTERM)
                print("Serviço encerrado.")
            except ProcessLookupError:
                print("O serviço já não estava rodando.")
            (PASTA / "servidor.json").unlink(missing_ok=True)
        else:
            print("O serviço não está rodando.")
        return 0
    if cmd == "novo-segredo":
        c["segredo"] = secrets.token_urlsafe(32)
        salvar_config(c)
        print("Novo segredo criado. Reinicie o serviço e atualize a URL do conector no Claude.")
        return 0
    if cmd == "voz":
        c["voz"] = a.estado == "sim"
        salvar_config(c)
        print(f"Voz {'ligada' if c['voz'] else 'desligada'}. Reinicie o serviço (sair e controle-ir).")
        return 0
    if cmd == "testar-emissor":
        print(json.dumps(EmissorTermux().disponivel(), ensure_ascii=False))
        return 0
    if cmd == "catalogo":
        if a.acao == "reconstruir":
            print(json.dumps(reconstruir_catalogo(), ensure_ascii=False))
        elif a.acao == "ampliar":
            ampliar_catalogo(a.sim, not a.sem_convertidos)
        else:
            k = cat_mod.Catalogo(PASTA / "catalogo.sqlite")
            print(json.dumps(k.estatisticas(), ensure_ascii=False, indent=1))
        return 0
    if cmd == "importar":
        texto = Path(a.arquivo).expanduser().read_text(errors="ignore")
        r = _api("importar", {"conteudo": texto, "nome": a.nome, "categoria": a.categoria})
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0
    if cmd == "tunel":
        t = {"modo": a.modo}
        if a.modo == "cloudflare":
            if not (a.token and a.url):
                print("use: controle-ir tunel cloudflare --token <token do túnel> --url https://seu.dominio")
                return 1
            t.update(token=a.token, url=a.url)
        if a.modo == "ngrok":
            if not a.dominio:
                print("use: controle-ir tunel ngrok --dominio seu-nome.ngrok-free.app")
                return 1
            dom = a.dominio.strip().removeprefix("https://").removeprefix("http://").strip("/")
            if dom.startswith("rd_") or "." not in dom:
                print("Isso parece o código interno (rd_...). Use o endereço, ex.: nome-1234.ngrok-free.app")
                return 1
            t.update(dominio=dom, url=f"https://{dom}")
        c["tunel"] = t
        salvar_config(c)
        print(f"Túnel configurado: {a.modo}. Reinicie com: controle-ir parar; controle-ir")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
