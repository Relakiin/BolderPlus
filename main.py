from functions.ui import create_gui
from functions.favorites import load_favorites
from functions.auth import authenticate_google, check_env
from functions.updater import check_for_updates

VERSION_NAME = "__VERSION_NAME__" # Placeholder for the version name, replaced in pipeline
GITHUB_REPO = "Relakiin/BolderPlus"
# This script is the main entry point for the BolderPlus application.

def bootstrap():
    """Bootstrap the application by checking for updates, authenticating, and launching the GUI."""
    check_env(current_version=VERSION_NAME)

    check_for_updates(current_version=VERSION_NAME, repo=GITHUB_REPO)

    # Authenticate with Google
    service = authenticate_google()

    # Load favorites
    favorites = load_favorites()

    # Launch the GUI
    create_gui(service, favorites, version=VERSION_NAME)

if __name__ == "__main__":
    bootstrap()
