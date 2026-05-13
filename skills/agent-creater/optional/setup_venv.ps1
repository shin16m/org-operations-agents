# PowerShell helper: create a venv at the repository root and install requirements
# Determine repository root from this script's location (three levels up)
$workspaceRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
$venvPath = Join-Path $workspaceRoot ".venv"

if (-Not (Test-Path $venvPath)) {
    python -m venv $venvPath
}

# Install requirements using the venv's python. requirements.txt lives next to this script.
$reqFile = Join-Path $PSScriptRoot "requirements.txt"
if (Test-Path $reqFile) {
    & "$venvPath\Scripts\python.exe" -m pip install --upgrade pip
    & "$venvPath\Scripts\python.exe" -m pip install -r $reqFile
} else {
    Write-Host "requirements.txt が見つかりません: $reqFile" -ForegroundColor Yellow
}

Write-Host "仮想環境を作成しました: $venvPath"
Write-Host "PowerShellで有効化するには: $venvPath\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "cmd.exe では: $venvPath\Scripts\activate.bat" -ForegroundColor Cyan
Write-Host "optional フォルダのスクリプトを実行するには: Set-Location (Join-Path $workspaceRoot 'skills\agent-creater\optional')" -ForegroundColor Green
Write-Host "実行例: .\.venv\Scripts\python.exe .\skills\agent-creater\optional\agent_handler_asana.py --project <PROJ> --name \"伝票電子化\" --notes \"テスト\"" -ForegroundColor Green
