"""PS4 pelo Remote Play: controle completo + habilidades + jogador que aprende. Entrada/saída: JSON.

Roda dentro do serviço (em_processo): a sessão com o PS4, o controle virtual e o jogador ficam abertos entre as
chamadas. Só para jogo offline (contra a máquina): bot contra pessoas viola os termos da PSN.
"""
import base64
import importlib.util
import json
import os
import sys
import threading
import time
import zlib

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("CONTROLE_IR_DIR") or os.path.expanduser("~/.controle-ir")
PASTA = os.path.join(BASE, "ps4")
CONF = os.path.join(PASTA, "ps4.json")
HAB = os.path.join(PASTA, "habilidades.json")
PARAR = os.path.join(BASE, "PARAR")
LIMITE_SINCRONO_S = 40.0


def _mod(nome):
    chave = f"ps4_{nome}"
    if chave not in sys.modules:
        spec = importlib.util.spec_from_file_location(chave, os.path.join(AQUI, f"{nome}.py"))
        m = importlib.util.module_from_spec(spec)
        sys.modules[chave] = m
        spec.loader.exec_module(m)
    return sys.modules[chave]


controle = _mod("controle")


# --------------------------------------------------------------------------- arquivos
def _ler(caminho, padrao):
    try:
        with open(caminho) as f:
            return json.load(f)
    except (OSError, ValueError):
        return padrao


def _gravar(caminho, dados):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    tmp = caminho + ".tmp"
    with open(tmp, "w") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)
    os.replace(tmp, caminho)


def habilidades():
    return _ler(HAB, {})


# --------------------------------------------------------------------------- imagem
def _png(rgb):
    import numpy as np
    a = np.ascontiguousarray(rgb[..., :3], dtype=np.uint8)
    h, w = a.shape[:2]
    cru = b"".join(b"\x00" + a[i].tobytes() for i in range(h))

    def bloco(tipo, dados):
        c = tipo + dados
        return len(dados).to_bytes(4, "big") + c + (zlib.crc32(c) & 0xFFFFFFFF).to_bytes(4, "big")
    cab = w.to_bytes(4, "big") + h.to_bytes(4, "big") + bytes([8, 2, 0, 0, 0])
    return (b"\x89PNG\r\n\x1a\n" + bloco(b"IHDR", cab) + bloco(b"IDAT", zlib.compress(cru, 6))
            + bloco(b"IEND", b""))


def reduzir_imagem(rgb, largura=640, recorte=None):
    import numpy as np
    a = np.asarray(rgb)
    if recorte:
        H, W = a.shape[:2]
        x, y, w, h = [float(v) for v in recorte]
        a = a[int(y * H):max(int(y * H) + 1, int((y + h) * H)), int(x * W):max(int(x * W) + 1, int((x + w) * W))]
    passo = max(1, int(round(a.shape[1] / max(64, int(largura)))))
    return a[::passo, ::passo]


def codificar(rgb):
    """JPEG pelo av (ffmpeg) quando houver; senão PNG puro."""
    try:
        import av
        h, w = rgb.shape[:2]
        h, w = h - h % 2, w - w % 2
        cc = av.CodecContext.create("mjpeg", "w")
        cc.width, cc.height, cc.pix_fmt = w, h, "yuvj420p"
        cc.options = {"qscale": "5"}
        fr = av.VideoFrame.from_ndarray(rgb[:h, :w, :3].copy(), format="rgb24").reformat(format="yuvj420p")
        dados = b"".join(bytes(p) for p in cc.encode(fr) + cc.encode(None))
        if dados:
            return "image/jpeg", dados
    except Exception:  # noqa: BLE001
        pass
    return "image/png", _png(rgb)


def imagem_json(rgb, largura=640, recorte=None):
    mime, dados = codificar(reduzir_imagem(rgb, largura, recorte))
    return {"mime": mime, "base64": base64.b64encode(dados).decode()}


# --------------------------------------------------------------------------- estado do processo
class Estado:
    def __init__(self):
        self.con = None
        self.trava = threading.Lock()
        self.tarefa = None  # thread de comando longo
        self.tarefa_info = {}
        self.parar_tarefa = threading.Event()
        self.jogador = None
        self.jog_th = None
        self.jog_parar = threading.Event()
        self.jog_info = {}

    def conexao(self):
        if self.con is None:
            self.con = _mod("conexao").Conexao(PASTA)
        return self.con

    def ocupado(self):
        if self.jog_th and self.jog_th.is_alive():
            return "o jogador está jogando (acao=jogador modo=parar)"
        if self.tarefa and self.tarefa.is_alive():
            return "um comando longo ainda está rodando (acao=parar)"
        return None


E = Estado()


def _parar_global():
    return os.path.exists(PARAR)


def _ip(a):
    ip = a.get("ip") or _ler(CONF, {}).get("ip")
    if not ip:
        raise RuntimeError("informe ip do PS4 (acao=procurar mostra)")
    return ip


# --------------------------------------------------------------------------- comandos
def rodar_comando(passos, origem="comando"):
    atom = controle.normalizar(passos, habilidades())
    with E.trava:
        return controle.executar(atom, E.conexao(), parar=lambda: E.parar_tarefa.is_set() or _parar_global())


def cmd_comando(a):
    if not E.conexao().conectado:
        return {"erro": "PS4 não conectado (acao=conectar)"}
    ocup = E.ocupado()
    if ocup:
        return {"erro": ocup}
    passos = a.get("passos")
    if passos is None:
        return {"erro": "informe passos (lista ou texto: 'x x r2:600 esperar:300')"}
    atom = controle.normalizar(passos, habilidades())
    dur = controle.duracao(atom)
    E.parar_tarefa.clear()
    demo = None
    if a.get("demonstrar") and E.jogador:
        nomes = [p["habilidade"] for p in (passos if isinstance(passos, list) else []) if isinstance(p, dict)
                 and "habilidade" in p]
        q = E.conexao().quadro()
        if q is not None and nomes:
            demo = {"estado": E.jogador.demonstrar(q, nomes[0]), "habilidade": nomes[0]}
            E.jogador.salvar()
    if dur > LIMITE_SINCRONO_S:
        def fundo():
            E.tarefa_info = {"inicio": time.time(), "duracao_prevista_s": dur}
            try:
                E.tarefa_info["resultado"] = rodar_comando(passos)
            except Exception as e:  # noqa: BLE001
                E.tarefa_info["erro"] = str(e)
        E.tarefa = threading.Thread(target=fundo, name="ps4-comando", daemon=True)
        E.tarefa.start()
        return {"em_segundo_plano": True, "duracao_prevista_s": dur, "passos_atomicos": len(atom),
                "dica": "acao=estado acompanha; acao=parar interrompe", "demonstracao": demo}
    t0 = time.monotonic()
    r = rodar_comando(passos)
    r.update({"segundos": round(time.monotonic() - t0, 2), "demonstracao": demo})
    if a.get("ver_depois"):
        time.sleep(max(0, float(a.get("esperar_ms", 300))) / 1000)
        q = E.conexao().quadro()
        if q is not None:
            r["_imagem"] = imagem_json(q, a.get("largura", 640))
    return r


def cmd_habilidade(a):
    modo = a.get("modo", "listar")
    hs = habilidades()
    nome = a.get("nome")
    if modo == "listar":
        return {"habilidades": {k: {"descricao": v.get("descricao", ""),
                                    "duracao_s": controle.duracao(controle.normalizar(v["passos"], hs))}
                                for k, v in hs.items()}}
    if not nome:
        return {"erro": "informe nome"}
    if modo == "salvar":
        if not a.get("passos"):
            return {"erro": "informe passos"}
        controle.normalizar(a["passos"], hs)  # valida antes de salvar
        hs[nome] = {"passos": a["passos"], "descricao": a.get("descricao", ""),
                    "atualizada": time.strftime("%Y-%m-%d %H:%M")}
        _gravar(HAB, hs)
        return {"salva": nome, "duracao_s": controle.duracao(controle.normalizar(a["passos"], hs))}
    if modo == "apagar":
        existia = hs.pop(nome, None) is not None
        _gravar(HAB, hs)
        return {"apagada": existia}
    if modo == "ver":
        return {"habilidade": hs.get(nome)}
    if modo == "rodar":
        return cmd_comando(dict(a, passos=[{"habilidade": nome}]))
    return {"erro": "modo: listar | salvar | ver | apagar | rodar"}


# --------------------------------------------------------------------------- jogador
def _guardar_quadro(pasta):
    def g(rgb, nome):
        mime, dados = codificar(reduzir_imagem(rgb, 480))
        arq = os.path.join(pasta, "quadros", nome + (".jpg" if mime == "image/jpeg" else ".png"))
        with open(arq, "wb") as f:
            f.write(dados)
        fotos = sorted(os.listdir(os.path.join(pasta, "quadros")))
        for velho in fotos[:-400]:
            os.remove(os.path.join(pasta, "quadros", velho))
        return os.path.basename(arq)
    return g


def _laco_jogador(cfg):
    j, con = E.jogador, E.conexao()
    fim = time.time() + cfg["duracao"]
    intervalo = cfg["intervalo_ms"] / 1000
    guardar = _guardar_quadro(j.pasta)
    E.jog_info.update({"inicio": time.time(), "passos": 0, "recompensa": 0.0, "estado_txt": "jogando"})

    def agir(h):
        rodar_comando([{"habilidade": h}])
    try:
        while time.time() < fim and not E.jog_parar.is_set() and not _parar_global():
            if not con.conectado:
                E.jog_info["estado_txt"] = "sessão caiu"
                break
            r = j.passo(con.quadro, agir, explorar=cfg["explorar"], guardar_quadro=guardar)
            if "erro" in r:
                time.sleep(0.5)
                continue
            E.jog_info["passos"] += 1
            E.jog_info["recompensa"] = round(E.jog_info["recompensa"] + r["recompensa"], 4)
            E.jog_info["ultimo"] = {k: r[k] for k in ("estado", "habilidade", "recompensa")}
            if E.jog_info["passos"] % 20 == 0:
                j.salvar()
            time.sleep(intervalo)
        else:
            E.jog_info["estado_txt"] = "terminou"
    except Exception as e:  # noqa: BLE001
        E.jog_info["estado_txt"] = f"erro: {str(e)[:160]}"
    finally:
        j.salvar()
        if E.jog_info.get("estado_txt") == "jogando":
            E.jog_info["estado_txt"] = "parado"


def cmd_jogador(a):
    modo = a.get("modo", "estado")
    jog = _mod("jogador")
    jogo = a.get("jogo") or (E.jogador.jogo if E.jogador else _ler(CONF, {}).get("jogo"))
    if modo in ("iniciar", "preparar"):
        ocup = E.ocupado()
        if ocup:
            return {"erro": ocup}
        if not jogo:
            return {"erro": "informe jogo (nome livre: a memória fica separada por jogo)"}
        hs = habilidades()
        nomes = a.get("habilidades") or list(hs)
        faltam = [n for n in nomes if n not in hs]
        if faltam or not nomes:
            return {"erro": f"habilidades inexistentes: {faltam}" if faltam else
                    "salve habilidades antes (acao=habilidade modo=salvar)"}
        anteriores = (_ler(os.path.join(PASTA, "jogadores", jog._seguro(jogo), "memoria.json"), {})
                      .get("detectores") or [])
        det = a.get("detectores") if a.get("detectores") is not None else anteriores
        for d in det:
            jog.medir(__import__("numpy").zeros((90, 160, 3), dtype="uint8"), d)  # valida
        extra = {k: float(a[k]) for k in ("curiosidade", "alfa", "gama") if a.get(k) is not None}
        E.jogador = jog.Jogador(os.path.join(PASTA, "jogadores"), jogo, nomes, det,
                                limiar=float(a.get("limiar", 0.08)), estados_max=int(a.get("estados_max", 48)),
                                **extra)
        conf = _ler(CONF, {})
        conf["jogo"] = jogo
        _gravar(CONF, conf)
        if modo == "preparar":
            return {"preparado": jogo, "relatorio": E.jogador.relatorio()}
        if not E.conexao().conectado:
            return {"erro": "PS4 não conectado (acao=conectar)", "preparado": jogo}
        cfg = {"duracao": max(10, min(float(a.get("duracao", 600)), 4 * 3600)),
               "intervalo_ms": max(0, min(int(a.get("intervalo_ms", 100)), 10000)),
               "explorar": a.get("explorar", True) is not False}
        E.jog_parar.clear()
        E.jog_info = {"cfg": cfg, "jogo": jogo}
        E.jog_th = threading.Thread(target=_laco_jogador, args=(cfg,), name="ps4-jogador", daemon=True)
        E.jog_th.start()
        return {"jogando": jogo, "habilidades": nomes, "detectores": len(det), **cfg}
    if modo == "parar":
        E.jog_parar.set()
        if E.jog_th:
            E.jog_th.join(timeout=8)
        return {"parado": True, "info": E.jog_info}
    if not E.jogador:
        if not jogo:
            return {"erro": "nenhum jogador carregado (modo=preparar ou iniciar)"}
        E.jogador = jog.Jogador(os.path.join(PASTA, "jogadores"), jogo, list(habilidades()), None)
    j = E.jogador
    if modo == "estado":
        return {"rodando": bool(E.jog_th and E.jog_th.is_alive()), "info": E.jog_info,
                "passos_total": j.passos_total, "estados": len(j.estados.prot)}
    if modo == "relatorio":
        return j.relatorio()
    if modo == "nota":
        n = j.nota(float(a.get("valor", 1)), int(a.get("ultimos", 5)))
        j.salvar()
        return {"nota": float(a.get("valor", 1)), "jogadas_afetadas": n}
    if modo == "detectores":
        if a.get("detectores") is not None:
            for d in a["detectores"]:
                jog.medir(__import__("numpy").zeros((90, 160, 3), dtype="uint8"), d)
            j.detectores = list(a["detectores"])
            j.salvar()
        q = E.conexao().quadro() if E.con else None
        medidas = {}
        if q is not None:
            for i, d in enumerate(j.detectores):
                v = jog.medir(q, d)
                medidas[d.get("nome", str(i))] = round(float(v.mean() if hasattr(v, "mean") else v), 4)
        return {"detectores": j.detectores, "medidas_agora": medidas}
    if modo == "revisar":
        n = max(1, min(int(a.get("n", 4)), 8))
        regs = []
        try:
            with open(os.path.join(j.pasta, "gravacao.jsonl")) as f:
                regs = [json.loads(l) for l in f.readlines()[-3000:] if l.strip()]
        except OSError:
            pass
        com_quadro = [r for r in regs if r.get("quadro")]
        escolha = sorted(com_quadro, key=lambda r: -abs(r.get("recompensa", 0)))[:n]
        imgs = []
        for r in escolha:
            try:
                with open(os.path.join(j.pasta, "quadros", r["quadro"]), "rb") as f:
                    dados = f.read()
                imgs.append({"mime": "image/jpeg" if r["quadro"].endswith(".jpg") else "image/png",
                             "base64": base64.b64encode(dados).decode()})
            except OSError:
                continue
        return {"jogadas": escolha, "ultimas": regs[-15:], "relatorio": j.relatorio(), "_imagens": imgs}
    if modo == "esquecer":
        E.jogador = None
        arq = os.path.join(PASTA, "jogadores", jog._seguro(jogo), "memoria.json")
        if os.path.exists(arq):
            os.replace(arq, arq + f".{int(time.time())}.bak")
        return {"esquecido": jogo, "copia": True}
    return {"erro": "modo: preparar | iniciar | parar | estado | relatorio | revisar | nota | detectores | esquecer"}


# --------------------------------------------------------------------------- entrada
def executar(a):
    acao = a.get("acao", "estado")
    try:
        if acao == "diagnostico":
            faltam = _mod("conexao").disponivel()
            return {"pronto": not faltam, "faltam": faltam, "instalar": _mod("conexao").DEPENDENCIAS,
                    "config": _ler(CONF, {})}
        if acao == "botoes":
            return {"botoes": controle.BOTOES, "apelidos": controle.APELIDOS,
                    "analogicos": "esquerdo | direito (x,y de -1 a 1; y -1 = cima) ou angulo/forca"}
        if acao == "habilidade":
            return cmd_habilidade(a)
        if acao == "jogador":
            return cmd_jogador(a)
        con = E.conexao()
        if acao == "estado":
            t = E.tarefa_info if (E.tarefa and E.tarefa.is_alive()) or E.tarefa_info else None
            return {**con.estado(), "config": _ler(CONF, {}), "comando_longo": t,
                    "jogador": {"rodando": bool(E.jog_th and E.jog_th.is_alive()), **E.jog_info}}
        if acao == "conta":
            if a.get("url") or a.get("conta_id"):
                nome = con.adicionar_conta(a.get("url"), a.get("conta_id"), a.get("nome"))
                return {"conta": nome, "proximo": "abra no PS4 Ajustes > Ajustes da conexão do Remote Play > "
                                                  "Adicionar dispositivo e use acao=parear com o PIN"}
            return {"contas": con.contas(), "link_login": con.link_login(),
                    "como": "entre na conta PSN por esse link; a página final fica em branco: copie o endereço "
                            "dela e envie em acao=conta url=... (vale poucos minutos)"}
        if acao == "procurar":
            achados = con.procurar()
            if len(achados) == 1:
                conf = _ler(CONF, {})
                conf["ip"] = achados[0]["ip"]
                _gravar(CONF, conf)
            return {"consoles": achados}
        if acao == "parear":
            r = con.parear(_ip(a), a.get("pin"), a.get("usuario"))
            conf = _ler(CONF, {})
            conf.update({"ip": _ip(a), "usuario": r["conta"]})
            _gravar(CONF, conf)
            return {"pareado": True, **r}
        if acao == "ligar":
            return con.ligar(_ip(a), a.get("usuario") or _ler(CONF, {}).get("usuario"))
        if acao == "repouso":
            E.jog_parar.set()
            return con.repouso(a.get("ip") or _ler(CONF, {}).get("ip"), _ler(CONF, {}).get("usuario"))
        if acao == "conectar":
            return con.conectar(_ip(a), a.get("usuario") or _ler(CONF, {}).get("usuario"),
                                a.get("resolucao", "720p"), a.get("fps", "high"))
        if acao == "desconectar":
            E.jog_parar.set()
            E.parar_tarefa.set()
            return con.desconectar()
        if acao == "parar":
            E.parar_tarefa.set()
            E.jog_parar.set()
            return {"parando": True}
        if acao == "comando":
            return cmd_comando(a)
        if acao == "quadro":
            q = con.quadro()
            if q is None:
                return {"erro": "sem imagem (conectado? o vídeo leva alguns segundos para começar)"}
            return {"tamanho": [int(q.shape[1]), int(q.shape[0])],
                    "_imagem": imagem_json(q, a.get("largura", 640), a.get("recorte"))}
        return {"erro": "acao desconhecida"}
    except controle.ErroComando as e:
        return {"erro": str(e)}
    except Exception as e:  # noqa: BLE001
        return {"erro": f"{type(e).__name__}: {str(e)[:300]}"}


def main():
    try:
        a = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        a = {}
    precisa_sessao = a.get("acao") in ("conectar", "comando", "quadro", "jogador")
    if precisa_sessao and not globals().get("EM_PROCESSO"):
        print(json.dumps({"erro": "esta ação precisa rodar dentro do serviço (atualize o controle-ir)"},
                         ensure_ascii=False))
        return
    print(json.dumps(executar(a), ensure_ascii=False))


if __name__ == "__main__":
    main()
