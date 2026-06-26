import pymysql

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DB = "smartbank_backup"

def show_all_tables():
    print("🔄 Connecting to MySQL Backup Database...")
    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        print("✅ Successfully connected to MySQL!\n")
        
        tables = ["accounts", "users", "logins", "verification_failures", "complaints"]
        
        with conn.cursor() as cursor:
            for table in tables:
                print("=" * 40)
                print(f" 📂 TABLE: {table.upper()}")
                print("=" * 40)
                try:
                    cursor.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    if not rows:
                        print("  (No records found)\n")
                    else:
                        print(f"  Found {len(rows)} record(s):\n")
                        for row in rows:
                            clean_row = {}
                            for key, val in row.items():
                                # Truncate very long data like base64 face images for easy reading
                                if isinstance(val, str) and len(val) > 60:
                                    clean_row[key] = val[:60] + "... [truncated]"
                                else:
                                    clean_row[key] = val
                            print(f"  {clean_row}")
                        print("\n")
                except Exception as e:
                    print(f"  ⚠️ Could not read table {table} (it might not exist yet): {e}\n")
                    
        conn.close()
    except Exception as e:
        print(f"❌ Failed to connect to MySQL: {e}")
        print("\nMake sure:")
        print("1. XAMPP, WAMP, or your MySQL server is running.")
        print("2. A user 'system' with password 'root' exists in your MySQL server.")

if __name__ == "__main__":
    show_all_tables()
