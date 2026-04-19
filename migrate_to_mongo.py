"""
Migration script: Import existing JSON data into MongoDB.
Run this ONCE to seed your MongoDB database with existing accounts, users, and login records.

Usage:
    python migrate_to_mongo.py
"""

import json
import os
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["smartbank"]


def migrate_accounts():
    """Migrate accounts.json → MongoDB 'accounts' collection."""
    filepath = "accounts.json"
    if not os.path.exists(filepath):
        print("[SKIP] accounts.json not found, skipping.")
        return

    with open(filepath, "r") as f:
        data = json.load(f)

    col = db["accounts"]
    count = 0
    for acc_no, details in data.items():
        doc = {"acc_no": acc_no, **details}
        col.replace_one({"acc_no": acc_no}, doc, upsert=True)
        count += 1

    print(f"[OK] Migrated {count} accounts to MongoDB.")


def migrate_users():
    """Migrate users.json → MongoDB 'users' collection."""
    filepath = "users.json"
    if not os.path.exists(filepath):
        print("[SKIP] users.json not found, skipping.")
        return

    with open(filepath, "r") as f:
        data = json.load(f)

    col = db["users"]
    count = 0
    for name, details in data.items():
        doc = {"name": name, **details}
        col.replace_one({"name": name}, doc, upsert=True)
        count += 1

    print(f"[OK] Migrated {count} users to MongoDB.")


def migrate_logins():
    """Migrate login.json → MongoDB 'logins' collection."""
    filepath = "login.json"
    if not os.path.exists(filepath):
        print("[SKIP] login.json not found, skipping.")
        return

    with open(filepath, "r") as f:
        records = json.load(f)

    col = db["logins"]
    if records:
        col.insert_many(records)
        print(f"[OK] Migrated {len(records)} login records to MongoDB.")
    else:
        print("[SKIP] login.json is empty, nothing to migrate.")


if __name__ == "__main__":
    print("=" * 50)
    print("  SmartBank -- JSON to MongoDB Migration")
    print("=" * 50)
    print(f"Connecting to: {MONGO_URI}")
    print()

    migrate_accounts()
    migrate_users()
    migrate_logins()

    print()
    print("[DONE] Migration complete!")
    print("You can now run the app with: python Application.py")
