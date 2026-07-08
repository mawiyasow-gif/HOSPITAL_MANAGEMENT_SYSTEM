import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from database import connect_db

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class AccountantDashboard(ctk.CTk):
    """Accountant Dashboard for the Physical Health Clinic Record System."""

    def __init__(self, accountant_user=None):
        super().__init__()

        self.title("Physical Health Clinic Record System - Accountant Dashboard")
        self.geometry("1600x900")
        self.resizable(True, True)

        self.accountant_user = accountant_user or {
            "user_id": 6,
            "worker_id": 8,
            "full_name": "Accountant Staff",
            "role": "Accountant"
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
            text="🏥 FINANCE PANEL",
            font=("Arial", 20, "bold"),
            text_color="#1F6AA5"
        )
        sidebar_title.pack(pady=30)

        # Menu items for Accountant
        menu_items = [
            ("🏠 Dashboard", self.refresh_dashboard),
            ("💳 Payments", self.open_payments),
            ("🧾 Receipts", self.open_receipts),
            ("📊 Financial Reports", self.open_financial_reports),
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

        welcome_text = f"👋 Welcome, {self.accountant_user['full_name']} (Accountant)"
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

        self.today_revenue_card = self.create_stat_card(
            cards_row, "📅", "Today's Revenue", "Le 0", "#4CAF50", self.open_payments
        )
        self.today_revenue_card.pack(side="left", padx=5, expand=True, fill="x")

        self.week_revenue_card = self.create_stat_card(
            cards_row, "📆", "Weekly Revenue", "Le 0", "#2196F3", self.open_payments
        )
        self.week_revenue_card.pack(side="left", padx=5, expand=True, fill="x")

        self.month_revenue_card = self.create_stat_card(
            cards_row, "📊", "Monthly Revenue", "Le 0", "#FF9800", self.open_payments
        )
        self.month_revenue_card.pack(side="left", padx=5, expand=True, fill="x")

        self.total_revenue_card = self.create_stat_card(
            cards_row, "💰", "Total Revenue", "Le 0", "#9C27B0", self.open_payments
        )
        self.total_revenue_card.pack(side="left", padx=5, expand=True, fill="x")

        # ==============================
        # Quick Actions
        # ==============================
        self.actions_frame = ctk.CTkFrame(self.scrollable_frame)
        self.actions_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(self.actions_frame, text="⚡ Quick Action Center", font=("Arial", 16, "bold")).pack(pady=10)

        actions_row = ctk.CTkFrame(self.actions_frame, fg_color="transparent")
        actions_row.pack(fill="x", padx=10, pady=10)

        actions = [
            ("💳 Record Payment", self.open_payments),
            ("🧾 Generate Receipt", self.open_receipts),
            ("📊 Financial Summary", self.open_financial_reports)
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

        # Left Column: Recent Payments
        self.left_col = ctk.CTkFrame(self.data_split_frame, fg_color="transparent")
        self.left_col.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.payments_table_frame = self.create_table_frame(self.left_col, "💳 Recent Payments", ("ID", "Patient Name", "Amount", "Method", "Date"))
        self.payments_table_frame.pack(fill="both", expand=True)

        # Right Column: Recent Receipts
        self.right_col = ctk.CTkFrame(self.data_split_frame, fg_color="transparent")
        self.right_col.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.receipts_table_frame = self.create_table_frame(self.right_col, "🧾 Recent Receipts", ("ID", "Receipt No", "Amount", "Issue Date"))
        self.receipts_table_frame.pack(fill="both", expand=True)

        # Load statistics & lists
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

        table = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        for col in columns:
            table.heading(col, text=col, anchor="center")
            table.column(col, width=100, anchor="center")

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
            cursor.execute("SELECT SUM(Amount) FROM Payments WHERE DATE(PaymentDate) = CURDATE()")
            today_rev = cursor.fetchone()[0] or 0
            self.today_revenue_card.value_label.configure(text=f"Le {today_rev:,.2f}")

            cursor.execute("SELECT SUM(Amount) FROM Payments WHERE YEARWEEK(PaymentDate, 1) = YEARWEEK(CURDATE(), 1)")
            week_rev = cursor.fetchone()[0] or 0
            self.week_revenue_card.value_label.configure(text=f"Le {week_rev:,.2f}")

            cursor.execute("SELECT SUM(Amount) FROM Payments WHERE MONTH(PaymentDate) = MONTH(CURDATE()) AND YEAR(PaymentDate) = YEAR(CURDATE())")
            month_rev = cursor.fetchone()[0] or 0
            self.month_revenue_card.value_label.configure(text=f"Le {month_rev:,.2f}")

            cursor.execute("SELECT SUM(Amount) FROM Payments")
            total_rev = cursor.fetchone()[0] or 0
            self.total_revenue_card.value_label.configure(text=f"Le {total_rev:,.2f}")

            # Payments Table
            p_table = self.payments_table_frame.table
            for item in p_table.get_children():
                p_table.delete(item)
            cursor.execute("""
                SELECT p.PaymentID, pat.FullName, p.Amount, p.PaymentMethod, DATE(p.PaymentDate)
                FROM Payments p
                LEFT JOIN Patients pat ON p.PatientID = pat.PatientID
                ORDER BY p.PaymentID DESC LIMIT 8
            """)
            for row in cursor.fetchall():
                p_table.insert("", "end", values=(row[0], row[1], f"Le {row[2]:,.2f}", row[3], str(row[4])))

            # Receipts Table
            r_table = self.receipts_table_frame.table
            for item in r_table.get_children():
                r_table.delete(item)
            cursor.execute("""
                SELECT r.ReceiptID, r.ReceiptNumber, r.TotalAmount, DATE(r.IssueDate)
                FROM Receipts r
                ORDER BY r.ReceiptID DESC LIMIT 8
            """)
            for row in cursor.fetchall():
                r_table.insert("", "end", values=(row[0], row[1], f"Le {row[2]:,.2f}", str(row[3])))

            conn.close()
        except Exception as e:
            print(f"Error loading accountant dashboard: {e}")

    def open_payments(self):
        from payment import PaymentWindow
        PaymentWindow(self)

    def open_receipts(self):
        from receipt import ReceiptWindow
        ReceiptWindow(self)

    def open_financial_reports(self):
        # Build a neat Financial Reports/Summary popup!
        FinancialSummaryWindow(self)

    def logout(self):
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to log out?")
        if confirm:
            self.destroy()
            from login import LoginApp
            app = LoginApp()
            app.mainloop()


class FinancialSummaryWindow(ctk.CTkToplevel):
    """Financial Summary Report popup for the Accountant."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Financial Summary Report")
        self.geometry("800x500")
        self.resizable(False, False)

        # Title
        ctk.CTkLabel(
            self,
            text="📊 Clinic Financial Summary Report",
            font=("Arial", 22, "bold"),
            text_color="#1F6AA5"
        ).pack(pady=20)

        # Frame
        report_frame = ctk.CTkFrame(self)
        report_frame.pack(fill="both", expand=True, padx=30, pady=10)

        # Labels for summary metrics
        self.metrics = [
            ("Today's Total Cash Payments:", "Le 0.00", "#4CAF50"),
            ("Today's Total Card/Mobile Payments:", "Le 0.00", "#2196F3"),
            ("Total Registered Patient Transactions:", "0", "gray"),
            ("This Month's Total Revenue:", "Le 0.00", "#FF9800"),
            ("Cumulative Clinic Revenue to Date:", "Le 0.00", "#9C27B0")
        ]

        self.labels = []
        for i, (label_text, val_text, color) in enumerate(self.metrics):
            ctk.CTkLabel(report_frame, text=label_text, font=("Arial", 14, "bold")).grid(row=i, column=0, padx=20, pady=15, sticky="e")
            lbl_val = ctk.CTkLabel(report_frame, text=val_text, font=("Arial", 16, "bold"), text_color=color)
            lbl_val.grid(row=i, column=1, padx=20, pady=15, sticky="w")
            self.labels.append(lbl_val)

        # Close button
        ctk.CTkButton(self, text="Close Report", width=200, command=self.destroy).pack(pady=20)

        self.load_financials()

    def load_financials(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Today's Cash
            cursor.execute("SELECT SUM(Amount) FROM Payments WHERE DATE(PaymentDate) = CURDATE() AND LOWER(PaymentMethod) LIKE '%cash%'")
            cash = cursor.fetchone()[0] or 0
            self.labels[0].configure(text=f"Le {cash:,.2f}")

            # Today's Card/Mobile
            cursor.execute("SELECT SUM(Amount) FROM Payments WHERE DATE(PaymentDate) = CURDATE() AND (LOWER(PaymentMethod) LIKE '%card%' OR LOWER(PaymentMethod) LIKE '%mobile%' OR LOWER(PaymentMethod) LIKE '%orange%' OR LOWER(PaymentMethod) LIKE '%tele%')")
            card = cursor.fetchone()[0] or 0
            self.labels[1].configure(text=f"Le {card:,.2f}")

            # Total Tx
            cursor.execute("SELECT COUNT(*) FROM Payments")
            tx_count = cursor.fetchone()[0] or 0
            self.labels[2].configure(text=str(tx_count))

            # This month revenue
            cursor.execute("SELECT SUM(Amount) FROM Payments WHERE MONTH(PaymentDate) = MONTH(CURDATE()) AND YEAR(PaymentDate) = YEAR(CURDATE())")
            month = cursor.fetchone()[0] or 0
            self.labels[3].configure(text=f"Le {month:,.2f}")

            # Cumulative
            cursor.execute("SELECT SUM(Amount) FROM Payments")
            total = cursor.fetchone()[0] or 0
            self.labels[4].configure(text=f"Le {total:,.2f}")

            conn.close()
        except Exception as e:
            print(f"Error loading report data: {e}")


if __name__ == "__main__":
    app = AccountantDashboard()
    app.mainloop()
