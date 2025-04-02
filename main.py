import tkinter as tk
import tkinter.messagebox as messagebox
import threading
from functions.auth import authenticate_google
from functions.favorites import load_favorites
from functions.google_docs import toggle_bold
from functions.ui import add_favorite, remove_favorite, import_favorite

def main():
    service = authenticate_google()
    favorites = load_favorites()

    def update_favorites_list():
        favorites_listbox.delete(0, tk.END)
        for name in favorites:
            favorites_listbox.insert(tk.END, name)

    def process_text(bold):
        """Process the text to toggle bold formatting in a separate thread."""
        selected = favorites_listbox.curselection()
        if not selected:
            messagebox.showerror("Errore", "Seleziona un documento preferito.")
            return

        name = favorites_listbox.get(selected)
        document_id = favorites[name].split('/')[-2]
        words = text_box.get("1.0", tk.END).strip().split(',')
        if words == ['']:
            messagebox.showerror("Errore", "Inserisci almeno una parola.")
            return
        ignore_case = ignore_case_var.get()

        # Show spinner
        spinner_label.config(text="Elaborazione in corso...", fg="white")
        spinner_label.pack()

        def run_toggle_bold():
            try:
                changes_count = toggle_bold(service, document_id, words, bold, ignore_case)
                if changes_count == 0:
                    messagebox.showinfo("Informazione", "Nessuna modifica effettuata.")
                else:
                    messagebox.showinfo("Successo", f"Formattazione del testo aggiornata con successo. {changes_count} modifiche apportate.")
            except Exception as error:
                print(error)
                messagebox.showerror("Errore", f"Si è verificato un errore: {error}")
            finally:
                # Hide spinner
                spinner_label.pack_forget()

        threading.Thread(target=run_toggle_bold).start()

    # GUI setup
    root = tk.Tk()
    root.title("Bolder v2.0")

    tk.Label(root, text="Nannix presents...", font=("Helvetica", 10)).pack()
    tk.Label(root, text="BOLDER 2.0", font=("Helvetica", 20)).pack()
    tk.Label(root, text="Documenti preferiti").pack()
    favorites_listbox = tk.Listbox(root)
    favorites_listbox.pack()

    tk.Button(root, text="Inserisci Preferito", command=lambda: add_favorite(favorites, update_favorites_list)).pack()
    tk.Button(root, text="Rimuovi Preferito", command=lambda: remove_favorite(favorites, favorites_listbox, update_favorites_list)).pack()
    tk.Button(root, text="Importa da Bolder 1", command=lambda: import_favorite(favorites, update_favorites_list)).pack()

    tk.Label(root, text="Inserisci parole (separate da virgola):").pack()
    text_box = tk.Text(root, height=5, width=40)
    text_box.pack()

    ignore_case_var = tk.BooleanVar()
    tk.Checkbutton(root, text="Ignora Maiuscole/Minuscole", variable=ignore_case_var).pack()

    spinner_label = tk.Label(root, text="", fg="white")

    tk.Button(root, text="Bold", command=lambda: process_text(True)).pack()
    tk.Button(root, text="Unbold", command=lambda: process_text(False)).pack()

    update_favorites_list()
    root.mainloop()

if __name__ == "__main__":
    main()