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

function Invoke-OrgOpsPython {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Args,
        [string]$RepoRoot = (Get-OrgOpsRoot)
    )
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
    if ($env:CURSOR_API_KEY) {
        $env:ORG_OPS_AUTO_KICK = "1"
    }
    else {
        Write-Warning "CURSOR_API_KEY unset — ORG_OPS_AUTO_KICK not enabled (snippet-only mode)."
    }
}

function Start-OrgOpsDashboard {
    param(
        [int]$Port = 8765,
        [string]$RepoRoot = (Get-OrgOpsRoot)
    )
    $py = Get-OrgOpsPython -RepoRoot $RepoRoot
    $logDir = Join-Path $RepoRoot "output\platform"
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    $log = Join-Path $logDir "dashboard.log"
    $err = Join-Path $logDir "dashboard.err.log"

    $existing = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "DASHBOARD  http://127.0.0.1:$Port/  (already listening)" -ForegroundColor Cyan
        return $true
    }

    $dashArgs = @(
        "tools/asana_ops_dashboard.py",
        "--port", "$Port"
    )
    Start-Process `
        -FilePath $py `
        -ArgumentList $dashArgs `
        -WorkingDirectory $RepoRoot `
        -RedirectStandardOutput $log `
        -RedirectStandardError $err `
        -WindowStyle Hidden | Out-Null

    Start-Sleep -Seconds 2
    $listening = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($listening) {
        Write-Host "DASHBOARD  http://127.0.0.1:$Port/  (background)" -ForegroundColor Cyan
        return $true
    }

    Write-Warning "Dashboard failed to bind port $Port. Check: $log and $err"
    if (Test-Path $err) {
        Get-Content $err -Tail 20 | ForEach-Object { Write-Warning $_ }
    }
    return $false
}
