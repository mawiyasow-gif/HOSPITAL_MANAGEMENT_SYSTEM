import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from database import connect_db
import os

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


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

        # Retrieve Doctor's Health Worker ID based on their Full Name or Username
        self.doctor_worker_id = self.get_doctor_worker_id()

        # ==============================
        # Main Layout Container
        # ==============================
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True)

        # ==============================
        # Left Sidebar (Navigation)
        # ==============================
        self.sidebar = ctk.CTkFrame(self.main_container, width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Sidebar Title Logo
        sidebar_title = ctk.CTkLabel(
            self.sidebar,
            text="🏥 DOCTOR PANEL",
            font=("Arial", 22, "bold"),
            text_color="#1F6AA5"
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
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                width=210,
                height=45,
                font=("Arial", 15, "bold"),
                anchor="w",
                command=command
            )
            btn.pack(pady=6)

        # ==============================
        # Right View Area (Scrollable)
        # ==============================
        self.content_frame = ctk.CTkFrame(self.main_container, corner_radius=0)
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.scrollable_frame = ctk.CTkScrollableFrame(self.content_frame, corner_radius=0)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ==============================
        # Header Info Bar
        # ==============================
        self.header_frame = ctk.CTkFrame(self.scrollable_frame)
        self.header_frame.pack(fill="x", pady=(0, 10))

        info_text = (
            f"🩺 {self.doctor_user['full_name']} | Employee ID: DOC-{self.doctor_worker_id}\n"
            f"Specialization: {self.doctor_user.get('specialization', 'General Physician')}"
        )
        self.info_lbl = ctk.CTkLabel(
            self.header_frame,
            text=info_text,
            font=("Arial", 14, "bold"),
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
            text_color="gray"
        )
        self.date_lbl.pack()

        self.time_lbl = ctk.CTkLabel(
            self.clock_frame,
            text="00:00:00",
            font=("Arial", 20, "bold"),
            text_color="#1F6AA5"
        )
        self.time_lbl.pack()

        # Start live clock update
        self.update_clock()

        # ==============================
        # Statistics Dashboard Cards
        # ==============================
        self.cards_frame = ctk.CTkFrame(self.scrollable_frame)
        self.cards_frame.pack(fill="x", pady=10)

        # 3 Cards Row 1
        cards_row1 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        cards_row1.pack(fill="x", pady=5)

        self.assigned_patients_card = self.create_stat_card(cards_row1, "👥", "Assigned Patients", "0", "#4CAF50")
        self.assigned_patients_card.pack(side="left", padx=5, expand=True, fill="x")

        self.today_appointments_card = self.create_stat_card(cards_row1, "📅", "Today's Appointments", "0", "#2196F3")
        self.today_appointments_card.pack(side="left", padx=5, expand=True, fill="x")

        self.diagnoses_card = self.create_stat_card(cards_row1, "🩺", "Diagnoses Completed", "0", "#9C27B0")
        self.diagnoses_card.pack(side="left", padx=5, expand=True, fill="x")

        # 3 Cards Row 2
        cards_row2 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        cards_row2.pack(fill="x", pady=5)

        self.treatments_card = self.create_stat_card(cards_row2, "💊", "Treatments Prescribed", "0", "#E91E63")
        self.treatments_card.pack(side="left", padx=5, expand=True, fill="x")

        self.pending_app_card = self.create_stat_card(cards_row2, "⏳", "Pending Appointments", "0", "#FF9800")
        self.pending_app_card.pack(side="left", padx=5, expand=True, fill="x")

        self.completed_consult_card = self.create_stat_card(cards_row2, "✅", "Completed Consultations", "0", "#00BCD4")
        self.completed_consult_card.pack(side="left", padx=5, expand=True, fill="x")

        # ==============================
        # Action Center & Notifications Split
        # ==============================
        self.action_split_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.action_split_frame.pack(fill="x", pady=10)

        # Quick Actions
        self.actions_frame = ctk.CTkFrame(self.action_split_frame)
        self.actions_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(self.actions_frame, text="⚡ Quick Action Center", font=("Arial", 16, "bold")).pack(pady=10)

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

    def create_stat_card(self, parent, icon, title, value, color):
        """Create a statistics card with a clean left accent bar to look professional."""
        card = ctk.CTkFrame(parent, corner_radius=10)
        accent_bar = ctk.CTkFrame(card, width=5, corner_radius=2, fg_color=color)
        accent_bar.pack(side="left", fill="y", padx=(10, 5), pady=10)

        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(5, 2))

        icon_label = ctk.CTkLabel(header_frame, text=icon, font=("Arial", 18))
        icon_label.pack(side="left")

        title_label = ctk.CTkLabel(header_frame, text=f"  {title}", font=("Arial", 11, "bold"), text_color=("#4A5568", "#CBD5E0"))
        title_label.pack(side="left")

        value_label = ctk.CTkLabel(content_frame, text=value, font=("Arial", 22, "bold"), text_color="#1F6AA5", anchor="w")
        value_label.pack(fill="x", pady=(2, 5))

        card.value_label = value_label
        return card

    def create_recent_table_frame(self, parent, title, columns):
        """Create a frame containing styled Treeview table."""
        frame = ctk.CTkFrame(parent)
        ctk.CTkLabel(frame, text=title, font=("Arial", 14, "bold"), text_color="#1F6AA5").pack(pady=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            rowheight=30,
            font=("Arial", 11)
        )
        style.map("Treeview", background=[("selected", "#1F6AA5")], foreground=[("selected", "white")])

        table = ttk.Treeview(frame, columns=columns, show="headings", height=6)
        for col in columns:
            table.heading(col, text=col, anchor="center")
            table.column(col, width=120, anchor="center")

        v_scroll = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=v_scroll.set)

        table.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

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
            cursor.execute("SELECT COUNT(*) FROM Diagnosis WHERE WorkerID = %s", (self.doctor_worker_id,))
            diag_count = cursor.fetchone()[0]
            self.diagnoses_card.value_label.configure(text=str(diag_count))

            # 4. Treatments Prescribed
            cursor.execute("SELECT COUNT(*) FROM Treatment WHERE WorkerID = %s", (self.doctor_worker_id,))
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
                WHERE a.WorkerID = %s AND a.AppointmentDate = CURDATE() AND a.Status = 'Pending'
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
                SELECT d.DiagnosisID, pat.FullName, d.Description, d.DiagnosisDate
                FROM Diagnosis d
                LEFT JOIN Patients pat ON d.PatientID = pat.PatientID
                WHERE d.WorkerID = %s
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
            cursor.execute("SELECT ItemName, Stock FROM Inventory WHERE Stock < 5 LIMIT 3")
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

    def on_unattended_select(self, event):
        """Enable the attend button when a patient is selected in the unattended queue."""
        selected = self.today_app_table.table.selection()
        if selected:
            self.attend_btn.configure(state="normal", fg_color="#4CAF50")
        else:
            self.attend_btn.configure(state="disabled", fg_color="gray")

    def attend_patient(self):
        """Mark the selected pending appointment as Completed and open DiagnosisWindow."""
        selected = self.today_app_table.table.selection()
        if not selected:
            messagebox.showwarning("Selection Warning", "Please select a patient appointment from the queue.")
            return

        row = self.today_app_table.table.item(selected[0], "values")
        if not row:
            return

        appointment_id = row[0]
        patient_name = row[1]

        confirm = messagebox.askyesno(
            "Attend Patient",
            f"Would you like to attend to {patient_name} and mark their consultation as completed?"
        )
        if confirm:
            try:
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Appointments SET Status = 'Completed' WHERE AppointmentID = %s",
                    (appointment_id,)
                )
                conn.commit()
                conn.close()

                messagebox.showinfo("Success", f"{patient_name}'s consultation is marked as completed.")
                self.refresh_dashboard()

                # Automatically open DiagnosisWindow to record details
                self.open_diagnosis()
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to update appointment status:\n{e}")

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
                SELECT d.DiagnosisID, d.DiagnosisDate, d.Description, w.FullName
                FROM Diagnosis d
                LEFT JOIN Health_Workers w ON d.WorkerID = w.WorkerID
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
