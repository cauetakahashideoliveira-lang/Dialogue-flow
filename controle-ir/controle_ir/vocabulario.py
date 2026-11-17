"""Vocabulário canônico: nomes de teclas, parâmetros e categorias.

Qualquer nome de tecla (``Vol_up``, ``VOL+``, ``HDMI 2``, ``Speed_3``,
``Oscillate``, ``Red``...) é convertido em um *termo* com chave estável,
rótulo em português, tipo e efeito sobre o estado do aparelho:

* ``tecla``    — ação sem estado (play, menu, disparo da câmera);
* ``alternar`` — inverte um parâmetro binário (liga/desliga único, mudo);
* ``definir``  — leva parâmetros a valores absolutos (ligar, HDMI 2, azul);
* ``ajustar``  — passo relativo (+1/−1) ou ciclo (próxima velocidade).

Nomes desconhecidos viram comandos personalizados ``x_<nome>`` do tipo
``tecla`` — nada no núcleo precisa mudar para aceitar um controle novo.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


def sem_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(texto)) if not unicodedata.combining(c))


def normalizar(texto: str) -> str:
    t = re.sub(r"([a-z])([A-Z])", r"\1 \2", sem_acentos(texto)).lower()  # volumeUp → volume up
    t = t.replace("+", " mais ").replace("＋", " mais ")
    t = re.sub(r"(?<=[a-z0-9])-(?=\s|$)", " menos ", t)  # "vol-" → "vol menos"
    t = re.sub(r"^-(?=\s|$)", " menos ", t)
    t = re.sub(r"([a-z])(\d)", r"\1 \2", t)  # hdmi2 → hdmi 2
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return " ".join(t.split())


def slug(texto: str) -> str:
    return normalizar(texto).replace(" ", "_") or "sem_nome"


@dataclass(frozen=True)
class Termo:
    chave: str
    rotulo: str
    tipo: str = "tecla"                 # tecla | alternar | definir | ajustar
    parametro: str | None = None        # alternar/ajustar
    passo: int = 0                      # ajustar: +1/−1; 0 = ciclo (próximo)
    efeitos: tuple = ()                 # definir: ((parametro, valor), ...)
    teste: int = 0                      # 0 = não usar em testes automáticos; maior = melhor
    risco: bool = False                 # serviço, restauração, programação

    def efeitos_dict(self) -> dict:
        return dict(self.efeitos)

    def para_dict(self) -> dict:
        d = {"chave": self.chave, "rotulo": self.rotulo, "tipo": self.tipo}
        if self.parametro:
            d["parametro"] = self.parametro
        if self.tipo == "ajustar":
            d["passo"] = self.passo if self.passo else "ciclo"
        if self.efeitos:
            d["efeitos"] = self.efeitos_dict()
        if self.risco:
            d["risco"] = True
        return d


# ------------------------------------------------------------------ parâmetros
PARAMETROS = {
    "energia": "Energia (ligado/desligado)",
    "volume": "Volume (relativo)",
    "mudo": "Mudo",
    "canal": "Canal",
    "entrada": "Entrada / fonte",
    "velocidade": "Velocidade",
    "oscilacao": "Oscilação",
    "cor": "Cor",
    "brilho": "Brilho",
    "temperatura": "Temperatura",
    "temperatura_cor": "Temperatura de cor da luz",
    "modo": "Modo",
    "ventilacao": "Ventilação",
    "temporizador": "Temporizador",
    "zoom": "Zoom",
    "foco": "Foco",
}

CORES = {
    "vermelho": ("red", "r", "vermelho", "vermelha"),
    "verde": ("green", "g", "verde"),
    "azul": ("blue", "b", "azul"),
    "branco": ("white", "w", "branco", "branca"),
    "amarelo": ("yellow", "amarelo", "amarela"),
    "laranja": ("orange", "laranja"),
    "ciano": ("cyan", "ciano", "aqua", "turquoise", "turquesa"),
    "roxo": ("purple", "roxo", "roxa", "violet", "violeta"),
    "rosa": ("pink", "rosa"),
    "magenta": ("magenta",),
    "quente": ("warm", "warm white", "quente", "amarelada"),
    "fria": ("cool white", "cold white", "fria"),
}

_VAL_LIGADO = {"ligado", "ligar", "liga", "on", "sim", "true", "1", "ativo", "ativar", "ativada", "ativado", "ligada"}
_VAL_DESLIGADO = {"desligado", "desligar", "desliga", "off", "nao", "false", "0", "inativo", "desativar",
                  "desativada", "desativado", "desligada"}

SINONIMOS_VALOR = {
    "baixa": {"baixa", "baixo", "low", "lo", "min", "minima", "1", "fraca", "fraco", "lenta"},
    "media": {"media", "medio", "mid", "med", "medium", "2", "intermediaria"},
    "alta": {"alta", "alto", "high", "hi", "max", "forte", "3", "rapida"},
    "automatica": {"automatica", "automatico", "auto", "a"},
    "turbo": {"turbo", "powerful", "maxima", "maximo", "highest", "jet"},
    "silenciosa": {"silenciosa", "silencioso", "quiet", "silent", "noturna", "noturno", "sleep"},
    "frio": {"frio", "fria", "cool", "cold", "resfriar", "refrigerar", "gelar"},
    "calor": {"calor", "quente", "heat", "hot", "aquecer", "aquecimento"},
    "desumidificar": {"desumidificar", "seco", "dry", "dh", "desumidificacao", "umidade"},
    "ventilar": {"ventilar", "ventilacao", "fan", "fan only", "fan_only", "ventilador", "so ventilar"},
    "automatico": {"automatico", "auto", "heat cool", "heat_cool", "automatica"},
}


def normalizar_valor(valor) -> str:
    if isinstance(valor, bool):
        return "ligado" if valor else "desligado"
    v = normalizar(str(valor))
    if v in _VAL_LIGADO:
        return "ligado"
    if v in _VAL_DESLIGADO:
        return "desligado"
    return v.replace(" ", "_")


def valores_equivalentes(pedido, aceitos: list) -> list:
    """Valores aceitos que correspondem ao pedido (exato primeiro, depois sinônimos)."""
    alvo = normalizar_valor(pedido)
    norm = {normalizar_valor(a): a for a in aceitos}
    if alvo in norm:
        return [norm[alvo]]
    alvo_esp = alvo.replace("_", " ")
    candidatos = []
    for canon, sins in SINONIMOS_VALOR.items():
        if alvo_esp in sins or alvo == canon:
            for n, original in norm.items():
                n_esp = n.replace("_", " ")
                if n == canon or n_esp in sins:
                    candidatos.append(original)
    # números: "2" ↔ "velocidade 2", "nivel 2"
    if not candidatos and re.fullmatch(r"\d+", alvo):
        for n, original in norm.items():
            if re.fullmatch(rf"\D*{alvo}", n):
                candidatos.append(original)
    vistos, out = set(), []
    for c in candidatos:
        if c not in vistos:
            vistos.add(c)
            out.append(c)
    return out


# ----------------------------------------------------------------- categorias
CATEGORIAS = {
    "tv": ("TV", ("tv", "tvs", "televisao", "televisor", "smart tv", "universal tv remotes")),
    "ar_condicionado": ("Ar-condicionado", ("ar", "ar condicionado", "acs", "ac", "split", "climatizador",
                                            "air conditioner", "climate", "janela")),
    "ventilador": ("Ventilador", ("ventilador", "fans", "fan", "ventilador de teto", "circulador")),
    "iluminacao": ("Iluminação / fita LED", ("led", "fita led", "led lighting", "luz", "luzes", "lampada",
                                             "luminaria", "light", "iluminacao", "abajur", "plafon")),
    "soundbar": ("Soundbar", ("soundbar", "soundbars", "barra de som", "home theater")),
    "caixa_de_som": ("Caixa de som / som", ("caixa de som", "speakers", "speaker", "som", "aparelho de som",
                                             "micro system", "minisystem", "cd players", "cd player", "minidisc",
                                             "multimedia")),
    "receiver": ("Receiver de áudio e vídeo", ("receiver", "audio and video receivers", "amplificador",
                                               "receiver av", "av receiver")),
    "projetor": ("Projetor", ("projetor", "projectors", "projector", "datashow", "data show")),
    "camera": ("Câmera", ("camera", "cameras", "cctv", "filmadora", "camera fotografica")),
    "tv_box": ("TV box, cabo e streaming", ("tv box", "streaming devices", "cable boxes", "dvb t", "tv tuner",
                                            "decodificador", "receptor", "conversor", "set top box", "sky",
                                            "claro tv", "chromecast", "converters")),
    "midia_fisica": ("Blu-ray, DVD e vídeo", ("blu ray", "dvd", "dvd players", "vcr", "laserdisc", "videocassete")),
    "aquecedor": ("Aquecedor e lareira", ("aquecedor", "heaters", "fireplaces", "lareira")),
    "purificador": ("Purificador, umidificador", ("purificador", "air purifiers", "humidifiers", "umidificador",
                                                  "dust collectors", "desumidificador")),
    "aspirador": ("Aspirador e robôs de limpeza", ("aspirador", "vacuum cleaners", "robo", "window cleaners")),
    "monitor": ("Monitor e telas", ("monitor", "monitors", "touchscreen displays", "digital signs", "whiteboards",
                                    "picture frames", "porta retrato", "painel")),
    "carro": ("Multimídia de carro", ("car multimedia", "head units", "som automotivo", "carro")),
    "brinquedo": ("Brinquedo", ("toys", "brinquedo", "carrinho")),
    "videoconferencia": ("Videoconferência", ("videoconferencing", "videoconferencia")),
    "outros": ("Outros", ("miscellaneous", "kvm", "clocks", "computers", "consoles", "bidet",
                          "handicap ceiling lifts", "outro", "outros", "relogio", "console", "videogame")),
}

_ALIAS_CATEGORIA = {}
for _chave, (_rot, _alias) in CATEGORIAS.items():
    _ALIAS_CATEGORIA[_chave.replace("_", " ")] = _chave
    for _a in _alias:
        _ALIAS_CATEGORIA[normalizar(_a)] = _chave


def categoria_canonica(texto: str | None) -> str | None:
    if not texto:
        return None
    n = normalizar(texto)
    if n in _ALIAS_CATEGORIA:
        return _ALIAS_CATEGORIA[n]
    for alias, chave in sorted(_ALIAS_CATEGORIA.items(), key=lambda x: -len(x[0])):
        if re.search(rf"\b{re.escape(alias)}\b", n):
            return chave
    return None


# ------------------------------------------------------------------ teclas
def _t(chave, rotulo, tipo="tecla", parametro=None, passo=0, efeitos=(), teste=0, risco=False):
    return Termo(chave, rotulo, tipo, parametro, passo, tuple(efeitos), teste, risco)


_RISCO = re.compile(
    r"\b(service|servico|factory|fabrica|reset|eeprom|hotel|install|instalacao|calib\w*|test mode|"
    r"shop|clear|erase|apagar|format|programming|program mode|prog mode|learn|aprender|pair\w*|pareamento|code set|"
    r"setup code|master|initial\w*|default|restaurar|restore|debug|engineer\w*)\b")

_DIRETOS: dict[str, Termo] = {}


def _registrar(termo: Termo, *nomes):
    for n in nomes:
        _DIRETOS[normalizar(n)] = termo


T_LIGA_DESLIGA = _t("energia_alternar", "Liga/desliga", "alternar", "energia", teste=10)
T_LIGAR = _t("energia_ligar", "Ligar", "definir", efeitos=[("energia", "ligado")], teste=9)
T_DESLIGAR = _t("energia_desligar", "Desligar", "definir", efeitos=[("energia", "desligado")], teste=4)
_registrar(T_LIGA_DESLIGA, "power", "pwr", "on off", "onoff", "power toggle", "standby", "stand by", "liga desliga",
           "energia", "power key", "tv power", "on standby", "power on off", "turn on off", "toggle", "power button",
           "on off toggle", "pow", "power onoff", "start stop")
_registrar(T_LIGAR, "power on", "poweron", "on", "ligar", "pwr on", "turn on", "discrete on", "power on only")
_registrar(T_DESLIGAR, "power off", "poweroff", "off", "desligar", "pwr off", "turn off", "discrete off", "all off")

_registrar(_t("volume_mais", "Volume +", "ajustar", "volume", +1, teste=8),
           "vol up", "volume up", "vol mais", "volume mais", "vol", "v mais", "vol plus", "volup", "vol u",
           "volume plus", "louder", "aumentar volume")
_registrar(_t("volume_menos", "Volume −", "ajustar", "volume", -1, teste=7),
           "vol dn", "vol down", "volume down", "vol menos", "volume menos", "v menos", "vol minus", "voldown",
           "vol d", "volume minus", "softer", "diminuir volume", "vol dwn", "vol dw")
_registrar(_t("mudo_alternar", "Mudo", "alternar", "mudo", teste=6), "mute", "mudo", "silenciar", "mute toggle",
           "audio mute", "sound off")
_registrar(_t("canal_mais", "Canal +", "ajustar", "canal", +1, teste=5),
           "ch up", "ch next", "channel up", "ch mais", "canal mais", "chan up", "ch plus", "p mais", "page up",
           "channel next", "next channel", "prog mais", "program up", "program mais", "pr mais")
_registrar(_t("canal_menos", "Canal −", "ajustar", "canal", -1, teste=4),
           "ch dn", "ch down", "ch prev", "channel down", "ch menos", "canal menos", "chan down", "ch minus",
           "p menos", "page down", "channel prev", "previous channel", "prev channel", "prog menos",
           "program down", "program menos", "pr menos")
for _i in range(10):
    _registrar(_t(f"numero_{_i}", f"Tecla {_i}", teste=1), str(_i), f"num {_i}", f"number {_i}", f"key {_i}",
               f"digit {_i}", f"btn {_i}", f"button {_i}", f"tecla {_i}", f"n {_i}")

# navegação e menus
for _ch, _rot, _nomes in (
    ("cima", "Seta para cima", ("up", "cima", "arrow up", "nav up", "cursor up", "dpad up", "navup")),
    ("baixo", "Seta para baixo", ("down", "baixo", "arrow down", "nav down", "cursor down", "dpad down", "dn",
                                  "navdown")),
    ("esquerda", "Seta para a esquerda", ("left", "esquerda", "arrow left", "nav left", "cursor left", "navleft")),
    ("direita", "Seta para a direita", ("right", "direita", "arrow right", "nav right", "cursor right",
                                        "navright")),
    ("ok", "OK / confirmar", ("ok", "enter", "select", "confirm", "confirmar", "sel", "okay")),
    ("voltar", "Voltar", ("back", "return", "voltar", "retornar", "ret", "previous menu")),
    ("menu", "Menu", ("menu", "main menu", "setup menu", "settings", "config", "configuracoes", "options",
                      "opcoes", "tools", "setting")),
    ("inicio", "Início (home)", ("home", "inicio", "smart", "smart hub", "my apps", "apps")),
    ("sair", "Sair", ("exit", "sair", "cancel")),
    ("informacao", "Informações", ("info", "display", "information", "disp", "osd", "status")),
    ("guia", "Guia de programação", ("guide", "guia", "epg")),
    ("lista", "Lista", ("list", "lista", "ch list", "channel list")),
    ("netflix", "Netflix", ("netflix",)),
    ("youtube", "YouTube", ("youtube",)),
    ("prime_video", "Prime Video", ("prime video", "amazon", "prime")),
    ("legenda", "Legenda", ("subtitle", "subtitles", "legenda", "cc", "caption")),
    ("audio", "Áudio / idioma", ("audio", "language", "idioma", "mts", "sap")),
    ("formato_tela", "Formato da imagem", ("aspect", "ratio", "zoom mode", "picture size", "wide", "formato")),
    ("modo_imagem", "Modo de imagem", ("picture", "picture mode", "p mode", "imagem")),
    ("modo_som", "Modo de som", ("sound", "sound mode", "s mode", "eq", "equalizer", "surround", "sound field")),
    ("dormir", "Desligamento automático (sleep)", ("sleep", "sleep timer", "dormir")),
):
    _registrar(_t(_ch, _rot, teste=2 if _ch in ("menu", "inicio", "informacao") else 0), *_nomes)

# reprodução
for _ch, _rot, _nomes in (
    ("reproduzir", "Reproduzir", ("play", "reproduzir", "tocar")),
    ("pausar", "Pausar", ("pause", "pausar", "pausa")),
    ("reproduzir_pausar", "Reproduzir/pausar", ("play pause", "playpause", "pause play")),
    ("parar", "Parar", ("stop", "parar")),
    ("proxima_faixa", "Próxima faixa", ("next", "skip", "skip fwd", "next track", "proximo", "proxima", "skip next",
                                        "track next", "skip forward")),
    ("faixa_anterior", "Faixa anterior", ("prev", "previous", "skip back", "prev track", "anterior", "skip prev",
                                          "track prev", "skip backward", "last")),
    ("avancar", "Avançar", ("ff", "fast forward", "fwd", "forward", "avancar", "scan forward", "ffwd")),
    ("retroceder", "Retroceder", ("rew", "rewind", "rw", "retroceder", "scan back", "fast back", "fr")),
    ("gravar", "Gravar", ("rec", "record", "gravar")),
    ("ejetar", "Ejetar", ("eject", "open close", "ejetar", "open")),
    ("repetir", "Repetir", ("repeat", "repetir")),
    ("aleatorio", "Aleatório", ("shuffle", "random", "aleatorio")),
):
    _registrar(_t(_ch, _rot, teste=1 if _ch in ("reproduzir", "pausar", "reproduzir_pausar") else 0), *_nomes)

# entradas
_registrar(_t("entrada_alternar", "Entrada / fonte (próxima)", "ajustar", "entrada", 0, teste=3),
           "input", "source", "src", "fonte", "entrada", "av tv", "tv av", "input select", "inputs", "sources",
           "input source", "function", "func", "selector", "mode input")
for _n in range(1, 6):
    _registrar(_t(f"entrada_hdmi{_n}", f"HDMI {_n}", "definir", efeitos=[("entrada", f"hdmi{_n}")], teste=2),
               f"hdmi {_n}", f"hdmi{_n}", f"input hdmi {_n}", f"hdmi input {_n}", f"source hdmi {_n}")
    _registrar(_t(f"entrada_av{_n}", f"AV {_n}", "definir", efeitos=[("entrada", f"av{_n}")], teste=1),
               f"av {_n}", f"video {_n}", f"input av {_n}", f"ext {_n}")
for _ch, _rot, _nomes in (
    ("hdmi", "HDMI", ("hdmi", "input hdmi", "hdmi arc", "arc", "hdmi cec")),
    ("tv", "TV (antena)", ("input tv", "tv input", "antenna", "antena", "dtv", "atv", "tuner")),
    ("componente", "Componente", ("component", "componente", "ypbpr", "comp")),
    ("pc", "PC / VGA", ("pc", "vga", "rgb", "computer", "computador")),
    ("usb", "USB", ("usb", "media", "usb media")),
    ("optica", "Óptica", ("optical", "optico", "optica", "opt", "toslink")),
    ("bluetooth", "Bluetooth", ("bluetooth", "bt", "pair bt")),
    ("aux", "AUX / linha", ("aux", "line", "line in", "analog", "auxiliar")),
    ("coaxial", "Coaxial", ("coaxial", "coax")),
    ("radio", "Rádio", ("fm", "am", "radio", "tuner fm", "am fm")),
):
    _registrar(_t(f"entrada_{_ch}", f"Entrada {_rot}", "definir", efeitos=[("entrada", _ch)], teste=1), *_nomes)

# ventiladores
_registrar(_t("velocidade_mais", "Velocidade +", "ajustar", "velocidade", +1, teste=6),
           "speed up", "speed mais", "fan up", "faster", "velocidade mais", "fan speed up", "wind up", "speed plus",
           "speed high up", "fan mais", "increase speed")
_registrar(_t("velocidade_menos", "Velocidade −", "ajustar", "velocidade", -1, teste=5),
           "speed down", "speed menos", "fan down", "slower", "velocidade menos", "fan speed down", "wind down",
           "speed minus", "fan menos", "decrease speed", "speed dn")
_registrar(_t("velocidade_ciclo", "Velocidade (próxima)", "ajustar", "velocidade", 0, teste=5),
           "speed", "fan speed", "velocidade", "wind speed", "speed cycle", "wind", "fan", "speed select", "vel",
           "level")
for _n in range(1, 13):
    _registrar(_t(f"velocidade_{_n}", f"Velocidade {_n}", "definir", efeitos=[("velocidade", str(_n))], teste=6),
               f"speed {_n}", f"fan {_n}", f"velocidade {_n}", f"level {_n}", f"nivel {_n}", f"wind {_n}",
               f"fan speed {_n}", f"speed level {_n}", f"vel {_n}", f"s {_n}")
for _v, _nomes in (("baixa", ("speed low", "fan low", "low speed", "velocidade baixa", "low")),
                   ("media", ("speed mid", "speed medium", "fan mid", "fan medium", "medium speed", "velocidade media",
                              "mid", "medium", "med")),
                   ("alta", ("speed high", "fan high", "high speed", "velocidade alta", "high", "hi"))):
    _registrar(_t(f"velocidade_{_v}", f"Velocidade {_v}", "definir", efeitos=[("velocidade", _v)], teste=5), *_nomes)
_registrar(_t("oscilacao_alternar", "Oscilação", "alternar", "oscilacao", teste=6),
           "oscillate", "oscillation", "osc", "oscilar", "oscilacao", "swing", "rotate", "rotation", "rotacao",
           "turn", "giro", "sweep", "louver", "swing toggle", "head", "oscillating", "rot", "swing mode", "airflow")
_registrar(_t("oscilacao_ligar", "Oscilação ligada", "definir", efeitos=[("oscilacao", "ligado")], teste=5),
           "oscillate on", "swing on", "rotate on", "osc on", "oscilacao ligar")
_registrar(_t("oscilacao_desligar", "Oscilação desligada", "definir", efeitos=[("oscilacao", "desligado")]),
           "oscillate off", "swing off", "rotate off", "osc off", "oscilacao desligar", "fix", "swing stop")
_registrar(_t("temporizador", "Temporizador", "tecla", teste=0), "timer", "temporizador", "off timer", "on timer",
           "timer mais", "set timer", "time")
_registrar(_t("modo_ciclo", "Modo (próximo)", "ajustar", "modo", 0, teste=3), "mode", "modo", "mode select",
           "wind mode", "modes", "fan mode", "mode button")
for _ch, _rot, _nomes in (
    ("natural", "Natural", ("natural", "nature", "natural wind", "breeze", "brisa", "natural mode")),
    ("noturno", "Noturno", ("night", "night mode", "noturno", "sleep mode", "sleep wind")),
    ("turbo", "Turbo", ("turbo", "boost", "jet", "powerful")),
    ("ionizador", "Ionizador", ("ion", "ionizer", "anion", "ionizador", "plasma")),
):
    _registrar(_t(f"modo_{_ch}", f"Modo {_rot}", "definir", efeitos=[("modo", _ch)], teste=2), *_nomes)

# iluminação
_registrar(_t("brilho_mais", "Brilho +", "ajustar", "brilho", +1, teste=6),
           "brightness up", "bright up", "brighter", "brilho mais", "brightness mais", "bright mais", "light up",
           "brighten", "lum mais", "dimmer up", "intensity up", "bright")
_registrar(_t("brilho_menos", "Brilho −", "ajustar", "brilho", -1, teste=5),
           "brightness down", "bright down", "dim", "darker", "brilho menos", "brightness menos", "bright menos",
           "light down", "lum menos", "dimmer down", "dimmer", "intensity down", "dim down")
_registrar(_t("temperatura_cor_mais", "Luz mais fria", "ajustar", "temperatura_cor", +1, teste=2),
           "colder", "cooler", "cool light", "luz fria")
_registrar(_t("temperatura_cor_menos", "Luz mais quente", "ajustar", "temperatura_cor", -1, teste=2),
           "warmer", "warm light", "luz quente")
for _cor, _nomes in CORES.items():
    _registrar(_t(f"cor_{_cor}", f"Cor {_cor}", "definir", efeitos=[("cor", _cor)], teste=7),
               *_nomes, *[f"color {n}" for n in _nomes if len(n) > 1], *[f"cor {n}" for n in _nomes])
    for _k in range(1, 6):
        _registrar(_t(f"cor_{_cor}_{_k}", f"Cor {_cor} (tom {_k})", "definir",
                      efeitos=[("cor", f"{_cor}_{_k}")], teste=5),
                   *[f"{n} {_k}" for n in _nomes if len(n) > 1 or n in "rgbw"])
for _ch, _rot, _nomes in (
    ("flash", "Efeito piscar", ("flash", "blink", "piscar")),
    ("strobe", "Efeito estroboscópico", ("strobe", "estrobo")),
    ("fade", "Efeito transição", ("fade", "fading", "transicao")),
    ("suave", "Efeito suave", ("smooth", "suave", "soft")),
    ("salto", "Efeito salto", ("jump", "jump 3", "jump 7", "salto")),
    ("automatico", "Efeito automático", ("auto", "demo", "auto mode", "cycle")),
    ("musica", "Efeito música", ("music", "musica", "music mode")),
):
    _registrar(_t(f"efeito_{_ch}", _rot, "definir", efeitos=[("modo", _ch)], teste=3), *_nomes)

# ar-condicionado por teclas
_registrar(_t("temperatura_mais", "Temperatura +", "ajustar", "temperatura", +1, teste=4),
           "temp up", "temp mais", "temperature up", "temperatura mais", "t mais", "temp plus", "temp u", "tem up")
_registrar(_t("temperatura_menos", "Temperatura −", "ajustar", "temperatura", -1, teste=4),
           "temp down", "temp dn", "temp menos", "temperature down", "temperatura menos", "t menos", "temp minus",
           "temp d", "tem down")
for _ch, _rot, _modo, _nomes in (
    ("ar_frio_forte", "Frio (forte)", "frio", ("cool hi", "cool high", "cool max", "cooling high")),
    ("ar_frio_suave", "Frio (suave)", "frio", ("cool lo", "cool low", "cool min", "cooling low")),
    ("ar_frio", "Frio", "frio", ("cool", "cooling", "frio", "cool mode", "mode cool")),
    ("ar_calor_forte", "Calor (forte)", "calor", ("heat hi", "heat high", "heat max")),
    ("ar_calor_suave", "Calor (suave)", "calor", ("heat lo", "heat low", "heat min")),
    ("ar_calor", "Calor", "calor", ("heat", "heating", "calor", "heat mode", "mode heat")),
    ("ar_desumidificar", "Desumidificar", "desumidificar", ("dh", "dry", "dehumidify", "desumidificar", "dry mode")),
    ("ar_ventilar", "Só ventilar", "ventilar", ("fan only", "ventilar", "fan mode only")),
):
    _registrar(_t(_ch, _rot, "definir", efeitos=[("energia", "ligado"), ("modo", _modo)], teste=8), *_nomes)

# câmeras e projetores
_registrar(_t("disparo", "Disparar (foto)", "tecla", teste=8), "shutter", "shot", "photo", "foto", "capture",
           "take photo", "trigger", "disparar", "shoot", "release")
_registrar(_t("disparo_atrasado", "Disparo com atraso", "tecla", teste=6), "shutter 2s", "2s", "delay", "timer shot",
           "2 sec", "shutter delay", "delayed")
_registrar(_t("zoom_mais", "Zoom +", "ajustar", "zoom", +1, teste=3), "zoom in", "zoom mais", "zoom t", "tele",
           "zoom up")
_registrar(_t("zoom_menos", "Zoom −", "ajustar", "zoom", -1, teste=3), "zoom out", "zoom menos", "zoom w", "wide angle",
           "zoom down")
_registrar(_t("foco_mais", "Foco +", "ajustar", "foco", +1), "focus up", "focus mais", "focus near", "focus in")
_registrar(_t("foco_menos", "Foco −", "ajustar", "foco", -1), "focus down", "focus menos", "focus far", "focus out")
for _ch, _rot, _nomes in (
    ("congelar", "Congelar imagem", ("freeze", "congelar", "still")),
    ("tela_preta", "Tela preta (blank)", ("blank", "av mute", "video mute", "hide", "no show", "pic mute",
                                          "blank screen", "a v mute", "shutter projector")),
    ("trapezio", "Correção de trapézio", ("keystone", "trapezio", "keystone mais", "keystone menos")),
    ("autoajuste", "Ajuste automático", ("auto adjust", "auto sync", "autoajuste", "auto image", "auto setup")),
):
    _registrar(_t(_ch, _rot, teste=1 if _ch == "tela_preta" else 0), *_nomes)


def _por_regex(n: str) -> Termo | None:
    m = re.fullmatch(r"(?:power|pwr|energia)\s*(on|off|ligar|desligar)", n)
    if m:
        return T_LIGAR if m.group(1) in ("on", "ligar") else T_DESLIGAR
    m = re.search(r"\bhdmi\s*(\d)\b", n)
    if m and int(m.group(1)) <= 5:
        return _DIRETOS[normalizar(f"hdmi {m.group(1)}")]
    m = re.fullmatch(r"(?:speed|fan|velocidade|level|nivel|wind)\s*(?:level\s*)?(\d{1,2})", n)
    if m and 1 <= int(m.group(1)) <= 12:
        return _DIRETOS[normalizar(f"speed {m.group(1)}")]
    if re.search(r"\b(vol|volume)\b.*\b(up|mais|plus|u)\b", n):
        return _DIRETOS["vol up"]
    if re.search(r"\b(vol|volume)\b.*\b(down|dn|menos|minus|d|dwn)\b", n):
        return _DIRETOS["vol down"]
    if re.search(r"\b(ch|chan|channel|canal)\b.*\b(up|next|mais|plus)\b", n):
        return _DIRETOS["ch up"]
    if re.search(r"\b(ch|chan|channel|canal)\b.*\b(down|dn|prev|menos|minus)\b", n):
        return _DIRETOS["ch down"]
    if re.search(r"\b(bright\w*|brilho|lum\w*|dimmer)\b.*\b(up|mais|plus)\b", n):
        return _DIRETOS["brightness up"]
    if re.search(r"\b(bright\w*|brilho|lum\w*|dimmer)\b.*\b(down|dn|menos|minus)\b", n):
        return _DIRETOS["brightness down"]
    if re.search(r"\b(temp\w*)\b.*\b(up|mais|plus)\b", n):
        return _DIRETOS["temp up"]
    if re.search(r"\b(temp\w*)\b.*\b(down|dn|menos|minus)\b", n):
        return _DIRETOS["temp down"]
    if re.search(r"\b(osc\w*|swing|rotat\w*)\b", n):
        if re.search(r"\b(on|ligar)\b", n):
            return _DIRETOS["oscillate on"]
        if re.search(r"\b(off|desligar|stop)\b", n):
            return _DIRETOS["oscillate off"]
        return _DIRETOS["oscillate"]
    if re.search(r"\b(power|pwr)\b", n) and not re.search(r"\b(on|off)\b", n):
        return T_LIGA_DESLIGA
    return None


def interpretar(nome: str) -> Termo:
    """Converte qualquer nome de tecla em um termo do vocabulário."""
    n = normalizar(nome)
    risco = bool(_RISCO.search(n))
    termo = _DIRETOS.get(n) or (None if risco else _por_regex(n))
    if termo is None:
        rot = " ".join(str(nome).replace("_", " ").split()) or "Tecla"
        return Termo(f"x_{slug(nome)}", rot[:60], "tecla", risco=risco)
    if risco and not termo.risco:
        return Termo(termo.chave, termo.rotulo, termo.tipo, termo.parametro, termo.passo, termo.efeitos, 0, True)
    return termo


def termo_por_chave(chave: str, rotulo: str | None = None) -> Termo:
    for t in _DIRETOS.values():
        if t.chave == chave:
            return t
    if chave.startswith("x_"):
        return Termo(chave, rotulo or chave[2:].replace("_", " "), "tecla", risco=bool(_RISCO.search(chave[2:].replace("_", " "))))
    return interpretar(rotulo or chave)


def todas_chaves() -> list[Termo]:
    vistos, out = set(), []
    for t in _DIRETOS.values():
        if t.chave not in vistos:
            vistos.add(t.chave)
            out.append(t)
    return out


# testes padrão por categoria (comandos observáveis com o aparelho desligado)
TESTE_PADRAO = {
    None: ["energia_alternar", "energia_ligar"],
    "iluminacao": ["energia_ligar", "energia_alternar", "cor_vermelho", "cor_azul"],
    "ar_condicionado": ["@estado_ligar", "energia_alternar", "energia_ligar", "ar_frio", "ar_frio_suave",
                        "ar_frio_forte"],
    "camera": ["disparo", "disparo_atrasado"],
    "ventilador": ["energia_alternar", "energia_ligar", "velocidade_1", "velocidade_ciclo"],
}

# pedido do usuário → lista de chaves de teste
TESTES_NOMEADOS = {
    "energia": ["energia_alternar", "energia_ligar"],
    "ligar": ["energia_ligar", "energia_alternar"],
    "desligar": ["energia_desligar", "energia_alternar"],
    "volume": ["volume_mais", "volume_menos"],
    "volume_mais": ["volume_mais"],
    "volume_menos": ["volume_menos"],
    "mudo": ["mudo_alternar"],
    "canal": ["canal_mais", "canal_menos"],
    "cor": ["cor_vermelho", "cor_azul", "cor_verde"],
    "azul": ["cor_azul"], "vermelho": ["cor_vermelho"], "verde": ["cor_verde"], "branco": ["cor_branco"],
    "brilho": ["brilho_mais", "brilho_menos"],
    "velocidade": ["velocidade_mais", "velocidade_ciclo", "velocidade_2", "velocidade_1"],
    "oscilacao": ["oscilacao_alternar", "oscilacao_ligar"],
    "entrada": ["entrada_alternar"],
    "menu": ["menu", "inicio"],
    "disparo": ["disparo", "disparo_atrasado"],
    "foto": ["disparo"],
}


def chaves_de_teste(categoria: str | None, comando_teste: str | None) -> list[str]:
    if comando_teste:
        n = slug(comando_teste)
        if n in TESTES_NOMEADOS:
            return TESTES_NOMEADOS[n]
        t = interpretar(comando_teste)
        if not t.chave.startswith("x_"):
            return [t.chave]
        return [n if n.startswith("x_") else f"x_{n}"]
    return TESTE_PADRAO.get(categoria, TESTE_PADRAO[None])

