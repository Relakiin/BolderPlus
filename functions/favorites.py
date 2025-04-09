import os
import json
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from utils.styles import configure_styles, dark_bg, dark_fg
from typing import Dict, Callable, Optional

FAVORITES_FILE = "favorites.json"

def open_favorite_dialog(title: str, initial_name: str = "", initial_url: str = "") -> Dict[str, Optional[str]]:
    """Open a dialog window with two text fields for name and URL."""
    dialog = tk.Toplevel()
    dialog.title(title)
    dialog.geometry("400x225")
    dialog.resizable(False, False)
    dialog.configure(bg=dark_bg)

    # Configure styles
    configure_styles()

    # Add padding to the dialog content
    content_frame = tk.Frame(dialog, bg=dark_bg, padx=20, pady=10)
    content_frame.pack(fill="both", expand=True)

    tk.Label(content_frame, text="Nome del documento:", bg=dark_bg, fg=dark_fg).pack(pady=5, anchor="w")
    name_entry = tk.Entry(content_frame, width=50, bg=dark_bg, fg=dark_fg, insertbackground=dark_fg)
    name_entry.pack(pady=5, fill="x")
    name_entry.insert(0, initial_name)

    tk.Label(content_frame, text="URL del documento:", bg=dark_bg, fg=dark_fg).pack(pady=5, anchor="w")
    url_entry = tk.Entry(content_frame, width=50, bg=dark_bg, fg=dark_fg, insertbackground=dark_fg)
    url_entry.pack(pady=5, fill="x")
    url_entry.insert(0, initial_url)

    result = {"name": None, "url": None}

    def on_submit():
        name = name_entry.get().strip()
        url = url_entry.get().strip()
        if not name or not url:
            messagebox.showerror("Errore", "Entrambi i campi devono essere compilati.")
            return
        result["name"] = name
        result["url"] = url
        dialog.destroy()

    # Add buttons with proper padding and spacing
    button_frame = tk.Frame(content_frame, bg=dark_bg, pady=10)
    button_frame.pack()

    ttk.Button(button_frame, text="Conferma", command=on_submit, style="Accent.TButton").pack(side="left", padx=5)
    ttk.Button(button_frame, text="Annulla", command=dialog.destroy, style="Accent.TButton").pack(side="left", padx=5)

    dialog.transient()
    dialog.grab_set()
    dialog.wait_window()

    return result

def add_favorite(favorites: Dict[str, str], update_favorites_list: Callable[[], None]) -> None:
    """Add a new favorite with a single dialog for name and URL."""
    name, url = open_favorite_dialog("Aggiungi Preferito").values()
    if name and url:
        favorites[name] = url
        save_favorites(favorites)
        update_favorites_list()
        messagebox.showinfo("Successo", "Preferito aggiunto con successo.")

def remove_favorite(favorites: Dict[str, str], favorites_listbox: tk.Listbox, update_favorites_list: Callable[[], None]) -> None:
    """Remove a selected favorite from the list."""
    selected = favorites_listbox.curselection()
    if selected:
        name = favorites_listbox.get(selected)
        del favorites[name]
        save_favorites(favorites)
        update_favorites_list()

def import_favorite(favorites: Dict[str, str], update_favorites_list: Callable[[], None]) -> None:
    """Import favorites from a .txt file and save them to the JSON file."""
    file_path = filedialog.askopenfilename(
        title="Seleziona il file favorites.txt",
        filetypes=[("Text Files", "*.txt")]
    )
    if not file_path:
        messagebox.showerror("Errore", "Nessun file selezionato.")
        return

    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if '|' in line:
                    name, document_id = map(str.strip, line.split('|'))
                    # Convert document_id to full URL
                    full_url = f"https://docs.google.com/document/d/{document_id}/edit"
                    favorites[name] = full_url
            save_favorites(favorites)
            update_favorites_list()
            messagebox.showinfo("Successo", "Preferiti importati con successo. Welcome to Bolder 2.0!")
    except Exception as e:
        messagebox.showerror("Errore", f"Si è verificato un errore durante l'importazione: {e}")

def edit_favorite(favorites: Dict[str, str], favorites_listbox: tk.Listbox, update_favorites_list: Callable[[], None]) -> None:
    """Edit the name or URL of an existing favorite with a single dialog."""
    selected = favorites_listbox.curselection()
    if not selected:
        messagebox.showerror("Errore", "Seleziona un preferito da modificare.")
        return

    # Get the selected favorite's name and URL
    old_name = favorites_listbox.get(selected)
    old_url = favorites[old_name]

    # Open the dialog with the current name and URL pre-filled
    new_name, new_url = open_favorite_dialog("Modifica Preferito", initial_name=old_name, initial_url=old_url).values()

    # Update the favorite if changes are made
    if new_name and new_url:
        # Preserve the position of the favorite in the list
        position = list(favorites.keys()).index(old_name)

        # Create a new ordered dictionary with the updated favorite
        updated_favorites = {}
        for i, (key, value) in enumerate(favorites.items()):
            if i == position:
                updated_favorites[new_name] = new_url  # Insert the updated favorite
            elif key != old_name:
                updated_favorites[key] = value  # Keep other favorites unchanged

        # Save the updated favorites and refresh the list
        favorites.clear()
        favorites.update(updated_favorites)
        save_favorites(favorites)
        update_favorites_list()

        # Reselect the edited favorite
        favorites_listbox.selection_clear(0, tk.END)
        favorites_listbox.selection_set(position)
        favorites_listbox.activate(position)

def load_favorites() -> Dict[str, str]:
    """Load favorites from the JSON file."""
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_favorites(favorites: Dict[str, str]) -> None:
    """Save favorites to the JSON file."""
    with open(FAVORITES_FILE, 'w') as file:
        json.dump(favorites, file)

def update_favorites_list(favorites: Dict[str, str], favorites_listbox: tk.Listbox) -> None:
    """
    Update the Listbox with the current favorites.
    
    Args:
        favorites (dict): The dictionary of favorites.
        favorites_listbox (tk.Listbox): The Listbox widget to update.
    """
    favorites_listbox.delete(0, "end")
    for name in favorites:
        favorites_listbox.insert("end", name)

def save_reordered_favorites(favorites: Dict[str, str], favorites_listbox: tk.Listbox) -> None:
    """
    Save the reordered favorites back to the JSON file.
    
    Args:
        favorites (dict): The dictionary of favorites.
        favorites_listbox (tk.Listbox): The Listbox widget containing the reordered items.
    """
    reordered_names = favorites_listbox.get(0, "end")
    reordered_favorites = {name: favorites[name] for name in reordered_names}
    favorites.clear()
    favorites.update(reordered_favorites)
    save_favorites(favorites)