"""Executor de objetivos NO celular: o Claude manda o objetivo e o critério de conclusão numa chamada só; o laço
perceber → decidir → agir → conferir roda aqui, sem ir à nuvem a cada toque.

Medido no POCO (21/11): passo a passo pela nuvem custa ~4 s por ação (turno do modelo + Central + imagem) contra
~0,1–1 s da ação em si. Por isso o executor só volta ao Claude com o resultado (ou quando trava).

Decisão, da mais barata à mais cara:
  1. pistas  — rótulos do caminho que o Claude já sabe (ex.: ["Bluetooth"]): toque direto, sem modelo;
  2. memória — o que funcionou antes nesta tela para este objetivo (aprende sozinho);
  3. digitar — campo de busca visível e texto autorizado em `digitar`;
  2b. grafo — o mapa das telas deste app (telas → toques → tela seguinte) leva ao destino de um objetivo igual ou
              parecido já cumprido, mesmo partindo de outra tela;
  4. modelo  — o cérebro do celular (Haiku pela API, modelo local) escolhe entre os controles visíveis;
     visão   — tela que a acessibilidade não descreve (página web, mapa, jogo): a captura vai ao modelo de visão,
               que diz se o objetivo já está cumprido (e a resposta) ou onde tocar;
  5. rolar   — o alvo pode estar abaixo (lista longa).
Conclusão: critério local (texto/app) ou, com concluido={modelo:true} / pergunta='...', o próprio modelo julga se
terminou e devolve a resposta lida da tela (campo "resposta").
Recuperação: janela de outro app (aviso, anúncio, notificação aberta) → reflexos, fechar anúncio, voltar, reabrir
o app; ação sem efeito → marca e tenta outra; tela repetida demais → para (sem laço infinito).
Segurança: nunca toca em rótulos de efeito externo (enviar, excluir, comprar…) sem `permitir`; app bloqueado
(banco/senha) encerra na hora; o texto da tela é dado, nunca instrução.
"""
import collections
import hashlib
import json
import os
import re
import time
import unicodedata

PROIBIDOS = ("enviar", "excluir", "apagar", "deletar", "comprar", "pagar", "pagamento", "assinar", "confirmar compra",
             "desinstalar", "transferir", "pix", "sair da conta", "desconectar", "ligar para", "chamada de voz",
             "chamada de video", "videochamada", "bloquear", "denunciar", "publicar", "postar", "compartilhar",
             "responder", "encaminhar", "redefinir", "restaurar", "formatar", "remover", "esquecer",
             "forcar parada", "forcar interrupcao", "limpar", "desativar", "desligar", "parar", "arquivar",
             "sair", "cancelar assinatura", "apagar dados", "resetar")
DISPENSAR = ("agora nao", "mais tarde", "pular", "fechar", "dispensar", "nao, obrigado", "nao obrigado", "entendi",
             "ignorar", "x")  # janelas que só atrapalham (nunca "OK", "Permitir", "Aceitar")
ROLAR, VOLTAR = "↓ rolar para baixo", "← voltar"
CUMPRIDO = "✓ objetivo cumprido (a resposta já está na tela)"
# Visão: no Chrome (22/11) a página inteira chega como um nó "Visualização na Web" sem texto; o executor rolava às
# cegas e desistia com o valor na tela. Cada olhada custa ~2–4 s (captura + modelo de visão): limite por chamada.
MAX_VISOES, LARGURA_VISAO = 8, 720
WEB = re.compile(r"webview|visualizacao na web|web view", re.I)
# O cliente do Claude desiste de uma chamada aos 60 s (medido em 21/11: o objetivo terminou no celular em 72 s e o
# resultado se perdeu). Acima disso, devolve "parado: prazo" e uma nova chamada continua da tela atual.
MAX_PASSOS, MAX_PRAZO, MAX_ROLAGENS = 25, 50, 30
# Escada de cérebros (chamados direto do celular, sem passar pela nuvem do Claude): modelos disparados juntos, vale
# o mais forte que responder no prazo. Sobe um degrau sozinho quando a tela já falhou ou se repetiu.
NIVEIS = {"rapido": (["claude-haiku-5-5"], False, 6),
          "padrao": (["claude-haiku-5-5", "claude-sonnet-5-5"], False, 10),
          "forte": (["claude-sonnet-5-5", "claude-opus-5-5"], False, 20),
          "maximo": (["claude-opus-5-5"], True, 40)}
ORDEM_NIVEIS = list(NIVEIS)


def norm(t):
    t = unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t).strip()


def rotulo(e):
    return (e.get("texto") or e.get("desc") or "").strip()


def proibido(texto, permitir=()):
    n = norm(texto)
    if any(norm(p) and norm(p) in n for p in permitir):
        return False
    return any(re.search(rf"(^|\W){re.escape(p)}(\W|$)", n) for p in PROIBIDOS)


def assinatura(els, app):
    """Identidade da tela: rótulos e ids do app (posição não entra: rolar 1 px não é tela nova)."""
    chaves = sorted({f"{e.get('id')}|{rotulo(e)}" for e in els if e.get("pacote") == app or not app})
    return hashlib.sha256(json.dumps(chaves, ensure_ascii=False).encode()).hexdigest()[:16]


def concluido(crit, els, app_atual, app=None, excluir=()):
    """Critério verificável localmente: texto(s) visível(is) e/ou app em primeiro plano. Com `app` (a tarefa é
    nele), só vale dentro dele: a barra "Pesquisar" da tela inicial não conclui uma tarefa na Play Store (21/11).
    `excluir`: textos digitados — o campo e as sugestões da busca (que COMEÇAM com o texto digitado) não valem:
    "cotação do dólar hoje em real" concluía {qualquer:["Real"]} antes de a página de resultado abrir (22/11)."""
    if not crit:
        return False
    if crit.get("app") and app_atual != crit["app"]:
        return False
    apps = {app} if isinstance(app, str) else set(app or ())
    if apps and app_atual not in apps:
        return False
    fora = [norm(x) for x in excluir if norm(x)]
    textos = [norm(rotulo(e)) for e in els if (not apps or e.get("pacote") in apps | {""})
              and not (fora and (e.get("editavel") or any(norm(rotulo(e)).startswith(f) for f in fora)))]
    if crit.get("texto") and not any(norm(crit["texto"]) in t for t in textos):
        return False
    if crit.get("qualquer") and not any(norm(q) in t for q in crit["qualquer"] for t in textos):
        return False
    if crit.get("todos") and not all(any(norm(q) in t for t in textos) for q in crit["todos"]):
        return False
    return bool(crit.get("app") or crit.get("texto") or crit.get("qualquer") or crit.get("todos"))


def validar(a):
    obj = a.get("objetivo") or a.get("texto")
    if not isinstance(obj, str) or not obj.strip():
        return "informe objetivo (o que alcançar)"
    crit = a.get("concluido")
    if crit is not None and (not isinstance(crit, dict) or not any(
            crit.get(k) for k in ("texto", "qualquer", "todos", "app", "modelo", "pergunta"))):
        return ("informe concluido: {texto} | {qualquer:[...]} | {todos:[...]} | {app} | {modelo:true} (como saber "
                "que terminou; sem concluido, o modelo do celular julga)")
    perg = a.get("pergunta")
    if perg is not None and (not isinstance(perg, str) or not perg.strip() or len(perg) > 300):
        return "pergunta deve ser um texto curto (o que ler na tela final)"
    for k in ("pistas", "permitir"):
        v = a.get(k)
        if v is not None and (not isinstance(v, list) or not all(isinstance(x, str) for x in v) or len(v) > 30):
            return f"{k} deve ser uma lista de textos"
    if a.get("app") is not None and not re.match(r"^[A-Za-z][\w.]{2,120}$", str(a["app"])):
        return "app deve ser o nome do pacote"
    return None


def palavras(t):
    return set(re.findall(r"\w{3,}", norm(t))) - IGNORADAS


def titulo(els, app=None):
    return " / ".join(textos_da_tela(els, app, 2))[:60]


class Grafo:
    """Mapa das telas de cada app: nó = assinatura da tela, aresta = rótulo tocado (ou rolar) → tela seguinte, com
    quantas vezes deu certo. Guarda também o destino de cada objetivo cumprido. Um objetivo IGUAL ou PARECIDO
    ("ver o Bluetooth" ≈ "abrir o Bluetooth") acha o caminho por busca em largura a partir da tela atual, mesmo
    que o caminho tenha sido aprendido em pedaços, por objetivos diferentes."""
    MAX_TELAS, MAX_OBJETIVOS, PARECIDO = 400, 300, 0.6

    def __init__(self, arq):
        self.arq = arq
        self.d = self._ler()

    def _ler(self):
        try:
            with open(self.arq) as f:
                d = json.load(f)
            if isinstance(d, dict) and isinstance(d.get("telas"), dict) and isinstance(d.get("objetivos"), dict):
                return d
        except (OSError, ValueError, TypeError):
            pass
        return {"telas": {}, "objetivos": {}}

    def _gravar(self):
        try:
            os.makedirs(os.path.dirname(self.arq) or ".", exist_ok=True)
            tmp = self.arq + ".tmp"
            with open(tmp, "w") as f:
                json.dump(self.d, f, ensure_ascii=False)
            os.replace(tmp, self.arq)
        except OSError:
            pass

    def registrar(self, app, trilha, destino, objetivo, titulo_destino=""):
        """trilha: [(tela, rótulo, tela_seguinte)] do caminho que deu certo (sem desvios)."""
        agora = int(time.time())
        telas = self.d["telas"].setdefault(app or "", {})
        for s_, r, d in trilha:
            if not (s_ and r and d) or s_ == d:
                continue
            no = telas.setdefault(s_, {"arestas": {}})
            no["v"] = agora
            ar = no["arestas"].setdefault(r, {"para": d, "ok": 0})
            ar.update(para=d, ok=ar.get("ok", 0) + 1, v=agora)
        if destino:
            fim = telas.setdefault(destino, {"arestas": {}})
            fim.update(v=agora, **({"titulo": titulo_destino} if titulo_destino else {}))
            o = self.d["objetivos"].setdefault(norm(objetivo), {"ok": 0})
            o.update(app=app or "", destino=destino, v=agora, ok=o.get("ok", 0) + 1)
        if len(telas) > self.MAX_TELAS:  # esquece as telas vistas há mais tempo
            for k in sorted(telas, key=lambda k: telas[k].get("v", 0))[:len(telas) - self.MAX_TELAS]:
                del telas[k]
        obj = self.d["objetivos"]
        if len(obj) > self.MAX_OBJETIVOS:
            for k in sorted(obj, key=lambda k: obj[k].get("v", 0))[:len(obj) - self.MAX_OBJETIVOS]:
                del obj[k]
        self._gravar()

    def destinos(self, app, objetivo):
        """Destinos de objetivos iguais ou parecidos (palavras em comum ≥ 60%) no mesmo app, do mais parecido."""
        alvo, exato, cands = palavras(objetivo), norm(objetivo), []
        for k, o in self.d["objetivos"].items():
            if o.get("app", "") != (app or "") or not o.get("destino"):
                continue
            p = palavras(k)
            sim = 2.0 if k == exato else (len(alvo & p) / len(alvo | p) if alvo and p else 0)
            if sim >= self.PARECIDO:
                cands.append((sim, o.get("ok", 0), o["destino"]))
        return [d for *_, d in sorted(cands, reverse=True)]

    def proximo(self, app, tela, destinos):
        """1º rótulo do caminho mais curto da tela atual até um dos destinos (None se não houver caminho)."""
        telas = self.d["telas"].get(app or "", {})
        for dest in destinos:
            if tela == dest:
                return None
            vistos, fila = {tela}, collections.deque([(tela, None)])
            while fila:
                s_, primeiro = fila.popleft()
                arestas = telas.get(s_, {}).get("arestas", {})
                for r, ar in sorted(arestas.items(), key=lambda kv: -kv[1].get("ok", 0)):
                    d = ar.get("para")
                    if not d or d in vistos:
                        continue
                    if d == dest:
                        return primeiro or r
                    vistos.add(d)
                    fila.append((d, primeiro or r))
        return None

    def resumo(self, n=20):
        obj = sorted(self.d["objetivos"].items(), key=lambda kv: -kv[1].get("v", 0))[:n]
        return {"apps": {a or "(qualquer)": len(t) for a, t in self.d["telas"].items()},
                "arestas": sum(len(no.get("arestas", {})) for t in self.d["telas"].values() for no in t.values()),
                "objetivos": [{"objetivo": k, "app": o.get("app"), "vezes": o.get("ok", 0)} for k, o in obj]}


def area_cega(els, regioes=(), so_regioes=False):
    """Região [x, y, l, a] que a acessibilidade não descreve: página web (o Chrome mostra só o nó "Visualização na
    Web", 22/11), mapa, vídeo, jogo. Só a imagem mostra o conteúdo dali. None se a tela é toda descrita.
    so_regioes: o celular já calculou as regiões pela ÁRVORE da tela (principal.regioes_web), que é a fonte certa;
    sem ela (testes), vale o heurístico pela posição dos elementos."""
    if so_regioes:
        return list(regioes[0]) if regioes else None
    if not els:
        return list(regioes[0]) if regioes else None
    larg = max(e.get("x", 0) + e.get("l", 0) // 2 for e in els) or 1
    alt = max(e.get("y", 0) + e.get("a", 0) // 2 for e in els) or 1
    for e in els:
        if not (WEB.search(str(e.get("classe", ""))) or WEB.search(norm(e.get("desc")))):
            continue
        l, a_ = e.get("l", 0), e.get("a", 0)
        if l * a_ < 0.15 * larg * alt:
            continue
        x0, y0 = e.get("x", 0) - l // 2, e.get("y", 0) - a_ // 2
        if textos_na_area(els, e, [x0, y0, l, a_]) < 3:
            # o Chrome às vezes expõe a página; com texto DELE dentro, a acessibilidade já descreve
            return [x0, y0, l, a_]
    return list(regioes[0]) if regioes else None


def textos_na_area(els, e, r):
    """Elementos com texto do MESMO app dentro da área: o teclado aberto por cima (outro pacote) tem uma descrição
    por tecla e fazia a página parecer descrita — o executor ficava sem a visão logo depois de digitar (23/11)."""
    return sum(1 for o in els if o is not e and rotulo(o) and o.get("pacote") == e.get("pacote")
               and not o.get("id") and no_retangulo(o.get("x", 0), o.get("y", 0), r))  # com id: botão nativo
               # do app (a barra do Chrome por cima da página), não conteúdo da página


def no_retangulo(x, y, r, folga=0):
    return r[0] - folga <= x <= r[0] + r[2] + folga and r[1] - folga <= y <= r[1] + r[3] + folga


class Executor:
    """`t` é o módulo da tela (ou uma imitação nos testes): foco, dump_ui, elementos, injetar, calma, abrir,
    bloqueado, aplicar_regras, em_anuncio, fechar_anuncio (opcionais: regioes(xml), capturar(largura, recorte) →
    (base64, fator real/imagem), recolher). `decidir(objetivo, resumo, opcoes, nivel)` → índice ou None.
    `olhar(objetivo, pergunta, contexto, b64, opcoes, nivel)` → {feito, resposta, acao: tocar|opcao|rolar|voltar,
    x, y, opcao, rotulo, fonte} (visão). `julgar(objetivo, pergunta, textos, b64|None, nivel)` → {feito, resposta}."""

    def __init__(self, t, decidir=None, memoria_arq=None, relogio=time.monotonic, olhar=None, julgar=None,
                 grafo_arq=None):
        self.t, self.decidir, self.relogio = t, decidir, relogio
        self.memoria_arq = memoria_arq
        self.olhar, self.julgar = olhar, julgar
        self.grafo = Grafo(grafo_arq) if grafo_arq else None

    # ----------------------------------------------------------- memória de caminhos que funcionaram
    def _memoria(self):
        try:
            with open(self.memoria_arq) as f:
                m = json.load(f)
            return m if isinstance(m, dict) else {}
        except (OSError, ValueError, TypeError):
            return {}

    def _lembrar(self, chave, novos):
        if not self.memoria_arq or not novos:
            return
        m = self._memoria()
        m[chave] = {**m.get(chave, {}), **novos}
        if len(m) > 200:  # guarda as 200 mais recentes
            m = dict(list(m.items())[-200:])
        try:
            os.makedirs(os.path.dirname(self.memoria_arq), exist_ok=True)
            tmp = self.memoria_arq + ".tmp"
            with open(tmp, "w") as f:
                json.dump(m, f, ensure_ascii=False)
            os.replace(tmp, self.memoria_arq)
        except OSError:
            pass

    def _esperar_app(self, app, segundos):
        fim = self.relogio() + segundos
        while self.relogio() < fim:
            f = self.t.foco()
            if f == app:
                return True
            if sistema(f):  # cortina/painel por cima: esperar não adianta, a recuperação recolhe
                return False
            self.t.calma(100, 300)
        return False

    # ----------------------------------------------------------- o laço
    def executar(self, a):
        erro = validar(a)
        if erro:
            return {"erro": erro}
        t = self.t
        objetivo = a.get("objetivo") or a.get("texto")
        app, crit = a.get("app"), a.get("concluido") or {"modelo": True}
        pergunta = (a.get("pergunta") or crit.get("pergunta") or "").strip() or None
        pistas = list(a.get("pistas") or [])
        permitir = list(a.get("permitir") or [])
        # digitar: "texto" ou {"texto", "depois_de": "pista"} (só depois de usar essa pista: nas Configurações há
        # busca na tela inicial E na lista de apps — a certa é a segunda)
        dg = a.get("digitar")
        digitar = dg if isinstance(dg, str) else (dg.get("texto") if isinstance(dg, dict) else None)
        digitar_depois = dg.get("depois_de") if isinstance(dg, dict) else None
        max_passos = max(1, min(int(a.get("max_passos", 12)), MAX_PASSOS))
        # padrão "forte": no POCO (21/11) Haiku decidiu em 1,46 s, Sonnet 1,55 s, Opus 1,68 s, Opus pensando 1,89 s
        # (todos acertaram): o mais inteligente custa ~0,2 s por decisão — vale sempre
        nivel_base = ORDEM_NIVEIS.index(a.get("cerebro")) if a.get("cerebro") in NIVEIS else 2
        prazo = self.relogio() + max(5, min(float(a.get("prazo", 45)), MAX_PRAZO))
        usar_modelo = a.get("modelo", True) is not False and self.decidir is not None
        usar_visao = (a.get("visao", True) is not False and a.get("modelo", True) is not False
                      and self.olhar is not None and hasattr(t, "capturar"))
        # o modelo julga o fim: sem critério local, ou pedido explícito (modelo/pergunta)
        julga = bool(crit.get("modelo") or crit.get("pergunta") or pergunta
                     or not any(crit.get(k) for k in ("texto", "qualquer", "todos", "app")))
        inicio = self.relogio()
        passos, vistos, falhas, novos = [], {}, {}, {}
        recuperacoes, consultas, digitado, usadas = 0, 0, set(), set()
        chave_mem = f"{app or ''}|{norm(objetivo)}"
        memoria = self._memoria().get(chave_mem, {})
        app_grafo = app or ""
        destinos = self.grafo.destinos(app_grafo, objetivo) if self.grafo else []
        resposta, conclusao, extraido, visoes = [None], ["criterio"], [False], [0]
        diag = {}  # visão: o que aconteceu (área cega vista, captura que falhou, erro do modelo) — vai no resultado
        xml_atual, nivel_atual = [""], [ORDEM_NIVEIS[nivel_base]]

        caminho = []  # [(tela, rótulo, tela seguinte)] do caminho que deu certo; desvios são cortados
        # apps da tarefa: o pedido + os que um toque NOSSO abriu (no HyperOS, Configurações → Apps abre a Central de
        # Segurança, outro pacote: o executor reabria as Configurações e desfazia o caminho — 21/11)
        apps_ok = {app} if app else set()
        ultimo_toque, passos_sig = [0.0], [None]

        def fim(estado, motivo=None, els=None, app_atual=None):
            if estado == "concluido":
                self._lembrar(chave_mem, {s_: r_ for s_, r_, _ in caminho})
                if self.grafo and els is not None:
                    self.grafo.registrar(app_grafo, caminho, assinar(els, app_atual, xml_atual[0]), objetivo,
                                         titulo(els, app_atual))
                if pergunta and not extraido[0] and els is not None and self.julgar is not None:
                    ler_resposta(els, app_atual)
            if estado == "parado" and motivo == "prazo esgotado":
                motivo = "prazo esgotado (chame de novo para continuar desta tela)"
            r = {"estado": estado, **({"motivo": motivo} if motivo else {}), "passos": passos,
                 "consultas_modelo": consultas, "recuperacoes": recuperacoes,
                 "ms": round((self.relogio() - inicio) * 1000)}
            if estado == "concluido":
                r["conclusao"] = conclusao[0]
                if resposta[0] is not None:
                    r["resposta"] = resposta[0]
            if visoes[0]:
                r["visoes"] = visoes[0]
            if diag:
                r["visao_diag"] = diag
            if a.get("ler", True) and els is not None:
                if (app and app_atual not in apps_ok) or sistema(app_atual):
                    # outra janela na frente (notificações, outro app): o conteúdo dela não sai do celular
                    r["tela"] = {"app": app_atual, "textos": [], "nota": "outra janela por cima: conteúdo não enviado"}
                else:
                    r["tela"] = {"app": app_atual, "textos": textos_da_tela(els, app_atual, int(a.get("ler_max", 60)))}
            return r

        def regioes(xml_):
            try:
                return t.regioes(xml_) if hasattr(t, "regioes") and xml_ else ()
            except Exception:  # noqa: BLE001 — sem regiões, só o heurístico do WebView
                return ()

        def cega_de(els_, xml_):
            if not (usar_visao or self.julgar):
                return None
            return area_cega(els_, regioes(xml_), so_regioes=hasattr(t, "regioes"))

        def assinar(els_, app_, xml_):
            """Assinatura da tela; numa área cega (página web), soma um resumo da IMAGEM dela: rolar a página ou
            abrir um link não muda a acessibilidade, e sem isso o executor achava que nada tinha mudado."""
            s_ = assinatura(els_, app_)
            cg = cega_de(els_, xml_) if usar_visao else None
            if cg:
                try:
                    b, _ = t.capturar(96, cg)
                except Exception:  # noqa: BLE001
                    b = None
                if b:
                    s_ += ":" + hashlib.sha256(b.encode()).hexdigest()[:8]
            return s_

        def ler_resposta(els_, app_):
            """A tela final responde à pergunta: o modelo lê (texto; imagem se a área é cega)."""
            extraido[0] = True
            b64 = None
            cg = cega_de(els_, xml_atual[0])
            if cg and hasattr(t, "capturar"):
                try:
                    b64, _ = t.capturar(LARGURA_VISAO)
                except Exception:  # noqa: BLE001
                    b64 = None
            try:
                j = self.julgar(objetivo, pergunta, textos_da_tela(els_, app_, 80), b64, nivel_atual[0]) or {}
            except Exception:  # noqa: BLE001 — sem leitura, o resultado ainda traz os textos da tela
                j = {}
            if j.get("resposta") not in (None, ""):
                resposta[0] = str(j["resposta"])[:500]
            return j

        feitas = set()  # (tela, ação) que já mudou a tela: se voltamos aqui, ela não leva ao objetivo

        def falhou(sig_, r):  # 1 falha = transitória (tenta de novo); 2 = desiste dessa ação nesta tela
            return falhas.get((sig_, r), 0) >= 2 or (sig_, r) in feitas

        def anotar(acao, alvo, via, t0):
            passos.append({"n": len(passos) + 1, "acao": acao, **({"alvo": alvo} if alvo else {}), "via": via,
                           "ms": round((self.relogio() - t0) * 1000)})

        if app and t.foco() != app:
            t0 = self.relogio()
            if t.bloqueado(app):
                return {"erro": "app bloqueado (banco, pagamento ou senha)"}
            if not t.abrir(app):
                return fim("parado", f"não consegui abrir {app}")
            self._esperar_app(app, 8)  # carregamento lento: espera o app vir para a frente antes de "corrigir"
            t.calma(150, 3000)
            anotar("abrir", app, "inicio", t0)

        els, app_atual = [], None
        while True:
            if self.relogio() > prazo:
                return fim("parado", "prazo esgotado", els, app_atual)
            app_atual = t.foco()
            if t.bloqueado(app_atual):
                return fim("parado", "app bloqueado em primeiro plano (banco, pagamento ou senha)")
            xml_atual[0] = t.dump_ui()
            els = t.elementos(xml_atual[0], 300)
            if concluido(crit, els, app_atual, apps_ok, [digitar] if digitar and digitado else ()):
                return fim("concluido", None, els, app_atual)
            rolagens = sum(p["via"] == "rolagem contínua" for p in passos)
            if len(passos) - rolagens >= max_passos or rolagens >= MAX_ROLAGENS:
                return fim("parado", "limite de passos", els, app_atual)

            # app que abriu logo depois de um toque nosso, mais devagar que a conferência (Central de Segurança, 21/11):
            # é resultado do toque, não intruso
            if (app and app_atual not in apps_ok and app_atual and not sistema(app_atual) and passos
                    and passos[-1]["acao"] == "tocar" and self.relogio() - ultimo_toque[0] < 4):
                apps_ok.add(app_atual)
                if passos[-1]["via"].endswith(" (sem efeito)"):
                    passos[-1]["via"] = passos[-1]["via"][:-len(" (sem efeito)")] + " (abriu devagar)"
                    falhas.pop((passos_sig[0], passos[-1].get("alvo")), None)
            # ---- recuperação: outro app na frente (aviso, anúncio, painel de notificações, app errado)
            if app and app_atual not in apps_ok:
                t0 = self.relogio()
                recuperacoes += 1
                if recuperacoes > 4:
                    return fim("parado", f"não consegui voltar para {app} (está em {app_atual})", els, app_atual)
                regra = None if sistema(app_atual) else t.aplicar_regras(app_atual, els)
                if sistema(app_atual) and recuperacoes <= 2 and hasattr(t, "recolher"):
                    t.recolher()  # cortina/painel do sistema: no HyperOS o "voltar" injetado não fecha (21/11)
                    t.calma(150, 1500)
                    anotar("recolher_paineis", app_atual, "recuperacao", t0)
                elif regra:
                    anotar("reflexo", regra, "recuperacao", t0)
                elif t.em_anuncio():
                    t.fechar_anuncio(app_atual)
                    anotar("fechar_anuncio", app_atual, "recuperacao", t0)
                elif sistema(app_atual) or recuperacoes > 2:
                    t.injetar("tecla 4")  # janela do sistema que não recolhe: voltar, sem tocar em nada dela
                    t.calma(150, 1500)
                    anotar("voltar", app_atual, "recuperacao", t0)
                else:
                    # outro app comum na frente: traz o app da tarefa de volta (voltar mexeria no outro app)
                    t.abrir(app)
                    self._esperar_app(app, 6)
                    t.calma(150, 3000)
                    anotar("reabrir", app, "recuperacao", t0)
                continue

            cega = cega_de(els, xml_atual[0])
            if cega:
                diag["telas_cegas"] = diag.get("telas_cegas", 0) + 1
                diag["area"] = cega
            else:
                web_ = [e for e in els if WEB.search(str(e.get("classe", ""))) or WEB.search(norm(e.get("desc")))]
                if web_:
                    w = web_[0]
                    r_ = [w.get("x", 0) - w.get("l", 0) // 2, w.get("y", 0) - w.get("a", 0) // 2, w.get("l", 0),
                          w.get("a", 0)]
                    diag["web_descrita"] = {"area": r_, "textos_do_app": textos_na_area(els, w, r_),
                                            "outros_apps": sorted({o.get("pacote") for o in els if o.get("pacote")
                                                                   != w.get("pacote")})[:4]}
            sig = assinar(els, app_atual, xml_atual[0])
            for k, (s_, _, _) in enumerate(caminho):
                if s_ == sig:  # voltamos a uma tela do caminho: o trecho depois dela foi desvio
                    del caminho[k:]
                    break
            vistos[sig] = vistos.get(sig, 0) + 1
            if vistos[sig] > 4:
                return fim("parado", "sem progresso (a mesma tela voltou várias vezes)", els, app_atual)

            alvos = [e for e in els if rotulo(e) and not e.get("desativado")
                     and (not app or e.get("pacote") in apps_ok)]
            t0 = self.relogio()
            escolha, via, escolhida_pista = None, None, None

            # 0. janela que só atrapalha (diálogo pequeno com "Agora não"/"Pular"…) — nunca OK/Permitir/Aceitar
            if len(alvos) <= 8 and not any(norm(p) in norm(rotulo(e)) for p in pistas for e in alvos):
                d = next((e for e in alvos if e.get("clicavel") and norm(rotulo(e)) in DISPENSAR
                          and not falhou(sig, rotulo(e)) and not interruptor(e, els)), None)
                if d:
                    escolha, via = d, "dispensar"
            # 1. pistas do Claude, na ordem — cada uma vale UMA vez: a tela seguinte costuma repetir o rótulo no
            # título ou num interruptor ("Opções do desenvolvedor" → interruptor geral: desligou o modo de
            # desenvolvedor e derrubou o Shizuku no teste de 21/11)
            if not escolha:
                for p in pistas:
                    if p in usadas:
                        continue
                    e = melhor(alvos, p, estrito=True)  # "Apps" ≠ "Atualização de apps do sistema" (21/11)
                    if e and not falhou(sig, rotulo(e)) and seguro(e, els, permitir):
                        escolha, via = e, "pista"
                        escolhida_pista = p
                        break
            # 2. memória deste objetivo nesta tela
            if not escolha and memoria.get(sig):
                e = melhor(alvos, memoria[sig])
                if e and not falhou(sig, rotulo(e)) and seguro(e, els, permitir):
                    escolha, via = e, "memoria"
            # 2b. grafo: caminho até o destino de um objetivo igual/parecido já cumprido (partindo desta tela)
            if not escolha and destinos:
                r_ = self.grafo.proximo(app_grafo, sig, destinos)
                if r_ == ROLAR:
                    if not falhou(sig, ROLAR) and (cega or any(e.get("rolavel") for e in els)):
                        escolha, via = ROLAR, "grafo"
                elif r_:
                    e = melhor(alvos, r_)
                    if e and not falhou(sig, rotulo(e)) and seguro(e, els, permitir):
                        escolha, via = e, "grafo"
            # 3. campo para digitar o texto autorizado (uma vez por tela)
            ja_escrito = any(e.get("editavel") and norm(digitar or "") in norm(e.get("texto")) for e in els)
            if (not escolha and digitar and not digitado and not ja_escrito
                    and (not digitar_depois or digitar_depois in usadas)):
                # uma vez por objetivo: cada letra muda a tela e a "tela nova" fazia digitar de novo (8× no POCO)
                campo = next((e for e in els if e.get("editavel") and not e.get("desativado")), None)
                atalho = None if campo else next((e for e in alvos if busca(e) and tocavel(e, els)
                                                  and not proibido(rotulo(e), permitir)), None)
                if atalho:  # "Pesquisar apps" da Central de Segurança é um botão que abre o campo (21/11)
                    t.injetar(f"tocar {atalho['x']} {atalho['y']}")
                    t.calma(150, 1500)
                    novos_els = t.elementos(t.dump_ui(), 300)
                    campo = next((e for e in novos_els if e.get("editavel") and not e.get("desativado")), None)
                    if campo:
                        anotar("abrir_busca", rotulo(atalho), "digitar", t0)
                        t0 = self.relogio()
                if campo:
                    digitado.add(sig)
                    t.injetar(f"tocar {campo['x']} {campo['y']}")
                    t.calma(100, 800)
                    t.injetar("texto " + digitar.encode().hex())
                    t.injetar("tecla 66")  # enter: busca
                    t.calma(150, 2500)
                    anotar("digitar", f"{len(digitar)} caracteres", "digitar", t0)
                    continue
            # 3b. pista ainda não usada e fora da tela: rolar procurando ANTES de o modelo adivinhar (no WhatsApp o
            # modelo abriu outra conversa enquanto a pista "Você" estava logo abaixo — 21/11)
            if (not escolha and any(p not in usadas for p in pistas) and not falhou(sig, ROLAR)
                    and any(e.get("rolavel") for e in els)):
                escolha, via = ROLAR, "procurando pista"
            # 3c. o modelo mandou rolar esta lista e nada visível lembra o objetivo: continua rolando sem perguntar
            # de novo (no teste dos Apps, 7 consultas seguidas de ~1,5 s só para dizer "rolar" — 21/11)
            if (not escolha and not cega and passos and passos[-1]["acao"] == "rolar"
                    and passos[-1]["via"].startswith(("modelo", "rolagem contínua"))
                    and not falhou(sig, ROLAR) and any(e.get("rolavel") for e in els)
                    and not any(ranquear([rotulo(e)], objetivo, 0, pontos=True) for e in alvos if rotulo(e))):
                escolha, via = ROLAR, "rolagem contínua"
            # 4. o cérebro do celular escolhe entre os controles visíveis; numa área cega (página web, mapa, jogo)
            # quem decide é a visão, olhando a captura — o texto sozinho não mostra o conteúdo dali
            if not escolha and (usar_modelo or (usar_visao and cega)):
                opcoes = []
                for e in alvos:
                    r = rotulo(e)
                    if cega and WEB.search(norm(r)):
                        continue  # o nó "Visualização na Web" não é um destino
                    # tocável: o próprio elemento ou a linha clicável que o contém (nas Configurações o título
                    # "Sobre o telefone" não é clicável, a linha sem texto é — 21/11, o modelo só via rolar/voltar)
                    if (r and r not in opcoes and tocavel(e, els) and not falhou(sig, r)
                            and seguro(e, els, permitir) and (digitar or not busca(e))):
                        opcoes.append(r)
                opcoes = ranquear(opcoes, objetivo, 7)  # o cérebro responde 1 dígito: até 7 + rolar + voltar
                extras = [x for x in (ROLAR, VOLTAR) if not falhou(sig, x)]
                if julga and not falhou(sig, CUMPRIDO):
                    extras = [CUMPRIDO] + extras  # o modelo também diz quando o objetivo já está na tela
                dificil = any(k[0] == sig for k in falhas) or vistos[sig] >= 2 or recuperacoes > 1
                nivel = ORDEM_NIVEIS[min(len(ORDEM_NIVEIS) - 1, nivel_base + (1 if dificil else 0))]
                nivel_atual[0] = nivel
                contexto = ("Tela atual (" + str(app_atual) + "): " + " | ".join(textos_da_tela(alvos, None, 80))
                            )[:1800]
                if passos:
                    contexto += "\nJá feito: " + "; ".join(
                        f"{p['acao']} {p.get('alvo', '')} ({p['via']})" for p in passos[-6:])
                visto = False
                if usar_visao and cega and visoes[0] < MAX_VISOES:
                    try:
                        b64, fator = t.capturar(LARGURA_VISAO)
                    except Exception as erro_c:  # noqa: BLE001 — sem captura, decide pelo texto
                        b64, fator = None, 1.0
                        diag["erro_captura"] = str(erro_c)[:120]
                    if not b64:
                        diag["capturas_falhas"] = diag.get("capturas_falhas", 0) + 1
                    if b64:
                        visto = True
                        visoes[0] += 1
                        consultas += 1
                        t_dec = self.relogio()
                        try:
                            res = self.olhar(objetivo, pergunta, contexto, b64, opcoes, nivel) or {}
                        except Exception as erro_v:  # noqa: BLE001
                            res = {"fonte": "erro"}
                            diag["erro_visao"] = str(erro_v)[:160]
                        if not (res.get("feito") or res.get("acao")):
                            diag["visao_sem_acao"] = {k: res[k] for k in list(res)[:4]}
                        via_v = f"visao:{res.get('fonte') or '?'} ({nivel}, {round((self.relogio() - t_dec) * 1000)} ms)"
                        if res.get("feito"):
                            if res.get("resposta") not in (None, ""):
                                resposta[0] = str(res["resposta"])[:500]
                                extraido[0] = True
                            conclusao[0] = "visao"
                            anotar("concluir", None, via_v, t0)
                            return fim("concluido", None, els, app_atual)
                        ac = res.get("acao")
                        if ac == "opcao":
                            k_ = inteiro(res.get("opcao"))
                            if k_ is not None and 1 <= k_ <= len(opcoes):
                                e = melhor(alvos, opcoes[k_ - 1])
                                if e is not None and seguro(e, els, permitir):
                                    escolha, via = e, via_v
                        elif ac == "tocar":
                            rot = str(res.get("rotulo") or "").strip()[:60]
                            x_, y_ = inteiro(res.get("x")), inteiro(res.get("y"))
                            if rot and x_ is not None and y_ is not None:
                                rx, ry = round(x_ * (fator or 1.0)), round(y_ * (fator or 1.0))
                                # toque por coordenada só DENTRO da área cega, e o rótulo passa pela mesma lista de
                                # efeitos externos (comprar, enviar…): o texto da página nunca é ordem
                                if (no_retangulo(rx, ry, cega, 8) and not proibido(rot, permitir)
                                        and not falhou(sig, rot)):
                                    escolha = {"texto": rot, "x": rx, "y": ry, "clicavel": True,
                                               "pacote": app_atual, "visao": True}
                                    via = via_v
                        elif ac == "rolar" and not falhou(sig, ROLAR):
                            escolha, via = ROLAR, via_v
                        elif ac == "voltar" and not falhou(sig, VOLTAR):
                            escolha, via = VOLTAR, via_v
                if not visto and usar_modelo and (opcoes or extras):
                    consultas += 1
                    t_dec = self.relogio()
                    res = self.decidir(objetivo, contexto, opcoes + extras, nivel)
                    idx, fonte = (res[0], res[1]) if isinstance(res, tuple) else (res, None)
                    via_modelo = f"modelo:{fonte or '?'} ({nivel}, {round((self.relogio() - t_dec) * 1000)} ms)"
                    if idx is not None and 0 <= idx < len(opcoes):
                        escolha, via = melhor(alvos, opcoes[idx]), via_modelo
                        if escolha is not None and not seguro(escolha, els, permitir):
                            escolha = None
                    elif idx is not None and 0 <= idx - len(opcoes) < len(extras):
                        via = via_modelo
                        escolha = extras[idx - len(opcoes)]
                        if escolha == CUMPRIDO:
                            escolha = None
                            j = ler_resposta(els, app_atual) if pergunta and self.julgar is not None else {}
                            if j.get("feito") is False:  # a leitura discorda: não está na tela ainda
                                falhas[(sig, CUMPRIDO)] = 2
                                resposta[0] = None
                                anotar("conferir", "não cumprido", via_modelo, t0)
                                continue
                            conclusao[0] = "modelo"
                            anotar("concluir", None, via_modelo, t0)
                            return fim("concluido", None, els, app_atual)
            # 5. sem decisão: o alvo pode estar mais abaixo
            if not escolha and not falhou(sig, ROLAR) and (cega or any(e.get("rolavel") for e in els)):
                escolha, via = ROLAR, "rolagem"
            if not escolha:
                return fim("parado", "não sei o próximo passo (preciso do Claude)", els, app_atual)

            # ---- agir
            if escolha == ROLAR:
                lista = max((e for e in els if e.get("rolavel")), key=lambda e: e.get("a", 0), default=None)
                if lista is None and cega:  # página web: a lista é a própria área cega
                    lista = {"x": cega[0] + cega[2] // 2, "y": cega[1] + cega[3] // 2, "a": cega[3]}
                x = lista["x"] if lista else 540
                y0 = (lista["y"] + lista.get("a", 1200) // 3) if lista else 1700
                y1 = (lista["y"] - lista.get("a", 1200) // 3) if lista else 700
                t.injetar(f"deslizar {x} {y0} {x} {y1} 700")  # gesto lento: sem "patinar" (a lista assenta logo)
                rotulo_acao, acao = ROLAR, "rolar"
            elif escolha == VOLTAR:
                t.injetar("tecla 4")
                rotulo_acao, acao = VOLTAR, "voltar"
            else:
                if not seguro(escolha, els, permitir):  # dupla checagem antes de qualquer toque
                    falhas[(sig, rotulo(escolha))] = 2
                    continue
                t.injetar(f"tocar {escolha['x']} {escolha['y']}")
                ultimo_toque[0], passos_sig[0] = self.relogio(), sig
                rotulo_acao, acao = rotulo(escolha), "tocar"
            t.calma(150, 1200 if acao == "rolar" else 2500)
            # ---- conferir: a tela mudou?
            xml_d = t.dump_ui()
            depois = t.elementos(xml_d, 300)
            app_depois = t.foco()
            sig_depois = assinar(depois, app_depois, xml_d)
            if (acao == "tocar" and app and app_depois and app_depois != app_atual and not sistema(app_depois)
                    and not t.bloqueado(app_depois)):
                apps_ok.add(app_depois)  # o nosso toque abriu este app: faz parte do caminho
            if sig_depois == sig and app_depois == app_atual and acao != "rolar":
                falhas[(sig, rotulo_acao)] = falhas.get((sig, rotulo_acao), 0) + 1  # sem efeito: 1ª vez repete,
                anotar(acao, rotulo_acao, via + " (sem efeito)", t0)                # 2ª tenta outra coisa
                vistos[sig] -= 1  # tela igual por falha da ação não conta como volta em círculo
            else:
                if acao == "rolar" and sig_depois == sig:
                    falhas[(sig, ROLAR)] = 2  # fim da lista
                if acao != "rolar":
                    feitas.add((sig, rotulo_acao))  # voltar a esta tela e repetir = ciclo (chat ↔ info, 21/11)
                if acao in ("tocar", "rolar") and via != "dispensar" and not (
                        isinstance(escolha, dict) and escolha.get("visao")):  # toque por coordenada não se repete
                    caminho.append((sig, rotulo_acao, sig_depois))
                elif acao == "voltar" and caminho:
                    caminho.pop()  # voltar desfaz o último passo: ele foi desvio
                if escolhida_pista:
                    usadas.add(escolhida_pista)
                anotar(acao, rotulo_acao, via, t0)


def inteiro(v):
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return None


def busca(e):
    """Campo/atalho de busca ou assistente (ex.: "Pergunte à Meta AI ou pesquise"): sem texto para digitar não leva
    a lugar nenhum — o modelo do celular escolheu isso no teste do WhatsApp (21/11)."""
    return bool(e.get("editavel")) or bool(re.search(r"pesquis|buscar|search|meta ai|pergunte", norm(rotulo(e))))


def tocavel(e, els):
    if e.get("clicavel"):
        return True
    x, y = e.get("x", 0), e.get("y", 0)
    return any(o.get("clicavel") and o is not e and abs(o.get("x", 0) - x) <= o.get("l", 0) / 2
               and abs(o.get("y", 0) - y) <= o.get("a", 0) / 2 for o in els)


IGNORADAS = {"abrir", "ver", "tela", "dentro", "das", "dos", "sem", "nada", "alterar", "app", "aplicativo", "apps",
             "configuracoes", "celular", "para", "com", "que", "uma", "um", "informacoes"}


def ranquear(opcoes, objetivo, n, pontos=False):
    """As `n` opções que mais lembram o objetivo (palavras em comum), na ordem da tela. pontos=True: só a pontuação
    da primeira opção (0 = nada a ver com o objetivo)."""
    alvo = set(re.findall(r"\w{3,}", norm(objetivo))) - IGNORADAS
    pont = {o: len(alvo & set(re.findall(r"\w{3,}", norm(o)))) for o in opcoes}
    if pontos:
        return pont[opcoes[0]] if opcoes else 0
    if len(opcoes) <= n:
        return opcoes
    melhores = set(sorted(opcoes, key=lambda o: -pont[o])[:n])
    return [o for o in opcoes if o in melhores]


def interruptor(e, els):
    """Liga/desliga: o próprio elemento é marcável (Switch, CheckBox) ou a linha dele tem um marcável ao lado
    (nas Configurações, tocar a linha alterna o interruptor). Mudar um ajuste é efeito, não navegação."""
    if e.get("marcado") is not None or re.search(r"switch|checkbox|toggle|radio", str(e.get("classe", "")), re.I):
        return True
    return any(o is not e and o.get("marcado") is not None and o.get("pacote") == e.get("pacote")
               and abs(int(o.get("y", -9999)) - int(e.get("y", 0))) <= 60 for o in els)


def seguro(e, els, permitir=()):
    """Pode tocar sem autorização: nem rótulo de efeito externo, nem interruptor (salvo se liberado em `permitir`)."""
    r = rotulo(e)
    liberado = any(norm(p) and norm(p) in norm(r) for p in permitir)
    return not proibido(r, permitir) and (liberado or not interruptor(e, els))


def sistema(pacote):
    """Janelas do sistema por cima do app (cortina de notificações, painel rápido)."""
    return bool(pacote) and (pacote == "com.android.systemui" or pacote.endswith(".systemui")
                             or pacote.startswith("miui.systemui"))


def melhor(els, texto, estrito=False):
    """Elemento cujo rótulo é o texto (igual > começa com > contém), preferindo clicável. estrito: sem "contém"."""
    alvo = norm(texto)
    if not alvo:
        return None
    testes = [lambda r: r == alvo, lambda r: r.startswith(alvo + " ") or r == alvo]
    if not estrito:
        testes.append(lambda r: alvo in r)
    for teste in testes:
        # campo de texto nunca é alvo de toque: depois de digitar "WhatsApp" a pista casava com o próprio campo
        cands = [e for e in els if teste(norm(rotulo(e))) and not e.get("editavel")]
        if cands:
            clic = [e for e in cands if e.get("clicavel")]
            return (clic or cands)[0]
    return None


def textos_da_tela(els, app, n=60):
    """O que está escrito na tela final (só do app em foco), na ordem de leitura: é a resposta para o Claude."""
    vistos, out = set(), []
    for e in sorted((e for e in els if not app or e.get("pacote") == app), key=lambda e: (e.get("y", 0), e.get("x", 0))):
        r = rotulo(e)
        if r and r not in vistos:
            vistos.add(r)
            out.append(r)
        if len(out) >= n:
            break
    return out
