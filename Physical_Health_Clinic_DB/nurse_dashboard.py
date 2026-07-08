import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from database import connect_db

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class NurseDashboard(ctk.CTk):
    """Nurse Dashboard for the Physical Health Clinic Record System."""

    def __init__(self, nurse_user=None):
        super().__init__()

        self.title("Physical Health Clinic Record System - Nurse Dashboard")
        self.geometry("1600x900")
        self.resizable(True, True)

        self.nurse_user = nurse_user or {
            "user_id": 4,
            "worker_id": 6,
            "full_name": "Nurse Staff",
            "role": "Nurse"
        }

        # Main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True)

        # Left Sidebar (Navigation)
        self.sidebar = ctk.CTkFrame(self.main_container, width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        sidebar_title = ctk.CTkLabel(
            self.sidebar,
            text="🏥 NURSE PANEL",
            font=("Arial", 20, "bold"),
            text_color="#1F6AA5"
        )
        sidebar_title.pack(pady=30)

        # Menu items for Nurse
        menu_items = [
            ("🏠 Dashboard", self.refresh_dashboard),
            ("👥 Patients", self.open_patients),
            ("🩺 Diagnosis", self.open_diagnosis),
            ("💊 Treatments", self.open_treatments),
            ("🚪 Logout", self.logout)
        ]

        for text, command in menu_items:
            if text == "🚪 Logout":
                btn = ctk.CTkButton(
                    self.sidebar,
                    text=text,
                    width=210,
                    height=45,
                    font=("Arial", 15, "bold"),
                    anchor="w",
                    fg_color="#D32F2F",
                    hover_color="#B71C1C",
                    command=command
                )
                btn.pack(side="bottom", pady=20)
            else:
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

        # Right View Area
        self.content_frame = ctk.CTkFrame(self.main_container, corner_radius=0)
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.scrollable_frame = ctk.CTkScrollableFrame(self.content_frame, corner_radius=0)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header Info Bar
        self.header_frame = ctk.CTkFrame(self.scrollable_frame)
        self.header_frame.pack(fill="x", pady=(0, 10))

        welcome_text = f"👋 Welcome Nurse {self.nurse_user['full_name']}"
        self.welcome_lbl = ctk.CTkLabel(
            self.header_frame,
            text=welcome_text,
            font=("Arial", 16, "bold"),
            text_color="#1F6AA5"
        )
        self.welcome_lbl.pack(side="left", padx=20, pady=15)

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

        self.update_clock()

        # ==============================
        # Clickable Stat Cards
        # ==============================
        self.cards_frame = ctk.CTkFrame(self.scrollable_frame)
        self.cards_frame.pack(fill="x", pady=10)

        cards_row = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        cards_row.pack(fill="x", pady=5)

        self.patients_card = self.create_stat_card(
            cards_row, "👥", "Total Patients", "0", "#4CAF50", self.open_patients
        )
        self.patients_card.pack(side="left", padx=5, expand=True, fill="x")

        self.today_appointments_card = self.create_stat_card(
            cards_row, "📅", "Today's Appointments", "0", "#2196F3", self.open_patients
        )
        self.today_appointments_card.pack(side="left", padx=5, expand=True, fill="x")

        self.diagnoses_card = self.create_stat_card(
            cards_row, "🩺", "Total Diagnoses", "0", "#9C27B0", self.open_diagnosis
        )
        self.diagnoses_card.pack(side="left", padx=5, expand=True, fill="x")

        self.treatments_card = self.create_stat_card(
            cards_row, "💊", "Total Treatments", "0", "#E91E63", self.open_treatments
        )
        self.treatments_card.pack(side="left", padx=5, expand=True, fill="x")

        # ==============================
        # Quick Actions
        # ==============================
        self.actions_frame = ctk.CTkFrame(self.scrollable_frame)
        self.actions_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(self.actions_frame, text="⚡ Quick Action Center", font=("Arial", 16, "bold")).pack(pady=10)

        actions_row = ctk.CTkFrame(self.actions_frame, fg_color="transparent")
        actions_row.pack(fill="x", padx=10, pady=10)

        actions = [
            ("👥 Register Patient", self.open_patients),
            ("🩺 Record Diagnosis", self.open_diagnosis),
            ("💊 Add Treatment", self.open_treatments)
        ]

        for text, command in actions:
            btn = ctk.CTkButton(
                actions_row,
                text=text,
                width=220,
                height=45,
                font=("Arial", 13, "bold"),
                command=command
            )
            btn.pack(side="left", padx=25, expand=True)

        # ==============================
        # Splitted Treeviews Section
        # ==============================
        self.data_split_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.data_split_frame.pack(fill="x", pady=10)

        # Left Column: Recent Patients
        self.left_col = ctk.CTkFrame(self.data_split_frame, fg_color="transparent")
        self.left_col.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.patients_table_frame = self.create_table_frame(self.left_col, "👥 Recent Patients", ("ID", "Name", "Gender", "Phone"))
        self.patients_table_frame.pack(fill="both", expand=True)

        # Right Column: Recent Diagnoses & Treatments
        self.right_col = ctk.CTkFrame(self.data_split_frame, fg_color="transparent")
        self.right_col.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.diagnoses_table_frame = self.create_table_frame(self.right_col, "🩺 Recent Diagnoses", ("ID", "Patient", "Description", "Date"))
        self.diagnoses_table_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.treatments_table_frame = self.create_table_frame(self.right_col, "💊 Recent Treatments", ("ID", "Patient", "Medicine", "Dosage", "Duration"))
        self.treatments_table_frame.pack(fill="both", expand=True)

        # Load data
        self.refresh_dashboard()

    def update_clock(self):
        self.time_lbl.configure(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self.update_clock)

    def create_stat_card(self, parent, icon, title, value, color, command=None):
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

        if command:
            card.configure(cursor="hand2")
            card.bind("<Button-1>", lambda e: command())
            accent_bar.bind("<Button-1>", lambda e: command())
            content_frame.bind("<Button-1>", lambda e: command())
            header_frame.bind("<Button-1>", lambda e: command())
            icon_label.bind("<Button-1>", lambda e: command())
            title_label.bind("<Button-1>", lambda e: command())
            value_label.bind("<Button-1>", lambda e: command())

        return card

    def create_table_frame(self, parent, title, columns):
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

        table = ttk.Treeview(frame, columns=columns, show="headings", height=5)
        for col in columns:
            table.heading(col, text=col, anchor="center")
            table.column(col, width=100, anchor="center")

        # Make description and medicine wider
        if "Description" in columns:
            table.column("Description", width=200, anchor="w")
        if "Medicine" in columns:
            table.column("Medicine", width=150, anchor="center")

        v_scroll = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=v_scroll.set)

        table.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

        frame.table = table
        return frame

    def refresh_dashboard(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Stats
            cursor.execute("SELECT COUNT(*) FROM Patients")
            self.patients_card.value_label.configure(text=str(cursor.fetchone()[0]))

            cursor.execute("SELECT COUNT(*) FROM Appointments WHERE AppointmentDate = CURDATE()")
            self.today_appointments_card.value_label.configure(text=str(cursor.fetchone()[0]))

            cursor.execute("SELECT COUNT(*) FROM Diagnosis")
            self.diagnoses_card.value_label.configure(text=str(cursor.fetchone()[0]))

            cursor.execute("SELECT COUNT(*) FROM Treatment")
            self.treatments_card.value_label.configure(text=str(cursor.fetchone()[0]))

            # Patients Table
            p_table = self.patients_table_frame.table
            for item in p_table.get_children():
                p_table.delete(item)
            cursor.execute("SELECT PatientID, FullName, Gender, PhoneNumber FROM Patients ORDER BY PatientID DESC LIMIT 5")
            for row in cursor.fetchall():
                p_table.insert("", "end", values=row)

            # Diagnoses Table
            d_table = self.diagnoses_table_frame.table
            for item in d_table.get_children():
                d_table.delete(item)
            cursor.execute("""
                SELECT d.DiagnosisID, p.FullName, d.Description, DATE(d.DiagnosisDate)
                FROM Diagnosis d
                LEFT JOIN Patients p ON d.PatientID = p.PatientID
                ORDER BY d.DiagnosisID DESC LIMIT 5
            """)
            for row in cursor.fetchall():
                d_table.insert("", "end", values=row)

            # Treatments Table
            t_table = self.treatments_table_frame.table
            for item in t_table.get_children():
                t_table.delete(item)
            cursor.execute("""
                SELECT t.TreatmentID, p.FullName, t.TreatmentName, t.Dosage, t.Duration
                FROM Treatment t
                LEFT JOIN Patients p ON t.PatientID = p.PatientID
                ORDER BY t.TreatmentID DESC LIMIT 5
            """)
            for row in cursor.fetchall():
                t_table.insert("", "end", values=row)

            conn.close()
        except Exception as e:
            print(f"Error loading nurse dashboard: {e}")

    def open_patients(self):
        from patients import PatientWindow
        PatientWindow(self)

    def open_diagnosis(self):
        from diagnosis import DiagnosisWindow
        DiagnosisWindow(self)

    def open_treatments(self):
        from treatment import TreatmentWindow
        TreatmentWindow(self)

    def logout(self):
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to log out?")
        if confirm:
            self.destroy()
            from login import LoginApp
            app = LoginApp()
            app.mainloop()

if __name__ == "__main__":
    app = NurseDashboard()
    app.mainloop()
