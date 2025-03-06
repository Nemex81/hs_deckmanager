"""
Modulo per la gestione delle finestre dell'applicazione.

Path:
        scr/views/view_manager.py

"""

# lib
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
        self.factory = self._select_factory()           # Seleziona la factory in base al flag
        self.windows = {}                               # Dizionario per memorizzare le finestre
        self.current_window = None                      # Finestra corrente


    def _select_factory(self):
        """ 
        Seleziona la factory da utilizzare (impostare quì la logica pe rselezionare factory alternative).
        """
        return ViewFactory(container=self.container) 


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

        # Risolvi il controller dal container se non è stato passato
        if not controller and self.container.has(f"{key.value.lower()}_controller"):
            controller = self.container.resolve(f"{key.value.lower()}_controller")

        # Crea la finestra utilizzando la factory
        view = self.factory.create_window(
            key=key,
            parent=parent,
            controller=controller,
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
        if not deck_name:
            log.error("'deck_name' è obbligatorio per DeckViewFrame")
            raise ValueError("'deck_name' è obbligatorio per DeckViewFrame")

        log.debug(f"chiamata alla factory per la creazione della finestra con chiave: {eg.WindowKey.DECK}")
        resolved_controller = controller or self.container.resolve("deck_controller")
        self.create_window(
            parent=parent,
            #controller=controller,
            controller=resolved_controller,
            key=eg.WindowKey.DECK,
            deck_name=deck_name
        )


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
