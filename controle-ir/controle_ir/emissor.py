"""Acesso ao emissor infravermelho.

* ``EmissorTermux`` usa ``termux-infrared-transmit`` (Termux:API → ConsumerIrManager do Android);
* ``EmissorSimulado`` registra as transmissões (testes e demonstração sem celular).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import threading
import time

from .sinais import Sinal


class ErroEmissor(RuntimeError):
    pass


class Emissor:
    nome = "base"

    def __init__(self):
        self.trava = threading.Lock()
        self.ultimo_envio = 0.0

    def frequencias(self) -> list[dict]:
        raise NotImplementedError

    def disponivel(self) -> dict:
        try:
            faixas = self.frequencias()
        except ErroEmissor as e:
            return {"disponivel": False, "motivo": str(e)}
        if not faixas:
            return {"disponivel": False, "motivo": "o Android informa que este aparelho não tem emissor infravermelho"}
        return {"disponivel": True, "faixas_hz": faixas, "backend": self.nome}

    def _transmitir(self, freq: int, pulsos: list[int]):
        raise NotImplementedError

    def enviar(self, sinal) -> dict:
        s = sinal if isinstance(sinal, Sinal) else Sinal(sinal)
        freq, pulsos = s.transmissao()
        with self.trava:
            # pequeno intervalo mínimo entre transmissões consecutivas
            espera = 0.12 - (time.monotonic() - self.ultimo_envio)
            if espera > 0:
                time.sleep(espera)
            self._transmitir(freq, pulsos)
            self.ultimo_envio = time.monotonic()
        return {"frequencia": freq, "duracoes": len(pulsos), "duracao_ms": round(sum(pulsos) / 1000)}


class EmissorTermux(Emissor):
    nome = "termux"

    def __init__(self, tempo_limite: float = 12.0):
        super().__init__()
        self.tempo_limite = tempo_limite
        self._faixas = None

    def _rodar(self, args: list[str]) -> str:
        if not shutil.which(args[0]):
            raise ErroEmissor(f"comando {args[0]} não encontrado — instale com: pkg install termux-api")
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=self.tempo_limite)
        except subprocess.TimeoutExpired as e:
            raise ErroEmissor("o Termux:API não respondeu — confira se o app Termux:API está instalado "
                              "(mesma fonte do Termux) e sem restrição de bateria") from e
        if r.returncode != 0:
            raise ErroEmissor((r.stderr or r.stdout or f"código {r.returncode}").strip()[:300])
        return r.stdout

    def frequencias(self) -> list[dict]:
        if self._faixas is None:
            saida = self._rodar(["termux-infrared-frequencies"]).strip() or "[]"
            try:
                self._faixas = json.loads(saida)
            except json.JSONDecodeError as e:
                raise ErroEmissor(f"resposta inesperada do Termux:API: {saida[:120]}") from e
        return self._faixas

    def _transmitir(self, freq: int, pulsos: list[int]):
        faixas = self._faixas or []
        if faixas and not any(f.get("min", 0) <= freq <= f.get("max", 10 ** 6) for f in faixas):
            # o hardware aceita poucas frequências: usa a mais próxima suportada
            freq = min((f["min"] for f in faixas), key=lambda x: abs(x - freq))
        saida = self._rodar(["termux-infrared-transmit", "-f", str(int(freq)), ",".join(str(int(p)) for p in pulsos)])
        if "error" in saida.lower() or "exception" in saida.lower():
            raise ErroEmissor(saida.strip()[:300])


class EmissorSimulado(Emissor):
    nome = "simulado"

    def __init__(self, falhar_em: set[int] | None = None):
        super().__init__()
        self.enviados: list[tuple[int, list[int]]] = []
        self.falhar_em = set(falhar_em or ())

    def frequencias(self) -> list[dict]:
        return [{"min": f, "max": f} for f in (30000, 33000, 36000, 38000, 40000, 56000)]

    def _transmitir(self, freq: int, pulsos: list[int]):
        n = len(self.enviados) + 1
        if n in self.falhar_em:
            self.falhar_em.discard(n)
            self.enviados.append((0, []))  # tentativa registrada, mas sem sucesso
            raise ErroEmissor("falha simulada do emissor")
        self.enviados.append((freq, list(pulsos)))
