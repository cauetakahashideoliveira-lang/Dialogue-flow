"""Planejamento e execução de pedidos (simples ou compostos).

O planejador consulta as capacidades antes de enviar qualquer sinal:

* usa uma tecla direta quando existe (``HDMI 2``, ``velocidade 2``);
* chega a um valor por passos quando há informação suficiente (estado
  conhecido, ou faixa não cíclica conhecida — saturando no mínimo);
* recusa ``alternar`` sem estado conhecido, a menos que o usuário aceite;
* em perfis de estado completo, monta a configuração inteira preservando o
  que não foi pedido a partir do último envio.

A execução para na primeira falha e informa o que já foi enviado, para que
nada seja duplicado (volume, avanço, alternância de energia).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from . import vocabulario
from .aparelhos import BINARIOS, agora, capacidades, hora_legivel
from .emissor import ErroEmissor
from .vocabulario import normalizar, normalizar_valor, valores_equivalentes

LIMITE_ETAPAS = 40
ORDEM_PARAMETROS = ["energia", "entrada", "modo", "velocidade", "temperatura", "ventilacao", "cor", "brilho",
                    "oscilacao", "mudo", "canal", "volume"]


@dataclass
class Etapa:
    chave: str
    rotulo: str
    sinal: dict
    efeitos: dict = field(default_factory=dict)  # parametro -> (valor, certeza)
    espera: float = 0.0
    motivo: str = ""

    def descricao(self) -> dict:
        d = {"comando": self.chave, "rotulo": self.rotulo}
        if self.motivo:
            d["motivo"] = self.motivo
        return d


@dataclass
class Plano:
    etapas: list[Etapa] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    bloqueios: list[str] = field(default_factory=list)
    erros: list[str] = field(default_factory=list)
    nao_suportado: list[str] = field(default_factory=list)
    estado_completo: dict | None = None


class Controlador:
    def __init__(self, aparelho: dict):
        self.ap = aparelho
        self.perfil = aparelho["perfil"]
        self.cap = capacidades(self.perfil, aparelho.get("faixas"), incluir_risco=True)
        self.cmds = {c["chave"]: c for c in self.perfil.get("comandos", [])}
        self.cfg = aparelho.get("config", {})

    # ------------------------------------------------------------ estado
    def conhecido(self, param: str, pedido_estado: dict) -> tuple[object, str] | None:
        if param in pedido_estado:
            return normalizar_valor(pedido_estado[param]), "informado agora por você"
        est = self.ap.get("estado", {})
        orig = est.get("controle_original_em") or 0
        conf = est.get("confirmado", {}).get(param)
        env = est.get("ultimo_envio", {}).get(param)
        candidatos = []
        if conf and conf.get("hora", 0) >= orig:
            candidatos.append((conf.get("hora", 0), conf["valor"], "confirmado por você em " + hora_legivel(conf["hora"])))
        if env and env.get("hora", 0) >= orig and env.get("certeza") in ("absoluto", "derivado"):
            candidatos.append((env.get("hora", 0), env["valor"], "presumido pelo último envio em " + hora_legivel(env["hora"])))
        if not candidatos:
            return None
        candidatos.sort(key=lambda x: -x[0])
        return candidatos[0][1], candidatos[0][2]

    def _etapa(self, chave: str, efeitos=None, motivo="") -> Etapa:
        c = self.cmds[chave]
        return Etapa(chave, c.get("rotulo") or chave, c["sinal"], efeitos or {}, self.cfg.get("intervalo_teclas", 0.45),
                     motivo)

    def _resolver_tecla(self, nome: str) -> str | None:
        if nome in self.cmds:
            return nome
        n = normalizar(nome)
        for c in self.cmds.values():
            if n in (normalizar(c.get("rotulo") or ""), normalizar(c.get("nome_original") or ""),
                     normalizar(c["chave"])):
                return c["chave"]
        t = vocabulario.interpretar(nome)
        if t.chave in self.cmds:
            return t.chave
        parecidos = [c["chave"] for c in self.cmds.values() if n and n in normalizar(c.get("rotulo") or "")]
        return parecidos[0] if len(parecidos) == 1 else None

    # ------------------------------------------------------------ planejamento
    def planejar(self, pedido: dict) -> Plano:
        plano = Plano()
        definir = {k: v for k, v in (pedido.get("definir") or {}).items() if v is not None}
        ajustar = dict(pedido.get("ajustar") or {})
        estado_pedido = {k: v for k, v in (pedido.get("estado_atual") or {}).items()}
        permitir = bool(pedido.get("permitir_alternancia"))
        if pedido.get("ligar") is not None:
            definir["energia"] = "ligado" if pedido["ligar"] else "desligado"
        definir = {normalizar(k).replace(" ", "_"): v for k, v in definir.items()}
        ajustar = {normalizar(k).replace(" ", "_"): v for k, v in ajustar.items()}
        sinonimos_param = {"temp": "temperatura", "ventilador": "ventilacao", "fan": "ventilacao",
                           "swing": "oscilacao", "fonte": "entrada", "input": "entrada", "power": "energia",
                           "ligado": "energia", "vel": "velocidade"}
        definir = {sinonimos_param.get(k, k): v for k, v in definir.items()}
        ajustar = {sinonimos_param.get(k, k): v for k, v in ajustar.items()}

        ec = self.perfil.get("estado_completo")
        if ec:
            self._planejar_estado(ec, definir, ajustar, plano)

        energia_final = None
        if "energia" in definir:
            alvo = normalizar_valor(definir.pop("energia"))
            if alvo not in ("ligado", "desligado"):
                plano.erros.append(f"energia aceita ligado ou desligado (recebi “{alvo}”)")
            elif alvo == "ligado":
                self._definir("energia", alvo, plano, estado_pedido, permitir, espera_ligar=True)
            else:
                energia_final = alvo
        for par in sorted(definir, key=lambda x: ORDEM_PARAMETROS.index(x) if x in ORDEM_PARAMETROS else 99):
            self._definir(par, definir[par], plano, estado_pedido, permitir)
        for par, n in ajustar.items():
            try:
                n = int(n)
            except (TypeError, ValueError):
                plano.erros.append(f"ajuste de {par} precisa ser um número inteiro de passos")
                continue
            self._ajustar(par, n, plano)
        for t in pedido.get("teclas") or []:
            nome, vezes = (t.get("comando") or t.get("nome"), int(t.get("vezes", 1))) if isinstance(t, dict) else (t, 1)
            chave = self._resolver_tecla(str(nome))
            if not chave:
                plano.erros.append(f"o aparelho não tem a tecla “{nome}”. Consulte opcoes para ver as teclas.")
                continue
            c = self.cmds[chave]
            if c.get("risco") and not pedido.get("permitir_servico"):
                plano.erros.append(f"“{c.get('rotulo')}” parece um comando de serviço/restauração. "
                                   "Repita com permitir_servico=true se tiver certeza.")
                continue
            for _ in range(max(1, min(vezes, LIMITE_ETAPAS))):
                plano.etapas.append(self._etapa(chave, self._efeitos_cmd(c, estado_pedido)))
        if energia_final:
            self._definir("energia", energia_final, plano, estado_pedido, permitir)
        if len(plano.etapas) > LIMITE_ETAPAS:
            plano.erros.append(f"o pedido geraria {len(plano.etapas)} transmissões (limite {LIMITE_ETAPAS}).")
        if not plano.etapas and not plano.erros and not plano.bloqueios and not plano.nao_suportado \
                and not plano.avisos:
            plano.erros.append("nenhuma ação pedida. Informe ligar, definir, ajustar, teclas ou macro.")
        return plano

    def _efeitos_cmd(self, c: dict, estado_pedido: dict) -> dict:
        tipo = c.get("tipo")
        if tipo == "definir":
            return {k: (str(v), "absoluto") for k, v in (c.get("efeitos") or {}).items()}
        if tipo == "alternar" and c.get("parametro"):
            atual = self.conhecido(c["parametro"], estado_pedido)
            if atual and atual[0] in ("ligado", "desligado"):
                return {c["parametro"]: ("desligado" if atual[0] == "ligado" else "ligado", "derivado")}
            return {c["parametro"]: ("alternado", "desconhecido")}
        return {}

    def _definir(self, par: str, valor, plano: Plano, estado_pedido: dict, permitir: bool, espera_ligar=False):
        ec = self.perfil.get("estado_completo") or {}
        if par in (ec.get("parametros") or {}) and par != "energia":
            return  # tratado em _planejar_estado
        d = self.cap["parametros"].get(par)
        if not d:
            plano.nao_suportado.append(self._sem_suporte(par))
            return
        alvo = normalizar_valor(valor)
        espera = self.cfg.get("espera_apos_ligar", 1.2) if espera_ligar else None
        # 1) tecla direta
        if "direto" in d:
            eq = valores_equivalentes(alvo, list(d["direto"]))
            if eq:
                chave = sorted(d["direto"][eq[0]], key=lambda k: len(self.cmds[k].get("efeitos") or {}))[0]
                e = self._etapa(chave, {par: (eq[0], "absoluto")}, "tecla direta")
                if espera:
                    e.espera = espera
                plano.etapas.append(e)
                return
        # 2) binário por alternância
        if par in BINARIOS and alvo in ("ligado", "desligado") and "alternar" in d:
            chave = d["alternar"][0]
            atual = self.conhecido(par, estado_pedido)
            rot = self.cmds[chave].get("rotulo")
            if atual and atual[0] in ("ligado", "desligado"):
                if atual[0] == alvo:
                    plano.avisos.append(f"{par} já está {alvo} ({atual[1]}); não enviei “{rot}” para não inverter.")
                    return
                e = self._etapa(chave, {par: (alvo, "derivado")}, f"alternância; estado anterior {atual[0]} ({atual[1]})")
                if espera:
                    e.espera = espera
                plano.etapas.append(e)
                return
            if permitir:
                e = self._etapa(chave, {par: ("alternado", "desconhecido")}, "alternância autorizada sem estado conhecido")
                if espera:
                    e.espera = espera
                plano.etapas.append(e)
                plano.avisos.append(f"“{rot}” só alterna: sem saber o estado atual, o resultado pode ser o oposto do pedido.")
                return
            plano.bloqueios.append(
                f"Este controle só tem “{rot}”, que alterna {par}. Não sei se o aparelho está ligado ou desligado "
                f"agora, então não consigo garantir “{alvo}”. Diga o estado atual (estado_atual) ou autorize "
                f"enviar mesmo assim (permitir_alternancia=true).")
            return
        valores = d.get("valores") or []
        faixa = (self.ap.get("faixas") or {}).get(par) or d.get("faixa")
        # 3) por passos relativos ou ciclo, com faixa conhecida
        ordem = None
        if faixa and "valores" in faixa:
            ordem = [str(v) for v in faixa["valores"]]
        elif faixa and "min" in faixa and "max" in faixa:
            ordem = [str(v) for v in range(int(faixa["min"]), int(faixa["max"]) + 1)]
        if ordem and ("mais" in d or "menos" in d or "ciclo" in d):
            eq = valores_equivalentes(alvo, ordem)
            if not eq:
                plano.erros.append(f"{par} aceita {', '.join(ordem)} (recebi “{valor}”)")
                return
            alvo_v = eq[0]
            i_alvo = ordem.index(alvo_v)
            atual = self.conhecido(par, estado_pedido)
            i_atual = ordem.index(str(atual[0])) if atual and str(atual[0]) in ordem else None
            ciclico = bool(faixa.get("ciclico"))
            if i_atual is not None:
                if i_atual == i_alvo:
                    plano.avisos.append(f"{par} já está em {alvo_v} ({atual[1]}).")
                    return
                if "mais" in d and (i_alvo > i_atual or ("menos" not in d and ciclico)):
                    passos = (i_alvo - i_atual) % len(ordem) if ciclico else i_alvo - i_atual
                    self._passos(d["mais"][0], passos, par, ordem, i_atual, +1, plano, ciclico)
                elif "menos" in d and i_alvo < i_atual:
                    self._passos(d["menos"][0], i_atual - i_alvo, par, ordem, i_atual, -1, plano, ciclico)
                elif "ciclo" in d:
                    passos = (i_alvo - i_atual) % len(ordem)
                    self._passos(d["ciclo"][0], passos, par, ordem, i_atual, +1, plano, True)
                else:
                    plano.erros.append(f"não há tecla para levar {par} de {ordem[i_atual]} a {alvo_v}.")
                return
            if not ciclico and "menos" in d and "mais" in d:
                # satura no mínimo e sobe: funciona sem saber o valor atual
                self._passos(d["menos"][0], len(ordem) - 1, par, ordem, None, -1, plano, False,
                             motivo="descendo até o mínimo (estado atual desconhecido)")
                if i_alvo:
                    self._passos(d["mais"][0], i_alvo, par, ordem, 0, +1, plano, False)
                return
            plano.bloqueios.append(
                f"Para chegar a {par} {alvo_v} só existe tecla de próximo/relativo e não sei o valor atual. "
                f"Diga o valor atual (estado_atual) para eu calcular os passos.")
            return
        if par == "canal" and d.get("digitos") and str(alvo).isdigit():
            for dig in str(alvo):
                plano.etapas.append(self._etapa(f"numero_{dig}", motivo=f"canal {alvo}"))
            if "ok" in self.cmds:
                plano.etapas.append(self._etapa("ok", {"canal": (str(alvo), "absoluto")}))
            else:
                plano.etapas[-1].efeitos = {"canal": (str(alvo), "absoluto")}
            return
        if "mais" in d or "menos" in d or "ciclo" in d:
            plano.bloqueios.append(
                f"O controle só muda {par} por passos ({', '.join(k for k in ('mais', 'menos', 'ciclo') if k in d)}) "
                f"e não conheço a quantidade de níveis. Diga quantos níveis existem (editar_aparelho com faixas) "
                f"ou use ajustar com o número de passos.")
            return
        opcoes = ", ".join(valores) if valores else "nenhum valor direto"
        plano.erros.append(f"{par} = “{valor}” não está disponível neste perfil (opções: {opcoes}).")

    def _passos(self, chave, n, par, ordem, i_ini, sentido, plano, ciclico, motivo=""):
        i = i_ini
        for k in range(n):
            efe = {}
            if i is not None:
                i = (i + sentido) % len(ordem) if ciclico else max(0, min(len(ordem) - 1, i + sentido))
                efe = {par: (ordem[i], "derivado")}
            plano.etapas.append(self._etapa(chave, efe, motivo if k == 0 else ""))

    def _ajustar(self, par: str, n: int, plano: Plano):
        ec = self.perfil.get("estado_completo") or {}
        if par in (ec.get("parametros") or {}):
            return
        d = self.cap["parametros"].get(par)
        if not d or not any(k in d for k in ("mais", "menos", "ciclo")):
            plano.nao_suportado.append(self._sem_suporte(par, relativo=True))
            return
        if n == 0:
            return
        if n > 0 and "mais" in d:
            chave = d["mais"][0]
        elif n < 0 and "menos" in d:
            chave = d["menos"][0]
        elif n > 0 and "ciclo" in d:
            chave = d["ciclo"][0]
        else:
            plano.erros.append(f"não há tecla para {'aumentar' if n > 0 else 'diminuir'} {par}.")
            return
        for _ in range(min(abs(n), LIMITE_ETAPAS)):
            plano.etapas.append(self._etapa(chave, {par: (f"{'+' if n > 0 else '-'}1", "relativo")}))

    def _sem_suporte(self, par: str, relativo=False) -> str:
        disp = sorted(set(self.cap["parametros"]) | set((self.cap.get("estado_completo") or {}).get("parametros", {})))
        nome = vocabulario.PARAMETROS.get(par, par).split(" (")[0].lower()
        return (f"O perfil deste aparelho não oferece {nome}{' (ajuste relativo)' if relativo else ''}. "
                f"Recursos disponíveis: {', '.join(disp) or 'apenas teclas avulsas'}. "
                f"Nada foi enviado para {par}.")

    def _planejar_estado(self, ec: dict, definir: dict, ajustar: dict, plano: Plano):
        params = ec.get("parametros", {})
        pedidos = {k: definir.pop(k) for k in list(definir) if k in params}
        ajustes = {k: ajustar.pop(k) for k in list(ajustar) if k in params}
        energia = definir.get("energia")
        if energia is not None and normalizar_valor(energia) == "desligado":
            definir.pop("energia")
            sinal = ec.get("desligar")
            if not sinal:
                plano.erros.append("este perfil não tem o código de desligar.")
                return
            plano.etapas.append(Etapa("desligar", "Desligar", sinal, {"energia": ("desligado", "absoluto")}))
            if pedidos or ajustes:
                plano.avisos.append("o aparelho será desligado; os demais valores pedidos foram ignorados.")
            return
        ligar = energia is not None and normalizar_valor(energia) == "ligado"
        if not (pedidos or ajustes or ligar):
            return
        definir.pop("energia", None)
        estados = ec.get("estados", [])
        ultimo = (self.ap.get("estado") or {}).get("estado_completo") or {}
        alvo: dict = {}
        origem: dict = {}
        for par, spec in params.items():
            if par in pedidos:
                continue
            if par in ultimo:
                alvo[par] = ultimo[par]
                origem[par] = "mantido do último envio"
        erros_antes = len(plano.erros)
        for par, val in pedidos.items():
            spec = params[par]
            if par == "temperatura":
                try:
                    t = float(str(val).replace(",", ".").replace("°", "").replace("c", "").strip())
                except ValueError:
                    plano.erros.append(f"temperatura inválida: {val}")
                    continue
                vals = sorted({e["temperatura"] for e in estados})
                if not any(abs(t - v) < 1e-6 for v in vals):
                    plano.erros.append(f"temperatura {val} °C não existe no perfil (faixa {vals[0]}–{vals[-1]} °C).")
                    continue
                alvo[par] = int(t) if float(t).is_integer() else t
            else:
                aceitos = spec if isinstance(spec, list) else []
                eq = valores_equivalentes(val, aceitos)
                if not eq:
                    plano.erros.append(f"{par} aceita: {', '.join(map(str, aceitos))} (recebi “{val}”).")
                    continue
                alvo[par] = eq[0]
            origem[par] = "pedido agora"
        for par, n in ajustes.items():
            if par != "temperatura":
                plano.erros.append(f"ajuste relativo só vale para temperatura neste perfil; use definir para {par}.")
                continue
            base = alvo.get("temperatura")
            if base is None:
                plano.bloqueios.append("Não sei a temperatura atual para somar/subtrair; diga a temperatura desejada.")
                continue
            passo = (params["temperatura"] or {}).get("passo", 1) or 1
            alvo["temperatura"] = base + int(n) * passo
            origem["temperatura"] = f"{base} {'+' if int(n) >= 0 else '−'} {abs(int(n)) * passo}"
        if len(plano.erros) > erros_antes:
            return
        # completa o que faltar com valores típicos
        for par in params:
            if par not in alvo:
                compat = [e for e in estados if all(e.get(k) == v for k, v in alvo.items() if k in e)]
                base = compat or estados
                if par == "temperatura":
                    vals = sorted({e["temperatura"] for e in base if "temperatura" in e})
                    if vals:
                        alvo[par] = min(vals, key=lambda v: abs(v - 24))
                else:
                    prefer = {"modo": ["frio"], "ventilacao": ["automatica", "baixa"],
                              "oscilacao": ["desligada", "ligada"]}.get(par, [])
                    vals = [e.get(par) for e in base if e.get(par) is not None]
                    escolha = next((p for p in prefer if p in vals), vals[0] if vals else None)
                    if escolha is not None:
                        alvo[par] = escolha
                if par in alvo:
                    origem[par] = "valor padrão (sem envio anterior)"
        exato = [e for e in estados if all(e.get(k) == v for k, v in alvo.items() if k in e)]
        if not exato:
            mesmos_modo = [e for e in estados if e.get("modo") == alvo.get("modo")]
            dica = ""
            if mesmos_modo:
                vents = sorted({str(e.get("ventilacao")) for e in mesmos_modo})
                temps = sorted({e.get("temperatura") for e in mesmos_modo})
                dica = (f" No modo {alvo.get('modo')} existem ventilação {', '.join(vents)} e "
                        f"temperaturas {temps[0]}–{temps[-1]} °C.")
            plano.erros.append(f"a combinação {self._fmt(alvo)} não existe neste perfil.{dica}")
            return
        e = exato[0]
        efeitos = {k: (str(v), "absoluto") for k, v in alvo.items()}
        efeitos["energia"] = ("ligado", "absoluto")
        plano.etapas.append(Etapa("estado_completo", f"Configuração: {self._fmt(alvo)}", e["sinal"], efeitos,
                                  self.cfg.get("intervalo_teclas", 0.45)))
        plano.estado_completo = {"valores": alvo, "origem": origem}

    @staticmethod
    def _fmt(alvo: dict) -> str:
        partes = []
        for k in ("modo", "temperatura", "ventilacao", "oscilacao"):
            if k in alvo:
                partes.append(f"{alvo[k]} °C" if k == "temperatura" else f"{k} {alvo[k]}")
        return ", ".join(partes)


def executar(aparelho: dict, plano: Plano, emissor, simular: bool = False) -> dict:
    res = {"aparelho": aparelho["nome"], "avisos": plano.avisos, "nao_suportado": plano.nao_suportado}
    if plano.estado_completo:
        res["configuracao"] = plano.estado_completo
    if plano.erros:
        res.update(status="nada_enviado", erros=plano.erros, plano=[e.descricao() for e in plano.etapas])
        return res
    if plano.bloqueios:
        res.update(status="precisa_confirmacao", explicacao=plano.bloqueios,
                   plano=[e.descricao() for e in plano.etapas])
        return res
    if not plano.etapas:
        res["status"] = "nada_enviado"
        return res
    if simular:
        res.update(status="simulado", plano=[e.descricao() for e in plano.etapas])
        return res
    enviados, pendentes = [], []
    falha = None
    estado = aparelho.setdefault("estado", {"ultimo_envio": {}, "confirmado": {}})
    for i, e in enumerate(plano.etapas):
        try:
            emissor.enviar(e.sinal)
        except (ErroEmissor, ValueError) as ex:
            falha = {"etapa": i + 1, "comando": e.chave, "rotulo": e.rotulo, "erro": str(ex)}
            pendentes = [x.descricao() for x in plano.etapas[i:]]
            break
        t = agora()
        enviados.append(dict(e.descricao(), ordem=i + 1, hora=hora_legivel(t)))
        for par, (val, certeza) in e.efeitos.items():
            estado.setdefault("ultimo_envio", {})[par] = {"valor": val, "certeza": certeza, "hora": t,
                                                          "comando": e.chave}
        if e.chave == "estado_completo" and plano.estado_completo:
            estado["estado_completo"] = dict(plano.estado_completo["valores"])
        if i < len(plano.etapas) - 1:
            time.sleep(max(e.espera, 0.0))
    hist = aparelho.setdefault("historico", [])
    hist.append({"hora": agora(), "enviados": [x["comando"] for x in enviados], "falha": falha})
    del hist[:-30]
    res["enviados"] = enviados
    if falha:
        res.update(status="parcial" if enviados else "falhou", falha=falha, pendentes=pendentes,
                   orientacao="As etapas em 'enviados' já saíram; não as repita. Corrija o problema e reenvie só "
                              "as 'pendentes'.")
    else:
        res["status"] = "sinal_enviado"
        res["observacao"] = ("A API confirmou a transmissão. Só você pode confirmar se o aparelho reagiu; "
                             "use registrar_estado se o resultado for diferente.")
    res["estado_presumido"] = {k: v["valor"] for k, v in estado.get("ultimo_envio", {}).items()}
    return res
