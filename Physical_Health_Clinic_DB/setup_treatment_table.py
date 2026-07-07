from database import connect_db

def create_treatment_table():
    """Create the Treatment table in the database."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Create Treatment table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS Treatment (
            TreatmentID INT AUTO_INCREMENT PRIMARY KEY,
            TreatmentName VARCHAR(255) NOT NULL,
            Dosage VARCHAR(255) NOT NULL,
            Duration VARCHAR(255) NOT NULL,
            PatientID INT NOT NULL,
            WorkerID INT NOT NULL,
            FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
            FOREIGN KEY (WorkerID) REFERENCES Health_Workers(WorkerID)
        )
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        
        print("✅ Treatment table created successfully!")
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating Treatment table: {e}")

if __name__ == "__main__":
    create_treatment_table()
