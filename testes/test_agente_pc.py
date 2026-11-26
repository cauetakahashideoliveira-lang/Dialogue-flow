"""Agente do PC (pc/agente_pc): assinatura da Central, guardião (armado/desarmado/travado) e ferramentas.

Roda em Linux (CI): os comandos usam sh; tela e entrada só existem no Windows e não são testadas aqui.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "controle-ir"))
sys.path.insert(0, str(RAIZ / "pc"))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat  # noqa: E402

from agente_pc import config, ferramentas as ferr_mod, tarefas as tarefas_mod  # noqa: E402
from agente_pc.ferramentas import Ferramentas  # noqa: E402
from agente_pc.servidor import Guardiao, ServidorMCP, criar_servidor  # noqa: E402


def b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


class CentralFalsa:
    """Faz o papel da Central: chave Ed25519, estado assinado e assinatura de cada chamada."""

    def __init__(self, pasta: Path):
        self.pasta = pasta
        self.chave = Ed25519PrivateKey.generate()
        pub = self.chave.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        self.cfg = {"url": "https://central.exemplo", "aparelho": "pc123", "token": "t", "chave_publica": b64u(pub),
                    "seq_max": 0, "offset": 0, "pareado_em": time.time()}
        self.seq = 0
        self.definir(armado=False)

    def definir(self, armado: bool, travado: bool = False):
        self.seq += 1
        estado = json.dumps({"v": 1, "aparelho": "pc123", "seq": self.seq, "travado": int(travado),
                             "armado_ate": time.time() + 3600 if armado else 0, "desarmado_permite": "nada"})
        self.cfg.update(estado=estado, assinatura=b64u(self.chave.sign(estado.encode())), seq_max=self.seq)
        (self.pasta / "painel.json").write_text(json.dumps(self.cfg))

    def assinar(self, corpo: bytes) -> str:
        ts, nonce = str(int(time.time())), secrets.token_hex(8)
        msg = f"{ts}.{nonce}.{hashlib.sha256(corpo).hexdigest()}".encode()
        return f"{ts}.{nonce}.{b64u(self.chave.sign(msg))}"


class TestAgentePC(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pasta = Path(self.tmp.name)
        self.central = CentralFalsa(self.pasta)
        self.cfg = config.ler(self.pasta)
        g = Guardiao(self.pasta, lambda: config.ler(self.pasta), lambda c: config.gravar(c, self.pasta))
        self.ferr = Ferramentas(self.pasta, g.auditar, g.estado, g.travar)
        self.srv = criar_servidor(self.pasta, 0, self.cfg["segredo"], ServidorMCP(self.ferr, g), g)
        self.porta = self.srv.server_address[1]
        import threading
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.n = 0

    def tearDown(self):
        self.ferr.tarefas.parar_todas()
        self.srv.shutdown()
        self.srv.server_close()
        self.tmp.cleanup()

    def rpc(self, metodo, params=None, assinar=True, segredo=None):
        self.n += 1
        corpo = json.dumps({"jsonrpc": "2.0", "id": self.n, "method": metodo, "params": params or {}}).encode()
        cab = {"Content-Type": "application/json"}
        if assinar:
            cab["X-Painel-Assinatura"] = self.central.assinar(corpo)
        req = urllib.request.Request(f"http://127.0.0.1:{self.porta}/mcp/{segredo or self.cfg['segredo']}",
                                     data=corpo, headers=cab, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")

    def chamar(self, nome, **args):
        st, r = self.rpc("tools/call", {"name": nome, "arguments": args})
        self.assertEqual(st, 200, r)
        res = r["result"]
        return json.loads(res["content"][0]["text"]), res["isError"]

    # ------------------------------------------------------------- segurança
    def test_sem_assinatura_ou_segredo_errado_e_recusado(self):
        st, r = self.rpc("tools/list", assinar=False)
        self.assertEqual(st, 401)
        st, _ = self.rpc("tools/list", segredo="errado")
        self.assertEqual(st, 404)

    def test_assinatura_repetida_e_recusada(self):
        corpo = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).encode()
        ass = self.central.assinar(corpo)
        url = f"http://127.0.0.1:{self.porta}/mcp/{self.cfg['segredo']}"
        cab = {"X-Painel-Assinatura": ass}
        with urllib.request.urlopen(urllib.request.Request(url, corpo, cab, method="POST"), timeout=10) as r:
            self.assertEqual(r.status, 200)
        with self.assertRaises(urllib.error.HTTPError) as e:
            urllib.request.urlopen(urllib.request.Request(url, corpo, cab, method="POST"), timeout=10)
        self.assertEqual(e.exception.code, 401)

    def test_lista_so_ferramentas_pc(self):
        st, r = self.rpc("tools/list")
        nomes = {t["name"] for t in r["result"]["tools"]}
        self.assertIn("pc_executar", nomes)
        self.assertTrue(all(n.startswith("pc_") for n in nomes))

    def test_desarmado_so_consultar_e_travar(self):
        d, erro = self.chamar("pc_executar", comando="echo oi")
        self.assertTrue(erro)
        self.assertTrue(d["bloqueado"])
        self.assertIn("DESARMADO", d["erro"])
        d, erro = self.chamar("pc_consultar")
        self.assertFalse(erro, d)
        self.assertFalse(d["seguranca"]["armado"])
        self.assertIn("memoria", d["pc"])

    def test_armado_executa_e_travar_bloqueia_ate_novo_armar(self):
        self.central.definir(armado=True)
        d, erro = self.chamar("pc_executar", comando="echo ola-pc", aguardar=20)
        self.assertFalse(erro, d)
        self.assertEqual(d["status"], "concluida")
        self.assertIn("ola-pc", d["saida"]["texto"])
        d, erro = self.chamar("pc_travar", motivo="teste")
        self.assertFalse(erro)
        d, erro = self.chamar("pc_executar", comando="echo x")
        self.assertTrue(erro)
        self.assertIn("travado", d["erro"])
        self.central.definir(armado=True)  # o dono arma de novo: seq maior que o da trava
        d, erro = self.chamar("pc_executar", comando="echo de-volta", aguardar=20)
        self.assertFalse(erro, d)

    def test_emergencia_na_central_bloqueia(self):
        self.central.definir(armado=True, travado=True)
        d, erro = self.chamar("pc_listar", caminho=str(self.pasta))
        self.assertTrue(erro)
        self.assertIn("EMERGÊNCIA", d["erro"])

    # ------------------------------------------------------------- ferramentas
    def test_tarefa_longa_acompanhar_e_parar(self):
        self.central.definir(armado=True)
        d, _ = self.chamar("pc_executar", comando="echo comecou; sleep 30", aguardar=1)
        self.assertEqual(d["status"], "rodando")
        ident = d["id"]
        d, _ = self.chamar("pc_tarefa", id=ident, acao="listar")
        self.assertTrue(any(t["id"] == ident for t in d["tarefas"]))
        d, _ = self.chamar("pc_tarefa", id=ident, acao="parar")
        self.assertEqual(d["status"], "parada")
        self.assertIn("comecou", d["saida"]["texto"])

    def test_tempo_limite_encerra(self):
        self.central.definir(armado=True)
        d, _ = self.chamar("pc_executar", comando="sleep 20", aguardar=10, tempo_limite=1)
        self.assertEqual(d["status"], "tempo_esgotado")

    def test_arquivos_escrever_editar_ler_listar(self):
        self.central.definir(armado=True)
        arq = self.pasta / "proj" / "a.luau"
        d, erro = self.chamar("pc_escrever_arquivo", caminho=str(arq), conteudo="local x = 1\r\nprint(x)\r\n")
        self.assertFalse(erro, d)
        d, erro = self.chamar("pc_editar_arquivo", caminho=str(arq), antigo="local x = 1\nprint", novo="local x = 2\nprint")
        self.assertFalse(erro, d)
        self.assertEqual(arq.read_bytes(), b"local x = 2\r\nprint(x)\r\n")  # manteve o \r\n
        d, _ = self.chamar("pc_ler_arquivo", caminho=str(arq))
        self.assertEqual(d["total_linhas"], 2)
        self.assertIn("local x = 2", d["conteudo"])
        d, erro = self.chamar("pc_editar_arquivo", caminho=str(arq), antigo="nao existe", novo="y")
        self.assertTrue(erro)
        d, _ = self.chamar("pc_listar", caminho=str(self.pasta), padrao="*.luau", recursivo=True)
        self.assertEqual([i["caminho"].replace("\\", "/") for i in d["itens"]], ["proj/a.luau"])
        png = self.pasta / "x.png"
        png.write_bytes(b"\x89PNG\r\n\x1a\nfalso")
        st, r = self.rpc("tools/call", {"name": "pc_ler_arquivo", "arguments": {"caminho": str(png)}})
        self.assertEqual(r["result"]["content"][1]["type"], "image")

    def test_auditoria_registra_comando(self):
        self.central.definir(armado=True)
        self.chamar("pc_executar", comando="echo auditado", motivo="teste de auditoria", aguardar=20)
        linhas = [json.loads(x) for x in (self.pasta / "auditoria.jsonl").read_text().splitlines()]
        self.assertTrue(any(x.get("evento") == "pc_comando" and "auditado" in x.get("comando", "") for x in linhas))


class TestUnidades(unittest.TestCase):
    def test_sendkeys_escapa_especiais(self):
        from agente_pc.tela import escapar_sendkeys
        self.assertEqual(escapar_sendkeys("a+b (1)\n"), "a{+}b {(}1{)}{ENTER}")

    def test_saida_nao_comeca_no_meio_de_caractere(self):
        with tempfile.TemporaryDirectory() as d:
            t = tarefas_mod.Tarefas(Path(d))
            (Path(d) / "tarefas" / "1.log").write_bytes(("ã" * 10).encode())
            r = t.saida("1", maximo=5)  # corta no meio de um "ã" (2 bytes)
            self.assertNotIn("�", r["texto"])

    def test_nomes_unicos_e_prefixo(self):
        nomes = [d["name"] for d in ferr_mod.DEFINICOES]
        self.assertEqual(len(nomes), len(set(nomes)))
        self.assertTrue(all(n.startswith("pc_") for n in nomes))


if __name__ == "__main__":
    unittest.main()
