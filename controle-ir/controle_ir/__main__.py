import os
import sys

from .cli import main

try:
    sys.exit(main())
except BrokenPipeError:
    # saída ligada a "| head" ou "| grep -q" (como no instalar.sh): quem lê fechou o cano; sair sem rastro
    os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    sys.exit(0)
