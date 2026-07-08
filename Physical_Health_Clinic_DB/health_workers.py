import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from database import connect_db
import os
import shutil

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class HealthWorkerWindow(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Health Worker Management")
        self.geometry("1500x850")
        self.resizable(True, True)

        # Track selected worker ID for updates/deletes
        self.selected_worker_id = None

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
            text="👩‍⚕️ Health Worker Management",
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

        ctk.CTkLabel(form_frame, text="Worker Information",
                     font=("Arial", 22, "bold")).pack(pady=20)

        self.fullname = ctk.CTkEntry(form_frame, width=320, placeholder_text="Full Name")
        self.fullname.pack(pady=10)

        self.gender = ctk.CTkComboBox(
            form_frame,
            values=["Male", "Female"]
        )
        self.gender.pack(pady=10)

        self.phone = ctk.CTkEntry(form_frame, width=320, placeholder_text="Phone Number")
        self.phone.pack(pady=10)

        self.address = ctk.CTkEntry(form_frame, width=320, placeholder_text="Address")
        self.address.pack(pady=10)

        self.role = ctk.CTkEntry(form_frame, width=320, placeholder_text="Role (e.g., Doctor, Nurse)")
        self.role.pack(pady=10)

        # Profile Photo Selection
        self.selected_image_path = None
        self.photo_btn = ctk.CTkButton(
            form_frame,
            text="📸 Select Profile Photo",
            width=320,
            command=self.select_photo,
            fg_color="#1F6AA5"
        )
        self.photo_btn.pack(pady=10)

        # =========================
        # Buttons
        # =========================

        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=25)

        ctk.CTkButton(button_frame, text="➕ Add", width=140, command=self.add_worker).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(button_frame, text="✏ Update", width=140, command=self.update_worker).grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkButton(button_frame, text="❌ Delete", width=140, command=self.delete_worker).grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkButton(button_frame, text="🧹 Clear", width=140, command=self.clear_fields).grid(row=1, column=1, padx=5, pady=5)

        # =========================
        # Right Frame (Table)
        # =========================

        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        search_frame = ctk.CTkFrame(table_frame)
        search_frame.pack(fill="x", pady=10)

        self.search = ctk.CTkEntry(search_frame, width=300, placeholder_text="Search Worker...")
        self.search.pack(side="left", padx=10)

        ctk.CTkButton(search_frame, text="Search", command=self.search_worker).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Refresh", command=self.refresh_table).pack(side="left", padx=5)

        columns = (
            "Worker ID",
            "Full Name",
            "Gender",
            "Phone Number",
            "Address",
            "Role"
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

        # Bind row selection to load worker details into form fields
        self.table.bind("<<TreeviewSelect>>", self.select_worker)

        # Load worker records from database automatically on startup
        self.load_workers()

    def load_workers(self):
        """Fetch all health worker records from the database and populate the treeview."""
        # Clear existing items in treeview
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = "SELECT WorkerID, FullName, Gender, PhoneNumber, Address, Role FROM Health_Workers"
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                cleaned_row = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned_row)

            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load health workers:\n{e}")

    def add_worker(self):
        """Add a new health worker record and create a linked user account."""
        name = self.fullname.get().strip()
        gender = self.gender.get()
        phone = self.phone.get().strip()
        address = self.address.get().strip()
        role = self.role.get().strip()

        if not name or not gender or not role:
            messagebox.showerror("Validation Error", "Full Name, Gender, and Role are required fields.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Normalize role for the Users table enum
            norm_role = role.capitalize()
            if norm_role not in ['Administrator', 'Doctor', 'Receptionist', 'Nurse', 'Pharmacist', 'Accountant']:
                norm_role = 'Nurse'

            # Generate a unique username
            base_username = "".join([c for c in name.lower() if c.isalnum()])
            if not base_username:
                base_username = "user"
            username = base_username
            suffix = 1
            while True:
                cursor.execute("SELECT UsersID FROM Users WHERE username = %s", (username,))
                if not cursor.fetchone():
                    break
                username = f"{base_username}{suffix}"
                suffix += 1

            # Insert into Users first
            user_query = """
                INSERT INTO Users (FullName, username, Password, Role, Email, Phone, Gender, Status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(user_query, (name, username, 'Password123', norm_role, None, phone, gender, 'Active'))
            users_id = cursor.lastrowid

            # Insert into Health_Workers linked to the UsersID
            query = """
                INSERT INTO Health_Workers (UsersID, FullName, Gender, PhoneNumber, Address, Role)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (users_id, name, gender, phone, address, role))
            conn.commit()
            
            # Save photo if selected
            worker_id = cursor.lastrowid
            if self.selected_image_path:
                os.makedirs("assets", exist_ok=True)
                dest_path = f"assets/doctor_{worker_id}.png"
                try:
                    shutil.copy(self.selected_image_path, dest_path)
                except Exception as e:
                    print(f"Error copying profile photo: {e}")

            conn.close()

            messagebox.showinfo("Success", f"Health worker and linked user '{username}' (password: Password123) added successfully!")
            self.load_workers()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add health worker:\n{e}")

    def update_worker(self):
        """Update the selected health worker record and propagate changes to their linked user account."""
        if not self.selected_worker_id:
            messagebox.showwarning("Selection Warning", "Please select a health worker from the list to update.")
            return

        name = self.fullname.get().strip()
        gender = self.gender.get()
        phone = self.phone.get().strip()
        address = self.address.get().strip()
        role = self.role.get().strip()

        if not name or not gender or not role:
            messagebox.showerror("Validation Error", "Full Name, Gender, and Role are required fields.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Check if there is a linked UsersID
            cursor.execute("SELECT UsersID FROM Health_Workers WHERE WorkerID = %s", (self.selected_worker_id,))
            linked_user_row = cursor.fetchone()

            norm_role = role.capitalize()
            if norm_role not in ['Administrator', 'Doctor', 'Receptionist', 'Nurse', 'Pharmacist', 'Accountant']:
                norm_role = 'Nurse'

            if linked_user_row and linked_user_row[0]:
                users_id = linked_user_row[0]
                cursor.execute("""
                    UPDATE Users
                    SET FullName = %s, Role = %s, Phone = %s, Gender = %s
                    WHERE UsersID = %s
                """, (name, norm_role, phone, gender, users_id))
            else:
                # Self-healing: Create missing user account
                base_username = "".join([c for c in name.lower() if c.isalnum()])
                if not base_username:
                    base_username = "user"
                username = base_username
                suffix = 1
                while True:
                    cursor.execute("SELECT UsersID FROM Users WHERE username = %s", (username,))
                    if not cursor.fetchone():
                        break
                    username = f"{base_username}{suffix}"
                    suffix += 1

                cursor.execute("""
                    INSERT INTO Users (FullName, username, Password, Role, Email, Phone, Gender, Status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (name, username, 'Password123', norm_role, None, phone, gender, 'Active'))
                new_users_id = cursor.lastrowid
                
                cursor.execute("UPDATE Health_Workers SET UsersID = %s WHERE WorkerID = %s", (new_users_id, self.selected_worker_id))

            # Update the Health Worker record
            query = """
                UPDATE Health_Workers 
                SET FullName = %s, Gender = %s, PhoneNumber = %s, Address = %s, Role = %s
                WHERE WorkerID = %s
            """
            cursor.execute(query, (name, gender, phone, address, role, self.selected_worker_id))
            conn.commit()
            
            # Save photo if selected
            if self.selected_image_path:
                os.makedirs("assets", exist_ok=True)
                dest_path = f"assets/doctor_{self.selected_worker_id}.png"
                try:
                    shutil.copy(self.selected_image_path, dest_path)
                except Exception as e:
                    print(f"Error copying profile photo: {e}")

            conn.close()

            messagebox.showinfo("Success", "Health worker updated successfully!")
            self.load_workers()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update health worker:\n{e}")

    def delete_worker(self):
        """Delete the selected health worker record and their linked user account."""
        if not self.selected_worker_id:
            messagebox.showwarning("Selection Warning", "Please select a health worker from the list to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this health worker record and its linked user credentials?")
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Retrieve the linked UsersID
            cursor.execute("SELECT UsersID FROM Health_Workers WHERE WorkerID = %s", (self.selected_worker_id,))
            linked_user_row = cursor.fetchone()

            # Delete the Health_Worker
            query = "DELETE FROM Health_Workers WHERE WorkerID = %s"
            cursor.execute(query, (self.selected_worker_id,))

            # Delete the linked User
            if linked_user_row and linked_user_row[0]:
                cursor.execute("DELETE FROM Users WHERE UsersID = %s", (linked_user_row[0],))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Health worker and linked user account deleted successfully!")
            self.load_workers()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete health worker:\n{e}")

    def clear_fields(self):
        """Clear all form entry fields and reset dropdown selections."""
        self.selected_worker_id = None
        self.fullname.delete(0, "end")
        self.gender.set("Male")
        self.phone.delete(0, "end")
        self.address.delete(0, "end")
        self.role.delete(0, "end")
        self.search.delete(0, "end")
        self.selected_image_path = None
        self.photo_btn.configure(text="📸 Select Profile Photo")
        self.table.selection_remove(self.table.selection())

    def select_worker(self, event=None):
        """Populate the form fields with data from the selected Treeview row."""
        selected_item = self.table.selection()
        if not selected_item:
            return

        row_values = self.table.item(selected_item[0], "values")
        if not row_values:
            return

        self.selected_worker_id = row_values[0]
        
        self.fullname.delete(0, "end")
        self.fullname.insert(0, row_values[1])

        self.gender.set(row_values[2])

        self.phone.delete(0, "end")
        self.phone.insert(0, row_values[3])

        self.address.delete(0, "end")
        self.address.insert(0, row_values[4])

        self.role.delete(0, "end")
        self.role.insert(0, row_values[5])

    def search_worker(self):
        """Search and display health workers matching the query from the search entry."""
        search_query = self.search.get().strip()
        if not search_query:
            self.load_workers()
            return

        # Clear existing items in treeview
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT WorkerID, FullName, Gender, PhoneNumber, Address, Role 
                FROM Health_Workers
                WHERE WorkerID LIKE %s OR FullName LIKE %s OR PhoneNumber LIKE %s OR Address LIKE %s OR Role LIKE %s
            """
            like_val = f"%{search_query}%"
            cursor.execute(query, (like_val, like_val, like_val, like_val, like_val))
            rows = cursor.fetchall()

            for row in rows:
                cleaned_row = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned_row)

            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to search health workers:\n{e}")

    def refresh_table(self):
        """Reload health worker data from database."""
        self.load_workers()

    def select_photo(self):
        """Open a file dialog for the admin to pick a profile photo."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp")]
        )
        if file_path:
            self.selected_image_path = file_path
            self.photo_btn.configure(text="✅ Photo Selected")


if __name__ == "__main__":
    class TestApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.geometry("1500x850")
            HealthWorkerWindow(self)
            
    app = TestApp()
    app.mainloop()
