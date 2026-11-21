"""Capacidade bluetooth: o leitor Java (compilado e rodado contra imitações do Android) e a classificação."""
from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
CAP = RAIZ / "controle-ir" / "capacidades" / "bluetooth"
STUB = Path(__file__).resolve().parent / "android_stub"


def _carregar():
    spec = importlib.util.spec_from_file_location("cap_bluetooth_teste", CAP / "principal.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@unittest.skipUnless(shutil.which("javac") and shutil.which("java"), "sem JDK")
class TestLeitorJava(unittest.TestCase):
    """Compila Bluetooth.java com as imitações e roda os cenários do celular."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        fontes = [str(p) for p in STUB.rglob("*.java")] + [str(CAP / "java" / "controleir" / "Bluetooth.java")]
        c = subprocess.run(["javac", "-nowarn", "-source", "8", "-target", "8", "-d", cls.tmp, *fontes],
                           capture_output=True, text=True, timeout=180)
        cls.erro_compilar = None if c.returncode == 0 else c.stderr[-1500:]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def rodar(self, modo):
        self.assertIsNone(self.erro_compilar)
        r = subprocess.run(["java", f"-Dstub.modo={modo}", "-cp", self.tmp, "controleir.Bluetooth", "50", "ble"],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        return _carregar().ultima_linha_json(r.stdout), r.stderr

    def test_ligado_escuta_e_junta_por_endereco(self):
        out, err = self.rodar("ligado")
        self.assertIn("criado como com.android.shell uid 2000", err)  # identidade do shell (permissões)
        self.assertIn("stopScan", err)
        self.assertEqual(out["busca"], "ok")
        self.assertTrue(out["bluetooth_ligado"])
        prox = {d["endereco"]: d for d in out["proximos"]}
        self.assertEqual(len(prox), 3)
        airpods = prox["BB:00:00:00:00:01"]
        self.assertEqual((airpods["vezes"], airpods["rssi_max"]), (2, -58))
        self.assertEqual(airpods["fabricante"], [{"id": 0x004C, "dados": "071901"}])
        self.assertNotIn("nome", airpods)  # sem nome e sem permissão para o nome: não quebra
        self.assertEqual(sorted(prox["BB:00:00:00:00:02"]["servicos"]), ["fd6f", "fe2c"])
        self.assertEqual(prox["AA:AA:AA:AA:AA:01"]["nome"], 'JBL "Flip" 5')  # aspas escapadas no JSON
        self.assertEqual([p["nome"] for p in out["pareados"]], ["JBL Flip 5", "Redmi Watch"])

    def test_desligado_usa_modo_so_ble_e_desfaz(self):
        out, err = self.rodar("desligado_ble")
        self.assertEqual((out["busca"], out["bluetooth_ligado"], out["modo_so_ble"]), ("ok", False, True))
        self.assertLess(err.index("enableBLE"), err.index("disableBLE"))
        self.assertEqual(len(out["proximos"]), 3)

    def test_desligado_sem_modo_ble_avisa(self):
        out, _ = self.rodar("desligado")
        self.assertEqual(out["busca"], "bluetooth_desligado")
        self.assertNotIn("proximos", out)
        self.assertEqual(len(out["pareados"]), 2)

    def test_falha_da_busca_vem_com_codigo(self):
        out, _ = self.rodar("falha")
        self.assertEqual((out["busca"], out["codigo_falha"]), ("falhou", 2))


class TestClassificacao(unittest.TestCase):
    def setUp(self):
        self.m = _carregar()

    def test_por_nome(self):
        casos = {"Galaxy Buds2 Pro": "fone ou caixa de som", "Galaxy Watch6": "relógio ou pulseira",
                 "[TV] Samsung 7 Series": "TV ou streaming", "HONDA HFT": "carro", "iPhone de Ana": "celular",
                 "Mi Smart Band 8": "relógio ou pulseira", "Xbox Wireless Controller": "teclado, mouse ou controle",
                 "ESP32_sensor": "placa eletrônica (DIY)", "Nokia 3310": "desconhecido"}
        for nome, tipo in casos.items():
            self.assertEqual(self.m.classificar({"nome": nome})[0], tipo, nome)

    def test_por_anuncio(self):
        c = self.m.classificar
        self.assertEqual(c({"fabricante": [{"id": 0x004C, "dados": "1219"}]})[0], "rastreador")
        self.assertEqual(c({"fabricante": [{"id": 0x004C, "dados": "10"}]})[:2], ("celular", "Apple"))
        self.assertEqual(c({"fabricante": [{"id": 0x004C, "dados": "ff"}]})[0], "aparelho Apple")
        self.assertEqual(c({"fabricante": [{"id": 0x0006, "dados": "0109"}]})[0], "computador")
        self.assertEqual(c({"servicos": ["fd5a"]})[0], "rastreador")
        self.assertEqual(c({"fabricante": [{"id": 0x0157, "dados": ""}]})[0], "aparelho Huami")
        self.assertEqual(c({"classe_maior": 0x0400})[0], "fone ou caixa de som")
        self.assertEqual(c({}), ("desconhecido", None, None))

    def test_distancia(self):
        d = self.m.distancia
        self.assertEqual([d(-50), d(-65), d(-80), d(-95), d(None)],
                         ["muito perto (até ~1 m)", "perto (~1–4 m)", "no ambiente (~4–10 m)",
                          "longe ou atrás de parede", None])

    def test_resumo_ordena_pelo_sinal_e_marca_pareados(self):
        bruto = {"bluetooth_ligado": True, "busca": "ok",
                 "pareados": [{"endereco": "A1", "nome": "JBL Go 3"}, {"endereco": "A2", "nome": "Redmi Watch"}],
                 "proximos": [{"endereco": "X", "rssi": -90, "rssi_max": -85},
                              {"endereco": "A1", "rssi": -60, "rssi_max": -999}]}
        r = self.m.resumir(bruto, limite=1)
        self.assertEqual(r["total_vistos"], 2)
        self.assertEqual(r["omitidos"], 1)
        self.assertEqual(r["aparelhos"][0]["nome"], "JBL Go 3")
        self.assertTrue(r["aparelhos"][0]["pareado"])
        self.assertEqual(r["aparelhos"][0]["rssi"], -60)  # rssi_max ausente (-999) cai no último
        self.assertEqual({p["nome"]: p["por_perto"] for p in r["pareados"]}, {"JBL Go 3": True, "Redmi Watch": False})
        self.assertEqual(self.m.resumir({"busca": "bluetooth_desligado"})["dica"][:24], "o Bluetooth está desliga")

    def test_pareados_pelo_dumpsys(self):
        texto = ("Bluetooth Status\n  enabled: true\nBonded devices:\n"
                 "  4C:87:5D:11:22:33 [ DUAL ] JBL Flip 5\n  E0:9D:13:AA:BB:CC [  LE  ] Redmi Watch 3 (Ativo)\n"
                 "\nConnection Manager:\n  something\n")
        self.assertEqual(self.m.ler_pareados_dumpsys(texto), [
            {"endereco": "4C:87:5D:11:22:33", "nome": "JBL Flip 5", "tipo_radio": "duplo"},
            {"endereco": "E0:9D:13:AA:BB:CC", "nome": "Redmi Watch 3", "tipo_radio": "ble"}])
        self.assertEqual(self.m.ler_pareados_dumpsys("nada aqui"), [])


class TestBuscarNoCelular(unittest.TestCase):
    """O caminho pelo Shizuku com o rish imitado: comando certo, liga/desliga só quando pedido."""

    def setUp(self):
        self.m = _carregar()
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        os.makedirs(os.path.join(self.tmp, "compilado"))
        jar = os.path.join(self.tmp, "compilado", "controle-bt-x.jar")
        Path(jar).write_bytes(b"jar")
        self.m.compilar = lambda: (jar, None)
        self.comandos = []
        saida = json.dumps({"bluetooth_ligado": True, "busca": "ok", "pareados": [], "proximos": []})

        class Tela:
            TMP_SHELL = "/data/local/tmp"

            @staticmethod
            def _pasta_troca():
                return self.tmp

            @staticmethod
            def rish(cmd, timeout=20):
                self.comandos.append(cmd)
                if cmd.startswith("settings get"):
                    return "0\n", "", 0
                return ("ruído\n" + saida + "\n") if "app_process" in cmd else "", "", 0

        self.tela = Tela

    def test_busca_roda_o_leitor_pelo_shell(self):
        r = self.m.buscar(8, tela=self.tela)
        self.assertEqual(r["busca"], "ok")
        self.assertEqual(len(self.comandos), 1)
        self.assertIn("app_process /system/bin controleir.Bluetooth 8000 ble", self.comandos[0])
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "controle-bt-x.jar")))  # cópia de troca apagada

    def test_ligar_liga_so_durante_a_busca(self):
        r = self.m.buscar(5, ligar=True, tela=self.tela)
        self.assertTrue(r["ligado_para_buscar"])
        self.assertIn("cmd bluetooth_manager enable", self.comandos[1])
        self.assertIn("app_process", self.comandos[2])
        self.assertEqual(self.comandos[-1], "cmd bluetooth_manager disable")

    def test_sem_resposta_do_leitor(self):
        self.tela.rish = staticmethod(lambda cmd, timeout=20: ("", "Exception in thread main", 1))
        r = self.m.buscar(5, tela=self.tela)
        self.assertEqual(r["erro"], "o leitor Bluetooth não respondeu")
        self.assertIn("Exception", r["detalhe"])

    def test_main_acao_invalida(self):
        saida = io.StringIO()
        with mock.patch.object(sys, "stdin", io.StringIO('{"acao":"conectar"}')), mock.patch("sys.stdout", saida):
            self.m.main()
        self.assertIn("erro", json.loads(saida.getvalue()))


class TestManifesto(unittest.TestCase):
    def test_capacidade_json(self):
        m = json.loads((CAP / "capacidade.json").read_text(encoding="utf-8"))
        self.assertEqual((m["nome"], m["executar"], m["efeito"]), ("bluetooth", "principal.py", "leitura"))
        self.assertFalse(m["entrada"]["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
