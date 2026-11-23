"""Capacidade modos: guardar, aplicar e restaurar toque/volumes; aprender métodos e condições; diagnóstico.

O celular falso imita o que o POCO (HyperOS, Android 16) mostrou em 22/11:
- `cmd audio set-ringer-mode` pelo shell muda o toque; no vibrar, toque e notificação leem 0;
- `cmd media_session volume --set` pelo shell é ignorado; `termux-volume` escreve.

Rodar na raiz: python3 -m unittest testes.test_modos
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

CAP = Path(__file__).resolve().parents[1] / "controle-ir" / "capacidades" / "modos"
NUM = {0: "call", 1: "system", 2: "ring", 3: "music", 4: "alarm", 5: "notification"}


def _carregar():
    spec = importlib.util.spec_from_file_location("cap_modos_teste", CAP / "principal.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class CelularFalso:
    def __init__(self, mod, ringer=2, shell_ok=True, shell_set_ignorado=True, ringer_ok=True, sdk="36",
                 termux_ok=True):
        self.mod = mod
        self.ringer = ringer
        self.vols = {"call": 12, "system": 1, "ring": 1, "music": 16, "alarm": 15, "notification": 1}
        self.shell_ok, self.shell_set_ignorado, self.ringer_ok = shell_ok, shell_set_ignorado, ringer_ok
        self.sdk, self.termux_ok = sdk, termux_ok
        self.log = []

    def efetivo(self, f):
        return 0 if f in ("ring", "notification") and self.ringer != 2 else self.vols[f]

    def shell(self, cmd, timeout):
        if not self.shell_ok:
            raise self.mod.SemShell("Shizuku parado")
        self.log.append(("shell", cmd))
        m = re.match(r"cmd audio set-ringer-mode (\w+)", cmd)
        if m:
            antigo = self.ringer
            if self.ringer_ok:
                self.ringer = {"NORMAL": 2, "VIBRATE": 1, "SILENT": 0}[m.group(1)]
            # como no POCO: as configurações refletem a mudança com atraso; só quem relê em laço vê o valor novo
            lido = self.ringer if "for i in" in cmd else antigo
            return f"R={lido}\n", "", 0
        m = re.match(r"cmd media_session volume --stream (\d) --set (\d+)", cmd)
        if m:
            if not self.shell_set_ignorado:
                self.vols[NUM[int(m.group(1))]] = int(m.group(2))
            return "[V] will set volume\n", "", 0
        linhas = [f"R={self.ringer}", f"SDK={self.sdk}"]
        for n in re.findall(r"--stream (\d) --get", cmd):
            linhas.append(f"V{NUM[int(n)]}={self.efetivo(NUM[int(n)])}")
        return "\n".join(linhas) + "\n", "", 0

    def termux(self, args, timeout):
        if not self.termux_ok:
            raise FileNotFoundError(args[0])
        self.log.append(("termux", tuple(args)))
        if len(args) == 1:
            return json.dumps([{"stream": f, "volume": self.efetivo(f)} for f in self.vols]), 0
        self.vols[args[1]] = int(args[2])
        return "", 0

    def android(self):
        return self.mod.Android(shell=self.shell, termux=self.termux)


class TestModos(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.mod = _carregar()
        self.mod.BASE = self.tmp.name
        self.home = mock.patch.dict(os.environ, {"HOME": self.tmp.name})
        self.home.start()
        self.addCleanup(self.home.stop)
        self.addCleanup(self.tmp.cleanup)

    def rodar(self, cel, **a):
        return self.mod.executar(a, cel.android())

    def test_reuniao_ciclo_completo_guarda_aplica_e_restaura(self):
        cel = CelularFalso(self.mod)
        r = self.rodar(cel, acao="entrar", modo="reunião")
        self.assertEqual(r["status"], "ativo")
        self.assertEqual(r["antes"], {"toque": "normal", "volumes": {"ring": 1, "notification": 1}})
        self.assertEqual(cel.ringer, 1)  # vibrar
        self.assertEqual(r["metodos"], {"toque": "shell"})
        self.assertEqual(self.rodar(cel, acao="entrar", modo="reuniao")["status"], "ja_ativo")  # não regrava o antes
        s = self.rodar(cel, acao="sair")
        self.assertEqual(s["status"], "restaurado")
        self.assertEqual((cel.ringer, cel.vols["ring"], cel.vols["notification"]), (2, 1, 1))
        self.assertEqual(self.rodar(cel, acao="sair")["status"], "nenhum_ativo")

    def test_alternar_liga_e_desliga(self):
        cel = CelularFalso(self.mod)
        self.assertEqual(self.rodar(cel, acao="alternar", modo="reuniao")["status"], "ativo")
        self.assertEqual(self.rodar(cel, acao="alternar", modo="reuniao")["status"], "restaurado")
        self.assertEqual(cel.ringer, 2)

    def test_volume_aprende_que_o_shell_e_ignorado_e_nao_tenta_de_novo(self):
        cel = CelularFalso(self.mod)
        self.mod.METODOS["volume"] = ["shell", "termux"]  # força começar pelo caminho que o HyperOS ignora
        self.addCleanup(self.mod.METODOS.__setitem__, "volume", ["termux", "shell"])
        self.rodar(cel, acao="definir", modo="cinema", toque="", volumes={"musica": 5})
        r = self.rodar(cel, acao="entrar", modo="cinema")
        self.assertEqual(r["status"], "ativo")
        self.assertEqual(cel.vols["music"], 5)
        self.assertTrue(any("ignorou" in d["conclusao"] for d in r["diagnostico"]))
        apr = self.rodar(cel, acao="listar")["aprendido"]["volume"]
        self.assertEqual(apr["ok"], "termux")
        self.assertIn("shell", apr["falhou"])
        self.rodar(cel, acao="sair")
        self.assertEqual(cel.vols["music"], 16)
        cel.log.clear()
        self.rodar(cel, acao="entrar", modo="cinema")  # agora vai direto pelo método confirmado
        self.assertFalse(any(c[0] == "shell" and "--set" in c[1] for c in cel.log))

    def test_falha_aprendida_com_codigo_antigo_e_revalidada(self):
        """22/11 no POCO: a 1ª versão leu o toque cedo demais e aprendeu "shell falhou". O código novo (outra
        versao_metodos) não pode herdar esse falso negativo."""
        os.makedirs(os.path.join(self.tmp.name, "modos"), exist_ok=True)
        with open(os.path.join(self.tmp.name, "modos", "aprendido.json"), "w") as f:
            json.dump({"metodos": {"toque": {"condicoes": {"android_sdk": "36", "shizuku": True},
                                             "falhou": {"shell": {"causa": "lido cedo demais"}}}}}, f)
        cel = CelularFalso(self.mod)
        r = self.rodar(cel, acao="entrar")
        self.assertEqual(r["metodos"], {"toque": "shell"})
        self.assertNotIn("plano_b", r["aplicado"])
        self.assertEqual(cel.ringer, 1)

    def test_condicao_mudou_revalida(self):
        cel = CelularFalso(self.mod)
        self.rodar(cel, acao="entrar")
        self.rodar(cel, acao="sair")
        cel.sdk = "37"  # atualização do Android
        r = self.rodar(cel, acao="entrar")
        self.assertEqual(r["status"], "ativo")
        self.assertTrue(any("condição mudou" in n for n in r["revalidacao"]))

    def test_sem_shizuku_diagnostica_e_silencia_pelos_volumes(self):
        cel = CelularFalso(self.mod, shell_ok=False)
        r = self.rodar(cel, acao="entrar")
        self.assertEqual(r["status"], "ativo")
        self.assertIn("plano_b", r["aplicado"])
        self.assertEqual((cel.vols["ring"], cel.vols["notification"]), (0, 0))
        self.assertTrue(any("Shizuku parado" in d["conclusao"] for d in r["diagnostico"]))
        # Shizuku parado é condição, não defeito: o método do toque não vira falha aprendida
        self.assertNotIn("shell", (self.rodar(cel, acao="listar")["aprendido"].get("toque") or {}).get("falhou", {}))
        s = self.rodar(cel, acao="sair")
        self.assertEqual(s["status"], "restaurado")
        self.assertEqual((cel.vols["ring"], cel.vols["notification"]), (1, 1))

    def test_sistema_recusa_o_toque_diagnostico_separa_a_causa(self):
        cel = CelularFalso(self.mod, ringer_ok=False)
        r = self.rodar(cel, acao="entrar")
        self.assertTrue(any(d["teste"] == "o valor mudou em até ~2,5 s?" for d in r["diagnostico"]))
        self.assertIn("plano_b", r["aplicado"])
        self.assertIn("shell", self.rodar(cel, acao="listar")["aprendido"]["toque"]["falhou"])
        self.rodar(cel, acao="sair")
        self.assertEqual(cel.vols["ring"], 1)

    def test_sem_termux_api_diagnostico(self):
        cel = CelularFalso(self.mod, shell_ok=False, termux_ok=False)
        r = self.rodar(cel, acao="entrar")
        self.assertEqual(r["status"], "falhou")
        self.assertTrue(any("Termux:API" in d["conclusao"] for d in r["diagnostico"]))

    def test_testar_valida_registra_condicoes_e_cria_atalho(self):
        cel = CelularFalso(self.mod)
        r = self.rodar(cel, acao="testar", modo="reuniao")
        self.assertEqual(r["status"], "validado")
        val = self.rodar(cel, acao="listar")["modos"]["reuniao"]["validacao"]
        self.assertTrue(val["ok"])
        self.assertEqual(val["condicoes"]["android_sdk"], "36")
        arq = Path(r["atalho"]["arquivo"])
        self.assertTrue(arq.exists())
        self.assertIn('"acao": "alternar"', arq.read_text())
        self.assertEqual(oct(arq.stat().st_mode & 0o777), "0o700")
        self.assertEqual(cel.ringer, 2)

    def test_correcao_do_usuario_fica_registrada_e_invalida_a_validacao(self):
        cel = CelularFalso(self.mod)
        self.rodar(cel, acao="testar", modo="reuniao", criar_atalho=False)
        r = self.rodar(cel, acao="definir", modo="reuniao", toque="silencioso")
        self.assertTrue(r["corrigido"])
        lst = self.rodar(cel, acao="listar")
        self.assertEqual(lst["correcoes"][-1]["de"]["toque"], "vibrar")
        self.assertEqual(lst["correcoes"][-1]["para"]["toque"], "silencioso")
        self.assertFalse(lst["modos"]["reuniao"]["validacao"]["ok"])
        self.rodar(cel, acao="entrar", modo="reuniao")
        self.assertEqual(cel.ringer, 0)

    def test_troca_de_modo_mantem_o_estado_original(self):
        cel = CelularFalso(self.mod)
        self.rodar(cel, acao="definir", modo="cinema", volumes={"music": 3})
        self.rodar(cel, acao="entrar", modo="reuniao")
        self.rodar(cel, acao="entrar", modo="cinema")
        s = self.rodar(cel, acao="sair")
        self.assertEqual(s["status"], "restaurado")
        self.assertEqual((cel.ringer, cel.vols["music"], cel.vols["ring"]), (2, 16, 1))

    def test_entradas_invalidas(self):
        cel = CelularFalso(self.mod)
        self.assertIn("erro", self.rodar(cel, acao="entrar", modo="inexistente"))
        self.assertIn("erro", self.rodar(cel, acao="definir", modo="x", volumes={"tv": 3}))
        self.assertIn("erro", self.rodar(cel, acao="definir", modo="x", toque="alto"))
        self.assertIn("erro", self.rodar(cel, acao="remover", modo="reuniao"))

    def test_manifesto_valido_e_aceita_os_argumentos(self):
        m = json.loads((CAP / "capacidade.json").read_text())
        self.assertEqual((m["nome"], m["executar"], m["efeito"]), ("modos", "principal.py", "acao"))
        self.assertTrue(m["em_processo"])
        for k in ("acao", "modo", "toque", "volumes", "avisar", "criar_atalho"):
            self.assertIn(k, m["entrada"]["properties"])
            self.assertIsInstance(m["entrada"]["properties"][k]["type"], str)


if __name__ == "__main__":
    unittest.main()
