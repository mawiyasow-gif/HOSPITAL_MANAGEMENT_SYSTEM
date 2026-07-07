import customtkinter as ctk
from tkinter import ttk, messagebox
from database import connect_db
from datetime import datetime, date

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class InventoryWindow(ctk.CTkToplevel):
    """Inventory Management Window for Physical Health Clinic Record System."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Inventory Management")
        self.geometry("1500x850")
        self.resizable(True, True)

        # Track selected inventory ID for updates and deletes
        self.selected_inventory_id = None

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
            text="📦 Inventory Management",
            font=("Arial", 30, "bold")
        )
        title.pack(pady=20)

        # ==============================
        # Main Frame
        # ==============================

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ==============================
        # Left Panel (Inventory Form)
        # ==============================

        form_frame = ctk.CTkFrame(main_frame, width=420)
        form_frame.pack(side="left", fill="y", padx=15, pady=15)

        ctk.CTkLabel(
            form_frame,
            text="Inventory Information",
            font=("Arial", 22, "bold")
        ).pack(pady=20)

        # Item Name Entry
        ctk.CTkLabel(
            form_frame,
            text="Item Name:",
            font=("Arial", 14)
        ).pack(pady=(10, 2), anchor="w", padx=50)

        self.item_name_entry = ctk.CTkEntry(
            form_frame,
            width=320,
            placeholder_text="e.g., Paracetamol"
        )
        self.item_name_entry.pack(pady=5)

        # Quantity Entry
        ctk.CTkLabel(
            form_frame,
            text="Quantity:",
            font=("Arial", 14)
        ).pack(pady=(10, 2), anchor="w", padx=50)

        self.quantity_entry = ctk.CTkEntry(
            form_frame,
            width=320,
            placeholder_text="e.g., 100"
        )
        self.quantity_entry.pack(pady=5)

        # Unit Price Entry
        ctk.CTkLabel(
            form_frame,
            text="Unit Price:",
            font=("Arial", 14)
        ).pack(pady=(10, 2), anchor="w", padx=50)

        self.unit_price_entry = ctk.CTkEntry(
            form_frame,
            width=320,
            placeholder_text="e.g., 10"
        )
        self.unit_price_entry.pack(pady=5)

        # Expiry Date Entry
        ctk.CTkLabel(
            form_frame,
            text="Expiry Date (YYYY-MM-DD):",
            font=("Arial", 14)
        ).pack(pady=(10, 2), anchor="w", padx=50)

        self.expiry_date_entry = ctk.CTkEntry(
            form_frame,
            width=320,
            placeholder_text="YYYY-MM-DD"
        )
        self.expiry_date_entry.pack(pady=5)

        # ==============================
        # Action Buttons
        # ==============================

        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=25)

        ctk.CTkButton(
            button_frame,
            text="➕ Add Item",
            width=140,
            command=self.add_inventory
        ).grid(row=0, column=0, padx=5, pady=5)

        ctk.CTkButton(
            button_frame,
            text="✏ Update",
            width=140,
            command=self.update_inventory
        ).grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkButton(
            button_frame,
            text="❌ Delete",
            width=140,
            command=self.delete_inventory
        ).grid(row=1, column=0, padx=5, pady=5)

        ctk.CTkButton(
            button_frame,
            text="🧹 Clear",
            width=140,
            command=self.clear_fields
        ).grid(row=1, column=1, padx=5, pady=5)

        # Sales Button
        ctk.CTkButton(
            button_frame,
            text="💰 Sell Item",
 width=140,
            command=self.sell_item
        ).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # ==============================
        # Right Panel (Treeview Table)
        # ==============================

        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        # Search bar at top of right panel
        search_frame = ctk.CTkFrame(table_frame)
        search_frame.pack(fill="x", pady=10)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=300,
            placeholder_text="Search Inventory..."
        )
        self.search_entry.pack(side="left", padx=10)

        ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_inventory
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="Refresh",
            command=self.refresh_table
        ).pack(side="left", padx=5)

        # Inventory count label
        self.count_label = ctk.CTkLabel(
            search_frame,
            text="Total Items: 0",
            font=("Arial", 14, "bold"),
            text_color="#1F6AA5"
        )
        self.count_label.pack(side="right", padx=20)

        # Treeview columns
        columns = (
            "Inventory ID",
            "Item Name",
            "Quantity",
            "Stock",
            "Unit Price",
            "Expiry Date",
            "Days Until Expiry"
        )

        # Style Treeview table (dark theme consistent with other modules)
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

        # Create Treeview widget
        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=20
        )

        for col in columns:
            self.table.heading(col, text=col, anchor="center")
            self.table.column(col, width=120, anchor="center")

        # Make Item Name column wider
        self.table.column("Item Name", width=200, anchor="center")

        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )

        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.table.xview
        )

        self.table.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )

        # Configure color tags for treeview rows
        self.table.tag_configure("expired", background="#8B0000", foreground="white")
        self.table.tag_configure("warning", background="#B8860B", foreground="white")
        self.table.tag_configure("low_stock", background="#FF8C00", foreground="white")
        self.table.tag_configure("normal", background="#2b2b2b", foreground="white")

        # Pack scrollbars and treeview
        h_scrollbar.pack(side="bottom", fill="x")
        self.table.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")

        # Bind row selection to populate the form
        self.table.bind("<<TreeviewSelect>>", self.select_inventory)

        # ==============================
        # Color Legend
        # ==============================

        legend_frame = ctk.CTkFrame(table_frame)
        legend_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            legend_frame,
            text="Color Legend:",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=10)

        # Expired legend
        expired_frame = ctk.CTkFrame(legend_frame, width=20, height=20, fg_color="#8B0000")
        expired_frame.pack(side="left", padx=5)
        ctk.CTkLabel(
            legend_frame,
            text="Expired",
            font=("Arial", 12)
        ).pack(side="left", padx=2)

        # Expiring soon legend
        warning_frame = ctk.CTkFrame(legend_frame, width=20, height=20, fg_color="#B8860B")
        warning_frame.pack(side="left", padx=5)
        ctk.CTkLabel(
            legend_frame,
            text="Expiring Soon (≤30 days)",
            font=("Arial", 12)
        ).pack(side="left", padx=2)

        # Low stock legend
        low_stock_frame = ctk.CTkFrame(legend_frame, width=20, height=20, fg_color="#FF8C00")
        low_stock_frame.pack(side="left", padx=5)
        ctk.CTkLabel(
            legend_frame,
            text="Low Stock (<10)",
            font=("Arial", 12)
        ).pack(side="left", padx=2)

        # Normal legend
        normal_frame = ctk.CTkFrame(legend_frame, width=20, height=20, fg_color="#2b2b2b")
        normal_frame.pack(side="left", padx=5)
        ctk.CTkLabel(
            legend_frame,
            text="Normal",
            font=("Arial", 12)
        ).pack(side="left", padx=2)

        # Load initial data into Treeview
        self.load_inventory()

    # ==============================
    # Helper Methods
    # ==============================

    def extract_id(self, combo_value):
        """Extract the integer ID from a ComboBox display string like '1 - Paracetamol'."""
        if not combo_value:
            return None
        try:
            parts = combo_value.split(" - ")
            return int(parts[0])
        except Exception:
            return None

    def calculate_days_until_expiry(self, expiry_date_str):
        """Calculate the number of days until expiry from today."""
        try:
            if not expiry_date_str:
                return "N/A"
            expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            today = date.today()
            delta = expiry_date - today
            return delta.days
        except Exception:
            return "N/A"

    def get_expiry_status_color(self, days_until_expiry):
        """Return color tag based on expiry status."""
        if days_until_expiry == "N/A":
            return "white"
        try:
            days = int(days_until_expiry)
            if days < 0:
                return "expired"  # Red for expired
            elif days <= 30:
                return "warning"  # Yellow for expiring soon
            else:
                return "normal"  # Green for normal
        except Exception:
            return "white"

    def get_stock_status_color(self, quantity):
        """Return color tag based on stock level."""
        try:
            qty = int(quantity)
            if qty < 10:
                return "low_stock"  # Orange for low stock
            else:
                return "normal"  # Normal for adequate stock
        except Exception:
            return "normal"

    # ==============================
    # Data Loading Methods
    # ==============================

    def load_inventory(self):
        """Fetch all inventory records from the database and populate the Treeview."""
        # Clear existing items in the treeview
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT 
                    i.InventoryID,
                    i.ItemName,
                    i.Quantity,
                    i.Stock,
                    i.UnitPrice,
                    i.ExpiryDate
                FROM Inventory i
                ORDER BY i.InventoryID DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            item_count = 0
            for row in rows:
                item_count += 1
                cleaned_row = ["" if val is None else str(val) for val in row]
                
                # Calculate days until expiry
                days_until_expiry = self.calculate_days_until_expiry(cleaned_row[5])
                cleaned_row.append(str(days_until_expiry))
                
                # Insert into treeview
                item_id = self.table.insert("", "end", values=cleaned_row)
                
                # Apply color tags based on expiry and stock status
                expiry_color = self.get_expiry_status_color(days_until_expiry)
                stock_color = self.get_stock_status_color(cleaned_row[3])
                
                # Priority: expired > low stock > normal
                if expiry_color == "expired":
                    self.table.item(item_id, tags=("expired",))
                elif expiry_color == "warning":
                    self.table.item(item_id, tags=("warning",))
                elif stock_color == "low_stock":
                    self.table.item(item_id, tags=("low_stock",))
                else:
                    self.table.item(item_id, tags=("normal",))

            # Update count label
            self.count_label.configure(text=f"Total Items: {item_count}")
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load inventory:\n{e}")

    # ==============================
    # CRUD Operations
    # ==============================

    def add_inventory(self):
        """Validate all fields and save a new inventory record to MySQL."""
        item_name = self.item_name_entry.get().strip()
        quantity_str = self.quantity_entry.get().strip()
        unit_price_str = self.unit_price_entry.get().strip()
        expiry_date = self.expiry_date_entry.get().strip()

        # Validate all required fields are filled
        if not item_name:
            messagebox.showerror("Validation Error", "Please enter the item name.")
            return
        if not quantity_str:
            messagebox.showerror("Validation Error", "Please enter the quantity.")
            return
        if not unit_price_str:
            messagebox.showerror("Validation Error", "Please enter the unit price.")
            return
        if not expiry_date:
            messagebox.showerror("Validation Error", "Please enter the expiry date.")
            return

        # Validate quantity is numeric and not negative
        try:
            quantity = float(quantity_str)
            if quantity < 0:
                messagebox.showerror("Validation Error", "Quantity cannot be negative.")
                return
            # Convert to integer if it's a whole number
            if quantity == int(quantity):
                quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Validation Error", "Quantity must be a valid number.")
            return

        # Validate unit price is numeric and not negative
        try:
            unit_price = float(unit_price_str)
            if unit_price < 0:
                messagebox.showerror("Validation Error", "Unit price cannot be negative.")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Unit price must be a valid number.")
            return

        # Validate expiry date format (YYYY-MM-DD)
        try:
            datetime.strptime(expiry_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "Validation Error",
                "Invalid date format. Please use YYYY-MM-DD."
            )
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                INSERT INTO Inventory (ItemName, Quantity, Stock, UnitPrice, ExpiryDate)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (item_name, quantity, quantity, unit_price, expiry_date))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Inventory item added successfully!")
            self.load_inventory()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add inventory item:\n{e}")

    def update_inventory(self):
        """Update the selected inventory record in the database."""
        if not self.selected_inventory_id:
            messagebox.showwarning(
                "Selection Warning",
                "Please select an inventory item from the table to update."
            )
            return

        item_name = self.item_name_entry.get().strip()
        quantity_str = self.quantity_entry.get().strip()
        unit_price_str = self.unit_price_entry.get().strip()
        expiry_date = self.expiry_date_entry.get().strip()

        # Validate all required fields
        if not item_name:
            messagebox.showerror("Validation Error", "Please enter the item name.")
            return
        if not quantity_str:
            messagebox.showerror("Validation Error", "Please enter the quantity.")
            return
        if not unit_price_str:
            messagebox.showerror("Validation Error", "Please enter the unit price.")
            return
        if not expiry_date:
            messagebox.showerror("Validation Error", "Please enter the expiry date.")
            return

        # Validate quantity is numeric and not negative
        try:
            quantity = float(quantity_str)
            if quantity < 0:
                messagebox.showerror("Validation Error", "Quantity cannot be negative.")
                return
            if quantity == int(quantity):
                quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Validation Error", "Quantity must be a valid number.")
            return

        # Validate unit price is numeric and not negative
        try:
            unit_price = float(unit_price_str)
            if unit_price < 0:
                messagebox.showerror("Validation Error", "Unit price cannot be negative.")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Unit price must be a valid number.")
            return

        # Validate expiry date format (YYYY-MM-DD)
        try:
            datetime.strptime(expiry_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "Validation Error",
                "Invalid date format. Please use YYYY-MM-DD."
            )
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                UPDATE Inventory
                SET ItemName = %s, Quantity = %s, Stock = %s, UnitPrice = %s, ExpiryDate = %s
                WHERE InventoryID = %s
            """
            # Get current stock to preserve it during update
            cursor.execute("SELECT Stock FROM Inventory WHERE InventoryID = %s", (self.selected_inventory_id,))
            current_stock = cursor.fetchone()[0]
            cursor.execute(query, (
                item_name, quantity, current_stock, unit_price, expiry_date,
                self.selected_inventory_id
            ))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Inventory item updated successfully!")
            self.load_inventory()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update inventory item:\n{e}")

    def delete_inventory(self):
        """Delete the selected inventory record after user confirmation."""
        if not self.selected_inventory_id:
            messagebox.showwarning(
                "Selection Warning",
                "Please select an inventory item from the table to delete."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this inventory item?"
        )
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = "DELETE FROM Inventory WHERE InventoryID = %s"
            cursor.execute(query, (self.selected_inventory_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Inventory item deleted successfully!")
            self.load_inventory()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete inventory item:\n{e}")

    # ==============================
    # Search, Select, Clear, Refresh
    # ==============================

    def search_inventory(self):
        """Search inventory by Item Name, Treatment Name, or Expiry Date.
        Displays only matching records in the Treeview."""
        search_query = self.search_entry.get().strip()
        if not search_query:
            self.load_inventory()
            return

        # Clear existing items in treeview
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            query = """
                SELECT 
                    i.InventoryID,
                    i.ItemName,
                    i.Quantity,
                    i.Stock,
                    i.UnitPrice,
                    i.ExpiryDate
                FROM Inventory i
                WHERE i.ItemName LIKE %s
                   OR i.ExpiryDate LIKE %s
                ORDER BY i.InventoryID DESC
            """
            like_val = f"%{search_query}%"
            cursor.execute(query, (like_val, like_val))
            rows = cursor.fetchall()

            item_count = 0
            for row in rows:
                item_count += 1
                cleaned_row = ["" if val is None else str(val) for val in row]
                
                # Calculate days until expiry
                days_until_expiry = self.calculate_days_until_expiry(cleaned_row[5])
                cleaned_row.append(str(days_until_expiry))
                
                # Insert into treeview
                item_id = self.table.insert("", "end", values=cleaned_row)
                
                # Apply color tags based on expiry and stock status
                expiry_color = self.get_expiry_status_color(days_until_expiry)
                stock_color = self.get_stock_status_color(cleaned_row[3])
                
                if expiry_color == "expired":
                    self.table.tag_configure("expired", background="#8B0000", foreground="white")
                    self.table.item(item_id, tags=("expired",))
                elif expiry_color == "warning":
                    self.table.tag_configure("warning", background="#B8860B", foreground="white")
                    self.table.item(item_id, tags=("warning",))
                elif stock_color == "low_stock":
                    self.table.tag_configure("low_stock", background="#FF8C00", foreground="white")
                    self.table.item(item_id, tags=("low_stock",))
                else:
                    self.table.tag_configure("normal", background="#2b2b2b", foreground="white")
                    self.table.item(item_id, tags=("normal",))

            # Update count label
            self.count_label.configure(text=f"Total Items: {item_count}")
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to search inventory:\n{e}")

    def select_inventory(self, event=None):
        """When a row in the Treeview is clicked, load all its data into the form fields."""
        selected_item = self.table.selection()
        if not selected_item:
            return

        row_values = self.table.item(selected_item[0], "values")
        if not row_values:
            return

        # Store the selected inventory ID
        self.selected_inventory_id = row_values[0]

        # Set the Item Name
        self.item_name_entry.delete(0, "end")
        self.item_name_entry.insert(0, row_values[1])

        # Set the Quantity
        self.quantity_entry.delete(0, "end")
        self.quantity_entry.insert(0, row_values[2])

        # Set the Unit Price
        self.unit_price_entry.delete(0, "end")
        self.unit_price_entry.insert(0, row_values[4])

        # Set the Expiry Date
        self.expiry_date_entry.delete(0, "end")
        self.expiry_date_entry.insert(0, row_values[5])

    def clear_fields(self):
        """Clear all form fields and reset the ComboBoxes and Treeview selection."""
        self.selected_inventory_id = None

        # Clear the Item Name field
        self.item_name_entry.delete(0, "end")

        # Clear the Quantity field
        self.quantity_entry.delete(0, "end")

        # Clear the Unit Price field
        self.unit_price_entry.delete(0, "end")

        # Clear the Expiry Date field
        self.expiry_date_entry.delete(0, "end")

        # Clear the search entry
        self.search_entry.delete(0, "end")

        # Remove Treeview selection highlight
        self.table.selection_remove(self.table.selection())

    def refresh_table(self):
        """Reload all inventory records from the database into the Treeview."""
        self.load_inventory()

    def sell_item(self):
        """Sell an item by reducing its quantity in the inventory."""
        if not self.selected_inventory_id:
            messagebox.showwarning(
                "Selection Warning",
                "Please select an inventory item from the table to sell."
            )
            return

        # Ask for quantity to sell
        sell_quantity_str = ctk.CTkInputDialog(
            text="Enter quantity to sell:",
            title="Sell Item"
        ).get_input()

        if not sell_quantity_str:
            return

        try:
            sell_quantity = int(sell_quantity_str)
            if sell_quantity <= 0:
                messagebox.showerror("Validation Error", "Quantity must be greater than 0.")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid number.")
            return

        # Get current quantity from the selected row
        selected_item = self.table.selection()
        if not selected_item:
            return

        row_values = self.table.item(selected_item[0], "values")
        current_stock = int(row_values[3])

        if sell_quantity > current_stock:
            messagebox.showerror(
                "Validation Error",
                f"Cannot sell {sell_quantity} items. Only {current_stock} available in stock."
            )
            return

        # Confirm sale
        confirm = messagebox.askyesno(
            "Confirm Sale",
            f"Are you sure you want to sell {sell_quantity} {row_values[1]}?"
        )
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # Update stock in database
            new_stock = current_stock - sell_quantity
            query = "UPDATE Inventory SET Stock = %s WHERE InventoryID = %s"
            cursor.execute(query, (new_stock, self.selected_inventory_id))
            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success",
                f"Successfully sold {sell_quantity} {row_values[1]}!\nRemaining stock: {new_stock}"
            )
            self.load_inventory()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to sell item:\n{e}")


if __name__ == "__main__":
    class TestApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.geometry("1500x850")
            InventoryWindow(self)

    app = TestApp()
    app.mainloop()
