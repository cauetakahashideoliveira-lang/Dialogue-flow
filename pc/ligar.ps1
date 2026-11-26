#Requires -Version 5.1
<#
  Botão "Ligar Agente PC" (o instalar.ps1 cria o atalho na área de trabalho).

  Liga o agente da Central se ele estiver parado e mostra numa janela se o PC está conectado à Central.
  Não pede senha de administrador: só dispara a tarefa agendada "Agente PC - Central", que já roda como
  administrador. Se o agente já estiver ligado, só confere a conexão.
#>
$ErrorActionPreference = 'Continue'
$tarefa = 'Agente PC - Central'
$dados = Join-Path $env:LOCALAPPDATA 'agente-pc'
Add-Type -AssemblyName System.Windows.Forms

function Aviso([string]$texto, [string]$icone = 'Information') {
    [void][System.Windows.Forms.MessageBox]::Show($texto, 'Agente PC - Central', [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::$icone)
}
function Saude {
    try {
        $porta = (Get-Content (Join-Path $dados 'config.json') -Raw | ConvertFrom-Json).porta
        Invoke-RestMethod "http://127.0.0.1:$porta/saude" -TimeoutSec 3
    } catch { $null }
}

if (-not (Get-ScheduledTask -TaskName $tarefa -ErrorAction SilentlyContinue)) {
    Aviso "A tarefa '$tarefa' não existe neste PC.`nRode o instalador: pc\instalar.ps1 (PowerShell como administrador)." 'Error'
    exit 1
}
$s = Saude
$ligou = $false
if (-not $s) {
    $ligou = $true
    try { Start-ScheduledTask -TaskName $tarefa -ErrorAction Stop }
    catch {
        # sem permissão para disparar a tarefa: pede o administrador uma vez (janela do UAC)
        Start-Process -FilePath schtasks.exe -ArgumentList '/run', '/tn', "`"$tarefa`"" -Verb RunAs -WindowStyle Hidden
    }
    for ($i = 0; $i -lt 40 -and -not $s; $i++) { Start-Sleep 1; $s = Saude }
}
if (-not $s) { Aviso "O agente não ligou.`n`nVeja o registro: $dados\agente.log" 'Error'; exit 1 }
if (-not $s.pareado) { Aviso "O agente está ligado, mas o PC não está pareado com a Central.`nRode pc\instalar.ps1 com -Url e -Codigo." 'Warning'; exit 1 }
for ($i = 0; $i -lt 30 -and $s.canal -and -not $s.canal.conectado; $i++) { Start-Sleep 1; $n = Saude; if ($n) { $s = $n } }

$estado = $(if ($ligou) { 'Agente ligado' } else { 'O agente já estava ligado' })
if ($null -eq $s.canal) {
    Aviso "$estado (versão $($s.versao))."
} elseif ($s.canal.conectado) {
    Aviso "$estado e conectado à Central (versão $($s.versao)).`n`nPara o Claude usar o PC, arme na Central com a digital."
} else {
    Aviso "$estado, mas ainda sem conexão com a Central.`nConfira a internet do PC; ele tenta de novo sozinho.`n`nMotivo: $($s.canal.erro)" 'Warning'
}
