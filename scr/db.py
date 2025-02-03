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

        Include una funzione `setup_database` che crea le tabelle del database se non esistono già.

    Funzionalità principali:

        - Creazione, lettura, aggiornamento ed eliminazione (CRUD) di carte e mazzi.
        - Gestione delle relazioni tra mazzi e carte.
        - Configurazione automatica del database SQLite.

    Esempio di utilizzo:
        from db import session, Card, Deck, DeckCard

        # Aggiungere una nuova carta
        new_card = Card(name="Dragone Rosso", mana_cost=8, card_type="Creatura")
        session.add(new_card)
        session.commit()

        # Creare un nuovo mazzo
        new_deck = Deck(name="Aggro Mage", player_class="Mage", game_format="Standard")
        session.add(new_deck)
        session.commit()

        # Aggiungere una carta a un mazzo
        deck_card = DeckCard(deck_id=new_deck.id, card_id=new_card.id, quantity=2)
        session.add(deck_card)
        session.commit()

    Modelli:

        - `Card`: Definisce una carta di Hearthstone.
            Attributi principali:
            - id (int): Identificativo univoco della carta.
            - name (str): Nome della carta.
            - class_name (str): Classe della carta.
            - mana_cost (int): Costo in mana.
            - card_type (str): Tipo di carta (Creatura, Magia, ecc.).
            - card_subtype (str): Sottotipo della carta (es. Drago).
            - attack (int): Attacco (opzionale, per Creature).
            - health (int): Salute (opzionale, per Creature).
            - durability (int): Integrità (opzionale, per Armi).
            - rarity (str): Rarità della carta (Comune, Rara, ecc.).
            - expansion (str): Espansione di appartenenza.

        - `Deck`: Definisce un mazzo di Hearthstone.
            Attributi principali:
            - id (int): Identificativo univoco del mazzo.
            - name (str): Nome del mazzo.
            - player_class (str): Classe del giocatore (Mage, Warrior, ecc.).
            - game_format (str): Formato del mazzo (Standard, Wild).

        - `DeckCard`: Gestisce la relazione tra carte e mazzi.
            Attributi principali:
            - deck_id (int): Identificativo del mazzo.
            - card_id (int): Identificativo della carta.
            - quantity (int): Quantità di copie della carta nel mazzo.

    Funzioni:
        - `setup_database`: Crea il database e le tabelle necessarie se non esistono già.

    Dipendenze:
        - sqlalchemy: Per la gestione del database e dei modelli.

    Note:
        Il database viene configurato automaticamente all'importazione del modulo. Per modificare il percorso del database, aggiornare la costante `DATABASE_PATH`.

"""

# lib
import os
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from utyls import logger as log
#import pdb

# Configurazione del database
DATABASE_PATH = "hearthstone_decks_storage.db"
engine = create_engine(f'sqlite:///{DATABASE_PATH}', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Base per i modelli SQLAlchemy
Base = declarative_base()


@contextmanager
def db_session():
    """ Gestisce la sessione del database e il commit/rollback automatico. """

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



class Card(Base):
    """
    Modello per rappresentare una carta di Hearthstone nel database.

    Attributi:
        id (int): Chiave primaria.
        name (str): Nome della carta.
        class_name (str): Classe di appartenenzadella carta.
        mana_cost (int): Costo in mana della carta.
        card_type (str): Tipo di carta (es. Creatura, Magia, Arma).
        card_subtype (str): Sottotipo della carta (opzionale).
        attack (int): Attacco della carta (opzionale, per Creature).
        health (int): Salute della carta (opzionale, per Creature).
        durability (int): Integrità della carta (opzionale, per Armi).
        rarity (str): Rarità della carta (es. Comune, Rara, Epica, Leggendaria).
        expansion (str): Espansione a cui appartiene la carta.
    """

    __tablename__ = 'cards'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    class_name = Column(String)
    mana_cost = Column(Integer, nullable=False)
    card_type = Column(String, nullable=False)
    card_subtype = Column(String)
    attack = Column(Integer)
    health = Column(Integer)
    durability = Column(Integer)
    rarity = Column(String)
    expansion = Column(String)

    def __repr__(self):
        return f"<Card(name='{self.name}', mana_cost={self.mana_cost}, type='{self.card_type}')>"



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
    print("Carico: %s" % __name__)
