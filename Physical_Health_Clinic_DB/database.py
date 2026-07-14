import mysql.connector

def connect_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="Alhaji",
        password="123456789",
        database="Pysical_Health_Clinic_DB"
    )
    return conn


def log_audit_action(user_id, action):
    """Automatically log user actions to the Audit_Log table."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Audit_Log (UserID, Action) VALUES (%s, %s)", (user_id, action))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[AUDIT LOG ERROR] Failed to write audit log: {e}")