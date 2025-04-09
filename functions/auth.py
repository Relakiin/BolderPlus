import os
import sys
from typing import Any
from tkinter import messagebox
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from utils.constants import VERSION_NAME

SCOPES = ['https://www.googleapis.com/auth/documents']

def authenticate_google() -> Any:
    """Authenticate the user with Google and return the service object."""
    creds = None
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
        except Exception as e:
            print(f"Impossibile aggiornare le credenziali: {e}")
            creds = None  # Force reauthentication if refresh fails

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('docs', 'v1', credentials=creds)

def check_env() -> None:
    """
    Checks if the 'credentials.json' file exists in the current working directory.
    If the file is not found, displays an error message using a message box and
    terminates the program.

    Raises:
        SystemExit: Exits the program with status code 1 if 'credentials.json' is missing.
    """
    if VERSION_NAME == "__VERSION_NAME__":
        # Show an error message and exit the program
        messagebox.showerror("Errore", "Versione sconosciuta di Bolder. Il programma verrà terminato.")
        sys.exit(1)

    if not os.path.exists('credentials.json'):
    # Show an error message and exit the program
        messagebox.showerror("Errore", "File 'credentials.json' non trovato. Impossibile avviare Bolder.")
        sys.exit(1)
