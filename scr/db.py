"""
    db.py

    Modulo per la gestione del database SQLite e dei modelli SQLAlchemy.

    path:
        scr/db.py

Descrizione:

    Questo modulo definisce il modello `Card` per rappresentare le carte di Hearthstone
    e gestisce la connessione al database SQLite. Fornisce funzioni per operazioni CRUD
    (Create, Read, Update, Delete) sulle carte.

Utilizzo:
    - Importare il modulo e utilizzare la sessione `session` per interagire con il database.
    - Utilizzare il modello `Card` per creare, aggiornare o eliminare carte.

Esempio:
    from db import session, Card

    # Aggiungere una nuova carta
    new_card = Card(name="Dragone Rosso", mana_cost=8, card_type="Creatura")
    session.add(new_card)
    session.commit()

Dipendenze:
    - sqlalchemy: Per la gestione del database e dei modelli.
"""

# lib
import os
import logging
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
#from utyls.logger import Logger
#import pdb

# Configurazione del database
DATABASE_PATH = "hearthstone_decks_storage.db"
engine = create_engine(f'sqlite:///{DATABASE_PATH}', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Base per i modelli SQLAlchemy
Base = declarative_base()



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
        logging.info(f"Database creato: {DATABASE_PATH}")
    else:
        logging.info(f"Database esistente trovato: {DATABASE_PATH}")



# Configura il database all'avvio del modulo
setup_database()



#@@@# Start del modulo
if __name__ != "__main__":
    print("Carico: %s" % __name__)
