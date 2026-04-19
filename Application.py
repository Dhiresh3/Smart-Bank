from flask import Flask, request, jsonify, send_file
from bank_logic import create_account, deposit, withdraw as withdraw_logic, check_balance, close_account, load_data, save_data
from face_auth import capture_and_verify
import os
from datetime import datetime
from pymongo import MongoClient

# MongoDB connection
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["smartbank"]
accounts_col = db["accounts"]
logins_col = db["logins"]


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


app = Flask(__name__)
passbook_failed_attempts = {}

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

@app.route("/open_account", methods=["POST"])
def open_account():
    data = request.json
    age = data.get("age", 0)
    if age < 18:
        return jsonify({
            "status": "fail",
            "message": "❌ You must be at least 18 years old to open an account."
        })
    
    if capture_and_verify(data["name"], enroll=True):
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
        "message": "❌ Face capture failed. Please try again."
    })

@app.route("/deposit", methods=["POST"])
def deposit_route():
    data = request.json
    name = data.get("name", "user")

    if capture_and_verify(name):
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

    if capture_and_verify(name):
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
    data = request.json
    return jsonify(check_balance(data))

@app.route("/close_account", methods=["POST"])
def close_route():
    data = request.json
    if capture_and_verify(data["name"]):
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

    if capture_and_verify(name):
        # Face capture success: reset failed attempts
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
        
        if attempts >= 3:
            # Ban/Close Account
            close_account({"name": name, "acc_no": acc_no, "pass": password})
            del passbook_failed_attempts[acc_no]
            return jsonify({"success": False, "status": "banned", "message": "Your account has been closed due to repeated failed verification attempts."})
        
        remaining = 3 - attempts
        return jsonify({"success": False, "status": "fail", "message": f"Camera failed to capture your face. You have {remaining} attempt(s) left."})

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

    if capture_and_verify(name):
        if not new_password or len(new_password.strip()) == 0:
            return jsonify({"success": False, "message": "New password cannot be empty"}), 400

        accounts_col.update_one(
            {"acc_no": acc_no},
            {"$set": {"pass": new_password}}
        )
        log_transaction(acc_no, "Password Reset", None, account["balance"])

        return jsonify({
            "success": True,
            "status": "success",
            "message": "✅ Password reset successfully!"
        })
    else:
        return jsonify({
            "success": False,
            "message": "❌ Camera failed to capture your face. Password reset blocked."
        })

@app.route("/update_face_capture", methods=["POST"])
def update_face_capture():
    data = request.get_json()
    acc_no = data.get("account_number")
    password = data.get("password")

    account = accounts_col.find_one({"acc_no": acc_no})

    if not account:
        return jsonify({"success": False, "message": "Account not found"}), 404

    if account["pass"] != password:
        return jsonify({"success": False, "message": "Invalid password"}), 401

    name = account["name"]

    if capture_and_verify(name, enroll=True):
        log_transaction(acc_no, "Face Capture Updated", None, account["balance"])
        return jsonify({
            "success": True,
            "status": "success",
            "message": "✅ Face capture updated successfully!"
        })
    
    return jsonify({
        "success": False,
        "message": "❌ Face capture failed. Please try again."
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
    login_time = data.get("login_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Insert login record into MongoDB
    logins_col.insert_one({
        "username": username,
        "login_time": login_time
    })

    return jsonify({"status": "success", "message": "Login recorded"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
