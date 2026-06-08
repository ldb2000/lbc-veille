"""Persistance du curseur round-robin (fichier JSON dans /data)."""
import json
import os


def load_cursor(path):
    """Lit le curseur. Retourne 0 si fichier absent ou corrompu."""
    try:
        with open(path) as f:
            return int(json.load(f).get("cursor", 0))
    except (OSError, ValueError, json.JSONDecodeError):
        return 0


def save_cursor(path, cursor):
    """Écrit le curseur de façon atomique (write tmp + replace)."""
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"cursor": int(cursor)}, f)
    os.replace(tmp, path)
