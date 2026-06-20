import pymysql
import json
import os
from pymongo import MongoClient

# MySQL connection settings
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "root")
MYSQL_DB = os.environ.get("MYSQL_DB", "smartbank_backup")

# MongoDB connection settings (for full sync)
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

def get_connection():
    try:
        # First connect without specifying DB to ensure it exists
        conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD)
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}")
        conn.close()

        # Return connection to the specific DB
        return pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print(f"⚠️ MySQL connection error: {e}")
        return None

def init_db():
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    acc_no VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255),
                    age INT,
                    income DOUBLE,
                    account_type VARCHAR(255),
                    location VARCHAR(255),
                    pass VARCHAR(255),
                    balance DOUBLE,
                    created_at VARCHAR(255)
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    acc_no VARCHAR(255),
                    date VARCHAR(255),
                    type VARCHAR(255),
                    description TEXT,
                    amount DOUBLE,
                    balance DOUBLE
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    name VARCHAR(255) PRIMARY KEY,
                    face_enrolled TINYINT(1),
                    image_format VARCHAR(50),
                    image_width INT,
                    image_height INT,
                    image_size INT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS user_faces (
                    name VARCHAR(255) PRIMARY KEY,
                    face_image LONGTEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS logins (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    account_number VARCHAR(255),
                    username VARCHAR(255),
                    login_time VARCHAR(255)
                )
            """)
            try:
                c.execute("ALTER TABLE logins ADD COLUMN account_number VARCHAR(255)")
            except Exception:
                pass
            c.execute("""
                CREATE TABLE IF NOT EXISTS verification_failures (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    account_number VARCHAR(255),
                    action VARCHAR(255),
                    attempt INT,
                    reason TEXT,
                    timestamp VARCHAR(255)
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS complaints (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255),
                    email VARCHAR(255),
                    contact_number VARCHAR(255),
                    comments TEXT,
                    timestamp VARCHAR(255)
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    ref_id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255),
                    type VARCHAR(255),
                    amount DOUBLE,
                    tenure DOUBLE,
                    email VARCHAR(255),
                    phone VARCHAR(255),
                    opt_in TINYINT(1),
                    timestamp VARCHAR(255)
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS notification_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ref_id VARCHAR(255),
                    recipient VARCHAR(255),
                    channel VARCHAR(50),
                    status VARCHAR(50),
                    message TEXT,
                    html_body LONGTEXT,
                    timestamp VARCHAR(255)
                )
            """)
        conn.commit()
        print("✅ MySQL backup database initialized successfully.")
    except Exception as e:
        print(f"⚠️ MySQL init_db error: {e}")
    finally:
        conn.close()

def sync_account(doc):
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as c:
            sql = """
                REPLACE INTO accounts 
                (acc_no, name, age, income, account_type, location, pass, balance, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            acc_no_str = str(doc.get("acc_no", ""))
            c.execute(sql, (
                acc_no_str,
                doc.get("name", ""),
                doc.get("age", 0),
                float(doc.get("income", 0.0)),
                doc.get("account_type", ""),
                doc.get("location", ""),
                doc.get("pass", ""),
                float(doc.get("balance", 0.0)),
                doc.get("created_at", "")
            ))
            
            # Sync transactions
            c.execute("DELETE FROM transactions WHERE acc_no = %s", (acc_no_str,))
            for tx in doc.get("history", []):
                if isinstance(tx, dict):
                    c.execute("""
                        INSERT INTO transactions (acc_no, date, type, description, amount, balance)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        acc_no_str,
                        tx.get("date", ""),
                        tx.get("type", ""),
                        tx.get("description", ""),
                        float(tx.get("amount") or 0.0),
                        float(tx.get("balance") or 0.0)
                    ))
                else:
                    c.execute("INSERT INTO transactions (acc_no, description) VALUES (%s, %s)", (acc_no_str, str(tx)))
        conn.commit()
    except Exception as e:
        print(f"⚠️ MySQL sync_account error: {e}")
    finally:
        conn.close()

def delete_account(acc_no):
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as c:
            c.execute("DELETE FROM accounts WHERE acc_no = %s", (str(acc_no),))
            c.execute("DELETE FROM transactions WHERE acc_no = %s", (str(acc_no),))
        conn.commit()
    except Exception as e:
        print(f"⚠️ MySQL delete_account error: {e}")
    finally:
        conn.close()

def sync_user(doc):
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as c:
            sql = """
                REPLACE INTO users 
                (name, face_enrolled, image_format, image_width, image_height, image_size)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            user_name = doc.get("name", "")
            c.execute(sql, (
                user_name,
                1 if doc.get("face_enrolled") else 0,
                doc.get("image_format", ""),
                doc.get("image_width", 0),
                doc.get("image_height", 0),
                doc.get("image_size", 0)
            ))
            
            if doc.get("face_image"):
                c.execute("REPLACE INTO user_faces (name, face_image) VALUES (%s, %s)", (user_name, doc.get("face_image", "")))
        conn.commit()
    except Exception as e:
        print(f"⚠️ MySQL sync_user error: {e}")
    finally:
        conn.close()

def delete_user(name):
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as c:
            c.execute("DELETE FROM users WHERE name = %s", (name,))
            c.execute("DELETE FROM user_faces WHERE name = %s", (name,))
        conn.commit()
    except Exception as e:
        print(f"⚠️ MySQL delete_user error: {e}")
    finally:
        conn.close()

def add_login(username, login_time, account_number=None):
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as c:
            c.execute("INSERT INTO logins (username, login_time, account_number) VALUES (%s, %s, %s)", (username, login_time, account_number))
        conn.commit()
    except Exception as e:
        print(f"⚠️ MySQL add_login error: {e}")
    finally:
        conn.close()

def add_verification_failure(acc_no, action, attempt, reason, timestamp):
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as c:
            c.execute("""
                INSERT INTO verification_failures (account_number, action, attempt, reason, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, (str(acc_no), action, attempt, reason, timestamp))
        conn.commit()
    except Exception as e:
        print(f"⚠️ MySQL add_verification_failure error: {e}")
    finally:
        conn.close()

def add_complaint(name, email, contact, comments, timestamp):
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as c:
            c.execute("""
                INSERT INTO complaints (name, email, contact_number, comments, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, email, contact, comments, timestamp))
        conn.commit()
    except Exception as e:
        print(f"⚠️ MySQL add_complaint error: {e}")
    finally:
        conn.close()

def sync_all_mongo_to_sqlite():
    """Reads all data from MongoDB and bulk populates MySQL backup DB on startup."""
    conn = get_connection()
    if not conn:
        print("⚠️ Skipping MySQL full sync (database not accessible).")
        return
    
    try:
        client = MongoClient(MONGO_URI)
        db = client["smartbank"]
        
        print("🔄 Starting full MongoDB to MySQL sync...")
        with conn.cursor() as c:
            # Sync Accounts
            for doc in db["accounts"].find():
                acc_no_str = str(doc.get("acc_no", ""))
                c.execute("""
                    REPLACE INTO accounts 
                    (acc_no, name, age, income, account_type, location, pass, balance, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    acc_no_str, doc.get("name", ""), doc.get("age", 0), float(doc.get("income", 0.0)),
                    doc.get("account_type", ""), doc.get("location", ""), doc.get("pass", ""), float(doc.get("balance", 0.0)),
                    doc.get("created_at", "")
                ))
                
                c.execute("DELETE FROM transactions WHERE acc_no = %s", (acc_no_str,))
                for tx in doc.get("history", []):
                    if isinstance(tx, dict):
                        c.execute("""
                            INSERT INTO transactions (acc_no, date, type, description, amount, balance)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            acc_no_str, tx.get("date", ""), tx.get("type", ""), tx.get("description", ""),
                            float(tx.get("amount") or 0.0), float(tx.get("balance") or 0.0)
                        ))
                    else:
                        c.execute("INSERT INTO transactions (acc_no, description) VALUES (%s, %s)", (acc_no_str, str(tx)))
            
            # Sync Users (faces)
            for doc in db["users"].find():
                user_name = doc.get("name", "")
                c.execute("""
                    REPLACE INTO users 
                    (name, face_enrolled, image_format, image_width, image_height, image_size)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    user_name, 1 if doc.get("face_enrolled") else 0,
                    doc.get("image_format", ""), doc.get("image_width", 0), doc.get("image_height", 0), doc.get("image_size", 0)
                ))
                if doc.get("face_image"):
                    c.execute("REPLACE INTO user_faces (name, face_image) VALUES (%s, %s)", (user_name, doc.get("face_image", "")))
            
            # Sync Logins
            c.execute("DELETE FROM logins")
            for doc in db["logins"].find():
                c.execute("INSERT INTO logins (username, login_time, account_number) VALUES (%s, %s, %s)", 
                          (doc.get("username", ""), doc.get("login_time", ""), doc.get("account_number", "")))
            
            # Sync Verification Failures
            c.execute("DELETE FROM verification_failures")
            for doc in db["verification_failures"].find():
                c.execute("""
                    INSERT INTO verification_failures (account_number, action, attempt, reason, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    str(doc.get("account_number", "")), doc.get("action", ""), doc.get("attempt", 0),
                    doc.get("reason", ""), doc.get("timestamp", "")
                ))
                
            # Sync Complaints
            c.execute("DELETE FROM complaints")
            for doc in db["complaints"].find():
                c.execute("""
                    INSERT INTO complaints (name, email, contact_number, comments, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    doc.get("name", ""), doc.get("email", ""), doc.get("contact_number", ""),
                    doc.get("comments", ""), doc.get("timestamp", "")
                ))
                
            # Sync Applications
            c.execute("DELETE FROM applications")
            for doc in db["applications"].find():
                c.execute("""
                    INSERT INTO applications (ref_id, name, type, amount, tenure, email, phone, opt_in, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    doc.get("ref_id", ""), doc.get("name", ""), doc.get("type", ""),
                    float(doc.get("amount", 0.0)), float(doc.get("tenure", 0.0)),
                    doc.get("email", ""), doc.get("phone", ""),
                    1 if doc.get("opt_in") else 0, doc.get("timestamp", "")
                ))

            # Sync Notification Logs
            c.execute("DELETE FROM notification_logs")
            for doc in db["notification_logs"].find():
                c.execute("""
                    INSERT INTO notification_logs (ref_id, recipient, channel, status, message, html_body, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    doc.get("ref_id", ""), doc.get("recipient", ""), doc.get("channel", ""),
                    doc.get("status", ""), doc.get("message", ""), doc.get("html_body", ""),
                    doc.get("timestamp", "")
                ))

        conn.commit()
        print("✅ Full MongoDB to MySQL sync completed successfully!")
    except Exception as e:
        print(f"⚠️ MySQL full sync error: {e}")
    finally:
        conn.close()

def add_application(ref_id, name, app_type, amount, tenure, email, phone, opt_in, timestamp):
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as c:
            c.execute("""
                INSERT INTO applications (ref_id, name, type, amount, tenure, email, phone, opt_in, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (ref_id, name, app_type, float(amount), float(tenure), email, phone, 1 if opt_in else 0, timestamp))
        conn.commit()
    except Exception as e:
        print(f"⚠️ MySQL add_application error: {e}")
    finally:
        conn.close()

def add_notification_log(ref_id, recipient, channel, status, message, timestamp, html_body=""):
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as c:
            c.execute("""
                INSERT INTO notification_logs (ref_id, recipient, channel, status, message, html_body, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (ref_id, recipient, channel, status, message, html_body, timestamp))
        conn.commit()
    except Exception as e:
        print(f"⚠️ MySQL add_notification_log error: {e}")
    finally:
        conn.close()
