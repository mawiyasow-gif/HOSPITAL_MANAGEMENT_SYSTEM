import customtkinter as ctk
from tkinter import ttk, messagebox
from database import connect_db

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class UserManagementWindow(ctk.CTkToplevel):
    """User Management Window for Administrator to manage clinic staff accounts."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("User Management - System Administrator")
        self.geometry("1500x850")
        self.resizable(True, True)

        # Track selected user ID
        self.selected_user_id = None

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

        # Total Users Badge (Top-Right)
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

        self.total_users_lbl = ctk.CTkLabel(
            self.badge_frame,
            text="👥 Total Users: 0",
            font=("Arial", 13, "bold"),
            text_color="#1F6AA5"
        )
        self.total_users_lbl.pack(padx=12, expand=True)

        # ==============================
        # Window Title
        # ==============================
        title = ctk.CTkLabel(
            self,
            text="👥 User Access Management",
            font=("Arial", 30, "bold")
        )
        title.pack(pady=20)

        # ==============================
        # Main Frame
        # ==============================
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ==============================
        # Left Panel (User Form)
        # ==============================
        form_frame = ctk.CTkFrame(main_frame, width=420)
        form_frame.pack(side="left", fill="y", padx=15, pady=15)

        ctk.CTkLabel(
            form_frame,
            text="User Account Details",
            font=("Arial", 22, "bold")
        ).pack(pady=15)

        # Full Name
        ctk.CTkLabel(form_frame, text="Full Name:", font=("Arial", 13, "bold")).pack(pady=(5, 2), anchor="w", padx=50)
        self.fullname_entry = ctk.CTkEntry(form_frame, width=320, placeholder_text="e.g. John Doe")
        self.fullname_entry.pack(pady=3)

        # Username
        ctk.CTkLabel(form_frame, text="Username:", font=("Arial", 13, "bold")).pack(pady=(5, 2), anchor="w", padx=50)
        self.username_entry = ctk.CTkEntry(form_frame, width=320, placeholder_text="e.g. jdoe")
        self.username_entry.pack(pady=3)

        # Password
        ctk.CTkLabel(form_frame, text="Password / Reset Password:", font=("Arial", 13, "bold")).pack(pady=(5, 2), anchor="w", padx=50)
        self.password_entry = ctk.CTkEntry(form_frame, width=320, placeholder_text="Enter new password", show="*")
        self.password_entry.pack(pady=3)

        # Role
        ctk.CTkLabel(form_frame, text="Assign Access Role:", font=("Arial", 13, "bold")).pack(pady=(5, 2), anchor="w", padx=50)
        self.role_combo = ctk.CTkComboBox(
            form_frame,
            width=320,
            values=["Administrator", "Doctor", "Receptionist", "Nurse", "Pharmacist", "Accountant"]
        )
        self.role_combo.set("Nurse")
        self.role_combo.pack(pady=3)

        # Email
        ctk.CTkLabel(form_frame, text="Email Address:", font=("Arial", 13, "bold")).pack(pady=(5, 2), anchor="w", padx=50)
        self.email_entry = ctk.CTkEntry(form_frame, width=320, placeholder_text="e.g. jdoe@clinic.com")
        self.email_entry.pack(pady=3)

        # Phone
        ctk.CTkLabel(form_frame, text="Phone Number:", font=("Arial", 13, "bold")).pack(pady=(5, 2), anchor="w", padx=50)
        self.phone_entry = ctk.CTkEntry(form_frame, width=320, placeholder_text="e.g. +23276XXXXXX")
        self.phone_entry.pack(pady=3)

        # Gender
        ctk.CTkLabel(form_frame, text="Gender:", font=("Arial", 13, "bold")).pack(pady=(5, 2), anchor="w", padx=50)
        self.gender_combo = ctk.CTkComboBox(form_frame, width=320, values=["Male", "Female"])
        self.gender_combo.set("Male")
        self.gender_combo.pack(pady=3)

        # Status
        ctk.CTkLabel(form_frame, text="Account Status:", font=("Arial", 13, "bold")).pack(pady=(5, 2), anchor="w", padx=50)
        self.status_combo = ctk.CTkComboBox(form_frame, width=320, values=["Active", "Inactive"])
        self.status_combo.set("Active")
        self.status_combo.pack(pady=3)

        # ==============================
        # Action Buttons
        # ==============================
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(
            button_frame,
            text="➕ Add Staff Account",
            width=140,
            command=self.add_user
        ).grid(row=0, column=0, padx=5, pady=5)

        ctk.CTkButton(
            button_frame,
            text="✏ Update Details",
            width=140,
            command=self.update_user
        ).grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkButton(
            button_frame,
            text="🧹 Clear Fields",
            width=140,
            command=self.clear_fields
        ).grid(row=1, column=0, padx=5, pady=5)

        ctk.CTkButton(
            button_frame,
            text="🔑 Reset Password",
            width=140,
            command=self.reset_password
        ).grid(row=1, column=1, padx=5, pady=5)

        # ==============================
        # Right Panel (Users Table)
        # ==============================
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        # Search bar
        search_frame = ctk.CTkFrame(table_frame)
        search_frame.pack(fill="x", pady=10)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=300,
            placeholder_text="Search staff by Name, Role, Status..."
        )
        self.search_entry.pack(side="left", padx=10)

        ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_users
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="Refresh",
            command=self.refresh_table
        ).pack(side="left", padx=5)

        # Table Columns
        columns = (
            "User ID",
            "Full Name",
            "Username",
            "Role",
            "Email Address",
            "Phone Number",
            "Status",
            "Last Login"
        )

        # Style Treeview table
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

        # Treeview widget
        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=20
        )

        for col in columns:
            self.table.heading(col, text=col, anchor="center")
            self.table.column(col, width=130, anchor="center")

        # Make Full Name and Email slightly wider
        self.table.column("Full Name", width=180, anchor="center")
        self.table.column("Email Address", width=180, anchor="center")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.table.xview)

        self.table.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        h_scrollbar.pack(side="bottom", fill="x")
        self.table.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")

        # Bind row select
        self.table.bind("<<TreeviewSelect>>", self.select_user)

        # Load users
        self.load_users()

    # ==============================
    # Core Functions
    # ==============================

    def load_users(self):
        """Fetch all user records from the database and populate the treeview."""
        # Clear existing items
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT UsersID, FullName, username, Role, Email, Phone, Status, LastLogin
                FROM Users
                ORDER BY UsersID DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                cleaned_row = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned_row)

            # Update total users label
            self.total_users_lbl.configure(text=f"👥 Total Users: {len(rows)}")

            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load users:\n{e}")

    def add_user(self):
        """Insert a new user account into the database with password hashing / plaintext."""
        fullname = self.fullname_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_combo.get()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        gender = self.gender_combo.get()
        status = self.status_combo.get()

        if not fullname or not username or not password or not role:
            messagebox.showerror("Validation Error", "Full Name, Username, Password, and Role are required.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Check if username exists
            cursor.execute("SELECT UsersID FROM Users WHERE username=%s", (username,))
            if cursor.fetchone():
                messagebox.showerror("Validation Error", "Username already exists. Please choose another.")
                conn.close()
                return

            cursor.execute(query, (fullname, username, password, role, email, phone, gender, status))
            new_users_id = cursor.lastrowid

            # Sync with Health_Workers table
            worker_phone = phone if phone else f"+232-00-{new_users_id:06d}"
            cursor.execute("SELECT WorkerID FROM Health_Workers WHERE PhoneNumber = %s", (worker_phone,))
            if cursor.fetchone():
                worker_phone = f"+232-99-{new_users_id:06d}"

            cursor.execute("""
                INSERT INTO Health_Workers (UsersID, FullName, Gender, PhoneNumber, Address, Role)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (new_users_id, fullname, gender, worker_phone, 'Clinic Staff', role))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "New staff account created successfully!")
            self.load_users()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add user:\n{e}")

    def update_user(self):
        """Update existing user details in the database."""
        if not self.selected_user_id:
            messagebox.showwarning("Selection Warning", "Please select a staff member to update.")
            return

        fullname = self.fullname_entry.get().strip()
        username = self.username_entry.get().strip()
        role = self.role_combo.get()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        gender = self.gender_combo.get()
        status = self.status_combo.get()

        if not fullname or not username or not role:
            messagebox.showerror("Validation Error", "Full Name, Username, and Role cannot be empty.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Check if username is taken by another user
            cursor.execute("SELECT UsersID FROM Users WHERE username=%s AND UsersID != %s", (username, self.selected_user_id))
            if cursor.fetchone():
                messagebox.showerror("Validation Error", "Username is already taken by another account.")
                conn.close()
                return

            cursor.execute(query, (fullname, username, role, email, phone, gender, status, self.selected_user_id))

            # Sync with Health_Workers table
            cursor.execute("SELECT WorkerID FROM Health_Workers WHERE UsersID = %s", (self.selected_user_id,))
            worker_row = cursor.fetchone()

            worker_phone = phone if phone else f"+232-00-{self.selected_user_id:06d}"

            if worker_row:
                cursor.execute("""
                    UPDATE Health_Workers
                    SET FullName = %s, Gender = %s, PhoneNumber = %s, Role = %s
                    WHERE UsersID = %s
                """, (fullname, gender, worker_phone, role, self.selected_user_id))
            else:
                cursor.execute("""
                    INSERT INTO Health_Workers (UsersID, FullName, Gender, PhoneNumber, Address, Role)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (self.selected_user_id, fullname, gender, worker_phone, 'Clinic Staff', role))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "User details updated successfully!")
            self.load_users()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update details:\n{e}")

    def reset_password(self):
        """Reset the password of the selected user."""
        if not self.selected_user_id:
            messagebox.showwarning("Selection Warning", "Please select a staff member to reset their password.")
            return

        password = self.password_entry.get().strip()
        if not password:
            messagebox.showerror("Validation Error", "Please enter a new password in the password field.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET Password=%s WHERE UsersID=%s", (password, self.selected_user_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Password reset successfully!")
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to reset password:\n{e}")

    def delete_user(self):
        # Admin can delete staff if needed, but standard is setting to Inactive.
        # We can implement this in user request if they want strict delete.
        pass

    def search_users(self):
        """Search staff members by name, role, email, or status."""
        search_query = self.search_entry.get().strip()
        if not search_query:
            self.load_users()
            return

        # Clear existing items
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT UsersID, FullName, username, Role, Email, Phone, Status, LastLogin
                FROM Users
                WHERE FullName LIKE %s OR username LIKE %s OR Role LIKE %s OR Email LIKE %s OR Status LIKE %s
                ORDER BY UsersID DESC
            """
            like_val = f"%{search_query}%"
            cursor.execute(query, (like_val, like_val, like_val, like_val, like_val))
            rows = cursor.fetchall()

            for row in rows:
                cleaned_row = ["" if val is None else str(val) for val in row]
                self.table.insert("", "end", values=cleaned_row)

            # Update the total users label
            self.total_users_lbl.configure(text=f"👥 Total Users: {len(rows)}")

            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to search users:\n{e}")

    def select_user(self, event=None):
        """Load selected user details from table into form fields."""
        selected_item = self.table.selection()
        if not selected_item:
            return

        row_values = self.table.item(selected_item[0], "values")
        if not row_values:
            return

        self.selected_user_id = row_values[0]

        # Reset form text fields
        self.fullname_entry.delete(0, "end")
        self.fullname_entry.insert(0, row_values[1])

        self.username_entry.delete(0, "end")
        self.username_entry.insert(0, row_values[2])

        self.password_entry.delete(0, "end")  # Hide passwords for security

        self.role_combo.set(row_values[3])

        self.email_entry.delete(0, "end")
        self.email_entry.insert(0, row_values[4])

        self.phone_entry.delete(0, "end")
        self.phone_entry.insert(0, row_values[5])

        self.status_combo.set(row_values[6])

        # Find gender from DB if needed, or default
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT Gender FROM Users WHERE UsersID=%s", (self.selected_user_id,))
            gender_val = cursor.fetchone()
            if gender_val:
                self.gender_combo.set(gender_val[0])
            conn.close()
        except:
            pass

    def clear_fields(self):
        """Clear all form inputs and select highlight."""
        self.selected_user_id = None
        self.fullname_entry.delete(0, "end")
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.role_combo.set("Nurse")
        self.gender_combo.set("Male")
        self.status_combo.set("Active")
        self.search_entry.delete(0, "end")
        self.table.selection_remove(self.table.selection())

    def refresh_table(self):
        """Reload all users list."""
        self.load_users()


if __name__ == "__main__":
    class TestApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.geometry("1500x850")
            UserManagementWindow(self)

    app = TestApp()
    app.mainloop()
