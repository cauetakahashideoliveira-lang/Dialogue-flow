#!/usr/bin/env python3
"""god-mode — adaptação do G0DM0D3 para o Claude Code (skill /god-mode).

Origem: https://github.com/elder-plinius/G0DM0D3, commit f630176 (15/07/2026), licença AGPL-3.0.
Portado para Python, só com a biblioteca padrão:
  - AutoTune de 20 contextos ........ index.html (AUTOTUNE_CONTEXT_PATTERNS/PROFILES, computeAutoTuneParams)
  - Aprendizado por notas (EMA) ..... src/lib/autotune-feedback.ts
  - STM ............................. src/stm/modules.ts (hedge_reducer, direct_mode, casual_mode)
  - Pontuação e corrida de modelos .. api/lib/ultraplinian.ts (scoreResponse, raceModels, queryModel)
Acréscimos desta adaptação: padrões em português, estimativa de custo com teto, checagem da chave antes de
enviar o pedido, servidor local OpenAI-compatível, estado em arquivo e testes (testes/test_god_mode.py).

Fica de fora de propósito: os prompts de jailbreak (GODMODE CLASSIC / L1B3RT4S), a diretiva "nunca recuse"
(DEPTH_DIRECTIVE), o "boost GODMODE", o Parseltongue (ofuscação para escapar de filtros) e o critério
"anti-recusa" da pontuação — aqui uma recusa só aparece como informação, sem mudar a nota.

Este arquivo deriva de código AGPL-3.0 e é distribuído sob a mesma licença (LICENSE-G0DM0D3.txt nesta pasta).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import queue
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path

VERSAO = "1.0.0"
ORIGEM = "G0DM0D3 f630176 (AGPL-3.0)"
PARAMS = ("temperature", "top_p", "top_k", "frequency_penalty", "presence_penalty", "repetition_penalty")
ROTULO_PARAM = {"temperature": "temperatura", "top_p": "top_p", "top_k": "top_k",
                "frequency_penalty": "freq", "presence_penalty": "pres", "repetition_penalty": "rep"}


class Erro(Exception):
    """Erro para o usuário (mensagem em português) com código de saída."""

    def __init__(self, mensagem: str, codigo: int = 1):
        super().__init__(mensagem)
        self.codigo = codigo


def js_round(x: float) -> int:
    """Math.round do JavaScript (meio arredonda para cima), para dar os mesmos números do original."""
    return math.floor(x + 0.5)


# ═════════════════════════════════════════════════════════════════════════════
# AutoTune — portado de index.html (20 contextos)
# ═════════════════════════════════════════════════════════════════════════════

_A = re.ASCII | re.IGNORECASE  # \b só ASCII, como o JavaScript sem a flag u (padrões originais)
_U = re.IGNORECASE             # \b Unicode (padrões em português, acréscimo desta adaptação)


def _c(padroes: list[str], flags: int) -> list[re.Pattern]:
    return [re.compile(p, flags) for p in padroes]


PADROES_ORIGINAIS: dict[str, list[re.Pattern]] = {
    "code": _c([
        r"\b(code|function|class|variable|bug|error|debug|compile|syntax|api|endpoint|regex|algorithm|refactor|typescript|javascript|python|rust|html|css|sql|json|xml|import|export|return|async|await|promise|interface|type|const|let|var)\b",
        r"```[\s\S]*```",
        r"\b(fix|implement|write|create|build|deploy|test|unit test|lint|npm|pip|cargo|git)\b.*\b(code|function|app|service|component|module)\b",
        r"[{}();=><]",
        r"\b(stack trace|null pointer|segfault|runtime|compiler|linker|dependency|package|library|framework|sdk|cli)\b",
    ], _A),
    "creative": _c([
        r"\b(write|story|poem|creative|imagine|fiction|narrative|character|plot|scene|dialogue|metaphor|lyrics|song|artistic|fantasy|dream|inspire|muse|prose|verse|haiku)\b",
        r"\b(describe|paint|envision|portray|illustrate|craft)\b.*\b(world|scene|character|feeling|emotion|atmosphere)\b",
        r"\b(roleplay|role-play|pretend|act as|you are a)\b",
        r"\b(brainstorm|ideate|come up with|think of|generate ideas)\b",
    ], _A),
    "analytical": _c([
        r"\b(analyze|analysis|compare|contrast|evaluate|assess|examine|investigate|research|study|review|critique|breakdown|data|statistics|metrics|benchmark|measure)\b",
        r"\b(pros and cons|advantages|disadvantages|trade-?offs|implications|consequences)\b",
        r"\b(why|how does|what causes|explain|elaborate|clarify|define|summarize|overview)\b",
    ], _A),
    "conversational": _c([
        r"\b(hey|hi|hello|sup|what's up|how are you|thanks|thank you|cool|nice|awesome|great|lol|haha)\b",
        r"\b(chat|talk|tell me about|what do you think|opinion|feel|believe)\b",
        r"^.{0,30}$",
    ], _A),
    "chaotic": _c([
        r"\b(chaos|random|wild|crazy|absurd|surreal|glitch|corrupt|break|destroy|unleash|madness|void|entropy)\b",
        r"\b(gl1tch|h4ck|pwn|1337|l33t)\b",
        r"(!{3,}|\?{3,}|\.{4,})",
    ], _A),
    "security": _c([
        r"\b(hack|exploit|vulnerability|CVE|payload|shellcode|injection|XSS|CSRF|SSRF|RCE|privilege escalation|buffer overflow|reverse shell)\b",
        r"\b(pentest|penetration test|red team|CTF|capture the flag|bug bounty|threat model|attack surface|zero-?day)\b",
        r"\b(malware|ransomware|trojan|rootkit|keylogger|backdoor|RAT|C2|command and control|botnet)\b",
        r"\b(nmap|metasploit|burp|wireshark|ghidra|ida pro|radare|hashcat|john the ripper|cobalt strike)\b",
    ], _A),
    "medical": _c([
        r"\b(symptom|diagnosis|treatment|medication|dosage|prescription|side effect|contraindication|overdose|withdrawal)\b",
        r"\b(disease|syndrome|disorder|infection|pathology|prognosis|clinical|patient|hospital|surgery)\b",
        r"\b(drug|pharmaceutical|compound|molecule|receptor|mechanism of action|pharmacology|toxicology|LD50)\b",
    ], _A),
    "legal": _c([
        r"\b(law|legal|statute|regulation|compliance|liability|tort|criminal|civil|constitutional|jurisdiction)\b",
        r"\b(contract|clause|provision|amendment|precedent|ruling|verdict|sentence|plea|defense|prosecution)\b",
        r"\b(rights|freedom|privacy|surveillance|warrant|subpoena|DMCA|GDPR|CCPA|FOIA)\b",
    ], _A),
    "financial": _c([
        r"\b(stock|trading|invest|portfolio|dividend|equity|bond|derivative|option|futures|hedge|leverage|margin)\b",
        r"\b(crypto|bitcoin|ethereum|defi|blockchain|wallet|mining|token|NFT|smart contract|staking)\b",
        r"\b(market|bull|bear|volatility|arbitrage|liquidity|yield|APR|APY|ROI|P/E ratio)\b",
    ], _A),
    "scientific": _c([
        r"\b(hypothesis|experiment|variable|control group|peer review|methodology|empirical|observation|replication)\b",
        r"\b(physics|quantum|relativity|thermodynamics|particle|wave|field|energy|mass|force|entropy)\b",
        r"\b(chemistry|reaction|catalyst|molecule|compound|element|bond|valence|organic|inorganic|synthesis)\b",
        r"\b(biology|cell|gene|DNA|RNA|protein|evolution|mutation|organism|ecology|neuroscience|CRISPR)\b",
    ], _A),
    "philosophical": _c([
        r"\b(ethics|morality|moral|consciousness|free will|determinism|existential|ontology|epistemology|metaphysics)\b",
        r"\b(meaning|purpose|existence|reality|truth|knowledge|belief|justice|virtue|good and evil)\b",
        r"\b(utilitarian|deontological|consequentialism|nihilism|absurdism|stoicism|rationalism|empiricism)\b",
    ], _A),
    "instructional": _c([
        r"\b(how to|step by step|tutorial|guide|walkthrough|instructions|recipe|procedure|method|technique)\b",
        r"\b(make|build|assemble|construct|prepare|set up|configure|install|setup)\b.*\b(a|the|my|your)\b",
        r"\b(DIY|homemade|from scratch|beginner|intermediate|advanced)\b",
    ], _A),
    "persuasive": _c([
        r"\b(convince|persuade|argue|debate|rhetoric|negotiate|influence|propaganda|manipulation|reframe)\b",
        r"\b(argument|counterargument|rebuttal|fallacy|logical|premise|conclusion|evidence|claim|warrant)\b",
    ], _A),
    "mathematical": _c([
        r"\b(calculate|equation|formula|proof|theorem|derivative|integral|matrix|vector|polynomial|logarithm)\b",
        r"\b(probability|statistics|distribution|regression|correlation|variance|standard deviation|mean|median)\b",
        r"[∫∑∏√π∞±≤≥≠∈∀∃]",
        r"\b(algebra|calculus|geometry|topology|number theory|combinatorics|discrete math|linear algebra)\b",
    ], _A),
    "historical": _c([
        r"\b(history|historical|ancient|medieval|renaissance|colonial|revolution|war|empire|dynasty|civilization)\b",
        r"\b(century|era|epoch|period|age|BC|AD|BCE|CE|circa|archaeological|artifact)\b",
    ], _A),
    "political": _c([
        r"\b(politics|policy|government|election|democracy|authoritarian|regime|legislation|senate|congress|parliament)\b",
        r"\b(liberal|conservative|left|right|progressive|libertarian|socialist|capitalist|communist|anarchist)\b",
        r"\b(geopolitics|foreign policy|sanctions|diplomacy|NATO|UN|sovereignty|nationalism|globalization)\b",
    ], _A),
    "subversive": _c([
        r"\b(bypass|circumvent|workaround|loophole|evade|avoid detection|undetectable|untraceable|anonymous)\b",
        r"\b(forbidden|banned|illegal|illicit|black market|underground|darknet|dark web|tor|onion)\b",
        r"\b(censor|censorship|suppressed|restricted|classified|redacted|cover-?up|whistleblow)\b",
    ], _A),
    "emotional": _c([
        r"\b(feel|feeling|emotion|sad|depressed|anxious|anxiety|lonely|grief|trauma|therapy|cope|coping)\b",
        r"\b(mental health|self-?harm|suicide|crisis|support|empathy|compassion|healing|recovery|wellness)\b",
    ], _A),
    "strategic": _c([
        r"\b(strategy|strategic|tactics|tactical|plan|planning|optimize|optimization|game theory|decision)\b",
        r"\b(competitive advantage|SWOT|risk assessment|scenario|contingency|roadmap|milestone|objective|KPI)\b",
    ], _A),
    "synthesis": _c([
        r"\b(combine|merge|synthesize|integrate|unify|cross-?reference|interdisciplinary|holistic|meta-?analysis)\b",
        r"\b(big picture|connect the dots|pattern|trend|signal|insight|framework|mental model|systems thinking)\b",
    ], _A),
}
CONTEXTOS = tuple(PADROES_ORIGINAIS)

# Acréscimo desta adaptação: o original só reconhece inglês. Usados quando a mensagem parece português.
PADROES_PT: dict[str, list[re.Pattern]] = {
    "code": _c([r"\b(código|codigo|função|funcao|variável|variavel|depurar|compilar|sintaxe|script|programar|programação|programacao|refatorar|biblioteca|repositório|repositorio)\b"], _U),
    "creative": _c([
        r"\b(história|historia|poema|poesia|criativ[oa]|imagine|ficção|ficcao|personagem|enredo|canção|cancao|conto|roteiro|fantasia)\b",
        r"\b(escreva|escrever)\b.*\b(texto|carta|música|musica|letra)\b",
        r"\b(ideias|tempestade de ideias)\b",
    ], _U),
    "analytical": _c([
        r"\b(analise|análise|analisar|compare|comparar|comparação|comparacao|avalie|avaliar|examine|investigue|critique|estatísticas|estatisticas|métricas|metricas)\b",
        r"\b(prós e contras|pros e contras|vantagens|desvantagens|implicações|implicacoes|consequências|consequencias)\b",
        r"\b(por que|por quê|como funciona|o que causa|explique|explicar|defina|resuma|resumo|visão geral|visao geral)\b",
    ], _U),
    "conversational": _c([
        r"\b(oi|olá|ola|e aí|e ai|tudo bem|obrigad[oa]|valeu|legal|massa|haha|kkk+)\b",
        r"\b(conversar|me conta|o que você acha|o que voce acha|sua opinião|sua opiniao)\b",
    ], _U),
    "instructional": _c([
        r"\b(como fazer|como faço|como faco|passo a passo|tutorial|guia|instruções|instrucoes|receita|procedimento)\b",
        r"\b(instalar|configurar|montar|preparar)\b.*\b(o|a|os|as|meu|minha|um|uma)\b",
    ], _U),
    "mathematical": _c([r"\b(calcule|calcular|equação|equacao|fórmula|formula|teorema|derivada|integral|matriz|vetor|polinômio|polinomio|logaritmo|probabilidade|média|mediana|desvio padrão|desvio padrao)\b"], _U),
    "scientific": _c([r"\b(hipótese|hipotese|experimento|física|fisica|química|quimica|biologia|célula|celula|proteína|proteina|evolução|evolucao|átomo|atomo|molécula|molecula)\b"], _U),
    "medical": _c([r"\b(sintomas?|diagnóstico|diagnostico|tratamento|remédio|remedio|medicamento|dosagem|efeito colateral|doença|doenca|paciente|cirurgia)\b"], _U),
    "legal": _c([r"\b(lei|leis|jurídico|juridico|contrato|cláusula|clausula|advogado|LGPD|tribunal|sentença|sentenca|processo judicial)\b"], _U),
    "financial": _c([r"\b(investir|investimento|carteira de investimentos|dividendos|renda fixa|tesouro direto|CDB|bolsa de valores|cripto|bitcoin|juros|financiamento)\b"], _U),
    "historical": _c([r"\b(antiguidade|medieval|império|imperio|revolução|revolucao|guerra|século|seculo|dinastia|civilização|civilizacao)\b"], _U),
    "philosophical": _c([r"\b(ética|etica|moral|consciência|consciencia|livre-arbítrio|livre arbitrio|existência|existencia|sentido da vida)\b"], _U),
    "emotional": _c([r"\b(triste|tristeza|ansios[oa]|ansiedade|sozinh[oa]|solidão|solidao|luto|depressão|depressao|terapia|saúde mental|saude mental)\b"], _U),
    "strategic": _c([r"\b(estratégia|estrategia|estratégico|estrategico|planejamento|otimizar|otimização|otimizacao|tomada de decisão|tomada de decisao|cenários|cenarios|metas)\b"], _U),
}

PERFIS: dict[str, dict[str, float]] = {
    "code": {"temperature": 0.15, "top_p": 0.8, "top_k": 25, "frequency_penalty": 0.2, "presence_penalty": 0.0, "repetition_penalty": 1.05},
    "creative": {"temperature": 1.15, "top_p": 0.95, "top_k": 85, "frequency_penalty": 0.5, "presence_penalty": 0.7, "repetition_penalty": 1.2},
    "analytical": {"temperature": 0.4, "top_p": 0.88, "top_k": 40, "frequency_penalty": 0.2, "presence_penalty": 0.15, "repetition_penalty": 1.08},
    "conversational": {"temperature": 0.75, "top_p": 0.9, "top_k": 50, "frequency_penalty": 0.1, "presence_penalty": 0.1, "repetition_penalty": 1.0},
    "chaotic": {"temperature": 1.7, "top_p": 0.99, "top_k": 100, "frequency_penalty": 0.8, "presence_penalty": 0.9, "repetition_penalty": 1.3},
    "security": {"temperature": 0.3, "top_p": 0.85, "top_k": 35, "frequency_penalty": 0.15, "presence_penalty": 0.2, "repetition_penalty": 1.1},
    "medical": {"temperature": 0.25, "top_p": 0.82, "top_k": 30, "frequency_penalty": 0.1, "presence_penalty": 0.1, "repetition_penalty": 1.05},
    "legal": {"temperature": 0.2, "top_p": 0.8, "top_k": 28, "frequency_penalty": 0.15, "presence_penalty": 0.05, "repetition_penalty": 1.05},
    "financial": {"temperature": 0.3, "top_p": 0.85, "top_k": 35, "frequency_penalty": 0.2, "presence_penalty": 0.1, "repetition_penalty": 1.08},
    "scientific": {"temperature": 0.35, "top_p": 0.85, "top_k": 35, "frequency_penalty": 0.2, "presence_penalty": 0.15, "repetition_penalty": 1.08},
    "philosophical": {"temperature": 0.9, "top_p": 0.92, "top_k": 65, "frequency_penalty": 0.4, "presence_penalty": 0.5, "repetition_penalty": 1.15},
    "instructional": {"temperature": 0.3, "top_p": 0.85, "top_k": 30, "frequency_penalty": 0.15, "presence_penalty": 0.1, "repetition_penalty": 1.05},
    "persuasive": {"temperature": 0.8, "top_p": 0.9, "top_k": 55, "frequency_penalty": 0.35, "presence_penalty": 0.4, "repetition_penalty": 1.12},
    "mathematical": {"temperature": 0.1, "top_p": 0.75, "top_k": 20, "frequency_penalty": 0.1, "presence_penalty": 0.0, "repetition_penalty": 1.02},
    "historical": {"temperature": 0.5, "top_p": 0.88, "top_k": 45, "frequency_penalty": 0.25, "presence_penalty": 0.2, "repetition_penalty": 1.1},
    "political": {"temperature": 0.7, "top_p": 0.9, "top_k": 55, "frequency_penalty": 0.3, "presence_penalty": 0.35, "repetition_penalty": 1.12},
    "subversive": {"temperature": 1.4, "top_p": 0.97, "top_k": 90, "frequency_penalty": 0.6, "presence_penalty": 0.7, "repetition_penalty": 1.25},
    "emotional": {"temperature": 0.85, "top_p": 0.92, "top_k": 60, "frequency_penalty": 0.3, "presence_penalty": 0.4, "repetition_penalty": 1.1},
    "strategic": {"temperature": 0.45, "top_p": 0.88, "top_k": 42, "frequency_penalty": 0.25, "presence_penalty": 0.2, "repetition_penalty": 1.1},
    "synthesis": {"temperature": 0.6, "top_p": 0.9, "top_k": 50, "frequency_penalty": 0.35, "presence_penalty": 0.3, "repetition_penalty": 1.12},
}

ESTRATEGIAS: dict[str, dict[str, float]] = {
    "precise": {"temperature": 0.2, "top_p": 0.85, "top_k": 30, "frequency_penalty": 0.3, "presence_penalty": 0.1, "repetition_penalty": 1.1},
    "balanced": {"temperature": 0.7, "top_p": 0.9, "top_k": 50, "frequency_penalty": 0.1, "presence_penalty": 0.1, "repetition_penalty": 1.0},
    "creative": {"temperature": 1.1, "top_p": 0.95, "top_k": 80, "frequency_penalty": 0.4, "presence_penalty": 0.6, "repetition_penalty": 1.15},
    "chaotic": {"temperature": 1.6, "top_p": 0.98, "top_k": 100, "frequency_penalty": 0.7, "presence_penalty": 0.8, "repetition_penalty": 1.25},
}

ROTULO_CONTEXTO = {
    "code": "código", "creative": "criativo", "analytical": "analítico", "conversational": "conversa",
    "chaotic": "caótico", "security": "segurança", "medical": "médico", "legal": "jurídico",
    "financial": "financeiro", "scientific": "científico", "philosophical": "filosófico",
    "instructional": "instrucional", "persuasive": "persuasivo", "mathematical": "matemático",
    "historical": "histórico", "political": "político", "subversive": "subversivo", "emotional": "emocional",
    "strategic": "estratégico", "synthesis": "síntese",
}

_PT = re.compile(r"\b(que|não|nao|de|da|do|para|pra|com|uma|um|os|as|é|está|esta|você|voce|como|por|isso|meu|minha)\b|ção|ções|ã|õ|ç", _U)
_EN = re.compile(r"\b(the|and|is|are|of|to|you|what|how|this|that|with|for|my|your|can|please)\b", _A)


def parece_portugues(texto: str) -> bool:
    pt = len(_PT.findall(texto))
    return pt > 0 and pt >= len(_EN.findall(texto))


def _descrever(p: re.Pattern) -> str:
    """describePattern do original: as três primeiras palavras do grupo, ou um apelido."""
    m = re.search(r"\\b\(([^)]+)\)\\b", p.pattern)
    if m:
        palavras = m.group(1).split("|")
        return ", ".join(palavras[:3]) + ("..." if len(palavras) > 3 else "")
    if "```" in p.pattern:
        return "bloco de código"
    if p.pattern == r"[{}();=><]":
        return "sintaxe de código"
    if p.pattern == r"^.{0,30}$":
        return "mensagem curta"
    if "!{3,}" in p.pattern:
        return "pontuação exagerada"
    return p.pattern[:20] + "..."


def _padroes(portugues: bool) -> dict[str, list[re.Pattern]]:
    if not portugues:
        return PADROES_ORIGINAIS
    return {c: PADROES_ORIGINAIS[c] + PADROES_PT.get(c, []) for c in CONTEXTOS}


def _texto(msg) -> str:
    if isinstance(msg, dict):
        return str(msg.get("content") or "")
    return str(msg or "")


def detectar_contexto(mensagem: str, historico=(), portugues: bool | None = None) -> dict:
    """detectAutoTuneContext: mensagem atual vale 3, as 4 últimas do histórico valem 1."""
    if portugues is None:
        portugues = parece_portugues(mensagem)
    padroes = _padroes(portugues)
    pontos = {c: 0 for c in CONTEXTOS}
    sinais: list[str] = []
    for ctx, lista in padroes.items():
        for p in lista:
            if p.search(mensagem):
                pontos[ctx] += 3
                sinais.append(f"{ctx}: {_descrever(p)}")
    for msg in list(historico)[-4:]:
        texto = _texto(msg)
        for ctx, lista in padroes.items():
            for p in lista:
                if p.search(texto):
                    pontos[ctx] += 1
    total = sum(pontos.values())
    ordem = sorted(pontos.items(), key=lambda kv: -kv[1])  # estável, como o sort do JavaScript
    if total == 0:
        return {"tipo": "conversational", "confianca": 0.5, "ranking": [], "sinais": ["nenhum padrão: conversa"],
                "portugues": portugues}
    tipo, melhor = ordem[0]
    ranking = [{"contexto": c, "pontos": p, "porcentagem": js_round(100 * p / total)} for c, p in ordem if p > 0]
    return {"tipo": tipo, "confianca": min(melhor / total, 1.0), "ranking": ranking, "sinais": sinais,
            "portugues": portugues}


def mesclar(a: dict, b: dict, peso_b: float) -> dict:
    w = min(max(peso_b, 0.0), 1.0)
    saida = {k: a[k] * (1 - w) + b[k] * w for k in PARAMS}
    saida["top_k"] = js_round(saida["top_k"])
    return saida


def limitar(p: dict) -> dict:
    """applyBounds do original."""
    def entre(v, lo, hi):
        return min(max(v, lo), hi)
    return {
        "temperature": round(entre(p["temperature"], 0.0, 2.0), 4),
        "top_p": round(entre(p["top_p"], 0.0, 1.0), 4),
        "top_k": int(entre(js_round(p["top_k"]), 1, 100)),
        "frequency_penalty": round(entre(p["frequency_penalty"], -2.0, 2.0), 4),
        "presence_penalty": round(entre(p["presence_penalty"], -2.0, 2.0), 4),
        "repetition_penalty": round(entre(p["repetition_penalty"], 0.0, 2.0), 4),
    }


def autotune(mensagem: str, historico=(), estrategia: str = "adaptive", aprendizado: dict | None = None,
             ajustes: dict | None = None, portugues: bool | None = None) -> dict:
    """computeAutoTuneParams do index.html, sem o 'boost GODMODE', com o aprendizado do src/ e ajustes manuais."""
    if estrategia != "adaptive" and estrategia not in ESTRATEGIAS:
        raise Erro(f"estratégia desconhecida: {estrategia} (use adaptive, {', '.join(ESTRATEGIAS)})")
    historico = list(historico)
    det = detectar_contexto(mensagem, historico, portugues)
    referencia = dict(ESTRATEGIAS["balanced" if estrategia == "adaptive" else estrategia])
    deltas: list[dict] = []
    if estrategia == "adaptive":
        params = dict(PERFIS[det["tipo"]])
        if det["confianca"] < 0.6:
            params = mesclar(params, ESTRATEGIAS["balanced"], 1 - det["confianca"])
        for k in PARAMS:
            if abs(params[k] - referencia[k]) > 0.001:
                deltas.append({"param": k, "antes": referencia[k], "depois": params[k],
                               "motivo": f"contexto {ROTULO_CONTEXTO[det['tipo']]}"})
    else:
        params = dict(ESTRATEGIAS[estrategia])
    n = len(historico)
    if n > 10:
        reforco = min((n - 10) * 0.01, 0.15)
        antes = params["repetition_penalty"]
        params["repetition_penalty"] = min(antes + reforco, 2.0)
        deltas.append({"param": "repetition_penalty", "antes": antes, "depois": params["repetition_penalty"],
                       "motivo": f"conversa longa ({n} mensagens)"})
    nota = ""
    if aprendizado and estrategia == "adaptive":
        novo, aplicado, nota = aplicar_aprendizado(params, det["tipo"], aprendizado)
        if aplicado:
            for k in PARAMS:
                if abs(novo[k] - params[k]) > 0.001:
                    deltas.append({"param": k, "antes": params[k], "depois": novo[k], "motivo": "aprendido das notas"})
            params = novo
    for k, v in (ajustes or {}).items():
        if k not in PARAMS:
            raise Erro(f"parâmetro desconhecido: {k} (use {', '.join(PARAMS)})")
        if v is not None:
            deltas.append({"param": k, "antes": params[k], "depois": float(v), "motivo": "ajuste manual"})
            params[k] = float(v)
    final = limitar(params)
    if estrategia == "adaptive":
        motivo = f"detectado: {ROTULO_CONTEXTO[det['tipo']]} ({js_round(det['confianca'] * 100)}% de confiança)"
    else:
        motivo = f"estratégia fixa: {estrategia}"
    if n > 10:
        motivo += " | conversa longa: +repetição"
    if nota:
        motivo += f" | {nota}"
    return {"params": final, "contexto": det["tipo"], "confianca": round(det["confianca"], 4),
            "estrategia": estrategia, "motivo": motivo, "ranking": det["ranking"], "sinais": det["sinais"],
            "deltas": deltas, "referencia": referencia, "portugues": det["portugues"]}


# ═════════════════════════════════════════════════════════════════════════════
# Aprendizado por notas — portado de src/lib/autotune-feedback.ts (agora com os 20 contextos)
# ═════════════════════════════════════════════════════════════════════════════

NEUTRO = {"temperature": 0.7, "top_p": 0.9, "top_k": 50, "frequency_penalty": 0.2, "presence_penalty": 0.2,
          "repetition_penalty": 1.1}
ALFA_EMA = 0.3
MAX_HISTORICO = 500
MIN_AMOSTRAS = 3
PESO_MAXIMO = 0.5
AMOSTRAS_PARA_PESO_MAXIMO = 20


def estado_inicial() -> dict:
    return {"history": [], "learnedProfiles": {}}


def _perfil_vazio(ctx: str) -> dict:
    return {"contextType": ctx, "sampleCount": 0, "positiveCount": 0, "negativeCount": 0,
            "positiveParams": dict(NEUTRO), "negativeParams": dict(NEUTRO), "adjustments": {}, "lastUpdated": 0}


def _ema(atual: dict, obs: dict, alfa: float) -> dict:
    saida = {k: atual[k] * (1 - alfa) + obs[k] * alfa for k in PARAMS}
    saida["top_k"] = js_round(saida["top_k"])
    return saida


def _delta_do_neutro(positivos: dict, escala: float) -> dict:
    adj = {}
    for k in PARAMS:
        d = (positivos[k] - NEUTRO[k]) * escala
        if abs(d) > 0.01:
            adj[k] = d
    return adj


def _calcular_ajustes(perfil: dict) -> dict:
    if perfil["positiveCount"] < 1 or perfil["negativeCount"] < 1:
        if perfil["positiveCount"] >= MIN_AMOSTRAS:
            return _delta_do_neutro(perfil["positiveParams"], 0.5)
        return {}
    adj = {}
    for k in PARAMS:
        pos = perfil["positiveParams"][k] - NEUTRO[k]
        neg = perfil["negativeParams"][k] - NEUTRO[k]
        a = (pos - neg) * 0.5  # empurra para o lado das notas boas, longe das ruins
        if abs(a) > 0.01:
            adj[k] = a
    return adj


def registrar_nota(estado: dict, registro: dict) -> dict:
    """processFeedback: guarda a nota e atualiza o perfil aprendido do contexto (média móvel exponencial)."""
    historia = (estado.get("history") or []) + [registro]
    if len(historia) > MAX_HISTORICO:
        historia = historia[-MAX_HISTORICO:]
    perfis = dict(estado.get("learnedProfiles") or {})
    ctx = registro["contextType"]
    perfil = json.loads(json.dumps(perfis.get(ctx) or _perfil_vazio(ctx)))
    perfil["sampleCount"] += 1
    perfil["lastUpdated"] = int(time.time() * 1000)
    if registro["rating"] == 1:
        perfil["positiveCount"] += 1
        perfil["positiveParams"] = _ema(perfil["positiveParams"], registro["params"], ALFA_EMA)
    else:
        perfil["negativeCount"] += 1
        perfil["negativeParams"] = _ema(perfil["negativeParams"], registro["params"], ALFA_EMA)
    perfil["adjustments"] = _calcular_ajustes(perfil)
    perfis[ctx] = perfil
    return {"history": historia, "learnedProfiles": perfis}


def aplicar_aprendizado(params: dict, ctx: str, perfis: dict) -> tuple[dict, bool, str]:
    """applyLearnedAdjustments: peso cresce com o número de notas, até 50%."""
    perfil = (perfis or {}).get(ctx)
    if not perfil or perfil["sampleCount"] < MIN_AMOSTRAS or not perfil["adjustments"]:
        return params, False, ""
    peso = min(perfil["sampleCount"] / AMOSTRAS_PARA_PESO_MAXIMO * PESO_MAXIMO, PESO_MAXIMO)
    novo = dict(params)
    for k, d in perfil["adjustments"].items():
        novo[k] = novo[k] + d * peso
    nota = (f"aprendido: {len(perfil['adjustments'])} parâmetro(s) ajustado(s) "
            f"({perfil['sampleCount']} notas, peso {js_round(peso * 100)}%)")
    return novo, True, nota


def heuristicas(resposta: str) -> dict:
    """computeHeuristics: tamanho, repetição de trigramas, frase média e diversidade de vocabulário."""
    palavras = [w for w in resposta.lower().split() if w]
    frases = [f for f in re.split(r"[.!?]+", resposta) if f.strip()]
    media_frase = (sum(len(f.split()) for f in frases) / len(frases)) if frases else 0
    return {"responseLength": len(resposta), "repetitionScore": round(_repeticao(palavras), 4),
            "averageSentenceLength": round(media_frase, 2),
            "vocabularyDiversity": round(len(set(palavras)) / len(palavras), 4) if palavras else 1}


def _repeticao(palavras: list[str]) -> float:
    if len(palavras) < 6:
        return 0.0
    contagem: dict[str, int] = {}
    total = 0
    for i in range(len(palavras) - 2):
        tri = " ".join(palavras[i:i + 3])
        contagem[tri] = contagem.get(tri, 0) + 1
        total += 1
    repetidos = sum(c - 1 for c in contagem.values() if c > 1)
    return min(repetidos / total, 1.0) if total else 0.0


def estatisticas(estado: dict) -> dict:
    """getFeedbackStats."""
    historia = estado.get("history") or []
    positivos = sum(1 for r in historia if r.get("rating") == 1)
    contextos = {}
    for ctx, p in (estado.get("learnedProfiles") or {}).items():
        contextos[ctx] = {"total": p["sampleCount"], "positivas": p["positiveCount"], "negativas": p["negativeCount"],
                          "aprendeu": p["sampleCount"] >= MIN_AMOSTRAS and bool(p["adjustments"]),
                          "ajustes": {k: round(v, 4) for k, v in p["adjustments"].items()}}
    return {"total": len(historia), "taxa_positiva": round(positivos / len(historia), 4) if historia else 0,
            "contextos": contextos}


# ═════════════════════════════════════════════════════════════════════════════
# STM — portado de src/stm/modules.ts (+ equivalentes em português)
# ═════════════════════════════════════════════════════════════════════════════

_HESITACOES = [re.compile(p, re.IGNORECASE) for p in (
    r"\bI think\s+", r"\bI believe\s+", r"\bperhaps\s+", r"\bmaybe\s+", r"\bIt seems like\s+",
    r"\bIt appears that\s+", r"\bprobably\s+", r"\bpossibly\s+", r"\bI would say\s+", r"\bIn my opinion,?\s*",
    r"\bFrom my perspective,?\s*",
    # português (acréscimo)
    r"\bEu acho que\s+", r"\bAcho que\s+", r"\bEu acredito que\s+", r"\bAcredito que\s+", r"\btalvez\s+",
    r"\bprovavelmente\s+", r"\bpossivelmente\s+", r"\bParece que\s+", r"\bNa minha opinião,?\s*",
    r"\bDo meu ponto de vista,?\s*", r"\bEu diria que\s+",
)]

_PREAMBULOS_STM = [re.compile(p, re.IGNORECASE) for p in (
    r"^(Sure\b,?\s*)", r"^(Of course\b,?\s*)", r"^(Certainly\b,?\s*)", r"^(Absolutely\b,?\s*)",
    r"^(Great question!?\s*)", r"^(That's a great question!?\s*)", r"^(I'd be happy to help( you)?( with that)?[.!]?\s*)",
    r"^(Let me help you with that[.!]?\s*)", r"^(I understand[.!]?\s*)", r"^(Thanks for asking[.!]?\s*)",
    # português (acréscimo)
    r"^(Claro\b[,!.]?\s*)", r"^(Com certeza\b[,!.]?\s*)", r"^(Certamente\b[,!.]?\s*)", r"^(Ótima pergunta[!.]?\s*)",
    r"^(Excelente pergunta[!.]?\s*)", r"^(Boa pergunta[!.]?\s*)", r"^(Fico feliz em ajudar[.!]?\s*)",
    r"^(Vou te ajudar com isso[.!]?\s*)", r"^(Entendi[.!]?\s*)", r"^(Obrigad[oa] por perguntar[.!]?\s*)",
)]

_CASUAL = [(re.compile(a, f), b) for a, b, f in (
    (r"\bHowever\b", "But", 0), (r"\bTherefore\b", "So", 0), (r"\bFurthermore\b", "Also", 0),
    (r"\bAdditionally\b", "Plus", 0), (r"\bNevertheless\b", "Still", 0), (r"\bConsequently\b", "So", 0),
    (r"\bMoreover\b", "Also", 0), (r"\bUtilize\b", "Use", 0), (r"\butilize\b", "use", 0), (r"\bPurchase\b", "Buy", 0),
    (r"\bpurchase\b", "buy", 0), (r"\bObtain\b", "Get", 0), (r"\bobtain\b", "get", 0), (r"\bCommence\b", "Start", 0),
    (r"\bcommence\b", "start", 0), (r"\bTerminate\b", "End", 0), (r"\bterminate\b", "end", 0),
    (r"\bPrior to\b", "Before", re.IGNORECASE), (r"\bSubsequent to\b", "After", re.IGNORECASE),
    (r"\bIn order to\b", "To", re.IGNORECASE), (r"\bDue to the fact that\b", "Because", re.IGNORECASE),
    (r"\bAt this point in time\b", "Now", re.IGNORECASE), (r"\bIn the event that\b", "If", re.IGNORECASE),
    # português (acréscimo)
    (r"\bEntretanto\b", "Mas", 0), (r"\bNo entanto\b", "Mas", 0), (r"\bTodavia\b", "Mas", 0), (r"\bContudo\b", "Mas", 0),
    (r"\bPortanto\b", "Então", 0), (r"\bConsequentemente\b", "Então", 0), (r"\bAlém disso\b", "E", 0),
    (r"\bUtilizar\b", "Usar", 0), (r"\butilizar\b", "usar", 0), (r"\bAdquirir\b", "Comprar", 0),
    (r"\badquirir\b", "comprar", 0), (r"\bIniciar\b", "Começar", 0), (r"\biniciar\b", "começar", 0),
    (r"\bFinalizar\b", "Terminar", 0), (r"\bfinalizar\b", "terminar", 0), (r"\bA fim de\b", "Pra", 0),
    (r"\ba fim de\b", "pra", 0), (r"\bDevido ao fato de que\b", "Porque", 0), (r"\bdevido ao fato de que\b", "porque", 0),
    (r"\bNeste momento\b", "Agora", 0), (r"\bneste momento\b", "agora", 0),
)]

_INICIO_FRASE = re.compile(r"(?:^|[.!?:]|\n)\s*$")


def _remover(texto: str, padrao: re.Pattern) -> str:
    """Remove o padrão e põe maiúscula só onde a remoção abriu uma frase (o original mexia em toda linha)."""
    partes: list[str] = []
    ultimo = 0
    posicoes: list[int] = []
    for m in padrao.finditer(texto):
        partes.append(texto[ultimo:m.start()])
        ultimo = m.end()
        prefixo = "".join(partes)
        if _INICIO_FRASE.search(prefixo):
            posicoes.append(len(prefixo))
    partes.append(texto[ultimo:])
    saida = "".join(partes)
    for pos in posicoes:
        if pos < len(saida) and saida[pos].islower():
            saida = saida[:pos] + saida[pos].upper() + saida[pos + 1:]
    return saida


def stm_hesitacao(texto: str) -> str:
    for p in _HESITACOES:
        texto = _remover(texto, p)
    return texto


def stm_direto(texto: str) -> str:
    for p in _PREAMBULOS_STM:
        texto = _remover(texto, p)
    return texto


def stm_casual(texto: str) -> str:
    for p, troca in _CASUAL:
        texto = p.sub(troca, texto)
    return texto


MODULOS_STM = {"hedge_reducer": stm_hesitacao, "direct_mode": stm_direto, "casual_mode": stm_casual}
APELIDOS_STM = {"hesitacao": "hedge_reducer", "hedge": "hedge_reducer", "direto": "direct_mode",
                "direct": "direct_mode", "casual": "casual_mode"}


def resolver_modulos(lista: str | None) -> list[str]:
    if not lista:
        return []
    saida = []
    for nome in (x.strip().lower() for x in lista.split(",") if x.strip()):
        nome = APELIDOS_STM.get(nome, nome)
        if nome not in MODULOS_STM:
            raise Erro(f"módulo STM desconhecido: {nome} (use hesitacao, direto, casual)")
        saida.append(nome)
    return saida


def aplicar_stm(texto: str, modulos: list[str]) -> str:
    for m in modulos:
        texto = MODULOS_STM[m](texto)
    return texto


# ═════════════════════════════════════════════════════════════════════════════
# Pontuação neutra — scoreResponse do original sem o critério "anti-recusa"
# ═════════════════════════════════════════════════════════════════════════════

_RECUSAS = [re.compile(p, re.IGNORECASE) for p in (
    r"I cannot|I can't|I'm unable to", r"I apologize|I'm sorry, but", r"As an AI|As a language model",
    r"I must decline|I have to refuse", r"It would be inappropriate", r"I'm not comfortable",
    # português (acréscimo)
    r"não posso|nao posso|não consigo ajudar|nao consigo ajudar", r"desculpe, mas|sinto muito, mas|lamento, mas",
    r"como (uma )?(IA|inteligência artificial)|como um modelo de linguagem",
    r"não seria apropriado|não é apropriado", r"não me sinto confortável|nao me sinto confortavel",
)]
_PREAMBULOS = [re.compile(p, re.IGNORECASE) for p in (
    r"^(Sure|Of course|Certainly|Absolutely|Great question)", r"^I'd be happy to help", r"^Let me help you",
    r"^Thanks for asking",
    r"^(Claro|Com certeza|Certamente|Ótima pergunta|Excelente pergunta|Boa pergunta)", r"^Fico feliz em ajudar",
    r"^Vou te ajudar", r"^Obrigad[oa] por perguntar",
)]
_CABECALHO = re.compile(r"^#{1,3}\s", re.MULTILINE)
_LISTA = re.compile(r"^[\s]*[-*•]\s", re.MULTILINE)
_BLOCO = re.compile(r"```")
PONTOS_MAXIMOS_NEUTROS = 75.0  # comprimento 25 + estrutura 20 + objetividade 15 + relevância 15


def pontuar(conteudo: str, pergunta: str = "") -> dict:
    """0–100. Mesmos critérios do original menos os 25 pontos de 'anti-recusa'; recusa só é informada."""
    recusa = bool(conteudo) and any(p.search(conteudo) for p in _RECUSAS)
    if not conteudo or len(conteudo) < 10:
        return {"pontos": 0, "comprimento": 0, "estrutura": 0, "objetividade": 0, "relevancia": 0,
                "possivel_recusa": recusa}
    comprimento = min(len(conteudo) / 40, 25)
    blocos = len(_BLOCO.findall(conteudo)) / 2
    estrutura = min(len(_CABECALHO.findall(conteudo)) * 3 + len(_LISTA.findall(conteudo)) * 1.5 + blocos * 5, 20)
    objetividade = 8 if any(p.search(conteudo.strip()) for p in _PREAMBULOS) else 15
    palavras = [w for w in re.findall(r"\w+", pergunta.lower()) if len(w) > 3]
    baixo = conteudo.lower()
    relevancia = (sum(1 for w in palavras if w in baixo) / len(palavras)) if palavras else 0.5
    bruto = comprimento + estrutura + objetividade + relevancia * 15
    return {"pontos": js_round(min(bruto / PONTOS_MAXIMOS_NEUTROS * 100, 100)), "comprimento": round(comprimento, 1),
            "estrutura": round(estrutura, 1), "objetividade": objetividade, "relevancia": round(relevancia * 15, 1),
            "possivel_recusa": recusa}


# ═════════════════════════════════════════════════════════════════════════════
# Modelos e provedores (OpenRouter ou servidor OpenAI-compatível)
# ═════════════════════════════════════════════════════════════════════════════

# ULTRAPLINIAN_MODELS do original (só os ids; cada camada inclui as anteriores). O catálogo muda: a
# disponibilidade é conferida na lista pública da OpenRouter antes de cada comparação.
CAMADAS = {
    "fast": ["google/gemini-2.5-flash", "google/gemini-3.5-flash", "deepseek/deepseek-chat", "perplexity/sonar",
             "meta-llama/llama-3.1-8b-instruct", "moonshotai/kimi-k2.5", "openai/gpt-oss-20b", "stepfun/step-3.5-flash",
             "google/gemini-3.1-flash-lite", "mistralai/mistral-small-3.2-24b-instruct",
             "nvidia/nemotron-3-nano-30b-a3b", "z-ai/glm-5-turbo"],
    "standard": ["anthropic/claude-sonnet-5", "meta-llama/llama-4-scout", "deepseek/deepseek-v3.2",
                 "nousresearch/hermes-3-llama-3.1-70b", "openai/gpt-4o", "google/gemini-2.5-pro",
                 "anthropic/claude-sonnet-4", "anthropic/claude-sonnet-4.6", "mistralai/mixtral-8x22b-instruct",
                 "meta-llama/llama-3.3-70b-instruct", "qwen/qwen-2.5-72b-instruct", "nousresearch/hermes-4-70b",
                 "mistralai/mistral-medium-3.1", "google/gemini-3-flash-preview", "google/gemma-3-27b-it"],
    "smart": ["openai/gpt-5", "openai/gpt-5.3-chat", "openai/gpt-5.5", "qwen/qwen3.5-plus-02-15", "qwen/qwen3.7-max",
              "z-ai/glm-5", "z-ai/glm-5.2", "openai/gpt-5.2", "anthropic/claude-opus-4.6", "anthropic/claude-opus-4.8",
              "anthropic/claude-fable-5", "openai/gpt-oss-120b", "deepseek/deepseek-r1",
              "nvidia/nemotron-3-super-120b-a12b"],
    "power": ["x-ai/grok-4.5", "openai/gpt-5.4", "openai/gpt-5.5-pro", "openai/gpt-5.6-luna", "z-ai/glm-4.7",
              "meta-llama/llama-4-maverick", "qwen/qwen3-235b-a22b", "qwen/qwen3-coder", "minimax/minimax-m2.5",
              "mistralai/mistral-large-2512", "google/gemini-3.1-pro-preview", "moonshotai/kimi-k2"],
    "ultra": ["anthropic/claude-opus-4.8-fast", "anthropic/claude-opus-4", "nousresearch/hermes-4-405b",
              "nousresearch/hermes-3-llama-3.1-405b", "openai/gpt-5.6-terra", "openai/gpt-5.6-sol",
              "mistralai/codestral-2508"],
}
ORDEM_CAMADAS = ("fast", "standard", "smart", "power", "ultra")
MODELO_PADRAO_OPENROUTER = "google/gemini-2.5-flash"
TIMEOUT_MODELO = 25.0      # PER_MODEL_TIMEOUT_MS
TENTATIVAS_429 = 2         # MAX_RETRIES_ON_429
MIN_RESULTADOS = 5         # raceModels: minResults
ESPERA_EXTRA = 5.0         # raceModels: gracePeriod
LIMITE_TOTAL = 45.0        # raceModels: hardTimeout


def modelos_da_camada(camada: str) -> list[str]:
    if camada not in CAMADAS:
        raise Erro(f"camada desconhecida: {camada} (use {', '.join(ORDEM_CAMADAS)})")
    saida: list[str] = []
    for c in ORDEM_CAMADAS:
        saida += CAMADAS[c]
        if c == camada:
            return saida
    return saida


def provedor(nome: str, base_url: str | None = None, chave_env: str | None = None) -> dict:
    if nome == "openrouter":
        base = base_url or os.environ.get("GOD_MODE_OPENROUTER_URL") or "https://openrouter.ai/api/v1"
        env = chave_env or "OPENROUTER_API_KEY"
    elif nome == "local":
        base = base_url or os.environ.get("GOD_MODE_LOCAL_URL") or "http://localhost:11434/v1"
        env = chave_env or "GOD_MODE_LOCAL_KEY"
    elif nome == "outro":
        if not base_url:
            raise Erro("--provedor outro precisa de --base-url (ex.: https://servidor/v1) e, se houver, --chave-env")
        base, env = base_url, chave_env
    else:
        raise Erro(f"provedor desconhecido: {nome} (use openrouter, local ou outro)")
    return {"nome": nome, "base": base.rstrip("/"), "chave_env": env or "",
            "chave": os.environ.get(env, "") if env else ""}


def _local(url: str) -> bool:
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    return host in ("localhost", "::1") or host.startswith("127.")


def _http(metodo: str, url: str, corpo=None, chave: str = "", timeout: float = 20.0):
    """Devolve (status, dados, cabeçalhos). Erros de rede sobem como OSError/URLError."""
    cab = {"User-Agent": f"god-mode-skill/{VERSAO}", "Accept": "application/json"}
    dados = None
    if corpo is not None:
        dados = json.dumps(corpo).encode("utf-8")
        cab["Content-Type"] = "application/json"
    if chave:
        cab["Authorization"] = f"Bearer {chave}"
    if "openrouter.ai" in url:
        cab["X-Title"] = "god-mode (Claude Code)"
    req = urllib.request.Request(url, data=dados, headers=cab, method=metodo)
    abrir = (urllib.request.build_opener(urllib.request.ProxyHandler({})).open if _local(url)
             else urllib.request.urlopen)
    try:
        with abrir(req, timeout=timeout) as r:
            return r.status, _ler_json(r.read()), r.headers
    except urllib.error.HTTPError as e:
        bruto = e.read() if e.fp else b""
        return e.code, _ler_json(bruto), e.headers


def _ler_json(bruto: bytes):
    try:
        return json.loads(bruto.decode("utf-8") or "null")
    except (ValueError, UnicodeDecodeError):
        return {"texto": bruto[:300].decode("utf-8", "replace")}


def _mensagem_erro(dados) -> str:
    if isinstance(dados, dict):
        e = dados.get("error")
        if isinstance(e, dict):
            return str(e.get("message") or e)[:300]
        if e:
            return str(e)[:300]
        return str(dados.get("texto") or dados)[:300]
    return str(dados)[:300]


def _motivo_rede(e: BaseException) -> str:
    return str(getattr(e, "reason", None) or e)[:200]


def listar_modelos(cfg: dict, timeout: float = 20.0) -> list[dict]:
    try:
        status, dados, _ = _http("GET", cfg["base"] + "/models", chave=cfg["chave"], timeout=timeout)
    except (OSError, urllib.error.URLError) as e:
        raise Erro(f"sem resposta de {cfg['base']}/models: {_motivo_rede(e)}", 2)
    if status != 200 or not isinstance(dados, dict):
        raise Erro(f"{cfg['base']}/models respondeu HTTP {status}: {_mensagem_erro(dados)}", 2)
    return [m for m in dados.get("data") or [] if isinstance(m, dict) and m.get("id")]


def explicar_chave(cfg: dict) -> str:
    return (f"Configure a chave na variável de ambiente {cfg['chave_env'] or 'da chave'} fora do código: "
            "no Claude Code na web, em Configurações do ambiente (Network secrets ou variável de ambiente); no "
            "computador, no perfil do shell ou em ~/.claude/settings.json (\"env\"). Depois abra uma sessão nova. "
            "Nunca cole a chave no chat.")


def verificar_autenticacao(cfg: dict) -> str:
    """Só para a OpenRouter: confere a chave em /key sem mandar o pedido do usuário."""
    if cfg["nome"] != "openrouter":
        return "não se aplica"
    try:
        status, dados, _ = _http("GET", cfg["base"] + "/key", chave=cfg["chave"], timeout=15)
    except (OSError, urllib.error.URLError) as e:
        raise Erro(f"sem acesso à OpenRouter: {_motivo_rede(e)}", 2)
    if status == 200:
        return "ok"
    if status in (401, 403):
        raise Erro(f"OpenRouter recusou a autenticação (HTTP {status}). {explicar_chave(cfg)}", 2)
    raise Erro(f"OpenRouter respondeu HTTP {status} ao conferir a chave: {_mensagem_erro(dados)}", 2)


def _falha(modelo: str, inicio: float, erro: str) -> dict:
    return {"modelo": modelo, "conteudo": "", "duracao_ms": int((time.monotonic() - inicio) * 1000),
            "sucesso": False, "erro": erro}


def consultar_modelo(cfg: dict, modelo: str, mensagens: list[dict], params: dict, max_tokens: int = 2048,
                     timeout: float = TIMEOUT_MODELO) -> dict:
    """queryModel: uma chamada /chat/completions, repetindo até 2 vezes em HTTP 429."""
    inicio = time.monotonic()
    corpo = {"model": modelo, "messages": mensagens, "max_tokens": max_tokens}
    corpo.update({k: v for k, v in params.items() if v is not None})
    status, dados = 0, None
    for tentativa in range(TENTATIVAS_429 + 1):
        try:
            status, dados, cab = _http("POST", cfg["base"] + "/chat/completions", corpo, cfg["chave"], timeout)
        except (OSError, urllib.error.URLError) as e:
            return _falha(modelo, inicio, f"rede: {_motivo_rede(e)}")
        if status == 429 and tentativa < TENTATIVAS_429:
            ra = (cab.get("Retry-After") if cab else None) or ""
            espera = min(float(ra), 5.0) if ra.strip().isdigit() else (tentativa + 1) * 1.5
            time.sleep(espera)
            continue
        break
    if status != 200:
        return _falha(modelo, inicio, f"HTTP {status}: {_mensagem_erro(dados)}")
    try:
        conteudo = dados["choices"][0]["message"].get("content") or ""
    except (KeyError, IndexError, TypeError, AttributeError):
        return _falha(modelo, inicio, "resposta fora do formato OpenAI")
    if isinstance(conteudo, list):  # alguns servidores devolvem partes
        conteudo = "".join(str(p.get("text", "")) for p in conteudo if isinstance(p, dict))
    if not str(conteudo).strip():
        return _falha(modelo, inicio, "resposta vazia")
    return {"modelo": modelo, "conteudo": str(conteudo), "duracao_ms": int((time.monotonic() - inicio) * 1000),
            "sucesso": True, "erro": None}


def corrida(cfg: dict, modelos: list[str], mensagens: list[dict], params: dict, max_tokens: int = 2048,
            min_resultados: int = MIN_RESULTADOS, espera_extra: float = ESPERA_EXTRA,
            limite_total: float = LIMITE_TOTAL, timeout_modelo: float = TIMEOUT_MODELO) -> tuple[list, list]:
    """raceModels: dispara todos juntos; com min_resultados prontos, espera mais espera_extra e encerra."""
    fila: queue.Queue = queue.Queue()

    def trabalhar(m: str) -> None:
        t0 = time.monotonic()
        try:
            fila.put(consultar_modelo(cfg, m, mensagens, params, max_tokens, timeout_modelo))
        except Exception as e:  # noqa: BLE001 — qualquer falha vira resultado de erro
            fila.put(_falha(m, t0, f"erro interno: {e}"))

    for m in modelos:
        threading.Thread(target=trabalhar, args=(m,), daemon=True).start()
    minimo = max(1, min(min_resultados, len(modelos)))
    inicio = time.monotonic()
    prazo_total = inicio + limite_total
    prazo_espera = None
    resultados: list[dict] = []
    sucessos = 0
    while len(resultados) < len(modelos):
        prazo = prazo_total if prazo_espera is None else min(prazo_total, prazo_espera)
        restante = prazo - time.monotonic()
        if restante <= 0:
            break
        try:
            r = fila.get(timeout=restante)
        except queue.Empty:
            break
        resultados.append(r)
        if r["sucesso"]:
            sucessos += 1
            if sucessos >= minimo and prazo_espera is None:
                prazo_espera = time.monotonic() + espera_extra
    respondidos = {r["modelo"] for r in resultados}
    return resultados, [m for m in modelos if m not in respondidos]


def estimar_custo(catalogo: list[dict], modelos: list[str], mensagens: list[dict], max_tokens: int) -> dict:
    """Teto em US$: entrada estimada (~3,5 caracteres por token) + max_tokens de saída, pelos preços públicos."""
    por_id = {m["id"]: m for m in catalogo}
    tokens_entrada = sum(len(_texto(m)) for m in mensagens) / 3.5 + 20
    total, ausentes, sem_preco = 0.0, [], []
    for mid in modelos:
        info = por_id.get(mid)
        if not info:
            ausentes.append(mid)
            continue
        preco = info.get("pricing") or {}
        try:
            entrada, saida = float(preco.get("prompt", 0)), float(preco.get("completion", 0))
        except (TypeError, ValueError):
            sem_preco.append(mid)
            continue
        if entrada < 0 or saida < 0:
            sem_preco.append(mid)
            continue
        total += tokens_entrada * entrada + max_tokens * saida
    return {"teto_usd": round(total, 4), "ausentes": ausentes, "sem_preco": sem_preco,
            "tokens_entrada": int(tokens_entrada)}


# ═════════════════════════════════════════════════════════════════════════════
# Estado em arquivo (fora do repositório)
# ═════════════════════════════════════════════════════════════════════════════

def pasta_estado() -> Path:
    p = Path(os.environ.get("GOD_MODE_DIR") or (Path.home() / ".god-mode")).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    return p


def _ler(caminho: Path, padrao):
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return padrao


def _gravar(caminho: Path, dados) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_suffix(caminho.suffix + ".tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, caminho)


def ler_aprendizado() -> dict:
    return _ler(pasta_estado() / "feedback.json", estado_inicial())


def guardar_ultimo(dados: dict) -> None:
    dados = dict(dados, quando=datetime.now().astimezone().isoformat(timespec="seconds"))
    _gravar(pasta_estado() / "ultimo.json", dados)


# ═════════════════════════════════════════════════════════════════════════════
# Linha de comando
# ═════════════════════════════════════════════════════════════════════════════

def _fmt_params(p: dict) -> str:
    def v(k):
        return str(p[k]) if k == "top_k" else f"{p[k]:.2f}"
    return " · ".join(f"{ROTULO_PARAM[k]} {v(k)}" for k in PARAMS)


def _ler_entrada(texto: str | None, arquivo: str | None) -> str:
    if arquivo:
        if arquivo == "-":
            return sys.stdin.read()
        return Path(arquivo).read_text(encoding="utf-8")
    if texto is None or texto == "-":
        if sys.stdin.isatty():
            raise Erro("passe o texto como argumento, por --arquivo ou pela entrada padrão")
        return sys.stdin.read()
    return texto


def _imprimir(dados, como_json: bool, texto: str) -> None:
    if como_json:
        print(json.dumps(dados, ensure_ascii=False, indent=2))
    else:
        print(texto)


def _parse_ajustes(itens: list[str] | None) -> dict:
    ajustes = {}
    for item in itens or []:
        if "=" not in item:
            raise Erro(f"ajuste inválido: {item} (use parametro=valor, ex.: temperature=0.3)")
        k, v = item.split("=", 1)
        try:
            ajustes[k.strip()] = float(v)
        except ValueError:
            raise Erro(f"valor inválido em {item}")
    return ajustes


def _autotune_dos_args(args, mensagem: str) -> dict:
    if getattr(args, "sem_autotune", False):
        return {"params": {"temperature": 0.7}, "contexto": "conversational", "confianca": 0, "motivo": "AutoTune desligado",
                "estrategia": "nenhuma", "ranking": [], "sinais": [], "deltas": []}
    aprendizado = None if getattr(args, "sem_aprendizado", False) else ler_aprendizado().get("learnedProfiles")
    return autotune(mensagem, (), args.estrategia, aprendizado, _parse_ajustes(args.ajuste))


def cmd_autotune(args) -> int:
    if args.listar:
        linhas = [f"{c:<15} {ROTULO_CONTEXTO[c]:<13} {_fmt_params(PERFIS[c])}" for c in CONTEXTOS]
        linhas += ["", "Estratégias fixas:"] + [f"{e:<15} {_fmt_params(p)}" for e, p in ESTRATEGIAS.items()]
        _imprimir({"contextos": PERFIS, "estrategias": ESTRATEGIAS}, args.json, "\n".join(linhas))
        return 0
    mensagem = _ler_entrada(args.mensagem, args.arquivo)
    historico = _ler(Path(args.historico), []) if args.historico else []
    aprendizado = None if args.sem_aprendizado else ler_aprendizado().get("learnedProfiles")
    r = autotune(mensagem, historico, args.estrategia, aprendizado, _parse_ajustes(args.ajuste))
    guardar_ultimo({"comando": "autotune", "contexto": r["contexto"], "params": r["params"], "modelo": ""})
    ranking = ", ".join(f"{ROTULO_CONTEXTO[x['contexto']]} {x['porcentagem']}%" for x in r["ranking"][:5]) or "—"
    linhas = [f"Contexto: {ROTULO_CONTEXTO[r['contexto']]} ({r['contexto']}) · {r['motivo']}",
              f"Parâmetros: {_fmt_params(r['params'])}",
              f"Disputa: {ranking}",
              f"Sinais: {'; '.join(r['sinais'][:6]) or '—'}"]
    _imprimir(r, args.json, "\n".join(linhas))
    return 0


def cmd_stm(args) -> int:
    modulos = resolver_modulos(args.modulos)
    texto = _ler_entrada(args.texto, args.arquivo)
    saida = aplicar_stm(texto, modulos)
    _imprimir({"modulos": modulos, "texto": saida}, args.json, saida)
    return 0


def cmd_pontuar(args) -> int:
    texto = _ler_entrada(args.texto, args.arquivo)
    r = pontuar(texto, args.pergunta or "")
    linha = (f"{r['pontos']}/100 · comprimento {r['comprimento']}/25 · estrutura {r['estrutura']}/20 · "
             f"objetividade {r['objetividade']}/15 · relevância {r['relevancia']}/15"
             + (" · possível recusa" if r["possivel_recusa"] else ""))
    _imprimir(r, args.json, linha)
    return 0


def _mensagens(args, pergunta: str) -> list[dict]:
    msgs = []
    if args.sistema:
        msgs.append({"role": "system", "content": args.sistema})
    msgs.append({"role": "user", "content": pergunta})
    return msgs


def _preparar_remoto(cfg: dict) -> None:
    if cfg["nome"] == "openrouter":
        verificar_autenticacao(cfg)


def cmd_perguntar(args) -> int:
    pergunta = _ler_entrada(args.mensagem, args.arquivo)
    cfg = provedor(args.provedor, args.base_url, args.chave_env)
    modelo = args.modelo or os.environ.get("GOD_MODE_MODELO") or ""
    if not modelo:
        if cfg["nome"] == "openrouter":
            modelo = MODELO_PADRAO_OPENROUTER
        else:
            lista = listar_modelos(cfg)
            if not lista:
                raise Erro(f"{cfg['base']} não lista nenhum modelo; passe --modelo", 2)
            modelo = lista[0]["id"]
    _preparar_remoto(cfg)
    at = _autotune_dos_args(args, pergunta)
    mensagens = _mensagens(args, pergunta)
    if cfg["nome"] == "openrouter":
        custo = estimar_custo(listar_modelos(cfg), [modelo], mensagens, args.max_tokens)
        if custo["ausentes"]:
            raise Erro(f"o modelo {modelo} não está na lista atual da OpenRouter (veja: god_mode.py modelos --busca)")
        if custo["teto_usd"] > args.orcamento:
            raise Erro(f"teto estimado US$ {custo['teto_usd']:.4f} passa do orçamento US$ {args.orcamento:.2f}; "
                       "reduza --max-tokens ou aumente --orcamento", 3)
    r = consultar_modelo(cfg, modelo, mensagens, at["params"], args.max_tokens, args.timeout)
    if not r["sucesso"]:
        raise Erro(f"{modelo} falhou: {r['erro']}", 4)
    modulos = resolver_modulos(args.stm)
    texto = aplicar_stm(r["conteudo"], modulos)
    guardar_ultimo({"comando": "perguntar", "contexto": at["contexto"], "params": at["params"], "modelo": modelo,
                    "heuristicas": heuristicas(r["conteudo"])})
    dados = {"modelo": modelo, "provedor": cfg["nome"], "contexto": at["contexto"], "params": at["params"],
             "duracao_ms": r["duracao_ms"], "stm": modulos, "resposta": texto, "pontuacao": pontuar(texto, pergunta)}
    rodape = (f"\n— {modelo} via {cfg['nome']} · {r['duracao_ms'] / 1000:.1f} s · contexto "
              f"{ROTULO_CONTEXTO.get(at['contexto'], at['contexto'])} · {_fmt_params(at['params'])}")
    _imprimir(dados, args.json, texto + rodape)
    return 0


def cmd_comparar(args) -> int:
    pergunta = _ler_entrada(args.mensagem, args.arquivo)
    cfg = provedor(args.provedor, args.base_url, args.chave_env)
    _preparar_remoto(cfg)
    catalogo = listar_modelos(cfg) if (cfg["nome"] == "openrouter" or not args.modelos) else []
    if args.modelos:
        modelos = [m.strip() for m in args.modelos.split(",") if m.strip()]
    elif cfg["nome"] == "openrouter":
        modelos = modelos_da_camada(args.camada)
    else:
        modelos = [m["id"] for m in catalogo]
    modelos = list(dict.fromkeys(modelos))
    fora: list[str] = []
    if cfg["nome"] == "openrouter":
        ids = {m["id"] for m in catalogo}
        fora = [m for m in modelos if m not in ids]
        modelos = [m for m in modelos if m in ids]
    if args.max and len(modelos) > args.max:
        modelos = modelos[:args.max]
    if not modelos:
        raise Erro("nenhum modelo disponível para comparar" + (f" (fora do catálogo: {', '.join(fora)})" if fora else ""))
    at = _autotune_dos_args(args, pergunta)
    mensagens = _mensagens(args, pergunta)
    custo = None
    if cfg["nome"] == "openrouter":
        custo = estimar_custo(catalogo, modelos, mensagens, args.max_tokens)
        if custo["teto_usd"] > args.orcamento:
            raise Erro(f"teto estimado US$ {custo['teto_usd']:.4f} para {len(modelos)} modelos passa do orçamento "
                       f"US$ {args.orcamento:.2f}; use menos modelos (--max), menos --max-tokens ou aumente --orcamento", 3)
    resultados, pendentes = corrida(cfg, modelos, mensagens, at["params"], args.max_tokens, args.min_resultados,
                                    args.espera, args.limite, args.timeout)
    modulos = resolver_modulos(args.stm)
    for r in resultados:
        if r["sucesso"]:
            r["pontuacao"] = pontuar(r["conteudo"], pergunta)
            r["pontos"] = r["pontuacao"]["pontos"]
            if modulos:
                r["conteudo_stm"] = aplicar_stm(r["conteudo"], modulos)
    ok = sorted((r for r in resultados if r["sucesso"]), key=lambda r: (-r["pontos"], r["duracao_ms"]))
    falhas = [r for r in resultados if not r["sucesso"]]
    pasta = pasta_estado() / "comparacoes"
    arquivo = pasta / f"{datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}.json"
    registro = {"pergunta": pergunta, "sistema": args.sistema or "", "provedor": cfg["nome"],
                "contexto": at["contexto"], "params": at["params"], "custo_estimado": custo,
                "fora_do_catalogo": fora, "sem_resposta_no_prazo": pendentes, "respostas": ok, "falhas": falhas}
    _gravar(arquivo, registro)
    if ok:
        guardar_ultimo({"comando": "comparar", "contexto": at["contexto"], "params": at["params"],
                        "modelo": ok[0]["modelo"], "heuristicas": heuristicas(ok[0]["conteudo"]),
                        "arquivo": str(arquivo)})
    linhas = [f"Contexto: {ROTULO_CONTEXTO.get(at['contexto'], at['contexto'])} · {_fmt_params(at['params'])}",
              f"Modelos: {len(modelos)} consultados · {len(ok)} responderam · {len(falhas)} com erro · "
              f"{len(pendentes)} sem resposta no prazo"
              + (f" · teto estimado US$ {custo['teto_usd']:.4f}" if custo else "")]
    if fora:
        linhas.append(f"Fora do catálogo atual (pulados): {', '.join(fora)}")
    linhas.append("")
    linhas.append(f"{'#':>2}  {'pontos':>6}  {'tempo':>7}  {'recusa?':<7}  modelo")
    for i, r in enumerate(ok, 1):
        linhas.append(f"{i:>2}  {r['pontos']:>6}  {r['duracao_ms'] / 1000:>6.1f}s  "
                      f"{'sim' if r['pontuacao']['possivel_recusa'] else 'não':<7}  {r['modelo']}")
    for r in falhas:
        linhas.append(f"{'-':>2}  {'-':>6}  {r['duracao_ms'] / 1000:>6.1f}s  {'':<7}  {r['modelo']} — {r['erro']}")
    for m in pendentes:
        linhas.append(f"{'-':>2}  {'-':>6}  {'—':>7}  {'':<7}  {m} — sem resposta no prazo")
    linhas.append("")
    linhas.append(f"Respostas completas: {arquivo}")
    if ok:
        melhor = ok[0]
        texto = melhor.get("conteudo_stm") or melhor["conteudo"]
        corte = texto if len(texto) <= args.mostrar else texto[:args.mostrar] + "\n[…]"
        linhas += ["", f"── maior pontuação: {melhor['modelo']} ──", corte]
    _imprimir(dict(registro, arquivo=str(arquivo)), args.json, "\n".join(linhas))
    return 0 if ok else 4


def cmd_modelos(args) -> int:
    cfg = provedor(args.provedor, args.base_url, args.chave_env)
    lista = listar_modelos(cfg)
    por_id = {m["id"]: m for m in lista}

    def preco(m):
        p = (m or {}).get("pricing") or {}
        try:
            return f"US$ {float(p.get('prompt', 0)) * 1e6:.2f}/M entrada · US$ {float(p.get('completion', 0)) * 1e6:.2f}/M saída"
        except (TypeError, ValueError):
            return "preço variável"

    if args.camada:
        ids = modelos_da_camada(args.camada)
        linhas = [f"Camada {args.camada} do original ({len(ids)} modelos) × catálogo atual de {cfg['nome']}:"]
        disp = 0
        for mid in ids:
            m = por_id.get(mid)
            disp += bool(m)
            linhas.append(f"  {'✓' if m else '✗'} {mid}" + (f" — {preco(m)}" if m and cfg['nome'] == 'openrouter' else ""))
        linhas.append(f"{disp} de {len(ids)} disponíveis agora.")
        _imprimir({"camada": args.camada, "modelos": [{"id": i, "disponivel": i in por_id} for i in ids]},
                  args.json, "\n".join(linhas))
        return 0
    filtro = (args.busca or "").lower()
    sel = [m for m in lista if filtro in m["id"].lower() or filtro in str(m.get("name", "")).lower()]
    linhas = [f"{len(sel)} de {len(lista)} modelos em {cfg['nome']}" + (f" com \"{args.busca}\"" if filtro else "") + ":"]
    for m in sel[:args.limite]:
        extra = f" — {preco(m)}" if cfg["nome"] == "openrouter" else ""
        ctx = f" · {m['context_length']:,} tokens".replace(",", ".") if m.get("context_length") else ""
        linhas.append(f"  {m['id']}{extra}{ctx}")
    if len(sel) > args.limite:
        linhas.append(f"  … mais {len(sel) - args.limite} (use --limite ou --busca)")
    _imprimir({"total": len(lista), "modelos": sel[:args.limite]}, args.json, "\n".join(linhas))
    return 0


def _nota_valor(texto: str) -> int:
    t = texto.strip().lower()
    if t in ("+1", "1", "+", "bom", "boa", "gostei", "sim", "up", "👍"):
        return 1
    if t in ("-1", "-", "ruim", "nao", "não", "naogostei", "não-gostei", "nao-gostei", "down", "👎"):
        return -1
    raise Erro(f"nota inválida: {texto} (use +1/bom ou -1/ruim)")


def cmd_nota(args) -> int:
    valor = _nota_valor(args.nota)
    ultimo = _ler(pasta_estado() / "ultimo.json", {})
    contexto = args.contexto or ultimo.get("contexto")
    params = json.loads(args.params) if args.params else ultimo.get("params")
    if not contexto or not params:
        raise Erro("nada para avaliar: rode autotune, perguntar ou comparar antes, ou passe --contexto e --params")
    if contexto not in CONTEXTOS:
        raise Erro(f"contexto desconhecido: {contexto}")
    completos = dict(NEUTRO)
    completos.update({k: float(v) for k, v in params.items() if k in PARAMS})
    registro = {"messageId": uuid.uuid4().hex, "timestamp": int(time.time() * 1000), "contextType": contexto,
                "model": args.modelo or ultimo.get("modelo", ""), "persona": "", "params": completos,
                "rating": valor, "heuristics": ultimo.get("heuristicas") or heuristicas("")}
    estado = registrar_nota(ler_aprendizado(), registro)
    _gravar(pasta_estado() / "feedback.json", estado)
    perfil = estado["learnedProfiles"][contexto]
    falta = max(0, MIN_AMOSTRAS - perfil["sampleCount"])
    linha = (f"Nota {'+1' if valor == 1 else '-1'} guardada para {ROTULO_CONTEXTO[contexto]} "
             f"({perfil['positiveCount']} boas, {perfil['negativeCount']} ruins). "
             + (f"Faltam {falta} nota(s) para o AutoTune começar a usar o aprendizado." if falta else
                "O AutoTune já usa o aprendizado deste contexto." if perfil["adjustments"] else
                "Ainda sem ajuste: as notas não apontam uma direção."))
    _imprimir({"registro": registro, "perfil": perfil}, args.json, linha)
    return 0


def cmd_aprendizado(args) -> int:
    estado = ler_aprendizado()
    if args.zerar:
        _gravar(pasta_estado() / "feedback.json", estado_inicial())
        print("Aprendizado zerado.")
        return 0
    st = estatisticas(estado)
    linhas = [(f"{st['total']} nota(s), {js_round(st['taxa_positiva'] * 100)}% boas · arquivo "
               f"{pasta_estado() / 'feedback.json'}")]
    for ctx, c in sorted(st["contextos"].items(), key=lambda kv: -kv[1]["total"]):
        aj = ", ".join(f"{ROTULO_PARAM[k]} {v:+.3f}" for k, v in c["ajustes"].items()) or "sem ajuste"
        linhas.append(f"  {ROTULO_CONTEXTO.get(ctx, ctx):<13} {c['positivas']}+ {c['negativas']}− · "
                      f"{'aplicando' if c['aprendeu'] else 'aprendendo'} · {aj}")
    _imprimir(st, args.json, "\n".join(linhas))
    return 0


def cmd_status(args) -> int:
    linhas = [f"god-mode {VERSAO} · {ORIGEM} · Python {sys.version.split()[0]}"]
    estado = ler_aprendizado()
    linhas.append(f"Estado: {pasta_estado()} · {len(estado.get('history') or [])} nota(s) de aprendizado")
    info: dict = {"versao": VERSAO, "estado": str(pasta_estado())}
    cfg = provedor("openrouter")
    try:
        n = len(listar_modelos(cfg, timeout=10))
        rede = f"rede ok ({n} modelos públicos)"
    except Erro as e:
        n, rede = 0, f"sem rede ({e})"
    if n:
        try:
            verificar_autenticacao(cfg)
            aut = "autenticada"
        except Erro:
            aut = "sem autenticação"
    else:
        aut = "não verificada"
    chave = "definida" if cfg["chave"] else "ausente"
    linhas.append(f"OpenRouter: {rede} · {cfg['chave_env']} {chave} · {aut}")
    info["openrouter"] = {"modelos": n, "chave_no_ambiente": bool(cfg["chave"]), "autenticacao": aut}
    loc = provedor("local")
    try:
        ids = [m["id"] for m in listar_modelos(loc, timeout=3)]
        linhas.append(f"Local ({loc['base']}): {len(ids)} modelo(s): {', '.join(ids[:5]) or '—'}")
        info["local"] = {"base": loc["base"], "modelos": ids}
    except Erro:
        linhas.append(f"Local ({loc['base']}): sem servidor (defina GOD_MODE_LOCAL_URL se usar Ollama/LM Studio)")
        info["local"] = {"base": loc["base"], "modelos": None}
    pronto = ["autotune", "stm", "pontuar", "nota", "aprendizado"]
    if aut == "autenticada" or info["local"]["modelos"]:
        pronto += ["perguntar", "comparar"]
    linhas.append(f"Disponível agora: {', '.join(pronto)}")
    if aut != "autenticada" and not info["local"]["modelos"]:
        linhas.append("Para perguntar/comparar: " + explicar_chave(cfg))
    info["disponivel"] = pronto
    _imprimir(info, args.json, "\n".join(linhas))
    return 0


def _comuns_modelo(p: argparse.ArgumentParser, timeout: float) -> None:
    p.add_argument("--provedor", default="openrouter", choices=["openrouter", "local", "outro"])
    p.add_argument("--base-url", help="URL OpenAI-compatível (…/v1); padrão por provedor")
    p.add_argument("--chave-env", help="nome da variável de ambiente com a chave")
    p.add_argument("--sistema", help="prompt de sistema (opcional)")
    p.add_argument("--max-tokens", type=int, default=2048)
    p.add_argument("--timeout", type=float, default=timeout, help="segundos por modelo")
    p.add_argument("--orcamento", type=float, default=0.25, help="teto estimado em US$ (OpenRouter)")
    p.add_argument("--estrategia", default="adaptive", choices=["adaptive", *ESTRATEGIAS])
    p.add_argument("--ajuste", action="append", metavar="PARAM=VALOR", help="sobrescreve um parâmetro")
    p.add_argument("--sem-autotune", action="store_true")
    p.add_argument("--sem-aprendizado", action="store_true")
    p.add_argument("--stm", help="módulos STM na resposta: hesitacao,direto,casual")
    p.add_argument("--arquivo", help="lê a pergunta de um arquivo (- = entrada padrão)")
    p.add_argument("--json", action="store_true")


def construir_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="god_mode.py", description="Adaptação do G0DM0D3 para o Claude Code.")
    sub = ap.add_subparsers(dest="comando", required=True)

    p = sub.add_parser("status", help="o que está disponível (chaves, rede, servidor local)")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("autotune", help="contexto e parâmetros de amostragem para uma mensagem")
    p.add_argument("mensagem", nargs="?")
    p.add_argument("--arquivo")
    p.add_argument("--historico", help="JSON com [{role, content}, …]")
    p.add_argument("--estrategia", default="adaptive", choices=["adaptive", *ESTRATEGIAS])
    p.add_argument("--ajuste", action="append", metavar="PARAM=VALOR")
    p.add_argument("--sem-aprendizado", action="store_true")
    p.add_argument("--listar", action="store_true", help="mostra os 20 contextos e as estratégias")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_autotune)

    p = sub.add_parser("stm", help="aplica os módulos de estilo a um texto")
    p.add_argument("modulos", help="hesitacao,direto,casual")
    p.add_argument("texto", nargs="?")
    p.add_argument("--arquivo")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_stm)

    p = sub.add_parser("pontuar", help="pontuação neutra (0–100) de uma resposta")
    p.add_argument("texto", nargs="?")
    p.add_argument("--pergunta", default="")
    p.add_argument("--arquivo")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_pontuar)

    p = sub.add_parser("perguntar", help="consulta um modelo com AutoTune")
    p.add_argument("mensagem", nargs="?")
    p.add_argument("--modelo")
    _comuns_modelo(p, timeout=90.0)
    p.set_defaults(func=cmd_perguntar)

    p = sub.add_parser("comparar", help="vários modelos em paralelo, pontuação neutra e arquivo para síntese")
    p.add_argument("mensagem", nargs="?")
    p.add_argument("--modelos", help="ids separados por vírgula")
    p.add_argument("--camada", default="fast", choices=list(ORDEM_CAMADAS))
    p.add_argument("--max", type=int, default=6, help="máximo de modelos (0 = todos da camada)")
    p.add_argument("--min-resultados", type=int, default=MIN_RESULTADOS)
    p.add_argument("--espera", type=float, default=ESPERA_EXTRA, help="segundos extras após o mínimo")
    p.add_argument("--limite", type=float, default=LIMITE_TOTAL, help="limite total em segundos")
    p.add_argument("--mostrar", type=int, default=4000, help="caracteres da melhor resposta na saída")
    _comuns_modelo(p, timeout=TIMEOUT_MODELO)
    p.set_defaults(func=cmd_comparar)

    p = sub.add_parser("modelos", help="lista modelos do provedor ou confere uma camada do original")
    p.add_argument("--provedor", default="openrouter", choices=["openrouter", "local", "outro"])
    p.add_argument("--base-url")
    p.add_argument("--chave-env")
    p.add_argument("--camada", choices=list(ORDEM_CAMADAS))
    p.add_argument("--busca")
    p.add_argument("--limite", type=int, default=30)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_modelos)

    p = sub.add_parser("nota", help="avalia a última resposta (+1/-1) para o AutoTune aprender")
    p.add_argument("nota")
    p.add_argument("--contexto", choices=list(CONTEXTOS))
    p.add_argument("--params", help="JSON com os parâmetros avaliados")
    p.add_argument("--modelo")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_nota)

    p = sub.add_parser("aprendizado", help="o que o AutoTune aprendeu com as notas")
    p.add_argument("--zerar", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_aprendizado)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = construir_parser().parse_args(sys.argv[1:] if argv is None else argv)
    try:
        return args.func(args)
    except Erro as e:
        print(f"erro: {e}", file=sys.stderr)
        return e.codigo


if __name__ == "__main__":
    sys.exit(main())
