import customtkinter as ctk
from tkinter import ttk, messagebox
from database import connect_db
from datetime import datetime, timedelta
import session

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class TreatmentWindow(ctk.CTkToplevel):
    """Treatment Management Panel (View/Edit) for Clinical Records."""

    def __init__(self, parent):
        super().__init__(parent)
        self.master = parent

        self.title("Treatment Management")
        self.geometry("1400x800")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.selected_treatment_id = None
        self.user_id = 1
        if hasattr(session, "current_user") and session.current_user:
            self.user_id = session.current_user.get("user_id", 1)

        # Back Button
        back_btn = ctk.CTkButton(self, text="⬅ Back", width=100, command=self.destroy)
        back_btn.place(x=20, y=20)

        # Title
        ctk.CTkLabel(self, text="💊 Treatment Plans Catalog", font=("Arial", 30, "bold")).pack(pady=20)

        # Main Layout
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Left Panel: Form
        form_frame = ctk.CTkFrame(main_frame, width=420)
        form_frame.pack(side="left", fill="y", padx=15, pady=15)
        form_frame.pack_propagate(False)

        ctk.CTkLabel(form_frame, text="Treatment Editor", font=("Arial", 22, "bold")).pack(pady=20)

        # Diagnosis Combo
        ctk.CTkLabel(form_frame, text="Select Linked Diagnosis ID:", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(5, 2))
        self.diagnosis_combo = ctk.CTkComboBox(form_frame, width=320, values=[])
        self.diagnosis_combo.pack(pady=3)
        self.load_diagnoses()

        # Patient Combo
        ctk.CTkLabel(form_frame, text="Select Patient:", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(5, 2))
        self.patient_combo = ctk.CTkComboBox(form_frame, width=320, values=[])
        self.patient_combo.pack(pady=3)
        self.load_patients()

        # Doctor Combo
        ctk.CTkLabel(form_frame, text="Select Doctor:", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(5, 2))
        self.doctor_combo = ctk.CTkComboBox(form_frame, width=320, values=[])
        self.doctor_combo.pack(pady=3)
        self.load_doctors()

        # Treatment Details Textbox
        ctk.CTkLabel(form_frame, text="Treatment Advice / Details:", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(5, 2))
        self.details_textbox = ctk.CTkTextbox(form_frame, width=320, height=100)
        self.details_textbox.pack(pady=3)

        # Dates (Start & End)
        dates_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        dates_frame.pack(fill="x", padx=50, pady=5)

        ctk.CTkLabel(dates_frame, text="Start Date:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="e", pady=5)
        self.start_date_entry = ctk.CTkEntry(dates_frame, width=100)
        self.start_date_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ctk.CTkLabel(dates_frame, text="End Date:", font=("Arial", 11, "bold")).grid(row=0, column=2, sticky="e", pady=5)
        self.end_date_entry = ctk.CTkEntry(dates_frame, width=100)
        self.end_date_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Status Combo
        ctk.CTkLabel(form_frame, text="Plan Status:", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(5, 2))
        self.status_combo = ctk.CTkComboBox(form_frame, width=320, values=["Active", "Completed", "Suspended"])
        self.status_combo.pack(pady=3)
        self.status_combo.set("Active")

        # Action Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="➕ Add Plan", command=self.add_treatment, width=145).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="✏ Update", command=self.update_treatment, width=145).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="❌ Delete", command=self.delete_treatment, fg_color="red", hover_color="#b71c1c", width=145).grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="🧹 Clear", command=self.clear_fields, width=145).grid(row=1, column=1, padx=5, pady=5)

        # Right Panel: Treeview Table
        self.table_frame = ctk.CTkFrame(main_frame)
        self.table_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        # Search Bar
        search_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=15, pady=10)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by Patient Name or Details...", width=300)
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.search_treatment)

        ctk.CTkButton(search_frame, text="Search", command=self.search_treatment, width=100).pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="Reset", command=self.refresh_table, width=100).pack(side="left")

        # Treeview Setup
        container = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=15, pady=5)

        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side="right", fill="y")

        columns = ("ID", "Diag ID", "Patient Name", "Doctor Name", "Details", "Start Date", "End Date", "Status")
        self.table = ttk.Treeview(container, columns=columns, show="headings", yscrollcommand=scrollbar.set, height=18)
        for col in columns:
            self.table.heading(col, text=col, anchor="w")
            self.table.column(col, anchor="w", width=100)
        self.table.column("ID", width=40, anchor="center")
        self.table.column("Diag ID", width=60, anchor="center")
        self.table.column("Details", width=250)

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.table.yview)

        self.table.bind("<<TreeviewSelect>>", self.on_row_selected)

        self.load_treatments()
        self.clear_fields()

    def extract_id(self, combo_value):
        if not combo_value:
            return None
        try:
            return int(combo_value.split("ID: ")[1].replace(")", ""))
        except:
            return None

    def load_diagnoses(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT DiagnosisID, DiagnosisDetails FROM Diagnosis ORDER BY DiagnosisID DESC")
            diags = [f"Diag #{row[0]} - {row[1][:25]} (ID: {row[0]})" for row in cursor.fetchall()]
            self.diagnosis_combo.configure(values=diags)
            if diags:
                self.diagnosis_combo.set(diags[0])
            conn.close()
        except Exception as e:
            print(f"Error loading diagnoses: {e}")

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

    def load_treatments(self):
        for item in self.table.get_children():
            self.table.delete(item)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.TreatmentID, t.DiagnosisID, p.FullName, hw.FullName, t.TreatmentDetails, t.StartDate, t.EndDate, t.Status
                FROM Treatment t
                LEFT JOIN Patients p ON t.PatientID = p.PatientID
                LEFT JOIN Health_Workers hw ON t.DoctorID = hw.WorkerID
                ORDER BY t.TreatmentID DESC
            """)
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error loading treatments: {e}")

    def on_row_selected(self, event):
        selected = self.table.selection()
        if not selected:
            return
        row = self.table.item(selected[0], "values")
        self.selected_treatment_id = int(row[0])

        # Match diagnosis combo
        diag_id = row[1]
        diag_vals = self.diagnosis_combo.cget("values")
        for dv in diag_vals:
            if f"ID: {diag_id}" in dv:
                self.diagnosis_combo.set(dv)
                break

        # Match patient combo
        pat_vals = self.patient_combo.cget("values")
        for p in pat_vals:
            if row[2] in p:
                self.patient_combo.set(p)
                break

        # Match doctor combo
        doc_vals = self.doctor_combo.cget("values")
        for d in doc_vals:
            if row[3] in d:
                self.doctor_combo.set(d)
                break

        self.details_textbox.delete("1.0", "end")
        self.details_textbox.insert("1.0", row[4])

        self.start_date_entry.delete(0, "end")
        self.start_date_entry.insert(0, row[5])

        self.end_date_entry.delete(0, "end")
        self.end_date_entry.insert(0, row[6])

        self.status_combo.set(row[7])

    def clear_fields(self):
        self.selected_treatment_id = None
        self.details_textbox.delete("1.0", "end")
        self.start_date_entry.delete(0, "end")
        self.start_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.end_date_entry.delete(0, "end")
        self.end_date_entry.insert(0, (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))
        self.status_combo.set("Active")
        self.table.selection_remove(self.table.selection())

    def add_treatment(self):
        diag_id = self.extract_id(self.diagnosis_combo.get())
        patient_id = self.extract_id(self.patient_combo.get())
        doctor_id = self.extract_id(self.doctor_combo.get())
        details = self.details_textbox.get("1.0", "end").strip()
        start = self.start_date_entry.get().strip()
        end = self.end_date_entry.get().strip()
        status = self.status_combo.get()

        if not diag_id or not patient_id or not doctor_id or not details or not start or not end:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            datetime.strptime(start, "%Y-%m-%d")
            datetime.strptime(end, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Use YYYY-MM-DD date format.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Treatment (DiagnosisID, PatientID, DoctorID, TreatmentDetails, StartDate, EndDate, Status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (diag_id, patient_id, doctor_id, details, start, end, status))
            treat_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # Write audit log
            from database import log_audit_action
            log_audit_action(self.user_id, f"Recorded treatment plan (TreatmentID: {treat_id}) for PatientID: {patient_id}")

            messagebox.showinfo("Success", "Treatment plan added successfully!")
            self.load_treatments()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add treatment:\n{e}")

    def update_treatment(self):
        if not self.selected_treatment_id:
            messagebox.showwarning("Warning", "Select a treatment record to update.")
            return

        diag_id = self.extract_id(self.diagnosis_combo.get())
        patient_id = self.extract_id(self.patient_combo.get())
        doctor_id = self.extract_id(self.doctor_combo.get())
        details = self.details_textbox.get("1.0", "end").strip()
        start = self.start_date_entry.get().strip()
        end = self.end_date_entry.get().strip()
        status = self.status_combo.get()

        if not diag_id or not patient_id or not doctor_id or not details or not start or not end:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            datetime.strptime(start, "%Y-%m-%d")
            datetime.strptime(end, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Use YYYY-MM-DD date format.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Treatment
                SET DiagnosisID = %s, PatientID = %s, DoctorID = %s, TreatmentDetails = %s, StartDate = %s, EndDate = %s, Status = %s
                WHERE TreatmentID = %s
            """, (diag_id, patient_id, doctor_id, details, start, end, status, self.selected_treatment_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Treatment plan updated successfully!")
            self.load_treatments()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update treatment:\n{e}")

    def delete_treatment(self):
        if not self.selected_treatment_id:
            messagebox.showwarning("Warning", "Select a treatment record to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this treatment record?")
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Treatment WHERE TreatmentID = %s", (self.selected_treatment_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Treatment plan deleted successfully!")
            self.load_treatments()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete treatment:\n{e}")

    def search_treatment(self, event=None):
        q = self.search_entry.get().strip()
        if not q:
            self.load_treatments()
            return
        for item in self.table.get_children():
            self.table.delete(item)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.TreatmentID, t.DiagnosisID, p.FullName, hw.FullName, t.TreatmentDetails, t.StartDate, t.EndDate, t.Status
                FROM Treatment t
                LEFT JOIN Patients p ON t.PatientID = p.PatientID
                LEFT JOIN Health_Workers hw ON t.DoctorID = hw.WorkerID
                WHERE p.FullName LIKE %s OR t.TreatmentDetails LIKE %s
                ORDER BY t.TreatmentID DESC
            """, (f"%{q}%", f"%{q}%"))
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error searching treatments: {e}")

    def refresh_table(self):
        self.search_entry.delete(0, "end")
        self.load_treatments()
        self.clear_fields()


if __name__ == "__main__":
    class TestApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.geometry("1400x800")
            TreatmentWindow(self)

    app = TestApp()
    app.mainloop()
