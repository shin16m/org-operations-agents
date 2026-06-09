#!/usr/bin/env pwsh
<#
.SYNOPSIS
  First-time onboarding: venv + .env（任意 Asana 連携用）。

.DESCRIPTION
  本番標準はチャット入口（docs/design/chat-driven-ops.md）。ASANA_TOKEN は任意。
  org-os doctor / watch は廃止（2026-06-09）。

.EXAMPLE
  .\scripts\org-ops\setup.ps1
  .\scripts\org-ops\setup.ps1 -SkipVenv -Online
  .\scripts\org-ops\setup.ps1 -Sync
#>
param(
    [switch]$SkipVenv,
    [switch]$Online,
    [switch]$Sync
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_common.ps1"

function Get-DotEnvValue {
    param([string]$Key, [string]$Path)
    if (-not (Test-Path $Path)) { return $null }
    foreach ($line in Get-Content -LiteralPath $Path -Encoding UTF8) {
        $t = $line.Trim()
        if ($t -match "^\s*#") { continue }
        if ($t -match "^${Key}=(.*)$") {
            return $matches[1].Trim()
        }
    }
    return $null
}

function Write-SyncGuide {
    param([string]$ProjectGid, [string]$Python)
    Write-Host ""
    Write-Host "NEXT  sync custom-field GIDs to .env:" -ForegroundColor Cyan
    if ($ProjectGid) {
        Write-Host "  $Python tools/sync_all_cf_env.py --project $ProjectGid --write -y"
    }
    else {
        Write-Host "  Set ASANA_PROJECT_ID in skills/platform/asana-buddy/optional/.env first."
        Write-Host "  List projects: $Python skills/platform/asana-buddy/optional/handoff_to_asana.py --list-projects"
    }
    Write-Host "  Then re-run: .\scripts\org-ops\setup.ps1 -SkipVenv"
}

$root = Get-OrgOpsRoot
$optionalDir = Join-Path $root "skills\platform\asana-buddy\optional"
$envFile = Join-Path $optionalDir ".env"
$envExample = Join-Path $optionalDir ".env.example"
$setupVenv = Join-Path $optionalDir "setup_venv.ps1"

Write-Host "SETUP  org-ops venv + .env（チャット入口 · Asana 任意）" -ForegroundColor Cyan
Write-Host "  repo: $root"

# 1. venv
if (-not $SkipVenv) {
    Write-Host ""
    Write-Host "[1/3] setup_venv" -ForegroundColor Cyan
    & $setupVenv
}
else {
    Write-Host ""
    Write-Host "[1/3] setup_venv  (skipped)" -ForegroundColor DarkGray
}

$py = Get-OrgOpsPython -RepoRoot $root

# 2. .env
Write-Host ""
Write-Host "[2/3] .env check" -ForegroundColor Cyan
if (-not (Test-Path $envFile)) {
    if (-not (Test-Path $envExample)) {
        throw ".env.example not found: $envExample"
    }
    Copy-Item -LiteralPath $envExample -Destination $envFile
    Write-Host "  CREATED  $envFile  (from .env.example)" -ForegroundColor Yellow
    Write-Host "  ACTION   Set ASANA_TOKEN in .env (https://app.asana.com/0/my-apps)" -ForegroundColor Yellow
}
else {
    Write-Host "  OK  .env exists" -ForegroundColor Green
}

$token = Get-DotEnvValue -Key "ASANA_TOKEN" -Path $envFile
$project = Get-DotEnvValue -Key "ASANA_PROJECT_ID" -Path $envFile
if (-not $token -or $token -eq "your_personal_access_token") {
    Write-Host "  WARN  ASANA_TOKEN not configured (manual step — excluded from automation)" -ForegroundColor Yellow
}

# 3. optional sync guidance
Write-Host ""
Write-Host "[3/3] Asana CF sync（任意）" -ForegroundColor Cyan
if ($Sync -and $project -and $token -and $token -ne "your_personal_access_token") {
    Invoke-OrgOpsPython -Args @("tools/sync_all_cf_env.py", "--project", $project, "--write", "-y")
}

Write-Host ""
Write-Host "DONE  setup complete." -ForegroundColor Green
Write-Host "  本番: Cursor チャットで和久桶さんに依頼（docs/design/chat-driven-ops.md）" -ForegroundColor Green
if (-not $token -or $token -eq "your_personal_access_token") {
    Write-Host "  Asana 未設定 — Handoff JSON / output/ のみで運用可" -ForegroundColor DarkGray
}
else {
    Write-SyncGuide -ProjectGid $project -Python $py
}
exit 0
