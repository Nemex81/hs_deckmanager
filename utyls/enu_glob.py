"""
	Modulo per la gestione delle enumerazioni globali

	path:
		utyls/enu_glob.py
		
	Descrizione:
	Contiene le enumerazioni globali utilizzate nell'applicazione.

"""




from enum import Enum
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Column, Integer, String, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
#import pdb

# colori rgb
from enum import Enum

class Colors(Enum):
    BLACK = 'black'
    WHITE = 'white'
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    YELLOW = 'yellow'

class CardType(Enum):
    CREATURA = "Creatura"
    MAGIA = "Magia"
    LUOGO = "Luogo"
    ARMA = "Arma"
    EROE = "Eroe"

class Rarity(Enum):
    COMUNE = "Comune"
    RARA = "Rara"
    EPICA = "Epica"
    LEGGENDARIA = "Leggendaria"

class Card(Base):
    # ... altre colonne ...
    name = Column(String(100), nullable=False)
    cost = Column(Integer, nullable=False)
    card_type = Column(SQLEnum(CardType), nullable=False)
    subtype = Column(String(50))
    expansion = Column(String(50), nullable=False)
    rarity = Column(SQLEnum(Rarity))
    Attack = Column(Integer)
    Health = Column(Integer)
    Durability = Column(Integer)

    # Aggiunta di vincoli e indici
    __table_args__ = (
        UniqueConstraint('name', 'expansion', name='uix_card_expansion'),
        Index('ix_card_name', 'name'),
    )




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
