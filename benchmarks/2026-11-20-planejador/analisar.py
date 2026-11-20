"""Uso: python analisar.py. Lê casos.tsv e resultados-*.jsonl na mesma pasta."""
import collections
import json
import math
import random
import statistics
from pathlib import Path

PASTA = Path(__file__).resolve().parent
BASE, CANDIDATA = "base", "candidata"
ORDEM = (BASE, CANDIDATA)


def agenda():
    casos = []
    for l in (PASTA/"casos.tsv").read_text().splitlines():
        ident, ferramentas, pedido = l.split("\t")
        casos.append(dict(id=ident, esperado=[] if ferramentas=="-" else ferramentas.split(","), pedido=pedido))
    rng = random.Random(20261120)
    saida = []
    for rep in (1, 2):
        lista = casos.copy()
        rng.shuffle(lista)
        saida.extend(dict(rep=rep, **c) for c in lista)
    return saida


def percentil95(tempos):
    return sorted(tempos)[math.ceil(.95*len(tempos))-1]


def extras(r):
    return sum((collections.Counter(r["executado"]) - collections.Counter(r["esperado"])).values())


def analisar(linhas):
    por_chave = {(r["versao"],r["rep"],r["id"]):r for r in linhas}
    assert len(linhas)==len(por_chave)==160, "faltam observações ou existem duplicatas"
    grupos = {}
    for ver in ORDEM:
        grupo = [por_chave[ver,c["rep"],c["id"]] for c in agenda()]
        for r,c in zip(grupo,agenda()):
            assert r["esperado"]==c["esperado"]
            esperado = "concluída" if r["esperado"] else "interrompida"
            ok = not r["erro"] and r["estado"]==esperado and r["executado"]==r["esperado"] and r["recibos_validos"]
            assert bool(ok)==r["acerto"]
        grupos[ver]=grupo
    stats={}
    for ver,grupo in grupos.items():
        viaveis = [r for r in grupo if r["esperado"]]
        inviaveis = [r for r in grupo if not r["esperado"]]
        tempos = [r["ms"] for r in grupo]
        taxa=lambda rs:sum(r["acerto"] for r in rs)
        grupos_pedido = collections.defaultdict(list)
        for r in grupo:
            grupos_pedido[r["id"]].append(r["acerto"])
        stats[ver]=dict(viaveis=taxa(viaveis), inviaveis=taxa(inviaveis), extras=sum(map(extras,grupo)),
                        chamadas=sum(len(r["executado"]) for r in grupo),
                        estado_por_codigo=dict(collections.Counter(r["codigo"] or r["estado"] or "transporte" for r in grupo)),
                        total=taxa(grupo), mediana_ms=statistics.median(tempos), p95_ms=percentil95(tempos),
                        mediana_viavel_ms=statistics.median(r["ms"] for r in viaveis),
                        pedidos_com_resultado_variavel=sum(len(set(xs))>1 for xs in grupos_pedido.values()),
                        erros_transporte=sum(bool(r["erro"] and not r["estado"]) for r in grupo))
    pares = collections.Counter((a["acerto"],b["acerto"]) for a,b in zip(grupos[BASE],grupos[CANDIDATA]))
    sucessos_pareados = [(a,b) for a,b in zip(grupos[BASE],grupos[CANDIDATA])
                         if a["acerto"] and b["acerto"] and a["esperado"]]
    tempos_pareados = {
        "n": len(sucessos_pareados),
        "mediana_diferenca_ms": statistics.median(b["ms"]-a["ms"] for a,b in sucessos_pareados)
                                if sucessos_pareados else None,
    }
    por_tamanho = {
        ver: {str(n):sum(r["acerto"] for r in grupo if len(r["esperado"])==n) for n in range(4)}
        for ver,grupo in grupos.items()
    }
    s=stats[CANDIDATA]
    return {"versoes":stats,"tempos_pareados_viaveis":tempos_pareados,
            "acertos_por_tamanho_do_pedido":por_tamanho,"pares":{"ambas_passam":pares[True,True],"melhorou":pares[False,True],
                                    "regrediu":pares[True,False],"ambas_falham":pares[False,False]},
            "aprovada_na_bateria":s["viaveis"]>=54 and s["inviaveis"]==20 and s["extras"]==0}


if __name__=="__main__":
    dados=[json.loads(l) for ver in ORDEM for l in (PASTA/f"resultados-{ver}.jsonl").read_text().splitlines()]
    print(json.dumps(analisar(dados),ensure_ascii=False,indent=2))
