import customtkinter as ctk
from tkinter import ttk, messagebox
from database import connect_db
from datetime import datetime
import session

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class PaymentWindow(ctk.CTkToplevel):
    """Payment & Billing Management Workspace."""

    def __init__(self, parent):
        super().__init__(parent)
        self.master = parent

        self.title("Payment & Billing Management")
        self.geometry("1500x850")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.selected_payment_id = None
        self.selected_patient_id = None
        self.selected_amount = 0.00

        self.worker_id = 2
        self.user_id = 1
        self.user_role = "Unknown"
        if hasattr(session, "current_user") and session.current_user:
            self.worker_id = session.current_user.get("worker_id", 2)
            self.user_id = session.current_user.get("user_id", 1)
            self.user_role = session.current_user.get("role", "Unknown")

        # Back Button
        back_btn = ctk.CTkButton(
            self,
            text="⬅ Back",
            width=100,
            command=self.destroy
        )
        back_btn.place(x=20, y=20)

        # Title
        title = ctk.CTkLabel(
            self,
            text="💳 Payment & Billing Center",
            font=("Arial", 30, "bold")
        )
        title.pack(pady=20)

        # Main Layout Frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Tabview for Form (Process Pending vs Create Manual Service Invoice) - hidden for Administrator
        if self.user_role == "Administrator":
            self.table_frame = ctk.CTkFrame(main_frame)
            self.table_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)
        else:
            self.form_tabview = ctk.CTkTabview(main_frame, width=420)
            self.form_tabview.pack(side="left", fill="y", padx=15, pady=15)
            
            self.tab_process = self.form_tabview.add("Process Pending Billing")
            self.tab_create = self.form_tabview.add("Add Service Invoice")

            self.setup_process_tab()
            self.setup_create_tab()

            # Right Panel (List Payments)
            self.table_frame = ctk.CTkFrame(main_frame)
            self.table_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        # Search Bar
        search_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=15, pady=10)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by Patient Name or ID...", width=300)
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.search_payment)

        ctk.CTkButton(search_frame, text="Search", command=self.search_payment, width=100).pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="Refresh", command=self.refresh_table, width=100).pack(side="left")

        # Payment Method Filter
        ctk.CTkLabel(search_frame, text="Method:", font=("Arial", 12, "bold")).pack(side="left", padx=(15, 5))
        self.filter_combo = ctk.CTkComboBox(
            search_frame,
            values=["All", "Cash", "Card", "Mobile Money", "Pending"],
            width=130,
            command=lambda choice: self.load_payments()
        )
        self.filter_combo.pack(side="left", padx=5)
        self.filter_combo.set("All")

        # Treeview setup
        container = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=15, pady=5)

        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side="right", fill="y")

        columns = ("ID", "Patient Name", "Amount", "Type", "Status / Method", "Billing Date")
        self.table = ttk.Treeview(
            container,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=18
        )
        for col in columns:
            self.table.heading(col, text=col, anchor="w")
            self.table.column(col, anchor="w", width=120)
        self.table.column("ID", width=50, anchor="center")

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.table.yview)

        # Selection Bind
        self.table.bind("<<TreeviewSelect>>", self.on_payment_selected)

        # Load initial values
        self.load_payments()

    def setup_process_tab(self):
        # UI controls to complete a pending payment
        ctk.CTkLabel(self.tab_process, text="Process Selected Pending Payment", font=("Arial", 14, "bold"), text_color="#1F6AA5").pack(pady=10)

        # Labels displaying selected info
        self.selected_patient_lbl = ctk.CTkLabel(self.tab_process, text="Patient: None selected", font=("Arial", 12, "bold"))
        self.selected_patient_lbl.pack(pady=8, anchor="w", padx=20)

        self.selected_type_lbl = ctk.CTkLabel(self.tab_process, text="Billing Type: N/A", font=("Arial", 12))
        self.selected_type_lbl.pack(pady=5, anchor="w", padx=20)

        self.selected_amount_lbl = ctk.CTkLabel(self.tab_process, text="Amount Due: Le 0.00", font=("Arial", 13, "bold"), text_color="#1F6AA5")
        self.selected_amount_lbl.pack(pady=8, anchor="w", padx=20)

        # Select Payment Method
        ctk.CTkLabel(self.tab_process, text="Select Payment Method:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(15, 2))
        self.method_combo = ctk.CTkComboBox(self.tab_process, width=320, values=["Cash", "Card", "Mobile Money"])
        self.method_combo.pack(pady=5)
        self.method_combo.set("Cash")

        # Process Button
        self.process_btn = ctk.CTkButton(
            self.tab_process,
            text="🔒 Collect Payment & Print",
            font=("Arial", 13, "bold"),
            fg_color="gray",
            state="disabled",
            command=self.complete_payment,
            height=38
        )
        self.process_btn.pack(pady=30, padx=20, fill="x")

    def setup_create_tab(self):
        # UI controls to manually issue an invoice for registration, consultation, or active hospital service
        ctk.CTkLabel(self.tab_create, text="Add Walk-in Service Invoice", font=("Arial", 14, "bold"), text_color="#1F6AA5").pack(pady=10)

        # Patient Combo
        ctk.CTkLabel(self.tab_create, text="Select Patient:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(5, 2))
        self.patient_combo = ctk.CTkComboBox(self.tab_create, width=320, values=[])
        self.patient_combo.pack(pady=5)
        
        self.load_patients()

        # Service Combo
        ctk.CTkLabel(self.tab_create, text="Select Service:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        self.service_combo = ctk.CTkComboBox(self.tab_create, width=320, values=[], command=self.on_service_selected)
        self.service_combo.pack(pady=5)

        self.load_services()

        # Service Price (read-only, fetched from Hospital_Services)
        ctk.CTkLabel(self.tab_create, text="Service Price (Le):", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        self.service_price_entry = ctk.CTkEntry(self.tab_create, width=320)
        self.service_price_entry.pack(pady=5)
        self.service_price_entry.configure(state="disabled")

        # Create invoice button
        ctk.CTkButton(
            self.tab_create,
            text="➕ Create Invoice",
            font=("Arial", 13, "bold"),
            command=self.create_manual_invoice,
            height=38
        ).pack(pady=30, padx=20, fill="x")

    def load_patients(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT PatientID, FullName FROM Patients ORDER BY PatientID DESC")
            rows = cursor.fetchall()
            conn.close()
            
            pat_list = [f"{name} (ID: {pid})" for pid, name in rows]
            self.patient_combo.configure(values=pat_list)
            if pat_list:
                self.patient_combo.set(pat_list[0])
        except Exception as e:
            print(f"Error loading patients combo: {e}")

    def load_services(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT ServiceID, ServiceName, Price FROM Hospital_Services WHERE Status = 'Active'")
            rows = cursor.fetchall()
            conn.close()
            
            svc_list = [f"{name} (ID: {sid} | Le {price:,.2f})" for sid, name, price in rows]
            self.service_combo.configure(values=svc_list)
            if svc_list:
                self.service_combo.set(svc_list[0])
                self.on_service_selected(svc_list[0])
        except Exception as e:
            print(f"Error loading services combo: {e}")

    def on_service_selected(self, value):
        try:
            price_val = value.split("| Le ")[1].replace(",", "").replace(")", "")
            self.service_price_entry.configure(state="normal")
            self.service_price_entry.delete(0, "end")
            self.service_price_entry.insert(0, price_val)
            self.service_price_entry.configure(state="disabled")
        except Exception as e:
            print(f"Error extracting price: {e}")

    def load_payments(self):
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # Check user role
            import session
            user_role = "Unknown"
            if hasattr(session, "current_user") and session.current_user:
                user_role = session.current_user.get("role", "Unknown")

            choice = self.filter_combo.get()
            
            query = """
                SELECT p.PaymentID, pat.FullName, p.Amount, p.PaymentType, p.PaymentMethod, p.PaymentDate
                FROM Payment p
                LEFT JOIN Patients pat ON p.PatientID = pat.PatientID
            """
            conditions = []
            params = []

            # Role constraint: Administrator and Accountant see all payments.
            # Receptionist can see all pending payments (e.g. Lab tests, Consultations) or payments billed by themselves.
            # Other roles (Pharmacist, Doctor, Lab Tech) see payments they billed/processed.
            if user_role != "Administrator" and user_role != "Accountant":
                if user_role == "Receptionist":
                    conditions.append("(p.PaymentMethod = 'Pending' OR p.BilledBy = %s)")
                    params.append(self.worker_id)
                else:
                    conditions.append("p.BilledBy = %s")
                    params.append(self.worker_id)

            # Filter condition
            if choice != "All":
                conditions.append("p.PaymentMethod = %s")
                params.append(choice)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY p.PaymentID DESC"

            cursor.execute(query, tuple(params))
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                cleaned[2] = f"Le {float(cleaned[2]):,.2f}" if cleaned[2] else "Le 0.00"
                self.table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error loading payments: {e}")

    def on_payment_selected(self, event):
        if self.user_role == "Administrator":
            return
        selected = self.table.selection()
        if not selected:
            return
        
        row = self.table.item(selected[0], "values")
        self.selected_payment_id = int(row[0])
        
        # Display selection details
        self.selected_patient_lbl.configure(text=f"Patient: {row[1]}")
        self.selected_type_lbl.configure(text=f"Billing Type: {row[3]}")
        self.selected_amount_lbl.configure(text=f"Amount Due: {row[2]}")
        
        self.selected_amount = float(row[2].replace("Le ", "").replace(",", ""))

        # Check status
        if row[4] == "Pending":
            if row[3] == "Medicines" and self.user_role == "Receptionist":
                self.process_btn.configure(state="disabled", fg_color="gray")
                self.process_btn.configure(text="❌ Medicines Paid to Pharmacist Only")
            else:
                self.process_btn.configure(state="normal", fg_color="#4CAF50")
                self.process_btn.configure(text="🔒 Collect Payment & Print")
        else:
            self.process_btn.configure(state="disabled", fg_color="gray")
            self.process_btn.configure(text="🔒 Invoice Paid Already")

    def create_manual_invoice(self):
        pat_val = self.patient_combo.get()
        svc_val = self.service_combo.get()
        
        if not pat_val or not svc_val:
            messagebox.showerror("Error", "Select both patient and service.")
            return

        try:
            patient_id = int(pat_val.split(" (ID: ")[1].replace(")", ""))
            service_id = int(svc_val.split(" (ID: ")[1].split(" |")[0])
            price = float(self.service_price_entry.get())
            service_name = svc_val.split(" (ID: ")[0]

            confirm = messagebox.askyesno("Confirm Invoice", f"Generate pending payment of Le {price:,.2f} for patient '{pat_val.split(' (ID')[0]}'?")
            if not confirm:
                return

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Payment (PatientID, Amount, PaymentType, ServiceID, LabRequestID, DispensingID, PaymentMethod, PaymentDate, BilledBy)
                VALUES (%s, %s, %s, %s, NULL, NULL, 'Pending', CURRENT_TIMESTAMP, %s)
            """, (patient_id, price, "Hospital Service", service_id, self.worker_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Pending service invoice added successfully!")
            self.load_payments()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to insert manual invoice:\n{e}")

    def complete_payment(self):
        if not self.selected_payment_id:
            return
            
        method = self.method_combo.get()
        
        confirm = messagebox.askyesno("Confirm Collection", f"Confirm payment collection of Le {self.selected_amount:,.2f} via {method}?")
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # 1. Update Payment status
            cursor.execute("""
                UPDATE Payment 
                SET PaymentMethod = %s, PaymentStatus = 'Paid', PaymentDate = CURRENT_TIMESTAMP, BilledBy = %s 
                WHERE PaymentID = %s
            """, (method, self.worker_id, self.selected_payment_id))

            # 2. Insert into Receipt
            cursor.execute("""
                INSERT INTO Receipt (PaymentID, IssueDate, PrintedBy)
                VALUES (%s, CURRENT_TIMESTAMP, %s)
            """, (self.selected_payment_id, self.worker_id))
            receipt_id = cursor.lastrowid

            # 3. Retrieve PatientID from Payment
            cursor.execute("SELECT PatientID FROM Payment WHERE PaymentID = %s", (self.selected_payment_id,))
            patient_id = cursor.fetchone()[0]

            conn.commit()
            conn.close()

            # Write audit logs
            from database import log_audit_action
            log_audit_action(self.user_id, f"Collected payment of Le {self.selected_amount:,.2f} for PatientID: {patient_id} (PaymentID: {self.selected_payment_id})")
            log_audit_action(self.user_id, f"Generated and printed receipt (ReceiptID: {receipt_id}) for PatientID: {patient_id}")

            messagebox.showinfo("Success", f"Payment completed successfully!\nReceipt ID: #{receipt_id}")
            
            # Print receipt PDF preview
            print_confirm = messagebox.askyesno("Print Receipt", "Would you like to print/export this Receipt as PDF now?")
            if print_confirm:
                self.open_receipt_print_dialog(receipt_id)

            self.load_payments()
            self.clear_fields()
            
            # Refresh receptionist dashboard parent metrics
            if hasattr(self.master, "refresh_dashboard"):
                self.master.refresh_dashboard()
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to complete payment transaction:\n{e}")

    def open_receipt_print_dialog(self, receipt_id):
        from receipt import ReceiptWindow
        r_win = ReceiptWindow(self)
        r_win.selected_receipt_id = receipt_id
        r_win.load_selected_receipt_details(receipt_id)

    def search_payment(self, event=None):
        q = self.search_entry.get().strip()
        if not q:
            self.load_payments()
            return
            
        for item in self.table.get_children():
            self.table.delete(item)
            
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            import session
            user_role = "Unknown"
            if hasattr(session, "current_user") and session.current_user:
                user_role = session.current_user.get("role", "Unknown")

            choice = self.filter_combo.get()

            query = """
                SELECT p.PaymentID, pat.FullName, p.Amount, p.PaymentType, p.PaymentMethod, p.PaymentDate
                FROM Payment p
                LEFT JOIN Patients pat ON p.PatientID = pat.PatientID
            """
            conditions = ["(pat.FullName LIKE %s OR p.PaymentID LIKE %s)"]
            params = [f"%{q}%", f"%{q}%"]

            if user_role == "Pharmacist":
                conditions.append("p.BilledBy = %s")
                params.append(self.worker_id)
            elif user_role == "Receptionist":
                conditions.append("(p.PaymentMethod = 'Pending' OR p.BilledBy = %s)")
                params.append(self.worker_id)
            elif user_role != "Administrator" and user_role != "Accountant":
                conditions.append("p.BilledBy = %s")
                params.append(self.worker_id)

            if choice != "All":
                conditions.append("p.PaymentMethod = %s")
                params.append(choice)

            query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY p.PaymentID DESC"

            cursor.execute(query, tuple(params))
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                cleaned[2] = f"Le {float(cleaned[2]):,.2f}" if cleaned[2] else "Le 0.00"
                self.table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error searching payments: {e}")

    def clear_fields(self):
        self.selected_payment_id = None
        self.selected_patient_id = None
        self.selected_amount = 0.00
        
        self.selected_patient_lbl.configure(text="Patient: None selected")
        self.selected_type_lbl.configure(text="Billing Type: N/A")
        self.selected_amount_lbl.configure(text="Amount Due: Le 0.00")
        
        self.process_btn.configure(state="disabled", fg_color="gray")
        self.process_btn.configure(text="🔒 Collect Payment & Print")
        
        self.table.selection_remove(self.table.selection())

    def refresh_table(self):
        self.search_entry.delete(0, "end")
        self.load_payments()
        self.clear_fields()


if __name__ == "__main__":
    class TestApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.geometry("1500x850")
            PaymentWindow(self)

    app = TestApp()
    app.mainloop()
