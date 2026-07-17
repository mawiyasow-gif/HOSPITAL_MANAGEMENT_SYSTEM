import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from database import connect_db
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import calendar

# Try to import matplotlib
try:
    import matplotlib
    matplotlib.use("TkAgg")
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False

# -----------------------------
# CustomTkinter Settings
# -----------------------------
import dashboard_theme

# Set appearance mode and color theme
dashboard_theme.apply_global_theme()


class AdminDashboard(ctk.CTk):
    """Administrator Dashboard for the Physical Health Clinic Record System."""

    def __init__(self, admin_user=None):
        super().__init__()

        self.title("Physical Health Clinic Record System - Administrator Dashboard")
        self.geometry("1600x900")
        self.resizable(True, True)

        # Store admin user information
        self.admin_user = admin_user or {"username": "Admin", "full_name": "Administrator", "role": "Administrator"}

        # ==============================
        # Main Container
        # ==============================
        self.main_container = ctk.CTkFrame(self, fg_color=dashboard_theme.BG_COLOR)
        self.main_container.pack(fill="both", expand=True)

        # ==============================
        # Sidebar (Left Navigation)
        # ==============================
        self.sidebar = ctk.CTkFrame(self.main_container, width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        dashboard_theme.style_sidebar(self.sidebar)

        # Sidebar Title
        sidebar_title = ctk.CTkLabel(
            self.sidebar,
            text="🏥 ADMIN PANEL",
            font=("Arial", 18, "bold"),
            text_color=dashboard_theme.TEXT_PRIMARY
        )
        sidebar_title.pack(pady=30)

        # Menu Items
        menu_items = [
            ("🏠 Dashboard", "open_dashboard"),
            ("👥 Patients", "open_patients"),
            ("👨‍⚕️ Health Workers", "open_health_workers"),
            ("📅 Appointments", "open_appointments"),
            ("🩺 Diagnosis", "open_diagnosis"),
            ("💊 Treatment", "open_treatment"),
            ("📦 Inventory", "open_inventory"),
            ("💳 Payment", "open_payment"),
            ("🧾 Receipt", "open_receipt"),
            ("📊 Reports", "open_reports"),
            ("🏥 Services Catalog", "open_services"),
            ("👤 User Management", "open_user_management"),
            ("⚙️ Settings", "open_settings")
        ]

        for item, command in menu_items:
            is_active = (item == "🏠 Dashboard")
            button = dashboard_theme.create_sidebar_button(
                self.sidebar,
                text=item,
                command=lambda cmd=command: getattr(self, cmd)(),
                active=is_active
            )
            button.pack(pady=4, padx=10)

        # Logout button packed at the bottom
        logout_button = ctk.CTkButton(
            self.sidebar,
            text="🚪 Logout",
            width=210,
            height=40,
            font=("Arial", 13, "bold"),
            anchor="w",
            fg_color=dashboard_theme.ACCENT_RED,
            hover_color="#B71C1C",
            command=self.logout
        )
        logout_button.pack(side="bottom", pady=15, padx=10)

        # ==============================
        # Main Content Area
        # ==============================
        self.content_area = ctk.CTkFrame(self.main_container, fg_color=dashboard_theme.BG_COLOR)
        self.content_area.pack(side="right", fill="both", expand=True)

        # ==============================
        # Top Header
        # ==============================
        self.header = ctk.CTkFrame(
            self.content_area,
            height=80,
            fg_color="#FFFFFF",
            border_color=dashboard_theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12
        )
        self.header.pack(fill="x", padx=20, pady=10)
        self.header.pack_propagate(False)

        # System Name
        system_name = ctk.CTkLabel(
            self.header,
            text="PHANCIAL HEALTH CLINIC SYSTEM",
            font=("Arial", 18, "bold"),
            text_color=dashboard_theme.TEXT_PRIMARY
        )
        system_name.pack(side="left", padx=20)

        # Search Bar
        self.search_entry = ctk.CTkEntry(
            self.header,
            width=300,
            placeholder_text="🔍 Global Search..."
        )
        self.search_entry.pack(side="left", padx=20)
        self.search_entry.bind("<Return>", self.global_search)

        # Clock
        self.clock_label = ctk.CTkLabel(
            self.header,
            text="",
            font=("Arial", 18, "bold"),
            text_color=dashboard_theme.ACCENT_BLUE
        )
        self.clock_label.pack(side="right", padx=20)

        # User Info
        user_info = ctk.CTkLabel(
            self.header,
            text=f"Welcome, {self.admin_user['full_name']}! 👋",
            font=("Arial", 14, "bold"),
            text_color=dashboard_theme.TEXT_PRIMARY
        )
        user_info.pack(side="right", padx=20)

        # Date
        self.date_label = ctk.CTkLabel(
            self.header,
            text="",
            font=("Arial", 12, "bold"),
            text_color=dashboard_theme.TEXT_SECONDARY
        )
        self.date_label.pack(side="right", padx=10)

        # ==============================
        # Scrollable Content
        # ==============================
        self.scrollable_frame = ctk.CTkScrollableFrame(self.content_area, fg_color=dashboard_theme.BG_COLOR)
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # ==============================
        # Dashboard Cards
        # ==============================
        self.cards_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.cards_frame.pack(fill="x", pady=10)

        cards_row1 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        cards_row1.pack(fill="x", pady=5)

        # Card 1: Total Patients
        self.patients_card = self.create_stat_card(cards_row1, "👥", "Total Patients", "0", "#4CAF50", self.open_patients)
        self.patients_card.pack(side="left", padx=5, expand=True, fill="x")

        # Card 2: Total Health Workers
        self.workers_card = self.create_stat_card(cards_row1, "👨‍⚕️", "Health Workers", "0", "#2196F3", self.open_health_workers)
        self.workers_card.pack(side="left", padx=5, expand=True, fill="x")

        # Card 3: Total Appointments
        self.appointments_card = self.create_stat_card(cards_row1, "📅", "Appointments", "0", "#FF9800", self.open_appointments)
        self.appointments_card.pack(side="left", padx=5, expand=True, fill="x")

        # Card 4: Total Diagnoses
        self.diagnoses_card = self.create_stat_card(cards_row1, "🩺", "Diagnoses", "0", "#9C27B0", self.open_diagnosis)
        self.diagnoses_card.pack(side="left", padx=5, expand=True, fill="x")

        cards_row2 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        cards_row2.pack(fill="x", pady=5)

        # Card 5: Total Treatments
        self.treatments_card = self.create_stat_card(cards_row2, "💊", "Treatments", "0", "#E91E63", self.open_treatment)
        self.treatments_card.pack(side="left", padx=5, expand=True, fill="x")

        # Card 6: Total Inventory
        self.inventory_card = self.create_stat_card(cards_row2, "📦", "Inventory Items", "0", "#00BCD4", self.open_inventory)
        self.inventory_card.pack(side="left", padx=5, expand=True, fill="x")

        # Card 7: Total Payments
        self.payments_card = self.create_stat_card(cards_row2, "💳", "Payments", "0", "#FF5722", self.open_payment)
        self.payments_card.pack(side="left", padx=5, expand=True, fill="x")

        # Card 8: Total Receipts
        self.receipts_card = self.create_stat_card(cards_row2, "🧾", "Receipts", "0", "#795548", self.open_receipt)
        self.receipts_card.pack(side="left", padx=5, expand=True, fill="x")

        # Card 9: Total Revenue
        self.revenue_card = self.create_stat_card(cards_row2, "💰", "Total Revenue", "Le 0", "#4CAF50", self.open_payment)
        self.revenue_card.pack(side="left", padx=5, expand=True, fill="x")

        # ==============================
        # Quick Action Buttons
        # ==============================
        self.actions_frame = ctk.CTkFrame(self.scrollable_frame)
        self.actions_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            self.actions_frame,
            text="⚡ Quick Actions",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        actions_row = ctk.CTkFrame(self.actions_frame, fg_color="transparent")
        actions_row.pack(fill="x", padx=10)

        actions = [
            ("➕ Register Patient", "open_patients"),
            ("➕ Add Health Worker", "open_health_workers"),
            ("➕ Book Appointment", "open_appointments"),
            ("➕ Record Diagnosis", "open_diagnosis"),
            ("➕ Add Treatment", "open_treatment"),
            ("➕ Add Inventory", "open_inventory"),
            ("➕ Record Payment", "open_payment"),
            ("🧾 Generate Receipt", "open_receipt")
        ]

        for action_text, command in actions:
            btn = ctk.CTkButton(
                actions_row,
                text=action_text,
                width=180,
                height=40,
                command=lambda cmd=command: getattr(self, cmd)()
            )
            btn.pack(side="left", padx=5, pady=5)

        # ==============================
        # Charts Section
        # ==============================
        if CHARTS_AVAILABLE:
            self.charts_frame = ctk.CTkFrame(self.scrollable_frame)
            self.charts_frame.pack(fill="x", pady=10)

            ctk.CTkLabel(
                self.charts_frame,
                text="📊 Analytics & Charts",
                font=("Arial", 16, "bold")
            ).pack(pady=10)

            charts_row = ctk.CTkFrame(self.charts_frame, fg_color="transparent")
            charts_row.pack(fill="x", padx=10)

            # Revenue Chart
            self.revenue_chart_frame = ctk.CTkFrame(charts_row)
            self.revenue_chart_frame.pack(side="left", padx=5, expand=True, fill="both")
            self.revenue_chart_frame.pack_propagate(False)
            self.revenue_chart_frame.configure(height=300)

            # Patient Registration Chart
            self.patient_chart_frame = ctk.CTkFrame(charts_row)
            self.patient_chart_frame.pack(side="left", padx=5, expand=True, fill="both")
            self.patient_chart_frame.pack_propagate(False)
            self.patient_chart_frame.configure(height=300)

        # ==============================
        # Recent Activities Section
        # ==============================
        self.recent_frame = ctk.CTkFrame(self.scrollable_frame)
        self.recent_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            self.recent_frame,
            text="📋 Recent Activities",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        recent_row = ctk.CTkFrame(self.recent_frame, fg_color="transparent")
        recent_row.pack(fill="x", padx=10)

        # Recent Patients
        self.recent_patients_frame = self.create_recent_table_frame(recent_row, "Recent Patients")
        self.recent_patients_frame.pack(side="left", padx=5, expand=True, fill="both")

        # Recent Payments
        self.recent_payments_frame = self.create_recent_table_frame(recent_row, "Recent Payments")
        self.recent_payments_frame.pack(side="left", padx=5, expand=True, fill="both")

        recent_row2 = ctk.CTkFrame(self.recent_frame, fg_color="transparent")
        recent_row2.pack(fill="x", padx=10, pady=5)

        # Recent Appointments
        self.recent_appointments_frame = self.create_recent_table_frame(recent_row2, "Recent Appointments")
        self.recent_appointments_frame.pack(side="left", padx=5, expand=True, fill="both")

        # Recent Diagnoses
        self.recent_diagnoses_frame = self.create_recent_table_frame(recent_row2, "Recent Diagnoses")
        self.recent_diagnoses_frame.pack(side="left", padx=5, expand=True, fill="both")

        # ==============================
        # Alerts Section
        # ==============================
        self.alerts_frame = ctk.CTkFrame(self.scrollable_frame)
        self.alerts_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            self.alerts_frame,
            text="⚠️ Alerts & Notifications",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        alerts_row = ctk.CTkFrame(self.alerts_frame, fg_color="transparent")
        alerts_row.pack(fill="x", padx=10)

        # Low Stock Alert
        self.low_stock_frame = self.create_alert_frame(alerts_row, "🟠 Low Stock Medicines")
        self.low_stock_frame.pack(side="left", padx=5, expand=True, fill="both")

        # Expired Medicines Alert
        self.expired_frame = self.create_alert_frame(alerts_row, "🔴 Expired Medicines")
        self.expired_frame.pack(side="left", padx=5, expand=True, fill="both")

        # Today's Appointments
        self.today_appointments_frame = self.create_alert_frame(alerts_row, "📅 Today's Appointments")
        self.today_appointments_frame.pack(side="left", padx=5, expand=True, fill="both")

        # ==============================
        # Revenue Summary Section
        # ==============================
        self.revenue_summary_frame = ctk.CTkFrame(self.scrollable_frame)
        self.revenue_summary_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            self.revenue_summary_frame,
            text="💰 Revenue Summary",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        revenue_row = ctk.CTkFrame(self.revenue_summary_frame, fg_color="transparent")
        revenue_row.pack(fill="x", padx=10)

        self.today_revenue_card = self.create_stat_card(revenue_row, "📅", "Today's Revenue", "Le 0", "#4CAF50", self.open_payment)
        self.today_revenue_card.pack(side="left", padx=5, expand=True, fill="x")

        self.week_revenue_card = self.create_stat_card(revenue_row, "📆", "This Week's Revenue", "Le 0", "#2196F3", self.open_payment)
        self.week_revenue_card.pack(side="left", padx=5, expand=True, fill="x")

        self.month_revenue_card = self.create_stat_card(revenue_row, "📊", "This Month's Revenue", "Le 0", "#FF9800", self.open_payment)
        self.month_revenue_card.pack(side="left", padx=5, expand=True, fill="x")

        self.total_revenue_card = self.create_stat_card(revenue_row, "💰", "Total Revenue", "Le 0", "#9C27B0", self.open_payment)
        self.total_revenue_card.pack(side="left", padx=5, expand=True, fill="x")

        # ==============================
        # User Information Panel
        # ==============================
        self.user_info_frame = ctk.CTkFrame(self.scrollable_frame)
        self.user_info_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            self.user_info_frame,
            text="👤 Administrator Information",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        user_info_row = ctk.CTkFrame(self.user_info_frame, fg_color="transparent")
        user_info_row.pack(fill="x", padx=10)

        ctk.CTkLabel(
            user_info_row,
            text=f"Full Name: {self.admin_user['full_name']}",
            font=("Arial", 12)
        ).pack(side="left", padx=20)

        ctk.CTkLabel(
            user_info_row,
            text=f"Username: {self.admin_user['username']}",
            font=("Arial", 12)
        ).pack(side="left", padx=20)

        ctk.CTkLabel(
            user_info_row,
            text=f"Role: {self.admin_user['role']}",
            font=("Arial", 12)
        ).pack(side="left", padx=20)

        ctk.CTkLabel(
            user_info_row,
            text=f"Status: Active",
            font=("Arial", 12),
            text_color="green"
        ).pack(side="left", padx=20)

        # ==============================
        # Notifications Panel
        # ==============================
        self.notifications_frame = ctk.CTkFrame(self.scrollable_frame)
        self.notifications_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            self.notifications_frame,
            text="🔔 Notifications",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        self.notifications_text = ctk.CTkTextbox(
            self.notifications_frame,
            height=100,
            width=1400
        )
        self.notifications_text.pack(padx=10, pady=5)
        self.notifications_text.configure(state="disabled")

        # Start clock update
        self.update_clock()

        # Load all dashboard data
        self.load_dashboard_statistics()
        self.load_recent_patients()
        self.load_recent_payments()
        self.load_recent_appointments()
        self.load_recent_diagnosis()
        self.load_low_stock()
        self.load_expired_medicines()
        self.load_revenue_summary()
        self.load_notifications()
        if CHARTS_AVAILABLE:
            self.load_charts()

    # ==============================
    # Helper Methods
    # ==============================

    def create_stat_card(self, parent, icon, title, value, color, command=None):
        """Create a modern clickable statistics card."""
        return dashboard_theme.create_modern_stat_card(parent, icon, title, value, color, command)

    def create_recent_table_frame(self, parent, title):
        """Create a frame for recent activities table."""
        frame = ctk.CTkFrame(parent, fg_color="#FFFFFF", border_color=dashboard_theme.BORDER_COLOR, border_width=1, corner_radius=12)
        
        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(header_frame, text=title, font=("Arial", 14, "bold"), text_color=dashboard_theme.TEXT_PRIMARY).pack(side="left")
        
        # Style
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

        # Treeview for recent items
        columns = ("Name", "Date")
        table = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        table.heading("Name", text="Name")
        table.heading("Date", text="Date")
        table.column("Name", width=150)
        table.column("Date", width=100)
        table.pack(padx=15, pady=(0, 15), fill="both", expand=True)
        
        frame.table = table
        return frame

    def create_alert_frame(self, parent, title):
        """Create a frame for alerts."""
        frame = ctk.CTkFrame(parent, fg_color="#FFFFFF", border_color=dashboard_theme.BORDER_COLOR, border_width=1, corner_radius=12)
        
        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(header_frame, text=title, font=("Arial", 14, "bold"), text_color=dashboard_theme.TEXT_PRIMARY).pack(side="left")
        
        # Style
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

        # Treeview for alerts
        columns = ("Item", "Details")
        table = ttk.Treeview(frame, columns=columns, show="headings", height=6)
        table.heading("Item", text="Item")
        table.heading("Details", text="Details")
        table.column("Item", width=120)
        table.column("Details", width=150)
        table.pack(padx=15, pady=(0, 15), fill="both", expand=True)
        
        frame.table = table
        return frame

    # ==============================
    # Clock Update
    # ==============================

    def update_clock(self):
        """Update the digital clock every second."""
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y-%m-%d")
        
        self.clock_label.configure(text=time_str)
        self.date_label.configure(text=date_str)
        
        self.after(1000, self.update_clock)

    # ==============================
    # Dashboard Statistics
    # ==============================

    def load_dashboard_statistics(self):
        """Load all dashboard statistics from MySQL."""
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Total Patients
            cursor.execute("SELECT COUNT(*) FROM Patients")
            patients_count = cursor.fetchone()[0]
            self.patients_card.value_label.configure(text=str(patients_count))

            # Total Health Workers
            cursor.execute("SELECT COUNT(*) FROM Health_Workers")
            workers_count = cursor.fetchone()[0]
            self.workers_card.value_label.configure(text=str(workers_count))

            # Total Appointments
            cursor.execute("SELECT COUNT(*) FROM Appointments")
            appointments_count = cursor.fetchone()[0]
            self.appointments_card.value_label.configure(text=str(appointments_count))

            # Total Diagnoses
            cursor.execute("SELECT COUNT(*) FROM Diagnosis")
            diagnoses_count = cursor.fetchone()[0]
            self.diagnoses_card.value_label.configure(text=str(diagnoses_count))

            # Total Treatments
            cursor.execute("SELECT COUNT(*) FROM Treatment")
            treatments_count = cursor.fetchone()[0]
            self.treatments_card.value_label.configure(text=str(treatments_count))

            # Total Inventory Items
            cursor.execute("SELECT COUNT(*) FROM Inventory")
            inventory_count = cursor.fetchone()[0]
            self.inventory_card.value_label.configure(text=str(inventory_count))

            # Total Payments
            cursor.execute("SELECT COUNT(*) FROM Payment")
            payments_count = cursor.fetchone()[0]
            self.payments_card.value_label.configure(text=str(payments_count))

            # Total Receipts
            cursor.execute("SELECT COUNT(*) FROM Receipt")
            receipts_count = cursor.fetchone()[0]
            self.receipts_card.value_label.configure(text=str(receipts_count))

            # Total Revenue
            cursor.execute("SELECT SUM(Amount) FROM Payment")
            total_revenue = cursor.fetchone()[0] or 0
            self.revenue_card.value_label.configure(text=f"Le {total_revenue:,.2f}")

            conn.close()
        except Exception as e:
            print(f"Error loading dashboard statistics: {e}")

    # ==============================
    # Recent Activities
    # ==============================

    def load_recent_patients(self):
        """Load recent patients into the recent patients table."""
        try:
            table = self.recent_patients_frame.table
            for item in table.get_children():
                table.delete(item)

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT FullName, DateOfBirth FROM Patients ORDER BY PatientID DESC LIMIT 10")
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                table.insert("", "end", values=(row[0], str(row[1])))
        except Exception as e:
            print(f"Error loading recent patients: {e}")

    def load_recent_payments(self):
        """Load recent payments into the recent payments table."""
        try:
            table = self.recent_payments_frame.table
            for item in table.get_children():
                table.delete(item)

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.Amount, p.PaymentDate, pat.FullName
                FROM Payment p
                LEFT JOIN Patients pat ON p.PatientID = pat.PatientID
                ORDER BY p.PaymentID DESC LIMIT 10
            """)
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                table.insert("", "end", values=(f"{row[2]} - Le {row[0]:,.2f}", str(row[1])))
        except Exception as e:
            print(f"Error loading recent payments: {e}")

    def load_recent_appointments(self):
        """Load recent appointments into the recent appointments table."""
        try:
            table = self.recent_appointments_frame.table
            for item in table.get_children():
                table.delete(item)

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.AppointmentDate, pat.FullName
                FROM Appointments a
                LEFT JOIN Patients pat ON a.PatientID = pat.PatientID
                ORDER BY a.AppointmentID DESC LIMIT 10
            """)
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                table.insert("", "end", values=(row[1], str(row[0])))
        except Exception as e:
            print(f"Error loading recent appointments: {e}")

    def load_recent_diagnosis(self):
        """Load recent diagnoses into the recent diagnoses table."""
        try:
            table = self.recent_diagnoses_frame.table
            for item in table.get_children():
                table.delete(item)

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.Description, d.DiagnosisDate, pat.FullName
                FROM Diagnosis d
                LEFT JOIN Patients pat ON d.PatientID = pat.PatientID
                ORDER BY d.DiagnosisID DESC LIMIT 10
            """)
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                table.insert("", "end", values=(f"{row[2]} - {row[0]}", str(row[1])))
        except Exception as e:
            print(f"Error loading recent diagnoses: {e}")

    # ==============================
    # Alerts
    # ==============================

    def load_low_stock(self):
        """Load low stock medicines into the low stock alert table."""
        try:
            table = self.low_stock_frame.table
            for item in table.get_children():
                table.delete(item)

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT MedicineName, Quantity FROM Inventory WHERE Quantity < 10")
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                table.insert("", "end", values=(row[0], f"Stock: {row[1]}"))
        except Exception as e:
            print(f"Error loading low stock: {e}")

    def load_expired_medicines(self):
        """Load expired medicines into the expired medicines alert table."""
        try:
            table = self.expired_frame.table
            for item in table.get_children():
                table.delete(item)

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT MedicineName, ExpiryDate FROM Inventory WHERE ExpiryDate < CURDATE()")
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                table.insert("", "end", values=(row[0], f"Expired: {row[1]}"))
        except Exception as e:
            print(f"Error loading expired medicines: {e}")

    # ==============================
    # Revenue Summary
    # ==============================

    def load_revenue_summary(self):
        """Load revenue summary statistics."""
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Today's Revenue
            cursor.execute("SELECT SUM(Amount) FROM Payment WHERE DATE(PaymentDate) = CURDATE()")
            today_revenue = cursor.fetchone()[0] or 0
            self.today_revenue_card.value_label.configure(text=f"Le {today_revenue:,.2f}")

            # This Week's Revenue
            cursor.execute("SELECT SUM(Amount) FROM Payment WHERE YEARWEEK(PaymentDate, 1) = YEARWEEK(CURDATE(), 1)")
            week_revenue = cursor.fetchone()[0] or 0
            self.week_revenue_card.value_label.configure(text=f"Le {week_revenue:,.2f}")

            # This Month's Revenue
            cursor.execute("SELECT SUM(Amount) FROM Payment WHERE MONTH(PaymentDate) = MONTH(CURDATE()) AND YEAR(PaymentDate) = YEAR(CURDATE())")
            month_revenue = cursor.fetchone()[0] or 0
            self.month_revenue_card.value_label.configure(text=f"Le {month_revenue:,.2f}")

            # Total Revenue
            cursor.execute("SELECT SUM(Amount) FROM Payment")
            total_revenue = cursor.fetchone()[0] or 0
            self.total_revenue_card.value_label.configure(text=f"Le {total_revenue:,.2f}")

            conn.close()
        except Exception as e:
            print(f"Error loading revenue summary: {e}")

    # ==============================
    # Notifications
    # ==============================

    def load_notifications(self):
        """Load notifications into the notifications panel."""
        try:
            notifications = []
            
            conn = connect_db()
            cursor = conn.cursor()

            # New Patients (last 24 hours)
            cursor.execute("SELECT COUNT(*) FROM Patients WHERE RegistrationDate >= DATE_SUB(CURDATE(), INTERVAL 1 DAY)")
            new_patients = cursor.fetchone()[0]
            if new_patients > 0:
                notifications.append(f"👥 {new_patients} new patient(s) registered in the last 24 hours")

            # Low Stock
            cursor.execute("SELECT COUNT(*) FROM Inventory WHERE Quantity < 10")
            low_stock_count = cursor.fetchone()[0]
            if low_stock_count > 0:
                notifications.append(f"🟠 {low_stock_count} medicine(s) with low stock")

            # Expired Medicines
            cursor.execute("SELECT COUNT(*) FROM Inventory WHERE ExpiryDate < CURDATE()")
            expired_count = cursor.fetchone()[0]
            if expired_count > 0:
                notifications.append(f"🔴 {expired_count} expired medicine(s) found")

            # Today's Appointments
            cursor.execute("SELECT COUNT(*) FROM Appointments WHERE DATE(AppointmentDate) = CURDATE()")
            today_appointments = cursor.fetchone()[0]
            notifications.append(f"📅 {today_appointments} appointment(s) scheduled for today")

            conn.close()

            if notifications:
                notification_text = "\n".join(notifications)
            else:
                notification_text = "✅ No new notifications"

            self.notifications_text.configure(state="normal")
            self.notifications_text.delete("1.0", "end")
            self.notifications_text.insert("1.0", notification_text)
            self.notifications_text.configure(state="disabled")

        except Exception as e:
            print(f"Error loading notifications: {e}")

    # ==============================
    # Charts
    # ==============================

    def load_charts(self):
        """Load charts with data from MySQL."""
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Monthly Revenue Chart
            cursor.execute("""
                SELECT MONTH(PaymentDate) as month, SUM(Amount) as total
                FROM Payment
                WHERE YEAR(PaymentDate) = YEAR(CURDATE())
                GROUP BY MONTH(PaymentDate)
                ORDER BY month
            """)
            revenue_data = cursor.fetchall()
            conn.close()

            months = [calendar.month_name[i] for i in range(1, 13)]
            revenue_values = [0] * 12
            for month, total in revenue_data:
                revenue_values[month - 1] = total

            # Create Revenue Chart
            self.create_chart(
                self.revenue_chart_frame,
                months,
                revenue_values,
                "Monthly Revenue",
                "Month",
                "Revenue (Le)"
            )

            # Patient Registration Chart
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT MONTH(RegistrationDate) as month, COUNT(*) as count
                FROM Patients
                WHERE YEAR(RegistrationDate) = YEAR(CURDATE())
                GROUP BY MONTH(RegistrationDate)
                ORDER BY month
            """)
            patient_data = cursor.fetchall()
            conn.close()

            patient_values = [0] * 12
            for month, count in patient_data:
                patient_values[month - 1] = count

            # Create Patient Chart
            self.create_chart(
                self.patient_chart_frame,
                months,
                patient_values,
                "Patient Registrations",
                "Month",
                "Patients"
            )

        except Exception as e:
            print(f"Error loading charts: {e}")

    def create_chart(self, parent, x_data, y_data, title, x_label, y_label):
        """Create a bar chart using Matplotlib."""
        try:
            fig = Figure(figsize=(5, 3), dpi=100)
            ax = fig.add_subplot(111)
            
            ax.bar(x_data, y_data, color='#1F6AA5')
            ax.set_title(title, fontsize=10)
            ax.set_xlabel(x_label, fontsize=8)
            ax.set_ylabel(y_label, fontsize=8)
            ax.tick_params(axis='x', rotation=45, labelsize=7)
            ax.tick_params(axis='y', labelsize=7)
            
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            print(f"Error creating chart: {e}")

    # ==============================
    # Navigation Functions
    # ==============================

    def open_dashboard(self):
        """Refresh the dashboard."""
        self.refresh_dashboard()

    def open_patients(self):
        """Open the Patients module."""
        from patients import PatientWindow
        PatientWindow(self)

    def open_health_workers(self):
        """Open the Health Workers module."""
        from health_workers import HealthWorkerWindow
        HealthWorkerWindow(self)

    def open_appointments(self):
        """Open the Appointments module."""
        from appointments import AppointmentWindow
        AppointmentWindow(self)

    def open_diagnosis(self):
        """Open the Diagnosis module."""
        from diagnosis import DiagnosisWindow
        DiagnosisWindow(self)

    def open_treatment(self):
        """Open the Treatment module."""
        from treatment import TreatmentWindow
        TreatmentWindow(self)

    def open_inventory(self):
        """Open the Inventory module."""
        from inventory import InventoryWindow
        InventoryWindow(self)

    def open_payment(self):
        """Open the Payment module."""
        from payment import PaymentWindow
        PaymentWindow(self)

    def open_receipt(self):
        """Open the Receipt module."""
        from receipt import ReceiptWindow
        ReceiptWindow(self)

    def open_reports(self):
        """Open the Reports module (placeholder)."""
        messagebox.showinfo("Reports Module", "Reports module will be implemented in reports.py")

    def open_services(self):
        """Open the Hospital Services Management module."""
        from services import HospitalServicesWindow
        HospitalServicesWindow(self)

    def open_user_management(self):
        """Open the User Management module."""
        from user_management import UserManagementWindow
        UserManagementWindow(self)

    def open_settings(self):
        """Open the Settings module."""
        from settings import SettingsWindow
        SettingsWindow(self)

    def logout(self):
        """Logout from the administrator dashboard."""
        confirm = messagebox.askyesno(
            "Logout",
            "Are you sure you want to logout?"
        )
        if confirm:
            self.destroy()
            # Import and show login window
            from main import LoginApp
            login_app = LoginApp()
            login_app.mainloop()

    # ==============================
    # Global Search
    # ==============================

    def global_search(self, event=None):
        """Perform a global search across all modules."""
        search_query = self.search_entry.get().strip()
        if not search_query:
            messagebox.showwarning("Search Warning", "Please enter a search term.")
            return

        # This is a placeholder for global search functionality
        messagebox.showinfo(
            "Global Search",
            f"Searching for: {search_query}\n\n"
            "Global search will search across:\n"
            "- Patients\n"
            "- Health Workers\n"
            "- Appointments\n"
            "- Payments\n\n"
            "This feature will be fully implemented in future updates."
        )

    # ==============================
    # Refresh Dashboard
    # ==============================

    def refresh_dashboard(self):
        """Refresh all dashboard data."""
        self.load_dashboard_statistics()
        self.load_recent_patients()
        self.load_recent_payments()
        self.load_recent_appointments()
        self.load_recent_diagnosis()
        self.load_low_stock()
        self.load_expired_medicines()
        self.load_revenue_summary()
        self.load_notifications()
        if CHARTS_AVAILABLE:
            self.load_charts()


if __name__ == "__main__":
    app = AdminDashboard()
    app.mainloop()
