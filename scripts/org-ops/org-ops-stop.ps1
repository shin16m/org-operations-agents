# Stop org-ops watch runner, kick chain, bridge, and dashboard (best-effort).
param(
    [int]$DashboardPort = 8765
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "_common.ps1")

$patterns = @(
    "asana_ops_runner\.py",
    "asana_ops_poller\.py",
    "asana_ops_dashboard\.py",
    "task_dispatcher\.py",
    "cursor_sdk_kick\.py",
    "cursor_worker_dispatch\.py",
    "cursor_epic_dispatch\.py",
    "pm_worker_complete_bridge\.py",
    "auto_intake_runner\.py",
    "approval_helper\.py",
    "cursor-sdk-bridge"
)

$stopped = 0
$seen = @{}

Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object {
        if (-not $_.CommandLine) { return $false }
        $cmd = $_.CommandLine
        foreach ($pat in $patterns) {
            if ($cmd -match $pat) { return $true }
        }
        return $false
    } |
    ForEach-Object {
        if ($seen.ContainsKey($_.ProcessId)) { return }
        $seen[$_.ProcessId] = $true
        Write-Host "STOP  pid=$($_.ProcessId)  $($_.Name)" -ForegroundColor Yellow
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        $stopped++
    }

$dashConn = Get-NetTCPConnection -LocalPort $DashboardPort -State Listen -ErrorAction SilentlyContinue
foreach ($conn in $dashConn) {
    if ($conn.OwningProcess -and -not $seen.ContainsKey($conn.OwningProcess)) {
        $seen[$conn.OwningProcess] = $true
        Write-Host "STOP  dashboard pid=$($conn.OwningProcess)  port=$DashboardPort" -ForegroundColor Yellow
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        $stopped++
    }
}

if ($stopped -eq 0) {
    Write-Host "OK  no org-ops runner/kick/dashboard process found" -ForegroundColor Green
}
else {
    Write-Host "DONE  stopped $stopped process(es)" -ForegroundColor Green
}
