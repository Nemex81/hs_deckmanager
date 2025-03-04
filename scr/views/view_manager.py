"""
Modulo per la gestione delle finestre dell'applicazione.

Path:
        scr/views/view_manager.py

"""

#lib
from enum import Enum
from .main_views import HearthstoneAppFrame
from .collection_view import CardCollectionFrame
from .decks_view import DecksViewFrame
from .deck_view import DeckViewFrame
from utyls import enu_glob as eg
from utyls import logger as log
#import pdb




__all__win__ = {
    eg.WindowKey.MAIN: HearthstoneAppFrame,
    eg.WindowKey.COLLECTION: CardCollectionFrame,
    eg.WindowKey.DECKS: DecksViewFrame,
    eg.WindowKey.DECK: DeckViewFrame,
}


class ViewFactory:
    """ Factory per la creazione delle view. """

    @staticmethod
    def create_view(key=None, parent=None, controller=None, **kwargs):
        """
        Crea una finestra senza renderla visibile.
        
        Args:
            window_key (WindowKey): Chiave della finestra da creare.
            parent: Finestra genitore.
            controller: Controller associato alla finestra.
            **kwargs: Parametri aggiuntivi specifici per la finestra.
        """

        if key == eg.WindowKey.DECK:
            deck_name = kwargs.get("deck")
            log.debug(f"Chiave finestra: {key}, Nome mazzo: {deck_name}")
            return __all__win__[key](parent, controller, deck_name)

        log.debug(f"Chiave finestra principale: {key}")
        log.debug(f"Controller da passare: {controller}")
        if key in __all__win__:
            return __all__win__[key](parent=parent, controller=controller)
        else:
            log.error(f"Tipo di finestra non supportato: {key}")
            raise ValueError(f"Tipo di finestra non supportato: {key}")





class WinController:
    """ Controller per la gestione delle finestre. """

    def __init__(self):
        self.windows = {}  # Dizionario per memorizzare le finestre
        self.current_window = None  # Finestra corrente


    def create_window(self, parent=None, controller=None, key=None, **kwargs):
        """
        Crea una finestra senza renderla visibile utilizzando la factory.
        
        Args:
            key (WindowKey): Chiave della finestra da creare.
            parent: Finestra genitore.
            controller: Controller associato alla finestra.
            **kwargs: Parametri aggiuntivi specifici per la finestra.
        """

        log.debug(f"Creazione finestra: {key}")

        view = ViewFactory.create_view(
            parent=parent,
            controller=controller,
            key=key,
            **kwargs
        )

        if view:
            self.windows[key] = view
            log.debug(f"Finestra creata: {self.windows[key]}")
        else:
                log.error(f"Finestra '{key}' non creata.")
                raise ValueError(f"Finestra '{key}' non creata.")

    def create_main_window(self, parent=None, controller=None):
        """Crea la finestra principale."""
        log.debug(f"Tentativo di creazione finestra con chiave: {eg.WindowKey.MAIN}")
        self.create_window(parent=parent, controller=controller, key=eg.WindowKey.MAIN)

    def create_collection_window(self, parent=None, controller=None):
            """Crea la finestra della collezione."""
            log.debug(f"Tentativo di creazione finestra con chiave: {eg.WindowKey.COLLECTION}")
            self.create_window(parent=parent, controller=controller, key=eg.WindowKey.COLLECTION)


    def create_decks_window(self, parent=None, controller=None):
        """Crea la finestra dei mazzi."""
        log.debug(f"Tentativo di creazione finestra con chiave: {eg.WindowKey.DECKS}")
        self.create_window(parent=parent, controller=controller, key=eg.WindowKey.DECKS)


    def create_deck_window(self, parent=None, controller=None, deck_name=None):
        """Crea la finestra di un mazzo."""

        log.debug(f"Tentativo di creazione finestra con chiave: {eg.WindowKey.DECK}")
        self.create_window(parent=parent, controller=controller, key=eg.WindowKey.DECK, deck_name=deck_name)


    def open_window(self, window_key, parent=None):
        """
        Rende visibile una finestra e nasconde la corrente.
        
        Args:
            window_key (WindowKey): Chiave della finestra da aprire.
            parent: Finestra genitore.
        """
        if window_key not in self.windows:
            log.error(f"Finestra '{window_key}' non creata.")
            raise ValueError(f"Finestra '{window_key}' non creata.")
        
        if self.current_window:
            self.current_window.Hide()
            log.debug(f"Finestra corrente nascosta: {self.current_window}")
        
        self.current_window = self.windows[window_key]
        self.current_window.Show()
        log.debug(f"Finestra corrente impostata: {self.current_window}")
        if parent:
            self.current_window.parent = parent
            log.debug(f"Finestra genitore impostata: {parent}")

    def close_current_window(self):
        """Chiude la finestra corrente e ripristina il genitore."""

        if self.current_window:
            parent = self.current_window.GetParent()
            self.current_window.Hide()
            if parent:
                log.debug(f"Ripristino finestra genitore: {parent}")
                self.current_window = parent
                parent.Show()
            else:
                log.debug("Nessuna finestra genitore trovata.")
                self.current_window = None



#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
