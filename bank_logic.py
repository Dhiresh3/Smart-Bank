import os
import random
from datetime import datetime
from pymongo import MongoClient

# MongoDB connection — uses MONGO_URI env var for deployment, falls back to localhost
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["smartbank"]
accounts_col = db["accounts"]


def load_data():
    """Load all accounts as a dict keyed by acc_no (backwards-compatible)."""
    result = {}
    for doc in accounts_col.find():
        acc_no = doc["acc_no"]
        # Remove MongoDB's internal _id and acc_no from the value dict
        entry = {k: v for k, v in doc.items() if k not in ("_id", "acc_no")}
        result[acc_no] = entry
    return result


def save_data(data):
    """
    Bulk-write all accounts from a dict (backwards-compatible helper).
    Replaces the entire collection with the provided dict.
    """
    for acc_no, details in data.items():
        doc = {"acc_no": acc_no, **details}
        accounts_col.replace_one({"acc_no": acc_no}, doc, upsert=True)


def generate_account_number():
    """Generate a unique 7-8 digit account number"""
    while True:
        num_digits = random.choice([7, 8])
        acc_no = str(random.randint(10**(num_digits-1), 10**num_digits - 1))
        if accounts_col.find_one({"acc_no": acc_no}) is None:
            return acc_no


def create_account(data):
    if "acc_no" in data and data["acc_no"]:
        acc_no = str(data["acc_no"])
    else:
        acc_no = generate_account_number()

    doc = {
        "acc_no": acc_no,
        "name": data["name"],
        "age": data.get("age", 18),
        "income": data.get("income", 0),
        "account_type": data.get("account_type", "Savings"),
        "location": data.get("location", ""),
        "pass": data["pass"],
        "balance": 0.0,
        "history": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    accounts_col.replace_one({"acc_no": acc_no}, doc, upsert=True)
    return {
        "status": "success",
        "message": f"Account created successfully for {data['name']}",
        "account_number": acc_no
    }


def deposit(data):
    acc_no = str(data["acc_no"])
    account = accounts_col.find_one({"acc_no": acc_no})

    if account and account["pass"] == data["pass"]:
        amount = float(data["amount"])

        # Per-transaction limit: ₹5,00,000
        if amount > 500000:
            return {
                "status": "fail",
                "message": "Deposit limit is ₹5,00,000 per transaction."
            }

        # Daily deposit count limit: max 5 successful deposits per day
        today = datetime.now().date()
        history = account.get("history", [])
        deposits_today = 0
        for h in history:
            if not isinstance(h, dict):
                continue
            h_date_str = h.get("date") or h.get("timestamp")
            if not h_date_str:
                continue
            try:
                h_date = datetime.fromisoformat(h_date_str).date() if "T" in h_date_str else datetime.strptime(
                    h_date_str, "%Y-%m-%d %H:%M:%S"
                ).date()
            except Exception:
                continue

            h_type = (h.get("type") or "").lower()
            h_desc = (h.get("description") or "").lower()
            is_deposit = (
                h_type in ("credit", "deposit")
                or "deposit" in h_desc
                or "credited" in h_desc
            )
            if h_date == today and is_deposit:
                deposits_today += 1

        if deposits_today >= 5:
            return {
                "status": "fail",
                "message": "Daily deposit limit reached (5 deposits per day)."
            }

        new_balance = account["balance"] + amount
        now = datetime.now()
        tx_entry = {
            "date": now.strftime("%Y-%m-%d %H:%M:%S"),
            "type": "Credit",
            "description": "Deposit",
            "amount": amount,
            "balance": new_balance,
        }

        accounts_col.update_one(
            {"acc_no": acc_no},
            {
                "$set": {"balance": new_balance},
                "$push": {"history": tx_entry}
            }
        )
        return {"status": "success", "message": f"₹{amount} deposited successfully"}
    return {"status": "fail", "message": "Invalid credentials"}


def withdraw(data):
    acc_no = str(data["acc_no"])
    account = accounts_col.find_one({"acc_no": acc_no})

    if account and account["pass"] == data["pass"]:
        amount = float(data["amount"])
        if account["balance"] >= amount:
            new_balance = account["balance"] - amount
            now = datetime.now()
            tx_entry = {
                "date": now.strftime("%Y-%m-%d %H:%M:%S"),
                "type": "Debit",
                "description": "Withdrawal",
                "amount": amount,
                "balance": new_balance,
            }

            accounts_col.update_one(
                {"acc_no": acc_no},
                {
                    "$set": {"balance": new_balance},
                    "$push": {"history": tx_entry}
                }
            )
            return {"status": "success", "message": f"₹{amount} withdrawn successfully"}
        return {"status": "fail", "message": "Insufficient balance"}
    return {"status": "fail", "message": "Invalid credentials"}


def check_balance(data):
    acc_no = str(data["acc_no"])
    account = accounts_col.find_one({"acc_no": acc_no})

    if account and account["pass"] == data["pass"]:
        balance = account["balance"]
        accounts_col.update_one(
            {"acc_no": acc_no},
            {"$push": {"history": "Checked balance"}}
        )
        return {
            "status": "success",
            "balance": balance,
            "message": f"Current balance: ₹{balance}"
        }
    return {"status": "fail", "message": "Invalid credentials"}


def close_account(data):
    acc_no = str(data["acc_no"])
    account = accounts_col.find_one({"acc_no": acc_no})

    if account and account["pass"] == data["pass"]:
        accounts_col.delete_one({"acc_no": acc_no})
        return {"status": "success", "message": f"Account {acc_no} closed successfully"}
    return {"status": "fail", "message": "Invalid credentials"}