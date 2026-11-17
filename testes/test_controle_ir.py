"""Testes do controle-ir (rodar na raiz: python3 -m unittest discover -s testes -v)."""
from __future__ import annotations

import json
import random
import shutil
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


if __name__ == "__main__":
    unittest.main()
