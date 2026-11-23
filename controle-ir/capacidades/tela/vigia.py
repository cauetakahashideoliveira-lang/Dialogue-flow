"""Vigias: missões de horas que rodam NO celular, sem o Claude no laço.

Um vigia repete um objetivo de LEITURA (cotação, preço, status de entrega, placar…) a cada N minutos: o executor de
objetivos (objetivo.py) abre o app, chega na tela e lê a resposta (com a visão nas páginas web). O vigia compara com a
leitura anterior e avisa no celular (notificação com som) quando a condição bate: mudou, abaixo de, acima de, contém,
variação de X%.

Regras de convivência e segurança:
- Só lê: o objetivo do vigia nunca recebe `permitir` (enviar, comprar, interruptores… ficam recusados).
- Não atropela o dono: no modo "livre" (padrão) só roda com a tela acesa na tela inicial (ou já no app do vigia) e
  volta para onde estava; com a tela apagada ou o dono usando outro app, adia 2 min. "sempre" roda por cima de
  qualquer app (e reabre o app anterior no fim).
- travar() / PARAR: o vigia pausa na hora e só volta com {nome, retomar:true}.
- Limites: até 10 vigias, intervalo de 5 min a 24 h, duração de até 72 h.
"""
from __future__ import annotations

import json
import os
import re
import threading
import time
import unicodedata

MIN_INTERVALO, MAX_INTERVALO, MAX_DURACAO_H, MAX_VIGIAS = 5, 1440, 72, 10
ADIAR_S, VOLTA_S, HISTORICO = 120, 20, 30
CAMPOS = ("nome", "objetivo", "app", "url", "pistas", "digitar", "pergunta", "concluido", "a_cada", "condicao",
          "duracao", "quando", "cerebro", "max_passos")


def norm(t):
    t = unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t).strip()


def numero(texto):
    """Número do texto, em pt-BR ou en: "R$ 5,99" → 5.99; "1.234,56" → 1234.56; "1,234.56" → 1234.56;
    "R$ 1.299" → 1299 (ponto com 3 casas = milhar, como no Brasil). Com "R$" no texto, vale o número dele:
    "1 dólar = R$ 5,99" → 5.99 (o 1º número seria o 1 do "1 dólar")."""
    texto = str(texto or "")
    m = re.search(r"R\$\s*(-?\d[\d.,]*)", texto)
    if m:
        return _converter(m.group(1))
    m = re.search(r"-?\d[\d.,]*", texto)
    return _converter(m.group()) if m else None


def _converter(bruto):
    s = bruto.rstrip(".,")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".") if s.count(",") == 1 else s.replace(",", "")
    elif s.count(".") > 1 or (s.count(".") == 1 and len(s.split(".")[1]) == 3):
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


def satisfaz(cond, valor, texto):
    """A leitura atende à condição de limite (abaixo/acima/contém)? None para condições relativas (muda/variação)."""
    if "abaixo" in cond:
        return valor is not None and valor < float(cond["abaixo"])
    if "acima" in cond:
        return valor is not None and valor > float(cond["acima"])
    if "contem" in cond:
        return norm(cond["contem"]) in norm(texto)
    return None


def disparou(cond, leitura, anterior, referencia=None):
    """(avisar?, motivo). Limites avisam ao CRUZAR (não a cada leitura enquanto continua abaixo); "muda" compara com
    a leitura anterior válida; "variacao" com a REFERÊNCIA (1ª leitura ou a do último aviso): três altas de 2% somam
    6% e avisam, em vez de nunca passar de 5% de uma leitura para a outra."""
    cond = cond or {"muda": True}
    texto, valor = leitura.get("resposta") or "", leitura.get("valor")
    lim = satisfaz(cond, valor, texto)
    if lim is not None:
        antes = satisfaz(cond, anterior.get("valor"), anterior.get("resposta") or "") if anterior else False
        if lim and not antes:
            if "abaixo" in cond:
                return True, f"{texto} (abaixo de {cond['abaixo']})"
            if "acima" in cond:
                return True, f"{texto} (acima de {cond['acima']})"
            return True, f"apareceu “{cond['contem']}”: {texto}"
        return False, None
    if not anterior:
        return False, None  # 1ª leitura: é a referência
    if "variacao" in cond:
        base = referencia or anterior
        a, v = base.get("valor"), valor
        if a and v is not None and abs(v - a) / abs(a) * 100 >= float(cond["variacao"]):
            return True, f"{base.get('resposta')} → {texto} ({(v - a) / abs(a) * 100:+.1f}%)"
        return False, None
    if valor is not None and anterior.get("valor") is not None:
        mudou = abs(valor - anterior["valor"]) > 1e-9
    else:
        mudou = norm(texto) != norm(anterior.get("resposta"))
    return (True, f"{anterior.get('resposta')} → {texto}") if mudou else (False, None)


def validar(cfg):
    if not isinstance(cfg, dict):
        return "vigia deve ser um objeto {nome, objetivo, a_cada, ...}"
    nome = cfg.get("nome")
    if not isinstance(nome, str) or not re.match(r"^[\w .-]{1,40}$", nome):
        return "nome: até 40 letras, números, espaço, ponto ou hífen"
    if cfg.get("parar") or cfg.get("retomar") or cfg.get("rodar"):
        return None
    if not isinstance(cfg.get("objetivo"), str) or not cfg["objetivo"].strip():
        return "objetivo: o que ler (ex.: 'ver a cotação do dólar no Google')"
    if cfg.get("permitir"):
        return "vigia só lê: permitir não é aceito"
    if cfg.get("url") is not None and not re.match(r"^https?://[^\s\"'<>]{3,500}$", str(cfg["url"])):
        return "url: endereço http(s)"
    try:
        a = float(cfg.get("a_cada", 30))
    except (TypeError, ValueError):
        return "a_cada: minutos (número)"
    if not MIN_INTERVALO <= a <= MAX_INTERVALO:
        return f"a_cada: de {MIN_INTERVALO} a {MAX_INTERVALO} minutos"
    try:
        d = float(cfg.get("duracao", 24))
    except (TypeError, ValueError):
        return "duracao: horas (número)"
    if not 0 < d <= MAX_DURACAO_H:
        return f"duracao: até {MAX_DURACAO_H} horas"
    c = cfg.get("condicao")
    if c is not None:
        if not isinstance(c, dict) or len(c) != 1 or next(iter(c)) not in ("muda", "abaixo", "acima", "contem",
                                                                            "variacao"):
            return "condicao: {muda:true} | {abaixo:N} | {acima:N} | {contem:'texto'} | {variacao:P (em %)}"
        k, v = next(iter(c.items()))
        if k in ("abaixo", "acima", "variacao"):
            try:
                float(v)
            except (TypeError, ValueError):
                return f"condicao.{k} deve ser número"
    if cfg.get("quando", "livre") not in ("livre", "sempre"):
        return "quando: livre (padrão: só com a tela inicial na frente) | sempre"
    return None


class Vigias:
    """rodar(cfg) → resultado do objetivo; livre(cfg) → (pode?, motivo, voltar_para); voltar(destino);
    avisar(titulo, texto, ident). O laço roda numa thread do serviço e se refaz a partir do arquivo."""

    def __init__(self, arq, rodar, livre, avisar, voltar=None, parar_arq=None, relogio=time.time, automatico=True):
        self.arq, self.rodar, self.livre, self.avisar = arq, rodar, livre, avisar
        self.automatico = automatico  # False nos testes: o laço é chamado à mão (passo)
        self.voltar = voltar or (lambda destino: None)
        self.parar_arq, self.relogio = parar_arq, relogio
        self.trava = threading.Lock()
        self.thread = None

    # ------------------------------------------------------------------ arquivo
    def _ler(self):
        try:
            with open(self.arq) as f:
                d = json.load(f)
            return d if isinstance(d, dict) else {}
        except (OSError, ValueError):
            return {}

    def _gravar(self, d):
        os.makedirs(os.path.dirname(self.arq) or ".", exist_ok=True)
        tmp = self.arq + ".tmp"
        with open(tmp, "w") as f:
            json.dump(d, f, ensure_ascii=False)
        os.replace(tmp, self.arq)

    def _travado(self):
        return bool(self.parar_arq) and os.path.exists(self.parar_arq)

    # ------------------------------------------------------------------ pedidos
    def criar(self, cfg):
        erro = validar(cfg)
        if erro:
            return {"erro": erro}
        nome = cfg["nome"]
        with self.trava:
            d = self._ler()
            if cfg.get("parar"):
                if d.pop(nome, None) is None:
                    return {"erro": f"vigia “{nome}” não existe", "vigias": sorted(d)}
                self._gravar(d)
                return {"parado": nome, "vigias": sorted(d)}
            if cfg.get("retomar"):
                if nome not in d:
                    return {"erro": f"vigia “{nome}” não existe"}
                if self._travado():
                    return {"erro": "o sistema está travado: destrave no celular antes de retomar"}
                d[nome].update(estado="ativo", proximo=self.relogio())
                self._gravar(d)
                self.garantir()
                return {"retomado": nome}
            if cfg.get("rodar"):
                if nome not in d:
                    return {"erro": f"vigia “{nome}” não existe"}
            else:
                if nome not in d and len(d) >= MAX_VIGIAS:
                    return {"erro": f"no máximo {MAX_VIGIAS} vigias: pare um antes"}
                agora = self.relogio()
                v = {k: cfg[k] for k in CAMPOS if cfg.get(k) is not None}
                v.update(a_cada=float(cfg.get("a_cada", 30)), duracao=float(cfg.get("duracao", 24)),
                         quando=cfg.get("quando", "livre"), condicao=cfg.get("condicao") or {"muda": True},
                         criado=agora, ate=agora + float(cfg.get("duracao", 24)) * 3600, proximo=agora,
                         estado="ativo", historico=[], falhas=0)
                d[nome] = v
                self._gravar(d)
        # 1ª leitura já (testa o ciclo inteiro e serve de referência), sem esperar o laço
        leitura = self.rodar_uma(nome, forcar=True) if cfg.get("rodar") or cfg.get("agora", True) else None
        self.garantir()
        out = {"vigia": self.descrever(nome)}
        if leitura is not None:
            out["leitura"] = leitura
        return out

    def listar(self):
        d = self._ler()
        return {"vigias": [self.descrever(n, d) for n in sorted(d)],
                "nota": "vigia={nome, objetivo, app, pistas, digitar, pergunta, a_cada (min), condicao, duracao (h), "
                        "quando} cria; {nome, parar:true} para; {nome, rodar:true} lê agora; {nome, retomar:true}"}

    def descrever(self, nome, d=None):
        v = (d or self._ler()).get(nome)
        if not v:
            return None
        h = v.get("historico") or []
        return {"nome": nome, "objetivo": v.get("objetivo"), "a_cada_min": v.get("a_cada"),
                "condicao": v.get("condicao"), "estado": v.get("estado"), "quando": v.get("quando"),
                "ate": time.strftime("%d/%m %H:%M", time.localtime(v.get("ate", 0))),
                "proxima": time.strftime("%H:%M", time.localtime(v.get("proximo", 0))),
                "ultima": h[-1] if h else None, "leituras": len(h), "avisos": v.get("avisos", 0)}

    # ------------------------------------------------------------------ execução
    def rodar_uma(self, nome, forcar=False):
        """Uma leitura: tela livre? → objetivo → número → condição → aviso. Devolve a leitura (ou o adiamento)."""
        with self.trava:
            v = self._ler().get(nome)
        if not v:
            return {"erro": f"vigia “{nome}” não existe"}
        if self._travado():
            self._atualizar(nome, estado="pausado (travar)")
            return {"adiado": "sistema travado"}
        # forcar: pedido feito agora pelo dono (criar/rodar) — roda mesmo com ele em outro app e volta para lá
        pode, motivo, destino = self.livre(dict(v, quando="sempre", agora=True) if forcar else v)
        if not pode:
            self._atualizar(nome, proximo=self.relogio() + ADIAR_S, adiado=motivo)
            return {"adiado": motivo, "proxima_tentativa_s": ADIAR_S}
        t0 = self.relogio()
        try:
            r = self.rodar(v) or {}
        except Exception as e:  # noqa: BLE001 — um erro não derruba o laço
            r = {"erro": str(e)[:160]}
        finally:
            try:
                self.voltar(destino)
            except Exception:  # noqa: BLE001
                pass
        resp = r.get("resposta")
        if resp in (None, "") and r.get("estado") == "concluido" and (r.get("tela") or {}).get("textos"):
            resp = " | ".join(r["tela"]["textos"][:3])
        leitura = {"quando": time.strftime("%d/%m %H:%M", time.localtime(t0)), "s": round(self.relogio() - t0, 1)}
        if r.get("estado") == "concluido" and resp not in (None, ""):
            v_ = r.get("valor")  # o número que o modelo separou da resposta vale mais que o lido do texto
            leitura.update(resposta=str(resp)[:200], valor=float(v_) if isinstance(v_, (int, float))
                           and not isinstance(v_, bool) else numero(resp))
        else:
            leitura["falha"] = r.get("erro") or r.get("motivo") or r.get("estado") or "sem leitura"
        aviso = None
        with self.trava:
            d = self._ler()
            v = d.get(nome)
            if not v:
                return leitura
            hist = v.setdefault("historico", [])
            anterior = next((x for x in reversed(hist) if "resposta" in x), None)
            if "resposta" in leitura:
                v["falhas"] = 0
                ok, motivo_ = disparou(v.get("condicao"), leitura, anterior, v.get("referencia"))
                if ok:
                    aviso = motivo_
                    leitura["aviso"] = True
                    v["avisos"] = v.get("avisos", 0) + 1
                if ok or not v.get("referencia"):
                    v["referencia"] = {"resposta": leitura["resposta"], "valor": leitura.get("valor")}
            else:
                v["falhas"] = v.get("falhas", 0) + 1
                if v["falhas"] == 3:
                    aviso = f"não consegui ler 3 vezes seguidas ({leitura['falha']})"
            hist.append(leitura)
            del hist[:-HISTORICO]
            v["proximo"] = self.relogio() + float(v.get("a_cada", 30)) * 60
            v.pop("adiado", None)
            if self.relogio() >= v.get("ate", 0):
                v["estado"] = "encerrado"
            d[nome] = v
            self._gravar(d)
        if aviso:
            try:
                self.avisar(f"Vigia: {nome}", aviso, nome)
            except Exception:  # noqa: BLE001
                pass
        return leitura

    def _atualizar(self, nome, **campos):
        with self.trava:
            d = self._ler()
            if nome in d:
                d[nome].update(campos)
                self._gravar(d)

    def vencidos(self):
        agora = self.relogio()
        return [n for n, v in self._ler().items() if v.get("estado") == "ativo" and v.get("proximo", 0) <= agora]

    def passo(self):
        """Uma volta do laço: encerra os vencidos, roda os que estão na hora. False quando não há mais o que vigiar."""
        if self._travado():
            for n, v in self._ler().items():
                if v.get("estado") == "ativo":
                    self._atualizar(n, estado="pausado (travar)")
            return False
        for n, v in self._ler().items():
            if v.get("estado") == "ativo" and self.relogio() >= v.get("ate", 0):
                self._atualizar(n, estado="encerrado")
                try:
                    self.avisar(f"Vigia: {n}", "terminou o prazo de vigilância", n)
                except Exception:  # noqa: BLE001
                    pass
        for n in self.vencidos():
            self.rodar_uma(n)
        return any(v.get("estado") == "ativo" for v in self._ler().values())

    def garantir(self):
        """Liga o laço se houver vigia ativo (chamado a cada uso da tela e no início do serviço)."""
        if not self.automatico:
            return False
        if self.thread and self.thread.is_alive():
            return True
        if not any(v.get("estado") == "ativo" for v in self._ler().values()):
            return False

        def laco():
            while True:
                try:
                    if not self.passo():
                        return
                except Exception:  # noqa: BLE001
                    pass
                time.sleep(VOLTA_S)
        self.thread = threading.Thread(target=laco, name="vigias", daemon=True)
        self.thread.start()
        return True
