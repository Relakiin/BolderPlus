import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define the Google Docs API scope
SCOPES = ['https://www.googleapis.com/auth/documents']

# Function to authenticate and create credentials
def authenticate_google_docs():
    creds = None
    try:
        # Check if there are already valid credentials (token.json)
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # If there are no valid credentials, or if the token is expired, prompt the user to log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # This flow will open the browser for the user to authenticate with Google
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run (to avoid re-authentication)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        return creds
    except Exception as e:
        messagebox.showerror("Authentication Error", f"Failed to authenticate: {str(e)}")
        return None

# Function to update text formatting (bold/unbold) in a Google Doc
def update_text_formatting(document_id, word, make_bold=True):
    creds = authenticate_google_docs()
    if creds is None:
        return

    try:
        service = build('docs', 'v1', credentials=creds)

        # Retrieve the document content
        doc = service.documents().get(documentId=document_id).execute()

        # Prepare requests to apply bold/unbold formatting
        requests = []
        for content in doc['body']['content']:
            if 'paragraph' in content:
                for element in content['paragraph']['elements']:
                    if 'textRun' in element:
                        text_run = element['textRun']['content']
                        start_index = element['startIndex']
                        
                        # Find the exact position of the word in the textRun
                        index = text_run.lower().find(word.lower())
                        if index != -1:
                            # Calculate the start and end index of the specific word
                            word_start_index = start_index + index
                            word_end_index = word_start_index + len(word)
                            
                            # Request to modify text style for the exact word
                            requests.append({
                                'updateTextStyle': {
                                    'range': {
                                        'startIndex': word_start_index,
                                        'endIndex': word_end_index
                                    },
                                    'textStyle': {
                                        'bold': make_bold
                                    },
                                    'fields': 'bold'
                                }
                            })

        if requests:
            service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
            messagebox.showinfo("Success", f"{len(requests)} text updates applied.")
        else:
            messagebox.showwarning("Not Found", "Word not found in the document.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update document: {str(e)}")

# GUI class for the application
class BoldUnboldApp:
    def __init__(self, master):
        self.master = master
        master.title("BOLDER by Demon Nannax")

        # Label for words to be bold/unbold
        self.label = tk.Label(master, text="Inserisci una o più parole separate da virgola:")
        self.label.pack()

        # Text entry field
        self.text_entry = tk.Entry(master)
        self.text_entry.pack()

        # Bold button
        self.bold_button = tk.Button(master, text="Bold", command=self.apply_bold)
        self.bold_button.pack()

        # Unbold button
        self.unbold_button = tk.Button(master, text="Unbold", command=self.apply_unbold)
        self.unbold_button.pack()

        # Sidebar to display favorite document links
        self.sidebar_label = tk.Label(master, text="Preferiti:")
        self.sidebar_label.pack()

        self.sidebar = tk.Listbox(master)
        self.sidebar.pack(side=tk.LEFT)

        self.add_fav_button = tk.Button(master, text="Aggiungi preferito", command=self.add_favorite)
        self.add_fav_button.pack()

        # Delete button for removing a favorite
        self.delete_fav_button = tk.Button(master, text="Cancella preferito", command=self.delete_favorite)
        self.delete_fav_button.pack()

        # Variable to keep track of the last selected document
        self.selected_doc_id = None

        # Load favorites
        self.load_favorites()

        # Bind the Listbox selection event
        self.sidebar.bind("<<ListboxSelect>>", self.on_select_favorite)

    def apply_bold(self):
        words = self.text_entry.get().split(',')
        doc_id = self.get_selected_doc_id()
        if doc_id:
            for word in words:
                update_text_formatting(doc_id, word.strip(), make_bold=True)

    def apply_unbold(self):
        words = self.text_entry.get().split(',')
        doc_id = self.get_selected_doc_id()
        if doc_id:
            for word in words:
                update_text_formatting(doc_id, word.strip(), make_bold=False)

    def load_favorites(self):
        # Load favorite document links from a file
        if os.path.exists('favorites.txt'):
            with open('favorites.txt', 'r') as file:
                favorites = file.readlines()
            for fav in favorites:
                self.sidebar.insert(tk.END, fav.strip().split(' | ')[0])

    def add_favorite(self):
        # Prompt user for a Google Docs ID and a descriptive name
        doc_id = simpledialog.askstring("Input", "Inserisci ID del Google Docs:")
        doc_name = simpledialog.askstring("Input", "Dai un nome al documento:")
        
        if doc_id and doc_name:
            self.sidebar.insert(tk.END, doc_name)
            # Save both the document ID and the descriptive name to the file
            with open('favorites.txt', 'a') as file:
                file.write(f"{doc_name} | {doc_id}\n")

    def delete_favorite(self):
        # Delete the selected favorite from the sidebar and file
        selected_index = self.sidebar.curselection()
        if selected_index:
            selected_index = selected_index[0]
            selected_name = self.sidebar.get(selected_index)

            # Confirm deletion
            if messagebox.askyesno("Delete Favorite", f"Vuoi davvero cancellare '{selected_name}'?"):
                # Remove from sidebar
                self.sidebar.delete(selected_index)

                # Remove from file
                with open('favorites.txt', 'r') as file:
                    lines = file.readlines()
                with open('favorites.txt', 'w') as file:
                    for line in lines:
                        if not line.startswith(selected_name + " | "):
                            file.write(line)

                # Reset selected document ID if it was deleted
                self.selected_doc_id = None
        else:
            messagebox.showwarning("No Selection", "Scegli un link preferito da eliminare")

    def get_selected_doc_id(self):
        # Return the last selected document ID or fetch from the sidebar if selected
        if self.selected_doc_id:
            return self.selected_doc_id
        else:
            try:
                selected_index = self.sidebar.curselection()[0]
                selected_name = self.sidebar.get(selected_index)

                # Retrieve the correct doc ID from the file
                with open('favorites.txt', 'r') as file:
                    for line in file:
                        name, doc_id = line.strip().split(' | ')
                        if name == selected_name:
                            self.selected_doc_id = doc_id
                            return doc_id
            except IndexError:
                messagebox.showwarning("No Selection", "Scegli un documento dai preferiti")
                return None

    def on_select_favorite(self, event):
        # Fetch the selected document ID and store it
        try:
            selected_index = self.sidebar.curselection()[0]
            selected_name = self.sidebar.get(selected_index)

            with open('favorites.txt', 'r') as file:
                for line in file:
                    name, doc_id = line.strip().split(' | ')
                    if name == selected_name:
                        self.selected_doc_id = doc_id
                        break
        except IndexError:
            self.selected_doc_id = None

# Run the Tkinter app
if __name__ == "__main__":
    root = tk.Tk()
    app = BoldUnboldApp(root)
    root.mainloop()
