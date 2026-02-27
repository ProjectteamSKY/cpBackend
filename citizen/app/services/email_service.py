import aiosmtplib
from email.message import EmailMessage
from app.core.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS


async def send_otp_email(email: str, otp: str):
    message = EmailMessage()
    message["From"] = SMTP_USER
    message["To"] = email
    message["Subject"] = "Your OTP Verification Code"

    message.set_content(f"""
    Hello,

    Your OTP code is: {otp}

    This code will expire in 10 minutes.

    Thank you.
    """)

    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASS,
        start_tls=True,
    )