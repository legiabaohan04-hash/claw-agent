#!/usr/bin/env python3
import json
import os
import smtplib
import ssl
import urllib.request
from email.message import EmailMessage


DEFAULT_ENDPOINT = "https://endpoint-14358055-e169-46fc-9328-8e14537c46cd.agentbase-runtime.aiplatform.vngcloud.vn"
DEFAULT_RECIPIENTS = [
    "hanlgb@vng.com.vn",
    "mynt5@vng.com.vn",
    "tramntq@vng.com.vn",
    "tranvhd@vng.com.vn",
]


def env(name, default=""):
    return os.getenv(name, default).strip()


def call_agent(endpoint):
    payload = {
        "action": "daily_email_report",
        "message": "Tạo daily report T-1 cho Insurance Performance và Traffic.",
        "use_tableau_live": True,
    }
    request = urllib.request.Request(
        f"{endpoint.rstrip('/')}/invocations",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-GreenNode-AgentBase-User-Id": "daily-email-job",
            "X-GreenNode-AgentBase-Session-Id": "daily-email-job",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))


def send_email(subject, body, recipients):
    host = env("SMTP_HOST")
    port = int(env("SMTP_PORT", "587"))
    username = env("SMTP_USERNAME")
    password = env("SMTP_PASSWORD")
    sender = env("SMTP_FROM", username)
    if not all([host, port, username, password, sender]):
        raise SystemExit("Missing SMTP_HOST/SMTP_PORT/SMTP_USERNAME/SMTP_PASSWORD/SMTP_FROM.")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port, timeout=60) as smtp:
        smtp.starttls(context=context)
        smtp.login(username, password)
        smtp.send_message(message)


def main():
    endpoint = env("AGENT_ENDPOINT", DEFAULT_ENDPOINT)
    result = call_agent(endpoint)
    recipients = [
        item.strip()
        for item in env("DAILY_REPORT_RECIPIENTS", ",".join(DEFAULT_RECIPIENTS)).split(",")
        if item.strip()
    ]
    subject = result.get("email", {}).get("subject") or "[Bé Hadi] Daily Insurance Pulse"
    body = result.get("response") or json.dumps(result, ensure_ascii=False, indent=2)
    send_email(subject, body, recipients)
    print(f"Sent daily report to {', '.join(recipients)}")


if __name__ == "__main__":
    main()
