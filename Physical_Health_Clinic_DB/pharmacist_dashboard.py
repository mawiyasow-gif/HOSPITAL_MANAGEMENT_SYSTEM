import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from database import connect_db

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class PharmacistDashboard(ctk.CTk):
    """Pharmacist Dashboard for the Physical Health Clinic Record System."""

    def __init__(self, pharmacist_user=None):
        super().__init__()

        self.title("Physical Health Clinic Record System - Pharmacist Dashboard")
        self.geometry("1600x900")
        self.resizable(True, True)

        self.pharmacist_user = pharmacist_user or {
            "user_id": 5,
            "worker_id": 7,
            "full_name": "Pharmacist Staff",
            "role": "Pharmacist"
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
            text="🏥 PHARMACY PANEL",
            font=("Arial", 20, "bold"),
            text_color="#1F6AA5"
        )
        sidebar_title.pack(pady=30)

        # Menu items for Pharmacist
        menu_items = [
            ("🏠 Dashboard", self.refresh_dashboard),
            ("📦 Inventory", self.open_inventory),
            ("💊 Treatments / Rx", self.open_treatments),
            ("⚡ Dispense Medicine", self.open_dispensing),
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

        welcome_text = f"👋 Welcome, {self.pharmacist_user['full_name']} (Pharmacist)"
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

        self.inventory_card = self.create_stat_card(
            cards_row, "📦", "Total Items", "0", "#4CAF50", self.open_inventory
        )
        self.inventory_card.pack(side="left", padx=5, expand=True, fill="x")

        self.low_stock_card = self.create_stat_card(
            cards_row, "⚠️", "Low Stock Items", "0", "#FF9800", self.open_inventory
        )
        self.low_stock_card.pack(side="left", padx=5, expand=True, fill="x")

        self.expired_card = self.create_stat_card(
            cards_row, "🚨", "Expired Medicines", "0", "#F44336", self.open_inventory
        )
        self.expired_card.pack(side="left", padx=5, expand=True, fill="x")

        self.prescriptions_card = self.create_stat_card(
            cards_row, "💊", "Pending Dispenses", "0", "#9C27B0", self.open_dispensing
        )
        self.prescriptions_card.pack(side="left", padx=5, expand=True, fill="x")

        # ==============================
        # Quick Actions
        # ==============================
        self.actions_frame = ctk.CTkFrame(self.scrollable_frame)
        self.actions_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(self.actions_frame, text="⚡ Quick Action Center", font=("Arial", 16, "bold")).pack(pady=10)

        actions_row = ctk.CTkFrame(self.actions_frame, fg_color="transparent")
        actions_row.pack(fill="x", padx=10, pady=10)

        actions = [
            ("📦 Manage Inventory", self.open_inventory),
            ("📋 View Prescriptions", self.open_treatments),
            ("⚡ Dispense Medicine", self.open_dispensing)
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

        # Left Column: Low Stock & Expired
        self.left_col = ctk.CTkFrame(self.data_split_frame, fg_color="transparent")
        self.left_col.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.low_stock_table_frame = self.create_table_frame(self.left_col, "⚠️ Low Stock Alert (Stock < 10)", ("Item Name", "Stock"))
        self.low_stock_table_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.expired_table_frame = self.create_table_frame(self.left_col, "🚨 Expired Medicines Alert", ("Item Name", "Expiry Date"))
        self.expired_table_frame.pack(fill="both", expand=True)

        # Right Column: Recent Prescriptions
        self.right_col = ctk.CTkFrame(self.data_split_frame, fg_color="transparent")
        self.right_col.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.treatments_table_frame = self.create_table_frame(self.right_col, "💊 Recent Prescriptions", ("ID", "Patient", "Medicine", "Dosage", "Dispense Status"))
        self.treatments_table_frame.pack(fill="both", expand=True)

        # Load statistics & data list
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

        table = ttk.Treeview(frame, columns=columns, show="headings", height=6)
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
            cursor.execute("SELECT COUNT(*) FROM Inventory")
            self.inventory_card.value_label.configure(text=str(cursor.fetchone()[0]))

            cursor.execute("SELECT COUNT(*) FROM Inventory WHERE Stock < 10")
            self.low_stock_card.value_label.configure(text=str(cursor.fetchone()[0]))

            cursor.execute("SELECT COUNT(*) FROM Inventory WHERE ExpiryDate < CURDATE()")
            self.expired_card.value_label.configure(text=str(cursor.fetchone()[0]))

            cursor.execute("SELECT COUNT(*) FROM Treatment WHERE DispensedStatus = 'Pending'")
            self.prescriptions_card.value_label.configure(text=str(cursor.fetchone()[0]))

            # Low Stock Table
            ls_table = self.low_stock_table_frame.table
            for item in ls_table.get_children():
                ls_table.delete(item)
            cursor.execute("SELECT ItemName, Stock FROM Inventory WHERE Stock < 10 LIMIT 5")
            for row in cursor.fetchall():
                ls_table.insert("", "end", values=row)

            # Expired Table
            ex_table = self.expired_table_frame.table
            for item in ex_table.get_children():
                ex_table.delete(item)
            cursor.execute("SELECT ItemName, ExpiryDate FROM Inventory WHERE ExpiryDate < CURDATE() LIMIT 5")
            for row in cursor.fetchall():
                ex_table.insert("", "end", values=(row[0], str(row[1])))

            # Prescriptions Table
            t_table = self.treatments_table_frame.table
            for item in t_table.get_children():
                t_table.delete(item)
            cursor.execute("""
                SELECT t.TreatmentID, p.FullName, t.TreatmentName, t.Dosage, t.DispensedStatus
                FROM Treatment t
                LEFT JOIN Patients p ON t.PatientID = p.PatientID
                ORDER BY t.TreatmentID DESC LIMIT 5
            """)
            for row in cursor.fetchall():
                t_table.insert("", "end", values=row)

            conn.close()
        except Exception as e:
            print(f"Error loading pharmacist dashboard: {e}")

    def open_inventory(self):
        from inventory import InventoryWindow
        InventoryWindow(self)

    def open_treatments(self):
        from treatment import TreatmentWindow
        TreatmentWindow(self)

    def open_dispensing(self):
        MedicineDispensingWindow(self)

    def logout(self):
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to log out?")
        if confirm:
            self.destroy()
            from login import LoginApp
            app = LoginApp()
            app.mainloop()


class MedicineDispensingWindow(ctk.CTkToplevel):
    """Pharmacy Medicine Dispensing interface."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Pharmacy Medicine Dispensing Portal")
        self.geometry("1100x650")
        self.resizable(True, True)

        # Title
        ctk.CTkLabel(
            self,
            text="💊 Medicine Dispensing Portal",
            font=("Arial", 22, "bold"),
            text_color="#1F6AA5"
        ).pack(pady=15)

        # Main Layout
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Table showing Pending Prescriptions
        self.table_frame = ctk.CTkFrame(main_frame)
        self.table_frame.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(
            self.table_frame,
            text="Pending Prescriptions Queue",
            font=("Arial", 14, "bold"),
            text_color="#1F6AA5"
        ).pack(anchor="w", padx=10, pady=5)

        columns = ("Treatment ID", "Patient Name", "Prescribed Medicine", "Dosage", "Duration", "Doctor")
        self.table = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=12)
        
        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=32, font=("Arial", 11))
        style.map("Treeview", background=[("selected", "#1F6AA5")], foreground=[("selected", "white")])

        for col in columns:
            self.table.heading(col, text=col, anchor="center")
            self.table.column(col, width=150, anchor="center")
        self.table.column("Prescribed Medicine", width=180)
        self.table.column("Patient Name", width=180)

        v_scroll = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=v_scroll.set)
        
        self.table.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

        self.table.bind("<<TreeviewSelect>>", self.on_select_pending)

        # Bottom Action Bar
        action_bar = ctk.CTkFrame(main_frame, height=80)
        action_bar.pack(fill="x", pady=10)
        action_bar.pack_propagate(False)

        self.dispense_btn = ctk.CTkButton(
            action_bar,
            text="⚡ Dispense Selected Medicine",
            font=("Arial", 14, "bold"),
            fg_color="gray",
            state="disabled",
            command=self.dispense_medicine
        )
        self.dispense_btn.pack(side="right", padx=20, pady=15)

        self.info_lbl = ctk.CTkLabel(
            action_bar,
            text="Select a pending prescription from the table to dispense.",
            font=("Arial", 12, "italic")
        )
        self.info_lbl.pack(side="left", padx=20, pady=15)

        # Load data
        self.load_pending_prescriptions()

    def load_pending_prescriptions(self):
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT t.TreatmentID, p.FullName, t.TreatmentName, t.Dosage, t.Duration, hw.FullName
                FROM Treatment t
                LEFT JOIN Patients p ON t.PatientID = p.PatientID
                LEFT JOIN Health_Workers hw ON t.WorkerID = hw.WorkerID
                WHERE t.DispensedStatus = 'Pending'
                ORDER BY t.TreatmentID DESC
            """
            cursor.execute(query)
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load pending prescriptions:\n{e}")

    def on_select_pending(self, event):
        selected = self.table.selection()
        if selected:
            self.dispense_btn.configure(state="normal", fg_color="#4CAF50")
            row = self.table.item(selected[0], "values")
            self.info_lbl.configure(text=f"Selected: {row[2]} for {row[1]}")
        else:
            self.dispense_btn.configure(state="disabled", fg_color="gray")
            self.info_lbl.configure(text="Select a pending prescription from the table to dispense.")

    def dispense_medicine(self):
        selected = self.table.selection()
        if not selected:
            return

        row = self.table.item(selected[0], "values")
        treatment_id = row[0]
        medicine_name = row[2]
        patient_name = row[1]

        confirm = messagebox.askyesno(
            "Dispense Medicine",
            f"Are you sure you want to dispense '{medicine_name}' to {patient_name}?"
        )
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # 1. Look up the medicine in Inventory
            # Match case-insensitively
            cursor.execute("SELECT InventoryID, Stock, Quantity FROM Inventory WHERE LOWER(ItemName) = LOWER(%s)", (medicine_name,))
            inv_row = cursor.fetchone()

            if not inv_row:
                messagebox.showerror(
                    "Dispense Error",
                    f"The prescribed medicine '{medicine_name}' was not found in the Inventory.\n"
                    "Please add it to the inventory first."
                )
                conn.close()
                return

            inv_id, stock, total_qty = inv_row

            # 2. Check stock level
            if stock <= 0:
                messagebox.showerror(
                    "Dispense Error",
                    f"Out of Stock! '{medicine_name}' has 0 units remaining."
                )
                conn.close()
                return

            # 3. Decrement stock
            new_stock = stock - 1
            cursor.execute("UPDATE Inventory SET Stock = %s WHERE InventoryID = %s", (new_stock, inv_id))

            # 4. Update Treatment Status to 'Dispensed'
            cursor.execute("UPDATE Treatment SET DispensedStatus = 'Dispensed' WHERE TreatmentID = %s", (treatment_id,))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Successfully dispensed 1 unit of '{medicine_name}' for {patient_name}.\nRemaining Stock: {new_stock}")
            
            # Reload list and refresh pharmacist dashboard stats
            self.load_pending_prescriptions()
            self.dispense_btn.configure(state="disabled", fg_color="gray")
            self.info_lbl.configure(text="Select a pending prescription from the table to dispense.")
            
            if hasattr(self.master, "refresh_dashboard"):
                self.master.refresh_dashboard()

        except Exception as e:
            messagebox.showerror("Dispense Error", f"Failed to complete dispensing process:\n{e}")


if __name__ == "__main__":
    app = PharmacistDashboard()
    app.mainloop()
