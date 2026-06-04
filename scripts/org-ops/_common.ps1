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
