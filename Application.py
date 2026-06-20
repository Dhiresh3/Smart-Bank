from flask import Flask, request, jsonify, send_file
from bank_logic import create_account, deposit, withdraw as withdraw_logic, check_balance, close_account, load_data, save_data
from face_auth import verify_face_image
import os
from datetime import datetime
from pymongo import MongoClient

# MongoDB connection
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["smartbank"]
accounts_col = db["accounts"]
logins_col = db["logins"]
verification_failures_col = db["verification_failures"]
complaints_col = db["complaints"]

import mysql_backup
import notification_service
import random



def log_transaction(account, tx_type, amount=None, balance=None):
    """Push a transaction entry into the account's history array in MongoDB."""
    tx_entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": tx_type,
        "amount": amount,
        "balance": balance
    }
    accounts_col.update_one(
        {"acc_no": account},
        {"$push": {"history": tx_entry}}
    )


app = Flask(__name__, static_folder="static")
passbook_failed_attempts = {}

# ── Allow camera/microphone on all responses (required for deployed HTTPS) ────
@app.route("/apply_scheme", methods=["POST"])
def apply_scheme():
    """Process loan/scheme applications and dispatch confirmation notifications.

    Captures contact details (phone/email), generates a reference ID,
    calculates financial details (EMI or maturity), persists to MongoDB
    and MySQL, then immediately triggers confirmation via SMS and/or email.
    """
    data = request.json
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    amount = float(data.get("amount", 0))
    tenure = float(data.get("tenure", 0))
    scheme_type = data.get("type", "").strip()
    opt_in = bool(data.get("opt_in", True))

    if not name or amount <= 0 or tenure <= 0 or not scheme_type:
        return jsonify({"status": "fail", "message": "❌ Invalid inputs provided."})

    # ── Generate unique reference ID ─────────────────────────────────────
    ref_id = f"REF-{random.randint(100000, 999999)}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ── Financial calculations ───────────────────────────────────────────
    is_deposit = "fd" in scheme_type.lower() or "rd" in scheme_type.lower()
    emi = 0
    maturity_amount = 0

    if is_deposit:
        rates = {"fd1": 6.5, "fd3": 7.0, "fd5": 7.5, "rd": 7.0}
        rate = rates.get(scheme_type, 7.0) / 100
        maturity_amount = amount * ((1 + rate) ** tenure)
    else:
        rates = {"home": 8.4, "personal": 10.5, "car": 8.5, "gold": 10.0}
        rate = rates.get(scheme_type, 8.5) / 100
        monthly_rate = rate / 12
        num_months = tenure * 12
        if monthly_rate > 0:
            emi = (amount * monthly_rate * ((1 + monthly_rate) ** num_months)) / (
                ((1 + monthly_rate) ** num_months) - 1
            )
        else:
            emi = amount / num_months

    # ── Encrypt contact data before storage ──────────────────────────────
    encrypted_email = notification_service.encrypt_contact(email)
    encrypted_phone = notification_service.encrypt_contact(phone)

    # ── Persist application to MongoDB ───────────────────────────────────
    app_doc = {
        "ref_id": ref_id,
        "name": name,
        "type": scheme_type,
        "amount": amount,
        "tenure": tenure,
        "email": encrypted_email,
        "phone": encrypted_phone,
        "opt_in": opt_in,
        "timestamp": timestamp
    }
    db["applications"].insert_one(app_doc)

    # ── Sync to MySQL backup ────────────────────────────────────────────
    mysql_backup.add_application(
        ref_id, name, scheme_type, amount, tenure,
        encrypted_email, encrypted_phone, opt_in, timestamp
    )

    # ── Dispatch confirmation notifications immediately ──────────────────
    email_status = "Skipped"
    sms_status = "Skipped"
    fallback_logged = False

    if opt_in:
        try:
            # Use the unified notification dispatcher
            notif_result = notification_service.send_confirmation_notification(
                name=name,
                email=email,
                phone=phone,
                app_type=scheme_type,
                amount=amount,
                ref_id=ref_id,
                tenure=tenure,
                emi=emi,
                maturity_amount=maturity_amount,
                is_deposit=is_deposit
            )
            email_status = notif_result["email_status"]
            sms_status = notif_result["sms_status"]
            fallback_logged = notif_result["fallback_logged"]
            msg_text = notif_result["msg_text"]
            html_body = notif_result.get("html_body", "")

            # ── Log notification attempts to MongoDB & MySQL ─────────────────
            if email:
                log_doc = {
                    "ref_id": ref_id,
                    "recipient": encrypted_email,
                    "channel": "email",
                    "status": email_status,
                    "message": msg_text,
                    "html_body": html_body,
                    "timestamp": timestamp
                }
                db["notification_logs"].insert_one(log_doc)
                mysql_backup.add_notification_log(
                    ref_id, encrypted_email, "email", email_status, msg_text, timestamp,
                    html_body=html_body
                )

            if phone:
                log_doc = {
                    "ref_id": ref_id,
                    "recipient": encrypted_phone,
                    "channel": "sms",
                    "status": sms_status,
                    "message": msg_text,
                    "html_body": "",
                    "timestamp": timestamp
                }
                db["notification_logs"].insert_one(log_doc)
                mysql_backup.add_notification_log(
                    ref_id, encrypted_phone, "sms", sms_status, msg_text, timestamp,
                    html_body=""
                )

            # ── Fallback: persist failed delivery for manual follow-up ───────
            if fallback_logged:
                db["notification_fallbacks"].insert_one({
                    "ref_id": ref_id,
                    "name": name,
                    "type": scheme_type,
                    "amount": amount,
                    "email_status": email_status,
                    "sms_status": sms_status,
                    "requires_manual_followup": True,
                    "timestamp": timestamp
                })
        except Exception as e:
            print(f"⚠️ Notification dispatch error (application still saved): {e}")
            email_status = "Failed"
            sms_status = "Failed"

    return jsonify({
        "status": "success",
        "message": f"✅ Application submitted successfully! Ref ID: {ref_id}",
        "ref_id": ref_id,
        "email_status": email_status,
        "sms_status": sms_status,
        "fallback_logged": fallback_logged
    })

@app.after_request

def set_permissions_policy(response):
    """
    Browsers block camera access unless the server explicitly allows it.
    These headers enable camera (and mic) for the origin that serves the page.
    """
    response.headers["Permissions-Policy"] = "camera=*, microphone=*"
    response.headers["Feature-Policy"]     = "camera *; microphone *"
    # Allow the page to be embedded in same origin (needed for some browsers)
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    return response

@app.route("/")
def root():
    return send_file("login.html")

@app.route("/login.html")
def login_page():
    return send_file("login.html")

@app.route("/index.html")
def home():
    return send_file("index.html")

@app.route("/accounts.json")
def get_accounts():
    """Serve accounts data from MongoDB as JSON (backwards-compatible with frontend)."""
    data = load_data()
    return jsonify(data)

@app.route("/index.js")
def get_js():
    return send_file("index.js")

@app.route("/index.css")
def get_css():
    return send_file("index.css")

@app.route("/bank.js")
def get_bank_js():
    return send_file("bank.js")

@app.route("/bank.css")
def get_bank_css():
    return send_file("bank.css")

@app.route("/Futuristic 3D logo d.png")
def logo_image():
    return send_file("Futuristic 3D logo d.png", mimetype="image/png")

@app.route("/test_camera.html")
def test_camera():
    return send_file("test_camera.html")

# ── Serve coin-drop login sound ──────────────────────────────────────────────
# File is at static/coin_drop.mp3 (committed to the repo, works on Render too)
COIN_DROP_AUDIO_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "static", "coin_drop.mp3"
)

@app.route("/coin_drop.mp3")
def coin_drop_audio():
    """Serve the coin-drop MP3 that plays after a successful login."""
    if os.path.exists(COIN_DROP_AUDIO_PATH):
        return send_file(COIN_DROP_AUDIO_PATH, mimetype="audio/mpeg")
    return jsonify({"error": "Audio file not found"}), 404

@app.route("/open_account", methods=["POST"])
def open_account():
    data = request.json
    age = data.get("age", 0)
    if age < 18:
        return jsonify({
            "status": "fail",
            "message": "❌ You must be at least 18 years old to open an account."
        })

    face_image = data.get("face_image", "")
    if verify_face_image(data["name"], face_image, enroll=True):
        result = create_account(data)
        account_number = result.get("account_number", "N/A")
        print(f"✅ Face captured and enrolled for {data['name']}. Account Number: {account_number}")
        return jsonify({
            "status": "success",
            "message": f"✅ Face captured for {data['name']}. Account created successfully!",
            "account_number": account_number,
            "name": data["name"],
            "age": data.get("age", 18),
            "income": data.get("income", 0),
            "account_type": data.get("account_type", "Savings"),
            "celebrate": True
        })
    return jsonify({
        "status": "fail",
        "message": "❌ Face not detected. Please allow camera access and try again."
    })

@app.route("/deposit", methods=["POST"])
def deposit_route():
    data = request.json
    name = data.get("name", "user")
    face_image = data.get("face_image", "")

    if verify_face_image(name, face_image):
        result = deposit(data)
        result["message"] = "✅ Face recognized. " + result.get("message", "")
        result["celebrate"] = True
        return jsonify(result)
    return jsonify({
        "status": "fail",
        "message": "❌ Face not recognized. Deposit blocked."
    })

@app.route("/withdraw", methods=["POST"])
def withdraw_route():
    data = request.json
    name = data.get("name", "user")
    face_image = data.get("face_image", "")

    if verify_face_image(name, face_image):
        result = withdraw_logic(data)
        result["message"] = "✅ Face recognized. " + result.get("message", "")
        result["celebrate"] = True
        return jsonify(result)
    return jsonify({
        "status": "fail",
        "message": "❌ Face not recognized. Withdrawal blocked."
    })

@app.route("/check_balance", methods=["POST"])
def balance_route():
    """
    Check balance requires face verification before returning account data.
    Expects: { acc_no, pass, face_image (base64) }
    """
    data = request.json
    name = data.get("name", "")
    face_image = data.get("face_image", "")

    # If a name is provided, require face verification
    if name:
        if not verify_face_image(name, face_image):
            return jsonify({
                "status": "fail",
                "message": "❌ Face not detected. Please allow camera access and try again."
            })

    result = check_balance(data)
    return jsonify(result)

@app.route("/close_account", methods=["POST"])
def close_route():
    data = request.json
    face_image = data.get("face_image", "")
    if verify_face_image(data["name"], face_image):
        result = close_account(data)
        result["message"] = "✅ Face recognized. " + result.get("message", "")
        result["celebrate"] = True
        return jsonify(result)
    return jsonify({
        "status": "fail",
        "message": "❌ Face not recognized. Account closure blocked."
    })

@app.route("/support", methods=["POST"])
def support():
    data = request.json
    message = data.get("message", "").lower()

    if "forgot" in message and "password" in message:
        reply = "You can reset your password by visiting your nearest SmartBank branch or contacting our helpline at 1800-123-456."
    elif "loan" in message:
        reply = "SmartBank offers personal and education loans at 8.5% interest. Would you like me to connect you with a loan officer?"
    elif "balance" in message:
        reply = "You can check your balance in the 'Check Balance' section of SmartBank 3D."
    else:
        reply = "Thank you for contacting SmartBank Support. A representative will get back to you soon."

    return jsonify({"reply": reply})

@app.route("/transaction_history", methods=["POST"])
def transaction_history():
    data = request.get_json()
    acc_no = data.get("account_number")
    password = data.get("password")

    account = accounts_col.find_one({"acc_no": acc_no})

    if not account or account["pass"] != password:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    history = account.get("history", [])
    account_name = account.get("name", "")

    return jsonify({"success": True, "history": history, "account_name": account_name})

@app.route("/passbook_data", methods=["POST"])
def passbook_data():
    data = request.get_json()
    acc_no = data.get("account_number")
    password = data.get("password")

    account = accounts_col.find_one({"acc_no": acc_no})

    if not account or account["pass"] != password:
        return jsonify({"success": False, "status": "fail", "message": "Invalid credentials"}), 401

    name = account["name"]

    face_image = data.get("face_image", "")
    if verify_face_image(name, face_image):
        # Face verification success: reset failed attempts
        if acc_no in passbook_failed_attempts:
            del passbook_failed_attempts[acc_no]

        account_details = {
            "name": account.get("name", ""),
            "age": account.get("age", ""),
            "income": account.get("income", ""),
            "account_type": account.get("account_type", ""),
            "balance": account.get("balance", 0),
            "history": account.get("history", [])
        }
        return jsonify({"success": True, "status": "success", "account_details": account_details})
    else:
        attempts = passbook_failed_attempts.get(acc_no, 0) + 1
        passbook_failed_attempts[acc_no] = attempts

        if attempts >= 5:
            close_account({"name": name, "acc_no": acc_no, "pass": password})
            if acc_no in passbook_failed_attempts:
                del passbook_failed_attempts[acc_no]
            return jsonify({"success": False, "status": "banned", "message": "Your account has been closed due to repeated failed verification attempts."})

        remaining = 5 - attempts
        return jsonify({"success": False, "status": "fail", "message": f"Face not detected. Please allow camera access. You have {remaining} attempt(s) left."})


@app.route("/reset_password", methods=["POST"])
def reset_password():
    data = request.get_json()
    acc_no = data.get("account_number")
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    account = accounts_col.find_one({"acc_no": acc_no})

    if not account:
        return jsonify({"success": False, "message": "Account not found"}), 404

    if account["pass"] != old_password:
        return jsonify({"success": False, "message": "Invalid current password"}), 401
    
    name = account["name"]

    face_image = data.get("face_image", "")
    if verify_face_image(name, face_image):
        if not new_password or len(new_password.strip()) == 0:
            return jsonify({"success": False, "message": "New password cannot be empty"}), 400

        accounts_col.update_one(
            {"acc_no": acc_no},
            {"$set": {"pass": new_password}}
        )
        log_transaction(acc_no, "Password Reset", None, account["balance"])
        
        updated_account = accounts_col.find_one({"acc_no": acc_no})
        if updated_account:
            mysql_backup.sync_account(updated_account)

        return jsonify({
            "success": True,
            "status": "success",
            "message": "✅ Password reset successfully!"
        })
    else:
        return jsonify({
            "success": False,
            "message": "❌ Face not detected. Please allow camera access. Password reset blocked."
        })

@app.route("/update_face_capture", methods=["POST"])
def update_face_capture():
    """
    Re-enroll the user's face using a browser-captured base64 image.
    Expects: { account_number, password, face_image (base64) }
    """
    data = request.get_json()
    acc_no = data.get("account_number")
    password = data.get("password")
    face_image = data.get("face_image", "")

    account = accounts_col.find_one({"acc_no": acc_no})

    if not account:
        return jsonify({"success": False, "message": "Account not found"}), 404

    if account["pass"] != password:
        return jsonify({"success": False, "message": "Invalid password"}), 401

    name = account["name"]

    if verify_face_image(name, face_image, enroll=True):
        log_transaction(acc_no, "Face Capture Updated", None, account["balance"])
        return jsonify({
            "success": True,
            "status": "success",
            "message": "✅ Face capture updated successfully!"
        })

    return jsonify({
        "success": False,
        "message": "❌ Face not detected in image. Please allow camera access and try again."
    })


def generate_safe_reply(user_message: str) -> str:
    if not user_message or not user_message.strip():
        return "I'm here to help with SmartBank services. How can I assist you today?"

    msg = user_message.lower()
    if any(k in msg for k in ["password", "otp", "pin", "cvv"]):
        return "For your security, please do not share passwords, PINs, CVVs, or OTPs. How else can I help?"

    if "balance" in msg:
        return "I can guide you on checking balances. For security, please use the Check Balance section in the app."
    if "open account" in msg or "create account" in msg:
        return "To open an account, please use the Open Account section and confirm you are above 18. I can guide you through the steps."
    if "loan" in msg or "eligibility" in msg:
        return "I can share general loan and eligibility info. For specifics, please provide product type and ensure required documents are ready."
    if "lost card" in msg or "block card" in msg:
        return "Please contact SmartBank support immediately to block your card. Do not share your card details here."
    if "contact" in msg or "support" in msg:
        return "You can reach SmartBank support at support@SmartBank3D.com or call 1800-123-456."
    if "hello" in msg or "hi" in msg:
        return "Hello! Welcome to Skiller SmartBank. How can I assist you today?"
    if "Bank Information" in msg or "bank Info" in msg:
        return "Bank is established in 2025 by Dhiresh Margaj."    
    if "thank" in msg:
        return "You're welcome! Is there anything else I can help you with?"

    return "I'm here to help with SmartBank services — accounts, deposits, withdrawals, loans, and more. How can I assist you?"


@app.route("/ai_chat", methods=["POST"])
def ai_chat():
    data = request.get_json(force=True, silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"reply": "Please enter a message so I can assist you."})

    reply = generate_safe_reply(user_message)
    return jsonify({"reply": reply})

@app.route("/log_login", methods=["POST"])
def log_login():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username", "Unknown")
    account_number = data.get("account_number", "Unknown")
    login_time = data.get("login_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Insert login record into MongoDB
    logins_col.insert_one({
        "username": username,
        "account_number": account_number,
        "login_time": login_time
    })
    mysql_backup.add_login(username, login_time, account_number)

    return jsonify({"status": "success", "message": "Login recorded"})


@app.route("/log_failed_attempt", methods=["POST"])
def log_failed_attempt():
    """
    Log verification failures into MongoDB for auditing purposes.
    Expects: { account_number, action, attempt, reason }
    """
    data = request.get_json(force=True, silent=True) or {}
    acc_no = data.get("account_number", "Unknown")
    action = data.get("action", "Unknown")
    attempt = data.get("attempt", 0)
    reason = data.get("reason", "Face verification failed")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Record failure event in MongoDB collection
    verification_failures_col.insert_one({
        "account_number": acc_no,
        "action": action,
        "attempt": attempt,
        "reason": reason,
        "timestamp": timestamp
    })
    mysql_backup.add_verification_failure(acc_no, action, attempt, reason, timestamp)

    print(f"AUDIT WARNING: Failed verification attempt {attempt}/5 on action '{action}' for account {acc_no}. Reason: {reason}")

    return jsonify({"status": "success", "message": "Verification failure logged for audit."})


@app.route("/register_complaint", methods=["POST"])
def register_complaint():
    data = request.get_json(force=True, silent=True) or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    contact = data.get("contact_number", "").strip()
    comments = data.get("comments", "").strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not name or not email or not contact or not comments:
        return jsonify({"success": False, "message": "All fields are required."}), 400

    # Insert into MongoDB
    complaints_col.insert_one({
        "name": name,
        "email": email,
        "contact_number": contact,
        "comments": comments,
        "timestamp": timestamp
    })

    # Backup to MySQL
    mysql_backup.add_complaint(name, email, contact, comments, timestamp)

    return jsonify({"success": True, "message": "✅ Your thoughts have been registered successfully! Thank you."})


if __name__ == "__main__":
    mysql_backup.init_db()
    mysql_backup.sync_all_mongo_to_sqlite()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

