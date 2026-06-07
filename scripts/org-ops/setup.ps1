#!/usr/bin/env pwsh
<#
.SYNOPSIS
  First-time org-ops onboarding: venv, .env, doctor, sync guidance.

.DESCRIPTION
  Aggregates setup_venv -> .env check -> doctor -> sync instructions.
  ASANA_TOKEN must be set manually in .env (not automated).

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

Write-Host "SETUP  org-ops first-time onboarding" -ForegroundColor Cyan
Write-Host "  repo: $root"

# 1. venv
if (-not $SkipVenv) {
    Write-Host ""
    Write-Host "[1/4] setup_venv" -ForegroundColor Cyan
    & $setupVenv
}
else {
    Write-Host ""
    Write-Host "[1/4] setup_venv  (skipped)" -ForegroundColor DarkGray
}

$py = Get-OrgOpsPython -RepoRoot $root

# 2. .env
Write-Host ""
Write-Host "[2/4] .env check" -ForegroundColor Cyan
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

# 3. doctor
Write-Host ""
Write-Host "[3/4] doctor$(if ($Online) { ' --online' })" -ForegroundColor Cyan
$doctorArgs = @("tools/run_org_os.py", "doctor")
if ($Online) { $doctorArgs += "--online" }
Invoke-OrgOpsPython -Args $doctorArgs
$doctorRc = $LASTEXITCODE

# 4. sync (optional auto or guidance)
Write-Host ""
Write-Host "[4/4] sync" -ForegroundColor Cyan
if ($Sync -and $doctorRc -ne 0 -and $project -and $token -and $token -ne "your_personal_access_token") {
    Write-Host "  Running sync scripts (--write -y) ..." -ForegroundColor Cyan
    Invoke-OrgOpsPython -Args @("tools/sync_all_cf_env.py", "--project", $project, "--write", "-y")
    Write-Host "  Re-running doctor ..." -ForegroundColor Cyan
    Invoke-OrgOpsPython -Args $doctorArgs
    $doctorRc = $LASTEXITCODE
}

if ($doctorRc -eq 0) {
    Write-Host "  OK  doctor passed — env ready for org-os" -ForegroundColor Green
    Write-Host ""
    Write-Host "DONE  setup complete. Try: $py tools/run_org_os.py watch --project <GID> --once" -ForegroundColor Green
    exit 0
}

Write-SyncGuide -ProjectGid $project -Python $py
Write-Host ""
Write-Host "SETUP  finished with doctor warnings — follow NEXT commands above" -ForegroundColor Yellow
exit $doctorRc
