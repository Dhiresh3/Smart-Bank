"""
Shows everything stored in MongoDB Atlas:
- All accounts (name, acc_no, balance, face_enrolled, transaction history)
- All logins
- All face data in users collection
"""
import os
import base64
import json
from pymongo import MongoClient

# Try to load .env manually
MONGO_URI = None
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("MONGO_URI="):
                MONGO_URI = line.split("=", 1)[1].strip()

if not MONGO_URI:
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

print(f"\n📡 Connecting to: {MONGO_URI[:60]}...\n")

client = MongoClient(MONGO_URI)
db = client["smartbank"]

# ── 1. Accounts ──────────────────────────────────────────────────
accounts_col = db["accounts"]
accounts = list(accounts_col.find())
print(f"{'='*60}")
print(f"📦 ACCOUNTS COLLECTION — {len(accounts)} record(s)")
print(f"{'='*60}")
for acc in accounts:
    face_stored = "✅ YES" if acc.get("face_image") else "❌ NO"
    enrolled    = "✅ YES" if acc.get("face_enrolled") else "❌ NO"
    history     = acc.get("history", [])
    print(f"\n  👤 Name      : {acc.get('name', 'N/A')}")
    print(f"     Acc No    : {acc.get('acc_no', 'N/A')}")
    print(f"     Balance   : ₹{acc.get('balance', 0)}")
    print(f"     Type      : {acc.get('account_type', 'N/A')}")
    print(f"     Age       : {acc.get('age', 'N/A')}")
    print(f"     Income    : ₹{acc.get('income', 'N/A')}")
    print(f"     Created   : {acc.get('created_at', 'N/A')}")
    print(f"     Face Img  : {face_stored}")
    print(f"     Enrolled  : {enrolled}")
    print(f"     Tx Count  : {len(history)} transaction(s)")
    if history:
        for tx in history[-3:]:  # Show last 3 transactions
            if isinstance(tx, dict):
                print(f"       └─ [{tx.get('date','?')}] {tx.get('type','?')} ₹{tx.get('amount','?')} → Bal ₹{tx.get('balance','?')}")
            else:
                print(f"       └─ {tx}")

# ── 2. Users (face auth) ─────────────────────────────────────────
users_col = db["users"]
users = list(users_col.find())
print(f"\n{'='*60}")
print(f"🔐 USERS (FACE AUTH) COLLECTION — {len(users)} record(s)")
print(f"{'='*60}")
for u in users:
    face_stored = "✅ YES" if u.get("face_image") else "❌ NO"
    img_size = len(u.get("face_image", "")) if u.get("face_image") else 0
    print(f"\n  👤 Name        : {u.get('name', 'N/A')}")
    print(f"     Face Enrolled: {'✅' if u.get('face_enrolled') else '❌'}")
    print(f"     Face Stored  : {face_stored}")
    print(f"     Image Size   : {img_size:,} chars (base64)")
    # Save face image if present
    if u.get("face_image"):
        try:
            b64 = u["face_image"]
            if "," in b64:
                b64 = b64.split(",", 1)[1]
            img_data = base64.b64decode(b64)
            fname = f"face_{u.get('name','unknown').replace(' ','_')}.jpg"
            with open(fname, "wb") as f:
                f.write(img_data)
            print(f"     💾 Saved to  : {fname}")
        except Exception as e:
            print(f"     ⚠️ Could not save image: {e}")

# ── 3. Logins ────────────────────────────────────────────────────
logins_col = db["logins"]
logins = list(logins_col.find().sort("login_time", -1).limit(10))
print(f"\n{'='*60}")
print(f"🔑 LOGINS COLLECTION — last {len(logins)} login(s)")
print(f"{'='*60}")
for lg in logins:
    print(f"  [{lg.get('login_time','?')}] {lg.get('username','?')}")

print(f"\n{'='*60}")
print("✅ Done! All data shown above.")
print(f"{'='*60}\n")
