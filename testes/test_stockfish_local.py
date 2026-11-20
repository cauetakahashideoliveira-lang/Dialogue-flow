"""Atalho de estudo e ciclo de vida do pedido local."""
import io
import json
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "controle-ir"))
from controle_ir import cli, estudo_xadrez, servidor


class TestStockfishLocal(unittest.TestCase):
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
            finally:
                srv.shutdown()
                srv.server_close()
                th.join()


if __name__ == "__main__":
    unittest.main()
