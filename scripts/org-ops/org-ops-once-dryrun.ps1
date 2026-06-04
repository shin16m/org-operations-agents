#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Safe smoke test: one runner cycle without side effects.

.EXAMPLE
  .\scripts\org-ops\org-ops-once-dryrun.ps1
  .\scripts\org-ops\org-ops-once-dryrun.ps1 -Project 1214771428861230
#>
param(
    [string]$Project = $env:ASANA_PROJECT_ID
)

. "$PSScriptRoot\_common.ps1"

$args = @("tools/asana_ops_runner.py", "--once", "--dry-run", "--human")
if ($Project) {
    $args += @("--project", $Project)
}

Invoke-OrgOpsPython -Args $args
