"""Catálogo local de perfis (SQLite).

* ``perfis``   — um controle remoto (marca, modelo, categoria, fonte, licença);
* ``sinais``   — transmissões únicas, identificadas pela impressão;
* ``comandos`` — liga perfis a sinais (um sinal pode pertencer a muitos perfis);
* ``estados``  — perfis de estado completo (ar-condicionado) guardam a tabela
  inteira comprimida e um sinal representativo de "ligar" para os testes.
"""
from __future__ import annotations

import gzip
import json
import os
import re
import sqlite3
import threading
import zlib
from pathlib import Path

from . import formatos, vocabulario
from .sinais import ErroSinal, Sinal

ESQUEMA = """
CREATE TABLE IF NOT EXISTS perfis(
  id INTEGER PRIMARY KEY, chave TEXT UNIQUE, nome TEXT, categoria TEXT, marca TEXT, marca_norm TEXT,
  modelo TEXT, modelo_norm TEXT, fonte TEXT, licenca TEXT, ncomandos INT, estado BLOB);
CREATE TABLE IF NOT EXISTS sinais(id INTEGER PRIMARY KEY, impressao TEXT UNIQUE, dados TEXT);
CREATE TABLE IF NOT EXISTS comandos(
  perfil INT, chave TEXT, base TEXT, rotulo TEXT, nome_original TEXT, tipo TEXT, meta TEXT, sinal INT,
  ordem INT);
CREATE TABLE IF NOT EXISTS fontes(id TEXT PRIMARY KEY, nome TEXT, licenca TEXT, url TEXT, nota TEXT, perfis INT);
CREATE INDEX IF NOT EXISTS ix_cmd_base ON comandos(base);
CREATE INDEX IF NOT EXISTS ix_cmd_sinal ON comandos(sinal);
CREATE INDEX IF NOT EXISTS ix_cmd_perfil ON comandos(perfil);
CREATE INDEX IF NOT EXISTS ix_perfil_cat ON perfis(categoria);
CREATE INDEX IF NOT EXISTS ix_perfil_marca ON perfis(marca_norm);
"""

FONTES = {
    "smartir": ("SmartIR (smartHomeHub)", "MIT", "https://github.com/smartHomeHub/SmartIR",
                "Copyright (c) 2019 Vassilis Panos — licença MIT incluída em LICENCAS/."),
    "flipper-irdb-cc0": ("Flipper-IRDB — contribuições sob CC0", "CC0-1.0",
                         "https://github.com/Lucaslhm/Flipper-IRDB",
                         "Somente arquivos adicionados após o commit 2319685 (adoção da CC0)."),
    "flipper-irdb": ("Flipper-IRDB completo (download no celular)", "CC0-1.0 parcial",
                     "https://github.com/Lucaslhm/Flipper-IRDB",
                     "Arquivos anteriores ao commit 2319685 não têm licença declarada; baixados pelo usuário "
                     "para uso pessoal."),
    "usuario": ("Importados pelo usuário", "do usuário", "", ""),
}

# marcas que compartilham fabricante/códigos no mercado brasileiro
MARCAS_RELACIONADAS = {
    "springer": ["midea", "carrier", "comfee"], "midea": ["springer", "carrier", "comfee"],
    "carrier": ["midea", "springer"], "comfee": ["midea"],
    "consul": ["brastemp", "whirlpool"], "brastemp": ["consul", "whirlpool"], "whirlpool": ["consul", "brastemp"],
    "semp": ["toshiba", "tcl", "semp toshiba"], "semp toshiba": ["toshiba", "tcl"], "toshiba": ["semp"],
    "tcl": ["semp"], "philco": ["britania", "tcl"], "britania": ["philco"], "aoc": ["philips"],
    "philips": ["aoc"], "elgin": ["gree", "midea"], "agratto": ["gree", "tcl"], "gradiente": ["gree"],
    "electrolux": ["frigidaire"], "lg": ["goldstar"], "samsung": [], "hitachi": ["daikin"],
    "multilaser": ["tcl"], "cce": ["hitachi"], "buster": ["philco"], "mondial": [], "arno": ["tefal"],
}


def normalizar_marca(marca: str | None) -> str:
    if not marca:
        return ""
    n = vocabulario.normalizar(str(marca).lower())  # sem separar camelCase em nomes de marca
    n = re.sub(r"\b(electronics?|eletronicos?|corp(oration)?|inc|ltd|co|brasil|brazil|group)\b", "", n)
    return " ".join(n.split())


def _zip(obj) -> bytes:
    return zlib.compress(json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode(), 6)


def _unzip(b: bytes):
    return json.loads(zlib.decompress(b).decode())


def estado_representativo(ec: dict) -> dict | None:
    """Escolhe um estado 'ligar' típico (frio, ~24 °C, ventilação automática/baixa, sem oscilação)."""
    estados = ec.get("estados") or []
    if not estados:
        return None

    def custo(e):
        c = 0 if e.get("modo") == "frio" else (1 if e.get("modo") == "automatico" else 3)
        try:
            c += abs(float(e.get("temperatura", 24)) - 24) / 2
        except (TypeError, ValueError):
            c += 5
        c += {"automatica": 0, "baixa": 0.5, "media": 1}.get(e.get("ventilacao"), 2)
        if "oscilacao" in e:
            c += 0 if e["oscilacao"] in ("desligada",) else 0.5
        return c

    return min(estados, key=custo)


class Catalogo:
    def __init__(self, caminho: str | os.PathLike):
        self.caminho = str(caminho)
        Path(self.caminho).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.caminho, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.trava = threading.RLock()
        with self.trava:
            self.db.executescript(ESQUEMA)
            self.db.execute("PRAGMA journal_mode=WAL")
        self._cache_sinal: dict[str, int] = {}

    def fechar(self):
        self.db.close()

    # ---------------------------------------------------------------- escrita
    def _id_sinal(self, sinal: dict) -> int:
        s = Sinal(sinal)
        imp = s.impressao()
        if imp in self._cache_sinal:
            return self._cache_sinal[imp]
        cur = self.db.execute("SELECT id FROM sinais WHERE impressao=?", (imp,))
        row = cur.fetchone()
        if row:
            sid = row[0]
        else:
            sid = self.db.execute("INSERT INTO sinais(impressao, dados) VALUES(?,?)",
                                  (imp, json.dumps(s.compacto(), separators=(",", ":")))).lastrowid
        if len(self._cache_sinal) > 200000:
            self._cache_sinal.clear()
        self._cache_sinal[imp] = sid
        return sid

    def adicionar_perfil(self, perfil: dict, substituir: bool = True) -> int:
        with self.trava:
            existente = self.db.execute("SELECT id FROM perfis WHERE chave=?", (perfil["chave"],)).fetchone()
            if existente:
                if not substituir:
                    return existente[0]
                self.remover_perfil(existente[0])
            ec = perfil.get("estado_completo")
            pid = self.db.execute(
                "INSERT INTO perfis(chave,nome,categoria,marca,marca_norm,modelo,modelo_norm,fonte,licenca,"
                "ncomandos,estado) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (perfil["chave"], perfil.get("nome"), perfil.get("categoria"), perfil.get("marca"),
                 normalizar_marca(perfil.get("marca")), perfil.get("modelo"),
                 vocabulario.normalizar(perfil.get("modelo") or ""), perfil.get("fonte"), perfil.get("licenca"),
                 len(perfil.get("comandos", [])), _zip(ec) if ec else None)).lastrowid
            linhas = []
            for i, c in enumerate(perfil.get("comandos", [])):
                try:
                    sid = self._id_sinal(c["sinal"])
                except (ErroSinal, ValueError):
                    continue
                meta = {k: c[k] for k in ("parametro", "passo", "efeitos", "risco") if k in c}
                linhas.append((pid, c["chave"], c.get("base", c["chave"]), c.get("rotulo"), c.get("nome_original"),
                               c.get("tipo", "tecla"),
                               json.dumps(meta, ensure_ascii=False) if meta else None, sid, i))
            if ec:
                rep = estado_representativo(ec)
                if rep:
                    try:
                        sid = self._id_sinal(rep["sinal"])
                        desc = f"Ligar em {rep.get('modo')} {rep.get('temperatura')} °C, ventilação {rep.get('ventilacao')}"
                        meta = {"efeitos": {k: rep[k] for k in ("modo", "temperatura", "ventilacao", "oscilacao")
                                            if k in rep} | {"energia": "ligado"}}
                        linhas.append((pid, "@estado_ligar", "@estado_ligar", desc, "estado", "definir",
                                       json.dumps(meta, ensure_ascii=False), sid, -1))
                    except (ErroSinal, ValueError):
                        pass
            self.db.executemany("INSERT INTO comandos VALUES(?,?,?,?,?,?,?,?,?)", linhas)
            return pid

    def remover_perfil(self, pid: int):
        with self.trava:
            self.db.execute("DELETE FROM comandos WHERE perfil=?", (pid,))
            self.db.execute("DELETE FROM perfis WHERE id=?", (pid,))

    def remover_fonte(self, fonte: str):
        with self.trava:
            self.db.execute("DELETE FROM comandos WHERE perfil IN (SELECT id FROM perfis WHERE fonte=?)", (fonte,))
            self.db.execute("DELETE FROM perfis WHERE fonte=?", (fonte,))
            self.db.execute("DELETE FROM sinais WHERE id NOT IN (SELECT DISTINCT sinal FROM comandos)")
            self.db.commit()

    def registrar_fonte(self, fid: str):
        nome, lic, url, nota = FONTES.get(fid, (fid, "", "", ""))
        n = self.db.execute("SELECT COUNT(*) FROM perfis WHERE fonte=?", (fid,)).fetchone()[0]
        self.db.execute("INSERT OR REPLACE INTO fontes VALUES(?,?,?,?,?,?)", (fid, nome, lic, url, nota, n))
        self.db.commit()

    def commit(self):
        with self.trava:
            self.db.commit()

    # ---------------------------------------------------------------- leitura
    def perfil(self, ident) -> dict | None:
        with self.trava:
            if isinstance(ident, int) or (isinstance(ident, str) and ident.isdigit()):
                row = self.db.execute("SELECT * FROM perfis WHERE id=?", (int(ident),)).fetchone()
            else:
                row = self.db.execute("SELECT * FROM perfis WHERE chave=?", (ident,)).fetchone()
            if not row:
                return None
            cmds = self.db.execute(
                "SELECT c.*, s.dados AS sdados FROM comandos c JOIN sinais s ON s.id=c.sinal "
                "WHERE c.perfil=? AND c.ordem>=0 ORDER BY c.ordem", (row["id"],)).fetchall()
        p = formatos.novo_perfil(row["chave"], row["nome"], row["categoria"], row["marca"], row["modelo"],
                                 row["fonte"], row["licenca"])
        p["id"] = row["id"]
        for c in cmds:
            d = {"chave": c["chave"], "base": c["base"], "rotulo": c["rotulo"], "nome_original": c["nome_original"],
                 "tipo": c["tipo"], "sinal": json.loads(c["sdados"]), "sinal_id": c["sinal"]}
            if c["meta"]:
                d.update(json.loads(c["meta"]))
            p["comandos"].append(d)
        if row["estado"]:
            p["estado_completo"] = _unzip(row["estado"])
        return p

    def resumo_perfil(self, row) -> dict:
        return {"id": row["id"], "nome": row["nome"], "marca": row["marca"], "modelo": row["modelo"],
                "categoria": row["categoria"], "comandos": row["ncomandos"],
                "estado_completo": row["estado"] is not None, "fonte": row["fonte"]}

    def sinal(self, sid: int) -> dict:
        with self.trava:
            row = self.db.execute("SELECT dados FROM sinais WHERE id=?", (sid,)).fetchone()
        if not row:
            raise KeyError(f"sinal {sid} não existe")
        return json.loads(row[0])

    def estatisticas(self) -> dict:
        with self.trava:
            cats = self.db.execute(
                "SELECT COALESCE(categoria,'desconhecida') c, COUNT(*) n FROM perfis GROUP BY c ORDER BY n DESC"
            ).fetchall()
            total = self.db.execute("SELECT COUNT(*) FROM perfis").fetchone()[0]
            nsin = self.db.execute("SELECT COUNT(*) FROM sinais").fetchone()[0]
            nmar = self.db.execute("SELECT COUNT(DISTINCT marca_norm) FROM perfis").fetchone()[0]
            fontes = self.db.execute("SELECT * FROM fontes").fetchall()
        return {"perfis": total, "sinais_unicos": nsin, "marcas": nmar,
                "categorias": {r["c"]: r["n"] for r in cats},
                "fontes": [{"id": f["id"], "nome": f["nome"], "licenca": f["licenca"], "perfis": f["perfis"],
                            "nota": f["nota"]} for f in fontes]}

    def marcas(self, categoria: str | None = None, texto: str | None = None, limite: int = 60) -> list[dict]:
        cat = vocabulario.categoria_canonica(categoria) if categoria else None
        sql = "SELECT marca, marca_norm, COUNT(*) n FROM perfis WHERE marca_norm<>''"
        args: list = []
        if cat:
            sql += " AND categoria=?"
            args.append(cat)
        if texto:
            sql += " AND marca_norm LIKE ?"
            args.append(f"%{normalizar_marca(texto)}%")
        sql += " GROUP BY marca_norm ORDER BY n DESC LIMIT ?"
        args.append(limite)
        with self.trava:
            return [{"marca": r["marca"], "perfis": r["n"]} for r in self.db.execute(sql, args)]

    def marca_existe(self, marca: str) -> list[str]:
        """Marcas instaladas que correspondem ao texto (exata, depois contendo)."""
        n = normalizar_marca(marca)
        if not n:
            return []
        with self.trava:
            exatas = [r[0] for r in self.db.execute("SELECT DISTINCT marca_norm FROM perfis WHERE marca_norm=?", (n,))]
            if exatas:
                return exatas
            return [r[0] for r in self.db.execute(
                "SELECT DISTINCT marca_norm FROM perfis WHERE marca_norm LIKE ? LIMIT 20", (f"%{n}%",))]

    def procurar(self, categoria=None, marca=None, modelo=None, texto=None, limite=20) -> list[dict]:
        sql = "SELECT * FROM perfis WHERE 1=1"
        args: list = []
        cat = vocabulario.categoria_canonica(categoria) if categoria else None
        if cat:
            sql += " AND categoria=?"
            args.append(cat)
        if marca:
            marcas = self.marca_existe(marca)
            if not marcas:
                return []
            sql += f" AND marca_norm IN ({','.join('?' * len(marcas))})"
            args += marcas
        if modelo:
            sql += " AND (modelo_norm LIKE ? OR nome LIKE ?)"
            m = vocabulario.normalizar(modelo)
            args += [f"%{m}%", f"%{modelo}%"]
        if texto:
            sql += " AND (nome LIKE ? OR marca LIKE ? OR modelo LIKE ?)"
            args += [f"%{texto}%"] * 3
        sql += " ORDER BY ncomandos DESC LIMIT ?"
        args.append(limite)
        with self.trava:
            return [self.resumo_perfil(r) for r in self.db.execute(sql, args)]

    def candidatos(self, chaves: list[str], categoria=None, marcas: list[str] | None = None,
                   excluir_marcas: list[str] | None = None, incluir_risco=False) -> list[dict]:
        """Sinais únicos que implementam as chaves de teste, com os perfis associados."""
        if not chaves:
            return []
        sql = (f"SELECT c.sinal, c.base AS chave, c.perfil, c.meta, p.marca_norm, p.modelo_norm, p.categoria "
               f"FROM comandos c JOIN perfis p ON p.id=c.perfil WHERE c.base IN ({','.join('?' * len(chaves))})")
        args: list = list(chaves)
        if categoria:
            sql += " AND p.categoria=?"
            args.append(categoria)
        if marcas:
            sql += f" AND p.marca_norm IN ({','.join('?' * len(marcas))})"
            args += marcas
        if excluir_marcas:
            sql += f" AND p.marca_norm NOT IN ({','.join('?' * len(excluir_marcas))})"
            args += excluir_marcas
        grupos: dict[int, dict] = {}
        prioridade = {c: i for i, c in enumerate(chaves)}
        with self.trava:
            rows = self.db.execute(sql, args).fetchall()
        for r in rows:
            if not incluir_risco and r["meta"] and '"risco": true' in r["meta"]:
                continue
            g = grupos.setdefault(r["sinal"], {"sinal_id": r["sinal"], "perfis": set(), "chaves": set(),
                                                "marcas": set(), "prioridade": 99})
            g["perfis"].add(r["perfil"])
            g["chaves"].add(r["chave"])
            g["marcas"].add(r["marca_norm"])
            g["prioridade"] = min(g["prioridade"], prioridade[r["chave"]])
        return list(grupos.values())

    def comandos_dos_perfis(self, perfis: list[int]) -> list[sqlite3.Row]:
        if not perfis:
            return []
        out = []
        with self.trava:
            for i in range(0, len(perfis), 500):
                parte = perfis[i:i + 500]
                out += self.db.execute(
                    f"SELECT perfil, chave, base, rotulo, tipo, meta, sinal FROM comandos WHERE perfil IN "
                    f"({','.join('?' * len(parte))}) AND ordem>=0", parte).fetchall()
        return out

    def perfis_com_sinal(self, sinal_id: int) -> list[int]:
        with self.trava:
            return [r[0] for r in self.db.execute("SELECT DISTINCT perfil FROM comandos WHERE sinal=?", (sinal_id,))]

    def nomes_perfis(self, ids: list[int], limite: int = 8) -> list[dict]:
        if not ids:
            return []
        ids = list(ids)[:limite]
        with self.trava:
            rows = self.db.execute(f"SELECT * FROM perfis WHERE id IN ({','.join('?' * len(ids))})", ids).fetchall()
        return [{"id": r["id"], "nome": r["nome"], "marca": r["marca"], "categoria": r["categoria"]} for r in rows]


# --------------------------------------------------------------- importadores

_CAT_FLIPPER = {
    "ACs": "ar_condicionado", "Air_Purifiers": "purificador", "Audio_and_Video_Receivers": "receiver",
    "Bidet": "outros", "Blu-Ray": "midia_fisica", "CCTV": "camera", "CD_Players": "caixa_de_som",
    "Cable_Boxes": "tv_box", "Cameras": "camera", "Car_Multimedia": "carro", "Clocks": "outros",
    "Computers": "outros", "Consoles": "outros", "Converters": "tv_box", "DVB-T": "tv_box",
    "DVD_Players": "midia_fisica", "Digital_Signs": "monitor", "Dust_Collectors": "purificador",
    "Fans": "ventilador", "Fireplaces": "aquecedor", "Handicap_Ceiling_Lifts": "outros", "Head_Units": "carro",
    "Heaters": "aquecedor", "Humidifiers": "purificador", "KVM": "outros", "LED_Lighting": "iluminacao",
    "Laserdisc": "midia_fisica", "MiniDisc": "caixa_de_som", "Miscellaneous": "outros", "Monitors": "monitor",
    "Multimedia": "caixa_de_som", "Picture_Frames": "monitor", "Projectors": "projetor", "SoundBars": "soundbar",
    "Speakers": "caixa_de_som", "Streaming_Devices": "tv_box", "TV_Tuner": "tv_box", "TVs": "tv",
    "Touchscreen_Displays": "monitor", "Toys": "brinquedo", "Universal_TV_Remotes": "tv", "VCR": "midia_fisica",
    "Vacuum_Cleaners": "aspirador", "Videoconferencing": "videoconferencia", "Whiteboards": "monitor",
    "Window_cleaners": "aspirador",
}


def metadados_flipper(rel: str) -> dict:
    partes = rel.replace("\\", "/").split("/")
    arquivo = partes[-1].rsplit(".", 1)[0]
    if partes[0] == "_Converted_":
        cat = None
        marca = partes[3] if len(partes) > 4 else (partes[2] if len(partes) > 3 else None)
    else:
        cat = _CAT_FLIPPER.get(partes[0])
        marca = partes[1] if len(partes) > 2 else None
    modelo = arquivo
    if marca and modelo.lower().startswith(marca.lower()):
        modelo = modelo[len(marca):].lstrip("_- ") or arquivo
    marca_txt = (marca or "").replace("_", " ").strip() or None
    nome = f"{marca_txt or ''} {modelo.replace('_', ' ')}".strip()
    return {"categoria": cat, "marca": marca_txt, "modelo": modelo.replace("_", " "), "nome": nome}


def importar_flipper(cat: Catalogo, raiz: str, arquivos: list[str] | None = None, fonte="flipper-irdb",
                     licenca="CC0-1.0 parcial", progresso=None, incluir_convertidos=True) -> dict:
    raiz_p = Path(raiz)
    if arquivos is None:
        arquivos = sorted(str(p.relative_to(raiz_p)) for p in raiz_p.rglob("*.ir"))
    if not incluir_convertidos:
        arquivos = [a for a in arquivos if not a.startswith("_Converted_")]
    ok = falhas = 0
    for i, rel in enumerate(arquivos):
        try:
            texto = (raiz_p / rel).read_text(errors="ignore")
            m = metadados_flipper(rel)
            p = formatos.ler_flipper(texto, f"flipper:{rel}", m["nome"], m["categoria"], m["marca"], m["modelo"],
                                     fonte, licenca)
            p["nome"] = m["nome"]
            cat.adicionar_perfil(p)
            ok += 1
        except (formatos.ErroFormato, OSError, ValueError):
            falhas += 1
        if progresso and i % 200 == 0:
            progresso(i, len(arquivos))
        if i % 1000 == 0:
            cat.commit()
    cat.commit()
    cat.registrar_fonte(fonte)
    return {"importados": ok, "falhas": falhas}


def importar_smartir(cat: Catalogo, raiz_codes: str, fonte="smartir", licenca="MIT", progresso=None) -> dict:
    ok = falhas = 0
    arquivos = sorted(Path(raiz_codes).glob("*/*.json"))
    for i, f in enumerate(arquivos):
        tipo = f.parent.name
        try:
            dados = json.loads(f.read_text(errors="ignore"))
            p = formatos.ler_smartir(dados, tipo, f"smartir:{tipo}/{f.stem}", fonte, licenca)
            cat.adicionar_perfil(p)
            ok += 1
        except (formatos.ErroFormato, ValueError, KeyError, TypeError, AttributeError):
            falhas += 1
        if progresso and i % 50 == 0:
            progresso(i, len(arquivos))
    cat.commit()
    cat.registrar_fonte(fonte)
    return {"importados": ok, "falhas": falhas}


def exportar_jsonl(perfis, destino: str):
    with gzip.open(destino, "wt", encoding="utf-8", compresslevel=9) as f:
        for p in perfis:
            f.write(json.dumps(p, ensure_ascii=False, separators=(",", ":")) + "\n")


def importar_jsonl(cat: Catalogo, origem: str, progresso=None) -> dict:
    ok = falhas = 0
    fontes = set()
    with gzip.open(origem, "rt", encoding="utf-8") as f:
        for i, linha in enumerate(f):
            try:
                p = json.loads(linha)
                cat.adicionar_perfil(p)
                fontes.add(p.get("fonte"))
                ok += 1
            except (ValueError, KeyError, ErroSinal):
                falhas += 1
            if progresso and i % 100 == 0:
                progresso(i, None)
    cat.commit()
    for fo in fontes:
        if fo:
            cat.registrar_fonte(fo)
    return {"importados": ok, "falhas": falhas}
