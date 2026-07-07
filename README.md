# 🏥 Physical Health Clinic Record System (EHR)

A complete, modern, and professional Electronic Health Record (EHR) & Clinic Management System built using **Python**, **CustomTkinter** (for a sleek, premium, light/dark-mode GUI), and a **MySQL** database backend. 

This system is designed to streamline clinic workflows, secure patient and medical data under role-based access control, and provide health workers with intuitive tools for patient care, scheduling, billing, and inventory tracking.

---

## 🌟 Key Features

### 🔐 1. Role-Based Access Control (RBAC)
*   **Multi-Role Authentication:** Access levels configured for **Administrators**, **Doctors**, **Nurses**, **Pharmacists**, **Receptionists**, and **Accountants**.
*   **Automatic Dashboard Routing:** The system identifies roles during login and securely redirects users to their designated views.
*   **Staff Profiles with Custom Avatars:** Doctors and health workers can view their clinic profiles alongside profile pictures uploaded by the Admin.

### 💼 2. Admin Command Center
*   **Clinic Statistics Overview:** Dynamic count counters for assigned patients, registered users, and active cases.
*   **Financial Tracking:** Real-time billing and revenue summaries displayed as daily, weekly, monthly, and overall stats.
*   **User Management:** Register new staff accounts, modify details, configure access levels, reset passwords, or suspend accounts.
*   **Alert Notifications:** System alerts highlighting critically low inventory stocks or expired pharmaceutical products.
*   **Maintenance & Backup Tools:** Integrated backup system exporting SQL structure and data statements to local `.sql` files, clinic settings adjustments, and theme toggle controls.

### 🩺 3. Doctor Workspace
*   **Unattended Patients Queue:** Instantly isolates today's pending appointments, allowing clinicians to select a patient, attend to them, and automatically log diagnoses.
*   **Consolidated Medical History:** View a patient's historical diagnoses, descriptions, drug prescriptions, and past medical records in a single interface.
*   **Consultation Logging:** Generate and export clinical performance summaries (Daily, Weekly, Monthly consultations).

### 👥 4. Patient & Medical Record Management
*   **Demographic Registers:** Create, search, and manage patient directories.
*   **Diagnosis and Treatment Logging:** Track description-based diagnoses, prescribe medications, specify exact dosages, and define treatment durations.
*   **Appointment Scheduler:** Set up, search, and manage appointment times and statuses (Pending, Completed, Cancelled).

### 📦 5. Auxiliary Clinic Services
*   **Inventory Control:** Track medical supplies, reorder thresholds, and expiration dates.
*   **Billing & Receipt Generator:** Manage patients' payment transactions, track outstanding balances, and print structured receipts.

---

## 🛠️ Technology Stack

*   **GUI Framework:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Sleek dark/light appearance, responsive designs)
*   **Database:** MySQL (Relational tables with foreign key constraints)
*   **Programming Language:** Python 3
*   **Libraries:** `mysql-connector-python`, `Pillow` (for profile photo manipulation), `shutil`, `json`

---

## 📂 Project Structure

```bash
Physical_Health_Clinic_DB/
│
├── main.py                   # App entrypoint
├── login.py                  # User authentication and role routing
├── admin_dashboard.py        # Administrator core dashboard
├── doctor_dashboard.py       # Doctor clinical workspace & Patient queue
│
├── patients.py               # Patient registration and demographic details
├── appointments.py           # Consultation scheduling and tracker
├── diagnosis.py              # Diagnosis entries and records
├── treatment.py              # Prescription and treatment management
├── user_management.py        # Staff user credential management
├── health_workers.py         # Clinician/worker profiles & photo uploads
├── inventory.py              # Pharmaceutical items and expiry alerts
├── payment.py                # Billing transactions ledger
├── receipt.py                # Receipt generation and printable layouts
│
├── database.py               # MySQL connection initializer
├── settings.py               # Local configurations and backup tools
├── assets/                   # Directory storing doctor profile photos
└── README.md                 # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

1.  **Python 3.8+** installed.
2.  **MySQL Server** active.
3.  Install dependencies:
    ```bash
    pip install customtkinter mysql-connector-python Pillow
    ```

### Database Setup

1.  Create a MySQL database as Pysical_Health_Clinic_DB.
2.  Import your schemas or migration scripts.
3.  Configure database credentials in `database.py`.

### Execution

To run the application, execute:
```bash
python3 main.py
```

---

## 🎨 Design Principles
*   **EHR Aesthetic:** Clean gray backgrounds, professional blue highlights, and standard color cues (green for actions, red for deletes).
*   **No Overhead Scrolling:** Designed to fit standard screen layouts with optimized widget sizing to prevent cutoffs.
*   **Role Isolation:** Filters record sets dynamically so clinicians only view their assigned patients, while administrators maintain a global overview.
