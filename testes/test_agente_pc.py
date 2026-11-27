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
    def test_saude_mostra_o_canal_quando_informado(self):
        import threading
        with tempfile.TemporaryDirectory() as d:
            pasta = Path(d)
            cfg = config.ler(pasta)
            g = Guardiao(pasta, lambda: config.ler(pasta), lambda c: config.gravar(c, pasta))
            f = Ferramentas(pasta, g.auditar, g.estado, g.travar)
            for canal, esperado in ((None, None), (lambda: {"conectado": False, "erro": "sem rede"}, {"conectado": False, "erro": "sem rede"})):
                srv = criar_servidor(pasta, 0, cfg["segredo"], ServidorMCP(f, g), g, canal=canal)
                threading.Thread(target=srv.serve_forever, daemon=True).start()
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:{srv.server_address[1]}/saude", timeout=5) as r:
                        saude = json.loads(r.read())
                finally:
                    srv.shutdown()
                    srv.server_close()
                self.assertTrue(saude["ok"])
                self.assertEqual(saude.get("canal"), esperado)

    def test_comando_que_termina_antes_da_espera_nao_quebra_o_pedir(self):
        """A6 (26/11): no CI, um comando rápido terminou e o _vigiar tirou o evento de fim do dicionário antes de o
        pedir esperar nele: KeyError: '1'. Aqui a thread roda inteira antes de o start() voltar (o pior caso)."""
        import threading
        from unittest import mock

        class ThreadQueTerminaNoStart(threading.Thread):
            def start(self):
                self.run()

        with tempfile.TemporaryDirectory() as d:
            t = tarefas_mod.Tarefas(Path(d))
            with mock.patch.object(tarefas_mod.threading, "Thread", ThreadQueTerminaNoStart):
                r = t.pedir("echo ok", aguardar=5)
            self.assertEqual(r["status"], "concluida")
            self.assertNotIn(r["id"], t.fim)  # o _vigiar limpou o evento, e o pedir não dependeu dele

    def test_ps1_preso_nao_derruba_o_fim_da_tarefa(self):
        """Regressão (26/11): o antivírus segurava o .ps1 e o unlink lançava PermissionError na thread que fecha a
        tarefa; o evento de fim nunca era sinalizado. Agora o .ps1 fica para depois e a tarefa termina normalmente."""
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            t = tarefas_mod.Tarefas(Path(d))
            original = Path.unlink

            def unlink_preso(self_, missing_ok=False):
                if self_.suffix == ".ps1":
                    raise PermissionError(5, "Acesso negado", str(self_))
                return original(self_, missing_ok=missing_ok)

            with mock.patch.object(Path, "unlink", unlink_preso):
                inicio = time.time()
                r = t.pedir("echo ok", aguardar=10)
                gasto = time.time() - inicio
            # com o defeito, o evento de fim não era sinalizado e o pedir esperava os 10 s inteiros
            self.assertEqual(r["status"], "concluida")
            self.assertLess(gasto, 5, f"pedir ficou preso {gasto:.1f} s esperando o fim da tarefa")

    def test_iniciar_rele_o_path_a_cada_volta(self):
        """Regressão A5 (26/11): o agente seguia com o PATH do logon e não via Node, Ollama nem Rokit instalados depois."""
        txt = (RAIZ / "pc" / "iniciar.ps1").read_text(encoding="utf-8-sig")
        laco = txt[txt.index("while ($true)"):]
        self.assertIn("GetEnvironmentVariable('Path', 'Machine')", laco)
        self.assertLess(laco.index("GetEnvironmentVariable('Path', 'Machine')"), laco.index("-m agente_pc ligar"))

    def test_atualizar_sem_ref_sai_do_head_destacado(self):
        """Depois de um pc_atualizar(ref=...) o repositório fica destacado; o próximo, sem ref, volta à branch padrão."""
        import subprocess
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)

            def git(*a, cwd=None):
                return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "init.defaultBranch=principal",
                                       *a], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()

            def commit(texto):
                (d / "trabalho" / "a.txt").write_text(texto)
                git("add", "-A", cwd=d / "trabalho")
                git("commit", "-qm", texto, cwd=d / "trabalho")
                git("push", "-q", "origin", "principal", cwd=d / "trabalho")

            git("init", "-q", "--bare", str(d / "origem.git"))
            git("clone", "-q", str(d / "origem.git"), str(d / "trabalho"))
            commit("1")
            git("clone", "-q", str(d / "origem.git"), str(d / "pc"))
            git("checkout", "-q", "--detach", "HEAD", cwd=d / "pc")
            commit("2")
            antigo, ferr_mod.REPO = ferr_mod.REPO, d / "pc"
            try:
                f = Ferramentas(d / "agente", lambda r: None, lambda: {}, lambda m: None, ao_reiniciar=lambda: None)
                r = f.pc_atualizar()
            finally:
                ferr_mod.REPO = antigo
            self.assertEqual(git("symbolic-ref", "--short", "HEAD", cwd=d / "pc"), "principal")
            self.assertEqual(r["para"], git("rev-parse", "--short", "HEAD", cwd=d / "trabalho"))

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


class TestVerATela(unittest.TestCase):
    """Ver melhor a tela (pc-1.0.3): ver=true, montagem de vários momentos e região. O PowerShell é falso: o que
    interessa aqui são as contas do agente e o que ele manda para o script; o script de verdade foi rodado no PC."""

    def setUp(self):
        from agente_pc import tela as tela_mod
        self.tela_mod = tela_mod
        self.chamadas = []
        self._orig = tela_mod.rodar_ps
        tela_mod.rodar_ps = self.ps_falso
        self.addCleanup(setattr, tela_mod, "rodar_ps", self._orig)

    def ps_falso(self, script, dados, timeout=60):
        self.chamadas.append((script, dados, timeout))
        if "SetCursorPos" in script:  # entrada
            return "10 20"
        if dados.get("quadros"):  # montagem
            n = dados["quadros"]
            return json.dumps({"x": 0, "y": 0, "largura": 1920, "altura": 1080, "w": 1600, "h": 900, "telas": 1,
                               "tempos": [round(i * dados["intervalo"] / 1000, 2) for i in range(n)], "jpeg": "QUJD"})
        reg = dados.get("regiao") or [0, 0, 1920, 1080]
        esc = min(1.0, dados["largura"] / reg[2])
        return json.dumps({"x": reg[0], "y": reg[1], "largura": reg[2], "altura": reg[3], "w": int(reg[2] * esc),
                           "h": int(reg[3] * esc), "telas": 1, "jpeg": "QUJD"})

    def tela_com_mapa(self):
        t = self.tela_mod.Tela()
        t.ultima = {"x": 100, "y": 50, "largura": 1920, "altura": 1080, "w": 960, "h": 540, "telas": 1, "escala": 0.5}
        return t

    def test_plano_da_grade(self):
        p = self.tela_mod.plano_montagem
        self.assertEqual((p(2, None, 1600)["colunas"], p(2, None, 1600)["linhas"]), (2, 1))
        self.assertEqual((p(4, None, 1600)["colunas"], p(4, None, 1600)["linhas"]), (2, 2))
        self.assertEqual((p(8, None, 1600)["colunas"], p(8, None, 1600)["linhas"]), (3, 3))
        self.assertEqual((p(12, None, 1600)["colunas"], p(12, None, 1600)["linhas"]), (4, 3))
        self.assertEqual(p(8, 4, 1600)["linhas"], 2)
        self.assertEqual(p(3, 9, 1600)["colunas"], 3)  # nunca mais colunas do que quadros
        self.assertEqual(p(8, None, 1600)["largura_celula"], 533)
        for ruim in (1, 0, 13):
            with self.assertRaises(ValueError):
                p(ruim, None, 1600)

    def test_regiao_da_imagem_vira_pixels_reais(self):
        t = self.tela_com_mapa()
        self.assertEqual(t.regiao_real([10, 20, 100, 60]), [120, 90, 200, 120])  # x = 100 + 10 / 0.5
        self.assertEqual(t.regiao_real([10, 20, 100, 60], "tela"), [10, 20, 100, 60])
        self.assertEqual(self.tela_mod.Tela().regiao_real([10, 20, 100, 60]), [10, 20, 100, 60])  # sem captura antes
        self.assertIsNone(t.regiao_real(None))
        for ruim in ([1, 2, 3], "abc", [0, 0, 4, 100]):
            with self.assertRaises(ValueError):
                t.regiao_real(ruim)

    def test_captura_de_regiao_manda_pixels_reais_e_refaz_o_mapa_de_cliques(self):
        t = self.tela_com_mapa()
        r = t.capturar(regiao=[10, 20, 100, 60], largura=320)
        self.assertEqual(self.chamadas[-1][1]["regiao"], [120, 90, 200, 120])
        self.assertIn("_imagem", r)
        # o mapa agora é o da região: um clique em (50, 30) da imagem cai em 120 + 50/escala, 90 + 30/escala
        self.assertEqual((t.ultima["x"], t.ultima["y"]), (120, 90))
        x, y = t.para_tela(50, 30)
        self.assertEqual((x, y), (120 + round(50 / t.ultima["escala"]), 90 + round(30 / t.ultima["escala"])))

    def test_montagem_junta_os_momentos_e_nao_mexe_no_mapa_de_cliques(self):
        t = self.tela_com_mapa()
        antes = dict(t.ultima)
        r = t.capturar(quadros=4, intervalo=50)  # 50 ms é pouco: o agente sobe para 100
        dados = self.chamadas[-1][1]
        self.assertEqual((dados["quadros"], dados["colunas"], dados["intervalo"]), (4, 2, 100))
        self.assertEqual(r["montagem"]["tempos_s"], [0.0, 0.1, 0.2, 0.3])
        self.assertEqual(r["montagem"]["linhas"], 2)
        self.assertIn("_imagem", r)
        self.assertEqual(t.ultima, antes)

    def test_montagem_longa_demais_e_recusada_e_o_tempo_de_espera_acompanha(self):
        t = self.tela_mod.Tela()
        with self.assertRaises(ValueError):
            t.capturar(quadros=12, intervalo=5000)  # 55 s
        self.assertEqual(self.chamadas, [])
        t.capturar(quadros=5, intervalo=1000)  # 4 s de captura
        self.assertGreaterEqual(self.chamadas[-1][2], 64)

    def test_pc_entrada_com_ver_devolve_a_tela_no_mesmo_passo(self):
        f = Ferramentas(Path(tempfile.mkdtemp()), lambda r: None, lambda: {}, lambda m: None)
        r = f.pc_entrada("clicar", x=10, y=20, coordenadas="tela")
        self.assertEqual(r["feito"], "clicar")
        self.assertNotIn("_imagem", r)  # sem ver, é só o clique, como antes
        r = f.pc_entrada("clicar", x=10, y=20, coordenadas="tela", ver=True, espera=0)
        self.assertEqual(r["feito"], "clicar")
        self.assertIn("_imagem", r)
        self.assertEqual(r["cursor_agora"], "10 20")
        r = f.pc_entrada("teclas", teclas="{ENTER}", ver=True, espera=0, quadros=3, intervalo=100)
        self.assertEqual(r["montagem"]["quadros"], 3)

    def test_ferramentas_anunciam_as_opcoes_novas(self):
        defs = {d["name"]: d["inputSchema"]["properties"] for d in ferr_mod.DEFINICOES}
        for campo in ("regiao", "quadros", "intervalo", "colunas"):
            self.assertIn(campo, defs["pc_tela"])
            self.assertIn(campo, defs["pc_entrada"])
        self.assertIn("ver", defs["pc_entrada"])
        self.assertIn("espera", defs["pc_entrada"])
        self.assertEqual(defs["pc_tela"]["regiao"]["minItems"], 4)

    def test_resposta_do_servidor_anexa_a_imagem_da_montagem(self):
        from agente_pc.servidor import _resultado
        r = _resultado({"montagem": {"quadros": 2}, "_imagem": {"base64": "QUJD", "mime": "image/jpeg"}}, False)
        self.assertEqual([c["type"] for c in r["content"]], ["text", "image"])
        self.assertIn("imagem_anexada", r["content"][0]["text"])


if __name__ == "__main__":
    unittest.main()
