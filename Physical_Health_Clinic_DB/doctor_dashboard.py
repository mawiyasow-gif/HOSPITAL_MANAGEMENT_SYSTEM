import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from database import connect_db
import os

import dashboard_theme

# Set appearance mode and color theme
dashboard_theme.apply_global_theme()


class DoctorDashboard(ctk.CTk):
    """Administrator/Doctor level dashboard for the Clinic System."""

    def __init__(self, doctor_user=None):
        super().__init__()

        self.title("Physical Health Clinic Record System - Doctor Dashboard")
        self.geometry("1600x900")
        self.resizable(True, True)

        # Store doctor profile details
        # Fallback values if not passed via Login Window
        self.doctor_user = doctor_user or {
            "user_id": 1,
            "username": "doctor_sow",
            "full_name": "Dr. Alhaji Mawiya Sow",
            "role": "Doctor",
            "email": "doctor_sow@clinic.com",
            "phone": "+232-76-987654",
            "specialization": "General Physician",
            "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Use the worker_id from session info
        self.doctor_worker_id = self.doctor_user.get("worker_id", 1)

        # ==============================
        # Main Layout Container
        # ==============================
        self.main_container = ctk.CTkFrame(self, fg_color=dashboard_theme.BG_COLOR)
        self.main_container.pack(fill="both", expand=True)

        # ==============================
        # Left Sidebar (Navigation)
        # ==============================
        self.sidebar = ctk.CTkFrame(self.main_container, width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        dashboard_theme.style_sidebar(self.sidebar)

        # Sidebar Title Logo
        # Sidebar Title Logo
        sidebar_title = ctk.CTkLabel(
            self.sidebar,
            text="🏥 DOCTOR PANEL",
            font=("Arial", 18, "bold"),
            text_color=dashboard_theme.TEXT_PRIMARY
        )
        sidebar_title.pack(pady=(30, 20))

        # Nav Buttons list
        menu_items = [
            ("🏠 Dashboard", self.refresh_dashboard),
            ("👥 Patients", self.open_patients),
            ("📅 Appointments", self.open_appointments),
            ("🩺 Diagnosis", self.open_diagnosis),
            ("💊 Treatment", self.open_treatment),
            ("📋 Medical History", self.open_medical_history),
            ("📈 Reports", self.open_reports),
            ("👤 My Profile", self.open_profile),
            ("🚪 Logout", self.logout)
        ]

        for text, command in menu_items:
            if text == "🚪 Logout":
                btn = ctk.CTkButton(
                    self.sidebar,
                    text=text,
                    width=210,
                    height=40,
                    font=("Arial", 13, "bold"),
                    anchor="w",
                    fg_color=dashboard_theme.ACCENT_RED,
                    hover_color="#B71C1C",
                    command=command
                )
                btn.pack(side="bottom", pady=25)
            else:
                is_active = (text == "🏠 Dashboard")
                btn = dashboard_theme.create_sidebar_button(
                    self.sidebar,
                    text=text,
                    command=command,
                    active=is_active
                )
                btn.pack(pady=6)

        # ==============================
        # Right View Area (Scrollable)
        # ==============================
        self.content_frame = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color=dashboard_theme.BG_COLOR)
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.scrollable_frame = ctk.CTkScrollableFrame(self.content_frame, corner_radius=0, fg_color=dashboard_theme.BG_COLOR)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ==============================
        # Header Info Bar
        # ==============================
        self.header_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="#FFFFFF",
            border_color=dashboard_theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12
        )
        self.header_frame.pack(fill="x", pady=(0, 10))

        info_text = (
            f"Welcome back, {self.doctor_user['full_name']}! 👋\n"
            f"Specialization: {self.doctor_user.get('specialization', 'General Physician')}"
        )
        self.info_lbl = ctk.CTkLabel(
            self.header_frame,
            text=info_text,
            font=("Arial", 16, "bold"),
            text_color=dashboard_theme.TEXT_PRIMARY,
            justify="left"
        )
        self.info_lbl.pack(side="left", padx=20, pady=15)

        # Clock & Date Panel
        self.clock_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.clock_frame.pack(side="right", padx=20, pady=10)

        self.date_lbl = ctk.CTkLabel(
            self.clock_frame,
            text=datetime.now().strftime("%A, %d %B %Y"),
            font=("Arial", 12, "bold"),
            text_color=dashboard_theme.TEXT_SECONDARY
        )
        self.date_lbl.pack()

        self.time_lbl = ctk.CTkLabel(
            self.clock_frame,
            text="00:00:00",
            font=("Arial", 18, "bold"),
            text_color=dashboard_theme.ACCENT_BLUE
        )
        self.time_lbl.pack()

        # Start live clock update
        self.update_clock()

        # Statistics Dashboard Cards
        # ==============================
        self.cards_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.cards_frame.pack(fill="x", pady=10)

        # 3 Cards Row 1
        cards_row1 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        cards_row1.pack(fill="x", pady=5)

        self.assigned_patients_card = self.create_stat_card(cards_row1, "👥", "Assigned Patients", "0", "#4CAF50", self.open_patients)
        self.assigned_patients_card.pack(side="left", padx=5, expand=True, fill="x")

        self.today_appointments_card = self.create_stat_card(cards_row1, "📅", "Today's Appointments", "0", "#2196F3", self.open_appointments)
        self.today_appointments_card.pack(side="left", padx=5, expand=True, fill="x")

        self.diagnoses_card = self.create_stat_card(cards_row1, "🩺", "Diagnoses Completed", "0", "#9C27B0", self.open_diagnosis)
        self.diagnoses_card.pack(side="left", padx=5, expand=True, fill="x")

        # 3 Cards Row 2
        cards_row2 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        cards_row2.pack(fill="x", pady=5)

        self.treatments_card = self.create_stat_card(cards_row2, "💊", "Treatments Prescribed", "0", "#E91E63", self.open_treatment)
        self.treatments_card.pack(side="left", padx=5, expand=True, fill="x")

        self.pending_app_card = self.create_stat_card(cards_row2, "⏳", "Pending Appointments", "0", "#FF9800", self.open_appointments)
        self.pending_app_card.pack(side="left", padx=5, expand=True, fill="x")

        self.completed_consult_card = self.create_stat_card(cards_row2, "✅", "Completed Consultations", "0", "#00BCD4", self.open_appointments)
        self.completed_consult_card.pack(side="left", padx=5, expand=True, fill="x")

        # ==============================
        # Action Center & Notifications Split
        # ==============================
        self.action_split_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.action_split_frame.pack(fill="x", pady=10)

        # Quick Actions
        self.actions_frame = ctk.CTkFrame(
            self.action_split_frame,
            fg_color="#FFFFFF",
            border_color=dashboard_theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12
        )
        self.actions_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(self.actions_frame, text="⚡ Quick Action Center", font=("Arial", 16, "bold"), text_color=dashboard_theme.TEXT_PRIMARY).pack(pady=10)

        actions_button_frame = ctk.CTkFrame(self.actions_frame, fg_color="transparent")
        actions_button_frame.pack(pady=10)

        ctk.CTkButton(actions_button_frame, text="👥 Register New Patient", font=("Arial", 12, "bold"), width=180, height=38, command=self.open_patients).grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkButton(actions_button_frame, text="🩺 Record Diagnosis", font=("Arial", 12, "bold"), width=180, height=38, command=self.open_diagnosis).grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkButton(actions_button_frame, text="💊 Prescribe Treatment", font=("Arial", 12, "bold"), width=180, height=38, command=self.open_treatment).grid(row=1, column=0, padx=10, pady=5)
        ctk.CTkButton(actions_button_frame, text="📅 Book Appointment", font=("Arial", 12, "bold"), width=180, height=38, command=self.open_appointments).grid(row=1, column=1, padx=10, pady=5)
        ctk.CTkButton(actions_button_frame, text="📋 Medical History", font=("Arial", 12, "bold"), width=180, height=38, command=self.open_medical_history).grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        # Notifications
        self.notif_frame = ctk.CTkFrame(self.action_split_frame, width=450)
        self.notif_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        self.notif_frame.pack_propagate(False)

        ctk.CTkLabel(self.notif_frame, text="🔔 Clinical Notifications", font=("Arial", 16, "bold")).pack(pady=10)
        self.notif_textbox = ctk.CTkTextbox(self.notif_frame, height=130, font=("Arial", 12))
        self.notif_textbox.pack(fill="both", expand=True, padx=10, pady=10)

        # ==============================
        # Main Patient Search Bar
        # ==============================
        self.search_frame = ctk.CTkFrame(self.scrollable_frame)
        self.search_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(self.search_frame, text="🔎 Patient Quick Search:", font=("Arial", 14, "bold")).pack(side="left", padx=15, pady=10)
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search by Patient ID, Name, or Phone...", width=380)
        self.search_entry.pack(side="left", padx=10)
        self.search_entry.bind("<KeyRelease>", self.search_patients)

        ctk.CTkButton(self.search_frame, text="Clear Search", command=self.clear_search).pack(side="left", padx=5)

        # ==============================
        # Assigned Patients Grid
        # ==============================
        self.patients_table_frame = ctk.CTkFrame(self.scrollable_frame)
        self.patients_table_frame.pack(fill="x", pady=10)

        self.patients_table = self.create_recent_table_frame(
            self.patients_table_frame,
            "📋 Assigned Patients & Last Visits",
            ("Patient ID", "Full Name", "Gender", "Phone Number", "Last Appointment Visit")
        )
        self.patients_table.pack(fill="both", expand=True, padx=10, pady=10)
        self.patients_table.table.bind("<Double-1>", self.on_patient_double_click)
        self.patients_table.table.bind("<<TreeviewSelect>>", self.on_assigned_select)

        self.attend_assigned_btn = ctk.CTkButton(
            self.patients_table_frame,
            text="🩺 Consult Selected Patient",
            font=("Arial", 12, "bold"),
            command=self.attend_assigned_patient,
            state="disabled",
            fg_color="gray"
        )
        self.attend_assigned_btn.pack(pady=5)

        # ==============================
        # Split Table Layout (Appointments / Diagnosis / Treatment)
        # ==============================
        self.split_tables_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.split_tables_frame.pack(fill="x", pady=10)

        # Today's appointments
        self.app_table_frame = ctk.CTkFrame(self.split_tables_frame)
        self.app_table_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.today_app_table = self.create_recent_table_frame(
            self.app_table_frame,
            "⚠️ Unattended Patients Queue",
            ("ID", "Patient Name", "Time", "Status")
        )
        self.today_app_table.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        self.today_app_table.table.bind("<Double-1>", self.on_patient_double_click)
        self.today_app_table.table.bind("<<TreeviewSelect>>", self.on_unattended_select)

        # Attend Selected Patient Button (Disabled by default)
        self.attend_btn = ctk.CTkButton(
            self.app_table_frame,
            text="🩺 Attend Selected Patient",
            font=("Arial", 12, "bold"),
            command=self.attend_patient,
            state="disabled",
            fg_color="gray"
        )
        self.attend_btn.pack(pady=5)

        # Diagnoses
        self.diag_table_frame = ctk.CTkFrame(self.split_tables_frame)
        self.diag_table_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        self.recent_diag_table = self.create_recent_table_frame(
            self.diag_table_frame,
            "🩺 Recent Diagnoses Prescribed",
            ("Diag ID", "Patient Name", "Diagnosis Description", "Date")
        )
        self.recent_diag_table.pack(fill="both", expand=True, padx=10, pady=10)

        # Initialize data
        self.refresh_dashboard()

    # ==============================
    # Helper Layout Utilities
    # ==============================

    def get_doctor_worker_id(self):
        """Retrieve the Health_Workers table ID corresponding to this logged-in user name."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT WorkerID FROM Health_Workers WHERE FullName = %s", (self.doctor_user["full_name"],))
            row = cursor.fetchone()
            conn.close()
            if row:
                return row[0]
        except:
            pass
        return 1  # Default fallback ID

    def create_stat_card(self, parent, icon, title, value, color, command=None):
        """Create a modern clickable statistics card."""
        return dashboard_theme.create_modern_stat_card(parent, icon, title, value, color, command)

    def create_recent_table_frame(self, parent, title, columns):
        """Create a frame containing styled Treeview table."""
        frame = ctk.CTkFrame(parent, fg_color="#FFFFFF", border_color=dashboard_theme.BORDER_COLOR, border_width=1, corner_radius=12)
        
        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(header_frame, text=title, font=("Arial", 14, "bold"), text_color=dashboard_theme.TEXT_PRIMARY).pack(side="left")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground="#1E293B",
            fieldbackground="#FFFFFF",
            rowheight=35,
            font=("Arial", 11)
        )
        style.configure(
            "Treeview.Heading",
            background="#F1F5F9",
            foreground="#475569",
            font=("Arial", 11, "bold"),
            relief="flat"
        )
        style.map("Treeview", background=[("selected", "#E2E8F0")], foreground=[("selected", "#0F172A")])

        table = ttk.Treeview(frame, columns=columns, show="headings", height=6)
        for col in columns:
            table.heading(col, text=col, anchor="center")
            table.column(col, width=120, anchor="center")

        v_scroll = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=v_scroll.set)

        table.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=(0, 15))
        v_scroll.pack(side="right", fill="y", pady=(0, 15), padx=(0, 15))

        frame.table = table
        return frame

    # ==============================
    # Clock & Live Updates
    # ==============================

    def update_clock(self):
        """Update clock display dynamically."""
        self.time_lbl.configure(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self.update_clock)

    # ==============================
    # Core Data Loading
    # ==============================

    def load_dashboard_statistics(self):
        """Query and populate card statistics from MySQL."""
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # 1. Total Assigned Patients
            cursor.execute("SELECT COUNT(DISTINCT PatientID) FROM Appointments WHERE WorkerID = %s", (self.doctor_worker_id,))
            assigned_patients = cursor.fetchone()[0]
            self.assigned_patients_card.value_label.configure(text=str(assigned_patients))

            # 2. Today's Appointments
            cursor.execute("SELECT COUNT(*) FROM Appointments WHERE WorkerID = %s AND AppointmentDate = CURDATE()", (self.doctor_worker_id,))
            today_app = cursor.fetchone()[0]
            self.today_appointments_card.value_label.configure(text=str(today_app))

            # 3. Diagnoses Completed
            cursor.execute("SELECT COUNT(*) FROM Diagnosis WHERE DoctorID = %s", (self.doctor_worker_id,))
            diag_count = cursor.fetchone()[0]
            self.diagnoses_card.value_label.configure(text=str(diag_count))

            # 4. Treatments Prescribed
            cursor.execute("SELECT COUNT(*) FROM Treatment WHERE DoctorID = %s", (self.doctor_worker_id,))
            treat_count = cursor.fetchone()[0]
            self.treatments_card.value_label.configure(text=str(treat_count))

            # 5. Pending Appointments
            cursor.execute("SELECT COUNT(*) FROM Appointments WHERE WorkerID = %s AND Status = 'Pending'", (self.doctor_worker_id,))
            pending_app = cursor.fetchone()[0]
            self.pending_app_card.value_label.configure(text=str(pending_app))

            # 6. Completed Consultations
            cursor.execute("SELECT COUNT(*) FROM Appointments WHERE WorkerID = %s AND Status = 'Completed'", (self.doctor_worker_id,))
            completed_app = cursor.fetchone()[0]
            self.completed_consult_card.value_label.configure(text=str(completed_app))

            conn.close()
        except Exception as e:
            print(f"Error loading dashboard statistics: {e}")

    def load_today_appointments(self):
        """Fetch and render today's appointment list."""
        table = self.today_app_table.table
        for item in table.get_children():
            table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT a.AppointmentID, pat.FullName, a.AppointmentTime, a.Status
                FROM Appointments a
                LEFT JOIN Patients pat ON a.PatientID = pat.PatientID
                WHERE a.WorkerID = %s 
                  AND a.AppointmentDate = CURDATE() 
                  AND a.Status = 'Pending'
                  AND EXISTS (
                      SELECT 1 FROM Payment p
                      WHERE p.PatientID = a.PatientID
                        AND p.PaymentType = 'Consultation'
                        AND p.PaymentMethod <> 'Pending'
                  )
                ORDER BY a.AppointmentTime ASC
            """
            cursor.execute(query, (self.doctor_worker_id,))
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error loading today's appointments: {e}")

    def load_assigned_patients(self):
        """Fetch and render all patients assigned to this doctor."""
        table = self.patients_table.table
        for item in table.get_children():
            table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT p.PatientID, p.FullName, p.Gender, p.PhoneNumber, MAX(a.AppointmentDate)
                FROM Patients p
                INNER JOIN Appointments a ON p.PatientID = a.PatientID
                WHERE a.WorkerID = %s
                GROUP BY p.PatientID
                ORDER BY MAX(a.AppointmentDate) DESC
            """
            cursor.execute(query, (self.doctor_worker_id,))
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error loading assigned patients: {e}")

    def load_recent_diagnosis(self):
        """Fetch and render doctor's recent diagnoses."""
        table = self.recent_diag_table.table
        for item in table.get_children():
            table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT d.DiagnosisID, pat.FullName, d.DiagnosisDetails, d.DiagnosisDate
                FROM Diagnosis d
                LEFT JOIN Patients pat ON d.PatientID = pat.PatientID
                WHERE d.DoctorID = %s
                ORDER BY d.DiagnosisID DESC LIMIT 10
            """
            cursor.execute(query, (self.doctor_worker_id,))
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error loading diagnoses: {e}")

    def load_notifications(self):
        """Check values to generate relevant clinic notifications."""
        self.notif_textbox.configure(state="normal")
        self.notif_textbox.delete("1.0", "end")

        notifs = []
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # New pending appointments today
            cursor.execute(
                "SELECT COUNT(*) FROM Appointments WHERE WorkerID=%s AND Status='Pending' AND AppointmentDate=CURDATE()",
                (self.doctor_worker_id,)
            )
            count = cursor.fetchone()[0]
            if count > 0:
                notifs.append(f"📅 You have {count} pending consultations scheduled for today.")

            # Urgently check inventory of standard items?
            cursor.execute("SELECT MedicineName, Quantity FROM Inventory WHERE Quantity < 5 LIMIT 3")
            low_stock = cursor.fetchall()
            for item in low_stock:
                notifs.append(f"🚨 Urgent: Medicine {item[0]} has critically low stock ({item[1]} units left).")

            conn.close()
        except Exception as e:
            print(f"Error checking notifications: {e}")

        if not notifs:
            notifs.append("✅ No urgent clinical notifications today.")

        self.notif_textbox.insert("1.0", "\n\n".join(notifs))
        self.notif_textbox.configure(state="disabled")

    # ==============================
    # Interactive Operations
    # ==============================

    def search_patients(self, event=None):
        """Filter the assigned patients table instantly based on search entries."""
        search_query = self.search_entry.get().strip()
        if not search_query:
            self.load_assigned_patients()
            return

        table = self.patients_table.table
        for item in table.get_children():
            table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT p.PatientID, p.FullName, p.Gender, p.PhoneNumber, MAX(a.AppointmentDate)
                FROM Patients p
                INNER JOIN Appointments a ON p.PatientID = a.PatientID
                WHERE a.WorkerID = %s AND (p.PatientID LIKE %s OR p.FullName LIKE %s OR p.PhoneNumber LIKE %s)
                GROUP BY p.PatientID
            """
            like_val = f"%{search_query}%"
            cursor.execute(query, (self.doctor_worker_id, like_val, like_val, like_val))
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error searching patients: {e}")

    def clear_search(self):
        """Reset search query text field."""
        self.search_entry.delete(0, "end")
        self.load_assigned_patients()

    def on_patient_double_click(self, event):
        """Open Patient details popup if double clicked."""
        selected = event.widget.selection()
        if not selected:
            return
        row = event.widget.item(selected[0], "values")
        if row:
            patient_id = row[0]
            # Opens medical history window directly for selected patient
            self.open_medical_history(patient_id)

    def on_assigned_select(self, event):
        selected = self.patients_table.table.selection()
        if selected:
            self.attend_assigned_btn.configure(state="normal", fg_color="#4CAF50")
        else:
            self.attend_assigned_btn.configure(state="disabled", fg_color="gray")

    def attend_assigned_patient(self):
        selected = self.patients_table.table.selection()
        if not selected:
            return
        row = self.patients_table.table.item(selected[0], "values")
        if row:
            patient_id = row[0]
            patient_name = row[1]
            self.attend_patient_by_id(patient_id, patient_name)

    def attend_patient_by_id(self, patient_id, patient_name):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # Find the latest pending/scheduled appointment today or in the future
            cursor.execute("""
                SELECT AppointmentID FROM Appointments 
                WHERE PatientID = %s AND WorkerID = %s AND Status IN ('Pending', 'Scheduled')
                ORDER BY AppointmentDate ASC, AppointmentTime ASC LIMIT 1
            """, (patient_id, self.doctor_worker_id))
            row_app = cursor.fetchone()
            
            if row_app:
                appointment_id = row_app[0]
            else:
                # If no pending appointment exists, create a walk-in appointment for today
                cursor.execute("""
                    INSERT INTO Appointments (PatientID, WorkerID, AppointmentDate, AppointmentTime, Status)
                    VALUES (%s, %s, CURDATE(), CURRENT_TIME(), 'Pending')
                """, (patient_id, self.doctor_worker_id))
                appointment_id = cursor.lastrowid
                conn.commit()

            conn.close()

            # Open ConsultationWindow
            ConsultationWindow(self, appointment_id, patient_id, patient_name, self.doctor_worker_id)
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to start consultation:\n{e}")

    def on_unattended_select(self, event):
        """Enable the attend button when a patient is selected in the unattended queue."""
        selected = self.today_app_table.table.selection()
        if selected:
            self.attend_btn.configure(state="normal", fg_color="#4CAF50")
        else:
            self.attend_btn.configure(state="disabled", fg_color="gray")

    def attend_patient(self):
        """Open the ConsultationWindow for the selected appointment."""
        selected = self.today_app_table.table.selection()
        if not selected:
            messagebox.showwarning("Selection Warning", "Please select a patient appointment from the queue.")
            return

        row = self.today_app_table.table.item(selected[0], "values")
        if not row:
            return

        appointment_id = row[0]
        patient_name = row[1]

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT PatientID FROM Appointments WHERE AppointmentID = %s", (appointment_id,))
            row_pat = cursor.fetchone()
            conn.close()
            if not row_pat:
                messagebox.showerror("Error", "Patient ID not found for this appointment.")
                return
            patient_id = row_pat[0]

            # Open ConsultationWindow
            ConsultationWindow(self, appointment_id, patient_id, patient_name, self.doctor_worker_id)
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to retrieve patient details:\n{e}")

    def refresh_dashboard(self):
        """Reload all data lists."""
        self.load_dashboard_statistics()
        self.load_today_appointments()
        self.load_assigned_patients()
        self.load_recent_diagnosis()
        self.load_notifications()
        # Reset attend button state
        self.attend_btn.configure(state="disabled", fg_color="gray")

    # ==============================
    # Navigation Openers
    # ==============================

    def open_patients(self):
        """Open patients management panel."""
        from patients import PatientWindow
        PatientWindow(self)

    def open_appointments(self):
        """Open appointments record manager."""
        from appointments import AppointmentWindow
        AppointmentWindow(self)

    def open_diagnosis(self):
        """Open diagnosis panel."""
        from diagnosis import DiagnosisWindow
        DiagnosisWindow(self)

    def open_treatment(self):
        """Open treatment manager."""
        from treatment import TreatmentWindow
        TreatmentWindow(self)

    def open_medical_history(self, patient_id=None):
        """Display patient medical record window."""
        MedicalHistoryWindow(self, patient_id)

    def open_reports(self):
        """Display reports manager window."""
        DoctorReportsWindow(self, self.doctor_worker_id)

    def open_profile(self):
        """Open doctor profile detail widget window."""
        ProfileWindow(self, self.doctor_user, self.doctor_worker_id)

    def logout(self):
        """Confirm sign-out procedure returning back to Login screen."""
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to sign out from the Doctor Panel?")
        if confirm:
            self.destroy()
            from login import LoginApp
            app = LoginApp()
            app.mainloop()


# ==============================================================
# Helper Windows (History / Profile / Reports)
# ==============================================================

class MedicalHistoryWindow(ctk.CTkToplevel):
    """Window showing consolidated patient diagnoses and treatments history."""

    def __init__(self, parent, patient_id=None):
        super().__init__(parent)
        self.title("Consolidated Medical History")
        self.geometry("1100x650")
        self.resizable(True, True)

        self.patient_id = patient_id

        # Title
        ctk.CTkLabel(self, text="📋 Consolidated Patient Medical History", font=("Arial", 22, "bold"), text_color="#1F6AA5").pack(pady=15)

        # Selection Bar if patient_id is not passed
        if not self.patient_id:
            select_frame = ctk.CTkFrame(self)
            select_frame.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(select_frame, text="Select Patient:", font=("Arial", 12, "bold")).pack(side="left", padx=10, pady=10)

            self.patient_combo = ctk.CTkComboBox(select_frame, width=300)
            self.patient_combo.pack(side="left", padx=10)
            self.load_patients_into_combo()

            ctk.CTkButton(select_frame, text="Load History", command=self.load_history_from_selection).pack(side="left", padx=10)
        else:
            self.load_patient_history(self.patient_id)

        # Tab view to separate Diagnoses vs Treatments
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=20)

        self.tab_diag = self.tabs.add("Diagnoses Records")
        self.tab_treat = self.tabs.add("Treatments History")

        # Diagnoses Table
        self.diag_table = ttk.Treeview(self.tab_diag, columns=("ID", "Diagnosis Date", "Description", "Assigned Doctor"), show="headings")
        for col in ("ID", "Diagnosis Date", "Description", "Assigned Doctor"):
            self.diag_table.heading(col, text=col)
            self.diag_table.column(col, width=150, anchor="center")
        self.diag_table.column("Description", width=400, anchor="w")
        self.diag_table.pack(fill="both", expand=True, padx=10, pady=10)

        # Treatments Table
        self.treat_table = ttk.Treeview(self.tab_treat, columns=("ID", "Medication", "Dosage", "Duration", "Prescribing Worker"), show="headings")
        for col in ("ID", "Medication", "Dosage", "Duration", "Prescribing Worker"):
            self.treat_table.heading(col, text=col)
            self.treat_table.column(col, width=150, anchor="center")
        self.treat_table.pack(fill="both", expand=True, padx=10, pady=10)

    def load_patients_into_combo(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT PatientID, FullName FROM Patients")
            self.patient_dict = {}
            vals = []
            for row in cursor.fetchall():
                display_str = f"{row[0]} - {row[1]}"
                vals.append(display_str)
                self.patient_dict[display_str] = row[0]
            self.patient_combo.configure(values=vals)
            if vals:
                self.patient_combo.set(vals[0])
            conn.close()
        except Exception as e:
            print(e)

    def load_history_from_selection(self):
        selected_val = self.patient_combo.get()
        p_id = self.patient_dict.get(selected_val)
        if p_id:
            self.load_patient_history(p_id)

    def load_patient_history(self, p_id):
        # Clear
        for item in self.diag_table.get_children():
            self.diag_table.delete(item)
        for item in self.treat_table.get_children():
            self.treat_table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Diagnoses
            cursor.execute("""
                SELECT d.DiagnosisID, d.DiagnosisDate, d.DiagnosisDetails, w.FullName
                FROM Diagnosis d
                LEFT JOIN Health_Workers w ON d.DoctorID = w.WorkerID
                WHERE d.PatientID = %s
                ORDER BY d.DiagnosisDate DESC
            """, (p_id,))
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                self.diag_table.insert("", "end", values=cleaned)

            # Treatments
            cursor.execute("""
                SELECT t.TreatmentID, t.TreatmentName, t.Dosage, t.Duration, w.FullName
                FROM Treatment t
                LEFT JOIN Health_Workers w ON t.WorkerID = w.WorkerID
                WHERE t.PatientID = %s
                ORDER BY t.TreatmentID DESC
            """, (p_id,))
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                self.treat_table.insert("", "end", values=cleaned)

            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load patient medical history:\n{e}")


class DoctorReportsWindow(ctk.CTkToplevel):
    """Reports configuration panel to view consultations and diagnoses reports."""

    def __init__(self, parent, doctor_worker_id):
        super().__init__(parent)
        self.title("Consultation & Prescription Reports")
        self.geometry("900x600")
        self.resizable(True, True)

        self.doctor_worker_id = doctor_worker_id

        ctk.CTkLabel(self, text="📈 Doctor Performance & Consultation Reports", font=("Arial", 20, "bold"), text_color="#1F6AA5").pack(pady=15)

        # Filters
        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(filter_frame, text="Filter Period:", font=("Arial", 12, "bold")).pack(side="left", padx=10, pady=10)
        self.period_combo = ctk.CTkComboBox(filter_frame, values=["Daily Consultations", "Weekly Consultations", "Monthly Consultations", "All Records"])
        self.period_combo.set("Daily Consultations")
        self.period_combo.pack(side="left", padx=10)

        ctk.CTkButton(filter_frame, text="Generate Report", command=self.generate_report).pack(side="left", padx=10)
        ctk.CTkButton(filter_frame, text="🖨️ Export PDF Placeholder", command=lambda: messagebox.showinfo("Export", "PDF Export functionality will be connected later.")).pack(side="left", padx=10)

        # Table showing results
        columns = ("Record ID", "Patient Name", "Consultation Date", "Status / Details")
        self.report_table = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for col in columns:
            self.report_table.heading(col, text=col)
            self.report_table.column(col, width=150, anchor="center")
        self.report_table.column("Patient Name", width=220)
        self.report_table.column("Status / Details", width=300)
        self.report_table.pack(fill="both", expand=True, padx=20, pady=15)

    def generate_report(self):
        for item in self.report_table.get_children():
            self.report_table.delete(item)

        period = self.period_combo.get()
        query = ""
        params = []

        if period == "Daily Consultations":
            query = """
                SELECT a.AppointmentID, pat.FullName, a.AppointmentDate, a.Status
                FROM Appointments a
                LEFT JOIN Patients pat ON a.PatientID = pat.PatientID
                WHERE a.WorkerID = %s AND a.AppointmentDate = CURDATE()
            """
            params = [self.doctor_worker_id]
        elif period == "Weekly Consultations":
            query = """
                SELECT a.AppointmentID, pat.FullName, a.AppointmentDate, a.Status
                FROM Appointments a
                LEFT JOIN Patients pat ON a.PatientID = pat.PatientID
                WHERE a.WorkerID = %s AND YEARWEEK(a.AppointmentDate, 1) = YEARWEEK(CURDATE(), 1)
            """
            params = [self.doctor_worker_id]
        elif period == "Monthly Consultations":
            query = """
                SELECT a.AppointmentID, pat.FullName, a.AppointmentDate, a.Status
                FROM Appointments a
                LEFT JOIN Patients pat ON a.PatientID = pat.PatientID
                WHERE a.WorkerID = %s AND MONTH(a.AppointmentDate) = MONTH(CURDATE()) AND YEAR(a.AppointmentDate) = YEAR(CURDATE())
            """
            params = [self.doctor_worker_id]
        else:
            query = """
                SELECT a.AppointmentID, pat.FullName, a.AppointmentDate, a.Status
                FROM Appointments a
                LEFT JOIN Patients pat ON a.PatientID = pat.PatientID
                WHERE a.WorkerID = %s
            """
            params = [self.doctor_worker_id]

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                self.report_table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate reports:\n{e}")


class ProfileWindow(ctk.CTkToplevel):
    """Personal Doctor Account Details Profile Panel."""

    def __init__(self, parent, user_data, worker_id):
        super().__init__(parent)
        self.title("My Profile - Doctor Access")
        self.geometry("750x550")
        self.resizable(False, False)

        ctk.CTkLabel(self, text="👤 My Account Profile", font=("Arial", 22, "bold"), text_color="#1F6AA5").pack(pady=20)

        main_panel = ctk.CTkFrame(self, fg_color="transparent")
        main_panel.pack(fill="both", expand=True, padx=20, pady=10)

        # Left Side: Profile Picture
        pic_frame = ctk.CTkFrame(main_panel, width=200, height=220)
        pic_frame.pack(side="left", fill="y", padx=15, pady=10)
        pic_frame.pack_propagate(False)

        # Check if doctor image exists
        image_path = f"assets/doctor_{worker_id}.png"
        from PIL import Image
        if os.path.exists(image_path):
            try:
                pil_img = Image.open(image_path)
                # Resize keeping aspect ratio
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(160, 180))
                img_lbl = ctk.CTkLabel(pic_frame, image=ctk_img, text="")
                img_lbl.pack(pady=15)
            except Exception as e:
                print(f"Error loading profile image: {e}")
                # Fallback to emoji placeholder
                ctk.CTkLabel(pic_frame, text="👨‍⚕️", font=("Arial", 90)).pack(pady=40)
        else:
            # Emoji placeholder
            ctk.CTkLabel(pic_frame, text="👨‍⚕️", font=("Arial", 90)).pack(pady=40)

        ctk.CTkLabel(pic_frame, text="Profile Photo", font=("Arial", 12, "bold"), text_color="gray").pack()

        # Right Side: Info Details
        info_frame = ctk.CTkFrame(main_panel)
        info_frame.pack(side="right", fill="both", expand=True, padx=15, pady=10)

        details = [
            ("Doctor Full Name:", user_data.get("full_name")),
            ("Employee Worker ID:", f"DOC-{worker_id}"),
            ("Account Username:", user_data.get("username")),
            ("Email Address:", user_data.get("email")),
            ("Phone Contact:", user_data.get("phone")),
            ("Access Role:", user_data.get("role")),
            ("Last Session Logged:", user_data.get("last_login"))
        ]

        for i, (label, val) in enumerate(details):
            ctk.CTkLabel(info_frame, text=label, font=("Arial", 13, "bold")).grid(row=i, column=0, padx=15, pady=8, sticky="e")
            ctk.CTkLabel(info_frame, text=val, font=("Arial", 13)).grid(row=i, column=1, padx=15, pady=8, sticky="w")


if __name__ == "__main__":
    app = DoctorDashboard()
    app.mainloop()


class ConsultationWindow(ctk.CTkToplevel):
    """Clinical Consultation Workspace for Doctor."""

    def __init__(self, parent, appointment_id, patient_id, patient_name, doctor_worker_id):
        super().__init__(parent)
        self.parent = parent
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.doctor_worker_id = doctor_worker_id

        self.title(f"Consultation Workspace - Patient: {patient_name} (ID: {patient_id})")
        self.geometry("1400x850")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.prescriptions = []

        # UI Layout
        # Top Panel
        top_panel = ctk.CTkFrame(self, height=60)
        top_panel.pack(fill="x", padx=15, pady=10)
        top_panel.pack_propagate(False)
        
        title_lbl = ctk.CTkLabel(top_panel, text=f"🩺 Patient Consultation: {patient_name} (ID: {patient_id})", font=("Arial", 18, "bold"), text_color="#1F6AA5")
        title_lbl.pack(side="left", padx=20, pady=15)
        
        close_btn = ctk.CTkButton(top_panel, text="Close Workspace", fg_color="red", hover_color="#b71c1c", width=120, command=self.destroy)
        close_btn.pack(side="right", padx=20, pady=15)

        # Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.tab_history = self.tabview.add("Patient Details & History")
        self.tab_lab = self.tabview.add("Laboratory Requests & Results")
        self.tab_diagnosis = self.tabview.add("Diagnosis & Treatment Plan")

        self.setup_history_tab()
        self.setup_lab_tab()
        self.setup_diagnosis_tab()

    def setup_history_tab(self):
        # Layout for history tab
        # 1. Demographics Panel
        demo_frame = ctk.CTkFrame(self.tab_history)
        demo_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(demo_frame, text="📋 Patient Demographics", font=("Arial", 14, "bold"), text_color="#1F6AA5").grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=5)
        
        # Query patient info
        dob = gender = phone = address = blood = ""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT DateOfBirth, Gender, PhoneNumber, Address, BloodGroup FROM Patients WHERE PatientID = %s", (self.patient_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                dob, gender, phone, address, blood = row
                dob = str(dob)
                blood = blood if blood else "Unknown"
        except Exception as e:
            print(f"Error fetching demographics: {e}")

        ctk.CTkLabel(demo_frame, text="Date of Birth:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="e", padx=10, pady=5)
        ctk.CTkLabel(demo_frame, text=dob, font=("Arial", 12)).grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        ctk.CTkLabel(demo_frame, text="Gender:", font=("Arial", 12, "bold")).grid(row=1, column=2, sticky="e", padx=10, pady=5)
        ctk.CTkLabel(demo_frame, text=gender, font=("Arial", 12)).grid(row=1, column=3, sticky="w", padx=10, pady=5)
        
        ctk.CTkLabel(demo_frame, text="Phone Number:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="e", padx=10, pady=5)
        ctk.CTkLabel(demo_frame, text=phone, font=("Arial", 12)).grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        ctk.CTkLabel(demo_frame, text="Blood Group:", font=("Arial", 12, "bold")).grid(row=2, column=2, sticky="e", padx=10, pady=5)
        ctk.CTkLabel(demo_frame, text=blood, font=("Arial", 12)).grid(row=2, column=3, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(demo_frame, text="Home Address:", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky="e", padx=10, pady=5)
        ctk.CTkLabel(demo_frame, text=address, font=("Arial", 12)).grid(row=3, column=1, columnspan=3, sticky="w", padx=10, pady=5)

        # 2. History tables frame (split layout)
        tables_frame = ctk.CTkFrame(self.tab_history, fg_color="transparent")
        tables_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Diagnoses Tree
        diag_frame = ctk.CTkFrame(tables_frame)
        diag_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        ctk.CTkLabel(diag_frame, text="🩺 Previous Diagnoses", font=("Arial", 14, "bold"), text_color="#1F6AA5").pack(pady=5)
        
        self.diag_tree = self.create_tree(diag_frame, ("Date", "Details", "Doctor"))
        self.diag_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Treatments Tree
        treat_frame = ctk.CTkFrame(tables_frame)
        treat_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        ctk.CTkLabel(treat_frame, text="💊 Previous Treatments & Prescriptions", font=("Arial", 14, "bold"), text_color="#1F6AA5").pack(pady=5)
        
        self.treat_tree = self.create_tree(treat_frame, ("Start Date", "End Date", "Treatment Details", "Doctor"))
        self.treat_tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_history_data()

    def create_tree(self, parent, columns):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side="right", fill="y")
        
        tree = ttk.Treeview(container, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        for col in columns:
            tree.heading(col, text=col, anchor="w")
            tree.column(col, anchor="w", width=120)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=tree.yview)
        return tree

    def load_history_data(self):
        # Load previous diagnoses
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.DiagnosisDate, d.DiagnosisDetails, hw.FullName
                FROM Diagnosis d
                LEFT JOIN Health_Workers hw ON d.DoctorID = hw.WorkerID
                WHERE d.PatientID = %s ORDER BY d.DiagnosisID DESC
            """, (self.patient_id,))
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                self.diag_tree.insert("", "end", values=cleaned)

            # Load previous treatments
            cursor.execute("""
                SELECT t.StartDate, t.EndDate, t.TreatmentDetails, hw.FullName
                FROM Treatment t
                LEFT JOIN Health_Workers hw ON t.DoctorID = hw.WorkerID
                WHERE t.PatientID = %s ORDER BY t.TreatmentID DESC
            """, (self.patient_id,))
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                self.treat_tree.insert("", "end", values=cleaned)
                
            conn.close()
        except Exception as e:
            print(f"Error loading history data: {e}")

    def setup_lab_tab(self):
        main_lab_frame = ctk.CTkFrame(self.tab_lab, fg_color="transparent")
        main_lab_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left Panel: Lab Requests Tree
        left_panel = ctk.CTkFrame(main_lab_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        ctk.CTkLabel(left_panel, text="📋 Lab Request Log", font=("Arial", 14, "bold"), text_color="#1F6AA5").pack(pady=5)
        
        self.lab_tree = self.create_tree(left_panel, ("Req ID", "Date", "Test Name", "Result Details", "Technician", "Status"))
        self.lab_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Right Panel: Create New Request
        right_panel = ctk.CTkFrame(main_lab_frame, width=350)
        right_panel.pack(side="right", fill="both", padx=(5, 0))
        right_panel.pack_propagate(False)

        ctk.CTkLabel(right_panel, text="➕ Create Laboratory Request", font=("Arial", 14, "bold"), text_color="#1F6AA5").pack(pady=10)
        
        # Test selection scrollable list
        ctk.CTkLabel(right_panel, text="Select Tests Required:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        
        self.tests_frame = ctk.CTkScrollableFrame(right_panel, height=250)
        self.tests_frame.pack(fill="x", padx=20, pady=5)
        
        # Query active tests from Laboratory_Tests
        self.test_checkboxes = {}
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT TestID, TestName, Price FROM Laboratory_Tests")
            tests = cursor.fetchall()
            conn.close()
            
            for test_id, name, price in tests:
                var = ctk.BooleanVar()
                cb = ctk.CTkCheckBox(self.tests_frame, text=f"{name} (Le {price:,.2f})", variable=var)
                cb.pack(anchor="w", padx=10, pady=4)
                self.test_checkboxes[test_id] = (var, name, price)
        except Exception as e:
            print(f"Error loading lab tests list: {e}")

        # Send Request Button
        self.req_btn = ctk.CTkButton(right_panel, text="🚀 Send Lab Request", font=("Arial", 13, "bold"), height=38, command=self.send_lab_request)
        self.req_btn.pack(pady=20, padx=20, fill="x")

        # Current Lab Status Label
        self.lab_status_lbl = ctk.CTkLabel(right_panel, text="Status: Ready for Consultation", font=("Arial", 12, "bold"), text_color="green")
        self.lab_status_lbl.pack(pady=10)

        self.load_lab_requests()
        self.check_pending_lab_status()

    def load_lab_requests(self):
        for item in self.lab_tree.get_children():
            self.lab_tree.delete(item)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT lr.RequestID, lr.RequestDate, lt.TestName, res.ResultDetails, tech.FullName, lr.Status
                FROM Laboratory_Requests lr
                LEFT JOIN Laboratory_Results res ON lr.RequestID = res.RequestID
                LEFT JOIN Laboratory_Tests lt ON res.TestID = lt.TestID
                LEFT JOIN Health_Workers tech ON res.TechnicianID = tech.WorkerID
                WHERE lr.PatientID = %s
                ORDER BY lr.RequestID DESC
            """, (self.patient_id,))
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                self.lab_tree.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error loading lab requests: {e}")

    def check_pending_lab_status(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Laboratory_Requests WHERE PatientID = %s AND Status = 'Pending'", (self.patient_id,))
            pending_count = cursor.fetchone()[0]
            conn.close()
            
            if pending_count > 0:
                self.lab_status_lbl.configure(text="⚠️ Waiting for Laboratory Results (Pending)", text_color="#FF9800")
                if hasattr(self, "finalize_btn"):
                    self.finalize_btn.configure(state="disabled", fg_color="gray")
                    self.finalize_btn.configure(text="🔒 Lab Tests Pending - Finalize Disabled")
            else:
                self.lab_status_lbl.configure(text="✅ Ready for Final Diagnosis (No Pending Tests)", text_color="green")
                if hasattr(self, "finalize_btn"):
                    self.finalize_btn.configure(state="normal", fg_color="#4CAF50")
                    self.finalize_btn.configure(text="💾 Finalize Consultation & Print Prescription")
        except Exception as e:
            print(f"Error checking pending lab status: {e}")

    def send_lab_request(self):
        selected_tests = [test_id for test_id, (var, name, price) in self.test_checkboxes.items() if var.get()]
        if not selected_tests:
            messagebox.showwarning("Selection Warning", "Please select at least one laboratory test.")
            return

        confirm = messagebox.askyesno("Confirm Request", "Send selected tests to the Laboratory?")
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO Laboratory_Requests (PatientID, DoctorID, AppointmentID, Status)
                VALUES (%s, %s, %s, 'Pending')
            """, (self.patient_id, self.doctor_worker_id, self.appointment_id))
            request_id = cursor.lastrowid
            
            total_price = 0.00
            for test_id in selected_tests:
                cursor.execute("""
                    INSERT INTO Laboratory_Results (RequestID, TestID, ResultDetails, TestDate, TechnicianID)
                    VALUES (%s, %s, NULL, NULL, NULL)
                """, (request_id, test_id))
                total_price += float(self.test_checkboxes[test_id][2])

            # Immediately queue a pending billing payment record for the receptionist
            cursor.execute("""
                INSERT INTO Payment (PatientID, Amount, PaymentType, ServiceID, LabRequestID, DispensingID, PaymentMethod, PaymentDate, BilledBy)
                VALUES (%s, %s, 'Laboratory', NULL, %s, NULL, 'Pending', CURRENT_TIMESTAMP, %s)
            """, (self.patient_id, total_price, request_id, self.doctor_worker_id))

            conn.commit()
            conn.close()
            
            # Write audit log
            import session
            user_id = session.current_user.get("user_id", 1) if (session and session.current_user) else 1
            from database import log_audit_action
            log_audit_action(user_id, f"Doctor requested laboratory tests (RequestID: {request_id}) and billed Le {total_price:,.2f} for PatientID: {self.patient_id}")
            
            for test_id in selected_tests:
                self.test_checkboxes[test_id][0].set(False)

            messagebox.showinfo("Success", "Laboratory request sent successfully and billed to Receptionist!")
            self.load_lab_requests()
            self.check_pending_lab_status()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to submit laboratory request:\n{e}")

    def setup_diagnosis_tab(self):
        main_diag_frame = ctk.CTkFrame(self.tab_diagnosis, fg_color="transparent")
        main_diag_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_panel = ctk.CTkFrame(main_diag_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(left_panel, text="Diagnosis Details:", font=("Arial", 13, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        self.diag_entry = ctk.CTkTextbox(left_panel, height=100)
        self.diag_entry.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(left_panel, text="Treatment Advice / Details:", font=("Arial", 13, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        self.treat_advice_entry = ctk.CTkTextbox(left_panel, height=100)
        self.treat_advice_entry.pack(fill="x", padx=20, pady=5)

        dates_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        dates_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(dates_frame, text="Start Date:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="e", padx=5)
        self.start_date_entry = ctk.CTkEntry(dates_frame, width=150)
        self.start_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.start_date_entry.grid(row=0, column=1, sticky="w", padx=5)

        ctk.CTkLabel(dates_frame, text="End Date:", font=("Arial", 12, "bold")).grid(row=0, column=2, sticky="e", padx=5)
        self.end_date_entry = ctk.CTkEntry(dates_frame, width=150)
        self.end_date_entry.insert(0, (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))
        self.end_date_entry.grid(row=0, column=3, sticky="w", padx=5)

        right_panel = ctk.CTkFrame(main_diag_frame, width=450)
        right_panel.pack(side="right", fill="both", padx=(5, 0))
        right_panel.pack_propagate(False)

        ctk.CTkLabel(right_panel, text="💊 Prescribe Medications", font=("Arial", 14, "bold"), text_color="#1F6AA5").pack(pady=5)
        
        ctk.CTkLabel(right_panel, text="Select Drug from Stock:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=2)
        self.med_combo = ctk.CTkComboBox(right_panel, width=400, values=[])
        self.med_combo.pack(padx=20, pady=5)
        
        self.load_inventory_meds()

        ctk.CTkLabel(right_panel, text="Dosage Instructions:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=2)
        self.dosage_entry = ctk.CTkEntry(right_panel, width=400, placeholder_text="e.g. 1 tab twice daily")
        self.dosage_entry.insert(0, "1 tablet daily")
        self.dosage_entry.pack(padx=20, pady=5)

        ctk.CTkLabel(right_panel, text="Quantity to Issue:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=2)
        self.qty_entry = ctk.CTkEntry(right_panel, width=400, placeholder_text="e.g. 10")
        self.qty_entry.insert(0, "10")
        self.qty_entry.pack(padx=20, pady=5)

        presc_btn_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        presc_btn_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(presc_btn_frame, text="➕ Add Drug", command=self.add_prescription_item, width=190).pack(side="left", padx=5)
        ctk.CTkButton(presc_btn_frame, text="❌ Remove Drug", fg_color="red", hover_color="#b71c1c", command=self.remove_prescription_item, width=190).pack(side="right", padx=5)

        self.presc_tree = self.create_tree(right_panel, ("Medicine Name", "Dosage", "Qty"))
        self.presc_tree.pack(fill="both", expand=True, padx=20, pady=10)

        self.finalize_btn = ctk.CTkButton(left_panel, text="💾 Finalize Consultation & Print Prescription", font=("Arial", 14, "bold"), height=45, fg_color="#4CAF50", hover_color="#43A047", command=self.finalize_consultation)
        self.finalize_btn.pack(pady=20, padx=20, fill="x")

        self.check_pending_lab_status()

    def load_inventory_meds(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT MedicineName, Quantity, SellingPrice FROM Inventory WHERE Quantity > 0")
            rows = cursor.fetchall()
            conn.close()
            
            med_list = [f"{name} (Stock: {qty} | Le {sell:,.2f})" for name, qty, sell in rows]
            self.med_combo.configure(values=med_list)
            if med_list:
                self.med_combo.set(med_list[0])
        except Exception as e:
            print(f"Error loading inventory meds: {e}")

    def add_prescription_item(self):
        med_val = self.med_combo.get()
        dosage = self.dosage_entry.get().strip()
        qty_str = self.qty_entry.get().strip()

        if not med_val:
            messagebox.showerror("Error", "No medicine selected.")
            return
        if not dosage:
            messagebox.showerror("Error", "Please fill in the dosage instruction.")
            return
        if not qty_str:
            messagebox.showerror("Error", "Please fill in the quantity.")
            return

        try:
            qty = int(qty_str)
            if qty <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive integer.")
            return

        medicine_name = med_val.split(" (Stock:")[0].strip()

        self.prescriptions.append({
            "medicine_name": medicine_name,
            "dosage": dosage,
            "quantity": qty
        })
        
        self.presc_tree.insert("", "end", values=(medicine_name, dosage, qty))
        self.dosage_entry.delete(0, "end")
        self.dosage_entry.insert(0, "1 tablet daily")
        self.qty_entry.delete(0, "end")
        self.qty_entry.insert(0, "10")

    def remove_prescription_item(self):
        selected = self.presc_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Warning", "Please select a drug item to remove.")
            return
            
        row = self.presc_tree.item(selected[0], "values")
        med_name = row[0]
        
        self.prescriptions = [item for item in self.prescriptions if item["medicine_name"] != med_name]
        self.presc_tree.delete(selected[0])

    def finalize_consultation(self):
        diag_details = self.diag_entry.get("1.0", "end").strip()
        treat_details = self.treat_advice_entry.get("1.0", "end").strip()
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()

        if not diag_details:
            messagebox.showerror("Validation Error", "Please provide diagnosis details.")
            return
        if not treat_details:
            messagebox.showerror("Validation Error", "Please provide treatment advice.")
            return
        if not start_date or not end_date:
            messagebox.showerror("Validation Error", "Start and End dates are required.")
            return

        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid date format. Please use YYYY-MM-DD.")
            return

        confirm = messagebox.askyesno("Finalize", "Are you sure you want to finalize this consultation?")
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT RequestID FROM Laboratory_Requests 
                WHERE PatientID = %s AND AppointmentID = %s AND Status = 'Completed'
                ORDER BY RequestID DESC LIMIT 1
            """, (self.patient_id, self.appointment_id))
            lab_req_row = cursor.fetchone()
            lab_request_id = lab_req_row[0] if lab_req_row else None

            cursor.execute("""
                INSERT INTO Diagnosis (AppointmentID, PatientID, DoctorID, DiagnosisDetails, DiagnosisDate, LabRequestID)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, %s)
            """, (self.appointment_id, self.patient_id, self.doctor_worker_id, diag_details, lab_request_id))
            diagnosis_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO Treatment (DiagnosisID, PatientID, DoctorID, TreatmentDetails, StartDate, EndDate, Status)
                VALUES (%s, %s, %s, %s, %s, %s, 'Active')
            """, (diagnosis_id, self.patient_id, self.doctor_worker_id, treat_details, start_date, end_date))
            treatment_id = cursor.lastrowid

            for item in self.prescriptions:
                cursor.execute("""
                    INSERT INTO Prescription (TreatmentID, PatientID, DoctorID, MedicineName, Dosage, QuantityPrescribed, Status)
                    VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
                """, (treatment_id, self.patient_id, self.doctor_worker_id, item["medicine_name"], item["dosage"], item["quantity"]))

            cursor.execute("""
                UPDATE Appointments SET Status = 'Completed' WHERE AppointmentID = %s
            """, (self.appointment_id,))

            conn.commit()
            conn.close()
 
            # Write audit logs for Diagnosis, Treatment and Prescriptions
            import session
            user_id = session.current_user.get("user_id", 1) if (session and session.current_user) else 1
            from database import log_audit_action
            log_audit_action(user_id, f"Recorded diagnosis (DiagnosisID: {diagnosis_id}) for PatientID: {self.patient_id}")
            log_audit_action(user_id, f"Recorded treatment (TreatmentID: {treatment_id}) for PatientID: {self.patient_id}")
            if self.prescriptions:
                log_audit_action(user_id, f"Created prescription for TreatmentID: {treatment_id} (Medicines: {[m['medicine_name'] for m in self.prescriptions]})")
 
            messagebox.showinfo("Success", "Patient consultation finalized successfully!")
            self.parent.refresh_dashboard()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save consultation details:\n{e}")
