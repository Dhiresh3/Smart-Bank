import pymysql
import json
import os
from pymongo import MongoClient

# MySQL connection settings
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_USER = os.environ.get("MYSQL_USER", "system")
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
                    history TEXT,
                    created_at VARCHAR(255)
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    name VARCHAR(255) PRIMARY KEY,
                    face_enrolled TINYINT(1),
                    face_image LONGTEXT,
                    image_format VARCHAR(50),
                    image_width INT,
                    image_height INT,
                    image_size INT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS logins (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255),
                    login_time VARCHAR(255)
                )
            """)
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
            history_str = json.dumps(doc.get("history", []))
            sql = """
                REPLACE INTO accounts 
                (acc_no, name, age, income, account_type, location, pass, balance, history, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            c.execute(sql, (
                str(doc.get("acc_no", "")),
                doc.get("name", ""),
                doc.get("age", 0),
                float(doc.get("income", 0.0)),
                doc.get("account_type", ""),
                doc.get("location", ""),
                doc.get("pass", ""),
                float(doc.get("balance", 0.0)),
                history_str,
                doc.get("created_at", "")
            ))
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
                (name, face_enrolled, face_image, image_format, image_width, image_height, image_size)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            c.execute(sql, (
                doc.get("name", ""),
                1 if doc.get("face_enrolled") else 0,
                doc.get("face_image", ""),
                doc.get("image_format", ""),
                doc.get("image_width", 0),
                doc.get("image_height", 0),
                doc.get("image_size", 0)
            ))
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
        conn.commit()
    except Exception as e:
        print(f"⚠️ MySQL delete_user error: {e}")
    finally:
        conn.close()

def add_login(username, login_time):
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as c:
            c.execute("INSERT INTO logins (username, login_time) VALUES (%s, %s)", (username, login_time))
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
                history_str = json.dumps(doc.get("history", []))
                c.execute("""
                    REPLACE INTO accounts 
                    (acc_no, name, age, income, account_type, location, pass, balance, history, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(doc.get("acc_no", "")), doc.get("name", ""), doc.get("age", 0), float(doc.get("income", 0.0)),
                    doc.get("account_type", ""), doc.get("location", ""), doc.get("pass", ""), float(doc.get("balance", 0.0)),
                    history_str, doc.get("created_at", "")
                ))
            
            # Sync Users (faces)
            for doc in db["users"].find():
                c.execute("""
                    REPLACE INTO users 
                    (name, face_enrolled, face_image, image_format, image_width, image_height, image_size)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    doc.get("name", ""), 1 if doc.get("face_enrolled") else 0, doc.get("face_image", ""),
                    doc.get("image_format", ""), doc.get("image_width", 0), doc.get("image_height", 0), doc.get("image_size", 0)
                ))
            
            # Sync Logins
            c.execute("DELETE FROM logins")
            for doc in db["logins"].find():
                c.execute("INSERT INTO logins (username, login_time) VALUES (%s, %s)", 
                          (doc.get("username", ""), doc.get("login_time", "")))
            
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
                
        conn.commit()
        print("✅ Full MongoDB to MySQL sync completed successfully!")
    except Exception as e:
        print(f"⚠️ MySQL full sync error: {e}")
    finally:
        conn.close()
