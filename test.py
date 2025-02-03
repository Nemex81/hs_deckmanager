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

class EnuSpellSubType(Enum):
    """ sottotipi delle carte Magia """

    ARCANO = "Arcano"
    FUOCO = "Fuoco"
    GELO = "Gelo"
    NATURA = "Natura"
    OMBRA = "Ombra"
    SACRO = "Sacra"
    FISICO = "Fisico"
    VENTO = "Vento"
    VENENO = "Veleno"
    SANGUE = "Sangue"
    EMPIETA = "Empietà"
    DIVINO = "Divino"
    FULMINE = "Fulmine"
    ACQUA = "Acqua"
    TERRA = "Terra"
    LUCE = "Luce"
    ANIMA = "Anima"
    VITA = "Vita"
    MORTE = "Morte"
    DEMONIACO = "Demoniaco"
    ANGELICO = "Angelico"

class EnuPetSubType(Enum):
    """ sottotipi delle carte Creatura """

    DRAGO = "Drago"
    FANTASMA = "Fantasma"
    BESTIA = "Bestia"
    ELEMENTALE = "Elementale"
    SPIRITO = "Spirito"
    TOTEM = "Totem"
    MECCANICO = "Meccanico"
    PIRATA = "Pirata"
    MURLOC = "Murloc"
    DRAGOIDE = "Dragoide"
    DEMONE = "Demone"
    ELFO = "Elfo"
    ORCO = "Orco"
    GNOMO = "Gnomo"
    UMANO = "Umano"
    NON_MORTO = "Non Morto"
    TROLL = "Troll"
    GOBLIN = "Goblin"
    NANO = "Nano"


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

    # Set di base: la collezione iniziale con cui i nuovi giocatori partono.
    SET_BASE = "Set Principale"

    # Espansioni classiche (prime espansioni rilasciate)
    MALEDIZIONE_NAXXRAMAS = "La Maledizione di Naxxramas"          # Avventura/espansione che introduce nuove meccaniche come il deathrattle
    GOBLIN_VS_GNOMI = "Goblin vs Gnomi"                             # Espansione incentrata sul contrasto tra goblin e gnomi
    BLACKROCK_MOUNTAIN = "Blackrock Mountain"                       # Avventura ambientata in una montagna infestata da draghi e boss epici
    GRAN_TOURNAMENT = "Il Grande Torneo"                            # Espansione a tema torneo con meccaniche come il joust
    LEGA_DEGLI_ESPLORATORI = "La Lega degli Esploratori"             # Avventura con meccanica Discover e ambientazione ispirata alle rovine
    SUSSURRI_DEGLI_DEI_ANTICHI = "Sussurri degli Dei Antichi"        # Espansione che porta in gioco poteri oscuri e riferimenti agli antichi dei
    UNA_NOTTE_A_KARAZHAN = "Una Notte a Karazhan"                    # Avventura ambientata nell’iconica torre di Karazhan
    QUARTIERI_MALFAMATI_DI_GADGETZAN = "I Quartieri Malfamati di Gadgetzan"   
    VIAGGIO_A_UNGORO = "Viaggio a Un'Goro"                           # Espansione che esplora un ambiente preistorico e selvaggio
    CAVALIERI_DEL_TRONO_GELATO = "Cavalieri del Trono Gelato"        # Espansione a tema freddo e misterioso con un trono di ghiaccio
    KOBOLD_E_CATACOMBE = "Kobold e Catacombe"                       # Espansione che richiama atmosfere oscure e fantasy
    IL_BOSCO_STREGATO = "Il Bosco Stregato"                         # Espansione che evoca un ambiente magico e inquietante
    PROGETTO_BOOMSDAY = "Il Progetto Boomsday"                       # Espansione con tema futuristico e tecnologico
    RUMBLE_DI_RASTAKHAN = "Il Rumble di Rastakhan"                   # Espansione ispirata alle atmosfere esotiche e al combattimento in arena
    L_ASCESA_DELLE_OMBRE = "L'Ascesa delle Ombre"                     # Espansione che introduce tematiche oscure e minacciose
    I_SALVATORI_DI_ULDUM = "I Salvatori di Uldum"                   # Espansione ambientata in un’ambientazione esotica e misteriosa
    LA_DISCESA_DEI_DRAGHI = "La Discesa dei Draghi"                   # Espansione incentrata sui draghi e le loro forze
    LE_CENERI_DI_OUTLAND = "Le Ceneri di Outland"                     # Espansione che porta il giocatore in un mondo in rovina
    ACCADEMIA_SCHOLOMANCE = "L'Accademia Scholomance"                # Espansione con ambientazione gotica e scolastica
    DARKMOON_FAIRE = "La Follia alla Fiera di Darkmoon"             # Espansione ispirata al famoso evento Darkmoon, con meccaniche di corruzione

    # Espansioni e Core più recenti
    CORE_2021 = "Core 2021"                                           # Nuovo set base annuale introdotto nel 2021
    FORGED_IN_THE_BARRENS = "Forgiato nei Barrens"                   # Espansione che esplora i paesaggi aridi dei Barrens
    UNITED_IN_STORMWIND = "Uniti a Stormwind"                         # Espansione a tema urbano e regale, ambientata a Stormwind
    FRACTURED_IN_ALTERAC_VALLEY = "Fratturato nella Valle d'Alterac"   # Espansione che porta battaglie epiche nella valle di Alterac
    CORE_2022 = "Core 2022"                                           # Nuovo set base annuale per il 2022
    VOYAGE_TO_THE_SUNKEN_CITY = "Viaggio nella Città Sommersa"         # Espansione con ambientazione subacquea e nuove meccaniche
    ASSASSINIO_AL_CASTELLO_DI_NATHRIA = "Assassinio al Castello di Nathria"  # Espansione che fonde mistero e ambientazioni gotiche
    MARCH_OF_THE_LICH_KING = "Marcia del Re dei Lich"                # Espansione dedicata al tema dei Re dei Lich
    CORE_2023 = "Core 2023"                                           # Nuovo set base annuale per il 2023
    FESTIVAL_OF_LEGENDS = "Festival delle Leggende"                   # Espansione festiva con nuove carte e temi epici
    TITANS = "Titani"                                                 # Espansione che evoca il potere dei titani
    SHOWDOWN_IN_THE_BADLANDS = "Showdown nelle Terre Malfamate"      # Espansione che porta scontri intensi in ambientazioni desolate
    CORE_2024 = "Core 2024"                                           # Nuovo set base annuale per il 2024
    WHIZBANGS_WORKSHOP = "La Bottega di Whizbang"                    # Espansione che unisce creatività e tecnologia in un laboratorio unico
    PERILS_IN_PARADISE = "Pericoli nel Paradiso"                      # Espansione che mescola bellezze paradisiache e insidie
    THE_GREAT_DARK_BEYOND = "Il Grande Oltre Oscuro"                 # Espansione che apre le porte a misteri e orrori oltre il conosciuto



#@@@# Start del modulo
if __name__ != "__main__":
    print("Carico: %s" % __name__)

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
DATABASE_PATH = "hearthstone_decks_storage.db"                      # Percorso del database SQLite
engine = create_engine(f'sqlite:///{DATABASE_PATH}', echo=True)     # Connessione al database SQLite
Session = sessionmaker(bind=engine)                                 # Sessione del database per l'interazione con il database
session = Session()                                                 # Sessione del database per l'interazione con il database
Base = declarative_base()                                           # Base per i modelli SQLAlchemy



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

"""
    models.py

    Modulo per la gestione dei mazzi di Hearthstone e delle operazioni correlate.

    Path:
        scr/models.py   

    Descrizione:
 
        Questo modulo contiene la classe DeckManager e funzioni utili per gestire:

            - Caricamento/salvataggio dei mazzi da/in file JSON
            - Parsing delle carte dai mazzi con verifica di validità
            - Sincronizzazione delle carte con il database
            - Calcolo delle statistiche e delle proprietà del mazzo
            - Manipolazione delle informazioni relative ai mazzi (aggiunta, eliminazione)

    Utilizzo:
        from models import DeckManager
        from db import session

        deck_manager = DeckManager()
        deck_manager.add_deck_from_clipboard()

    Classi:
        - DeckManager: Classe principale per la gestione dei mazzi.

    Funzioni:
        - parse_deck_metadata(deck_string): Estrae metadati (nome, classe, formato) dalla stringa del mazzo.
        - parse_cards_from_deck(deck_string): Estrae le carte da una stringa di mazzo utilizzando regex.

    Esempio di utilizzo:
        deck_manager = DeckManager()
        deck_manager.add_deck_from_clipboard()

    Note:
        Questo modulo utilizza il modulo `db` per l'interazione con il database SQLite.
        Le funzioni di parsing utilizzano regex per estrarre le informazioni dai mazzi.

"""

#lib
import os
import shutil
import re
import pyperclip
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from .db import session, db_session, Deck, DeckCard, Card
from utyls import logger as log
#import pdb



def parse_deck_metadata(deck_string):
    """ Estrae nome, classe e formato dalla stringa grezza del mazzo copiato. """

    lines = deck_string.splitlines()[:3]
    metadata = {
        "name": lines[0].replace("###", "").strip(),
        "player_class": "Neutrale",
        "game_format": "Standard"
    }
    
    for line in lines[1:]:
        if "Classe:" in line:
            metadata["player_class"] = line.split(":")[1].strip()
        elif "Formato:" in line:
            metadata["game_format"] = line.split(":")[1].strip()
    
    return metadata



class DeckManager:
    """ Classe per la gestione dei mazzi di Hearthstone. """

    def __init__(self, file_path="decks.json"):
        #self.file_path = file_path
        #self.decks = {}
        #self.loaded = False
        #self.load_decks()
        pass

    def is_valid_deck(self, deck_string):
        """Verifica se una stringa rappresenta un mazzo valido."""
        return bool(
            deck_string and 
            deck_string.startswith("###") and 
            len(deck_string.splitlines()) >= 10
        )

    def add_deck_from_clipboard(self):
        try:
            deck_string = pyperclip.paste()
            if not self.is_valid_deck(deck_string):
                log.error("Il mazzo copiato non è valido.")
                raise ValueError("Il mazzo copiato non è valido.")

            metadata = parse_deck_metadata(deck_string)
            deck_name = metadata["name"]
            cards = self.parse_cards_from_deck(deck_string)

            # Log informativo
            log.info(f"Tentativo di aggiunta del mazzo '{deck_name}' dagli appunti.")

            # Utilizzo di db_session per gestire la sessione
            with db_session():
                # Creazione del nuovo mazzo
                new_deck = Deck(
                    name=deck_name,
                    player_class=metadata["player_class"],
                    game_format=metadata["game_format"]
                )
                session.add(new_deck)

                # Sincronizzazione delle carte con il database
                self.sync_cards_with_database(deck_string)

                # Aggiunta delle relazioni tra mazzo e carte
                deck_cards = []
                for card_data in cards:
                    card = session.query(Card).filter_by(name=card_data["name"]).first()
                    if not card:
                        log.warning(f"Carta '{card_data['name']}' non trovata nel database.")
                        continue

                    deck_cards.append(DeckCard(deck_id=new_deck.id, card_id=card.id, quantity=card_data["quantity"]))
                
                session.bulk_save_objects(deck_cards)

            # Log di successo
            log.info(f"Mazzo '{deck_name}' aggiunto con successo.")
            return True  # Indica che l'operazione è riuscita


        except pyperclip.PyperclipException as e:
            log.error(f"Errore negli appunti: {str(e)}")
            raise

        except ValueError as e:
            log.warning(f"Errore di validazione: {str(e)}")
            raise

        except Exception as e:
            log.error(f"Errore imprevisto durante l'aggiunta del mazzo: {str(e)}")
            raise


    def sync_cards_with_database(self, deck_string):
        """ Sincronizza le carte del mazzo con il database. """

        log.info("Inizio sincronizzazione delle carte con il database.")
        try:
            cards = self.parse_cards_from_deck(deck_string)
            card_names = [card["name"] for card in cards]

            # Recupera tutte le carte esistenti in una singola query
            existing_cards = session.query(Card.name).filter(Card.name.in_(card_names)).all()
            existing_card_names = {card.name for card in existing_cards}

            # Filtra le nuove carte
            new_cards_data = [card for card in cards if card["name"] not in existing_card_names]

            # Crea una lista di oggetti Card per le nuove carte
            new_cards = [
                Card(
                    name=card_data["name"],
                    class_name="Unknown",
                    mana_cost=card_data["mana_cost"],
                    card_type="Unknown",
                    card_subtype="Unknown",
                    rarity="Unknown",
                    expansion="Unknown"
                )
                for card_data in new_cards_data
            ]

            # Inserisci tutte le nuove carte in una sola operazione
            session.bulk_save_objects(new_cards)
            session.commit()
            log.info("Sincronizzazione delle carte completata con successo.")

        except SQLAlchemyError as e:
            log.error(f"Errore del database durante la sincronizzazione: {str(e)}")
            session.rollback()
            raise
        except Exception as e:
            log.error(f"Errore imprevisto durante la sincronizzazione: {str(e)}")
            raise


    def parse_cards_from_deck(self, deck_string):
        cards = []
        pattern = r'^#*\s*(\d+)x?\s*\((\d+)\)\s*(.+)$'
        
        for line in deck_string.splitlines():
            try:
                match = re.match(pattern, line.strip())
                if match and not line.startswith("###"):
                    quantity = int(match.group(1))
                    mana_cost = int(match.group(2))
                    name = match.group(3).strip()
                    
                    # Pulizia nome per casi particolari
                    name = re.sub(r'\s*\d+$', '', name)  # Rimuove numeri finali
                    name = re.sub(r'^[#\s]*', '', name)  # Rimuove caratteri speciali iniziali
                    
                    cards.append({
                        "name": name,
                        "mana_cost": mana_cost,
                        "quantity": quantity
                    })
                    
            except (ValueError, IndexError) as e:
                log.warning(f"Errore durante il parsing della riga: {line}. Dettagli: {str(e)}")
            except Exception as e:
                log.error(f"Errore imprevisto durante il parsing della riga: {line}. Dettagli: {str(e)}")

        if not cards:
            log.warning("Nessuna carta valida trovata nel mazzo.")
        
        return cards


    def is_card_in_database(self, card_name):
        """Verifica se una carta esiste nel database."""
        return session.query(Card).filter_by(name=card_name).first() is not None

    def add_card_to_database(self, card):
        """Aggiunge una nuova carta al database."""
        new_card = Card(
            name=card["name"],
            class_name="Unknown",
            mana_cost=card["mana_cost"],
            card_type="Unknown",
            card_subtype="Unknown",
            rarity="Unknown",
            expansion="Unknown"
        )
        session.add(new_card)
        session.commit()
        log.info(f"Carta '{card['name']}' aggiunta al database.")

    def get_deck(self, deck_name):
        """Restituisce il contenuto di un mazzo dal database."""
        deck = session.query(Deck).filter_by(name=deck_name).first()
        if deck:
            deck_cards = session.query(DeckCard).filter_by(deck_id=deck.id).all()
            cards = []
            for deck_card in deck_cards:
                card = session.query(Card).filter_by(id=deck_card.card_id).first()
                if card:
                    cards.append({
                        "name": card.name,
                        "mana_cost": card.mana_cost,
                        "quantity": deck_card.quantity
                    })
            return {
                "name": deck.name,
                "player_class": deck.player_class,
                "game_format": deck.game_format,
                "cards": cards
            }
        return None

    def delete_deck(self, deck_name):
        """ Elimina un mazzo dal database. """

        try:
            with db_session():
                deck = session.query(Deck).filter_by(name=deck_name).first()
                if not deck:
                    log.warning(f"Tentativo di eliminazione del mazzo '{deck_name}' non trovato.")
                    return

                # Elimina le carte associate al mazzo
                session.query(DeckCard).filter_by(deck_id=deck.id).delete()
                # Elimina il mazzo
                session.delete(deck)

            log.info(f"Mazzo '{deck_name}' eliminato con successo.")
            return True


        except SQLAlchemyError as e:
            log.error(f"Errore del database durante l'eliminazione del mazzo '{deck_name}': {str(e)}")
            session.rollback() # Annulla le modifiche in caso di errore

        except Exception as e:
            log.error(f"Errore imprevisto durante l'eliminazione del mazzo '{deck_name}': {str(e)}")
            raise


    def get_deck_statistics(self, deck_name):
        """Calcola statistiche dettagliate per un mazzo."""
        deck = self.get_deck(deck_name)
        if not deck:
            return None

        stats = {
            "Nome Mazzo": deck["name"],
            "Eroe": deck["player_class"],
            "Numero Carte": sum(card["quantity"] for card in deck["cards"]),
            "Creature": 0,
            "Magie": 0,
            "Armi": 0,
            "Luoghi": 0,
            "Costo Mana Medio": 0.0
        }

        total_mana = 0
        for card in deck["cards"]:
            db_card = session.query(Card).filter_by(name=card["name"]).first()
            if db_card:
                card_type = db_card.card_type.lower()
                if card_type == "creatura":
                    stats["Creature"] += card["quantity"]
                elif card_type == "magia":
                    stats["Magie"] += card["quantity"]
                elif card_type == "arma":
                    stats["Armi"] += card["quantity"]
                elif card_type == "luogo":
                    stats["Luoghi"] += card["quantity"]

                # Calcola il costo totale del mana
                total_mana += db_card.mana_cost * card["quantity"]

        if stats["Numero Carte"] > 0:
            stats["Costo Mana Medio"] = total_mana / stats["Numero Carte"]

        # Arrotonda i valori a 2 decimali
        for key, value in stats.items():
            if isinstance(value, float):
                stats[key] = round(value, 2)

        return stats



#@@@# Fine del modulo
if __name__ != "__main__":
    print("Carico: %s" % __name__)

"""
views.py

Modulo per le finestre di dialogo dell'interfaccia utente.

path:
    scr/views.py

Descrizione:
    Contiene le classi per:
    - DeckStatsDialog: Visualizza le statistiche di un mazzo
    - FilterDialog: Gestisce i filtri di ricerca
    - CardCollectionDialog: Mostra la collezione di carte

Utilizzo:
    Importare le classi necessarie e utilizzarle nell'interfaccia principale.
"""

import wx
import logging
from .db import session, Card
from utyls.enu_glob import EnuColors, ENUCARD, EnuExtraCard, EnuCardType, EnuHero, EnuRarity, EnuExpansion
from utyls import logger as log
#import pdb



class CardEditDialog(wx.Dialog):
    """Finestra di dialogo per aggiungere o modificare una carta."""

    def __init__(self, parent, card=None):
        title = "Modifica Carta" if card else "Aggiungi Carta"
        super().__init__(parent, title=title, size=(400, 400))
        self.SetBackgroundColour('green')
        self.card = card
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Campi di input
        fields = [
            ("Nome:", wx.TextCtrl(panel)),
            ("Classe:", wx.ComboBox(panel, choices=[h.value for h in EnuHero], style=wx.CB_READONLY)),
            ("Costo Mana:", wx.SpinCtrl(panel, min=0, max=20)),
            ("Tipo:", wx.ComboBox(panel, choices=[t.value for t in EnuCardType], style=wx.CB_READONLY)),
            ("Rarità:", wx.ComboBox(panel, choices=[r.value for r in EnuRarity], style=wx.CB_READONLY)),
            ("Espansione:", wx.ComboBox(panel, choices=[e.value for e in EnuExpansion], style=wx.CB_READONLY))
        ]

        # Aggiungi i campi alla finestra
        for label, control in fields:
            row = wx.BoxSizer(wx.HORIZONTAL)
            row.Add(wx.StaticText(panel, label=label), flag=wx.LEFT | wx.RIGHT, border=10)
            row.Add(control, proportion=1)
            sizer.Add(row, flag=wx.EXPAND | wx.ALL, border=5)
            setattr(self, label.lower().replace(" ", "_").replace(":", ""), control)

        # Pulsanti
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_save = wx.Button(panel, label="Salva")
        btn_close = wx.Button(panel, label="Chiudi")
        btn_sizer.Add(btn_save, flag=wx.RIGHT, border=10)
        btn_sizer.Add(btn_close)

        # Eventi
        btn_save.Bind(wx.EVT_BUTTON, self.on_save)
        btn_close.Bind(wx.EVT_BUTTON, lambda e: self.Close())

        sizer.Add(btn_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)
        panel.SetSizer(sizer)
        self.Centre()

        # Se è una modifica, pre-carica i dati della carta
        if self.card:
            self.nome.SetValue(self.card.name)
            self.classe.SetValue(self.card.class_name)
            self.costo_mana.SetValue(self.card.mana_cost)
            self.tipo.SetValue(self.card.card_type)
            self.rarità.SetValue(self.card.rarity)
            self.espansione.SetValue(self.card.expansion)

    def on_save(self, event):
        """Salva la carta nel database."""
        try:
            card_data = {
                "name": self.nome.GetValue(),
                "class_name": self.classe.GetValue(),
                "mana_cost": self.costo_mana.GetValue(),
                "card_type": self.tipo.GetValue(),
                "rarity": self.rarità.GetValue(),
                "expansion": self.espansione.GetValue()
            }

            if self.card:
                # Modifica la carta esistente
                self.card.name = card_data["name"]
                self.card.class_name = card_data["class_name"]
                self.card.mana_cost = card_data["mana_cost"]
                self.card.card_type = card_data["card_type"]
                self.card.rarity = card_data["rarity"]
                self.card.expansion = card_data["expansion"]
            else:
                # Aggiungi una nuova carta
                new_card = Card(**card_data)
                session.add(new_card)

            session.commit()
            self.EndModal(wx.ID_OK)  # Chiudi la finestra e notifica che i dati sono stati salvati

        except Exception as e:
            wx.MessageBox(f"Errore durante il salvataggio: {str(e)}", "Errore")



class DeckStatsDialog(wx.Dialog):
    """Finestra di dialogo per visualizzare le statistiche di un mazzo."""
    def __init__(self, parent, stats):
        super().__init__(parent, title="Statistiche Mazzo", size=(300, 390))
        self.SetBackgroundColour('green')
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Titolo
        title = wx.StaticText(panel, label="Statistiche del Mazzo")
        title.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer.Add(title, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)
        
        # Statistiche
        for key, value in stats.items():
            row = wx.BoxSizer(wx.HORIZONTAL)
            row.Add(wx.StaticText(panel, label=f"{key}:"), flag=wx.LEFT, border=20)
            row.Add(wx.StaticText(panel, label=str(value)), flag=wx.LEFT|wx.RIGHT, border=20)
            sizer.Add(row, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=5)

        # impostiamo un separatore tra le statistiche delmazzo ed il pusante chiudi.
        sizer.Add(wx.StaticLine(panel), flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=10)

        # Pulsante Chiudi
        btn_close = wx.Button(panel, label="Chiudi", size=(100, 30))
        btn_close.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        sizer.Add(btn_close, flag=wx.ALIGN_CENTER|wx.ALL, border=10)
        
        panel.SetSizer(sizer)
        self.Centre()

class FilterDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Filtri di Ricerca", size=(300, 300))
        self.SetBackgroundColour('green')
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Elementi UI
        self.search_ctrl = wx.SearchCtrl(panel)
        self.mana_cost = wx.SpinCtrl(panel, min=0, max=20)
        self.card_type = wx.ComboBox(panel, choices=["Tutti"] + [t.value for t in EnuCardType], style=wx.CB_READONLY)  # Usa EnuCardType
        self.rarity = wx.ComboBox(panel, choices=["Tutti"] + [r.value for r in EnuRarity], style=wx.CB_READONLY)  # Usa EnuRarity

        # Layout
        controls = [
            ("Nome:", self.search_ctrl),
            ("Costo Mana:", self.mana_cost),
            ("Tipo:", self.card_type),
            ("Rarità:", self.rarity)
        ]
        for label, control in controls:
            row = wx.BoxSizer(wx.HORIZONTAL)
            row.Add(wx.StaticText(panel, label=label), flag=wx.LEFT|wx.RIGHT, border=10)
            row.Add(control, proportion=1)
            sizer.Add(row, flag=wx.EXPAND|wx.ALL, border=5)

        # Pulsanti
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_apply = wx.Button(panel, label="Applica")
        self.btn_cancel = wx.Button(panel, label="Annulla")
        btn_sizer.Add(self.btn_apply, flag=wx.RIGHT, border=10)
        btn_sizer.Add(self.btn_cancel)

        # Eventi
        self.btn_apply.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_OK))
        self.btn_cancel.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))

        sizer.Add(btn_sizer, flag=wx.ALIGN_RIGHT|wx.ALL, border=10)
        panel.SetSizer(sizer)
        self.Centre()



class CardCollectionDialog(wx.Dialog):
    def __init__(self, parent, deck_manager):
        super().__init__(parent, title="Collezione Carte", size=(800, 800))
        self.SetBackgroundColour('green')
        self.deck_manager = deck_manager
        self.current_filters = {}
        self.init_ui()
        self.load_cards()

    def init_ui(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Barra strumenti
        toolbar = wx.BoxSizer(wx.HORIZONTAL)
        self.search_ctrl = wx.SearchCtrl(panel)
        self.btn_filters = wx.Button(panel, label="Filtri Avanzati")
        toolbar.Add(self.search_ctrl, proportion=1, flag=wx.EXPAND)
        toolbar.Add(self.btn_filters, flag=wx.LEFT, border=10)
        
        # Lista carte
        self.card_list = wx.ListCtrl(
            panel, 
            style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.BORDER_SUNKEN
        )
        self.card_list.AppendColumn("Nome", width=200)
        self.card_list.AppendColumn("classe", width=150)
        self.card_list.AppendColumn("Mana", width=50)
        self.card_list.AppendColumn("Tipo", width=150)
        self.card_list.AppendColumn("Rarità", width=100)
        self.card_list.AppendColumn("Espansione", width=150)
        
        # Pulsanti azione
        btn_panel = wx.Panel(panel)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        for label in ["Aggiungi", "Modifica", "Elimina", "Chiudi"]:
            btn = wx.Button(btn_panel, label=label)
            btn_sizer.Add(btn, flag=wx.RIGHT, border=5)
            if label == "Aggiungi":
                btn.Bind(wx.EVT_BUTTON, self.on_add_card)
            elif label == "Modifica":
                btn.Bind(wx.EVT_BUTTON, self.on_edit_card)
            elif label == "Elimina":
                btn.Bind(wx.EVT_BUTTON, self.on_delete_card)
            else:
                btn.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        
        # Assemblaggio finale
        btn_panel.SetSizer(btn_sizer)
        sizer.Add(toolbar, flag=wx.EXPAND|wx.ALL, border=10)
        sizer.Add(self.card_list, proportion=1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(btn_panel, flag=wx.ALIGN_RIGHT|wx.ALL, border=10)
        
        # Eventi
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.on_search)
        self.btn_filters.Bind(wx.EVT_BUTTON, self.on_show_filters)
        
        panel.SetSizer(sizer)
        self.Centre()
    
    def load_cards(self, filters=None):
        """Carica le carte dal database applicando i filtri."""
        self.card_list.DeleteAllItems()
        query = session.query(Card)
        
        if filters:
            if filters.get("name"):
                query = query.filter(Card.name.ilike(f"%{filters['name']}%"))
            if filters.get("mana_cost", 0) > 0:
                query = query.filter(Card.mana_cost == filters["mana_cost"])
            if filters.get("card_type") not in [None, "Tutti"]:
                query = query.filter(Card.card_type == filters["card_type"])
            if filters.get("rarity") not in [None, "Tutti"]:
                query = query.filter(Card.rarity == filters["rarity"])

        # Aggiungi le carte alla lista
        for card in query.order_by(Card.mana_cost, Card.name):
            self.card_list.Append([
                card.name,
                card.class_name,
                str(card.mana_cost),
                card.card_type,
                card.rarity,
                card.expansion
            ])

    def on_search(self, event):
        """Gestisce la ricerca testuale."""
        self.current_filters["name"] = self.search_ctrl.GetValue()
        self.load_cards(self.current_filters)
    
    def on_show_filters(self, event):
        """Mostra la finestra dei filtri avanzati."""
        dlg = FilterDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.current_filters.update({
                "name": dlg.search_ctrl.GetValue(),
                "mana_cost": dlg.mana_cost.GetValue(),
                "card_type": dlg.card_type.GetValue(),
                "rarity": dlg.rarity.GetValue()
            })
            self.load_cards(self.current_filters)
        dlg.Destroy()

    def on_add_card(self, event):
        """Apre la finestra per aggiungere una nuova carta."""
        dlg = CardEditDialog(self)
        if dlg.ShowModal() == wx.ID_OK:  # Se l'utente ha premuto "Salva"
            self.load_cards(self.current_filters)  # Ricarica la lista delle carte
        dlg.Destroy()

    def on_edit_card(self, event):
        """Apre la finestra per modificare una carta esistente."""
        selected = self.card_list.GetFirstSelected()
        if selected != -1:
            name = self.card_list.GetItemText(selected)
            card = session.query(Card).filter_by(name=name).first()
            if card:
                dlg = CardEditDialog(self, card)
                if dlg.ShowModal() == wx.ID_OK:  # Se l'utente ha premuto "Salva"
                    self.load_cards(self.current_filters)  # Ricarica la lista delle carte
                dlg.Destroy()
            else:
                wx.MessageBox("Carta non trovata nel database.", "Errore")
        else:
            wx.MessageBox("Seleziona una carta da modificare.", "Errore")

    def on_delete_card(self, event):
        """Elimina la carta selezionata."""

        selected = self.card_list.GetFirstSelected()
        if selected != -1:
            name = self.card_list.GetItemText(selected)
            if wx.MessageBox(f"Eliminare la carta '{name}'?", "Conferma", wx.YES_NO) == wx.YES:
                card = session.query(Card).filter_by(name=name).first()
                if card:
                    session.delete(card)
                    session.commit()
                    self.card_list.DeleteAllItems() # Svuota la lista delle carte
                    self.load_cards(self.current_filters)
                    logging.info(f"Carta '{name}' eliminata")
                else:
                    logging.error(f"Carta '{name}' non trovata")
                    wx.MessageBox("Carta non trovata nel database.", "Errore")
        else:
                logging.error("Nessuna carta selezionata")
                wx.MessageBox("Seleziona una carta da eliminare.", "Errore")




#@@@# Start del modulo
if __name__ != "__main__":
    print("Carico: %s." % __name__)

"""
    app.py

    Modulo principale dell'applicazione Hearthstone Deck Manager.

    Path:
        scr/app.py

    Componenti:

    - HearthstoneApp (Finestra principale):
        - Gestisce l'interfaccia utente principale tramite wxPython.
        - Visualizza l'elenco dei mazzi in un controllo (wx.ListCtrl) con colonne per nome, classe e formato.
        - Include una barra di ricerca per filtrare i mazzi.
        - Presenta vari pulsanti per operazioni quali aggiunta, copia, visualizzazione, aggiornamento, eliminazione dei mazzi, visualizzazione della collezione carte e uscita dall'applicazione.
        - Gestisce una barra di stato per mostrare messaggi informativi.
        
    - AppController (Controller):
        - Coordina le operazioni tra l'interfaccia utente e il gestore dei mazzi (DeckManager).
        - Gestisce eventi dell'interfaccia quali l'aggiunta di un mazzo (importandolo dagli appunti), la cancellazione di un mazzo e il recupero delle statistiche del mazzo.

    Descrizione:

        Questo modulo rappresenta il cuore dell'applicazione, coordinando l'interazione tra l'interfaccia grafica, il database e la logica di gestione dei mazzi.
        Le funzionalità principali includono:

          - Visualizzazione e aggiornamento dell'elenco dei mazzi.
          - Gestione degli eventi dell'utente per l'aggiunta (tramite contenuti copiati negli appunti), la copia (formattazione e copia negli appunti), la visualizzazione dettagliata, l'aggiornamento e l'eliminazione dei mazzi.
          - Calcolo e visualizzazione delle statistiche dei mazzi (attraverso l'integrazione con il DeckManager e l'utilizzo di dialoghi specifici come DeckStatsDialog).
          - Accesso alla collezione delle carte tramite CardCollectionDialog.
          
    Dipendenze:
        - wxPython: per l'interfaccia grafica.
        - pyperclip: per l'interazione con gli appunti.
        - logging: per la gestione e il tracciamento degli errori.
        - SQLAlchemy (attraverso scr.db): per la gestione del database contenente i mazzi e le carte.
        - Moduli interni (scr.models, scr.views, utyls.enu_glob, utyls.logger): per la gestione dei mazzi, dei dialoghi e per il logging personalizzato.

    Utilizzo:
        L'applicazione viene avviata creando un'istanza di wx.App, istanziando HearthstoneApp e avviando il MainLoop di wxPython.

    Note:
        - Il modulo sfrutta il pattern MVC in maniera semplificata, con HearthstoneApp che rappresenta la vista e AppController che gestisce la logica applicativa.
        - La gestione dei mazzi si avvale di DeckManager, il quale si occupa anche di importare mazzi dagli appunti, effettuare parsing dei dati e interfacciarsi con il database.
"""

# lib
import wx
import logging
import pyperclip
from scr.db import session, Deck, DeckCard, Card
from sqlalchemy.exc import SQLAlchemyError
from scr.models import Deck
from scr.models import DeckManager, parse_deck_metadata
from scr.views import CardCollectionDialog, DeckStatsDialog
from scr.db import session
from utyls import enu_glob as eg
from utyls import logger as log
#import pdb



class AppController:
    """ Controller per la gestione delle operazioni dell'applicazione. """

    def __init__(self, deck_manager, app):
        self.deck_manager = deck_manager
        self.app = app

    def add_deck(self, deck_name):
        try:
            self.deck_manager.add_deck_from_clipboard(deck_name)
            self.app.update_deck_list()
            self.app.update_status(f"Mazzo '{deck_name}' aggiunto con successo.")
            wx.MessageBox(f"Mazzo '{deck_name}' aggiunto con successo.", "Successo")
        except ValueError as e:
            wx.MessageBox(str(e), "Errore")
        except Exception as e:
            logging.error(f"Errore durante l'aggiunta del mazzo: {e}")
            wx.MessageBox(f"Si è verificato un errore: {e}", "Errore")

    def delete_deck(self, deck_name):
        try:
            if self.deck_manager.delete_deck(deck_name):
                self.app.update_deck_list()
                self.app.update_status(f"Mazzo '{deck_name}' eliminato con successo.")
                log.info(f"Mazzo '{deck_name}' eliminato con successo.")
                return True

        except SQLAlchemyError as e:
            wx.MessageBox("Errore del database. Verificare le procedure.", "Errore")

        except Exception as e:
            wx.MessageBox(f"Si è verificato un errore: {e}", "Errore")

    def get_deck_statistics(self, deck_name):
        """Restituisce le statistiche del mazzo."""
        return self.deck_manager.get_deck_statistics(deck_name)



class HearthstoneApp(wx.Frame):
    """ Finestra principale dell'applicazione. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.deck_manager = DeckManager()
        self.controller = AppController(self.deck_manager, self)
        self.init_ui()


    def init_ui(self):
        """ Inizializza l'interfaccia utente. """

        # Impostazioni finestra principale
        self.SetBackgroundColour('green')
        self.panel = wx.Panel(self)

        # Layout principale
        self.Centre()
        lbl_title = wx.StaticText(self.panel, label="Elenco Mazzi")
        #self.deck_list = wx.ListBox(self.panel)
        self.deck_list = wx.ListCtrl(
            self.panel,
            #style=wx.LC_REPORT | wx.BORDER_SUNKEN
            style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.BORDER_SUNKEN
        )

        # aggiungiamo le righe e le colonne
        self.deck_list.InsertColumn(0, "mazzo", width=260)
        self.deck_list.InsertColumn(1, "Classe ", width=200)
        self.deck_list.InsertColumn(2, "Formato ", width=120)

        # carichiamo i mazzi
        self.load_decks()

        # Barra di ricerca
        self.search_bar = wx.SearchCtrl(self.panel)
        self.search_bar.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.on_search)

        # Pulsanti
        btn_add = wx.Button(self.panel, label="Aggiungi Mazzo")
        btn_copy = wx.Button(self.panel, label="Copia Mazzo")
        btn_view = wx.Button(self.panel, label="Visualizza Mazzo")
        btn_stats = wx.Button(self.panel, label="Statistiche Mazzo")
        btn_update = wx.Button(self.panel, label="Aggiorna Mazzo")
        btn_delete = wx.Button(self.panel, label="Elimina Mazzo")
        btn_collection = wx.Button(self.panel, label="Collezione Carte")
        btn_exit = wx.Button(self.panel, label="Esci")

        # Layout principale
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(lbl_title, flag=wx.CENTER | wx.TOP, border=10)
        sizer.Add(self.search_bar, flag=wx.EXPAND | wx.ALL, border=5)

        # Separatore tra barra di ricerca e lista dei mazzi
        sizer.Add(wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)
        sizer.Add(self.deck_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Separatore tra lista dei mazzi e pulsanti
        sizer.Add(wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        # Layout pulsanti
        btn_sizer = wx.GridSizer(rows=4, cols=2, hgap=10, vgap=10)
        btn_sizer.Add(btn_add, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_copy, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_view, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_stats, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_update, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_delete, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_collection, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_exit, flag=wx.EXPAND | wx.ALL, border=5)
        sizer.Add(btn_sizer, flag=wx.EXPAND | wx.ALL, border=10)

        # Separatore tra pulsanti e barra di stato
        sizer.Add(wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        self.panel.SetSizer(sizer)

        # Barra di stato
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("Pronto")

        # Eventi
        btn_add.Bind(wx.EVT_BUTTON, self.on_add_deck)
        btn_copy.Bind(wx.EVT_BUTTON, self.on_copy_deck)
        btn_view.Bind(wx.EVT_BUTTON, self.on_view_deck)
        btn_update.Bind(wx.EVT_BUTTON, self.on_update_deck)
        btn_stats.Bind(wx.EVT_BUTTON, self.on_view_stats)
        btn_collection.Bind(wx.EVT_BUTTON, self.on_view_collection)
        btn_delete.Bind(wx.EVT_BUTTON, self.on_delete_deck)
        btn_exit.Bind(wx.EVT_BUTTON, self.on_exit)


    def load_decks(self):
        """Carica i mazzi ."""

        # svuotiamo la
        #self.deck_list.DeleteAllItems()

        # carichiamo i mazzi
        decks = session.query(Deck).all()
        # utilizzando insert
        for deck in decks:
            Index = self.deck_list.InsertItem(self.deck_list.GetItemCount(), deck.name)
            self.deck_list.SetItem(Index, 1, deck.player_class)
            self.deck_list.SetItem(Index, 2, deck.game_format)


    def update_deck_list(self):
        """Aggiorna la lista dei mazzi."""

        self.deck_list.DeleteAllItems()  # Pulisce la lista

        decks = session.query(Deck).all()
        for deck in decks:
            index = self.deck_list.InsertItem(self.deck_list.GetItemCount(), deck.name)  # Prima colonna
            self.deck_list.SetItem(index, 1, deck.player_class)  # Seconda colonna
            self.deck_list.SetItem(index, 2, deck.game_format)  # Terza colonna


    def update_status(self, message):
        """Aggiorna la barra di stato."""
        self.status_bar.SetStatusText(message)


    def get_selected_deck(self):
        """Restituisce il mazzo selezionato nella lista."""

        selection = self.deck_list.GetFirstSelected()
        if selection != wx.NOT_FOUND:
            return self.deck_list.GetItemText(selection)
        return None


    def on_add_deck(self, event):
        """Aggiunge un mazzo dagli appunti con una finestra di conferma."""

        try:
            # Recupera la stringa del mazzo dagli appunti
            deck_string = pyperclip.paste()

            # Verifica se la stringa è un mazzo valido
            if not self.deck_manager.is_valid_deck(deck_string):
                wx.MessageBox("Il mazzo copiato non è valido.", "Errore")
                return

            # Estrae i metadati (nome, classe, formato) dalla stringa del mazzo
            metadata = parse_deck_metadata(deck_string)
            deck_name = metadata["name"]
            player_class = metadata["player_class"]
            game_format = metadata["game_format"]

            # Mostra una finestra di conferma con i dati estratti
            confirm_message = (
                f"È stato rilevato un mazzo valido negli appunti.\n\n"
                f"Nome: {deck_name}\n"
                f"Classe: {player_class}\n"
                f"Formato: {game_format}\n\n"
                f"Vuoi utilizzare questi dati per creare il mazzo?"
            )

            confirm_dialog = wx.MessageDialog(
                self,
                confirm_message,
                "Conferma Creazione Mazzo",
                wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION
            )

            # Gestisce le risposte dell'utente
            result = confirm_dialog.ShowModal()
            if result == wx.ID_YES:
                # Utilizza i dati estratti per creare il mazzo
                success = self.deck_manager.add_deck_from_clipboard()
                if success:
                    self.update_deck_list()
                    self.update_status("Mazzo aggiunto con successo.")
                    wx.MessageBox("Mazzo aggiunto con successo.", "Successo")

            elif result == wx.ID_NO:
                # Chiede di inserire manualmente il nome del mazzo
                name_dialog = wx.TextEntryDialog(
                    self,
                    "Inserisci il nome per il nuovo mazzo:",
                    "Nome del Mazzo",
                    deck_name  # Suggerisci il nome estratto come valore predefinito
                )

                if name_dialog.ShowModal() == wx.ID_OK:
                    new_name = name_dialog.GetValue()
                    if new_name:
                        metadata["name"] = new_name
                        success = self.deck_manager.add_deck_from_clipboard()
                        if success:
                            self.update_deck_list()
                            self.update_status("Mazzo aggiunto con successo.")
                            wx.MessageBox("Mazzo aggiunto con successo.", "Successo")
                    else:
                        wx.MessageBox("Il nome del mazzo non può essere vuoto.", "Errore")
            elif result == wx.ID_CANCEL:
                # L'utente ha scelto di annullare l'operazione
                self.update_status("Operazione annullata.")
                wx.MessageBox("Operazione annullata.", "Annullato")

        except pyperclip.PyperclipException as e:
            wx.MessageBox("Errore negli appunti. Assicurati di aver copiato un mazzo valido.", "Errore")

        except ValueError as e:
            wx.MessageBox(str(e), "Errore")

        except Exception as e:
            log.error(f"Errore durante l'aggiunta del mazzo: {e}")
            wx.MessageBox("Si è verificato un errore imprevisto.", "Errore")


    def on_copy_deck(self, event):
        """Copia il mazzo selezionato negli appunti."""

        deck_name = self.get_selected_deck()
        if deck_name:
            deck_content = self.deck_manager.get_deck(deck_name)
            if deck_content:
                # Formatta il contenuto del mazzo in una stringa compatibile con Hearthstone
                deck_info = f"### {deck_content['name']}\n"
                deck_info += f"# Classe: {deck_content['player_class']}\n"
                deck_info += f"# Formato: {deck_content['game_format']}\n"
                deck_info += "# Anno del Pegaso\n"  # Espansione (puoi personalizzarla)
                deck_info += "#\n"
                
                # Aggiungi le carte
                for card in deck_content["cards"]:
                    deck_info += f"# {card['quantity']}x ({card['mana_cost']}) {card['name']}\n"

            # Aggiungi il codice del mazzo alla fine
                deck_info += "#\n"
                deck_info += "AAECAeSKBwaU1ATj+AXpngbSsAb3wAbO8QYMg58E0p8E7KAEx7AG7eoGn/EGwvEG3vEG4/EG5fEGqPcGiPgGAAA=\n#\n# Per utilizzare questo mazzo, copialo negli appunti e crea un nuovo mazzo in Hearthstone\n"

                # Copia il contenuto del mazzo negli appunti
                pyperclip.copy(deck_info)
                self.update_status(f"Mazzo '{deck_name}' copiato negli appunti.")
                wx.MessageBox(f"Mazzo '{deck_name}' copiato negli appunti.", "Successo")
            else:
                wx.MessageBox("Errore: Mazzo vuoto o non trovato.", "Errore")
        else:
            wx.MessageBox("Seleziona un mazzo prima di copiarlo negli appunti.", "Errore")

    def on_view_deck(self, event):
        """Mostra il mazzo selezionato."""

        deck_name = self.get_selected_deck()
        if deck_name:
            deck_content = self.deck_manager.get_deck(deck_name)
            if deck_content:
                # Formatta il contenuto del mazzo in una stringa leggibile
                deck_info = f"Mazzo: {deck_content['name']}\n"
                deck_info += f"Classe: {deck_content['player_class']}\n"
                deck_info += f"Formato: {deck_content['game_format']}\n\n"
                deck_info += "Carte:\n"
                for card in deck_content["cards"]:
                    deck_info += f"{card['quantity']}x {card['name']} (Mana: {card['mana_cost']})\n"
                
                # Mostra il contenuto del mazzo
                wx.MessageBox(deck_info, f"Mazzo: {deck_name}")
            else:
                wx.MessageBox("Errore: Mazzo vuoto o non trovato.", "Errore")
        else:
            wx.MessageBox("Seleziona un mazzo prima di visualizzarlo.", "Errore")

    def on_update_deck(self, event):
        """Aggiorna il mazzo selezionato con il contenuto degli appunti."""

        deck_name = self.get_selected_deck()
        if deck_name:
            if wx.MessageBox(
                f"Sei sicuro di voler aggiornare '{deck_name}' con il contenuto degli appunti?",
                "Conferma",
                wx.YES_NO
            ) == wx.YES:
                try:
                    deck_string = pyperclip.paste()
                    if self.deck_manager.is_valid_deck(deck_string):
                        # Trova il mazzo nel database
                        deck = session.query(Deck).filter_by(name=deck_name).first()
                        if deck:
                            # Elimina le vecchie relazioni mazzo-carta
                            session.query(DeckCard).filter_by(deck_id=deck.id).delete()
                            session.commit()

                            # Sincronizza le nuove carte con il database
                            self.deck_manager.sync_cards_with_database(deck_string)

                            # Aggiungi le nuove carte al mazzo
                            cards = self.deck_manager.parse_cards_from_deck(deck_string)
                            for card_data in cards:
                                # Verifica se la carta esiste già nel database
                                card = session.query(Card).filter_by(name=card_data["name"]).first()
                                if not card:
                                    # Se la carta non esiste, creala
                                    card = Card(
                                        name=card_data["name"],
                                        class_name="Unknown",
                                        mana_cost=card_data["mana_cost"],
                                        card_type="Unknown",
                                        card_subtype="Unknown",
                                        rarity="Unknown",
                                        expansion="Unknown"
                                    )
                                    session.add(card)
                                    session.commit()

                                # Aggiungi la relazione tra il mazzo e la carta
                                deck_card = DeckCard(deck_id=deck.id, card_id=card.id, quantity=card_data["quantity"])
                                session.add(deck_card)
                                session.commit()

                            self.update_deck_list()
                            self.update_status(f"Mazzo '{deck_name}' aggiornato con successo.")
                            wx.MessageBox(f"Mazzo '{deck_name}' aggiornato con successo.", "Successo")
                        else:
                            wx.MessageBox("Errore: Mazzo non trovato nel database.", "Errore")
                    else:
                        wx.MessageBox("Il mazzo negli appunti non è valido.", "Errore")
                except Exception as e:
                    logging.error(f"Errore durante l'aggiornamento del mazzo: {e}")
                    wx.MessageBox(f"Si è verificato un errore: {e}", "Errore")
        else:
            wx.MessageBox("Seleziona un mazzo prima di aggiornarlo.", "Errore")

    def on_view_stats(self, event):
        """Mostra le statistiche del mazzo selezionato."""

        deck_name = self.get_selected_deck()
        if deck_name:
            stats = self.controller.get_deck_statistics(deck_name)
            if stats:
                DeckStatsDialog(self, stats).ShowModal()  # Mostra la finestra come modale
            else:
                wx.MessageBox("Impossibile calcolare le statistiche per questo mazzo.", "Errore")
        else:
            wx.MessageBox("Seleziona un mazzo prima di visualizzare le statistiche.", "Errore")

    def on_view_collection(self, event):
        """Mostra la collezione delle carte."""

        collection_dialog = CardCollectionDialog(self, self.deck_manager)
        collection_dialog.ShowModal()  # Mostra la finestra come modale

    def on_delete_deck(self, event):
        """Elimina il mazzo selezionato."""

        deck_name = self.get_selected_deck()
        if deck_name:
            if wx.MessageBox(f"Sei sicuro di voler eliminare '{deck_name}'?", "Conferma", wx.YES_NO) == wx.YES:
                try:
                    #success = self.deck_manager.delete_deck(deck_name)
                    success = self.controller.delete_deck(deck_name)
                    if success:
                        self.update_deck_list()
                        self.update_status(f"Mazzo '{deck_name}' eliminato con successo.")
                        wx.MessageBox(f"Mazzo '{deck_name}' eliminato con successo.", "Successo")
                    else:
                        wx.MessageBox(f"Mazzo '{deck_name}' non trovato.", "Errore")

                except SQLAlchemyError as e:
                    wx.MessageBox("Errore del database. Verificare le procedure.", "Errore")

                except Exception as e:
                    wx.MessageBox("Si è verificato un errore imprevisto.", "Errore")
        else:
            wx.MessageBox("Seleziona un mazzo prima di eliminarlo.", "Errore")

    def on_search(self, event):
        """Filtra i mazzi in base al testo di ricerca."""

            # cerchiamo la parola richeista dall0utente sia nei nomi dei mazzi sia nella classe
        search_text = self.search_bar.GetValue()
        self.deck_list.DeleteAllItems()
        decks = session.query(Deck).filter(Deck.name.ilike(f"%{search_text}%") | Deck.player_class.ilike(f"%{search_text}%")).all()
        for deck in decks:
            Index = self.deck_list.InsertItem(self.deck_list.GetItemCount(), deck.name)
            self.deck_list.SetItem(Index, 1, deck.player_class)
            self.deck_list.SetItem(Index, 2, deck.game_format)


    def on_exit(self, event):
        """Chiude l'applicazione."""

        self.Close()




#@@@# Start del modulo
if __name__ != "__main__":
    print("Carico: %s." % __name__)

"""
    Progetto gestione e salvataggio mazzi di Hearthstone

    Autore: Nemex81
    E-mail: nemex1981@gmail.com
    Versione: 0.5

    path:
        ./main.py

    Descrizione:

        Questo progetto implementa un'applicazione per la gestione di mazzi del gioco di carte collezionabili Hearthstone.
        Permette di creare, salvare, caricare, modificare e visualizzare mazzi di Hearthstone.
        Include anche una funzionalità per la gestione di una collezione di carte, con la possibilità di filtrare le carte
        per nome, costo in mana, tipo, sottotipo, rarità ed espansione.

    Cartelle:
        - img:              Contiene le immagini utilizzate nell'applicazione.
        - scr:              Contiene i moduli principali dell'applicazione.
        - utyls:            Contiene funzioni, enum e costanti di utilità generiche in uso nel progetto.

    Moduli:

        - main.py:          Modulo principale. Avvia l'applicazione e gestisce le configurazioni generali.
        - app.py:           Contiene la logica dell'applicazione, incluse la finestra principale (HearthstoneApp) e il controller (AppController).
        - db.py:            Gestisce l'interazione con il database SQLite per la memorizzazione delle carte. Definisce il modello Card e la funzione setup_database.
        - models.py:        Definisce la classe DeckManager per la gestione dei mazzi (caricamento, salvataggio, parsing, ecc.).
        - views.py:         Contiene le classi per le finestre di dialogo dell'interfaccia utente (CollectionDialog, FilterDialog, DeckStatsDialog).
        - config.py:        (Opzionale) Definisce le costanti di configurazione, come il percorso del database e altre costanti di sistema.
        - enu_glob.py:         Contiene le enum  globali in uso nel progetto.
        - utyls.py:         Contiene funzioni di utilità generiche utilizzate in tutto il progetto.
        - logger.py:        Contiene la classe Logger per la gestione dei log dell'applicazione.
        - screen_reader.py:  Contiene la classe ScreenReader per la lettura dello schermo e l'interazione con le finestre di Hearthstone.

    Funzionamento:

        L'applicazione utilizza la libreria wxPython per l'interfaccia grafica e SQLAlchemy per la gestione del database.
        I mazzi sono salvati in un file JSON (decks.json, configurabile in config.py).
        Le carte sono memorizzate in un database SQLite (hearthstone_decks_storage.db, configurabile in config.py).

    Esecuzione:

        Per avviare l'applicazione, eseguire il comando:
            python main.py

    librerie necessarie:
                            pip install wxPython sqlalchemy pyperclip

"""

# lib
import wx
from scr.app import HearthstoneApp



if __name__ == "__main__":
    app = wx.App(False)
    frame = HearthstoneApp(None, title="Hearthstone Deck Manager", size=(650, 700))
    frame.Show()
    app.MainLoop()
