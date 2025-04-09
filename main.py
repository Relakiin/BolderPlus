from functions.ui import create_gui
from functions.favorites import load_favorites
from functions.auth import authenticate_google, check_env
from functions.updater import check_for_updates

CURRENT_VERSION = "0.0.1"

def bootstrap():
    """Bootstrap the application by checking for updates, authenticating, and launching the GUI."""
    check_env()

    check_for_updates(CURRENT_VERSION)

    # Authenticate with Google
    service = authenticate_google()

    # Load favorites
    favorites = load_favorites()

    # Launch the GUI
    create_gui(service, favorites)

if __name__ == "__main__":
    bootstrap()