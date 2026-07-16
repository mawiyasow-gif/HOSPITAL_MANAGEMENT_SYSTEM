# dashboard_theme.py
import customtkinter as ctk
from tkinter import ttk

# Modern Light Theme Design Tokens
BG_COLOR = "#F8FAFC"       # Clean light slate-grey background
CARD_BG = "#FFFFFF"        # Pure white card background
BORDER_COLOR = "#E2E8F0"   # Soft slate grey borders
TEXT_PRIMARY = "#0F172A"   # Deep dark slate text
TEXT_SECONDARY = "#64748B" # Slate grey secondary text
ACCENT_BLUE = "#2563EB"    # Vibrant primary blue
ACCENT_BLUE_HOVER = "#1D4ED8"
ACCENT_GREEN = "#10B981"   # Success green
ACCENT_RED = "#EF4444"     # Danger/Alert red
ACCENT_ORANGE = "#F59E0B"  # Warning orange
ACCENT_PURPLE = "#8B5CF6"  # Info purple

def apply_global_theme():
    """Apply global light appearance mode and blue theme."""
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")
    
    # Configure ttk.Treeview styles universally
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Treeview",
        background="#FFFFFF",
        foreground="#1E293B",
        fieldbackground="#FFFFFF",
        rowheight=35,
        font=("Arial", 11)
    )
    style.configure(
        "Treeview.Heading",
        background="#F1F5F9",
        foreground="#475569",
        font=("Arial", 11, "bold"),
        relief="flat"
    )
    style.map(
        "Treeview",
        background=[("selected", "#E2E8F0")],
        foreground=[("selected", "#0F172A")]
    )

def get_light_bg(color_hex):
    """Return a standard 6-digit hex light tint background for an accent color."""
    c = color_hex.upper()
    mapping = {
        "#4CAF50": "#E8F5E9",  # Green
        "#2196F3": "#E3F2FD",  # Blue
        "#2563EB": "#DBEAFE",  # Accent Blue
        "#FF9800": "#FFF3E0",  # Orange
        "#E91E63": "#FCE4EC",  # Pink
        "#9C27B0": "#F3E5F5",  # Purple
        "#00BCD4": "#E0F7FA",  # Cyan
        "#FF5722": "#FBE9E7",  # Deep Orange
        "#795548": "#EFEBE9",  # Brown
        "#EF4444": "#FEE2E2",  # Red
    }
    return mapping.get(c, "#F1F5F9")  # fallback to soft grey

def create_modern_stat_card(parent, icon, title, value, color_hex, command=None, height=130):
    """Create a highly rounded, bordered stat card matching the modern design."""
    card = ctk.CTkFrame(
        parent, 
        fg_color=CARD_BG, 
        border_color=BORDER_COLOR, 
        border_width=1, 
        corner_radius=15,
        height=height
    )
    card.pack_propagate(False)
    
    # Left container for vertical alignment of card elements
    content_frame = ctk.CTkFrame(card, fg_color="transparent")
    content_frame.pack(fill="both", expand=True, padx=15, pady=12)
    
    # Top Row: Icon inside a soft-tint circular frame
    icon_bg = ctk.CTkFrame(
        content_frame, 
        width=36, 
        height=36, 
        corner_radius=18, 
        fg_color=get_light_bg(color_hex)
    )
    icon_bg.pack(anchor="w", pady=(0, 4))
    icon_bg.pack_propagate(False)
    
    icon_lbl = ctk.CTkLabel(icon_bg, text=icon, font=("Arial", 16), text_color=color_hex)
    icon_lbl.place(relx=0.5, rely=0.5, anchor="center")
    
    # Title Label
    title_lbl = ctk.CTkLabel(
        content_frame, 
        text=title.upper(), 
        font=("Arial", 10, "bold"), 
        text_color=TEXT_SECONDARY
    )
    title_lbl.pack(anchor="w", pady=1)
    
    # Value Label
    value_lbl = ctk.CTkLabel(
        content_frame, 
        text=str(value), 
        font=("Arial", 24, "bold"), 
        text_color=TEXT_PRIMARY
    )
    value_lbl.pack(anchor="w", pady=1)
    
    card.value_label = value_lbl
    
    # Bind commands for click interactions if command is supplied
    if command:
        card.configure(cursor="hand2")
        for widget in [card, content_frame, icon_bg, icon_lbl, title_lbl, value_lbl]:
            widget.bind("<Button-1>", lambda e: command())
            
    return card

def style_sidebar(sidebar_frame):
    """Style the left sidebar panel with pure white and subtle divider border."""
    sidebar_frame.configure(
        fg_color="#FFFFFF",
        border_color=BORDER_COLOR,
        border_width=1
    )

def create_sidebar_button(parent, text, command, image=None, active=False):
    """Create a modern rounded button for left navigation sidebar."""
    if active:
        bg = ACCENT_BLUE
        text_col = "#FFFFFF"
        hover_bg = ACCENT_BLUE_HOVER
    else:
        bg = "transparent"
        text_col = TEXT_PRIMARY
        hover_bg = "#F1F5F9"
        
    btn = ctk.CTkButton(
        parent,
        text=text,
        command=command,
        image=image,
        width=210,
        height=40,
        corner_radius=8,
        fg_color=bg,
        text_color=text_col,
        hover_color=hover_bg,
        font=("Arial", 13, "bold" if active else "normal"),
        anchor="w"
    )
    return btn
