"""Executa rotas confirmadas no MCP residente do próprio telefone."""
import json
import urllib.error
import urllib.request

from .cli import _LOCAL, _porta_ativa, carregar_config


def executar(pacote, nome):
    config = carregar_config()
    req = urllib.request.Request(
        f"http://127.0.0.1:{_porta_ativa(config)}/api/rota", data=json.dumps({"pacote": pacote, "nome": nome}).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + config["token_local"]})
    try:
        with _LOCAL.open(req, timeout=120) as response:
            return json.load(response)
    except (OSError, ValueError, KeyError) as erro:
        return {"erro": str(erro)}
