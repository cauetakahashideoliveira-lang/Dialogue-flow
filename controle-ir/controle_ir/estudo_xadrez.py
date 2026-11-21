"""Estudo local com Stockfish e controle do piloto no tabuleiro do Chess.com."""
import json
import shutil
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

INICIAL = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
PECAS = dict(zip("KQRBNPkqrbnp", "♔♕♖♗♘♙♚♛♜♝♞♟"))
ARQUIVO = "stockfish.json"


@dataclass(frozen=True)
class Preferencias:
    nivel: int = 20
    ms_lance: int | None = None

    def resumo(self):
        if self.ms_lance is None:
            tempo = "automático (0,5 s no estudo e de 0,2 a 0,1 s no piloto)"
        else:
            tempo = f"{self.ms_lance / 1000:g} s por lance".replace(".", ",")
        return f"Nível {self.nivel}/20 • tempo {tempo}"


def ler_preferencias(pasta):
    try:
        dados = json.loads((pasta / ARQUIVO).read_text())
    except (FileNotFoundError, ValueError):
        return Preferencias()
    if not isinstance(dados, dict):
        return Preferencias()
    nivel, ms = dados.get("nivel"), dados.get("ms_lance")
    return Preferencias(nivel if type(nivel) is int and 0 <= nivel <= 20 else 20,
                        ms if type(ms) is int and 50 <= ms <= 30000 else None)


def configurar(pasta):
    atual = ler_preferencias(pasta)
    print(atual.resumo())
    print("Enter mantém o valor atual.")
    while True:
        valor = input("Nível de habilidade (0 a 20) › ").strip()
        if not valor:
            nivel = atual.nivel
            break
        try:
            nivel = int(valor)
            if 0 <= nivel <= 20:
                break
        except ValueError:
            pass
        print("Digite um número inteiro de 0 a 20.")
    while True:
        valor = input("Tempo por lance em segundos (0,05 a 30, ou auto) › ").strip().lower()
        if not valor:
            ms = atual.ms_lance
            break
        if valor == "auto":
            ms = None
            break
        try:
            segundos = float(valor.replace(",", "."))
            if 0.05 <= segundos <= 30:
                ms = round(segundos * 1000)
                break
        except ValueError:
            pass
        print("Digite o tempo em segundos, por exemplo 0,5, ou auto.")
    nova = Preferencias(nivel, ms)
    pasta.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=pasta) as tmp:
        arquivo = Path(tmp) / ARQUIVO
        arquivo.write_text(json.dumps(asdict(nova)) + "\n")
        arquivo.replace(pasta / ARQUIVO)
    print("Salvo.", nova.resumo())
    return nova


def mostrar(fen):
    for n, linha in enumerate(fen.split()[0].split("/")):
        casas = []
        for c in linha:
            casas.extend(["·"] * int(c) if c.isdigit() else [PECAS[c]])
        print(f"{8-n}  " + " ".join(casas))
    print("   a b c d e f g h")


def estudar(motor):
    from .cli import PASTA
    posicoes = [INICIAL]
    prefs = ler_preferencias(PASTA)
    motor.definir_nivel(prefs.nivel)
    print("Stockfish •", prefs.resumo())
    print("Digite configurar para escolher o nível e o tempo de pensamento.")
    print("Sugestão inicial:", motor.lance(INICIAL, prefs.ms_lance or 500))
    print("Digite um lance (e2e4) ou uma sequência (e2e4 e7e5).")
    print("Enter sugere um lance. Digite voltar para desfazer ou sair para encerrar.")
    print("Chess.com: digite piloto para jogar ou parar para desligar. Se precisar indicar sua vez, use piloto agora.")
    while True:
        atual = posicoes[-1]
        mostrar(atual)
        vez = "Brancas" if atual.split()[1] == "w" else "Pretas"
        linha = input(f"{vez} › ").strip().lower()
        if linha in ("sair", "piloto", "piloto agora", "parar"):
            return linha
        if linha == "configurar":
            prefs = configurar(PASTA)
            motor.definir_nivel(prefs.nivel)
            continue
        if linha == "voltar":
            if len(posicoes) > 1:
                posicoes.pop()
            continue
        if not linha:
            lance = motor.lance(atual, prefs.ms_lance or 500)
            print("Sugestão:", lance if lance and lance != "0000" else "partida encerrada")
            continue
        novas = []
        for lance in linha.split():
            proxima = motor.fen_apos_lance_legal(atual, lance)
            if proxima is None:
                print(f"Lance inválido: {lance}. A posição anterior foi mantida.")
                break
            novas.append(proxima)
            atual = proxima
        else:
            posicoes.extend(novas)


def piloto_local(iniciar, minha_vez=False):
    from . import cli
    if not cli.servico_ativo():
        if not iniciar:
            print("O serviço local está desligado.")
            return
        cli.iniciar_em_segundo_plano()
        limite = time.monotonic() + 20
        while not cli.servico_ativo():
            if time.monotonic() >= limite:
                print("O serviço do POCO não iniciou. Consulte controle-ir log.")
                return
            time.sleep(0.5)
    dados = {"acao":"parar"}
    if iniciar:
        preparo = cli._api("stockfish", {"acao":"preparar"}, sair=False)
        if "pedido" not in preparo:
            print(preparo.get("erro", "Não foi possível preparar o piloto."))
            return
        dados = {"acao":"iniciar", "pedido":preparo["pedido"], "minha_vez":minha_vez}
    while True:
        resposta = cli._api("stockfish", dados, sair=False)
        if not resposta.get("aguardar_tabuleiro"):
            cli._aviso(resposta.get("mensagem") or resposta.get("erro") or "Resposta local inesperada.")
            return
        time.sleep(1)


def abrir(acao=None):
    from .cli import PACOTE, PASTA
    from .capacidades import modulo_embutido
    try:
        if acao == "configurar":
            configurar(PASTA)
            return 0
        if not shutil.which("stockfish"):
            print("Instale o motor uma vez no Termux com: pkg install stockfish")
            return 1
        tela = modulo_embutido(PACOTE / "capacidades" / "tela", "tela")
        motor = tela._modulo_piloto().Motor(threads=2, hash_mb=64)
        try:
            acao = estudar(motor)
        finally:
            motor.fechar()
        if acao in ("piloto", "piloto agora", "parar"):
            piloto_local(acao != "parar", minha_vez=acao == "piloto agora")
    except (EOFError, KeyboardInterrupt):
        print()
    except (OSError, RuntimeError) as exc:
        print(f"Stockfish não pôde continuar ({exc}).")
        return 1
    return 0
