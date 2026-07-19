import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from database import connect_db
import session
import os

# Try to import reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class ReceiptWindow(ctk.CTkToplevel):
    """Receipt Management & Professional PDF Generation Window."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("🧾 Receipt & Billing Management")
        self.geometry("1500x850")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.selected_receipt_id = None
        self.selected_payment_data = None

        # Check current user worker id
        self.worker_id = 1
        if hasattr(session, "current_user") and session.current_user:
            self.worker_id = session.current_user.get("worker_id", 1)

        # Back Button
        back_btn = ctk.CTkButton(
            self,
            text="⬅ Back",
            width=100,
            command=self.destroy
        )
        back_btn.place(x=20, y=20)

        # Window Title
        title = ctk.CTkLabel(
            self,
            text="🧾 Receipt & Billing Management",
            font=("Arial", 30, "bold")
        )
        title.pack(pady=20)

        # Main Frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Left Panel (Form)
        form_frame = ctk.CTkFrame(main_frame, width=420)
        form_frame.pack(side="left", fill="y", padx=15, pady=15)

        ctk.CTkLabel(
            form_frame,
            text="Receipt Operations",
            font=("Arial", 22, "bold")
        ).pack(pady=20)

        # Payment ComboBox
        ctk.CTkLabel(form_frame, text="Select Completed Payment:", font=("Arial", 13, "bold")).pack(pady=(10, 2), anchor="w", padx=50)
        self.payment_combo = ctk.CTkComboBox(form_frame, width=320, values=[])
        self.payment_combo.pack(pady=5)
        self.payment_combo.bind("<<ComboboxSelected>>", self.on_payment_selected)

        # Receipt Number Entry
        ctk.CTkLabel(form_frame, text="Receipt Number (Auto-assigned):", font=("Arial", 13, "bold")).pack(pady=(10, 2), anchor="w", padx=50)
        self.receipt_number_entry = ctk.CTkEntry(form_frame, width=320, placeholder_text="RCP-XXXXXX")
        self.receipt_number_entry.pack(pady=5)
        self.receipt_number_entry.configure(state="disabled")

        # Issue Date Entry
        ctk.CTkLabel(form_frame, text="Issue Date:", font=("Arial", 13, "bold")).pack(pady=(10, 2), anchor="w", padx=50)
        self.issue_date_entry = ctk.CTkEntry(form_frame, width=320, placeholder_text="YYYY-MM-DD")
        self.issue_date_entry.pack(pady=5)

        # Total Amount Entry
        ctk.CTkLabel(form_frame, text="Total Amount (Le):", font=("Arial", 13, "bold")).pack(pady=(10, 2), anchor="w", padx=50)
        self.total_amount_entry = ctk.CTkEntry(form_frame, width=320)
        self.total_amount_entry.pack(pady=5)
        self.total_amount_entry.configure(state="disabled")

        # Action Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(pady=25)

        ctk.CTkButton(btn_frame, text="➕ Generate Receipt", command=self.generate_receipt, width=155).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="👁 Preview Text", command=self.print_receipt, width=155).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="📄 Export PDF Receipt", command=self.export_pdf, fg_color="#4CAF50", hover_color="#43A047", width=155).grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="❌ Delete Receipt", command=self.delete_receipt, fg_color="red", hover_color="#b71c1c", width=155).grid(row=1, column=1, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="🧹 Clear Fields", command=self.clear_fields, width=320).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Right Panel (List)
        self.table_frame = ctk.CTkFrame(main_frame)
        self.table_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        # Search Bar
        search_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=15, pady=10)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by Patient Name or Receipt ID...", width=300)
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.search_receipt)

        ctk.CTkButton(search_frame, text="Search", command=self.search_receipt, width=100).pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="Reset", command=self.refresh_table, width=100).pack(side="left")

        # Summary count/revenue labels
        self.summary_frame = ctk.CTkFrame(self.table_frame, height=40, fg_color="transparent")
        self.summary_frame.pack(fill="x", padx=15)
        self.count_label = ctk.CTkLabel(self.summary_frame, text="Total Receipts: 0", font=("Arial", 12, "bold"))
        self.count_label.pack(side="left", padx=10)
        self.revenue_label = ctk.CTkLabel(self.summary_frame, text="Total Revenue: Le 0.00", font=("Arial", 12, "bold"), text_color="#1F6AA5")
        self.revenue_label.pack(side="right", padx=10)

        # Treeview setup
        container = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=15, pady=10)

        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side="right", fill="y")

        columns = ("Receipt ID", "Payment ID", "Patient Name", "Total Amount", "Issue Date", "Issued By Staff")
        self.table = ttk.Treeview(
            container,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=15
        )
        for col in columns:
            self.table.heading(col, text=col, anchor="w")
            self.table.column(col, anchor="w", width=140)

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.table.yview)

        # Binds
        self.table.bind("<<TreeviewSelect>>", self.select_receipt)

        # Load
        self.load_payments()
        self.load_receipts()

    def load_selected_receipt_details(self, receipt_id):
        """Pre-load a specific receipt details directly and trigger preview."""
        try:
            self.selected_receipt_id = receipt_id
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.ReceiptID, r.PaymentID, p.Amount, r.IssueDate, p.PaymentMethod, pat.FullName
                FROM Receipt r
                JOIN Payment p ON r.PaymentID = p.PaymentID
                JOIN Patients pat ON p.PatientID = pat.PatientID
                WHERE r.ReceiptID = %s
            """, (receipt_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                self.selected_payment_data = {
                    'PaymentID': row[1],
                    'Amount': row[2],
                    'PaymentDate': row[3],
                    'PaymentMethod': row[4],
                    'PatientName': row[5]
                }
                self.receipt_number_entry.configure(state="normal")
                self.receipt_number_entry.delete(0, "end")
                self.receipt_number_entry.insert(0, f"RCP-{row[0]:06d}")
                self.receipt_number_entry.configure(state="disabled")
                
                self.total_amount_entry.configure(state="normal")
                self.total_amount_entry.delete(0, "end")
                self.total_amount_entry.insert(0, f"Le {row[2]:,.2f}")
                self.total_amount_entry.configure(state="disabled")

                self.issue_date_entry.delete(0, "end")
                self.issue_date_entry.insert(0, str(row[3]))

                # Automatically trigger preview box
                self.print_receipt()
        except Exception as e:
            print(f"Error loading direct receipt: {e}")

    def load_payments(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.PaymentID, pat.FullName, p.Amount
                FROM Payment p
                LEFT JOIN Patients pat ON p.PatientID = pat.PatientID
                WHERE p.PaymentMethod <> 'Pending'
                ORDER BY p.PaymentID DESC
            """)
            payment_list = [f"Payment #{row[0]} - {row[1]} - Le {row[2]:,.2f}" for row in cursor.fetchall()]
            self.payment_combo.configure(values=payment_list)
            if payment_list:
                self.payment_combo.set(payment_list[0])
            conn.close()
        except Exception as e:
            print(f"Error loading payments: {e}")

    def on_payment_selected(self, event):
        val = self.payment_combo.get()
        if not val:
            return
        try:
            payment_id = int(val.split("Payment #")[1].split(" - ")[0])
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.PaymentID, pat.FullName, p.Amount, p.PaymentDate, p.PaymentMethod
                FROM Payment p
                LEFT JOIN Patients pat ON p.PatientID = pat.PatientID
                WHERE p.PaymentID = %s
            """, (payment_id,))
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
                self.total_amount_entry.configure(state="normal")
                self.total_amount_entry.delete(0, "end")
                self.total_amount_entry.insert(0, str(row[2]))
                self.total_amount_entry.configure(state="disabled")

                self.issue_date_entry.delete(0, "end")
                self.issue_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        except Exception as e:
            print(f"Error handling payment selection: {e}")

    def load_receipts(self):
        for item in self.table.get_children():
            self.table.delete(item)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.ReceiptID, r.PaymentID, pat.FullName, p.Amount, r.IssueDate, hw.FullName
                FROM Receipt r
                JOIN Payment p ON r.PaymentID = p.PaymentID
                JOIN Patients pat ON p.PatientID = pat.PatientID
                LEFT JOIN Health_Workers hw ON r.PrintedBy = hw.WorkerID
                ORDER BY r.ReceiptID DESC
            """)
            rows = cursor.fetchall()
            conn.close()

            count = 0
            revenue = 0.0
            for row in rows:
                count += 1
                revenue += float(row[3])
                cleaned = ["" if val is None else str(val) for val in row]
                cleaned[3] = f"Le {float(cleaned[3]):,.2f}"
                self.table.insert("", "end", values=cleaned)
                
            self.count_label.configure(text=f"Total Receipts: {count}")
            self.revenue_label.configure(text=f"Total Revenue: Le {revenue:,.2f}")
        except Exception as e:
            print(f"Error loading receipts: {e}")

    def generate_receipt(self):
        val = self.payment_combo.get()
        if not val:
            messagebox.showerror("Error", "Please select a payment.")
            return
        
        try:
            payment_id = int(val.split("Payment #")[1].split(" - ")[0])
            issue_date = self.issue_date_entry.get().strip()
            
            # Check if receipt exists
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT ReceiptID FROM Receipt WHERE PaymentID = %s", (payment_id,))
            exists = cursor.fetchone()
            
            if exists:
                messagebox.showerror("Duplicate Warning", f"A receipt has already been generated for Payment #{payment_id}.")
                conn.close()
                return

            cursor.execute("""
                INSERT INTO Receipt (PaymentID, IssueDate, PrintedBy)
                VALUES (%s, %s, %s)
            """, (payment_id, issue_date, self.worker_id))
            receipt_id = cursor.lastrowid
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Receipt generated successfully!\nReceipt ID: {receipt_id}")
            self.load_receipts()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to generate receipt:\n{e}")

    def select_receipt(self, event):
        selected = self.table.selection()
        if not selected:
            return
        row = self.table.item(selected[0], "values")
        self.selected_receipt_id = row[0]
        payment_id = row[1]

        # Sync combo
        vals = self.payment_combo.cget("values")
        for v in vals:
            if f"Payment #{payment_id}" in v:
                self.payment_combo.set(v)
                self.on_payment_selected(None)
                break

        self.receipt_number_entry.configure(state="normal")
        self.receipt_number_entry.delete(0, "end")
        self.receipt_number_entry.insert(0, f"RCP-{int(row[0]):06d}")
        self.receipt_number_entry.configure(state="disabled")

        self.issue_date_entry.delete(0, "end")
        self.issue_date_entry.insert(0, row[4])

    def clear_fields(self):
        self.selected_receipt_id = None
        self.selected_payment_data = None
        self.receipt_number_entry.configure(state="normal")
        self.receipt_number_entry.delete(0, "end")
        self.receipt_number_entry.configure(state="disabled")
        self.issue_date_entry.delete(0, "end")
        self.total_amount_entry.configure(state="normal")
        self.total_amount_entry.delete(0, "end")
        self.total_amount_entry.configure(state="disabled")
        self.table.selection_remove(self.table.selection())

    def delete_receipt(self):
        if not self.selected_receipt_id:
            messagebox.showwarning("Warning", "Select a receipt to delete.")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this receipt?")
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Receipt WHERE ReceiptID = %s", (self.selected_receipt_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Receipt deleted successfully!")
            self.load_receipts()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete receipt:\n{e}")

    def search_receipt(self, event=None):
        q = self.search_entry.get().strip()
        if not q:
            self.load_receipts()
            return
            
        for item in self.table.get_children():
            self.table.delete(item)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.ReceiptID, r.PaymentID, pat.FullName, p.Amount, r.IssueDate, hw.FullName
                FROM Receipt r
                JOIN Payment p ON r.PaymentID = p.PaymentID
                JOIN Patients pat ON p.PatientID = pat.PatientID
                LEFT JOIN Health_Workers hw ON r.PrintedBy = hw.WorkerID
                WHERE pat.FullName LIKE %s OR r.ReceiptID LIKE %s
                ORDER BY r.ReceiptID DESC
            """, (f"%{q}%", f"%{q}%"))
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                cleaned = ["" if val is None else str(val) for val in row]
                cleaned[3] = f"Le {float(cleaned[3]):,.2f}"
                self.table.insert("", "end", values=cleaned)
        except Exception as e:
            print(f"Error searching receipts: {e}")

    def refresh_table(self):
        self.search_entry.delete(0, "end")
        self.load_payments()
        self.load_receipts()

    def _fetch_receipt_items(self, payment_id):
        """Retrieve dynamic line-item billing items for a given payment ID."""
        items = []
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # Fetch Payment Type and links
            cursor.execute("""
                SELECT PaymentType, LabRequestID, DispensingID, ServiceID, Amount, PrescriptionID 
                FROM Payment 
                WHERE PaymentID = %s
            """, (payment_id,))
            pay_row = cursor.fetchone()
            
            if pay_row:
                ptype, lab_req, disp_id, service_id, amount, prescription_id = pay_row
                
                if ptype == "Medicines":
                    if prescription_id:
                        # Query by TreatmentID (PrescriptionID stores TreatmentID in new flow)
                        cursor.execute("""
                            SELECT pr.MedicineName, pr.QuantityPrescribed, inv.SellingPrice
                            FROM Prescription pr
                            LEFT JOIN Inventory inv ON LOWER(pr.MedicineName) = LOWER(inv.MedicineName)
                            WHERE pr.TreatmentID = %s
                        """, (prescription_id,))
                        for row in cursor.fetchall():
                            name, qty, sell = row
                            price = float(sell) if sell else 0.0
                            items.append({
                                "description": name,
                                "qty": qty,
                                "price": price,
                                "total": qty * price
                            })
                    elif disp_id:
                        # Fallback to old DispensingID structure
                        cursor.execute("""
                            SELECT pr.MedicineName, md.QuantityDispensed, inv.SellingPrice
                            FROM Medicine_Dispensing md
                            JOIN Prescription pr ON md.PrescriptionID = pr.PrescriptionID
                            JOIN Inventory inv ON md.InventoryID = inv.InventoryID
                            WHERE md.DispensingID = %s
                        """, (disp_id,))
                    for row in cursor.fetchall():
                        name, qty, sell = row
                        items.append({
                            "description": name,
                            "qty": qty,
                            "price": float(sell),
                            "total": qty * float(sell)
                        })
                elif ptype == "Laboratory" and lab_req:
                    # Query laboratory tests completed
                    cursor.execute("""
                        SELECT lt.TestName, lt.Price
                        FROM Laboratory_Results res
                        JOIN Laboratory_Tests lt ON res.TestID = lt.TestID
                        WHERE res.RequestID = %s
                    """, (lab_req,))
                    for row in cursor.fetchall():
                        name, price = row
                        items.append({
                            "description": name,
                            "qty": 1,
                            "price": float(price),
                            "total": float(price)
                        })
                elif ptype == "Registration":
                    items.append({
                        "description": "Patient Registration Fee",
                        "qty": 1,
                        "price": float(amount),
                        "total": float(amount)
                    })
                elif ptype == "Consultation":
                    items.append({
                        "description": "Doctor Clinical Consultation",
                        "qty": 1,
                        "price": float(amount),
                        "total": float(amount)
                    })
                elif service_id:
                    cursor.execute("SELECT ServiceName, Price FROM Hospital_Services WHERE ServiceID = %s", (service_id,))
                    svc = cursor.fetchone()
                    if svc:
                        items.append({
                            "description": svc[0],
                            "qty": 1,
                            "price": float(svc[1]),
                            "total": float(svc[1])
                        })
                else:
                    items.append({
                        "description": f"{ptype} Service Charge",
                        "qty": 1,
                        "price": float(amount),
                        "total": float(amount)
                    })
            conn.close()
        except Exception as e:
            print(f"Error fetching receipt items: {e}")
            
        # Fallback if empty
        if not items and self.selected_payment_data:
            items.append({
                "description": "Hospital Service Rendered",
                "qty": 1,
                "price": float(self.selected_payment_data['Amount']),
                "total": float(self.selected_payment_data['Amount'])
            })
        return items

    def _generate_receipt_text(self):
        if not self.selected_payment_data:
            return "No payment selected."
            
        data = self.selected_payment_data
        receipt_num = self.receipt_number_entry.get() or "RCP-PENDING"
        items = self._fetch_receipt_items(data['PaymentID'])
        
        text = (
            "==================================================\n"
            "            PHYSICAL HEALTH CLINIC                \n"
            "       🏥 Your Trusted Healthcare Partner        \n"
            "==================================================\n"
            "📍 123 Hospital Road, Freetown, Sierra Leone     \n"
            "📞 +232 76 123 456 | 🌐 physicalhealthclinic.sl \n"
            "--------------------------------------------------\n"
            f"RECEIPT NUMBER: {receipt_num}\n"
            f"DATE: {self.issue_date_entry.get() or datetime.now().strftime('%Y-%m-%d')}\n"
            f"PATIENT: {data['PatientName']}\n"
            f"PAYMENT ID: #{data['PaymentID']}\n"
            f"METHOD: {data['PaymentMethod']}\n"
            "--------------------------------------------------\n"
            "ITEM DESCRIPTION           QTY    UNIT PRICE     TOTAL\n"
            "--------------------------------------------------\n"
        )
        total = 0.0
        for item in items:
            desc = item['description'][:24].ljust(25)
            qty = str(item['qty']).rjust(4)
            price = f"Le {item['price']:,.2f}".rjust(12)
            item_tot = f"Le {item['total']:,.2f}".rjust(12)
            text += f"{desc} {qty} {price} {item_tot}\n"
            total += item['total']
            
        text += (
            "--------------------------------------------------\n"
            f"TOTAL PAID:                        Le {total:,.2f}\n"
            "--------------------------------------------------\n"
            "✅ STATUS: PAID\n"
            "Thank you for choosing our clinic!\n"
            "==================================================\n"
        )
        return text

    def print_receipt(self):
        if not self.selected_payment_data:
            messagebox.showwarning("Warning", "Please select a receipt/payment first.")
            return
        
        # Show text preview
        messagebox.showinfo("Receipt Preview", self._generate_receipt_text())

    def export_pdf(self):
        if not PDF_AVAILABLE:
            messagebox.showerror(
                "PDF Library Missing",
                "ReportLab library is required for PDF exports.\nInstall it using: pip install reportlab"
            )
            return

        if not self.selected_payment_data:
            messagebox.showwarning("Warning", "Select a payment first.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save PDF Receipt"
        )
        if not file_path:
            return

        try:
            self._create_pdf_receipt(file_path)
            messagebox.showinfo("Success", f"PDF receipt saved successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to generate PDF:\n{e}")

    def _create_pdf_receipt(self, file_path):
        data = self.selected_payment_data
        receipt_num = self.receipt_number_entry.get() or f"RCP-{self.selected_receipt_id:06d}"
        issue_date = self.issue_date_entry.get() or datetime.now().strftime("%Y-%m-%d")
        items = self._fetch_receipt_items(data['PaymentID'])

        # Create doc
        doc = SimpleDocTemplate(file_path, pagesize=letter, topMargin=54, bottomMargin=54, leftMargin=54, rightMargin=54)
        styles = getSampleStyleSheet()
        story = []

        # Styles
        title_style = ParagraphStyle(
            'ReceiptTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=24,
            textColor=colors.HexColor('#1F6AA5'),
            alignment=TA_CENTER
        )
        subtitle_style = ParagraphStyle(
            'ReceiptSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        meta_style = ParagraphStyle(
            'ReceiptMeta',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.black
        )

        # Header Block
        story.append(Paragraph("PHYSICAL HEALTH CLINIC", title_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph("Your Trusted Partners in Premium Clinical Healthcare", subtitle_style))
        story.append(Spacer(1, 10))

        # Contact table
        contact_data = [
            [
                Paragraph("<b>📍 Address:</b> 123 Hospital Road, Freetown, Sierra Leone", meta_style),
                Paragraph("<b>📞 Contact:</b> +232 76 123 456", meta_style)
            ],
            [
                Paragraph("<b>📧 Email:</b> billing@physicalhealthclinic.sl", meta_style),
                Paragraph("<b>🌐 Web:</b> physicalhealthclinic.sl", meta_style)
            ]
        ]
        contact_table = Table(contact_data, colWidths=[250, 250])
        contact_table.setStyle(TableStyle([
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor('#1F6AA5')),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(contact_table)
        story.append(Spacer(1, 15))

        # Meta Panel (Receipt ID, Date, Patient, Payment ID)
        meta_left = (
            f"<b>Receipt No:</b> {receipt_num}<br/>"
            f"<b>Issue Date:</b> {issue_date}<br/>"
            f"<b>Printed By:</b> Staff ID {self.worker_id}"
        )
        meta_right = (
            f"<b>Patient Name:</b> {data['PatientName']}<br/>"
            f"<b>Payment ID:</b> #{data['PaymentID']}<br/>"
            f"<b>Payment Method:</b> {data['PaymentMethod']}"
        )
        panel_data = [
            [Paragraph(meta_left, meta_style), Paragraph(meta_right, meta_style)]
        ]
        panel_table = Table(panel_data, colWidths=[250, 250])
        panel_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F7F9FC')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(panel_table)
        story.append(Spacer(1, 20))

        # Itemized Table
        table_headers = [Paragraph("<b>Item Description</b>", meta_style), 
                         Paragraph("<b>Qty</b>", meta_style), 
                         Paragraph("<b>Unit Price</b>", meta_style), 
                         Paragraph("<b>Total</b>", meta_style)]
        table_rows = [table_headers]
        
        subtotal = 0.0
        for item in items:
            table_rows.append([
                Paragraph(item['description'], meta_style),
                Paragraph(str(item['qty']), meta_style),
                Paragraph(f"Le {item['price']:,.2f}", meta_style),
                Paragraph(f"Le {item['total']:,.2f}", meta_style)
            ])
            subtotal += item['total']

        # Totals rows
        table_rows.append([Paragraph("", meta_style), Paragraph("", meta_style), Paragraph("<b>Subtotal:</b>", meta_style), Paragraph(f"Le {subtotal:,.2f}", meta_style)])
        table_rows.append([Paragraph("", meta_style), Paragraph("", meta_style), Paragraph("<b>Total Paid:</b>", meta_style), Paragraph(f"<b>Le {subtotal:,.2f}</b>", meta_style)])

        item_table = Table(table_rows, colWidths=[240, 50, 100, 110])
        item_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F6AA5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -3), 0.5, colors.HexColor('#CBD5E0')),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
        ]))
        story.append(item_table)
        story.append(Spacer(1, 30))

        # Paid stamp
        paid_style = ParagraphStyle(
            'PaidStamp',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=colors.HexColor('#4CAF50'),
            alignment=TA_CENTER
        )
        story.append(Paragraph("✅ PAID & VERIFIED", paid_style))
        story.append(Spacer(1, 20))

        # Validity stamp
        valid_style = ParagraphStyle(
            'ValidStamp',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        story.append(Paragraph("This is an officially certified electronic receipt valid for all medical claims and audits.", valid_style))

        doc.build(story)


if __name__ == "__main__":
    class TestApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.geometry("1500x850")
            ReceiptWindow(self)

    app = TestApp()
    app.mainloop()
