import os
import sys
import traceback

# Ensure project root is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ""))
if project_root not in sys.path:
    sys.path.append(project_root)

def log(message):
    # Ensure Unicode characters are safely printed on Windows console
    # Replace any non‑ASCII characters (e.g., ₹) with a placeholder to avoid cp1252 errors
    safe_msg = ''.join(c if ord(c) < 128 else '?' for c in str(message))
    print(f"[HealthCheck] {safe_msg}")

def check_mongo_connection():
    try:
        from pymongo import MongoClient
        client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
        client.admin.command('ping')
        log("MongoDB connection successful.")
        return True
    except Exception as e:
        log(f"MongoDB connection failed: {e}")
        return False

def check_notification_service():
    try:
        import notification_service as ns
        result_email = ns.send_email("test@example.com", "HealthCheck", "<p>test</p>")
        result_sms = ns.send_sms("+1234567890", "HealthCheck message")
        log(f"Email send returned {result_email}, SMS send returned {result_sms} (expected False if credentials missing).")
        return True
    except Exception as e:
        log(f"Notification service check failed: {e}")
        return False

def check_face_auth():
    try:
        import face_auth
        # Just ensure the module loads; actual capture requires hardware.
        log("face_auth module imported successfully.")
        return True
    except Exception as e:
        log(f"face_auth import failed: {e}")
        return False

def check_bank_logic():
    try:
        import bank_logic as bl
        # Create a dummy account
        dummy = {
            "name": "Test User",
            "pass": "1234",
            "age": 30,
            "income": 50000,
            "account_type": "Savings",
            "location": "Nowhere"
        }
        create_res = bl.create_account(dummy)
        acc_no = create_res.get("account_number")
        log(f"Created dummy account #{acc_no}")
        # Deposit
        deposit_res = bl.deposit({"acc_no": acc_no, "pass": "1234", "amount": 1000})
        log(f"Deposit result: {deposit_res}")
        # Withdraw
        withdraw_res = bl.withdraw({"acc_no": acc_no, "pass": "1234", "amount": 500})
        log(f"Withdraw result: {withdraw_res}")
        # Balance check
        bal_res = bl.check_balance({"acc_no": acc_no, "pass": "1234"})
        log(f"Balance check: {bal_res}")
        # Close
        close_res = bl.close_account({"acc_no": acc_no, "pass": "1234"})
        log(f"Close account result: {close_res}")
        return True
    except Exception as e:
        log(f"Bank logic check failed: {e}\n{traceback.format_exc()}")
        return False

def main():
    log("Starting health checks...")
    results = {
        "mongo": check_mongo_connection(),
        "notification": check_notification_service(),
        "face_auth": check_face_auth(),
        "bank_logic": check_bank_logic()
    }
    passed = all(results.values())
    log(f"Health check summary: {results}, overall passed: {passed}")
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
