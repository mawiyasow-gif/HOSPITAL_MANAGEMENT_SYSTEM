# doctor_monitoring.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import calendar
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import connect_db
import dashboard_theme

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class DoctorMonitoringWindow(ctk.CTkToplevel):
    """Doctor Performance and Monitoring Dashboard for Administrators."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Role-based access control check
        user_role = getattr(parent, 'admin_user', {}).get("role", "")
        if user_role != "Administrator":
            messagebox.showerror("Access Denied", "Only users with the Administrator role can access this dashboard.")
            self.destroy()
            return

        self.title("🔬 Doctor Performance & Monitoring Dashboard")
        self.geometry("1480x880")
        self.resizable(True, True)
        self.configure(fg_color=dashboard_theme.BG_COLOR)
        
        self.transient(parent)
        self.grab_set()

        # State Variables
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_views())

        # Main Layout: Scrollable Frame
        self.scrollable = ctk.CTkScrollableFrame(self, fg_color=dashboard_theme.BG_COLOR)
        self.scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        # Header Title and Control Panel
        self.setup_header()

        # Badges (Top stats/highlights)
        self.setup_badges_panel()

        # Summary Cards Panel
        self.setup_summary_cards()

        # Workspace split (Table left, Visualizations right)
        self.setup_workspace()

        # Start dynamic auto-refresh loop
        self.auto_refresh()

    # ==============================
    # UI Component Setup
    # ==============================

    def setup_header(self):
        header_frame = ctk.CTkFrame(self.scrollable, fg_color=dashboard_theme.CARD_BG, border_color=dashboard_theme.BORDER_COLOR, border_width=1, corner_radius=12)
        header_frame.pack(fill="x", pady=10)

        # Title
        title_lbl = ctk.CTkLabel(header_frame, text="📊 Doctor Performance Dashboard", font=("Arial", 22, "bold"), text_color=dashboard_theme.TEXT_PRIMARY)
        title_lbl.grid(row=0, column=0, sticky="w", padx=20, pady=15)

        # Search Bar
        search_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        search_frame.grid(row=0, column=1, sticky="w", padx=10)
        ctk.CTkLabel(search_frame, text="🔍 Search:", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, width=220, textvariable=self.search_var, placeholder_text="Name or ID...")
        self.search_entry.pack(side="left", padx=5)

        # Range Selector Dropdown
        filter_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filter_frame.grid(row=0, column=2, sticky="w", padx=10)
        ctk.CTkLabel(filter_frame, text="Filter:", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        self.range_combo = ctk.CTkComboBox(
            filter_frame,
            values=["Today", "Yesterday", "This Week", "This Month", "Custom Range"],
            command=self.on_range_changed,
            width=130
        )
        self.range_combo.set("Today")
        self.range_combo.pack(side="left", padx=5)

        # Date Picker entries
        self.start_date_entry = ctk.CTkEntry(filter_frame, width=100, placeholder_text="YYYY-MM-DD")
        self.start_date_entry.pack(side="left", padx=2)
        self.start_date_entry.configure(state="disabled")

        self.end_date_entry = ctk.CTkEntry(filter_frame, width=100, placeholder_text="YYYY-MM-DD")
        self.end_date_entry.pack(side="left", padx=2)
        self.end_date_entry.configure(state="disabled")

        # Action Control Panel
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=3, sticky="e", padx=20)
        
        btn_refresh = ctk.CTkButton(actions_frame, text="🔄 Refresh", width=90, fg_color=dashboard_theme.ACCENT_BLUE, text_color="#FFFFFF", font=("Arial", 12, "bold"), command=self.refresh_views)
        btn_refresh.pack(side="left", padx=4)

        btn_pdf = ctk.CTkButton(actions_frame, text="📄 Export PDF", width=100, fg_color="#F43F5E", hover_color="#E11D48", text_color="#FFFFFF", font=("Arial", 12, "bold"), command=self.export_pdf)
        btn_pdf.pack(side="left", padx=4)

        btn_excel = ctk.CTkButton(actions_frame, text="💚 Excel (CSV)", width=100, fg_color="#10B981", hover_color="#059669", text_color="#FFFFFF", font=("Arial", 12, "bold"), command=self.export_excel)
        btn_excel.pack(side="left", padx=4)

        btn_print = ctk.CTkButton(actions_frame, text="🖨️ Print", width=80, fg_color="#64748B", hover_color="#475569", text_color="#FFFFFF", font=("Arial", 12, "bold"), command=self.print_report)
        btn_print.pack(side="left", padx=4)

    def setup_badges_panel(self):
        self.badges_frame = ctk.CTkFrame(self.scrollable, fg_color="transparent")
        self.badges_frame.pack(fill="x", pady=5)

        self.badge_top_doctor = self.create_badge(self.badges_frame, "👑 Top Doctor:", "Calculating...", "#3B82F6")
        self.badge_top_doctor.pack(side="left", padx=10, fill="x", expand=True)

        self.badge_highest_workload = self.create_badge(self.badges_frame, "⚡ Workload Peak:", "Calculating...", "#EF4444")
        self.badge_highest_workload.pack(side="left", padx=10, fill="x", expand=True)

        self.badge_avg_time = self.create_badge(self.badges_frame, "⏱️ Avg Consult:", "Calculating...", "#10B981")
        self.badge_avg_time.pack(side="left", padx=10, fill="x", expand=True)

    def create_badge(self, parent, label_text, value_text, color_hex):
        frame = ctk.CTkFrame(parent, fg_color=dashboard_theme.CARD_BG, border_color=dashboard_theme.BORDER_COLOR, border_width=1, corner_radius=10, height=45)
        frame.pack_propagate(False)

        lbl = ctk.CTkLabel(frame, text=label_text, font=("Arial", 12, "bold"), text_color=dashboard_theme.TEXT_SECONDARY)
        lbl.pack(side="left", padx=15)

        val = ctk.CTkLabel(frame, text=value_text, font=("Arial", 12, "bold"), text_color=color_hex)
        val.pack(side="left", padx=5)

        frame.value_lbl = val
        return frame

    def setup_summary_cards(self):
        cards_frame = ctk.CTkFrame(self.scrollable, fg_color="transparent")
        cards_frame.pack(fill="x", pady=10)

        self.card_registered = dashboard_theme.create_modern_stat_card(cards_frame, "👥", "Registered Patients", "0", "#3B82F6")
        self.card_registered.pack(side="left", padx=10, expand=True, fill="x")

        self.card_assigned = dashboard_theme.create_modern_stat_card(cards_frame, "📅", "Assigned Patients", "0", "#EC4899")
        self.card_assigned.pack(side="left", padx=10, expand=True, fill="x")

        self.card_attended = dashboard_theme.create_modern_stat_card(cards_frame, "✅", "Attended Patients", "0", "#10B981")
        self.card_attended.pack(side="left", padx=10, expand=True, fill="x")

        self.card_waiting = dashboard_theme.create_modern_stat_card(cards_frame, "⏳", "Waiting Patients", "0", "#F59E0B")
        self.card_waiting.pack(side="left", padx=10, expand=True, fill="x")

        self.card_doctors = dashboard_theme.create_modern_stat_card(cards_frame, "👨‍⚕️", "Doctors on Duty", "0", "#8B5CF6")
        self.card_doctors.pack(side="left", padx=10, expand=True, fill="x")

    def setup_workspace(self):
        workspace = ctk.CTkFrame(self.scrollable, fg_color="transparent")
        workspace.pack(fill="both", expand=True, pady=10)

        # Left Column: Doctor performance Table
        left_panel = ctk.CTkFrame(workspace, fg_color=dashboard_theme.CARD_BG, border_color=dashboard_theme.BORDER_COLOR, border_width=1, corner_radius=12)
        left_panel.pack(side="left", fill="both", expand=True, padx=5)

        title_tbl = ctk.CTkLabel(left_panel, text="📋 Doctor Performance Breakdown", font=("Arial", 15, "bold"), text_color=dashboard_theme.TEXT_PRIMARY)
        title_tbl.pack(anchor="w", padx=20, pady=15)

        table_container = ctk.CTkFrame(left_panel, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        scrollbar = ttk.Scrollbar(table_container)
        scrollbar.pack(side="right", fill="y")

        columns = ("Doctor ID", "Doctor Name", "Specialization", "Assigned", "Attended", "Pending", "Completion %", "Status")
        self.table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=18
        )
        for col in columns:
            self.table.heading(col, text=col, anchor="w")
            self.table.column(col, anchor="w", width=110)
        self.table.column("Doctor ID", width=70, anchor="center")
        self.table.column("Doctor Name", width=160)
        self.table.column("Completion %", width=100, anchor="center")
        self.table.column("Status", width=105, anchor="center")

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.table.yview)

        # Right Column: Visual analytics Charts
        right_panel = ctk.CTkFrame(workspace, fg_color=dashboard_theme.CARD_BG, border_color=dashboard_theme.BORDER_COLOR, border_width=1, corner_radius=12, width=540)
        right_panel.pack(side="right", fill="both", expand=False, padx=5)
        right_panel.pack_propagate(False)

        title_charts = ctk.CTkLabel(right_panel, text="📈 Live Performance Analytics", font=("Arial", 15, "bold"), text_color=dashboard_theme.TEXT_PRIMARY)
        title_charts.pack(anchor="w", padx=20, pady=15)

        self.charts_container = ctk.CTkFrame(right_panel, fg_color="transparent")
        self.charts_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ==============================
    # Event Handlers & Calculations
    # ==============================

    def on_range_changed(self, choice):
        if choice == "Custom Range":
            self.start_date_entry.configure(state="normal")
            self.end_date_entry.configure(state="normal")
            today_str = datetime.now().strftime("%Y-%m-%d")
            if not self.start_date_entry.get():
                self.start_date_entry.insert(0, today_str)
            if not self.end_date_entry.get():
                self.end_date_entry.insert(0, today_str)
        else:
            self.start_date_entry.delete(0, "end")
            self.end_date_entry.delete(0, "end")
            self.start_date_entry.configure(state="disabled")
            self.end_date_entry.configure(state="disabled")
        
        self.refresh_views()

    def get_date_conditions(self, date_col="AppointmentDate"):
        choice = self.range_combo.get()
        if choice == "Today":
            return f"DATE({date_col}) = CURDATE()", ()
        elif choice == "Yesterday":
            return f"DATE({date_col}) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)", ()
        elif choice == "This Week":
            return f"YEARWEEK({date_col}, 1) = YEARWEEK(CURDATE(), 1)", ()
        elif choice == "This Month":
            return f"MONTH({date_col}) = MONTH(CURDATE()) AND YEAR({date_col}) = YEAR(CURDATE())", ()
        elif choice == "Custom Range":
            start_val = self.start_date_entry.get().strip()
            end_val = self.end_date_entry.get().strip()
            try:
                datetime.strptime(start_val, "%Y-%m-%d")
                datetime.strptime(end_val, "%Y-%m-%d")
                return f"DATE({date_col}) BETWEEN %s AND %s", (start_val, end_val)
            except:
                pass
        return f"DATE({date_col}) = CURDATE()", ()

    def refresh_views(self):
        """Fetch fresh statistics and redraw tables/charts."""
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Date clauses
            apt_clause, apt_params = self.get_date_conditions("AppointmentDate")
            reg_clause, reg_params = self.get_date_conditions("RegistrationDate")

            # 1. Stats Card counts
            cursor.execute(f"SELECT COUNT(*) FROM Patients WHERE {reg_clause}", reg_params)
            self.card_registered.value_label.configure(text=str(cursor.fetchone()[0]))

            cursor.execute(f"SELECT COUNT(*) FROM Appointments WHERE {apt_clause}", apt_params)
            assigned_count = cursor.fetchone()[0]
            self.card_assigned.value_label.configure(text=str(assigned_count))

            cursor.execute(f"SELECT COUNT(*) FROM Appointments WHERE Status = 'Completed' AND {apt_clause}", apt_params)
            attended_count = cursor.fetchone()[0]
            self.card_attended.value_label.configure(text=str(attended_count))

            cursor.execute(f"SELECT COUNT(*) FROM Appointments WHERE Status = 'Pending' AND {apt_clause}", apt_params)
            waiting_count = cursor.fetchone()[0]
            self.card_waiting.value_label.configure(text=str(waiting_count))

            cursor.execute(f"SELECT COUNT(DISTINCT WorkerID) FROM Appointments WHERE {apt_clause}", apt_params)
            self.card_doctors.value_label.configure(text=str(cursor.fetchone()[0]))

            # 2. Avg Consultation Time
            avg_time_query = f"""
                SELECT AVG(TIME_TO_SEC(TIMEDIFF(TIME(d.DiagnosisDate), a.AppointmentTime))) / 60
                FROM Appointments a
                JOIN Diagnosis d ON a.AppointmentID = d.AppointmentID
                WHERE a.Status = 'Completed' 
                  AND TIME_TO_SEC(TIMEDIFF(TIME(d.DiagnosisDate), a.AppointmentTime)) BETWEEN 60 AND 7200
                  AND {apt_clause}
            """
            cursor.execute(avg_time_query, apt_params)
            avg_val = cursor.fetchone()[0]
            if avg_val:
                self.badge_avg_time.value_lbl.configure(text=f"{avg_val:,.1f} mins")
            else:
                self.badge_avg_time.value_lbl.configure(text="N/A")

            # 3. Retrieve Doctors List and detailed counts
            cursor.execute("SELECT WorkerID, FullName, Role FROM Health_Workers WHERE Role LIKE '%Doctor%' OR Role LIKE '%Physician%'")
            doctors_list = cursor.fetchall()

            search_query = self.search_entry.get().strip().lower()
            
            # Clear Table
            for item in self.table.get_children():
                self.table.delete(item)

            doctor_perf_stats = []
            top_doc = None
            max_completion = -1.0
            max_attended_cnt = -1

            highest_workload_doc = None
            max_workload_cnt = -1

            for doc_id, full_name, role in doctors_list:
                # Search filter check
                if search_query and (search_query not in full_name.lower() and search_query not in str(doc_id)):
                    continue

                # Assigned
                cursor.execute(f"SELECT COUNT(*) FROM Appointments WHERE WorkerID = %s AND {apt_clause}", (doc_id,) + apt_params)
                assigned = cursor.fetchone()[0]

                # Attended
                cursor.execute(f"SELECT COUNT(*) FROM Appointments WHERE WorkerID = %s AND Status = 'Completed' AND {apt_clause}", (doc_id,) + apt_params)
                attended = cursor.fetchone()[0]

                # Pending
                cursor.execute(f"SELECT COUNT(*) FROM Appointments WHERE WorkerID = %s AND Status = 'Pending' AND {apt_clause}", (doc_id,) + apt_params)
                pending = cursor.fetchone()[0]

                completion = 0.0
                if assigned > 0:
                    completion = (attended / assigned) * 100.0

                # Current Status (🟢 Available, 🟡 Busy, 🔴 Off Duty)
                cursor.execute("SELECT COUNT(*) FROM Appointments WHERE WorkerID = %s AND AppointmentDate = CURDATE()", (doc_id,))
                assigned_today = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM Appointments WHERE WorkerID = %s AND Status = 'Pending' AND AppointmentDate = CURDATE()", (doc_id,))
                pending_today = cursor.fetchone()[0]

                if assigned_today == 0:
                    status_str = "🔴 Off Duty"
                elif pending_today > 0:
                    status_str = "🟡 Busy"
                else:
                    status_str = "🟢 Available"

                # Insert Row
                self.table.insert("", "end", values=(
                    doc_id,
                    full_name,
                    role,
                    assigned,
                    attended,
                    pending,
                    f"{completion:.1f}%",
                    status_str
                ))

                doctor_perf_stats.append({
                    'id': doc_id,
                    'name': full_name,
                    'role': role,
                    'assigned': assigned,
                    'attended': attended,
                    'pending': pending,
                    'completion': completion,
                    'status': status_str
                })

                # Highlight Top Performer
                if assigned > 0:
                    if (completion > max_completion) or (completion == max_completion and attended > max_attended_cnt):
                        max_completion = completion
                        max_attended_cnt = attended
                        top_doc = f"Dr. {full_name.split()[-1]} ({completion:.1f}%)"

                # Highlight Workload
                if assigned > max_workload_cnt:
                    max_workload_cnt = assigned
                    highest_workload_doc = f"Dr. {full_name.split()[-1]} ({assigned} pts)"

            # Set Badges
            self.badge_top_doctor.value_lbl.configure(text=top_doc if top_doc else "None Today")
            self.badge_highest_workload.value_lbl.configure(text=highest_workload_doc if highest_workload_doc else "None Today")

            # Retain stats object for PDF extraction
            self.cached_doctor_stats = doctor_perf_stats

            # 4. Redraw Visual Charts
            self.redraw_charts(doctor_perf_stats, attended_count, waiting_count, assigned_count)

            conn.close()
        except Exception as e:
            print(f"Error loading monitoring dashboard: {e}")

    def redraw_charts(self, doctor_stats, attended, waiting, total):
        # Clear previous widgets in charts panel
        for widget in self.charts_container.winfo_children():
            widget.destroy()

        # Build figure
        fig = plt.figure(figsize=(5, 6.5), dpi=100)
        fig.patch.set_facecolor('#FFFFFF')
        
        # 1. Bar Chart: Attended patients by doctor
        ax1 = fig.add_subplot(211)
        ax1.set_facecolor('#FFFFFF')
        
        names = []
        attended_vals = []
        for doc in doctor_stats:
            # Shorten name for space
            short_name = doc['name'].split()[-1]
            names.append(short_name)
            attended_vals.append(doc['attended'])

        if not attended_vals:
            names = ['No Data']
            attended_vals = [0]

        colors_bar = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899']
        bars = ax1.bar(names, attended_vals, color=colors_bar[:len(names)], width=0.45)
        ax1.set_title("Attended Patients by Doctor", fontsize=10, fontweight='bold', color='#0F172A')
        ax1.tick_params(colors='#64748B', labelsize=8)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_color('#E2E8F0')
        ax1.spines['bottom'].set_color('#E2E8F0')

        # Add values on top of bars
        for bar in bars:
            height = bar.get_height()
            ax1.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, color='#475569')

        # 2. Pie Chart: Breakdowns
        ax2 = fig.add_subplot(212)
        ax2.set_facecolor('#FFFFFF')

        labels = ['Attended', 'Waiting', 'Other/Cancelled']
        other = max(0, total - (attended + waiting))
        sizes = [attended, waiting, other]
        pie_colors = ['#10B981', '#F59E0B', '#64748B']

        if sum(sizes) == 0:
            sizes = [1, 0, 0]
            labels = ['No Data', '', '']
            pie_colors = ['#E2E8F0', '#E2E8F0', '#E2E8F0']

        # Filter out empty slices
        final_sizes = []
        final_labels = []
        final_colors = []
        for s, l, c in zip(sizes, labels, pie_colors):
            if s > 0 or l == 'No Data':
                final_sizes.append(s)
                final_labels.append(l)
                final_colors.append(c)

        ax2.pie(final_sizes, labels=final_labels, colors=final_colors, autopct=lambda p: '{:.1f}%'.format(p) if p > 0 else '', startangle=90, textprops={'fontsize': 8, 'color': '#0F172A'})
        ax2.set_title("Breakdown of Assignments Status", fontsize=10, fontweight='bold', color='#0F172A')
        ax2.axis('equal')

        fig.tight_layout()

        # Canvas binding
        canvas = FigureCanvasTkAgg(fig, master=self.charts_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def auto_refresh(self):
        """Automatically refresh details every 5 seconds, checking window existence."""
        if self.winfo_exists():
            self.refresh_views()
            self.after(5000, self.auto_refresh)

    # ==============================
    # Report Export Actions
    # ==============================

    def export_pdf(self):
        """Generate a formatted PDF Performance report."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")],
            title="Export Doctor Performance Report"
        )
        if not file_path:
            return

        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'ReportTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#0F172A'),
                spaceAfter=15
            )
            meta_style = ParagraphStyle(
                'ReportMeta',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#475569'),
                spaceAfter=20
            )
            h2_style = ParagraphStyle(
                'ReportSection',
                parent=styles['Heading2'],
                fontSize=13,
                textColor=colors.HexColor('#1E3A8A'),
                spaceBefore=15,
                spaceAfter=10
            )

            story = []

            # Document Title
            story.append(Paragraph("Doctor Performance and Activity Report", title_style))
            story.append(Paragraph(f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Range: {self.range_combo.get()}", meta_style))
            story.append(Spacer(1, 10))

            # Statistics table summary
            stats_data = [
                ["Patients Registered", "Patients Assigned", "Patients Attended", "Patients Waiting"],
                [
                    self.card_registered.value_label.cget("text"),
                    self.card_assigned.value_label.cget("text"),
                    self.card_attended.value_label.cget("text"),
                    self.card_waiting.value_label.cget("text")
                ]
            ]
            t_summary = Table(stats_data, colWidths=[120, 120, 120, 120])
            t_summary.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0F172A')),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#FFFFFF')),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
            ]))
            story.append(Paragraph("Overall Clinic Summary Metrics", h2_style))
            story.append(t_summary)
            story.append(Spacer(1, 20))

            # Performance Details table
            perf_headers = ["Doctor ID", "Doctor Name", "Assigned", "Attended", "Pending", "Completion %", "Status"]
            table_rows = [perf_headers]

            for row in self.cached_doctor_stats:
                table_rows.append([
                    str(row['id']),
                    row['name'],
                    str(row['assigned']),
                    str(row['attended']),
                    str(row['pending']),
                    f"{row['completion']:.1f}%",
                    row['status']
                ])

            t_perf = Table(table_rows, colWidths=[60, 150, 70, 70, 70, 80, 80])
            t_perf.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('ALIGN', (0,0), (0,-1), 'CENTER'),
                ('ALIGN', (5,0), (5,-1), 'CENTER'),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ]))
            story.append(Paragraph("Doctor Performance Breakdown", h2_style))
            story.append(t_perf)

            # Build document
            doc.build(story)
            messagebox.showinfo("Success", f"Doctor performance report exported successfully to:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to write PDF report:\n{e}")

    def export_excel(self):
        """Export doctor statistics to a clean CSV spreadsheet."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Spreadsheets", "*.csv")],
            title="Export Doctor Performance Excel Sheet"
        )
        if not file_path:
            return

        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Title
                writer.writerow(["Doctor Performance Report"])
                writer.writerow([f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                writer.writerow([f"Date Range Filter: {self.range_combo.get()}"])
                writer.writerow([])

                # Overall counts
                writer.writerow(["Overall Metrics Summary"])
                writer.writerow(["Registered Patients Today", "Assigned Patients", "Attended Patients", "Waiting Patients"])
                writer.writerow([
                    self.card_registered.value_label.cget("text"),
                    self.card_assigned.value_label.cget("text"),
                    self.card_attended.value_label.cget("text"),
                    self.card_waiting.value_label.cget("text")
                ])
                writer.writerow([])

                # Breakdown Table
                writer.writerow(["Doctor Breakdown Stats"])
                writer.writerow(["Doctor ID", "Doctor Name", "Specialization/Role", "Assigned", "Attended", "Pending", "Completion Percentage", "Current Status"])
                
                for row in self.cached_doctor_stats:
                    writer.writerow([
                        row['id'],
                        row['name'],
                        row['role'],
                        row['assigned'],
                        row['attended'],
                        row['pending'],
                        f"{row['completion']:.1f}%",
                        row['status']
                    ])

            messagebox.showinfo("Success", f"Doctor report spreadsheet exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to save CSV file:\n{e}")

    def print_report(self):
        """Simulate printing by showing a formatted printable text dialog representation."""
        print_window = ctk.CTkToplevel(self)
        print_window.title("🖨️ Print Doctor Performance Report")
        print_window.geometry("800x600")
        print_window.transient(self)
        print_window.grab_set()

        # Header Info
        header_text = f"""========================================================================
                      PHYSICAL HEALTH CLINIC RECORD SYSTEM
                           DOCTOR PERFORMANCE REPORT
========================================================================
Report Range : {self.range_combo.get()}
Generated On : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
------------------------------------------------------------------------
Registered   : {self.card_registered.value_label.cget("text")}
Assigned     : {self.card_assigned.value_label.cget("text")}
Attended     : {self.card_attended.value_label.cget("text")}
Waiting      : {self.card_waiting.value_label.cget("text")}
------------------------------------------------------------------------
"""

        # Table Headers
        table_header = f"{'ID':<6} | {'Doctor Name':<24} | {'Assigned':<8} | {'Attended':<8} | {'Pending':<8} | {'Comp %':<8} | {'Status':<12}\n"
        divider = "-" * 80 + "\n"
        
        table_rows_text = ""
        for row in self.cached_doctor_stats:
            table_rows_text += f"{row['id']:<6} | {row['name'][:24]:<24} | {row['assigned']:<8} | {row['attended']:<8} | {row['pending']:<8} | {row['completion']:>5.1f}% | {row['status']:<12}\n"

        full_print_content = header_text + table_header + divider + table_rows_text + divider + "\n[System Signature: Physical Health Clinic Administrator]"

        # Text display panel
        text_panel = ctk.CTkTextbox(print_window, font=("Courier", 11), fg_color="#FFFFFF", text_color="#000000")
        text_panel.pack(fill="both", expand=True, padx=20, pady=20)
        text_panel.insert("1.0", full_print_content)
        text_panel.configure(state="disabled")

        # Command control buttons
        btn_frame = ctk.CTkFrame(print_window, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 15))
        
        btn_send = ctk.CTkButton(btn_frame, text="🖨️ Send to Printer", fg_color=dashboard_theme.ACCENT_BLUE, command=lambda: messagebox.showinfo("Printing", "Sending document stream to clinic printer queue..."))
        btn_send.pack(side="left", padx=50)

        btn_close = ctk.CTkButton(btn_frame, text="Close View", fg_color="red", hover_color="#C0392B", command=print_window.destroy)
        btn_close.pack(side="right", padx=50)
