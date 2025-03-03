"""
    db.py

    Modulo per la gestione del database SQLite e dei modelli SQLAlchemy.

    Path:
        scr/db.py

    Descrizione:

        Questo modulo gestisce la connessione a un database SQLite per la memorizzazione delle carte e dei mazzi di Hearthstone.
        Definisce tre modelli principali:

            - `Card`: Rappresenta una singola carta del gioco.
            - `Deck`: Rappresenta un mazzo di carte.
            - `DeckCard`: Gestisce la relazione tra mazzi e carte, inclusa la quantità di ciascuna carta in un mazzo.

    Note:
        Il database viene configurato automaticamente all'importazione del modulo. Per modificare il percorso del database, aggiornare la costante `DATABASE_PATH`.

"""

# lib
import os
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from utyls import helper as hp
from utyls import logger as log
#import pdb

# Configurazione del database
DATABASE_PATH = "hearthstone_decks_storage.db"                      # Percorso del database SQLite
engine = create_engine(f'sqlite:///{DATABASE_PATH}', echo=False)     # Connessione al database SQLite
Session = sessionmaker(bind=engine)                                 # Sessione del database per l'interazione con il database
session = Session()                                                 # Sessione del database per l'interazione con il database
Base = declarative_base()                                           # Base per i modelli SQLAlchemy



@contextmanager
def db_session():
    """ Gestisce la sessione del database e il commit/rollback automatico. """
    session = Session()  # Crea una nuova sessione ogni volta
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        log.error(f"Errore del database: {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        log.error(f"Errore imprevisto: {str(e)}")
        raise
    finally:
        session.close()


class Card(Base):
    """
    Modello per rappresentare una carta di Hearthstone nel database.

    Attributi:
        id (int): Chiave primaria.
        name (str): Nome della carta.
        class_name (str): Classe di appartenenzadella carta.
        mana_cost (int): Costo in mana della carta.
        card_type (str): Tipo di carta (es. Creatura, Magia, Arma).
        spell_type (str): Tipo di magia (opzionale, opzioni: ((segreto, incanto))
        card_subtype (str): Sottotipo della carta (opzionale).
        attack (int): Attacco della carta (opzionale, per Creature).
        health (int): Salute della carta (opzionale, per Creature).
        durability (int): Integrità della carta (opzionale, per Armi).
        rarity (str): Rarità della carta (es. Comune, Rara, Epica, Leggendaria).
        expansion (str): Espansione a cui appartiene la carta.
    """

    __tablename__ = 'cards'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)  # Aggiungo un indice sul campo 'name'
    class_name = Column(String)
    mana_cost = Column(Integer, nullable=False)
    card_type = Column(String, nullable=False)
    spell_type = Column(String)
    card_subtype = Column(String)
    attack = Column(Integer)
    health = Column(Integer)
    durability = Column(Integer)
    rarity = Column(String)
    expansion = Column(String)

    # Aggiungi un indice sul campo `name`
    __table_args__ = (
        Index('idx_card_name', 'name'),
    )

    def __repr__(self):
        return f"<Card(name='{self.name}', class='{self.class_name}', mana={self.mana_cost}, type='{self.card_type}', rarity='{self.rarity}')>"



class Deck(Base):
    """Modello per rappresentare un mazzo di Hearthstone."""

    __tablename__ = 'decks'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    player_class = Column(String, nullable=False)
    game_format = Column(String, nullable=False)

    def __repr__(self):
        return f"<Deck(name='{self.name}', class='{self.player_class}', format='{self.game_format}')>"



class DeckCard(Base):
    """Modello per rappresentare la relazione tra mazzi e carte."""

    __tablename__ = 'deck_cards'
    deck_id = Column(Integer, ForeignKey('decks.id'), primary_key=True)
    card_id = Column(Integer, ForeignKey('cards.id'), primary_key=True)
    quantity = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<DeckCard(deck_id={self.deck_id}, card_id={self.card_id}, quantity={self.quantity})>"



#@@# Start del modulo

def setup_database():
    """Crea il database e le tabelle se non esistono già."""

    if not os.path.exists(DATABASE_PATH):
        Base.metadata.create_all(engine)
        log.info(f"Database creato: {DATABASE_PATH}")
    else:
        log.info(f"Database esistente trovato: {DATABASE_PATH}")



# Configura il database all'avvio del modulo
setup_database()



#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
