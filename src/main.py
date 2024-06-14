import os
import ssl
import time
import ngrok
import smtplib
from pathlib import Path
from dotenv import load_dotenv
from email.message import EmailMessage


NGROK_API_KEY           = None
SENDER_EMAIL_PASSWORD   = None
SENDER_EMAIL_ADDRESS    = None
RECEIVER_EMAIL_ADDRESS  = None
SMTP_ADDRESS            = None
SMTP_PORT               = None
EXPECTED_TUNNEL_COUNT   = 1
RETRY_WAIT_TIME         = 120


def main():
    load_environment_variables()
    while True:
        tunnels = get_ngrok_tunnels()
        if len(tunnels.tunnels) >= EXPECTED_TUNNEL_COUNT:
            break
        time.sleep(RETRY_WAIT_TIME)
    mail_body = stringify_tunnel_info(tunnels)
    send_mail("Ngrok Tunnels Update", mail_body)


def send_mail(subject, content):
    email_message = EmailMessage()
    email_message["From"] = SENDER_EMAIL_ADDRESS
    email_message["To"] = RECEIVER_EMAIL_ADDRESS
    email_message["subject"] = subject
    email_message.set_content(content)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_ADDRESS, SMTP_PORT, context=context) as smtp:
        smtp.login(SENDER_EMAIL_ADDRESS, SENDER_EMAIL_PASSWORD)
        smtp.sendmail(SENDER_EMAIL_ADDRESS, RECEIVER_EMAIL_ADDRESS, email_message.as_string())


def stringify_tunnel_info(tunnels):
    result = "Here's a brief update on your ngrok tunnels:\n\n"
    for i, tunnel in enumerate(tunnels):
        result += f"Tunnel {i+1} (forwarding to {tunnel.forwards_to})\n"
        for identifier in ["started_at", "public_url"]:
            result += f"\t{identifier}: {tunnel._props[identifier]}\n"
        result += f"\tendpoint: {tunnel._props['endpoint'].uri}\n"
    return result


def get_ngrok_tunnels():
    client = ngrok.Client(NGROK_API_KEY)
    return client.tunnels.list()


def load_environment_variables():
    global NGROK_API_KEY, SENDER_EMAIL_PASSWORD, SENDER_EMAIL_ADDRESS, RECEIVER_EMAIL_ADDRESS, SMTP_ADDRESS, SMTP_PORT
    load_dotenv()
    NGROK_API_KEY           = os.getenv("NGROK_API_KEY")
    SENDER_EMAIL_PASSWORD   = os.getenv("SENDER_EMAIL_PASSWORD")
    SENDER_EMAIL_ADDRESS    = os.getenv("SENDER_EMAIL_ADDRESS")
    RECEIVER_EMAIL_ADDRESS  = os.getenv("RECEIVER_EMAIL_ADDRESS")
    SMTP_ADDRESS            = os.getenv("SMTP_ADDRESS")
    SMTP_PORT               = int(os.getenv("SMTP_PORT"))

if __name__ == "__main__":
    main()

