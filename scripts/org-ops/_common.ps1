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

function Start-OrgOpsWatchBackground {
    <#
      Run asana_ops_runner --watch without a visible console.
      stdout + stderr are merged into output/platform/runner-watch.log
      (pythonw splits streams and buffers stdout — avoided here).
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$RunnerArgs,
        [string]$RepoRoot = (Get-OrgOpsRoot)
    )
    Import-OrgOpsDotEnv -RepoRoot $RepoRoot | Out-Null
    $py = Get-OrgOpsPython -RepoRoot $RepoRoot
    $logDir = Join-Path $RepoRoot "output\platform"
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    $log = Join-Path $logDir "runner-watch.log"
    $argTokens = @("-u") + $RunnerArgs | ForEach-Object {
        if ($_ -match '\s') { "`"$_`"" } else { $_ }
    }
    $runnerLine = "`"$py`" " + ($argTokens -join " ")
    $cmd = "/c $runnerLine >> `"$log`" 2>&1"

    Start-Process `
        -FilePath "cmd.exe" `
        -ArgumentList $cmd `
        -WorkingDirectory $RepoRoot `
        -WindowStyle Hidden | Out-Null

    Write-Host "WATCH  background  (hidden)  log=$log" -ForegroundColor Cyan
    Write-Host "WATCH  note  IDE terminal (pwsh) exits immediately; watch runs in background." -ForegroundColor DarkGray
}
