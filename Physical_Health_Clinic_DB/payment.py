import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from database import connect_db

# -----------------------------
# CustomTkinter Settings
# -----------------------------
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class PaymentWindow(ctk.CTkToplevel):
    """Payment Management Window for the Physical Health Clinic Record System."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("💰 Payment Management")
        self.geometry("1500x850")
        self.resizable(True, True)

        # Track selected payment ID
        self.selected_payment_id = None

        # ==============================
        # Back Button
        # ==============================

        back_btn = ctk.CTkButton(
            self,
            text="⬅ Back",
            width=100,
            command=self.destroy
        )
        back_btn.place(x=20, y=20)

        # ==============================
        # Window Title
        # ==============================

        title = ctk.CTkLabel(
            self,
            text="💰 Payment Management",
            font=("Arial", 30, "bold")
        )
        title.pack(pady=20)

        # ==============================
        # Main Frame
        # ==============================

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ==============================
        # Left Panel (Payment Form)
        # ==============================

        form_frame = ctk.CTkFrame(main_frame, width=420)
        form_frame.pack(side="left", fill="y", padx=15, pady=15)

        ctk.CTkLabel(
            form_frame,
            text="Payment Information",
            font=("Arial", 22, "bold")
        ).pack(pady=20)

        # Patient ComboBox
        ctk.CTkLabel(
            form_frame,
            text="Select Patient:",
            font=("Arial", 14)
        ).pack(pady=(10, 2), anchor="w", padx=50)

        self.patient_combo = ctk.CTkComboBox(form_frame, width=320, values=[])
        self.patient_combo.pack(pady=5)

        # Amount Paid Entry
        ctk.CTkLabel(
            form_frame,
            text="Amount Paid:",
            font=("Arial", 14)
        ).pack(pady=(10, 2), anchor="w", padx=50)

        self.amount_entry = ctk.CTkEntry(
            form_frame,
            width=320,
            placeholder_text="Enter amount (e.g., 5000)"
        )
        self.amount_entry.pack(pady=5)

        # Payment Date Entry
        ctk.CTkLabel(
            form_frame,
            text="Payment Date (YYYY-MM-DD HH:MM:SS):",
            font=("Arial", 14)
        ).pack(pady=(10, 2), anchor="w", padx=50)

        self.date_entry = ctk.CTkEntry(
            form_frame,
            width=320,
            placeholder_text="Auto-filled on Add Payment"
        )
        self.date_entry.pack(pady=5)

        # Payment Method ComboBox
        ctk.CTkLabel(
            form_frame,
            text="Payment Method:",
            font=("Arial", 14)
        ).pack(pady=(10, 2), anchor="w", padx=50)

        payment_methods = [
            "Cash",
            "Orange Money",
            "AfriMoney",
            "QMoney",
            "Wave",
            "Bank Transfer",
            "Credit Card",
            "Debit Card"
        ]
        self.payment_method_combo = ctk.CTkComboBox(
            form_frame,
            width=320,
            values=payment_methods
        )
        self.payment_method_combo.pack(pady=5)

        # ==============================
        # Action Buttons
        # ==============================

        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=25)

        ctk.CTkButton(
            button_frame,
            text="➕ Add Payment",
            width=140,
            command=self.add_payment
        ).grid(row=0, column=0, padx=5, pady=5)

        ctk.CTkButton(
            button_frame,
            text="✏️ Update",
            width=140,
            command=self.update_payment
        ).grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkButton(
            button_frame,
            text="❌ Delete",
            width=140,
            command=self.delete_payment
        ).grid(row=1, column=0, padx=5, pady=5)

        ctk.CTkButton(
            button_frame,
            text="🧹 Clear",
            width=140,
            command=self.clear_fields
        ).grid(row=1, column=1, padx=5, pady=5)

        # Generate Receipt Button
        ctk.CTkButton(
            button_frame,
            text="🖨️ Generate Receipt",
            width=290,
            command=self.generate_receipt
        ).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # ==============================
        # Right Panel (Treeview Table)
        # ==============================

        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        # Search bar at top of right panel
        search_frame = ctk.CTkFrame(table_frame)
        search_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            search_frame,
            text="🔍 Search:",
            font=("Arial", 14)
        ).pack(side="left", padx=10)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=300,
            placeholder_text="Patient Name, Payment Method, or Date"
        )
        self.search_entry.pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="Search",
            width=100,
            command=self.search_payment
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="🔄 Refresh",
            width=100,
            command=self.refresh_table
        ).pack(side="left", padx=5)

        # Payment count label
        self.count_label = ctk.CTkLabel(
            search_frame,
            text="Total Payments: 0",
            font=("Arial", 14, "bold"),
            text_color="#1F6AA5"
        )
        self.count_label.pack(side="right", padx=20)

        # Total amount label
        self.total_label = ctk.CTkLabel(
            search_frame,
            text="Total Amount: Le 0",
            font=("Arial", 14, "bold"),
            text_color="#1F6AA5"
        )
        self.total_label.pack(side="right", padx=20)

        # Treeview columns
        columns = (
            "Payment ID",
            "Patient",
            "Amount Paid",
            "Payment Date",
            "Payment Method"
        )

        # Style Treeview table (dark theme consistent with other modules)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            rowheight=35,
            font=("Arial", 13)
        )
        style.map(
            "Treeview",
            background=[("selected", "#1F6AA5")],
            foreground=[("selected", "white")]
        )
        style.configure(
            "Treeview.Heading",
            background="#1f1f1f",
            foreground="white",
            font=("Arial", 14, "bold"),
            relief="flat"
        )
        style.map(
            "Treeview.Heading",
            background=[("active", "#2d2d2d")]
        )

        # Create Treeview widget
        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=20
        )

        for col in columns:
            self.table.heading(col, text=col, anchor="center")
            self.table.column(col, width=120, anchor="center")

        # Make Patient and Payment Method columns wider
        self.table.column("Patient", width=200, anchor="center")
        self.table.column("Payment Method", width=150, anchor="center")

        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )

        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.table.xview
        )

        self.table.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )

        # Pack scrollbars and treeview
        h_scrollbar.pack(side="bottom", fill="x")
        self.table.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")

        # Bind row selection to populate the form
        self.table.bind("<<TreeviewSelect>>", self.select_payment)

        # Load initial data into ComboBoxes and Treeview
        self.load_patients()
        self.load_payments()

    # ==============================
    # Helper Methods
    # ==============================

    def extract_id(self, combo_value):
        """Extract the integer ID from a ComboBox display string like '1 - Alhaji Mawiya Sow'."""
        if not combo_value:
            return None
        try:
            return int(combo_value.split(" - ")[0])
        except (IndexError, ValueError):
            return None

    # ==============================
    # Data Loading Methods
    # ==============================

    def load_patients(self):
        """Load all patients from the Patients table into the Patient ComboBox."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = "SELECT PatientID, FullName FROM Patients ORDER BY PatientID"
            cursor.execute(query)
            rows = cursor.fetchall()

            patient_list = []
            for row in rows:
                patient_list.append(f"{row[0]} - {row[1]}")

            self.patient_combo.configure(values=patient_list)
            if patient_list:
                self.patient_combo.set(patient_list[0])
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load patients:\n{e}")

    def load_payments(self):
        """Fetch all payment records from the database and populate the Treeview."""
        # Clear existing items in the treeview
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT 
                    p.PaymentID,
                    pat.FullName AS PatientName,
                    p.Amount,
                    p.PaymentDate,
                    p.PaymentMethod
                FROM Payments p
                LEFT JOIN Patients pat ON p.PatientID = pat.PatientID
                ORDER BY p.PaymentID DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            payment_count = 0
            total_amount = 0.0

            for row in rows:
                payment_count += 1
                total_amount += float(row[2])
                cleaned_row = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned_row)

            # Update count and total labels
            self.count_label.configure(text=f"Total Payments: {payment_count}")
            self.total_label.configure(text=f"Total Amount: Le {total_amount:,.2f}")

            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load payments:\n{e}")

    # ==============================
    # CRUD Operations
    # ==============================

    def add_payment(self):
        """Validate all fields and save a new payment record to MySQL."""
        patient_val = self.patient_combo.get()
        amount_str = self.amount_entry.get().strip()
        payment_date = self.date_entry.get().strip()
        payment_method = self.payment_method_combo.get()

        # Extract patient ID from ComboBox display string
        patient_id = self.extract_id(patient_val)

        # Validate all required fields are filled
        if not patient_id:
            messagebox.showerror("Validation Error", "Please select a valid patient.")
            return
        if not amount_str:
            messagebox.showerror("Validation Error", "Please enter the amount paid.")
            return
        if not payment_method:
            messagebox.showerror("Validation Error", "Please select a payment method.")
            return

        # Validate amount is numeric and greater than zero
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Validation Error", "Amount must be greater than zero.")
                return
            # Convert to integer if it's a whole number
            if amount == int(amount):
                amount = int(amount)
        except ValueError:
            messagebox.showerror("Validation Error", "Amount must be a valid number.")
            return

        # Auto-fill date if not provided
        if not payment_date:
            payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.date_entry.delete(0, "end")
            self.date_entry.insert(0, payment_date)
        else:
            # Validate date format (YYYY-MM-DD HH:MM:SS)
            try:
                datetime.strptime(payment_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror(
                    "Validation Error",
                    "Invalid date format. Please use YYYY-MM-DD HH:MM:SS."
                )
                return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                INSERT INTO Payments (PatientID, Amount, PaymentDate, PaymentMethod)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (patient_id, amount, payment_date, payment_method))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Payment added successfully!")
            self.load_payments()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add payment:\n{e}")

    def update_payment(self):
        """Update the selected payment record in the database."""
        if not self.selected_payment_id:
            messagebox.showwarning(
                "Selection Warning",
                "Please select a payment from the table to update."
            )
            return

        patient_val = self.patient_combo.get()
        amount_str = self.amount_entry.get().strip()
        payment_date = self.date_entry.get().strip()
        payment_method = self.payment_method_combo.get()

        patient_id = self.extract_id(patient_val)

        # Validate all required fields
        if not patient_id:
            messagebox.showerror("Validation Error", "Please select a valid patient.")
            return
        if not amount_str:
            messagebox.showerror("Validation Error", "Please enter the amount paid.")
            return
        if not payment_method:
            messagebox.showerror("Validation Error", "Please select a payment method.")
            return

        # Validate amount is numeric and greater than zero
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Validation Error", "Amount must be greater than zero.")
                return
            if amount == int(amount):
                amount = int(amount)
        except ValueError:
            messagebox.showerror("Validation Error", "Amount must be a valid number.")
            return

        # Validate date format
        if payment_date:
            try:
                datetime.strptime(payment_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror(
                    "Validation Error",
                    "Invalid date format. Please use YYYY-MM-DD HH:MM:SS."
                )
                return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                UPDATE Payments
                SET PatientID = %s, Amount = %s, PaymentDate = %s, PaymentMethod = %s
                WHERE PaymentID = %s
            """
            cursor.execute(query, (
                patient_id, amount, payment_date, payment_method,
                self.selected_payment_id
            ))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Payment updated successfully!")
            self.load_payments()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update payment:\n{e}")

    def delete_payment(self):
        """Delete the selected payment record after user confirmation."""
        if not self.selected_payment_id:
            messagebox.showwarning(
                "Selection Warning",
                "Please select a payment from the table to delete."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this payment?"
        )
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = "DELETE FROM Payments WHERE PaymentID = %s"
            cursor.execute(query, (self.selected_payment_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Payment deleted successfully!")
            self.load_payments()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete payment:\n{e}")

    def search_payment(self):
        """Search for payments by Patient Name, Payment Method, or Payment Date."""
        search_query = self.search_entry.get().strip()

        if not search_query:
            messagebox.showwarning("Search Warning", "Please enter a search term.")
            return

        # Clear existing items in the treeview
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT 
                    p.PaymentID,
                    pat.FullName AS PatientName,
                    p.Amount,
                    p.PaymentDate,
                    p.PaymentMethod
                FROM Payments p
                LEFT JOIN Patients pat ON p.PatientID = pat.PatientID
                WHERE pat.FullName LIKE %s
                   OR p.PaymentMethod LIKE %s
                   OR p.PaymentDate LIKE %s
                ORDER BY p.PaymentID DESC
            """
            like_val = f"%{search_query}%"
            cursor.execute(query, (like_val, like_val, like_val))
            rows = cursor.fetchall()

            payment_count = 0
            total_amount = 0.0

            for row in rows:
                payment_count += 1
                total_amount += float(row[2])
                cleaned_row = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned_row)

            # Update count and total labels
            self.count_label.configure(text=f"Found Payments: {payment_count}")
            self.total_label.configure(text=f"Total Amount: Le {total_amount:,.2f}")

            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to search payments:\n{e}")

    def select_payment(self, event):
        """Load the selected payment from the Treeview into the form fields."""
        selected_item = self.table.selection()
        if not selected_item:
            return

        row_values = self.table.item(selected_item[0], "values")
        self.selected_payment_id = row_values[0]

        # Set the Patient ComboBox to match the selected row
        patient_name = row_values[1]
        patient_values = self.patient_combo.cget("values")
        for val in patient_values:
            if patient_name in val:
                self.patient_combo.set(val)
                break

        # Set the Amount Paid
        self.amount_entry.delete(0, "end")
        self.amount_entry.insert(0, row_values[2])

        # Set the Payment Date
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, row_values[3])

        # Set the Payment Method
        self.payment_method_combo.set(row_values[4])

    def clear_fields(self):
        """Clear all form fields and reset the ComboBoxes and Treeview selection."""
        self.selected_payment_id = None

        # Clear the Amount Paid field
        self.amount_entry.delete(0, "end")

        # Clear the Payment Date field
        self.date_entry.delete(0, "end")

        # Clear the search entry
        self.search_entry.delete(0, "end")

        # Remove Treeview selection highlight
        self.table.selection_remove(self.table.selection())

        # Reset the Patient ComboBox to the first value
        patient_values = self.patient_combo.cget("values")
        if patient_values:
            self.patient_combo.set(patient_values[0])

        # Reset the Payment Method ComboBox to the first value
        payment_method_values = self.payment_method_combo.cget("values")
        if payment_method_values:
            self.payment_method_combo.set(payment_method_values[0])

    def refresh_table(self):
        """Reload all payment records from the database into the Treeview.
        Also resets the Patient ComboBox."""
        self.load_patients()
        self.load_payments()

    def generate_receipt(self):
        """Generate a receipt for the selected payment.
        This will open the Receipt module (to be implemented separately)."""
        if not self.selected_payment_id:
            messagebox.showwarning(
                "Selection Warning",
                "Please select a payment from the table to generate a receipt."
            )
            return

        # Placeholder for Receipt module integration
        messagebox.showinfo(
            "Receipt Generation",
            f"Receipt generation for Payment ID: {self.selected_payment_id}\n\n"
            "This feature will be implemented in the Receipt module."
        )


if __name__ == "__main__":
    class TestApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.geometry("1500x850")
            PaymentWindow(self)

    app = TestApp()
    app.mainloop()
