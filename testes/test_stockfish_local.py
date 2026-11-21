"""Atalho de estudo e ciclo de vida do pedido local."""
import io
import json
import sys
import tempfile
import threading
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, call, patch
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "controle-ir"))
from controle_ir import cli, estudo_xadrez, servidor
from controle_ir.capacidades import modulo_embutido


class TestStockfishLocal(unittest.TestCase):
    def test_historico_indica_vez_mesmo_no_meio_da_partida(self):
        tela = modulo_embutido(ROOT / "controle-ir/capacidades/tela", "tela")
        def linha(*textos):
            return [{"texto": texto, "x": x * 100, "y": 400} for x, texto in enumerate(textos)]
        self.assertEqual(tela.vez_no_historico(linha("cxd4", "4.", "nxd4", "Nf6")), "w")
        self.assertEqual(tela.vez_no_historico(linha("9.", "O-O", "e5", "10.", "exd6")), "b")
        self.assertIsNone(tela.vez_no_historico(linha("4.", "Opções")))
        self.assertIsNone(tela.vez_no_historico(linha("0:46", "0:55")))

    def test_perder_foco_antes_do_toque_espera_e_retoma(self):
        tela = modulo_embutido(ROOT / "controle-ir/capacidades/tela", "tela")
        m = tela._modulo_piloto()
        casas = {f"{c}{r}": (x, 8-r, m.INICIAL[(8-r)*8+x].replace(".", ""))
                 for r in range(1, 9) for x, c in enumerate("abcdefgh")}
        foco = threading.Event()
        foco.set()
        interrompido = threading.Event()
        jogou = threading.Event()
        toques = []
        def tocar(x, y):
            toques.append((x, y, foco.is_set()))
            if len(toques) == 2:
                jogou.set()
        def decidir(*_):
            if not interrompido.is_set():
                foco.clear()
                interrompido.set()
            return "e2e4"
        motor = Mock()
        motor.lance.side_effect = decidir
        motor.tab_apos.return_value = m.INICIAL
        piloto = m.Piloto({"tabuleiro_local": foco.is_set, "vez": lambda: None,
                           "aguardar": lambda c, ms: c, "casas": lambda: casas, "tocar": tocar})
        with patch.object(m, "Motor", return_value=motor):
            try:
                piloto.iniciar({"modo":"xadrez", "app":"com.chess", "tabuleiro_local":True, "cerebros":["memoria"]})
                self.assertTrue(interrompido.wait(2))
                limite = time.monotonic() + 2
                while "aguardando o tabuleiro" not in piloto.estado_txt and time.monotonic() < limite:
                    time.sleep(0.01)
                self.assertTrue(piloto.rodando)
                self.assertEqual(toques, [])
                foco.set()
                self.assertTrue(jogou.wait(3))
                self.assertEqual(toques[:2], [(4, 6, True), (4, 4, True)])
            finally:
                piloto.encerrar()

    def test_atalho_interativo(self):
        with tempfile.TemporaryDirectory() as d, patch.object(cli, "pasta_atalhos", return_value=Path(d)/".shortcuts/tasks"):
            for _ in range(2):
                self.assertEqual(cli.criar_atalhos(True), 0)
            arq = Path(d)/".shortcuts/Stockfish"
            self.assertEqual(arq.stat().st_mode & 0o777, 0o700)
            self.assertTrue(arq.read_text().rstrip().endswith('controle-ir" stockfish'))
            self.assertFalse((arq.parent/"tasks/Stockfish").exists())

    def test_falha_no_segundo_lance_conserva_posicao(self):
        motor = Mock()
        motor.lance.return_value = "e2e4"
        motor.fen_apos_lance_legal.side_effect = ["fen intermediária", None]
        with patch("builtins.input",side_effect=["e2e4 e2e9","","sair"]), redirect_stdout(io.StringIO()):
            estudo_xadrez.estudar(motor)
        self.assertEqual(motor.lance.call_args.args[0], estudo_xadrez.INICIAL)

    def test_configurar_no_terminal_e_no_estudo_preserva_posicao(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(cli, "PASTA", Path(tmp)), redirect_stdout(io.StringIO()):
            self.assertEqual(estudo_xadrez.ler_preferencias(cli.PASTA), estudo_xadrez.Preferencias())
            with patch("builtins.input", side_effect=["21", "0", "nan", "0,001", "0,05"]):
                self.assertEqual(cli.main(["stockfish", "configurar"]), 0)
            posicao = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
            motor = Mock()
            motor.fen_apos_lance_legal.return_value = posicao
            with patch("builtins.input", side_effect=["e2e4", "configurar", "20", "1,5", "", "sair"]):
                self.assertEqual(estudo_xadrez.estudar(motor), "sair")
            self.assertEqual(motor.definir_nivel.call_args_list, [call(0), call(20)])
            self.assertEqual(motor.lance.call_args_list, [call(estudo_xadrez.INICIAL, 50), call(posicao, 1500)])
            with patch("builtins.input", side_effect=["", ""]):
                self.assertEqual(estudo_xadrez.configurar(cli.PASTA), estudo_xadrez.Preferencias(20, 1500))
            with patch("builtins.input", side_effect=["1", "31", "30"]):
                self.assertEqual(estudo_xadrez.configurar(cli.PASTA), estudo_xadrez.Preferencias(1, 30000))
            with patch("builtins.input", side_effect=["5", EOFError()]):
                self.assertEqual(cli.main(["stockfish", "configurar"]), 0)
            self.assertEqual(estudo_xadrez.ler_preferencias(cli.PASTA), estudo_xadrez.Preferencias(1, 30000))
            with patch("builtins.input", side_effect=["", "auto"]):
                self.assertEqual(estudo_xadrez.configurar(cli.PASTA), estudo_xadrez.Preferencias(1))

    def test_nivel_uci_e_tempo_do_piloto_no_fim_da_partida(self):
        tela = modulo_embutido(ROOT / "controle-ir/capacidades/tela", "tela")
        m = tela._modulo_piloto()
        with patch.object(m.Motor, "_mandar") as enviar:
            m.Motor.definir_nivel(object.__new__(m.Motor), 0)
            enviar.assert_called_once_with("setoption name Skill Level value 0")
        casas = {f"{c}{r}": (x, 8-r, m.INICIAL[(8-r)*8+x].replace(".", ""))
                 for r in range(1, 9) for x, c in enumerate("abcdefgh")}
        for rodadas, fixo, esperado in [(0, True, 1500), (30, True, 1500), (50, True, 1500),
                                         (0, False, 1500), (30, False, 750), (50, False, 100)]:
            with self.subTest(rodadas=rodadas, fixo=fixo), patch.object(m, "Motor") as fabrica:
                piloto = m.Piloto({"tabuleiro_local": lambda: True, "casas": lambda: casas,
                                   "aguardar": lambda c, ms: c})
                piloto.cfg = {"nivel": 0, "ms_lance": 1500, "tempo_fixo": fixo, "tabuleiro_local": True}
                piloto.rodadas.extend([{}] * rodadas)
                motor = fabrica.return_value
                motor.lance.return_value = None
                piloto._laco_xadrez()
                motor.definir_nivel.assert_called_once_with(0)
                motor.lance.assert_called_once_with(estudo_xadrez.INICIAL, esperado)

    def test_pedido_cancelado_nao_inicia_e_outro_piloto_nao_e_interrompido(self):
        with tempfile.TemporaryDirectory() as pasta, patch.object(servidor,"ServidorMCP") as mcp:
            srv = servidor.criar_servidor(Mock(pasta=Path(pasta)), "teste", porta=0, token_local="local")
            th = threading.Thread(target=srv.serve_forever, daemon=True)
            th.start()
            def post(acao, **dados):
                url = f"http://127.0.0.1:{srv.server_port}/api/stockfish?t=local"
                with urlopen(Request(url,data=json.dumps(dict(acao=acao,**dados)).encode()),timeout=3) as r:
                    return json.load(r)
            try:
                ident = post("preparar")["pedido"]
                chamada = mcp.return_value.chamar
                chamada.return_value = {"structuredContent":{"resultado":{"rodando":True,"cfg":{"modo":"quiz"}}}}
                self.assertIn("Outro piloto",post("parar")["mensagem"])
                self.assertIn("cancelado",post("iniciar",pedido=ident)["mensagem"])
                chamada.assert_called_once_with("cap_tela",{"acao":"piloto"})
                ident = post("preparar")["pedido"]
                chamada.return_value = {"structuredContent":{"erro":"bloqueado"}}
                self.assertEqual(post("iniciar",pedido=ident),{"erro":"bloqueado"})
                (Path(pasta) / estudo_xadrez.ARQUIVO).write_text('{"nivel": 0, "ms_lance": 1250}')
                chamada.side_effect = [{"structuredContent":{"resultado":{"rodando":False}}},
                                       {"structuredContent":{"resultado":{"rodando":True}}}]
                post("iniciar", pedido=ident)
                cfg = chamada.call_args.args[1]["iniciar"]
                self.assertEqual((cfg["nivel"], cfg["ms_lance"], cfg["tempo_fixo"]), (0, 1250, True))
            finally:
                srv.shutdown()
                srv.server_close()
                th.join()


if __name__ == "__main__":
    unittest.main()
