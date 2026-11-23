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
        self.niveis = []

    def executor(self, cel, escolher=None):
        def decidir(objetivo, resumo, opcoes, nivel="padrao"):
            self.perguntas.append(opcoes)
            self.niveis.append(nivel)
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
        self.assertTrue(all(p["via"].startswith("modelo:") for p in r["passos"]))
        self.assertEqual(self.niveis, ["forte", "forte"])  # padrão: Sonnet + Opus correndo juntos
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

    def test_7_app_lento_para_abrir_espera_e_nao_conclui_em_outro_app(self):
        # 21/11, POCO: a Play Store demorou; o executor apertou voltar no app anterior, caiu na tela inicial e a
        # barra "Pesquisar" dela "concluiu" a tarefa. Agora espera o app e só conclui dentro dele.
        telas = {"loja": ([el("Pesquisar apps e jogos", 100)], {})}
        cel = Celular(telas, "loja", app="com.android.settings")
        demora = {"n": 4}
        foco_original = cel.foco

        def foco():
            if cel.app == APP and demora["n"] > 0:
                demora["n"] -= 1
                return "com.android.settings"  # ainda carregando
            return foco_original()
        cel.foco = foco
        r = self.executor(cel).executar({"objetivo": "abrir a loja", "app": APP,
                                         "concluido": {"texto": "Pesquisar"}, "modelo": False})
        self.assertEqual(r["estado"], "concluido")
        self.assertEqual([p["acao"] for p in r["passos"]], ["abrir"])
        self.assertNotIn("tecla 4", cel.injetados)  # não apertou voltar no app que estava na frente

        telas = {"home": ([el("Pesquisar", 100, pacote="com.launcher")], {})}
        cel = Celular(telas, "home", app="com.launcher")
        cel.abrir = lambda pac: True  # o app nunca abre
        ex = self.executor(cel)
        ex._esperar_app = lambda app, s: False  # sem esperar de verdade no teste
        r = ex.executar({"objetivo": "abrir a loja", "app": APP, "concluido": {"texto": "Pesquisar"},
                         "modelo": False, "prazo": 5})
        self.assertEqual(r["estado"], "parado")  # o "Pesquisar" da tela inicial não conclui

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

    def test_pista_vale_uma_vez_e_interruptor_nunca_sem_permissao(self):
        # 21/11, POCO: a pista "Opções do desenvolvedor" foi tocada de novo na tela seguinte, onde o mesmo rótulo é o
        # interruptor geral — desligou o modo de desenvolvedor (e o Shizuku caiu). Isso não pode se repetir.
        telas = {
            "adicionais": ([el("Configurações adicionais", 50, clic=False), el("Opções do desenvolvedor", 300)],
                           {"Opções do desenvolvedor": "dev"}),
            "dev": ([el("Opções do desenvolvedor", 50, clic=False), el("Opções do desenvolvedor", 200),
                     el("", 200, clic=True, marcado=True, classe="Switch"),
                     el("Lista", 800, clic=False, rolavel=True, a=1500)],
                    {"Opções do desenvolvedor": "desligado", "<rolar>": "dev_baixo"}),
            "dev_baixo": ([el("Depuração USB", 300), el("", 300, clic=True, marcado=True, classe="Switch")], {}),
            "desligado": ([el("Opções do desenvolvedor desativadas", 50, clic=False)], {}),
        }
        cel = Celular(telas, "adicionais")
        r = self.executor(cel, lambda o: 0).executar(
            {"objetivo": "abrir opções do desenvolvedor", "app": APP, "concluido": {"texto": "Depuração USB"},
             "pistas": ["Opções do desenvolvedor"]})
        self.assertNotEqual(cel.atual, "desligado")
        self.assertEqual(r["estado"], "concluido")
        self.assertEqual(sum(p.get("alvo") == "Opções do desenvolvedor" for p in r["passos"]), 1)
        self.assertTrue(all("Opções do desenvolvedor" not in o for o in self.perguntas))  # nem ao modelo

    def test_interruptor_so_com_permitir(self):
        telas = {"a": ([el("Wi-Fi", 200), el("", 200, marcado=False, classe="Switch")], {"Wi-Fi": "ligado"}),
                 "ligado": ([el("Wi-Fi ligado", 50, clic=False)], {})}
        r = self.executor(Celular(telas, "a")).executar(
            {"objetivo": "ligar wifi", "app": APP, "concluido": {"texto": "ligado"}, "pistas": ["Wi-Fi"]})
        self.assertEqual(r["estado"], "parado")
        r = self.executor(Celular(telas, "a")).executar(
            {"objetivo": "ligar wifi", "app": APP, "concluido": {"texto": "ligado"}, "pistas": ["Wi-Fi"],
             "permitir": ["Wi-Fi"]})
        self.assertEqual(r["estado"], "concluido")

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

    def test_digita_uma_vez_so_mesmo_com_a_tela_mudando(self):
        # 21/11, POCO: cada letra mudava a "identidade" da tela e o texto foi digitado 8 vezes
        telas = {"busca": ([el("", 100, editavel=True), el("Resultado: conta", 300)], {}),
                 "resultados": ([el("WhatsApp", 100, editavel=True), el("Resultado: conta", 300)], {})}
        cel = Celular(telas, "busca")
        orig = cel.injetar

        def injetar(cmd):
            r = orig(cmd)
            if cmd.startswith("texto"):
                cel.atual = "resultados"
            return r
        cel.injetar = injetar
        r = self.executor(cel).executar({"objetivo": "achar o app", "app": APP, "digitar": "WhatsApp",
                                         "concluido": {"texto": "Forçar parada"}, "modelo": False, "max_passos": 8})
        self.assertEqual(cel.digitado, "WhatsApp")
        self.assertEqual(sum(p["acao"] == "digitar" for p in r["passos"]), 1)

    def test_digitar_so_depois_da_pista_indicada(self):
        telas = {"inicio": ([el("", 100, editavel=True), el("Apps", 300)], {"Apps": "apps"}),
                 "apps": ([el("", 100, editavel=True), el("Lista", 800, clic=False, rolavel=True)], {"<enter>": "res"}),
                 "res": ([el("WhatsApp", 300)], {"WhatsApp": "info"}),
                 "info": ([el("Forçar parada", 900)], {})}
        cel = Celular(telas, "inicio")
        r = self.executor(cel).executar({"objetivo": "info do WhatsApp", "app": APP, "pistas": ["Apps", "WhatsApp"],
                                         "digitar": {"texto": "WhatsApp", "depois_de": "Apps"},
                                         "concluido": {"texto": "Forçar parada"}, "modelo": False})
        self.assertEqual(r["estado"], "concluido")
        self.assertEqual([p["acao"] for p in r["passos"]], ["tocar", "digitar", "tocar"])

    def test_pista_estrita_e_app_que_abre_devagar(self):
        seg = "com.miui.securitycenter"
        telas = {"inicio": ([el("Atualização de apps do sistema", 200), el("Apps", 600)], {"Apps": "lista"}),
                 "lista": ([el("WhatsApp", 300, pacote=seg)], {"WhatsApp": "info"}),
                 "info": ([el("Forçar parada", 900, pacote=seg)], {})}
        cel = Celular(telas, "inicio")
        orig_inj, orig_foco = cel.injetar, cel.foco
        lento = {"n": 0}

        def injetar(cmd):
            r = orig_inj(cmd)
            if cel.atual == "lista" and lento["n"] == 0:
                lento["n"] = 3  # a Central de Segurança demora: as 3 primeiras olhadas ainda mostram Configurações
            return r

        def foco():
            if lento["n"] > 0:
                lento["n"] -= 1
                return APP
            return seg if cel.atual in ("lista", "info") else orig_foco()

        def elementos(nome, limite=300):
            if lento["n"] > 0:
                return [dict(e) for e in telas["inicio"][0]]
            return [dict(e) for e in cel.telas[nome][0]]
        cel.injetar, cel.foco, cel.elementos = injetar, foco, elementos
        r = self.executor(cel).executar({"objetivo": "info do WhatsApp", "app": APP, "pistas": ["Apps", "WhatsApp"],
                                         "concluido": {"texto": "Forçar parada"}, "modelo": False})
        self.assertEqual(r["estado"], "concluido")
        self.assertFalse(any(p.get("alvo") == "Atualização de apps do sistema" for p in r["passos"]))
        self.assertEqual(r["recuperacoes"], 0)  # não "corrigiu" o app que abriu devagar

    def test_atalho_de_busca_que_abre_o_campo(self):
        telas = {"lista": ([el("Pesquisar apps", 100), el("Lista", 800, clic=False, rolavel=True)],
                           {"Pesquisar apps": "busca"}),
                 "busca": ([el("", 100, editavel=True)], {"<enter>": "res"}),
                 "res": ([el("WhatsApp", 300)], {"WhatsApp": "info"}),
                 "info": ([el("Forçar parada", 900)], {})}
        cel = Celular(telas, "lista")
        r = self.executor(cel).executar({"objetivo": "info do WhatsApp", "app": APP, "pistas": ["WhatsApp"],
                                         "digitar": "WhatsApp", "concluido": {"texto": "Forçar parada"},
                                         "modelo": False})
        self.assertEqual(r["estado"], "concluido")
        self.assertEqual([p["acao"] for p in r["passos"]], ["abrir_busca", "digitar", "tocar"])

    def test_pista_nao_casa_com_o_campo_de_busca(self):
        els = [el("WhatsApp", 100, editavel=True), el("WhatsApp", 400)]
        self.assertEqual(self.m.melhor(els, "WhatsApp", estrito=True)["y"], 400)

    def test_app_bloqueado_para_na_hora(self):
        cel = Celular(TELAS, "inicio", app="com.banco")
        r = self.executor(cel).executar({"objetivo": "x", "concluido": {"texto": "y"}})
        self.assertEqual(r["estado"], "parado")
        self.assertIn("bloqueado", r["motivo"])
        self.assertNotIn("tela", r)  # nada da tela do banco sai do celular

    def test_modelo_ve_os_titulos_das_linhas_clicaveis(self):
        # Configurações do HyperOS: a linha (sem texto) é clicável, o título não. O modelo precisa ver o título.
        linha = dict(el("", 400, clic=True), l=1200, a=160)
        titulo = el("Sobre o telefone", 400, clic=False)
        telas = {"inicio": ([el("Configurações", 50, clic=False), linha, titulo,
                             el("Lista", 800, clic=False, rolavel=True, a=1500)], {"Sobre o telefone": "sobre"}),
                 "sobre": ([el("Versão do Android", 200, clic=False)], {})}
        cel = Celular(telas, "inicio")
        orig = cel.injetar

        def injetar(cmd):  # o toque no título cai na linha
            if cmd.startswith("tocar") and cmd.split()[2] == "400":
                cel.atual = "sobre"
                cel.injetados.append(cmd)
                return True
            return orig(cmd)
        cel.injetar = injetar
        r = self.executor(cel, lambda o: o.index("Sobre o telefone")).executar(
            {"objetivo": "ver a versão do Android", "app": APP, "concluido": {"texto": "Versão do Android"}})
        self.assertEqual(r["estado"], "concluido")
        self.assertIn("Sobre o telefone", self.perguntas[0])
        self.assertLessEqual(len(self.perguntas[0]), 9)  # o cérebro responde 1 dígito
        self.assertEqual(self.m.ranquear([f"Item {i}" for i in range(12)] + ["Versão do sistema"],
                                         "ver a versão do sistema", 3)[-1], "Versão do sistema")

    def test_ciclo_chat_info_e_cortado_e_busca_fora_das_opcoes(self):
        # 21/11, WhatsApp: chat → tocar no título → informações → voltar → chat → tocar no título de novo…
        telas = {"lista": ([el("Pergunte à Meta AI ou pesquise", 100), el("Você", 300)], {"Você": "chat"}),
                 "chat": ([el("Você", 50), el("Última: oi", 600, clic=False)], {"Você": "info"}),
                 "info": ([el("Grupo · 1 membro", 100, clic=False), el("Membros", 300, clic=False)], {})}
        cel = Celular(telas, "lista")

        def escolher(opcoes):
            for o in ("Você", "← voltar"):
                if o in opcoes:
                    return opcoes.index(o)
            return None
        r = self.executor(cel, escolher).executar(
            {"objetivo": "ler a conversa Você", "app": APP, "concluido": {"texto": "Anexar"}, "max_passos": 20})
        self.assertEqual(r["estado"], "parado")
        self.assertLessEqual(len(r["passos"]), 6)  # não fica indo e voltando até o limite (20)
        self.assertEqual(sum(p.get("alvo") == "Você" for p in r["passos"]), 2)  # uma vez na lista, uma no chat
        self.assertTrue(all("Pergunte à Meta AI ou pesquise" not in o for o in self.perguntas))

    def test_pista_fora_da_tela_rola_antes_de_perguntar_ao_modelo(self):
        r = self.executor(Celular(TELAS, "inicio"), lambda o: 0).executar(
            {"objetivo": "ver o modelo", "app": APP, "concluido": {"texto": "Modelo:"}, "pistas": ["Sobre o telefone"]})
        self.assertEqual(r["estado"], "concluido")
        self.assertEqual([p["via"] for p in r["passos"]], ["procurando pista", "pista"])
        self.assertEqual(r["consultas_modelo"], 0)

    def test_memoria_guarda_so_o_caminho_certo_sem_desvios(self):
        telas = {"lista": ([el("Mae", 200), el("Você", 300)], {"Mae": "chat_mae", "Você": "chat_voce"}),
                 "chat_mae": ([el("Mae", 50, clic=False), el("Olá filho", 300, clic=False)], {}),
                 "chat_voce": ([el("Você", 50, clic=False), el("Anexar", 900)], {})}
        escolhas = iter(["Mae", "← voltar"])

        def escolher(opcoes):
            alvo = next(escolhas, None)
            return opcoes.index(alvo) if alvo in opcoes else None
        pedido = {"objetivo": "abrir Você", "app": APP, "concluido": {"texto": "Anexar"}, "pistas": ["Você"]}
        cel = Celular(dict(telas), "lista")
        cel.telas["lista"] = ([el("Mae", 200)], {"Mae": "chat_mae"})  # "Você" ainda não aparece

        def depois_de_voltar(cmd, orig=cel.injetar):
            r = orig(cmd)
            if cmd == "tecla 4":
                cel.telas["lista"] = telas["lista"]  # agora aparece
            return r
        cel.injetar = depois_de_voltar
        r = self.executor(cel, escolher).executar(pedido)
        self.assertEqual(r["estado"], "concluido")
        import json as _j
        with open(self.mem) as f:
            memoria = list(_j.load(f).values())[0]
        self.assertEqual(sorted(memoria.values()), ["Você"])  # o desvio por "Mae" não foi aprendido

    def test_escada_de_cerebros_sobe_quando_a_tela_ja_falhou(self):
        cel = Celular(TELAS, "inicio")
        cel.falhar = {"Sistema": 99}  # o modelo escolhe "Sistema", que não responde
        vistos = []

        def escolher(opcoes):
            vistos.append(list(opcoes))
            return opcoes.index("Sistema") if "Sistema" in opcoes else opcoes.index("Bluetooth")
        r = self.executor(cel, escolher).executar(
            {"objetivo": "abrir o Bluetooth", "app": APP, "concluido": {"texto": "AirPods"}})
        self.assertEqual(r["estado"], "concluido")
        self.assertEqual(self.niveis[0], "forte")
        self.assertIn("maximo", self.niveis[1:])  # depois da falha, Opus pensando
        r = self.executor(Celular(TELAS, "inicio"), lambda o: o.index("Bluetooth")).executar(
            {"objetivo": "ver os fones conectados", "app": APP, "concluido": {"texto": "AirPods"}, "cerebro": "maximo"})
        self.assertEqual(self.niveis[-1], "maximo")  # pedido explícito: Opus pensando
        self.assertEqual(set(self.m.NIVEIS), {"rapido", "padrao", "forte", "maximo"})

    def test_botoes_de_info_do_app_sao_proibidos(self):
        for r in ("Forçar parada", "Limpar dados", "Desinstalar", "Desativar", "Desligar"):
            self.assertTrue(self.m.proibido(r), r)
        for r in ("Armazenamento", "Notificações", "Sobre o telefone", "Apps"):
            self.assertFalse(self.m.proibido(r), r)

    def test_toque_que_abre_outro_app_faz_parte_do_caminho(self):
        # HyperOS: Configurações → "Apps" abre com.miui.securitycenter. Não é "app errado": foi o nosso toque.
        seg = "com.miui.securitycenter"
        telas = {"inicio": ([el("Apps", 300)], {"Apps": "gerenciar"}),
                 "gerenciar": ([el("WhatsApp", 300, pacote=seg)], {"WhatsApp": "info"}),
                 "info": ([el("WhatsApp", 100, clic=False, pacote=seg), el("Forçar parada", 900, pacote=seg)], {})}
        cel = Celular(telas, "inicio")
        orig = cel.injetar

        def injetar(cmd):
            r = orig(cmd)
            cel.app = seg if cel.atual in ("gerenciar", "info") else APP
            return r
        cel.injetar = injetar
        r = self.executor(cel).executar({"objetivo": "info do WhatsApp", "app": APP,
                                         "concluido": {"texto": "Forçar parada"}, "pistas": ["Apps", "WhatsApp"]})
        self.assertEqual(r["estado"], "concluido")
        self.assertEqual(r["recuperacoes"], 0)
        self.assertFalse(any(p["acao"] == "tocar" and p.get("alvo") == "Forçar parada" for p in r["passos"]))
        self.assertIn("Forçar parada", r["tela"]["textos"])

    def test_rolagem_continua_sem_perguntar_ao_modelo_a_cada_tela(self):
        lista = [f"App {chr(65 + i)}" for i in range(12)] + ["WhatsApp"]
        telas = {}
        for k in range(0, len(lista), 3):
            nome = f"p{k}"
            itens = [el(t, 200 + 100 * j) for j, t in enumerate(lista[k:k + 3])]
            prox = {"<rolar>": f"p{k + 3}"} if k + 3 < len(lista) else {}
            prox.update({t: "info" for t in lista[k:k + 3] if t == "WhatsApp"})
            telas[nome] = (itens + [el("Lista", 800, clic=False, rolavel=True, a=1500)], prox)
        telas["info"] = ([el("Forçar parada", 900)], {})
        r = self.executor(Celular(telas, "p0"), lambda o: o.index("WhatsApp") if "WhatsApp" in o else o.index(
            "↓ rolar para baixo")).executar({"objetivo": "abrir informações do WhatsApp", "app": APP,
                                              "concluido": {"texto": "Forçar parada"}, "max_passos": 12})
        self.assertEqual(r["estado"], "concluido")
        self.assertLessEqual(r["consultas_modelo"], 2)  # 1ª: rolar; depois rola sozinho até aparecer "WhatsApp"
        self.assertIn("rolagem contínua", [p["via"] for p in r["passos"]])

    def test_validacao(self):
        ex = self.executor(Celular(TELAS, "inicio"))
        self.assertNotIn("erro", ex.executar({"objetivo": "x"}))  # sem critério: o modelo julga (1.0.102)
        self.assertIn("erro", ex.executar({"objetivo": "x", "concluido": {"nada": 1}}))
        self.assertIn("erro", ex.executar({"objetivo": "x", "pergunta": ""}))
        self.assertIn("erro", ex.executar({"concluido": {"texto": "x"}}))
        self.assertIn("erro", ex.executar({"objetivo": "x", "concluido": {"texto": "y"}, "pistas": "nao-lista"}))


if __name__ == "__main__":
    unittest.main()


class TestPilotoVisao(unittest.TestCase):
    """Piloto com visão: pergunta desenhada (Mental Math Master, 21/11) → recorte → modelo de visão no celular →
    conta feita no celular → toque. Sem a nuvem do Claude no laço."""

    def setUp(self):
        spec = importlib.util.spec_from_file_location("tela_piloto_teste", CAP / "piloto.py")
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)

    def tela(self):
        def b(t, x):
            return {"texto": t, "desc": "", "clicavel": True, "x": x, "y": 2538, "l": 250, "a": 250, "pacote": "g"}
        return [{"texto": "", "desc": "", "clicavel": True, "x": 640, "y": 906, "l": 1100, "a": 560, "pacote": "g"},
                {"texto": "9", "desc": "", "clicavel": False, "x": 640, "y": 1660, "l": 60, "a": 80, "pacote": "g"},
                {"texto": "", "desc": "", "clicavel": True, "x": 692, "y": 2265, "l": 700, "a": 180, "pacote": "g"},
                {"texto": "Parar Cronômetro (10)", "desc": "", "clicavel": False, "x": 692, "y": 2265, "l": 400,
                 "a": 80, "pacote": "g"},
                b("19", 239), b("20", 639), b("16", 1040)]

    def test_conta_e_escolha(self):
        m = self.m
        self.assertEqual(m.calcular("(5 × 3) + 4"), 19)
        self.assertEqual(m.calcular("74 + 12"), 86)
        self.assertEqual(m.calcular("2^3 - 1"), 7)
        self.assertIsNone(m.calcular("__import__('os')"))
        ops = [{"texto": "19"}, {"texto": "20"}, {"texto": "16"}]
        self.assertEqual(m.escolher_pela_conta("(5*3)+4\n1", ops), (0, "visao+conta"))
        self.assertEqual(m.escolher_pela_conta("ilegível\n2", ops), (1, "visao"))  # cai no número do modelo
        self.assertEqual(m.escolher_pela_conta("(5*3)+4\n3", ops), (0, "visao+conta"))  # a conta manda

    def test_quiz_sem_pergunta_e_caixa(self):
        m = self.m
        self.assertIsNone(m.quiz_da_tela(self.tela()))
        perg, ops = m.quiz_da_tela(self.tela(), sem_pergunta=True)
        self.assertIsNone(perg)
        self.assertEqual([o["texto"] for o in ops], ["19", "20", "16"])
        self.assertEqual(m.caixa_da_pergunta(self.tela(), ops), [90, 626, 1100, 560])

    def test_rodada_por_visao_toca_a_certa(self):
        m = self.m
        toques = []
        f = {"capturar": lambda caixa: "QUJD", "tocar": lambda x, y: toques.append((x, y))}
        p = m.Piloto(f)
        p.cfg = {}

        class Cer:
            def visao(self, b64, opcoes, modelo):
                return "(5 x 3) + 4\n2"
        p.cerebros = Cer()
        p._ultima_visao, p._ultimas_opcoes, p._ultima_expr, p._ultimo_toque = None, None, None, 0.0
        _, ops = m.quiz_da_tela(self.tela(), sem_pergunta=True)
        self.assertTrue(p._responder_por_visao(self.tela(), ops))
        self.assertEqual(toques, [(239, 2538)])  # 19, pela conta (o modelo disse 2, errado)
        self.assertFalse(p._responder_por_visao(self.tela(), ops))  # a mesma pergunta não é respondida 2×
        f["capturar"] = lambda caixa: "OUTRA"  # tela de feedback (imagem diferente, mesmas opções): não toca
        self.assertFalse(p._responder_por_visao(self.tela(), ops))
        self.assertEqual(len(toques), 1)

    def test_visao_sem_leitura_nao_chuta_e_continuar_por_texto(self):
        m = self.m
        toques = []
        f = {"capturar": lambda caixa: "QUJD", "tocar": lambda x, y: toques.append((x, y))}
        p = m.Piloto(f)
        p.cfg = {"continuar": [{"se": "Jogar Novamente", "tocar": "Jogar Novamente"}], "pausa_continuar": 0}

        class Cer:
            def visao(self, b64, opcoes, modelo):
                return ""  # tela em transição: nada legível
        p.cerebros = Cer()
        p._ultima_visao, p._ultimas_opcoes, p._ultima_expr, p._ultimo_toque = None, None, None, 0.0
        _, ops = m.quiz_da_tela(self.tela(), sem_pergunta=True)
        self.assertFalse(p._responder_por_visao(self.tela(), ops))
        self.assertEqual(toques, [])  # sem chute (o chute perdeu a rodada em 22/11)
        fim = [{"texto": "Recarregar Paradas", "x": 100, "y": 2000}, {"texto": "Jogar Novamente", "x": 640, "y": 2400}]
        self.assertTrue(p._continuar(fim))
        self.assertEqual(toques, [(640, 2400)])


CHROME = "com.android.chrome"


def web(y=1400, a=2200):
    """O nó que o Chrome expõe para a página inteira (22/11): sem texto dentro, só a descrição."""
    return {"texto": "", "desc": "Visualização na Web", "id": "", "classe": "WebView", "clicavel": False,
            "x": 640, "y": y, "l": 1280, "a": a, "pacote": CHROME, "editavel": False, "rolavel": False}


class CelularWeb(Celular):
    """Celular com páginas web: a acessibilidade só mostra a barra e o nó da página; a captura mostra o conteúdo
    (aqui, o nome da tela e quanto rolou, em base64). Links da página: tela → [(x, y, próxima)]."""

    def __init__(self, telas, inicio, links=None, fundo=None):
        super().__init__(telas, inicio, app=CHROME)
        self.links, self.fundo = links or {}, fundo or {}
        self.rolado = 0
        self.capturas = []

    def capturar(self, largura, recorte=None):
        import base64
        self.capturas.append((largura, recorte))
        return base64.b64encode(f"{self.atual}:{self.rolado}".encode()).decode(), 1280 / largura

    def injetar(self, cmd):
        partes = cmd.split()
        if partes[0] == "deslizar" and any(e.get("classe") == "WebView" for e in self.telas[self.atual][0]):
            self.injetados.append(cmd)
            if self.rolado < self.fundo.get(self.atual, 0):
                self.rolado += 1
            return True
        if partes[0] == "tocar":
            x, y = int(partes[1]), int(partes[2])
            for lx, ly, prox in self.links.get(self.atual, []):
                if abs(lx - x) <= 40 and abs(ly - y) <= 40:
                    self.injetados.append(cmd)
                    self.pilha.append(self.atual)
                    self.atual, self.rolado = prox, 0
                    return True
        return super().injetar(cmd)


def estado_da_captura(b64):
    import base64
    tela, rolado = base64.b64decode(b64).decode().split(":")
    return tela, int(rolado)


BARRA = el("google.com/search?q=dolar", 243, pacote=CHROME, editavel=False)


class TestObjetivoVisaoEGrafo(unittest.TestCase):
    def setUp(self):
        self.m = _carregar()
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.olhadas, self.julgados, self.decisoes = [], [], []

    def executor(self, cel, olhar=None, julgar=None, decidir=None, grafo=True):
        def dec(objetivo, resumo, opcoes, nivel="padrao"):
            self.decisoes.append(list(opcoes))
            return decidir(opcoes) if decidir else None

        def olh(objetivo, pergunta, contexto, b64, opcoes, nivel):
            self.olhadas.append((estado_da_captura(b64), list(opcoes)))
            return olhar(estado_da_captura(b64), opcoes) if olhar else {}

        def jul(objetivo, pergunta, textos, b64, nivel):
            self.julgados.append((pergunta, list(textos), b64 is not None))
            return julgar(textos, b64) if julgar else {}
        return self.m.Executor(cel, dec, os.path.join(self.tmp, "objetivos.json"), olhar=olh, julgar=jul,
                               grafo_arq=os.path.join(self.tmp, "grafo.json") if grafo else None)

    def test_sugestoes_da_busca_nao_concluem(self):
        # 22/11, POCO: "cotação do dólar hoje em real" (sugestão) concluía {qualquer:["Real"]} antes do resultado
        telas = {"busca": ([el("", 100, editavel=True, pacote=CHROME)], {"<enter>": "sugestoes"}),
                 "sugestoes": ([el("cotação do dólar hoje", 100, editavel=True, pacote=CHROME),
                                el("cotação do dólar hoje em real", 300, pacote=CHROME)], {"<rolar>": "res"}),
                 "res": ([el("1 Dólar americano igual a 5,99 Real brasileiro", 400, pacote=CHROME)], {})}
        telas["sugestoes"][0].append(el("Lista", 800, clic=False, rolavel=True, a=1500, pacote=CHROME))
        cel = Celular(telas, "busca", app=CHROME)
        r = self.m.Executor(cel, None, None).executar(
            {"objetivo": "cotação do dólar", "app": CHROME, "digitar": "cotação do dólar hoje",
             "concluido": {"qualquer": ["Real"]}, "modelo": False})
        self.assertEqual(r["estado"], "concluido")
        self.assertEqual(cel.atual, "res")  # só concluiu na página de resultado

    def test_pagina_web_cega_a_visao_toca_rola_e_le_a_resposta(self):
        telas = {"busca": ([BARRA, web()], {}), "pagina": ([BARRA, web()], {})}
        links = {"busca": [(640, 900, "pagina")]}
        cel = CelularWeb(telas, "busca", links, fundo={"pagina": 2})

        def olhar(estado, opcoes):
            tela, rolado = estado
            if tela == "busca":
                return {"acao": "tocar", "x": 360, "y": 506, "rotulo": "Cotação do dólar - resultado", "fonte": "v"}
            if rolado < 2:
                return {"acao": "rolar", "fonte": "v"}
            return {"feito": True, "resposta": "US$ 1 = R$ 5,99", "fonte": "v"}
        r = self.executor(cel, olhar).executar({"objetivo": "ler a cotação do dólar", "app": CHROME,
                                                "pergunta": "quanto vale 1 dólar em reais?"})
        self.assertEqual((r["estado"], r["conclusao"], r["resposta"]), ("concluido", "visao", "US$ 1 = R$ 5,99"))
        self.assertEqual([p["acao"] for p in r["passos"]], ["tocar", "rolar", "rolar", "concluir"])
        self.assertIn("tocar 640 900", cel.injetados)  # 360×(1280/720) = 640: coordenada da imagem → tela
        self.assertEqual(r["visoes"], 4)
        self.assertTrue(all(o[1] == [] or "Visualização na Web" not in o[1] for o in self.olhadas))

    def test_visao_nao_toca_em_efeito_externo_nem_fora_da_pagina(self):
        telas = {"loja": ([BARRA, web()], {})}
        cel = CelularWeb(telas, "loja", {"loja": [(640, 900, "comprado"), (640, 243, "barra")]})
        cel.telas["comprado"] = ([el("Pedido feito", 300, pacote=CHROME)], {})
        respostas = iter([{"acao": "tocar", "x": 360, "y": 506, "rotulo": "Comprar agora"},
                          {"acao": "tocar", "x": 360, "y": 136, "rotulo": "barra de endereço"}])
        r = self.executor(cel, lambda e, o: next(respostas, {})).executar(
            {"objetivo": "ver o produto", "app": CHROME, "concluido": {"texto": "Pedido feito"}, "max_passos": 4})
        self.assertNotEqual(cel.atual, "comprado")
        self.assertFalse(any(c.startswith("tocar") for c in cel.injetados))
        self.assertNotEqual(r["estado"], "concluido")

    def test_modelo_diz_cumprido_e_a_leitura_extrai_a_resposta(self):
        telas = {"inicio": ([el("Bateria", 100), el("85% — cerca de 1 dia", 200, clic=False)], {})}

        def decidir(opcoes):
            return opcoes.index(self.m.CUMPRIDO)
        r = self.executor(Celular(telas, "inicio"), decidir=decidir,
                          julgar=lambda textos, b64: {"feito": True, "resposta": "85%"}).executar(
            {"objetivo": "ver a bateria", "app": APP, "pergunta": "qual a porcentagem da bateria?"})
        self.assertEqual((r["estado"], r["conclusao"], r["resposta"]), ("concluido", "modelo", "85%"))
        self.assertIn(self.m.CUMPRIDO, self.decisoes[0])
        self.assertEqual(self.julgados[0][0], "qual a porcentagem da bateria?")
        self.assertIn("85% — cerca de 1 dia", self.julgados[0][1])

    def test_leitura_que_discorda_nao_conclui(self):
        telas = {"inicio": ([el("Bateria", 100), el("Lista", 800, clic=False, rolavel=True, a=1500)],
                            {"<rolar>": "baixo"}),
                 "baixo": ([el("Uso: 85%", 200, clic=False)], {})}
        def decidir(opcoes):  # modelo apressado: diz "cumprido" sempre que pode; senão rola
            return opcoes.index(self.m.CUMPRIDO if self.m.CUMPRIDO in opcoes else self.m.ROLAR)
        r = self.executor(Celular(telas, "inicio"), decidir=decidir,
                          julgar=lambda textos, b64: ({"feito": True, "resposta": "85%"}
                                                      if any("85%" in t for t in textos) else {"feito": False})
                          ).executar({"objetivo": "ver o uso da bateria", "app": APP, "pergunta": "qual o uso?"})
        self.assertEqual((r["estado"], r.get("resposta")), ("concluido", "85%"))
        self.assertIn("conferir", [p["acao"] for p in r["passos"]])  # 1ª vez: "cumprido" recusado pela leitura

    def test_criterio_local_com_pergunta_le_a_resposta_no_fim(self):
        r = self.executor(Celular(TELAS, "inicio"), julgar=lambda textos, b64: {"feito": True, "resposta": "POCO"}
                          ).executar({"objetivo": "ver o modelo", "app": APP, "concluido": {"texto": "Modelo:"},
                                      "pistas": ["Sobre o telefone"], "pergunta": "qual o modelo?", "modelo": False})
        self.assertEqual((r["estado"], r["conclusao"], r["resposta"]), ("concluido", "criterio", "POCO"))
        self.assertEqual(len(self.julgados), 1)

    def test_grafo_leva_objetivo_parecido_ao_destino_sem_modelo(self):
        def escolher(opcoes):
            for alvo in ("Atualizações", "Sistema"):
                if alvo in opcoes:
                    return opcoes.index(alvo)
            return None
        ex = self.executor(Celular(TELAS, "inicio"), decidir=escolher)
        r = ex.executar({"objetivo": "ver a versão do sistema", "app": APP, "concluido": {"texto": "Versão"}})
        self.assertEqual(r["estado"], "concluido")
        self.decisoes.clear()
        # outras palavras, mesmo destino: o grafo acha o caminho sem perguntar ao modelo
        r2 = self.executor(Celular(TELAS, "inicio"), decidir=escolher).executar(
            {"objetivo": "versão do sistema", "app": APP, "concluido": {"texto": "Versão"}})
        self.assertEqual((r2["estado"], r2["consultas_modelo"]), ("concluido", 0))
        self.assertEqual([p["via"] for p in r2["passos"]], ["grafo", "grafo"])
        resumo = self.m.Grafo(os.path.join(self.tmp, "grafo.json")).resumo()
        self.assertEqual(resumo["apps"][APP], 3)
        self.assertEqual(resumo["arestas"], 2)

    def test_grafo_parte_de_outra_tela_e_inclui_rolagem(self):
        ex = self.executor(Celular(TELAS, "inicio"))
        r = ex.executar({"objetivo": "ver o modelo do celular", "app": APP, "concluido": {"texto": "Modelo:"},
                         "pistas": ["Sobre o telefone"], "modelo": False})
        self.assertEqual([p["acao"] for p in r["passos"]], ["rolar", "tocar"])
        g = self.m.Grafo(os.path.join(self.tmp, "grafo.json"))
        inicio = self.m.assinatura(Celular(TELAS, "inicio").elementos("inicio"), APP)
        baixo = self.m.assinatura(Celular(TELAS, "inicio").elementos("inicio_baixo"), APP)
        destinos = g.destinos(APP, "modelo do celular")
        self.assertEqual(g.proximo(APP, inicio, destinos), self.m.ROLAR)
        self.assertEqual(g.proximo(APP, baixo, destinos), "Sobre o telefone")  # já no meio do caminho
        self.assertEqual(g.destinos(APP, "ligar o wi-fi"), [])  # nada parecido

    def test_visao_digita_de_novo_o_texto_autorizado_numa_pagina_nova(self):
        # 23/11, POCO: o modelo de texto tocou "Nova guia"; na guia nova a visão queria buscar de novo e não podia
        campo = el("", 700, editavel=True, pacote=CHROME)
        telas = {"busca": ([el("", 100, editavel=True, pacote=CHROME)], {"<enter>": "nova"}),
                 "nova": ([BARRA, web(), campo], {"<enter>": "res"}),
                 "res": ([BARRA, web()], {})}
        cel = CelularWeb(telas, "busca")

        def olhar(estado, opcoes):
            if estado[0] == "nova":
                return {"acao": "digitar", "x": 169, "y": 394, "rotulo": "Pesquisar"}  # 300×(720/1280), 700×…
            if estado[0] == "res":
                return {"feito": True, "resposta": "R$ 5,99"}
            return {}
        r = self.executor(cel, olhar).executar({"objetivo": "cotação do dólar", "app": CHROME,
                                                "digitar": "dolar hoje", "pergunta": "quanto?"})
        self.assertEqual((r["estado"], r["resposta"]), ("concluido", "R$ 5,99"))
        self.assertEqual([p["acao"] for p in r["passos"]], ["digitar", "digitar", "concluir"])
        self.assertEqual(cel.digitado, "dolar hojedolar hoje")  # o mesmo texto autorizado, uma vez a mais
        # e só uma vez a mais: a terceira tentativa é recusada e anotada
        cel = CelularWeb({"busca": telas["busca"], "nova": ([BARRA, web(), campo], {"<enter>": "nova"})}, "busca")
        r = self.executor(cel, lambda e, o: {"acao": "digitar", "x": 169, "y": 394}).executar(
            {"objetivo": "cotação do dólar", "app": CHROME, "digitar": "dolar hoje", "max_passos": 6})
        self.assertEqual(sum(p["acao"] == "digitar" for p in r["passos"]), 2)
        self.assertIn("visao_recusada", r["visao_diag"])

    def test_area_cega(self):
        self.assertIsNotNone(self.m.area_cega([BARRA, web()]))
        cheia = [BARRA, web()] + [el(f"linha {k}", 600 + k * 100, pacote=CHROME) for k in range(5)]
        self.assertIsNone(self.m.area_cega(cheia))  # o Chrome expôs o texto da página: não precisa de imagem
        self.assertIsNone(self.m.area_cega([el("Wi-Fi", 200), el("Bluetooth", 300)]))
        self.assertEqual(self.m.area_cega([el("x", 10)], [[0, 0, 10, 10]]), [0, 0, 10, 10])


class TestAreaCegaComTeclado(unittest.TestCase):
    def test_teclado_aberto_por_cima_nao_descreve_a_pagina(self):
        m = _carregar()
        teclas = [el(t, 2300, pacote="com.google.android.inputmethod.latin") for t in "qwertyuiop"]
        self.assertIsNotNone(m.area_cega([BARRA, web()] + teclas))  # 23/11: sem isto, a visão não entrava
