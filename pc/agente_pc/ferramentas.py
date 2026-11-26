"""Ferramentas pc_* do conector: o que o Claude pode fazer no PC.

Todas passam pela Central (assinadas) e pelo guardião local (servidor.py): desarmado, só pc_consultar e pc_travar.
"""
from __future__ import annotations

import base64 as b64mod
import fnmatch
import os
import subprocess
import threading
import time
from pathlib import Path

from . import __version__, sistema
from .config import REPO
from .tarefas import Tarefas
from .tela import Tela

TEXTO_MAX = 200_000  # caracteres por leitura de arquivo
BINARIO_MAX = 8 * 2**20  # bytes por leitura/escrita em base64
IMAGENS = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}


def _obj(props: dict, req: list | None = None) -> dict:
    d = {"type": "object", "properties": props, "additionalProperties": False}
    if req:
        d["required"] = req
    return d


S = {"type": "string"}
N = {"type": "number"}
B = {"type": "boolean"}

DEFINICOES = [
    {"name": "pc_consultar", "title": "Consultar o PC",
     "description": "PC Windows do dono (agente na Central): sistema, CPU, memória, discos, placa de vídeo (nvidia-smi), "
                    "programas instalados (git, python, node, rojo, ollama, Roblox Studio…), tarefas rodando e se o PC "
                    "está armado. Sempre responde, mesmo desarmado.",
     "inputSchema": _obj({})},
    {"name": "pc_executar", "title": "Executar um comando no PC",
     "description": "Roda um comando no PC (PowerShell por padrão; cmd, pwsh ou bash) como tarefa numerada, com os "
                    "direitos do usuário em modo administrador. Espera até 'aguardar' s (máx. 55) e devolve status e o "
                    "fim da saída; o que demorar mais continua rodando: acompanhe com pc_tarefa. Scripts longos podem "
                    "ir inteiros no comando (vão para um .ps1).",
     "inputSchema": _obj({"comando": S, "shell": {"type": "string", "enum": ["powershell", "pwsh", "cmd", "bash"]},
                          "pasta": {"type": "string", "description": "diretório de trabalho (padrão: pasta do usuário)"},
                          "aguardar": {"type": "number", "description": "segundos para esperar (padrão 30, máx. 55)"},
                          "tempo_limite": {"type": "number", "description": "segundos até encerrar (padrão 600, máx. 86400)"},
                          "motivo": {"type": "string", "description": "por quê (fica no histórico da Central)"}},
                         ["comando"])},
    {"name": "pc_tarefa", "title": "Acompanhar ou parar uma tarefa do PC",
     "description": "acao=ver (padrão; 'aguardar' até 55 s pelo fim, 'desde' para ler a saída a partir de um byte), "
                    "parar (encerra a árvore de processos) ou listar.",
     "inputSchema": _obj({"id": S, "acao": {"type": "string", "enum": ["ver", "parar", "listar"]},
                          "aguardar": N, "desde": N})},
    {"name": "pc_ler_arquivo", "title": "Ler um arquivo do PC",
     "description": "Lê um arquivo de texto (UTF-8) por linhas: 'inicio' (1 = primeira) e 'linhas' (padrão 2000). "
                    "Imagens (png/jpg/gif/webp) voltam como imagem; modo=base64 lê qualquer arquivo binário (até 8 MB).",
     "inputSchema": _obj({"caminho": S, "inicio": N, "linhas": N,
                          "modo": {"type": "string", "enum": ["auto", "texto", "base64"]}}, ["caminho"])},
    {"name": "pc_escrever_arquivo", "title": "Escrever um arquivo no PC",
     "description": "Cria ou substitui um arquivo (texto UTF-8 em 'conteudo', ou binário em 'base64'); cria as pastas "
                    "que faltarem. acrescentar=true escreve no fim.",
     "inputSchema": _obj({"caminho": S, "conteudo": S, "base64": S, "acrescentar": B}, ["caminho"])},
    {"name": "pc_editar_arquivo", "title": "Editar um trecho de arquivo no PC",
     "description": "Troca 'antigo' por 'novo' num arquivo de texto. 'antigo' precisa aparecer exatamente uma vez "
                    "(ou use todas=true). Mantém a codificação e as quebras de linha do arquivo.",
     "inputSchema": _obj({"caminho": S, "antigo": S, "novo": S, "todas": B}, ["caminho", "antigo", "novo"])},
    {"name": "pc_listar", "title": "Listar arquivos do PC",
     "description": "Lista uma pasta (padrão: pasta do usuário), com filtro (ex.: *.luau) e opção recursiva (máx. 500 itens; "
                    "pula .git e node_modules).",
     "inputSchema": _obj({"caminho": S, "padrao": S, "recursivo": B, "maximo": N})},
    {"name": "pc_tela", "title": "Ver a tela do PC",
     "description": "Captura a tela (todos os monitores, ou monitor=1, 2…) e devolve a imagem. Use antes do pc_entrada.",
     "inputSchema": _obj({"monitor": N, "largura": {"type": "number", "description": "largura máxima (padrão 1600)"},
                          "qualidade": N})},
    {"name": "pc_entrada", "title": "Mouse e teclado do PC",
     "description": "acao: clicar, duplo, direito, meio, mover, arrastar (x2,y2), rolar (quantidade: negativo desce), "
                    "digitar (texto) ou teclas (formato SendKeys: ^s = Ctrl+S, %{F4} = Alt+F4, {ENTER}). x,y nas "
                    "coordenadas da última imagem do pc_tela (coordenadas=tela para pixels reais).",
     "inputSchema": _obj({"acao": {"type": "string", "enum": ["clicar", "duplo", "direito", "meio", "mover", "arrastar",
                                                               "rolar", "digitar", "teclas"]},
                          "x": N, "y": N, "x2": N, "y2": N, "texto": S, "teclas": S, "quantidade": N,
                          "coordenadas": {"type": "string", "enum": ["imagem", "tela"]}}, ["acao"])},
    {"name": "pc_atualizar", "title": "Atualizar o agente do PC",
     "description": "Atualiza o agente pelo Git (git pull no repositório dialogue-flow do PC, ou checkout de 'ref') e "
                    "reinicia o agente. A conexão volta sozinha em alguns segundos.",
     "inputSchema": _obj({"ref": S})},
    {"name": "pc_travar", "title": "Travar o PC agora",
     "description": "Encerra todas as tarefas e bloqueia as ferramentas do PC (menos consultar) até o dono armar de novo "
                    "na Central. Sempre responde.",
     "inputSchema": _obj({"motivo": S})},
]
NOMES = {d["name"] for d in DEFINICOES}


def _caminho(c: str) -> Path:
    if not c:
        raise ValueError("informe o caminho")
    return Path(os.path.expandvars(os.path.expanduser(str(c))))


class Ferramentas:
    def __init__(self, pasta: Path, auditar, estado_seguranca, travar_local, canal=None, ao_reiniciar=None):
        self.pasta = Path(pasta)
        self.auditar = auditar
        self.estado_seguranca = estado_seguranca
        self.travar_local = travar_local
        self.canal = canal
        self.ao_reiniciar = ao_reiniciar or (lambda: os._exit(3))
        self.tarefas = Tarefas(self.pasta, auditar)
        self.tela = Tela()

    def chamar(self, nome: str, args: dict) -> dict:
        fn = getattr(self, nome, None)
        if nome not in NOMES or not fn:
            raise ValueError(f"ferramenta desconhecida: {nome}")
        return fn(**(args or {}))

    # ------------------------------------------------------------- ferramentas
    def pc_consultar(self) -> dict:
        r = {"agente": __version__, "repositorio": str(REPO), "seguranca": self.estado_seguranca(),
             "pc": sistema.retrato(), "tarefas_rodando": [{"id": t["id"], "comando": t["comando"][:120]}
                                                           for t in self.tarefas.ativas()]}
        if self.canal:
            r["canal"] = self.canal.estado()
        return r

    def pc_executar(self, comando: str, shell: str | None = None, pasta: str | None = None, aguardar: float = 30,
                    tempo_limite: float = 600, motivo: str | None = None) -> dict:
        return self.tarefas.pedir(comando, shell, pasta, aguardar, tempo_limite, motivo)

    def pc_tarefa(self, id: str | None = None, acao: str = "ver", aguardar: float = 0, desde: int | None = None) -> dict:
        if acao == "listar" or not id:
            return {"tarefas": self.tarefas.listar()}
        if acao == "parar":
            return self.tarefas.parar(id)
        return self.tarefas.ver(id, desde, aguardar)

    def pc_ler_arquivo(self, caminho: str, inicio: int = 1, linhas: int = 2000, modo: str = "auto") -> dict:
        p = _caminho(caminho)
        if not p.is_file():
            raise ValueError(f"arquivo não existe: {p}")
        tam = p.stat().st_size
        ext = p.suffix.lower()
        if modo == "base64" or (modo == "auto" and ext in IMAGENS):
            if tam > BINARIO_MAX:
                raise ValueError(f"arquivo grande demais para base64 ({tam} bytes; máx. {BINARIO_MAX})")
            dados = b64mod.b64encode(p.read_bytes()).decode()
            if modo == "auto":
                return {"caminho": str(p), "tamanho": tam, "_imagem": {"base64": dados, "mime": IMAGENS[ext]}}
            return {"caminho": str(p), "tamanho": tam, "base64": dados}
        bruto = p.read_bytes()
        if b"\0" in bruto[:8192]:
            raise ValueError("parece binário: use modo=base64")
        texto = bruto.decode("utf-8-sig", errors="replace")
        todas = texto.splitlines()
        inicio = max(1, int(inicio or 1))
        linhas = max(1, min(int(linhas or 2000), 20000))
        trecho = todas[inicio - 1:inicio - 1 + linhas]
        conteudo = "\n".join(f"{inicio + i:6}\t{l}" for i, l in enumerate(trecho))
        r = {"caminho": str(p), "tamanho": tam, "total_linhas": len(todas), "de": inicio,
             "ate": inicio + len(trecho) - 1, "conteudo": conteudo[:TEXTO_MAX]}
        if len(conteudo) > TEXTO_MAX or inicio - 1 + linhas < len(todas):
            r["mais"] = f"continue com inicio={inicio + len(trecho)}"
        return r

    def pc_escrever_arquivo(self, caminho: str, conteudo: str | None = None, base64: str | None = None,
                            acrescentar: bool = False) -> dict:
        p = _caminho(caminho)
        if conteudo is None and base64 is None:
            raise ValueError("informe conteudo (texto) ou base64")
        dados = b64mod.b64decode(base64) if base64 is not None else conteudo.encode("utf-8")
        if len(dados) > BINARIO_MAX * 4:
            raise ValueError("conteúdo grande demais")
        p.parent.mkdir(parents=True, exist_ok=True)
        if acrescentar:
            with open(p, "ab") as f:
                f.write(dados)
        else:
            tmp = p.with_name(p.name + ".agente-novo")
            tmp.write_bytes(dados)
            os.replace(tmp, p)
        self.auditar({"evento": "pc_arquivo_escrito", "caminho": str(p)[:300], "bytes": len(dados)})
        return {"caminho": str(p), "bytes": len(dados), "acrescentado": bool(acrescentar)}

    def pc_editar_arquivo(self, caminho: str, antigo: str, novo: str, todas: bool = False) -> dict:
        p = _caminho(caminho)
        bruto = p.read_bytes()
        bom = bruto.startswith(b"\xef\xbb\xbf")
        texto = bruto[3:].decode("utf-8") if bom else bruto.decode("utf-8")
        crlf = "\r\n" in texto
        if crlf and "\r\n" not in antigo:  # o Claude manda \n; o arquivo usa \r\n
            antigo, novo = antigo.replace("\n", "\r\n"), novo.replace("\n", "\r\n")
        n = texto.count(antigo)
        if n == 0:
            raise ValueError("trecho 'antigo' não encontrado")
        if n > 1 and not todas:
            raise ValueError(f"trecho 'antigo' aparece {n} vezes: dê mais contexto ou use todas=true")
        texto = texto.replace(antigo, novo) if todas else texto.replace(antigo, novo, 1)
        tmp = p.with_name(p.name + ".agente-novo")
        tmp.write_bytes((b"\xef\xbb\xbf" if bom else b"") + texto.encode("utf-8"))
        os.replace(tmp, p)
        self.auditar({"evento": "pc_arquivo_editado", "caminho": str(p)[:300], "trocas": n if todas else 1})
        return {"caminho": str(p), "trocas": n if todas else 1}

    def pc_listar(self, caminho: str | None = None, padrao: str = "*", recursivo: bool = False, maximo: int = 200) -> dict:
        base = _caminho(caminho) if caminho else Path.home()
        if not base.is_dir():
            raise ValueError(f"pasta não existe: {base}")
        maximo = max(1, min(int(maximo or 200), 500))
        itens, cortado = [], False
        for raiz, pastas, arquivos in os.walk(base):
            pastas[:] = sorted(d for d in pastas if d not in (".git", "node_modules", "__pycache__"))
            for nome in sorted(pastas) + sorted(arquivos):
                if not fnmatch.fnmatch(nome.lower(), (padrao or "*").lower()):
                    continue
                c = Path(raiz) / nome
                try:
                    st = c.stat()
                except OSError:
                    continue
                itens.append({"caminho": str(c.relative_to(base)), "tipo": "pasta" if c.is_dir() else "arquivo",
                              "bytes": None if c.is_dir() else st.st_size,
                              "modificado": time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime))})
                if len(itens) >= maximo:
                    cortado = True
                    break
            if cortado or not recursivo:
                break
        return {"pasta": str(base), "itens": itens, **({"cortado_em": maximo} if cortado else {})}

    def pc_tela(self, monitor: int = 0, largura: int = 1600, qualidade: int = 70) -> dict:
        return self.tela.capturar(monitor, largura, qualidade)

    def pc_entrada(self, acao: str, **kw) -> dict:
        r = self.tela.entrada(acao, **kw)
        self.auditar({"evento": "pc_entrada", "acao": acao})
        return r

    def pc_atualizar(self, ref: str | None = None) -> dict:
        def git(*a):
            return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True, timeout=120,
                                  creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        antes = git("rev-parse", "--short", "HEAD").stdout.strip()
        if ref:
            r = git("fetch", "origin", ref)
            r = r if r.returncode else git("checkout", "--detach", "FETCH_HEAD")
        else:
            r = git("pull", "--ff-only")
        if r.returncode:
            raise ValueError(f"git falhou: {(r.stderr or r.stdout).strip()[-400:]}")
        depois = git("rev-parse", "--short", "HEAD").stdout.strip()
        self.auditar({"evento": "pc_atualizado", "de": antes, "para": depois})
        threading.Timer(1.5, self.ao_reiniciar).start()  # responde antes de reiniciar
        return {"de": antes, "para": depois, "reiniciando": True,
                "dica": "a ferramenta volta em ~10 s; confira com pc_consultar"}

    def pc_travar(self, motivo: str | None = None) -> dict:
        n = self.tarefas.parar_todas()
        self.travar_local(motivo or "pc_travar")
        return {"travado": True, "tarefas_encerradas": n,
                "para_voltar": "o dono arma de novo na Central de Controle, com a digital"}
