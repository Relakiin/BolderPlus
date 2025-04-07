import tkinter as tk
import tkinter.messagebox as messagebox
import threading
from functions.auth import authenticate_google
from functions.favorites import load_favorites, save_favorites
from functions.google_docs import toggle_formatting
from functions.ui import add_favorite, remove_favorite, import_favorite, edit_favorite
from tkinter import font

def main():

    # GUI setup
    root = tk.Tk()
    root.title("Bolder +")

    # Apply dark mode styles
    dark_bg = "#2e2e2e"  # Dark background color
    dark_fg = "#ffffff"  # Light foreground color (text color)
    accent_color = "#ffcc00"  # Accent color for highlights (e.g., gold)

    root.configure(bg=dark_bg)  # Set the background color of the root window

    # Update styles for all widgets
    style_options = {
        "bg": dark_bg,
        "fg": dark_fg,
        "highlightbackground": dark_bg,
        "highlightcolor": dark_fg
    }

    service = authenticate_google()
    favorites = load_favorites()

    # Variable to store the selected document name
    selected_document_name = tk.StringVar(value="Nessun documento selezionato", )

    def update_favorites_list():
        """Update the Listbox with the current favorites."""
        favorites_listbox.delete(0, tk.END)
        for name in favorites:
            favorites_listbox.insert(tk.END, name)

    def save_reordered_favorites():
        """Save the reordered favorites back to the JSON file."""
        reordered_names = favorites_listbox.get(0, tk.END)
        reordered_favorites = {name: favorites[name] for name in reordered_names}
        favorites.clear()
        favorites.update(reordered_favorites)
        save_favorites(favorites)

    def on_drag_start(event):
        """Start dragging an item."""
        widget = event.widget
        widget.dragged_item_index = widget.nearest(event.y)

    def on_drag_motion(event):
        """Handle the dragging motion."""
        widget = event.widget
        dragged_item_index = widget.dragged_item_index
        target_index = widget.nearest(event.y)

        if dragged_item_index != target_index:
            # Swap the items in the Listbox
            dragged_item = widget.get(dragged_item_index)
            widget.delete(dragged_item_index)
            widget.insert(target_index, dragged_item)
            widget.dragged_item_index = target_index

    def on_drag_release(event):
        """Handle the release of the dragged item."""
        save_reordered_favorites()

    def on_listbox_select(event):
        """Store the selected document name and update the label."""
        selected_indices = favorites_listbox.curselection()
        if selected_indices:
            selected_name = favorites_listbox.get(selected_indices[0])
            selected_document_name.set(f"Documento selezionato: {selected_name}")

    def restore_selection(event=None):
        """Restore the previously selected document in the Listbox."""
        current_document = selected_document_name.get().replace("Documento selezionato: ", "")
        if current_document in favorites:
            index = list(favorites.keys()).index(current_document)
            favorites_listbox.selection_clear(0, tk.END)  # Clear any existing selection
            favorites_listbox.selection_set(index)  # Reselect the previously selected document
            favorites_listbox.activate(index)  # Ensure the selection is visually highlighted

    def process_text():
        """Process the text to apply formatting in a separate thread."""
        # Get the currently selected document from the variable
        current_document = selected_document_name.get().replace("Documento selezionato: ", "")
        if current_document == "Nessun documento selezionato":
            messagebox.showerror("Errore", "Seleziona un documento preferito.")
            return

        # Get the document ID from the favorites dictionary
        if current_document not in favorites:
            messagebox.showerror("Errore", "Il documento selezionato non è valido.")
            return

        document_id = favorites[current_document].split('/')[-2]
        words = text_box.get("1.0", tk.END).strip().split(',')
        if words == ['']:
            messagebox.showerror("Errore", "Inserisci almeno una parola.")
            return
        ignore_case = ignore_case_var.get()

        # Get formatting options from checkboxes
        formatting_options = {
            'bold': bold_var.get(),
            'italic': italic_var.get(),
            'underline': underline_var.get(),
            'strikethrough': strikethrough_var.get()
        }

        # Show spinner
        spinner_label.config(text="Elaborazione in corso...", fg="white")
        spinner_label.pack()

        def run_toggle_formatting():
            try:
                changes_count = toggle_formatting(service, document_id, words, formatting_options, ignore_case)
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

        threading.Thread(target=run_toggle_formatting).start()

    tk.Label(root, text="Nannix presents...", font=("Helvetica", 8), **style_options).pack()
        # Add styled labels for "Bolder +"
    bolder_frame = tk.Frame(root, bg=dark_bg)
    bolder_frame.pack(pady=10)

    bolder_label = tk.Label(bolder_frame, text="Bolder", font=("Helvetica", 25, "bold"), fg=dark_fg, bg=dark_bg)
    bolder_label.pack(side="left", padx=(10, 0))

    plus_label = tk.Label(bolder_frame, text="+", font=("Helvetica", 20, "bold"), fg=accent_color, bg=dark_bg)
    plus_label.pack(side="left", padx=(0, 10))
    tk.Label(root, text="Documenti preferiti", **style_options).pack()

    # Create a frame to hold the Listbox and buttons
    main_frame = tk.Frame(root, bg=dark_bg)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Configure the rows and columns of the main_frame
    main_frame.grid_rowconfigure(0, weight=1)  # Add flexible space above the button_frame
    main_frame.grid_rowconfigure(1, weight=0)  # Keep the button_frame in the middle
    main_frame.grid_rowconfigure(2, weight=1)  # Add flexible space below the button_frame
    main_frame.grid_columnconfigure(0, weight=1)  # Allow the Listbox column to expand horizontally

    # Create the Listbox for the documents
    favorites_listbox = tk.Listbox(main_frame, height=15, width=40, bg=dark_bg, fg=dark_fg, selectbackground=accent_color, selectforeground=dark_bg)
    favorites_listbox.grid(row=0, column=0, rowspan=3, padx=10, pady=5, sticky="ns")

    # Bind drag-and-drop events to the Listbox
    favorites_listbox.bind("<Button-1>", on_drag_start)
    favorites_listbox.bind("<B1-Motion>", on_drag_motion)
    favorites_listbox.bind("<ButtonRelease-1>", on_drag_release)

    # Bind events to handle selection persistence
    favorites_listbox.bind("<<ListboxSelect>>", on_listbox_select)
    favorites_listbox.bind("<FocusOut>", restore_selection)
    favorites_listbox.bind("<FocusIn>", restore_selection)

    # Create a frame for the buttons
    button_frame = tk.Frame(main_frame, bg=dark_bg)
    button_frame.grid(row=1, column=1, padx=10, pady=5)  # Place the button_frame in the middle row

    # Add buttons to the button frame
    tk.Button(button_frame, text="+ Aggiungi Preferito", command=lambda: add_favorite(favorites, update_favorites_list), bg=dark_bg, fg=accent_color).pack(pady=5, fill="x")
    tk.Button(button_frame, text="- Rimuovi Preferito", command=lambda: remove_favorite(favorites, favorites_listbox, update_favorites_list), bg=dark_bg, fg=accent_color).pack(pady=5, fill="x")
    tk.Button(button_frame, text="* Modifica Preferito", command=lambda: edit_favorite(favorites, favorites_listbox, update_favorites_list), bg=dark_bg, fg=accent_color).pack(pady=5, fill="x")
    tk.Button(button_frame, text="! Importa da Bolder 1", command=lambda: import_favorite(favorites, update_favorites_list), bg=dark_bg, fg=accent_color).pack(pady=5, fill="x")

    # Label to display the currently selected document
    selected_document_label = tk.Label(root, textvariable=selected_document_name, font=("Helvetica", 10), fg=dark_fg, bg=dark_bg)
    selected_document_label.pack(pady=5)

    tk.Label(root, text="Inserisci parole (separate da virgola):", **style_options).pack()
    text_box = tk.Text(root, height=5, width=40, bg=dark_bg, fg=dark_fg, insertbackground=dark_fg)
    text_box.pack()

    # Bind the text box to restore selection when it gains focus
    text_box.bind("<FocusIn>", restore_selection)

    ignore_case_var = tk.BooleanVar()
    tk.Checkbutton(root, text="Ignora Maiuscole/Minuscole", variable=ignore_case_var, bg=dark_bg, fg=dark_fg, selectcolor=dark_bg).pack()

    # Create a frame to hold the checkboxes
    checkbox_frame = tk.Frame(root, bg=dark_bg)
    checkbox_frame.pack()

    # Add checkboxes for formatting options with styled text
    bold_var = tk.BooleanVar()
    italic_var = tk.BooleanVar()
    underline_var = tk.BooleanVar()
    strikethrough_var = tk.BooleanVar()

    # Define custom fonts for each style
    bold_font = font.Font(root, weight="bold", size=10)
    italic_font = font.Font(root, slant="italic", size=10)
    underline_font = font.Font(root, underline=True, size=10)
    strikethrough_font = font.Font(root, overstrike=True, size=10)

    # Create styled checkboxes and place them in a 2x2 grid
    tk.Checkbutton(checkbox_frame, text="Grassetto", variable=bold_var, font=bold_font, bg=dark_bg, fg=dark_fg, selectcolor=dark_bg).grid(row=0, column=0, pady=2, sticky="w")
    tk.Checkbutton(checkbox_frame, text="Corsivo", variable=italic_var, font=italic_font, bg=dark_bg, fg=dark_fg, selectcolor=dark_bg).grid(row=0, column=1, pady=2, sticky="w")
    tk.Checkbutton(checkbox_frame, text="Sottolineato", variable=underline_var, font=underline_font, bg=dark_bg, fg=dark_fg, selectcolor=dark_bg).grid(row=1, column=0, pady=2, sticky="w")
    tk.Checkbutton(checkbox_frame, text="Barrato", variable=strikethrough_var, font=strikethrough_font, bg=dark_bg, fg=dark_fg, selectcolor=dark_bg).grid(row=1, column=1, pady=2, sticky="w")

    spinner_label = tk.Label(root, text="", fg=dark_fg, bg=dark_bg)

    tk.Button(root, text="Applica", command=process_text, bg=dark_bg, fg=accent_color).pack()

    update_favorites_list()
    root.mainloop()

if __name__ == "__main__":
    main()