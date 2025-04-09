import tkinter as tk
from tkinter import ttk, font, messagebox
from utils.styles import style_options, dark_bg, dark_fg, accent_color, configure_styles
from functions.favorites import (
    update_favorites_list,
    save_reordered_favorites,
    add_favorite,
    remove_favorite,
    import_favorite,
    edit_favorite,
)
from functions.google_docs import toggle_formatting
import threading
from typing import Dict
from main import VERSION_NAME

def create_gui(service: object, favorites: Dict[str, str]) -> None:
    """Create the GUI and handle events.

    Args:
        service (object): The Google Docs API service object.
        favorites (Dict[str, str]): A dictionary of favorite documents.
    """
    # GUI setup
    root = tk.Tk()
    root.title("Bolder +")
    root.configure(bg=dark_bg)

    # Configure styles
    configure_styles()

    # Variable to store the selected document name
    selected_document_name = tk.StringVar(value="Nessun documento selezionato")

    def on_drag_start(event: tk.Event) -> None:
        """Start dragging an item.

        Args:
            event (tk.Event): The drag start event.
        """
        widget = event.widget
        widget.dragged_item_index = widget.nearest(event.y)

    def on_drag_motion(event: tk.Event) -> None:
        """Handle the dragging motion.

        Args:
            event (tk.Event): The drag motion event.
        """
        widget = event.widget
        dragged_item_index = widget.dragged_item_index
        target_index = widget.nearest(event.y)

        if dragged_item_index != target_index:
            # Swap the items in the Listbox
            dragged_item = widget.get(dragged_item_index)
            widget.delete(dragged_item_index)
            widget.insert(target_index, dragged_item)
            widget.dragged_item_index = target_index

    def on_drag_release(event: tk.Event) -> None:
        """Handle the release of the dragged item.

        Args:
            event (tk.Event): The drag release event.
        """
        save_reordered_favorites(favorites, favorites_listbox)

    def on_listbox_select(event: tk.Event) -> None:
        """Store the selected document name and update the label.

        Args:
            event (tk.Event): The listbox select event.
        """
        selected_indices = favorites_listbox.curselection()
        if selected_indices:
            selected_name = favorites_listbox.get(selected_indices[0])
            selected_document_name.set(f"Documento selezionato: {selected_name}")

    def restore_selection(event: tk.Event = None) -> None:
        """Restore the previously selected document in the Listbox.

        Args:
            event (tk.Event, optional): The focus event. Defaults to None.
        """
        current_document = selected_document_name.get().replace("Documento selezionato: ", "")
        if current_document in favorites:
            index = list(favorites.keys()).index(current_document)
            favorites_listbox.selection_clear(0, "end")  # Clear any existing selection
            favorites_listbox.selection_set(index)  # Reselect the previously selected document
            favorites_listbox.activate(index)  # Ensure the selection is visually highlighted

    def process_text() -> None:
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

        def run_toggle_formatting() -> None:
            """Run the toggle formatting operation in a separate thread."""
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

    # GUI components
    tk.Label(root, text="Nannix presents...", font=("Helvetica", 8), **style_options).pack()
    bolder_frame = tk.Frame(root, bg=dark_bg)
    bolder_frame.pack(pady=10)

    title_frame = tk.Frame(bolder_frame, bg=dark_bg)
    title_frame.pack()

    bolder_label = tk.Label(title_frame, text="Bolder", font=("Helvetica", 25, "bold"), fg=dark_fg, bg=dark_bg)
    bolder_label.pack(side="left")

    plus_label = tk.Label(title_frame, text="+", font=("Helvetica", 20, "bold"), fg=accent_color, bg=dark_bg)
    plus_label.pack(side="left")

    ver_label = tk.Label(bolder_frame, text="v" + VERSION_NAME, font=("Helvetica", 10, "bold"), fg=accent_color, bg=dark_bg)
    ver_label.pack(pady=(2, 0))

    main_frame = tk.Frame(root, bg=dark_bg)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=0)
    main_frame.grid_rowconfigure(2, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    favorites_listbox = tk.Listbox(main_frame, height=15, width=40, bg=dark_bg, fg=dark_fg, selectbackground=accent_color, selectforeground=dark_bg)
    favorites_listbox.grid(row=0, column=0, rowspan=3, padx=10, pady=5, sticky="ns")

    favorites_listbox.bind("<Button-1>", on_drag_start)
    favorites_listbox.bind("<B1-Motion>", on_drag_motion)
    favorites_listbox.bind("<ButtonRelease-1>", on_drag_release)
    favorites_listbox.bind("<<ListboxSelect>>", on_listbox_select)
    favorites_listbox.bind("<FocusOut>", restore_selection)
    favorites_listbox.bind("<FocusIn>", restore_selection)

    button_frame = tk.Frame(main_frame, bg=dark_bg)
    button_frame.grid(row=1, column=1, padx=10, pady=5)

    ttk.Button(button_frame, text="+ Aggiungi Preferito", command=lambda: add_favorite(favorites, lambda: update_favorites_list(favorites, favorites_listbox)), style="Accent.TButton").pack(pady=5, fill="x")
    ttk.Button(button_frame, text="- Rimuovi Preferito", command=lambda: remove_favorite(favorites, favorites_listbox, lambda: update_favorites_list(favorites, favorites_listbox)), style="Accent.TButton").pack(pady=5, fill="x")
    ttk.Button(button_frame, text="* Modifica Preferito", command=lambda: edit_favorite(favorites, favorites_listbox, lambda: update_favorites_list(favorites, favorites_listbox)), style="Accent.TButton").pack(pady=5, fill="x")
    ttk.Button(button_frame, text="! Importa da Bolder 1", command=lambda: import_favorite(favorites, lambda: update_favorites_list(favorites, favorites_listbox)), style="Accent.TButton").pack(pady=5, fill="x")

    selected_document_label = tk.Label(root, textvariable=selected_document_name, font=("Helvetica", 10), fg=dark_fg, bg=dark_bg)
    selected_document_label.pack(pady=5)

    tk.Label(root, text="Inserisci parole (separate da virgola):", **style_options).pack()
    text_box = tk.Text(root, height=5, width=40, bg=dark_bg, fg=dark_fg, insertbackground=dark_fg)
    text_box.pack()

    text_box.bind("<FocusIn>", restore_selection)

    ignore_case_var = tk.BooleanVar()
    tk.Checkbutton(root, text="Ignora Maiuscole/Minuscole", variable=ignore_case_var, bg=dark_bg, fg=dark_fg, selectcolor=dark_bg).pack()

    checkbox_frame = tk.Frame(root, bg=dark_bg)
    checkbox_frame.pack()

    bold_var = tk.BooleanVar()
    italic_var = tk.BooleanVar()
    underline_var = tk.BooleanVar()
    strikethrough_var = tk.BooleanVar()

    bold_font = font.Font(root, weight="bold", size=10)
    italic_font = font.Font(root, slant="italic", size=10)
    underline_font = font.Font(root, underline=True, size=10)
    strikethrough_font = font.Font(root, overstrike=True, size=10)

    tk.Checkbutton(checkbox_frame, text="Grassetto", variable=bold_var, font=bold_font, bg=dark_bg, fg=dark_fg, selectcolor=dark_bg).grid(row=0, column=0, pady=2, sticky="w")
    tk.Checkbutton(checkbox_frame, text="Corsivo", variable=italic_var, font=italic_font, bg=dark_bg, fg=dark_fg, selectcolor=dark_bg).grid(row=0, column=1, pady=2, sticky="w")
    tk.Checkbutton(checkbox_frame, text="Sottolineato", variable=underline_var, font=underline_font, bg=dark_bg, fg=dark_fg, selectcolor=dark_bg).grid(row=1, column=0, pady=2, sticky="w")
    tk.Checkbutton(checkbox_frame, text="Barrato", variable=strikethrough_var, font=strikethrough_font, bg=dark_bg, fg=dark_fg, selectcolor=dark_bg).grid(row=1, column=1, pady=2, sticky="w")

    spinner_label = tk.Label(root, text="", fg=dark_fg, bg=dark_bg)

    ttk.Button(root, text="Applica", command=process_text, style="Accent.TButton").pack()

    update_favorites_list(favorites, favorites_listbox)
    root.mainloop()