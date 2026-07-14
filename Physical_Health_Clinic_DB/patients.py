import customtkinter as ctk
from tkinter import ttk, messagebox
from database import connect_db

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class PatientWindow(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Patient Management")
        self.geometry("1500x850")
        self.resizable(True, True)

        # Track selected patient ID for updates/deletes
        self.selected_patient_id = None

        # Back Button at top-left
        back_btn = ctk.CTkButton(
            self,
            text="⬅ Back",
            width=100,
            command=self.destroy
        )
        back_btn.place(x=20, y=20)

        # Total Patients Badge (Top-Right)
        self.badge_frame = ctk.CTkFrame(
            self,
            fg_color=("#EBF3F9", "#2D3748"),
            border_color="#1F6AA5",
            border_width=1.5,
            corner_radius=12,
            height=35
        )
        self.badge_frame.place(relx=0.98, y=20, anchor="ne")
        self.badge_frame.pack_propagate(False)

        self.total_patients_lbl = ctk.CTkLabel(
            self.badge_frame,
            text="👥 Total Patients: 0",
            font=("Arial", 13, "bold"),
            text_color="#1F6AA5"
        )
        self.total_patients_lbl.pack(padx=12, expand=True)

        # =========================
        # Title
        # =========================

        title = ctk.CTkLabel(
            self,
            text="👨‍⚕️ Patient Management",
            font=("Arial", 30, "bold")
        )
        title.pack(pady=20)

        # =========================
        # Main Frame
        # =========================

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # =========================
        # Left Frame (Form)
        # =========================

        form_frame = ctk.CTkFrame(main_frame, width=420)
        form_frame.pack(side="left", fill="y", padx=15, pady=15)

        ctk.CTkLabel(form_frame, text="Patient Information",
                     font=("Arial", 22, "bold")).pack(pady=20)

        self.fullname = ctk.CTkEntry(form_frame, width=320, placeholder_text="Full Name")
        self.fullname.pack(pady=10)

        self.dob = ctk.CTkEntry(form_frame, width=320, placeholder_text="Date of Birth (YYYY-MM-DD)")
        self.dob.pack(pady=10)

        self.gender = ctk.CTkComboBox(
            form_frame,
            values=["Male", "Female"]
        )
        self.gender.pack(pady=10)

        self.phone = ctk.CTkEntry(form_frame, width=320, placeholder_text="Phone Number")
        self.phone.pack(pady=10)
        self.address = ctk.CTkEntry(form_frame, width=320, placeholder_text="Address")
        self.address.pack(pady=10)

        # Assign Doctor ComboBox
        ctk.CTkLabel(form_frame, text="Assign Doctor:", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(5, 0))
        self.doctor_combo = ctk.CTkComboBox(form_frame, width=320, values=[])
        self.doctor_combo.pack(pady=10)

        self.load_doctors()

        # =========================
        # Buttons
        # =========================

        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=25)

        ctk.CTkButton(button_frame, text="➕ Add", width=140, command=self.add_patient).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(button_frame, text="✏ Update", width=140, command=self.update_patient).grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkButton(button_frame, text="❌ Delete", width=140, command=self.delete_patient).grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkButton(button_frame, text="🧹 Clear", width=140, command=self.clear_field).grid(row=1, column=1, padx=5, pady=5)

        # =========================
        # Right Frame (Table)
        # =========================

        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        search_frame = ctk.CTkFrame(table_frame)
        search_frame.pack(fill="x", pady=10)

        self.search = ctk.CTkEntry(search_frame, width=300, placeholder_text="Search Patient...")
        self.search.pack(side="left", padx=10)

        ctk.CTkButton(search_frame, text="Search", command=self.search_patient).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Refresh", command=self.load_data).pack(side="left", padx=5)

        columns = (
            "ID",
            "Full Name",
            "Date of Birth",
            "Gender",
            "Phone",
            "Address"
        )

        # Style Treeview table (dark theme, but not too dark)
        style = ttk.Style()
        style.theme_use("clam")
        style.map("Treeview",
            background=[("selected", "#1F6AA5")],
            foreground=[("selected", "white")]
        )
        style.configure("Treeview.Heading",
            background="#1f1f1f",
            foreground="white",
            font=("Arial", 14, "bold"),
            relief="flat"
        )
        style.map("Treeview.Heading",
            background=[("active", "#2d2d2d")]
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=20
        )

        for col in columns:
            self.table.heading(col, text=col, anchor="center")
            self.table.column(col, width=150, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )

        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind row selection to load patient details into form fields
        self.table.bind("<<TreeviewSelect>>", self.load_patient)

        print("[DEBUG] PatientWindow initialized. Loading data automatically...")
        # Load patient records from database automatically on startup
        self.load_data()

    def load_doctors(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT WorkerID, FullName FROM Health_Workers WHERE Role = 'Doctor'")
            docs = cursor.fetchall()
            conn.close()
            
            doc_list = [f"Dr. {name} (ID: {wid})" for wid, name in docs]
            self.doctor_combo.configure(values=doc_list)
            if doc_list:
                self.doctor_combo.set(doc_list[0])
        except Exception as e:
            print(f"Error loading doctors: {e}")

    def load_data(self):
        """Load all patient records from MySQL and render inside Treeview."""
        print("[DEBUG] load_data() triggered...")
        for item in self.table.get_children():
            self.table.delete(item)
 
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT PatientID, FullName, DateOfBirth, Gender, PhoneNumber, Address FROM Patients ORDER BY PatientID DESC")
            rows = cursor.fetchall()
 
            print(f"[DEBUG] DB returned {len(rows)} patient rows.")
            for row in rows:
                cleaned_row = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned_row)
 
            # Update total patients badge if parent has it
            cursor.execute("SELECT COUNT(*) FROM Patients")
            total = cursor.fetchone()[0]
            self.total_patients_lbl.configure(text=f"👥 Total Patients: {total}")
 
            conn.close()
            print("[DEBUG] load_data() completed successfully and connection closed.")
        except Exception as e:
            print(f"[ERROR] load_data() failed: {e}")
            messagebox.showerror("Database Error", f"Failed to load patients:\n{e}")

    def add_patient(self):
        """Add a new patient record, create appointment, and insert pending consultation payment."""
        name = self.fullname.get().strip()
        dob = self.dob.get().strip()
        gender = self.gender.get()
        phone = self.phone.get().strip()
        address = self.address.get().strip()
        doc_val = self.doctor_combo.get()
 
        if not name or not dob or not gender:
            messagebox.showerror("Validation Error", "Full Name, Date of Birth, and Gender are required fields.")
            return
            
        if not doc_val:
            messagebox.showerror("Validation Error", "Please assign a doctor to the patient.")
            return
 
        try:
            # Extract doctor ID
            doctor_id = int(doc_val.split("ID: ")[1].replace(")", ""))
            
            # Fetch current receptionist worker ID if available in session
            import session
            receptionist_worker_id = 2
            if hasattr(session, "current_user") and session.current_user:
                receptionist_worker_id = session.current_user.get("worker_id", 2)
 
            conn = connect_db()
            cursor = conn.cursor()
            
            # 1. Insert patient
            query = """
                INSERT INTO Patients (FullName, DateOfBirth, Gender, PhoneNumber, Address)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, dob, gender, phone, address))
            patient_id = cursor.lastrowid
            
            # 2. Get consultation price from Hospital_Services
            cursor.execute("SELECT Price FROM Hospital_Services WHERE ServiceName = 'Consultation'")
            svc_row = cursor.fetchone()
            consult_price = float(svc_row[0]) if svc_row else 200.00
            
            # 3. Insert pending Payment record
            cursor.execute("""
                INSERT INTO Payment (PatientID, Amount, PaymentType, ServiceID, LabRequestID, DispensingID, PaymentMethod, PaymentDate, BilledBy)
                VALUES (%s, %s, 'Consultation', NULL, NULL, NULL, 'Pending', CURRENT_TIMESTAMP, %s)
            """, (patient_id, consult_price, receptionist_worker_id))
            
            # 4. Insert Appointments record
            cursor.execute("""
                INSERT INTO Appointments (PatientID, WorkerID, AppointmentDate, AppointmentTime, Status)
                VALUES (%s, %s, CURDATE(), CURRENT_TIME(), 'Pending')
            """, (patient_id, doctor_id))
 
            conn.commit()
            conn.close()
 
            # Write audit logs
            user_id = 1
            if hasattr(session, "current_user") and session.current_user:
                user_id = session.current_user.get("user_id", 1)
            from database import log_audit_action
            log_audit_action(user_id, f"Registered patient '{name}' (PatientID: {patient_id})")
            log_audit_action(user_id, f"Created appointment for PatientID: {patient_id} assigned to Doctor ID: {doctor_id}")
 
            messagebox.showinfo("Success", f"Patient registered successfully!\nAssigned to {doc_val.split(' (ID:')[0]}.")
            self.load_data()
            self.clear_field()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to register patient:\n{e}")

    def update_patient(self):
        """Update the selected patient record in the database."""
        if not self.selected_patient_id:
            messagebox.showwarning("Selection Warning", "Please select a patient from the list to update.")
            return

        name = self.fullname.get().strip()
        dob = self.dob.get().strip()
        gender = self.gender.get()
        phone = self.phone.get().strip()
        address = self.address.get().strip()

        if not name or not dob or not gender:
            messagebox.showerror("Validation Error", "Full Name, Date of Birth, and Gender are required fields.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                UPDATE Patients 
                SET FullName = %s, DateOfBirth = %s, Gender = %s, PhoneNumber = %s, Address = %s
                WHERE PatientID = %s
            """
            cursor.execute(query, (name, dob, gender, phone, address, self.selected_patient_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Patient updated successfully!")
            self.load_data()
            self.clear_field()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update patient:\n{e}")

    def delete_patient(self):
        """Delete the selected patient record from the database."""
        if not self.selected_patient_id:
            messagebox.showwarning("Selection Warning", "Please select a patient from the list to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this patient record?")
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = "DELETE FROM Patients WHERE PatientID = %s"
            cursor.execute(query, (self.selected_patient_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Patient deleted successfully!")
            self.load_data()
            self.clear_field()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete patient:\n{e}")

    def clear_field(self):
        """Clear all form entry fields and reset dropdown selections."""
        self.selected_patient_id = None
        self.fullname.delete(0, "end")
        self.dob.delete(0, "end")
        self.gender.set("Male")
        self.phone.delete(0, "end")
        self.address.delete(0, "end")
        self.search.delete(0, "end")
        self.table.selection_remove(self.table.selection())

    def load_patient(self, event=None):
        """Populate the form fields with data from the selected Treeview row."""
        selected_item = self.table.selection()
        if not selected_item:
            return

        row_values = self.table.item(selected_item[0], "values")
        if not row_values:
            return

        self.selected_patient_id = row_values[0]
        
        self.fullname.delete(0, "end")
        self.fullname.insert(0, row_values[1])

        self.dob.delete(0, "end")
        self.dob.insert(0, row_values[2])

        self.gender.set(row_values[3])

        self.phone.delete(0, "end")
        self.phone.insert(0, row_values[4])

        self.address.delete(0, "end")
        self.address.insert(0, row_values[5])

    def search_patient(self):
        """Search and display patients matching the query from the search entry."""
        search_query = self.search.get().strip()
        print(f"[DEBUG] search_patient() triggered. Query: '{search_query}'")
        if not search_query:
            print("[DEBUG] Empty search query, reloading all records.")
            self.load_data()
            return

        # Clear existing items in treeview
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            if hasattr(self.master, "doctor_worker_id"):
                query = """
                    SELECT DISTINCT p.PatientID, p.FullName, p.DateOfBirth, p.Gender, p.PhoneNumber, p.Address 
                    FROM Patients p
                    INNER JOIN Appointments a ON p.PatientID = a.PatientID
                    WHERE a.WorkerID = %s AND (p.PatientID LIKE %s OR p.FullName LIKE %s OR p.PhoneNumber LIKE %s OR p.Address LIKE %s)
                """
                like_val = f"%{search_query}%"
                cursor.execute(query, (self.master.doctor_worker_id, like_val, like_val, like_val, like_val))
            else:
                query = """
                    SELECT PatientID, FullName, DateOfBirth, Gender, PhoneNumber, Address 
                    FROM Patients
                    WHERE PatientID LIKE %s OR FullName LIKE %s OR PhoneNumber LIKE %s OR Address LIKE %s
                """
                like_val = f"%{search_query}%"
                cursor.execute(query, (like_val, like_val, like_val, like_val))
                
            rows = cursor.fetchall()
            print(f"[DEBUG] Search executed. Found {len(rows)} matching records.")

            for row in rows:
                cleaned_row = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned_row)

            # Update the total patients label
            self.total_patients_lbl.configure(text=f"👥 Total Patients: {len(rows)}")

            conn.close()
            print("[DEBUG] search_patient() completed successfully and connection closed.")
        except Exception as e:
            print(f"[ERROR] search_patient() failed: {e}")
            messagebox.showerror("Database Error", f"Failed to search patients:\n{e}")