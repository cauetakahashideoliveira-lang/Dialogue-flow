"""Linha de comando ``controle-ir``.

    controle-ir                  inicia o serviço (servidor + túnel) e mostra a URL; se ele já estiver
                                 rodando (ex.: aberto pelo Termux:Boot), abre só o console
    controle-ir iniciar [--fundo]  inicia nesta sessão (--fundo: sem console, saída em servico.log)
    controle-ir inicio-automatico sim|nao|status   abre o serviço sozinho quando o celular liga (Termux:Boot)
    controle-ir log [-n N]       últimas linhas do registro do serviço em segundo plano
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
PREFIXO_TERMUX = os.environ.get("PREFIX") or "/data/data/com.termux/files/usr"
LIMITE_LOG = 1_000_000
# conexões com o próprio servidor nunca passam por proxy (HTTP_PROXY do ambiente)
_LOCAL = urllib.request.build_opener(urllib.request.ProxyHandler({}))


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


def _porta_ativa(c: dict | None = None) -> int:
    c = c or carregar_config()
    return int(estado_servidor().get("porta") or c["porta"])


def _api(acao: str, dados: dict | None = None, metodo="POST", sair=True) -> dict:
    c = carregar_config()
    url = f"http://127.0.0.1:{_porta_ativa(c)}/api/{acao}?t={c['segredo']}"
    req = urllib.request.Request(url, data=json.dumps(dados or {}).encode() if metodo == "POST" else None,
                                 headers={"Content-Type": "application/json"}, method=metodo)
    try:
        with _LOCAL.open(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode() or "{}")
        except ValueError:
            return {"erro": f"resposta HTTP {e.code}"}
    except OSError:
        if not sair:
            return {"erro": "o serviço não está respondendo (ainda iniciando ou parado)"}
        print("O serviço não está rodando. Abra o Termux e digite: controle-ir")
        sys.exit(1)


def _saude(porta: int, tempo: float = 1.5) -> bool:
    try:
        with _LOCAL.open(f"http://127.0.0.1:{int(porta)}/saude", timeout=tempo) as r:
            return json.loads(r.read().decode() or "{}").get("servico") == "controle-ir"
    except (OSError, ValueError):
        return False


def servico_ativo() -> dict | None:
    """Estado do serviço se ele responde em 127.0.0.1 (aberto aqui, em outra sessão ou pelo Termux:Boot)."""
    c = carregar_config()
    e = estado_servidor()
    for porta in dict.fromkeys([int(e.get("porta") or c["porta"]), int(c["porta"])]):
        if _saude(porta):
            return dict(e, porta=porta) if int(e.get("porta") or porta) == porta else {"porta": porta}
    return None


def _pid_do_servico(pid) -> bool:
    """O pid ainda é do controle-ir? (evita matar outro processo que herdou o número após reiniciar)."""
    try:
        cmd = Path(f"/proc/{int(pid)}/cmdline").read_bytes()
    except (OSError, ValueError):
        return False
    return b"controle_ir" in cmd or b"controle-ir" in cmd


def parar_servico(esperar: float = 15.0) -> bool:
    e = estado_servidor()
    pid = e.get("pid")
    ativo = servico_ativo()
    if pid and _pid_do_servico(pid):
        try:
            os.kill(int(pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            pid = None
    else:
        pid = None
    if not pid:
        if ativo:
            print("O serviço responde, mas não achei o processo dele. Feche a sessão do Termux em que ele roda "
                  "(digite sair nela).")
            return False
        (PASTA / "servidor.json").unlink(missing_ok=True)
        print("O serviço não está rodando.")
        return False
    porta = (ativo or {}).get("porta") or e.get("porta")
    limite = time.monotonic() + esperar
    while time.monotonic() < limite:
        if not _pid_do_servico(pid) and not (porta and _saude(porta, 0.5)):
            break
        time.sleep(0.3)
    (PASTA / "servidor.json").unlink(missing_ok=True)
    print("Serviço encerrado.")
    return True


# ----------------------------------------------------------------- segundo plano e Termux:Boot
def caminho_log() -> Path:
    return PASTA / "servico.log"


def arquivo_boot() -> Path:
    pasta = os.environ.get("CONTROLE_IR_BOOT_DIR") or str(Path.home() / ".termux" / "boot")
    return Path(pasta) / "controle-ir"


def boot_ativado() -> bool:
    return arquivo_boot().is_file()


def script_boot() -> str:
    cli = Path(PREFIXO_TERMUX) / "bin" / "controle-ir"
    return (f"#!{PREFIXO_TERMUX}/bin/sh\n"
            "# Início automático do Controle IR pelo app Termux:Boot.\n"
            "# Criado por: controle-ir inicio-automatico sim  ·  para desligar: controle-ir inicio-automatico nao\n"
            "# Registro: ~/.controle-ir/servico.log (controle-ir log)\n"
            "termux-wake-lock\n"
            f"exec \"{cli}\" iniciar --fundo\n")


def inicio_automatico(acao: str, silencioso: bool = False) -> int:
    arq = arquivo_boot()
    if acao == "status":
        print("Início automático: " + (f"ATIVADO ({arq})" if boot_ativado() else "desativado"))
        return 0 if boot_ativado() else 1
    if acao == "nao":
        if arq.exists():
            arq.unlink()
            print("Início automático desativado. O serviço não abrirá mais sozinho quando o celular ligar.")
        else:
            print("O início automático já estava desativado.")
        return 0
    arq.parent.mkdir(parents=True, exist_ok=True)
    tmp = arq.with_name(arq.name + ".novo")
    tmp.write_text(script_boot())
    os.chmod(tmp, 0o700)
    os.replace(tmp, arq)
    if silencioso:
        print("Início automático: script atualizado.")
        return 0
    print("✔ Início automático ativado: o serviço abrirá em segundo plano quando o celular ligar.")
    print("  Falta, uma vez só, no celular:")
    print("  1. Instale o app Termux:Boot do F-Droid (mesma fonte do Termux) e ABRA-O uma vez.")
    print("  2. HyperOS: Configurações → Apps → Termux:Boot → Início automático: ativado;")
    print("     Economia de bateria: Sem restrições (o mesmo para Termux e Termux:API).")
    print("  A URL do conector não muda. Para conferir depois de reiniciar o celular: abra o Termux e")
    print("  digite  controle-ir  (abre só o console do serviço que já está rodando).")
    print("  A partir de agora,  controle-ir  também abre o serviço em segundo plano: fechar o Termux")
    print("  ou usar CTRL+C no console não derruba mais o conector. Para encerrar: controle-ir parar")
    return 0


def _redirecionar_para_log():
    """Modo --fundo: sem terminal; stdin vazio e toda a saída anexada a servico.log (permissão 600)."""
    log = caminho_log()
    log.parent.mkdir(parents=True, exist_ok=True)
    try:
        if log.exists() and log.stat().st_size > LIMITE_LOG:
            os.replace(log, log.with_name(log.name + ".1"))
    except OSError:
        pass
    fd = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    os.chmod(log, 0o600)
    nulo = os.open(os.devnull, os.O_RDONLY)
    os.dup2(nulo, 0)
    os.dup2(fd, 1)
    os.dup2(fd, 2)
    os.close(fd)
    os.close(nulo)
    for f in (sys.stdout, sys.stderr):
        try:
            f.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except (AttributeError, ValueError):
            pass


def iniciar_em_segundo_plano() -> int:
    """Abre ``controle-ir iniciar --fundo`` desligado deste terminal; devolve a posição do log antes do início."""
    log = caminho_log()
    pos = log.stat().st_size if log.exists() else 0
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PACOTE) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env["PYTHONUNBUFFERED"] = "1"
    subprocess.Popen([sys.executable, "-m", "controle_ir", "iniciar", "--fundo"], stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True,
                     cwd=str(Path.home()), env=env)
    return pos


def mostrar_log(n: int = 40) -> int:
    log = caminho_log()
    if not log.exists():
        print("Ainda não há registro: ele é criado quando o serviço roda em segundo plano "
              "(Termux:Boot ou controle-ir com o início automático ativado).")
        return 1
    with open(log, "rb") as f:
        f.seek(max(0, log.stat().st_size - 200_000))
        linhas = f.read().decode("utf-8", "replace").splitlines()
    print("\n".join(linhas[-max(1, n):]))
    return 0


def _seguir_log(desde: int | None, parar_ev: threading.Event):
    log = caminho_log()
    f = None
    pos = desde
    while not parar_ev.is_set():
        try:
            if f is None:
                if not log.exists():
                    parar_ev.wait(0.5)
                    continue
                f = open(log, "r", encoding="utf-8", errors="replace")
                f.seek(pos if pos is not None and pos <= log.stat().st_size else
                       (0 if pos is not None else log.stat().st_size))
            linha = f.readline()
            if linha:
                print(linha.rstrip("\n"), flush=True)
                pos = f.tell()
                continue
            if log.exists() and log.stat().st_size < (pos or 0):  # log girado
                f.close()
                f, pos = None, 0
                continue
            parar_ev.wait(0.5)
        except OSError:
            f, pos = None, None
            parar_ev.wait(1)


def console(estado: dict | None = None, desde_log: int | None = None) -> int:
    """Console de um serviço que roda fora deste terminal: Enter pausa a busca, c continua etc.
    Sair do console (sair, CTRL+C ou fechar o Termux) não encerra o serviço."""
    c = carregar_config()
    if estado:
        desde = time.strftime("%H:%M", time.localtime(estado["iniciado"])) if estado.get("iniciado") else None
        print("O Controle IR já está rodando" + (" em segundo plano" if estado.get("fundo") else "") +
              (f" (desde {desde})." if desde else "."))
    else:
        print("Abrindo o Controle IR em segundo plano… (o registro aparece abaixo)")
    parar_ev = threading.Event()
    threading.Thread(target=_seguir_log, args=(desde_log, parar_ev), name="log", daemon=True).start()
    t0 = time.time() - 2

    def url_quando_pronta():
        fim = time.monotonic() + 900
        while not parar_ev.is_set() and time.monotonic() < fim:
            e = estado_servidor()
            recente = estado is not None or (e.get("iniciado") or 0) >= t0  # não a URL de uma execução antiga
            if e.get("url") and recente and servico_ativo():
                mostrar_url(e["url"] + f"/mcp/{c['segredo']}", console=True)
                return
            parar_ev.wait(1)
    threading.Thread(target=url_quando_pronta, name="url", daemon=True).start()
    try:
        while True:
            linha = input().strip().lower()
            if linha == "":
                r = _api("pausar", {"origem": "Enter no console"}, sair=False)
                if "erro" in r:
                    print(f"(nada pausado: {r['erro']})")
                else:
                    print("⏸  Busca pausada.")
                    for s in r.get("suspeitos", []):
                        print(f"   suspeito nº {s['numero']} ({s.get('segundos_antes_da_pausa')} s antes da pausa)")
                    print("   Conte ao Claude o que aconteceu (ex.: “ligou”).")
            elif linha in ("c", "continuar"):
                r = _api("retomar", sair=False)
                print("▶  Busca retomada." if "erro" not in r else r["erro"])
            elif linha in ("copiar", "copy"):
                url = estado_servidor().get("url")
                if url and _termux("termux-clipboard-set", url + f"/mcp/{c['segredo']}"):
                    print("✔ URL copiada. Cole direto no cadastro do conector no Claude.")
                else:
                    print("A URL ainda não está pronta ou o Termux:API não respondeu.")
            elif linha == "url":
                url = estado_servidor().get("url")
                print(f"{url}/mcp/{c['segredo']}" if url else "túnel ainda não está ativo")
            elif linha in ("painel", "p"):
                _termux("termux-open-url", f"http://127.0.0.1:{_porta_ativa(c)}/painel?t={c['segredo']}")
            elif linha == "log":
                mostrar_log(30)
            elif linha == "parar":
                parar_servico()
                return 0
            elif linha in ("sair", "q"):
                break
            elif linha in ("ajuda", "?", "h"):
                print("Enter = pausar · c = continuar · copiar · url · painel · log · "
                      "parar = encerra o serviço · sair = fecha só este console")
    except (EOFError, KeyboardInterrupt):
        print()
    finally:
        parar_ev.set()
    print("Console fechado; o serviço continua rodando. Para encerrar: controle-ir parar")
    return 0


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
def _travar_inicio():
    """Trava exclusiva enquanto um início confere a porta, reconstrói o catálogo e abre o servidor:
    o Termux:Boot e um controle-ir digitado ao mesmo tempo não reconstroem o catálogo juntos."""
    try:
        import fcntl
    except ImportError:  # pragma: no cover — fora do Linux/Android
        return None
    PASTA.mkdir(parents=True, exist_ok=True)
    f = open(PASTA / ".iniciar.trava", "w")
    fcntl.flock(f, fcntl.LOCK_EX)
    return f


def _soltar_inicio(f):
    if f is not None and not f.closed:
        try:
            import fcntl
            fcntl.flock(f, fcntl.LOCK_UN)
        finally:
            f.close()


def iniciar(args):
    trava = _travar_inicio()
    try:
        return _iniciar(args, trava)
    finally:
        _soltar_inicio(trava)  # normalmente já solta logo após abrir o servidor


def _iniciar(args, trava):
    from .servico import Servico
    from .servidor import Notificador, criar_servidor
    from .tunel import Tunel

    c = carregar_config()
    porta = int(args.porta or c["porta"])
    fundo = bool(getattr(args, "fundo", False))
    tty = bool(sys.stdin and sys.stdin.isatty())
    ativo = servico_ativo()
    if ativo:
        _soltar_inicio(trava)
        if tty and not fundo:
            return console(ativo, None)
        print("O serviço já está rodando; nada a fazer.")
        return 0
    if fundo:
        _redirecionar_para_log()
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        print(f"\n=== controle-ir {__version__} em segundo plano · {time.strftime('%d/%m/%Y %H:%M:%S')} "
              f"· pid {os.getpid()} ===", flush=True)
    if not catalogo_atual():
        print("Preparando o catálogo de controles…")
        reconstruir_catalogo(silencioso=fundo)
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
    _soltar_inicio(trava)
    _termux("termux-wake-lock")
    inicio = time.time()

    def gravar_estado(url=None):
        d = {"pid": os.getpid(), "porta": porta, "url": url, "iniciado": inicio, "fundo": fundo,
             "versao": __version__}
        f = PASTA / "servidor.json"
        f.write_text(json.dumps(d))
        os.chmod(f, 0o600)

    def ao_mudar_url(url):
        servico.url_publica = url
        gravar_estado(url)
        mudou = bool(estado_anterior.get("url")) and estado_anterior.get("url") != url
        if fundo:
            # o registro nunca leva o segredo: só o endereço do túnel
            print(f"{time.strftime('%H:%M:%S')} túnel ativo em {url}" +
                  (" — A URL MUDOU: atualize o conector no Claude (controle-ir copiar)" if mudou else ""),
                  flush=True)
            notificar.servico_ativo(url)
        else:
            mostrar_url(url + f"/mcp/{c['segredo']}", mudou=mudou)
        estado_anterior["url"] = url

    estado_anterior = {"url": estado_servidor().get("url")}
    gravar_estado(None)
    tunel_cfg = {"modo": "nenhum"} if args.sem_tunel else c["tunel"]
    tunel = Tunel(porta, tunel_cfg, ao_mudar_url, log=lambda *a: print(time.strftime("%H:%M:%S"), *a, flush=True))
    tunel.iniciar()
    if tunel_cfg.get("modo") == "nenhum":
        print(f"Servidor local em http://127.0.0.1:{porta}/mcp/<segredo> (sem túnel).")
        if fundo:
            notificar.servico_ativo(None)
    else:
        print("Abrindo o túnel seguro… (pode levar até 30 s)", flush=True)

    def encerrar(*_):
        tunel.parar()
        notificar.limpar()
        notificar.servico_ativo(None, encerrar=True)
        _termux("termux-wake-unlock")
        (PASTA / "servidor.json").unlink(missing_ok=True)
        os._exit(0)

    signal.signal(signal.SIGTERM, encerrar)
    signal.signal(signal.SIGINT, encerrar)
    if fundo or not tty:
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


def mostrar_url(url_mcp: str, mudou: bool = False, console: bool = False):
    linha = "═" * 46
    print(f"\n{linha}")
    if mudou:
        print(" A URL DO TÚNEL MUDOU — atualize o conector no Claude")
    print(" Controle IR pronto" + (" (em segundo plano)" if console else ""))
    print(" URL privada do conector (não compartilhe; cubra em capturas):")
    print(f" {url_mcp}")
    print("")
    print(" Digite  copiar  e Enter para copiar a URL.")
    print(" Enter sozinho = pausar a busca · c = continuar")
    if console:
        print(" painel · log · parar = encerra o serviço · sair = fecha só este console")
    else:
        print(" painel = abrir o painel · sair = encerrar")
    print(f"{linha}\n", flush=True)


# ----------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(prog="controle-ir", description="Controle infravermelho universal + Claude (MCP)")
    ap.add_argument("--versao", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("iniciar")
    p.add_argument("--porta", type=int)
    p.add_argument("--simulado", action="store_true", help="sem emissor real (testes)")
    p.add_argument("--sem-tunel", action="store_true")
    p.add_argument("--fundo", action="store_true", help="sem console; saída em ~/.controle-ir/servico.log")
    for n in ("copiar", "pausar", "retomar", "painel", "status", "url", "parar", "novo-segredo", "testar-emissor"):
        sub.add_parser(n)
    pb = sub.add_parser("inicio-automatico", help="abre o serviço quando o celular liga (app Termux:Boot)")
    pb.add_argument("acao", nargs="?", default="status", choices=["sim", "nao", "status"])
    pb.add_argument("--silencioso", action="store_true")
    pl = sub.add_parser("log", help="últimas linhas do registro do serviço em segundo plano")
    pl.add_argument("-n", type=int, default=40)
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
            if sys.stdin and sys.stdin.isatty():
                ativo = servico_ativo()
                if ativo:
                    return console(ativo, None)
                if boot_ativado():
                    # com o início automático o serviço sempre vive fora do terminal
                    return console(None, iniciar_em_segundo_plano())
        return iniciar(a)
    if cmd == "inicio-automatico":
        return inicio_automatico(a.acao, a.silencioso)
    if cmd == "log":
        return mostrar_log(a.n)
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
        _termux("termux-open-url", f"http://127.0.0.1:{_porta_ativa(c)}/painel?t={c['segredo']}")
        return 0
    if cmd == "status":
        ativo = servico_ativo()
        print("Serviço: " + ("rodando" + (" em segundo plano" if (ativo or {}).get("fundo") else "")
                             if ativo else "parado"))
        print("Início automático (Termux:Boot): " + ("ativado" if boot_ativado() else "desativado"))
        if ativo:
            print(json.dumps(_api("estado", metodo="GET"), ensure_ascii=False, indent=1)[:4000])
        return 0
    if cmd == "parar":
        parar_servico()
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
