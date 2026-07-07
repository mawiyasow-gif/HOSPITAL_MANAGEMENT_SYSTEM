import customtkinter as ctk
from tkinter import messagebox, filedialog
import json
import os
from database import connect_db

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

CONFIG_PATH = "settings.json"


class SettingsWindow(ctk.CTkToplevel):
    """Settings Window for Administrator to configure clinic metadata and perform database maintenance."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("System Settings & Maintenance")
        self.geometry("1400x800")
        self.resizable(True, True)

        # Load current configurations
        self.config = self.load_config()

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
            text="⚙️ System Settings & Maintenance",
            font=("Arial", 30, "bold")
        )
        title.pack(pady=20)

        # ==============================
        # Main Frame Split Layout
        # ==============================
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Left Frame: Clinic Profile Configurations
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            left_frame,
            text="🏥 Clinic Profile Configuration",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        # Clinic Name
        ctk.CTkLabel(left_frame, text="Clinic Name:", font=("Arial", 13, "bold")).pack(pady=(10, 2), anchor="w", padx=40)
        self.clinic_name = ctk.CTkEntry(left_frame, width=380)
        self.clinic_name.insert(0, self.config.get("clinic_name", "Physical Health Clinic"))
        self.clinic_name.pack(pady=5)

        # Clinic Address
        ctk.CTkLabel(left_frame, text="Clinic Address:", font=("Arial", 13, "bold")).pack(pady=(10, 2), anchor="w", padx=40)
        self.clinic_address = ctk.CTkEntry(left_frame, width=380)
        self.clinic_address.insert(0, self.config.get("clinic_address", "123 Main Street, Freetown"))
        self.clinic_address.pack(pady=5)

        # Clinic Phone
        ctk.CTkLabel(left_frame, text="Contact Number:", font=("Arial", 13, "bold")).pack(pady=(10, 2), anchor="w", padx=40)
        self.clinic_phone = ctk.CTkEntry(left_frame, width=380)
        self.clinic_phone.insert(0, self.config.get("clinic_phone", "+232-76-123456"))
        self.clinic_phone.pack(pady=5)

        # Clinic Email
        ctk.CTkLabel(left_frame, text="Clinic Email:", font=("Arial", 13, "bold")).pack(pady=(10, 2), anchor="w", padx=40)
        self.clinic_email = ctk.CTkEntry(left_frame, width=380)
        self.clinic_email.insert(0, self.config.get("clinic_email", "info@physicalhealthclinic.com"))
        self.clinic_email.pack(pady=5)

        # Currency
        ctk.CTkLabel(left_frame, text="System Currency Prefix:", font=("Arial", 13, "bold")).pack(pady=(10, 2), anchor="w", padx=40)
        self.currency = ctk.CTkEntry(left_frame, width=380)
        self.currency.insert(0, self.config.get("currency", "Le"))
        self.currency.pack(pady=5)

        # Save clinic settings button
        ctk.CTkButton(
            left_frame,
            text="💾 Save Clinic Settings",
            width=200,
            command=self.save_clinic_settings,
            fg_color="#1F6AA5"
        ).pack(pady=25)

        # Right Frame: Database & Appearance Maintenance
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # --- Subframe 1: Appearance Customization ---
        appearance_frame = ctk.CTkFrame(right_frame)
        appearance_frame.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(
            appearance_frame,
            text="🎨 Appearance Preferences",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        ctk.CTkLabel(appearance_frame, text="System Theme Color Mode:", font=("Arial", 12)).pack(pady=2)
        self.theme_combo = ctk.CTkComboBox(
            appearance_frame,
            values=["Light", "Dark", "System"],
            command=self.change_theme_mode
        )
        self.theme_combo.set(self.config.get("theme", "Light"))
        self.theme_combo.pack(pady=5)

        # --- Subframe 2: Database Maintenance ---
        db_frame = ctk.CTkFrame(right_frame)
        db_frame.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            db_frame,
            text="🗄️ Database Backup & Recovery",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        ctk.CTkLabel(
            db_frame,
            text="Perform database backup or restore point verification below.",
            font=("Arial", 12),
            text_color="gray"
        ).pack(pady=5)

        # Backup Button
        ctk.CTkButton(
            db_frame,
            text="📦 Backup Database (.sql)",
            width=220,
            command=self.backup_database,
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        ).pack(pady=15)

        # Restore Button
        ctk.CTkButton(
            db_frame,
            text="↩️ Restore Database",
            width=220,
            command=self.restore_database,
            fg_color="#D84315",
            hover_color="#BF360C"
        ).pack(pady=15)

    # ==============================
    # Configuration Load / Save
    # ==============================

    def load_config(self):
        """Load configuration settings from JSON."""
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as file:
                    return json.load(file)
            except:
                pass
        return {
            "clinic_name": "Physical Health Clinic",
            "clinic_address": "123 Main Street, Freetown",
            "clinic_phone": "+232-76-123456",
            "clinic_email": "info@physicalhealthclinic.com",
            "currency": "Le",
            "theme": "Light"
        }

    def save_clinic_settings(self):
        """Save the custom clinic settings to configuration JSON."""
        self.config["clinic_name"] = self.clinic_name.get().strip()
        self.config["clinic_address"] = self.clinic_address.get().strip()
        self.config["clinic_phone"] = self.clinic_phone.get().strip()
        self.config["clinic_email"] = self.clinic_email.get().strip()
        self.config["currency"] = self.currency.get().strip()

        try:
            with open(CONFIG_PATH, "w") as file:
                json.dump(self.config, file, indent=4)
            messagebox.showinfo("Success", "Clinic configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configurations:\n{e}")

    def change_theme_mode(self, val):
        """Toggle system appearance mode color instantly."""
        ctk.set_appearance_mode(val)
        self.config["theme"] = val
        try:
            with open(CONFIG_PATH, "w") as file:
                json.dump(self.config, file, indent=4)
        except:
            pass

    # ==============================
    # Database Backup / Restore Point
    # ==============================

    def backup_database(self):
        """Export the database structure and records into a .sql file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL Files", "*.sql")],
            initialfile="clinic_backup.sql"
        )
        if not file_path:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Get list of all tables
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]

            sql_content = []
            sql_content.append(f"-- SQL Database Backup")
            sql_content.append(f"-- Clinic: {self.config.get('clinic_name')}")
            sql_content.append(f"-- Backup Point Generated\n")

            # Loop through tables to generate schema and insertions
            for table in tables:
                sql_content.append(f"-- Table Structure for `{table}`")
                sql_content.append(f"DROP TABLE IF EXISTS `{table}`;")

                # Get create structure
                cursor.execute(f"SHOW CREATE TABLE `{table}`")
                create_stmt = cursor.fetchone()[1]
                sql_content.append(f"{create_stmt};\n")

                # Get insertions
                cursor.execute(f"SELECT * FROM `{table}`")
                rows = cursor.fetchall()
                if rows:
                    sql_content.append(f"-- Data insertions for `{table}`")
                    for row in rows:
                        row_vals = []
                        for val in row:
                            if val is None:
                                row_vals.append("NULL")
                            elif isinstance(val, (int, float)):
                                row_vals.append(str(val))
                            else:
                                # Escape quotes for SQL compatibility
                                clean_val = str(val).replace("'", "''")
                                row_vals.append(f"'{clean_val}'")

                        vals_str = ", ".join(row_vals)
                        sql_content.append(f"INSERT INTO `{table}` VALUES ({vals_str});")
                    sql_content.append("")

            conn.close()

            with open(file_path, "w", encoding="utf-8") as file:
                file.write("\n".join(sql_content))

            messagebox.showinfo("Success", "Clinic database backup generated successfully!")

        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to complete database backup:\n{e}")

    def restore_database(self):
        """Import the records and structures from a selected backup point SQL script."""
        file_path = filedialog.askopenfilename(
            filetypes=[("SQL Files", "*.sql")]
        )
        if not file_path:
            return

        confirm = messagebox.askyesno(
            "Confirm Restore",
            "Are you sure you want to restore? This will override all current database tables and records!"
        )
        if not confirm:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                sql_script = file.read()

            conn = connect_db()
            cursor = conn.cursor()

            # Execute SQL commands
            # Split commands by semicolon, ensuring we skip remarks
            commands = sql_script.split(";")
            for command in commands:
                clean_command = command.strip()
                if clean_command and not clean_command.startswith("--"):
                    cursor.execute(clean_command)

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Clinic records restored from backup point successfully!")

        except Exception as e:
            messagebox.showerror("Restore Error", f"Database restore point failed:\n{e}")


if __name__ == "__main__":
    class TestApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.geometry("1400x800")
            SettingsWindow(self)

    app = TestApp()
    app.mainloop()
