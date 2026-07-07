from database import connect_db

def check_patients_table():
    """Check if Patients table exists and show its structure."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Check if Patients table exists
        cursor.execute("SHOW TABLES LIKE 'Patients'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("📋 Patients table exists. Checking structure...")
            cursor.execute("DESCRIBE Patients")
            columns = cursor.fetchall()
            print("\nCurrent Patients table structure:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
            
            # Check if there are any patients
            cursor.execute("SELECT COUNT(*) FROM Patients")
            count = cursor.fetchone()[0]
            print(f"\n👥 Total patients in table: {count}")
            
            if count > 0:
                cursor.execute("SELECT PatientID, FirstName, LastName FROM Patients LIMIT 5")
                patients = cursor.fetchall()
                print("\nSample patients:")
                for p in patients:
                    print(f"  - {p[0]} - {p[1]} {p[2]}")
        else:
            print("❌ Patients table does not exist!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_patients_table()
