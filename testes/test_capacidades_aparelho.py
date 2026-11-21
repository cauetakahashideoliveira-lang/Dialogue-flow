"""Correções da checagem completa no POCO (21/11): diagnóstico de rede, termômetro e sonar.

Rodar na raiz: python3 -m unittest testes.test_capacidades_aparelho
"""
from __future__ import annotations

import importlib.util
import io
import os
import shutil
import subprocess
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

CAPS = Path(__file__).resolve().parents[1] / "controle-ir" / "capacidades"


def _carregar(nome: str):
    spec = importlib.util.spec_from_file_location(f"cap_{nome}_teste", CAPS / nome / "principal.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # os três só rodam main() como script
    return mod


class _Resposta:
    def __init__(self, dados: bytes):
        self.dados = io.BytesIO(dados)

    def read(self, n=-1):
        return self.dados.read(n)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class TestDiagnosticoRede(unittest.TestCase):
    """No POCO o teste de download voltava HTTP 403 (a Cloudflare recusa o urllib sem User-Agent próprio) e um
    único ping perdido para 1.1.1.1 culpava o provedor mesmo com 0 % de perda para 8.8.8.8."""

    def setUp(self):
        self.m = _carregar("diagnostico_rede")

    def test_download_manda_user_agent_e_usa_a_reserva(self):
        pedidos = []

        def urlopen(req, timeout=None):
            pedidos.append((req.full_url, req.get_header("User-agent")))
            if "cloudflare" in req.full_url:
                raise urllib.error.HTTPError(req.full_url, 403, "Forbidden", {}, None)
            return _Resposta(b"x" * 1000)

        with mock.patch.object(self.m.urllib.request, "urlopen", urlopen):
            r = self.m.download(1)
        self.assertEqual((r["fonte"], r["bytes"]), ("proof.ovh.net", 1000))
        self.assertIn("speed.cloudflare.com", pedidos[0][0])
        self.assertTrue(all(ua and "controle-ir" in ua for _, ua in pedidos))

    def test_sem_nenhuma_fonte_devolve_os_dois_erros(self):
        def urlopen(req, timeout=None):
            raise urllib.error.URLError("sem rede")

        with mock.patch.object(self.m.urllib.request, "urlopen", urlopen):
            r = self.m.download(1)
        self.assertIn("speed.cloudflare.com", r["erro"])
        self.assertIn("proof.ovh.net", r["erro"])

    def test_ping_perdido_num_destino_so_nao_culpa_o_provedor(self):
        r = {"wifi": {"rssi": -60}, "ping": {"roteador": {"perda_pct": 0, "ms_med": 5},
                                              "1.1.1.1": {"perda_pct": 10, "ms_med": 68},
                                              "8.8.8.8": {"perda_pct": 0, "ms_med": 71}}}
        achados, _ = self.m.analisar(r)
        self.assertFalse(any("provedor" in a for a in achados), achados)
        r["ping"]["8.8.8.8"]["perda_pct"] = 20
        achados, _ = self.m.analisar(r)
        self.assertTrue(any("provedor" in a for a in achados), achados)


class TestTermometroSemResposta(unittest.TestCase):
    """Uma leitura do Termux:API passou de 15 s (havia outra chamada em andamento) e derrubava a medição."""

    def setUp(self):
        self.m = _carregar("termometro")

    def test_leitura_que_nao_responde_vira_amostra_ausente(self):
        erro = subprocess.TimeoutExpired("termux-battery-status", 15)
        with mock.patch.object(self.m.subprocess, "run", side_effect=erro):
            self.assertIsNone(self.m.bateria())

    def test_medir_sem_resposta_devolve_erro_sem_quebrar(self):
        with mock.patch.object(self.m, "bateria", return_value=None), mock.patch.object(self.m.time, "sleep"):
            r = self.m.medir(0)
        self.assertIn("erro", r)

    def test_amostra_perdida_no_meio_e_pulada(self):
        boas = {"temperature": 30.0, "plugged": "UNPLUGGED", "current": -200000}
        respostas = iter([None, boas, boas])
        relogio = iter([0.0, 0.0, 1.0, 2.0, 99.0, 99.0, 99.0, 99.0])
        with mock.patch.object(self.m, "bateria", side_effect=lambda: next(respostas)), \
                mock.patch.object(self.m.time, "time", side_effect=lambda: next(relogio, 99.0)), \
                mock.patch.object(self.m.time, "sleep"), mock.patch.object(self.m, "gravar"), \
                mock.patch.object(self.m, "historico", return_value=[]):
            r = self.m.medir(3)
        self.assertNotIn("erro", r)
        self.assertEqual(r["bateria_c"], 30.0)


class TestSonarFrequencia(unittest.TestCase):
    """No POCO, 19 e 18 kHz não chegam ao microfone e 17 kHz chega com folga: sem frequência pedida, o sonar desce
    até a que funciona e lembra dela."""

    def setUp(self):
        self.m = _carregar("sonar")
        pasta = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, pasta, True)
        self.m.MEMORIA = os.path.join(pasta, "medicoes", "sonar.json")

    @staticmethod
    def _falso(funcionam):
        chamadas = []

        def testar(freq, segundos, volume):
            chamadas.append(freq)
            ok = freq in funcionam
            return {"suporte": ok, "tom_acima_do_ruido_db": 90.0 if ok else 0.0, "frequencia_hz": freq}

        return testar, chamadas

    def test_sem_pedido_desce_ate_a_minima_e_lembra(self):
        testar, chamadas = self._falso({17000})
        r = self.m.escolher_e_testar({"acao": "testar"}, testar)
        self.assertEqual(chamadas, [19000, 17000])
        self.assertTrue(r["suporte"])
        self.assertEqual([t["frequencia_hz"] for t in r["tentativas"]], [19000, 17000])
        testar, chamadas = self._falso({17000})
        r = self.m.escolher_e_testar({"acao": "testar"}, testar)
        self.assertEqual(chamadas, [17000])  # a lembrada vem primeiro
        self.assertNotIn("tentativas", r)

    def test_frequencia_pedida_testa_so_ela_e_respeita_os_limites(self):
        testar, chamadas = self._falso(set())
        r = self.m.escolher_e_testar({"acao": "testar", "frequencia": 16000}, testar)
        self.assertEqual(chamadas, [17000])
        self.assertFalse(r["suporte"])
        self.assertFalse(os.path.exists(self.m.MEMORIA))

    def test_sugestao_desce_um_passo_e_para_na_minima(self):
        self.assertIn("tente 18000 Hz", self.m.sugestao_sem_tom(19000))
        self.assertIn("tente 17000 Hz", self.m.sugestao_sem_tom(18000))
        self.assertIn("não serve", self.m.sugestao_sem_tom(17000))

    def _sinal(self, freq, segundos=10, atraso=0.4, mexe_desde=None, semente=4):
        """Como no celular: a gravação começa ~0,4 s antes do tom (com rampa); opcionalmente alguém se mexe."""
        np = self._numpy()
        taxa = 48000
        rng = np.random.default_rng(semente)
        tom = self.m.gerar_tom(freq, segundos).astype(np.float32) / 32768.0 * 0.3
        x = np.concatenate([np.zeros(int(atraso * taxa), np.float32), tom])
        t = np.arange(x.size) / taxa
        if mexe_desde is not None:
            fase = 2 * np.pi * np.cumsum(freq + 60 * np.sin(2 * np.pi * 0.8 * t)) / taxa
            x = x + np.where(t >= mexe_desde, 0.03 * np.sin(fase), 0).astype(np.float32)
        return (x + rng.normal(0, 0.002, x.size)).astype(np.float32)

    @staticmethod
    def _numpy():
        try:
            import numpy
        except ImportError:
            raise unittest.SkipTest("numpy ausente")
        return numpy

    def test_inicio_da_gravacao_sem_tom_nao_vira_movimento(self):
        for freq in (17000, 19000):
            for atraso in (0.0, 0.4, 1.0):
                r = self.m.analisar_sonar(self._sinal(freq, atraso=atraso), freq)
                self.assertTrue(r["suporte"])
                self.assertEqual(sum(r["linha_do_tempo_meio_s"]), 0, (freq, atraso, r["linha_do_tempo_meio_s"]))

    def test_movimento_na_maior_parte_da_gravacao_ainda_aparece(self):
        r = self.m.analisar_sonar(self._sinal(17000, mexe_desde=2.4), 17000)
        linha = r["linha_do_tempo_meio_s"]
        self.assertEqual(sum(linha[:4]), 0, linha)  # parado até ~2 s
        self.assertGreaterEqual(sum(linha[6:]), len(linha[6:]) - 1, linha)  # mexendo até o fim

    def test_erro_do_aparelho_para_a_fila(self):
        chamadas = []

        def testar(freq, segundos, volume):
            chamadas.append(freq)
            return {"erro": "faltam: termux-media-player"}

        self.assertIn("erro", self.m.escolher_e_testar({"acao": "testar"}, testar))
        self.assertEqual(chamadas, [19000])


if __name__ == "__main__":
    unittest.main()
