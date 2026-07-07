import customtkinter as ctk
from patients import PatientWindow

# -----------------------------
# CustomTkinter Settings
# -----------------------------
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class Dashboard(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Physical Health Clinic Record System")
        self.geometry("1600x900")
        self.resizable(True, True)

        # ==========================
        # Sidebar
        # ==========================

        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=20
        )

        self.sidebar.pack(
            side="left",
            fill="y",
            padx=20,
            pady=20
        )

        title = ctk.CTkLabel(
            self.sidebar,
            text="🏥 Clinic System",
            font=("Arial", 24, "bold")
        )

        title.pack(pady=(30, 25))

        menu = [
            "Dashboard",
            "Patients",
            "Health Workers",
            "Appointments",
            "Diagnosis",
            "Treatments",
            "Inventory",
            "Payments",
            "Receipts",
            "Logout"
        ]

        for item in menu:

            if item == "Patients":
                button = ctk.CTkButton(
                    self.sidebar,
                    text="Patients",
                    width=210,
                    height=45,
                    font=("Arial", 16),
                    command=self.open_patients
                )

            elif item == "Health Workers":
                button = ctk.CTkButton(
                    self.sidebar,
                    text="Health Workers",
                    width=210,
                    height=45,
                    font=("Arial", 16),
                    command=self.open_health_workers
                )

            elif item == "Appointments":
                button = ctk.CTkButton(
                    self.sidebar,
                    text="Appointments",
                    width=210,
                    height=45,
                    font=("Arial", 16),
                    command=self.open_appointments
                )

            elif item == "Diagnosis":
                button = ctk.CTkButton(
                    self.sidebar,
                    text="Diagnosis",
                    width=210,
                    height=45,
                    font=("Arial", 16),
                    command=self.open_diagnosis
                )

            elif item == "Treatments":
                button = ctk.CTkButton(
                    self.sidebar,
                    text="Treatments",
                    width=210,
                    height=45,
                    font=("Arial", 16),
                    command=self.open_treatments
                )

            elif item == "Inventory":
                button = ctk.CTkButton(
                    self.sidebar,
                    text="Inventory",
                    width=210,
                    height=45,
                    font=("Arial", 16),
                    command=self.open_inventory
                )

            elif item == "Payments":
                button = ctk.CTkButton(
                    self.sidebar,
                    text="Payments",
                    width=210,
                    height=45,
                    font=("Arial", 16),
                    command=self.open_payments
                )

            elif item == "Receipts":
                button = ctk.CTkButton(
                    self.sidebar,
                    text="Receipts",
                    width=210,
                    height=45,
                    font=("Arial", 16),
                    command=self.open_receipts
                )

            else:
                button = ctk.CTkButton(
                    self.sidebar,
                    text=item,
                    width=210,
                    height=45,
                    font=("Arial", 16)
                )

            button.pack(pady=8)

        # ==========================
        # Main Frame
        # ==========================

        self.main = ctk.CTkFrame(
            self,
            corner_radius=20
        )

        self.main.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 20),
            pady=20
        )

        heading = ctk.CTkLabel(
            self.main,
            text="Dashboard",
            font=("Arial", 36, "bold")
        )

        heading.pack(pady=(30, 10))

        welcome = ctk.CTkLabel(
            self.main,
            text="Welcome to the Physical Health Clinic Record System",
            font=("Arial", 20)
        )

        welcome.pack(pady=(0, 30))

        # ==========================
        # Dashboard Cards
        # ==========================

        cards = ctk.CTkFrame(
            self.main,
            fg_color="transparent"
        )

        cards.pack(
            expand=True,
            fill="both",
            padx=40,
            pady=20
        )

        for i in range(3):
            cards.grid_columnconfigure(i, weight=1)

        self.create_card(cards, "👨 Patients", "20", 0, 0)
        self.create_card(cards, "👩‍⚕️ Health Workers", "15", 0, 1)
        self.create_card(cards, "📅 Appointments", "18", 0, 2)

        self.create_card(cards, "💊 Treatments", "12", 1, 0)
        self.create_card(cards, "📦 Inventory", "150", 1, 1)
        self.create_card(cards, "💰 Payments", "Le25,000", 1, 2)

    # =========================================
    # Card Function
    # =========================================

    def create_card(self, parent, title, value, row, column):

        card = ctk.CTkFrame(
            parent,
            width=320,
            height=200,
            corner_radius=20
        )

        card.grid(
            row=row,
            column=column,
            padx=25,
            pady=25,
            sticky="nsew"
        )

        card.grid_propagate(False)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 22, "bold")
        )

        title_label.pack(pady=(35, 15))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 48, "bold"),
            text_color="#1F6AA5"
        )

        value_label.pack()

    def open_patients(self):
        from patients import PatientWindow
        PatientWindow(self)

    def open_health_workers(self):
        from health_workers import HealthWorkerWindow
        HealthWorkerWindow(self)

    def open_appointments(self):
        from appointments import AppointmentWindow
        AppointmentWindow(self)

    def open_diagnosis(self):
        from diagnosis import DiagnosisWindow
        DiagnosisWindow(self)

    def open_treatments(self):
        from treatment import TreatmentWindow
        TreatmentWindow(self)

    def open_inventory(self):
        from inventory import InventoryWindow
        InventoryWindow(self)

    def open_payments(self):
        from payment import PaymentWindow
        PaymentWindow(self)

    def open_receipts(self):
        from receipt import ReceiptWindow
        ReceiptWindow(self)

if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()