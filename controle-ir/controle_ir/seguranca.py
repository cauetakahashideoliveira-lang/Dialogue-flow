"""Guardião das chamadas ao conector (Etapa 0 da arquitetura em docs/seguranca.md).

O sistema fica DESARMADO por padrão: pelo conector só passam as ferramentas de baixo risco (infravermelho,
consulta e o próprio freio). Terminal, tela, câmera, microfone, capacidades e atualização exigem o sistema ARMADO,
e armar só existe no celular (widget "Armar Controle IR" ou `controle-ir armar`), que pede o aparelho
desbloqueado — a digital do dono. Nenhuma ferramenta remota arma, destrava ou libera.

Isto não substitui a Etapa 1 (painel com passkey, OAuth e liberações assinadas): durante uma janela armada, quem
tiver a URL do conector tem o alcance da política vigente.
"""
from __future__ import annotations

import time

# o freio e a consulta valem sempre (só informam ou tiram poder)
SEMPRE = frozenset({"consultar", "politica", "travar"})
# infravermelho e cadastro de aparelhos: liberados também com o sistema desarmado (se desarmado_permite == "ir")
BAIXO_RISCO = SEMPRE | frozenset({
    "procurar_perfis", "opcoes", "controlar", "registrar_estado", "buscar", "progresso", "pausar", "retomar",
    "retestar", "confirmar", "distinguir", "salvar_aparelho", "editar_aparelho", "importar", "exportar",
    "enviar_sinal",
})
COMO_ARMAR = ("arme no celular: widget “Armar Controle IR” (vale até a meia-noite) ou, no Termux, "
              "controle-ir armar")


def fim_do_dia(agora: float | None = None) -> float:
    """Próxima meia-noite no fuso do aparelho."""
    agora = time.time() if agora is None else agora
    t = time.localtime(agora)
    return time.mktime((t.tm_year, t.tm_mon, t.tm_mday + 1, 0, 0, 0, 0, 0, -1))


def armado(pol: dict, agora: float | None = None) -> bool:
    agora = time.time() if agora is None else agora
    return not pol.get("travado") and agora < float(pol.get("armado_ate") or 0)


def permitido(ferramenta: str, pol: dict, agora: float | None = None) -> tuple[bool, str]:
    """Decide se a ferramenta MCP pode rodar agora. Devolve (ok, motivo). `pol` = Politica.efetiva()."""
    como = "arme pela Central de Controle, com a digital" if pol.get("modo_painel") else COMO_ARMAR
    if ferramenta in SEMPRE:
        return True, "sempre"
    if pol.get("travado"):
        return False, ("execução TRAVADA no celular: só consultar, politica e travar respondem. "
                       "Para voltar, " + como)
    if armado(pol, agora):
        return True, "armado"
    if pol.get("desarmado_permite", "ir") == "ir" and ferramenta in BAIXO_RISCO:
        return True, "baixo_risco"
    return False, f"o sistema está DESARMADO: “{ferramenta}” precisa dele armado. Para usar, {como}"
