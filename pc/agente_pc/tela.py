"""Tela, mouse e teclado do Windows, pelo PowerShell (.NET), sem instalar nada.

O agente roda na sessão do usuário (tarefa agendada no logon), por isso enxerga e controla a área de trabalho.
As coordenadas do pc_entrada são, por padrão, as da última imagem do pc_tela: o agente converte para a tela real.
"""
from __future__ import annotations

import base64
import json
import os
import subprocess

WINDOWS = os.name == "nt"

_CAPTURA = r"""
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
Add-Type -Namespace AgPc -Name Dpi -MemberDefinition '[DllImport("user32.dll")] public static extern bool SetProcessDPIAware();'
[void][AgPc.Dpi]::SetProcessDPIAware()
$telas = [System.Windows.Forms.Screen]::AllScreens
if ($D.regiao) { $b = New-Object System.Drawing.Rectangle ([int]$D.regiao[0]), ([int]$D.regiao[1]), ([int]$D.regiao[2]), ([int]$D.regiao[3]) }
elseif ($D.monitor -ge 1 -and $D.monitor -le $telas.Count) { $b = $telas[$D.monitor - 1].Bounds }
else { $b = [System.Windows.Forms.SystemInformation]::VirtualScreen }
$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Left, $b.Top, 0, 0, $bmp.Size)
$g.Dispose()
$esc = [Math]::Min(1.0, $D.largura / $b.Width)
$w = [int]($b.Width * $esc); $h = [int]($b.Height * $esc)
$out = New-Object System.Drawing.Bitmap $w, $h
$g2 = [System.Drawing.Graphics]::FromImage($out)
$g2.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g2.DrawImage($bmp, 0, 0, $w, $h)
$g2.Dispose()
$cod = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$ep = New-Object System.Drawing.Imaging.EncoderParameters 1
$ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), ([long]$D.qualidade)
$ms = New-Object System.IO.MemoryStream
$out.Save($ms, $cod, $ep)
@{ x = $b.Left; y = $b.Top; largura = $b.Width; altura = $b.Height; w = $w; h = $h; telas = $telas.Count;
   jpeg = [Convert]::ToBase64String($ms.ToArray()) } | ConvertTo-Json -Compress
"""

# Vários momentos numa imagem só (grade), cada quadro com a hora em que foi tirado. Serve para ver animações,
# transições de tela e o resultado de uma ação sem uma chamada por foto.
_MONTAGEM = r"""
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
Add-Type -Namespace AgPc -Name Dpi -MemberDefinition '[DllImport("user32.dll")] public static extern bool SetProcessDPIAware();'
[void][AgPc.Dpi]::SetProcessDPIAware()
$telas = [System.Windows.Forms.Screen]::AllScreens
if ($D.regiao) { $b = New-Object System.Drawing.Rectangle ([int]$D.regiao[0]), ([int]$D.regiao[1]), ([int]$D.regiao[2]), ([int]$D.regiao[3]) }
elseif ($D.monitor -ge 1 -and $D.monitor -le $telas.Count) { $b = $telas[$D.monitor - 1].Bounds }
else { $b = [System.Windows.Forms.SystemInformation]::VirtualScreen }
$n = [int]$D.quadros; $cols = [int]$D.colunas; $linhas = [int][Math]::Ceiling($n / $cols)
$cw = [int][Math]::Min([int]$D.largura_celula, $b.Width)
$ch = [int][Math]::Max(1, [Math]::Round($cw * $b.Height / $b.Width))
$folha = New-Object System.Drawing.Bitmap ($cw * $cols), ($ch * $linhas)
$gf = [System.Drawing.Graphics]::FromImage($folha)
$gf.Clear([System.Drawing.Color]::Black)
$gf.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$fonte = New-Object System.Drawing.Font 'Segoe UI', 14, ([System.Drawing.FontStyle]::Bold), ([System.Drawing.GraphicsUnit]::Pixel)
$fundo = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(200, 0, 0, 0))
$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$relogio = [System.Diagnostics.Stopwatch]::StartNew()
$tempos = New-Object System.Collections.ArrayList
for ($i = 0; $i -lt $n; $i++) {
  $falta = $i * [int]$D.intervalo - $relogio.ElapsedMilliseconds
  if ($falta -gt 0) { Start-Sleep -Milliseconds $falta }
  $t = $relogio.ElapsedMilliseconds
  $g.CopyFromScreen($b.Left, $b.Top, 0, 0, $bmp.Size)
  $cx = ($i % $cols) * $cw; $cy = [int][Math]::Floor($i / $cols) * $ch
  $gf.DrawImage($bmp, $cx, $cy, $cw, $ch)
  $gf.FillRectangle($fundo, $cx, $cy, 64, 24)
  $gf.DrawString(('{0:N1}s' -f ($t / 1000.0)), $fonte, [System.Drawing.Brushes]::White, ($cx + 4), ($cy + 3))
  [void]$tempos.Add([Math]::Round($t / 1000.0, 2))
}
$g.Dispose(); $bmp.Dispose(); $gf.Dispose()
$cod = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
$ep = New-Object System.Drawing.Imaging.EncoderParameters 1
$ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), ([long]$D.qualidade)
$ms = New-Object System.IO.MemoryStream
$folha.Save($ms, $cod, $ep)
@{ x = $b.Left; y = $b.Top; largura = $b.Width; altura = $b.Height; w = $folha.Width; h = $folha.Height; telas = $telas.Count;
   tempos = @($tempos); jpeg = [Convert]::ToBase64String($ms.ToArray()) } | ConvertTo-Json -Compress
"""

_ENTRADA = r"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -Namespace AgPc -Name In -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
[DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
[DllImport("user32.dll")] public static extern void mouse_event(uint f, int dx, int dy, int d, System.UIntPtr e);
'@
[void][AgPc.In]::SetProcessDPIAware()
function Ev($f, $d = 0) { [AgPc.In]::mouse_event([uint32]$f, 0, 0, [int]$d, [UIntPtr]::Zero) }
function Pos($x, $y) { [void][AgPc.In]::SetCursorPos([int]$x, [int]$y); Start-Sleep -Milliseconds 40 }
function Clique($baixo, $cima) { Ev $baixo; Start-Sleep -Milliseconds 30; Ev $cima }
switch ($D.acao) {
  'mover'    { Pos $D.x $D.y }
  'clicar'   { Pos $D.x $D.y; Clique 2 4 }
  'duplo'    { Pos $D.x $D.y; Clique 2 4; Start-Sleep -Milliseconds 70; Clique 2 4 }
  'direito'  { Pos $D.x $D.y; Clique 8 16 }
  'meio'     { Pos $D.x $D.y; Clique 32 64 }
  'arrastar' {
    Pos $D.x $D.y; Ev 2
    for ($i = 1; $i -le 20; $i++) { Pos ($D.x + ($D.x2 - $D.x) * $i / 20) ($D.y + ($D.y2 - $D.y) * $i / 20) }
    Ev 4
  }
  'rolar'    { if ($null -ne $D.x) { Pos $D.x $D.y }; Ev 0x800 (120 * $D.quantidade) }
  'digitar'  { [System.Windows.Forms.SendKeys]::SendWait($D.texto) }
  'teclas'   { [System.Windows.Forms.SendKeys]::SendWait($D.teclas) }
}
$p = [System.Windows.Forms.Cursor]::Position
"$($p.X) $($p.Y)"
"""


def rodar_ps(script: str, dados: dict, timeout: float = 60) -> str:
    """Roda um script curto do PowerShell com $D = dados (JSON). Devolve a saída; lança RuntimeError se falhar."""
    if not WINDOWS:
        raise RuntimeError("tela e entrada só no Windows")
    b64 = base64.b64encode(json.dumps(dados).encode()).decode()
    completo = ("$ErrorActionPreference = 'Stop'\n"
                f"$D = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{b64}')) | ConvertFrom-Json\n"
                + script)
    cod = base64.b64encode(completo.encode("utf-16-le")).decode()
    r = subprocess.run(["powershell", "-NoLogo", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                        "-EncodedCommand", cod], capture_output=True, timeout=timeout,
                       creationflags=subprocess.CREATE_NO_WINDOW)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode("utf-8", errors="replace").strip()[-600:] or f"PowerShell saiu com {r.returncode}")
    return r.stdout.decode("utf-8", errors="replace").strip()


LIMITE_QUADROS = 12
LIMITE_TOTAL_MS = 20_000  # tempo máximo de uma montagem: a chamada inteira precisa caber na espera do conector


def plano_montagem(quadros: int, colunas: int | None, largura: int) -> dict:
    """Grade da montagem: quantas colunas e linhas, e a largura de cada quadro (a largura total é o teto)."""
    n = int(quadros)
    if not 2 <= n <= LIMITE_QUADROS:
        raise ValueError(f"quadros deve ficar entre 2 e {LIMITE_QUADROS} (1 é uma captura normal)")
    cols = max(1, min(int(colunas), n)) if colunas else (2 if n <= 4 else 3 if n <= 9 else 4)
    return {"quadros": n, "colunas": cols, "linhas": -(-n // cols), "largura_celula": max(160, int(largura) // cols)}


def escapar_sendkeys(texto: str) -> str:
    especiais = set("+^%~(){}[]")
    saida = []
    for c in texto:
        if c in especiais:
            saida.append("{" + c + "}")
        elif c == "\n":
            saida.append("{ENTER}")
        elif c == "\t":
            saida.append("{TAB}")
        elif c != "\r":
            saida.append(c)
    return "".join(saida)


class Tela:
    def __init__(self):
        self.ultima: dict | None = None  # mapeamento da última captura (imagem -> tela)

    def regiao_real(self, regiao, coordenadas: str = "imagem"):
        """[x, y, largura, altura] nas coordenadas da última imagem (ou da tela) -> pixels reais da tela."""
        if regiao is None:
            return None
        try:
            x, y, w, h = (float(v) for v in regiao)
        except (TypeError, ValueError):
            raise ValueError("regiao deve ser [x, y, largura, altura]") from None
        if w < 8 or h < 8:
            raise ValueError("regiao pequena demais (mínimo 8 x 8)")
        u = self.ultima
        if coordenadas != "tela" and u:
            x, y, w, h = u["x"] + x / u["escala"], u["y"] + y / u["escala"], w / u["escala"], h / u["escala"]
        return [int(round(x)), int(round(y)), max(1, int(round(w))), max(1, int(round(h)))]

    def capturar(self, monitor: int = 0, largura: int = 1600, qualidade: int = 70, regiao=None, quadros: int = 1,
                 intervalo: int = 500, colunas: int | None = None, coordenadas: str = "imagem") -> dict:
        largura = max(320, min(int(largura or 1600), 3840))
        qualidade = max(20, min(int(qualidade or 70), 95))
        quadros = int(quadros or 1)
        reg = self.regiao_real(regiao, coordenadas)
        base = {"monitor": int(monitor or 0), "largura": largura, "qualidade": qualidade, "regiao": reg}
        if quadros > 1:
            return self._montagem(base, quadros, int(intervalo or 500), colunas)
        r = json.loads(rodar_ps(_CAPTURA, base))
        jpeg = r.pop("jpeg")
        r["escala"] = round(r["w"] / r["largura"], 5)
        self.ultima = r  # com região, o mapa passa a ser o da região: clicar na imagem cai no lugar certo
        return {"tela": {"origem": [r["x"], r["y"]], "tamanho_real": [r["largura"], r["altura"]],
                         "tamanho_imagem": [r["w"], r["h"]], "monitores": r["telas"]},
                "dica": "pc_entrada usa as coordenadas desta imagem (o agente converte para a tela real)",
                "_imagem": {"base64": jpeg, "mime": "image/jpeg"}}

    def _montagem(self, base: dict, quadros: int, intervalo: int, colunas) -> dict:
        intervalo = max(100, min(intervalo, 5000))
        total = (quadros - 1) * intervalo
        if total > LIMITE_TOTAL_MS:
            raise ValueError(f"montagem longa demais ({total / 1000:.0f} s): use no máximo {LIMITE_TOTAL_MS // 1000} s "
                             "(menos quadros ou intervalo menor)")
        plano = plano_montagem(quadros, colunas, base["largura"])
        r = json.loads(rodar_ps(_MONTAGEM, {**base, "intervalo": intervalo, "colunas": plano["colunas"],
                                            "quadros": plano["quadros"], "largura_celula": plano["largura_celula"]},
                                timeout=60 + total / 1000))
        jpeg = r.pop("jpeg")
        # a montagem não muda o mapa de cliques (self.ultima): as coordenadas de uma grade não valem para o pc_entrada
        return {"montagem": {"quadros": plano["quadros"], "colunas": plano["colunas"], "linhas": plano["linhas"],
                             "intervalo_ms": intervalo, "tempos_s": r["tempos"],
                             "area": [r["x"], r["y"], r["largura"], r["altura"]]},
                "tela": {"tamanho_imagem": [r["w"], r["h"]], "monitores": r["telas"]},
                "dica": "grade da esquerda para a direita e de cima para baixo; o rótulo de cada quadro é o tempo em "
                        "segundos. Não use estas coordenadas no pc_entrada: faça um pc_tela normal antes de clicar.",
                "_imagem": {"base64": jpeg, "mime": "image/jpeg"}}

    def para_tela(self, x, y, coordenadas: str = "imagem"):
        if x is None or y is None:
            return None, None
        if coordenadas == "tela" or not self.ultima:
            return int(x), int(y)
        u = self.ultima
        return int(round(u["x"] + float(x) / u["escala"])), int(round(u["y"] + float(y) / u["escala"]))

    def entrada(self, acao: str, x=None, y=None, x2=None, y2=None, texto=None, teclas=None, quantidade=None,
                coordenadas: str = "imagem") -> dict:
        acoes = {"mover", "clicar", "duplo", "direito", "meio", "arrastar", "rolar", "digitar", "teclas"}
        if acao not in acoes:
            raise ValueError(f"acao deve ser uma de: {', '.join(sorted(acoes))}")
        d = {"acao": acao}
        if acao in ("mover", "clicar", "duplo", "direito", "meio", "arrastar") and (x is None or y is None):
            raise ValueError("informe x e y")
        d["x"], d["y"] = self.para_tela(x, y, coordenadas)
        if acao == "arrastar":
            if x2 is None or y2 is None:
                raise ValueError("arrastar precisa de x2 e y2")
            d["x2"], d["y2"] = self.para_tela(x2, y2, coordenadas)
        if acao == "rolar":
            d["quantidade"] = int(quantidade or -3)  # negativo = para baixo
        if acao == "digitar":
            if not texto:
                raise ValueError("informe o texto")
            d["texto"] = escapar_sendkeys(str(texto))
        if acao == "teclas":
            if not teclas:
                raise ValueError("informe as teclas no formato do SendKeys, ex.: ^s, {ENTER}, %{F4}")
            d["teclas"] = str(teclas)
        cursor = rodar_ps(_ENTRADA, d)
        return {"feito": acao, "na_tela": [d.get("x"), d.get("y")], "cursor_agora": cursor}
