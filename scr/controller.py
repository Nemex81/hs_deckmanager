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
from .views.main_views import HearthstoneAppFrame
from .views.collection_view import CardCollectionFrame
from .views.deck_view import DeckViewFrame
from .views.decks_view import DecksManagerFrame
from utyls import enu_glob as eg
from utyls import helper as hp
from utyls import logger as log
#import pdb



class DeckController:
    """ Controller per la vista di un mazzo. """

    def __init__(self, parent=None, db_manager=None):
        self.parent= parent
        self.db_manager = db_manager



class CollectionController:
    """ Controller per la vista della collezione di carte. """

    def __init__(self, parent=None, db_manager=None):
        self.parent= parent
        self.db_manager = db_manager



class DecksController:
    """ Controller per la vista dei mazzi. """

    def __init__(self, parent=None, db_manager=None):
        self.parent= parent
        self.db_manager = db_manager


    def run_dec_frame(self, parent=None, controller=None, deck_name=None):
        """ carica l'interfaccia per la gestione di un mazzo. """

        frame = DeckViewFrame(parent, controller=self.parent.deck_controller, deck_name=deck_name)
        frame.Show()



class HearthstoneManager():
    """ gestore dell'applicazione. """

    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.collection_controller = None
        self.decks_controller = None
        self.deck_controller = None


    def set_collection_controller(self, controller=None):
        self.collection_controller = controller


    def set_decks_controller(self, controller=None):
        self.decks_controller = controller


    def set_deck_controller(self, controller=None):
        self.deck_controller = controller


    def run_decks_frame(self, parent=None, controller=None, deck_name=None):
        """ carica l'interfaccia per la gestione dei mazzi. """

        frame = DecksManagerFrame(parent, controller=self.decks_controller)
        frame.Show()


    def run_dec_frame(self, parent=None, controller=None, deck_name=None):
        """ carica l'interfaccia per la gestione di un mazzo. """

        frame = DeckViewFrame(parent, controller=self.deck_controller, deck_name=deck_name)
        frame.Show()


    def run_collection_frame(self, parent=None):
        """ carica l'interfaccia pe rla collezzione completa di carte. """

        frame = CardCollectionFrame(parent, controller=self.collection_controller)
        frame.Show()


    def run(self):
        """ avvia l'applicazione. """

        app = wx.App(False)

        self.set_collection_controller(CollectionController(parent=self, db_manager=self.db_manager))
        self.set_decks_controller(DecksController(parent=self, db_manager=self.db_manager))
        self.set_deck_controller(DeckController(parent=self, db_manager=self.db_manager))

        frame = HearthstoneAppFrame(None, title="Hearthstone Deck Manager, by Nemex81")
        frame.set_controller(self)
        frame.Show()

        app.MainLoop()



#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
