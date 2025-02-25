"""
    controller.py

    Modulo principale per la gestione dell'applicazione Hearthstone Deck Manager.

    Path:
        scr/controller.py

    Descrizione:
                Questo modulo rappresenta il cuore dell'applicazione, coordinando l'interazione tra le interfacce grafiche, il database e la logica di gestione.
                La classe HearthstoneManager si occupa di inizializzare l'applicazione, creare le finestre principali e gestire le operazioni di visualizzazione e modifica dei mazzi e delle carte.
                L'applicazione segue il pattern MVC, con la classe HearthstoneManager che funge da controller, le finestre come viste e il database come modello.

"""

# lib
import wx
from .models import load_cards
from .views.main_views import HearthstoneAppFrame
from .views.collection_view import CardCollectionFrame
from .views.deck_view import DeckViewFrame
from .views.decks_view import DecksManagerFrame
from utyls import enu_glob as eg
from utyls import helper as hp
from utyls import logger as log
#import pdb



class CollectionController:
    """Controller per la vista della collezione di carte."""

    def __init__(self, parent=None, db_manager=None):
        self.parent = parent            # Riferimento al controller principale
        self.db_manager = db_manager    # Istanza di DbManager

    def load_collection(self, filters=None):
        """
        Carica la collezione di carte dal database, applicando eventuali filtri.

        Args:
            filters (dict, optional): Dizionario di filtri da applicare. Default è None.

        Returns:
            list: Lista di carte che soddisfano i filtri.

        """

        try:
            # Utilizza il DbManager per caricare le carte
            cards = self.db_manager.get_cards(filters=filters)
            return cards

        except Exception as e:
            log.error(f"Errore durante il caricamento della collezione: {str(e)}")
            return []

    def add_card(self, card_data):
        """
        Aggiunge una nuova carta alla collezione.

        Args:
            card_data (dict): Dati della carta da aggiungere.

        Returns:
            bool: True se l'operazione è riuscita, False altrimenti.
        """
        try:
            # Verifica se la carta esiste già nel database
            if self.db_manager.get_card_by_name(card_data["name"]):
                log.warning(f"Carta '{card_data['name']}' già esistente.")
                return False

            # Aggiunge la carta al database utilizzando DbManager
            self.db_manager.add_card_to_database(card_data)
            log.info(f"Carta '{card_data['name']}' aggiunta con successo.")
            return True
        except Exception as e:
            log.error(f"Errore durante l'aggiunta della carta: {str(e)}")
            return False

    def edit_card(self, card_name, new_data):
        """
        Modifica una carta esistente nella collezione.

        Args:
            card_name (str): Nome della carta da modificare.
            new_data (dict): Nuovi dati della carta.

        Returns:
            bool: True se l'operazione è riuscita, False altrimenti.
        """
        try:
            # Recupera la carta dal database
            card = self.db_manager.get_card_by_name(card_name)
            if not card:
                log.warning(f"Carta '{card_name}' non trovata.")
                return False

            # Aggiorna i dati della carta
            updated_card = {**card, **new_data}  # Unisce i dati esistenti con i nuovi dati
            self.db_manager.add_card_to_database(updated_card)  # Sovrascrive la carta esistente
            log.info(f"Carta '{card_name}' modificata con successo.")
            return True
        except Exception as e:
            log.error(f"Errore durante la modifica della carta: {str(e)}")
            return False

    def delete_card(self, card_name):
        """
        Rimuove una carta dalla collezione.

        Args:
            card_name (str): Nome della carta da rimuovere.

        Returns:
            bool: True se l'operazione è riuscita, False altrimenti.
        """
        try:
            # Verifica se la carta esiste nel database
            card = self.db_manager.get_card_by_name(card_name)
            if not card:
                log.warning(f"Carta '{card_name}' non trovata.")
                return False

            # Elimina la carta utilizzando DbManager
            self.db_manager.delete_card(card_name)
            log.info(f"Carta '{card_name}' rimossa con successo.")
            return True
        except Exception as e:
            log.error(f"Errore durante la rimozione della carta: {str(e)}")
            return False



class DeckController:
    """ Controller per la vista di un mazzo. """

    def __init__(self, parent=None, db_manager=None):
        self.parent= parent
        self.db_manager = db_manager



class DecksController:
    """ Controller per la vista dei mazzi. """

    def __init__(self, parent=None, db_manager=None):
        self.parent= parent
        self.db_manager = db_manager


    def run_deck_frame(self, parent=None, controller=None, deck_name=None):
        """ carica l'interfaccia per la gestione di un mazzo. """

        frame = DeckViewFrame(parent, controller=self, deck_name=deck_name)
        frame.Show()



class MainController():
    """ gestore dell'applicazione. """

    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.collection_controller = None
        self.decks_controller = None
        self.deck_controller = None
        self.set_controllers()


    def set_collection_controller(self, controller=None):
        self.collection_controller = controller


    def set_decks_controller(self, controller=None):
        self.decks_controller = controller


    def set_deck_controller(self, controller=None):
        self.deck_controller = controller


    def set_controllers(self):
        """ inizializza i controller dell'applicazione. """

        # Inizializza i controller
        self.collection_controller = CollectionController(parent=self, db_manager=self.db_manager)
        self.decks_controller = DecksController(parent=self, db_manager=self.db_manager)
        self.deck_controller = DeckController(parent=self, db_manager=self.db_manager)

        # 
        self.set_collection_controller(self.collection_controller)
        self.set_decks_controller(self.decks_controller)
        self.set_deck_controller(self.deck_controller)


    def run_decks_frame(self, parent=None, controller=None):
        """ carica l'interfaccia per la gestione dei mazzi. """

        frame = DecksManagerFrame(parent, controller=self)
        frame.Show()


    def run_deck_frame(self, parent=None, controller=None, deck_name=None):
        """ carica l'interfaccia per la gestione di un mazzo. """

        frame = DeckViewFrame(parent, controller=self, deck_name=deck_name)
        frame.Show()


    def run_collection_frame(self, parent=None, controller=None):
        """ carica l'interfaccia pe rla collezzione completa di carte. """

        frame = CardCollectionFrame(parent=parent, controller=controller)
        frame.Show()


    def run(self):
        """ avvia l'applicazione. """

        app = wx.App(False)
        frame = HearthstoneAppFrame(parent=None, controller=self)
        frame.Show()
        app.MainLoop()





#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
