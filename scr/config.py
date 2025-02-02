"""
    Modulo per la gestione delle configurazioni dell'applicazione.
     
    path:
        scr/config.py
          
"""


# lib
from enum import Enum
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Column, Integer, String, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from .db import Base




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
    card_type = Column(SQLEnum(CardType), nullable=False)
    rarity = Column(SQLEnum(Rarity))
    
    # Aggiunta di vincoli e indici
    __table_args__ = (
        UniqueConstraint('name', 'expansion', name='uix_card_expansion'),
        Index('ix_card_name', 'name'),
    )







#@@@# Start del modulo
if __name__ != "__main__":
    print("Carico: %s." % __name__)
