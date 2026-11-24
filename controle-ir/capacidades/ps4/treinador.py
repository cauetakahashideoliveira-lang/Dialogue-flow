"""Técnico ao vivo: um modelo da Anthropic olha a luta a cada poucos segundos (quadro + placar + o que está
conectando) e reescreve a estratégia do jogador (ordem dos golpes por situação). O jogador continua decidindo
no laço rápido; o técnico só muda o plano. Chave: ~/.controle-ir/anthropic.key (a mesma do piloto)."""
import base64
import json
import os
import re
import ssl
import time
import urllib.request

API = "https://api.anthropic.com/v1/messages"
VERSAO = "2023-06-01"
SITUACOES = ["perto|chao", "medio|chao", "longe|chao", "*|ar"]


def ler_chave(base):
    k = os.environ.get("ANTHROPIC_API_KEY")
    if k:
        return k.strip()
    try:
        with open(os.path.join(base, "anthropic.key")) as f:
            return f.read().strip() or None
    except OSError:
        return None


def montar_pedido(relatorio, habilidades, estrategia, jpeg, objetivo):
    """Texto + imagem para o modelo. Pede só JSON."""
    resumo = {
        "placar": relatorio.get("placar"),
        "ultima_percepcao": relatorio.get("ultima_percepcao"),
        "valor_por_situacao": {k: {"melhor": v.get("melhor"), "valores": v.get("valores")}
                               for k, v in (relatorio.get("politica") or {}).items()},
        "estrategia_atual": {k: estrategia.get("situacoes", {}).get(k) for k in SITUACOES},
    }
    texto = (
        f"Você é o técnico de um jogador automático de luta. Objetivo: {objetivo}. O jogador reage em ~0,4 s, "
        "então prefira golpes rápidos e seguros, punição depois de defender e distância quando estiver perdendo.\n"
        f"Habilidades disponíveis (nome: descrição): {json.dumps(habilidades, ensure_ascii=False)}\n"
        f"Situação agora: {json.dumps(resumo, ensure_ascii=False)}\n"
        "A imagem é o quadro atual da luta. Responda SÓ um JSON: {\"situacoes\": {\"perto|chao\": [...], "
        "\"medio|chao\": [...], \"longe|chao\": [...], \"*|ar\": [...]}, \"variar\": 0.0-0.4, \"dica\": \"frase curta\"} "
        "com 2 a 5 habilidades por situação, da melhor para a pior, usando só os nomes listados.")
    conteudo = [{"type": "text", "text": texto}]
    if jpeg:
        conteudo.insert(0, {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                                         "data": base64.b64encode(jpeg).decode()}})
    return conteudo


def interpretar(texto, nomes_validos):
    """Extrai o JSON da resposta e mantém só habilidades que existem. None se não der para usar."""
    m = re.search(r"\{.*\}", texto or "", re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except ValueError:
        return None
    sit = {}
    for k in SITUACOES:
        lista = [h for h in (d.get("situacoes") or {}).get(k, []) if h in nomes_validos]
        if lista:
            sit[k] = lista[:6]
    if not sit:
        return None
    out = {"situacoes": sit, "dica": str(d.get("dica", ""))[:200]}
    try:
        out["variar"] = max(0.0, min(0.4, float(d.get("variar", 0.15))))
    except (TypeError, ValueError):
        pass
    return out


def perguntar(chave, modelo, conteudo, timeout=12):
    corpo = json.dumps({"model": modelo, "max_tokens": 400,
                        "messages": [{"role": "user", "content": conteudo}]}).encode()
    req = urllib.request.Request(API, data=corpo, headers={
        "content-type": "application/json", "x-api-key": chave, "anthropic-version": VERSAO})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as r:
        d = json.loads(r.read())
    return "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text")


def aplicar(estrategia, plano):
    """Troca as listas das situações que o técnico mandou; guarda o resto."""
    sit = dict(estrategia.get("situacoes") or {})
    sit.update(plano["situacoes"])
    estrategia["situacoes"] = sit
    if "variar" in plano:
        estrategia["variar"] = plano["variar"]
    estrategia["dica_tecnico"] = plano.get("dica")
    estrategia["tecnico_em"] = time.strftime("%H:%M:%S")
    return estrategia
