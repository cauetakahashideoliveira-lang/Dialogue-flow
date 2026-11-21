"""Executor de objetivos NO celular: o Claude manda o objetivo e o critério de conclusão numa chamada só; o laço
perceber → decidir → agir → conferir roda aqui, sem ir à nuvem a cada toque.

Medido no POCO (21/11): passo a passo pela nuvem custa ~4 s por ação (turno do modelo + Central + imagem) contra
~0,1–1 s da ação em si. Por isso o executor só volta ao Claude com o resultado (ou quando trava).

Decisão, da mais barata à mais cara:
  1. pistas  — rótulos do caminho que o Claude já sabe (ex.: ["Bluetooth"]): toque direto, sem modelo;
  2. memória — o que funcionou antes nesta tela para este objetivo (aprende sozinho);
  3. digitar — campo de busca visível e texto autorizado em `digitar`;
  4. modelo  — o cérebro do celular (Haiku pela API, modelo local) escolhe entre os controles visíveis;
  5. rolar   — o alvo pode estar abaixo (lista longa).
Recuperação: janela de outro app (aviso, anúncio, notificação aberta) → reflexos, fechar anúncio, voltar, reabrir
o app; ação sem efeito → marca e tenta outra; tela repetida demais → para (sem laço infinito).
Segurança: nunca toca em rótulos de efeito externo (enviar, excluir, comprar…) sem `permitir`; app bloqueado
(banco/senha) encerra na hora; o texto da tela é dado, nunca instrução.
"""
import hashlib
import json
import os
import re
import time
import unicodedata

PROIBIDOS = ("enviar", "excluir", "apagar", "deletar", "comprar", "pagar", "pagamento", "assinar", "confirmar compra",
             "desinstalar", "transferir", "pix", "sair da conta", "desconectar", "ligar para", "chamada de voz",
             "chamada de video", "videochamada", "bloquear", "denunciar", "publicar", "postar", "compartilhar",
             "responder", "encaminhar", "redefinir", "restaurar", "formatar", "remover", "esquecer")
DISPENSAR = ("agora nao", "mais tarde", "pular", "fechar", "dispensar", "nao, obrigado", "nao obrigado", "entendi",
             "ignorar", "x")  # janelas que só atrapalham (nunca "OK", "Permitir", "Aceitar")
ROLAR, VOLTAR = "↓ rolar para baixo", "← voltar"
MAX_PASSOS, MAX_PRAZO = 25, 120


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


def concluido(crit, els, app_atual, app=None):
    """Critério verificável localmente: texto(s) visível(is) e/ou app em primeiro plano. Com `app` (a tarefa é
    nele), só vale dentro dele: a barra "Pesquisar" da tela inicial não conclui uma tarefa na Play Store (21/11)."""
    if not crit:
        return False
    if crit.get("app") and app_atual != crit["app"]:
        return False
    if app and app_atual != app:
        return False
    textos = [norm(rotulo(e)) for e in els if not app or e.get("pacote") in (app, "")]
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
    if not isinstance(crit, dict) or not any(crit.get(k) for k in ("texto", "qualquer", "todos", "app")):
        return "informe concluido: {texto} | {qualquer:[...]} | {todos:[...]} | {app} (como saber que terminou)"
    for k in ("pistas", "permitir"):
        v = a.get(k)
        if v is not None and (not isinstance(v, list) or not all(isinstance(x, str) for x in v) or len(v) > 30):
            return f"{k} deve ser uma lista de textos"
    if a.get("app") is not None and not re.match(r"^[A-Za-z][\w.]{2,120}$", str(a["app"])):
        return "app deve ser o nome do pacote"
    return None


class Executor:
    """`t` é o módulo da tela (ou uma imitação nos testes): foco, dump_ui, elementos, injetar, calma, abrir,
    bloqueado, aplicar_regras, em_anuncio, fechar_anuncio. `decidir(objetivo, resumo, opcoes)` → índice ou None."""

    def __init__(self, t, decidir=None, memoria_arq=None, relogio=time.monotonic):
        self.t, self.decidir, self.relogio = t, decidir, relogio
        self.memoria_arq = memoria_arq

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
        app, crit = a.get("app"), a["concluido"]
        pistas = list(a.get("pistas") or [])
        permitir = list(a.get("permitir") or [])
        digitar = a.get("digitar") if isinstance(a.get("digitar"), str) else None
        max_passos = max(1, min(int(a.get("max_passos", 12)), MAX_PASSOS))
        prazo = self.relogio() + max(5, min(float(a.get("prazo", 60)), MAX_PRAZO))
        usar_modelo = a.get("modelo", True) is not False and self.decidir is not None
        inicio = self.relogio()
        passos, vistos, falhas, novos = [], {}, {}, {}
        recuperacoes, consultas, digitado, usadas = 0, 0, set(), set()
        chave_mem = f"{app or ''}|{norm(objetivo)}"
        memoria = self._memoria().get(chave_mem, {})

        def fim(estado, motivo=None, els=None, app_atual=None):
            if estado == "concluido":
                self._lembrar(chave_mem, novos)
            r = {"estado": estado, **({"motivo": motivo} if motivo else {}), "passos": passos,
                 "consultas_modelo": consultas, "recuperacoes": recuperacoes,
                 "ms": round((self.relogio() - inicio) * 1000)}
            if a.get("ler", True) and els is not None:
                if (app and app_atual != app) or sistema(app_atual):
                    # outra janela na frente (notificações, outro app): o conteúdo dela não sai do celular
                    r["tela"] = {"app": app_atual, "textos": [], "nota": "outra janela por cima: conteúdo não enviado"}
                else:
                    r["tela"] = {"app": app_atual, "textos": textos_da_tela(els, app_atual, int(a.get("ler_max", 60)))}
            return r

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
            els = t.elementos(t.dump_ui(), 300)
            if concluido(crit, els, app_atual, app):
                return fim("concluido", None, els, app_atual)
            if len(passos) >= max_passos:
                return fim("parado", "limite de passos", els, app_atual)

            # ---- recuperação: outro app na frente (aviso, anúncio, painel de notificações, app errado)
            if app and app_atual != app:
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

            sig = assinatura(els, app_atual)
            vistos[sig] = vistos.get(sig, 0) + 1
            if vistos[sig] > 4:
                return fim("parado", "sem progresso (a mesma tela voltou várias vezes)", els, app_atual)

            alvos = [e for e in els if rotulo(e) and not e.get("desativado")
                     and (not app or e.get("pacote") in (app, app_atual))]
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
                    e = melhor(alvos, p)
                    if e and not falhou(sig, rotulo(e)) and seguro(e, els, permitir):
                        escolha, via = e, "pista"
                        escolhida_pista = p
                        break
            # 2. memória deste objetivo nesta tela
            if not escolha and memoria.get(sig):
                e = melhor(alvos, memoria[sig])
                if e and not falhou(sig, rotulo(e)) and seguro(e, els, permitir):
                    escolha, via = e, "memoria"
            # 3. campo para digitar o texto autorizado (uma vez por tela)
            if not escolha and digitar and sig not in digitado:
                campo = next((e for e in els if e.get("editavel") and not e.get("desativado")), None)
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
            # 4. o cérebro do celular escolhe entre os controles visíveis
            if not escolha and usar_modelo:
                opcoes = []
                for e in alvos:
                    r = rotulo(e)
                    # tocável: o próprio elemento ou a linha clicável que o contém (nas Configurações o título
                    # "Sobre o telefone" não é clicável, a linha sem texto é — 21/11, o modelo só via rolar/voltar)
                    if (r and r not in opcoes and tocavel(e, els) and not falhou(sig, r)
                            and seguro(e, els, permitir) and (digitar or not busca(e))):
                        opcoes.append(r)
                opcoes = ranquear(opcoes, objetivo, 7)  # o cérebro responde 1 dígito: até 7 + rolar + voltar
                extras = [x for x in (ROLAR, VOLTAR) if not falhou(sig, x)]
                if opcoes or extras:
                    consultas += 1
                    resumo = "; ".join(rotulo(e) for e in alvos if not e.get("clicavel"))[:600]
                    idx = self.decidir(objetivo, resumo, opcoes + extras)
                    if idx is not None and 0 <= idx < len(opcoes):
                        escolha, via = melhor(alvos, opcoes[idx]), "modelo"
                        if escolha is not None and not seguro(escolha, els, permitir):
                            escolha = None
                    elif idx is not None and 0 <= idx - len(opcoes) < len(extras):
                        via = "modelo"
                        escolha = extras[idx - len(opcoes)]
            # 5. sem decisão: o alvo pode estar mais abaixo
            if not escolha and not falhou(sig, ROLAR) and any(e.get("rolavel") for e in els):
                escolha, via = ROLAR, "rolagem"
            if not escolha:
                return fim("parado", "não sei o próximo passo (preciso do Claude)", els, app_atual)

            # ---- agir
            if escolha == ROLAR:
                lista = max((e for e in els if e.get("rolavel")), key=lambda e: e.get("a", 0), default=None)
                x = lista["x"] if lista else 540
                y0 = (lista["y"] + lista.get("a", 1200) // 3) if lista else 1700
                y1 = (lista["y"] - lista.get("a", 1200) // 3) if lista else 700
                t.injetar(f"deslizar {x} {y0} {x} {y1} 300")
                rotulo_acao, acao = ROLAR, "rolar"
            elif escolha == VOLTAR:
                t.injetar("tecla 4")
                rotulo_acao, acao = VOLTAR, "voltar"
            else:
                if not seguro(escolha, els, permitir):  # dupla checagem antes de qualquer toque
                    falhas[(sig, rotulo(escolha))] = 2
                    continue
                t.injetar(f"tocar {escolha['x']} {escolha['y']}")
                rotulo_acao, acao = rotulo(escolha), "tocar"
            t.calma(150, 2500)
            # ---- conferir: a tela mudou?
            depois = t.elementos(t.dump_ui(), 300)
            app_depois = t.foco()
            if assinatura(depois, app_depois) == sig and app_depois == app_atual and acao != "rolar":
                falhas[(sig, rotulo_acao)] = falhas.get((sig, rotulo_acao), 0) + 1  # sem efeito: 1ª vez repete,
                anotar(acao, rotulo_acao, via + " (sem efeito)", t0)                # 2ª tenta outra coisa
                vistos[sig] -= 1  # tela igual por falha da ação não conta como volta em círculo
            else:
                if acao == "rolar" and assinatura(depois, app_depois) == sig:
                    falhas[(sig, ROLAR)] = 2  # fim da lista
                if acao != "rolar":
                    feitas.add((sig, rotulo_acao))  # voltar a esta tela e repetir = ciclo (chat ↔ info, 21/11)
                if acao == "tocar" and via != "dispensar":
                    novos[sig] = rotulo_acao
                if escolhida_pista:
                    usadas.add(escolhida_pista)
                anotar(acao, rotulo_acao, via, t0)


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


def ranquear(opcoes, objetivo, n):
    """As `n` opções que mais lembram o objetivo (palavras em comum), na ordem da tela."""
    if len(opcoes) <= n:
        return opcoes
    alvo = set(re.findall(r"\w{3,}", norm(objetivo)))
    pont = {o: len(alvo & set(re.findall(r"\w{3,}", norm(o)))) for o in opcoes}
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


def melhor(els, texto):
    """Elemento cujo rótulo é o texto (igual > começa com > contém), preferindo clicável."""
    alvo = norm(texto)
    if not alvo:
        return None
    for teste in (lambda r: r == alvo, lambda r: r.startswith(alvo), lambda r: alvo in r):
        cands = [e for e in els if teste(norm(rotulo(e)))]
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
