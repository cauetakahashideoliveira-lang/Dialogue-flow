"""Empacota os arquivos versionados do celular ou confere o ZIP já publicado."""
import argparse
import hashlib
import os
import stat
import subprocess
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

RAIZ = Path(__file__).resolve().parents[1]
ZIP = RAIZ / "dist/controle-ir.zip"
SOMA = ZIP.with_suffix(".zip.sha256")


def fontes():
    registros = subprocess.check_output(
        ["git", "ls-files", "--stage", "-z", "--", "controle-ir/"], cwd=RAIZ)
    arquivos = {}
    for registro in registros.split(b"\0"):
        if not registro:
            continue
        meta, nome = registro.split(b"\t", 1)
        modo, _, estagio = meta.split()
        nome = os.fsdecode(nome)
        if estagio != b"0" or modo not in (b"100644", b"100755") or (RAIZ / nome).is_symlink():
            raise ValueError(f"Arquivo não empacotável: {nome}")
        arquivos[nome] = int(modo, 8)
    if not arquivos:
        raise ValueError("O índice do Git não contém os fontes de controle-ir/")
    return arquivos


def checksum():
    return hashlib.sha256(ZIP.read_bytes()).hexdigest() + "  controle-ir.zip\n"


def empacotar(arquivos):
    ZIP.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ZIP.parent) as tmp:
        saida = Path(tmp) / ZIP.name
        with ZipFile(saida, "w") as z:
            for nome, modo in arquivos.items():
                info = ZipInfo(nome)  # data estável independentemente do checkout
                info.create_system = 3
                info.external_attr = modo << 16
                z.writestr(info, (RAIZ / nome).read_bytes(), compress_type=ZIP_DEFLATED, compresslevel=9)
        saida.replace(ZIP)
        soma = Path(tmp) / SOMA.name
        soma.write_text(checksum(), encoding="ascii")
        soma.replace(SOMA)


def verificar(arquivos):
    if SOMA.read_text(encoding="ascii") != checksum():
        raise ValueError("SHA-256 diferente do manifesto em dist/")
    with ZipFile(ZIP) as z:
        entradas = [info for info in z.infolist() if not info.is_dir()]
        nomes = [info.filename for info in entradas]
        if len(nomes) != len(set(nomes)) or set(nomes) != arquivos.keys():
            raise ValueError("O ZIP e o índice do Git têm listas de arquivos diferentes")
        for info in entradas:
            nome = info.filename
            if z.read(info) != (RAIZ / nome).read_bytes():
                raise ValueError(f"Conteúdo divergente: {nome}")
            if stat.S_IMODE(info.external_attr >> 16) != stat.S_IMODE(arquivos[nome]):
                raise ValueError(f"Permissão divergente: {nome}")
    print(f"{len(arquivos)} arquivos conferidos. SHA-256 {checksum().split()[0]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verificar", action="store_true", help="conferir a distribuição sem regravá-la")
    args = parser.parse_args()
    arquivos = fontes()
    if not args.verificar:
        empacotar(arquivos)
    verificar(arquivos)
