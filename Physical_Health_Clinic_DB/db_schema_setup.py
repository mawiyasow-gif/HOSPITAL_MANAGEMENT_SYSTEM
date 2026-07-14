import mysql.connector
import hashlib
from database import connect_db

def hash_pass(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def run_setup():
    print("🚀 Starting Database Schema Setup & Seeding...")
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Disable foreign key checks to safely drop tables
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        # Drop existing tables
        tables_to_drop = [
            "Receipt", "Receipts",
            "Payment", "Payments",
            "Medicine_Dispensing",
            "Prescription",
            "Treatment",
            "Diagnosis",
            "Laboratory_Results",
            "Laboratory_Requests",
            "Laboratory_Tests",
            "Hospital_Services",
            "Appointments",
            "Patients",
            "Inventory",
            "Health_Workers",
            "Audit_Log",
            "Users"
        ]
        for table in tables_to_drop:
            print(f"Dropping table if exists: {table}...")
            cursor.execute(f"DROP TABLE IF EXISTS `{table}`")

        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()

        # 1. Create Users Table
        print("Creating Users table...")
        cursor.execute("""
            CREATE TABLE Users (
                UsersID INT AUTO_INCREMENT PRIMARY KEY,
                FullName VARCHAR(100) NOT NULL,
                Username VARCHAR(50) NOT NULL UNIQUE,
                Password VARCHAR(255) NOT NULL,
                Role ENUM('Administrator', 'Receptionist', 'Doctor', 'Laboratory Technician', 'Pharmacist', 'Accountant') NOT NULL,
                Email VARCHAR(100),
                Phone VARCHAR(20),
                Gender VARCHAR(20),
                Status ENUM('Active', 'Inactive') DEFAULT 'Active',
                LastLogin DATETIME DEFAULT NULL,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Create Health_Workers Table
        print("Creating Health_Workers table...")
        cursor.execute("""
            CREATE TABLE Health_Workers (
                WorkerID INT AUTO_INCREMENT PRIMARY KEY,
                UsersID INT UNIQUE,
                FullName VARCHAR(100) NOT NULL,
                Gender VARCHAR(20),
                PhoneNumber VARCHAR(20),
                Address VARCHAR(150),
                Role VARCHAR(50) NOT NULL,
                FOREIGN KEY (UsersID) REFERENCES Users(UsersID) ON DELETE CASCADE
            )
        """)

        # 3. Create Patients Table
        print("Creating Patients table...")
        cursor.execute("""
            CREATE TABLE Patients (
                PatientID INT AUTO_INCREMENT PRIMARY KEY,
                FullName VARCHAR(100) NOT NULL,
                DateOfBirth DATE NOT NULL,
                Gender VARCHAR(20) NOT NULL,
                PhoneNumber VARCHAR(20),
                Address VARCHAR(150),
                BloodGroup VARCHAR(5),
                RegistrationDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 4. Create Appointments Table
        print("Creating Appointments table...")
        cursor.execute("""
            CREATE TABLE Appointments (
                AppointmentID INT AUTO_INCREMENT PRIMARY KEY,
                PatientID INT NOT NULL,
                WorkerID INT NOT NULL,
                AppointmentDate DATE NOT NULL,
                AppointmentTime TIME NOT NULL,
                Status ENUM('Pending', 'Completed', 'Cancelled', 'Scheduled') DEFAULT 'Pending',
                FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE,
                FOREIGN KEY (WorkerID) REFERENCES Health_Workers(WorkerID) ON DELETE CASCADE
            )
        """)

        # 5. Create Hospital_Services Table
        print("Creating Hospital_Services table...")
        cursor.execute("""
            CREATE TABLE Hospital_Services (
                ServiceID INT AUTO_INCREMENT PRIMARY KEY,
                ServiceName VARCHAR(100) NOT NULL UNIQUE,
                Price DECIMAL(10, 2) NOT NULL
            )
        """)

        # 6. Create Laboratory_Tests Table
        print("Creating Laboratory_Tests table...")
        cursor.execute("""
            CREATE TABLE Laboratory_Tests (
                TestID INT AUTO_INCREMENT PRIMARY KEY,
                TestName VARCHAR(100) NOT NULL UNIQUE,
                Price DECIMAL(10, 2) NOT NULL
            )
        """)

        # 7. Create Laboratory_Requests Table
        print("Creating Laboratory_Requests table...")
        cursor.execute("""
            CREATE TABLE Laboratory_Requests (
                RequestID INT AUTO_INCREMENT PRIMARY KEY,
                PatientID INT NOT NULL,
                DoctorID INT NOT NULL,
                AppointmentID INT,
                RequestDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                Status ENUM('Pending', 'Completed') DEFAULT 'Pending',
                FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE,
                FOREIGN KEY (DoctorID) REFERENCES Health_Workers(WorkerID) ON DELETE CASCADE,
                FOREIGN KEY (AppointmentID) REFERENCES Appointments(AppointmentID) ON DELETE SET NULL
            )
        """)

        # 8. Create Laboratory_Results Table
        print("Creating Laboratory_Results table...")
        cursor.execute("""
            CREATE TABLE Laboratory_Results (
                ResultID INT AUTO_INCREMENT PRIMARY KEY,
                RequestID INT NOT NULL,
                TestID INT NOT NULL,
                ResultDetails TEXT,
                TestDate TIMESTAMP NULL DEFAULT NULL,
                TechnicianID INT,
                FOREIGN KEY (RequestID) REFERENCES Laboratory_Requests(RequestID) ON DELETE CASCADE,
                FOREIGN KEY (TestID) REFERENCES Laboratory_Tests(TestID) ON DELETE CASCADE,
                FOREIGN KEY (TechnicianID) REFERENCES Health_Workers(WorkerID) ON DELETE SET NULL
            )
        """)

        # 9. Create Diagnosis Table
        print("Creating Diagnosis table...")
        cursor.execute("""
            CREATE TABLE Diagnosis (
                DiagnosisID INT AUTO_INCREMENT PRIMARY KEY,
                AppointmentID INT,
                PatientID INT NOT NULL,
                DoctorID INT NOT NULL,
                DiagnosisDetails TEXT NOT NULL,
                DiagnosisDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                LabRequestID INT,
                FOREIGN KEY (AppointmentID) REFERENCES Appointments(AppointmentID) ON DELETE SET NULL,
                FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE,
                FOREIGN KEY (DoctorID) REFERENCES Health_Workers(WorkerID) ON DELETE CASCADE,
                FOREIGN KEY (LabRequestID) REFERENCES Laboratory_Requests(RequestID) ON DELETE SET NULL
            )
        """)

        # 10. Create Treatment Table
        print("Creating Treatment table...")
        cursor.execute("""
            CREATE TABLE Treatment (
                TreatmentID INT AUTO_INCREMENT PRIMARY KEY,
                DiagnosisID INT NOT NULL,
                PatientID INT NOT NULL,
                DoctorID INT NOT NULL,
                TreatmentDetails TEXT NOT NULL,
                StartDate DATE NOT NULL,
                EndDate DATE NOT NULL,
                Status VARCHAR(50) DEFAULT 'Active',
                FOREIGN KEY (DiagnosisID) REFERENCES Diagnosis(DiagnosisID) ON DELETE CASCADE,
                FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE,
                FOREIGN KEY (DoctorID) REFERENCES Health_Workers(WorkerID) ON DELETE CASCADE
            )
        """)

        # 11. Create Inventory Table
        print("Creating Inventory table...")
        cursor.execute("""
            CREATE TABLE Inventory (
                InventoryID INT AUTO_INCREMENT PRIMARY KEY,
                MedicineName VARCHAR(100) NOT NULL UNIQUE,
                BatchNumber VARCHAR(50) NOT NULL,
                Quantity INT NOT NULL,
                CostPrice DECIMAL(10, 2) NOT NULL,
                SellingPrice DECIMAL(10, 2) NOT NULL,
                ExpiryDate DATE NOT NULL,
                Supplier VARCHAR(100)
            )
        """)

        # 12. Create Prescription Table
        print("Creating Prescription table...")
        cursor.execute("""
            CREATE TABLE Prescription (
                PrescriptionID INT AUTO_INCREMENT PRIMARY KEY,
                TreatmentID INT NOT NULL,
                PatientID INT NOT NULL,
                DoctorID INT NOT NULL,
                MedicineName VARCHAR(100) NOT NULL,
                Dosage VARCHAR(100) NOT NULL,
                QuantityPrescribed INT NOT NULL,
                Status ENUM('Pending', 'Dispensed') DEFAULT 'Pending',
                DatePrescribed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (TreatmentID) REFERENCES Treatment(TreatmentID) ON DELETE CASCADE,
                FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE,
                FOREIGN KEY (DoctorID) REFERENCES Health_Workers(WorkerID) ON DELETE CASCADE
            )
        """)

        # 13. Create Medicine_Dispensing Table
        print("Creating Medicine_Dispensing table...")
        cursor.execute("""
            CREATE TABLE Medicine_Dispensing (
                DispensingID INT AUTO_INCREMENT PRIMARY KEY,
                PrescriptionID INT NOT NULL,
                InventoryID INT NOT NULL,
                QuantityDispensed INT NOT NULL,
                DispensedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PharmacistID INT NOT NULL,
                FOREIGN KEY (PrescriptionID) REFERENCES Prescription(PrescriptionID) ON DELETE CASCADE,
                FOREIGN KEY (InventoryID) REFERENCES Inventory(InventoryID) ON DELETE CASCADE,
                FOREIGN KEY (PharmacistID) REFERENCES Health_Workers(WorkerID) ON DELETE CASCADE
            )
        """)

        # 14. Create Payment Table
        print("Creating Payment table...")
        cursor.execute("""
            CREATE TABLE Payment (
                PaymentID INT AUTO_INCREMENT PRIMARY KEY,
                PatientID INT NOT NULL,
                Amount DECIMAL(10, 2) NOT NULL,
                PaymentType ENUM('Registration', 'Consultation', 'Laboratory', 'Medicines') NOT NULL,
                ServiceID INT,
                LabRequestID INT,
                DispensingID INT,
                PaymentMethod VARCHAR(50) NOT NULL,
                PaymentDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                BilledBy INT,
                FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE,
                FOREIGN KEY (ServiceID) REFERENCES Hospital_Services(ServiceID) ON DELETE SET NULL,
                FOREIGN KEY (LabRequestID) REFERENCES Laboratory_Requests(RequestID) ON DELETE SET NULL,
                FOREIGN KEY (DispensingID) REFERENCES Medicine_Dispensing(DispensingID) ON DELETE SET NULL,
                FOREIGN KEY (BilledBy) REFERENCES Health_Workers(WorkerID) ON DELETE SET NULL
            )
        """)

        # 15. Create Receipt Table
        print("Creating Receipt table...")
        cursor.execute("""
            CREATE TABLE Receipt (
                ReceiptID INT AUTO_INCREMENT PRIMARY KEY,
                PaymentID INT NOT NULL,
                IssueDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PrintedBy INT,
                FOREIGN KEY (PaymentID) REFERENCES Payment(PaymentID) ON DELETE CASCADE,
                FOREIGN KEY (PrintedBy) REFERENCES Health_Workers(WorkerID) ON DELETE SET NULL
            )
        """)

        # 16. Create Audit_Log Table
        print("Creating Audit_Log table...")
        cursor.execute("""
            CREATE TABLE Audit_Log (
                LogID INT AUTO_INCREMENT PRIMARY KEY,
                UserID INT NOT NULL,
                Action TEXT NOT NULL,
                ActionDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (UserID) REFERENCES Users(UsersID) ON DELETE CASCADE
            )
        """)

        conn.commit()
        print("Tables created successfully. Seeding initial data...")

        # --- SEEDING DATA ---

        # Seed Users
        users_data = [
            ("Admin Staff", "admin", "admin123", "Administrator", "admin@clinic.com", "+232-76-000001", "Male"),
            ("Dr. Alhaji Mawiya Sow", "doctor", "doctor123", "Doctor", "doctor_sow@clinic.com", "+232-76-987654", "Male"),
            ("Receptionist Staff", "receptionist", "receptionist123", "Receptionist", "receptionist@clinic.com", "+232-76-000002", "Female"),
            ("Laboratory Technician Staff", "labtech", "labtech123", "Laboratory Technician", "labtech@clinic.com", "+232-76-000003", "Male"),
            ("Pharmacist Staff", "pharmacist", "pharmacist123", "Pharmacist", "pharmacist@clinic.com", "+232-76-000004", "Male"),
            ("Accountant Staff", "accountant", "accountant123", "Accountant", "accountant@clinic.com", "+232-76-000005", "Female")
        ]

        for full_name, username, password, role, email, phone, gender in users_data:
            cursor.execute("""
                INSERT INTO Users (FullName, Username, Password, Role, Email, Phone, Gender, Status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Active')
            """, (full_name, username, hash_pass(password), role, email, phone, gender))
            user_id = cursor.lastrowid
            
            # Create corresponding Health Worker
            cursor.execute("""
                INSERT INTO Health_Workers (UsersID, FullName, Gender, PhoneNumber, Address, Role)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, full_name, gender, phone, "Clinic Campus", role))

        # Seed Hospital Services
        services = [
            ("Registration", 50000.00),
            ("Consultation", 100000.00)
        ]
        for name, price in services:
            cursor.execute("INSERT INTO Hospital_Services (ServiceName, Price) VALUES (%s, %s)", (name, price))

        # Seed Laboratory Tests
        lab_tests = [
            ("Malaria Test", 30000.00),
            ("Blood Sugar", 40000.00),
            ("Urine Test", 20000.00),
            ("Stool Test", 20000.00),
            ("Full Blood Count", 80000.00)
        ]
        for name, price in lab_tests:
            cursor.execute("INSERT INTO Laboratory_Tests (TestName, Price) VALUES (%s, %s)", (name, price))

        # Seed Inventory
        medicines = [
            ("Paracetamol 500mg", "B-PA101", 500, 1000.00, 1500.00, "2027-12-31", "Sierra Pharm Ltd"),
            ("Amoxicillin 250mg", "B-AM202", 300, 3000.00, 5000.00, "2028-06-30", "GHC Supply"),
            ("Ciprofloxacin 500mg", "B-CI303", 200, 6000.00, 10000.00, "2027-08-15", "Apex Health"),
            ("Artemether-Lumefantrine (ACT)", "B-AC404", 150, 12000.00, 20000.00, "2027-11-20", "Sierra Pharm Ltd"),
            ("Metronidazole 400mg", "B-ME505", 400, 1500.00, 2500.00, "2028-01-10", "GHC Supply")
        ]
        for name, batch, qty, cost, sell, expiry, supplier in medicines:
            cursor.execute("""
                INSERT INTO Inventory (MedicineName, BatchNumber, Quantity, CostPrice, SellingPrice, ExpiryDate, Supplier)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, batch, qty, cost, sell, expiry, supplier))

        conn.commit()
        conn.close()
        print("✅ Database Redesign Schema Setup & Seeding Complete!")
    except Exception as e:
        print(f"❌ Error during database setup: {e}")

if __name__ == "__main__":
    run_setup()
