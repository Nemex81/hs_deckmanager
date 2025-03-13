"""
Modulo per la gestione delle finestre dell'applicazione.

Path:
        scr/views/view_manager.py

"""

# lib
import wx
from enum import Enum

from scr.views.builder.dependency_container import DependencyContainer          # Nuovo container
from scr.views.builder.view_factory import ViewFactory        # Factory per la creazione delle view
from scr.views.builder.view_factory import WidgetFactory                        # Factory per la creazione dei widget

from utyls import enu_glob as eg
from utyls import logger as log



class WinController:
    """ Controller per la gestione delle finestre. """

    def __init__(self, container=None):
        self.container = container                      # Memorizza il container
        if not self.container:
            log.error("Container non fornito al WinController.")
            raise ValueError("Container non fornito al WinController.")

        # Inizializza le altre proprietà
        self.factory = self._select_factory()                               # Seleziona la factory in base al flag
        self.windows = {}                                                   # Dizionario per memorizzare le finestre
        self.current_window = None                                          # Finestra corrente
        self.parent_stack = []                                              # Stack per tenere traccia delle finestre genitore


    def _select_factory(self):
        """ 
        Seleziona la factory da utilizzare (impostare quì la logica pe rselezionare factory alternative).
        """
        return ViewFactory(container=self.container) 


    def get_current_window(self):
        """ Restituisce la finestra corrente. """
        return self.current_window

    def create_window(self, parent=None, key=None, **kwargs):
        """
        Crea una finestra senza renderla visibile.
        Args:
            key: Chiave della finestra da creare.
            parent: Finestra genitore.
            **kwargs: Parametri aggiuntivi specifici per la finestra.
        """
        log.info(f"Creazione finestra: {key}")
        view = self.factory.create_window(key=key, parent=parent, **kwargs)
        if view:
            view.Bind(wx.EVT_CLOSE, lambda e: self.close_current_window())
            self.windows[key] = view
            log.info(f"Finestra '{key}' creata con genitore: {parent}")
        else:
            log.error(f"Finestra '{key}' non creata.")
            raise ValueError(f"Finestra '{key}' non creata.")


    def create_main_window(self, parent=None, controller=None):
        """Crea la finestra principale."""
        log.info(f"Tentativo di creazione finestra con chiave: {eg.WindowKey.MAIN}")
        self.create_window(parent=parent, controller=controller, key=eg.WindowKey.MAIN)
        self.open_window(eg.WindowKey.MAIN, parent)


    def create_collection_window(self, parent=None, controller=None):
        """Crea la finestra della collezione."""
        log.info(f"Tentativo di creazione finestra con chiave: {eg.WindowKey.COLLECTION}")
        self.create_window(parent=parent, controller=controller, key=eg.WindowKey.COLLECTION)
        self.open_window(eg.WindowKey.COLLECTION, parent)


    def create_decks_window(self, parent=None, controller=None):
        """Crea la finestra dei mazzi."""
        log.info(f"Tentativo di creazione finestra con chiave: {eg.WindowKey.DECKS}")
        self.create_window(parent=parent, controller=controller, key=eg.WindowKey.DECKS)
        self.open_window(eg.WindowKey.DECKS, parent)


    def create_deck_window(self, parent=None, controller=None, deck_name=None):
        """Crea la finestra di un mazzo."""

        log.info(f"Tentativo di creazione finestra con chiave: {eg.WindowKey.DECK}")
        if not deck_name:
            log.error("'deck_name' è obbligatorio per DeckViewFrame")
            raise ValueError("'deck_name' è obbligatorio per DeckViewFrame")

        log.debug(f"chiamata alla factory per la creazione della finestra con chiave: {eg.WindowKey.DECK}")
        resolved_controller = controller or self.container.resolve("main_controller")
        self.create_window(
            parent=parent,
            #controller=controller,
            controller=resolved_controller,
            key=eg.WindowKey.DECK,
            deck_name=deck_name
        )

        self.open_window(eg.WindowKey.DECK, parent)


    def open_window(self, window_key, parent=None):
        """
        Mostra una finestra esistente.
        Args:
            window_key: Chiave della finestra da mostrare.
            parent: Finestra genitore.
        """
        if window_key not in self.windows:
            log.error(f"Finestra '{window_key}' non trovata.")
            raise ValueError(f"Finestra '{window_key}' non trovata.")

        if self.current_window:
            self.current_window.Hide()
            self.parent_stack.append(self.current_window)

        self.current_window = self.windows[window_key]
        self.current_window.Show()


    def close_current_window(self):
        """
        Chiude la finestra corrente.
        """
        if self.current_window:
            self.current_window.Hide()
            self.current_window = None


    def close_current_window(self):
        """
        Chiude la finestra corrente e ripristina il genitore.
        """
        if self.current_window:
            parent = self.current_window.GetParent()
            self.current_window.Hide()
            
            # Ripristina la finestra genitore, se presente
            if parent:
                log.info(f"Ripristino finestra genitore: {parent}")
                self.current_window = parent
                parent.Show()
            else:
                log.warning("Nessuna finestra genitore trovata.")
                self.current_window = None



#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
