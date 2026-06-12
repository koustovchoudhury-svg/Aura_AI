# AURA Host Companion Agent — Uninstaller
# Removes the scheduled task that auto-starts the agent.
#
# Usage:
#   .\uninstall.ps1

$taskName = "AuraHostAgent"

$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Removed scheduled task '$taskName'." -ForegroundColor Green
} else {
    Write-Host "Scheduled task '$taskName' not found."
}

Write-Host "Note: venv and host_agent\.env were left in place. Delete the host_agent folder to fully remove."
