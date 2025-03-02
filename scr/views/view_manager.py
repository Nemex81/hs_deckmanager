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



class ViewFactory:
    @staticmethod
    def create_view(view_type, parent, controller, **kwargs):
        """
        Crea una view in base al tipo specificato.
        """
        win_controller = controller.win_controller  # Utilizza il WinController del controller principale
        win_controller.create_window(view_type, parent, controller, **kwargs)
        return win_controller.windows[view_type]



class WinController:
    """ Controller per la gestione delle finestre. """

    def __init__(self):
        self.windows = {}  # Dizionario per memorizzare le finestre
        self.current_window = None  # Finestra corrente

    def create_window(self, window_key, parent=None, controller=None, **kwargs):
        """
        Crea una finestra senza renderla visibile.
        
        Args:
            window_key (WindowKey): Chiave della finestra da creare.
            parent: Finestra genitore.
            controller: Controller associato alla finestra.
            **kwargs: Parametri aggiuntivi specifici per la finestra.
        """
        if window_key in self.windows:
            raise ValueError(f"Finestra '{window_key}' già creata.")
        
        if window_key == eg. WindowKey.MAIN:
            self.windows[window_key] = HearthstoneAppFrame(parent, controller)
        elif window_key == eg.WindowKey.COLLECTION:
            self.windows[window_key] = CardCollectionFrame(parent, controller)
        elif window_key == eg.WindowKey.DECKS:
            self.windows[window_key] = DecksViewFrame(parent, controller)
        elif window_key == eg.WindowKey.DECK:
            deck_name = kwargs.get('deck_name')
            self.windows[window_key] = DeckViewFrame(parent, controller, deck_name)
        else:
            raise ValueError(f"Tipo di finestra non supportato: {window_key}")

    def open_window(self, window_key, parent=None):
        """
        Rende visibile una finestra e nasconde la corrente.
        
        Args:
            window_key (WindowKey): Chiave della finestra da aprire.
            parent: Finestra genitore.
        """
        if window_key not in self.windows:
            raise ValueError(f"Finestra '{window_key}' non creata.")
        
        if self.current_window:
            self.current_window.Hide()
        
        self.current_window = self.windows[window_key]
        self.current_window.Show()
        if parent:
            self.current_window.SetParent(parent)

    def close_current_window(self):
        """Chiude la finestra corrente e ripristina la genitore."""
        if self.current_window:
            parent = self.current_window.GetParent()
            self.current_window.Hide()
            if parent:
                self.current_window = parent
                parent.Show()
            else:
                self.current_window = None



#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
