import requests
from tkinter import messagebox
from utils.constants import GITHUB_REPO, VERSION_NAME
import platform
import webbrowser
import sys

def get_latest_release():
    """Fetch the latest release information from the GitHub API."""
    url = f'https://api.github.com/repos/{GITHUB_REPO}/releases'
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    releases = response.json()
    return releases[0] if releases else None

def check_for_updates() -> None:
    """Check for updates and download the new release if available."""
    release = get_latest_release()
    if release:
        latest_version = release['name']
        if latest_version != VERSION_NAME:
            # Ask the user if they want to update
            update_prompt = messagebox.askyesno(
                "Aggiornamento Disponibile",
                f"È disponibile una nuova versione di Bolder Plus ({latest_version}). Vuoi aggiornare ora?"
            )
            if update_prompt:
                # Detect the user's operating system
                system = platform.system().lower()
                asset_name = None

                if system == "windows":
                    asset_name = "BolderPlus.exe"
                elif system == "darwin":  # macOS
                    asset_name = "BolderPlus.app.zip"
                elif system == "linux":
                    asset_name = "bolderplus"

                if not asset_name:
                    messagebox.showerror("Errore", "Sistema operativo non supportato.")
                    return

                # Find the corresponding asset in the release
                asset_url = None
                for asset in release['assets']:
                    if asset['name'] == asset_name:
                        asset_url = asset['browser_download_url']
                        break

                if not asset_url:
                    messagebox.showerror("Errore", f"Impossibile trovare il file per {system}.")
                    return

                # Open the user's browser and download the asset
                webbrowser.open(asset_url, new=2)
                sys.exit(0)  # Exit the program after opening the browser
