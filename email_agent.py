# email_agent.py
import os
from typing import Dict
from agents import Agent, function_tool

@function_tool
def send_email(subject: str, html_body: str) -> Dict[str, str]:
    """Send an email with the given subject and HTML body via SendGrid."""
    try:
        import sendgrid
        from sendgrid.helpers.mail import Email, Mail, Content, To
    except ImportError as e:
        return {"status": "disabled", "reason": "sendgrid not installed"}

    api_key = os.getenv("SENDGRID_API_KEY")
    from_addr = os.getenv("SENDER_EMAIL")
    to_addr = os.getenv("RECIPIENT_EMAIL")
    if not api_key or not from_addr or not to_addr:
        return {"status": "disabled", "reason": "SENDGRID_API_KEY/SENDER_EMAIL/RECIPIENT_EMAIL not set"}

    sg = sendgrid.SendGridAPIClient(api_key=api_key)
    mail = Mail(Email(from_addr), To(to_addr), subject, Content("text/html", html_body)).get()
    resp = sg.client.mail.send.post(request_body=mail)
    return {"status": "success", "code": resp.status_code}

INSTRUCTIONS = (
    "You can send a nicely formatted HTML email based on a detailed report. "
    "Use the send_email tool exactly once with a concise subject and the report as clean HTML."
)

email_agent = Agent(
    name="Email agent",
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini",
)
