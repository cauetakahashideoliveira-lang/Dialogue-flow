"""Capacidade ps4: linguagem de comandos, jogador que aprende e a cola (sem console: conexão de mentira)."""
import importlib.util
import json
import os
import random
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA_CAP = RAIZ / "controle-ir" / "capacidades" / "ps4"
sys.path.insert(0, str(RAIZ / "controle-ir"))

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None


def _mod(nome, arquivo):
    spec = importlib.util.spec_from_file_location(nome, PASTA_CAP / arquivo)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


controle = _mod("ps4_controle_teste", "controle.py")


class Gravador:
    def __init__(self):
        self.ev = []

    def apertar(self, b):
        self.ev.append(("p", b))

    def soltar(self, b):
        self.ev.append(("s", b))

    def analogico(self, l, x, y):
        self.ev.append(("a", l, round(x, 3), round(y, 3)))


class TestComandos(unittest.TestCase):
    def test_apelidos_e_texto(self):
        self.assertEqual(controle.botao("bola"), "CIRCLE")
        self.assertEqual(controle.botao("Triângulo"), "TRIANGLE")
        self.assertEqual(controle.botao("r2"), "R2")
        with self.assertRaises(controle.ErroComando):
            controle.botao("pular")
        atom = controle.normalizar("x r2:600 esperar:300 l1+r1")
        self.assertEqual(atom[0], ("apertar", "CROSS"))
        self.assertIn(("esperar", 0.6), atom)
        self.assertIn(("esperar", 0.3), atom)
        self.assertEqual([a for a in atom if a[0] == "apertar"][-2:], [("apertar", "L1"), ("apertar", "R1")])

    def test_angulo_repetir_habilidade(self):
        x, y = controle.ponto({"angulo": 90, "forca": 1})
        self.assertAlmostEqual(x, 0, places=3)
        self.assertAlmostEqual(y, -1, places=3)  # 90° = cima = y negativo no PS4
        hs = {"pular": {"passos": [{"botao": "x", "ms": 50}]}}
        atom = controle.normalizar([{"repetir": 3, "passos": [{"habilidade": "pular"}]}], hs)
        self.assertEqual(sum(1 for a in atom if a == ("apertar", "CROSS")), 3)
        self.assertAlmostEqual(controle.duracao(atom), 0.15)
        with self.assertRaises(controle.ErroComando):
            controle.normalizar([{"habilidade": "voar"}], hs)

    def test_executar_segura_e_solta(self):
        g = Gravador()
        atom = controle.normalizar([{"segurar": "r2"}, {"analogico": "esquerdo", "x": 1, "y": 0, "ms": 10},
                                    {"botao": "quadrado", "ms": 0}])
        r = controle.executar(atom, g, dormir=lambda s: None)
        self.assertEqual(r["segurando"], ["R2"])  # segurar sem soltar continua preso para o próximo comando
        self.assertEqual(g.ev[1], ("a", "left", 1.0, 0.0))
        self.assertEqual(g.ev[2], ("a", "left", 0.0, 0.0))  # com ms volta ao centro
        g2 = Gravador()
        r2 = controle.executar(atom, g2, dormir=lambda s: None, parar=lambda: len(g2.ev) >= 2)
        self.assertTrue(r2["interrompido"])
        self.assertIn(("s", "R2"), g2.ev)  # interrompido: solta tudo e centraliza
        self.assertIn(("a", "left", 0.0, 0.0), g2.ev)


@unittest.skipIf(np is None, "numpy ausente")
class TestJogador(unittest.TestCase):
    def setUp(self):
        self.jog = _mod("ps4_jogador_teste", "jogador.py")
        self.pasta = tempfile.mkdtemp(prefix="ps4-")

    def test_recompensa_barra(self):
        a = np.zeros((90, 160, 3), dtype=np.uint8)
        b = a.copy()
        b[0:9, 0:80] = [0, 255, 0]  # barra verde enche metade da região
        det = [{"tipo": "barra", "regiao": [0, 0, 1, 0.1], "cor": [0, 255, 0], "peso": 2, "nome": "vida"}]
        r, d = self.jog.recompensa(a, b, det)
        self.assertAlmostEqual(r, 1.0, places=2)
        self.assertAlmostEqual(d["vida"], 1.0, places=2)
        r2, _ = self.jog.recompensa(a, b, [{"tipo": "cor_aparece", "regiao": [0, 0, 0.5, 0.1], "cor": [0, 255, 0]}])
        self.assertEqual(r2, 1.0)

    def test_aprende_a_melhor_habilidade_por_situacao(self):
        """Jogo de mentira: tela vermelha pede 'atacar', tela azul pede 'defender'. O jogador descobre sozinho."""
        random.seed(3)
        tela = {"cor": "vermelha", "vida": 40}

        def olhar():
            q = np.zeros((90, 160, 3), dtype=np.uint8)
            q[20:, :] = [220, 30, 30] if tela["cor"] == "vermelha" else [30, 30, 220]
            q[0:9, :tela["vida"]] = [0, 255, 0]
            return q

        def agir(h):
            certo = (tela["cor"] == "vermelha") == (h == "atacar")
            tela["vida"] = max(8, min(152, tela["vida"] + (8 if certo else -8)))
            tela["cor"] = random.choice(["vermelha", "azul"])

        det = [{"tipo": "barra", "regiao": [0, 0, 1, 0.1], "cor": [0, 255, 0], "nome": "vida"}]
        j = self.jog.Jogador(self.pasta, "teste", ["atacar", "defender"], det, gama=0.0)
        for _ in range(250):
            j.passo(olhar, agir)
        pol = j.relatorio()["politica"]
        tela["cor"] = "vermelha"
        s_verm = j.estados.atribuir(self.jog.reduzir(olhar()), aprender=False)
        tela["cor"] = "azul"
        s_azul = j.estados.atribuir(self.jog.reduzir(olhar()), aprender=False)
        self.assertNotEqual(s_verm, s_azul)
        self.assertEqual(pol[s_verm]["melhor"], "atacar")
        self.assertEqual(pol[s_azul]["melhor"], "defender")
        # sem explorar, acerta quase sempre
        acertos = 0
        for _ in range(60):
            cor = tela["cor"]
            r = j.passo(olhar, agir, explorar=False)
            acertos += (r["habilidade"] == "atacar") == (cor == "vermelha")
        self.assertGreaterEqual(acertos, 57)
        # memória em disco: um jogador novo do mesmo jogo continua de onde parou
        j.salvar()
        j2 = self.jog.Jogador(self.pasta, "teste", ["atacar", "defender"], None)
        self.assertEqual(j2.passos_total, j.passos_total)
        self.assertEqual(j2.cerebro.politica(len(j2.estados.prot))[s_verm]["melhor"], "atacar")

    def test_demonstracao_e_nota(self):
        j = self.jog.Jogador(self.pasta, "demo", ["a", "b"], [])
        q = np.full((90, 160, 3), 128, dtype=np.uint8)
        s = j.demonstrar(q, "b")
        for _ in range(3):
            j.demonstrar(q, "b")
        self.assertEqual(j.cerebro.escolher(s, explorar=False), "b")
        j.ultimos = [(s, "b", 0.0)]
        j.nota(-5, 1)
        self.assertLess(j.cerebro.valor(s, "b"), 0)


class TestConexaoLaco(unittest.TestCase):
    def test_funcao_sincrona_roda_dentro_do_laco(self):
        """A pyremoteplay chama asyncio.get_event_loop() ao ler o estado do PS4; numa thread do serviço isso
        quebrava ("There is no current event loop"). _sync roda dentro do laço da conexão."""
        import asyncio
        import threading
        con = _mod("ps4_conexao_teste", "conexao.py").Conexao(tempfile.mkdtemp(prefix="ps4c-"))

        def le_estado():
            asyncio.ensure_future(asyncio.sleep(0))  # o que a biblioteca faz em _set_status
            return asyncio.get_event_loop().is_running()

        out = {}
        th = threading.Thread(target=lambda: out.update(r=con._sync(le_estado)))
        th.start()
        th.join(5)
        self.assertTrue(out["r"])
        con.loop.call_soon_threadsafe(con.loop.stop)


class TestCompatPyAV(unittest.TestCase):
    def test_decodifica_h264_com_pyav_novo(self):
        """A pyremoteplay usa Flags.LOW_DELAY (PyAV antigo); no PyAV 14+ isso quebrava a abertura do vídeo."""
        try:
            import av
            from pyremoteplay.receiver import AVReceiver
        except Exception:  # noqa: BLE001
            raise unittest.SkipTest("pyremoteplay/av ausentes")
        _mod("ps4_conexao_compat", "conexao.py").compat_av()
        try:
            enc = av.CodecContext.create("libx264", "w")
        except Exception:  # noqa: BLE001
            raise unittest.SkipTest("sem codificador H.264")
        enc.width, enc.height, enc.pix_fmt = 160, 96, "yuv420p"
        enc.options = {"tune": "zerolatency"}  # como o PS4: sem quadros B
        pacotes = []
        for i in range(6):
            img = np.zeros((96, 160, 3), np.uint8)
            img[:, :20 * (i + 1)] = [200, 50, 50]
            pacotes += enc.encode(av.VideoFrame.from_ndarray(img, format="rgb24").reformat(format="yuv420p"))
        pacotes += enc.encode(None)
        dec = AVReceiver.video_codec("h264")
        quadros = [q for q in (AVReceiver.video_frame(bytes(p), dec, "rgb24") for p in pacotes) if q is not None]
        self.assertGreaterEqual(len(quadros), 5)


class ConexaoFalsa(Gravador):
    conectado = True

    def quadro(self):
        return np.full((72, 128, 3), 90, dtype=np.uint8)

    def estado(self):
        return {"conectado": True}


@unittest.skipIf(np is None, "numpy ausente")
class TestPrincipal(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="ps4b-")
        os.environ["CONTROLE_IR_DIR"] = self.dir
        self.p = _mod("ps4_principal_teste", "principal.py")
        self.p.E.con = ConexaoFalsa()

    def tearDown(self):
        os.environ.pop("CONTROLE_IR_DIR", None)

    def test_habilidade_comando_quadro(self):
        r = self.p.executar({"acao": "habilidade", "modo": "salvar", "nome": "combo",
                             "passos": "quadrado quadrado triangulo:0", "descricao": "combo básico"})
        self.assertEqual(r["salva"], "combo")
        self.assertIn("combo", self.p.executar({"acao": "habilidade"})["habilidades"])
        r = self.p.executar({"acao": "comando", "passos": [{"habilidade": "combo"}, "x:0"]})
        self.assertEqual(r["feitos"], 12)
        self.assertEqual(self.p.E.con.ev[0], ("p", "SQUARE"))
        self.assertIn("erro", self.p.executar({"acao": "comando", "passos": "pular"}))
        img = self.p.executar({"acao": "quadro", "largura": 64})["_imagem"]
        dados = __import__("base64").b64decode(img["base64"])
        if img["mime"] == "image/png":
            self.assertTrue(dados.startswith(b"\x89PNG"))
            self.assertGreater(len(zlib.decompress(dados[41:-12])), 0)
        else:
            self.assertTrue(dados.startswith(b"\xff\xd8"))

    def test_jogador_preparar_detectores_relatorio(self):
        self.p.executar({"acao": "habilidade", "modo": "salvar", "nome": "a", "passos": "x:0"})
        r = self.p.executar({"acao": "jogador", "modo": "preparar", "jogo": "Teste 1",
                             "detectores": [{"tipo": "brilho", "regiao": [0, 0, 1, 1], "nome": "luz"}]})
        self.assertEqual(r["preparado"], "Teste 1")
        m = self.p.executar({"acao": "jogador", "modo": "detectores"})
        self.assertAlmostEqual(m["medidas_agora"]["luz"], 90 / 255, places=3)
        self.assertIn("erro", self.p.executar({"acao": "jogador", "modo": "preparar", "jogo": "x",
                                               "detectores": [{"tipo": "raio", "regiao": [0, 0, 1, 1]}]}))
        self.assertEqual(self.p.executar({"acao": "jogador", "modo": "relatorio"})["passos"], 0)

    def test_manifesto(self):
        m = json.loads((PASTA_CAP / "capacidade.json").read_text())
        self.assertTrue(m["em_processo"])
        self.assertEqual(m["efeito"], "acao")
        self.assertEqual(m["nome"], "ps4")

    def test_capacidade_ativa_no_servico(self):
        from controle_ir.emissor import EmissorSimulado
        from controle_ir.servico import Servico
        s = Servico(tempfile.mkdtemp(prefix="cir-"), EmissorSimulado())
        nomes = {c["nome"]: c["estado"] for c in s.capacidades()["capacidades"]}
        self.assertEqual(nomes.get("ps4"), "ativa")


if __name__ == "__main__":
    unittest.main()
