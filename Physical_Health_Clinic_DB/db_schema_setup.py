import mysql.connector
from database import connect_db

def run_setup():
    print("🚀 Starting Database Schema Setup & User Sync...")
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # 1. Add UsersID column to Health_Workers if it doesn't exist
        print("Checking Health_Workers columns...")
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = 'Health_Workers' 
              AND COLUMN_NAME = 'UsersID'
        """)
        if not cursor.fetchone():
            print("Adding UsersID column to Health_Workers table...")
            cursor.execute("ALTER TABLE Health_Workers ADD COLUMN UsersID INT DEFAULT NULL")
            conn.commit()

        # 2. Check if foreign key exists, if not add it
        print("Checking foreign key constraint for Health_Workers...")
        cursor.execute("""
            SELECT CONSTRAINT_NAME 
            FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS 
            WHERE CONSTRAINT_SCHEMA = DATABASE() 
              AND TABLE_NAME = 'Health_Workers' 
              AND CONSTRAINT_NAME = 'fk_healthworker_user'
        """)
        if not cursor.fetchone():
            print("Adding fk_healthworker_user foreign key constraint to Health_Workers...")
            try:
                cursor.execute("""
                    ALTER TABLE Health_Workers 
                    ADD CONSTRAINT fk_healthworker_user 
                    FOREIGN KEY (UsersID) REFERENCES Users(UsersID) 
                    ON DELETE SET NULL ON UPDATE CASCADE
                """)
                conn.commit()
            except Exception as fk_err:
                print(f"Warning adding constraint (it might already exist): {fk_err}")

        # 3. Add DispensedStatus column to Treatment if it doesn't exist
        print("Checking Treatment columns...")
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = 'Treatment' 
              AND COLUMN_NAME = 'DispensedStatus'
        """)
        if not cursor.fetchone():
            print("Adding DispensedStatus column to Treatment table...")
            cursor.execute("ALTER TABLE Treatment ADD COLUMN DispensedStatus VARCHAR(50) DEFAULT 'Pending'")
            conn.commit()

        # 4. Sync Users and Health_Workers
        print("Syncing Users and Health_Workers records...")
        cursor.execute("SELECT UsersID, FullName, Role, Phone, Gender FROM Users")
        users = cursor.fetchall()

        for user_id, full_name, role, phone, gender in users:
            # Check if this user is already linked in Health_Workers
            cursor.execute("SELECT WorkerID FROM Health_Workers WHERE UsersID = %s", (user_id,))
            linked_worker = cursor.fetchone()

            if linked_worker:
                print(f"  - User '{full_name}' (ID {user_id}) is already linked to Worker ID {linked_worker[0]}.")
                continue

            # Check if there is an unlinked worker with the same name
            cursor.execute("SELECT WorkerID FROM Health_Workers WHERE FullName = %s AND UsersID IS NULL", (full_name,))
            unlinked_worker = cursor.fetchone()

            if unlinked_worker:
                worker_id = unlinked_worker[0]
                print(f"  - Linking existing worker '{full_name}' (Worker ID {worker_id}) to User ID {user_id}...")
                cursor.execute("UPDATE Health_Workers SET UsersID = %s WHERE WorkerID = %s", (user_id, worker_id))
                conn.commit()
                continue

            # Otherwise, create a new Health Worker record for this User
            print(f"  - Creating missing Health Worker record for User '{full_name}' (ID {user_id})...")
            
            # Generate a unique phone number since it's UNIQUE and NOT NULL
            worker_phone = phone if phone else f"+232-00-{user_id:06d}"
            # Ensure the phone number doesn't already exist
            cursor.execute("SELECT WorkerID FROM Health_Workers WHERE PhoneNumber = %s", (worker_phone,))
            if cursor.fetchone():
                worker_phone = f"+232-99-{user_id:06d}" # Alternative dummy phone

            worker_gender = gender if gender in ['Male', 'Female'] else 'Male'
            worker_role = role if role else 'Staff'

            cursor.execute("""
                INSERT INTO Health_Workers (UsersID, FullName, Gender, PhoneNumber, Address, Role)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, full_name, worker_gender, worker_phone, 'Clinic Staff', worker_role))
            conn.commit()
            new_worker_id = cursor.lastrowid
            print(f"    Created Worker ID {new_worker_id} for User ID {user_id}.")

        conn.close()
        print("✅ Database Schema Setup & Sync Complete!")
    except Exception as e:
        print(f"❌ Error during database setup: {e}")

if __name__ == "__main__":
    run_setup()
