import os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

async def send_email(to: str, subject: str, body: str) -> dict:
    host, port = os.getenv("SMTP_HOST",""), int(os.getenv("SMTP_PORT","587"))
    user, pw   = os.getenv("SMTP_USER",""), os.getenv("SMTP_PASS","")
    if not all([host, user, pw]):
        return {"error": "SMTP not configured"}
    msg = MIMEMultipart(); msg["Subject"]=subject; msg["From"]=user; msg["To"]=to
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP(host, port) as s:
            s.starttls(); s.login(user, pw); s.sendmail(user, to, msg.as_string())
        return {"status": "sent"}
    except Exception as e:
        return {"error": str(e)}
