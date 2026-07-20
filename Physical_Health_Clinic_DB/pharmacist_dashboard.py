import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from database import connect_db
import os

import dashboard_theme

# Set appearance mode and color theme
dashboard_theme.apply_global_theme()

class PharmacistDashboard(ctk.CTk):
    """Pharmacist Dashboard for the Physical Health Clinic Record System."""

    def __init__(self, pharmacist_user=None):
        super().__init__()

        self.title("Physical Health Clinic Record System - Pharmacist Dashboard")
        self.geometry("1600x900")
        self.resizable(True, True)

        self.pharmacist_user = pharmacist_user or {
            "user_id": 5,
            "worker_id": 5,
            "full_name": "Pharmacist Staff",
            "role": "Pharmacist"
        }
        self.pharmacist_worker_id = self.pharmacist_user.get("worker_id", 5)

        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color=dashboard_theme.BG_COLOR)
        self.main_container.pack(fill="both", expand=True)

        # Left Sidebar (Navigation)
        self.sidebar = ctk.CTkFrame(self.main_container, width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        dashboard_theme.style_sidebar(self.sidebar)

        sidebar_title = ctk.CTkLabel(
            self.sidebar,
            text="🏥 PHARMACY PANEL",
            font=("Arial", 18, "bold"),
            text_color=dashboard_theme.TEXT_PRIMARY
        )
        sidebar_title.pack(pady=30)

        # Menu items for Pharmacist
        menu_items = [
            ("🏠 Dashboard", self.refresh_dashboard),
            ("📦 Inventory", self.open_inventory),
            ("⚡ Dispense Medicine", self.open_dispensing),
            ("🧾 Receipts", self.open_receipts),
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
                btn.pack(side="bottom", pady=20)
            else:
                is_active = (text == "🏠 Dashboard")
                btn = dashboard_theme.create_sidebar_button(
                    self.sidebar,
                    text=text,
                    command=command,
                    active=is_active
                )
                btn.pack(pady=6)

        # Right View Area
        self.content_frame = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color=dashboard_theme.BG_COLOR)
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.scrollable_frame = ctk.CTkScrollableFrame(self.content_frame, corner_radius=0, fg_color=dashboard_theme.BG_COLOR)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header Info Bar
        self.header_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="#FFFFFF",
            border_color=dashboard_theme.BORDER_COLOR,
            border_width=1,
            corner_radius=12
        )
        self.header_frame.pack(fill="x", pady=(0, 10))

        welcome_text = f"Welcome back, Pharmacist! 👋"
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

        # Clickable Stat Cards
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

        # Table showing Active Stock
        self.stock_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#FFFFFF", border_color=dashboard_theme.BORDER_COLOR, border_width=1, corner_radius=12)
        self.stock_frame.pack(fill="both", expand=True, pady=15)

        ctk.CTkLabel(self.stock_frame, text="📋 Current Pharmaceutical Stock Status", font=("Arial", 16, "bold"), text_color=dashboard_theme.TEXT_PRIMARY).pack(anchor="w", padx=20, pady=10)

        container = ctk.CTkFrame(self.stock_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 15))

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

        columns = ("Medicine Name", "Batch Number", "Quantity In Stock", "Selling Price", "Expiry Date", "Supplier")
        self.stock_table = ttk.Treeview(container, columns=columns, show="headings", yscrollcommand=scrollbar.set, height=12)
        for col in columns:
            self.stock_table.heading(col, text=col, anchor="w")
            self.stock_table.column(col, anchor="w", width=200)
        self.stock_table.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.stock_table.yview)

        self.refresh_dashboard()

    def update_clock(self):
        self.time_lbl.configure(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self.update_clock)

    def create_stat_card(self, parent, icon, title, value, color, command=None):
        """Create a modern clickable statistics card."""
        return dashboard_theme.create_modern_stat_card(parent, icon, title, value, color, command)
        return card

    def refresh_dashboard(self):
        self.load_dashboard_statistics()
        self.load_stock_table()

    def load_dashboard_statistics(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # Total medicine kinds
            cursor.execute("SELECT COUNT(*) FROM Inventory")
            self.inventory_card.value_label.configure(text=str(cursor.fetchone()[0]))

            # Low stock items (< 10 units)
            cursor.execute("SELECT COUNT(*) FROM Inventory WHERE Quantity < 10")
            self.low_stock_card.value_label.configure(text=str(cursor.fetchone()[0]))

            # Expired medicines
            cursor.execute("SELECT COUNT(*) FROM Inventory WHERE ExpiryDate < CURDATE()")
            self.expired_card.value_label.configure(text=str(cursor.fetchone()[0]))

            # Pending dispenses
            cursor.execute("SELECT COUNT(*) FROM Prescription WHERE Status = 'Pending'")
            self.prescriptions_card.value_label.configure(text=str(cursor.fetchone()[0]))

            conn.close()
        except Exception as e:
            print(f"Error loading stats: {e}")

    def load_stock_table(self):
        for item in self.stock_table.get_children():
            self.stock_table.delete(item)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT MedicineName, BatchNumber, Quantity, SellingPrice, ExpiryDate, Supplier
                FROM Inventory
                ORDER BY MedicineName ASC
            """)
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                cleaned[3] = f"Le {float(cleaned[3]):,.2f}" if cleaned[3] else "Le 0.00"
                self.stock_table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error loading stock: {e}")

    def open_inventory(self):
        from inventory import InventoryWindow
        InventoryWindow(self)

    def open_dispensing(self):
        """Open Medicine Dispensing window."""
        MedicineDispensingWindow(self)

    def open_receipts(self):
        """Open Receipt management module."""
        from receipt import ReceiptWindow
        ReceiptWindow(self)

    def logout(self):
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to sign out from the Pharmacist Panel?")
        if confirm:
            self.destroy()
            from login import LoginApp
            app = LoginApp()
            app.mainloop()


class MedicineDispensingWindow(ctk.CTkToplevel):
    """Grouped Prescription Dispensing and Integrated Payment Processing."""

    def __init__(self, parent):
        super().__init__(parent)
        self.master = parent

        self.title("Pharmacy Dispensing & Cashier Portal")
        self.geometry("1400x820")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        # Selected prescription tracking
        self.selected_treatment_id = None
        self.selected_patient_id = None
        self.selected_patient_name = None
        self.selected_status = None
        self.prescription_items = []
        self.grand_total = 0.00

        # Title
        ctk.CTkLabel(
            self,
            text="💊 Pharmacy Dispensing & Integrated Payment Portal",
            font=("Arial", 22, "bold"),
            text_color="#1F6AA5"
        ).pack(pady=15)

        # Main Split Workspace
        workspace = ctk.CTkFrame(self, fg_color="transparent")
        workspace.pack(fill="both", expand=True, padx=20, pady=10)

        # ==============================
        # Left Panel: Pending Queue
        # ==============================
        left_panel = ctk.CTkFrame(workspace, fg_color=dashboard_theme.CARD_BG, border_color=dashboard_theme.BORDER_COLOR, border_width=1, corner_radius=12)
        left_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(
            left_panel,
            text="📋 Pending Prescriptions Queue",
            font=("Arial", 15, "bold"),
            text_color=dashboard_theme.TEXT_PRIMARY
        ).pack(anchor="w", padx=15, pady=10)

        container_queue = ctk.CTkFrame(left_panel, fg_color="transparent")
        container_queue.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        scrollbar_queue = ttk.Scrollbar(container_queue)
        scrollbar_queue.pack(side="right", fill="y")

        columns_queue = ("Presc ID", "Patient Name", "Date", "Doctor", "Medicines", "Status")
        self.queue_table = ttk.Treeview(
            container_queue,
            columns=columns_queue,
            show="headings",
            yscrollcommand=scrollbar_queue.set,
            height=15
        )
        for col in columns_queue:
            self.queue_table.heading(col, text=col, anchor="center")
            self.queue_table.column(col, width=110, anchor="center")
        self.queue_table.column("Patient Name", width=140)
        self.queue_table.column("Medicines", width=250, anchor="w")
        self.queue_table.column("Status", width=130)

        self.queue_table.pack(side="left", fill="both", expand=True)
        scrollbar_queue.config(command=self.queue_table.yview)
        self.queue_table.bind("<<TreeviewSelect>>", self.on_select_prescription)

        # ==============================
        # Right Panel: Detail & Action Panel
        # ==============================
        self.right_panel = ctk.CTkFrame(workspace, fg_color=dashboard_theme.CARD_BG, border_color=dashboard_theme.BORDER_COLOR, border_width=1, corner_radius=12, width=640)
        self.right_panel.pack(side="right", fill="both", expand=False, padx=5, pady=5)
        self.right_panel.pack_propagate(False)

        ctk.CTkLabel(
            self.right_panel,
            text="🩺 Prescription & Billing Summary",
            font=("Arial", 15, "bold"),
            text_color=dashboard_theme.TEXT_PRIMARY
        ).pack(anchor="w", padx=20, pady=10)

        # Patient Context Box
        self.patient_info_frame = ctk.CTkFrame(self.right_panel, fg_color="#F8FAFC", corner_radius=8)
        self.patient_info_frame.pack(fill="x", padx=20, pady=5)

        self.patient_lbl = ctk.CTkLabel(self.patient_info_frame, text="Patient: No selection", font=("Arial", 12, "bold"), text_color=dashboard_theme.TEXT_PRIMARY)
        self.patient_lbl.pack(anchor="w", padx=15, pady=4)

        self.presc_meta_lbl = ctk.CTkLabel(self.patient_info_frame, text="Prescription details will appear here.", font=("Arial", 11), text_color=dashboard_theme.TEXT_SECONDARY)
        self.presc_meta_lbl.pack(anchor="w", padx=15, pady=4)

        # Table showing Prescription Items
        self.items_container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.items_container.pack(fill="both", expand=True, padx=20, pady=10)

        scrollbar_items = ttk.Scrollbar(self.items_container)
        scrollbar_items.pack(side="right", fill="y")

        columns_items = ("Medicine", "Qty", "Price", "Subtotal", "Stock Status")
        self.items_table = ttk.Treeview(
            self.items_container,
            columns=columns_items,
            show="headings",
            yscrollcommand=scrollbar_items.set,
            height=6
        )
        for col in columns_items:
            self.items_table.heading(col, text=col, anchor="w")
            self.items_table.column(col, width=90, anchor="w")
        self.items_table.column("Medicine", width=160)
        self.items_table.column("Stock Status", width=120)

        self.items_table.pack(side="left", fill="both", expand=True)
        scrollbar_items.config(command=self.items_table.yview)

        # Grand Total Card
        self.total_card = ctk.CTkFrame(self.right_panel, fg_color="#F0FDF4", border_color="#DCFCE7", border_width=1, corner_radius=10, height=60)
        self.total_card.pack(fill="x", padx=20, pady=10)
        self.total_card.pack_propagate(False)

        self.total_lbl = ctk.CTkLabel(self.total_card, text="Grand Total: Le 0.00", font=("Arial", 18, "bold"), text_color="#15803D")
        self.total_lbl.pack(side="left", padx=25, pady=15)

        # Action Panel Split
        self.action_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.action_frame.pack(fill="x", padx=20, pady=5)

        # Dispensing Control
        self.dispense_frame = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        self.dispense_frame.pack(fill="x", pady=5)
        
        self.dispense_btn = ctk.CTkButton(
            self.dispense_frame,
            text="⚡ Step 1: Dispense Medicines",
            font=("Arial", 13, "bold"),
            fg_color="gray",
            state="disabled",
            height=40,
            command=self.dispense_prescription
        )
        self.dispense_btn.pack(fill="x")

        # Payment Control
        self.payment_frame = ctk.CTkFrame(self.action_frame, fg_color="#F8FAFC", corner_radius=10, border_color=dashboard_theme.BORDER_COLOR, border_width=1)
        self.payment_frame.pack(fill="x", pady=5, ipady=10)

        ctk.CTkLabel(
            self.payment_frame,
            text="💵 Step 2: Integrated Payment Collection",
            font=("Arial", 12, "bold"),
            text_color=dashboard_theme.TEXT_PRIMARY
        ).pack(anchor="w", padx=15, pady=(8, 4))

        select_pay_frame = ctk.CTkFrame(self.payment_frame, fg_color="transparent")
        select_pay_frame.pack(fill="x", padx=15, pady=4)
        
        ctk.CTkLabel(select_pay_frame, text="Payment Method:", font=("Arial", 12)).pack(side="left", padx=5)
        
        self.method_combo = ctk.CTkComboBox(
            select_pay_frame,
            values=["Cash", "Orange Money", "AfriMoney", "QMoney", "Wave"],
            width=160
        )
        self.method_combo.pack(side="left", padx=10)
        self.method_combo.set("Cash")

        self.pay_btn = ctk.CTkButton(
            self.payment_frame,
            text="Receive Payment",
            font=("Arial", 13, "bold"),
            fg_color="gray",
            state="disabled",
            height=40,
            command=self.receive_payment
        )
        self.pay_btn.pack(fill="x", padx=15, pady=(10, 0))

        # Initial Load
        self.load_pending_prescriptions()

    def load_pending_prescriptions(self):
        for item in self.queue_table.get_children():
            self.queue_table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            # Fetch grouped TreatmentID (representing the prescription list)
            query = """
                SELECT pr.TreatmentID, p.FullName, DATE(pr.DatePrescribed), hw.FullName, 
                       GROUP_CONCAT(pr.MedicineName SEPARATOR ', '), pr.Status, p.PatientID
                FROM Prescription pr
                LEFT JOIN Patients p ON pr.PatientID = p.PatientID
                LEFT JOIN Health_Workers hw ON pr.DoctorID = hw.WorkerID
                WHERE pr.Status IN ('Pending', 'Dispensed')
                GROUP BY pr.TreatmentID, p.FullName, DATE(pr.DatePrescribed), hw.FullName, pr.Status, p.PatientID
                ORDER BY pr.Status DESC, pr.TreatmentID DESC
            """
            cursor.execute(query)
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                
                # Format Status visually
                status = cleaned[5]
                if status == 'Pending':
                    cleaned[5] = "⏳ Pending Dispense"
                elif status == 'Dispensed':
                    cleaned[5] = "💵 Pending Payment"

                # Keep TreatmentID raw, but format visual columns
                self.queue_table.insert("", "end", values=(
                    f"PR-{int(cleaned[0]):04d}",
                    cleaned[1],
                    cleaned[2],
                    cleaned[3],
                    cleaned[4],
                    cleaned[5],
                    cleaned[6]  # Hidden PatientID context
                ))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load pending prescriptions:\n{e}")

    def on_select_prescription(self, event):
        selected = self.queue_table.selection()
        if not selected:
            self.clear_details()
            return

        row = self.queue_table.item(selected[0], "values")
        treatment_id = int(row[0].replace("PR-", ""))
        patient_name = row[1]
        date_prescribed = row[2]
        doctor_name = row[3]
        status_label = row[5]

        self.selected_treatment_id = treatment_id
        self.selected_patient_name = patient_name
        self.selected_patient_id = int(row[6])
        
        # Load details
        self.patient_lbl.configure(text=f"Patient: {patient_name} (PR-{treatment_id:04d})")
        self.presc_meta_lbl.configure(text=f"Doctor: {doctor_name} | Date: {date_prescribed}")

        # Clear Items Table
        for item in self.items_table.get_children():
            self.items_table.delete(item)

        self.prescription_items = []
        self.grand_total = 0.00
        has_stock_error = False

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pr.PrescriptionID, pr.MedicineName, pr.QuantityPrescribed, pr.Status
                FROM Prescription pr
                WHERE pr.TreatmentID = %s AND pr.Status IN ('Pending', 'Dispensed')
            """, (treatment_id,))
            rows = cursor.fetchall()

            for presc_id, med_name, qty, item_status in rows:
                # Query stock availability & price
                cursor.execute("""
                    SELECT InventoryID, Quantity, SellingPrice 
                    FROM Inventory 
                    WHERE LOWER(MedicineName) = LOWER(%s)
                """, (med_name,))
                inv = cursor.fetchone()

                if inv:
                    inv_id, current_qty, sell_price = inv
                    subtotal = qty * float(sell_price)
                    self.grand_total += subtotal

                    if current_qty == 0:
                        stock_status = "🔴 Out of Stock"
                        has_stock_error = True
                    elif current_qty < qty:
                        stock_status = f"🔴 Low (In Stock: {current_qty})"
                        has_stock_error = True
                    else:
                        stock_status = f"🟢 In Stock ({current_qty})"

                    self.prescription_items.append({
                        'presc_id': presc_id,
                        'med_name': med_name,
                        'qty': qty,
                        'inv_id': inv_id,
                        'current_qty': current_qty,
                        'price': float(sell_price),
                        'subtotal': subtotal
                    })

                    self.items_table.insert("", "end", values=(
                        med_name,
                        qty,
                        f"Le {float(sell_price):,.2f}",
                        f"Le {subtotal:,.2f}",
                        stock_status
                    ))
                else:
                    self.items_table.insert("", "end", values=(
                        med_name,
                        qty,
                        "N/A",
                        "N/A",
                        "🔴 Out of Stock"
                    ))
                    has_stock_error = True

            conn.close()

            # Set Grand Total Label
            self.total_lbl.configure(text=f"Grand Total: Le {self.grand_total:,.2f}")

            # Check logical workflow state (Dispense vs Collect Payment)
            if "Pending Dispense" in status_label:
                self.selected_status = 'Pending'
                if has_stock_error:
                    self.dispense_btn.configure(state="disabled", fg_color="gray", text="⚡ Insufficient Inventory")
                else:
                    self.dispense_btn.configure(state="normal", fg_color="#3B82F6", text="⚡ Step 1: Dispense Medicines")
                self.pay_btn.configure(state="disabled", fg_color="gray")
            elif "Pending Payment" in status_label:
                self.selected_status = 'Dispensed'
                self.dispense_btn.configure(state="disabled", fg_color="gray", text="✅ Already Dispensed")
                self.pay_btn.configure(state="normal", fg_color="#10B981")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve prescription details:\n{e}")

    def clear_details(self):
        self.selected_treatment_id = None
        self.selected_patient_id = None
        self.selected_patient_name = None
        self.selected_status = None
        self.prescription_items = []
        self.grand_total = 0.00
        self.patient_lbl.configure(text="Patient: No selection")
        self.presc_meta_lbl.configure(text="Prescription details will appear here.")
        self.total_lbl.configure(text="Grand Total: Le 0.00")
        self.dispense_btn.configure(state="disabled", fg_color="gray", text="⚡ Step 1: Dispense Medicines")
        self.pay_btn.configure(state="disabled", fg_color="gray")
        for item in self.items_table.get_children():
            self.items_table.delete(item)

    def dispense_prescription(self):
        if not self.selected_treatment_id or self.selected_status != 'Pending':
            return

        confirm = messagebox.askyesno(
            "Confirm Dispensing",
            f"Are you sure you want to dispense prescription PR-{self.selected_treatment_id:04d} for {self.selected_patient_name}?"
        )
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Iterate and dispense each line item
            for item in self.prescription_items:
                presc_id = item['presc_id']
                inv_id = item['inv_id']
                qty = item['qty']
                current_qty = item['current_qty']

                # Double check inventory levels
                if current_qty < qty:
                    messagebox.showerror("Stock Error", f"Insufficient inventory for {item['med_name']}.\nProcess canceled.")
                    conn.close()
                    return

                # 1. Decrement Quantity in Inventory
                new_qty = current_qty - qty
                cursor.execute("UPDATE Inventory SET Quantity = %s WHERE InventoryID = %s", (new_qty, inv_id))

                # 2. Record in Medicine_Dispensing
                cursor.execute("""
                    INSERT INTO Medicine_Dispensing (PrescriptionID, InventoryID, QuantityDispensed, DispensedDate, PharmacistID)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s)
                """, (presc_id, inv_id, qty, self.master.pharmacist_worker_id))

                # 3. Update individual Prescription status to 'Dispensed'
                cursor.execute("UPDATE Prescription SET Status = 'Dispensed' WHERE PrescriptionID = %s", (presc_id,))

            conn.commit()
            conn.close()

            # Write audit log
            user_id = self.master.pharmacist_user.get("user_id", 1)
            from database import log_audit_action
            log_audit_action(user_id, f"Dispensed items for Prescription/Treatment ID: {self.selected_treatment_id} (Patient: {self.selected_patient_name})")

            messagebox.showinfo("Success", f"Prescription PR-{self.selected_treatment_id:04d} successfully dispensed!\nPlease collect payment now.")
            
            # Reload views
            self.load_pending_prescriptions()
            self.clear_details()
            self.master.refresh_dashboard()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to dispense prescription:\n{e}")

    def receive_payment(self):
        if not self.selected_treatment_id or self.selected_status != 'Dispensed':
            return

        method = self.method_combo.get()
        confirm = messagebox.askyesno(
            "Confirm Payment",
            f"Confirm payment collection of Le {self.grand_total:,.2f} via {method} for PR-{self.selected_treatment_id:04d}?"
        )
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # 1. Create a single grouped Payment record for this entire prescription
            cursor.execute("""
                INSERT INTO Payment (PatientID, Amount, PaymentType, PrescriptionID, PaymentMethod, PaymentDate, BilledBy, PharmacistID, PaymentStatus)
                VALUES (%s, %s, 'Medicines', %s, %s, CURRENT_TIMESTAMP, %s, %s, 'Paid')
            """, (self.selected_patient_id, self.grand_total, self.selected_treatment_id, method, self.master.pharmacist_worker_id, self.master.pharmacist_worker_id))
            payment_id = cursor.lastrowid

            # 2. Create corresponding Receipt record
            cursor.execute("""
                INSERT INTO Receipt (PaymentID, IssueDate, PrintedBy)
                VALUES (%s, CURRENT_TIMESTAMP, %s)
            """, (payment_id, self.master.pharmacist_worker_id))
            receipt_id = cursor.lastrowid

            # 3. Mark all prescriptions in this Treatment group as 'Paid'
            cursor.execute("UPDATE Prescription SET Status = 'Paid' WHERE TreatmentID = %s", (self.selected_treatment_id,))

            conn.commit()
            conn.close()

            # Write audit logs
            user_id = self.master.pharmacist_user.get("user_id", 1)
            from database import log_audit_action
            log_audit_action(user_id, f"Collected payment of Le {self.grand_total:,.2f} via {method} for Prescription ID: {self.selected_treatment_id} (ReceiptID: {receipt_id})")

            messagebox.showinfo("Success", f"Payment received successfully!\nGroup Receipt ID generated: #{receipt_id}")
            
            # Print/Export receipt
            print_confirm = messagebox.askyesno("Print Receipt", "Would you like to print/export the grouped PDF Receipt now?")
            if print_confirm:
                self.open_receipt_print_dialog(receipt_id)

            # Reload views
            self.load_pending_prescriptions()
            self.clear_details()
            self.master.refresh_dashboard()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete payment receipt:\n{e}")

    def open_receipt_print_dialog(self, receipt_id):
        from receipt import ReceiptWindow
        r_win = ReceiptWindow(self)
        r_win.selected_receipt_id = receipt_id
        r_win.load_selected_receipt_details(receipt_id)


if __name__ == "__main__":
    app = PharmacistDashboard()
    app.mainloop()
