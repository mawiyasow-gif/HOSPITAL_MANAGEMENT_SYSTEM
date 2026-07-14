import customtkinter as ctk
from tkinter import ttk, messagebox
from database import connect_db
from datetime import datetime
import session

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class DiagnosisWindow(ctk.CTkToplevel):
    """Diagnosis Management Panel (View/Edit) for Clinical Records."""

    def __init__(self, parent):
        super().__init__(parent)
        self.master = parent

        self.title("Diagnosis Management")
        self.geometry("1400x800")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.selected_diagnosis_id = None
        self.user_id = 1
        if hasattr(session, "current_user") and session.current_user:
            self.user_id = session.current_user.get("user_id", 1)

        # Back Button
        back_btn = ctk.CTkButton(self, text="⬅ Back", width=100, command=self.destroy)
        back_btn.place(x=20, y=20)

        # Title
        ctk.CTkLabel(self, text="🩺 Diagnosis Catalog", font=("Arial", 30, "bold")).pack(pady=20)

        # Main Layout
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Left Panel (Edit Form)
        form_frame = ctk.CTkFrame(main_frame, width=420)
        form_frame.pack(side="left", fill="y", padx=15, pady=15)
        form_frame.pack_propagate(False)

        ctk.CTkLabel(form_frame, text="Diagnosis Details", font=("Arial", 22, "bold")).pack(pady=20)

        # Patient Combo
        ctk.CTkLabel(form_frame, text="Select Patient:", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(10, 2))
        self.patient_combo = ctk.CTkComboBox(form_frame, width=320, values=[])
        self.patient_combo.pack(pady=5)
        self.load_patients()

        # Doctor Combo
        ctk.CTkLabel(form_frame, text="Select Doctor:", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(10, 2))
        self.doctor_combo = ctk.CTkComboBox(form_frame, width=320, values=[])
        self.doctor_combo.pack(pady=5)
        self.load_doctors()

        # Date Entry
        ctk.CTkLabel(form_frame, text="Diagnosis Date (YYYY-MM-DD):", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(10, 2))
        self.date_entry = ctk.CTkEntry(form_frame, width=320)
        self.date_entry.pack(pady=5)

        # Details Textbox
        ctk.CTkLabel(form_frame, text="Clinical Findings / Details:", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(10, 2))
        self.details_textbox = ctk.CTkTextbox(form_frame, width=320, height=120)
        self.details_textbox.pack(pady=5)

        # Action Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="➕ Add", command=self.add_diagnosis, width=145).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="✏ Update", command=self.update_diagnosis, width=145).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="❌ Delete", command=self.delete_diagnosis, fg_color="red", hover_color="#b71c1c", width=145).grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="🧹 Clear", command=self.clear_fields, width=145).grid(row=1, column=1, padx=5, pady=5)

        # Right Panel (List)
        self.table_frame = ctk.CTkFrame(main_frame)
        self.table_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        # Search Bar
        search_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=15, pady=10)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by Patient or Findings...", width=300)
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.search_diagnosis)

        ctk.CTkButton(search_frame, text="Search", command=self.search_diagnosis, width=100).pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="Reset", command=self.refresh_table, width=100).pack(side="left")

        # Treeview Setup
        container = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=15, pady=5)

        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side="right", fill="y")

        columns = ("ID", "Patient Name", "Doctor Name", "Date", "Diagnosis Details")
        self.table = ttk.Treeview(container, columns=columns, show="headings", yscrollcommand=scrollbar.set, height=18)
        for col in columns:
            self.table.heading(col, text=col, anchor="w")
            self.table.column(col, anchor="w", width=130)
        self.table.column("ID", width=50, anchor="center")
        self.table.column("Diagnosis Details", width=300)

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.table.yview)

        self.table.bind("<<TreeviewSelect>>", self.on_row_selected)

        self.load_diagnoses()
        self.clear_fields()

    def extract_id(self, combo_value):
        if not combo_value:
            return None
        try:
            return int(combo_value.split("ID: ")[1].replace(")", ""))
        except:
            return None

    def load_patients(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT PatientID, FullName FROM Patients ORDER BY PatientID DESC")
            pats = [f"{name} (ID: {pid})" for pid, name in cursor.fetchall()]
            self.patient_combo.configure(values=pats)
            if pats:
                self.patient_combo.set(pats[0])
            conn.close()
        except Exception as e:
            print(f"Error loading patients: {e}")

    def load_doctors(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT WorkerID, FullName FROM Health_Workers WHERE Role = 'Doctor'")
            docs = [f"Dr. {name} (ID: {wid})" for wid, name in cursor.fetchall()]
            self.doctor_combo.configure(values=docs)
            if docs:
                self.doctor_combo.set(docs[0])
            conn.close()
        except Exception as e:
            print(f"Error loading doctors: {e}")

    def load_diagnoses(self):
        for item in self.table.get_children():
            self.table.delete(item)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.DiagnosisID, p.FullName, hw.FullName, DATE(d.DiagnosisDate), d.DiagnosisDetails
                FROM Diagnosis d
                LEFT JOIN Patients p ON d.PatientID = p.PatientID
                LEFT JOIN Health_Workers hw ON d.DoctorID = hw.WorkerID
                ORDER BY d.DiagnosisID DESC
            """)
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error loading diagnoses: {e}")

    def on_row_selected(self, event):
        selected = self.table.selection()
        if not selected:
            return
        row = self.table.item(selected[0], "values")
        self.selected_diagnosis_id = int(row[0])

        # Match patient combo
        pat_vals = self.patient_combo.cget("values")
        for p in pat_vals:
            if row[1] in p:
                self.patient_combo.set(p)
                break

        # Match doctor combo
        doc_vals = self.doctor_combo.cget("values")
        for d in doc_vals:
            if row[2] in d:
                self.doctor_combo.set(d)
                break

        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, row[3])

        self.details_textbox.delete("1.0", "end")
        self.details_textbox.insert("1.0", row[4])

    def clear_fields(self):
        self.selected_diagnosis_id = None
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.details_textbox.delete("1.0", "end")
        self.table.selection_remove(self.table.selection())

    def add_diagnosis(self):
        patient_id = self.extract_id(self.patient_combo.get())
        doctor_id = self.extract_id(self.doctor_combo.get())
        diag_date = self.date_entry.get().strip()
        details = self.details_textbox.get("1.0", "end").strip()

        if not patient_id or not doctor_id or not details:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            datetime.strptime(diag_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Use YYYY-MM-DD date format.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Diagnosis (AppointmentID, PatientID, DoctorID, DiagnosisDetails, DiagnosisDate, LabRequestID)
                VALUES (NULL, %s, %s, %s, %s, NULL)
            """, (patient_id, doctor_id, details, diag_date))
            diag_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # Write audit log
            from database import log_audit_action
            log_audit_action(self.user_id, f"Recorded diagnosis (DiagnosisID: {diag_id}) for PatientID: {patient_id}")

            messagebox.showinfo("Success", "Diagnosis added successfully!")
            self.load_diagnoses()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add diagnosis:\n{e}")

    def update_diagnosis(self):
        if not self.selected_diagnosis_id:
            messagebox.showwarning("Warning", "Select a diagnosis record to update.")
            return

        patient_id = self.extract_id(self.patient_combo.get())
        doctor_id = self.extract_id(self.doctor_combo.get())
        diag_date = self.date_entry.get().strip()
        details = self.details_textbox.get("1.0", "end").strip()

        if not patient_id or not doctor_id or not details:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            datetime.strptime(diag_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Use YYYY-MM-DD date format.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Diagnosis
                SET PatientID = %s, DoctorID = %s, DiagnosisDetails = %s, DiagnosisDate = %s
                WHERE DiagnosisID = %s
            """, (patient_id, doctor_id, details, diag_date, self.selected_diagnosis_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Diagnosis updated successfully!")
            self.load_diagnoses()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update diagnosis:\n{e}")

    def delete_diagnosis(self):
        if not self.selected_diagnosis_id:
            messagebox.showwarning("Warning", "Select a diagnosis record to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this diagnosis record?")
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Diagnosis WHERE DiagnosisID = %s", (self.selected_diagnosis_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Diagnosis deleted successfully!")
            self.load_diagnoses()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete diagnosis:\n{e}")

    def search_diagnosis(self, event=None):
        q = self.search_entry.get().strip()
        if not q:
            self.load_diagnoses()
            return
        for item in self.table.get_children():
            self.table.delete(item)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.DiagnosisID, p.FullName, hw.FullName, DATE(d.DiagnosisDate), d.DiagnosisDetails
                FROM Diagnosis d
                LEFT JOIN Patients p ON d.PatientID = p.PatientID
                LEFT JOIN Health_Workers hw ON d.DoctorID = hw.WorkerID
                WHERE p.FullName LIKE %s OR d.DiagnosisDetails LIKE %s
                ORDER BY d.DiagnosisID DESC
            """, (f"%{q}%", f"%{q}%"))
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error searching diagnoses: {e}")

    def refresh_table(self):
        self.search_entry.delete(0, "end")
        self.load_diagnoses()
        self.clear_fields()


if __name__ == "__main__":
    class TestApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.geometry("1400x800")
            DiagnosisWindow(self)

    app = TestApp()
    app.mainloop()
