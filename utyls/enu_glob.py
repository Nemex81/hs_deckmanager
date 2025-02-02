"""
    Modulo per la gestione delle enumerazioni globali

    path:
        utyls/enu_glob.py
        
    Descrizione:
    Contiene le enumerazioni globali utilizzate nell'applicazione.

"""




from enum import Enum
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import  Column, Integer, String, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from scr.db import Base, session, Card, Deck, DeckCard
# from utyls.logger import Logger
#import pdb

# colori rgb
class EnuColors(Enum):
    BLACK = 'black'
    WHITE = 'white'
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    YELLOW = 'yellow'

class EnuCard(Enum):
    Name = ""
    CLASS = ""
    ManaCost = 0
    CardType = ""
    CardSubType = ""
    Rarity = ""
    Expansion = ""
    Text = ""
    Attack = 0
    Health = 0
    Durability = 0


class EnuCardType(Enum):
    CREATURA = "Creatura"
    MAGIA = "Magia"
    LUOGO = "Luogo"
    ARMA = "Arma"
    EROE = "Eroe"

class EnuRarity(Enum):
    COMUNE = "Comune"
    RARA = "Rara"
    EPICA = "Epica"
    LEGGENDARIA = "Leggendaria"






# classi per la gestione degli stati del personaggio
class Position(Enum):
    REGLINING = 0
    SITTING = 1
    STANDING = 2
    FLOATING = 3


class ChStatus(Enum):
    CREAZIONE = -2
    MORTO = -1
    INATTIVO = 0
    FERMO = 1
    MOVIMENTO = 2



#@@@# Start del modulo
if __name__ != "__main__":
    print("Carico: %s" % __name__)
