"""Executor de objetivos no celular (capacidades/tela/objetivo.py) contra um celular simulado: telas, transições,
notificação por cima, lista longa (rolar), toque que falha uma vez, diálogo que atrapalha, botões proibidos."""
from __future__ import annotations

import importlib.util
import os
import shutil
import tempfile
import unittest
from pathlib import Path

CAP = Path(__file__).resolve().parent.parent / "controle-ir" / "capacidades" / "tela"


def _carregar():
    spec = importlib.util.spec_from_file_location("tela_objetivo_teste", CAP / "objetivo.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


APP = "com.exemplo.ajustes"


def el(texto, y, clic=True, pacote=APP, **k):
    return {"texto": texto, "desc": "", "id": "", "clicavel": clic, "x": 300, "y": y, "pacote": pacote,
            "a": 100, "editavel": False, "rolavel": False, **k}


class Celular:
    """Telas: nome → (elementos, {rótulo tocado: próxima tela}). Extras: rolagem revela, falhas pontuais, sobreposição."""

    def __init__(self, telas, inicio, app=APP):
        self.telas, self.atual, self.app = telas, inicio, app
        self.pilha = []
        self.sobreposto = None  # (pacote, vezes) — notificação/janela de outro app por cima
        self.falhar = {}  # rótulo → quantas vezes o toque não faz efeito
        self.injetados = []
        self.digitado = ""
        self.abertos = []

    # ferramentas que o executor usa
    def foco(self):
        if self.sobreposto and self.sobreposto[1] > 0:
            return self.sobreposto[0]
        return self.app

    def dump_ui(self):
        return self.atual

    def elementos(self, nome, limite=300):
        if self.sobreposto and self.sobreposto[1] > 0:
            return [el("Nova mensagem de Ana: oi", 100, pacote=self.sobreposto[0])]
        return [dict(e) for e in self.telas[nome][0]]

    def calma(self, *a):
        return 10

    def em_anuncio(self):
        return False

    def fechar_anuncio(self, app):
        pass

    def aplicar_regras(self, app, els):
        return None

    def bloqueado(self, pac):
        return pac == "com.banco"

    def abrir(self, pac):
        self.abertos.append(pac)
        self.app = pac
        return True

    def injetar(self, cmd):
        self.injetados.append(cmd)
        partes = cmd.split()
        if partes[0] == "tecla" and partes[1] == "4":
            if self.sobreposto and self.sobreposto[1] > 0:
                self.sobreposto = (self.sobreposto[0], 0)
            elif self.pilha:
                self.atual = self.pilha.pop()
            return True
        if partes[0] == "tecla" and partes[1] == "66":
            transicoes = self.telas[self.atual][1]
            if "<enter>" in transicoes and self.digitado:
                self.pilha.append(self.atual)
                self.atual = transicoes["<enter>"]
            return True
        if partes[0] == "texto":
            self.digitado += bytes.fromhex(partes[1]).decode()
            return True
        if partes[0] == "deslizar":
            prox = self.telas[self.atual][1].get("<rolar>")
            if prox:
                self.atual = prox
            return True
        if partes[0] == "tocar":
            x, y = int(partes[1]), int(partes[2])
            alvo = next((e for e in self.telas[self.atual][0] if e["y"] == y), None)
            if not alvo:
                return True
            r = alvo["texto"]
            if self.falhar.get(r, 0) > 0:
                self.falhar[r] -= 1
                return True
            prox = self.telas[self.atual][1].get(r)
            if prox:
                self.pilha.append(self.atual)
                self.atual = prox
            return True
        return True


TELAS = {
    "inicio": ([el("Configurações", 50, clic=False), el("Wi-Fi", 200), el("Bluetooth", 300), el("Sistema", 400),
                el("Lista", 800, clic=False, rolavel=True, a=1500)],
               {"Bluetooth": "bt", "Sistema": "sistema", "<rolar>": "inicio_baixo"}),
    "inicio_baixo": ([el("Configurações", 50, clic=False), el("Bateria", 200), el("Sobre o telefone", 300),
                      el("Lista", 800, clic=False, rolavel=True, a=1500)],
                     {"Sobre o telefone": "sobre"}),
    "bt": ([el("Bluetooth", 50, clic=False), el("Nome do dispositivo", 200), el("AirPods Pro", 300)], {}),
    "sistema": ([el("Sistema", 50, clic=False), el("Idioma", 200), el("Atualizações", 300)], {"Atualizações": "atual"}),
    "atual": ([el("Atualizações", 50, clic=False), el("Versão 1.0", 200, clic=False)], {}),
    "sobre": ([el("Sobre o telefone", 50, clic=False), el("Modelo: POCO", 200, clic=False)], {}),
}


class TestExecutorObjetivo(unittest.TestCase):
    def setUp(self):
        self.m = _carregar()
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.mem = os.path.join(self.tmp, "objetivos.json")
        self.perguntas = []

    def executor(self, cel, escolher=None):
        def decidir(objetivo, resumo, opcoes):
            self.perguntas.append(opcoes)
            return escolher(opcoes) if escolher else None
        return self.m.Executor(cel, decidir, self.mem)

    def test_1_navegacao_simples_por_pista_sem_modelo(self):
        cel = Celular(TELAS, "inicio")
        r = self.executor(cel).executar({"objetivo": "abrir o Bluetooth", "app": APP,
                                         "concluido": {"texto": "Nome do dispositivo"}, "pistas": ["Bluetooth"]})
        self.assertEqual(r["estado"], "concluido")
        self.assertEqual([(p["acao"], p["alvo"], p["via"]) for p in r["passos"]], [("tocar", "Bluetooth", "pista")])
        self.assertEqual(r["consultas_modelo"], 0)
        self.assertIn("AirPods Pro", r["tela"]["textos"])  # a resposta já vem: sem outra olhada da nuvem

    def test_2_varias_etapas_pelo_modelo_e_memoria_na_segunda_vez(self):
        def escolher(opcoes):
            for alvo in ("Atualizações", "Sistema"):
                if alvo in opcoes:
                    return opcoes.index(alvo)
            return None
        pedido = {"objetivo": "ver a versão do sistema", "app": APP, "concluido": {"texto": "Versão"}}
        r = self.executor(Celular(TELAS, "inicio"), escolher).executar(pedido)
        self.assertEqual(r["estado"], "concluido")
        self.assertEqual(r["consultas_modelo"], 2)
        self.assertEqual([p["via"] for p in r["passos"]], ["modelo", "modelo"])
        r2 = self.executor(Celular(TELAS, "inicio"), escolher).executar(pedido)  # aprendeu o caminho
        self.assertEqual((r2["estado"], r2["consultas_modelo"]), ("concluido", 0))
        self.assertEqual([p["via"] for p in r2["passos"]], ["memoria", "memoria"])

    def test_3_abre_o_app_e_le_resultado(self):
        cel = Celular(TELAS, "inicio")
        cel.app = "com.android.launcher"
        r = self.executor(cel).executar({"objetivo": "Bluetooth", "app": APP, "concluido": {"texto": "AirPods"},
                                         "pistas": ["Bluetooth"]})
        self.assertEqual(cel.abertos, [APP])
        self.assertEqual(r["passos"][0]["acao"], "abrir")
        self.assertEqual(r["estado"], "concluido")

    def test_5_notificacao_por_cima_e_fechada_e_a_tarefa_segue(self):
        cel = Celular(TELAS, "inicio")
        cel.sobreposto = ("com.android.systemui", 1)
        r = self.executor(cel).executar({"objetivo": "Bluetooth", "app": APP, "concluido": {"texto": "AirPods"},
                                         "pistas": ["Bluetooth"]})
        self.assertEqual(r["estado"], "concluido")
        self.assertEqual(r["recuperacoes"], 1)
        self.assertEqual([p["acao"] for p in r["passos"]], ["abrir", "voltar", "tocar"])  # fecha com voltar,
        # sem tocar em nada da notificação, e segue com a pista
        self.assertFalse(any("Ana" in str(p) for p in r["passos"]))

    def test_5b_cortina_do_sistema_que_ignora_voltar_e_recolhida_sem_vazar_mensagens(self):
        cel = Celular(TELAS, "inicio")
        cel.sobreposto = ("com.android.systemui", 1)
        cel.injetar_original = cel.injetar

        def injetar(cmd):  # no HyperOS o "voltar" injetado não fecha a cortina
            if cmd == "tecla 4" and cel.sobreposto and cel.sobreposto[1] > 0:
                cel.injetados.append(cmd)
                return True
            return cel.injetar_original(cmd)
        cel.injetar = injetar
        cel.recolher = lambda: setattr(cel, "sobreposto", None)
        r = self.executor(cel).executar({"objetivo": "Bluetooth", "app": APP, "concluido": {"texto": "AirPods"},
                                         "pistas": ["Bluetooth"]})
        self.assertEqual(r["estado"], "concluido")
        self.assertIn("recolher_paineis", [p["acao"] for p in r["passos"]])
        # se travar com a cortina aberta, o texto das notificações NÃO volta para a nuvem
        cel = Celular(TELAS, "inicio")
        cel.sobreposto = ("com.android.systemui", 99)
        orig = cel.injetar
        cel.injetar = lambda cmd: True if cmd == "tecla 4" else orig(cmd)  # nada fecha a cortina
        cel.recolher = lambda: None
        r = self.executor(cel).executar({"objetivo": "Bluetooth", "app": APP, "concluido": {"texto": "AirPods"}})
        self.assertEqual(r["estado"], "parado")
        self.assertEqual(r["tela"]["textos"], [])
        self.assertNotIn("Ana", str(r))

    def test_6_interface_mudou_alvo_abaixo_rola_e_acha(self):
        cel = Celular(TELAS, "inicio")
        r = self.executor(cel).executar({"objetivo": "ver o modelo", "app": APP, "concluido": {"texto": "Modelo:"},
                                         "pistas": ["Sobre o telefone"], "modelo": False})
        self.assertEqual(r["estado"], "concluido")
        self.assertEqual([p["acao"] for p in r["passos"]], ["rolar", "tocar"])

    def test_8_toque_sem_efeito_repete_uma_vez_e_depois_desiste(self):
        cel = Celular(TELAS, "inicio")
        cel.falhar = {"Bluetooth": 1}  # transitório: o 1º toque não pega
        r = self.executor(cel).executar({"objetivo": "Bluetooth", "app": APP, "concluido": {"texto": "AirPods"},
                                         "pistas": ["Bluetooth"]})
        self.assertEqual(r["estado"], "concluido")
        self.assertEqual([p["via"] for p in r["passos"]], ["pista (sem efeito)", "pista"])
        cel = Celular(TELAS, "inicio")
        cel.falhar = {"Bluetooth": 99}  # estrutural: nunca pega → não insiste para sempre
        r = self.executor(cel).executar({"objetivo": "Bluetooth", "app": APP, "concluido": {"texto": "AirPods"},
                                         "pistas": ["Bluetooth"], "modelo": False, "max_passos": 10})
        self.assertEqual(r["estado"], "parado")
        self.assertEqual(sum(p["alvo"] == "Bluetooth" for p in r["passos"]), 2)

    def test_dialogo_que_atrapalha_e_dispensado_sem_aceitar_nada(self):
        telas = dict(TELAS)
        telas["dialogo"] = ([el("Nova versão disponível", 100, clic=False), el("Atualizar", 200),
                             el("Agora não", 300)], {"Agora não": "inicio", "Atualizar": "sistema"})
        r = self.executor(Celular(telas, "dialogo")).executar(
            {"objetivo": "Bluetooth", "app": APP, "concluido": {"texto": "AirPods"}, "pistas": ["Bluetooth"]})
        self.assertEqual(r["estado"], "concluido")
        self.assertEqual([(p["alvo"], p["via"]) for p in r["passos"]], [("Agora não", "dispensar"), ("Bluetooth", "pista")])

    def test_rotulos_de_efeito_externo_sao_recusados_sem_permissao(self):
        telas = {"chat": ([el("Ana", 50, clic=False), el("Enviar", 900), el("Excluir conversa", 1000)],
                          {"Enviar": "enviado"}), "enviado": ([el("Enviado", 50)], {})}
        r = self.executor(Celular(telas, "chat"), lambda o: 0).executar(
            {"objetivo": "mandar", "app": APP, "concluido": {"texto": "Enviado"}, "pistas": ["Enviar"]})
        self.assertNotEqual(r["estado"], "concluido")
        self.assertFalse(any(p.get("alvo") == "Enviar" for p in r["passos"]))
        self.assertTrue(all("Enviar" not in o and "Excluir conversa" not in o for o in self.perguntas))
        r = self.executor(Celular(telas, "chat")).executar(
            {"objetivo": "mandar", "app": APP, "concluido": {"texto": "Enviado"}, "pistas": ["Enviar"],
             "permitir": ["Enviar"]})
        self.assertEqual(r["estado"], "concluido")  # só com autorização explícita

    def test_sem_laco_infinito(self):
        telas = {"a": ([el("Ir para B", 100)], {"Ir para B": "b"}), "b": ([el("Ir para A", 100)], {"Ir para A": "a"})}
        r = self.executor(Celular(telas, "a"), lambda o: 0).executar(
            {"objetivo": "chegar em C", "app": APP, "concluido": {"texto": "C"}, "max_passos": 25})
        self.assertEqual(r["estado"], "parado")
        self.assertLessEqual(len(r["passos"]), 10)

    def test_digitar_busca_autorizada(self):
        telas = {"busca": ([el("", 100, editavel=True)], {"<enter>": "resultados"}),
                 "resultados": ([el("Resultado: Bluetooth", 200)], {})}
        cel = Celular(telas, "busca")
        r = self.executor(cel).executar({"objetivo": "buscar bluetooth", "app": APP, "digitar": "bluetooth",
                                         "concluido": {"texto": "Resultado"}})
        self.assertEqual(r["estado"], "concluido")
        self.assertEqual(cel.digitado, "bluetooth")

    def test_app_bloqueado_para_na_hora(self):
        cel = Celular(TELAS, "inicio", app="com.banco")
        r = self.executor(cel).executar({"objetivo": "x", "concluido": {"texto": "y"}})
        self.assertEqual(r["estado"], "parado")
        self.assertIn("bloqueado", r["motivo"])
        self.assertNotIn("tela", r)  # nada da tela do banco sai do celular

    def test_validacao(self):
        ex = self.executor(Celular(TELAS, "inicio"))
        self.assertIn("erro", ex.executar({"objetivo": "x"}))  # sem critério de conclusão
        self.assertIn("erro", ex.executar({"concluido": {"texto": "x"}}))
        self.assertIn("erro", ex.executar({"objetivo": "x", "concluido": {"texto": "y"}, "pistas": "nao-lista"}))


if __name__ == "__main__":
    unittest.main()
