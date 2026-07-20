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

class ReceiptPreviewModal(ctk.CTkToplevel):
    """Interactive On-Screen Receipt Preview Modal."""

    def __init__(self, parent, receipt_id, worker_id=1, user_role="Unknown"):
        super().__init__(parent)
        self.master = parent
        self.receipt_id = receipt_id
        self.worker_id = worker_id
        self.user_role = user_role

        self.title(f"🧾 Receipt Preview - RCP-{int(receipt_id):06d}")
        self.geometry("680x820")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.receipt_data = None
        self.line_items = []

        self.setup_ui()
        self.load_receipt_details()

    def setup_ui(self):
        container = ctk.CTkFrame(self, fg_color="#F8FAFC", corner_radius=12)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # 1. Header Banner
        header = ctk.CTkFrame(container, fg_color="#1E3A8A", corner_radius=8, height=85)
        header.pack(fill="x", padx=10, pady=10)
        header.pack_propagate(False)

        logo_canvas = ctk.CTkCanvas(header, width=45, height=45, bg="#1E3A8A", highlightthickness=0)
        logo_canvas.pack(side="left", padx=15, pady=15)
        logo_canvas.create_rectangle(2, 2, 43, 43, fill="#1D4ED8", outline="#60A5FA", width=1.5)
        logo_canvas.create_rectangle(19, 10, 26, 35, fill="#FFFFFF", outline="")
        logo_canvas.create_rectangle(10, 19, 35, 26, fill="#FFFFFF", outline="")

        header_title_frame = ctk.CTkFrame(header, fg_color="transparent")
        header_title_frame.pack(side="left", fill="both", expand=True, pady=10)

        ctk.CTkLabel(
            header_title_frame,
            text="PHYSICAL HEALTH CLINIC",
            font=("Arial", 16, "bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_title_frame,
            text="“Quality Healthcare, Trusted Care”",
            font=("Arial", 11, "italic"),
            text_color="#CBD5E1"
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_title_frame,
            text="📍 123 Hospital Road, Freetown, SL | 📞 +232 76 123456",
            font=("Arial", 9),
            text_color="#94A3B8"
        ).pack(anchor="w")

        # 2. Metadata Panel
        self.meta_frame = ctk.CTkFrame(container, fg_color="#FFFFFF", border_color="#E2E8F0", border_width=1, corner_radius=8)
        self.meta_frame.pack(fill="x", padx=10, pady=5)

        self.meta_left_lbl = ctk.CTkLabel(self.meta_frame, text="Loading details...", font=("Arial", 11), text_color="#1E293B", justify="left")
        self.meta_left_lbl.pack(side="left", padx=15, pady=10, anchor="w")

        self.meta_right_lbl = ctk.CTkLabel(self.meta_frame, text="", font=("Arial", 11), text_color="#1E293B", justify="left")
        self.meta_right_lbl.pack(side="right", padx=15, pady=10, anchor="e")

        # 3. Itemized List Frame
        self.items_frame = ctk.CTkScrollableFrame(container, fg_color="#FFFFFF", border_color="#E2E8F0", border_width=1, corner_radius=8, height=260)
        self.items_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 4. Grand Total & Verification Box
        total_box = ctk.CTkFrame(container, fg_color="#F0FDF4", border_color="#DCFCE7", border_width=1, corner_radius=8, height=65)
        total_box.pack(fill="x", padx=10, pady=5)
        total_box.pack_propagate(False)

        self.total_lbl = ctk.CTkLabel(total_box, text="GRAND TOTAL PAID: Le 0.00", font=("Arial", 16, "bold"), text_color="#15803D")
        self.total_lbl.pack(side="left", padx=20, pady=15)

        status_frame = ctk.CTkFrame(total_box, fg_color="transparent")
        status_frame.pack(side="right", padx=15, pady=8)

        ctk.CTkLabel(status_frame, text="✅ PAID & VERIFIED", font=("Arial", 11, "bold"), text_color="#15803D").pack(anchor="e")

        qr_canvas = ctk.CTkCanvas(status_frame, width=32, height=32, bg="#F0FDF4", highlightthickness=0)
        qr_canvas.pack(anchor="e", pady=2)
        qr_canvas.create_rectangle(1, 1, 31, 31, fill="#FFFFFF", outline="#15803D")
        qr_canvas.create_rectangle(3, 3, 10, 10, fill="#1E3A8A")
        qr_canvas.create_rectangle(21, 3, 28, 10, fill="#1E3A8A")
        qr_canvas.create_rectangle(3, 21, 10, 28, fill="#1E3A8A")
        qr_canvas.create_rectangle(14, 14, 18, 18, fill="#1E3A8A")

        # 5. Control Action Bar
        action_bar = ctk.CTkFrame(container, fg_color="transparent")
        action_bar.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(action_bar, text="🖨 Print", font=("Arial", 12, "bold"), fg_color="#3B82F6", hover_color="#2563EB", width=120, height=36, command=self.print_pdf).pack(side="left", padx=5)
        ctk.CTkButton(action_bar, text="📄 Save as PDF", font=("Arial", 12, "bold"), fg_color="#10B981", hover_color="#059669", width=130, height=36, command=self.export_pdf).pack(side="left", padx=5)
        ctk.CTkButton(action_bar, text="🔄 Reprint", font=("Arial", 12, "bold"), fg_color="#8B5CF6", hover_color="#7C3AED", width=120, height=36, command=self.reprint_action).pack(side="left", padx=5)
        ctk.CTkButton(action_bar, text="🚪 Close", font=("Arial", 12, "bold"), fg_color="#64748B", hover_color="#475569", width=110, height=36, command=self.destroy).pack(side="right", padx=5)

    def load_receipt_details(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    r.ReceiptID, 
                    r.PaymentID, 
                    p.Amount, 
                    r.IssueDate, 
                    p.PaymentMethod, 
                    pat.FullName,
                    p.PrescriptionID,
                    (SELECT CONCAT(hw.FullName, ' (ID: HW-', LPAD(hw.WorkerID, 3, '0'), ')') FROM Health_Workers hw 
                     JOIN Prescription pr ON hw.WorkerID = pr.DoctorID 
                     WHERE pr.TreatmentID = p.PrescriptionID LIMIT 1) AS PrescribingDoctor,
                    (SELECT CONCAT(hw.FullName, ' (ID: HW-', LPAD(hw.WorkerID, 3, '0'), ')') FROM Health_Workers hw 
                     JOIN Laboratory_Requests lr ON hw.WorkerID = lr.DoctorID 
                     WHERE lr.RequestID = p.LabRequestID LIMIT 1) AS LabDoctor,
                    ph.FullName AS StaffName,
                    ph.WorkerID AS StaffWorkerID,
                    p.PaymentType
                FROM Receipt r
                JOIN Payment p ON r.PaymentID = p.PaymentID
                JOIN Patients pat ON p.PatientID = pat.PatientID
                LEFT JOIN Health_Workers ph ON r.PrintedBy = ph.WorkerID
                WHERE r.ReceiptID = %s
            """, (self.receipt_id,))
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return

            # Determine appropriate doctor
            ptype = row[11]
            if ptype == "Medicines" and row[7]:
                doc_name = row[7]
            elif ptype == "Laboratory" and row[8]:
                doc_name = row[8]
            elif row[7]:
                doc_name = row[7]
            elif row[8]:
                doc_name = row[8]
            else:
                doc_name = "N/A"

            self.receipt_data = {
                'ReceiptID': row[0],
                'PaymentID': row[1],
                'Amount': float(row[2]),
                'IssueDate': row[3],
                'PaymentMethod': row[4],
                'PatientName': row[5],
                'PrescriptionID': row[6],
                'DoctorName': doc_name,
                'PharmacistName': row[9] if row[9] else "Staff Duty",
                'StaffWorkerID': row[10] if row[10] else 1,
                'PaymentType': row[11]
            }

            # Fetch line items
            p_id = row[1]
            p_type = row[9]
            disp_id = None
            lab_req = None
            service_id = None

            cursor.execute("SELECT LabRequestID, DispensingID, ServiceID FROM Payment WHERE PaymentID = %s", (p_id,))
            p_meta = cursor.fetchone()
            if p_meta:
                lab_req, disp_id, service_id = p_meta

            self.line_items = []
            if p_type == "Medicines":
                if row[6]:  # TreatmentID
                    cursor.execute("""
                        SELECT pr.MedicineName, pr.QuantityPrescribed, inv.SellingPrice
                        FROM Prescription pr
                        LEFT JOIN Inventory inv ON LOWER(pr.MedicineName) = LOWER(inv.MedicineName)
                        WHERE pr.TreatmentID = %s
                    """, (row[6],))
                    for name, qty, sell in cursor.fetchall():
                        price = float(sell) if sell else 0.0
                        self.line_items.append({"desc": name, "qty": qty, "price": price, "total": qty * price})
                elif disp_id:
                    cursor.execute("""
                        SELECT pr.MedicineName, md.QuantityDispensed, inv.SellingPrice
                        FROM Medicine_Dispensing md
                        JOIN Prescription pr ON md.PrescriptionID = pr.PrescriptionID
                        JOIN Inventory inv ON md.InventoryID = inv.InventoryID
                        WHERE md.DispensingID = %s
                    """, (disp_id,))
                    for name, qty, sell in cursor.fetchall():
                        self.line_items.append({"desc": name, "qty": qty, "price": float(sell), "total": qty * float(sell)})
            elif p_type == "Laboratory":
                if lab_req:
                    cursor.execute("""
                        SELECT lt.TestName, lt.Price
                        FROM Laboratory_Results res
                        JOIN Laboratory_Tests lt ON res.TestID = lt.TestID
                        WHERE res.RequestID = %s
                    """, (lab_req,))
                    for name, price in cursor.fetchall():
                        p_val = float(price) if price else 0.0
                        self.line_items.append({"desc": f"Lab Test: {name}", "qty": 1, "price": p_val, "total": p_val})
                if not self.line_items:
                    self.line_items.append({"desc": f"Laboratory Test Request (#{lab_req})" if lab_req else "Laboratory Services", "qty": 1, "price": float(row[2]), "total": float(row[2])})
            elif p_type == "Registration":
                self.line_items.append({"desc": "Patient Registration Fee", "qty": 1, "price": float(row[2]), "total": float(row[2])})
            elif p_type == "Consultation":
                self.line_items.append({"desc": "Doctor Clinical Consultation Fee", "qty": 1, "price": float(row[2]), "total": float(row[2])})
            elif service_id:
                cursor.execute("SELECT ServiceName, Price FROM Hospital_Services WHERE ServiceID = %s", (service_id,))
                svc = cursor.fetchone()
                if svc:
                    self.line_items.append({"desc": svc[0], "qty": 1, "price": float(svc[1]), "total": float(svc[1])})

            if not self.line_items:
                self.line_items.append({"desc": f"{p_type} Charge", "qty": 1, "price": float(row[2]), "total": float(row[2])})

            conn.close()

            r_num = f"RCP-{self.receipt_data['ReceiptID']:06d}"
            pr_num = f"PR-{self.receipt_data['PrescriptionID']:04d}" if self.receipt_data['PrescriptionID'] else "N/A"

            doc_lbl = "Ordering Doctor" if p_type == "Laboratory" else "Prescribing Doctor"
            staff_id_str = f"HW-{self.receipt_data['StaffWorkerID']:03d}" if isinstance(self.receipt_data['StaffWorkerID'], int) else str(self.receipt_data['StaffWorkerID'])

            meta_left_text = (
                f"Receipt No: {r_num}\n"
                f"Prescription No: {pr_num}\n"
                f"Date & Time: {self.receipt_data['IssueDate']}"
            )
            meta_right_text = (
                f"Patient Name: {self.receipt_data['PatientName']}\n"
                f"{doc_lbl}: {self.receipt_data['DoctorName']}\n"
                f"Issued By Staff: {self.receipt_data['PharmacistName']} (ID: {staff_id_str})"
            )

            self.meta_left_lbl.configure(text=meta_left_text)
            self.meta_right_lbl.configure(text=meta_right_text)

            for child in self.items_frame.winfo_children():
                child.destroy()

            is_med = (p_type == "Medicines")
            if is_med:
                header_row = ctk.CTkFrame(self.items_frame, fg_color="#1E3A8A", corner_radius=4, height=30)
                header_row.pack(fill="x", pady=(0, 4))
                header_row.pack_propagate(False)
                ctk.CTkLabel(header_row, text="Medicine / Service", font=("Arial", 11, "bold"), text_color="#FFFFFF", anchor="w").pack(side="left", padx=10)
                ctk.CTkLabel(header_row, text="Subtotal", font=("Arial", 11, "bold"), text_color="#FFFFFF", anchor="e").pack(side="right", padx=10)
                ctk.CTkLabel(header_row, text="Price", font=("Arial", 11, "bold"), text_color="#FFFFFF", anchor="e").pack(side="right", padx=25)
                ctk.CTkLabel(header_row, text="Qty", font=("Arial", 11, "bold"), text_color="#FFFFFF", anchor="center").pack(side="right", padx=20)

                for item in self.line_items:
                    row_f = ctk.CTkFrame(self.items_frame, fg_color="transparent", height=28)
                    row_f.pack(fill="x", pady=2)
                    row_f.pack_propagate(False)
                    ctk.CTkLabel(row_f, text=item["desc"], font=("Arial", 11), text_color="#1E293B", anchor="w").pack(side="left", padx=10)
                    ctk.CTkLabel(row_f, text=f"Le {item['total']:,.2f}", font=("Arial", 11, "bold"), text_color="#1E293B", anchor="e").pack(side="right", padx=10)
                    ctk.CTkLabel(row_f, text=f"Le {item['price']:,.2f}", font=("Arial", 11), text_color="#475569", anchor="e").pack(side="right", padx=25)
                    ctk.CTkLabel(row_f, text=str(item["qty"]), font=("Arial", 11), text_color="#475569", anchor="center").pack(side="right", padx=25)
            else:
                header_row = ctk.CTkFrame(self.items_frame, fg_color="#1E3A8A", corner_radius=4, height=30)
                header_row.pack(fill="x", pady=(0, 4))
                header_row.pack_propagate(False)
                ctk.CTkLabel(header_row, text="Description / Clinical Service", font=("Arial", 11, "bold"), text_color="#FFFFFF", anchor="w").pack(side="left", padx=10)
                ctk.CTkLabel(header_row, text="Amount", font=("Arial", 11, "bold"), text_color="#FFFFFF", anchor="e").pack(side="right", padx=10)

                for item in self.line_items:
                    row_f = ctk.CTkFrame(self.items_frame, fg_color="transparent", height=28)
                    row_f.pack(fill="x", pady=2)
                    row_f.pack_propagate(False)
                    ctk.CTkLabel(row_f, text=item["desc"], font=("Arial", 11), text_color="#1E293B", anchor="w").pack(side="left", padx=10)
                    ctk.CTkLabel(row_f, text=f"Le {item['total']:,.2f}", font=("Arial", 11, "bold"), text_color="#1E293B", anchor="e").pack(side="right", padx=10)

            self.total_lbl.configure(text=f"GRAND TOTAL PAID: Le {self.receipt_data['Amount']:,.2f}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load modal receipt preview:\n{e}")

    def generate_pdf_file(self, file_path):
        if hasattr(self.master, "_create_pdf_receipt"):
            self.master.selected_payment_data = self.receipt_data
            self.master.selected_receipt_id = self.receipt_id
            self.master._create_pdf_receipt(file_path)
        else:
            r_win = ReceiptWindow(self)
            r_win.withdraw()
            r_win.selected_payment_data = self.receipt_data
            r_win.selected_receipt_id = self.receipt_id
            r_win._create_pdf_receipt(file_path)
            r_win.destroy()

    def print_pdf(self):
        import tempfile
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"receipt_{self.receipt_id}.pdf")
        try:
            self.generate_pdf_file(file_path)
            import sys
            import subprocess
            if sys.platform == "darwin":
                result = subprocess.run(["lp", file_path], capture_output=True)
                if result.returncode != 0:
                    self.preview_pdf()
                else:
                    messagebox.showinfo("Success", "Receipt sent to printer.")
            elif sys.platform == "win32":
                os.startfile(file_path, "print")
            else:
                subprocess.run(["lpr", file_path])
        except Exception:
            self.preview_pdf()

    def preview_pdf(self):
        import tempfile
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"receipt_{self.receipt_id}.pdf")
        try:
            self.generate_pdf_file(file_path)
            import sys
            import subprocess
            if sys.platform == "darwin":
                subprocess.run(["open", file_path])
            elif sys.platform == "win32":
                os.startfile(file_path)
            else:
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview PDF:\n{e}")

    def export_pdf(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title=f"Save Receipt RCP-{int(self.receipt_id):06d}"
        )
        if not file_path:
            return
        try:
            self.generate_pdf_file(file_path)
            messagebox.showinfo("Success", f"PDF saved successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export PDF:\n{e}")

    def reprint_action(self):
        try:
            from database import log_audit_action
            log_audit_action(self.worker_id, f"Reprinted receipt RCP-{self.receipt_id:06d}")
        except Exception:
            pass
        self.print_pdf()


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

        # Check current user worker id and role
        self.worker_id = 1
        self.user_role = "Unknown"
        if hasattr(session, "current_user") and session.current_user:
            self.worker_id = session.current_user.get("worker_id", 1)
            self.user_role = session.current_user.get("role", "Unknown")

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

        # Left Panel (Form) - Hidden for Lab Techs
        if self.user_role != "Laboratory Technician":
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
            btn_frame.pack(pady=15)

            ctk.CTkButton(btn_frame, text="➕ Generate Receipt", command=self.generate_receipt, width=155).grid(row=0, column=0, padx=5, pady=4)
            ctk.CTkButton(btn_frame, text="👁 Preview On-Screen", command=self.open_selected_on_screen_preview, width=155).grid(row=0, column=1, padx=5, pady=4)
            ctk.CTkButton(btn_frame, text="🖨 Print PDF", command=self.print_pdf, fg_color="#3B82F6", hover_color="#2563EB", width=155).grid(row=1, column=0, padx=5, pady=4)
            ctk.CTkButton(btn_frame, text="📄 Save as PDF", command=self.export_pdf, fg_color="#10B981", hover_color="#059669", width=155).grid(row=1, column=1, padx=5, pady=4)
            ctk.CTkButton(btn_frame, text="🧹 Clear Fields", command=self.clear_fields, width=155).grid(row=2, column=0, padx=5, pady=4)
            
            if self.user_role == "Administrator":
                ctk.CTkButton(btn_frame, text="❌ Delete", command=self.delete_receipt, fg_color="red", hover_color="#b71c1c", width=155).grid(row=2, column=1, padx=5, pady=4)
            
            ctk.CTkButton(btn_frame, text="🚪 Close Window", command=self.destroy, fg_color="#4B5563", hover_color="#374151", width=320).grid(row=3, column=0, columnspan=2, padx=5, pady=8)

        # Right Panel (List)
        self.table_frame = ctk.CTkFrame(main_frame)
        self.table_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        # Filter Bar for Accountant / Admin
        if self.user_role in ("Accountant", "Administrator"):
            filter_bar = ctk.CTkFrame(self.table_frame, fg_color="#F8FAFC", corner_radius=8, border_color="#CBD5E1", border_width=1)
            filter_bar.pack(fill="x", padx=15, pady=(10, 5))

            f_row1 = ctk.CTkFrame(filter_bar, fg_color="transparent")
            f_row1.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(f_row1, text="Department:", font=("Arial", 11, "bold")).pack(side="left", padx=(5, 2))
            self.dept_filter = ctk.CTkComboBox(f_row1, values=["All Departments", "Pharmacy", "Reception", "Laboratory"], width=130)
            self.dept_filter.pack(side="left", padx=5)

            ctk.CTkLabel(f_row1, text="Method:", font=("Arial", 11, "bold")).pack(side="left", padx=(10, 2))
            self.method_filter = ctk.CTkComboBox(f_row1, values=["All Methods", "Cash", "Orange Money", "AfriMoney", "QMoney", "Wave", "Card"], width=120)
            self.method_filter.pack(side="left", padx=5)

            ctk.CTkLabel(f_row1, text="Staff:", font=("Arial", 11, "bold")).pack(side="left", padx=(10, 2))
            self.staff_filter = ctk.CTkComboBox(f_row1, values=["All Staff"], width=160)
            self.staff_filter.pack(side="left", padx=5)
            self.load_staff_members()

            f_row2 = ctk.CTkFrame(filter_bar, fg_color="transparent")
            f_row2.pack(fill="x", padx=10, pady=(0, 5))

            ctk.CTkLabel(f_row2, text="Start Date:", font=("Arial", 11, "bold")).pack(side="left", padx=(5, 2))
            self.start_date_entry = ctk.CTkEntry(f_row2, placeholder_text="YYYY-MM-DD", width=110)
            self.start_date_entry.pack(side="left", padx=5)

            ctk.CTkLabel(f_row2, text="End Date:", font=("Arial", 11, "bold")).pack(side="left", padx=(10, 2))
            self.end_date_entry = ctk.CTkEntry(f_row2, placeholder_text="YYYY-MM-DD", width=110)
            self.end_date_entry.pack(side="left", padx=5)

            ctk.CTkButton(f_row2, text="🔍 Filter", width=90, font=("Arial", 11, "bold"), fg_color="#1E3A8A", command=self.load_receipts).pack(side="left", padx=10)
            ctk.CTkButton(f_row2, text="🔄 Reset Filters", width=110, font=("Arial", 11, "bold"), fg_color="#64748B", command=self.reset_filters).pack(side="left", padx=2)

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
                SELECT 
                    r.ReceiptID, 
                    r.PaymentID, 
                    p.Amount, 
                    r.IssueDate, 
                    p.PaymentMethod, 
                    pat.FullName,
                    p.PrescriptionID,
                    (SELECT CONCAT(hw.FullName, ' (ID: HW-', LPAD(hw.WorkerID, 3, '0'), ')') FROM Health_Workers hw 
                     JOIN Prescription pr ON hw.WorkerID = pr.DoctorID 
                     WHERE pr.TreatmentID = p.PrescriptionID LIMIT 1) AS PrescribingDoctor,
                    (SELECT CONCAT(hw.FullName, ' (ID: HW-', LPAD(hw.WorkerID, 3, '0'), ')') FROM Health_Workers hw 
                     JOIN Laboratory_Requests lr ON hw.WorkerID = lr.DoctorID 
                     WHERE lr.RequestID = p.LabRequestID LIMIT 1) AS LabDoctor,
                    ph.FullName AS StaffName,
                    ph.WorkerID AS StaffWorkerID,
                    p.PaymentType
                FROM Receipt r
                JOIN Payment p ON r.PaymentID = p.PaymentID
                JOIN Patients pat ON p.PatientID = pat.PatientID
                LEFT JOIN Health_Workers ph ON r.PrintedBy = ph.WorkerID
                WHERE r.ReceiptID = %s
            """, (receipt_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                ptype = row[11]
                if ptype == "Medicines" and row[7]:
                    doc_name = row[7]
                elif ptype == "Laboratory" and row[8]:
                    doc_name = row[8]
                elif row[7]:
                    doc_name = row[7]
                elif row[8]:
                    doc_name = row[8]
                else:
                    doc_name = "N/A"

                self.selected_payment_data = {
                    'PaymentID': row[1],
                    'Amount': row[2],
                    'PaymentDate': row[3],
                    'PaymentMethod': row[4],
                    'PatientName': row[5],
                    'PrescriptionID': row[6],
                    'DoctorName': doc_name,
                    'PharmacistName': row[9] if row[9] else "Staff Duty",
                    'StaffWorkerID': row[10] if row[10] else 1,
                    'PaymentType': row[11]
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
            query = """
                SELECT p.PaymentID, pat.FullName, p.Amount
                FROM Payment p
                LEFT JOIN Patients pat ON p.PatientID = pat.PatientID
                WHERE p.PaymentMethod <> 'Pending'
            """
            params = []
            if self.user_role != "Administrator" and self.user_role != "Accountant":
                query += " AND p.BilledBy = %s"
                params.append(self.worker_id)
            query += " ORDER BY p.PaymentID DESC"
            cursor.execute(query, tuple(params))
            payment_list = [f"Payment #{row[0]} - {row[1]} - Le {row[2]:,.2f}" for row in cursor.fetchall()]
            if hasattr(self, 'payment_combo') and self.payment_combo:
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
                SELECT 
                    p.PaymentID, 
                    pat.FullName, 
                    p.Amount, 
                    p.PaymentDate, 
                    p.PaymentMethod,
                    p.PrescriptionID,
                    (SELECT CONCAT(hw.FullName, ' (ID: HW-', LPAD(hw.WorkerID, 3, '0'), ')') FROM Health_Workers hw 
                     JOIN Prescription pr ON hw.WorkerID = pr.DoctorID 
                     WHERE pr.TreatmentID = p.PrescriptionID LIMIT 1) AS PrescribingDoctor,
                    (SELECT CONCAT(hw.FullName, ' (ID: HW-', LPAD(hw.WorkerID, 3, '0'), ')') FROM Health_Workers hw 
                     JOIN Laboratory_Requests lr ON hw.WorkerID = lr.DoctorID 
                     WHERE lr.RequestID = p.LabRequestID LIMIT 1) AS LabDoctor,
                    ph.FullName AS StaffName,
                    ph.WorkerID AS StaffWorkerID,
                    p.PaymentType
                FROM Payment p
                LEFT JOIN Patients pat ON p.PatientID = pat.PatientID
                LEFT JOIN Health_Workers ph ON p.BilledBy = ph.WorkerID
                WHERE p.PaymentID = %s
            """, (payment_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                ptype = row[10]
                if ptype == "Medicines" and row[6]:
                    doc_name = row[6]
                elif ptype == "Laboratory" and row[7]:
                    doc_name = row[7]
                elif row[6]:
                    doc_name = row[6]
                elif row[7]:
                    doc_name = row[7]
                else:
                    doc_name = "N/A"

                self.selected_payment_data = {
                    'PaymentID': row[0],
                    'PatientName': row[1],
                    'Amount': row[2],
                    'PaymentDate': row[3],
                    'PaymentMethod': row[4],
                    'PrescriptionID': row[5],
                    'DoctorName': doc_name,
                    'PharmacistName': row[8] if row[8] else "Staff Duty",
                    'StaffWorkerID': row[9] if row[9] else 1,
                    'PaymentType': row[10]
                }
                self.total_amount_entry.configure(state="normal")
                self.total_amount_entry.delete(0, "end")
                self.total_amount_entry.insert(0, str(row[2]))
                self.total_amount_entry.configure(state="disabled")

                self.issue_date_entry.delete(0, "end")
                self.issue_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        except Exception as e:
            print(f"Error handling payment selection: {e}")

    def load_staff_members(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT WorkerID, FullName, Role FROM Health_Workers ORDER BY FullName ASC")
            staff_list = ["All Staff"] + [f"{row[1]} ({row[2]}) | ID:{row[0]}" for row in cursor.fetchall()]
            conn.close()
            if hasattr(self, "staff_filter"):
                self.staff_filter.configure(values=staff_list)
                self.staff_filter.set("All Staff")
        except Exception as e:
            print(f"Error loading staff members: {e}")

    def reset_filters(self):
        if hasattr(self, "dept_filter"):
            self.dept_filter.set("All Departments")
        if hasattr(self, "method_filter"):
            self.method_filter.set("All Methods")
        if hasattr(self, "staff_filter"):
            self.staff_filter.set("All Staff")
        if hasattr(self, "start_date_entry"):
            self.start_date_entry.delete(0, "end")
        if hasattr(self, "end_date_entry"):
            self.end_date_entry.delete(0, "end")
        if hasattr(self, "search_entry"):
            self.search_entry.delete(0, "end")
        self.load_receipts()

    def load_receipts(self):
        for item in self.table.get_children():
            self.table.delete(item)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT r.ReceiptID, r.PaymentID, pat.FullName, p.Amount, r.IssueDate, hw.FullName
                FROM Receipt r
                JOIN Payment p ON r.PaymentID = p.PaymentID
                JOIN Patients pat ON p.PatientID = pat.PatientID
                LEFT JOIN Health_Workers hw ON r.PrintedBy = hw.WorkerID
            """
            conditions = []
            params = []

            # Role Access Scopes
            if self.user_role == "Pharmacist":
                conditions.append("(r.PrintedBy = %s OR p.BilledBy = %s)")
                params.extend([self.worker_id, self.worker_id])
                conditions.append("p.PaymentType = 'Medicines'")
            elif self.user_role == "Receptionist":
                conditions.append("(r.PrintedBy = %s OR p.BilledBy = %s)")
                params.extend([self.worker_id, self.worker_id])
                conditions.append("p.PaymentType IN ('Registration', 'Consultation', 'Hospital Service')")
            elif self.user_role == "Laboratory Technician":
                conditions.append("p.PaymentType = 'Laboratory'")
            elif self.user_role in ("Accountant", "Administrator"):
                if hasattr(self, "dept_filter"):
                    dept = self.dept_filter.get()
                    if dept == "Pharmacy":
                        conditions.append("p.PaymentType = 'Medicines'")
                    elif dept == "Reception":
                        conditions.append("p.PaymentType IN ('Registration', 'Consultation', 'Hospital Service')")
                    elif dept == "Laboratory":
                        conditions.append("p.PaymentType = 'Laboratory'")

                if hasattr(self, "method_filter") and self.method_filter.get() != "All Methods":
                    conditions.append("p.PaymentMethod = %s")
                    params.append(self.method_filter.get())

                if hasattr(self, "staff_filter") and self.staff_filter.get() != "All Staff":
                    staff_val = self.staff_filter.get()
                    if "| ID:" in staff_val:
                        staff_id = int(staff_val.split("| ID:")[1].strip())
                        conditions.append("(r.PrintedBy = %s OR p.BilledBy = %s)")
                        params.extend([staff_id, staff_id])

                if hasattr(self, "start_date_entry") and self.start_date_entry.get().strip():
                    conditions.append("DATE(r.IssueDate) >= %s")
                    params.append(self.start_date_entry.get().strip())

                if hasattr(self, "end_date_entry") and self.end_date_entry.get().strip():
                    conditions.append("DATE(r.IssueDate) <= %s")
                    params.append(self.end_date_entry.get().strip())

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY r.ReceiptID DESC"
            cursor.execute(query, tuple(params))
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

        if hasattr(self, "payment_combo"):
            vals = self.payment_combo.cget("values")
            for v in vals:
                if f"Payment #{payment_id}" in v:
                    self.payment_combo.set(v)
                    self.on_payment_selected(None)
                    break

        if hasattr(self, "receipt_number_entry"):
            self.receipt_number_entry.configure(state="normal")
            self.receipt_number_entry.delete(0, "end")
            self.receipt_number_entry.insert(0, f"RCP-{int(row[0]):06d}")
            self.receipt_number_entry.configure(state="disabled")

        if hasattr(self, "issue_date_entry"):
            self.issue_date_entry.delete(0, "end")
            self.issue_date_entry.insert(0, row[4])

        # Open On-Screen Receipt Preview Modal
        ReceiptPreviewModal(self, row[0], self.worker_id, self.user_role)

    def open_selected_on_screen_preview(self):
        if not self.selected_receipt_id:
            messagebox.showwarning("Warning", "Select a receipt first.")
            return
        ReceiptPreviewModal(self, self.selected_receipt_id, self.worker_id, self.user_role)

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
            query = """
                SELECT r.ReceiptID, r.PaymentID, pat.FullName, p.Amount, r.IssueDate, hw.FullName
                FROM Receipt r
                JOIN Payment p ON r.PaymentID = p.PaymentID
                JOIN Patients pat ON p.PatientID = pat.PatientID
                LEFT JOIN Health_Workers hw ON r.PrintedBy = hw.WorkerID
                WHERE (pat.FullName LIKE %s OR r.ReceiptID LIKE %s)
            """
            params = [f"%{q}%", f"%{q}%"]
            if self.user_role != "Administrator" and self.user_role != "Accountant":
                query += " AND p.BilledBy = %s"
                params.append(self.worker_id)
            query += " ORDER BY r.ReceiptID DESC"
            cursor.execute(query, tuple(params))
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
                elif ptype == "Laboratory":
                    if lab_req:
                        cursor.execute("""
                            SELECT lt.TestName, lt.Price
                            FROM Laboratory_Results res
                            JOIN Laboratory_Tests lt ON res.TestID = lt.TestID
                            WHERE res.RequestID = %s
                        """, (lab_req,))
                        for row in cursor.fetchall():
                            name, price = row
                            p_val = float(price) if price else 0.0
                            items.append({
                                "description": f"Lab Test: {name}",
                                "qty": 1,
                                "price": p_val,
                                "total": p_val
                            })
                    if not items:
                        items.append({
                            "description": f"Laboratory Test Request (#{lab_req})" if lab_req else "Laboratory Services",
                            "qty": 1,
                            "price": float(amount),
                            "total": float(amount)
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

    def preview_pdf(self):
        if not PDF_AVAILABLE:
            messagebox.showerror("PDF Library Missing", "ReportLab library is required.\nInstall it using: pip install reportlab")
            return
        if not self.selected_payment_data:
            messagebox.showwarning("Warning", "Select a payment/receipt first.")
            return

        import tempfile
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"receipt_{self.selected_receipt_id or 0}.pdf")
        try:
            self._create_pdf_receipt(file_path)
            import sys
            import subprocess
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", file_path])
            elif sys.platform == "win32":  # Windows
                os.startfile(file_path)
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview PDF:\n{e}")

    def print_pdf(self):
        if not PDF_AVAILABLE:
            messagebox.showerror("PDF Library Missing", "ReportLab library is required.\nInstall it using: pip install reportlab")
            return
        if not self.selected_payment_data:
            messagebox.showwarning("Warning", "Select a payment/receipt first.")
            return

        import tempfile
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"receipt_{self.selected_receipt_id or 0}.pdf")
        try:
            self._create_pdf_receipt(file_path)
            import sys
            import subprocess
            if sys.platform == "darwin":  # macOS
                # Try printing via lp, if it fails because of missing default printer, open Preview directly
                result = subprocess.run(["lp", file_path], capture_output=True)
                if result.returncode != 0:
                    # Silently fallback to Preview / manual printing
                    self.preview_pdf()
                else:
                    messagebox.showinfo("Success", "Receipt sent to printer successfully.")
            elif sys.platform == "win32":  # Windows
                os.startfile(file_path, "print")
            else:  # Linux
                subprocess.run(["lpr", file_path])
        except Exception as e:
            # Fallback to preview
            self.preview_pdf()

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

    def _get_clinic_logo_drawing(self):
        from reportlab.graphics.shapes import Drawing, Rect
        d = Drawing(40, 40)
        # Blue background
        d.add(Rect(0, 0, 40, 40, fillColor=colors.HexColor('#1E3A8A'), strokeColor=None, rx=8, ry=8))
        # White medical cross
        d.add(Rect(16, 8, 8, 24, fillColor=colors.white, strokeColor=None))
        d.add(Rect(8, 16, 24, 8, fillColor=colors.white, strokeColor=None))
        return d

    def _get_qr_code_drawing(self, receipt_num):
        from reportlab.graphics.shapes import Drawing, Rect
        import random
        width, height = 50, 50
        d = Drawing(width, height)
        # Border/bg
        d.add(Rect(0, 0, width, height, fillColor=colors.white, strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=0.5))
        # Top-Left finder
        d.add(Rect(2, height - 12, 10, 10, fillColor=colors.HexColor('#1E3A8A'), strokeColor=None))
        d.add(Rect(4, height - 10, 6, 6, fillColor=colors.white, strokeColor=None))
        d.add(Rect(5, height - 9, 4, 4, fillColor=colors.HexColor('#1E3A8A'), strokeColor=None))
        # Top-Right finder
        d.add(Rect(width - 12, height - 12, 10, 10, fillColor=colors.HexColor('#1E3A8A'), strokeColor=None))
        d.add(Rect(width - 10, height - 10, 6, 6, fillColor=colors.white, strokeColor=None))
        d.add(Rect(width - 9, height - 9, 4, 4, fillColor=colors.HexColor('#1E3A8A'), strokeColor=None))
        # Bottom-Left finder
        d.add(Rect(2, 2, 10, 10, fillColor=colors.HexColor('#1E3A8A'), strokeColor=None))
        d.add(Rect(4, 4, 6, 6, fillColor=colors.white, strokeColor=None))
        d.add(Rect(5, 5, 4, 4, fillColor=colors.HexColor('#1E3A8A'), strokeColor=None))
        # Random QR pixel seed
        val = sum(ord(c) for c in receipt_num)
        random.seed(val)
        for x in range(0, int(width), 2):
            for y in range(0, int(height), 2):
                if (x < 13 and y < 13) or (x < 13 and y > height - 13) or (x > width - 13 and y > height - 13):
                    continue
                if random.choice([True, False, False]):
                    d.add(Rect(x, y, 1.8, 1.8, fillColor=colors.HexColor('#1E3A8A'), strokeColor=None))
        return d

    def _build_receipt_copy_table(self, receipt_num, issue_date, data, items, copy_title):
        from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        
        styles = getSampleStyleSheet()
        
        # Styles for receipt elements
        banner_style = ParagraphStyle(
            'BannerText',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            textColor=colors.HexColor('#1E3A8A'),
            alignment=TA_CENTER
        )
        title_style = ParagraphStyle(
            'HeaderTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=13,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=1
        )
        motto_style = ParagraphStyle(
            'HeaderMotto',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=7.5,
            textColor=colors.HexColor('#4B5563'),
            spaceAfter=2
        )
        address_style = ParagraphStyle(
            'HeaderAddress',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7.5,
            textColor=colors.HexColor('#6B7280')
        )
        meta_style = ParagraphStyle(
            'MetaText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            textColor=colors.black,
            leading=10
        )
        item_header_style = ParagraphStyle(
            'ItemHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            textColor=colors.white
        )
        item_text_style = ParagraphStyle(
            'ItemText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            textColor=colors.black
        )
        total_text_style = ParagraphStyle(
            'TotalText',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            textColor=colors.HexColor('#15803D')
        )

        copy_elements = []

        # 1. Copy banner
        banner_table = Table([[Paragraph(f"••• {copy_title.upper()} •••", banner_style)]], colWidths=[515])
        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('PADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        copy_elements.append(banner_table)
        copy_elements.append(Spacer(1, 4))

        # 2. Header (Logo + Details)
        logo = self._get_clinic_logo_drawing()
        header_para = Paragraph(
            "<b>PHYSICAL HEALTH CLINIC</b><br/>"
            "<i>“Quality Healthcare, Trusted Care”</i><br/>"
            "📍 123 Hospital Road, Freetown, Sierra Leone  |  📞 +232 76 123 456",
            title_style
        )
        
        # We can construct the header details as a nested table
        header_table_data = [
            [logo, header_para]
        ]
        header_table = Table(header_table_data, colWidths=[50, 465])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 2),
            ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor('#1E3A8A')),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        copy_elements.append(header_table)
        copy_elements.append(Spacer(1, 5))

        # 3. Metadata Panel
        presc_id = data.get('PrescriptionID')
        presc_str = f"PR-{presc_id:04d}" if presc_id else "N/A"
        doctor_name = data.get('DoctorName', 'N/A')
        staff_name = data.get('PharmacistName', 'Staff Duty')
        staff_id = data.get('StaffWorkerID', 1)
        staff_id_str = f"HW-{staff_id:03d}" if isinstance(staff_id, int) else str(staff_id)
        p_type = data.get('PaymentType', '')
        doc_label = "Ordering Doctor" if p_type == "Laboratory" else "Prescribing Doctor"
        
        meta_left = (
            f"<b>Receipt No:</b> {receipt_num}<br/>"
            f"<b>Prescription No:</b> {presc_str}<br/>"
            f"<b>Date & Time:</b> {issue_date}"
        )
        meta_right = (
            f"<b>Patient Name:</b> {data['PatientName']}<br/>"
            f"<b>{doc_label}:</b> {doctor_name}<br/>"
            f"<b>Issued By Staff:</b> {staff_name} (ID: {staff_id_str})"
        )
        
        meta_table_data = [
            [Paragraph(meta_left, meta_style), Paragraph(meta_right, meta_style)]
        ]
        meta_table = Table(meta_table_data, colWidths=[250, 265])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        copy_elements.append(meta_table)
        copy_elements.append(Spacer(1, 5))

        # 4. Itemized Table
        is_medicine = (data.get('PaymentType') == 'Medicines')
        subtotal = 0.0

        if is_medicine:
            table_headers = [
                Paragraph("<b>Medicine / Service</b>", item_header_style), 
                Paragraph("<b>Qty</b>", item_header_style), 
                Paragraph("<b>Unit Price</b>", item_header_style), 
                Paragraph("<b>Subtotal</b>", item_header_style)
            ]
            table_rows = [table_headers]
            for item in items:
                table_rows.append([
                    Paragraph(item['description'], item_text_style),
                    Paragraph(str(item['qty']), item_text_style),
                    Paragraph(f"Le {item['price']:,.2f}", item_text_style),
                    Paragraph(f"Le {item['total']:,.2f}", item_text_style)
                ])
                subtotal += item['total']

            # Add total row
            table_rows.append([
                Paragraph("<b>GRAND TOTAL DUE</b>", total_text_style), 
                Paragraph("", item_text_style), 
                Paragraph("", item_text_style), 
                Paragraph(f"<b>Le {subtotal:,.2f}</b>", total_text_style)
            ])

            item_table = Table(table_rows, colWidths=[245, 50, 110, 110])
            item_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
                ('TOPPADDING', (0, 0), (-1, 0), 4),
                ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#E2E8F0')),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F0FDF4')),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#15803D')),
            ]))
        else:
            table_headers = [
                Paragraph("<b>Description / Service</b>", item_header_style), 
                Paragraph("<b>Amount</b>", item_header_style)
            ]
            table_rows = [table_headers]
            for item in items:
                table_rows.append([
                    Paragraph(item['description'], item_text_style),
                    Paragraph(f"Le {item['total']:,.2f}", item_text_style)
                ])
                subtotal += item['total']

            # Add total row
            table_rows.append([
                Paragraph("<b>GRAND TOTAL DUE</b>", total_text_style), 
                Paragraph(f"<b>Le {subtotal:,.2f}</b>", total_text_style)
            ])

            item_table = Table(table_rows, colWidths=[385, 130])
            item_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
                ('TOPPADDING', (0, 0), (-1, 0), 4),
                ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#E2E8F0')),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('ALIGN', (1, -1), (1, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F0FDF4')),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#15803D')),
            ]))
        copy_elements.append(item_table)
        copy_elements.append(Spacer(1, 5))

        # 5. Footer (Payment details + QR Code)
        qr_drawing = self._get_qr_code_drawing(receipt_num)
        
        footer_left = (
            f"<b>Payment Method:</b> {data['PaymentMethod']}<br/>"
            f"<b>Payment Status:</b> <font color='#15803D'><b>PAID & VERIFIED</b></font><br/>"
            f"<font color='#6B7280' size='6.5'>Verified clinic electronic receipt. Secure transaction.</font>"
        )
        
        footer_table_data = [
            [Paragraph(footer_left, meta_style), qr_drawing]
        ]
        footer_table = Table(footer_table_data, colWidths=[420, 95])
        footer_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('PADDING', (0,0), (-1,-1), 2),
        ]))
        copy_elements.append(footer_table)

        # Wrap everything into a single outer Table so it behaves as a single block
        outer_table_data = [[copy_elements]]
        outer_table = Table(outer_table_data, colWidths=[515])
        outer_table.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94A3B8')),
            ('PADDING', (0,0), (-1,-1), 10),
            ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ]))

        return outer_table

    def _create_pdf_receipt(self, file_path):
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        
        data = self.selected_payment_data
        receipt_num = self.receipt_number_entry.get() or f"RCP-{self.selected_receipt_id:06d}"
        issue_date = self.issue_date_entry.get() or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        items = self._fetch_receipt_items(data['PaymentID'])

        # Create A4 document (A4 width=595.27, height=841.89)
        # Margins: left/right=40, top/bottom=30
        doc = SimpleDocTemplate(
            file_path,
            pagesize=(595.27, 841.89),
            leftMargin=40,
            rightMargin=40,
            topMargin=30,
            bottomMargin=30
        )
        
        story = []

        # 1. Build Patient Copy
        patient_copy = self._build_receipt_copy_table(receipt_num, issue_date, data, items, "Patient Copy")
        story.append(patient_copy)
        story.append(Spacer(1, 15))

        # 2. Build Dashed Cut Line
        styles = getSampleStyleSheet()
        cut_line_style = ParagraphStyle(
            'CutLineText',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=7.5,
            textColor=colors.HexColor('#6B7280'),
            alignment=TA_CENTER
        )
        
        cut_table_data = [[
            Paragraph("✂-------------------------------------------------- FOLD / CUT HERE --------------------------------------------------✂", cut_line_style)
        ]]
        cut_table = Table(cut_table_data, colWidths=[515])
        cut_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('PADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(cut_table)
        story.append(Spacer(1, 15))

        # 3. Build Clinic Copy
        clinic_copy = self._build_receipt_copy_table(receipt_num, issue_date, data, items, "Clinic Copy")
        story.append(clinic_copy)

        doc.build(story)


if __name__ == "__main__":
    class TestApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.geometry("1500x850")
            ReceiptWindow(self)

    app = TestApp()
    app.mainloop()
