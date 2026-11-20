"""Missão de navegação executada no processo residente da capacidade de tela."""
import threading
import time

_EM_USO = threading.Lock()


def executar(a, navegar, escolher):
    inicio = time.monotonic()
    objetivo = a.get("texto")
    etapas = a.get("passos")
    if not isinstance(objetivo, str) or not objetivo.strip() or not isinstance(etapas, list) or not 1 <= len(etapas) <= 16:
        return {"erro": "informe o objetivo e de uma a dezesseis etapas"}
    for etapa in etapas:
        if not isinstance(etapa, dict) or not all(isinstance(etapa.get(c), str) and etapa[c].strip()
                for c in ("pacote", "texto")):
            return {"erro": "cada etapa precisa de pacote e objetivo"}
        if "controles" in etapa or "marcador" in etapa:
            cs = etapa.get("controles")
            if not isinstance(etapa.get("marcador"), str) or not etapa["marcador"].strip() or (cs is not None and (not isinstance(cs, list) or not 1 <= len(cs) <= 32 or not all(isinstance(c, str) and c.strip() for c in cs))):
                return {"erro": "marcador ou controles inválidos"}
    if not _EM_USO.acquire(blocking=False):
        return {"erro": "outra missão está em execução"}
    resultados = []
    try:
        for etapa in etapas:
            pacote, pedido = etapa["pacote"], etapa["texto"]
            if "marcador" in etapa:
                args = {"pacote": pacote, "passos": [etapa], "iniciar": {"abrir": True, "descobrir": etapa.get("controles") is None}}
            else:
                rotas = navegar({"pacote": pacote, "mostrar": True})
                nomes = rotas.get("rotas", [])
                nome = next((n for n in nomes if n.casefold() == pedido.casefold()), None)
                if nome is None and nomes:
                    nome = escolher(objetivo, pedido, nomes)
                if nome not in nomes:
                    resultados.append({"pedido": pedido, "estado": rotas.get("erro") or "sem rota compatível"})
                    break
                args = {"pacote": pacote, "nome": nome, "iniciar": {"abrir": True}}
            r = navegar(args)
            medidas = r.get("etapas", [r])
            confirmado = bool(medidas) and all(m.get("estado") == "objetivo confirmado" for m in medidas)
            resultados.append({"pedido": pedido, "estado": "confirmado" if confirmado else
                               (medidas[-1].get("erro") or medidas[-1].get("estado") if medidas else "sem resultado"),
                               "gestos": sum(m.get("gestos", 0) for m in medidas)})
            if not confirmado:
                break
        concluida = len(resultados) == len(etapas) and all(r["estado"] == "confirmado" for r in resultados)
        return {"objetivo": objetivo, "estado": "concluída" if concluida else "interrompida",
                "resultados": resultados, "ms": round((time.monotonic() - inicio) * 1000)}
    finally:
        _EM_USO.release()
