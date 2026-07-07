import customtkinter as ctk
from tkinter import ttk, messagebox
from database import connect_db

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class TreatmentWindow(ctk.CTkToplevel):
    """Treatment Management Window for Physical Health Clinic Record System."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Treatment Management")
        self.geometry("1500x850")
        self.resizable(True, True)

        # Track selected treatment ID for updates and deletes
        self.selected_treatment_id = None

        # ==============================
        # Back Button (top-left corner)
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
            text="💊 Treatment Management",
            font=("Arial", 30, "bold")
        )
        title.pack(pady=20)

        # ==============================
        # Main Frame
        # ==============================

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ==============================
        # Left Panel (Treatment Form)
        # ==============================

        form_frame = ctk.CTkFrame(main_frame, width=420)
        form_frame.pack(side="left", fill="y", padx=15, pady=15)

        ctk.CTkLabel(
            form_frame,
            text="Treatment Information",
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

        # Health Worker ComboBox
        ctk.CTkLabel(
            form_frame,
            text="Select Health Worker:",
            font=("Arial", 14)
        ).pack(pady=(10, 2), anchor="w", padx=50)

        self.worker_combo = ctk.CTkComboBox(form_frame, width=320, values=[])
        self.worker_combo.pack(pady=5)

        # Treatment Name Entry
        ctk.CTkLabel(
            form_frame,
            text="Treatment Name:",
            font=("Arial", 14)
        ).pack(pady=(10, 2), anchor="w", padx=50)

        self.treatment_name_entry = ctk.CTkEntry(
            form_frame,
            width=320,
            placeholder_text="e.g., Paracetamol"
        )
        self.treatment_name_entry.pack(pady=5)

        # Dosage Entry
        ctk.CTkLabel(
            form_frame,
            text="Dosage:",
            font=("Arial", 14)
        ).pack(pady=(10, 2), anchor="w", padx=50)

        self.dosage_entry = ctk.CTkEntry(
            form_frame,
            width=320,
            placeholder_text="e.g., 500mg Every 8 Hours"
        )
        self.dosage_entry.pack(pady=5)

        # Duration Entry
        ctk.CTkLabel(
            form_frame,
            text="Duration:",
            font=("Arial", 14)
        ).pack(pady=(10, 2), anchor="w", padx=50)

        self.duration_entry = ctk.CTkEntry(
            form_frame,
            width=320,
            placeholder_text="e.g., 5 Days"
        )
        self.duration_entry.pack(pady=5)

        # ==============================
        # Action Buttons
        # ==============================

        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=25)

        ctk.CTkButton(
            button_frame,
            text="➕ Add Treatment",
            width=140,
            command=self.add_treatment
        ).grid(row=0, column=0, padx=5, pady=5)

        ctk.CTkButton(
            button_frame,
            text="✏ Update",
            width=140,
            command=self.update_treatment
        ).grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkButton(
            button_frame,
            text="❌ Delete",
            width=140,
            command=self.delete_treatment
        ).grid(row=1, column=0, padx=5, pady=5)

        ctk.CTkButton(
            button_frame,
            text="🧹 Clear",
            width=140,
            command=self.clear_fields
        ).grid(row=1, column=1, padx=5, pady=5)

        # ==============================
        # Right Panel (Treeview Table)
        # ==============================

        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        # Search bar at top of right panel
        search_frame = ctk.CTkFrame(table_frame)
        search_frame.pack(fill="x", pady=10)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=300,
            placeholder_text="Search Treatment..."
        )
        self.search_entry.pack(side="left", padx=10)

        ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_treatment
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="Refresh",
            command=self.refresh_table
        ).pack(side="left", padx=5)

        # Treeview columns
        columns = (
            "Treatment ID",
            "Patient",
            "Health Worker",
            "Treatment Name",
            "Dosage",
            "Duration"
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
            self.table.column(col, width=150, anchor="center")

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
        self.table.bind("<<TreeviewSelect>>", self.select_treatment)

        # Load initial data into ComboBoxes and Treeview
        self.load_patients()
        self.load_workers()
        self.load_treatments()

    # ==============================
    # Helper Methods
    # ==============================

    def extract_id(self, combo_value):
        """Extract the integer ID from a ComboBox display string like '1 - Alhaji Mawiya Sow'."""
        if not combo_value:
            return None
        try:
            parts = combo_value.split(" - ")
            return int(parts[0])
        except Exception:
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

    def load_workers(self):
        """Load all health workers from the Health_Workers table into the Worker ComboBox."""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = "SELECT WorkerID, FullName FROM Health_Workers ORDER BY WorkerID"
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

    def load_treatments(self):
        """Fetch all treatment records from the database and populate the Treeview."""
        # Clear existing items in the treeview
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            if hasattr(self.master, 'doctor_worker_id'):
                query = """
                    SELECT 
                        t.TreatmentID,
                        COALESCE(CONCAT(p.PatientID, ' - ', p.FullName), 'Unknown Patient'),
                        COALESCE(CONCAT(w.WorkerID, ' - ', w.FullName), 'Unknown Worker'),
                        t.TreatmentName,
                        t.Dosage,
                        t.Duration
                    FROM Treatment t
                    LEFT JOIN Patients p ON t.PatientID = p.PatientID
                    LEFT JOIN Health_Workers w ON t.WorkerID = w.WorkerID
                    WHERE t.WorkerID = %s
                    ORDER BY t.TreatmentID DESC
                """
                cursor.execute(query, (self.master.doctor_worker_id,))
            else:
                query = """
                    SELECT 
                        t.TreatmentID,
                        COALESCE(CONCAT(p.PatientID, ' - ', p.FullName), 'Unknown Patient'),
                        COALESCE(CONCAT(w.WorkerID, ' - ', w.FullName), 'Unknown Worker'),
                        t.TreatmentName,
                        t.Dosage,
                        t.Duration
                    FROM Treatment t
                    LEFT JOIN Patients p ON t.PatientID = p.PatientID
                    LEFT JOIN Health_Workers w ON t.WorkerID = w.WorkerID
                    ORDER BY t.TreatmentID DESC
                """
                cursor.execute(query)
                
            rows = cursor.fetchall()

            for row in rows:
                cleaned_row = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned_row)

            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load treatments:\n{e}")

    # ==============================
    # CRUD Operations
    # ==============================

    def add_treatment(self):
        """Validate all fields and save a new treatment record to MySQL."""
        patient_val = self.patient_combo.get()
        worker_val = self.worker_combo.get()
        treatment_name = self.treatment_name_entry.get().strip()
        dosage = self.dosage_entry.get().strip()
        duration = self.duration_entry.get().strip()

        # Extract IDs from ComboBox display strings
        patient_id = self.extract_id(patient_val)
        worker_id = self.extract_id(worker_val)

        # Validate all required fields are filled
        if not patient_id:
            messagebox.showerror("Validation Error", "Please select a valid patient.")
            return
        if not worker_id:
            messagebox.showerror("Validation Error", "Please select a valid health worker.")
            return
        if not treatment_name:
            messagebox.showerror("Validation Error", "Please enter the treatment name.")
            return
        if not dosage:
            messagebox.showerror("Validation Error", "Please enter the dosage.")
            return
        if not duration:
            messagebox.showerror("Validation Error", "Please enter the duration.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                INSERT INTO Treatment (PatientID, WorkerID, TreatmentName, Dosage, Duration)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (patient_id, worker_id, treatment_name, dosage, duration))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Treatment added successfully!")
            self.load_treatments()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add treatment:\n{e}")

    def update_treatment(self):
        """Update the selected treatment record in the database."""
        if not self.selected_treatment_id:
            messagebox.showwarning(
                "Selection Warning",
                "Please select a treatment from the table to update."
            )
            return

        patient_val = self.patient_combo.get()
        worker_val = self.worker_combo.get()
        treatment_name = self.treatment_name_entry.get().strip()
        dosage = self.dosage_entry.get().strip()
        duration = self.duration_entry.get().strip()

        patient_id = self.extract_id(patient_val)
        worker_id = self.extract_id(worker_val)

        # Validate all required fields
        if not patient_id:
            messagebox.showerror("Validation Error", "Please select a valid patient.")
            return
        if not worker_id:
            messagebox.showerror("Validation Error", "Please select a valid health worker.")
            return
        if not treatment_name:
            messagebox.showerror("Validation Error", "Please enter the treatment name.")
            return
        if not dosage:
            messagebox.showerror("Validation Error", "Please enter the dosage.")
            return
        if not duration:
            messagebox.showerror("Validation Error", "Please enter the duration.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                UPDATE Treatment
                SET PatientID = %s, WorkerID = %s, TreatmentName = %s, Dosage = %s, Duration = %s
                WHERE TreatmentID = %s
            """
            cursor.execute(query, (
                patient_id, worker_id, treatment_name, dosage, duration,
                self.selected_treatment_id
            ))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Treatment updated successfully!")
            self.load_treatments()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update treatment:\n{e}")

    def delete_treatment(self):
        """Delete the selected treatment record after user confirmation."""
        if not self.selected_treatment_id:
            messagebox.showwarning(
                "Selection Warning",
                "Please select a treatment from the table to delete."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this treatment record?"
        )
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = "DELETE FROM Treatment WHERE TreatmentID = %s"
            cursor.execute(query, (self.selected_treatment_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Treatment deleted successfully!")
            self.load_treatments()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete treatment:\n{e}")

    # ==============================
    # Search, Select, Clear, Refresh
    # ==============================

    def search_treatment(self):
        """Search treatments by Patient Name, Health Worker Name, or Treatment Name.
        Displays only matching records in the Treeview."""
        search_query = self.search_entry.get().strip()
        if not search_query:
            self.load_treatments()
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
                        t.TreatmentID,
                        COALESCE(CONCAT(p.PatientID, ' - ', p.FullName), 'Unknown Patient'),
                        COALESCE(CONCAT(w.WorkerID, ' - ', w.FullName), 'Unknown Worker'),
                        t.TreatmentName,
                        t.Dosage,
                        t.Duration
                    FROM Treatment t
                    LEFT JOIN Patients p ON t.PatientID = p.PatientID
                    LEFT JOIN Health_Workers w ON t.WorkerID = w.WorkerID
                    WHERE t.WorkerID = %s AND (p.FullName LIKE %s
                       OR w.FullName LIKE %s
                       OR t.TreatmentName LIKE %s)
                    ORDER BY t.TreatmentID DESC
                """
                like_val = f"%{search_query}%"
                cursor.execute(query, (self.master.doctor_worker_id, like_val, like_val, like_val))
            else:
                query = """
                    SELECT 
                        t.TreatmentID,
                        COALESCE(CONCAT(p.PatientID, ' - ', p.FullName), 'Unknown Patient'),
                        COALESCE(CONCAT(w.WorkerID, ' - ', w.FullName), 'Unknown Worker'),
                        t.TreatmentName,
                        t.Dosage,
                        t.Duration
                    FROM Treatment t
                    LEFT JOIN Patients p ON t.PatientID = p.PatientID
                    LEFT JOIN Health_Workers w ON t.WorkerID = w.WorkerID
                    WHERE p.FullName LIKE %s
                       OR w.FullName LIKE %s
                       OR t.TreatmentName LIKE %s
                    ORDER BY t.TreatmentID DESC
                """
                like_val = f"%{search_query}%"
                cursor.execute(query, (like_val, like_val, like_val))
                
            rows = cursor.fetchall()

            for row in rows:
                cleaned_row = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned_row)

            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to search treatments:\n{e}")

    def select_treatment(self, event=None):
        """When a row in the Treeview is clicked, load all its data into the form fields."""
        selected_item = self.table.selection()
        if not selected_item:
            return

        row_values = self.table.item(selected_item[0], "values")
        if not row_values:
            return

        # Store the selected treatment ID
        self.selected_treatment_id = row_values[0]

        # Set the Patient ComboBox to match the selected row
        patient_info = row_values[1]
        patient_values = self.patient_combo.cget("values")
        if patient_info in patient_values:
            self.patient_combo.set(patient_info)
        else:
            for val in patient_values:
                if val.startswith(patient_info.split(" - ")[0] + " "):
                    self.patient_combo.set(val)
                    break

        # Set the Health Worker ComboBox to match the selected row
        worker_info = row_values[2]
        worker_values = self.worker_combo.cget("values")
        if worker_info in worker_values:
            self.worker_combo.set(worker_info)
        else:
            for val in worker_values:
                if val.startswith(worker_info.split(" - ")[0] + " "):
                    self.worker_combo.set(val)
                    break

        # Set the Treatment Name
        self.treatment_name_entry.delete(0, "end")
        self.treatment_name_entry.insert(0, row_values[3])

        # Set the Dosage
        self.dosage_entry.delete(0, "end")
        self.dosage_entry.insert(0, row_values[4])

        # Set the Duration
        self.duration_entry.delete(0, "end")
        self.duration_entry.insert(0, row_values[5])

    def clear_fields(self):
        """Clear all form fields and reset the ComboBoxes and Treeview selection."""
        self.selected_treatment_id = None

        # Clear the Treatment Name field
        self.treatment_name_entry.delete(0, "end")

        # Clear the Dosage field
        self.dosage_entry.delete(0, "end")

        # Clear the Duration field
        self.duration_entry.delete(0, "end")

        # Clear the search entry
        self.search_entry.delete(0, "end")

        # Remove Treeview selection highlight
        self.table.selection_remove(self.table.selection())

        # Reset the Patient ComboBox to the first value
        patient_values = self.patient_combo.cget("values")
        if patient_values:
            self.patient_combo.set(patient_values[0])

        # Reset the Health Worker ComboBox to the first value
        worker_values = self.worker_combo.cget("values")
        if worker_values:
            self.worker_combo.set(worker_values[0])

    def refresh_table(self):
        """Reload all treatment records from the database into the Treeview.
        Also resets the Patient and Health Worker ComboBoxes."""
        self.load_patients()
        self.load_workers()
        self.load_treatments()


if __name__ == "__main__":
    class TestApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.geometry("1500x850")
            TreatmentWindow(self)

    app = TestApp()
    app.mainloop()
