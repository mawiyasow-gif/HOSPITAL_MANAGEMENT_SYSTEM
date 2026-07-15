import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from database import connect_db
import os

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
            "worker_id": 5,
            "full_name": "Pharmacist Staff",
            "role": "Pharmacist"
        }
        self.pharmacist_worker_id = self.pharmacist_user.get("worker_id", 5)

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

        welcome_text = f"👋 Welcome Pharmacist, {self.pharmacist_user['full_name']}"
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
        self.stock_frame = ctk.CTkFrame(self.scrollable_frame)
        self.stock_frame.pack(fill="both", expand=True, pady=15)

        ctk.CTkLabel(self.stock_frame, text="📋 Current Pharmaceutical Stock Status", font=("Arial", 16, "bold"), text_color="#1F6AA5").pack(anchor="w", padx=20, pady=10)

        container = ctk.CTkFrame(self.stock_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)

        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side="right", fill="y")

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
        card = ctk.CTkFrame(parent, corner_radius=10, cursor="hand2" if command else None)
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

        value_label = ctk.CTkLabel(content_frame, text=value, font=("Arial", 20, "bold"), text_color="#1F6AA5")
        value_label.pack(anchor="w", padx=5, pady=(2, 5))

        if command:
            card.bind("<Button-1>", lambda e: command())
            icon_label.bind("<Button-1>", lambda e: command())
            title_label.bind("<Button-1>", lambda e: command())
            value_label.bind("<Button-1>", lambda e: command())
            
        card.value_label = value_label
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
        MedicineDispensingWindow(self)

    def logout(self):
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to sign out from the Pharmacist Panel?")
        if confirm:
            self.destroy()
            from login import LoginApp
            app = LoginApp()
            app.mainloop()


class MedicineDispensingWindow(ctk.CTkToplevel):
    """Pharmacy Medicine Dispensing interface."""

    def __init__(self, parent):
        super().__init__(parent)
        self.master = parent

        self.title("Pharmacy Medicine Dispensing Portal")
        self.geometry("1200x700")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

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

        columns = ("Prescription ID", "Patient Name", "Prescribed Medicine", "Dosage", "Qty", "Doctor", "Date")
        self.table = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=12)
        
        # Style
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=28)

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

        self.load_pending_prescriptions()

    def load_pending_prescriptions(self):
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT pr.PrescriptionID, p.FullName, pr.MedicineName, pr.Dosage, pr.QuantityPrescribed, hw.FullName, DATE(pr.DatePrescribed)
                FROM Prescription pr
                LEFT JOIN Patients p ON pr.PatientID = p.PatientID
                LEFT JOIN Health_Workers hw ON pr.DoctorID = hw.WorkerID
                WHERE pr.Status = 'Pending'
                ORDER BY pr.PrescriptionID DESC
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
            self.info_lbl.configure(text=f"Selected: {row[2]} (Qty: {row[4]}) for {row[1]}")
        else:
            self.dispense_btn.configure(state="disabled", fg_color="gray")
            self.info_lbl.configure(text="Select a pending prescription from the table to dispense.")

    def dispense_medicine(self):
        selected = self.table.selection()
        if not selected:
            return

        row = self.table.item(selected[0], "values")
        prescription_id = row[0]
        patient_name = row[1]
        medicine_name = row[2]
        qty_prescribed = int(row[4])

        confirm = messagebox.askyesno(
            "Dispense Medicine",
            f"Are you sure you want to dispense {qty_prescribed} unit(s) of '{medicine_name}' to {patient_name}?"
        )
        if not confirm:
            return

        # Prompt for payment method
        dialog = PaymentMethodDialog(self)
        self.wait_window(dialog)
        method = dialog.selected_method
        if not method:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # 1. Look up the medicine in Inventory
            cursor.execute("""
                SELECT InventoryID, Quantity, SellingPrice 
                FROM Inventory 
                WHERE LOWER(MedicineName) = LOWER(%s) AND Quantity > 0 
                LIMIT 1
            """, (medicine_name,))
            inv_row = cursor.fetchone()

            if not inv_row:
                messagebox.showerror(
                    "Dispense Error",
                    f"The prescribed medicine '{medicine_name}' is currently OUT OF STOCK.\n"
                    "Please contact the Administrator to restock."
                )
                conn.close()
                return

            inv_id, current_qty, selling_price = inv_row

            # 2. Check if inventory has enough stock
            if current_qty < qty_prescribed:
                messagebox.showerror(
                    "Dispense Error",
                    f"Insufficient Stock! '{medicine_name}' only has {current_qty} unit(s) in stock.\n"
                    f"Required: {qty_prescribed} unit(s)."
                )
                conn.close()
                return

            # 3. Decrement Quantity in Inventory
            new_qty = current_qty - qty_prescribed
            cursor.execute("UPDATE Inventory SET Quantity = %s WHERE InventoryID = %s", (new_qty, inv_id))

            # 4. Record details in Medicine_Dispensing table
            cursor.execute("""
                INSERT INTO Medicine_Dispensing (PrescriptionID, InventoryID, QuantityDispensed, DispensedDate, PharmacistID)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s)
            """, (prescription_id, inv_id, qty_prescribed, self.master.pharmacist_worker_id))
            dispensing_id = cursor.lastrowid

            # 5. Update Prescription Status to 'Dispensed'
            cursor.execute("UPDATE Prescription SET Status = 'Dispensed' WHERE PrescriptionID = %s", (prescription_id,))

            # 6. Retrieve PatientID from Prescription
            cursor.execute("SELECT PatientID FROM Prescription WHERE PrescriptionID = %s", (prescription_id,))
            patient_id = cursor.fetchone()[0]

            # 7. Create Payment record for Medicines
            total_amount = qty_prescribed * float(selling_price)
            cursor.execute("""
                INSERT INTO Payment (PatientID, Amount, PaymentType, ServiceID, LabRequestID, DispensingID, PaymentMethod, PaymentDate, BilledBy)
                VALUES (%s, %s, 'Medicines', NULL, NULL, %s, %s, CURRENT_TIMESTAMP, %s)
            """, (patient_id, total_amount, dispensing_id, method, self.master.pharmacist_worker_id))
            payment_id = cursor.lastrowid

            # 8. Create Receipt record (prints medicine receipt)
            cursor.execute("""
                INSERT INTO Receipt (PaymentID, IssueDate, PrintedBy)
                VALUES (%s, CURRENT_TIMESTAMP, %s)
            """, (payment_id, self.master.pharmacist_worker_id))
            receipt_id = cursor.lastrowid

            conn.commit()
            conn.close()
 
            # Write audit logs
            user_id = self.master.pharmacist_user.get("user_id", 1)
            from database import log_audit_action
            log_audit_action(user_id, f"Dispensed {qty_prescribed} unit(s) of '{medicine_name}' (DispensingID: {dispensing_id}) for PatientID: {patient_id}")
            log_audit_action(user_id, f"Created medicine payment of Le {total_amount:,.2f} for PatientID: {patient_id} (PaymentID: {payment_id})")
            log_audit_action(user_id, f"Generated medicine receipt (ReceiptID: {receipt_id}) for PatientID: {patient_id}")
 
            messagebox.showinfo(
                "Success", 
                f"Dispensed successfully!\n"
                f"Medicine: {medicine_name}\n"
                f"Quantity: {qty_prescribed} units\n"
                f"Remaining Stock: {new_qty} units\n"
                f"Receipt ID generated: #{receipt_id}"
            )
            
            # Ask to print receipt
            print_confirm = messagebox.askyesno("Print Receipt", "Would you like to print/export the Medicine Receipt now?")
            if print_confirm:
                self.open_receipt_print_dialog(receipt_id)

            # Reload lists and stats
            self.load_pending_prescriptions()
            self.dispense_btn.configure(state="disabled", fg_color="gray")
            self.info_lbl.configure(text="Select a pending prescription from the table to dispense.")
            
            self.master.refresh_dashboard()

        except Exception as e:
            messagebox.showerror("Dispense Error", f"Failed to complete dispensing process:\n{e}")

    def open_receipt_print_dialog(self, receipt_id):
        # We can import and trigger receipt PDF popup directly
        from receipt import ReceiptWindow
        r_win = ReceiptWindow(self)
        r_win.selected_receipt_id = receipt_id
        r_win.load_selected_receipt_details(receipt_id)


class PaymentMethodDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Select Payment Method")
        self.geometry("420x220")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.selected_method = None

        ctk.CTkLabel(
            self, 
            text="💳 Select Payment Method for Medicines", 
            font=("Arial", 16, "bold"),
            text_color="#1F6AA5"
        ).pack(pady=25)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="💵 Cash", width=100, command=lambda: self.select("Cash")).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="📱 Mobile Money", width=120, command=lambda: self.select("Mobile Money")).grid(row=0, column=1, padx=5)
        ctk.CTkButton(btn_frame, text="💳 Card", width=100, command=lambda: self.select("Card")).grid(row=0, column=2, padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def select(self, method):
        self.selected_method = method
        self.destroy()

    def on_close(self):
        self.selected_method = None
        self.destroy()


if __name__ == "__main__":
    app = PharmacistDashboard()
    app.mainloop()
