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
if ($D.monitor -ge 1 -and $D.monitor -le $telas.Count) { $b = $telas[$D.monitor - 1].Bounds }
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

    def capturar(self, monitor: int = 0, largura: int = 1600, qualidade: int = 70) -> dict:
        largura = max(320, min(int(largura or 1600), 3840))
        qualidade = max(20, min(int(qualidade or 70), 95))
        r = json.loads(rodar_ps(_CAPTURA, {"monitor": int(monitor or 0), "largura": largura, "qualidade": qualidade}))
        jpeg = r.pop("jpeg")
        r["escala"] = round(r["w"] / r["largura"], 5)
        self.ultima = r
        return {"tela": {"origem": [r["x"], r["y"]], "tamanho_real": [r["largura"], r["altura"]],
                         "tamanho_imagem": [r["w"], r["h"]], "monitores": r["telas"]},
                "dica": "pc_entrada usa as coordenadas desta imagem (o agente converte para a tela real)",
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
