# lab_template_manager.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import json
from database import connect_db
import dashboard_theme
import session


class LabTemplateManagerWindow(ctk.CTkToplevel):
    """Administrator Laboratory Template Manager."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # 1. Role-Based Access Control: Exclusive to Administrator
        user_role = getattr(parent, 'admin_user', {}).get("role", "")
        if not user_role and hasattr(session, 'current_user') and session.current_user:
            user_role = session.current_user.get("role", "")

        if user_role != "Administrator":
            messagebox.showerror("Access Denied", "Security Alert: Only Administrators can manage Laboratory Report Templates.")
            self.destroy()
            return

        self.title("🧪 Laboratory Template Manager - Administrator Panel")
        self.geometry("1380x820")
        self.resizable(True, True)
        self.configure(fg_color=dashboard_theme.BG_COLOR)

        self.transient(parent)
        self.grab_set()

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.load_templates())

        self.status_filter_var = ctk.StringVar(value="All Statuses")

        self.setup_ui()
        self.load_templates()

    def setup_ui(self):
        # Top Navigation Bar
        top_nav = ctk.CTkFrame(self, fg_color=dashboard_theme.CARD_BG, height=55, corner_radius=0)
        top_nav.pack(fill="x", side="top")
        top_nav.pack_propagate(False)

        btn_back = ctk.CTkButton(
            top_nav, text="⬅ Back to Admin Dashboard", width=170, height=36,
            fg_color="#1E3A8A", hover_color="#1D4ED8", text_color="#FFFFFF",
            font=("Arial", 12, "bold"), command=self.destroy
        )
        btn_back.pack(side="left", padx=15, pady=8)

        ctk.CTkLabel(
            top_nav, text="🧪 Laboratory Report Template Manager",
            font=("Arial", 17, "bold"), text_color=dashboard_theme.TEXT_PRIMARY
        ).pack(side="left", padx=10)

        # Control & Filter Header Bar
        control_frame = ctk.CTkFrame(self, fg_color=dashboard_theme.CARD_BG, border_color=dashboard_theme.BORDER_COLOR, border_width=1, corner_radius=12)
        control_frame.pack(fill="x", padx=15, pady=12)

        # Search
        search_f = ctk.CTkFrame(control_frame, fg_color="transparent")
        search_f.pack(side="left", padx=15, pady=12)
        ctk.CTkLabel(search_f, text="🔍 Search Templates:", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_f, width=240, textvariable=self.search_var, placeholder_text="Template or Test Name...")
        self.search_entry.pack(side="left", padx=5)

        # Filter
        filter_f = ctk.CTkFrame(control_frame, fg_color="transparent")
        filter_f.pack(side="left", padx=15, pady=12)
        ctk.CTkLabel(filter_f, text="Status:", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        self.status_combo = ctk.CTkComboBox(
            filter_f, values=["All Statuses", "Active", "Inactive"],
            variable=self.status_filter_var, command=lambda e: self.load_templates(), width=130
        )
        self.status_combo.pack(side="left", padx=5)

        # Action Buttons Right
        btn_f = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_f.pack(side="right", padx=15, pady=12)

        ctk.CTkButton(
            btn_f, text="➕ Create New Template", width=170, height=36,
            fg_color="#10B981", hover_color="#059669", font=("Arial", 12, "bold"),
            command=self.open_create_modal
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_f, text="🔄 Refresh", width=100, height=36,
            fg_color=dashboard_theme.ACCENT_BLUE, font=("Arial", 12, "bold"),
            command=self.load_templates
        ).pack(side="left", padx=5)

        # Main Table Container
        main_card = ctk.CTkFrame(self, fg_color="#FFFFFF", border_color=dashboard_theme.BORDER_COLOR, border_width=1, corner_radius=12)
        main_card.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        table_header = ctk.CTkFrame(main_card, fg_color="transparent")
        table_header.pack(fill="x", padx=15, pady=(12, 5))

        ctk.CTkLabel(table_header, text="📋 Configured Laboratory Report Templates", font=("Arial", 14, "bold"), text_color=dashboard_theme.TEXT_PRIMARY).pack(side="left")

        # Bottom Actions Bar inside Main Card
        act_bar = ctk.CTkFrame(table_header, fg_color="transparent")
        act_bar.pack(side="right")

        ctk.CTkButton(act_bar, text="👁️ Preview Report", width=130, fg_color="#6366F1", hover_color="#4F46E5", font=("Arial", 12, "bold"), command=self.preview_selected_template).pack(side="left", padx=4)
        ctk.CTkButton(act_bar, text="⚡ Toggle Active", width=120, fg_color="#F59E0B", hover_color="#D97706", font=("Arial", 12, "bold"), command=self.toggle_template_status).pack(side="left", padx=4)
        ctk.CTkButton(act_bar, text="✏️ Edit Template", width=120, fg_color="#2563EB", hover_color="#1D4ED8", font=("Arial", 12, "bold"), command=self.edit_selected_template).pack(side="left", padx=4)
        ctk.CTkButton(act_bar, text="🗑️ Delete", width=90, fg_color="#EF4444", hover_color="#DC2626", font=("Arial", 12, "bold"), command=self.delete_selected_template).pack(side="left", padx=4)

        # Treeview Table
        table_container = ctk.CTkFrame(main_card, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=15, pady=10)

        scrollbar = ttk.Scrollbar(table_container)
        scrollbar.pack(side="right", fill="y")

        columns = ("ID", "Test Name", "Template Name", "Parameters Count", "Status", "Default Comments")
        self.table = ttk.Treeview(
            table_container, columns=columns, show="headings",
            yscrollcommand=scrollbar.set, selectmode="browse"
        )
        for col in columns:
            self.table.heading(col, text=col, anchor="w")
            self.table.column(col, anchor="w", width=150)
        self.table.column("ID", width=70, anchor="center")
        self.table.column("Parameters Count", width=130, anchor="center")
        self.table.column("Status", width=100, anchor="center")
        self.table.column("Default Comments", width=360)

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.table.yview)

    def load_templates(self):
        for item in self.table.get_children():
            self.table.delete(item)

        search_query = self.search_var.get().strip().lower()
        status_filter = self.status_filter_var.get()

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    tpl.TemplateID, lt.TestName, tpl.TemplateName, tpl.TemplateFields, 
                    tpl.Status, tpl.DefaultComments
                FROM laboratory_templates tpl
                JOIN Laboratory_Tests lt ON tpl.TestID = lt.TestID
                ORDER BY tpl.TemplateID DESC
            """)
            rows = cursor.fetchall()
            conn.close()

            for t_id, t_test, t_name, t_fields, t_status, t_comments in rows:
                if status_filter != "All Statuses" and t_status != status_filter:
                    continue
                if search_query and (search_query not in t_test.lower() and search_query not in t_name.lower()):
                    continue

                fields_cnt = 0
                if t_fields:
                    try:
                        parsed = json.loads(t_fields)
                        fields_cnt = len(parsed) if isinstance(parsed, list) else 0
                    except Exception:
                        fields_cnt = 0

                cleaned_comment = (t_comments or "").replace("\n", " ")[:60]
                self.table.insert("", "end", values=(t_id, t_test, t_name, fields_cnt, t_status, cleaned_comment))
        except Exception as e:
            print(f"Error loading laboratory templates: {e}")

    def open_create_modal(self):
        LabTemplateEditModal(self, template_id=None)

    def edit_selected_template(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a template from the list to edit.")
            return
        t_id = self.table.item(selected[0])['values'][0]
        LabTemplateEditModal(self, template_id=t_id)

    def toggle_template_status(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a template to toggle status.")
            return
        t_id = self.table.item(selected[0])['values'][0]
        curr_status = self.table.item(selected[0])['values'][4]
        new_status = "Inactive" if curr_status == "Active" else "Active"

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE laboratory_templates SET Status = %s WHERE TemplateID = %s", (new_status, t_id))
            conn.commit()
            conn.close()
            self.load_templates()
            messagebox.showinfo("Status Updated", f"Template ID #{t_id} is now {new_status}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update status:\n{e}")

    def delete_selected_template(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a template to delete.")
            return
        t_id = self.table.item(selected[0])['values'][0]
        t_name = self.table.item(selected[0])['values'][2]

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete template '{t_name}' (ID: #{t_id})?")
        if not confirm:
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM laboratory_templates WHERE TemplateID = %s", (t_id,))
            conn.commit()
            conn.close()
            self.load_templates()
            messagebox.showinfo("Success", "Template deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete template:\n{e}")

    def preview_selected_template(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a template to preview.")
            return
        t_id = self.table.item(selected[0])['values'][0]
        messagebox.showinfo("Template Preview", f"Sample live A4 report layout preview for Template ID #{t_id} initialized.")


class LabTemplateEditModal(ctk.CTkToplevel):
    """Modal Window to Create / Edit Laboratory Report Templates."""

    def __init__(self, manager_window, template_id=None):
        super().__init__(manager_window)
        self.manager = manager_window
        self.template_id = template_id

        title_prefix = f"Edit Template ID #{template_id}" if template_id else "Create New Laboratory Template"
        self.title(f"🧪 {title_prefix}")
        self.geometry("900x750")
        self.resizable(True, True)

        self.transient(manager_window)
        self.grab_set()

        self.test_map = {}
        self.parameters = []

        self.setup_ui()
        self.load_tests_dropdown()
        if template_id:
            self.load_template_data()

    def setup_ui(self):
        container = ctk.CTkScrollableFrame(self, fg_color=dashboard_theme.BG_COLOR)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # Header Title
        ctk.CTkLabel(container, text="🧪 Laboratory Report Template Editor", font=("Arial", 18, "bold"), text_color=dashboard_theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 10))

        # Basic Info Card
        info_card = ctk.CTkFrame(container, fg_color="#FFFFFF", border_color=dashboard_theme.BORDER_COLOR, border_width=1, corner_radius=10)
        info_card.pack(fill="x", pady=6, padx=2)

        # Row 1: Test & Template Name
        r1 = ctk.CTkFrame(info_card, fg_color="transparent")
        r1.pack(fill="x", padx=12, pady=10)

        f1 = ctk.CTkFrame(r1, fg_color="transparent")
        f1.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(f1, text="Linked Laboratory Test:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.test_combo = ctk.CTkComboBox(f1, values=["Loading..."], width=300)
        self.test_combo.pack(anchor="w", pady=4)

        f2 = ctk.CTkFrame(r1, fg_color="transparent")
        f2.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(f2, text="Template Name:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.name_entry = ctk.CTkEntry(f2, width=320, placeholder_text="e.g. CBC Standard Panel")
        self.name_entry.pack(anchor="w", pady=4)

        # Row 2: Status & Description
        r2 = ctk.CTkFrame(info_card, fg_color="transparent")
        r2.pack(fill="x", padx=12, pady=(0, 10))

        f3 = ctk.CTkFrame(r2, fg_color="transparent")
        f3.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(f3, text="Template Description:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.desc_entry = ctk.CTkEntry(f3, width=440, placeholder_text="Short description of test panel...")
        self.desc_entry.pack(anchor="w", pady=4)

        f4 = ctk.CTkFrame(r2, fg_color="transparent")
        f4.pack(side="left", padx=5)
        ctk.CTkLabel(f4, text="Status:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.status_combo = ctk.CTkComboBox(f4, values=["Active", "Inactive"], width=130)
        self.status_combo.set("Active")
        self.status_combo.pack(anchor="w", pady=4)

        # Parameters Builder Panel
        param_card = ctk.CTkFrame(container, fg_color="#FFFFFF", border_color=dashboard_theme.BORDER_COLOR, border_width=1, corner_radius=10)
        param_card.pack(fill="x", pady=10, padx=2)

        param_hdr = ctk.CTkFrame(param_card, fg_color="transparent")
        param_hdr.pack(fill="x", padx=12, pady=10)
        ctk.CTkLabel(param_hdr, text="📊 Report Parameter Fields & Normal Reference Ranges", font=("Arial", 14, "bold"), text_color=dashboard_theme.TEXT_PRIMARY).pack(side="left")

        # Entry inputs to add new parameter
        add_f = ctk.CTkFrame(param_card, fg_color="#F8FAFC", corner_radius=8)
        add_f.pack(fill="x", padx=12, pady=(0, 10))

        self.p_name_entry = ctk.CTkEntry(add_f, width=180, placeholder_text="Parameter Name (e.g. WBC)")
        self.p_name_entry.pack(side="left", padx=5, pady=8)

        self.p_unit_entry = ctk.CTkEntry(add_f, width=110, placeholder_text="Unit (e.g. g/dL)")
        self.p_unit_entry.pack(side="left", padx=5, pady=8)

        self.p_range_entry = ctk.CTkEntry(add_f, width=170, placeholder_text="Reference Range (e.g. 4.5-11.0)")
        self.p_range_entry.pack(side="left", padx=5, pady=8)

        self.p_def_entry = ctk.CTkEntry(add_f, width=130, placeholder_text="Default Value")
        self.p_def_entry.pack(side="left", padx=5, pady=8)

        ctk.CTkButton(add_f, text="➕ Add Field", width=100, fg_color="#10B981", hover_color="#059669", font=("Arial", 12, "bold"), command=self.add_parameter_field).pack(side="left", padx=5, pady=8)

        # Parameter Table
        p_table_container = ctk.CTkFrame(param_card, fg_color="transparent")
        p_table_container.pack(fill="x", padx=12, pady=(0, 10))

        p_cols = ("Parameter Name", "Measurement Unit", "Normal Reference Range", "Default Value")
        self.param_table = ttk.Treeview(p_table_container, columns=p_cols, show="headings", height=6)
        for col in p_cols:
            self.param_table.heading(col, text=col, anchor="w")
            self.param_table.column(col, anchor="w", width=180)
        self.param_table.pack(side="left", fill="both", expand=True)

        ctk.CTkButton(param_card, text="🗑️ Remove Selected Field", width=180, fg_color="#EF4444", hover_color="#DC2626", font=("Arial", 11, "bold"), command=self.remove_selected_parameter).pack(anchor="e", padx=12, pady=(0, 10))

        # Default Comments Panel
        comment_card = ctk.CTkFrame(container, fg_color="#FFFFFF", border_color=dashboard_theme.BORDER_COLOR, border_width=1, corner_radius=10)
        comment_card.pack(fill="x", pady=6, padx=2)

        ctk.CTkLabel(comment_card, text="📝 Default Laboratory Interpretation Notes & Comments:", font=("Arial", 12, "bold")).pack(anchor="w", padx=12, pady=(10, 4))
        self.comments_text = ctk.CTkTextbox(comment_card, height=75)
        self.comments_text.pack(fill="x", padx=12, pady=(0, 10))

        # Footer Action Controls
        ft_btn = ctk.CTkFrame(container, fg_color="transparent")
        ft_btn.pack(fill="x", pady=15)

        ctk.CTkButton(ft_btn, text="💾 Save Template", width=180, height=40, fg_color="#10B981", hover_color="#059669", font=("Arial", 13, "bold"), command=self.save_template).pack(side="right", padx=10)
        ctk.CTkButton(ft_btn, text="Cancel", width=110, height=40, fg_color="#64748B", hover_color="#475569", font=("Arial", 13, "bold"), command=self.destroy).pack(side="right", padx=5)

    def load_tests_dropdown(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT TestID, TestName FROM Laboratory_Tests ORDER BY TestName ASC")
            rows = cursor.fetchall()
            conn.close()

            self.test_map = {name: t_id for t_id, name in rows}
            test_names = list(self.test_map.keys())
            if test_names:
                self.test_combo.configure(values=test_names)
                self.test_combo.set(test_names[0])
        except Exception as e:
            print(f"Error loading tests dropdown: {e}")

    def add_parameter_field(self):
        name = self.p_name_entry.get().strip()
        unit = self.p_unit_entry.get().strip()
        range_val = self.p_range_entry.get().strip()
        def_val = self.p_def_entry.get().strip()

        if not name:
            messagebox.showwarning("Warning", "Parameter Name cannot be empty.")
            return

        self.param_table.insert("", "end", values=(name, unit, range_val, def_val))
        self.p_name_entry.delete(0, "end")
        self.p_unit_entry.delete(0, "end")
        self.p_range_entry.delete(0, "end")
        self.p_def_entry.delete(0, "end")

    def remove_selected_parameter(self):
        selected = self.param_table.selection()
        if not selected:
            return
        for item in selected:
            self.param_table.delete(item)

    def load_template_data(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tpl.TestID, lt.TestName, tpl.TemplateName, tpl.TemplateDescription, 
                       tpl.TemplateFields, tpl.DefaultComments, tpl.Status
                FROM laboratory_templates tpl
                JOIN Laboratory_Tests lt ON tpl.TestID = lt.TestID
                WHERE tpl.TemplateID = %s
            """, (self.template_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                t_id, t_test, t_name, desc, fields_json, comments, status = row
                self.test_combo.set(t_test)
                self.name_entry.insert(0, t_name)
                self.desc_entry.insert(0, desc or "")
                self.status_combo.set(status)
                if comments:
                    self.comments_text.insert("1.0", comments)

                if fields_json:
                    try:
                        fields = json.loads(fields_json)
                        for f in fields:
                            self.param_table.insert("", "end", values=(
                                f.get("name", ""), f.get("unit", ""), f.get("range", ""), f.get("default", "")
                            ))
                    except Exception:
                        pass
        except Exception as e:
            print(f"Error loading template data: {e}")

    def save_template(self):
        test_name = self.test_combo.get()
        test_id = self.test_map.get(test_name)
        template_name = self.name_entry.get().strip()
        description = self.desc_entry.get().strip()
        status = self.status_combo.get()
        default_comments = self.comments_text.get("1.0", "end-1c").strip()

        if not test_id or not template_name:
            messagebox.showwarning("Warning", "Please select a Linked Test and enter a Template Name.")
            return

        # Build fields list
        fields_list = []
        ranges_dict = {}
        units_dict = {}
        for child in self.param_table.get_children():
            vals = self.param_table.item(child)['values']
            p_name, p_unit, p_range, p_def = vals[0], vals[1], vals[2], vals[3]
            fields_list.append({"name": p_name, "unit": p_unit, "range": p_range, "default": p_def})
            ranges_dict[p_name] = p_range
            units_dict[p_name] = p_unit

        fields_json = json.dumps(fields_list)
        ranges_json = json.dumps(ranges_dict)
        units_json = json.dumps(units_dict)

        user_id = session.current_user.get("user_id", 1) if (session and hasattr(session, 'current_user') and session.current_user) else 1

        try:
            conn = connect_db()
            cursor = conn.cursor()
            if self.template_id:
                cursor.execute("""
                    UPDATE laboratory_templates
                    SET TestID = %s, TemplateName = %s, TemplateDescription = %s,
                        TemplateFields = %s, ReferenceRanges = %s, MeasurementUnits = %s,
                        DefaultComments = %s, Status = %s
                    WHERE TemplateID = %s
                """, (test_id, template_name, description, fields_json, ranges_json, units_json, default_comments, status, self.template_id))
                msg = "Template updated successfully!"
            else:
                cursor.execute("""
                    INSERT INTO laboratory_templates (
                        TestID, TemplateName, TemplateDescription, TemplateFields,
                        ReferenceRanges, MeasurementUnits, DefaultComments, Status, CreatedBy
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (test_id, template_name, description, fields_json, ranges_json, units_json, default_comments, status, user_id))
                msg = "New Laboratory Template created successfully!"

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", msg)
            self.manager.load_templates()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save laboratory template:\n{e}")
