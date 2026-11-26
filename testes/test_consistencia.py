"""Consistência entre as partes que precisam concordar: celular × Central, missão × ferramentas, resumos.

Rodar na raiz: python3 -m unittest testes.test_consistencia
"""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "controle-ir"))

from controle_ir import aparelhos, mcp, seguranca  # noqa: E402

INDEX_JS = RAIZ / "painel" / "src" / "index.js"
CAPS = RAIZ / "controle-ir" / "capacidades"


def _conjunto_js(nome: str, fonte: str, conhecidos: dict[str, set[str]]) -> set[str]:
    """Lê `const NOME = new Set([...])` do Worker, resolvendo `...OUTRO` com os conjuntos já lidos."""
    m = re.search(rf"const {nome} = new Set\(\[(.*?)\]\);", fonte, re.S)
    if not m:
        raise AssertionError(f"{nome} não encontrado em painel/src/index.js")
    corpo = m.group(1)
    itens = set(re.findall(r"'([a-z_]+)'", corpo))
    for outro in re.findall(r"\.\.\.([A-Z_]+)", corpo):
        itens |= conhecidos[outro]
    return itens


class TestParidadeDoBloqueio(unittest.TestCase):
    """A Central bloqueia na borda com o mesmo critério do guardião do celular (seguranca.py). Se as listas
    divergirem, uma ferramenta passaria por um lado e seria barrada no outro."""

    @classmethod
    def setUpClass(cls):
        cls.fonte = INDEX_JS.read_text(encoding="utf-8")
        cls.sempre = _conjunto_js("SEMPRE", cls.fonte, {})
        cls.baixo = _conjunto_js("BAIXO_RISCO", cls.fonte, {"SEMPRE": cls.sempre})

    def test_listas_iguais_nos_dois_lados(self):
        self.assertEqual(self.sempre, set(seguranca.SEMPRE))
        self.assertEqual(self.baixo, set(seguranca.BAIXO_RISCO))

    def test_pc_mesmas_ferramentas_sempre_liberadas(self):
        """O PC (agente_pc) tem a lista própria; a Central barra na borda com a mesma."""
        sys.path.insert(0, str(RAIZ / "pc"))
        from agente_pc import ferramentas, servidor
        self.assertEqual(_conjunto_js("SEMPRE_PC", self.fonte, {}), servidor.SEMPRE)
        self.assertLessEqual(servidor.SEMPRE, ferramentas.NOMES)
        self.assertFalse(self.sempre & servidor.SEMPRE)

    def test_listas_so_tem_ferramentas_que_existem(self):
        fixas = {f["name"] for f in mcp.FERRAMENTAS}
        self.assertLessEqual(set(seguranca.BAIXO_RISCO), fixas)

    def test_decisoes_iguais_para_cada_ferramenta(self):
        """Mesma ordem de regras: sempre → travado → armado → baixo risco desarmado."""
        agora = 1_000_000.0
        estados = [
            {"travado": True, "armado_ate": 0, "desarmado_permite": "ir"},
            {"travado": False, "armado_ate": agora + 60, "desarmado_permite": "ir"},
            {"travado": False, "armado_ate": 0, "desarmado_permite": "ir"},
            {"travado": False, "armado_ate": 0, "desarmado_permite": "nada"},
        ]

        def borda(nome, e):  # tradução literal de bloqueioNaBorda (index.js)
            if nome in self.sempre:
                return True
            if e["travado"]:
                return False
            if e["armado_ate"] > agora:
                return True
            return e["desarmado_permite"] == "ir" and nome in self.baixo

        for e in estados:
            for f in mcp.FERRAMENTAS:
                with self.subTest(ferramenta=f["name"], estado=e):
                    ok, _ = seguranca.permitido(f["name"], e, agora)
                    self.assertEqual(ok, borda(f["name"], e))

    def test_funcao_da_borda_continua_com_a_mesma_ordem(self):
        corpo = re.search(r"function bloqueioNaBorda\(nome, e\) \{(.*?)\n\}", self.fonte, re.S).group(1)
        ordem = [corpo.find(t) for t in ("SEMPRE.has", "e.travado", "e.armado_ate", "BAIXO_RISCO.has")]
        self.assertTrue(all(i >= 0 for i in ordem) and ordem == sorted(ordem), ordem)


class TestFerramentasDaMissao(unittest.TestCase):
    """Toda ferramenta que a missão pode escolher sozinha existe no MCP (fixa ou cap_ de uma embutida)."""

    def test_permitidas_existem(self):
        arvore = ast.parse((RAIZ / "controle-ir" / "controle_ir" / "ambiente_missao.py").read_text("utf-8"))
        permitidas = None
        for no in ast.walk(arvore):
            if isinstance(no, ast.Assign) and any(getattr(t, "id", "") == "permitidas" for t in no.targets):
                permitidas = {e.value for e in no.value.elts}
        self.assertTrue(permitidas, "conjunto 'permitidas' não encontrado em ambiente_missao.executar")
        fixas = {f["name"] for f in mcp.FERRAMENTAS}
        embutidas = {"cap_" + json.loads(p.read_text("utf-8"))["nome"] for p in CAPS.glob("*/capacidade.json")}
        self.assertEqual(permitidas - fixas - embutidas, set())


class TestResumoSemRepeticao(unittest.TestCase):
    """Perfil misto (teclas + estado completo): cada parâmetro aparece uma vez no resumo do consultar."""

    def test_modo_nas_teclas_e_no_estado_completo(self):
        perfil = {"nome": "Gree misto", "comandos": [
            {"chave": "energia_desligar", "tipo": "definir", "efeitos": {"energia": "desligado"}},
            {"chave": "modo_turbo", "tipo": "definir", "efeitos": {"modo": "turbo"}},
            {"chave": "oscilacao_alternar", "tipo": "alternar", "parametro": "oscilacao"},
        ], "estado_completo": {"parametros": {"modo": {"valores": ["frio", "seco"]},
                                              "temperatura": {"min": 16, "max": 30},
                                              "ventilacao": {"valores": ["auto", "baixa"]}},
                               "estados": [], "desligar": True}}
        r = aparelhos.resumo_aparelho({"nome": "ar do quarto", "categoria": "ar_condicionado", "perfil": perfil})
        self.assertEqual(r["tipo_controle"], "misto")
        self.assertEqual(r["parametros"], ["energia", "modo", "oscilacao", "temperatura", "ventilacao"])
        self.assertEqual(len(r["parametros"]), len(set(r["parametros"])))

    def test_estado_completo_puro_e_so_teclas_continuam_iguais(self):
        ec = {"parametros": {"modo": {}, "temperatura": {"min": 17, "max": 30}}, "estados": []}
        so_ec = aparelhos.resumo_aparelho({"nome": "a", "perfil": {"comandos": [], "estado_completo": ec}})
        self.assertEqual(so_ec["parametros"], ["modo", "temperatura"])
        teclas = aparelhos.resumo_aparelho({"nome": "t", "perfil": {"comandos": [
            {"chave": "volume_mais", "tipo": "ajustar", "parametro": "volume", "passo": 1}]}})
        self.assertEqual(teclas["parametros"], ["volume"])


def _estado_celular():
    spec = importlib.util.spec_from_file_location("estado_celular_teste", CAPS / "estado_celular" / "principal.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # só define funções: o JSON sai em main()
    return mod


class TestEstadoCelularSemProc(unittest.TestCase):
    """Android 16: o app não lê /proc/uptime nem /proc/loadavg. O tempo ligado vem do CLOCK_BOOTTIME e a carga
    sem leitura vira null (antes saía 0, como se o processador estivesse ocioso)."""

    def test_sem_proc_usa_o_relogio_de_boot(self):
        mod = _estado_celular()
        with mock.patch.object(mod, "ler", return_value=None), \
                mock.patch.object(mod.time, "clock_gettime", return_value=7200.0):
            self.assertEqual(mod.ligado_ha_horas(), 2.0)

    def test_sem_leitura_da_carga_nao_finge_ocioso(self):
        mod = _estado_celular()
        with mock.patch.object(mod, "ler", return_value=None), \
                mock.patch.object(mod.os, "getloadavg", side_effect=OSError("bloqueado")):
            self.assertIsNone(mod.carga_cpu_1min())
        with mock.patch.object(mod, "ler", return_value=None), \
                mock.patch.object(mod.os, "getloadavg", return_value=(1.234, 1.0, 0.5)):
            self.assertEqual(mod.carga_cpu_1min(), 1.23)

    def test_com_proc_legivel_continua_igual(self):
        mod = _estado_celular()
        with mock.patch.object(mod, "ler", side_effect=lambda c: ["36000.5", "1"] if "uptime" in c else ["0.42"]):
            self.assertEqual(mod.ligado_ha_horas(), 10.0)
            self.assertEqual(mod.carga_cpu_1min(), 0.42)

    def test_script_ainda_imprime_o_json_completo(self):
        r = subprocess.run([sys.executable, str(CAPS / "estado_celular" / "principal.py")], input="{}",
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        dados = json.loads(r.stdout)
        for campo in ("modelo", "android", "bateria", "wifi", "armazenamento_livre_gb", "ligado_ha_horas",
                      "carga_cpu_1min", "termux_api_disponivel"):
            self.assertIn(campo, dados)
        self.assertIsInstance(dados["ligado_ha_horas"], float)


class TestAtualizacaoRecompila(unittest.TestCase):
    """Os arquivos do ZIP têm data fixa (1980). Sem apagar os __pycache__, um fonte novo do mesmo tamanho (só a
    versão mudou) reaproveita o .pyc antigo: em 21/11 o POCO rodava o código da 1.0.66 dizendo 1.0.65."""

    @staticmethod
    def _versao(raiz: str) -> str:
        env = {k: v for k, v in os.environ.items() if k != "PYTHONDONTWRITEBYTECODE"}
        r = subprocess.run([sys.executable, "-c", "import pacote_teste; print(pacote_teste.v)"], cwd=raiz,
                           capture_output=True, text=True, timeout=30, env=env)
        return r.stdout.strip()

    def test_instalador_apaga_os_caches_antes_de_religar(self):
        linha = next(ln for ln in (RAIZ / "controle-ir" / "instalar.sh").read_text("utf-8").splitlines()
                     if ln.startswith("find ") and "__pycache__" in ln)
        data_do_zip = 315532800  # 01/01/1980, a data que o unzip aplica aos arquivos do pacote
        with tempfile.TemporaryDirectory() as tmp:
            ini = Path(tmp) / "pacote_teste" / "__init__.py"
            ini.parent.mkdir()
            for versao in ("1.0.65", "1.0.66"):
                ini.write_text(f'v = "{versao}"\n')
                os.utime(ini, (data_do_zip, data_do_zip))
                self.assertEqual(self._versao(tmp), "1.0.65")  # 2ª volta: o .pyc antigo passa por válido
            subprocess.run(["bash", "-c", linha], env={**os.environ, "DIR": tmp}, check=True, timeout=30)
            self.assertFalse((ini.parent / "__pycache__").exists())
            self.assertEqual(self._versao(tmp), "1.0.66")


if __name__ == "__main__":
    unittest.main()
