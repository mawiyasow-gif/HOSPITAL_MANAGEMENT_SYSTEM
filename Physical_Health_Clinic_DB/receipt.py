import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from database import connect_db
import os

# Try to import reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# -----------------------------
# CustomTkinter Settings
# -----------------------------
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class ReceiptWindow(ctk.CTkToplevel):
    """Receipt Management Window for the Physical Health Clinic Record System."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("🧾 Receipt Management")
        self.geometry("1500x850")
        self.resizable(True, True)

        # Track selected receipt ID
        self.selected_receipt_id = None

        # Store payment details for selected payment
        self.selected_payment_data = None

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
            text="🧾 Receipt Management",
            font=("Arial", 30, "bold")
        )
        title.pack(pady=20)

        # ==============================
        # Main Frame
        # ==============================

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ==============================
        # Left Panel (Receipt Form)
        # ==============================

        form_frame = ctk.CTkFrame(main_frame, width=420)
        form_frame.pack(side="left", fill="y", padx=15, pady=15)

        ctk.CTkLabel(
            form_frame,
            text="Receipt Information",
            font=("Arial", 22, "bold")
        ).pack(pady=20)

        # Payment ComboBox
        ctk.CTkLabel(
            form_frame,
            text="Select Payment:",
            font=("Arial", 14)
        ).pack(pady=(10, 2), anchor="w", padx=50)

        self.payment_combo = ctk.CTkComboBox(form_frame, width=320, values=[])
        self.payment_combo.pack(pady=5)
        self.payment_combo.bind("<<ComboboxSelected>>", self.on_payment_selected)

        # Receipt Number Entry (read-only)
        ctk.CTkLabel(
            form_frame,
            text="Receipt Number:",
            font=("Arial", 14)
        ).pack(pady=(10, 2), anchor="w", padx=50)

        self.receipt_number_entry = ctk.CTkEntry(
            form_frame,
            width=320,
            placeholder_text="Auto-generated after saving"
        )
        self.receipt_number_entry.pack(pady=5)
        self.receipt_number_entry.configure(state="disabled")

        # Issue Date Entry
        ctk.CTkLabel(
            form_frame,
            text="Issue Date (YYYY-MM-DD):",
            font=("Arial", 14)
        ).pack(pady=(10, 2), anchor="w", padx=50)

        self.issue_date_entry = ctk.CTkEntry(
            form_frame,
            width=320,
            placeholder_text="Auto-filled with today's date"
        )
        self.issue_date_entry.pack(pady=5)

        # Total Amount Entry (read-only)
        ctk.CTkLabel(
            form_frame,
            text="Total Amount:",
            font=("Arial", 14)
        ).pack(pady=(10, 2), anchor="w", padx=50)

        self.total_amount_entry = ctk.CTkEntry(
            form_frame,
            width=320,
            placeholder_text="Auto-filled from payment"
        )
        self.total_amount_entry.pack(pady=5)
        self.total_amount_entry.configure(state="disabled")

        # ==============================
        # Action Buttons
        # ==============================

        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=25)

        ctk.CTkButton(
            button_frame,
            text="➕ Generate Receipt",
            width=140,
            command=self.generate_receipt
        ).grid(row=0, column=0, padx=5, pady=5)

        ctk.CTkButton(
            button_frame,
            text="✏️ Update",
            width=140,
            command=self.update_receipt
        ).grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkButton(
            button_frame,
            text="❌ Delete",
            width=140,
            command=self.delete_receipt
        ).grid(row=1, column=0, padx=5, pady=5)

        ctk.CTkButton(
            button_frame,
            text="🧹 Clear",
            width=140,
            command=self.clear_fields
        ).grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkButton(
            button_frame,
            text="🖨️ Print Receipt",
            width=140,
            command=self.print_receipt
        ).grid(row=2, column=0, padx=5, pady=5)

        ctk.CTkButton(
            button_frame,
            text="💾 Export PDF",
            width=140,
            command=self.export_pdf
        ).grid(row=2, column=1, padx=5, pady=5)

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
            placeholder_text="Receipt ID, Patient Name, Payment ID, or Date"
        )
        self.search_entry.pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="Search",
            width=100,
            command=self.search_receipt
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="🔄 Refresh",
            width=100,
            command=self.refresh_table
        ).pack(side="left", padx=5)

        # Receipt count label
        self.count_label = ctk.CTkLabel(
            search_frame,
            text="Total Receipts: 0",
            font=("Arial", 14, "bold"),
            text_color="#1F6AA5"
        )
        self.count_label.pack(side="right", padx=20)

        # Total revenue label
        self.revenue_label = ctk.CTkLabel(
            search_frame,
            text="Total Revenue: Le 0",
            font=("Arial", 14, "bold"),
            text_color="#1F6AA5"
        )
        self.revenue_label.pack(side="right", padx=20)

        # Treeview columns
        columns = (
            "Receipt ID",
            "Payment ID",
            "Patient Name",
            "Issue Date",
            "Total Amount"
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

        # Make Patient Name column wider
        self.table.column("Patient Name", width=200, anchor="center")

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
        self.table.bind("<<TreeviewSelect>>", self.select_receipt)

        # Load initial data into ComboBoxes and Treeview
        self.load_payments()
        self.load_receipts()

    # ==============================
    # Helper Methods
    # ==============================

    def extract_payment_id(self, combo_value):
        """Extract the integer Payment ID from a ComboBox display string like 'Payment #1 - Alhaji Mawiya Sow - Le 1,000'."""
        if not combo_value:
            return None
        try:
            # Extract the number after "Payment #"
            return int(combo_value.split("Payment #")[1].split(" - ")[0])
        except (IndexError, ValueError):
            return None

    def on_payment_selected(self, event):
        """Handle payment selection from ComboBox."""
        payment_val = self.payment_combo.get()
        payment_id = self.extract_payment_id(payment_val)

        if payment_id:
            # Load payment details
            try:
                conn = connect_db()
                cursor = conn.cursor()
                query = """
                    SELECT 
                        p.PaymentID,
                        pat.FullName,
                        p.Amount,
                        p.PaymentDate,
                        p.PaymentMethod
                    FROM Payments p
                    LEFT JOIN Patients pat ON p.PatientID = pat.PatientID
                    WHERE p.PaymentID = %s
                """
                cursor.execute(query, (payment_id,))
                row = cursor.fetchone()
                conn.close()

                if row:
                    self.selected_payment_data = {
                        'PaymentID': row[0],
                        'PatientName': row[1],
                        'Amount': row[2],
                        'PaymentDate': row[3],
                        'PaymentMethod': row[4]
                    }

                    # Auto-fill total amount
                    self.total_amount_entry.configure(state="normal")
                    self.total_amount_entry.delete(0, "end")
                    self.total_amount_entry.insert(0, str(row[2]))
                    self.total_amount_entry.configure(state="disabled")

                    # Auto-fill today's date if empty
                    if not self.issue_date_entry.get():
                        today = datetime.now().strftime("%Y-%m-%d")
                        self.issue_date_entry.delete(0, "end")
                        self.issue_date_entry.insert(0, today)

            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to load payment details:\n{e}")

    # ==============================
    # Data Loading Methods
    # ==============================

    def load_payments(self):
        """Load all payment records from the Payments table into the Payment ComboBox."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT 
                    p.PaymentID,
                    pat.FullName,
                    p.Amount
                FROM Payments p
                LEFT JOIN Patients pat ON p.PatientID = pat.PatientID
                ORDER BY p.PaymentID DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            payment_list = []
            for row in rows:
                payment_list.append(f"Payment #{row[0]} - {row[1]} - Le {row[2]:,.2f}")

            self.payment_combo.configure(values=payment_list)
            if payment_list:
                self.payment_combo.set(payment_list[0])
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load payments:\n{e}")

    def load_receipts(self):
        """Fetch all receipt records from the database and populate the Treeview."""
        # Clear existing items in the treeview
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT 
                    r.ReceiptID,
                    r.PaymentID,
                    pat.FullName AS PatientName,
                    r.IssueDate,
                    r.TotalAmount
                FROM Receipts r
                LEFT JOIN Payments p ON r.PaymentID = p.PaymentID
                LEFT JOIN Patients pat ON p.PatientID = pat.PatientID
                ORDER BY r.ReceiptID DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            receipt_count = 0
            total_revenue = 0.0

            for row in rows:
                receipt_count += 1
                total_revenue += float(row[4])
                cleaned_row = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned_row)

            # Update count and revenue labels
            self.count_label.configure(text=f"Total Receipts: {receipt_count}")
            self.revenue_label.configure(text=f"Total Revenue: Le {total_revenue:,.2f}")

            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load receipts:\n{e}")

    # ==============================
    # CRUD Operations
    # ==============================

    def generate_receipt(self):
        """Generate a new receipt from the selected payment."""
        payment_val = self.payment_combo.get()
        payment_id = self.extract_payment_id(payment_val)
        issue_date = self.issue_date_entry.get().strip()

        # Validate payment selection
        if not payment_id:
            messagebox.showerror("Validation Error", "Please select a valid payment.")
            return

        # Validate issue date
        if not issue_date:
            messagebox.showerror("Validation Error", "Please enter the issue date.")
            return

        # Validate date format (YYYY-MM-DD)
        try:
            datetime.strptime(issue_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "Validation Error",
                "Invalid date format. Please use YYYY-MM-DD."
            )
            return

        # Check if receipt already exists for this payment
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT ReceiptID FROM Receipts WHERE PaymentID = %s", (payment_id,))
            existing = cursor.fetchone()
            conn.close()

            if existing:
                confirm = messagebox.askyesno(
                    "Duplicate Receipt",
                    f"A receipt already exists for Payment #{payment_id}.\n\n"
                    "Do you want to generate a new receipt anyway?"
                )
                if not confirm:
                    return
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to check for existing receipts:\n{e}")
            return

        # Get payment details
        if not self.selected_payment_data:
            self.on_payment_selected(None)

        if not self.selected_payment_data:
            messagebox.showerror("Error", "Could not retrieve payment details.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                INSERT INTO Receipts (PaymentID, IssueDate, TotalAmount)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (
                payment_id,
                issue_date,
                self.selected_payment_data['Amount']
            ))
            conn.commit()
            receipt_id = cursor.lastrowid
            conn.close()

            # Display receipt number
            self.receipt_number_entry.configure(state="normal")
            self.receipt_number_entry.delete(0, "end")
            self.receipt_number_entry.insert(0, f"RCP-{receipt_id:06d}")
            self.receipt_number_entry.configure(state="disabled")

            messagebox.showinfo("Success", f"Receipt generated successfully!\nReceipt ID: {receipt_id}")
            self.load_receipts()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to generate receipt:\n{e}")

    def update_receipt(self):
        """Update the selected receipt record in the database."""
        if not self.selected_receipt_id:
            messagebox.showwarning(
                "Selection Warning",
                "Please select a receipt from the table to update."
            )
            return

        payment_val = self.payment_combo.get()
        payment_id = self.extract_payment_id(payment_val)
        issue_date = self.issue_date_entry.get().strip()

        # Validate payment selection
        if not payment_id:
            messagebox.showerror("Validation Error", "Please select a valid payment.")
            return

        # Validate issue date
        if not issue_date:
            messagebox.showerror("Validation Error", "Please enter the issue date.")
            return

        # Validate date format
        try:
            datetime.strptime(issue_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "Validation Error",
                "Invalid date format. Please use YYYY-MM-DD."
            )
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                UPDATE Receipts
                SET PaymentID = %s, IssueDate = %s, TotalAmount = %s
                WHERE ReceiptID = %s
            """
            cursor.execute(query, (
                payment_id,
                issue_date,
                self.selected_payment_data['Amount'] if self.selected_payment_data else 0,
                self.selected_receipt_id
            ))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Receipt updated successfully!")
            self.load_receipts()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update receipt:\n{e}")

    def delete_receipt(self):
        """Delete the selected receipt record after user confirmation."""
        if not self.selected_receipt_id:
            messagebox.showwarning(
                "Selection Warning",
                "Please select a receipt from the table to delete."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this receipt?"
        )
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = "DELETE FROM Receipts WHERE ReceiptID = %s"
            cursor.execute(query, (self.selected_receipt_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Receipt deleted successfully!")
            self.load_receipts()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete receipt:\n{e}")

    def search_receipt(self):
        """Search for receipts by Receipt ID, Patient Name, Payment ID, or Issue Date."""
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
                    r.ReceiptID,
                    r.PaymentID,
                    pat.FullName AS PatientName,
                    r.IssueDate,
                    r.TotalAmount
                FROM Receipts r
                LEFT JOIN Payments p ON r.PaymentID = p.PaymentID
                LEFT JOIN Patients pat ON p.PatientID = pat.PatientID
                WHERE r.ReceiptID LIKE %s
                   OR r.PaymentID LIKE %s
                   OR pat.FullName LIKE %s
                   OR r.IssueDate LIKE %s
                ORDER BY r.ReceiptID DESC
            """
            like_val = f"%{search_query}%"
            cursor.execute(query, (like_val, like_val, like_val, like_val))
            rows = cursor.fetchall()

            receipt_count = 0
            total_revenue = 0.0

            for row in rows:
                receipt_count += 1
                total_revenue += float(row[4])
                cleaned_row = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned_row)

            # Update count and revenue labels
            self.count_label.configure(text=f"Found Receipts: {receipt_count}")
            self.revenue_label.configure(text=f"Total Amount: Le {total_revenue:,.2f}")

            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to search receipts:\n{e}")

    def select_receipt(self, event):
        """Load the selected receipt from the Treeview into the form fields."""
        selected_item = self.table.selection()
        if not selected_item:
            return

        row_values = self.table.item(selected_item[0], "values")
        self.selected_receipt_id = row_values[0]

        # Set the Payment ComboBox to match the selected row
        payment_id = row_values[1]
        payment_values = self.payment_combo.cget("values")
        for val in payment_values:
            if f"Payment #{payment_id}" in val:
                self.payment_combo.set(val)
                break

        # Load payment details
        self.on_payment_selected(None)

        # Set the Receipt Number
        self.receipt_number_entry.configure(state="normal")
        self.receipt_number_entry.delete(0, "end")
        self.receipt_number_entry.insert(0, f"RCP-{row_values[0]}")
        self.receipt_number_entry.configure(state="disabled")

        # Set the Issue Date
        self.issue_date_entry.delete(0, "end")
        self.issue_date_entry.insert(0, row_values[3])

    def clear_fields(self):
        """Clear all form fields and reset the ComboBoxes and Treeview selection."""
        self.selected_receipt_id = None
        self.selected_payment_data = None

        # Clear the Issue Date field
        self.issue_date_entry.delete(0, "end")

        # Clear the search entry
        self.search_entry.delete(0, "end")

        # Clear the Receipt Number
        self.receipt_number_entry.configure(state="normal")
        self.receipt_number_entry.delete(0, "end")
        self.receipt_number_entry.configure(state="disabled")

        # Clear the Total Amount
        self.total_amount_entry.configure(state="normal")
        self.total_amount_entry.delete(0, "end")
        self.total_amount_entry.configure(state="disabled")

        # Remove Treeview selection highlight
        self.table.selection_remove(self.table.selection())

        # Reset the Payment ComboBox to the first value
        payment_values = self.payment_combo.cget("values")
        if payment_values:
            self.payment_combo.set(payment_values[0])

    def refresh_table(self):
        """Reload all receipt records from the database into the Treeview.
        Also resets the Payment ComboBox."""
        self.load_payments()
        self.load_receipts()

    # ==============================
    # Print and Export Functions
    # ==============================

    def print_receipt(self):
        """Generate and print a professional receipt for the selected payment."""
        if not self.selected_payment_data:
            messagebox.showwarning(
                "Selection Warning",
                "Please select a payment to generate a receipt."
            )
            return

        # Create receipt text
        receipt_text = self._generate_receipt_text()

        # Show receipt in a message box for preview
        messagebox.showinfo(
            "Receipt Preview",
            receipt_text
        )

        # Note: Actual printing would require additional libraries like win32print on Windows
        # or lpr on Linux. For cross-platform compatibility, we show the preview.
        messagebox.showinfo(
            "Print Information",
            "To print this receipt:\n"
            "1. Take a screenshot of the receipt preview\n"
            "2. Or use the Export PDF option for a printable format"
        )

    def _generate_receipt_text(self):
        """Generate the receipt text content."""
        if not self.selected_payment_data:
            return ""

        data = self.selected_payment_data
        receipt_id = self.receipt_number_entry.get() or "Pending"
        issue_date = self.issue_date_entry.get() or datetime.now().strftime("%Y-%m-%d")

        receipt = (
            "╔" + "═" * 48 + "╗\n"
            "║" + " " * 48 + "║\n"
            "║" + " " * 10 + "PHYSICAL HEALTH CLINIC" + " " * 14 + "║\n"
            "║" + " " * 48 + "║\n"
            "║" + " " * 6 + "🏥 Your Trusted Healthcare Partner" + " " * 12 + "║\n"
            "║" + " " * 48 + "║\n"
            "╚" + "═" * 48 + "╝\n\n"
            "📍 Address: 123 Hospital Road, Freetown, Sierra Leone\n"
            "📞 Phone: +232 76 123 456\n"
            "📧 Email: info@physicalhealthclinic.sl\n"
            "🌐 Website: www.physicalhealthclinic.sl\n\n"
            "─" * 50 + "\n"
            f"RECEIPT NO: {receipt_id}\n"
            "─" * 50 + "\n\n"
            f"Patient Name: {data['PatientName']}\n"
            f"Payment ID: #{data['PaymentID']}\n"
            f"Issue Date: {issue_date}\n"
            f"Payment Method: {data['PaymentMethod']}\n\n"
            "─" * 50 + "\n"
            f"AMOUNT PAID: Le {data['Amount']:,.2f}\n"
            "─" * 50 + "\n\n"
            "✅ STATUS: PAID\n\n"
            "─" * 50 + "\n"
            "Thank You For Choosing Our Clinic!\n"
            "We appreciate your trust in our healthcare services.\n"
            "─" * 50 + "\n"
            "This receipt is valid for all medical and tax purposes.\n"
            "─" * 50
        )
        return receipt

    def export_pdf(self):
        """Export the receipt as a PDF file."""
        if not PDF_AVAILABLE:
            messagebox.showerror(
                "PDF Library Not Available",
                "The ReportLab library is required for PDF export.\n"
                "Install it using: pip install reportlab"
            )
            return

        if not self.selected_payment_data:
            messagebox.showwarning(
                "Selection Warning",
                "Please select a payment to export as PDF."
            )
            return

        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save Receipt"
        )

        if not file_path:
            return

        try:
            self._create_pdf_receipt(file_path)
            messagebox.showinfo("Success", f"Receipt exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("PDF Error", f"Failed to export PDF:\n{e}")

    def _create_pdf_receipt(self, file_path):
        """Create a professional PDF receipt using ReportLab."""
        if not self.selected_payment_data:
            return

        data = self.selected_payment_data
        receipt_id = self.receipt_number_entry.get() or "Pending"
        issue_date = self.issue_date_entry.get() or datetime.now().strftime("%Y-%m-%d")

        # Create PDF document
        doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=72, bottomMargin=72)
        styles = getSampleStyleSheet()
        story = []

        # Clinic Header
        header_style = styles["Heading1"]
        header_style.alignment = TA_CENTER
        header = Paragraph("PHYSICAL HEALTH CLINIC", header_style)
        story.append(header)
        story.append(Spacer(1, 6))

        # Tagline
        tagline_style = styles["Normal"]
        tagline_style.alignment = TA_CENTER
        tagline = Paragraph("<i>Your Trusted Healthcare Partner</i>", tagline_style)
        story.append(tagline)
        story.append(Spacer(1, 12))

        # Contact Information
        contact_style = styles["Normal"]
        contact_style.alignment = TA_CENTER
        contact_style.fontSize = 10
        contact = Paragraph(
            "📍 123 Hospital Road, Freetown, Sierra Leone<br/>"
            "📞 +232 76 123 456<br/>"
            "📧 info@physicalhealthclinic.sl<br/>"
            "🌐 www.physicalhealthclinic.sl",
            contact_style
        )
        story.append(contact)
        story.append(Spacer(1, 24))

        # Divider line
        story.append(Spacer(1, 6))

        # Receipt Number
        receipt_style = styles["Heading2"]
        receipt_style.alignment = TA_CENTER
        receipt_para = Paragraph(f"RECEIPT NO: {receipt_id}", receipt_style)
        story.append(receipt_para)
        story.append(Spacer(1, 12))

        # Receipt details table
        receipt_data = [
            ["Patient Name:", data['PatientName']],
            ["Payment ID:", f"#{data['PaymentID']}"],
            ["Issue Date:", issue_date],
            ["Payment Method:", data['PaymentMethod']],
            ["", ""],
            ["Amount Paid:", f"<b>Le {data['Amount']:,.2f}</b>"],
        ]

        table = Table(receipt_data, colWidths=[150, 200])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (1, 5), (1, 5), 'Helvetica-Bold'),
        ]))
        story.append(table)
        story.append(Spacer(1, 24))

        # Status
        status_style = styles["Heading2"]
        status_style.alignment = TA_CENTER
        status_style.textColor = colors.green
        status = Paragraph("✅ STATUS: PAID", status_style)
        story.append(status)
        story.append(Spacer(1, 24))

        # Thank you message
        thank_style = styles["Normal"]
        thank_style.alignment = TA_CENTER
        thank = Paragraph(
            "<b>Thank You For Choosing Our Clinic!</b><br/>"
            "<i>We appreciate your trust in our healthcare services.</i>",
            thank_style
        )
        story.append(thank)
        story.append(Spacer(1, 12))

        # Validity notice
        valid_style = styles["Normal"]
        valid_style.alignment = TA_CENTER
        valid_style.fontSize = 9
        valid_style.textColor = colors.grey
        valid = Paragraph(
            "This receipt is valid for all medical and tax purposes.",
            valid_style
        )
        story.append(valid)

        # Build PDF
        doc.build(story)


if __name__ == "__main__":
    class TestApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.geometry("1500x850")
            ReceiptWindow(self)

    app = TestApp()
    app.mainloop()
