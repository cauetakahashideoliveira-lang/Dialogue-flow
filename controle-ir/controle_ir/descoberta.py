"""Descoberta automática do controle certo por testes observáveis.

Fluxo:
1. ``iniciar`` monta a fila de candidatos (sinais únicos que implementam o
   comando de teste) priorizando marca, modelo, categoria e popularidade;
2. uma thread envia um candidato a cada ``intervalo`` segundos, em lotes;
3. ``pausar`` (Claude, painel, notificação ou Enter no Termux) interrompe na
   hora e aponta os *suspeitos* — o último sinal e os enviados durante o
   tempo de reação humana;
4. ``retestar`` repete qualquer tentativa; ``confirmar`` registra o que
   funcionou e, se vários perfis compartilham o sinal, propõe testes de
   distinção com uma segunda função; ``distinguir`` envia cada variante.

O estado da sessão fica em disco: dá para fechar o app e continuar depois.
"""
from __future__ import annotations

import json
import math
import os
import tempfile
import threading
import time
import uuid
from pathlib import Path

from . import vocabulario
from .aparelhos import agora, hora_legivel
from .catalogo import MARCAS_RELACIONADAS, Catalogo, normalizar_marca
from .emissor import ErroEmissor
from .sinais import Sinal

INTERVALO_PADRAO = 8.0
LOTE_PADRAO = 25
LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class ErroDescoberta(RuntimeError):
    pass


class Descoberta:
    def __init__(self, catalogo: Catalogo, emissor, caminho: str | os.PathLike, notificar=None):
        self.cat = catalogo
        self.emissor = emissor
        self.caminho = Path(caminho)
        self.notificar = notificar or (lambda evento: None)
        self.trava = threading.RLock()
        self.acordar = threading.Event()
        self.thread: threading.Thread | None = None
        self.s: dict | None = None
        if self.caminho.exists():
            try:
                self.s = json.loads(self.caminho.read_text())
                if self.s.get("estado") == "executando":
                    self.s["estado"] = "pausado"
                    self.s["pausado_em"] = agora()
                    self.s["motivo_pausa"] = "o serviço foi reiniciado"
            except (json.JSONDecodeError, OSError):
                self.s = None

    # ----------------------------------------------------------- persistência
    def _gravar(self):
        if not self.s:
            return
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(self.caminho.parent), prefix=".sessao")
        with os.fdopen(fd, "w") as f:
            json.dump(self.s, f, ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp, self.caminho)

    def _exigir(self) -> dict:
        if not self.s:
            raise ErroDescoberta("nenhuma busca em andamento — use buscar para começar")
        return self.s

    # ----------------------------------------------------------- candidatos
    def _fila_perfis(self, categoria, marca, modelo, comando_teste, apenas_marca, avisos) -> tuple[list, dict]:
        cat = vocabulario.categoria_canonica(categoria) if categoria else None
        if categoria and not cat:
            avisos.append(f"categoria “{categoria}” não reconhecida; buscando em todas.")
        chaves = vocabulario.chaves_de_teste(cat, comando_teste)
        marcas_ok: list[str] = []
        relacionadas: list[str] = []
        if marca:
            marcas_ok = self.cat.marca_existe(marca)
            for m in marcas_ok or [normalizar_marca(marca)]:
                relacionadas += [r for r in MARCAS_RELACIONADAS.get(m, []) if self.cat.marca_existe(r)]
            if not marcas_ok:
                avisos.append(f"a marca “{marca}” não está no catálogo instalado; a busca não foi filtrada por marca.")
        filtro_marcas = (marcas_ok + relacionadas) if (marcas_ok and apenas_marca) else None
        grupos = self.cat.candidatos(chaves, cat, filtro_marcas)
        if cat and filtro_marcas:
            # perfis da marca sem categoria (coleções convertidas) entram depois
            extra = self.cat.candidatos(chaves, None, filtro_marcas)
            ids = {g["sinal_id"] for g in grupos}
            for g in extra:
                if g["sinal_id"] not in ids:
                    g["sem_categoria"] = True
                    grupos.append(g)
        if not grupos and cat:
            avisos.append(f"nenhum perfil de {cat} com o comando de teste; ampliando para todas as categorias.")
            grupos = self.cat.candidatos(chaves, None, filtro_marcas)
        modelo_tok = set(vocabulario.normalizar(modelo or "").split())

        def pontuar(g):
            s = 10 * math.log2(1 + len(g["perfis"]))
            if marcas_ok and set(marcas_ok) & g["marcas"]:
                s += 60
            elif relacionadas and set(relacionadas) & g["marcas"]:
                s += 35
            if g.get("sem_categoria"):
                s -= 15
            s -= 4 * g["prioridade"]
            return s

        if modelo_tok:
            # bônus por modelo: busca perfis com o modelo no nome
            achados = self.cat.procurar(cat, None, modelo, limite=200) if modelo else []
            ids_modelo = {p["id"] for p in achados}
            for g in grupos:
                if ids_modelo & g["perfis"]:
                    g["bonus_modelo"] = True
        grupos.sort(key=lambda g: -(pontuar(g) + (80 if g.get("bonus_modelo") else 0)))
        fila = [{"sinal_id": g["sinal_id"], "perfis": sorted(g["perfis"]), "chaves": sorted(g["chaves"]),
                 "marcas": sorted(m for m in g["marcas"] if m)[:6]} for g in grupos]
        return fila, {"categoria": cat, "chaves_teste": chaves, "marcas_filtradas": filtro_marcas or [],
                      "marcas_relacionadas": relacionadas}

    def _fila_teclas(self, aparelho: dict, varredura: bool, avisos: list) -> tuple[list, dict]:
        conhecidos = {Sinal(c["sinal"]).impressao() for c in aparelho["perfil"].get("comandos", [])}
        perfis: set[int] = set()
        for imp in conhecidos:
            with self.cat.trava:
                row = self.cat.db.execute("SELECT id FROM sinais WHERE impressao=?", (imp,)).fetchone()
            if row:
                perfis |= set(self.cat.perfis_com_sinal(row[0]))
        grupos: dict[int, dict] = {}
        for r in self.cat.comandos_dos_perfis(sorted(perfis)):
            if r["meta"] and '"risco": true' in r["meta"]:
                continue
            g = grupos.setdefault(r["sinal"], {"sinal_id": r["sinal"], "perfis": set(), "funcoes": {}})
            g["perfis"].add(r["perfil"])
            g["funcoes"][r["base"]] = g["funcoes"].get(r["base"], 0) + 1
        fila = []
        for g in grupos.values():
            imp = self.cat.db.execute("SELECT impressao FROM sinais WHERE id=?", (g["sinal_id"],)).fetchone()[0]
            if imp in conhecidos:
                continue
            funcao = max(g["funcoes"], key=g["funcoes"].get)
            fila.append({"sinal_id": g["sinal_id"], "perfis": sorted(g["perfis"]), "chaves": [funcao],
                         "funcao_provavel": vocabulario.termo_por_chave(funcao).rotulo, "votos": g["funcoes"][funcao]})
        fila.sort(key=lambda x: -x["votos"])
        if varredura:
            proto = next((c["sinal"] for c in aparelho["perfil"].get("comandos", []) if "protocolo" in c["sinal"]), None)
            if proto is None:
                for c in aparelho["perfil"].get("comandos", []):
                    comp = Sinal(c["sinal"]).compacto()
                    if "protocolo" in comp:
                        proto = comp
                        break
            if proto:
                from .protocolos import TAMANHOS
                bits = TAMANHOS[proto["protocolo"]][1]
                limite = min(2 ** bits, 256)
                existentes = {Sinal(c["sinal"]).impressao() for c in aparelho["perfil"].get("comandos", [])}
                existentes |= {Sinal(self.cat.sinal(f["sinal_id"])).impressao() for f in fila}
                for cmd in range(limite):
                    if proto["protocolo"] == "NECext" and bits == 16:
                        cmd_val = cmd | ((cmd ^ 0xFF) << 8)
                    else:
                        cmd_val = cmd
                    s = {"protocolo": proto["protocolo"], "endereco": proto["endereco"], "comando": cmd_val}
                    if Sinal(s).impressao() in existentes:
                        continue
                    fila.append({"sinal": s, "perfis": [], "chaves": [], "funcao_provavel": f"comando 0x{cmd:02X} (gerado)",
                                 "gerado": True})
                avisos.append("A varredura gera comandos do mesmo endereço que nunca foram catalogados. "
                              "Ela pode atingir menus de serviço; acompanhe a tela e pause se algo estranho aparecer.")
            else:
                avisos.append("varredura indisponível: o aparelho não tem sinal de protocolo reconhecido.")
        return fila, {"aparelho": aparelho["nome"], "perfis_relacionados": len(perfis)}

    # ----------------------------------------------------------- API pública
    def iniciar(self, categoria=None, marca=None, modelo=None, pistas=None, comando_teste=None,
                intervalo=None, lote=None, modo="perfis", aparelho=None, varredura=False,
                apenas_marca=True, iniciar_pausado=False) -> dict:
        avisos: list[str] = []
        if pistas and not (categoria or marca or modelo):
            # pistas livres: tenta extrair categoria e marca do texto
            categoria = vocabulario.categoria_canonica(pistas)
            for palavra in vocabulario.normalizar(pistas).split():
                if len(palavra) > 2 and self.cat.marca_existe(palavra) and palavra not in ("tv", "led", "som"):
                    marca = palavra
                    break
        if modo == "teclas":
            if not aparelho:
                raise ErroDescoberta("modo teclas precisa do aparelho salvo (salve a tecla que funcionou primeiro)")
            fila, filtros = self._fila_teclas(aparelho, varredura, avisos)
        else:
            fila, filtros = self._fila_perfis(categoria, marca, modelo, comando_teste, apenas_marca, avisos)
        if not fila:
            raise ErroDescoberta("nenhum candidato para esses filtros. Tente sem marca, outra categoria, outro "
                                 "comando de teste, ou amplie o catálogo (controle-ir catalogo ampliar).")
        intervalo = max(2.0, min(float(intervalo or INTERVALO_PADRAO), 60.0))
        lote = max(1, min(int(lote or LOTE_PADRAO), 500))
        self.parar_thread()
        with self.trava:
            self.s = {
                "id": uuid.uuid4().hex[:8], "criado": agora(), "modo": modo,
                "filtros": dict(filtros, marca=marca, modelo=modelo, pistas=pistas, comando_teste=comando_teste),
                "intervalo": intervalo, "lote": lote, "candidatos": fila, "cursor": 0, "inicio_lote": 0,
                "historico": [], "estado": "pausado" if iniciar_pausado else "executando",
                "pausado_em": agora() if iniciar_pausado else None, "motivo_pausa": None,
                "descartados": [], "confirmacoes": [], "perfis_ativos": None, "testes_distincao": [],
                "avisos": avisos,
            }
            self._gravar()
        if not iniciar_pausado:
            self._iniciar_thread()
        r = self.progresso(ultimos=0)
        r["avisos"] = avisos
        r["como_parar"] = ("Enter sozinho no Termux, o botão “Reagiu — pausar” no painel ou na notificação, "
                           "ou diga “ligou/apitou” no chat (o Claude chama pausar).")
        r["proximos"] = [self._descr_candidato(i) for i in range(0, min(3, len(fila)))]
        return r

    def _descr_candidato(self, idx: int) -> dict:
        c = self.s["candidatos"][idx]
        d = {"posicao": idx + 1, "perfis": len(c.get("perfis", []))}
        if c.get("funcao_provavel"):
            d["funcao_provavel"] = c["funcao_provavel"]
        if c.get("marcas"):
            d["marcas"] = c["marcas"]
        if c.get("chaves"):
            d["teste"] = [vocabulario.termo_por_chave(k).rotulo if not k.startswith("@") else "ligar (estado)"
                          for k in c["chaves"]]
        return d

    def _sinal_candidato(self, c: dict) -> dict:
        return c["sinal"] if "sinal" in c else self.cat.sinal(c["sinal_id"])

    def _enviar(self, sinal: dict, entrada: dict) -> dict:
        try:
            info = self.emissor.enviar(sinal)
            entrada.update(status="enviado", duracao_ms=info.get("duracao_ms"))
        except (ErroEmissor, ValueError, KeyError) as e:
            entrada.update(status="erro", erro=str(e))
        with self.trava:
            self.s["contador"] = self.s.get("contador", len(self.s["historico"])) + 1
            entrada["n"] = self.s["contador"]
            self.s["historico"].append(entrada)
            if len(self.s["historico"]) > 800:
                del self.s["historico"][:-400]
        return entrada

    def passo(self) -> dict | None:
        """Envia o próximo candidato (usado pela thread e pelos testes)."""
        with self.trava:
            s = self._exigir()
            if s["estado"] != "executando":
                return None
            if s["cursor"] >= len(s["candidatos"]):
                s["estado"] = "concluido"
                self._gravar()
                self.notificar({"tipo": "concluido", "total": len(s["candidatos"])})
                return None
            if s["cursor"] - s["inicio_lote"] >= s["lote"]:
                s["estado"] = "lote_concluido"
                s["pausado_em"] = agora()
                self._gravar()
                self.notificar({"tipo": "lote", "testados": s["cursor"], "total": len(s["candidatos"])})
                return None
            idx = s["cursor"]
            c = s["candidatos"][idx]
            s["cursor"] += 1
        entrada = {"tipo": "teste", "candidato": idx, "posicao": idx + 1, "hora": agora()}
        entrada = self._enviar(self._sinal_candidato(c), entrada)
        with self.trava:
            self._gravar()
        self.notificar({"tipo": "teste", "n": entrada["n"], "posicao": idx + 1, "total": len(self.s["candidatos"]),
                        "status": entrada["status"], "marcas": c.get("marcas", []),
                        "funcao": c.get("funcao_provavel")})
        return entrada

    def _laco(self):
        while True:
            with self.trava:
                if not self.s or self.s["estado"] != "executando":
                    return
                intervalo = self.s["intervalo"]
            self.passo()
            if self.acordar.wait(intervalo):
                self.acordar.clear()
                with self.trava:
                    if not self.s or self.s["estado"] != "executando":
                        return

    def _iniciar_thread(self):
        self.acordar.clear()
        self.thread = threading.Thread(target=self._laco, name="descoberta", daemon=True)
        self.thread.start()

    def parar_thread(self):
        t = self.thread
        if t and t.is_alive():
            with self.trava:
                if self.s and self.s["estado"] == "executando":
                    self.s["estado"] = "pausado"
            self.acordar.set()
            t.join(timeout=15)
        self.thread = None

    def pausar(self, origem: str = "claude") -> dict:
        with self.trava:
            s = self._exigir()
            if s["estado"] == "executando":
                s["estado"] = "pausado"
                s["pausado_em"] = agora()
                s["motivo_pausa"] = f"pausado por {origem}"
            self._gravar()
        self.acordar.set()
        self.notificar({"tipo": "pausado", "origem": origem})
        return self.progresso(ultimos=4) | {"suspeitos": self.suspeitos()}

    def suspeitos(self) -> list[dict]:
        s = self._exigir()
        testes = [h for h in s["historico"] if h["tipo"] in ("teste", "reteste") and h.get("status") == "enviado"]
        if not testes:
            return []
        ref = s.get("pausado_em") or agora()
        janela = max(12.0, s["intervalo"] + 10.0)
        sel = [h for h in testes if 0 <= ref - h["hora"] <= janela]
        ultimo = testes[-1]
        if ultimo not in sel:
            sel.append(ultimo)
        if len(testes) > 1 and ref - ultimo["hora"] < 3.0 and testes[-2] not in sel:
            sel.append(testes[-2])
        sel = sorted(sel, key=lambda h: h["n"])[-4:]
        return [self._descr_hist(h, ref) for h in sel]

    def _descr_hist(self, h: dict, ref: float | None = None) -> dict:
        d = {"numero": h["n"], "tipo": h["tipo"], "hora": hora_legivel(h["hora"]), "status": h.get("status")}
        if ref:
            d["segundos_antes_da_pausa"] = round(ref - h["hora"], 1)
        if "candidato" in h:
            c = self.s["candidatos"][h["candidato"]]
            d["candidato"] = h["candidato"] + 1
            d["perfis"] = len(c.get("perfis", []))
            if c.get("marcas"):
                d["marcas"] = c["marcas"][:4]
            if c.get("funcao_provavel"):
                d["funcao_provavel"] = c["funcao_provavel"]
        if h.get("teste"):
            d["teste_distincao"] = h["teste"]
            d["variante"] = h.get("variante")
        if h.get("erro"):
            d["erro"] = h["erro"]
        return d

    def retomar(self, intervalo=None, a_partir_de=None, lote=None) -> dict:
        with self.trava:
            s = self._exigir()
            if intervalo:
                s["intervalo"] = max(2.0, min(float(intervalo), 60.0))
            if lote:
                s["lote"] = max(1, min(int(lote), 500))
            if a_partir_de:
                s["cursor"] = max(0, min(int(a_partir_de) - 1, len(s["candidatos"])))
            if s["cursor"] >= len(s["candidatos"]):
                return self.progresso() | {"aviso": "todos os candidatos já foram testados"}
            s["inicio_lote"] = s["cursor"]
            s["estado"] = "executando"
            s["pausado_em"] = None
            s["motivo_pausa"] = None
            self._gravar()
        self.parar_thread_se_morta()
        if not (self.thread and self.thread.is_alive()):
            self._iniciar_thread()
        return self.progresso(ultimos=0)

    def parar_thread_se_morta(self):
        if self.thread and not self.thread.is_alive():
            self.thread = None

    def ajustar_intervalo(self, intervalo: float) -> dict:
        with self.trava:
            s = self._exigir()
            s["intervalo"] = max(2.0, min(float(intervalo), 60.0))
            self._gravar()
        return {"intervalo": self.s["intervalo"]}

    def retestar(self, numeros: list[int], intervalo: float | None = None) -> dict:
        s = self._exigir()
        if s["estado"] == "executando":
            self.pausar("reteste")
        resultados = []
        espera = max(2.0, float(intervalo or 5.0))
        por_n = {h["n"]: h for h in s["historico"]}
        for i, n in enumerate(numeros):
            h = por_n.get(int(n))
            if not h:
                resultados.append({"numero": n, "erro": "esse número não está no histórico"})
                continue
            if "candidato" in h:
                sinal = self._sinal_candidato(s["candidatos"][h["candidato"]])
                entrada = {"tipo": "reteste", "candidato": h["candidato"], "repete": h["n"], "hora": agora()}
            else:
                sinal = h["sinal"]
                entrada = {"tipo": "reteste", "repete": h["n"], "hora": agora(), "teste": h.get("teste"),
                           "variante": h.get("variante"), "sinal": sinal, "perfis_variante": h.get("perfis_variante")}
            e = self._enviar(sinal, entrada)
            resultados.append({"numero_original": int(n), "novo_numero": e["n"], "status": e["status"],
                               "hora": hora_legivel(e["hora"]), **({"erro": e["erro"]} if e.get("erro") else {})})
            self.notificar({"tipo": "reteste", "n": e["n"], "repete": int(n)})
            if i < len(numeros) - 1:
                time.sleep(espera)
        with self.trava:
            self._gravar()
        return {"retestes": resultados,
                "orientacao": "Diga qual número fez o aparelho reagir; use confirmar com o número original ou o novo."}

    def confirmar(self, numero: int, funcionou: bool = True) -> dict:
        with self.trava:
            s = self._exigir()
            h = next((x for x in s["historico"] if x["n"] == int(numero)), None)
            if not h:
                raise ErroDescoberta(f"número {numero} não está no histórico")
            if s["estado"] == "executando":
                s["estado"] = "pausado"
                s["pausado_em"] = agora()
            if "candidato" in h:
                c = s["candidatos"][h["candidato"]]
                perfis = set(c.get("perfis", []))
                if funcionou:
                    s["confirmacoes"].append({"numero": h["n"], "candidato": h["candidato"], "hora": agora(),
                                              "sinal": self._sinal_candidato(c), "chaves": c.get("chaves", []),
                                              "funcao": c.get("funcao_provavel")})
                    if s["modo"] == "perfis":
                        s["perfis_ativos"] = sorted(perfis) if s["perfis_ativos"] is None else \
                            sorted(set(s["perfis_ativos"]) & perfis or perfis)
                    s["estado"] = "confirmado"
                else:
                    s["descartados"].append(h["candidato"])
            else:
                perfis = set(h.get("perfis_variante") or [])
                ativos = set(s["perfis_ativos"] or [])
                if funcionou:
                    s["confirmacoes"].append({"numero": h["n"], "teste": h.get("teste"), "hora": agora(),
                                              "sinal": h["sinal"], "chaves": [h.get("teste")]})
                    novo = ativos & perfis
                else:
                    novo = ativos - perfis
                s["perfis_ativos"] = sorted(novo or ativos)
                if not novo:
                    s.setdefault("avisos", []).append("o resultado contradiz as confirmações anteriores; mantive a lista.")
            self._gravar()
        self.acordar.set()
        return self.situacao()

    def situacao(self) -> dict:
        s = self._exigir()
        out = {"estado": s["estado"], "confirmacoes": [{"numero": c["numero"], "funcao": c.get("funcao"),
                                                        "chaves": c.get("chaves")} for c in s["confirmacoes"]]}
        ativos = s.get("perfis_ativos")
        if s["modo"] == "perfis" and ativos:
            out["perfis_possiveis"] = len(ativos)
            out["exemplos"] = self.cat.nomes_perfis(ativos, 10)
            if len(ativos) > 1:
                testes = self._calcular_distincao(ativos)
                with self.trava:
                    s["testes_distincao"] = testes
                    self._gravar()
                out["testes_distincao"] = [self._resumo_teste(t) for t in testes]
                out["orientacao"] = (
                    "Vários perfis usam esse mesmo sinal. Escolha um teste de distinção (de preferência com "
                    "efeito visível), envie cada variante com distinguir e diga qual reagiu; depois confirmar "
                    "com o número dessa variante. Também é possível salvar já o melhor perfil ou só a tecla que funcionou.")
            else:
                out["orientacao"] = "Perfil identificado. Use salvar_aparelho com o nome desejado."
        elif s["modo"] == "teclas":
            out["orientacao"] = "Use editar_aparelho → adicionar_comando com o número que funcionou e o nome da função."
        return out

    def _calcular_distincao(self, ativos: list[int]) -> list[dict]:
        s = self.s
        usadas = set()
        for c in s["confirmacoes"]:
            usadas |= set(c.get("chaves") or [])
        usadas |= set(s.get("filtros", {}).get("chaves_teste") or [])
        por_chave: dict[str, dict[int, set]] = {}
        for r in self.cat.comandos_dos_perfis(ativos):
            if r["base"] in usadas or r["base"].startswith("@") or (r["meta"] and '"risco": true' in r["meta"]):
                continue
            por_chave.setdefault(r["base"], {}).setdefault(r["sinal"], set()).add(r["perfil"])
        n = len(ativos)
        testes = []
        for chave, grupos in por_chave.items():
            presentes = set().union(*grupos.values())
            # um perfil pode ter variações da mesma tecla; conta o grupo principal de cada perfil
            tamanhos = [len(g) for g in grupos.values()]
            ausentes = n - len(presentes)
            fr = [t / n for t in tamanhos] + ([ausentes / n] if ausentes else [])
            impureza = 1 - sum(f * f for f in fr)
            if len(grupos) < 2 and not ausentes:
                continue
            termo = vocabulario.termo_por_chave(chave)
            valor = impureza * (1 + termo.teste / 5) * (len(presentes) / n)
            variantes = sorted(grupos.items(), key=lambda x: -len(x[1]))[:8]
            testes.append({"teste": chave, "rotulo": termo.rotulo, "valor": round(valor, 3),
                           "cobertura": len(presentes), "sem_a_tecla": ausentes,
                           "variantes": [{"variante": LETRAS[i], "sinal_id": sid, "perfis": sorted(ps)}
                                         for i, (sid, ps) in enumerate(variantes)]})
        testes.sort(key=lambda t: -t["valor"])
        return testes[:4]

    def _resumo_teste(self, t: dict) -> dict:
        return {"teste": t["teste"], "rotulo": t["rotulo"], "perfis_com_a_tecla": t["cobertura"],
                "variantes": [{"variante": v["variante"], "perfis": len(v["perfis"]),
                               "exemplos": [p["nome"] for p in self.cat.nomes_perfis(v["perfis"], 3)]}
                              for v in t["variantes"]]}

    def distinguir(self, teste: str, variante: str) -> dict:
        s = self._exigir()
        t = next((x for x in s.get("testes_distincao") or [] if x["teste"] == teste), None)
        if not t:
            raise ErroDescoberta("teste de distinção não encontrado; chame confirmar ou progresso para ver os testes")
        v = next((x for x in t["variantes"] if x["variante"] == str(variante).upper()), None)
        if not v:
            raise ErroDescoberta(f"variante {variante} não existe neste teste")
        sinal = self.cat.sinal(v["sinal_id"])
        entrada = {"tipo": "distincao", "teste": teste, "variante": v["variante"], "hora": agora(),
                   "sinal": sinal, "perfis_variante": v["perfis"]}
        e = self._enviar(sinal, entrada)
        with self.trava:
            self._gravar()
        self.notificar({"tipo": "distincao", "n": e["n"], "teste": t["rotulo"], "variante": v["variante"]})
        return {"numero": e["n"], "status": e["status"], "teste": t["rotulo"], "variante": v["variante"],
                "perfis_nesta_variante": len(v["perfis"]),
                "orientacao": f"Observe se “{t['rotulo']}” teve efeito. Depois confirmar(numero={e['n']}, "
                              f"funcionou=true/false)."}

    def progresso(self, ultimos: int = 8) -> dict:
        s = self._exigir()
        total = len(s["candidatos"])
        out = {"sessao": s["id"], "modo": s["modo"], "estado": s["estado"], "testados": s["cursor"],
               "total": total, "intervalo_s": s["intervalo"], "lote": s["lote"],
               "lote_atual": f"{s['cursor'] - s['inicio_lote']}/{s['lote']}",
               "filtros": {k: v for k, v in s["filtros"].items() if v}}
        if s.get("motivo_pausa"):
            out["motivo_pausa"] = s["motivo_pausa"]
        if s["cursor"] < total:
            out["proximo"] = self._descr_candidato(s["cursor"])
        if ultimos:
            out["historico"] = [self._descr_hist(h) for h in s["historico"][-ultimos:]]
        if s["estado"] == "lote_concluido":
            out["orientacao"] = (f"Lote concluído sem confirmação. Restam {total - s['cursor']} candidatos; use "
                                 "retomar para o próximo lote.")
        if s["estado"] == "concluido":
            out["orientacao"] = ("Todos os candidatos foram testados. Considere: outro comando de teste, sem filtro "
                                 "de marca, ampliar o catálogo, importar um perfil SmartIR/Flipper do modelo ou um "
                                 "sinal capturado.")
            out["resumo_testado"] = self.resumo_testado()
        if s.get("perfis_ativos"):
            out["perfis_possiveis"] = len(s["perfis_ativos"])
        return out

    def resumo_testado(self) -> dict:
        s = self._exigir()
        marcas: dict[str, int] = {}
        for c in s["candidatos"][: s["cursor"]]:
            for m in c.get("marcas", []):
                marcas[m] = marcas.get(m, 0) + 1
        return {"candidatos_testados": s["cursor"], "erros_envio": sum(1 for h in s["historico"] if h.get("status") == "erro"),
                "marcas_cobertas": dict(sorted(marcas.items(), key=lambda x: -x[1])[:25]),
                "comandos_de_teste": s["filtros"].get("chaves_teste")}

    def resultado_para_salvar(self) -> dict:
        s = self._exigir()
        if not s["confirmacoes"]:
            raise ErroDescoberta("nada confirmado ainda nesta busca")
        return {"perfis_ativos": s.get("perfis_ativos") or [], "confirmacoes": s["confirmacoes"], "modo": s["modo"],
                "sessao": s["id"], "filtros": s["filtros"]}

    def sinal_do_historico(self, numero: int) -> tuple[dict, dict]:
        s = self._exigir()
        h = next((x for x in s["historico"] if x["n"] == int(numero)), None)
        if not h:
            raise ErroDescoberta(f"número {numero} não está no histórico")
        if "candidato" in h:
            c = s["candidatos"][h["candidato"]]
            return self._sinal_candidato(c), c
        return h["sinal"], {"chaves": [h.get("teste")] if h.get("teste") else []}

    def painel(self) -> dict | None:
        if not self.s:
            return None
        s = self.s
        atual = s["historico"][-1] if s["historico"] else None
        return {"estado": s["estado"], "testados": s["cursor"], "total": len(s["candidatos"]),
                "intervalo": s["intervalo"], "lote": s["lote"], "inicio_lote": s["inicio_lote"],
                "atual": self._descr_hist(atual) if atual else None,
                "historico": [self._descr_hist(h) for h in s["historico"][-12:]][::-1],
                "perfis_possiveis": len(s["perfis_ativos"]) if s.get("perfis_ativos") else None}
