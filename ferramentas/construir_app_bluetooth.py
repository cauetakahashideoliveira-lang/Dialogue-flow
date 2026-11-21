"""Impressão digital dos fontes do app auxiliar de Bluetooth (usada pelo script de montagem e pelo teste)."""
import hashlib
from pathlib import Path

CAP = Path(__file__).resolve().parents[1] / "controle-ir" / "capacidades" / "bluetooth"


def fontes():
    return [CAP / "app" / "AndroidManifest.xml", CAP / "java" / "controleir" / "Bluetooth.java",
            *sorted((CAP / "app" / "java").rglob("*.java"))]


def impressao():
    h = hashlib.sha256()
    for f in fontes():
        h.update(f.relative_to(CAP).as_posix().encode() + b"\0" + f.read_bytes() + b"\0")
    return h.hexdigest()


if __name__ == "__main__":
    print(impressao())
