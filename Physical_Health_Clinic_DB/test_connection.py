from database import connect_db

try:
    conn = connect_db()

    if conn.is_connected():
        print("Database Connected Successfully!")

    conn.close()

except Exception as e:
    print("Connection Failed")
    print(e)