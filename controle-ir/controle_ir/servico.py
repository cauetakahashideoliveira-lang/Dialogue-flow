"""Camada de serviço: as operações expostas ao Claude (MCP) e ao painel.

Cada método recebe argumentos simples e devolve um dicionário estruturado.
Erros esperados viram ``ErroUso`` com mensagem em português para o Claude
explicar ao usuário.
"""
from __future__ import annotations

import copy
import threading
import time
from pathlib import Path

from . import __version__, formatos, vocabulario
from .aparelhos import Aparelhos, ErroAparelho, agora, capacidades, hora_legivel, resumo_aparelho
from .catalogo import Catalogo
from .controle import Controlador, executar
from .descoberta import Descoberta, ErroDescoberta
from .emissor import ErroEmissor
from .sinais import ErroSinal, Sinal


class ErroUso(ValueError):
    pass


class Servico:
    def __init__(self, pasta: str, emissor, catalogo: Catalogo | None = None, notificar=None):
        self.pasta = Path(pasta)
        self.pasta.mkdir(parents=True, exist_ok=True)
        self.emissor = emissor
        self.cat = catalogo or Catalogo(self.pasta / "catalogo.sqlite")
        self.aparelhos = Aparelhos(self.pasta / "aparelhos.json")
        self.desc = Descoberta(self.cat, emissor, self.pasta / "sessao.json", notificar)
        self.trava_envio = threading.Lock()
        self.ultima_requisicao_claude: float | None = None
        self.url_publica: str | None = None
        self.inicio = agora()

    # ------------------------------------------------------------- consulta
    def consultar(self, categoria=None, marca=None, texto=None) -> dict:
        est = self.cat.estatisticas()
        out = {
            "servidor": {"versao": __version__, "ativo_desde": hora_legivel(self.inicio)},
            "emissor": self.emissor.disponivel(),
            "catalogo": {"perfis": est["perfis"], "sinais_unicos": est["sinais_unicos"], "marcas": est["marcas"],
                         "categorias": est["categorias"], "fontes": est["fontes"]},
            "aparelhos_salvos": [resumo_aparelho(a) for a in self.aparelhos.listar()],
        }
        out["marcas"] = self.cat.marcas(categoria, marca or texto, 40)
        if categoria:
            out["filtro_categoria"] = vocabulario.categoria_canonica(categoria)
        if self.desc.s:
            p = self.desc.progresso(ultimos=0)
            out["busca"] = {k: p[k] for k in ("estado", "testados", "total") if k in p}
        out["categorias_aceitas"] = {k: v[0] for k, v in vocabulario.CATEGORIAS.items()}
        return out

    def procurar_perfis(self, categoria=None, marca=None, modelo=None, texto=None, limite=20) -> dict:
        res = self.cat.procurar(categoria, marca, modelo, texto, int(limite or 20))
        out = {"perfis": res, "quantidade": len(res)}
        if marca and not self.cat.marca_existe(marca):
            out["aviso"] = f"a marca “{marca}” não está no catálogo instalado"
            out["marcas_parecidas"] = self.cat.marcas(categoria, marca[:3], 10)
        return out

    def opcoes(self, aparelho=None, perfil=None) -> dict:
        if aparelho:
            a = self._aparelho(aparelho)
            cap = capacidades(a["perfil"], a.get("faixas"))
            est = a.get("estado", {})
            return {"aparelho": a["nome"], "categoria": a.get("categoria"), "perfil": a["perfil"].get("nome"),
                    **cap, "faixas": a.get("faixas", {}), "macros": {k: v.get("descricao") for k, v in a.get("macros", {}).items()},
                    "ultimo_envio": {k: v["valor"] for k, v in est.get("ultimo_envio", {}).items()},
                    "ultima_configuracao_completa": est.get("estado_completo"),
                    "confirmado_por_voce": {k: v["valor"] for k, v in est.get("confirmado", {}).items()},
                    "controle_original_usado_em": hora_legivel(est.get("controle_original_em")),
                    "alternativos": len(a.get("origem", {}).get("alternativos", []))}
        if perfil is not None:
            p = self.cat.perfil(perfil)
            if not p:
                raise ErroUso(f"perfil {perfil} não encontrado")
            return {"perfil": p["nome"], "id": p["id"], "marca": p["marca"], "categoria": p["categoria"],
                    "fonte": p["fonte"], "licenca": p["licenca"], **capacidades(p)}
        raise ErroUso("informe aparelho (nome salvo) ou perfil (id do catálogo)")

    # ------------------------------------------------------------- descoberta
    def buscar(self, categoria=None, marca=None, modelo=None, pistas=None, comando_teste=None, intervalo=None,
               lote=None, modo="perfis", aparelho=None, varredura=False, apenas_marca=True, continuar=False) -> dict:
        disp = self.emissor.disponivel()
        if not disp.get("disponivel"):
            raise ErroUso(f"emissor indisponível: {disp.get('motivo')}")
        if continuar:
            return self.desc.retomar(intervalo=intervalo, lote=lote)
        ap = self._aparelho(aparelho) if aparelho else None
        try:
            return self.desc.iniciar(categoria, marca, modelo, pistas, comando_teste, intervalo, lote,
                                     modo or "perfis", ap, bool(varredura), apenas_marca if apenas_marca is not None else True)
        except ErroDescoberta as e:
            raise ErroUso(str(e)) from e

    def progresso(self, ultimos=8):
        return self._d(lambda: self.desc.progresso(int(ultimos or 8)))

    def pausar(self, origem="claude"):
        return self._d(lambda: self.desc.pausar(origem))

    def retomar(self, intervalo=None, a_partir_de=None, lote=None):
        return self._d(lambda: self.desc.retomar(intervalo, a_partir_de, lote))

    def retestar(self, numeros, intervalo=None):
        if isinstance(numeros, (int, str)):
            numeros = [numeros]
        return self._d(lambda: self.desc.retestar([int(n) for n in numeros], intervalo))

    def confirmar(self, numero, funcionou=True):
        return self._d(lambda: self.desc.confirmar(int(numero), bool(funcionou)))

    def distinguir(self, teste, variante):
        return self._d(lambda: self.desc.distinguir(teste, variante))

    @staticmethod
    def _d(f):
        try:
            return f()
        except ErroDescoberta as e:
            raise ErroUso(str(e)) from e

    # ------------------------------------------------------------- aparelhos
    def _aparelho(self, nome) -> dict:
        try:
            return self.aparelhos.obter(str(nome))
        except ErroAparelho as e:
            raise ErroUso(str(e)) from e

    def salvar_aparelho(self, nome, perfil=None, somente_confirmado=False, categoria=None, substituir=False,
                        numero=None, funcao=None) -> dict:
        if not nome or not str(nome).strip():
            raise ErroUso("informe o nome do aparelho, por exemplo “ventilador da sala”")
        origem: dict = {}
        avisos = []
        if perfil is not None:
            p = self.cat.perfil(perfil)
            if not p:
                raise ErroUso(f"perfil {perfil} não encontrado no catálogo")
            origem = {"perfil_id": p["id"], "perfil_chave": p["chave"]}
        else:
            try:
                r = self.desc.resultado_para_salvar()
            except ErroDescoberta as e:
                raise ErroUso(f"{e}. Informe perfil=<id> para salvar a partir do catálogo.") from e
            ativos = r["perfis_ativos"]
            if r["modo"] == "perfis" and ativos and not somente_confirmado:
                escolhido = self._melhor_perfil(ativos, r["filtros"])
                p = self.cat.perfil(escolhido)
                origem = {"perfil_id": p["id"], "perfil_chave": p["chave"], "sessao": r["sessao"],
                          "alternativos": [x for x in ativos if x != escolhido][:50]}
                if len(ativos) > 1:
                    avisos.append(f"{len(ativos)} perfis compartilhavam o sinal confirmado; salvei “{p['nome']}”. "
                                  "Se alguma tecla não funcionar, rode os testes de distinção ou troque o perfil "
                                  "com editar_aparelho(trocar_perfil=<id>).")
            else:
                p = formatos.novo_perfil(f"usuario:{vocabulario.slug(nome)}", str(nome), categoria)
                for c in r["confirmacoes"]:
                    chave = (c.get("chaves") or ["x_tecla"])[0]
                    if funcao:
                        termo = vocabulario.interpretar(funcao)
                    elif chave.startswith("@"):
                        termo = vocabulario.Termo("ligar_estado", "Ligar (configuração testada)", "definir",
                                                  efeitos=(("energia", "ligado"),))
                    else:
                        termo = vocabulario.termo_por_chave(chave)
                    formatos.adicionar_comando(p, formatos.comando(termo.rotulo, c["sinal"], termo))
                origem = {"sessao": r["sessao"], "somente_confirmado": True}
                avisos.append("Salvei apenas as teclas confirmadas. Para descobrir as outras teclas use "
                              "buscar(modo=\"teclas\", aparelho=...).")
        try:
            a = self.aparelhos.novo(str(nome), p, categoria or p.get("categoria"), origem, bool(substituir))
        except ErroAparelho as e:
            raise ErroUso(str(e)) from e
        cap = capacidades(a["perfil"])
        return {"salvo": a["nome"], "perfil": a["perfil"].get("nome"), "comandos": len(a["perfil"]["comandos"]),
                "parametros": sorted(cap["parametros"]) + sorted((cap.get("estado_completo") or {}).get("parametros", {})),
                "avisos": avisos}

    def _melhor_perfil(self, ids: list[int], filtros: dict) -> int:
        marca = (filtros or {}).get("marca")
        melhores = []
        for p in self.cat.nomes_perfis(ids, 500):
            row = self.cat.db.execute("SELECT ncomandos, estado IS NOT NULL, marca_norm FROM perfis WHERE id=?",
                                      (p["id"],)).fetchone()
            pont = row[0] + (200 if row[1] else 0)
            if marca and vocabulario.normalizar(marca) in (row[2] or ""):
                pont += 1000
            melhores.append((pont, p["id"]))
        return max(melhores)[1]

    def controlar(self, aparelho, ligar=None, definir=None, ajustar=None, teclas=None, macro=None,
                  permitir_alternancia=False, estado_atual=None, simular=False, permitir_servico=False,
                  repetir_ultimo=False) -> dict:
        a = self._aparelho(aparelho)
        if repetir_ultimo:
            if not a.get("ultimo_pedido"):
                raise ErroUso("não há pedido anterior para repetir neste aparelho")
            pedidos = [a["ultimo_pedido"]]
        elif macro:
            m = self._macro(a, macro)
            pedidos = m["passos"]
        else:
            pedidos = [{"ligar": ligar, "definir": definir, "ajustar": ajustar, "teclas": teclas,
                        "permitir_alternancia": permitir_alternancia, "estado_atual": estado_atual,
                        "permitir_servico": permitir_servico}]
        resultados = []
        with self.trava_envio:
            for i, ped in enumerate(pedidos):
                ped = {k: v for k, v in ped.items() if v not in (None, {}, [])}
                ped.setdefault("permitir_alternancia", permitir_alternancia)
                ctrl = Controlador(a)
                plano = ctrl.planejar(ped)
                r = executar(a, plano, self.emissor, simular)
                resultados.append(r)
                if r["status"] in ("sinal_enviado", "parcial") and not simular and not macro and not repetir_ultimo:
                    a["ultimo_pedido"] = ped
                if r["status"] not in ("sinal_enviado",) and len(pedidos) > 1:
                    r["macro_interrompida_no_passo"] = i + 1
                    break
            if not simular:
                self.aparelhos.salvar(a)
        if len(resultados) == 1:
            return resultados[0]
        return {"aparelho": a["nome"], "macro": macro, "passos": resultados,
                "status": "sinal_enviado" if all(r["status"] == "sinal_enviado" for r in resultados) else "parcial"}

    def _macro(self, a: dict, nome: str) -> dict:
        macros = a.get("macros", {})
        n = vocabulario.normalizar(nome)
        for k, m in macros.items():
            if vocabulario.normalizar(k) == n:
                return m
        for k, m in macros.items():
            if n in vocabulario.normalizar(k):
                return m
        raise ErroUso(f"o aparelho {a['nome']} não tem a macro “{nome}”. Macros: {', '.join(macros) or 'nenhuma'}")

    def registrar_estado(self, aparelho, estado=None, controle_original_usado=False) -> dict:
        a = self._aparelho(aparelho)
        est = a.setdefault("estado", {"ultimo_envio": {}, "confirmado": {}})
        t = agora()
        if controle_original_usado:
            est["controle_original_em"] = t
            est["estado_completo"] = None if not estado else est.get("estado_completo")
        for k, v in (estado or {}).items():
            par = vocabulario.normalizar(k).replace(" ", "_")
            est.setdefault("confirmado", {})[par] = {"valor": vocabulario.normalizar_valor(v)
                                                     if par != "temperatura" else v, "hora": t + 0.05}
        ec_par = (a["perfil"].get("estado_completo") or {}).get("parametros", {})
        if estado and ec_par:
            base = dict(est.get("estado_completo") or {})
            for k, v in estado.items():
                par = vocabulario.normalizar(k).replace(" ", "_")
                if par in ec_par:
                    if par == "temperatura":
                        base[par] = v
                    else:
                        eq = vocabulario.valores_equivalentes(v, ec_par[par])
                        if eq:
                            base[par] = eq[0]
            est["estado_completo"] = base or None
        self.aparelhos.salvar(a)
        return {"aparelho": a["nome"], "confirmado": {k: v["valor"] for k, v in est.get("confirmado", {}).items()},
                "controle_original_usado_em": hora_legivel(est.get("controle_original_em")),
                "observacao": "Próximos pedidos usarão estes valores como estado atual."}

    def editar_aparelho(self, aparelho, renomear=None, adicionar_comando=None, remover_comando=None,
                        renomear_comando=None, faixas=None, macro=None, remover_macro=None, trocar_perfil=None,
                        configuracao=None, excluir=False) -> dict:
        a = self._aparelho(aparelho)
        feitos = []
        if excluir:
            self.aparelhos.remover(a["nome"])
            return {"excluido": a["nome"]}
        if trocar_perfil is not None:
            p = self.cat.perfil(trocar_perfil)
            if not p:
                raise ErroUso(f"perfil {trocar_perfil} não encontrado")
            extras = [c for c in a["perfil"]["comandos"] if c.get("adicionado_pelo_usuario")]
            a["perfil"] = copy.deepcopy(p)
            for c in extras:
                formatos.adicionar_comando(a["perfil"], c)
            a.setdefault("origem", {})["perfil_id"] = p["id"]
            feitos.append(f"perfil trocado para {p['nome']} (mantidos {len(extras)} comandos seus)")
        if adicionar_comando:
            ac = adicionar_comando
            nome = ac.get("nome") or ac.get("funcao")
            if not nome:
                raise ErroUso("adicionar_comando precisa de nome (ex.: “volume +” ou “apresentação”)")
            if ac.get("numero") is not None:
                try:
                    sinal, _ = self.desc.sinal_do_historico(int(ac["numero"]))
                except ErroDescoberta as e:
                    raise ErroUso(str(e)) from e
            elif ac.get("sinal"):
                sinal = Sinal(ac["sinal"]).compacto()
            elif ac.get("conteudo"):
                sinal = formatos.ler_sinal_texto(ac["conteudo"])
            elif ac.get("de_perfil") is not None and ac.get("comando"):
                p = self.cat.perfil(ac["de_perfil"])
                c = next((x for x in (p or {}).get("comandos", []) if x["chave"] == ac["comando"]), None)
                if not c:
                    raise ErroUso("comando não encontrado nesse perfil")
                sinal = c["sinal"]
            else:
                raise ErroUso("informe numero (do histórico da busca), sinal, conteudo ou de_perfil+comando")
            termo = vocabulario.interpretar(ac.get("funcao") or nome)
            if ac.get("funcao") and ac.get("nome") and ac["nome"] != ac["funcao"]:
                termo = vocabulario.Termo(termo.chave, ac["nome"], termo.tipo, termo.parametro, termo.passo,
                                          termo.efeitos, termo.teste, termo.risco)
            elif termo.chave.startswith("x_"):
                termo = vocabulario.Termo(termo.chave, str(nome), "tecla")
            cmd = formatos.comando(nome, sinal, termo)
            cmd["adicionado_pelo_usuario"] = True
            c = formatos.adicionar_comando(a["perfil"], cmd)
            feitos.append(f"comando “{c['rotulo']}” ({c['chave']}, tipo {c['tipo']}) adicionado")
        if remover_comando:
            antes = len(a["perfil"]["comandos"])
            chave = Controlador(a)._resolver_tecla(remover_comando) or remover_comando
            a["perfil"]["comandos"] = [c for c in a["perfil"]["comandos"] if c["chave"] != chave]
            feitos.append(f"{antes - len(a['perfil']['comandos'])} comando(s) removido(s)")
        if renomear_comando:
            chave = Controlador(a)._resolver_tecla(renomear_comando.get("de", "")) or renomear_comando.get("de")
            for c in a["perfil"]["comandos"]:
                if c["chave"] == chave:
                    c["rotulo"] = renomear_comando.get("para") or c["rotulo"]
                    feitos.append(f"comando renomeado para “{c['rotulo']}”")
        if faixas:
            for par, f in faixas.items():
                par_n = vocabulario.normalizar(par).replace(" ", "_")
                if f is None:
                    a.setdefault("faixas", {}).pop(par_n, None)
                    continue
                a.setdefault("faixas", {})[par_n] = {k: v for k, v in f.items() if k in ("min", "max", "valores", "ciclico")}
            feitos.append(f"faixas atualizadas: {a['faixas']}")
        if macro:
            nome_m = macro.get("nome")
            passos = macro.get("passos")
            if not nome_m or not passos:
                raise ErroUso("macro precisa de nome e passos (lista de pedidos como em controlar)")
            teste = Controlador(a)
            for p in passos:
                pl = teste.planejar({k: v for k, v in p.items() if v is not None})
                if pl.erros:
                    raise ErroUso(f"passo inválido na macro: {pl.erros}")
            a.setdefault("macros", {})[nome_m] = {"passos": passos, "descricao": macro.get("descricao"),
                                                  "criada": agora()}
            feitos.append(f"macro “{nome_m}” salva com {len(passos)} passo(s)")
        if remover_macro:
            a.get("macros", {}).pop(remover_macro, None)
            feitos.append(f"macro “{remover_macro}” removida")
        if configuracao:
            for k in ("intervalo_teclas", "espera_apos_ligar"):
                if k in configuracao:
                    a.setdefault("config", {})[k] = max(0.1, min(float(configuracao[k]), 10.0))
            feitos.append(f"configuração: {a['config']}")
        if renomear:
            novo_id = vocabulario.slug(renomear)
            if novo_id != a["id"] and novo_id in self.aparelhos.dados["aparelhos"]:
                raise ErroUso(f"já existe um aparelho chamado “{renomear}”")
            del self.aparelhos.dados["aparelhos"][a["id"]]
            a["id"], a["nome"] = novo_id, renomear
            feitos.append(f"renomeado para “{renomear}”")
        self.aparelhos.salvar(a)
        return {"aparelho": a["nome"], "alteracoes": feitos}

    # ------------------------------------------------------------- import/export
    def importar(self, conteudo, nome=None, categoria=None, marca=None, modelo=None, destino="catalogo",
                 aparelho=None) -> dict:
        if not conteudo or not str(conteudo).strip():
            raise ErroUso("conteúdo vazio")
        try:
            p = formatos.importar_texto(str(conteudo), nome, categoria, marca, modelo)
        except (formatos.ErroFormato, ErroSinal, ValueError) as e:
            raise ErroUso(f"não consegui importar: {e}") from e
        p["fonte"], p["licenca"] = "usuario", "do usuário"
        if destino == "aparelho":
            if aparelho:
                a = self._aparelho(aparelho)
                for c in p["comandos"]:
                    c["adicionado_pelo_usuario"] = True
                    formatos.adicionar_comando(a["perfil"], c)
                self.aparelhos.salvar(a)
                return {"aparelho": a["nome"], "comandos_adicionados": len(p["comandos"])}
            if not nome:
                raise ErroUso("para criar um aparelho a partir da importação, informe nome")
            a = self.aparelhos.novo(nome, p, categoria, {"importado": True})
            return {"aparelho": a["nome"], "comandos": len(p["comandos"]),
                    "capacidades": sorted(capacidades(p)["parametros"])}
        p["chave"] = f"usuario:{vocabulario.slug(p.get('nome') or 'importado')}:{int(time.time())}"
        pid = self.cat.adicionar_perfil(p)
        self.cat.commit()
        self.cat.registrar_fonte("usuario")
        pasta = self.pasta / "importados"
        pasta.mkdir(exist_ok=True)
        (pasta / f"{pid}.json").write_text(formatos.exportar(p, "json"))
        return {"perfil_id": pid, "nome": p["nome"], "comandos": len(p["comandos"]),
                "estado_completo": bool(p.get("estado_completo")),
                "capacidades": sorted(capacidades(p)["parametros"]),
                "orientacao": "O perfil já pode ser usado em buscar (entra nos candidatos) ou salvo com "
                              f"salvar_aparelho(perfil={pid})."}

    def exportar(self, aparelho=None, perfil=None, formato="json") -> dict:
        if aparelho:
            a = self._aparelho(aparelho)
            p = dict(a["perfil"], nome=a["nome"])
        elif perfil is not None:
            p = self.cat.perfil(perfil)
            if not p:
                raise ErroUso("perfil não encontrado")
        else:
            raise ErroUso("informe aparelho ou perfil")
        texto = formatos.exportar(p, formato)
        destino = self.pasta / "exportados"
        destino.mkdir(exist_ok=True)
        ext = {"flipper": "ir", "ir": "ir", "pronto": "txt"}.get((formato or "json").lower(), "json")
        arq = destino / f"{vocabulario.slug(p['nome'])}.{ext}"
        arq.write_text(texto)
        return {"arquivo_no_celular": str(arq), "formato": formato, "conteudo": texto[:20000],
                "truncado": len(texto) > 20000}

    def enviar_sinal(self, sinal=None, conteudo=None, vezes=1) -> dict:
        try:
            s = Sinal(sinal) if sinal else Sinal(formatos.ler_sinal_texto(conteudo or ""))
        except (ErroSinal, formatos.ErroFormato, ValueError) as e:
            raise ErroUso(f"sinal inválido: {e}") from e
        enviados = 0
        with self.trava_envio:
            for _ in range(max(1, min(int(vezes or 1), 10))):
                try:
                    self.emissor.enviar(s)
                    enviados += 1
                except ErroEmissor as e:
                    return {"status": "falhou", "enviados": enviados, "erro": str(e)}
                time.sleep(0.3)
        return {"status": "sinal_enviado", "enviados": enviados, "sinal": s.descricao(),
                "orientacao": "Se funcionou, guarde com editar_aparelho(adicionar_comando={nome, conteudo}) ou importar."}

    # ------------------------------------------------------------- painel
    def estado_painel(self) -> dict:
        disp = self.emissor.disponivel()
        return {
            "versao": __version__,
            "claude": {"ultima_requisicao": hora_legivel(self.ultima_requisicao_claude),
                       "segundos": round(time.time() - self.ultima_requisicao_claude, 0)
                       if self.ultima_requisicao_claude else None,
                       "url": self.url_publica},
            "emissor": disp,
            "busca": self.desc.painel(),
            "aparelhos": [{"nome": a["nome"], "categoria": a.get("categoria"),
                           "teclas": [{"chave": c["chave"], "rotulo": c.get("rotulo")}
                                      for c in a["perfil"].get("comandos", []) if not c.get("risco")][:40],
                           "estado": {k: v["valor"] for k, v in a.get("estado", {}).get("ultimo_envio", {}).items()}}
                          for a in self.aparelhos.listar()],
        }
