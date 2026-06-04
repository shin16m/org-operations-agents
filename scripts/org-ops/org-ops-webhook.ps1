#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Start Asana webhook handler (metrics on /metrics).

.EXAMPLE
  .\scripts\org-ops\org-ops-webhook.ps1
  .\scripts\org-ops\org-ops-webhook.ps1 -Port 8766 -RequireSecret
#>
param(
    [int]$Port = 8766,
    [string]$ListenHost = "127.0.0.1",
    [switch]$RequireSecret
)

. "$PSScriptRoot\_common.ps1"

$args = @(
    "tools/asana_webhook_handler.py",
    "--host", $ListenHost,
    "--port", "$Port"
)
if ($RequireSecret) {
    $args += "--require-secret"
}

Invoke-OrgOpsPython -Args $args
