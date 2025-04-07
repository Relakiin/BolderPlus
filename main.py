from functions.ui import create_gui
from functions.favorites import load_favorites
from functions.auth import authenticate_google
from functions.updater import get_latest_release, download_asset
from tkinter import messagebox
import os
import sys

CURRENT_VERSION = "0.0.1"

def bootstrap():
    """Bootstrap the application by checking for updates, authenticating, and launching the GUI."""
    release = get_latest_release()
    if release:
        latest_version = release['tag_name']
        if latest_version != CURRENT_VERSION:
            # Ask the user if they want to update
            update_prompt = messagebox.askyesno(
                "Aggiornamento Disponibile",
                f"È disponibile una nuova versione di Bolder Plus ({latest_version}). Vuoi aggiornare ora?"
            )

    # Authenticate with Google
    service = authenticate_google()

    # Load favorites
    favorites = load_favorites()

    # Launch the GUI
    create_gui(service, favorites)

if __name__ == "__main__":
    bootstrap()