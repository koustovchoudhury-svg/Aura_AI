# AURA Host Companion Agent

Gives AURA (running in Docker) controlled, approval-gated access to your Windows machine:
opening installed apps, opening URLs in your default browser, and reading/writing/listing
files anywhere on disk.

## Install

Open PowerShell **in this folder** and run:

```powershell
.\install.ps1
```

This will:
1. Create a Python virtual environment and install dependencies
2. Generate a random auth token (`host_agent\.env`)
3. Register a Task Scheduler task (`AuraHostAgent`) that starts the agent at logon
4. Start the agent immediately and verify it responds on `http://127.0.0.1:5678/health`

## Connect it to AURA

Copy the `HOST_AGENT_TOKEN=...` value printed by the installer into the **AURA project's**
`.env` file (`d:\Project\Aura AI\aura-ai-os\aura-ai\.env`), so both sides share the same secret.
Then recreate the API container:

```powershell
docker compose up -d api
```

## Use it

In the AURA chat (text or voice), try:
- "Open Notepad"
- "Open youtube.com in my browser"
- "What's in my Downloads folder?"
- "Read the file C:\Users\<you>\Desktop\notes.txt"

Each of these will prompt for **approval** in the chat UI before running on your PC.

## Manage

```powershell
Get-ScheduledTask -TaskName AuraHostAgent
Stop-ScheduledTask -TaskName AuraHostAgent
Start-ScheduledTask -TaskName AuraHostAgent
```

## Uninstall

```powershell
.\uninstall.ps1
```

## Security notes

- The agent only accepts requests carrying the `HOST_AGENT_TOKEN` bearer token.
- It listens on all interfaces (`0.0.0.0:5678`) so Docker (`host.docker.internal`) can reach it —
  if you're on an untrusted network, consider a Windows Firewall rule restricting port 5678
  to the Docker bridge / localhost only.
- AURA's approval gate still requires you to click "Approve" for every `host_action` before
  this agent executes anything.
