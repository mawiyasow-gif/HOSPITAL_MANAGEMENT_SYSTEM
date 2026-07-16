import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
import hashlib
from database import connect_db

import dashboard_theme

# Set appearance mode and color theme
dashboard_theme.apply_global_theme()


class LoginApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Physical Health Clinic Record System")
        self.geometry("700x500")
        self.resizable(False, False)

        self.configure(fg_color=dashboard_theme.BG_COLOR)

        card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            border_color=dashboard_theme.BORDER_COLOR,
            border_width=1,
            corner_radius=15,
            width=450,
            height=400
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        title = ctk.CTkLabel(
            card,
            text="Physical Health Clinic System",
            font=("Arial", 20, "bold"),
            text_color=dashboard_theme.TEXT_PRIMARY
        )
        title.pack(pady=(25, 5))

        subtitle = ctk.CTkLabel(
            card,
            text="Sign in to your workspace",
            font=("Arial", 13, "bold"),
            text_color=dashboard_theme.TEXT_SECONDARY
        )
        subtitle.pack(pady=(0, 20))

        self.username = ctk.CTkEntry(
            card,
            width=320,
            height=40,
            placeholder_text="Username"
        )
        self.username.pack(pady=10)

        # Password layout frame to keep the toggle button inline
        password_frame = ctk.CTkFrame(card, fg_color="transparent")
        password_frame.pack(pady=10)

        self.password = ctk.CTkEntry(
            password_frame,
            width=275,
            height=40,
            placeholder_text="Password",
            show="*"
        )
        self.password.pack(side="left")

        self.password_visible = False
        self.toggle_btn = ctk.CTkButton(
            password_frame,
            text="👁️",
            width=40,
            height=40,
            font=("Arial", 14),
            fg_color="transparent",
            text_color="gray",
            hover_color=("#EAEAEA", "#2D2D2D"),
            command=self.toggle_password_visibility
        )
        self.toggle_btn.pack(side="left", padx=(5, 0))

        login_btn = ctk.CTkButton(
            card,
            text="Login",
            width=320,
            height=40,
            fg_color=dashboard_theme.ACCENT_BLUE,
            hover_color=dashboard_theme.ACCENT_BLUE_HOVER,
            command=self.login
        )
        login_btn.pack(pady=(20, 10))

        exit_btn = ctk.CTkButton(
            card,
            text="Exit System",
            width=320,
            height=35,
            fg_color="transparent",
            text_color=dashboard_theme.ACCENT_RED,
            hover_color="#FEE2E2",
            command=self.destroy
        )
        exit_btn.pack()

    def toggle_password_visibility(self):
        if self.password_visible:
            self.password.configure(show="*")
            self.toggle_btn.configure(text_color="gray")
            self.password_visible = False
        else:
            self.password.configure(show="")
            self.toggle_btn.configure(text_color=dashboard_theme.ACCENT_BLUE)
            self.password_visible = True

    def login(self):
        user = self.username.get().strip()
        password = self.password.get().strip()

        if not user or not password:
            messagebox.showerror("Validation Error", "Please fill in both Username and Password.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Hash the input password using SHA-256
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

            # Query to join Users and Health_Workers to get IDs, FullName, Role, and Status
            query = """
                SELECT u.UsersID, hw.WorkerID, u.FullName, u.Role, u.Status, u.Phone, u.Gender
                FROM Users u
                LEFT JOIN Health_Workers hw ON u.UsersID = hw.UsersID
                WHERE u.username = %s AND u.Password = %s
            """
            cursor.execute(query, (user, hashed_password))
            result = cursor.fetchone()

            if result:
                user_id, worker_id, full_name, role, status, phone, gender = result

                # Verify Status is Active
                if status != "Active":
                    messagebox.showerror("Access Denied", "Your account is Inactive. Please contact the System Administrator.")
                    conn.close()
                    return

                # Self-healing: if worker_id is missing, create it on the fly
                if worker_id is None:
                    worker_phone = phone if phone else f"+232-00-{user_id:06d}"
                    cursor.execute("SELECT WorkerID FROM Health_Workers WHERE PhoneNumber = %s", (worker_phone,))
                    if cursor.fetchone():
                        worker_phone = f"+232-99-{user_id:06d}"

                    cursor.execute("""
                        INSERT INTO Health_Workers (UsersID, FullName, Gender, PhoneNumber, Address, Role)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user_id, full_name, gender if gender else 'Male', worker_phone, 'Clinic Staff', role))
                    conn.commit()
                    worker_id = cursor.lastrowid

                messagebox.showinfo("Success", f"Welcome back, {full_name}!")
                self.destroy()

                # Store user info in session
                current_user = {
                    "user_id": user_id,
                    "worker_id": worker_id,
                    "full_name": full_name,
                    "role": role
                }
                import session
                session.current_user = current_user
                from database import log_audit_action
                log_audit_action(user_id, f"User '{user}' logged in successfully.")

                # Route to appropriate dashboard based on Role
                if role == "Administrator":
                    from admin_dashboard import AdminDashboard
                    app = AdminDashboard(admin_user=current_user)
                elif role == "Doctor":
                    from doctor_dashboard import DoctorDashboard
                    app = DoctorDashboard(doctor_user=current_user)
                elif role == "Receptionist":
                    from receptionist_dashboard import ReceptionistDashboard
                    app = ReceptionistDashboard(receptionist_user=current_user)
                elif role == "Laboratory Technician":
                    from laboratory_technician_dashboard import LaboratoryTechnicianDashboard
                    app = LaboratoryTechnicianDashboard(lab_user=current_user)
                elif role == "Pharmacist":
                    from pharmacist_dashboard import PharmacistDashboard
                    app = PharmacistDashboard(pharmacist_user=current_user)
                elif role == "Accountant":
                    from accountant_dashboard import AccountantDashboard
                    app = AccountantDashboard(accountant_user=current_user)
                else:
                    from dashboard import Dashboard
                    app = Dashboard()
                
                app.mainloop()

            else:
                messagebox.showerror("Error", "Invalid Username or Password")

            conn.close()

        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred during login:\n{e}")


if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()