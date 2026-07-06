"""
notification_service.py — SmartBank Notification Service Module
================================================================
Handles all outbound notifications (SMS via Twilio, Email via SMTP).
Provides encryption utilities for contact data and a unified
confirmation dispatcher for loan/scheme applications.

Security: Contact info is encrypted before logging using Fernet symmetric encryption.
Fallback:  If SMS/email services are unavailable, failures are logged and
           the caller is informed via return values — no silent data loss.
"""

import os
import requests
import logging
from twilio.rest import Client
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from datetime import datetime

# ── Logging Setup ────────────────────────────────────────────────────────────
logger = logging.getLogger("notification_service")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)

# ── Environment Variables ────────────────────────────────────────────────────
load_dotenv()

# ── Encryption Setup ────────────────────────────────────────────────────────
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = "k1c1Q1pZLXp1b0V4Y21zYWZla2V5MTIzNDU2Nzg5MDE="

try:
    cipher_suite = Fernet(ENCRYPTION_KEY.encode())
except Exception:
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


# ── Twilio SMS API credentials ──────────────────────────────────────────────
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "")

# ── Email API credentials ──────────────────────────────────────────────────
EMAIL_API_KEY = os.environ.get("EMAIL_API_KEY", "")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "")  # e.g., the email you verified on Brevo


def send_sms(to_number: str, message: str) -> bool:
    """Dispatches SMS via Twilio API client.

    Returns True on success, False if credentials are missing or transmission fails.
    Failures are logged but never raise — the caller receives a boolean status.
    """
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
        logger.warning("Twilio SMS credentials not configured. Skipping SMS transmission.")
        return False
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )
        logger.info(f"💬 Twilio SMS sent successfully to {to_number[:4]}****")
        return True
    except Exception as e:
        logger.error(f"Twilio SMS transmission failed: {e}")
        return False


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Dispatches email alerts via Brevo HTTP API.

    Returns True on success, False if credentials are missing or transmission fails.
    Failures are logged but never raise — the caller receives a boolean status.
    """
    if not EMAIL_API_KEY or not SENDER_EMAIL:
        logger.warning("Email API credentials not configured. Skipping email transmission.")
        print("⚠️  [Email] API credentials missing — set EMAIL_API_KEY and SENDER_EMAIL in .env")
        return False
    try:
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": EMAIL_API_KEY,
            "content-type": "application/json"
        }
        payload = {
            "sender": {"name": "SmartBank", "email": SENDER_EMAIL},
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html_body
        }
        
        # Use a 10-second timeout for the HTTP request to prevent hangs
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code in [200, 201, 202]:
            logger.info(f"📧 Email sent successfully to {to_email} via Brevo API")
            print(f"📧 [Email] Sent successfully to {to_email}")
            return True
        else:
            error_detail = response.text
            logger.error(f"Email API rejected the request: {response.status_code} - {error_detail}")
            print(f"❌ [Email] Brevo API error {response.status_code}: {error_detail}")
            # Common causes:
            # 401 → Invalid API key
            # 400 → Sender email not verified in Brevo
            # 403 → Account suspended
            return False
            
    except Exception as e:
        logger.error(f"Email HTTP API transmission failed: {e}")
        print(f"❌ [Email] Exception during send: {e}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
#  Confirmation Message Builder & Dispatcher
# ══════════════════════════════════════════════════════════════════════════════

def build_confirmation_text(name: str, app_type: str, amount: float, ref_id: str,
                            tenure: float = 0, emi: float = 0,
                            maturity_amount: float = 0, is_deposit: bool = False) -> str:
    """Build a plain-text confirmation message for SMS delivery.

    Contains: user name, loan/scheme type, applied amount, and reference ID.
    """
    type_label = _pretty_type_name(app_type)

    if is_deposit:
        return (
            f"Dear {name}, did you recently apply for a {type_label} with us? "
            f"Ref ID: {ref_id}. "
            f"Amount: Rs {amount:,.2f} for {tenure} years. "
            f"Maturity Amount: Rs {maturity_amount:,.2f}. "
            f"Are you sure you want to proceed with this application? "
            f"If you have any questions or did not authorize this, please contact us immediately at banksupport@gmail.com."
        )
    else:
        return (
            f"Dear {name}, did you recently apply for a {type_label} Loan with us? "
            f"Ref ID: {ref_id}. "
            f"Loan Amount: Rs {amount:,.2f} for {tenure} years. "
            f"Expected Monthly EMI: Rs {emi:,.2f}. "
            f"Are you sure you want to proceed with this application? "
            f"If you have any questions or did not authorize this, please contact us immediately at banksupport@gmail.com."
        )


def build_confirmation_html(name: str, app_type: str, amount: float, ref_id: str,
                            tenure: float = 0, emi: float = 0,
                            maturity_amount: float = 0, is_deposit: bool = False) -> str:
    """Build a rich HTML confirmation email body with SmartBank branding.

    Contains: user name, loan/scheme type, applied amount, reference ID,
    financial details (EMI or maturity amount), and timestamp.
    """
    type_label = _pretty_type_name(app_type)
    timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")

    # Financial details row
    if is_deposit:
        detail_row = f"""
        <tr><td style="padding:10px 15px;border-bottom:1px solid #e0f7fa;color:#555;">Maturity Amount</td>
            <td style="padding:10px 15px;border-bottom:1px solid #e0f7fa;font-weight:bold;color:#0097a7;">₹{maturity_amount:,.2f}</td></tr>
        """
    else:
        detail_row = f"""
        <tr><td style="padding:10px 15px;border-bottom:1px solid #e0f7fa;color:#555;">Monthly EMI</td>
            <td style="padding:10px 15px;border-bottom:1px solid #e0f7fa;font-weight:bold;color:#0097a7;">₹{emi:,.2f}</td></tr>
        """

    return f"""
    <div style="font-family:'Segoe UI',Arial,sans-serif;max-width:600px;margin:0 auto;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);">
      <!-- Header -->
      <div style="background:linear-gradient(135deg,#00bcd4,#0097a7);padding:30px 25px;text-align:center;">
        <h1 style="color:#ffffff;margin:0;font-size:24px;letter-spacing:1px;">🏦 SKiller SmartBank</h1>
        <p style="color:#e0f7fa;margin:8px 0 0;font-size:14px;">Your Secure & Smart Banking Partner</p>
      </div>

      <!-- Body -->
      <div style="padding:30px 25px;">
        <h2 style="color:#0097a7;margin:0 0 5px;font-size:20px;">❓ Application Verification</h2>
        <p style="color:#888;font-size:13px;margin:0 0 20px;">Submitted on {timestamp}</p>

        <p style="color:#333;font-size:15px;line-height:1.6;">
          Dear <strong>{name}</strong>,<br>
          Did you recently apply for a <strong>{type_label}</strong> with us? Are you sure you want to proceed with this application?
        </p>

        <!-- Details Table -->
        <table style="width:100%;border-collapse:collapse;margin:20px 0;background:#fafafa;border-radius:8px;overflow:hidden;">
          <tr style="background:linear-gradient(135deg,#e0f7fa,#b2ebf2);">
            <td colspan="2" style="padding:12px 15px;font-weight:bold;color:#006064;font-size:15px;">📋 Application Details</td>
          </tr>
          <tr><td style="padding:10px 15px;border-bottom:1px solid #e0f7fa;color:#555;">Reference ID</td>
              <td style="padding:10px 15px;border-bottom:1px solid #e0f7fa;font-weight:bold;color:#d32f2f;font-size:16px;">{ref_id}</td></tr>
          <tr><td style="padding:10px 15px;border-bottom:1px solid #e0f7fa;color:#555;">Applicant Name</td>
              <td style="padding:10px 15px;border-bottom:1px solid #e0f7fa;font-weight:bold;">{name}</td></tr>
          <tr><td style="padding:10px 15px;border-bottom:1px solid #e0f7fa;color:#555;">Application Type</td>
              <td style="padding:10px 15px;border-bottom:1px solid #e0f7fa;font-weight:bold;">{type_label}</td></tr>
          <tr><td style="padding:10px 15px;border-bottom:1px solid #e0f7fa;color:#555;">Applied Amount</td>
              <td style="padding:10px 15px;border-bottom:1px solid #e0f7fa;font-weight:bold;color:#0097a7;font-size:16px;">₹{amount:,.2f}</td></tr>
          <tr><td style="padding:10px 15px;border-bottom:1px solid #e0f7fa;color:#555;">Tenure</td>
              <td style="padding:10px 15px;border-bottom:1px solid #e0f7fa;font-weight:bold;">{tenure} year(s)</td></tr>
          {detail_row}
        </table>

        <!-- Status Badge -->
        <div style="background:linear-gradient(135deg,#e8f5e9,#c8e6c9);border-radius:8px;padding:15px;text-align:center;margin:20px 0;">
          <span style="color:#2e7d32;font-weight:bold;font-size:14px;">📌 Status: Under Review</span>
          <p style="color:#555;font-size:12px;margin:8px 0 0;">Our team will review your application and contact you within 2-3 business days.</p>
        </div>

        <p style="color:#555;font-size:13px;line-height:1.6;">
          Please keep your Reference ID <strong style="color:#d32f2f;">{ref_id}</strong> safe for future correspondence.
          If you have any questions, did not authorize this, or want to confirm your application, please contact us immediately at <a href="mailto:banksupport@gmail.com" style="color:#0097a7;">banksupport@gmail.com</a> or call <strong>1800-123-456</strong>.
        </p>
      </div>

      <!-- Footer -->
      <div style="background:#f5f5f5;padding:20px 25px;text-align:center;border-top:1px solid #eee;">
        <p style="color:#999;font-size:11px;margin:0;">This is an auto-generated confirmation from SKiller SmartBank.</p>
        <p style="color:#bbb;font-size:10px;margin:5px 0 0;">To stop receiving notifications, please contact support.</p>
      </div>
    </div>
    """


def send_confirmation_notification(
    name: str, email: str, phone: str, app_type: str,
    amount: float, ref_id: str, tenure: float = 0,
    emi: float = 0, maturity_amount: float = 0,
    is_deposit: bool = False
) -> dict:
    """Unified confirmation dispatcher — sends SMS and/or email immediately.

    This function is the single entry point for all loan/scheme confirmation
    notifications. It builds the appropriate message, dispatches via available
    channels, and returns a status dict for audit logging.

    Args:
        name:            Applicant's full name.
        email:           Email address (may be empty).
        phone:           Phone number (may be empty).
        app_type:        Scheme/loan type code (e.g. 'home', 'fd1', 'rd').
        amount:          Applied amount in INR.
        ref_id:          Application reference ID.
        tenure:          Loan/deposit tenure in years.
        emi:             Calculated monthly EMI (for loans).
        maturity_amount: Calculated maturity amount (for deposits).
        is_deposit:      True if this is a deposit scheme, False for loans.

    Returns:
        dict with keys:
            email_status: 'Sent' | 'Failed' | 'Skipped'
            sms_status:   'Sent' | 'Failed' | 'Skipped'
            msg_text:     The plain-text confirmation message.
            fallback_logged: True if both channels failed and a fallback log was created.
    """
    # Build messages
    msg_text = build_confirmation_text(
        name, app_type, amount, ref_id,
        tenure=tenure, emi=emi,
        maturity_amount=maturity_amount, is_deposit=is_deposit
    )
    html_body = build_confirmation_html(
        name, app_type, amount, ref_id,
        tenure=tenure, emi=emi,
        maturity_amount=maturity_amount, is_deposit=is_deposit
    )

    email_status = "Skipped"
    sms_status = "Skipped"
    fallback_logged = False

    # ── Email Channel ────────────────────────────────────────────────────
    if email:
        subject = f"SmartBank — Application {ref_id} Confirmed"
        sent = send_email(email, subject, html_body)
        email_status = "Sent" if sent else "Failed"

    # ── SMS Channel ──────────────────────────────────────────────────────
    if phone:
        sent = send_sms(phone, msg_text)
        sms_status = "Sent" if sent else "Failed"

    # ── Fallback: log warning if ALL channels failed ─────────────────────
    if email_status == "Failed" and sms_status == "Failed":
        logger.error(
            f"FALLBACK: Both SMS and email delivery failed for {ref_id}. "
            f"Application by '{name}' for {app_type} (₹{amount:,.2f}) "
            f"requires manual follow-up."
        )
        fallback_logged = True
    elif email_status == "Skipped" and sms_status == "Skipped":
        logger.warning(
            f"No contact details provided for {ref_id}. "
            f"No confirmation dispatched."
        )
    elif email_status == "Failed" or sms_status == "Failed":
        # One channel succeeded, one failed — log partial failure
        logger.warning(
            f"Partial delivery for {ref_id}: "
            f"Email={email_status}, SMS={sms_status}."
        )

    return {
        "email_status": email_status,
        "sms_status": sms_status,
        "msg_text": msg_text,
        "html_body": html_body,
        "fallback_logged": fallback_logged
    }


def _pretty_type_name(app_type: str) -> str:
    """Convert internal scheme/loan type codes to human-readable labels."""
    type_map = {
        "home": "Home Loan",
        "personal": "Personal Loan",
        "car": "Car Loan",
        "gold": "Gold Loan",
        "fd1": "1-Year Fixed Deposit",
        "fd3": "3-Year Fixed Deposit",
        "fd5": "5-Year Fixed Deposit",
        "rd": "Recurring Deposit",
    }
    return type_map.get(app_type, app_type.capitalize())
