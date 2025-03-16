"""
    Modulo per la gestione delle configurazioni personalizzate dall'utente.
     
    path:
        scr/user_settings.py

    Descrizione:
        Contiene le configurazioni personalizzate dell'applicazione, come colori, dimensioni dei widget, filtri predefiniti e costanti globali.

"""

# lib
import wx, os, sys
from enum import Enum
from pathlib import Path
from scr.views.builder.default_settings import *
from utyls import enu_glob as eg
from utyls import logger as log



# === PERCORSI ===
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
IMG_DIR = BASE_DIR / "img"
SOUNDS_DIR = BASE_DIR / "sounds"

# === CONFIGURAZIONI GLOBALI ===
APP_NAME = "Hearthstone Deck Manager"
APP_AUTHOR = "Nemex81"
APP_EMAIL = "nemex1981@gmail.com"
APP_VERSION = "0.9.3"
DEBUG_MODE = False
DEFAULT_THEME = "DARK"

# === CONFIGURAZIONI DEL DATABASE ===
DB_PATH = BASE_DIR / "data" / "hearthstone_decks_storage.db"
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

# colori
class AppColors(Enum):
    DEFAULT_BG = eg.BLACK
    DEFAULT_TEXT = eg.WHITE
    FOCUS_BG = eg.BLUE
    FOCUS_TEXT = eg.WHITE
    ERROR_BG = eg.RED
    ERROR_TEXT = eg.WHITE
    WARNING_BG = eg.ORANGE
    WARNING_text = eg.WHITE

# === CONFIGURAZIONI DEI WIDGET ===
DEFAULT_BUTTON_SIZE = (180, 70)
DEFAULT_FONT_SIZE = 16
DEFAULT_LIST_STYLE = wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN

# === FILTRI E RICERCHE ===
DEFAULT_FILTERS = ["tutti", "qualsiasi", "all"]
DEFAULT_DECK_FORMAT = "Standard"
DEFAULT_PLAYER_CLASS = "guerriero"

# === COSTANTI GLOBALI ===
MAX_MANA_COST = 20
MAX_ATTACK = 20
MAX_HEALTH = 20
MAX_DURABILITY = 20





#@@@# Start del modulo
if __name__ != "__main__":
    log.debug("Modulo config.py importato")
