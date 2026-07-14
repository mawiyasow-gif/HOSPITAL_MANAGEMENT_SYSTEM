# Physical Health Clinic Record & Hospital Management System

A modern, secure, role-based desktop hospital management system built with Python, CustomTkinter, and MySQL. This system automates the clinical care lifecycle and coordinates operations across multiple hospital roles.

---

## 🏗 System Architecture & Workflow

The application enforces a structured medical and financial workflow:

```
  Patient Registered
 (Receptionist)
       ↓
 Consultation Billed & Paid
 (Receptionist / Billing Center)
       ↓
 Patient Queued to Assigned Doctor
 (Doctor Dashboard)
       ↓
 Lab Requested (Optional)  →  Perform Test & Save Results  →  View Lab Results
 (Doctor Dashboard)           (Laboratory Technician)           (Doctor Dashboard)
       ↓
 Enter Diagnosis & Treatment
 (Doctor Dashboard)
       ↓
 Prescribe Medicines
 (Doctor Dashboard)
       ↓
 Dispense Medicines & Auto-Decrement Stock
 (Pharmacist Dashboard)
       ↓
 Print Dynamic PDF Receipt & Log Audit Trail
 (Pharmacist / Receptionist)
```

---

## 👥 Role-Based Features

### 1. 🔑 Administrator
*   **User Management**: Add, update, delete, and control active/inactive status of employee accounts.
*   **Active Services Catalog**: Manage walk-in clinic service items (e.g. X-Ray, ECG, Consultation fees) and their pricing.
*   **Inventory Control**: Full write-access (Add, Update, Delete, Restock, Expiry alerts) to the clinic's medical inventory.
*   **Metrics**: View total patients, today's appointments, active doctors, pending laboratory requests, low stock items, and daily revenue statistics.

### 2. 👤 Receptionist
*   **Intake & Registration**: Register new patients and choose an assigned doctor.
*   **Scheduling**: Book clinical appointments.
*   **Invoicing & Receipts**: Create billing invoices and print itemized PDF receipts for consultation, registration, or walk-in services.
*   **Queue Management**: Route patient status immediately to the doctor once payments are settled.

### 3. 👨‍⚕️ Doctor
*   **My Patient Queue**: Display only patients assigned directly to the logged-in doctor.
*   **Lab Orders**: Submit requests to the laboratory.
*   **Safe Diagnosis**: The system blocks entering a final diagnosis while requested laboratory results are pending.
*   **Treatment & Prescriptions**: Record diagnoses, input active treatment advice, and draft prescriptions from current inventory stocks.

### 4. 🔬 Laboratory Technician
*   **Test Management**: View pending laboratory requests.
*   **Results Input**: Record findings and close completed tests.
*   **Auto-billing**: Submitting a test result automatically inserts a pending billing record under the patient's account.

### 5. 💊 Pharmacist
*   **Dispensing Hub**: View and process pending prescriptions.
*   **Auto-Inventory Decrement**: Dispensing medicines automatically subtracts stock from the inventory table.
*   **Financial Integration**: Dispensing immediately locks in prescription billing, creates corresponding receipts, and updates stock metrics.

### 6. 📊 Accountant
*   **Financial Logs**: Track total payments, payment methods, and revenue summaries.
*   **System Ledger**: Query database reports mapping dynamic receipt details.

---

## 🛠 Tech Stack

*   **GUI Framework**: CustomTkinter (Modernized styling over standard Tkinter)
*   **Database**: MySQL
*   **PDF Generation**: ReportLab
*   **Security**: SHA-256 Password Hashing

---

## 🚀 Installation & Setup

### 1. Install Dependencies
Ensure Python 3 is installed, then run:
```bash
pip install customtkinter mysql-connector-python reportlab
```

### 2. Configure Database Credentials
Open [database.py](database.py) and enter your local MySQL connection settings:
```python
import mysql.connector

def connect_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="YOUR_MYSQL_USER",
        password="YOUR_MYSQL_PASSWORD",
        database="YOUR_DATABASE_NAME"
    )
    return conn
```

### 3. Initialize & Seed Database
Execute the database setup script to drop existing tables, construct the new schema, and populate default credentials/catalog services:
```bash
python3 db_schema_setup.py
```

### 4. Run the Application
Start the clinical portal by executing:
```bash
python3 login.py
```

---

## 👤 Default Seeded Accounts

All default passwords are set to `[username]123`. The system automatically encrypts and verifies logins using SHA-256 hashing.

| Role | Username | Plaintext Password |
| :--- | :--- | :--- |
| **System Administrator** | `admin` | `admin123` |
| **Doctor** | `doctor` | `doctor123` |
| **Receptionist** | `receptionist` | `receptionist123` |
| **Laboratory Technician** | `labtech` | `labtech123` |
| **Pharmacist** | `pharmacist` | `pharmacist123` |
| **Accountant** | `accountant` | `accountant123` |
