import tkinter as tk
from tkinter import ttk

# Define dark mode styles
dark_bg = "#2e2e2e"  # Dark background color
dark_fg = "#ffffff"  # Light foreground color (text color)
accent_color = "#EFBF04"  # Accent color for highlights (e.g., gold)

# Global style options for widgets
style_options = {
    "bg": dark_bg,
    "fg": dark_fg,
    "highlightbackground": dark_bg,
    "highlightcolor": dark_fg
}

def configure_styles():
    """Configure global ttk styles."""
    style = ttk.Style()

    # Set the theme to "clam" for better customization
    style.theme_use("clam")

    # Configure the Accent.TButton style
    style.configure(
        "Accent.TButton",
        background=dark_bg,  # Button background
        foreground=accent_color,  # Button text color
        borderwidth=1,
        padding=(10, 5),  # Add padding to fix text cut-off
        anchor="center",  # Center-align the text
    )

    # Configure button behavior for different states
    style.map(
        "Accent.TButton",
        background=[("active", dark_fg), ("pressed", accent_color)],
        foreground=[("active", accent_color), ("pressed", dark_bg)]
    )