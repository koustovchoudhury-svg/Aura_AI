# AURA Host Companion Agent — Windows Installer
# Sets up a Python venv, installs dependencies, generates a secure token,
# and registers the agent to start automatically at user logon via Task Scheduler.
#
# Usage (run from a normal PowerShell prompt, in this folder):
#   .\install.ps1

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "== AURA Host Companion Agent installer ==" -ForegroundColor Cyan

# 1. Create virtual environment
if (-not (Test-Path "$root\venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv "$root\venv"
}

# 2. Install dependencies
Write-Host "Installing dependencies..."
& "$root\venv\Scripts\pip.exe" install --quiet --upgrade pip
& "$root\venv\Scripts\pip.exe" install --quiet -r "$root\requirements.txt"

# 3. Generate a secure token if not already configured
$envFile = "$root\.env"
if (-not (Test-Path $envFile)) {
    $token = [System.Convert]::ToHexString((New-Object byte[] 24 | ForEach-Object { (New-Object Random).NextBytes($_); $_ }))
    $token = -join ((48..57)+(97..102) | Get-Random -Count 48 | ForEach-Object {[char]$_})
    "HOST_AGENT_TOKEN=$token" | Out-File -Encoding utf8 $envFile
    Write-Host "Generated new token in host_agent\.env" -ForegroundColor Yellow
    Write-Host "Copy this line into your AURA project's .env file:" -ForegroundColor Yellow
    Write-Host "  HOST_AGENT_TOKEN=$token" -ForegroundColor Green
} else {
    Write-Host "Existing host_agent\.env found — keeping current token."
}

# 4. Register a scheduled task to run at user logon
$taskName = "AuraHostAgent"
$pythonExe = "$root\venv\Scripts\pythonw.exe"
$scriptPath = "$root\main.py"

$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing existing scheduled task..."
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

$action  = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$scriptPath`"" -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "AURA AI-OS Host Companion Agent" | Out-Null

Write-Host "Registered scheduled task '$taskName' to start at logon." -ForegroundColor Green

# 5. Start it now
Write-Host "Starting agent now..."
Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 2

try {
    $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5678/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "Agent is running: $($resp.Content)" -ForegroundColor Green
} catch {
    Write-Host "Could not reach agent yet. Check Task Scheduler > $taskName, or run 'python main.py' manually to debug." -ForegroundColor Red
}

Write-Host ""
Write-Host "== Done =="
Write-Host "Make sure HOST_AGENT_TOKEN in this folder's .env matches HOST_AGENT_TOKEN in the AURA project's .env"
Write-Host "Manage: Get-ScheduledTask -TaskName $taskName | Stop-ScheduledTask / Start-ScheduledTask / Unregister-ScheduledTask"
