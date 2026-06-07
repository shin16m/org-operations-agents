#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Start org-ops dashboard (sessions, queue, runner log).

.EXAMPLE
  .\scripts\org-ops\org-ops-dashboard.ps1
  .\scripts\org-ops\org-ops-dashboard.ps1 -Port 8765 -Foreground
#>
param(
    [int]$Port = 8765,
    [switch]$Foreground
)

. "$PSScriptRoot\_common.ps1"

if ($Foreground) {
    Invoke-OrgOpsPython -Args @("tools/asana_ops_dashboard.py", "--port", "$Port")
}
else {
    if (-not (Start-OrgOpsDashboard -Port $Port)) {
        exit 1
    }
}
