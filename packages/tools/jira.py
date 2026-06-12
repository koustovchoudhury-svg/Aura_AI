import os, httpx, base64

async def create_jira_issue(project: str, summary: str, description: str = "") -> dict:
    url, user, token = os.getenv("JIRA_URL",""), os.getenv("JIRA_USER",""), os.getenv("JIRA_TOKEN","")
    if not all([url, user, token]):
        return {"error": "Jira not configured — set JIRA_URL, JIRA_USER, JIRA_TOKEN"}
    creds = base64.b64encode(f"{user}:{token}".encode()).decode()
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{url}/rest/api/3/issue",
            headers={"Authorization":f"Basic {creds}","Content-Type":"application/json"},
            json={"fields":{"project":{"key":project},"summary":summary,
                            "description":{"type":"doc","version":1,"content":[
                                {"type":"paragraph","content":[{"type":"text","text":description}]}]},
                            "issuetype":{"name":"Task"}}})
        return r.json()
