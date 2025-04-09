import os
import requests
from tkinter import messagebox
import sys
from tkinter import Tk, ttk
from utils.constants import GITHUB_REPO, CURRENT_VERSION
import platform
import zipfile
import shutil

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

def unzip_file(zip_path: str, extract_to: str) -> None:
    """
    Unzip a .zip file to the specified directory.

    Args:
        zip_path (str): The path to the .zip file.
        extract_to (str): The directory where the contents will be extracted.
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Extracted {zip_path} to {extract_to}")

def replace_old_app(new_app_path: str, app_dir: str) -> None:
    """
    Replace the old .app directory with the new one.

    Args:
        new_app_path (str): The path to the new .app directory.
        app_dir (str): The path to the existing .app directory.
    """
    if os.path.exists(app_dir):
        shutil.rmtree(app_dir)  # Remove the old .app directory
        print(f"Removed old app at {app_dir}")
    shutil.move(new_app_path, app_dir)  # Move the new .app to the target location
    print(f"Replaced old app with new app at {app_dir}")

def check_for_updates() -> None:
    """Check for updates and download the new release if available."""
    release = get_latest_release()
    if release:
        latest_version = release['tag_name']
        if latest_version != CURRENT_VERSION:
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

                # Download the new release
                output_path = os.path.join(os.getcwd(), asset_name)
                download_new_release(asset_url, output_path)

                # Handle macOS-specific logic for unzipping and replacing the old app
                if system == "darwin":
                    app_dir = os.path.join(os.getcwd(), "BolderPlus.app")
                    unzip_dir = os.getcwd()
                    unzip_file(output_path, unzip_dir)
                    new_app_path = os.path.join(unzip_dir, "BolderPlus.app")
                    replace_old_app(new_app_path, app_dir)
                    os.remove(output_path)  # Delete the .zip file
                    print(f"Deleted zip file at {output_path}")

                # Notify the user and launch the new version (if applicable)
                messagebox.showinfo("Aggiornamento Completato", f"Bolder Plus è stato aggiornato con successo. Verrà avviata la nuova versione.")
                if system == "windows":
                    os.startfile(output_path)  # Launch the new executable on Windows
                elif system == "darwin":
                    os.system(f"open {app_dir}")  # Launch the .app on macOS
                elif system == "linux":
                    os.system(f"chmod +x {output_path} && {output_path}")  # Make executable and run on Linux

                sys.exit(0)  # Exit the current process