import os
import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = os.getenv("SMTP_SERVER", "sandbox.smtp.mailtrap.io")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_otp(to_email: str, otp: str):
    subject = "Your OTP code"
    body = f"Your OTP code is : {otp}. It is valid for 10 minutes"
    message = MIMEText(body)
    message["Subject"] = subject
    message["from"] = SMTP_EMAIL
    message["to"] = to_email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, message.as_string())
        

    