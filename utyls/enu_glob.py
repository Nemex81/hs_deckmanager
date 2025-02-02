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

class ENUCARD(Enum):
    """ info base obblicagorie delel carte pe rl'interazione con il db. """

    Name = "name"
    ManaCost = "mana_cost"
    CardType = "card_type"

class EnuExtraCard(Enum):
    """ info extra delle carte pe rl'interazione con il db. """

    Name = "name"
    CLASS = "class"
    ManaCost = "mana_cost"
    CardType = "card_type"
    CardSubType = "card_subtype"
    Rarity = "rarity"
    Expansion = "expansion"
    Attack = "attack"
    Health = "health"
    Durability = "durability"


class EnuCardType(Enum):
    """ tipi di carte """

    CREATURA = "Creatura"
    MAGIA = "Magia"
    LUOGO = "Luogo"
    ARMA = "Arma"
    EROE = "Eroe"

class EnuHero(Enum):
    """ eroi delle carte """
    
    CACCIATORE = "Cacciatore"
    DRUIDO = "Druido"
    GUERRIERO = "Guerriero"
    KNIGHTDEATH = "cavaliere della morte"
    LADRO = "Ladro"
    MAGO = "Mago"
    PALADINO = "Paladino"
    SACERDOTE = "Sacerdote"
    SCIAMANO = "Sciamano"
    SHADOHUNTER = "Cacciatore di demoni"
    STREGONE = "Stregone"

class EnuRarity(Enum):
    """ rarità delle carte """

    COMUNE = "Comune"
    RARA = "Rara"
    EPICA = "Epica"
    LEGGENDARIA = "Leggendaria"

class EnuExpansion(Enum):
    """ espansioni delle carte """

    STANDARD = "standard"
    CLASSIC = "Classic"
    UNKNOWN = "Unknown"




#@@@# Start del modulo
if __name__ != "__main__":
    print("Carico: %s" % __name__)
