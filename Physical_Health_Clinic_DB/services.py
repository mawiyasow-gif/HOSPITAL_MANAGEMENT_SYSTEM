import customtkinter as ctk
from tkinter import ttk, messagebox
from database import connect_db

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class HospitalServicesWindow(ctk.CTkToplevel):
    """Hospital Services Management panel for Administrator."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Hospital Services Management")
        self.geometry("1100x650")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.selected_service_id = None

        # Title
        ctk.CTkLabel(
            self,
            text="🏥 Hospital Services Management",
            font=("Arial", 22, "bold"),
            text_color="#1F6AA5"
        ).pack(pady=15)

        # Main Layout
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Left Panel: Form
        form_frame = ctk.CTkFrame(main_frame, width=350)
        form_frame.pack(side="left", fill="y", padx=10, pady=10)
        form_frame.pack_propagate(False)

        ctk.CTkLabel(form_frame, text="Service Editor", font=("Arial", 16, "bold")).pack(pady=10)

        # Service Name
        ctk.CTkLabel(form_frame, text="Service Name:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        self.name_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="e.g. X-Ray / ECG")
        self.name_entry.pack(pady=5)

        # Price
        ctk.CTkLabel(form_frame, text="Price (Le):", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        self.price_entry = ctk.CTkEntry(form_frame, width=300, placeholder_text="e.g. 150.00")
        self.price_entry.pack(pady=5)

        # Status
        ctk.CTkLabel(form_frame, text="Status:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        self.status_combo = ctk.CTkComboBox(form_frame, width=300, values=["Active", "Inactive"])
        self.status_combo.pack(pady=5)
        self.status_combo.set("Active")

        # Action Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="➕ Add Service", command=self.add_service, width=140).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="✏ Update", command=self.update_service, width=140).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="❌ Delete", command=self.delete_service, fg_color="red", hover_color="#b71c1c", width=140).grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="🧹 Clear", command=self.clear_fields, width=140).grid(row=1, column=1, padx=5, pady=5)

        # Right Panel: Services Table
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(table_frame, text="Hospital Services Catalog", font=("Arial", 14, "bold"), text_color="#1F6AA5").pack(anchor="w", padx=10, pady=5)

        container = ctk.CTkFrame(table_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side="right", fill="y")

        columns = ("Service ID", "Service Name", "Price", "Status")
        self.table = ttk.Treeview(container, columns=columns, show="headings", yscrollcommand=scrollbar.set, height=12)
        for col in columns:
            self.table.heading(col, text=col, anchor="w")
            self.table.column(col, anchor="w", width=150)
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.table.yview)

        self.table.bind("<<TreeviewSelect>>", self.on_row_selected)

        self.load_services()

    def load_services(self):
        for item in self.table.get_children():
            self.table.delete(item)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT ServiceID, ServiceName, Price, Status FROM Hospital_Services ORDER BY ServiceID ASC")
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                cleaned[2] = f"Le {float(cleaned[2]):,.2f}" if cleaned[2] else "Le 0.00"
                self.table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error loading services: {e}")

    def on_row_selected(self, event):
        selected = self.table.selection()
        if not selected:
            return
        row = self.table.item(selected[0], "values")
        self.selected_service_id = row[0]
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, row[1])
        
        # Remove "Le " and commas from price
        price_val = row[2].replace("Le ", "").replace(",", "")
        self.price_entry.delete(0, "end")
        self.price_entry.insert(0, price_val)
        
        self.status_combo.set(row[3])

    def clear_fields(self):
        self.selected_service_id = None
        self.name_entry.delete(0, "end")
        self.price_entry.delete(0, "end")
        self.status_combo.set("Active")
        self.table.selection_remove(self.table.selection())

    def add_service(self):
        name = self.name_entry.get().strip()
        price_str = self.price_entry.get().strip()
        status = self.status_combo.get()

        if not name or not price_str:
            messagebox.showerror("Error", "Service Name and Price are required.")
            return

        try:
            price = float(price_str)
            if price < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Price must be a positive decimal.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Hospital_Services (ServiceName, Price, Status)
                VALUES (%s, %s, %s)
            """, (name, price, status))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Hospital service added successfully!")
            self.load_services()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add service:\n{e}")

    def update_service(self):
        if not self.selected_service_id:
            messagebox.showwarning("Warning", "Select a service to update.")
            return

        name = self.name_entry.get().strip()
        price_str = self.price_entry.get().strip()
        status = self.status_combo.get()

        if not name or not price_str:
            messagebox.showerror("Error", "Service Name and Price are required.")
            return

        try:
            price = float(price_str)
            if price < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Price must be a positive decimal.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Hospital_Services
                SET ServiceName = %s, Price = %s, Status = %s
                WHERE ServiceID = %s
            """, (name, price, status, self.selected_service_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Hospital service updated successfully!")
            self.load_services()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update service:\n{e}")

    def delete_service(self):
        if not self.selected_service_id:
            messagebox.showwarning("Warning", "Select a service to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this service?")
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Hospital_Services WHERE ServiceID = %s", (self.selected_service_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Hospital service deleted successfully!")
            self.load_services()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete service:\n{e}")
