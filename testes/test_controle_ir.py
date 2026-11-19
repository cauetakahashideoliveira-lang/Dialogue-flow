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
    return Servico(pasta, emissor or EmissorSimulado()), pasta


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
        self.assertTrue(o.verificar("160.79.105.20, 10.0.0.1"))
        self.assertFalse(o.verificar("203.0.113.9"))
        self.assertTrue(o.verificar(None))  # chamada local, sem túnel


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
        self.assertEqual(self.s.atualizar_sistema("abc1234", "teste", aguardar=0)["status"], "aguardando_aprovacao")
        with self.assertRaises(Exception):
            self.s.atualizar_sistema("x; rm -rf ~")
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
        # cauteloso volta a pedir e não auto-ativa
        self.ex.politica.aplicar_perfil("cauteloso")
        self.assertEqual(self.s.executar_comando("ping -c1 1.1.1.1", aguardar=0)["status"], "aguardando_aprovacao")
        self.s.propor_capacidade("eco2", manifesto=eco["manifesto"], arquivos=eco["arquivos"])
        self.assertEqual(self.s.capacidades("listar")["capacidades"][0].get("estado") if False else
                         next(c["estado"] for c in self.s.capacidades("listar")["capacidades"] if c["nome"] == "eco2"),
                         "aguardando_aprovacao")
        aud = (Path(self.pasta) / "auditoria.jsonl").read_text()
        self.assertIn("capacidade_auto_aprovada", aud)

    def test_aprovar_pelo_chat_padrao_e_desligada(self):
        r = self.s.executar_comando("echo pelo chat", aguardar=0)
        self.assertEqual(r["status"], "aguardando_aprovacao")
        self.assertEqual(self.s.politica()["aprovacao_remota"], "chat")
        out = self.s.autorizar(tarefa=r["id"])  # sem código: basta o sim do usuário na conversa
        self.assertEqual(out["tarefa"]["status"], "executando")
        with self.assertRaises(Exception):
            self.s.autorizar()  # precisa dizer o que aprovar
        p = self.ex.politica.ler()
        p["aprovacao_remota"] = "desligada"
        self.ex.politica.gravar(p)
        with self.assertRaises(Exception):
            self.s.autorizar(liberar_minutos=10)
        self.assertIn('"modo": "chat"', (Path(self.pasta) / "auditoria.jsonl").read_text())

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
        for f in (ligar, desligar, tarefas, tarefas.parent):
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
        rish.write_text('[ "$1" = "-c" ] && shift && exec sh -c "$1"\n')  # imita o rish: roda como "shell"
        bin_ = self.tmp / "bin"
        bin_.mkdir()
        (bin_ / "uiautomator").write_text(f'cat > "$2" <<\'FIM\'\n{TestTela.XML}\nFIM\necho "UI hierchary dumped to: $2"\n')
        (bin_ / "input").write_text('if [ "$BLOQUEAR_INPUT" = 1 ]; then echo "java.lang.SecurityException: Injecting '
                                    'to another application requires INJECT_EVENTS permission" >&2; exit 1; fi\n'
                                    'if [ "$BLOQUEAR_INPUT" = 2 ]; then echo "cmd: Failure calling service input: '
                                    'Failed transaction (2147483646)"; exit 2; fi\n'
                                    'echo "input $*" >> "$REGISTRO_INPUT"\n')
        for f in bin_.iterdir():
            f.chmod(0o755)
        self.m.RISH = str(rish)
        self.m.COMPARTILHADA = str(self.tmp / "compartilhada")
        self.m.TMP = str(self.tmp / "tela")
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

if __name__ == "__main__":
    unittest.main()
