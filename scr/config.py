"""
    Modulo per la gestione delle configurazioni dell'applicazione.
     
    path:
        scr/config.py

    Descrizione:
        Contiene le configurazioni generali dell'applicazione, come il nome del progetto, la versione, l'autore e l'email di contatto.      

"""

# lib
from utyls import logger as log
#import pdb



# Configurazioni generali
PROJECT_NAME = "Hearthstone Deck Manager"
VERSION = "0.5"
AUTHOR = "Nemex81"
EMAIL = "nemex1981@gmail.com"


# configurazioni di sistema
SOUNDS_PATH = "sounds"
IMG_PATH = "img"

# configurazioni del database
DATABASE_PATH = "hearthstone_decks_storage.db"











#@@@# Start del modulo
if __name__ != "__main__":
    print("Carico: %s" % __name__)
