import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from cryptography.fernet import Fernet

# Fernet contact data encryption setup
# Use a static fallback key if ENCRYPTION_KEY environment variable is not defined
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Safe static key for local testing
    ENCRYPTION_KEY = "k1c1Q1pZLXp1b0V4Y21zYWZla2V5MTIzNDU2Nzg5MDE="
    
try:
    cipher_suite = Fernet(ENCRYPTION_KEY.encode())
except Exception:
    # If the key provided is invalid, generate a temporary valid one for this runtime session
    cipher_suite = Fernet(Fernet.generate_key())

def encrypt_contact(data: str) -> str:
    """Symmetrically encrypt contact info before logging."""
    if not data:
        return ""
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_contact(token: str) -> str:
    """Decrypt logged contact info for inspection."""
    if not token:
        return ""
    try:
        return cipher_suite.decrypt(token.encode()).decode()
    except Exception:
        return "[Decryption Failed]"

# Twilio SMS API credentials
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "")

# SMTP Email credentials
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")

def send_sms(to_number: str, message: str) -> bool:
    """Dispatches SMS via Twilio API client."""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
        print("⚠️ Twilio SMS credentials not configured. Skipping SMS transmission.")
        return False
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )
        print(f"💬 Twilio SMS sent successfully to {to_number[:4]}****")
        return True
    except Exception as e:
        print(f"⚠️ Twilio SMS transmission failed: {e}")
        return False

def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Dispatches transaction alerts via SMTP standard library."""
    if not SMTP_USER or not SMTP_PASSWORD:
        print("⚠️ SMTP credentials not configured. Skipping email transmission.")
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
        server.quit()
        print(f"📧 SMTP email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"⚠️ SMTP email transmission failed: {e}")
        return False
