from functions.ui import create_gui
from functions.favorites import load_favorites
from functions.auth import authenticate_google, check_env
from functions.updater import check_for_updates

VERSION_NAME = "__VERSION_NAME__" # Placeholder for the version name, replaced in pipeline
GITHUB_REPO = "Relakiin/BolderPlus"

def bootstrap():
    """Bootstrap the application by checking for updates, authenticating, and launching the GUI."""
    check_env()

    check_for_updates()

    # Authenticate with Google
    service = authenticate_google()

    # Load favorites
    favorites = load_favorites()

    # Launch the GUI
    create_gui(service, favorites)

if __name__ == "__main__":
    bootstrap()