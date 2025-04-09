import os
import requests
from tkinter import messagebox
import sys
from tkinter import Tk, ttk

GITLAB_PROJECT_ID = '68606627'

def get_latest_release():
    """Fetch the latest release information from the GitLab API."""
    url = f'https://gitlab.com/api/v4/projects/{GITLAB_PROJECT_ID}/releases'
    response = requests.get(url)
    response.raise_for_status()
    releases = response.json()
    return releases[0] if releases else None

def download_new_release(asset_url: str, output_path: str) -> None:
    """
    Download the new release and overwrite the old file if it exists, with a graphical progress bar.

    Args:
        asset_url (str): The URL of the release asset to download.
        output_path (str): The path where the downloaded file will be saved.
    """
    # Create a simple Tkinter window with a progress bar
    root = Tk()
    root.title("Scaricando aggiornamento")
    progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
    progress.pack(pady=20, padx=20)
    label = ttk.Label(root, text="Scaricando l'aggiornamento...")
    label.pack(pady=10)
    root.update()

    # Start the download
    response = requests.get(asset_url, stream=True)
    response.raise_for_status()

    # Get the total file size from the headers
    total_size = int(response.headers.get('content-length', 0))
    downloaded_size = 0

    # Write the file to the specified output path
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded_size += len(chunk)
            progress['value'] = (downloaded_size / total_size) * 100
            root.update()

    root.destroy()
    print(f"Downloaded new release to {output_path}")

def check_for_updates(current_version: str) -> None:
    """Check for updates and download the new release if available."""
    release = get_latest_release()
    if release:
        latest_version = release['name']
        if latest_version != current_version:
            # Ask the user if they want to update
            update_prompt = messagebox.askyesno(
                "Aggiornamento Disponibile",
                f"È disponibile una nuova versione di Bolder Plus ({latest_version}). Vuoi aggiornare ora?"
            )
            if update_prompt:
                # Find the .exe file in the assets
                asset_url = None
                for link in release['assets']['links']:
                    if link['name'].endswith('.exe'):
                        asset_url = link['url']
                        break

                if not asset_url:
                    messagebox.showerror("Errore", "Impossibile trovare il file eseguibile per l'aggiornamento.")
                    return

                # Download the new release
                output_path = os.path.join(os.getcwd(), 'BolderPlus.exe')
                download_new_release(asset_url, output_path)

                # Notify the user and launch the new version
                messagebox.showinfo("Aggiornamento Completato", "Bolder Plus è stato aggiornato con successo. Verrà avviata la nuova versione.")
                os.startfile(output_path)  # Launch the new executable
                sys.exit(0)  # Exit the current process