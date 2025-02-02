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

"""
    models.py

    Modulo per la gestione dei mazzi di Hearthstone e delle operazioni correlate.

  path:
        scr/models.py   

Descrizione:

    Questo modulo contiene la classe DeckManager che gestisce:
    - Caricamento/salvataggio dei mazzi da/in file JSON
    - Parsing delle carte dai mazzi
    - Sincronizzazione con il database
    - Calcolo delle statistiche dei mazzi

Utilizzo:
    from models import DeckManager
    from db import session

    deck_manager = DeckManager()
    deck_manager.add_deck_from_clipboard("Mazzo Prova")
"""

import json
import os
import shutil
import logging
import re
import wx
import pyperclip
from .db import session, Deck, DeckCard
from datetime import datetime
from .db import session, Card



def parse_deck_metadata(deck_string):
    """Estrae nome, classe e formato dal mazzo"""

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
        """Aggiunge un mazzo dagli appunti."""

        deck_string = pyperclip.paste()
        if self.is_valid_deck(deck_string):
            # Estrai i metadati del mazzo (incluso il nome)
            metadata = parse_deck_metadata(deck_string)
            deck_name = metadata["name"]

            # Prosegui con la creazione del mazzo
            cards = self.parse_cards_from_deck(deck_string)

            # Crea un nuovo mazzo nel database
            new_deck = Deck(
                name=deck_name,
                player_class=metadata["player_class"],
                game_format=metadata["game_format"]
            )
            session.add(new_deck)
            session.commit()

            # Sincronizza le carte con il database
            self.sync_cards_with_database(deck_string)

            # Aggiungi le carte al mazzo
            for card_data in cards:
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
                deck_card = DeckCard(deck_id=new_deck.id, card_id=card.id, quantity=card_data["quantity"])
                session.add(deck_card)
                session.commit()

            logging.info(f"Mazzo '{deck_name}' aggiunto con successo.")
            wx.MessageBox(f"Mazzo '{deck_name}' aggiunto con successo.", "Successo")
        else:
            raise ValueError("Il mazzo copiato non è valido.")
            logging.info(f"Mazzo '{deck_name}' aggiunto con successo.")
            wx.MessageBox("Il mazzo copiato non è valido.", "Errore")

    def last_add_deck_from_clipboard(self, deck_name):
        """Aggiunge un mazzo dagli appunti."""

        deck_string = pyperclip.paste()
        if self.is_valid_deck(deck_string):
            metadata = parse_deck_metadata(deck_string)
            cards = self.parse_cards_from_deck(deck_string)

            # Crea un nuovo mazzo nel database
            new_deck = Deck(
                name=deck_name,
                player_class=metadata["player_class"],
                game_format=metadata["game_format"]
            )
            session.add(new_deck)
            session.commit()

            # Sincronizza le carte con il database
            self.sync_cards_with_database(deck_string)

            # Aggiungi le carte al mazzo
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
                deck_card = DeckCard(deck_id=new_deck.id, card_id=card.id, quantity=card_data["quantity"])
                session.add(deck_card)
                session.commit()
            logging.info(f"Mazzo '{deck_name}' aggiunto con successo.")
        else:
            raise ValueError("Il mazzo copiato non è valido.")
        logging.info(f"Mazzo '{deck_name}' aggiunto con successo.")

    def sync_cards_with_database(self, deck_string):
        """Sincronizza le carte del mazzo con il database."""
        for card in self.parse_cards_from_deck(deck_string):
            if not self.is_card_in_database(card["name"]):
                self.add_card_to_database(card)

    def parse_cards_from_deck(self, deck_string):
        """Estrae le carte da una stringa di mazzo con regex migliorata."""

        cards = []
        pattern = r'^#*\s*(\d+)x?\s*\((\d+)\)\s*(.+)$'
        
        for line in deck_string.splitlines():
            match = re.match(pattern, line.strip())
            if match and not line.startswith("###"):
                try:
                    quantity = int(match.group(1))
                    mana_cost = int(match.group(2))
                    name = match.group(3).strip()
                    hero_class = name.split()[-1]  # Estrae la classe eroe dal nome
                    
                    # Pulizia nome per casi particolari
                    name = re.sub(r'\s*\d+$', '', name)  # Rimuove numeri finali
                    name = re.sub(r'^[#\s]*', '', name)  # Rimuove caratteri speciali iniziali
                    
                    cards.append({
                        "name": name,
                        "mana_cost": mana_cost,
                        "quantity": quantity
                    })
                    
                except (ValueError, IndexError) as e:
                    logging.warning(f"Errore parsing riga: {line} - {str(e)}")

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
        logging.info(f"Carta '{card['name']}' aggiunta al database.")

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
        """Elimina un mazzo esistente dal database."""
        deck = session.query(Deck).filter_by(name=deck_name).first()
        if deck:
            # Elimina le carte associate al mazzo
            session.query(DeckCard).filter_by(deck_id=deck.id).delete()
            # Elimina il mazzo
            session.delete(deck)
            session.commit()
            logging.info(f"Mazzo '{deck_name}' eliminato con successo.")
        else:
            logging.warning(f"Mazzo '{deck_name}' non trovato.")

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



class DeckStatsDialog(wx.Dialog):
    """Finestra di dialogo per visualizzare le statistiche di un mazzo."""
    def __init__(self, parent, stats):
        super().__init__(parent, title="Statistiche Mazzo", size=(300, 333))
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
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Elementi UI
        self.search_ctrl = wx.SearchCtrl(panel)
        self.mana_cost = wx.SpinCtrl(panel, min=0, max=20)
        self.card_type = wx.ComboBox(panel, choices=["Tutti", "Creatura", "Magia", "Arma"], style=wx.CB_READONLY)
        self.rarity = wx.ComboBox(panel, choices=["Tutti", "Comune", "Rara", "Epica", "Leggendaria"], style=wx.CB_READONLY)

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
        super().__init__(parent, title="Collezione Carte", size=(700, 700))
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
        logging.info("Aggiunta di una nuova carta (non implementato)")
        wx.MessageBox("Funzionalità non implementata.", "Errore")
    
    def on_edit_card(self, event):
        """Apre modificare una carta esistente."""
        logging.info("Modifica una carta (non implementato)")
        wx.MessageBox("Funzionalità non implementata.", "Errore")
    
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

Modulo principale dell'applicazione 

path:
    scr/app.py

Componenti:
- Finestra principale (HearthstoneApp): interfaccia utente principale dell'applicazione
- Controller (AppController): gestione degli eventi dell'interfaccia utente
- Gestione degli eventi dell'interfaccia utente: aggiunta, copia, visualizzazione, aggiornamento, eliminazione e statistiche dei mazzi

Descrizione:
    Questo modulo gestisce l'interfaccia utente principale e coordina
    le operazioni tra i vari componenti dell'applicazione.
"""

import wx
import logging
import pyperclip
from scr.db import session, Deck, DeckCard, Card
from scr.models import Deck
from scr.models import DeckManager
from scr.views import CardCollectionDialog, DeckStatsDialog
from scr.db import session
from utyls import enu_glob as eg



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
            self.deck_manager.delete_deck(deck_name)
            self.app.update_deck_list()
            self.app.update_status(f"Mazzo '{deck_name}' eliminato con successo.")
            wx.MessageBox(f"Mazzo '{deck_name}' eliminato con successo.", "Successo")
        except Exception as e:
            logging.error(f"Errore durante l'eliminazione del mazzo: {e}")
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
        self.SetBackgroundColour('black')
        self.panel = wx.Panel(self)

        # Layout principale
        self.Centre()
        lbl_title = wx.StaticText(self.panel, label="Elenco Mazzi")
        #self.deck_list = wx.ListBox(self.panel)
        self.deck_list = wx.ListCtrl(
            self.panel,
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
            #style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.BORDER_SUNKEN
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
        for deck in decks:
            self.deck_list.Append(deck.name)

    def update_deck_list(self):
        """Aggiorna la lista dei mazzi."""

        # Svuota la lista
        #self.deck_list.DeleteAllItems()
        decks = session.query(Deck).all()
        for deck in decks:
            self.deck_list.Append(deck.name)

    def update_status(self, message):
        """Aggiorna la barra di stato."""
        self.status_bar.SetStatusText(message)

    def get_selected_deck(self):
        """Restituisce il mazzo selezionato nella lista."""

        selection = self.deck_list.GetSelection()
        if selection != wx.NOT_FOUND:
            return self.deck_list.GetString(selection)
        return None

    def on_add_deck(self, event):
        """Aggiunge un mazzo dagli appunti."""

        try:
            self.deck_manager.add_deck_from_clipboard()
            self.update_deck_list()
            self.update_status("Mazzo aggiunto con successo.")

        except ValueError as e:
            wx.MessageBox(str(e), "Errore")

        except Exception as e:
            logging.error(f"Errore durante l'aggiunta del mazzo: {e}")
            wx.MessageBox(f"Si è verificato un errore: {e}", "Errore")

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
                deck_info += "# Anno del Pegaso\n\n"  # Espansione (puoi personalizzarla)
                
                # Aggiungi le carte
                for card in deck_content["cards"]:
                    deck_info += f"{card['quantity']}x ({card['mana_cost']}) {card['name']}\n"
                
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
                self.controller.delete_deck(deck_name)
        else:
            wx.MessageBox("Seleziona un mazzo prima di eliminarlo.", "Errore")

    def on_search(self, event):
        """Filtra i mazzi in base alla ricerca."""
        search_term = self.search_bar.GetValue().lower()
        decks = session.query(Deck).filter(Deck.name.ilike(f"%{search_term}%")).all()
        #self.deck_list.DeleteAllItems()
        for deck in decks:
            self.deck_list.Append(deck.name)

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

Moduli:

    - main.py:          Modulo principale. Avvia l'applicazione e gestisce le configurazioni generali.
    - app.py:           Contiene la logica dell'applicazione, incluse la finestra principale (HearthstoneApp) e il controller (AppController).
    - db.py:            Gestisce l'interazione con il database SQLite per la memorizzazione delle carte. Definisce il modello Card e la funzione setup_database.
    - models.py:        Definisce la classe DeckManager per la gestione dei mazzi (caricamento, salvataggio, parsing, ecc.).
    - views.py:         Contiene le classi per le finestre di dialogo dell'interfaccia utente (CollectionDialog, FilterDialog, DeckStatsDialog).
    - config.py:        (Opzionale) Definisce le costanti di configurazione, come il percorso del database e il percorso del file JSON dei mazzi.

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

"""
main.py

Punto di ingresso principale dell'applicazione.
"""

# lib
import wx
from scr.app import HearthstoneApp

if __name__ == "__main__":
    app = wx.App(False)
    frame = HearthstoneApp(None, title="Hearthstone Deck Manager", size=(650, 700))
    frame.Show()
    app.MainLoop()
