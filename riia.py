import json
import os
import random
import uuid
import hashlib
from datetime import datetime


def load_data():
    if not os.path.exists("accounts.json"):
        return {}
    try:
        with open("accounts.json", "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_data(data):
    with open("accounts.json", "w") as f:
        json.dump(data, f, indent=4)



def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def generate_account_number():
    accounts = load_data()
    while True:
        num_digits = random.choice([7, 8])
        acc_no = str(random.randint(10**(num_digits - 1), 10**num_digits - 1))
        if acc_no not in accounts:
            return acc_no

def generate_customer_uuid():
    return str(uuid.uuid4())

def create_account(data):
    accounts = load_data()

    acc_no = generate_account_number()
    customer_uuid = generate_customer_uuid()

    accounts[acc_no] = {
        "customer_uuid": customer_uuid,
        "full_name": data["full_name"],
        "age": data.get("age", 18),
        "upi_id": data.get("upi_id", ""),
        "bank_name": data.get("bank_name", "MyBank"),
        "account_number": acc_no,
        "ifsc_code": data.get("ifsc_code", ""),
        "home_branch": data.get("home_branch", ""),
        "registered_phone_number": data.get("registered_phone_number", ""),
        "registered_device_id": data.get("registered_device_id", ""),
        "registered_ip_address": data.get("registered_ip_address", ""),
        "account_balance": 0.0,
        "last_transaction_amount": 0.0,
        "total_transactions_count": 0,
        "total_transactions_amount": 0.0,
        "account_open_date": datetime.now().strftime("%Y-%m-%d"),
        "password": hash_password(data["pass"]),
        "history": []
    }

    save_data(accounts)

    return {
        "status": "success",
        "message": f"Account created successfully for {data['full_name']}",
        "account_number": acc_no,
        "customer_uuid": customer_uuid
    }

def deposit(data):
    accounts = load_data()
    acc_no = str(data["acc_no"])

    if acc_no in accounts and accounts[acc_no]["password"] == hash_password(data["pass"]):
        amount = float(data["amount"])
        if amount <= 0:
            return {"status": "fail", "message": "Deposit amount must be positive"}

        accounts[acc_no]["account_balance"] += amount
        accounts[acc_no]["last_transaction_amount"] = amount
        accounts[acc_no]["total_transactions_count"] += 1
        accounts[acc_no]["total_transactions_amount"] += amount

        accounts[acc_no]["history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "deposit",
            "amount": amount
        })

        save_data(accounts)
        return {"status": "success", "message": f"₹{amount} deposited successfully"}

    return {"status": "fail", "message": "Invalid credentials"}

def withdraw(data):
    accounts = load_data()
    acc_no = str(data["acc_no"])

    if acc_no in accounts and accounts[acc_no]["password"] == hash_password(data["pass"]):
        amount = float(data["amount"])
        if amount <= 0:
            return {"status": "fail", "message": "Withdrawal amount must be positive"}

        if accounts[acc_no]["account_balance"] >= amount:
            accounts[acc_no]["account_balance"] -= amount
            accounts[acc_no]["last_transaction_amount"] = amount
            accounts[acc_no]["total_transactions_count"] += 1
            accounts[acc_no]["total_transactions_amount"] += amount

            accounts[acc_no]["history"].append({
                "timestamp": datetime.now().isoformat(),
                "action": "withdraw",
                "amount": amount
            })

            save_data(accounts)
            return {"status": "success", "message": f"₹{amount} withdrawn successfully"}

        return {"status": "fail", "message": "Insufficient balance"}

    return {"status": "fail", "message": "Invalid credentials"}


def check_balance(data):
    accounts = load_data()
    acc_no = str(data["acc_no"])

    if acc_no in accounts and accounts[acc_no]["password"] == hash_password(data["pass"]):
        balance = accounts[acc_no]["account_balance"]

        accounts[acc_no]["history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "check_balance",
            "amount": None
        })

        save_data(accounts)

        return {
            "status": "success",
            "balance": balance,
            "message": f"Current balance: ₹{balance}"
        }

    return {"status": "fail", "message": "Invalid credentials"}

def close_account(data):
    accounts = load_data()
    acc_no = str(data["acc_no"])

    if acc_no in accounts and accounts[acc_no]["password"] == hash_password(data["pass"]):
        del accounts[acc_no]
        save_data(accounts)
        return {"status": "success", "message": f"Account {acc_no} closed successfully"}

    return {"status": "fail", "message": "Invalid credentials"}


def detect_anomalies(accounts):
    """
    Analyze all accounts and return a list of (account_number, issue) tuples.
    This is backend logic only – the frontend can call this via an API or directly.
    """
    anomalies = []

    for acc_no, acc in accounts.items():
        # --- 1. Password strength check ---
        password = acc.get("pass") or acc.get("password") or ""
        if isinstance(password, str) and password.isdigit() and len(password) < 6:
            anomalies.append((acc_no, "Weak password"))

        # --- 2. History structure check ---
        history = acc.get("history", [])
        for entry in history:
            if isinstance(entry, str):
                # Plain text history instead of structured dict
                anomalies.append((acc_no, "Unstructured history entry"))

        # --- 3. Balance validation from transaction history ---
        calculated_balance = 0.0
        for entry in history:
            if isinstance(entry, dict):
                amount = entry.get("amount")
                if amount is None:
                    continue

                # Support both "type" (Credit/Debit) and "action" (deposit/withdraw)
                tx_type = (entry.get("type") or entry.get("action") or "").lower()

                if tx_type in ("credit", "deposit"):
                    calculated_balance += float(amount)
                elif tx_type in ("debit", "withdraw"):
                    calculated_balance -= float(amount)

        # Stored balance can be under different keys depending on source
        stored_balance = acc.get("balance", acc.get("account_balance", 0.0))
        try:
            stored_balance = float(stored_balance)
        except (TypeError, ValueError):
            anomalies.append((acc_no, "Invalid balance value"))
            continue

        # Only compare if we have some structured history
        if history and round(calculated_balance, 2) != round(stored_balance, 2):
            anomalies.append((acc_no, "Balance mismatch"))

        # --- 4. Negative balance check ---
        if stored_balance < 0:
            anomalies.append((acc_no, "Negative balance"))

    return anomalies


def get_anomalies():
    """
    Helper for the frontend / API layer.
    Loads data from JSON and returns anomalies in a JSON‑friendly structure.
    """
    accounts = load_data()
    anomaly_list = detect_anomalies(accounts)

    # Convert tuples to dicts for clean JSON
    return [
        {"account_number": acc_no, "issue": issue}
        for acc_no, issue in anomaly_list
    ]


# =========================
# RIIA Investigation Logic
# =========================

TRANSACTIONS_FILE = "riia_transactions.json"
CUSTOMERS_FILE = "riia_customers.json"
MERCHANTS_FILE = "riia_merchants.json"

MAX_TX_AMOUNT = 20000.0  # hard limit
HIGH_VALUE_THRESHOLD = 10000.0  # used for velocity checks
VELOCITY_WINDOW_MINUTES = 10
VELOCITY_COUNT_THRESHOLD = 5
FAILED_LOGIN_BLOCK_THRESHOLD = 3


def _load_json(path):
    if not os.path.exists(path):
        return {} if path != TRANSACTIONS_FILE else []
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {} if path != TRANSACTIONS_FILE else []


def load_investigation_data():
    """
    Load customers, merchants, and transactions used by the investigation engine.
    """
    customers = _load_json(CUSTOMERS_FILE)
    merchants = _load_json(MERCHANTS_FILE)
    transactions = _load_json(TRANSACTIONS_FILE)
    return customers, merchants, transactions


def _parse_iso(ts):
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def evaluate_transaction(tx, customer, merchant, all_customer_transactions):
    """
    Core investigation logic for a single transaction.

    Returns a dict with:
    - verdict: "Approve" | "Reject" | "Escalate"
    - red_flags: list of strings
    """
    red_flags = []

    amount = float(tx.get("transaction_amount", 0.0))
    tx_time = _parse_iso(tx.get("transaction_timestamp", ""))
    tx_location = tx.get("transaction_location", "")

    # --- 0. Basic customer risk (failed logins / blocked) ---
    failed_logins = int(customer.get("failed_login_attempts", 0))
    is_blocked = bool(customer.get("is_blocked", False))
    if failed_logins >= FAILED_LOGIN_BLOCK_THRESHOLD or is_blocked:
        red_flags.append("Customer blocked due to multiple failed logins")

    # --- 1. Amount limit ---
    if amount > MAX_TX_AMOUNT:
        red_flags.append(f"Transaction amount above limit ₹{MAX_TX_AMOUNT}")

    # --- 2. Location mismatch ---
    known_locations = customer.get("known_locations", [])
    if known_locations and tx_location and tx_location not in known_locations:
        red_flags.append("Location mismatch: new transaction city for this user")

    # --- 3. Merchant risk (new category) ---
    known_categories = customer.get("known_merchant_categories", [])
    merchant_category = merchant.get("merchant_category", "")
    if known_categories and merchant_category and merchant_category not in known_categories:
        red_flags.append("Merchant risk: new merchant category for this user")

    # --- 4. Velocity checks: N high-value tx in short window ---
    if tx_time:
        window_start = tx_time.replace()  # copy
        # use timedelta in minutes
        from datetime import timedelta

        window_start = tx_time - timedelta(minutes=VELOCITY_WINDOW_MINUTES)
        recent_high_value = 0
        for other in all_customer_transactions:
            if other.get("status") != "SUCCESS":
                continue
            other_time = _parse_iso(other.get("transaction_timestamp", ""))
            if not other_time:
                continue
            if not (window_start <= other_time <= tx_time):
                continue
            other_amount = float(other.get("transaction_amount", 0.0))
            if other_amount >= HIGH_VALUE_THRESHOLD:
                recent_high_value += 1

        if recent_high_value >= VELOCITY_COUNT_THRESHOLD:
            red_flags.append(
                f"Velocity: {recent_high_value} high-value tx "
                f"in {VELOCITY_WINDOW_MINUTES} minutes"
            )

    # --- 5. Failed transaction / status-based protection ---
    status = (tx.get("status") or "").upper()
    if status == "FAILED":
        red_flags.append("Multiple failed transactions observed for this customer")

    
    if amount > MAX_TX_AMOUNT or failed_logins >= FAILED_LOGIN_BLOCK_THRESHOLD or is_blocked:
        verdict = "Reject"
    # Escalate if any red flags but not hard reject
    elif red_flags:
        verdict = "Escalate"
    else:
        verdict = "Approve"

    return {"verdict": verdict, "red_flags": red_flags}


def investigate_all_transactions():
    """
    Run investigation over all transactions and return a list of enriched records
    for the UI / admin dashboard.

    Each item includes:
    - transaction fields (uuid, amount, timestamp, location, device, IP, etc.)
    - linked customer_uuid and merchant_uuid
    - full merchant details
    - verdict and red_flags
    """
    customers, merchants, transactions = load_investigation_data()

    # Index transactions per customer for velocity checks
    tx_by_customer = {}
    for tx in transactions:
        cust_id = tx.get("customer_uuid")
        tx_by_customer.setdefault(cust_id, []).append(tx)

    results = []
    for tx in transactions:
        cust_id = tx.get("customer_uuid")
        merch_id = tx.get("merchant_uuid")

        customer = customers.get(cust_id, {})
        merchant = merchants.get(merch_id, {})

        customer_txs = tx_by_customer.get(cust_id, [])
        investigation = evaluate_transaction(tx, customer, merchant, customer_txs)

        enriched = {
            # Transaction fields for officer view
            "transaction_uuid": tx.get("transaction_uuid"),
            "customer_uuid": cust_id,
            "merchant_uuid": merch_id,
            "transaction_amount": tx.get("transaction_amount"),
            "transaction_timestamp": tx.get("transaction_timestamp"),
            "transaction_location": tx.get("transaction_location"),
            "customer_device_id": tx.get("customer_device_id"),
            "customer_ip_address": tx.get("customer_ip_address"),
            "status": tx.get("status"),

            # Merchant details (for drill-down)
            "merchant_name": merchant.get("merchant_name"),
            "merchant_upi_id": merchant.get("merchant_upi_id"),
            "merchant_bank_name": merchant.get("merchant_bank_name"),
            "merchant_account_number": merchant.get("merchant_account_number"),
            "merchant_ifsc_code": merchant.get("merchant_ifsc_code"),
            "merchant_bank_branch": merchant.get("merchant_bank_branch"),
            "merchant_bank_address": merchant.get("merchant_bank_address"),
            "merchant_account_open_date": merchant.get("merchant_account_open_date"),
            "merchant_category": merchant.get("merchant_category"),

            # Investigation outcome
            "verdict": investigation["verdict"],
            "red_flags": investigation["red_flags"],
        }
        results.append(enriched)

    return results