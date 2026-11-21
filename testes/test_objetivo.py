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
        memoria = list(_j.load(open(self.mem)).values())[0]
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

    def test_validacao(self):
        ex = self.executor(Celular(TELAS, "inicio"))
        self.assertIn("erro", ex.executar({"objetivo": "x"}))  # sem critério de conclusão
        self.assertIn("erro", ex.executar({"concluido": {"texto": "x"}}))
        self.assertIn("erro", ex.executar({"objetivo": "x", "concluido": {"texto": "y"}, "pistas": "nao-lista"}))


if __name__ == "__main__":
    unittest.main()
