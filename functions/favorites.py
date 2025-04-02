import os
import json

FAVORITES_FILE = "favorites.json"

def load_favorites():
    """Load favorites from the JSON file."""
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_favorites(favorites):
    """Save favorites to the JSON file."""
    with open(FAVORITES_FILE, 'w') as file:
        json.dump(favorites, file)