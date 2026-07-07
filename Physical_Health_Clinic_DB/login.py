import customtkinter as ctk
from tkinter import messagebox
from database import connect_db

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class LoginApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Physical Health Clinic Record System")
        self.geometry("700x500")
        self.resizable(False, False)

        title = ctk.CTkLabel(
            self,
            text="Physical Health Clinic Record System",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=30)

        subtitle = ctk.CTkLabel(
            self,
            text="Login",
            font=("Arial", 18)
        )
        subtitle.pack(pady=10)

        self.username = ctk.CTkEntry(
            self,
            width=300,
            placeholder_text="Username"
        )
        self.username.pack(pady=10)

        self.password = ctk.CTkEntry(
            self,
            width=300,
            placeholder_text="Password",
            show="*"
        )
        self.password.pack(pady=10)

        login_btn = ctk.CTkButton(
            self,
            text="Login",
            width=300,
            command=self.login
        )
        login_btn.pack(pady=20)

        exit_btn = ctk.CTkButton(
            self,
            text="Exit",
            width=300,
            fg_color="red",
            command=self.destroy
        )
        exit_btn.pack()

    def login(self):

        user = self.username.get()
        password = self.password.get()

        try:

            conn = connect_db()
            cursor = conn.cursor()

            query = """
            SELECT *
            FROM Users
            WHERE username=%s
            AND Password=%s
            """

            cursor.execute(query, (user, password))

            result = cursor.fetchone()

            if result:
                messagebox.showinfo("Success", "Login Successful!")
                self.destroy()

                role = result[4]
                user_info = {
                    "username": result[2],
                    "full_name": result[1],
                    "role": result[4]
                }

                if role == "Administrator":
                    from admin_dashboard import AdminDashboard
                    app = AdminDashboard(admin_user=user_info)
                elif role == "Doctor":
                    from doctor_dashboard import DoctorDashboard
                    app = DoctorDashboard(doctor_user=user_info)
                else:
                    from dashboard import Dashboard
                    app = Dashboard()
                app.mainloop()

            else:
                messagebox.showerror("Error", "Invalid Username or Password")

            conn.close()

        except Exception as e:
            messagebox.showerror("Database Error", str(e))


if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()