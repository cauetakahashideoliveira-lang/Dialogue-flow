"""Capacidades plugáveis: ferramentas novas sem mexer no núcleo do servidor.

Uma capacidade é uma pasta com ``capacidade.json`` (manifesto) e um script
(``.py`` ou ``.sh``) que lê os argumentos em JSON pela entrada padrão e
escreve o resultado em JSON na saída padrão. O registro relê as pastas a cada
chamada: uma capacidade nova fica disponível sem reiniciar.

Pastas:
* ``<pacote>/capacidades/``          — embutidas, vêm com o instalador (confiáveis);
* ``~/.controle-ir/capacidades/``    — criadas pelo usuário/Claude, só rodam aprovadas;
* ``~/.controle-ir/capacidades/_propostas/`` — aguardando aprovação no celular.

A aprovação grava o SHA-256 dos arquivos: se o código mudar depois, a
capacidade volta a exigir aprovação. ``propor`` nunca executa nada.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

NOME_OK = re.compile(r"^[a-z][a-z0-9_]{1,39}$")
LIMITE_ARQUIVOS = 100_000
LIMITE_SAIDA = 200_000
TIPOS = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "object": dict, "array": list}


class ErroCapacidade(ValueError):
    pass


def _hash(pasta: Path) -> str:
    """SHA-256 de todos os arquivos (subpastas incluídas), exceto os de controle (.aprovacao, .notas) e cache."""
    h = hashlib.sha256()
    for f in sorted(pasta.rglob("*")):
        rel = f.relative_to(pasta)
        if f.is_file() and not any(p.startswith(".") or p == "__pycache__" for p in rel.parts):
            h.update(str(rel).encode() + b"\0" + f.read_bytes() + b"\0")
    return h.hexdigest()


def _manifesto(pasta: Path) -> dict:
    m = json.loads((pasta / "capacidade.json").read_text())
    if m.get("nome") != pasta.name or not NOME_OK.match(pasta.name):
        raise ErroCapacidade(f"manifesto de {pasta.name}: o nome deve ser igual ao da pasta (a-z, 0-9, _)")
    if not (pasta / m.get("executar", "")).is_file() or Path(m["executar"]).suffix not in (".py", ".sh"):
        raise ErroCapacidade(f"{pasta.name}: 'executar' deve apontar para um .py ou .sh da pasta")
    m.setdefault("entrada", {})
    return m


class Registro:
    def __init__(self, embutidas: Path, pasta_usuario: Path, notificar=None):
        self.embutidas = Path(embutidas)
        self.usuario = Path(pasta_usuario) / "capacidades"
        self.propostas = self.usuario / "_propostas"
        self.notificar = notificar

    # ------------------------------------------------------------- leitura
    def _pastas(self) -> dict[str, tuple[Path, str]]:
        out: dict[str, tuple[Path, str]] = {}
        for raiz, origem in ((self.embutidas, "embutida"), (self.usuario, "usuario")):
            if raiz.is_dir():
                for p in sorted(raiz.iterdir()):
                    if p.is_dir() and not p.name.startswith(("_", ".")) and (p / "capacidade.json").exists():
                        out.setdefault(p.name, (p, origem))  # embutida vence homônima do usuário
        return out

    def _estado(self, pasta: Path, origem: str) -> str:
        if origem == "embutida":
            return "ativa"
        try:
            ap = json.loads((pasta / ".aprovacao.json").read_text())
        except (OSError, ValueError):
            return "sem_aprovacao"
        return "ativa" if ap.get("sha256") == _hash(pasta) else "alterada_reaprovar"

    def listar(self) -> list[dict]:
        out = []
        for nome, (pasta, origem) in self._pastas().items():
            try:
                m = _manifesto(pasta)
            except (ErroCapacidade, OSError, ValueError) as e:
                out.append({"nome": nome, "estado": "invalida", "erro": str(e)[:200]})
                continue
            out.append({"nome": nome, "titulo": m.get("titulo"), "descricao": m.get("descricao"),
                        "efeito": m.get("efeito", "leitura"), "acessos": m.get("acessos", []),
                        "entrada": m["entrada"], "origem": origem, "estado": self._estado(pasta, origem),
                        "notas": self._notas(pasta)[-5:]})
        for p in sorted(self.propostas.glob("*/")) if self.propostas.is_dir() else []:
            out.append({"nome": p.name, "estado": "aguardando_aprovacao"})
        return out

    def ativas(self) -> list[dict]:
        return [c for c in self.listar() if c.get("estado") == "ativa"]

    def ver(self, nome: str, proposta: bool = False) -> dict:
        pasta = (self.propostas / nome) if proposta else self._pastas().get(nome, (None,))[0]
        if not pasta or not pasta.is_dir():
            raise ErroCapacidade(f"capacidade “{nome}” não encontrada")
        arquivos = {str(f.relative_to(pasta)): f.read_text(errors="replace")[:20000] for f in sorted(pasta.rglob("*"))
                    if f.is_file() and not any(x.startswith(".") or x == "__pycache__"
                                               for x in f.relative_to(pasta).parts)}
        return {"nome": nome, "pasta": str(pasta), "arquivos": arquivos, "sha256": _hash(pasta)}

    @staticmethod
    def _notas(pasta: Path) -> list:
        try:
            return json.loads((pasta / ".notas.json").read_text())
        except (OSError, ValueError):
            return []

    def anotar(self, nome: str, nota: str) -> dict:
        pasta = self._pastas().get(nome, (None,))[0]
        if not pasta:
            raise ErroCapacidade(f"capacidade “{nome}” não encontrada")
        notas = self._notas(pasta) + [{"quando": time.strftime("%d/%m/%Y %H:%M"), "nota": str(nota)[:500]}]
        destino = pasta / ".notas.json" if os.access(pasta, os.W_OK) else None
        if destino is None:
            raise ErroCapacidade("pasta sem permissão de escrita")
        destino.write_text(json.dumps(notas[-50:], ensure_ascii=False, indent=1))
        return {"capacidade": nome, "notas": notas[-5:]}

    # ------------------------------------------------------------- execução
    @staticmethod
    def _validar(entrada: dict, args: dict):
        props = entrada.get("properties", {})
        for k in entrada.get("required", []):
            if k not in args:
                raise ErroCapacidade(f"falta o argumento obrigatório “{k}”")
        for k, v in args.items():
            if k not in props:
                raise ErroCapacidade(f"argumento desconhecido “{k}”; aceitos: {', '.join(props) or 'nenhum'}")
            tipo = TIPOS.get(props[k].get("type"))
            if tipo and (not isinstance(v, tipo) or (props[k].get("type") in ("integer", "number")
                                                      and isinstance(v, bool))):
                raise ErroCapacidade(f"“{k}” deve ser {props[k].get('type')}")

    def executar(self, nome: str, args: dict | None = None, ambiente: dict | None = None) -> dict:
        args = args or {}
        achada = self._pastas().get(nome)
        if not achada:
            props = [p.name for p in self.propostas.glob("*/")] if self.propostas.is_dir() else []
            dica = " Ela ainda aguarda aprovação no celular." if nome in props else ""
            raise ErroCapacidade(f"capacidade “{nome}” não está ativa.{dica}")
        pasta, origem = achada
        estado = self._estado(pasta, origem)
        if estado != "ativa":
            raise ErroCapacidade(f"capacidade “{nome}” bloqueada ({estado}): aprove no celular com "
                                 f"controle-ir capacidade aprovar {nome}")
        m = _manifesto(pasta)
        self._validar(m["entrada"], args)
        script = pasta / m["executar"]
        cmd = [sys.executable, str(script)] if script.suffix == ".py" else [shutil.which("sh") or "sh", str(script)]
        env = dict(os.environ, **(ambiente or {}))
        t0 = time.monotonic()
        try:
            r = subprocess.run(cmd, input=json.dumps(args), capture_output=True, text=True, cwd=str(pasta),
                               timeout=float(m.get("tempo_limite", 60)), env=env)
        except subprocess.TimeoutExpired:
            return {"capacidade": nome, "status": "tempo_esgotado", "tempo_limite_s": m.get("tempo_limite", 60)}
        dur = round(time.monotonic() - t0, 2)
        saida = (r.stdout or "")[:LIMITE_SAIDA]
        try:
            dados = json.loads(saida) if saida.strip() else {}
        except ValueError:
            dados = {"saida_texto": saida[-4000:]}
        out = {"capacidade": nome, "status": "ok" if r.returncode == 0 else "falhou", "segundos": dur,
               "resultado": dados}
        if r.returncode != 0:
            out["codigo"] = r.returncode
            out["erro"] = (r.stderr or "")[-2000:]
        return out

    # ------------------------------------------------------------- criação com aprovação
    def propor(self, nome: str, manifesto: dict, arquivos: dict) -> dict:
        if not NOME_OK.match(str(nome or "")):
            raise ErroCapacidade("nome inválido: use 2–40 caracteres a-z, 0-9 e _ começando por letra")
        if nome in self._pastas() and self._pastas()[nome][1] == "embutida":
            raise ErroCapacidade(f"“{nome}” é uma capacidade embutida; escolha outro nome")
        if not isinstance(arquivos, dict) or not arquivos:
            raise ErroCapacidade("arquivos deve ser {nome_do_arquivo: conteúdo}")
        total = sum(len(str(v)) for v in arquivos.values())
        if total > LIMITE_ARQUIVOS:
            raise ErroCapacidade(f"arquivos grandes demais ({total} caracteres; limite {LIMITE_ARQUIVOS})")
        for f in arquivos:
            if not re.match(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,60}$", f) or f == "capacidade.json":
                raise ErroCapacidade(f"nome de arquivo inválido: {f}")
        m = dict(manifesto or {}, nome=nome)
        destino = self.propostas / nome
        if destino.exists():
            shutil.rmtree(destino)
        destino.mkdir(parents=True)
        for f, conteudo in arquivos.items():
            (destino / f).write_text(str(conteudo))
        (destino / "capacidade.json").write_text(json.dumps(m, ensure_ascii=False, indent=1))
        try:
            _manifesto(destino)
        except (ErroCapacidade, ValueError) as e:
            shutil.rmtree(destino)
            raise ErroCapacidade(str(e)) from e
        sha = _hash(destino)
        if self.notificar:
            self.notificar({"tipo": "capacidade_proposta", "nome": nome, "descricao": m.get("descricao", ""),
                            "sha256": sha})
        return {"capacidade": nome, "status": "aguardando_aprovacao", "sha256": sha,
                "orientacao": "Nada foi executado. Peça ao usuário para tocar em “Aprovar” na notificação do "
                              "celular (ou rodar  controle-ir capacidade aprovar " + nome + "). Depois chame "
                              "executar_capacidade."}

    def aprovar(self, nome: str, sha: str | None = None) -> dict:
        """sha: início do SHA-256 que o usuário revisou (o botão da notificação sempre envia). Se o código
        mudou depois da notificação (nova proposta com o mesmo nome), a aprovação é recusada."""
        prop = self.propostas / nome
        alvo = self.usuario / nome
        atual = _hash(prop) if prop.is_dir() else (_hash(alvo) if alvo.is_dir() else None)
        if sha is not None and (not atual or not sha or not atual.startswith(sha)):
            raise ErroCapacidade(f"o código de “{nome}” mudou depois da notificação (esperado {sha[:16] or '?'}, "
                                 f"atual {(atual or '?')[:16]}): veja o código de novo antes de aprovar")
        if prop.is_dir():
            if alvo.exists():
                shutil.rmtree(alvo)
            shutil.move(str(prop), str(alvo))
        elif not alvo.is_dir():
            raise ErroCapacidade(f"não há proposta nem capacidade “{nome}”")
        sha = _hash(alvo)
        (alvo / ".aprovacao.json").write_text(json.dumps({"sha256": sha, "quando": time.time()}))
        return {"capacidade": nome, "status": "ativa", "sha256": sha}

    def recusar(self, nome: str) -> dict:
        prop = self.propostas / nome
        if not prop.is_dir():
            raise ErroCapacidade(f"não há proposta “{nome}”")
        shutil.rmtree(prop)
        return {"capacidade": nome, "status": "recusada"}

    def remover(self, nome: str) -> dict:
        alvo = self.usuario / nome
        if not alvo.is_dir():
            raise ErroCapacidade(f"“{nome}” não é uma capacidade do usuário")
        shutil.rmtree(alvo)
        return {"capacidade": nome, "status": "removida"}


def resumo_instrucoes(ativas: list[dict]) -> str:
    if not ativas:
        return ""
    linhas = [f"- {c['nome']}: {c.get('descricao') or c.get('titulo') or ''}"[:200] for c in ativas]
    return ("Capacidades extras (chame executar_capacidade(nome, argumentos); veja os argumentos em "
            "capacidades(acao='listar')). Uma necessidade nova pode virar capacidade com propor_capacidade, "
            "que só roda depois de o usuário aprovar no celular:\n" + "\n".join(linhas))
