import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from database import connect_db

# Set appearance mode and color theme
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class ReceptionistDashboard(ctk.CTk):
    """Receptionist Dashboard for Physical Health Clinic Record System."""

    def __init__(self, receptionist_user=None):
        super().__init__()

        # Window Settings
        self.title("Physical Health Clinic System - Receptionist Dashboard")
        self.geometry("1600x900")
        self.resizable(True, True)

        # Store session user details
        self.receptionist_user = receptionist_user or {
            "user_id": 3,
            "worker_id": 5,
            "full_name": "Receptionist Staff",
            "role": "Receptionist"
        }

        # Initialize Notification Queue / List
        self.notifications = [
            "📋 Welcome to the Receptionist Control Panel.",
            "🔔 Waiting Patient Alert: Please manage the queue below."
        ]

        # ==========================================
        # Main Layout Frame
        # ==========================================
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True)

        # ==========================================
        # Sidebar (Left Navigation)
        # ==========================================
        self.sidebar = ctk.CTkFrame(self.main_container, width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Sidebar Title
        sidebar_title = ctk.CTkLabel(
            self.sidebar,
            text="🏥 RECEPTION PANEL",
            font=("Arial", 20, "bold"),
            text_color="#1F6AA5"
        )
        sidebar_title.pack(pady=(30, 20))

        # Menu Items configuration
        menu_items = [
            ("🏠 Dashboard", self.refresh_dashboard),
            ("👥 Patients", self.open_patients),
            ("📅 Appointments", self.open_appointments),
            ("💳 Payments", self.open_payments),
            ("🧾 Receipts", self.open_receipts),
            ("📋 Queue Management", self.open_queue),
            ("👤 My Profile", self.open_profile),
            ("🚪 Logout", self.logout)
        ]

        # Instantiating navigation buttons in the sidebar
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
                btn.pack(side="bottom", pady=25)
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

        # ==========================================
        # Right View Area (Scrollable Main View)
        # ==========================================
        self.content_frame = ctk.CTkFrame(self.main_container, corner_radius=0)
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.scrollable_frame = ctk.CTkScrollableFrame(self.content_frame, corner_radius=0)
        self.scrollable_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # ==========================================
        # Header Info Bar
        # ==========================================
        self.header_frame = ctk.CTkFrame(self.scrollable_frame)
        self.header_frame.pack(fill="x", pady=(0, 10))

        # Clinic Branding & Logged In User Info
        welcome_text = f"👋 Welcome, {self.receptionist_user['full_name']} (Receptionist)"
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

        # Start live digital clock updates
        self.update_clock()

        # ==========================================
        # Clickable Stat Cards Row
        # ==========================================
        self.cards_frame = ctk.CTkFrame(self.scrollable_frame)
        self.cards_frame.pack(fill="x", pady=10)

        cards_row = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        cards_row.pack(fill="x", pady=5)

        # Stat cards linked to their respective modules via commands
        self.patients_card = self.create_stat_card(
            cards_row, "👥", "Total Patients", "0", "#4CAF50", self.open_patients
        )
        self.patients_card.pack(side="left", padx=5, expand=True, fill="x")

        self.appointments_card = self.create_stat_card(
            cards_row, "📅", "Today's Appointments", "0", "#2196F3", self.open_appointments
        )
        self.appointments_card.pack(side="left", padx=5, expand=True, fill="x")

        self.waiting_card = self.create_stat_card(
            cards_row, "⏳", "Waiting Patients", "0", "#FF9800", self.open_queue
        )
        self.waiting_card.pack(side="left", padx=5, expand=True, fill="x")

        self.payments_card = self.create_stat_card(
            cards_row, "💳", "Today's Payments", "Le 0.00", "#E91E63", self.open_payments
        )
        self.payments_card.pack(side="left", padx=5, expand=True, fill="x")

        self.receipts_card = self.create_stat_card(
            cards_row, "🧾", "Receipts Generated Today", "0", "#9C27B0", self.open_receipts
        )
        self.receipts_card.pack(side="left", padx=5, expand=True, fill="x")

        # ==========================================
        # Quick Actions Section
        # ==========================================
        self.actions_frame = ctk.CTkFrame(self.scrollable_frame)
        self.actions_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(self.actions_frame, text="⚡ Quick Action Center", font=("Arial", 16, "bold")).pack(pady=10)

        actions_row = ctk.CTkFrame(self.actions_frame, fg_color="transparent")
        actions_row.pack(fill="x", padx=10, pady=10)

        actions = [
            ("👥 Register Patient", self.open_patients),
            ("📅 Book Appointment", self.open_appointments),
            ("💳 Record Payment", self.open_payments),
            ("🧾 Generate Receipt", self.open_receipts),
            ("📋 Manage Queue", self.open_queue)
        ]

        for text, command in actions:
            btn = ctk.CTkButton(
                actions_row,
                text=text,
                width=180,
                height=45,
                font=("Arial", 13, "bold"),
                command=command
            )
            btn.pack(side="left", padx=15, expand=True)

        # ==========================================
        # Patient Quick Search Section
        # ==========================================
        self.search_section_frame = ctk.CTkFrame(self.scrollable_frame)
        self.search_section_frame.pack(fill="x", pady=10)

        search_header = ctk.CTkFrame(self.search_section_frame, fg_color="transparent")
        search_header.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(search_header, text="🔍 Patient Quick Search:", font=("Arial", 14, "bold")).pack(side="left", padx=5)
        
        self.search_entry = ctk.CTkEntry(
            search_header,
            placeholder_text="Enter Patient ID, Full Name, or Phone Number...",
            width=400
        )
        self.search_entry.pack(side="left", padx=10)
        self.search_entry.bind("<KeyRelease>", self.search_patients)

        ctk.CTkButton(search_header, text="Clear Search", width=100, command=self.clear_search).pack(side="left", padx=5)

        # Dynamic Search Results Table Frame
        self.search_results_frame = ctk.CTkFrame(self.search_section_frame, height=180)
        self.search_results_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.search_results_frame.pack_propagate(False)

        columns_search = ("ID", "Full Name", "Gender", "Phone Number", "Address")
        self.search_table = ttk.Treeview(self.search_results_frame, columns=columns_search, show="headings", height=4)
        for col in columns_search:
            self.search_table.heading(col, text=col, anchor="center")
            self.search_table.column(col, width=120, anchor="center")
        self.search_table.column("Full Name", width=180)

        v_scroll_search = ttk.Scrollbar(self.search_results_frame, orient="vertical", command=self.search_table.yview)
        self.search_table.configure(yscrollcommand=v_scroll_search.set)
        self.search_table.pack(side="left", fill="both", expand=True)
        v_scroll_search.pack(side="right", fill="y")

        # ==========================================
        # Split Data Tables Grid Layout
        # ==========================================
        self.grid_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.grid_frame.pack(fill="x", pady=10)

        # Left Column: Today's Appointments & Queue
        self.left_col = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
        self.left_col.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Today's Appointments Table
        self.today_app_frame = self.create_table_frame(
            self.left_col, 
            "📅 Today's Appointments Calendar", 
            ("ID", "Patient Name", "Assigned Doctor", "Time", "Status"),
            height=7
        )
        self.today_app_frame.pack(fill="x", pady=(0, 10))

        # Patient Queue Panel (Call Next / Completed actions)
        self.queue_frame = ctk.CTkFrame(self.left_col)
        self.queue_frame.pack(fill="x")
        
        ctk.CTkLabel(
            self.queue_frame, 
            text="📋 Today's Waiting Patient Queue", 
            font=("Arial", 14, "bold"), 
            text_color="#1F6AA5"
        ).pack(anchor="w", padx=15, pady=8)

        # Queue Table
        columns_queue = ("Queue ID", "Patient Name", "App. Time", "Status")
        self.queue_table = ttk.Treeview(self.queue_frame, columns=columns_queue, show="headings", height=5)
        for col in columns_queue:
            self.queue_table.heading(col, text=col, anchor="center")
            self.queue_table.column(col, width=100, anchor="center")
        self.queue_table.column("Patient Name", width=150)

        v_scroll_q = ttk.Scrollbar(self.queue_frame, orient="vertical", command=self.queue_table.yview)
        self.queue_table.configure(yscrollcommand=v_scroll_q.set)
        self.queue_table.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=5)
        v_scroll_q.pack(side="right", fill="y", pady=5, padx=(0, 15))

        # Queue Action Bar
        queue_actions = ctk.CTkFrame(self.queue_frame, fg_color="transparent")
        queue_actions.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(
            queue_actions, 
            text="🔊 Call Next Patient", 
            fg_color="#4CAF50", 
            hover_color="#43A047", 
            font=("Arial", 12, "bold"),
            command=self.call_next_patient
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            queue_actions, 
            text="✅ Mark As Completed", 
            fg_color="#2196F3", 
            hover_color="#1E88E5", 
            font=("Arial", 12, "bold"),
            command=self.mark_completed
        ).pack(side="left", padx=5)

        # Right Column: Recent Patients, Recent Payments & Notifications
        self.right_col = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
        self.right_col.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Recent Patients Table
        self.recent_patients_frame = self.create_table_frame(
            self.right_col, 
            "👥 Latest Registered Patients", 
            ("ID", "Full Name", "Gender", "Phone Number", "Reg Date"),
            height=5
        )
        self.recent_patients_frame.pack(fill="x", pady=(0, 10))

        # Recent Payments Table
        self.recent_payments_frame = self.create_table_frame(
            self.right_col, 
            "💳 Recent Payments Processed", 
            ("ID", "Patient Name", "Amount", "Method", "Date"),
            height=5
        )
        self.recent_payments_frame.pack(fill="x", pady=(0, 10))

        # Notifications Log Area
        self.notif_panel = ctk.CTkFrame(self.right_col)
        self.notif_panel.pack(fill="x")

        ctk.CTkLabel(
            self.notif_panel, 
            text="🔔 Waiting Alert & Activity Log", 
            font=("Arial", 14, "bold"), 
            text_color="#1F6AA5"
        ).pack(anchor="w", padx=15, pady=5)

        self.notif_text = ctk.CTkTextbox(self.notif_panel, height=95)
        self.notif_text.pack(fill="x", padx=15, pady=5)
        self.notif_text.configure(state="disabled")

        # Initial Load of all statistics & tables
        self.refresh_dashboard()

    # ==========================================
    # Helper Layout Utilities
    # ==========================================

    def create_stat_card(self, parent, icon, title, value, color, command=None):
        """Create a clickable statistics card with accent colors."""
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

    def create_table_frame(self, parent, title, columns, height=6):
        """Standard styled Treeview table container frame."""
        frame = ctk.CTkFrame(parent)
        ctk.CTkLabel(frame, text=title, font=("Arial", 14, "bold"), text_color="#1F6AA5").pack(pady=5, anchor="w", padx=15)

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

        table = ttk.Treeview(frame, columns=columns, show="headings", height=height)
        for col in columns:
            table.heading(col, text=col, anchor="center")
            table.column(col, width=100, anchor="center")

        if "Patient Name" in columns:
            table.column("Patient Name", width=140)
        if "Assigned Doctor" in columns:
            table.column("Assigned Doctor", width=140)

        v_scroll = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=v_scroll.set)

        table.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=5)
        v_scroll.pack(side="right", fill="y", pady=5, padx=(0, 15))

        frame.table = table
        return frame

    # ==========================================
    # Clock & Live Updates
    # ==========================================

    def update_clock(self):
        """Update live clock and date display."""
        now = datetime.now()
        self.time_lbl.configure(text=now.strftime("%H:%M:%S"))
        self.date_lbl.configure(text=now.strftime("%A, %d %B %Y"))
        self.after(1000, self.update_clock)

    # ==========================================
    # Clinical Log & Notifications
    # ==========================================

    def append_notification(self, text):
        """Add notification entry to the active UI log panel."""
        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        self.notifications.insert(0, timestamp + text)
        if len(self.notifications) > 10:
            self.notifications.pop()
        
        self.notif_text.configure(state="normal")
        self.notif_text.delete("1.0", "end")
        self.notif_text.insert("1.0", "\n".join(self.notifications))
        self.notif_text.configure(state="disabled")

    # ==========================================
    # Core Data Loading Methods
    # ==========================================

    def load_dashboard_statistics(self):
        """Fetch and populate cards with aggregate metrics from MySQL."""
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # 1. Total patients
            cursor.execute("SELECT COUNT(*) FROM Patients")
            self.patients_card.value_label.configure(text=str(cursor.fetchone()[0]))

            # 2. Today's Appointments
            cursor.execute("SELECT COUNT(*) FROM Appointments WHERE AppointmentDate = CURDATE()")
            self.appointments_card.value_label.configure(text=str(cursor.fetchone()[0]))

            # 3. Waiting Patients
            cursor.execute("SELECT COUNT(*) FROM Appointments WHERE Status = 'Pending' AND AppointmentDate = CURDATE()")
            self.waiting_card.value_label.configure(text=str(cursor.fetchone()[0]))

            # 4. Payments received today
            cursor.execute("SELECT SUM(Amount) FROM Payment WHERE DATE(PaymentDate) = CURDATE()")
            total_pay = cursor.fetchone()[0] or 0
            self.payments_card.value_label.configure(text=f"Le {total_pay:,.2f}")

            # 5. Receipts generated today
            cursor.execute("SELECT COUNT(*) FROM Receipt WHERE DATE(IssueDate) = CURDATE()")
            self.receipts_card.value_label.configure(text=str(cursor.fetchone()[0]))

            conn.close()
        except Exception as e:
            print(f"Error loading stats: {e}")

    def load_today_appointments(self):
        """Render all calendar appointments for today."""
        table = self.today_app_frame.table
        for item in table.get_children():
            table.delete(item)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT a.AppointmentID, p.FullName, hw.FullName, a.AppointmentTime, a.Status
                FROM Appointments a
                LEFT JOIN Patients p ON a.PatientID = p.PatientID
                LEFT JOIN Health_Workers hw ON a.WorkerID = hw.WorkerID
                WHERE a.AppointmentDate = CURDATE()
                ORDER BY a.AppointmentTime ASC
            """
            cursor.execute(query)
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error loading today's appointments: {e}")

    def load_patient_queue(self):
        """Render the waiting queue queue table."""
        for item in self.queue_table.get_children():
            self.queue_table.delete(item)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT a.AppointmentID, p.FullName, a.AppointmentTime, a.Status
                FROM Appointments a
                LEFT JOIN Patients p ON a.PatientID = p.PatientID
                WHERE a.AppointmentDate = CURDATE() AND a.Status = 'Pending'
                ORDER BY a.AppointmentTime ASC
            """
            cursor.execute(query)
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                self.queue_table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error loading queue: {e}")

    def load_recent_patients(self):
        """Render recent registration records."""
        table = self.recent_patients_frame.table
        for item in table.get_children():
            table.delete(item)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT PatientID, FullName, Gender, PhoneNumber, DATE(RegistrationDate)
                FROM Patients
                ORDER BY PatientID DESC
                LIMIT 5
            """
            cursor.execute(query)
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error loading recent patients: {e}")

    def load_recent_payments(self):
        """Render recent transaction logs."""
        table = self.recent_payments_frame.table
        for item in table.get_children():
            table.delete(item)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT py.PaymentID, pt.FullName, py.Amount, py.PaymentMethod, DATE(py.PaymentDate)
                FROM Payment py
                LEFT JOIN Patients pt ON py.PatientID = pt.PatientID
                ORDER BY py.PaymentID DESC
                LIMIT 5
            """
            cursor.execute(query)
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                cleaned[2] = f"Le {float(cleaned[2]):,.2f}" if cleaned[2] else "Le 0.00"
                table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error loading recent payments: {e}")

    # ==========================================
    # Interactive Search
    # ==========================================

    def search_patients(self, event=None):
        """Dynamic text-search against database records."""
        query_str = self.search_entry.get().strip()
        for item in self.search_table.get_children():
            self.search_table.delete(item)

        if not query_str:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT PatientID, FullName, Gender, PhoneNumber, Address
                FROM Patients
                WHERE PatientID LIKE %s OR FullName LIKE %s OR PhoneNumber LIKE %s
                LIMIT 5
            """
            val = f"%{query_str}%"
            cursor.execute(query, (val, val, val))
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                self.search_table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error searching patients: {e}")

    def clear_search(self):
        """Reset the search entry field and clear query results."""
        self.search_entry.delete(0, "end")
        for item in self.search_table.get_children():
            self.search_table.delete(item)

    # ==========================================
    # Queue Action Operations
    # ==========================================

    def call_next_patient(self):
        """Retrieve the next pending patient and broadcast notice."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT a.AppointmentID, p.FullName, hw.FullName, a.AppointmentTime
                FROM Appointments a
                LEFT JOIN Patients p ON a.PatientID = p.PatientID
                LEFT JOIN Health_Workers hw ON a.WorkerID = hw.WorkerID
                WHERE a.AppointmentDate = CURDATE() AND a.Status = 'Pending'
                ORDER BY a.AppointmentTime ASC
                LIMIT 1
            """
            cursor.execute(query)
            row = cursor.fetchone()
            conn.close()

            if row:
                app_id, patient_name, doctor_name, app_time = row
                msg = f"📣 CALLING NEXT: {patient_name} to see {doctor_name} (Scheduled: {app_time})"
                self.append_notification(msg)
                messagebox.showinfo("Patient Called", msg)
            else:
                messagebox.showinfo("Queue Empty", "No pending patients waiting in today's queue.")
        except Exception as e:
            messagebox.showerror("Queue Error", f"Failed to call next patient:\n{e}")

    def mark_completed(self):
        """Set a queue appointment as completed."""
        selected = self.queue_table.selection()
        if not selected:
            messagebox.showwarning("Selection Warning", "Please select a patient from the waiting queue table.")
            return

        row = self.queue_table.item(selected[0], "values")
        appointment_id = row[0]
        patient_name = row[1]

        confirm = messagebox.askyesno(
            "Confirm Status", 
            f"Are you sure you want to mark {patient_name}'s appointment as Completed?"
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
                
                self.append_notification(f"✅ Mark Completed: {patient_name}'s consultation finished.")
                self.refresh_dashboard()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update status:\n{e}")

    # ==========================================
    # Global Refresh
    # ==========================================

    def refresh_dashboard(self):
        """Reload all cards data, calendars, and queues."""
        self.load_dashboard_statistics()
        self.load_today_appointments()
        self.load_patient_queue()
        self.load_recent_patients()
        self.load_recent_payments()
        self.append_notification("🔄 Dashboard refresh successfully completed.")

    # ==========================================
    # Navigation Openers
    # ==========================================

    def open_patients(self):
        from patients import PatientWindow
        PatientWindow(self)

    def open_appointments(self):
        from appointments import AppointmentWindow
        AppointmentWindow(self)

    def open_payments(self):
        from payment import PaymentWindow
        PaymentWindow(self)

    def open_receipts(self):
        from receipt import ReceiptWindow
        ReceiptWindow(self)

    def open_queue(self):
        """Open specialized patient queue window popup."""
        QueueWindow(self)

    def open_profile(self):
        """Open receptionist detailed account details."""
        ProfileWindow(self, self.receptionist_user)

    def logout(self):
        """Close dashboard and return back to LoginApp."""
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to exit the Reception Panel?")
        if confirm:
            self.destroy()
            from login import LoginApp
            app = LoginApp()
            app.mainloop()


# ==============================================================
# Helper Windows (Queue Management / Profile)
# ==============================================================

class QueueWindow(ctk.CTkToplevel):
    """Detailed Queue Management window popup."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Queue Management Portal")
        self.geometry("900x600")
        self.resizable(True, True)

        ctk.CTkLabel(
            self, 
            text="📋 Detailed Patient Queue Management", 
            font=("Arial", 20, "bold"), 
            text_color="#1F6AA5"
        ).pack(pady=15)

        # Container
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Styled Table showing today's waiting list
        columns = ("App ID", "Patient Name", "Assigned Doctor", "Time Slot", "Status")
        self.table = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=12)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=32, font=("Arial", 11))
        style.map("Treeview", background=[("selected", "#1F6AA5")], foreground=[("selected", "white")])

        for col in columns:
            self.table.heading(col, text=col, anchor="center")
            self.table.column(col, width=130, anchor="center")
        self.table.column("Patient Name", width=180)
        self.table.column("Assigned Doctor", width=180)

        v_scroll = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=v_scroll.set)
        
        self.table.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

        # Action Buttons
        actions_bar = ctk.CTkFrame(self, height=70)
        actions_bar.pack(fill="x", padx=20, pady=15)
        actions_bar.pack_propagate(False)

        ctk.CTkButton(
            actions_bar, 
            text="📣 Call Selected Patient", 
            font=("Arial", 13, "bold"), 
            fg_color="#4CAF50",
            command=self.call_selected
        ).pack(side="left", padx=10, pady=15)

        ctk.CTkButton(
            actions_bar, 
            text="✅ Set Status Completed", 
            font=("Arial", 13, "bold"), 
            fg_color="#2196F3",
            command=self.complete_selected
        ).pack(side="left", padx=10, pady=15)

        ctk.CTkButton(
            actions_bar, 
            text="Close Panel", 
            font=("Arial", 13), 
            command=self.destroy
        ).pack(side="right", padx=10, pady=15)

        self.load_queue_list()

    def load_queue_list(self):
        for item in self.table.get_children():
            self.table.delete(item)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT a.AppointmentID, p.FullName, hw.FullName, a.AppointmentTime, a.Status
                FROM Appointments a
                LEFT JOIN Patients p ON a.PatientID = p.PatientID
                LEFT JOIN Health_Workers hw ON a.WorkerID = hw.WorkerID
                WHERE a.AppointmentDate = CURDATE() AND a.Status = 'Pending'
                ORDER BY a.AppointmentTime ASC
            """
            cursor.execute(query)
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load queue details:\n{e}")

    def call_selected(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Selection Warning", "Please select a patient to call.")
            return

        row = self.table.item(selected[0], "values")
        patient_name = row[1]
        doctor_name = row[2]
        app_time = row[3]

        msg = f"📣 CALLING: {patient_name} to see {doctor_name} (Scheduled: {app_time})"
        messagebox.showinfo("Calling Patient", msg)
        
        # Log to parent dashboard notifications if it has the method
        if hasattr(self.master, "append_notification"):
            self.master.append_notification(msg)

    def complete_selected(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Selection Warning", "Please select a patient to complete.")
            return

        row = self.table.item(selected[0], "values")
        app_id = row[0]
        patient_name = row[1]

        confirm = messagebox.askyesno("Confirm Status", f"Mark appointment ID {app_id} for {patient_name} as Completed?")
        if confirm:
            try:
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("UPDATE Appointments SET Status = 'Completed' WHERE AppointmentID = %s", (app_id,))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", f"Appointment for {patient_name} marked as Completed!")
                self.load_queue_list()
                
                # Refresh parent dashboard
                if hasattr(self.master, "refresh_dashboard"):
                    self.master.refresh_dashboard()
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to update appointment:\n{e}")


class ProfileWindow(ctk.CTkToplevel):
    """Detailed Receptionist Account Profile widget."""

    def __init__(self, parent, user_session):
        super().__init__(parent)
        self.title("My Profile - Receptionist Panel")
        self.geometry("700x480")
        self.resizable(False, False)

        ctk.CTkLabel(
            self, 
            text="👤 Receptionist Profile Information", 
            font=("Arial", 22, "bold"), 
            text_color="#1F6AA5"
        ).pack(pady=20)

        main_panel = ctk.CTkFrame(self)
        main_panel.pack(fill="both", expand=True, padx=25, pady=10)

        # Profile Emoji Icon
        avatar_lbl = ctk.CTkLabel(main_panel, text="👩‍💻", font=("Arial", 80))
        avatar_lbl.grid(row=0, column=0, rowspan=6, padx=30, pady=20)

        # Get details from MySQL based on worker_id
        profile_details = {
            "Full Name": user_session["full_name"],
            "Employee ID": f"REC-{user_session['worker_id']}",
            "Phone Number": "N/A",
            "Email Address": "N/A",
            "Access Role": user_session["role"],
            "Last Login": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT hw.PhoneNumber, u.Email, u.LastLogin
                FROM Health_Workers hw
                LEFT JOIN Users u ON hw.UsersID = u.UsersID
                WHERE hw.WorkerID = %s
            """, (user_session["worker_id"],))
            row = cursor.fetchone()
            if row:
                if row[0]: profile_details["Phone Number"] = row[0]
                if row[1]: profile_details["Email Address"] = row[1]
                if row[2]: profile_details["Last Login"] = str(row[2])
            conn.close()
        except Exception as e:
            print(f"Error loading profile info: {e}")

        # Render fields dynamically
        for i, (label_key, val) in enumerate(profile_details.items()):
            ctk.CTkLabel(main_panel, text=label_key + ":", font=("Arial", 13, "bold")).grid(row=i, column=1, padx=10, pady=8, sticky="e")
            ctk.CTkLabel(main_panel, text=val, font=("Arial", 13)).grid(row=i, column=2, padx=10, pady=8, sticky="w")

        # Close
        ctk.CTkButton(self, text="Close Profile", width=150, command=self.destroy).pack(pady=15)


if __name__ == "__main__":
    app = ReceptionistDashboard()
    app.mainloop()
