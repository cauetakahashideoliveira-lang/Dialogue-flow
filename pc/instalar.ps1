#Requires -Version 5.1
<#
  Instala (ou atualiza) o agente do PC da Central de Controle neste Windows.

  No PowerShell COMO ADMINISTRADOR:
    powershell -ExecutionPolicy Bypass -File C:\dev\dialogue-flow\pc\instalar.ps1 -Url https://SUA-CENTRAL.workers.dev -Codigo ABCD1234

  -Url     endereço da sua Central de Controle (o mesmo que você abre para armar)
  -Codigo  código de pareamento: na Central, "Cadastrar celular" (vale 10 min, uso único)
  -Nome    nome do PC na Central (padrão: nome do computador)

  Sem -Url/-Codigo, só instala ou atualiza; para parear depois, rode de novo com eles.
  O que faz: Python 3.12 (winget, se faltar), ambiente próprio em %LOCALAPPDATA%\agente-pc com a biblioteca
  cryptography, pareamento e uma tarefa agendada que liga o agente no logon, oculto e como administrador.
#>
param([string]$Url, [string]$Codigo, [string]$Nome = $env:COMPUTERNAME)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$dados = Join-Path $env:LOCALAPPDATA 'agente-pc'
$venv = Join-Path $dados 'venv'
$py = Join-Path $venv 'Scripts\python.exe'
$tarefa = 'Agente PC - Central'
function Passo($t) { Write-Host "`n== $t" -ForegroundColor Cyan }

$eu = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $eu.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Abra o PowerShell como administrador e rode de novo.'
}
if (-not (Test-Path "$repo\pc\agente_pc\__init__.py")) { throw "Repositório não encontrado em $repo" }

Passo '1/5 Python 3.10+'
function AcharPython {
    foreach ($c in @(@('py', '-3.12'), @('py', '-3'), @('python', ''))) {
        $exe = Get-Command $c[0] -ErrorAction SilentlyContinue
        if (-not $exe) { continue }
        $a = @(); if ($c[1]) { $a += $c[1] }
        try {
            $ok = & $exe.Source @a -c 'import sys; print(sys.version_info >= (3, 10))' 2>$null
            if ($ok -eq 'True') { return , @($exe.Source, $a) }
        } catch {}
    }
    return $null
}
$base = AcharPython
if (-not $base) {
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
    $base = AcharPython
    if (-not $base) { throw 'Python não encontrado depois do winget: feche e abra o PowerShell e rode de novo.' }
}
$pyBase, $pyArgs = $base[0], $base[1]
Write-Host "   $pyBase $pyArgs"

Passo '2/5 Ambiente do agente e a biblioteca cryptography'
New-Item -ItemType Directory -Force $dados | Out-Null
if (-not (Test-Path $py)) { & $pyBase @pyArgs -m venv $venv }
& $py -m pip install --upgrade --quiet --disable-pip-version-check pip cryptography
if ($LASTEXITCODE) { throw 'pip falhou' }
$env:PYTHONPATH = "$repo\pc;$repo\controle-ir"
$env:PYTHONUTF8 = '1'

Passo '3/5 Parar a versão em execução (se houver)'
Stop-ScheduledTask -TaskName $tarefa -ErrorAction SilentlyContinue
Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
    Where-Object { $_.CommandLine -like '*agente_pc ligar*' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

if ($Url -and $Codigo) {
    Passo '4/5 Pareamento com a Central'
    & $py -m agente_pc parear $Url $Codigo --nome $Nome
    if ($LASTEXITCODE) { throw 'Pareamento falhou: gere um código novo na Central e rode de novo.' }
} else {
    Passo '4/5 Pareamento: pulado (sem -Url e -Codigo)'
}

Passo '5/5 Tarefa agendada (liga no logon, oculta, como administrador) e botão Ligar Agente PC'
$usuario = "$env:USERDOMAIN\$env:USERNAME"
$acao = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$repo\pc\iniciar.ps1`""
$gatilho = New-ScheduledTaskTrigger -AtLogOn -User $usuario
$quem = New-ScheduledTaskPrincipal -UserId $usuario -LogonType Interactive -RunLevel Highest
$ajustes = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable `
    -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName $tarefa -Action $acao -Trigger $gatilho -Principal $quem -Settings $ajustes -Force | Out-Null
Start-ScheduledTask -TaskName $tarefa
# Botão na área de trabalho: liga o agente se ele cair e mostra se conectou (sem pedir administrador)
$atalho = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Ligar Agente PC.lnk'
$lnk = (New-Object -ComObject WScript.Shell).CreateShortcut($atalho)
$lnk.TargetPath = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
$lnk.Arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$repo\pc\ligar.ps1`""
$lnk.WorkingDirectory = $repo
$lnk.IconLocation = "$env:SystemRoot\System32\shell32.dll,27"
$lnk.Description = 'Liga o agente do PC da Central de Controle e mostra se conectou'
$lnk.Save()
Write-Host "   botão na área de trabalho: $atalho"

$cfg = Join-Path $dados 'config.json'
$fim = (Get-Date).AddSeconds(30)
$saude = $null
while ((Get-Date) -lt $fim -and -not $saude) {
    Start-Sleep -Seconds 2
    if (Test-Path $cfg) {
        $porta = (Get-Content $cfg -Raw | ConvertFrom-Json).porta
        try { $saude = Invoke-RestMethod "http://127.0.0.1:$porta/saude" -TimeoutSec 3 } catch {}
    }
}
if (-not $saude) { throw "O agente não respondeu. Veja o registro: $dados\agente.log" }
& $py -m agente_pc estado
Write-Host "`nPronto. O agente liga sozinho a cada logon (e pelo botão 'Ligar Agente PC')." -ForegroundColor Green
if ($saude.pareado) {
    Write-Host 'Na Central: arme com a digital para liberar as ferramentas pc_*. No Claude, abra uma conversa nova.'
} else {
    Write-Host 'Falta parear: rode de novo com -Url e -Codigo.'
}
