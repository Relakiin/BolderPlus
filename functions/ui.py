import tkinter as tk
from tkinter import messagebox, filedialog
from functions.favorites import save_favorites

def open_favorite_dialog(title, initial_name="", initial_url=""):
    """Open a dialog window with two text fields for name and URL."""
    dialog = tk.Toplevel()
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.resizable(False, False)

    # Add padding to the dialog content
    content_frame = tk.Frame(dialog, padx=20, pady=10)
    content_frame.pack(fill="both", expand=True)

    tk.Label(content_frame, text="Nome del documento:").pack(pady=5, anchor="w")
    name_entry = tk.Entry(content_frame, width=50)
    name_entry.pack(pady=5, fill="x")
    name_entry.insert(0, initial_name)

    tk.Label(content_frame, text="URL del documento:").pack(pady=5, anchor="w")
    url_entry = tk.Entry(content_frame, width=50)
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
    button_frame = tk.Frame(content_frame, pady=10)
    button_frame.pack()

    tk.Button(button_frame, text="Conferma", command=on_submit, width=15).pack(side="left", padx=5)
    tk.Button(button_frame, text="Annulla", command=dialog.destroy, width=15).pack(side="left", padx=5)

    dialog.transient()  # Make the dialog modal
    dialog.grab_set()
    dialog.wait_window()

    return result["name"], result["url"]

def add_favorite(favorites, update_favorites_list):
    """Add a new favorite with a single dialog for name and URL."""
    name, url = open_favorite_dialog("Aggiungi Preferito")
    if name and url:
        favorites[name] = url
        save_favorites(favorites)
        update_favorites_list()
        messagebox.showinfo("Successo", "Preferito aggiunto con successo.")

def remove_favorite(favorites, favorites_listbox, update_favorites_list):
    selected = favorites_listbox.curselection()
    if selected:
        name = favorites_listbox.get(selected)
        del favorites[name]
        save_favorites(favorites)
        update_favorites_list()

def import_favorite(favorites, update_favorites_list):
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

def edit_favorite(favorites, favorites_listbox, update_favorites_list):
    """Edit the name or URL of an existing favorite with a single dialog."""
    selected = favorites_listbox.curselection()
    if not selected:
        messagebox.showerror("Errore", "Seleziona un preferito da modificare.")
        return

    # Get the selected favorite's name and URL
    old_name = favorites_listbox.get(selected)
    old_url = favorites[old_name]

    # Open the dialog with the current name and URL pre-filled
    new_name, new_url = open_favorite_dialog("Modifica Preferito", initial_name=old_name, initial_url=old_url)

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