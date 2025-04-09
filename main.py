from functions.ui import create_gui
from functions.favorites import load_favorites
from functions.auth import authenticate_google, check_env
from functions.updater import check_for_updates

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