import os
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
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
                       'Paid' AS PaymentStatus, lr.Status
                FROM Laboratory_Requests lr
                JOIN Patients p ON lr.PatientID = p.PatientID
                LEFT JOIN Health_Workers hw ON lr.DoctorID = hw.WorkerID
                JOIN Payment py ON py.LabRequestID = lr.RequestID AND py.PaymentMethod != 'Pending'
                WHERE lr.Status = 'Pending'
                GROUP BY lr.RequestID, lr.RequestDate, p.FullName, hw.FullName, lr.Status
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
            messagebox.showwarning("Selection Required", "Please select a pending request from the table.")
            return
        
        row = self.queue_table.item(selected[0], "values")
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
        top_hdr = ctk.CTkFrame(self.tab_completed, fg_color="transparent")
        top_hdr.pack(fill="x", padx=15, pady=(5, 5))

        ctk.CTkLabel(top_hdr, text="📋 Completed Laboratory Reports History", font=("Arial", 14, "bold"), text_color=dashboard_theme.TEXT_PRIMARY).pack(side="left")

        act_btn_f = ctk.CTkFrame(top_hdr, fg_color="transparent")
        act_btn_f.pack(side="right")

        ctk.CTkButton(act_btn_f, text="👁️ View A4 Report", width=130, fg_color="#6366F1", hover_color="#4F46E5", font=("Arial", 11, "bold"), command=self.open_lab_report).pack(side="left", padx=4)
        ctk.CTkButton(act_btn_f, text="📄 Save PDF", width=100, fg_color="#10B981", hover_color="#059669", font=("Arial", 11, "bold"), command=self.save_lab_report_pdf).pack(side="left", padx=4)
        ctk.CTkButton(act_btn_f, text="🖨️ Print Report", width=110, fg_color="#2563EB", hover_color="#1D4ED8", font=("Arial", 11, "bold"), command=self.print_lab_report).pack(side="left", padx=4)

        container = ctk.CTkFrame(self.tab_completed, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

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
                WHERE lr.Status = 'Completed'
                GROUP BY lr.RequestID, res.TestDate, p.FullName, hw.FullName
                ORDER BY res.TestDate DESC
            """)
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                self.completed_table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error loading completed requests: {e}")

    def open_lab_report(self):
        selected = self.completed_table.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a completed test from the history table.")
            return
        req_id = self.completed_table.item(selected[0], "values")[0]
        try:
            import tempfile
            import subprocess
            import sys
            from lab_report_generator import generate_combined_lab_report_pdf
            
            pdf_path = os.path.join(tempfile.gettempdir(), f"LabReport_REQ_{req_id}.pdf")
            generate_combined_lab_report_pdf(req_id, pdf_path)
            
            if sys.platform == "darwin":
                subprocess.run(["open", pdf_path])
            elif sys.platform == "win32":
                os.startfile(pdf_path)
            else:
                subprocess.run(["xdg-open", pdf_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open laboratory report:\n{e}")

    def save_lab_report_pdf(self):
        selected = self.completed_table.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a completed test from the history table.")
            return
        req_id = self.completed_table.item(selected[0], "values")[0]
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title=f"Save Laboratory Report LAB-REQ-{req_id:06d}"
        )
        if not file_path:
            return
            
        try:
            from lab_report_generator import generate_combined_lab_report_pdf
            generate_combined_lab_report_pdf(req_id, file_path)
            messagebox.showinfo("Success", f"Laboratory report saved successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF report:\n{e}")

    def print_lab_report(self):
        selected = self.completed_table.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a completed test from the history table.")
            return
        req_id = self.completed_table.item(selected[0], "values")[0]
        self.open_lab_report()

    def open_receipts(self):
        """Open Receipt management module for Paid Lab Receipts verification."""
        from receipt import ReceiptWindow
        ReceiptWindow(self)


class LabResultsEntryWindow(ctk.CTkToplevel):
    """Window to enter results for a selected laboratory request using Administrator templates."""

    def __init__(self, parent, request_id, patient_name):
        super().__init__(parent)
        self.parent = parent
        self.request_id = request_id
        self.patient_name = patient_name

        self.title(f"Enter Lab Results: {patient_name} (Request #{request_id})")
        self.geometry("900x750")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.test_param_entries = {}
        self.notes_entries = {}
        self.test_ids = []

        # Heading
        hdr_f = ctk.CTkFrame(self, fg_color=dashboard_theme.CARD_BG, height=50, corner_radius=0)
        hdr_f.pack(fill="x", side="top")
        hdr_f.pack_propagate(False)

        ctk.CTkLabel(
            hdr_f, 
            text=f"🔬 Laboratory Patient Result Entry — Patient: {patient_name} (Request #{request_id})", 
            font=("Arial", 15, "bold"), 
            text_color=dashboard_theme.TEXT_PRIMARY
        ).pack(side="left", padx=20, pady=10)

        # Scrollable Form Body
        self.container = ctk.CTkScrollableFrame(self, fg_color=dashboard_theme.BG_COLOR)
        self.container.pack(fill="both", expand=True, padx=15, pady=10)

        self.load_request_templates()

        # Submit Bar
        btn_frame = ctk.CTkFrame(self, fg_color=dashboard_theme.CARD_BG, height=60, corner_radius=0)
        btn_frame.pack(fill="x", side="bottom")

        submit_btn = ctk.CTkButton(
            btn_frame, 
            text="💾 Save Results & Complete Request", 
            font=("Arial", 13, "bold"), 
            fg_color="#10B981", 
            hover_color="#059669",
            width=260, height=38,
            command=self.submit_results
        )
        submit_btn.pack(side="right", padx=20, pady=10)

        cancel_btn = ctk.CTkButton(
            btn_frame, 
            text="Cancel", 
            fg_color="#64748B", 
            hover_color="#475569", 
            width=120, height=38,
            command=self.destroy
        )
        cancel_btn.pack(side="right", padx=10, pady=10)

    def load_request_templates(self):
        try:
            import json
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT res.ResultID, lt.TestID, lt.TestName
                FROM Laboratory_Results res
                JOIN Laboratory_Tests lt ON res.TestID = lt.TestID
                WHERE res.RequestID = %s
            """, (self.request_id,))
            tests = cursor.fetchall()

            if not tests:
                conn.close()
                ctk.CTkLabel(self.container, text="No laboratory tests found for this request.", font=("Arial", 14, "bold")).pack(pady=20)
                return

            for result_id, test_id, test_name in tests:
                self.test_ids.append((result_id, test_id, test_name))

                # Fetch active template for this test
                cursor.execute("""
                    SELECT TemplateName, TemplateDescription, TemplateFields, ReferenceRanges, MeasurementUnits, DefaultComments
                    FROM laboratory_templates
                    WHERE TestID = %s AND Status = 'Active'
                    ORDER BY TemplateID DESC LIMIT 1
                """, (test_id,))
                tpl = cursor.fetchone()

                tpl_name = tpl[0] if tpl else f"{test_name} Standard Template"
                tpl_desc = tpl[1] if tpl else ""
                tpl_fields = json.loads(tpl[2]) if (tpl and tpl[2]) else []
                def_comments = tpl[5] if (tpl and tpl[5]) else ""

                # Card for this Test
                t_card = ctk.CTkFrame(self.container, fg_color="#FFFFFF", border_color=dashboard_theme.BORDER_COLOR, border_width=1, corner_radius=12)
                t_card.pack(fill="x", pady=10, padx=5)

                t_hdr = ctk.CTkFrame(t_card, fg_color="#EFF6FF", corner_radius=8)
                t_hdr.pack(fill="x", padx=10, pady=8)
                ctk.CTkLabel(t_hdr, text=f"📋 {test_name.upper()} — Template: {tpl_name}", font=("Arial", 14, "bold"), text_color="#1E3A8A").pack(side="left", padx=10, pady=6)

                if tpl_desc:
                    ctk.CTkLabel(t_card, text=f"Description: {tpl_desc}", font=("Arial", 11, "italic"), text_color="#64748B").pack(anchor="w", padx=15, pady=(0, 6))

                # Parameters Input Table
                p_frame = ctk.CTkFrame(t_card, fg_color="transparent")
                p_frame.pack(fill="x", padx=12, pady=6)

                # Header Row
                h_row = ctk.CTkFrame(p_frame, fg_color="#1E3A8A", height=28, corner_radius=4)
                h_row.pack(fill="x", pady=(0, 4))
                h_row.pack_propagate(False)

                ctk.CTkLabel(h_row, text="Test Parameter", font=("Arial", 11, "bold"), text_color="#FFFFFF", anchor="w").pack(side="left", padx=10)
                ctk.CTkLabel(h_row, text="Unit", font=("Arial", 11, "bold"), text_color="#FFFFFF", anchor="w").pack(side="left", padx=110)
                ctk.CTkLabel(h_row, text="Normal Reference Range", font=("Arial", 11, "bold"), text_color="#FFFFFF", anchor="w").pack(side="left", padx=40)
                ctk.CTkLabel(h_row, text="Patient Result Value", font=("Arial", 11, "bold"), text_color="#FFFFFF", anchor="e").pack(side="right", padx=40)

                self.test_param_entries[result_id] = {}

                if tpl_fields:
                    for f in tpl_fields:
                        p_name = f.get("name", "")
                        p_unit = f.get("unit", "")
                        p_range = f.get("range", "")
                        p_def = f.get("default", "")

                        r_box = ctk.CTkFrame(p_frame, fg_color="transparent", height=36)
                        r_box.pack(fill="x", pady=2)
                        r_box.pack_propagate(False)

                        ctk.CTkLabel(r_box, text=p_name, font=("Arial", 12, "bold"), text_color="#0F172A", anchor="w", width=180).pack(side="left", padx=10)
                        ctk.CTkLabel(r_box, text=p_unit, font=("Arial", 11), text_color="#64748B", anchor="w", width=90).pack(side="left", padx=5)
                        ctk.CTkLabel(r_box, text=p_range, font=("Arial", 11), text_color="#2563EB", anchor="w", width=180).pack(side="left", padx=5)

                        val_entry = ctk.CTkEntry(r_box, width=220, placeholder_text=f"Enter {p_name} result...")
                        if p_def:
                            val_entry.insert(0, str(p_def))
                        val_entry.pack(side="right", padx=10)

                        self.test_param_entries[result_id][p_name] = val_entry
                else:
                    # Fallback single field if no template parameters configured
                    r_box = ctk.CTkFrame(p_frame, fg_color="transparent", height=36)
                    r_box.pack(fill="x", pady=2)
                    r_box.pack_propagate(False)
                    ctk.CTkLabel(r_box, text="Result Findings", font=("Arial", 12, "bold"), text_color="#0F172A", width=180, anchor="w").pack(side="left", padx=10)
                    val_entry = ctk.CTkEntry(r_box, width=350, placeholder_text="Enter clinical laboratory findings...")
                    val_entry.pack(side="right", padx=10)
                    self.test_param_entries[result_id]["Findings"] = val_entry

                # Technician Notes input
                notes_f = ctk.CTkFrame(t_card, fg_color="transparent")
                notes_f.pack(fill="x", padx=12, pady=(4, 10))
                ctk.CTkLabel(notes_f, text="Technician Observations / Notes:", font=("Arial", 11, "bold"), text_color="#475569").pack(anchor="w")
                n_entry = ctk.CTkEntry(notes_f, placeholder_text="Optional laboratory technician clinical notes...")
                n_entry.pack(fill="x", pady=2)
                self.notes_entries[result_id] = n_entry

            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load request templates:\n{e}")
            self.destroy()

    def submit_results(self):
        import json
        results_data = {}

        for result_id, param_map in self.test_param_entries.items():
            vals = {}
            for p_name, entry in param_map.items():
                v = entry.get().strip()
                if not v:
                    messagebox.showwarning("Incomplete Form", f"Please enter a result value for '{p_name}'.")
                    return
                vals[p_name] = v

            notes = self.notes_entries[result_id].get().strip() if result_id in self.notes_entries else ""
            results_data[result_id] = json.dumps({"values": vals, "notes": notes})

        confirm = messagebox.askyesno("Confirm Submission", "Save these patient laboratory results and mark request as completed?")
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # 1. Update Laboratory_Results
            for result_id, raw_json in results_data.items():
                cursor.execute("""
                    UPDATE Laboratory_Results 
                    SET ResultDetails = %s, TestDate = CURRENT_TIMESTAMP, TechnicianID = %s
                    WHERE ResultID = %s
                """, (raw_json, self.parent.lab_worker_id, result_id))

            # 2. Mark request as Completed
            cursor.execute("UPDATE Laboratory_Requests SET Status = 'Completed' WHERE RequestID = %s", (self.request_id,))

            conn.commit()
            conn.close()

            # Audit log
            user_id = self.parent.lab_user.get("user_id", 1)
            from database import log_audit_action
            log_audit_action(user_id, f"Uploaded laboratory results for RequestID: {self.request_id} (Patient: {self.patient_name})")

            messagebox.showinfo("Success", "Laboratory results submitted and request marked as completed!")
            self.parent.refresh_dashboard()

            # Ask to view A4 report
            view_rpt = messagebox.askyesno("Print Report", "Would you like to view/print the generated A4 Laboratory Report now?")
            if view_rpt:
                try:
                    import tempfile
                    import subprocess
                    import sys
                    from lab_report_generator import generate_combined_lab_report_pdf

                    pdf_path = os.path.join(tempfile.gettempdir(), f"LabReport_REQ_{self.request_id}.pdf")
                    generate_combined_lab_report_pdf(self.request_id, pdf_path)

                    if sys.platform == "darwin":
                        subprocess.run(["open", pdf_path])
                    elif sys.platform == "win32":
                        os.startfile(pdf_path)
                    else:
                        subprocess.run(["xdg-open", pdf_path])
                except Exception as e:
                    messagebox.showerror("Report Error", f"Failed to launch laboratory report PDF:\n{e}")

            self.destroy()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to submit laboratory results:\n{e}")


if __name__ == "__main__":
    app = LaboratoryTechnicianDashboard()
    app.mainloop()
