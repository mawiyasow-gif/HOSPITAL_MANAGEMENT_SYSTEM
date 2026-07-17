import customtkinter as ctk
from tkinter import ttk, messagebox
from database import connect_db
from datetime import datetime
import session

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class InventoryWindow(ctk.CTkToplevel):
    """Inventory Management Window for Physical Health Clinic Record System."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Inventory Management")
        self.geometry("1500x850")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        # Track selected ID
        self.selected_inventory_id = None

        # Check current user's role
        self.user_role = "Staff"
        if hasattr(session, "current_user") and session.current_user:
            self.user_role = session.current_user.get("role", "Staff")

        self.is_admin = (self.user_role == "Administrator")

        # Back Button
        back_btn = ctk.CTkButton(
            self,
            text="⬅ Back",
            width=100,
            command=self.destroy
        )
        back_btn.place(x=20, y=20)

        # Title
        title = ctk.CTkLabel(
            self,
            text="📦 Inventory Management" if self.is_admin else "📦 Clinic Stock Viewer",
            font=("Arial", 30, "bold")
        )
        title.pack(pady=20)

        # Main Container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Left Panel (Add/Edit Form - Admin only)
        if self.is_admin:
            self.form_frame = ctk.CTkFrame(main_frame, width=420)
            self.form_frame.pack(side="left", fill="y", padx=15, pady=15)

            ctk.CTkLabel(
                self.form_frame,
                text="Inventory Information",
                font=("Arial", 22, "bold")
            ).pack(pady=20)

            # Medicine Name
            ctk.CTkLabel(self.form_frame, text="Medicine Name:", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(10, 2))
            self.name_entry = ctk.CTkEntry(self.form_frame, width=320, placeholder_text="e.g. Paracetamol 500mg")
            self.name_entry.pack(pady=3)

            # Batch Number
            ctk.CTkLabel(self.form_frame, text="Batch Number:", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(10, 2))
            self.batch_entry = ctk.CTkEntry(self.form_frame, width=320, placeholder_text="e.g. B-PA101")
            self.batch_entry.pack(pady=3)

            # Quantity
            ctk.CTkLabel(self.form_frame, text="Quantity:", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(10, 2))
            self.qty_entry = ctk.CTkEntry(self.form_frame, width=320, placeholder_text="e.g. 500")
            self.qty_entry.pack(pady=3)

            # Cost Price
            ctk.CTkLabel(self.form_frame, text="Cost Price:", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(10, 2))
            self.cost_entry = ctk.CTkEntry(self.form_frame, width=320, placeholder_text="e.g. 1000.00")
            self.cost_entry.pack(pady=3)

            # Selling Price
            ctk.CTkLabel(self.form_frame, text="Selling Price:", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(10, 2))
            self.sell_entry = ctk.CTkEntry(self.form_frame, width=320, placeholder_text="e.g. 1500.00")
            self.sell_entry.pack(pady=3)

            # Expiry Date
            ctk.CTkLabel(self.form_frame, text="Expiry Date (YYYY-MM-DD):", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(10, 2))
            self.expiry_entry = ctk.CTkEntry(self.form_frame, width=320, placeholder_text="YYYY-MM-DD")
            self.expiry_entry.pack(pady=3)

            # Supplier
            ctk.CTkLabel(self.form_frame, text="Supplier:", font=("Arial", 12, "bold")).pack(anchor="w", padx=50, pady=(10, 2))
            self.supplier_entry = ctk.CTkEntry(self.form_frame, width=320, placeholder_text="e.g. Sierra Pharm Ltd")
            self.supplier_entry.pack(pady=3)

            # CRUD Action Buttons
            btn_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
            btn_frame.pack(pady=20)

            ctk.CTkButton(btn_frame, text="➕ Add Item", command=self.add_inventory, width=150).grid(row=0, column=0, padx=5, pady=5)
            ctk.CTkButton(btn_frame, text="✏ Update Item", command=self.update_inventory, width=150).grid(row=0, column=1, padx=5, pady=5)
            ctk.CTkButton(btn_frame, text="❌ Delete Item", command=self.delete_inventory, fg_color="red", hover_color="#b71c1c", width=150).grid(row=1, column=0, padx=5, pady=5)
            ctk.CTkButton(btn_frame, text="🧹 Clear Fields", command=self.clear_fields, width=150).grid(row=1, column=1, padx=5, pady=5)
        else:
            # Read-only notice
            self.form_frame = ctk.CTkFrame(main_frame, width=280)
            self.form_frame.pack(side="left", fill="y", padx=15, pady=15)
            
            ctk.CTkLabel(self.form_frame, text="ℹ️ Access Control", font=("Arial", 16, "bold"), text_color="#1F6AA5").pack(pady=20)
            notice = (
                "You are logged in as a Pharmacist/Staff.\n\n"
                "You have Read-Only access to clinic inventory.\n\n"
                "Only the Administrator can add, update, or remove inventory records."
            )
            ctk.CTkLabel(self.form_frame, text=notice, font=("Arial", 12), justify="left", wraplength=240).pack(padx=20, pady=10)

        # Right Panel (List Stock)
        self.table_frame = ctk.CTkFrame(main_frame)
        self.table_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        # Search Bar
        search_frame = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=15, pady=10)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by Medicine Name or Batch...", width=350)
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.search_inventory)

        ctk.CTkButton(search_frame, text="Search", command=self.search_inventory, width=100).pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="Clear Search", command=self.clear_search, width=100).pack(side="left")

        # Treeview setup
        container = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=15, pady=10)

        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side="right", fill="y")

        columns = ("ID", "Medicine Name", "Batch No", "Quantity", "Cost Price", "Selling Price", "Expiry Date", "Supplier", "Days to Expire")
        self.table = ttk.Treeview(
            container,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=20
        )
        
        # Table Styling
        style = ttk.Style()
        self.table.heading("ID", text="ID", anchor="center")
        self.table.column("ID", width=40, anchor="center")
        
        for col in columns[1:]:
            self.table.heading(col, text=col, anchor="w")
            self.table.column(col, anchor="w", width=130)

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.table.yview)

        # Selection Binds for Admin to Edit
        if self.is_admin:
            self.table.bind("<<TreeviewSelect>>", self.on_row_selected)

        # Load Inventory Data
        self.load_inventory()

    def load_inventory(self):
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT InventoryID, MedicineName, BatchNumber, Quantity, CostPrice, SellingPrice, ExpiryDate, Supplier
                FROM Inventory
                ORDER BY InventoryID DESC
            """)
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                
                # Calculate Days to Expire
                days = self.calculate_days_to_expire(cleaned[6])
                cleaned.append(str(days))
                
                self.table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory:\n{e}")

    def calculate_days_to_expire(self, expiry_str):
        try:
            exp_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            today = datetime.now().date()
            diff = (exp_date - today).days
            return diff
        except:
            return "N/A"

    def search_inventory(self, event=None):
        q = self.search_entry.get().strip()
        if not q:
            self.load_inventory()
            return

        for item in self.table.get_children():
            self.table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT InventoryID, MedicineName, BatchNumber, Quantity, CostPrice, SellingPrice, ExpiryDate, Supplier
                FROM Inventory
                WHERE MedicineName LIKE %s OR BatchNumber LIKE %s
                ORDER BY InventoryID DESC
            """, (f"%{q}%", f"%{q}%"))
            for row in cursor.fetchall():
                cleaned = ["" if val is None else str(val) for val in row]
                days = self.calculate_days_to_expire(cleaned[6])
                cleaned.append(str(days))
                self.table.insert("", "end", values=cleaned)
            conn.close()
        except Exception as e:
            print(f"Error searching inventory: {e}")

    def clear_search(self):
        self.search_entry.delete(0, "end")
        self.load_inventory()

    def on_row_selected(self, event):
        selected = self.table.selection()
        if not selected:
            return
            
        row = self.table.item(selected[0], "values")
        self.selected_inventory_id = row[0]

        # Populate fields
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, row[1])

        self.batch_entry.delete(0, "end")
        self.batch_entry.insert(0, row[2])

        self.qty_entry.delete(0, "end")
        self.qty_entry.insert(0, row[3])

        self.cost_entry.delete(0, "end")
        self.cost_entry.insert(0, row[4])

        self.sell_entry.delete(0, "end")
        self.sell_entry.insert(0, row[5])

        self.expiry_entry.delete(0, "end")
        self.expiry_entry.insert(0, row[6])

        self.supplier_entry.delete(0, "end")
        self.supplier_entry.insert(0, row[7])

    def clear_fields(self):
        self.selected_inventory_id = None
        self.name_entry.delete(0, "end")
        self.batch_entry.delete(0, "end")
        self.qty_entry.delete(0, "end")
        self.cost_entry.delete(0, "end")
        self.sell_entry.delete(0, "end")
        self.expiry_entry.delete(0, "end")
        self.supplier_entry.delete(0, "end")
        self.table.selection_remove(self.table.selection())

    def add_inventory(self):
        name = self.name_entry.get().strip()
        batch = self.batch_entry.get().strip()
        qty_str = self.qty_entry.get().strip()
        cost_str = self.cost_entry.get().strip()
        sell_str = self.sell_entry.get().strip()
        expiry = self.expiry_entry.get().strip()
        supplier = self.supplier_entry.get().strip()

        if not name or not batch or not qty_str or not cost_str or not sell_str or not expiry:
            messagebox.showerror("Validation Error", "All fields except supplier are required.")
            return

        try:
            qty = int(qty_str)
            cost = float(cost_str)
            sell = float(sell_str)
            datetime.strptime(expiry, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Please ensure Quantity is an integer, prices are decimals, and Expiry is YYYY-MM-DD.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Inventory (MedicineName, BatchNumber, Quantity, CostPrice, SellingPrice, ExpiryDate, Supplier)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, batch, qty, cost, sell, expiry, supplier))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Inventory item added successfully!")
            self.load_inventory()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add inventory item:\n{e}")

    def update_inventory(self):
        if not self.selected_inventory_id:
            messagebox.showwarning("Selection Warning", "Please select an item to update.")
            return

        name = self.name_entry.get().strip()
        batch = self.batch_entry.get().strip()
        qty_str = self.qty_entry.get().strip()
        cost_str = self.cost_entry.get().strip()
        sell_str = self.sell_entry.get().strip()
        expiry = self.expiry_entry.get().strip()
        supplier = self.supplier_entry.get().strip()

        if not name or not batch or not qty_str or not cost_str or not sell_str or not expiry:
            messagebox.showerror("Validation Error", "All fields except supplier are required.")
            return

        try:
            qty = int(qty_str)
            cost = float(cost_str)
            sell = float(sell_str)
            datetime.strptime(expiry, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Please ensure Quantity is an integer, prices are decimals, and Expiry is YYYY-MM-DD.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Inventory
                SET MedicineName = %s, BatchNumber = %s, Quantity = %s, CostPrice = %s, SellingPrice = %s, ExpiryDate = %s, Supplier = %s
                WHERE InventoryID = %s
            """, (name, batch, qty, cost, sell, expiry, supplier, self.selected_inventory_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Inventory item updated successfully!")
            self.load_inventory()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update inventory item:\n{e}")

    def delete_inventory(self):
        if not self.selected_inventory_id:
            messagebox.showwarning("Selection Warning", "Please select an item to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this inventory item?")
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Inventory WHERE InventoryID = %s", (self.selected_inventory_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Inventory item deleted successfully!")
            self.load_inventory()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete inventory item:\n{e}")
