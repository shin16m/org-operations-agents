#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Dispatch next incomplete execution child (task_dispatcher wrapper).

.EXAMPLE
  .\scripts\org-ops\org-ops-dispatch.ps1 -Parent 1215412762687733 -List
  .\scripts\org-ops\org-ops-dispatch.ps1 -Parent 1215412762687733 -DryRun
  .\scripts\org-ops\org-ops-dispatch.ps1 -Parent 1215412762687733 -Kick -Yes
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Parent,
    [string]$Task,
    [string]$Department,
    [switch]$List,
    [switch]$DryRun,
    [switch]$Kick,
    [switch]$Yes
)

. "$PSScriptRoot\_common.ps1"

if ($Kick -and $Yes) {
    Enable-OrgOpsAutoKick
}

$args = @("tools/task_dispatcher.py", "--parent", $Parent)
if ($Task) { $args += @("--task", $Task) }
if ($Department) { $args += @("--department", $Department) }
if ($List) { $args += "--list" }
if ($DryRun) { $args += "--dry-run" }
if ($Kick) { $args += "--kick" }
if ($Yes) { $args += "-y" }

Invoke-OrgOpsPython -Args $args
