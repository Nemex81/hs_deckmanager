"""
    Modulo per la composizione iniziale dell'applicazione
     
    path:
        scr/hdm.py

    Descrizione:
                Questo modulo si occupa di assemblare i componenti dell'applicazione, inizializzando il DbManager e i controller.
                La classe AppBuilder è responsabile della costruzione e inizializzazione dell'applicazione.
                L'applicazione viene costruita a partire dai controller, che a loro volta si interfacciano con il modello (DbManager).
                L'applicazione può essere avviata tramite il metodo run_app().

"""

# lib
from scr.models import DbManager
from scr.controller import MainController, CollectionController, DecksController, DeckController
from utyls import logger as log
#import pdb



class AppBuilder:
    """Classe responsabile della costruzione e inizializzazione dell'applicazione."""

    def __init__(self):
        """Inizializza l'AppBuilder e tutti i controller."""

        # Inizializza il DbManager (modello)
        self.db_manager = DbManager()

        # Inizializza i controller
        self.collection_controller = CollectionController(db_manager=self.db_manager)
        self.decks_controller = DecksController(db_manager=self.db_manager)
        self.deck_controller = DeckController(db_manager=self.db_manager)

        # Inizializza il MainController, passandogli gli altri controller
        self.main_controller = MainController(
            db_manager=self.db_manager,
            collection_controller=self.collection_controller,
            decks_controller=self.decks_controller,
            deck_controller=self.deck_controller
        )

    def build_app(self):
        """Restituisce l'applicazione inizializzata."""
        return self.main_controller

    def run_app(self):
        """Avvia l'applicazione."""
        if self.main_controller:
            self.main_controller.run()
        else:
            raise ValueError("L'applicazione non è stata costruita correttamente.")




#@@@# Start del modulo
if __name__ != "__main__":
    log.info(f"Carico: {__name__}")
