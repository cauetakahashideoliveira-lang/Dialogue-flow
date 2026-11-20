"""Testes do controle-ir (rodar na raiz: python3 -m unittest discover -s testes -v)."""
from __future__ import annotations

import base64
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "controle-ir"))

from controle_ir import catalogo, formatos, protocolos, vocabulario  # noqa: E402
from controle_ir.controle import Controlador, executar  # noqa: E402
from controle_ir.emissor import EmissorSimulado  # noqa: E402
from controle_ir.servico import Servico  # noqa: E402
from controle_ir.servidor import criar_servidor  # noqa: E402
from controle_ir.sinais import Sinal, broadlink_para_pulsos, pronto_para_pulsos, pulsos_para_broadlink, \
    pulsos_para_pronto  # noqa: E402

BASE = RAIZ / "controle-ir" / "dados" / "base.jsonl.gz"
_CAT_CACHE = {}


def catalogo_base() -> str:
    """Catálogo SQLite com o pacote base (montado uma vez por execução)."""
    if "arq" not in _CAT_CACHE:
        d = tempfile.mkdtemp(prefix="cir-cat-")
        c = catalogo.Catalogo(Path(d) / "catalogo.sqlite")
        catalogo.importar_jsonl(c, str(BASE))
        c.fechar()
        _CAT_CACHE["arq"] = str(Path(d) / "catalogo.sqlite")
    return _CAT_CACHE["arq"]


def novo_servico(emissor=None, com_base=True):
    pasta = tempfile.mkdtemp(prefix="cir-")
    if com_base:
        shutil.copy(catalogo_base(), Path(pasta) / "catalogo.sqlite")
    s = Servico(pasta, emissor or EmissorSimulado())
    s.exec.politica.armar()  # instalação nova nasce desarmada; os testes de função partem do sistema armado
    return s, pasta


class TestProtocolos(unittest.TestCase):
    def test_ida_e_volta_todos_os_protocolos(self):
        rnd = random.Random(7)
        for p in protocolos.PROTOCOLOS:
            na, nc = protocolos.TAMANHOS[p]
            for _ in range(200):
                a, c = rnd.getrandbits(na), rnd.getrandbits(nc)
                if p == "RC5X":
                    c |= 0x40
                f, d = protocolos.codificar(p, a, c)
                self.assertEqual(protocolos.decodificar(d, f), (p, a, c), p)

    def test_nec_bits_lsb_primeiro(self):
        f, d = protocolos.codificar("NEC", 0x04, 0x08)
        self.assertEqual(f, 38000)
        self.assertEqual(d[:2], [9000, 4500])
        # endereço 0x04 = 00100000 em LSB primeiro → terceiro bit é 1
        espacos = d[3:3 + 16:2]
        self.assertEqual([1 if s > 1000 else 0 for s in espacos], [0, 0, 1, 0, 0, 0, 0, 0])
        self.assertEqual(len(d), 2 + 64 + 1)

    def test_sony_repete_tres_quadros(self):
        f, d = protocolos.codificar("SIRC", 1, 0x15)
        self.assertEqual(f, 40000)
        self.assertEqual(sum(1 for x in d if x == 2400), 3)

    def test_decodifica_captura_real_com_ruido(self):
        f, d = protocolos.codificar("Samsung32", 0x07, 0x02)
        rnd = random.Random(1)
        ruido = [max(50, int(x * rnd.uniform(0.9, 1.1))) for x in d]
        self.assertEqual(protocolos.decodificar(ruido), ("Samsung32", 7, 2))


class TestFormatos(unittest.TestCase):
    IR = """Filetype: IR signals file
Version: 1
#
name: Power
type: parsed
protocol: NECext
address: BA A0 00 00
command: 4C B3 00 00
#
name: Vol_up
type: raw
frequency: 38000
duty_cycle: 0.330000
data: 9000 4500 560 560 560 560 560 1690 560 560 560 560 560 560 560 560 560 560 560 1690 560 1690 560 560 560 1690 560 1690 560 1690 560 1690 560 1690 560 560 560 560 560 560 560 1690 560 560 560 560 560 560 560 560 560 1690 560 1690 560 1690 560 560 560 1690 560 1690 560 1690 560 1690 560
#
name: Power
type: parsed
protocol: NEC
address: 04 00 00 00
command: 08 00 00 00
#
name: Netflix
type: raw
frequency: 38000
duty_cycle: 0.33
data: 1000 500 1000 500 3000
"""

    def test_flipper_ler_e_exportar(self):
        p = formatos.ler_flipper(self.IR, "t", "TV teste", "tv", "Teste")
        chaves = [c["chave"] for c in p["comandos"]]
        self.assertEqual(chaves, ["energia_alternar", "volume_mais", "energia_alternar_2", "netflix"])
        # captura bruta reconhecida como NEC vira forma compacta
        self.assertIn("protocolo", p["comandos"][1]["sinal"])
        texto = formatos.escrever_flipper(p)
        p2 = formatos.ler_flipper(texto, "t2")
        self.assertEqual([Sinal(c["sinal"]).impressao() for c in p["comandos"]],
                         [Sinal(c["sinal"]).impressao() for c in p2["comandos"]])

    def test_captura_corrompida_nao_derruba_importacao(self):
        texto = self.IR + """#
name: Quebrado
type: raw
frequency: 38000
duty_cycle: 0.33
data: 1073741453 500
"""
        p = formatos.ler_flipper(texto, "t")
        self.assertEqual(len(p["comandos"]), 4)
        self.assertEqual(p["descartados"], 1)

    def test_pronto_e_broadlink(self):
        f, d = protocolos.codificar("NEC", 0x10, 0x22)
        pr = pulsos_para_pronto(f, d)
        f2, d2 = pronto_para_pulsos(pr)
        self.assertEqual(protocolos.decodificar(d2), ("NEC", 0x10, 0x22))
        self.assertLess(abs(f2 - 38000), 400)
        bl = pulsos_para_broadlink(d)
        _, d3 = broadlink_para_pulsos(bl)
        self.assertEqual(protocolos.decodificar(d3), ("NEC", 0x10, 0x22))

    def test_texto_bruto_detectado(self):
        s = formatos.ler_sinal_texto("38000: +9000 -4500 +560 -560 +560 -1690 +560")
        self.assertEqual(s["frequencia"], 38000)
        self.assertEqual(s["pulsos"], [9000, 4500, 560, 560, 560, 1690, 560])
        f, d = protocolos.codificar("RC6", 0, 12)
        self.assertEqual(formatos.ler_sinal_texto(json.dumps(d)), {"protocolo": "RC6", "endereco": 0, "comando": 12})

    def test_importar_smartir_climate(self):
        dados = {"manufacturer": "X", "supportedModels": ["A1"], "supportedController": "Broadlink",
                 "commandsEncoding": "Base64", "minTemperature": 22, "maxTemperature": 23, "precision": 1,
                 "operationModes": ["cool"], "fanModes": ["low", "auto"],
                 "commands": {"off": pulsos_para_broadlink(protocolos.codificar("NEC", 1, 1)[1]),
                              "cool": {f: {str(t): pulsos_para_broadlink(protocolos.codificar("NEC", 1, t + i)[1])
                                           for t in (22, 23)} for i, f in enumerate(("low", "auto"))}}}
        p = formatos.importar_texto(json.dumps(dados))
        ec = p["estado_completo"]
        self.assertEqual(ec["parametros"]["modo"], ["frio"])
        self.assertEqual(ec["parametros"]["ventilacao"], ["baixa", "automatica"])
        self.assertEqual(len(ec["estados"]), 4)


class TestVocabulario(unittest.TestCase):
    def test_nomes(self):
        casos = {"Power": "energia_alternar", "VOL+": "volume_mais", "vol_dn": "volume_menos", "Ch_next": "canal_mais",
                 "HDMI2": "entrada_hdmi2", "Speed_3": "velocidade_3", "Speed_dn": "velocidade_menos",
                 "Rotation": "oscilacao_alternar", "Blue": "cor_azul", "Brightness+": "brilho_mais",
                 "Cool_hi": "ar_frio_forte", "Power_off": "energia_desligar", "volumeUp": "volume_mais",
                 "Prog+": "canal_mais", "Shutter": "disparo"}
        for nome, chave in casos.items():
            self.assertEqual(vocabulario.interpretar(nome).chave, chave, nome)

    def test_risco(self):
        for n in ("Factory Reset", "Service Menu", "EEPROM", "Hotel mode"):
            self.assertTrue(vocabulario.interpretar(n).risco, n)
        self.assertFalse(vocabulario.interpretar("Menu").risco)

    def test_valores(self):
        self.assertEqual(vocabulario.valores_equivalentes("baixa", ["low", "mid", "high"]), ["low"])
        self.assertEqual(vocabulario.valores_equivalentes("frio", ["frio", "calor"]), ["frio"])
        self.assertEqual(vocabulario.valores_equivalentes(True, ["ligado", "desligado"]), ["ligado"])
        self.assertEqual(vocabulario.categoria_canonica("fita LED"), "iluminacao")
        self.assertEqual(vocabulario.categoria_canonica("ar do quarto"), "ar_condicionado")


class TestCatalogo(unittest.TestCase):
    def test_dedup_preserva_associacoes(self):
        d = tempfile.mkdtemp()
        c = catalogo.Catalogo(Path(d) / "c.sqlite")
        bruto = {"frequencia": 38000, "pulsos": protocolos.codificar("NEC", 9, 3)[1]}
        for i, s in enumerate(({"protocolo": "NEC", "endereco": 9, "comando": 3}, bruto)):
            p = formatos.novo_perfil(f"p{i}", f"P{i}", "tv", f"Marca{i}")
            formatos.adicionar_comando(p, formatos.comando("Power", s))
            c.adicionar_perfil(p)
        c.commit()
        self.assertEqual(c.estatisticas()["sinais_unicos"], 1)
        g = c.candidatos(["energia_alternar"])
        self.assertEqual(len(g), 1)
        self.assertEqual(len(g[0]["perfis"]), 2)

    def test_catalogo_base_tem_categorias_variadas(self):
        c = catalogo.Catalogo(catalogo_base())
        cats = c.estatisticas()["categorias"]
        for k in ("ar_condicionado", "tv", "ventilador", "iluminacao", "projetor"):
            self.assertIn(k, cats)


class TestControle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = catalogo.Catalogo(catalogo_base())

    def aparelho(self, chave, nome="x", faixas=None):
        from controle_ir.aparelhos import Aparelhos
        a = Aparelhos(Path(tempfile.mkdtemp()) / "a.json")
        ap = a.novo(nome, self.cat.perfil(chave))
        if faixas:
            ap["faixas"] = faixas
        ap["config"]["intervalo_teclas"] = 0
        ap["config"]["espera_apos_ligar"] = 0
        return ap

    def test_ar_estado_completo_e_mudanca_parcial(self):
        ap = self.aparelho("smartir:climate/1382", "ar do quarto")
        em = EmissorSimulado()
        ctrl = Controlador(ap)
        r = executar(ap, ctrl.planejar({"ligar": True, "definir": {"temperatura": 23, "modo": "frio",
                                                                   "ventilacao": "baixa"}}), em)
        self.assertEqual(r["status"], "sinal_enviado")
        self.assertEqual(len(em.enviados), 1)  # uma única transmissão com tudo
        self.assertEqual(r["configuracao"]["valores"], {"modo": "frio", "temperatura": 23, "ventilacao": "baixa"})
        r2 = executar(ap, Controlador(ap).planejar({"definir": {"temperatura": 22}}), em)
        self.assertEqual(r2["configuracao"]["valores"], {"modo": "frio", "temperatura": 22, "ventilacao": "baixa"})
        self.assertEqual(r2["configuracao"]["origem"]["modo"], "mantido do último envio")
        esperado = next(e for e in ap["perfil"]["estado_completo"]["estados"]
                        if e["modo"] == "frio" and e["temperatura"] == 22 and e["ventilacao"] == "baixa")
        self.assertEqual(em.enviados[-1], Sinal(esperado["sinal"]).transmissao())
        r3 = executar(ap, Controlador(ap).planejar({"definir": {"oscilacao": "ligado"}}), em)
        self.assertEqual(r3["status"], "nada_enviado")
        self.assertTrue(any("oscila" in x for x in r3["nao_suportado"]))
        r4 = executar(ap, Controlador(ap).planejar({"ligar": False}), em)
        self.assertEqual(r4["status"], "sinal_enviado")
        self.assertEqual(em.enviados[-1], Sinal(ap["perfil"]["estado_completo"]["desligar"]).transmissao())

    def test_ar_com_oscilacao(self):
        ap = self.aparelho("smartir:climate/1396")
        r = executar(ap, Controlador(ap).planejar({"definir": {"modo": "frio", "temperatura": 24,
                                                               "oscilacao": "ligada"}}), EmissorSimulado())
        self.assertEqual(r["status"], "sinal_enviado")
        self.assertEqual(r["configuracao"]["valores"]["oscilacao"], "ligada")

    def test_ar_valor_invalido_nao_envia(self):
        ap = self.aparelho("smartir:climate/1382")
        em = EmissorSimulado()
        r = executar(ap, Controlador(ap).planejar({"definir": {"temperatura": 40}}), em)
        self.assertEqual(r["status"], "nada_enviado")
        self.assertEqual(em.enviados, [])

    def test_ventilador_alternancia_exige_estado(self):
        ap = self.aparelho("flipper:Fans/Domo/DOMO_DO8149.ir", "ventilador da sala")
        em = EmissorSimulado()
        r = executar(ap, Controlador(ap).planejar({"ligar": True}), em)
        self.assertEqual(r["status"], "precisa_confirmacao")
        self.assertEqual(em.enviados, [])
        r = executar(ap, Controlador(ap).planejar({"ligar": True, "estado_atual": {"energia": "desligado"}}), em)
        self.assertEqual(r["status"], "sinal_enviado")
        # agora o estado é presumido: pedir de novo não inverte
        r = executar(ap, Controlador(ap).planejar({"ligar": True}), em)
        self.assertEqual(r["status"], "nada_enviado")
        self.assertTrue(r["avisos"])

    def test_ventilador_velocidade_por_saturacao(self):
        ap = self.aparelho("flipper:Fans/Domo/DOMO_DO8149.ir", faixas={"velocidade": {"min": 1, "max": 3}})
        plano = Controlador(ap).planejar({"definir": {"velocidade": 2}})
        self.assertEqual([e.chave for e in plano.etapas],
                         ["velocidade_menos", "velocidade_menos", "velocidade_mais"])
        r = executar(ap, plano, EmissorSimulado())
        self.assertEqual(r["estado_presumido"]["velocidade"], "2")
        plano2 = Controlador(ap).planejar({"definir": {"velocidade": 3}})
        self.assertEqual([e.chave for e in plano2.etapas], ["velocidade_mais"])

    def test_ventilador_sem_faixa_explica(self):
        ap = self.aparelho("flipper:Fans/Domo/DOMO_DO8149.ir")
        plano = Controlador(ap).planejar({"definir": {"velocidade": 2}})
        self.assertTrue(plano.bloqueios)
        self.assertFalse(plano.etapas)

    def test_falha_no_meio_informa_enviados_e_pendentes(self):
        ap = self.aparelho("flipper:Fans/Domo/DOMO_DO8149.ir")
        em = EmissorSimulado(falhar_em={2})
        r = executar(ap, Controlador(ap).planejar({"ajustar": {"velocidade": 3}}), em)
        self.assertEqual(r["status"], "parcial")
        self.assertEqual(len(r["enviados"]), 1)
        self.assertEqual(len(r["pendentes"]), 2)
        self.assertEqual(r["falha"]["etapa"], 2)

    def test_projetor_hdmi2_tecla_direta(self):
        ap = self.aparelho("flipper:Projectors/NEC/NEC_RU_M124.ir")
        plano = Controlador(ap).planejar({"definir": {"entrada": "HDMI 2"}})
        self.assertEqual([e.chave for e in plano.etapas], ["entrada_hdmi2"])

    def test_fita_led_cor(self):
        ap = self.aparelho("flipper:LED_Lighting/Unknown/44_Button_LED.ir")
        plano = Controlador(ap).planejar({"definir": {"cor": "azul"}})
        self.assertEqual([e.chave for e in plano.etapas], ["cor_azul"])
        plano = Controlador(ap).planejar({"ajustar": {"volume": 2}})
        self.assertTrue(plano.nao_suportado)


class TestDescoberta(unittest.TestCase):
    def catalogo_sintetico(self):
        d = tempfile.mkdtemp()
        c = catalogo.Catalogo(Path(d) / "catalogo.sqlite")
        # três perfis compartilham o mesmo "liga/desliga"; volume distingue A de B/C; mudo distingue B de C
        specs = [("MarcaA TV1", "marcaa", 0x10, 0x11, 0x20), ("MarcaB TV2", "marcab", 0x10, 0x12, 0x21),
                 ("MarcaB TV3", "marcab", 0x10, 0x12, 0x22), ("Outra", "outra", 0x55, 0x56, 0x57)]
        for i, (nome, marca, pw, vol, mute) in enumerate(specs):
            p = formatos.novo_perfil(f"s{i}", nome, "tv", marca)
            for n, cmd in (("Power", pw), ("Vol_up", vol), ("Mute", mute), ("Factory reset", 0x99)):
                formatos.adicionar_comando(p, formatos.comando(n, {"protocolo": "NEC", "endereco": 1, "comando": cmd}))
            c.adicionar_perfil(p)
        c.commit()
        return c, d

    def test_fluxo_completo(self):
        cat, pasta = self.catalogo_sintetico()
        em = EmissorSimulado()
        srv = Servico(pasta, em, cat)
        r = srv.desc.iniciar(categoria="tv", intervalo=2, lote=10, iniciar_pausado=True)
        self.assertEqual(r["total"], 2)  # dois sinais de energia únicos
        srv.desc.s["estado"] = "executando"
        h1 = srv.desc.passo()
        h2 = srv.desc.passo()
        self.assertEqual((h1["n"], h2["n"]), (1, 2))
        # nenhum candidato usa o comando de serviço
        self.assertNotIn((1, 0x99), [(1, protocolos.decodificar(p)[2]) for _, p in em.enviados])
        p = srv.pausar()
        self.assertEqual(p["estado"], "pausado")
        self.assertEqual([s["numero"] for s in p["suspeitos"]], [1, 2])
        # o usuário reteste um a um e identifica o nº 1
        rt = srv.retestar([1])
        self.assertEqual(rt["retestes"][0]["novo_numero"], 3)
        c = srv.confirmar(3)
        self.assertEqual(c["perfis_possiveis"], 3)
        teste = c["testes_distincao"][0]
        self.assertIn(teste["teste"], ("volume_mais", "mudo_alternar"))
        # envia variantes até achar a que reage (simula: perfil “MarcaB TV3”)
        alvo = next(x for x in cat.nomes_perfis(list(range(1, 10))) if x["nome"] == "MarcaB TV3")["id"]
        for _ in range(3):
            st = srv.desc.s
            t = st["testes_distincao"][0]
            v = next(v for v in t["variantes"] if alvo in v["perfis"])
            d = srv.distinguir(t["teste"], v["variante"])
            c = srv.confirmar(d["numero"], True)
            if c.get("perfis_possiveis") == 1:
                break
        self.assertEqual(c["perfis_possiveis"], 1)
        self.assertEqual(c["exemplos"][0]["nome"], "MarcaB TV3")
        s = srv.salvar_aparelho("TV do quarto")
        self.assertEqual(s["perfil"], "MarcaB TV3")
        self.assertIn("volume", s["parametros"])

    def test_marca_filtra_e_lote(self):
        cat, pasta = self.catalogo_sintetico()
        srv = Servico(pasta, EmissorSimulado(), cat)
        r = srv.desc.iniciar(categoria="tv", marca="MarcaB", intervalo=2, lote=1, iniciar_pausado=True)
        self.assertEqual(r["total"], 1)
        self.assertEqual(r["filtros"]["marcas_filtradas"], ["marcab"])
        srv.desc.iniciar(categoria="tv", intervalo=2, lote=1, iniciar_pausado=True)
        srv.desc.s["estado"] = "executando"
        self.assertIsNotNone(srv.desc.passo())
        self.assertIsNone(srv.desc.passo())
        self.assertEqual(srv.desc.s["estado"], "lote_concluido")
        srv.retomar()
        time.sleep(0.4)
        srv.desc.parar_thread()
        self.assertEqual(srv.desc.s["cursor"], 2)

    def test_salvar_tecla_unica_e_descobrir_outras(self):
        cat, pasta = self.catalogo_sintetico()
        srv = Servico(pasta, EmissorSimulado(), cat)
        srv.desc.iniciar(categoria="tv", intervalo=2, iniciar_pausado=True)
        srv.desc.s["estado"] = "executando"
        h = srv.desc.passo()
        srv.confirmar(h["n"])
        s = srv.salvar_aparelho("tv velha", somente_confirmado=True)
        self.assertEqual(s["comandos"], 1)
        srv.desc.iniciar(modo="teclas", aparelho=srv.aparelhos.obter("tv velha"), intervalo=2,
                             iniciar_pausado=True)
        funcoes = {c.get("funcao_provavel") for c in srv.desc.s["candidatos"]}
        self.assertIn("Volume +", funcoes)
        self.assertNotIn("x_factory_reset", {k for c in srv.desc.s["candidatos"] for k in c["chaves"]})
        srv.desc.s["estado"] = "executando"
        h = srv.desc.passo()
        e = srv.editar_aparelho("tv velha", adicionar_comando={"nome": "volume +", "numero": h["n"]})
        self.assertTrue(e["alteracoes"])

    def test_adicionar_sinal_repetido_avisa_tecla_existente(self):
        cat, pasta = self.catalogo_sintetico()
        srv = Servico(pasta, EmissorSimulado(), cat)
        srv.desc.iniciar(categoria="tv", intervalo=2, iniciar_pausado=True)
        srv.desc.s["estado"] = "executando"
        srv.confirmar(srv.desc.passo()["n"])
        srv.salvar_aparelho("tv velha", somente_confirmado=True)
        sinal = {"protocolo": "Samsung32", "endereco": 7, "comando": 0x79}
        e1 = srv.editar_aparelho("tv velha", adicionar_comando={"nome": "Smart Hub", "funcao": "home", "sinal": sinal})
        self.assertIn("adicionado", e1["alteracoes"][0])
        n = len(srv.aparelhos.obter("tv velha")["perfil"]["comandos"])
        e2 = srv.editar_aparelho("tv velha", adicionar_comando={"nome": "Abrir o Smart Hub", "funcao": "home",
                                                                "sinal": sinal})
        self.assertTrue(e2["alteracoes"][0].startswith("nada adicionado"), e2)
        self.assertIn("inicio", e2["alteracoes"][0])
        self.assertEqual(len(srv.aparelhos.obter("tv velha")["perfil"]["comandos"]), n)

    def test_thread_pausa_imediata(self):
        cat, pasta = self.catalogo_sintetico()
        em = EmissorSimulado()
        srv = Servico(pasta, em, cat)
        srv.desc.iniciar(categoria="tv", intervalo=30, lote=10)
        time.sleep(0.5)
        t0 = time.monotonic()
        srv.pausar()
        srv.desc.thread.join(timeout=3)
        self.assertLess(time.monotonic() - t0, 3)
        self.assertEqual(len(em.enviados), 1)

    def test_sessao_persiste_e_retoma(self):
        cat, pasta = self.catalogo_sintetico()
        srv = Servico(pasta, EmissorSimulado(), cat)
        srv.desc.iniciar(categoria="tv", intervalo=2, iniciar_pausado=True)
        srv.desc.s["estado"] = "executando"
        srv.desc.passo()
        srv.desc._gravar()
        srv2 = Servico(pasta, EmissorSimulado(), cat)
        self.assertEqual(srv2.desc.s["estado"], "pausado")
        self.assertEqual(srv2.desc.s["cursor"], 1)


class TestCanal(unittest.TestCase):
    """Canal direto com a Central: o cliente WebSocket do celular contra uma 'Central' mínima feita aqui."""

    def test_canal_repassa_chamada_e_aviso(self):
        import base64 as b64
        import hashlib as hl
        import socket as so
        import struct as st
        from controle_ir import canal as canal_mod
        pasta = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, pasta, True)
        # servidor local falso (o /mcp do celular): ecoa a assinatura e o corpo
        recebidas = []

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                corpo = self.rfile.read(int(self.headers["Content-Length"]))
                recebidas.append((self.path, self.headers.get("X-Painel-Assinatura"), corpo))
                b = json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"eco": corpo.decode()}}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(b)))
                self.end_headers()
                self.wfile.write(b)

        local = ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=local.serve_forever, daemon=True).start()
        self.addCleanup(local.shutdown)
        # "Central" mínima: aceita o WebSocket, confere o token, manda um aviso e uma chamada, lê a resposta
        srv = so.socket()
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        porta_ws = srv.getsockname()[1]
        visto = {}

        def central():
            c, _ = srv.accept()
            req = b""
            while b"\r\n\r\n" not in req:
                req += c.recv(4096)
            linhas = req.decode().split("\r\n")
            visto["auth"] = next((ln for ln in linhas if ln.lower().startswith("authorization:")), "")
            chave = next(ln.split(":", 1)[1].strip() for ln in linhas if ln.lower().startswith("sec-websocket-key"))
            aceite = b64.b64encode(hl.sha1((chave + canal_mod.GUID).encode()).digest()).decode()
            c.sendall(f"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                      f"Sec-WebSocket-Accept: {aceite}\r\n\r\n".encode())

            def mandar(txt):
                d = txt.encode()
                c.sendall(bytes([0x81, 126]) + st.pack("!H", len(d)) + d if len(d) >= 126 else bytes([0x81, len(d)]) + d)

            def ler():
                b1, b2 = c.recv(2)
                n = b2 & 0x7F
                if n == 126:
                    n = st.unpack("!H", c.recv(2))[0]
                elif n == 127:
                    n = st.unpack("!Q", c.recv(8))[0]
                m = c.recv(4)
                d = b""
                while len(d) < n:
                    d += c.recv(n - len(d))
                return bytes(x ^ m[i % 4] for i, x in enumerate(d))

            mandar(json.dumps({"t": "sync"}))
            mandar(json.dumps({"t": "req", "id": "r1", "h": {"x-painel-assinatura": "1.abcdefgh.sig",
                                                              "content-type": "application/json", "cookie": "não"},
                               "b": json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call"})}))
            while True:
                txt = ler().decode()
                if txt.startswith("{"):
                    m = json.loads(txt)
                    if m.get("t") == "ok":
                        visto["confirmou"] = m.get("id")  # recebeu: confirma antes de executar
                        continue
                    visto["resposta"] = m
                    break
            c.close()

        threading.Thread(target=central, daemon=True).start()
        from controle_ir import painel as painel_mod
        painel_mod.gravar(pasta, {"url": f"http://127.0.0.1:{porta_ws}", "aparelho": "a1", "token": "tok-123",
                                  "chave_publica": "x"})
        acordou = threading.Event()
        cn = canal_mod.Canal(pasta, local.server_address[1], "segredo-x", ao_sincronizar=acordou.set).iniciar()
        self.addCleanup(cn.parar.set)
        fim = time.time() + 10
        while "resposta" not in visto and time.time() < fim:
            time.sleep(0.05)
        self.assertEqual(visto["auth"], "Authorization: Bearer tok-123")  # entra com o token do aparelho
        self.assertEqual(visto["confirmou"], "r1")  # confirmação de recebimento (a Central não cai para o túnel)
        self.assertTrue(acordou.is_set())  # aviso "sync" → sincroniza na hora
        caminho, ass, corpo = recebidas[0]
        self.assertEqual(caminho, "/mcp/segredo-x")  # entregue ao servidor LOCAL, com o segredo
        self.assertEqual(ass, "1.abcdefgh.sig")  # a assinatura da Central segue junto (é ela que vale)
        r = visto["resposta"]
        self.assertEqual((r["t"], r["id"], r["s"]), ("res", "r1", 200))
        self.assertIn("tools/call", json.loads(r["b"])["result"]["eco"])
        self.assertEqual(cn.atendidas, 1)


class TestServidorMCP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv_obj, _ = novo_servico()
        cls.segredo = "segredo-de-teste-123"
        cls.http = criar_servidor(cls.srv_obj, cls.segredo, 0)
        cls.porta = cls.http.server_address[1]
        threading.Thread(target=cls.http.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()

    def post(self, caminho, corpo, cab=None):
        req = urllib.request.Request(f"http://127.0.0.1:{self.porta}{caminho}", json.dumps(corpo).encode(),
                                     {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
                                      **(cab or {})})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status, (json.loads(r.read() or b"null"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"null")

    def test_fluxo_mcp(self):
        url = f"/mcp/{self.segredo}"
        st, r = self.post(url, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                                           "clientInfo": {"name": "teste", "version": "0"}}})
        self.assertEqual(st, 200)
        self.assertEqual(r["result"]["protocolVersion"], "2025-06-18")
        st, r = self.post(url, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        self.assertEqual(st, 202)
        st, r = self.post(url, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        nomes = {t["name"] for t in r["result"]["tools"]}
        for n in ("consultar", "buscar", "pausar", "confirmar", "opcoes", "controlar", "retestar", "salvar_aparelho"):
            self.assertIn(n, nomes)
        st, r = self.post(url, {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                                "params": {"name": "consultar", "arguments": {"categoria": "ar"}}})
        res = r["result"]
        self.assertFalse(res["isError"])
        self.assertTrue(res["structuredContent"]["marcas"])
        self.assertEqual(json.loads(res["content"][0]["text"]), res["structuredContent"])
        st, r = self.post(url, {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                                "params": {"name": "controlar", "arguments": {"aparelho": "inexistente"}}})
        self.assertTrue(r["result"]["isError"])

    def test_reenvio_da_rede_nao_executa_duas_vezes(self):
        from controle_ir.servidor import Reenvios
        r = Reenvios(janela=0.5)
        n = {"execucoes": 0}

        def lento():
            n["execucoes"] += 1
            time.sleep(0.3)
            return 200, {"ok": n["execucoes"]}

        corpo = {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "x"}}
        chave = Reenvios.chave(json.dumps(corpo).encode(), corpo)
        res = []
        ts = [threading.Thread(target=lambda: res.append(r.executar(chave, lento))) for _ in range(2)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        self.assertEqual(n["execucoes"], 1)  # o reenvio chegou com a primeira rodando: esperou e reaproveitou
        self.assertEqual(sorted(x[2] for x in res), [False, True])
        self.assertTrue(r.executar(chave, lento)[2])  # logo depois de terminar: ainda é reenvio
        time.sleep(0.6)
        self.assertFalse(r.executar(chave, lento)[2])  # passada a janela: pedido novo de verdade
        self.assertEqual(n["execucoes"], 2)
        self.assertIsNone(Reenvios.chave(b"{}", {"method": "tools/list", "id": 1}))  # só ferramentas

    def test_seguranca(self):
        st, _ = self.post("/mcp/errado", {"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        self.assertEqual(st, 401)
        st, _ = self.post("/mcp", {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                          {"Authorization": f"Bearer {self.segredo}"})
        self.assertEqual(st, 200)
        st, _ = self.post(f"/mcp/{self.segredo}", {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                          {"Origin": "https://site-malicioso.example"})
        self.assertEqual(st, 403)
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{self.porta}/mcp/{self.segredo}", timeout=5)
            self.fail("GET deveria ser recusado")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 405)
        st, _ = self.post("/api/pausar", {})
        self.assertEqual(st, 401)

    def test_api_de_aprovacao_nao_passa_pelo_tunel(self):
        st, _ = self.post(f"/api/pausar?t={self.segredo}", {}, {"X-Forwarded-For": "160.79.104.10"})
        self.assertEqual(st, 401)  # mesmo com o segredo certo, vindo do túnel
        st, _ = self.post(f"/api/pausar?t={self.segredo}", {})
        self.assertIn(st, (200, 400))  # local: aceito (400 = nenhuma busca para pausar)

    def test_origens_observar_e_exigir(self):
        from controle_ir.servidor import Origens
        url = f"/mcp/{self.segredo}"
        msg = {"jsonrpc": "2.0", "id": 1, "method": "ping"}
        st, _ = self.post(url, msg, {"X-Forwarded-For": "203.0.113.9"})
        self.assertEqual(st, 200)  # padrão: só observa
        self.assertIn("203.0.113.9", (Path(self.srv_obj.pasta) / "origens.json").read_text())
        o = Origens(Path(tempfile.mkdtemp()), lambda: {"modo": "exigir"})
        self.assertTrue(o.verificar("10.0.0.1, 160.79.105.20"))  # vale o IP acrescentado pelo proxy, no fim
        self.assertFalse(o.verificar("160.79.105.20, 203.0.113.9"))  # o começo vem do cliente: falsificável
        self.assertFalse(o.verificar("203.0.113.9"))
        self.assertTrue(o.verificar(None))  # chamada local, sem túnel


class TestArmacao(unittest.TestCase):
    """Etapa 0 de segurança: desarmado, pelo conector só passa o baixo risco; armar só no celular."""

    def setUp(self):
        from controle_ir.mcp import ServidorMCP
        self.s, self.pasta = novo_servico(com_base=False)
        self.pol = self.s.exec.politica
        self.mcp = ServidorMCP(self.s)

    def chamar(self, nome, **args):
        r = self.mcp.chamar(nome, args)
        return json.loads(r["content"][0]["text"]), r["isError"]

    def test_quem_atualiza_fica_armado_ate_meia_noite_e_sem_politica_nasce_desarmado(self):
        from controle_ir.execucao import Politica
        from controle_ir.seguranca import fim_do_dia
        pasta = Path(tempfile.mkdtemp())
        (pasta / "politica.json").write_text(json.dumps({"perfil": "autonomo"}))  # política antiga, sem o campo
        self.assertAlmostEqual(Politica(pasta).ler()["armado_ate"], fim_do_dia(), delta=2)
        nova = Path(tempfile.mkdtemp())  # sem arquivo (instalação nova ou política apagada): desarmado
        self.assertEqual(Politica(nova).ler()["armado_ate"], 0)
        self.assertEqual(Politica(nova).decidir("leitura"), "negar")

    def test_desarmado_so_baixo_risco(self):
        self.pol.desarmar()
        for alto in ("executar_comando", "tarefa", "executar_capacidade", "cap_estado_celular", "atualizar_sistema",
                     "propor_capacidade", "capacidades", "autorizar"):
            d, erro = self.chamar(alto, comando="ls") if alto == "executar_comando" else self.chamar(alto)
            self.assertTrue(erro and d.get("bloqueado"), alto)
            self.assertIn("DESARMADO", d["erro"])
        d, erro = self.chamar("consultar")
        self.assertFalse(erro)
        d, erro = self.chamar("procurar_perfis", marca="Gree")  # infravermelho segue liberado
        self.assertNotIn("bloqueado", d)
        with self.assertRaises(Exception):  # e nenhum outro caminho do serviço roda capacidade
            self.s.executar_capacidade("estado_celular")
        self.assertEqual(self.s.exec.pedir("ls", aguardar=0)["status"], "negada")
        p = self.pol.ler()
        p["desarmado_permite"] = "nada"
        self.pol.gravar(p)
        self.assertTrue(self.chamar("procurar_perfis", marca="Gree")[0].get("bloqueado"))
        self.assertFalse(self.chamar("politica")[1])
        self.assertIn("bloqueado", (Path(self.pasta) / "auditoria.jsonl").read_text())

    def test_travar_pelo_conector_e_definitivo_ate_armar_no_celular(self):
        d, erro = self.chamar("travar")
        self.assertFalse(erro)
        self.assertTrue((Path(self.pasta) / "PARAR").exists())  # laços em 2º plano param
        for nome, args in (("controlar", {"aparelho": "x"}), ("executar_comando", {"comando": "ls"}),
                           ("autorizar", {"destravar": True})):
            self.assertTrue(self.chamar(nome, **args)[0].get("bloqueado"), nome)
        with self.assertRaises(Exception):
            self.s.autorizar(destravar=True)  # nem chamando o serviço direto
        self.pol.aplicar_perfil("autonomo")  # perfil não destrava
        self.assertTrue(self.pol.ler()["travado"])
        from controle_ir.execucao import Politica
        self.assertTrue(Politica(Path(self.pasta)).ler()["travado"])  # sobrevive a reinício (arquivo)
        self.pol.armar()  # só no celular
        self.assertFalse(self.chamar("executar_comando", comando="echo ok", aguardar=5)[0].get("bloqueado"))

    def test_armar_por_horas_e_expirar(self):
        from controle_ir.seguranca import armado, permitido
        p = self.pol.armar(2)
        self.assertAlmostEqual(p["armado_ate"] - time.time(), 7200, delta=5)
        self.assertTrue(permitido("executar_comando", p)[0])
        self.assertFalse(armado(p, agora=p["armado_ate"] + 1))
        self.assertFalse(permitido("executar_comando", p, agora=p["armado_ate"] + 1)[0])

    def test_classe_protegida_nunca_roda(self):
        from controle_ir.execucao import classificar
        for cmd in ("cat ~/.controle-ir/config.json", "cat .controle-ir/autorizacao.json", "cp ~/.controle-ir/* /sdcard",
                    "sed -i s/true/false/ ~/.controle-ir/politica.json", "cat ~/.config/ngrok/ngrok.yml",
                    "cat /proc/123/environ", "ls ~/.ssh/"):
            self.assertEqual(classificar(cmd), "protegido", cmd)
        self.assertEqual(classificar("cat ~/.controle-ir/servico.log"), "leitura")
        self.pol.aplicar_perfil("autonomo")
        self.assertEqual(self.pol.decidir("protegido"), "negar")
        self.assertEqual(self.s.exec.pedir("cat ~/.controle-ir/config.json", aguardar=0)["status"], "negada")

    def test_tunel_sem_inspetor_e_sem_token_no_argv(self):
        from controle_ir.tunel import Tunel
        self.assertIn("--inspect=false", Tunel(8765, {"modo": "ngrok", "dominio": "x.ngrok-free.app"}).comando())
        cmd = Tunel(8765, {"modo": "cloudflare", "token": "SEGREDO-TESTE"}).comando()
        self.assertNotIn("SEGREDO-TESTE", " ".join(cmd))


class TestPainel(unittest.TestCase):
    """Pareado, só um estado ASSINADO pelo painel arma o celular; revogar e emergência reduzem na hora."""

    def setUp(self):
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
        from controle_ir import painel
        self.p = painel
        self.chave = Ed25519PrivateKey.generate()
        pub = self.chave.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        self.s, self.pasta = novo_servico(com_base=False)
        self.pol = self.s.exec.politica
        self.cfg = {"url": "http://127.0.0.1:1", "aparelho": "pocoX", "token": "t", "seq_max": 0, "offset": 0,
                    "chave_publica": base64.urlsafe_b64encode(pub).decode().rstrip("=")}
        painel.gravar(self.pasta, self.cfg)
        p = self.pol.ler()
        p["modo_painel"] = True
        self.pol.gravar(p)

    def assinado(self, chave=None, **campos):
        e = {"v": 1, "aparelho": "pocoX", "seq": 1, "armado_ate": int(time.time()) + 3600, "travado": 0,
             "desarmado_permite": "ir", "emitido_em": int(time.time()), **campos}
        txt = json.dumps(e)
        sig = (chave or self.chave).sign(txt.encode())
        return txt, base64.urlsafe_b64encode(sig).decode().rstrip("=")

    def gravar_estado(self, txt, sig, seq_max=0):
        self.p.gravar(self.pasta, {**self.cfg, "estado": txt, "assinatura": sig, "seq_max": seq_max})

    def test_so_estado_assinado_arma(self):
        from controle_ir.seguranca import permitido
        self.assertFalse(permitido("executar_comando", self.pol.efetiva())[0])  # pareado sem estado: desarmado
        self.gravar_estado(*self.assinado())
        self.assertTrue(permitido("executar_comando", self.pol.efetiva())[0])
        txt, sig = self.assinado()
        self.gravar_estado(txt.replace('"travado": 0', '"travado": 0 '), sig)  # texto alterado
        self.assertFalse(permitido("executar_comando", self.pol.efetiva())[0])
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        self.gravar_estado(*self.assinado(chave=Ed25519PrivateKey.generate()))  # outra chave
        self.assertFalse(permitido("executar_comando", self.pol.efetiva())[0])
        self.gravar_estado(*self.assinado(aparelho="outro"))
        self.assertFalse(permitido("executar_comando", self.pol.efetiva())[0])
        self.gravar_estado(*self.assinado(seq=3), seq_max=5)  # estado antigo reapresentado
        self.assertFalse(permitido("executar_comando", self.pol.efetiva())[0])

    def test_armar_local_recusado_e_desarmar_local_veta(self):
        self.gravar_estado(*self.assinado(seq=4))
        with self.assertRaises(ValueError):
            self.pol.armar()
        self.pol.desarmar()  # o dono no celular sempre consegue tirar poder
        self.assertEqual(self.pol.efetiva()["armado_ate"], 0)
        self.gravar_estado(*self.assinado(seq=5))  # nova armação no painel vence o veto
        self.assertGreater(self.pol.efetiva()["armado_ate"], time.time())

    def test_comandos_administrativos_e_arquivo_do_painel_protegidos(self):
        from controle_ir.execucao import classificar
        for cmd in ("cat ~/.controle-ir/painel.json", "controle-ir armar 24", "controle-ir exec liberar 60",
                    "controle-ir exec modo autonomo", "controle-ir painel parear x y", "controle-ir atualizar --ref main"):
            self.assertEqual(classificar(cmd), "protegido", cmd)
        self.assertNotEqual(classificar("controle-ir exec travar"), "protegido")  # tirar poder continua livre

    def test_sincronizar_com_painel_falso(self):
        estados, recebidos = [], []

        class P(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                if self.headers.get("Authorization") != "Bearer t":
                    return self._r(401, {"erro": "x"})
                txt, sig = estados[-1]
                self._r(200, {"estado": txt, "assinatura": sig})

            def do_POST(self):
                recebidos.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
                self._r(200, {"ok": True})

            def _r(self, st, d):
                b = json.dumps(d).encode()
                self.send_response(st)
                self.send_header("Content-Length", str(len(b)))
                self.end_headers()
                self.wfile.write(b)

        srv = ThreadingHTTPServer(("127.0.0.1", 0), P)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.shutdown)
        self.p.gravar(self.pasta, {**self.cfg, "url": f"http://127.0.0.1:{srv.server_address[1]}"})
        reduzidos = []
        self.s.exec.auditar({"evento": "teste_auditoria"})
        estados.append(self.assinado(seq=1))
        r = self.p.sincronizar(self.pasta, "1.0.24", reduzidos.append)
        self.assertEqual((r["seq"], r["travado"]), (1, 0))
        self.assertTrue(self.s.politica()["armado"])
        self.assertEqual(recebidos[-1]["seq"], 1)  # o painel só mostra "aplicado" com esta confirmação
        self.assertIn("teste_auditoria", json.dumps(recebidos[-1]["eventos"]))
        estados.append(self.assinado(seq=2, travado=1, armado_ate=0))  # EMERGÊNCIA no painel
        self.p.sincronizar(self.pasta, "1.0.24", reduzidos.append)
        self.assertEqual(reduzidos, ["emergência no painel"])
        self.assertTrue(self.s.politica()["travado"])
        estados.append(self.assinado(seq=1))  # painel (ou alguém no meio) devolvendo estado velho
        with self.assertRaises(ValueError):
            self.p.sincronizar(self.pasta, "1.0.24", reduzidos.append)
        self.p.gravar(self.pasta, {**self.p.ler(self.pasta), "token": "revogado"})
        self.assertTrue(self.p.sincronizar(self.pasta, "1.0.24", reduzidos.append)["revogado"])
        self.assertIsNone(self.p.estado_valido(self.pasta))  # revogado: falha fechada
        self.assertFalse(self.s.politica()["armado"])

    def test_sem_rede_e_historico_desde_o_pareamento(self):
        st, r = self.p._http("GET", "http://127.0.0.1:1/x", timeout=2)  # nada escutando: offline, sem exceção
        self.assertEqual(st, 0)
        self.assertIn("erro", r)
        arq = Path(self.pasta) / "auditoria.jsonl"
        arq.write_text(json.dumps({"quando": "2026-01-01 10:00:00", "evento": "antigo"}) + "\n" +
                       "".join(json.dumps({"quando": "2026-11-19 10:00:00", "evento": f"novo{i}"}) + "\n"
                               for i in range(40)))
        ev, fim, arquivo = self.p._eventos_novos(self.pasta, 0, "2026-11-19 00:00:00")
        self.assertEqual(len(ev), self.p.MAX_EVENTOS)  # lote limitado (uma transação no painel)
        self.assertNotIn("antigo", json.dumps(ev))  # o que é de antes do pareamento fica só no celular
        self.assertEqual(ev[-1]["_fim"], fim)  # posição de cada evento: o painel ignora repetidos
        self.assertTrue(arquivo)
        ev2, fim2, _ = self.p._eventos_novos(self.pasta, fim, "2026-11-19 00:00:00")
        self.assertEqual((len(ev2), fim2), (10, arq.stat().st_size))

    def assinar_req(self, corpo: bytes, ts=None, chave=None):
        import hashlib
        ts = int(time.time()) if ts is None else ts
        nonce = base64.urlsafe_b64encode(os.urandom(12)).decode().rstrip("=")
        sig = (chave or self.chave).sign(f"{ts}.{nonce}.{hashlib.sha256(corpo).hexdigest()}".encode())
        return f"{ts}.{nonce}." + base64.urlsafe_b64encode(sig).decode().rstrip("=")

    def test_chamada_repassada_pelo_painel_assinada(self):
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        corpo = b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
        v = self.p.verificar_requisicao
        self.assertTrue(v(self.pasta, self.assinar_req(corpo), corpo))
        self.assertFalse(v(self.pasta, self.assinar_req(corpo), corpo + b" "))  # corpo trocado no caminho
        self.assertFalse(v(self.pasta, self.assinar_req(corpo, ts=int(time.time()) - 600), corpo))  # velha
        self.assertFalse(v(self.pasta, self.assinar_req(corpo, chave=Ed25519PrivateKey.generate()), corpo))
        cab = self.assinar_req(corpo)
        self.assertTrue(v(self.pasta, cab, corpo))
        self.assertFalse(v(self.pasta, cab, corpo))  # a mesma assinatura não vale duas vezes (repetição)
        self.assertFalse(v(self.pasta, None, corpo))

    def test_servidor_aceita_painel_e_recusa_direto_quando_so_pelo_painel(self):
        segredo = "segredo-de-teste-456"
        http = criar_servidor(self.s, segredo, 0)
        threading.Thread(target=http.serve_forever, daemon=True).start()
        self.addCleanup(http.shutdown)
        url = f"http://127.0.0.1:{http.server_address[1]}/mcp/{segredo}"

        def post(corpo: bytes, cab=None):
            req = urllib.request.Request(url, corpo, {"Content-Type": "application/json", **(cab or {})})
            try:
                with urllib.request.urlopen(req, timeout=10) as r:
                    return r.status
            except urllib.error.HTTPError as e:
                return e.code
        corpo = b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
        self.assertEqual(post(corpo, {"X-Painel-Assinatura": self.assinar_req(corpo)}), 200)
        self.assertEqual(post(corpo, {"X-Painel-Assinatura": "123.abcdefgh.falsa"}), 401)
        self.assertEqual(post(corpo), 200)  # direto pelo ngrok ainda vale até o dono ligar "só pelo painel"
        self.p.gravar(self.pasta, {**self.p.ler(self.pasta), "so_pelo_painel": 1})
        self.assertTrue(self.pol.efetiva()["so_pelo_painel"])
        self.assertEqual(post(corpo), 403)  # URL do ngrok vazada não basta mais
        self.assertEqual(post(corpo, {"X-Painel-Assinatura": self.assinar_req(corpo)}), 200)


class TestImagensAninhadas(unittest.TestCase):
    def test_imagem_dentro_de_sequencia_vira_anexo(self):
        from controle_ir.mcp import _extrair_imagens
        d = {"capacidade": "tela", "resultado": {"feito": "2 passos", "tela": {"app": "x",
             "_imagem": {"mime": "image/jpeg", "base64": "QUJD"}}}}
        imgs = _extrair_imagens(d)
        self.assertEqual([i["data"] for i in imgs], ["QUJD"])
        self.assertNotIn("_imagem", json.dumps(d))  # o base64 não vai no texto
        self.assertEqual(d["resultado"]["tela"]["imagens_anexadas"], 1)


class TestObservador(unittest.TestCase):
    """O que a Central mostra em "Agora no celular": tarefas, capacidades, câmera/microfone (AppOps)."""

    def setUp(self):
        from controle_ir import observador
        self.o = observador

    def test_appops_running_vira_app_usando(self):
        saida = ("  Uid 10324:\n    Package com.termux.api:\n      CAMERA (allow):\n        null=[\n"
                 "          Access: [fgsvc-s] 2026-11-19 10:44:06 (-2s) duration=+2s\n          Running start at: +2s\n"
                 "    Package com.android.camera:\n          Access: [top-s] 2026-11-15 duration=+32s\n"
                 "#####\n    Package com.whatsapp:\n      RECORD_AUDIO (allow):\n          Running start at: +1s\n")
        self.assertEqual(self.o.apps_usando(saida), {"câmera": ["com.termux.api"], "microfone": ["com.whatsapp"]})
        self.assertEqual(self.o.apps_usando(""), {"câmera": [], "microfone": []})

    def test_recursos_e_tarefas_em_execucao(self):
        self.assertEqual(self.o.recursos_do_comando("termux-microphone-record -f a.m4a"), ["microfone"])
        self.assertEqual(self.o.recursos_do_comando("ls -la"), [])
        pasta = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, pasta, True)
        (pasta / "tarefas").mkdir()
        (pasta / "tarefas" / "1.json").write_text(json.dumps({"id": "1", "status": "executando",
                                                             "comando": "termux-camera-photo x.jpg", "inicio": 1}))
        (pasta / "tarefas" / "2.json").write_text(json.dumps({"id": "2", "status": "concluida", "comando": "ls"}))
        r = self.o.em_uso(pasta, android=False, ao_vivo=True)
        tipos = [(i["tipo"], tuple(i.get("recursos", []))) for i in r["itens"]]
        self.assertIn(("terminal", ("terminal", "câmera")), tipos)
        self.assertIn(("tela", ("tela",)), tipos)  # transmitindo para a Central
        self.assertNotIn("ls", json.dumps(r))  # só o que está rodando


class TestGreeVariante(unittest.TestCase):
    """ferramentas/gree_variante.py: sinais que funcionaram no “ar do quarto” (Gree GWH09KF) em 17/11/2026."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(RAIZ / "ferramentas"))
        import gree_variante
        cls.g = gree_variante

    def test_oscilar_muda_so_dois_bits_e_mantem_checksum(self):
        r = self.g.gerar("frio", "automatica", 16, oscilar=True)
        self.assertEqual(r["original"], "09 00 20 50 00 20 00 50")
        self.assertEqual(r["bytes"], "49 00 20 50 01 20 00 50")
        p = self.g.perfil()
        e = next(e for e in p["estado_completo"]["estados"]
                 if (e["modo"], e["ventilacao"], e["temperatura"]) == ("frio", "automatica", 16))
        _, orig = broadlink_para_pulsos(e["sinal"]["broadlink"])
        difs = [i for i, (a, b) in enumerate(zip(orig, r["pulsos"])) if a != b]
        self.assertEqual(difs, [15, 75])  # só os espaços do bit 0x40 do byte 0 e do 0x01 do byte 4

    def test_visor_desligado_e_checksum_recalculado(self):
        r = self.g.gerar("frio", "automatica", 16, visor_desligado=True)
        self.assertEqual(r["bytes"], "09 00 00 50 00 20 00 50")
        r = self.g.gerar("frio", "media", 23, visor_desligado=True, oscilar=True)
        b = [int(x, 16) for x in r["bytes"].split()]
        self.assertEqual(b[2] & 0x20, 0)
        self.assertEqual(b[7] >> 4, self.g.checksum(b))

    def test_turbo_liga_bit_0x10_do_byte_2(self):
        r = self.g.gerar("frio", "automatica", 16, oscilar=True, visor_desligado=True, turbo=True)
        self.assertEqual(r["bytes"], "49 00 10 50 01 20 00 50")

    def test_quadro_duplo_e_recusado(self):
        with self.assertRaises(self.g.ErroGree):
            self.g.gerar("frio", "baixa", 18, oscilar=True)


class TestResumoInstrucoes(unittest.TestCase):
    """Resumo dos aparelhos nas instruções do MCP (economiza a chamada opcoes antes de cada pedido)."""

    @classmethod
    def setUpClass(cls):
        cls.s, _ = novo_servico()
        s = cls.s
        sinal = lambda c: {"protocolo": "NEC", "endereco": 1, "comando": c}  # noqa: E731
        s.salvar_aparelho("ar do quarto", perfil=105)
        s.editar_aparelho("ar do quarto", adicionar_comando={"nome": "Visor desligado (16 °C, frio)",
                                                             "funcao": "luz", "sinal": sinal(10)})
        s.editar_aparelho("ar do quarto", observacao="  Os botões extras   fixam 16 °C, frio, automática. ")
        s.salvar_aparelho("tv do quarto", perfil=613)
        s.editar_aparelho("tv do quarto", macro={"nome": "abrir Netflix", "descricao": "Smart Hub e OK",
                                                 "passos": [{"teclas": ["ok"]}]})
        s.salvar_aparelho("ar do escritório", perfil=94)
        s.salvar_aparelho("ar condicionado laboratório", perfil=94)

    def test_resumo_traz_nomes_valores_teclas_macros(self):
        from controle_ir.aparelhos import resumo_para_instrucoes
        t = resumo_para_instrucoes(self.s.aparelhos.listar())
        for trecho in ('"ar do quarto"', '"tv do quarto"', '"ar do escritório"', '"ar condicionado laboratório"',
                       "temperatura 16–30", "temperatura 17–30", "frio|", "abrir Netflix (Smart Hub e OK)",
                       "Visor desligado (16 °C, frio)", "volume: +/−", "número 0–9",
                       "observação: Os botões extras fixam 16 °C, frio, automática."):
            self.assertIn(trecho, t)
        self.assertNotIn("numero_5", t)  # as teclas 0–9 já estão em "número 0–9"
        self.assertNotIn("ultimo", t.lower())  # sem estado: ele envelhece durante a conversa
        # os dois aparelhos do perfil 94 avisam que um envio pode acionar o outro
        bloco = t.split('"ar do escritório"')[1].split("\n- ")[0]
        self.assertIn("mesmos códigos de: ar condicionado laboratório", bloco)
        self.assertNotIn("mesmos códigos", t.split('"ar do quarto"')[1].split("\n- ")[0])

    def test_limites(self):
        from controle_ir.aparelhos import resumo_para_instrucoes
        t = resumo_para_instrucoes(self.s.aparelhos.listar(), limite_teclas=3)
        self.assertIn("veja opcoes)", t)
        t = resumo_para_instrucoes(self.s.aparelhos.listar(), limite=600)
        self.assertLessEqual(len(t), 600)
        self.assertIn("resumo cortado", t)
        self.assertIn("nenhum ainda", resumo_para_instrucoes([]))

    def test_observacao_em_opcoes_e_apagar(self):
        s = self.s
        self.assertEqual(s.opcoes("ar do quarto")["observacao"], "Os botões extras fixam 16 °C, frio, automática.")
        s.editar_aparelho("ar do escritório", observacao="teste")
        self.assertEqual(s.opcoes("ar do escritório")["observacao"], "teste")
        r = s.editar_aparelho("ar do escritório", observacao="")
        self.assertIn("observação apagada", r["alteracoes"])
        self.assertNotIn("observacao", s.opcoes("ar do escritório"))

    def test_initialize_entrega_resumo_atualizado(self):
        from controle_ir.mcp import ServidorMCP
        m = ServidorMCP(self.s)
        _, r = m.tratar({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25"}})
        ins = r["result"]["instructions"]
        self.assertIn("chame controlar direto", ins)
        self.assertIn('"tv do quarto"', ins)
        self.s.salvar_aparelho("ventilador da sala", perfil=94)
        try:
            _, r = m.tratar({"jsonrpc": "2.0", "id": 2, "method": "initialize", "params": {}})
            self.assertIn('"ventilador da sala"', r["result"]["instructions"])
        finally:
            self.s.editar_aparelho("ventilador da sala", excluir=True)
        # um aparelho corrompido não derruba o initialize
        self.s.aparelhos.dados["aparelhos"]["quebrado"] = {"id": "quebrado", "nome": "quebrado", "perfil": None}
        try:
            _, r = m.tratar({"jsonrpc": "2.0", "id": 3, "method": "initialize", "params": {}})
            self.assertIn("instructions", r["result"])
        finally:
            del self.s.aparelhos.dados["aparelhos"]["quebrado"]



class TestCapacidades(unittest.TestCase):
    """Capacidades plugáveis: embutidas, proposta → aprovação no celular → execução, e exposição no MCP."""

    ECO = {"manifesto": {"titulo": "Eco", "descricao": "devolve o texto", "executar": "principal.py",
                         "entrada": {"type": "object", "properties": {"texto": {"type": "string"},
                                                                       "dormir": {"type": "number"}},
                                     "required": ["texto"]}, "tempo_limite": 2},
           "arquivos": {"principal.py": "import json,sys,time\na=json.load(sys.stdin)\ntime.sleep(a.get('dormir',0))\n"
                                        "print(json.dumps({'eco': a['texto'].upper()}))\n"}}

    def setUp(self):
        self.s, self.pasta = novo_servico(com_base=False)

    def test_embutidas_ativas_e_estado_celular_roda(self):
        nomes = {c["nome"]: c["estado"] for c in self.s.capacidades()["capacidades"]}
        self.assertEqual(nomes.get("diagnostico_rede"), "ativa")
        self.assertEqual(nomes.get("estado_celular"), "ativa")
        r = self.s.executar_capacidade("estado_celular")
        self.assertEqual(r["status"], "ok")
        self.assertIn("armazenamento_livre_gb", r["resultado"])

    def test_descobrir_rede_embutida_e_classifica_sem_rede(self):
        import importlib.util
        nomes = {c["nome"]: c["estado"] for c in self.s.capacidades()["capacidades"]}
        self.assertEqual(nomes.get("descobrir_rede"), "ativa")
        caminho = Path(__file__).resolve().parent.parent / "controle-ir" / "capacidades" / "descobrir_rede" / "principal.py"
        spec = importlib.util.spec_from_file_location("descobrir_rede_principal", caminho)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(mod.classificar([554])[0], "câmera IP provável")
        self.assertEqual(mod.classificar([53, 9000], e_gateway=True)[0], "roteador")
        self.assertEqual(mod.classificar([8001])[0], "TV (Samsung/Tizen provável)")
        self.assertEqual(mod.classificar([], gree=True)[0], "ar-condicionado (Gree)")
        self.assertEqual(mod.classificar([])[0], "não identificado")

    def test_proposta_so_roda_depois_de_aprovada_e_reaprova_se_mudar(self):
        r = self.s.propor_capacidade("eco", **self.ECO)
        self.assertEqual(r["status"], "aguardando_aprovacao")
        with self.assertRaises(Exception) as e:
            self.s.executar_capacidade("eco", {"texto": "oi"})
        self.assertIn("aguarda aprovação", str(e.exception))
        self.s.reg.aprovar("eco")
        r = self.s.executar_capacidade("eco", {"texto": "oi"})
        self.assertEqual((r["status"], r["resultado"]), ("ok", {"eco": "OI"}))
        (Path(self.pasta) / "capacidades" / "eco" / "principal.py").write_text("print('{}')")
        with self.assertRaises(Exception) as e:
            self.s.executar_capacidade("eco", {"texto": "oi"})
        self.assertIn("alterada_reaprovar", str(e.exception))

    def test_aprovacao_presa_ao_codigo_revisado(self):
        r1 = self.s.propor_capacidade("eco", **self.ECO)
        outro = dict(self.ECO, arquivos={"principal.py": "print(1)"})
        self.s.propor_capacidade("eco", **outro)  # trocou o código depois da notificação
        with self.assertRaises(Exception) as e:
            self.s.reg.aprovar("eco", r1["sha256"][:16])
        self.assertIn("mudou", str(e.exception))
        r2 = self.s.reg.ver("eco", proposta=True)
        self.assertEqual(self.s.reg.aprovar("eco", r2["sha256"][:16])["status"], "ativa")
        sub = Path(self.pasta) / "capacidades" / "eco" / "lib"
        sub.mkdir()
        (sub / "x.py").write_text("x = 1")  # código em subpasta também entra no hash
        with self.assertRaises(Exception):
            self.s.executar_capacidade("eco", {"texto": "a"})

    def test_validacao_tempo_limite_e_nomes(self):
        self.s.propor_capacidade("eco", **self.ECO)
        self.s.reg.aprovar("eco")
        for args, msg in (({}, "obrigatório"), ({"texto": 1}, "string"), ({"texto": "a", "x": 1}, "desconhecido")):
            with self.assertRaises(Exception) as e:
                self.s.executar_capacidade("eco", args)
            self.assertIn(msg, str(e.exception))
        self.assertEqual(self.s.executar_capacidade("eco", {"texto": "a", "dormir": 5})["status"], "tempo_esgotado")
        for nome, arqs in (("Eco!", {"a.py": ""}), ("diagnostico_rede", {"a.py": ""}), ("ok", {"../x.py": ""}),
                           ("ok", {"capacidade.json": "{}"})):
            with self.assertRaises(Exception):
                self.s.propor_capacidade(nome, {"executar": "a.py"}, arqs)
        r = self.s.capacidades("anotar", "eco", "funcionou no POCO em 18/11")
        self.assertEqual(r["notas"][-1]["nota"], "funcionou no POCO em 18/11")

    def test_mcp_expoe_ferramenta_por_capacidade_e_instrucoes(self):
        from controle_ir.mcp import ServidorMCP
        m = ServidorMCP(self.s)
        self.s.propor_capacidade("eco", **self.ECO)
        nomes = {t["name"] for t in m.tratar({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})[1]["result"]["tools"]}
        self.assertIn("cap_diagnostico_rede", nomes)
        self.assertNotIn("cap_eco", nomes)  # ainda não aprovada
        self.s.reg.aprovar("eco")
        _, r = m.tratar({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertIn("cap_eco", {t["name"] for t in r["result"]["tools"]})
        _, r = m.tratar({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                         "params": {"name": "cap_eco", "arguments": {"texto": "luz"}}})
        self.assertEqual(r["result"]["structuredContent"]["resultado"], {"eco": "LUZ"})
        _, r = m.tratar({"jsonrpc": "2.0", "id": 4, "method": "initialize", "params": {}})
        self.assertIn("- eco: devolve o texto", r["result"]["instructions"])



class TestExecucao(unittest.TestCase):
    """Execução governada: o Claude pede, o celular concede (política só muda no aparelho)."""

    def setUp(self):
        self.s, self.pasta = novo_servico(com_base=False)
        self.ex = self.s.exec

    def test_classificacao(self):
        from controle_ir.execucao import classificar
        for cmd, c in (("ls -la", "leitura"), ("getprop ro.product.model", "leitura"), ("pkg list-installed", "leitura"),
                       ("pkg install nmap", "pacotes"), ("ping -c 3 1.1.1.1", "rede"), ("rm -rf x", "livre"),
                       ("ls; rm x", "livre"), ("cat a | sh", "livre"), ("echo $HOME", "livre"),
                       ("grep -r segredo /", "livre"), ("python3 x.py", "livre")):
            self.assertEqual(classificar(cmd), c, cmd)

    def test_leitura_roda_direto_e_audita(self):
        r = self.s.executar_comando("ls /", aguardar=10)
        self.assertEqual((r["status"], r["classe"]), ("concluida", "leitura"))
        self.assertIn("tmp", r["saida"])
        aud = (Path(self.pasta) / "auditoria.jsonl").read_text()
        self.assertIn('"evento": "pedido"', aud)
        self.assertIn('"evento": "fim"', aud)

    def test_perguntar_aprovar_negar(self):
        threading.Timer(0.5, lambda: self.ex.decidir("1", True)).start()
        r = self.s.executar_comando("echo ok; echo fim", aguardar=10, motivo="teste")
        self.assertEqual((r["status"], r["decisao"]), ("concluida", "aprovada"))
        self.assertTrue(r["saida"].endswith("fim"))
        r = self.s.executar_comando("echo nao", aguardar=0)
        self.assertEqual(r["status"], "aguardando_aprovacao")
        self.ex.decidir(r["id"], False)
        self.assertEqual(self.s.tarefa(r["id"])["status"], "negada")

    def test_liberar_travar_sistema_e_tempo(self):
        pol = self.ex.politica
        p = pol.ler()
        p["liberado_ate"] = time.time() + 60
        pol.gravar(p)
        self.assertEqual(self.s.executar_comando("echo livre; true", aguardar=10)["status"], "concluida")
        self.assertEqual(self.s.atualizar_sistema("a" * 40, "teste", aguardar=0)["status"], "aguardando_aprovacao")
        for ref in ("x; rm -rf ~", "main", "abc1234", "a/../../../../atacante/repo/raw/main"):
            with self.assertRaises(Exception):  # só o hash completo: nada de branch nem de outro repositório
                self.s.atualizar_sistema(ref)
        r = self.s.executar_comando("sleep 5; echo", aguardar=0, tempo_limite=1)
        time.sleep(2.5)
        self.assertEqual(self.s.tarefa(r["id"])["status"], "tempo_esgotado")
        r = self.s.executar_comando("sleep 30; echo", aguardar=0.3)
        self.assertEqual(r["status"], "executando")
        p["travado"] = True
        pol.gravar(p)
        self.assertEqual(self.ex.parar_todas(), 1)
        time.sleep(0.5)
        self.assertEqual(self.s.tarefa(r["id"])["status"], "parada")
        self.assertEqual(self.s.executar_comando("ls", aguardar=1)["status"], "negada")

    def test_reinicio_marca_interrompida_e_mcp_nao_muda_politica(self):
        from controle_ir.execucao import Execucao
        from controle_ir.mcp import FERRAMENTAS
        r = self.s.executar_comando("echo x", aguardar=0)
        Execucao(Path(self.pasta))  # serviço reiniciou
        self.assertEqual(self.s.tarefa(r["id"])["status"], "interrompida")
        nomes = " ".join(t["name"] for t in FERRAMENTAS)
        for proibido in ("liberar", "destravar", "aprovar", "classe", "remoto"):  # classes e modo: só no celular
            self.assertNotIn(proibido, nomes)
        self.assertIn("politica", nomes)

    def test_totp_rfc6238_e_uso_unico(self):
        import base64
        from controle_ir.execucao import Autorizacao, totp
        seg = base64.b32encode(b"12345678901234567890").decode()
        self.assertEqual(totp(seg, 59 // 30, 8), "94287082")  # vetor de teste da RFC 6238 (SHA-1)
        au = Autorizacao(Path(self.pasta))
        with self.assertRaises(ValueError):
            au.verificar("123456")  # não configurada
        seg = au.configurar()
        t = 1_800_000_000
        cod = totp(seg, t // 30)
        self.assertTrue(au.verificar(cod, t))
        self.assertFalse(au.verificar(cod, t))  # o mesmo código não vale duas vezes
        self.assertTrue(au.verificar(totp(seg, t // 30 + 1), t))  # janela de ±30 s
        for _ in range(5):
            self.assertFalse(au.verificar("000000", t + 60))
        with self.assertRaises(ValueError):  # bloqueada após 5 erros
            au.verificar(totp(seg, (t + 90) // 30), t + 90)

    def test_modo_autonomo_executa_sem_pedir_e_ativa_capacidade(self):
        from controle_ir.capacidades import resumo_instrucoes  # noqa: F401
        self.ex.politica.aplicar_perfil("autonomo")
        self.assertEqual(self.s.politica()["perfil"], "autonomo")
        # comando que normalmente pediria aprovação (rede) roda direto
        r = self.s.executar_comando("echo autonomo; true", aguardar=10)
        self.assertEqual(r["status"], "concluida")
        self.assertEqual(self.s.exec.politica.decidir("pacotes"), "permitir")
        # capacidade proposta já entra ativa
        eco = {"manifesto": {"titulo": "Eco", "descricao": "x", "executar": "principal.py",
                             "entrada": {"type": "object", "properties": {"texto": {"type": "string"}},
                                         "required": ["texto"]}},
               "arquivos": {"principal.py": "import json,sys\nprint(json.dumps({'e': json.load(sys.stdin)['texto']}))\n"}}
        out = self.s.propor_capacidade("eco", **eco)
        self.assertEqual(out["status"], "ativa")
        self.assertTrue(out["auto_aprovada"])
        self.assertEqual(self.s.executar_capacidade("eco", {"texto": "ok"})["resultado"], {"e": "ok"})
        # o freio volta a barrar tudo, mesmo autônomo
        self.s.travar()
        self.assertEqual(self.s.executar_comando("ls", aguardar=1)["status"], "negada")
        # trocar de perfil NÃO destrava (antes destravava); só armar no celular devolve o poder
        self.ex.politica.aplicar_perfil("cauteloso")
        self.assertEqual(self.s.executar_comando("ping -c1 1.1.1.1", aguardar=0)["status"], "negada")
        self.ex.politica.armar()
        self.assertEqual(self.s.executar_comando("ping -c1 1.1.1.1", aguardar=0)["status"], "aguardando_aprovacao")
        self.s.propor_capacidade("eco2", manifesto=eco["manifesto"], arquivos=eco["arquivos"])
        self.assertEqual(self.s.capacidades("listar")["capacidades"][0].get("estado") if False else
                         next(c["estado"] for c in self.s.capacidades("listar")["capacidades"] if c["nome"] == "eco2"),
                         "aguardando_aprovacao")
        aud = (Path(self.pasta) / "auditoria.jsonl").read_text()
        self.assertIn("capacidade_auto_aprovada", aud)

    def test_agente_nao_aprova_a_si_mesmo(self):
        r = self.s.executar_comando("echo pelo chat", aguardar=0)
        self.assertEqual(r["status"], "aguardando_aprovacao")
        self.assertEqual(self.s.politica()["aprovacao_remota"], "desligada")  # o antigo "chat" não existe mais
        p = self.ex.politica.ler()
        p["aprovacao_remota"] = "chat"  # política antiga gravada no arquivo vira "desligada"
        self.ex.politica.gravar(p)
        for pedido in ({"tarefa": r["id"]}, {"liberar_minutos": 10}, {"destravar": True},
                       {"capacidade": "x", "sha": "abc"}):
            with self.assertRaises(Exception):
                self.s.autorizar(**pedido)
        self.assertEqual(self.s.tarefa(r["id"])["status"], "aguardando_aprovacao")
        self.assertIn("recusada_sem_codigo", (Path(self.pasta) / "auditoria.jsonl").read_text())

    def test_autorizar_de_outro_aparelho_e_travar(self):
        from controle_ir.execucao import totp
        p = self.ex.politica.ler()
        p["aprovacao_remota"] = "codigo"
        self.ex.politica.gravar(p)
        seg = self.ex.autorizacao.configurar()
        cod = lambda: totp(seg, int(time.time() // 30))  # noqa: E731
        r = self.s.executar_comando("echo remoto", aguardar=0)
        self.assertEqual(r["status"], "aguardando_aprovacao")
        with self.assertRaises(Exception):
            self.s.autorizar(codigo="111111", tarefa=r["id"])
        out = self.s.autorizar(codigo=cod(), tarefa=r["id"])
        self.assertEqual(out["tarefa"]["status"], "executando")
        with self.assertRaises(Exception):  # código já usado
            self.s.autorizar(codigo=cod(), liberar_minutos=10)
        self.assertTrue(self.s.travar()["travado"])
        self.assertEqual(self.s.executar_comando("ls", aguardar=1)["status"], "negada")
        self.ex.autorizacao._gravar({**self.ex.autorizacao._ler(), "ultimo": 0})  # próximo passo de 30 s
        self.s.autorizar(codigo=cod(), destravar=True, liberar_minutos=5)
        self.assertEqual(self.s.executar_comando("echo livre; true", aguardar=10)["status"], "concluida")
        aud = (Path(self.pasta) / "auditoria.jsonl").read_text()
        self.assertIn("autorizacao_remota", aud)
        self.assertIn("travado_remotamente", aud)

    def test_reverter_so_shell(self):
        from controle_ir.cli import REVERTER_SH
        home = Path(tempfile.mkdtemp())
        (home / "controle-ir").mkdir()
        (home / "controle-ir" / "v").write_text("nova")
        (home / "controle-ir.anterior").mkdir()
        (home / "controle-ir.anterior" / "v").write_text("antiga")
        binp = home / "bin"
        binp.mkdir()
        for nome in ("termux-toast", "controle-ir"):
            (binp / nome).write_text("#!/bin/sh\necho \"$0 $*\" >> \"$HOME/chamadas\"\n")
            (binp / nome).chmod(0o755)
        env = dict(os.environ, HOME=str(home), PATH=f"{binp}:{os.environ['PATH']}")
        self.assertEqual(subprocess.run(["sh", "-c", REVERTER_SH], env=env).returncode, 0)
        self.assertEqual((home / "controle-ir" / "v").read_text(), "antiga")
        self.assertEqual((home / "controle-ir.quebrada" / "v").read_text(), "nova")
        self.assertIn("controle-ir ligar", (home / "chamadas").read_text())


@unittest.skipUnless(hasattr(os, "fork") and sys.platform.startswith("linux"), "precisa de Linux (como o Termux)")
class TestSegundoPlano(unittest.TestCase):
    """Início automático (Termux:Boot), serviço em segundo plano, console e parar — num HOME temporário."""

    def setUp(self):
        import socket
        from controle_ir import __version__
        self.tmp = Path(tempfile.mkdtemp(prefix="cir-fundo-"))
        home = self.tmp / "home"
        self.pasta = home / ".controle-ir"
        self.pasta.mkdir(parents=True)
        shutil.copy(catalogo_base(), self.pasta / "catalogo.sqlite")
        (self.pasta / "catalogo.versao").write_text("catalogo-1:" + str(BASE.stat().st_mtime))
        so = socket.socket()
        so.bind(("127.0.0.1", 0))
        self.porta = so.getsockname()[1]
        so.close()
        self.segredo = "segredo-do-teste-de-fundo"
        (self.pasta / "config.json").write_text(json.dumps({"segredo": self.segredo, "porta": self.porta,
                                                            "tunel": {"modo": "nenhum"}}))
        self.boot = home / ".termux" / "boot" / "controle-ir"
        self.env = dict(os.environ, HOME=str(home), CONTROLE_IR_DIR=str(self.pasta),
                        CONTROLE_IR_BOOT_DIR=str(self.boot.parent), PYTHONPATH=str(RAIZ / "controle-ir"),
                        PYTHONUNBUFFERED="1")

    def tearDown(self):
        self.cli("parar")
        shutil.rmtree(self.tmp, ignore_errors=True)

    def cli(self, *args):
        r = subprocess.run([sys.executable, "-m", "controle_ir", *args], env=self.env, capture_output=True,
                           text=True, timeout=60, stdin=subprocess.DEVNULL)
        return r.returncode, r.stdout + r.stderr

    def saude(self):
        op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with op.open(f"http://127.0.0.1:{self.porta}/saude", timeout=1):
                return True
        except OSError:
            return False

    def esperar(self, cond, seg=20):
        fim = time.time() + seg
        while time.time() < fim:
            if cond():
                return True
            time.sleep(0.2)
        return False

    def test_script_do_termux_boot(self):
        self.assertEqual(self.cli("inicio-automatico")[0], 1)
        self.assertEqual(self.cli("inicio-automatico", "sim")[0], 0)
        txt = self.boot.read_text()
        self.assertTrue(txt.startswith("#!") and txt.rstrip().endswith("iniciar --fundo"))
        self.assertIn("termux-wake-lock", txt)
        self.assertEqual(self.boot.stat().st_mode & 0o777, 0o700)
        self.assertEqual(self.cli("inicio-automatico", "status")[0], 0)
        self.assertIn("ativado", self.cli("status")[1])
        self.cli("inicio-automatico", "nao")
        self.assertFalse(self.boot.exists())

    def test_fundo_log_sem_segredo_instancia_unica_e_parar(self):
        p = subprocess.Popen([sys.executable, "-m", "controle_ir", "iniciar", "--fundo", "--simulado"], env=self.env,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)
        try:
            self.assertTrue(self.esperar(self.saude))
            est = json.loads((self.pasta / "servidor.json").read_text())
            self.assertTrue(est["fundo"])
            self.assertEqual(est["pid"], p.pid)
            self.assertIn("já está rodando", self.cli("iniciar", "--fundo", "--simulado")[1])
            self.assertIn("rodando em segundo plano", self.cli("status")[1])
            log = self.pasta / "servico.log"
            self.assertIn("em segundo plano", log.read_text())
            self.assertNotIn(self.segredo, log.read_text())
            self.assertEqual(log.stat().st_mode & 0o777, 0o600)
            self.assertIn("Serviço encerrado", self.cli("parar")[1])
            self.assertEqual(p.wait(timeout=10), 0)
            self.assertFalse(self.saude())
            self.assertFalse((self.pasta / "servidor.json").exists())
        finally:
            if p.poll() is None:
                p.kill()

    def test_parar_nao_mata_pid_reaproveitado(self):
        # servidor.json velho (celular reiniciou) apontando para um processo que não é o controle-ir
        outro = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            (self.pasta / "servidor.json").write_text(json.dumps({"pid": outro.pid, "porta": self.porta}))
            self.assertIn("não está rodando", self.cli("parar")[1])
            self.assertIsNone(outro.poll())
        finally:
            outro.kill()
            outro.wait()

    def test_atualizar_programa_nao_refaz_catalogo(self):
        base = str(BASE.stat().st_mtime)
        versao = self.pasta / "catalogo.versao"
        versao.write_text("1.0.6:" + base)  # carimbo gravado pela 1.0.6 no celular
        self.assertIn("já está atualizado", self.cli("catalogo", "atualizar")[1])
        versao.write_text("1.0.6:123.0")  # base diferente: refaz
        self.assertIn("importados", self.cli("catalogo", "atualizar")[1])
        self.assertTrue(versao.read_text().startswith("catalogo-1:"))
        self.assertIn("já está atualizado", self.cli("catalogo", "atualizar")[1])

    def test_atalhos_do_widget_ligar_e_desligar(self):
        self.assertEqual(self.cli("atalhos")[0], 0)
        tarefas = Path(self.env["HOME"]) / ".shortcuts" / "tasks"
        ligar, desligar = tarefas / "Ligar Controle IR", tarefas / "Desligar Controle IR"
        self.assertTrue(ligar.read_text().rstrip().endswith(" ligar"))
        self.assertIn("termux-wake-lock", ligar.read_text())
        self.assertTrue(desligar.read_text().rstrip().endswith(" desligar"))
        reiniciar = tarefas / "Reiniciar Controle IR"
        self.assertTrue(reiniciar.read_text().rstrip().endswith(" reiniciar"))
        for f in (ligar, desligar, reiniciar, tarefas, tarefas.parent):
            self.assertEqual(f.stat().st_mode & 0o777, 0o700)
        self.assertTrue((tarefas / "Modo autonomo Controle IR").read_text().rstrip().endswith("exec modo autonomo"))
        self.assertTrue((tarefas / "Travar Controle IR").read_text().rstrip().endswith("exec travar"))
        self.assertTrue((tarefas / "Modo cauteloso Controle IR").exists())
        self.assertIn("já estava desligado", self.cli("desligar")[1])
        self.assertIn("desligar: pedido", (self.pasta / "servico.log").read_text())  # rastro mesmo sem serviço
        p = subprocess.Popen([sys.executable, "-m", "controle_ir", "ligar"], env=self.env, stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        try:
            self.assertTrue(self.esperar(self.saude))
            self.assertIn("já está ligado", self.cli("ligar")[1])
            self.assertIn("ligar: já estava ligado", (self.pasta / "servico.log").read_text())
            self.assertTrue(self.esperar(lambda: "ligado — pode pedir" in
                                         (self.pasta / "servico.log").read_text(), 5))
            self.assertIn("Controle IR desligado", self.cli("desligar")[1])
            self.assertEqual(p.wait(timeout=10), 0)
            self.assertFalse(self.saude())
        finally:
            if p.poll() is None:
                p.kill()

    def test_reiniciar_servico_em_execucao(self):
        def processo(cmd):
            return subprocess.Popen([sys.executable, "-m", "controle_ir", cmd], env=self.env,
                                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, start_new_session=True)
        processos = []
        try:
            primeiro = processo("ligar")
            processos.append(primeiro)
            self.assertTrue(self.esperar(lambda: (self.pasta / "servidor.json").is_file() and self.saude()))
            segundo = processo("reiniciar")
            processos.append(segundo)
            self.assertEqual(primeiro.wait(timeout=20), 0)
            def reiniciado():
                try:
                    return json.loads((self.pasta / "servidor.json").read_text())["pid"] == segundo.pid and self.saude()
                except (OSError, ValueError):
                    return False
            self.assertTrue(self.esperar(reiniciado))
        finally:
            self.cli("desligar")
            for p in processos:
                if p.poll() is None:
                    p.kill()
                p.wait()

    def test_console_abre_em_segundo_plano_e_sair_nao_derruba(self):
        import pty
        import select
        self.cli("inicio-automatico", "sim")

        def abrir_console(comandos, espera_inicial):
            pid, fd = pty.fork()
            if pid == 0:  # pragma: no cover — processo filho
                os.execve(sys.executable, [sys.executable, "-m", "controle_ir"], self.env)
            saida = bytearray()

            def ler(seg):
                fim = time.time() + seg
                while time.time() < fim:
                    r, _, _ = select.select([fd], [], [], 0.2)
                    if r:
                        try:
                            saida.extend(os.read(fd, 4096))
                        except OSError:
                            return
            ler(espera_inicial)
            for c in comandos:
                os.write(fd, c)
                ler(1.5)
            _, status = os.waitpid(pid, 0)
            os.close(fd)
            return status, saida.decode(errors="replace")

        status, txt = abrir_console([b"\n", b"sair\n"], 1)
        self.assertEqual(status, 0)
        self.assertIn("segundo plano", txt)
        self.assertIn("nada pausado", txt)
        self.assertTrue(self.esperar(self.saude))
        status, txt = abrir_console([b"sair\n"], 2)
        self.assertIn("já está rodando", txt)
        self.assertTrue(self.saude(), "sair do console não pode encerrar o serviço")



class TestTunel(unittest.TestCase):
    """O túnel ngrok encerra agentes órfãos antes de abrir (senão o domínio fixo fica preso e dá Not Found)."""

    def _tunel(self, modo):
        from controle_ir.tunel import Tunel
        return Tunel(8765, {"modo": modo, "dominio": "x.ngrok-free.app"})

    def test_falha_ao_criar_processo_tenta_novamente(self):
        from unittest import mock
        t = self._tunel("ngrok")
        def tentativa(*args, **kwargs):
            if iniciar.call_count == 2:
                t.parar_evento.set()
            raise OSError("falha temporária")
        with mock.patch.object(t, "limpar_orfaos"), mock.patch("shutil.which", return_value="/bin/ngrok"), \
                mock.patch.object(t.parar_evento, "wait") as espera, \
                mock.patch("subprocess.Popen", side_effect=tentativa) as iniciar:
            t._laco()
        self.assertEqual(iniciar.call_count, 2)
        self.assertEqual(espera.call_args_list[0], mock.call(3))

    def test_limpa_orfao_so_no_modo_ngrok(self):
        from unittest import mock
        chamadas = []
        def falso_run(cmd, **kw):
            chamadas.append(cmd)
            return subprocess.CompletedProcess(cmd, 0)
        with mock.patch("controle_ir.tunel.shutil.which", return_value="/bin/pkill"), \
             mock.patch("controle_ir.tunel.subprocess.run", side_effect=falso_run), \
             mock.patch("controle_ir.tunel.time.sleep"):
            self.assertTrue(self._tunel("ngrok").limpar_orfaos())
            self.assertFalse(self._tunel("rapido").limpar_orfaos())
            self.assertFalse(self._tunel("cloudflare").limpar_orfaos())
        self.assertEqual(chamadas, [["pkill", "-x", "ngrok"]])

    def test_sem_orfao_nao_espera(self):
        from unittest import mock
        with mock.patch("controle_ir.tunel.shutil.which", return_value="/bin/pkill"), \
             mock.patch("controle_ir.tunel.subprocess.run",
                        return_value=subprocess.CompletedProcess(["pkill"], 1)), \
             mock.patch("controle_ir.tunel.time.sleep") as dormir:
            self.assertFalse(self._tunel("ngrok").limpar_orfaos())
            dormir.assert_not_called()

    def test_parar_encerra_o_grupo_inteiro(self):
        t = self._tunel("nenhum")
        neto = Path(tempfile.mkdtemp()) / "neto.pid"
        t.proc = subprocess.Popen([sys.executable, "-c", "import subprocess,sys,time;"
                                   "p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)']);"
                                   f"open({str(neto)!r},'w').write(str(p.pid));time.sleep(30)"],
                                  start_new_session=True)
        for _ in range(50):
            if neto.exists() and neto.read_text():
                break
            time.sleep(0.1)
        pid_neto = int(neto.read_text())
        t.parar()
        self.assertIsNotNone(t.proc.poll())
        time.sleep(0.3)

        def vivo(pid):  # zumbi (sem init para recolher no contêiner) conta como encerrado
            try:
                return "\tZ" not in Path(f"/proc/{pid}/status").read_text().split("State:")[1][:4]
            except (OSError, IndexError):
                return False
        self.assertFalse(vivo(pid_neto))


class TestOuvirBipe(unittest.TestCase):
    """Detecção de bipe (tom curto e puro) em áudio sintético; sem microfone."""

    @classmethod
    def setUpClass(cls):
        try:
            import numpy  # noqa: F401
        except ImportError:
            raise unittest.SkipTest("numpy ausente")
        import importlib.util
        caminho = Path(__file__).resolve().parent.parent / "controle-ir" / "capacidades" / "ouvir_bipe" / "principal.py"
        spec = importlib.util.spec_from_file_location("ouvir_bipe_principal", caminho)
        cls.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.m)

    def _ruido(self, seg=4):
        import numpy as np
        return np.random.default_rng(7).normal(0, 0.05, 16000 * seg).astype(np.float32)

    def test_acha_bipe_no_ruido(self):
        import numpy as np
        x = self._ruido()
        t = np.arange(int(0.15 * 16000)) / 16000
        x[32000:32000 + t.size] += 0.3 * np.sin(2 * np.pi * 2730 * t)
        b = self.m.detectar_bipes(x)
        self.assertEqual(len(b), 1)
        self.assertAlmostEqual(b[0]["freq_hz"], 2730, delta=60)
        self.assertAlmostEqual(b[0]["inicio_s"], 2.0, delta=0.05)

    def test_ruido_e_tom_continuo_nao_sao_bipe(self):
        import numpy as np
        self.assertEqual(self.m.detectar_bipes(self._ruido()), [])
        x = self._ruido()
        x += 0.3 * np.sin(2 * np.pi * 1500 * np.arange(x.size) / 16000)  # zumbido longo (ventilador, motor)
        self.assertEqual(self.m.detectar_bipes(x), [])

    def test_fala_clique_e_artefato_baixo_nao_sao_bipe(self):
        import numpy as np
        rng = np.random.default_rng(3)
        x = rng.normal(0, 0.01, 16000 * 4).astype(np.float32)
        t = np.arange(int(0.3 * 16000)) / 16000
        x[16000:16000 + t.size] += 0.3 * sum(np.sin(2 * np.pi * 180 * k * t) / k for k in range(1, 30))  # voz
        x[40000:40080] += 0.9  # clique
        self.assertEqual(self.m.detectar_bipes(x), [])
        q = rng.normal(0, 1e-4, 16000 * 4).astype(np.float32)  # sala muda + tonzinho de compressão (−57 dBFS)
        q[20000:20800] += 0.002 * np.sin(2 * np.pi * 2300 * np.arange(800) / 16000)
        self.assertEqual(self.m.detectar_bipes(q), [])

    def test_janela_do_envio(self):
        bipes = [{"inicio_s": 0.5}, {"inicio_s": 3.2}, {"inicio_s": 9.0}]
        j = self.m.filtrar_janela(bipes, envio_s=3.0)
        self.assertEqual([b["inicio_s"] for b in j], [3.2])
        self.assertEqual(j[0]["atraso_s"], 0.2)
        self.assertEqual(self.m.filtrar_janela(bipes, None), bipes)

    def test_controlar_com_ouvir_envia_mesmo_sem_microfone(self):
        s, _ = novo_servico()
        s.salvar_aparelho("ar do quarto", perfil=105)
        r = s.controlar("ar do quarto", ligar=True, definir={"temperatura": 24, "modo": "frio"}, ouvir=True)
        self.assertEqual(r["status"], "sinal_enviado")
        self.assertEqual(r["ouvido"]["veredito"], "sem_escuta")  # sem Termux:API aqui: avisa, não falha
        self.assertNotIn("ouvido", s.controlar("ar do quarto", definir={"temperatura": 23}))

    def test_ouvido_do_ar_compara_ruido_antes_e_depois(self):
        import numpy as np
        rng = np.random.default_rng(5)
        T = 16000

        def sala(antes, depois, seg=11, envio=3.0):
            x = rng.normal(0, antes, T * seg).astype(np.float32)
            i = int((envio + 1.0) * T)  # o ventilador muda ~1 s depois do comando
            x[i:] = rng.normal(0, depois, x.size - i)
            t = np.arange(x.size - i) / T
            if depois > antes:
                x[i:] += 3 * depois * np.sin(2 * np.pi * 438 * t)  # zumbido do motor
            return x

        r = self.m.comparar_ruido(sala(0.003, 0.03), 3.0)
        self.assertEqual(r["veredito"], "mais_alto")
        self.assertTrue(any(abs(f - 438) <= 8 for f in r["tons_depois_hz"]), r["tons_depois_hz"])
        self.assertEqual(self.m.comparar_ruido(sala(0.03, 0.003), 3.0)["veredito"], "mais_baixo")
        self.assertEqual(self.m.comparar_ruido(sala(0.01, 0.01), 3.0)["veredito"], "sem_mudanca")
        self.assertIsNone(self.m.comparar_ruido(sala(0.01, 0.01, seg=3, envio=1.0), 1.0))  # pouco áudio antes/depois

    def test_comparar_com_referencia(self):
        bipes = [{"freq_hz": 2700}, {"freq_hz": 4000}]
        self.assertEqual(self.m.comparar(bipes, {"freq_hz": 2750}), [{"freq_hz": 2700}])
        self.assertEqual(self.m.comparar(bipes, None), [])


class TestImagemNoMcp(unittest.TestCase):
    """Capacidade que devolve _imagem vira conteúdo de imagem do MCP (o Claude enxerga), sem base64 no texto."""

    def test_imagem_vira_conteudo_de_imagem(self):
        from controle_ir.mcp import ServidorMCP
        r = ServidorMCP._resultado({"capacidade": "foto", "status": "ok",
                                    "resultado": {"bytes": 3, "_imagem": {"mime": "image/jpeg", "base64": "QUJD"}}},
                                   False)
        tipos = [c["type"] for c in r["content"]]
        self.assertEqual(tipos, ["text", "image"])
        self.assertEqual(r["content"][1], {"type": "image", "data": "QUJD", "mimeType": "image/jpeg"})
        self.assertNotIn("QUJD", r["content"][0]["text"])
        self.assertEqual(r["structuredContent"]["resultado"]["imagens_anexadas"], 1)

    def test_sem_imagem_fica_igual(self):
        from controle_ir.mcp import ServidorMCP
        r = ServidorMCP._resultado({"ok": True}, False)
        self.assertEqual([c["type"] for c in r["content"]], ["text"])

    def test_recorte_da_foto(self):
        import importlib.util
        caminho = Path(__file__).resolve().parent.parent / "controle-ir" / "capacidades" / "foto" / "principal.py"
        spec = importlib.util.spec_from_file_location("foto_principal", caminho)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        self.assertEqual(m.validar_recorte([0.5, 0.1, 0.7, 0.3]), [0.5, 0.1, 0.7, 0.3])
        for ruim in ([0.7, 0.1, 0.5, 0.3], [0, 0, 1], [0, 0, 1.2, 1], [0.5, 0.5, 0.51, 0.9], "x"):
            with self.assertRaises(ValueError):
                m.validar_recorte(ruim)
        self.assertEqual(m.filtro(960, [0.5, 0.1, 0.7, 0.3]),
                         "crop=iw*0.2000:ih*0.2000:iw*0.5000:ih*0.1000,scale='min(960,iw)':-2")
        self.assertEqual(m.filtro(960), "scale='min(960,iw)':-2")

    def test_foto_embutida_e_ativa(self):
        s, _ = novo_servico(com_base=False)
        self.assertEqual({c["nome"]: c["estado"] for c in s.capacidades()["capacidades"]}.get("foto"), "ativa")


class TestTela(unittest.TestCase):
    """Agente de tela: leitura do dump do uiautomator, busca por texto, bloqueio de apps e escape do input text."""

    XML = ('<?xml version="1.0" encoding="UTF-8"?><hierarchy rotation="0">'
           '<node text="" class="android.widget.FrameLayout" package="com.android.settings" clickable="false" '
           'bounds="[0,0][1080,2400]">'
           '<node text="Wi-Fi" resource-id="android:id/title" class="android.widget.TextView" '
           'package="com.android.settings" content-desc="" clickable="false" bounds="[40,300][400,360]"/>'
           '<node text="" content-desc="Configurações de Wi-Fi" class="android.widget.LinearLayout" '
           'package="com.android.settings" clickable="true" bounds="[0,280][1080,380]"/>'
           '<node text="Bluetooth" class="android.widget.TextView" package="com.android.settings" clickable="true" '
           'bounds="[40,420][400,480]"/>'
           '<node text="" class="android.widget.EditText" package="com.android.settings" clickable="true" '
           'resource-id="com.android.settings:id/busca" bounds="[40,100][1040,180]"/>'
           '</node></hierarchy>')

    @classmethod
    def setUpClass(cls):
        import importlib.util
        caminho = Path(__file__).resolve().parent.parent / "controle-ir" / "capacidades" / "tela" / "principal.py"
        spec = importlib.util.spec_from_file_location("tela_principal", caminho)
        cls.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.m)

    def test_elementos_e_busca(self):
        els = self.m.elementos(self.XML)
        self.assertEqual(len(els), 4)  # o FrameLayout vazio e não clicável fica de fora
        bt = self.m.achar(els, "bluetooth")
        self.assertEqual((bt["x"], bt["y"], bt["clicavel"]), (220, 450, True))
        wifi = self.m.achar(els, "wi-fi")  # o texto não é clicável; prefere o igual e clicável (a descrição contém)
        self.assertTrue(wifi["clicavel"] or wifi["texto"] == "Wi-Fi")
        self.assertEqual(self.m.achar(els, "configuracoes de wi-fi")["y"], 330)  # sem acento também acha
        self.assertEqual(self.m.achar(els, "busca")["editavel"], True)  # pelo id
        self.assertIsNone(self.m.achar(els, "nada disso"))
        self.assertEqual(self.m.elementos("isso não é xml"), [])

    def test_bloqueio_de_apps_sensiveis(self):
        lista = self.m.BLOQUEADOS_PADRAO
        for p in ("com.nu.production", "br.com.bb.android", "com.itau.empresas", "com.x8bit.bitwarden"):
            self.assertTrue(self.m.bloqueado(p, lista), p)
        for p in ("com.android.settings", "com.google.android.youtube", None):
            self.assertFalse(self.m.bloqueado(p, lista), p)

    def test_input_text_e_foco(self):
        self.assertEqual(self.m.escapar_input_text("oi mundo"), ("oi%smundo", None))
        t, aviso = self.m.escapar_input_text("ação 50%")
        self.assertEqual(t, "acao%s50\\%")
        self.assertIsNotNone(aviso)
        d = "  mCurrentFocus=Window{a1b2 u0 com.android.settings/com.android.settings.Settings}"
        self.assertEqual(self.m.app_em_foco(d), "com.android.settings")
        self.assertEqual(self.m.ler_bounds("[0,280][1080,380]"), (0, 280, 1080, 380))

    def test_tela_embutida_e_ativa(self):
        s, _ = novo_servico(com_base=False)
        self.assertEqual({c["nome"]: c["estado"] for c in s.capacidades()["capacidades"]}.get("tela"), "ativa")


class TestTelaPorArquivo(unittest.TestCase):
    """O rish devolve a saída por arquivo na pasta de troca (o cano do rish cortava e misturava saídas no POCO).

    Um rish falso roda o comando com sh, e screencap/uiautomator/input falsos ficam no PATH."""

    def setUp(self):
        import importlib.util
        caminho = Path(__file__).resolve().parent.parent / "controle-ir" / "capacidades" / "tela" / "principal.py"
        spec = importlib.util.spec_from_file_location("tela_por_arquivo", caminho)
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        rish = self.tmp / "rish" / "rish"
        rish.parent.mkdir()
        rish.write_text('if [ "$1" = "-c" ]; then shift; exec sh -c "$1"; else exec sh; fi\n')  # imita o rish
        bin_ = self.tmp / "bin"
        bin_.mkdir()
        (bin_ / "uiautomator").write_text(f'cat > "$2" <<\'FIM\'\n{TestTela.XML}\nFIM\necho "UI hierchary dumped to: $2"\n')
        # como no POCO: o system_server recusa a saída de `cmd input` na memória compartilhada ou num cano
        (bin_ / "input").write_text('case "$(readlink /proc/$$/fd/1) $(readlink /proc/$$/fd/0)" in *compartilhada*|*pipe:*) '
                                    'echo "cmd: Failure calling service input: Failed transaction (2147483646)"; exit 2;; esac\n'
                                    'if [ "$BLOQUEAR_INPUT" = 1 ]; then echo "java.lang.SecurityException: Injecting '
                                    'to another application requires INJECT_EVENTS permission" >&2; exit 1; fi\n'
                                    'if [ "$BLOQUEAR_INPUT" = 2 ]; then echo "cmd: Failure calling service input: '
                                    'Failed transaction (2147483646)"; exit 2; fi\n'
                                    'echo "input $*" >> "$REGISTRO_INPUT"\n')
        for f in bin_.iterdir():
            f.chmod(0o755)
        self.m.RISH = str(rish)
        self.m.COMPARTILHADA = str(self.tmp / "compartilhada")
        self.m.TMP = str(self.tmp / "tela")
        self.m.TMP_SHELL = str(self.tmp / "local_tmp")
        Path(self.m.TMP_SHELL).mkdir()
        self.registro = self.tmp / "input.log"
        self.env = mock.patch.dict(os.environ, {"PATH": f"{bin_}:{os.environ['PATH']}",
                                                "REGISTRO_INPUT": str(self.registro)})
        self.env.start()
        self.addCleanup(self.env.stop)

    def _sobras(self):
        return [p.name for p in Path(self.m.COMPARTILHADA).iterdir() if p.name != ".nomedia"]

    def test_saida_erro_e_codigo_por_arquivo(self):
        out, err, cod = self.m.rish("echo oi; echo ruim >&2; exit 3")
        self.assertEqual((out, err, cod), ("oi\n", "ruim\n", 3))
        grande = self.m.rish("head -c 300000 /dev/zero | tr '\\0' x")[0]
        self.assertEqual(len(grande), 300000)  # sem corte
        self.assertEqual(self._sobras(), [])  # nada fica na memória compartilhada
        self.assertEqual(list(Path(self.m.TMP_SHELL).iterdir()), [])  # nem na área do shell
        self.assertTrue((Path(self.m.COMPARTILHADA) / ".nomedia").exists())

    def test_dump_ui_e_toque(self):
        self.assertTrue(self.m.dump_ui().startswith("<?xml"))
        r = self.m.agir({"acao": "tocar", "texto": "bluetooth"})
        self.assertEqual(r["feito"], "toque em 220,450")
        self.assertIn("input tap 220 450", self.registro.read_text())
        for modo in ("1", "2"):  # SecurityException (MIUI) e "Failed transaction" (HyperOS 3 no POCO)
            with mock.patch.dict(os.environ, {"BLOQUEAR_INPUT": modo}):
                r = self.m.agir({"acao": "tecla", "tecla": "voltar"})
            self.assertIn("Configurações de segurança", r["erro"], modo)
        self.assertEqual(self._sobras(), [])

    def _dumpsys_falso(self, foco="com.android.settings"):
        d = self.tmp / "bin" / "dumpsys"
        d.write_text('case "$1" in window) echo "  mCurrentFocus=Window{1a2b u0 ${FOCO:-%s}/.Principal}";; '
                     'power) echo "  mWakefulness=Awake";; esac\n' % foco)
        d.chmod(0o755)

    def test_sequencia_numa_viagem(self):
        self._dumpsys_falso()
        chamadas = []
        original = self.m.rish
        self.m.rish = lambda cmd, timeout=20: (chamadas.append(cmd), original(cmd, timeout))[1]
        r = self.m.agir({"acao": "sequencia", "passos": [
            {"tocar": [10, 20]}, {"tocar": [[1, 2], [3, 4]], "intervalo": 0}, {"tecla": "voltar"},
            {"digitar": "oi mundo"}, {"esperar": 0.01}, {"esperar_texto": "Bluetooth", "ate": 2},
            {"tocar": "bluetooth"}, {"deslizar": [1, 2, 3, 4]}]})
        self.assertIn("8 passos", r["feito"])
        log = self.registro.read_text().splitlines()
        self.assertEqual(log, ["input tap 10 20", "input tap 1 2", "input tap 3 4", "input keyevent 4",
                               "input text oi%smundo", "input tap 220 450", "input swipe 1 2 3 4 300"])
        toques = [c for c in chamadas if "input " in c]
        self.assertEqual(len(toques), 2)  # 5 passos de uma vez; o toque por texto precisou ler a tela antes
        self.assertEqual(r["app"], "com.android.settings")
        self.assertEqual(self._sobras(), [])

    def test_sequencia_recusa_app_bloqueado_e_texto_ausente(self):
        self._dumpsys_falso("com.nu.production")
        r = self.m.agir({"acao": "sequencia", "passos": [{"tocar": [10, 20]}]})
        self.assertIn("bloqueados", r["erro"])
        self.assertNotIn("toque", self.registro.read_text() if self.registro.exists() else "")  # nenhum toque saiu
        self._dumpsys_falso()
        r = self.m.agir({"acao": "sequencia", "passos": [{"esperar_texto": "Inexistente", "ate": 0.5}]})
        self.assertIn("não apareceu", r["erro"])
        self.assertIn("passo", self.m.agir({"acao": "sequencia", "passos": [{"pular": 1}]})["erro"])

    def test_ver_em_uma_chamada_e_compacto(self):
        self._dumpsys_falso()
        if shutil.which("ffmpeg"):
            png = self.tmp / "origem.png"
            subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=c=blue:s=400x800", "-frames:v", "1",
                            str(png)], check=True, capture_output=True)
            sc = self.tmp / "bin" / "screencap"
            sc.write_text(f'cp "{png}" "$2"\n')
            sc.chmod(0o755)
        chamadas = []
        original = self.m.rish
        self.m.rish = lambda cmd, timeout=20: (chamadas.append(cmd), original(cmd, timeout))[1]
        r = self.m.ver(imagem=bool(shutil.which("ffmpeg")), largura=320, recorte=[0, 0, 200, 200], formato="json")
        self.assertEqual(len(chamadas), 1)  # dump, captura, foco e tela acesa numa viagem só
        self.assertEqual((r["app"], r["tela_acesa"]), ("com.android.settings", True))
        bt = [e for e in r["elementos"] if e.get("texto") == "Bluetooth"][0]
        self.assertNotIn("classe", bt)
        self.assertNotIn("desc", bt)  # vazio não vai na resposta
        if shutil.which("ffmpeg"):
            self.assertEqual(r["resolucao"], "400x800")
            self.assertTrue(base64.b64decode(r["_imagem"]["base64"]).startswith(b"\xff\xd8"))
        self.assertEqual(self._sobras(), [])
        r2 = self.m.agir({"acao": "tecla", "tecla": "voltar"})  # sem ver_depois: resposta curta
        self.assertEqual(set(r2), {"feito", "app"})

    def _leitor_falso(self, quebrado=False):
        """app_process falso: fala o protocolo do Tela.java (linhas na entrada, respostas em PASTA/ID.r)."""
        ap = self.tmp / "bin" / "app_process"
        ap.write_text(f"""#!{sys.executable}
import os, subprocess, sys
import time
pasta, token = sys.argv[3], sys.argv[4]
if {quebrado!r}:
    sys.exit(1)
open(os.path.join(pasta, "pronto-" + token), "w").close()
xml = {TestTela.XML!r}
reg = os.environ["REGISTRO_INPUT"]
cont = 0
for linha in sys.stdin:
    p = linha.split()
    if not p:
        continue
    ident, cmd = p[0], p[1]
    if cmd == "dump":
        r = xml
    elif cmd in ("foco", "estado"):
        arq = os.environ.get("FOCO_ARQ", "")
        r = open(arq).read().strip() if arq and os.path.exists(arq) else "com.android.settings"
        if cmd == "estado":
            r += "\\n1"
    elif cmd == "calma":
        open(reg, "a").write("leitor " + " ".join(p[1:]) + "\\n")
        r = "ok 3"
    elif cmd == "eventos":
        cont += 1
        jan = os.path.join(os.path.dirname(reg), "janela.txt")
        chave = open(jan).read().strip() if os.path.exists(jan) else "com.android.settings|com.android.settings.Principal|"
        r = f"0 {{cont}} {{int(time.monotonic() * 1000)}} " + chave
    elif cmd == "historico":
        h = os.path.join(os.path.dirname(reg), "historico.txt")
        r = f"{{int(time.monotonic() * 1000) - 1500}} " + open(h).read().strip() if os.path.exists(h) else ""
    elif cmd == "toquesv":
        open(reg, "a").write("leitor " + " ".join(p[1:]) + "\\n")
        parar = os.path.join(os.path.dirname(reg), "parar.txt")
        r = "ok"
        if os.path.exists(parar):
            r = "parou 1 " + open(parar).read().strip()
            os.remove(parar)
    elif cmd == "aguardar":
        r = str(int(p[2]) + 1)
    elif cmd in ("limparmodelos", "modelos"):
        open(reg, "a").write("leitor " + " ".join(p[1:]) + "\\n")
        r = "ok 9"
    elif cmd == "ler":
        g1, g2 = (os.path.join(os.path.dirname(reg), f) for f in ("grade1.txt", "grade2.txt"))
        lidas = getattr(sys, "lidas", 0) + 1
        sys.lidas = lidas
        txt = open(g2 if lidas > 2 and os.path.exists(g2) else g1).read().strip()
        r = "\\n".join(" ".join(ch for ch in ln) for ln in txt.split("\\n"))
    elif cmd == "shell":
        pr = subprocess.run(["sh", "-c", bytes.fromhex(p[2]).decode()], capture_output=True, text=True)
        r = f"{{pr.returncode}} {{len(pr.stdout)}}\\n" + pr.stdout + pr.stderr
    elif cmd == "texto":
        open(reg, "a").write("leitor texto " + bytes.fromhex(p[2]).decode() + "\\n")
        r = "ok"
    else:
        open(reg, "a").write("leitor " + " ".join(p[1:]) + "\\n")
        r = "ok"
    tmp = os.path.join(pasta, ident + ".tmp")
    open(tmp, "w").write(r)
    os.replace(tmp, os.path.join(pasta, ident + ".r"))
    if cmd == "sair":
        break
""")
        ap.chmod(0o755)
        jar = self.tmp / "falso.jar"
        jar.write_bytes(b"jar")
        self.m._jar = lambda: str(jar)
        self.m.EM_PROCESSO = True
        self.m.AJUDANTE = self.m.Ajudante()
        self.addCleanup(self.m.AJUDANTE._matar)

    def test_leitor_rapido_aberto_entre_chamadas(self):
        self._leitor_falso()
        aberturas = []
        popen = subprocess.Popen
        with mock.patch.object(self.m.subprocess, "Popen", side_effect=lambda *a, **k: (aberturas.append(a), popen(*a, **k))[1]):
            self.assertTrue(self.m.dump_ui().startswith("<?xml"))
            self.assertEqual(self.m.foco(), "com.android.settings")
            self.assertEqual(self.m.rish("echo oi; echo ruim >&2; exit 2"), ("oi\n", "ruim\n", 2))
            r = self.m.agir({"acao": "tocar", "texto": "bluetooth"})
            self.assertEqual(r["feito"], "toque em 220,450")
            self.m.agir({"acao": "digitar", "texto": "olá, mundo"})
            rs = self.m.agir({"acao": "sequencia", "passos": [{"tocar": [5, 6]}, {"digitar": "ação"}, {"tecla": "voltar"}]})
            self.assertIn("3 passos", rs.get("feito", ""), rs)
        self.assertEqual(len(aberturas), 1)  # um só processo do leitor para tudo
        log = self.registro.read_text()
        self.assertIn("leitor tocar 220 450", log)  # toque injetado, sem o input do shell
        self.assertIn("leitor texto olá, mundo", log)  # com acento
        self.assertIn("leitor texto ação", log)
        self.assertIn("leitor toques 50 5 6", log)  # na sequência, os toques também vão injetados
        self.assertIn("leitor tecla 4", log)
        self.assertNotIn("input ", log)  # nada pelo `input` do shell
        self.assertIn("calma", log)  # depois de agir, espera a tela assentar antes de olhar
        self.assertEqual([p for p in self._sobras() if not p.startswith("pronto")], [])

    def test_ver_depois_diz_so_o_que_mudou(self):
        self._leitor_falso()
        r1 = self.m.agir({"acao": "tecla", "tecla": "voltar"})  # primeira olhada: lista inteira
        self.assertIn("elementos", r1["tela"])
        self.assertEqual(r1["tela"]["app"], "com.android.settings")
        self.assertIs(r1["tela"]["tela_acesa"], True)  # pelo leitor, sem dumpsys
        r2 = self.m.agir({"acao": "sequencia", "passos": [{"tocar": [5, 6]}]})
        self.assertEqual(r2["tela"]["mudancas"], "nenhuma")
        self.assertIn("acoes", r2["tempos"])

    def test_diferenca_entre_telas(self):
        a = [{"id": "placar", "texto": "0", "x": 1, "y": 1}, {"texto": "Sair", "x": 5, "y": 5},
             {"id": "ok", "x": 9, "y": 9, "clicavel": True}]
        d = [{"id": "placar", "texto": "10", "x": 1, "y": 1}, {"id": "ok", "x": 9, "y": 9, "clicavel": True},
             {"texto": "Venceu!", "x": 3, "y": 3}]
        dif = self.m.diferenca(a, d, "app", "app")
        self.assertEqual(dif["entrou"], [{"texto": "Venceu!", "x": 3, "y": 3}])
        self.assertEqual(dif["saiu"], [{"texto": "Sair", "x": 5, "y": 5}])
        self.assertEqual(dif["mudou"], [{"id": "placar", "texto": "10", "x": 1, "y": 1, "antes": {"texto": "0"}}])
        self.assertIsNone(self.m.diferenca(a, d, "app", "outro"))  # outro app: lista inteira
        self.assertIsNone(self.m.diferenca(None, d))  # primeira olhada
        muitos = [{"texto": str(k), "x": k, "y": k} for k in range(40)]
        self.assertIsNone(self.m.diferenca(a, muitos, "app", "app"))  # tela nova de fato

    def test_condicoes_e_lacos_no_celular(self):
        self._leitor_falso()
        r = self.m.agir({"acao": "sequencia", "ver_depois": "nada", "passos": [
            {"se": "Bluetooth", "entao": [{"tocar": [1, 1]}], "senao": [{"tocar": [2, 2]}]},
            {"se_nao": "Bluetooth", "entao": [{"tocar": [3, 3]}]},
            {"repetir": [{"tocar": [4, 4], "intervalo": 0}], "vezes": 5, "ate_texto": "Bluetooth"},
            {"tocar": [[7, 8]], "segurar": 600}, {"calma": 0.5}]})
        self.assertIn("7 passos", r["feito"], r)  # 5 da lista + 2 dos ramos e do laço
        log = self.registro.read_text()
        self.assertIn("leitor toques 50 1 1", log)
        self.assertNotIn(" 2 2", log)
        self.assertNotIn(" 3 3", log)
        self.assertEqual(log.count("leitor toques 0 4 4"), 1)  # o texto já estava lá: uma volta só
        self.assertIn("leitor tocar 7 8 600", log)
        self.assertIn("leitor calma 120 500", log)
        r = self.m.agir({"acao": "sequencia", "passos": [
            {"repetir": [{"tocar": [4, 4]}], "vezes": 3, "ate_sumir": "Bluetooth"}]})
        self.assertIn("repetiu 3 vezes", r["erro"])
        r = self.m.agir({"acao": "sequencia", "passos": [{"repetir": [{"repetir": [{"repetir": [{"repetir": [
            {"repetir": [{"tocar": [1, 1]}]}]}]}]}]}]})
        self.assertIn("aninhados", r["erro"])

    def test_reflexo_para_quando_surge_outra_janela(self):
        self._leitor_falso()
        (self.tmp / "parar.txt").write_text("com.outro|com.outro.PopupActivity|Aviso")
        r = self.m.agir({"acao": "sequencia", "passos": [{"tocar": [[1, 1], [2, 2], [3, 3]]}, {"tocar": [9, 9]}]})
        self.assertIn("janela nova", r["interrompido"])
        self.assertIn("PopupActivity", r["interrompido"])
        self.assertIn("depois de 1 de 3 toques", r["interrompido"])
        self.assertNotIn(" 9 9", self.registro.read_text())  # o passo seguinte não saiu
        self.assertIn("tela", r)  # e já vem o que está na tela para decidir de novo

    def test_reflexo_segue_se_e_a_mesma_tela(self):
        self._leitor_falso()
        (self.tmp / "parar.txt").write_text("com.android.settings|com.android.settings.Principal|")
        r = self.m.agir({"acao": "sequencia", "ver_depois": "nada", "passos": [{"tocar": [[1, 1], [2, 2], [3, 3]]}]})
        self.assertNotIn("interrompido", r)
        log = self.registro.read_text()
        self.assertIn("leitor toquesv 50 1 1 2 2 3 3", log)
        self.assertIn("leitor toquesv 50 2 2 3 3", log)  # retomou de onde parou

    def test_reflexo_por_texto_e_espera_de_mudanca(self):
        self._leitor_falso()
        r = self.m.agir({"acao": "sequencia", "parar_se": ["bluetooth"], "ver_depois": "nada",
                         "passos": [{"tocar": [[1, 1], [2, 2], [3, 3]]}]})
        self.assertIn("Bluetooth", r["interrompido"])
        self.assertIn("220,450", r["elemento"])
        self.assertNotIn(" 3 3", self.registro.read_text())  # parou depois do 1º pedaço de 2 toques
        t = time.time()
        r = self.m.agir({"acao": "sequencia", "ver_depois": "nada", "passos": [{"esperar_mudanca": 0.3}]})
        self.assertGreaterEqual(time.time() - t, 0.25)  # nada mudou: esperou o prazo e seguiu
        self.assertIn("1 passos", r["feito"])
        self.assertTrue(self.m.janela_nova("a|A|", "b|B|"))
        self.assertFalse(self.m.janela_nova("a|A|", "a|A|outro"))
        self.assertFalse(self.m.janela_nova("a|A|", "teclado|android.inputmethodservice.SoftInputWindow|"))

    def test_formato_curto(self):
        e = {"texto": "Sincronizar", "id": "syncTv", "x": 640, "y": 2375, "clicavel": True, "marcado": False}
        self.assertEqual(self.m.curto(e), '"Sincronizar" #syncTv 640,2375 cm')
        self.assertEqual(self.m.curto({"desc": "Voltar", "x": 1, "y": 2}), "(Voltar) 1,2")
        dif = {"entrou": [{"texto": "Venceu!", "x": 3, "y": 3}], "saiu": [{"texto": "Sair", "x": 5, "y": 5}],
               "mudou": [{"id": "placar", "texto": "10", "x": 1, "y": 1, "antes": {"texto": "0"}}]}
        self.assertEqual(self.m.diferenca_curta(dif), ['+ "Venceu!" 3,3', '- "Sair" 5,5', '~ "10" #placar 1,1 (era "0")'])

    def test_linha_do_tempo_e_reflexos(self):
        self._leitor_falso()
        self.m.REFLEXOS_ARQ = str(self.tmp / "reflexos.json")
        self.m.ver(imagem=False)  # primeira olhada marca a hora
        (self.tmp / "historico.txt").write_text("com.x|com.x.Popup|Oi")
        r = self.m.ver(imagem=False, so_mudancas=True)
        self.assertEqual(r["surgiu"], ["-1.5s com.x Popup «Oi»"])  # o que surgiu enquanto o Claude pensava
        self.assertIn("erro", self.m.reflexos([{"se": "x"}]))  # sem ação
        self.assertIn("erro", self.m.reflexos([{"se": "x", "tecla": "pular"}]))
        self.m.reflexos([{"janela": "PopupActivity", "tecla": "voltar"}])
        self.assertEqual(self.m.executar({"acao": "reflexos"})["regras"][0]["janela"], "PopupActivity")
        (self.tmp / "parar.txt").write_text("com.outro|com.outro.PopupActivity|Aviso")
        r = self.m.agir({"acao": "sequencia", "ver_depois": "nada", "passos": [{"tocar": [[1, 1], [2, 2], [3, 3]]}]})
        self.assertNotIn("interrompido", r)  # o reflexo resolveu sem parar
        self.assertEqual(r["reflexos"], ["PopupActivity"])
        log = self.registro.read_text()
        self.assertIn("leitor tecla 4", log)
        self.assertIn("leitor toquesv 50 2 2 3 3", log)  # e seguiu com os toques que faltavam

    def test_coordenada_so_vale_na_tela_em_que_foi_lida(self):
        self._leitor_falso()
        self.m.ver(imagem=False)  # o Claude olhou: a referência é a janela de agora
        (self.tmp / "janela.txt").write_text("com.android.settings|com.android.settings.Aviso|Sair?")
        r = self.m.agir({"acao": "sequencia", "passos": [{"tocar": [[1, 1], [2, 2]]}]})
        self.assertIn("a tela mudou", r["interrompido"])  # surgiu outra janela desde a olhada: não toca às cegas
        self.assertFalse(self.registro.exists() and " 1 1" in self.registro.read_text())
        # a resposta interrompida já mostrou a tela nova: agora ela é a referência. Se mudar de novo, não toca
        (self.tmp / "janela.txt").write_text("com.android.settings|com.android.settings.Outra|")
        r = self.m.agir({"acao": "tocar", "x": 5, "y": 5})  # ação única: mesma regra
        self.assertIn("interrompido", r)
        self.assertNotIn("tocar 5 5", self.registro.read_text() if self.registro.exists() else "")
        r = self.m.agir({"acao": "sequencia", "ver_depois": "nada",
                         "passos": [{"tocar": "bluetooth"}, {"tocar": [[1, 1], [2, 2]]}]})
        self.assertNotIn("interrompido", r)  # tocou por texto (leu a tela): reancorou e as coordenadas valem
        r = self.m.agir({"acao": "sequencia", "ver_depois": "nada", "passos": [
            {"deslizar": [1, 900, 1, 300]}, {"deslizar": [1, 900, 1, 300]}, {"tocar": [7, 7]}]})
        self.assertIn("rolou", r["interrompido"])  # rolar de novo pode; tocar onde estava antes, não
        r = self.m.agir({"acao": "sequencia", "ver_depois": "nada",
                         "passos": [{"deslizar": [1, 900, 1, 300]}, {"tocar": [7, 7], "confiar": True}]})
        self.assertNotIn("interrompido", r)

    def test_imagem_so_da_area_visual(self):
        xml = ('<?xml version="1.0"?><hierarchy><node bounds="[0,0][1000,2000]" text="" content-desc="">'
               '<node bounds="[0,200][1000,1200]" text="" content-desc="" class="BoardView"/>'
               '<node bounds="[0,1300][500,1400]" text="Desfazer" content-desc=""/></node></hierarchy>')
        self.assertEqual(self.m.regioes_visuais(xml), [[0, 200, 1000, 1000]])
        self.assertEqual(self.m.regioes_visuais(TestTela.XML), [])  # tela só de texto: nada de imagem
        self.assertTrue(self.m.dentro([500, 700], [0, 200, 1000, 1000]))
        self._leitor_falso()
        self.m.ver(imagem=False)
        self.m._ULTIMA["regioes"] = [[0, 200, 1000, 1000]]
        self.m.dump_ui = lambda: xml
        self.m.agir({"acao": "sequencia", "passos": [{"tocar": [500, 700]}]})
        self.assertIn("leitor foto 480 110000", self.registro.read_text())  # pediu o recorte do tabuleiro
        self.assertIn(" 0 200 1000 1000", self.registro.read_text())

    def test_botao_de_fechar_anuncio(self):
        els = [{"texto": "", "desc": "Peça agora", "x": 640, "y": 1973, "l": 900, "a": 150, "clicavel": True},
               {"texto": "5s", "desc": "", "x": 1165, "y": 275, "l": 90, "a": 90, "desativado": True},
               {"texto": "", "desc": "", "x": 640, "y": 1462, "l": 1280, "a": 2772, "clicavel": True}]
        self.assertIsNone(self.m.botao_fechar(els))  # contagem ainda correndo e o resto é o próprio anúncio
        els.append({"texto": "", "desc": "Anúncio fechado", "x": 1182, "y": 262, "l": 80, "a": 80, "clicavel": True})
        self.assertEqual(self.m.botao_fechar(els)["x"], 1182)
        self.assertEqual(self.m.botao_fechar([{"texto": "Instalar e fechar", "desc": "", "x": 1, "y": 1}]), None)
        self.assertTrue(self.m.ANUNCIO.search("com.applovin.adview.AppLovinFullscreenActivity"))
        self.assertTrue(self.m.ANUNCIO.search("com.bytedance.sdk.openadsdk.activity.TTFullScreenExpressVideoActivity"))
        self.assertFalse(self.m.ANUNCIO.search("easy.sudoku.MainActivity"))

    def test_anuncio_e_fechado_no_celular(self):
        self._leitor_falso()
        jan = self.tmp / "janela.txt"
        jan.write_text("app|com.applovin.adview.AppLovinFullscreenActivity|")
        xml = ('<?xml version="1.0"?><hierarchy><node bounds="[0,0][1280,2772]" text="" content-desc="" '
               'clickable="true"><node bounds="[1140,220][1220,300]" text="" content-desc="Fechar" clickable="true"/>'
               '</node></hierarchy>')
        orig = self.m.dump_ui
        self.m.dump_ui = lambda: xml
        self.m._injetar = lambda c: (jan.write_text("com.android.settings|com.android.settings.Principal|"),
                                     open(self.registro, "a").write("leitor " + c + "\n"))[0] is None
        r = self.m.fechar_anuncio("com.android.settings", limite=3)
        self.assertEqual(r["anuncio"], "fechado")
        self.assertIn("leitor tocar 1180 260", self.registro.read_text())  # tocou o fechar, não o anúncio
        self.m.dump_ui = orig

    def test_grade_teclado_e_sudoku(self):
        reg = [14, 617, 1252, 1252]
        els = [{"clicavel": True, "x": 90 + 137 * k, "y": 2362, "l": 128, "a": 190} for k in range(9)]
        els += [{"clicavel": True, "x": 198 + 300 * k, "y": 2115, "l": 200, "a": 150} for k in range(4)]
        tec = self.m.teclado_da_grade(els, reg, 9)
        self.assertEqual([t[0] for t in tec], [90 + 137 * k for k in range(9)])
        g = ["850700206", "201090080", "769000150", "670059800", "000000000",
             "005360072", "027000948", "080040605", "406002017"]
        sol = self.m.resolver_sudoku([[int(c) for c in ln] for ln in g])
        self.assertEqual("".join(map(str, sol[0])), "854713296")
        self.assertIsNone(self.m.resolver_sudoku([[5, 5] + [0] * 7] + [[0] * 9] * 8))  # leitura com repetido

    def test_grade_resolve_preenche_e_confere(self):
        self._leitor_falso()
        sol = ["854713296", "231695784", "769824153", "672459831", "348271569",
               "915368472", "527136948", "183947625", "496582317"]
        quase = [ln for ln in sol]
        quase[0] = "054713296"  # uma casa vazia
        (self.tmp / "grade1.txt").write_text("\n".join(quase))
        (self.tmp / "grade2.txt").write_text("\n".join(sol))
        tec = [[90 + 137 * k, 2362, 128, 190] for k in range(9)]
        r = self.m.grade({"resolver": True, "recorte": [14, 617, 1252, 1252], "teclado": tec,
                          "antes": [{"esperar": 0.01}]})
        self.assertEqual(r["vazias"], 1, r)
        self.assertTrue(r["conferido"], r)
        log = self.registro.read_text()
        self.assertIn("leitor toquesv 8:12 83 686 1049 2362", log)  # casa (0,0) e o botão 8, leva rápida e vigiada
        self.assertNotIn("refeitos", r)

    def test_grade_16x16_blocos_e_correcao_de_duvida(self):
        rows = ["D.7.....69.4C..5", "1G.E.D248.5.A96.", ".4...7A9B....21E", "3.9F58...1EG4...",
                ".2D.F.G.7.4...86", "97..E2CB3F6.1.A.", ".1A864.3..BD..F.", ".6....8..5...C.9",
                "..6.AF.5CG.E2.D.", "A54.1.D...2B6.C7", "2..C9...4.3...5A", "BE...C.8.A1.3.94",
                "8..4.B.EA.....G.", "5...8G.7D..29.E.", "FD164.9...C..8..", "G.....F21.....43"]
        S = self.m.SIMBOLOS
        g = [[0 if ch == "." else S.index(ch) + 1 for ch in r] for r in rows]
        sol = self.m.resolver_grade(g)
        self.assertIsNotNone(sol)
        for r in range(16):  # linhas, colunas e blocos 4x4 completos
            self.assertEqual(sorted(sol[r]), list(range(1, 17)))
            self.assertEqual(sorted(sol[i][r] for i in range(16)), list(range(1, 17)))
        self.assertEqual(sorted(sol[i][j] for i in range(4) for j in range(4)), list(range(1, 17)))
        self.assertEqual(self.m._caixa(6), (2, 3))
        g[0][1] = g[0][0]  # leitura errada vira repetição: aponta as duas casas
        self.assertTrue({(0, 0), (0, 1)} <= self.m._conflitos(g))  # (e o outro D da coluna)
        self.assertIsNone(self.m.resolver_grade(g))

    def test_app_de_banco_nunca_e_lido(self):
        xml = ('<?xml version="1.0"?><hierarchy>'
               '<node text="Saldo R$ 1.234" package="com.c6bank.app.yellow" bounds="[0,0][100,100]" clickable="true"/>'
               '<node text="Pergunta 1" package="com.android.chrome" bounds="[0,200][100,300]"/>'
               '</hierarchy>')
        textos = [e["texto"] for e in self.m.elementos(xml)]
        self.assertEqual(textos, ["Pergunta 1"])  # o nó do banco some antes de qualquer coisa
        self.assertTrue(self.m._privado("com.nu.production"))
        self.assertFalse(self.m._privado("com.android.chrome"))
        self.assertIn("app privado", self.m._janela_curta("com.c6bank.app.yellow|MainActivity|Saldo R$ 10"))
        self.assertNotIn("Saldo", self.m._janela_curta("com.c6bank.app.yellow|MainActivity|Saldo R$ 10"))

    def test_tabuleiro_de_xadrez_compacto(self):
        ini = {"a1": "Brancas Torre", "e1": "Brancas Rei", "e4": "Brancas Peão", "e8": "Pretas Rei", "f6": "Pretas Cavalo"}
        els = []
        for r in range(1, 9):
            for f in "abcdefgh":
                sq = f + str(r)
                els.append({"desc": f"{ini[sq]} em {sq}" if sq in ini else f"{sq}, vazio",
                            "x": 80 + 160 * "abcdefgh".index(f), "y": 967 + 160 * (8 - r)})
        els += [{"texto": "0:58", "x": 205, "y": 2245}, {"texto": "0:41.2", "x": 1153, "y": 2245},
                {"texto": "e4", "x": 100, "y": 2434}, {"texto": "Nf6", "x": 200, "y": 2434}]
        t = self.m.tabuleiro_curto(els)
        self.assertEqual(t["tabuleiro"][0], "....k... 8")
        self.assertEqual(t["tabuleiro"][2], ".....n.. 6")
        self.assertEqual(t["tabuleiro"][7], "R...K... 1")
        self.assertEqual(t["relogios"], ["0:58", "0:41.2"])
        self.assertEqual(t["ultimos"], ["e4", "Nf6"])
        self.assertEqual(self.m.casas_xadrez(els)["e4"], (720, 1607, "P"))
        self.assertIsNone(self.m.casas_xadrez(els[:10]))

    def test_teclado_em_paginas_e_regra_de_texto_curto(self):
        reg = [17, 617, 1244, 1243]
        pag2 = [{"clicavel": True, "x": x, "y": 2362, "l": 150, "a": 190} for x in (107, 285, 462, 640, 818, 996, 1173)]
        ferramentas = [{"clicavel": True, "x": 168 + 240 * k, "y": 2115, "l": 200, "a": 150} for k in range(5)]
        self.assertEqual(len(self.m.teclado_da_grade(pag2 + ferramentas, reg)), 7)  # a fileira maior é o teclado
        els = [{"texto": "Facebook", "desc": "", "x": 1, "y": 1, "clicavel": True},
               {"texto": "OK", "desc": "", "x": 9, "y": 9, "clicavel": True}]
        self.assertEqual(self.m.achar_regra(els, "ok")["x"], 9)  # "ok" não casa com "Facebook"
        self.assertIsNone(self.m.achar_regra(els[:1], "ok"))
        r = {"app": "app.jogo", "se": "OK", "tocar": "OK"}
        self.assertEqual(self.m.regra_vale(r, "app.jogo", lambda: els), (9, 9))
        self.assertIsNone(self.m.regra_vale(r, "com.whatsapp", lambda: els))  # regra de um app não vale em outro
        self.assertIn("erro", self.m.reflexos([{"se": "x", "tocar": "x", "app": "não é pacote!"}]))

    def test_rotinas_guardadas_e_repetidas(self):
        self._leitor_falso()
        self.m.ROTINAS_ARQ = str(self.tmp / "rotinas.json")
        self.assertIn("erro", self.m.rotina({"salvar": {"nome": "x y", "args": {"acao": "ver"}}}))
        self.assertIn("erro", self.m.rotina({"salvar": {"nome": "laco", "args": {"acao": "rotina"}}}))  # sem recursão
        r = self.m.rotina({"salvar": {"nome": "toque", "args": {"acao": "sequencia", "ver_depois": "nada",
                                                               "passos": [{"tocar": [3, 4], "confiar": True}]}}})
        self.assertEqual(r["rotinas"], ["toque"])
        self.assertEqual(self.m.executar({"acao": "rotina"})["rotinas"], {"toque": "sequencia"})
        r = self.m.executar({"acao": "rotina", "nome": "toque", "vezes": 3})
        self.assertEqual((r["feitas"], r["pedidas"]), (3, 3))
        self.assertTrue(all(v["ok"] for v in r["voltas"]))
        self.assertEqual(self.registro.read_text().count(" 3 4\n"), 3)  # um toque por volta
        self.assertIn("erro", self.m.rotina({"nome": "nenhuma"}))
        self.m.rotina({"apagar": "toque"})
        self.assertEqual(self.m.rotina({})["rotinas"], {})

    def test_anuncio_por_baixo_da_barra_do_sistema(self):
        self._leitor_falso()
        (self.tmp / "janela.txt").write_text("com.android.systemui|android.widget.FrameLayout|Gravador de Tela")
        d = self.tmp / "bin" / "dumpsys"
        d.write_text('echo "    topResumedActivity=ActivityRecord{1 u0 app.x/com.applovin.adview.AppLovinFullscreenActivity t8}"\n')
        d.chmod(0o755)
        self.assertTrue(self.m.em_anuncio())  # o último evento é do sistema: confere a atividade no topo
        (self.tmp / "janela.txt").write_text("app.x|app.x.MainActivity|")
        self.assertFalse(self.m.em_anuncio())  # evento do próprio app e não é anúncio: nem precisa do dumpsys

    def test_leitor_recusa_app_bloqueado(self):
        foco = self.tmp / "foco.txt"
        foco.write_text("com.nu.production")
        with mock.patch.dict(os.environ, {"FOCO_ARQ": str(foco)}):
            self._leitor_falso()
            r = self.m.agir({"acao": "sequencia", "passos": [{"tocar": [10, 20]}]})
        self.assertIn("bloqueados", r["erro"])
        self.assertNotIn("toque", self.registro.read_text() if self.registro.exists() else "")  # nenhum toque saiu

    def test_leitor_que_nao_sobe_cai_no_caminho_antigo(self):
        self._leitor_falso(quebrado=True)
        self.assertTrue(self.m.dump_ui().startswith("<?xml"))  # uiautomator falso do caminho antigo
        r = self.m.agir({"acao": "tocar", "texto": "bluetooth"})
        self.assertEqual(r["feito"], "toque em 220,450")
        self.assertIn("input tap 220 450", self.registro.read_text())
        self.assertGreater(self.m.AJUDANTE.falhou_em, 0)  # não tenta de novo a toda hora

    def test_captura_por_arquivo(self):
        if not shutil.which("ffmpeg"):
            self.skipTest("ffmpeg ausente")
        png = self.tmp / "origem.png"
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=c=red:s=640x360", "-frames:v", "1",
                        str(png)], check=True, capture_output=True)
        screencap = self.tmp / "bin" / "screencap"
        screencap.write_text(f'cp "{png}" "$2"\n')
        screencap.chmod(0o755)
        b64, largura = self.m.captura(320)
        self.assertTrue(base64.b64decode(b64).startswith(b"\xff\xd8"))  # JPEG
        self.assertEqual(largura, 320)
        self.assertEqual(self._sobras(), [])
        screencap.write_text("exit 0\n")  # sem imagem (ex.: app protegido): não quebra
        self.assertEqual(self.m.captura(320), (None, None))

    def test_shizuku_parado(self):
        Path(self.m.RISH).write_text("echo 'Shizuku is not running' >&2; exit 1\n")
        with self.assertRaises(self.m.SemShizuku):
            self.m.rish("id")


class TestTermometro(unittest.TestCase):
    """Temperatura do ar pela bateria: confiança conforme carga/consumo/variação, e tendência."""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        caminho = Path(__file__).resolve().parent.parent / "controle-ir" / "capacidades" / "termometro" / "principal.py"
        spec = importlib.util.spec_from_file_location("termometro_principal", caminho)
        cls.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.m)

    def test_parado_da_confianca_alta(self):
        a = [{"temperature": 27.0, "plugged": "UNPLUGGED", "current": -60000},
             {"temperature": 27.2, "plugged": "UNPLUGGED", "current": -55000}]
        r = self.m.avaliar(a, 2.0)
        self.assertEqual((r["ar_estimado_c"], r["confianca"], r["motivos"]), (25.1, "alta", []))

    def test_em_uso_ou_na_tomada_baixa_confianca(self):
        uso = [{"temperature": 33.0, "plugged": "UNPLUGGED", "current": 357000}] * 2
        self.assertEqual(self.m.avaliar(uso, 2.0)["confianca"], "media")
        tomada = [{"temperature": 35.0, "plugged": "PLUGGED_AC", "current": 900000},
                  {"temperature": 36.0, "plugged": "PLUGGED_AC", "current": 900000}]
        r = self.m.avaliar(tomada, 2.0)
        self.assertEqual(r["confianca"], "baixa")
        self.assertEqual(len(r["motivos"]), 3)
        self.assertIn("erro", self.m.avaliar([{}], 2.0))

    def test_tendencia(self):
        agora = time.time()
        h = [{"t": agora - 1800 + i * 600, "ar_estimado_c": 26.0 - i * 0.5, "confianca": "alta"} for i in range(4)]
        self.assertAlmostEqual(self.m.tendencia(h), -3.0, places=1)  # caindo 0,5 °C a cada 10 min
        self.assertIsNone(self.m.tendencia(h[:2]))

    def test_termometro_embutido_e_ativo(self):
        s, _ = novo_servico(com_base=False)
        self.assertEqual({c["nome"]: c["estado"] for c in s.capacidades()["capacidades"]}.get("termometro"), "ativa")


def _carregar_cap(nome):
    import importlib.util
    caminho = Path(__file__).resolve().parent.parent / "controle-ir" / "capacidades" / nome / "principal.py"
    spec = importlib.util.spec_from_file_location(f"{nome}_principal", caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestSono(unittest.TestCase):
    """Laboratório do sono: roncos no ritmo da respiração, sem confundir fala, batida e silêncio."""

    @classmethod
    def setUpClass(cls):
        try:
            import numpy  # noqa: F401
        except ImportError:
            raise unittest.SkipTest("numpy ausente")
        cls.m = _carregar_cap("sono")

    def _base(self, seg=60, a=0.003):
        import numpy as np
        return np.random.default_rng(2).normal(0, a, 16000 * seg).astype(np.float32)

    def test_ronco_ritmado(self):
        import numpy as np
        x = self._base()
        t = np.arange(16000) / 16000
        som = sum(np.sin(2 * np.pi * 110 * k * t) / k for k in range(1, 6)) * np.sin(np.pi * t) ** 2 * 0.08
        for i in range(10):
            j = int((2 + 4 * i) * 16000)
            x[j:j + t.size] += som
        r = self.m.analisar_trecho(x)
        self.assertEqual((r["roncos"], r["ritmo_s"]), (10, 4.0))

    def test_fala_batida_silencio(self):
        import numpy as np
        y = self._base()
        t = np.arange(int(1.2 * 16000)) / 16000
        for c in (5, 13, 30, 41):  # voz aguda, sem ritmo de respiração
            j = c * 16000
            y[j:j + t.size] += 0.05 * sum(np.sin(2 * np.pi * 230 * k * t) for k in range(3, 12)) * np.sin(np.pi * t / 1.2) ** 2
        self.assertEqual(self.m.analisar_trecho(y)["roncos"], 0)
        z = self._base()
        z[320000:320300] += 0.8
        r = self.m.analisar_trecho(z)
        self.assertEqual((r["roncos"], r["barulhos"]), (0, 1))
        self.assertEqual(self.m.analisar_trecho(self._base())["roncos"], 0)

    def test_resumo_por_hora(self):
        t0 = time.mktime((2026, 11, 19, 1, 0, 0, 0, 0, -1))
        linhas = [{"t": t0 + i * 600, "duracao_s": 60, "roncos": 5 if i < 3 else 0, "ronco_s": 4.0 if i < 3 else 0,
                   "barulhos": 1, "nivel_db": -45.0, "ar_estimado_c": 24.0 - i * 0.2} for i in range(9)]
        r = self.m.resumir(linhas)
        self.assertEqual((r["trechos"], r["roncos"], r["barulhos"]), (9, 15, 9))
        self.assertEqual(r["hora_com_mais_ronco"], "01:00")
        self.assertEqual([h["hora"] for h in r["por_hora"]], ["01:00", "02:00"])
        self.assertIn("erro", self.m.resumir([]))


class TestSonar(unittest.TestCase):
    """Sonar: detecta o tom (suporte) e o desvio Doppler de quem se mexe."""

    @classmethod
    def setUpClass(cls):
        try:
            import numpy  # noqa: F401
        except ImportError:
            raise unittest.SkipTest("numpy ausente")
        cls.m = _carregar_cap("sonar")

    def test_movimento_na_segunda_metade(self):
        import numpy as np
        T, f = 48000, 19000
        t = np.arange(T * 10) / T
        rng = np.random.default_rng(4)
        x = 0.2 * np.sin(2 * np.pi * f * t) + rng.normal(0, 0.002, t.size)
        fase = 2 * np.pi * np.cumsum(f + 60 * np.sin(2 * np.pi * 0.8 * t)) / T
        x = x + np.where(t >= 5, 0.02 * np.sin(fase), 0)
        r = self.m.analisar_sonar(x.astype(np.float32), f)
        self.assertTrue(r["suporte"])
        linha = r["linha_do_tempo_meio_s"]
        self.assertEqual(sum(linha[:8]), 0)  # parado na 1ª metade
        self.assertGreaterEqual(sum(linha[10:]), 8)  # mexendo na 2ª
        self.assertFalse(self.m.analisar_sonar(rng.normal(0, 0.002, t.size).astype(np.float32), f)["suporte"])

    def test_tom_sem_estalo(self):
        tom = self.m.gerar_tom(19000, 2.0)
        self.assertEqual(tom.dtype.name, "int16")
        self.assertLess(abs(int(tom[0])), 50)
        self.assertLess(abs(int(tom[-1])), 50)

    def test_novas_capacidades_ativas(self):
        s, _ = novo_servico(com_base=False)
        nomes = {c["nome"]: c["estado"] for c in s.capacidades()["capacidades"]}
        self.assertEqual((nomes.get("sono"), nomes.get("sonar")), ("ativa", "ativa"))



class TestRepositorio(unittest.TestCase):
    """De onde o celular baixa as atualizações (para continuar o projeto em outro repositório)."""

    def test_padrao_arquivo_ambiente_e_invalido(self):
        from controle_ir import cli
        pasta = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, pasta, True)
        antes = cli.PASTA
        cli.PASTA = pasta
        self.addCleanup(setattr, cli, "PASTA", antes)
        os.environ.pop("CONTROLE_IR_REPO", None)
        self.assertEqual(cli.repositorio(), cli.REPO_PADRAO)
        (pasta / "repositorio").write_text("https://github.com/outro-dev/novo-repo/\n")
        self.assertEqual(cli.repositorio(), "https://github.com/outro-dev/novo-repo")
        (pasta / "repositorio").write_text("https://exemplo.com/malicioso; rm -rf ~")
        self.assertEqual(cli.repositorio(), cli.REPO_PADRAO)  # só aceita uma URL do GitHub limpa
        os.environ["CONTROLE_IR_REPO"] = "https://github.com/a/b"
        self.addCleanup(os.environ.pop, "CONTROLE_IR_REPO", None)
        self.assertEqual(cli.repositorio(), "https://github.com/a/b")

class TestPiloto(unittest.TestCase):
    """Piloto: o laço rápido no celular (percepção do quiz, memória, corrida de cérebros com streaming)."""

    def setUp(self):
        import importlib.util
        caminho = Path(__file__).resolve().parent.parent / "controle-ir" / "capacidades" / "tela" / "piloto.py"
        spec = importlib.util.spec_from_file_location("piloto_teste", caminho)
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.m.PASTA = str(self.tmp)
        self.m.MEMORIA_ARQ = str(self.tmp / "memoria.json")
        self.m.GRAVADOR_ARQ = str(self.tmp / "rodadas.jsonl")

    @staticmethod
    def tela(pergunta="Qual é a capital da Austrália?", ops=("Sydney", "Canberra", "Melbourne", "Perth")):
        els = [{"texto": "Pergunta 3 de 15", "x": 640, "y": 300, "l": 400, "a": 60},
               {"texto": pergunta, "x": 640, "y": 700, "l": 1100, "a": 200},
               {"texto": "Pular", "x": 640, "y": 2500, "l": 300, "a": 120, "clicavel": True}]
        for i, o in enumerate(ops):  # botão clicável sem texto + o texto por dentro (como nos apps de verdade)
            y = 1200 + 220 * i
            els.append({"x": 640, "y": y, "l": 1100, "a": 180, "clicavel": True})
            els.append({"texto": o, "x": 600, "y": y, "l": 500, "a": 80})
        return els

    def test_le_pergunta_e_opcoes(self):
        perg, ops = self.m.quiz_da_tela(self.tela())
        self.assertEqual(perg, "Qual é a capital da Austrália?")
        self.assertEqual([o["texto"] for o in ops], ["Sydney", "Canberra", "Melbourne", "Perth"])
        self.assertEqual((ops[1]["x"], ops[1]["y"]), (640, 1420))  # toca no botão, não no texto
        self.assertIsNone(self.m.quiz_da_tela(self.tela()[:3]))  # sem opções não é quiz

    def _servidor_sse(self, texto, atraso=0.0):
        class H(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *a):
                pass

            def do_POST(self):
                self.rfile.read(int(self.headers["Content-Length"]))
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Transfer-Encoding", "chunked")
                self.end_headers()

                def pedaco(b):
                    self.wfile.write(f"{len(b):x}\r\n".encode() + b + b"\r\n")
                    self.wfile.flush()
                time.sleep(atraso)
                for t in texto:
                    ev = {"choices": [{"delta": {"content": t}}]}
                    pedaco(f"data: {json.dumps(ev)}\n\n".encode())
                pedaco(b"data: [DONE]\n\n")
                self.wfile.write(b"0\r\n\r\n")

        srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.shutdown)
        return f"http://127.0.0.1:{srv.server_address[1]}"

    def test_corrida_streaming_memoria_e_prazo(self):
        url = self._servidor_sse(["Resposta", ": 2"])
        c = self.m.Cerebros({"cerebros": ["local"], "local_url": url})
        ops = [{"texto": t} for t in ("Sydney", "Canberra", "Melbourne")]
        idx, fonte, seg, erros = c.decidir("Capital da Austrália?", ops, 3)
        self.assertEqual((idx, fonte), (1, "local"), erros)
        idx, *_ = c.decidir("Capital da Austrália?", ops, 3)  # conexão persistente reaproveitada
        self.assertEqual(idx, 1)
        c.memoria[self.m.norm("Qual a cor do céu?")] = "Azul"  # memória responde sem rede
        idx, fonte, seg, _ = c.decidir("Qual a cor do céu?", [{"texto": "Verde"}, {"texto": "Azul"}], 3)
        self.assertEqual((idx, fonte), (1, "memoria"))
        self.assertLess(seg, 0.05)
        lento = self.m.Cerebros({"cerebros": ["local"], "local_url": self._servidor_sse(["1"], atraso=1.5)})
        idx, fonte, seg, _ = lento.decidir("x?", ops, 0.4)  # prazo estoura: ninguém respondeu
        self.assertIsNone(idx)
        self.assertLess(seg, 1.0)

    def _servidor_eventos(self, eventos, atraso=0.0):
        """SSE com eventos JSON prontos (formato da Anthropic ou do llama-server)."""
        class H(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *a):
                pass

            def do_POST(self):
                self.rfile.read(int(self.headers["Content-Length"]))
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Transfer-Encoding", "chunked")
                self.end_headers()
                time.sleep(atraso)
                for ev in eventos:
                    b = f"data: {json.dumps(ev)}\n\n".encode()
                    self.wfile.write(f"{len(b):x}\r\n".encode() + b + b"\r\n")
                    self.wfile.flush()
                self.wfile.write(b"0\r\n\r\n")

        srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.shutdown)
        return f"http://127.0.0.1:{srv.server_address[1]}"

    def test_escada_de_inteligencia(self):
        import math

        def local(digito, prob):
            return self._servidor_eventos([{"choices": [{"delta": {"content": digito}, "logprobs": {"content": [
                {"token": digito, "logprob": math.log(prob)}]}}]}])
        api = self._servidor_eventos([{"type": "content_block_delta", "delta": {"type": "text_delta", "text": "3"}}],
                                     atraso=0.3)
        ops = [{"texto": t} for t in ("a", "b", "c")]
        self.m.ler_chave = lambda: "chave-falsa"
        base = {"cerebros": ["local", "api"], "api_base": api, "modelos": ["forte"]}
        # local com certeza alta: vai na hora, sem esperar a API
        c = self.m.Cerebros(dict(base, local_url=local("1", 0.99)))
        idx, fonte, seg, _ = c.decidir("p?", ops, 3)
        self.assertEqual((idx, fonte), (0, "local 99%"))
        self.assertLess(seg, 0.25)
        # local em dúvida: espera o forte, que discorda — vale o forte
        c = self.m.Cerebros(dict(base, local_url=local("1", 0.40)))
        idx, fonte, seg, _ = c.decidir("p?", ops, 3)
        self.assertEqual((idx, fonte), (2, "forte"))
        # prazo curto: o forte não chega a tempo — vale a melhor que chegou (o local em dúvida)
        c = self.m.Cerebros(dict(base, local_url=local("2", 0.40)))
        idx, fonte, seg, _ = c.decidir("p?", ops, 0.15)
        self.assertEqual((idx, fonte), (1, "local 40%"))
        # aprende durante a partida: o local tocou sozinho (99%), o forte discorda depois → a precisão medida cai,
        # o local deixa de agir sozinho e a memória corrige
        c = self.m.Cerebros(dict(base, local_url=local("1", 0.99)))
        idx, fonte, *_ = c.decidir("Moeda do Japão?", ops, 3)
        self.assertEqual(idx, 0)
        fim = time.time() + 3
        while not c.correcoes and time.time() < fim:
            time.sleep(0.02)
        ap = c.aprendizado()
        self.assertEqual(ap["discordancias"], 1)
        self.assertFalse(ap["local_sozinho"])
        self.assertEqual(c.memoria[self.m.chave_quiz("Moeda do Japão?", ops)], "c")
        idx, fonte, *_ = c.decidir("Moeda do Japão?", ops, 3)
        self.assertEqual((idx, fonte), (2, "memoria"))  # na próxima vez: certo e instantâneo
        idx, fonte, *_ = c.decidir("Outra?", ops, 3)
        self.assertEqual(fonte, "forte")  # sem confiança, espera o forte
        # o forte passa a CONFIRMAR o local (mesmo dígito): a precisão medida volta e o local é liberado de novo
        c.local = self.m.Cerebros(dict(base, local_url=local("3", 0.99))).local
        for k in range(18):  # 2 discordâncias: (18+9)/(18+2+10) = 0,90
            c.decidir(f"Pergunta {k}?", ops, 3)
        fim = time.time() + 3
        while not c.aprendizado()["local_sozinho"] and time.time() < fim:
            time.sleep(0.02)
        self.assertTrue(c.aprendizado()["local_sozinho"], c.aprendizado())
        idx, fonte, seg, _ = c.decidir("Mais uma?", ops, 3)
        self.assertEqual(fonte, "local 99%")
        self.assertLess(seg, 0.25)
        self.assertEqual(self.m.corpo_api("claude-haiku-5-5", "s", "u")["thinking"], {"type": "disabled"})
        self.assertEqual(self.m.corpo_api("claude-sonnet-5-5", "s", "u")["thinking"], {"type": "between_tools"})
        self.assertNotIn("thinking", self.m.corpo_api("claude-opus-5-5", "s", "u"))

    def test_laco_toca_no_alvo_semantico_e_grava(self):
        url = self._servidor_sse(["2"])
        telas = [self.tela(), self.tela()]
        # entre a leitura e o toque as opções trocam de lugar: o toque segue o TEXTO escolhido
        trocada = self.tela(ops=("Canberra", "Sydney", "Melbourne", "Perth"))
        sequencia = [telas[0], trocada] + [trocada] * 50
        tocados = []

        def elementos():
            return sequencia.pop(0) if len(sequencia) > 1 else sequencia[0]
        f = {"aguardar": lambda c, ms: (time.sleep(0.01), c + 1)[1], "elementos": elementos,
             "tocar": lambda x, y: tocados.append((x, y)), "bloqueado": lambda app: False}
        p = self.m.Piloto(f)
        p.iniciar({"cerebros": ["local"], "local_url": url, "duracao": 10})
        fim = time.time() + 3
        while not tocados and time.time() < fim:
            time.sleep(0.02)
        p.encerrar()
        self.assertEqual(tocados[0], (640, 1200))  # "Canberra" estava agora na 1ª posição
        e = p.estado()
        self.assertEqual(e["ultimas"][0]["escolha"], "Canberra")
        self.assertEqual(e["ultimas"][0]["fonte"], "local")
        self.assertEqual(len(tocados), 1)  # mesma pergunta não é respondida duas vezes
        self.assertTrue((self.tmp / "rodadas.jsonl").exists())

    def test_xadrez_joga_na_vez_certa(self):
        m = self.m
        self.assertEqual(m.fen(m.INICIAL, "w"), "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        estado = {"tab": list(m.INICIAL)}
        idx = {f"{c}{r}": (8 - r) * 8 + "abcdefgh".index(c) for r in range(1, 9) for c in "abcdefgh"}

        def casas():
            return {sq: (80 + 160 * "abcdefgh".index(sq[0]), 967 + 160 * (8 - int(sq[1])),
                         "" if estado["tab"][i] == "." else estado["tab"][i]) for sq, i in idx.items()}
        pos = {(v[0], v[1]): k for k, v in casas().items()}

        def mover(a, b):
            t = estado["tab"]
            t[idx[b]], t[idx[a]] = t[idx[a]], "."

        respostas = iter([("e7", "e5"), ("b8", "c6")])
        toques = []

        def tocar(x, y):
            toques.append(pos[(x, y)])
            if len(toques) % 2 == 0:
                mover(toques[-2], toques[-1])  # o app aplica o meu lance…

                def robo():  # …e o robô responde um pouco depois
                    time.sleep(0.15)
                    a, b = next(respostas, (None, None))
                    if a:
                        mover(a, b)
                threading.Thread(target=robo, daemon=True).start()

        class MotorFalso:
            lances = iter(["e2e4", "g1f3", "f1c4"])

            def __init__(self, *a, **k):
                pass

            def lance(self, fen_, ms):
                return next(self.lances)

            def fechar(self):
                pass
        m.Motor = MotorFalso
        f = {"aguardar": lambda c, ms: (time.sleep(0.02), c + 1)[1], "casas": casas, "tocar": tocar,
             "contra_robo": lambda: True, "bloqueado": lambda app: False}
        p = m.Piloto(f)
        p.iniciar({"modo": "xadrez", "duracao": 10})
        fim = time.time() + 4
        while len(toques) < 6 and time.time() < fim:
            time.sleep(0.02)
        time.sleep(0.3)
        p.encerrar()
        self.assertEqual(toques, ["e2", "e4", "g1", "f3", "f1", "c4"])  # 3 lances, cada um na sua vez
        self.assertTrue(all(r["ok"] for r in p.rodadas))
        # contra pessoas (não é partida contra robô): o piloto não joga
        p2 = m.Piloto(dict(f, contra_robo=lambda: False))
        p2.iniciar({"modo": "xadrez", "duracao": 10})
        time.sleep(0.2)
        self.assertIn("não é partida contra robô", p2.estado()["estado"])
        p2.encerrar()

    def test_sobreposicao_do_sistema_nao_trava_o_piloto(self):
        url = self._servidor_sse(["2"])
        barra = [{"texto": "12:00", "pacote": "com.android.systemui", "x": 50, "y": 20, "l": 80, "a": 40}]
        tela = barra + [dict(e, pacote="com.android.chrome") for e in self.tela()]
        tocados = []
        f = {"aguardar": lambda c, ms: (time.sleep(0.01), c + 1)[1], "elementos": lambda: tela,
             "tocar": lambda x, y: tocados.append((x, y)), "bloqueado": lambda app: app.startswith("com.c6bank")}
        p = self.m.Piloto(f)
        p.iniciar({"cerebros": ["local"], "local_url": url, "duracao": 10, "app": "com.android.chrome"})
        fim = time.time() + 3
        while not tocados and time.time() < fim:
            time.sleep(0.02)
        p.encerrar()
        self.assertEqual(tocados[:1], [(640, 1420)])  # a barra do sistema na frente não impede de jogar
        banco = [{"texto": "Saldo", "pacote": "com.c6bank.app", "x": 1, "y": 1, "l": 9, "a": 9}] + tela
        p = self.m.Piloto(dict(f, elementos=lambda: banco))
        p.iniciar({"cerebros": ["local"], "local_url": url, "duracao": 10, "app": "com.android.chrome"})
        time.sleep(0.3)
        self.assertIn("bloqueado", p.estado()["estado"])  # app de banco na tela: o piloto para
        p.encerrar()

    def test_leitura_rasgada_espera_as_opcoes_novas(self):
        url = self._servidor_sse(["2"])
        q1 = self.tela()
        rasgada = self.tela(pergunta="Quantos lados tem um hexágono?")  # pergunta nova, botões ainda da anterior
        q2 = self.tela(pergunta="Quantos lados tem um hexágono?", ops=("5", "6", "7", "8"))
        seq = [q1] * 3 + [rasgada] * 3 + [q2] * 80
        tocados, escolhas = [], []

        def elementos():
            return seq.pop(0) if len(seq) > 1 else seq[0]
        f = {"aguardar": lambda c, ms: (time.sleep(0.01), c + 1)[1], "elementos": elementos,
             "tocar": lambda x, y: tocados.append((x, y)), "bloqueado": lambda app: False}
        p = self.m.Piloto(f)
        p.iniciar({"cerebros": ["local"], "local_url": url, "duracao": 10, "conferir": False})
        fim = time.time() + 4
        while len(tocados) < 2 and time.time() < fim:
            time.sleep(0.02)
        p.encerrar()
        escolhas = [r["escolha"] for r in p.estado(20)["ultimas"] if r.get("total_ms") is not None]
        self.assertEqual(escolhas, ["Canberra", "6"])  # nada respondido com as opções velhas

if __name__ == "__main__":
    unittest.main()
