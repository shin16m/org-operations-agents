#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Production watch loop: bootstrap + approval helper + resume + archive.

.EXAMPLE
  .\scripts\org-ops\org-ops-watch.ps1
  .\scripts\org-ops\org-ops-watch.ps1 -Yes -AutoKick -Interval 60
  .\scripts\org-ops\org-ops-watch.ps1 -Project 1214771428861230 -Yes
#>
param(
    [string]$Project = $env:ASANA_PROJECT_ID,
    [int]$Interval = 60,
    [switch]$Yes,
    [switch]$AutoKick,
    [switch]$Human
)

. "$PSScriptRoot\_common.ps1"

if ($AutoKick) {
    Enable-OrgOpsAutoKick
}

$args = @(
    "tools/asana_ops_runner.py",
    "--watch",
    "--interval", "$Interval"
)
if ($Project) {
    $args += @("--project", $Project)
}
if ($Yes) {
    $args += "-y"
}
if ($Human -or -not $Yes) {
    $args += "--human"
}

Invoke-OrgOpsPython -Args $args
