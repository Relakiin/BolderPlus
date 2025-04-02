import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from functions.favorites import save_favorites

def add_favorite(favorites, update_favorites_list):
    name = simpledialog.askstring("Aggiungi Preferito", "Inserisci un nome per il documento:")
    link = simpledialog.askstring("Aggiungi Preferito", "Inserisci il link completo al documento:")
    if name and link:
        favorites[name] = link
        save_favorites(favorites)
        update_favorites_list()

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
        title="Seleziona il file .txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
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