import smtplib
import os
import streamlit as st
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def get_secret(key):
    try:
        return st.secrets[key]   # deployed
    except:
        return os.getenv(key)    # local


EMAIL_USER = get_secret("EMAIL_USER")
EMAIL_PASS = get_secret("EMAIL_PASS")

# ✅ Safety check (IMPORTANT)
if not EMAIL_USER or not EMAIL_PASS:
    raise ValueError("❌ Email credentials missing. Check .env or Streamlit secrets.")


def send_otp_email(to_email, otp):
    msg = MIMEText(f"Your OTP is: {otp}")
    msg["Subject"] = "Your Login OTP"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)