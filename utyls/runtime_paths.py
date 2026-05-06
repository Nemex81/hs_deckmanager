"""
    Utility per risolvere i path runtime dell'applicazione.
"""

import os
import sys


def get_app_root():
    """Restituisce la cartella base dell'app o dell'eseguibile compilato."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))

    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def resolve_app_path(*path_parts):
    """Costruisce un path assoluto relativo alla cartella base dell'app."""
    return os.path.join(get_app_root(), *path_parts)


def ensure_app_dir(*path_parts):
    """Crea e restituisce una directory relativa alla cartella base dell'app."""
    directory = resolve_app_path(*path_parts)
    os.makedirs(directory, exist_ok=True)
    return directory


def get_log_file(filename="hdm.log"):
    """Restituisce il file di log nella cartella logs dell'app."""
    return os.path.join(ensure_app_dir("logs"), filename)


def get_database_path(filename="hearthstone_decks_storage.db"):
    """Restituisce il path assoluto del database dell'app."""
    return resolve_app_path(filename)