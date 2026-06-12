import os, httpx

async def post_slack_message(channel: str, text: str, token: str = None) -> dict:
    token = token or os.getenv("SLACK_BOT_TOKEN","")
    if not token:
        return {"ok": False, "error": "No Slack token configured"}
    async with httpx.AsyncClient() as client:
        r = await client.post("https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {token}"},
            json={"channel": channel, "text": text})
        return r.json()
