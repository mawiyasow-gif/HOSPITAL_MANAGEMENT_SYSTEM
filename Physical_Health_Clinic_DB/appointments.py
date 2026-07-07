import customtkinter as ctk
from tkinter import ttk, messagebox
from database import connect_db

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class AppointmentWindow(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Appointment Management")
        self.geometry("1500x850")
        self.resizable(True, True)

        # Track selected appointment ID for updates/deletes
        self.selected_appointment_id = None

        # Back Button at top-left
        back_btn = ctk.CTkButton(
            self,
            text="⬅ Back",
            width=100,
            command=self.destroy
        )
        back_btn.place(x=20, y=20)

        # =========================
        # Title
        # =========================

        title = ctk.CTkLabel(
            self,
            text="📅 Appointment Management",
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

        ctk.CTkLabel(form_frame, text="Appointment Information",
                     font=("Arial", 22, "bold")).pack(pady=20)

        # Patient Combo
        ctk.CTkLabel(form_frame, text="Select Patient:", font=("Arial", 14)).pack(pady=(10, 2), anchor="w", padx=50)
        self.patient_combo = ctk.CTkComboBox(form_frame, width=320, values=[])
        self.patient_combo.pack(pady=5)

        # Worker Combo
        ctk.CTkLabel(form_frame, text="Select Health Worker:", font=("Arial", 14)).pack(pady=(10, 2), anchor="w", padx=50)
        self.worker_combo = ctk.CTkComboBox(form_frame, width=320, values=[])
        self.worker_combo.pack(pady=5)

        # Appointment Date
        ctk.CTkLabel(form_frame, text="Date (YYYY-MM-DD):", font=("Arial", 14)).pack(pady=(10, 2), anchor="w", padx=50)
        self.date_entry = ctk.CTkEntry(form_frame, width=320, placeholder_text="YYYY-MM-DD")
        self.date_entry.pack(pady=5)

        # Appointment Time
        ctk.CTkLabel(form_frame, text="Time (HH:MM:SS):", font=("Arial", 14)).pack(pady=(10, 2), anchor="w", padx=50)
        self.time_entry = ctk.CTkEntry(form_frame, width=320, placeholder_text="HH:MM:SS")
        self.time_entry.pack(pady=5)

        # Status Combo
        ctk.CTkLabel(form_frame, text="Status:", font=("Arial", 14)).pack(pady=(10, 2), anchor="w", padx=50)
        self.status_combo = ctk.CTkComboBox(
            form_frame,
            width=320,
            values=["Scheduled", "Completed", "Cancelled", "Pending"]
        )
        self.status_combo.set("Scheduled")
        self.status_combo.pack(pady=5)

        # =========================
        # Buttons
        # =========================

        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=25)

        ctk.CTkButton(button_frame, text="➕ Add Appointment", width=140, command=self.add_appointment).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(button_frame, text="✏ Update", width=140, command=self.update_appointment).grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkButton(button_frame, text="❌ Delete", width=140, command=self.delete_appointment).grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkButton(button_frame, text="🧹 Clear", width=140, command=self.clear_fields).grid(row=1, column=1, padx=5, pady=5)

        # =========================
        # Right Frame (Table)
        # =========================

        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        search_frame = ctk.CTkFrame(table_frame)
        search_frame.pack(fill="x", pady=10)

        self.search = ctk.CTkEntry(search_frame, width=300, placeholder_text="Search Appointment...")
        self.search.pack(side="left", padx=10)

        ctk.CTkButton(search_frame, text="Search", command=self.search_appointment).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Refresh", command=self.refresh_table).pack(side="left", padx=5)

        columns = (
            "Appointment ID",
            "Patient",
            "Health Worker",
            "Date",
            "Time",
            "Status"
        )

        # Style Treeview table (dark theme, but not too dark)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            rowheight=35,
            font=("Arial", 13)
        )
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

        # Bind row selection to load appointment details into form fields
        self.table.bind("<<TreeviewSelect>>", self.select_appointment)

        # Load patients and workers into ComboBoxes
        self.load_patients()
        self.load_workers()

        # Load appointment records from database automatically on startup
        self.load_appointments()

    def extract_id(self, combo_val):
        """Helper to extract integer ID from ComboBox string (e.g. '1 - Alhaji Mawiya')."""
        if not combo_val:
            return None
        try:
            parts = combo_val.split(" - ")
            return int(parts[0])
        except Exception:
            return None

    def load_patients(self):
        """Load patients from database and populate the Patient ComboBox."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = "SELECT PatientID, FullName FROM Patients"
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

    def load_workers(self):
        """Load health workers from database and populate the Worker ComboBox."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = "SELECT WorkerID, FullName FROM Health_Workers"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            worker_list = []
            for row in rows:
                worker_list.append(f"{row[0]} - {row[1]}")
                
            self.worker_combo.configure(values=worker_list)
            if worker_list:
                self.worker_combo.set(worker_list[0])
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load health workers:\n{e}")

    def load_appointments(self):
        """Fetch all appointment records from the database and populate the treeview."""
        # Clear existing items in treeview
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            if hasattr(self.master, 'doctor_worker_id'):
                query = """
                    SELECT 
                        a.AppointmentID, 
                        COALESCE(CONCAT(p.PatientID, ' - ', p.FullName), 'Unknown Patient'),
                        COALESCE(CONCAT(w.WorkerID, ' - ', w.FullName), 'Unknown Worker'),
                        a.AppointmentDate, 
                        a.AppointmentTime, 
                        a.Status 
                    FROM Appointments a
                    LEFT JOIN Patients p ON a.PatientID = p.PatientID
                    LEFT JOIN Health_Workers w ON a.WorkerID = w.WorkerID
                    WHERE a.WorkerID = %s
                """
                cursor.execute(query, (self.master.doctor_worker_id,))
            else:
                query = """
                    SELECT 
                        a.AppointmentID, 
                        COALESCE(CONCAT(p.PatientID, ' - ', p.FullName), 'Unknown Patient'),
                        COALESCE(CONCAT(w.WorkerID, ' - ', w.FullName), 'Unknown Worker'),
                        a.AppointmentDate, 
                        a.AppointmentTime, 
                        a.Status 
                    FROM Appointments a
                    LEFT JOIN Patients p ON a.PatientID = p.PatientID
                    LEFT JOIN Health_Workers w ON a.WorkerID = w.WorkerID
                """
                cursor.execute(query)
                
            rows = cursor.fetchall()

            for row in rows:
                cleaned_row = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned_row)

            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load appointments:\n{e}")

    def add_appointment(self):
        """Add a new appointment to the database."""
        patient_val = self.patient_combo.get()
        worker_val = self.worker_combo.get()
        app_date = self.date_entry.get().strip()
        app_time = self.time_entry.get().strip()
        status = self.status_combo.get()

        patient_id = self.extract_id(patient_val)
        worker_id = self.extract_id(worker_val)

        if not patient_id or not worker_id or not app_date or not app_time:
            messagebox.showerror("Validation Error", "All fields are required.")
            return

        # Map "Scheduled" status to "Pending" to comply with DB Enum constraints
        db_status = "Pending" if status == "Scheduled" else status

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                INSERT INTO Appointments (PatientID, WorkerID, AppointmentDate, AppointmentTime, Status)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (patient_id, worker_id, app_date, app_time, db_status))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Appointment added successfully!")
            self.load_appointments()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add appointment:\n{e}")

    def update_appointment(self):
        """Update the selected appointment in the database."""
        if not self.selected_appointment_id:
            messagebox.showwarning("Selection Warning", "Please select an appointment from the list to update.")
            return

        patient_val = self.patient_combo.get()
        worker_val = self.worker_combo.get()
        app_date = self.date_entry.get().strip()
        app_time = self.time_entry.get().strip()
        status = self.status_combo.get()

        patient_id = self.extract_id(patient_val)
        worker_id = self.extract_id(worker_val)

        if not patient_id or not worker_id or not app_date or not app_time:
            messagebox.showerror("Validation Error", "All fields are required.")
            return

        # Map "Scheduled" to "Pending" for DB compatibility
        db_status = "Pending" if status == "Scheduled" else status

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                UPDATE Appointments 
                SET PatientID = %s, WorkerID = %s, AppointmentDate = %s, AppointmentTime = %s, Status = %s
                WHERE AppointmentID = %s
            """
            cursor.execute(query, (patient_id, worker_id, app_date, app_time, db_status, self.selected_appointment_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Appointment updated successfully!")
            self.load_appointments()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update appointment:\n{e}")

    def delete_appointment(self):
        """Delete the selected appointment from the database."""
        if not self.selected_appointment_id:
            messagebox.showwarning("Selection Warning", "Please select an appointment from the list to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this appointment?")
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = "DELETE FROM Appointments WHERE AppointmentID = %s"
            cursor.execute(query, (self.selected_appointment_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Appointment deleted successfully!")
            self.load_appointments()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete appointment:\n{e}")

    def clear_fields(self):
        """Clear all form fields and reset selections."""
        self.selected_appointment_id = None
        self.date_entry.delete(0, "end")
        self.time_entry.delete(0, "end")
        self.status_combo.set("Scheduled")
        self.search.delete(0, "end")
        self.table.selection_remove(self.table.selection())

        # Reset combos
        if self.patient_combo.cget("values"):
            self.patient_combo.set(self.patient_combo.cget("values")[0])
        if self.worker_combo.cget("values"):
            self.worker_combo.set(self.worker_combo.cget("values")[0])

    def select_appointment(self, event=None):
        """Populate the form fields when an item in the treeview is clicked."""
        selected_item = self.table.selection()
        if not selected_item:
            return

        row_values = self.table.item(selected_item[0], "values")
        if not row_values:
            return

        self.selected_appointment_id = row_values[0]
        
        # Select patient in combo
        patient_info = row_values[1]
        p_values = self.patient_combo.cget("values")
        if patient_info in p_values:
            self.patient_combo.set(patient_info)
        else:
            for val in p_values:
                if val.startswith(patient_info.split(" - ")[0] + " "):
                    self.patient_combo.set(val)
                    break

        # Select worker in combo
        worker_info = row_values[2]
        w_values = self.worker_combo.cget("values")
        if worker_info in w_values:
            self.worker_combo.set(worker_info)
        else:
            for val in w_values:
                if val.startswith(worker_info.split(" - ")[0] + " "):
                    self.worker_combo.set(val)
                    break

        # Set date and time
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, row_values[3])

        self.time_entry.delete(0, "end")
        self.time_entry.insert(0, row_values[4])

        # Set status
        status_val = row_values[5]
        # Map "Pending" to "Scheduled" if needed, but since we support Pending in ComboBox we can set directly
        self.status_combo.set(status_val)

    def search_appointment(self):
        """Search and display appointments matching the query."""
        search_query = self.search.get().strip()
        if not search_query:
            self.load_appointments()
            return

        # Clear existing items in treeview
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            if hasattr(self.master, 'doctor_worker_id'):
                query = """
                    SELECT 
                        a.AppointmentID, 
                        COALESCE(CONCAT(p.PatientID, ' - ', p.FullName), 'Unknown Patient'),
                        COALESCE(CONCAT(w.WorkerID, ' - ', w.FullName), 'Unknown Worker'),
                        a.AppointmentDate, 
                        a.AppointmentTime, 
                        a.Status 
                    FROM Appointments a
                    LEFT JOIN Patients p ON a.PatientID = p.PatientID
                    LEFT JOIN Health_Workers w ON a.WorkerID = w.WorkerID
                    WHERE a.WorkerID = %s AND (a.AppointmentID LIKE %s 
                       OR p.FullName LIKE %s 
                       OR w.FullName LIKE %s 
                       OR a.AppointmentDate LIKE %s 
                       OR a.Status LIKE %s)
                """
                like_val = f"%{search_query}%"
                cursor.execute(query, (self.master.doctor_worker_id, like_val, like_val, like_val, like_val, like_val))
            else:
                query = """
                    SELECT 
                        a.AppointmentID, 
                        COALESCE(CONCAT(p.PatientID, ' - ', p.FullName), 'Unknown Patient'),
                        COALESCE(CONCAT(w.WorkerID, ' - ', w.FullName), 'Unknown Worker'),
                        a.AppointmentDate, 
                        a.AppointmentTime, 
                        a.Status 
                    FROM Appointments a
                    LEFT JOIN Patients p ON a.PatientID = p.PatientID
                    LEFT JOIN Health_Workers w ON a.WorkerID = w.WorkerID
                    WHERE a.AppointmentID LIKE %s 
                       OR p.FullName LIKE %s 
                       OR w.FullName LIKE %s 
                       OR a.AppointmentDate LIKE %s 
                       OR a.Status LIKE %s
                """
                like_val = f"%{search_query}%"
                cursor.execute(query, (like_val, like_val, like_val, like_val, like_val))
                
            rows = cursor.fetchall()

            for row in rows:
                cleaned_row = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned_row)

            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to search appointments:\n{e}")

    def refresh_table(self):
        """Reload appointments data from database."""
        self.load_appointments()


if __name__ == "__main__":
    class TestApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.geometry("1500x850")
            AppointmentWindow(self)
            
    app = TestApp()
    app.mainloop()
