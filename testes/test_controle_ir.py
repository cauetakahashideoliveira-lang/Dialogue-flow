"""Testes do controle-ir (rodar na raiz: python3 -m unittest discover -s testes -v)."""
from __future__ import annotations

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
        for proibido in ("liberar", "destravar", "aprovar", "classe"):  # só por autorizar(código) ou no celular
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

    def test_autorizar_de_outro_aparelho_e_travar(self):
        from controle_ir.execucao import totp
        seg = self.ex.autorizacao.configurar()
        cod = lambda: totp(seg, int(time.time() // 30))  # noqa: E731
        r = self.s.executar_comando("echo remoto", aguardar=0)
        self.assertEqual(r["status"], "aguardando_aprovacao")
        with self.assertRaises(Exception):
            self.s.autorizar("111111", tarefa=r["id"])
        out = self.s.autorizar(cod(), tarefa=r["id"])
        self.assertEqual(out["tarefa"]["status"], "executando")
        with self.assertRaises(Exception):  # código já usado
            self.s.autorizar(cod(), liberar_minutos=10)
        self.assertTrue(self.s.travar()["travado"])
        self.assertEqual(self.s.executar_comando("ls", aguardar=1)["status"], "negada")
        self.ex.autorizacao._gravar({**self.ex.autorizacao._ler(), "ultimo": 0})  # próximo passo de 30 s
        self.s.autorizar(cod(), destravar=True, liberar_minutos=5)
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
        self.assertIn("já estava desligado", self.cli("desligar")[1])
        p = subprocess.Popen([sys.executable, "-m", "controle_ir", "ligar"], env=self.env, stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        try:
            self.assertTrue(self.esperar(self.saude))
            self.assertIn("já está ligado", self.cli("ligar")[1])
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


if __name__ == "__main__":
    unittest.main()
