"""Estudo local com Stockfish e acesso ao piloto de partidas contra robôs."""
import shutil
import time

INICIAL = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
PECAS = dict(zip("KQRBNPkqrbnp", "♔♕♖♗♘♙♚♛♜♝♞♟"))


def mostrar(fen):
    for n, linha in enumerate(fen.split()[0].split("/")):
        casas = []
        for c in linha:
            casas.extend(["·"] * int(c) if c.isdigit() else [PECAS[c]])
        print(f"{8-n}  " + " ".join(casas))
    print("   a b c d e f g h")


def estudar(motor):
    posicoes = [INICIAL]
    print("Stockfish • estudo no POCO")
    print("Sugestão inicial:", motor.lance(INICIAL, 500))
    print("Digite um lance (e2e4) ou uma sequência (e2e4 e7e5).")
    print("Enter sugere um lance. Digite voltar para desfazer ou sair para encerrar.")
    print("Para o Chess.com: digite piloto para ativar contra o robô ou parar para desligar.")
    while True:
        atual = posicoes[-1]
        mostrar(atual)
        vez = "Brancas" if atual.split()[1] == "w" else "Pretas"
        linha = input(f"{vez} › ").strip().lower()
        if linha in ("sair", "piloto", "parar"):
            return linha
        if linha == "voltar":
            if len(posicoes) > 1:
                posicoes.pop()
            continue
        if not linha:
            lance = motor.lance(atual, 500)
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


def piloto_local(iniciar):
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
        minha_vez = input("Já está no meio da partida e é a sua vez? [s/N] › ").strip().lower() == "s"
        preparo = cli._api("stockfish", {"acao":"preparar"}, sair=False)
        if "pedido" not in preparo:
            print(preparo.get("erro", "Não foi possível preparar o piloto."))
            return
        dados = {"acao":"iniciar", "pedido":preparo["pedido"], "minha_vez":minha_vez}
        cli._aviso("Volte à partida contra o robô no Chess.com em até 45 segundos.")
    limite = time.monotonic() + 45
    while True:
        resposta = cli._api("stockfish", dados, sair=False)
        if not resposta.get("aguardar_tabuleiro"):
            cli._aviso(resposta.get("mensagem") or resposta.get("erro") or "Resposta local inesperada.")
            return
        if time.monotonic() >= limite:
            cli._aviso("Tempo encerrado. Abra a partida contra o robô e tente novamente.")
            return
        time.sleep(1)


def abrir():
    from .cli import PACOTE
    from .capacidades import modulo_embutido
    try:
        if not shutil.which("stockfish"):
            print("Instale o motor uma vez no Termux com: pkg install stockfish")
            return 1
        tela = modulo_embutido(PACOTE / "capacidades" / "tela", "tela")
        motor = tela._modulo_piloto().Motor(threads=2, hash_mb=64)
        try:
            acao = estudar(motor)
        finally:
            motor.fechar()
        if acao in ("piloto", "parar"):
            piloto_local(acao == "piloto")
    except (EOFError, KeyboardInterrupt):
        print()
    except (OSError, RuntimeError) as exc:
        print(f"Stockfish não pôde continuar ({exc}).")
        return 1
    return 0
