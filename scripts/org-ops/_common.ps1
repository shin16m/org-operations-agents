# Shared helpers for org-ops batch scripts (repo root + venv python).
$ErrorActionPreference = "Stop"

function Get-OrgOpsRoot {
    if ($env:ORG_OPS_REPO_ROOT) {
        return (Resolve-Path $env:ORG_OPS_REPO_ROOT).Path
    }
    return (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

function Get-OrgOpsPython {
    param([string]$RepoRoot = (Get-OrgOpsRoot))
    $py = Join-Path $RepoRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $py)) {
        throw "venv not found: $py — run skills/platform/asana-buddy/optional/setup_venv.ps1 first"
    }
    return $py
}

function Get-OrgOpsPythonW {
    param([string]$RepoRoot = (Get-OrgOpsRoot))
    $pyw = Join-Path $RepoRoot ".venv\Scripts\pythonw.exe"
    if (Test-Path $pyw) {
        return $pyw
    }
    return Get-OrgOpsPython -RepoRoot $RepoRoot
}

function Get-OrgOpsEnvFile {
    param([string]$RepoRoot = (Get-OrgOpsRoot))
    if ($env:ORG_OS_ENV_FILE) {
        return (Resolve-Path $env:ORG_OS_ENV_FILE).Path
    }
    return (Join-Path $RepoRoot "skills\platform\asana-buddy\optional\.env")
}

function Import-OrgOpsDotEnv {
    <#
      Load org-ops .env into the current PowerShell session (does not override existing env vars).
      Matches Python load_env_from_dotfile / org_os.env default path.
    #>
    param([string]$RepoRoot = (Get-OrgOpsRoot))
    $envFile = Get-OrgOpsEnvFile -RepoRoot $RepoRoot
    if (-not (Test-Path $envFile)) {
        return $false
    }
    foreach ($line in Get-Content -Path $envFile -Encoding UTF8) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#") -or -not $trimmed.Contains("=")) {
            continue
        }
        $key, $val = $trimmed -split "=", 2
        $key = $key.Trim()
        if (-not $key) { continue }
        if (-not (Get-Item -Path "Env:$key" -ErrorAction SilentlyContinue)) {
            Set-Item -Path "Env:$key" -Value $val.Trim()
        }
    }
    return $true
}

function Invoke-OrgOpsPython {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Args,
        [string]$RepoRoot = (Get-OrgOpsRoot)
    )
    Import-OrgOpsDotEnv -RepoRoot $RepoRoot | Out-Null
    $py = Get-OrgOpsPython -RepoRoot $RepoRoot
    $env:PYTHONIOENCODING = "utf-8"
    Push-Location $RepoRoot
    try {
        & $py @Args
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    finally {
        Pop-Location
    }
}

function Enable-OrgOpsAutoKick {
    Import-OrgOpsDotEnv | Out-Null
    if ($env:CURSOR_API_KEY) {
        $env:ORG_OPS_AUTO_KICK = "1"
        Write-Host "AUTOKICK  ORG_OPS_AUTO_KICK=1  (CURSOR_API_KEY from env/.env)" -ForegroundColor Cyan
    }
    elseif ($env:ORG_OPS_AUTO_KICK -eq "1") {
        Write-Host "AUTOKICK  ORG_OPS_AUTO_KICK=1  (from .env; CURSOR_API_KEY loaded by Python at kick)" -ForegroundColor Cyan
    }
    else {
        Write-Warning "CURSOR_API_KEY unset and ORG_OPS_AUTO_KICK not set — snippet-only mode."
    }
}
