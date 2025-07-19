# app/utils/email_utils.py
import os
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from app.core.cache import set_cache, get_cache
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parents[1] / "config.env"
load_dotenv(dotenv_path=env_path)

# Generate a random 6-digit code
def generate_code() -> str:
    return str(random.randint(100000, 999999))


# Send email with subject and body
def send_email(to_email: str, subject: str, body: str) -> None:
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv('USER_MAIL')
    sender_password = os.getenv('EMAIL_PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {e}"
        )


# Store a reset/verification code temporarily in cache
def store_code(email: str, prefix: str = "reset_code", timeout: int = 60) -> str:
    code = generate_code()
    key = f"{prefix}_{email}"
    set_cache(key, code, timeout=timeout)
    return code


# Verify the stored code against user input
def verify_code(email: str, input_code: str, prefix: str = "reset_code") -> bool:
    key = f"{prefix}_{email}"
    stored_code = get_cache(key)
    return stored_code == input_code
