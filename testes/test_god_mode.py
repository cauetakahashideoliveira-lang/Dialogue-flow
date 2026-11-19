"""Testes da skill god-mode (.claude/skills/god-mode/god_mode.py), adaptação do G0DM0D3.

Sem rede: as chamadas de modelo vão para um servidor falso compatível com a API da OpenAI em 127.0.0.1.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import tempfile
import threading
import time
import unittest
from contextlib import redirect_stderr, redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("god_mode", RAIZ / ".claude" / "skills" / "god-mode" / "god_mode.py")
gm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gm)

RESPOSTA_BOA = ("## Configurar o ngrok no Termux\n- instale o ngrok\n- configure o token do ngrok\n"
                "- rode o túnel no Termux\n```bash\nngrok http 8080\n```\n")


class _Servidor(BaseHTTPRequestHandler):
    """Imita /v1/models, /v1/key e /v1/chat/completions com modelos de comportamento conhecido."""

    def log_message(self, *a):  # silencioso
        pass

    def _responder(self, status, dados, cab=None):
        corpo = json.dumps(dados).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        for k, v in (cab or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        srv = self.server
        if self.path.endswith("/models"):
            self._responder(200, {"data": [{"id": m, "pricing": srv.precos.get(m, {"prompt": "0.0000001", "completion": "0.0000002"})}
                                           for m in srv.modelos]})
        elif self.path.endswith("/key"):
            if self.headers.get("Authorization") == "Bearer chave-certa":
                self._responder(200, {"data": {"label": "teste"}})
            else:
                self._responder(401, {"error": {"message": "No auth credentials found", "code": 401}})
        else:
            self._responder(404, {"error": "não existe"})

    def do_POST(self):
        srv = self.server
        tamanho = int(self.headers.get("Content-Length") or 0)
        corpo = json.loads(self.rfile.read(tamanho) or b"{}")
        with srv.trava:
            srv.pedidos.append({"corpo": corpo, "auth": self.headers.get("Authorization")})
        modelo = corpo.get("model")
        if modelo == "lento":
            time.sleep(4)
        if modelo == "medio":
            time.sleep(0.3)
        if modelo == "quebrado":
            return self._responder(500, {"error": {"message": "falha interna"}})
        if modelo == "limite":
            with srv.trava:
                srv.vezes_limite += 1
                primeira = srv.vezes_limite == 1
            if primeira:
                return self._responder(429, {"error": {"message": "devagar"}}, {"Retry-After": "0"})
        conteudo = {"recusa": "I'm sorry, but I can't help with that request about the termux setup.",
                    "vazio": ""}.get(modelo, RESPOSTA_BOA)
        self._responder(200, {"choices": [{"message": {"role": "assistant", "content": conteudo}}]})


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"GOD_MODE_DIR": self.tmp.name}, clear=False)
        self.env.start()
        for v in ("OPENROUTER_API_KEY", "GOD_MODE_LOCAL_KEY", "GOD_MODE_LOCAL_URL", "GOD_MODE_OPENROUTER_URL",
                  "GOD_MODE_MODELO"):
            os.environ.pop(v, None)

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def rodar(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            codigo = gm.main(list(argv))
        return codigo, out.getvalue(), err.getvalue()


class _ComServidor(_Base):
    def setUp(self):
        super().setUp()
        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), _Servidor)
        self.srv.daemon_threads = True
        self.srv.modelos = ["rapido", "medio", "quebrado", "recusa", "lento", "limite", "vazio"]
        self.srv.precos = {}
        self.srv.pedidos = []
        self.srv.vezes_limite = 0
        self.srv.trava = threading.Lock()
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.srv.server_address[1]}/v1"

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()
        super().tearDown()


class TestGodModeAutoTune(_Base):
    def test_codigo_em_ingles(self):
        r = gm.autotune("Fix this python function, it throws a TypeError")
        self.assertEqual(r["contexto"], "code")
        self.assertEqual(r["params"]["temperature"], 0.15)
        self.assertFalse(r["portugues"])

    def test_padroes_em_portugues(self):
        r = gm.autotune("calcule a probabilidade de tirar dois seis em dois dados")
        self.assertTrue(r["portugues"])
        self.assertEqual(r["contexto"], "mathematical")
        # sem os padrões em português (comportamento do original) nada casa: conversa com 50%
        r0 = gm.autotune("calcule a probabilidade de tirar dois seis em dois dados", portugues=False)
        self.assertEqual(r0["contexto"], "conversational")
        self.assertEqual(r0["confianca"], 0.5)

    def test_sem_padrao_mistura_com_balanced(self):
        r = gm.autotune("zzz qqq www eee rrr ttt yyy uuu iii ooo")
        self.assertEqual(r["contexto"], "conversational")
        self.assertAlmostEqual(r["params"]["temperature"], 0.725)  # 0,75 e 0,70 meio a meio

    def test_estrategia_fixa_e_ajuste_manual_com_limite(self):
        r = gm.autotune("qualquer coisa", estrategia="precise")
        self.assertEqual(r["params"], gm.limitar(gm.ESTRATEGIAS["precise"]))
        r = gm.autotune("qualquer coisa", ajustes={"temperature": 5, "top_k": 500})
        self.assertEqual(r["params"]["temperature"], 2.0)
        self.assertEqual(r["params"]["top_k"], 100)
        with self.assertRaises(gm.Erro):
            gm.autotune("x", ajustes={"inexistente": 1})

    def test_conversa_longa_aumenta_repeticao(self):
        historico = [{"role": "user", "content": "zzz"}] * 15
        r = gm.autotune("zzz qqq www eee rrr ttt yyy uuu iii ooo", historico)
        self.assertAlmostEqual(r["params"]["repetition_penalty"], gm.limitar(
            gm.mesclar(gm.PERFIS["conversational"], gm.ESTRATEGIAS["balanced"], 0.5))["repetition_penalty"] + 0.05)

    def test_vinte_contextos(self):
        self.assertEqual(len(gm.CONTEXTOS), 20)
        self.assertEqual(set(gm.CONTEXTOS), set(gm.PERFIS))


class TestGodModeAprendizado(_Base):
    def test_tres_notas_boas_puxam_a_temperatura(self):
        estado = gm.estado_inicial()
        baixo = dict(gm.NEUTRO, temperature=0.1)
        for _ in range(3):
            estado = gm.registrar_nota(estado, {"contextType": "code", "rating": 1, "params": baixo})
        perfil = estado["learnedProfiles"]["code"]
        self.assertIn("temperature", perfil["adjustments"])
        r = gm.autotune("Fix this python function", aprendizado=estado["learnedProfiles"])
        self.assertLess(r["params"]["temperature"], 0.15)
        self.assertIn("aprendido", r["motivo"])
        # com duas notas ainda não aplica (mínimo de 3)
        e2 = gm.estado_inicial()
        for _ in range(2):
            e2 = gm.registrar_nota(e2, {"contextType": "code", "rating": 1, "params": baixo})
        self.assertEqual(gm.autotune("Fix this python function", aprendizado=e2["learnedProfiles"])["params"]["temperature"], 0.15)

    def test_heuristica_de_repeticao(self):
        self.assertGreater(gm.heuristicas("a b c " * 20)["repetitionScore"], 0.5)
        self.assertEqual(gm.heuristicas("cada palavra aqui aparece somente uma vez mesmo")["repetitionScore"], 0)

    def test_nota_pela_linha_de_comando(self):
        codigo, _, _ = self.rodar("autotune", "Fix this python function")
        self.assertEqual(codigo, 0)
        for _ in range(3):
            codigo, saida, _ = self.rodar("nota", "+1")
            self.assertEqual(codigo, 0)
        self.assertIn("já usa o aprendizado", saida)
        codigo, saida, _ = self.rodar("nota", "-1", "--modelo", "x")  # -1 com opção depois
        self.assertEqual(codigo, 0)
        codigo, saida, _ = self.rodar("aprendizado", "--json")
        self.assertEqual(json.loads(saida)["contextos"]["code"]["total"], 4)


class TestGodModeStmEPontuacao(unittest.TestCase):
    def test_hesitacao(self):
        self.assertEqual(gm.stm_hesitacao("I think the answer is 42."), "The answer is 42.")
        self.assertEqual(gm.stm_hesitacao("Eu acho que a resposta é 42."), "A resposta é 42.")
        self.assertEqual(gm.stm_hesitacao("It will maybe rain."), "It will rain.")
        # não mexe em linhas que não tiveram remoção (o original capitalizava toda linha)
        self.assertEqual(gm.stm_hesitacao("x = 1\n  return x"), "x = 1\n  return x")

    def test_direto_e_casual(self):
        self.assertEqual(gm.stm_direto("Sure, here it is"), "Here it is")
        self.assertEqual(gm.stm_direto("Surely not"), "Surely not")
        self.assertEqual(gm.stm_direto("Claro! Aqui está."), "Aqui está.")
        self.assertEqual(gm.stm_casual("However, we must utilize it"), "But, we must use it")
        self.assertEqual(gm.stm_casual("Entretanto, vamos utilizar"), "Mas, vamos usar")
        self.assertEqual(gm.resolver_modulos("hesitacao, direto,casual"), ["hedge_reducer", "direct_mode", "casual_mode"])
        with self.assertRaises(gm.Erro):
            gm.resolver_modulos("parseltongue")

    def test_pontuacao_neutra(self):
        boa = gm.pontuar(RESPOSTA_BOA, "como configurar o ngrok no termux")
        curta = gm.pontuar("Sim.", "como configurar o ngrok no termux")
        recusa = gm.pontuar("I'm sorry, but I can't help with configuring ngrok in termux right now.",
                            "como configurar o ngrok no termux")
        self.assertGreater(boa["pontos"], 40)
        self.assertEqual(curta["pontos"], 0)
        self.assertTrue(recusa["possivel_recusa"])
        self.assertFalse(boa["possivel_recusa"])
        self.assertLessEqual(boa["pontos"], 100)
        # a recusa não perde pontos por ser recusa (só os critérios neutros contam)
        sem_recusa = gm.pontuar("Right now nothing will help with configuring ngrok in termux, sadly.",
                                "como configurar o ngrok no termux")
        self.assertLessEqual(abs(recusa["pontos"] - sem_recusa["pontos"]), 2)


class TestGodModeModelos(_ComServidor):
    def test_corrida_com_minimo_espera_e_erros(self):
        os.environ["GOD_MODE_LOCAL_KEY"] = "chave-teste"
        cfg = gm.provedor("local", self.url)
        params = gm.autotune("como configurar o ngrok no termux")["params"]
        inicio = time.monotonic()
        res, pend = gm.corrida(cfg, ["rapido", "medio", "quebrado", "recusa", "lento", "limite"],
                               [{"role": "user", "content": "como configurar o ngrok no termux"}], params,
                               min_resultados=3, espera_extra=0.5, limite_total=3.0, timeout_modelo=10)
        self.assertLess(time.monotonic() - inicio, 3.5)
        self.assertEqual(pend, ["lento"])
        por = {r["modelo"]: r for r in res}
        self.assertTrue(por["rapido"]["sucesso"])
        self.assertTrue(por["limite"]["sucesso"])  # repetiu depois do 429
        self.assertFalse(por["quebrado"]["sucesso"])
        self.assertIn("HTTP 500", por["quebrado"]["erro"])
        pedido = next(p for p in self.srv.pedidos if p["corpo"]["model"] == "rapido")
        self.assertEqual(pedido["auth"], "Bearer chave-teste")
        for k in gm.PARAMS:
            self.assertIn(k, pedido["corpo"])

    def test_comparar_pela_linha_de_comando(self):
        os.environ["GOD_MODE_LOCAL_KEY"] = "chave-secreta-teste"
        codigo, saida, err = self.rodar("comparar", "como configurar o ngrok no termux", "--provedor", "local",
                                        "--base-url", self.url, "--modelos", "rapido,recusa,quebrado,vazio",
                                        "--min-resultados", "2", "--espera", "0.3", "--limite", "5")
        self.assertEqual(codigo, 0, err)
        self.assertNotIn("chave-secreta-teste", saida + err)
        self.assertIn("Respostas completas:", saida)
        arquivo = Path(saida.split("Respostas completas: ")[1].splitlines()[0])
        dados = json.loads(arquivo.read_text(encoding="utf-8"))
        self.assertEqual(dados["respostas"][0]["modelo"], "rapido")
        self.assertTrue(next(r for r in dados["respostas"] if r["modelo"] == "recusa")["pontuacao"]["possivel_recusa"])
        self.assertEqual({f["modelo"] for f in dados["falhas"]}, {"quebrado", "vazio"})
        self.assertNotIn("chave-secreta-teste", arquivo.read_text(encoding="utf-8"))
        codigo, saida, _ = self.rodar("nota", "bom")
        self.assertEqual(codigo, 0)
        self.assertIn("rapido", json.loads((Path(self.tmp.name) / "feedback.json").read_text())["history"][0]["model"])

    def test_perguntar_local_com_stm(self):
        codigo, saida, err = self.rodar("perguntar", "como configurar o ngrok no termux", "--provedor", "local",
                                        "--base-url", self.url, "--modelo", "rapido", "--stm", "casual", "--json")
        self.assertEqual(codigo, 0, err)
        dados = json.loads(saida)
        self.assertEqual(dados["modelo"], "rapido")
        self.assertIn("ngrok", dados["resposta"])

    def test_openrouter_sem_chave_nao_envia_pedido(self):
        os.environ["GOD_MODE_OPENROUTER_URL"] = self.url
        codigo, _, err = self.rodar("perguntar", "pergunta que não pode sair daqui", "--modelo", "rapido")
        self.assertEqual(codigo, 2)
        self.assertIn("OPENROUTER_API_KEY", err)
        self.assertEqual(self.srv.pedidos, [])  # nada foi para /chat/completions

    def test_openrouter_orcamento(self):
        os.environ["GOD_MODE_OPENROUTER_URL"] = self.url
        os.environ["OPENROUTER_API_KEY"] = "chave-certa"
        self.srv.precos["rapido"] = {"prompt": "0.001", "completion": "0.002"}  # caro de propósito
        codigo, _, err = self.rodar("comparar", "oi", "--modelos", "rapido,medio")
        self.assertEqual(codigo, 3)
        self.assertIn("orçamento", err)
        self.assertEqual(self.srv.pedidos, [])
        codigo, saida, err = self.rodar("comparar", "oi", "--modelos", "medio,inexistente", "--min-resultados", "1",
                                        "--espera", "0.1")
        self.assertEqual(codigo, 0, err)
        self.assertIn("Fora do catálogo atual (pulados): inexistente", saida)

    def test_status_com_servidor_local(self):
        os.environ["GOD_MODE_LOCAL_URL"] = self.url
        os.environ["GOD_MODE_OPENROUTER_URL"] = self.url
        codigo, saida, _ = self.rodar("status", "--json")
        self.assertEqual(codigo, 0)
        info = json.loads(saida)
        self.assertIn("rapido", info["local"]["modelos"])
        self.assertIn("comparar", info["disponivel"])
        self.assertEqual(info["openrouter"]["autenticacao"], "sem autenticação")


if __name__ == "__main__":
    unittest.main()
