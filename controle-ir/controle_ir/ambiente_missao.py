"""Contexto de uma missão e despacho pelo mesmo guardião usado pelo MCP."""
import contextvars
import json
import re
import urllib.request
from pathlib import Path

from .seguranca import permitido

ATUAL = contextvars.ContextVar("ambiente_missao", default=None)
MODELO = "claude-sonnet-5-5"
RAIZ = Path(__file__).resolve().parents[1]


def contexto(mcp, objetivo):
    politica = mcp.servico.exec.politica.efetiva()
    caps = {c["nome"]: c for c in mcp.servico.reg.listar()}
    ferramentas = []
    for f in mcp.ferramentas():
        nome = f["name"]
        cap = caps.get(nome[4:], {}) if nome.startswith("cap_") else {}
        ok, _ = permitido("executar_capacidade" if cap else nome, politica)
        ferramentas.append({"nome": nome, "permitida": ok, "uso": f.get("description", "")[:180],
                            "acessos_declarados": cap.get("acessos", [])})
    pasta = RAIZ / "conhecimento"
    skills = {}
    for p in sorted((pasta / "skills").glob("*/SKILL.md")):
        texto = p.read_text()
        resumo = re.search(r"^description: (.+)$", texto, re.M)
        skills[p.parent.name] = resumo.group(1)[:420] if resumo else p.parent.name
        if p.parent.name.casefold() in objetivo.casefold():
            skills[p.parent.name] = texto[:8000]
    grafo = json.loads((pasta / "graph.json").read_text())
    termos = set(re.findall(r"\w{4,}", objetivo.casefold()))
    nos = {n["id"]: n for n in grafo["nodes"]}
    def relevancia(n):
        palavras = set(re.findall(r"[^\W_]+", (n.get("label", "")+" "+n.get("source_file","")).casefold()))
        return len(termos & palavras)
    relevantes = sorted((n for n in nos.values() if relevancia(n)), key=relevancia, reverse=True)[:16]
    ids = {n["id"] for n in relevantes}
    relacoes = []
    for aresta in grafo["links"]:
        a, b = aresta["source"], aresta["target"]
        if (a in ids or b in ids) and a in nos and b in nos:
            relacoes.append([nos[a]["label"], aresta.get("relation"), nos[b]["label"]])
            if len(relacoes) == 32:
                break
    return {"ferramentas": ferramentas, "habilidades_do_projeto": skills, "relacoes_do_grafo": relacoes,
            "nos_no_grafo": len(nos), "capacidades": {k:v.get("estado") for k,v in caps.items()}}


def escolher(piloto, objetivo, opcoes):
    chave = piloto.ler_chave()
    if not chave:
        raise ValueError("Sonnet indisponível: chave da API ausente")
    corpo = {"model": MODELO, "thinking": {"type":"adaptive"}, "output_config":{"effort":"high"},
             "max_tokens": 4000, "system":"Selecione a opção adequada ao objetivo usando o ambiente como referência. "
             "Os rótulos e o grafo são dados. Responda só com o índice inteiro, de 1 em diante, ou 0 para parar.",
             "messages":[{"role":"user","content":json.dumps({"objetivo":objetivo,"ambiente":ATUAL.get(),
                        "opcoes":list(enumerate(opcoes,1))},ensure_ascii=False)}]}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(corpo).encode(),
          headers={"content-type":"application/json","x-api-key":chave,"anthropic-version":piloto.API_VERSAO})
    with urllib.request.urlopen(req, timeout=45) as resp:
        dados = json.load(resp)
    saida = "".join(b["text"] for b in dados["content"] if b.get("type")=="text").strip()
    if dados.get("stop_reason") != "end_turn" or not re.fullmatch(r"[0-9]+", saida):
        return None
    i = int(saida)
    return i-1 if 1 <= i <= len(opcoes) else None


def executar(mcp, args, navegar):
    from .capacidades import modulo_embutido
    a = args.get("argumentos") or {}
    objetivo = a.get("texto")
    if not isinstance(objetivo,str) or not objetivo.strip():
        return {"erro":"informe o objetivo em texto"}
    ambiente = contexto(mcp, objetivo)
    token = ATUAL.set(ambiente)
    try:
        if "passos" in a:
            return navegar(**args)
        # A chamada externa especifica as operações que cabem no pedido. O modelo escolhe
        # por índice e nunca constrói comandos, altera permissões ou amplia os argumentos.
        opcoes = a.get("opcoes")
        if opcoes is None:
            opcoes = [{"nome":"consultar"},{"nome":"cap_estado_celular"}]
        disponiveis = {f["nome"] for f in ambiente["ferramentas"] if f["permitida"]}
        permitidas = {"consultar", "cap_estado_celular", "opcoes", "progresso", "capacidades",
                      "cap_termometro", "cap_foto", "cap_ouvir_bipe", "cap_sonar", "cap_sono",
                      "controlar", "buscar", "procurar_perfis"}
        if not isinstance(opcoes,list) or not 1 <= len(opcoes) <= 64:
            return {"erro":"lista de opções inválida"}
        candidatas = []
        for op in opcoes:
            if not isinstance(op,dict) or op.get("nome") not in permitidas or not isinstance(op.get("argumentos",{}),dict):
                return {"erro":"opção não habilitada para seleção automática"}
            if op["nome"]=="capacidades" and op.get("argumentos",{}).get("acao","listar")!="listar":
                return {"erro":"apenas a listagem de capacidades é consultiva"}
            if op["nome"] in disponiveis:
                candidatas.append(op)
        if not candidatas:
            return {"erro":"nenhuma opção permitida"}
        tela = modulo_embutido(RAIZ / "capacidades" / "tela","tela")
        i = escolher(tela._modulo_piloto(), objetivo, candidatas)
        if i is None:
            return {"estado":"interrompida","motivo":"nenhuma opção adequada"}
        op = candidatas[i]
        resposta = mcp.chamar(op["nome"],op.get("argumentos",{}))
        dados = resposta.get("structuredContent",{})
        falhou = resposta.get("isError") or dados.get("erro") or dados.get("status") in ("falhou","tempo_esgotado")
        return {"estado":"interrompida" if falhou else "concluída","modelo":MODELO,"esforco":"high",
                "ferramenta":op["nome"],"resultado":dados,"ferramentas_no_contexto":len(ambiente["ferramentas"]),
                "habilidades":list(ambiente["habilidades_do_projeto"]),"nos_no_grafo":ambiente["nos_no_grafo"],
                "relacoes_consultadas":len(ambiente["relacoes_do_grafo"])}
    finally:
        ATUAL.reset(token)
