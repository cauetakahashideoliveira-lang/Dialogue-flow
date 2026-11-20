"""Testes de contrato do plano de operações. Não chamam rede ou hardware."""
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

for raiz in Path(__file__).resolve().parents:
    if (raiz / "controle-ir/controle_ir/ambiente_missao.py").is_file():
        sys.path.insert(0, str(raiz / "controle-ir"))
        break
from controle_ir import ambiente_missao as agente

OPCOES = [{"nome":"cap_estado_celular"}, {"nome":"politica"}]


class PlanoTest(unittest.TestCase):
    def planejar(self, resposta):
        with patch.object(agente, "consultar_modelo", return_value=resposta):
            return agente.planejar(None, "objetivo", OPCOES)

    def test_ordem_e_plano_vazio(self):
        self.assertEqual(self.planejar('{"indices":[2,1]}'), OPCOES[::-1])
        self.assertEqual(self.planejar('{"indices":[]}'), [])

    def test_rejeita_respostas_invalidas(self):
        entradas = ["", "não sei", "null", "[]", '{"indices":"1"}', '{"indices":[true]}',
                    '{"indices":[0]}', '{"indices":[3]}', '{"indices":[1,1]}',
                    '{"indices":[1],"extra":2}', '{"indices":[1,2,3,4,5,6,7,8,9]}']
        for entrada in entradas:
            with self.subTest(entrada=entrada), self.assertRaises(agente.RespostaDePlanoInvalida):
                self.planejar(entrada)

    def test_contrato_da_requisicao(self):
        piloto = Mock(API_VERSAO="teste")
        piloto.ler_chave.return_value = "valor-de-teste"
        def resposta(req, timeout):
            corpo = json.loads(req.data)
            self.assertEqual(corpo["output_config"], {"effort":"high","format":{
                "type":"json_schema","schema":agente.ESQUEMA_PLANO}})
            self.assertEqual(timeout,45)
            return io.BytesIO(b'{"stop_reason":"end_turn","content":[{"type":"text","text":"{\\"indices\\":[1]}"}]}')
        with patch.object(agente.urllib.request, "urlopen", side_effect=resposta):
            self.assertEqual(agente.planejar(piloto, "objetivo", OPCOES), OPCOES[:1])

    def test_diagnostico_e_despacho(self):
        ctx = {"ferramentas":[{"nome":o["nome"], "permitida":True} for o in OPCOES],
               "habilidades_do_projeto":{}, "nos_no_grafo":0, "relacoes_do_grafo":[]}
        teste = {"argumentos":{"texto":"objetivo", "opcoes":OPCOES}}
        for plano,codigo,n in [(agente.RespostaDePlanoInvalida("x"),"resposta_invalida",0),
                               (TimeoutError(),"modelo_indisponivel",0),([],"plano_vazio",0),
                               (OPCOES,"execucao_falhou",1)]:
            with self.subTest(codigo=codigo), patch.object(agente,"contexto",return_value=ctx), \
                    patch("controle_ir.capacidades.modulo_embutido"), patch.object(agente,"planejar") as decidir:
                if isinstance(plano,Exception):
                    decidir.side_effect = plano
                else:
                    decidir.return_value = plano
                mcp = Mock()
                mcp.chamar.return_value = {"isError":True, "structuredContent":{"erro":"bloqueado"}}
                r = agente.executar(mcp,teste,None)
                self.assertEqual((r["estado"],r["codigo"]),("interrompida",codigo))
                self.assertEqual(mcp.chamar.call_count,n)
                self.assertIsNone(agente.ATUAL.get())

    def test_permissao_antes_de_consultar_modelo(self):
        ctx = {"ferramentas":[{"nome":o["nome"],"permitida":False} for o in OPCOES]}
        with patch.object(agente,"contexto",return_value=ctx), patch.object(agente,"planejar") as decidir:
            mcp = Mock()
            r = agente.executar(mcp,{"argumentos":{"texto":"objetivo","opcoes":OPCOES}},None)
            self.assertEqual(r["codigo"],"nenhuma_opcao_permitida")
            decidir.assert_not_called()
            mcp.chamar.assert_not_called()

if __name__ == "__main__":
    unittest.main()
