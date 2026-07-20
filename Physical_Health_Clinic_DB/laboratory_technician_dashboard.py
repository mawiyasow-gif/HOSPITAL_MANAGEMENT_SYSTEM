import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from database import connect_db

import dashboard_theme

# Set appearance mode and color theme
dashboard_theme.apply_global_theme()

class LaboratoryTechnicianDashboard(ctk.CTk):
    """Laboratory Technician Dashboard for the Physical Health Clinic Record System."""

    def __init__(self, lab_user=None):
        super().__init__()

        self.title("Physical Health Clinic Record System - Lab Technician Dashboard")
        self.geometry("1600x900")
        self.resizable(True, True)

        # Store logged-in user information
        self.lab_user = lab_user or {
            "user_id": 4,
            "worker_id": 4,
            "full_name": "Laboratory Technician Staff",
            "role": "Laboratory Technician"
        }
        self.lab_worker_id = self.lab_user.get("worker_id", 4)

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
            text="🧪 LAB PANEL",
            font=("Arial", 18, "bold"),
            text_color=dashboard_theme.TEXT_PRIMARY
        )
        sidebar_title.pack(pady=30)

        # Menu Items
        menu_items = [
            ("🏠 Dashboard", self.refresh_dashboard),
            ("🧾 Paid Lab Receipts", self.open_receipts),
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
        # Main Content Area
        # ==============================
        self.content_frame = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color=dashboard_theme.BG_COLOR)
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.scrollable_frame = ctk.CTkScrollableFrame(self.content_frame, corner_radius=0, fg_color=dashboard_theme.BG_COLOR)
        self.scrollable_frame.pack(fill="both", expand=True, padx=15, pady=15)

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

        welcome_text = f"Welcome back, {self.lab_user['full_name']}! 👋"
        self.welcome_lbl = ctk.CTkLabel(
            self.header_frame,
            text=welcome_text,
            font=("Arial", 22, "bold"),
            text_color=dashboard_theme.TEXT_PRIMARY
        )
        self.welcome_lbl.pack(side="left", padx=20, pady=15)

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
        self.update_clock()

        # ==============================
        # Dashboard Statistics Cards
        # ==============================
        self.cards_frame = ctk.CTkFrame(self.scrollable_frame)
        self.cards_frame.pack(fill="x", pady=10)

        self.pending_card = self.create_stat_card(self.cards_frame, "⏳", "Pending Lab Requests", "0", "#FF9800")
        self.pending_card.pack(side="left", padx=10, expand=True, fill="x")

        self.completed_card = self.create_stat_card(self.cards_frame, "✅", "Completed Today", "0", "#4CAF50")
        self.completed_card.pack(side="left", padx=10, expand=True, fill="x")

        # ==============================
        # Requests & History Section
        # ==============================
        self.table_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#FFFFFF", border_color=dashboard_theme.BORDER_COLOR, border_width=1, corner_radius=12)
        self.table_frame.pack(fill="both", expand=True, pady=10)

        # Tabview container
        self.tabview = ctk.CTkTabview(self.table_frame, height=550)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=10)

        self.tab_pending = self.tabview.add("⏳ Pending Requests")
        self.tab_completed = self.tabview.add("✅ Completed Tests History")

        # Table header inside tab_pending
        table_header = ctk.CTkFrame(self.tab_pending, fg_color="transparent")
        table_header.pack(fill="x", padx=15, pady=(5, 5))

        ctk.CTkLabel(
            table_header, 
            text="📋 Pending Laboratory Requests Queue", 
            font=("Arial", 14, "bold"), 
            text_color=dashboard_theme.TEXT_PRIMARY
        ).pack(side="left")

        self.process_btn = ctk.CTkButton(
            table_header,
            text="🧪 Enter Results & Complete",
            font=("Arial", 12, "bold"),
            fg_color="gray",
            state="disabled",
            command=self.process_selected_request
        )
        self.process_btn.pack(side="right")

        # Setup Tables
        self.setup_queue_table()
        self.setup_completed_table()

        # Load Data
        self.refresh_dashboard()

    def update_clock(self):
        self.time_lbl.configure(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self.update_clock)

    def create_stat_card(self, parent, icon, title, value, color):
        """Create a modern statistics card."""
        return dashboard_theme.create_modern_stat_card(parent, icon, title, value, color)

    def setup_queue_table(self):
        container = ctk.CTkFrame(self.tab_pending, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side="right", fill="y")

        # Styling
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

        columns = ("Request ID", "Date Requested", "Patient Name", "Doctor Name", "Payment Status", "Status")
        self.queue_table = ttk.Treeview(
            container, 
            columns=columns, 
            show="headings", 
            yscrollcommand=scrollbar.set,
            height=15
        )
        for col in columns:
            self.queue_table.heading(col, text=col, anchor="w")
            self.queue_table.column(col, anchor="w", width=180)
        self.queue_table.column("Request ID", width=100, anchor="center")

        self.queue_table.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.queue_table.yview)

        # Selection Bind
        self.queue_table.bind("<<TreeviewSelect>>", self.on_request_selected)

    def on_request_selected(self, event):
        selected = self.queue_table.selection()
        if selected:
            row = self.queue_table.item(selected[0], "values")
            payment_status = row[4]
            if payment_status == "Paid":
                self.process_btn.configure(state="normal", fg_color=dashboard_theme.ACCENT_BLUE)
            else:
                self.process_btn.configure(state="disabled", fg_color="gray")
        else:
            self.process_btn.configure(state="disabled", fg_color="gray")

    def refresh_dashboard(self):
        self.load_statistics()
        self.load_pending_requests()
        self.load_completed_requests()
        self.process_btn.configure(state="disabled", fg_color="gray")

    def load_statistics(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # Pending Requests Count
            cursor.execute("SELECT COUNT(*) FROM Laboratory_Requests WHERE Status = 'Pending'")
            self.pending_card.value_label.configure(text=str(cursor.fetchone()[0]))

            # Completed Requests Count Today
            cursor.execute("SELECT COUNT(*) FROM Laboratory_Requests WHERE Status = 'Completed' AND DATE(RequestDate) = CURDATE()")
            self.completed_card.value_label.configure(text=str(cursor.fetchone()[0]))

            conn.close()
        except Exception as e:
            print(f"Error loading stats: {e}")

    def load_pending_requests(self):
        for item in self.queue_table.get_children():
            self.queue_table.delete(item)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT lr.RequestID, lr.RequestDate, p.FullName, hw.FullName, 
                       (SELECT IF(COUNT(*) > 0, 'Paid', 'Unpaid') 
                        FROM Payment py 
                        WHERE py.LabRequestID = lr.RequestID AND py.PaymentMethod != 'Pending') AS PaymentStatus,
                       lr.Status
                FROM Laboratory_Requests lr
                LEFT JOIN Patients p ON lr.PatientID = p.PatientID
                LEFT JOIN Health_Workers hw ON lr.DoctorID = hw.WorkerID
                WHERE lr.Status = 'Pending'
                ORDER BY lr.RequestID ASC
            """)
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                self.queue_table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error loading pending requests: {e}")

    def process_selected_request(self):
        selected = self.queue_table.selection()
        if not selected:
            return
        
        row = self.queue_table.item(selected[0], "values")
        payment_status = row[4]
        if payment_status != "Paid":
            messagebox.showwarning("Payment Required", "This patient has not paid for this laboratory request yet.")
            return

        request_id = row[0]
        patient_name = row[2]
        
        # Open results entering popup window
        LabResultsEntryWindow(self, request_id, patient_name)

    def logout(self):
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to sign out from the Laboratory Panel?")
        if confirm:
            self.destroy()
            from login import LoginApp
            app = LoginApp()
            app.mainloop()

    def setup_completed_table(self):
        container = ctk.CTkFrame(self.tab_completed, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side="right", fill="y")

        columns = ("Request ID", "Completed Date", "Patient Name", "Doctor Name", "Test Details")
        self.completed_table = ttk.Treeview(
            container, 
            columns=columns, 
            show="headings", 
            yscrollcommand=scrollbar.set,
            height=15
        )
        for col in columns:
            self.completed_table.heading(col, text=col, anchor="w")
            self.completed_table.column(col, anchor="w", width=180)
        self.completed_table.column("Request ID", width=100, anchor="center")
        self.completed_table.column("Test Details", width=400)

        self.completed_table.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.completed_table.yview)

    def load_completed_requests(self):
        for item in self.completed_table.get_children():
            self.completed_table.delete(item)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT lr.RequestID, res.TestDate, p.FullName, hw.FullName, 
                       GROUP_CONCAT(CONCAT(lt.TestName, ': ', res.ResultDetails) SEPARATOR '; ') AS TestDetails
                FROM Laboratory_Requests lr
                LEFT JOIN Patients p ON lr.PatientID = p.PatientID
                LEFT JOIN Health_Workers hw ON lr.DoctorID = hw.WorkerID
                JOIN Laboratory_Results res ON lr.RequestID = res.RequestID
                JOIN Laboratory_Tests lt ON res.TestID = lt.TestID
                WHERE lr.Status = 'Completed' AND res.TechnicianID = %s
                GROUP BY lr.RequestID, res.TestDate, p.FullName, hw.FullName
                ORDER BY res.TestDate DESC
            """, (self.lab_worker_id,))
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                self.completed_table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error loading completed requests: {e}")

    def open_receipts(self):
        """Open Receipt management module for Paid Lab Receipts verification."""
        from receipt import ReceiptWindow
        ReceiptWindow(self)


class LabResultsEntryWindow(ctk.CTkToplevel):
    """Window to enter results for a selected laboratory request."""

    def __init__(self, parent, request_id, patient_name):
        super().__init__(parent)
        self.parent = parent
        self.request_id = request_id
        self.patient_name = patient_name

        self.title(f"Enter Results: {patient_name} (Request #{request_id})")
        self.geometry("600x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Heading
        ctk.CTkLabel(
            self, 
            text=f"🔬 Enter Lab Results - Request ID #{request_id}", 
            font=("Arial", 16, "bold"), 
            text_color="#1F6AA5"
        ).pack(pady=15)

        # Inner Panel
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Retrieve tests associated with this request
        self.test_entries = {}
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT res.ResultID, lt.TestName
                FROM Laboratory_Results res
                JOIN Laboratory_Tests lt ON res.TestID = lt.TestID
                WHERE res.RequestID = %s
            """, (self.request_id,))
            rows = cursor.fetchall()
            conn.close()

            # Render entry fields for each test
            for i, (result_id, test_name) in enumerate(rows):
                ctk.CTkLabel(form_frame, text=f"{test_name}:", font=("Arial", 12, "bold")).grid(row=i, column=0, sticky="e", padx=20, pady=10)
                entry = ctk.CTkEntry(form_frame, width=300, placeholder_text=f"Enter findings for {test_name}")
                entry.grid(row=i, column=1, sticky="w", padx=10, pady=10)
                self.test_entries[result_id] = entry
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve tests for request:\n{e}")
            self.destroy()
            return

        # Submit Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)

        submit_btn = ctk.CTkButton(
            btn_frame, 
            text="💾 Save & Complete", 
            font=("Arial", 13, "bold"), 
            fg_color="#4CAF50", 
            hover_color="#43A047",
            width=180, 
            command=self.submit_results
        )
        submit_btn.pack(side="left", padx=60)

        cancel_btn = ctk.CTkButton(
            btn_frame, 
            text="Cancel", 
            fg_color="red", 
            hover_color="#D32F2F", 
            width=180, 
            command=self.destroy
        )
        cancel_btn.pack(side="right", padx=60)

    def submit_results(self):
        # Validate that all results are filled
        results_data = {}
        for result_id, entry in self.test_entries.items():
            val = entry.get().strip()
            if not val:
                messagebox.showerror("Validation Error", "Please fill in results for all tests.")
                return
            results_data[result_id] = val

        confirm = messagebox.askyesno("Confirm", "Do you want to save these results and complete the request?")
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # 1. Update Laboratory_Results
            for result_id, val in results_data.items():
                cursor.execute("""
                    UPDATE Laboratory_Results 
                    SET ResultDetails = %s, TestDate = CURRENT_TIMESTAMP, TechnicianID = %s
                    WHERE ResultID = %s
                """, (val, self.parent.lab_worker_id, result_id))

            # 2. Mark request as Completed
            cursor.execute("""
                UPDATE Laboratory_Requests 
                SET Status = 'Completed' 
                WHERE RequestID = %s
            """, (self.request_id,))

            # 3. Retrieve PatientID from Laboratory_Requests
            cursor.execute("SELECT PatientID FROM Laboratory_Requests WHERE RequestID = %s", (self.request_id,))
            patient_id = cursor.fetchone()[0]

            # 4. Calculate total amount for these tests
            cursor.execute("""
                SELECT SUM(lt.Price) 
                FROM Laboratory_Results res
                JOIN Laboratory_Tests lt ON res.TestID = lt.TestID
                WHERE res.RequestID = %s
            """, (self.request_id,))
            total_price = cursor.fetchone()[0] or 0.00

            # 5. Billing record is created upfront by Doctor, no need to recreate here.

            conn.commit()
            conn.close()
 
            # Write audit logs
            user_id = self.parent.lab_user.get("user_id", 1)
            from database import log_audit_action
            log_audit_action(user_id, f"Uploaded laboratory results for RequestID: {self.request_id} (PatientID: {patient_id})")
 
            messagebox.showinfo("Success", "Laboratory results submitted and request marked as completed!")
            self.parent.refresh_dashboard()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to submit laboratory results:\n{e}")


if __name__ == "__main__":
    app = LaboratoryTechnicianDashboard()
    app.mainloop()
