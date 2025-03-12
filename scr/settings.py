"""
    Modulo per la gestione delle configurazioni dell'applicazione.
     
    path:
        scr/settings.py

    Descrizione:
        Contiene le configurazioni generali dell'applicazione, come il nome del progetto, la versione, l'autore e l'email di contatto.      

"""

# lib
from utyls import logger as log
#import pdb



# Configurazioni generali
PROJECT_NAME = "Hearthstone Deck Manager"
VERSION = "0.93"
AUTHOR = "Nemex81"
EMAIL = "nemex1981@gmail.com"


# configurazioni di sistema
SOUNDS_PATH = "./sounds"
IMG_PATH = "./img"

# configurazioni del database
DATABASE_PATH = "./hearthstone_decks_storage.db"







# settings.py
import wx
import os, sys
from pathlib import Path
from enum import Enum

# === PERCORSI ===
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
DB_PATH = BASE_DIR / "data" / "hearthstone_decks_storage.db"

# === CONFIGURAZIONI GLOBALI ===
APP_NAME = "Hearthstone Deck Manager"
APP_VERSION = "0.9.3"
DEBUG_MODE = False
DEFAULT_THEME = "DARK"

# === CONFIGURAZIONI DEL DATABASE ===
DATABASE_URL = f"sqlite:///{DB_PATH}"
SQLALCHEMY_ECHO = DEBUG_MODE  # Abilita il logging SQL solo in modalità debug

# === LOGGING ===
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
    },
    "handlers": {
        "file_handler": {
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "hdm.log",
            "formatter": "default",
        },
        "console_handler": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["file_handler", "console_handler"],
        "level": "DEBUG" if DEBUG_MODE else "INFO",
    },
}

# === INTERFACCIA UTENTE ===
class AppColors(Enum):
    DEFAULT_BG = "#2C2F33"
    DEFAULT_TEXT = "#FFFFFF"
    FOCUS_BG = "#FF5733"
    FOCUS_TEXT = "#000000"

DEFAULT_BUTTON_SIZE = (180, 70)
DEFAULT_FONT_SIZE = 16
DEFAULT_LIST_STYLE = wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN

# === FILTRI E RICERCHE ===
DEFAULT_FILTERS = ["tutti", "qualsiasi", "all"]
DEFAULT_DECK_FORMAT = "Standard"
DEFAULT_PLAYER_CLASS = "Neutrale"

# === COSTANTI GLOBALI ===
MAX_MANA_COST = 20
MAX_ATTACK = 20
MAX_HEALTH = 20
MAX_DURABILITY = 20





#@@@# Start del modulo
if __name__ != "__main__":
    log.debug("Modulo config.py importato")
