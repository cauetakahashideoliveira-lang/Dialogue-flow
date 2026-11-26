# Laço do serviço do agente do PC: a tarefa agendada "Agente PC - Central" roda isto no logon (janela oculta).
# Reabre o agente se ele cair ou for atualizado (pc_atualizar sai com código 3). "python -m agente_pc desligar"
# encerra com código 0 e o laço termina.
$ErrorActionPreference = 'Continue'
$repo = Split-Path -Parent $PSScriptRoot
$dados = Join-Path $env:LOCALAPPDATA 'agente-pc'
$py = Join-Path $dados 'venv\Scripts\python.exe'
$log = Join-Path $dados 'agente.log'
$env:PYTHONPATH = "$repo\pc;$repo\controle-ir"
$env:PYTHONUTF8 = '1'
$env:AGENTE_PC_LOG = $log
while ($true) {
    if ((Test-Path $log) -and (Get-Item $log).Length -gt 5MB) { Move-Item -Force $log "$log.1" }
    & $py -m agente_pc ligar
    if ($LASTEXITCODE -eq 0) { break }
    Start-Sleep -Seconds 3
}
