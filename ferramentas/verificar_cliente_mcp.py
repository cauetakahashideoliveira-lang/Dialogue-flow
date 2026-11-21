#!/usr/bin/env python3
"""Verifica o servidor com o SDK oficial de MCP (cliente Streamable HTTP).

    python3 -m venv /tmp/v && /tmp/v/bin/pip install mcp
    /tmp/v/bin/python ferramentas/verificar_cliente_mcp.py

Sobe o servidor com emissor simulado e catálogo base, conecta como cliente
MCP, lista as ferramentas e executa um roteiro: consultar, salvar um ar
SmartIR, pedido composto, mudança só de temperatura, oscilação sem suporte
e desligar.
"""
import asyncio
from contextlib import ExitStack
import json
import sys
import tempfile
import threading
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "controle-ir"))

from controle_ir import catalogo  # noqa: E402
from controle_ir.emissor import EmissorSimulado  # noqa: E402
from controle_ir.servico import Servico  # noqa: E402
from controle_ir.servidor import criar_servidor  # noqa: E402

from mcp import ClientSession  # noqa: E402
from mcp.client.streamable_http import streamable_http_client  # noqa: E402
from httpx import AsyncClient  # noqa: E402


def preparar(recursos):
    pasta = recursos.enter_context(tempfile.TemporaryDirectory(prefix="cir-sdk-"))
    c = catalogo.Catalogo(Path(pasta) / "catalogo.sqlite")
    recursos.callback(c.fechar)
    catalogo.importar_jsonl(c, str(RAIZ / "controle-ir" / "dados" / "base.jsonl.gz"))
    em = EmissorSimulado()
    s = Servico(pasta, em, c)
    srv = criar_servidor(s, "segredo-sdk", 0)
    recursos.callback(srv.server_close)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    recursos.callback(th.join)
    recursos.callback(srv.shutdown)
    return srv.server_address[1], em


async def main(porta, em):
    url = f"http://127.0.0.1:{porta}/mcp/segredo-sdk"
    async with AsyncClient(trust_env=False) as http, streamable_http_client(url, http_client=http) as (ler, escrever, *_):
        async with ClientSession(ler, escrever) as sessao:
            init = await sessao.initialize()
            g = lambda o, a, b: getattr(o, a, None) if hasattr(o, a) else getattr(o, b)  # SDK 1.x/2.x
            print("protocolo negociado:", g(init, "protocol_version", "protocolVersion"), "| servidor:",
                  g(init, "server_info", "serverInfo").name)
            tools = await sessao.list_tools()
            print("ferramentas:", ", ".join(t.name for t in tools.tools))

            async def chamar(ferramenta, **args):
                r = await sessao.call_tool(ferramenta, args)
                dados = g(r, "structured_content", "structuredContent") or json.loads(r.content[0].text)
                print(f"\n→ {ferramenta} {json.dumps(args, ensure_ascii=False)}\n  isError={g(r, 'is_error', 'isError')}")
                return dados

            d = await chamar("consultar", categoria="ar")
            print("  marcas de ar:", [m["marca"] for m in d["marcas"][:5]], "| emissor:", d["emissor"]["disponivel"])
            d = await chamar("procurar_perfis", categoria="ar", marca="Midea", modelo="MSY-12HRDN1")
            pid = d["perfis"][0]["id"]
            d = await chamar("salvar_aparelho", nome="ar do quarto", perfil=pid)
            print("  salvo:", d["salvo"], d["parametros"])
            d = await chamar("opcoes", aparelho="ar do quarto")
            print("  estado completo:", d["estado_completo"]["parametros"]["modo"])
            d = await chamar("controlar", aparelho="ar do quarto", ligar=True,
                             definir={"temperatura": 23, "modo": "frio", "ventilacao": "baixa"})
            print("  status:", d["status"], d["configuracao"]["valores"], "| transmissões:", len(em.enviados))
            d = await chamar("controlar", aparelho="ar do quarto", definir={"temperatura": 22})
            print("  status:", d["status"], d["configuracao"]["valores"], d["configuracao"]["origem"])
            d = await chamar("controlar", aparelho="ar do quarto", definir={"oscilacao": "ligado"})
            print("  status:", d["status"], d["nao_suportado"][0][:90])
            d = await chamar("controlar", aparelho="ar do quarto", ligar=False)
            print("  status:", d["status"], "| transmissões:", len(em.enviados))
    assert len(em.enviados) == 3, em.enviados
    print("\nOK: cliente MCP oficial conversou com o servidor e o roteiro produziu 3 transmissões.")


if __name__ == "__main__":
    with ExitStack() as recursos:
        asyncio.run(main(*preparar(recursos)))
