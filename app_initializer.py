"""


    path:
        ./app_initializer.py
"""

# Lib
from scr.views.builder.dependency_container import DependencyContainer
from scr.views.builder.color_system import ColorManager
from scr.views.builder.focus_handler import FocusHandler
from scr.views.builder.win_builder_manager import WinBuildManager
from scr.views.view_manager import WinController
from scr.controller import MainController, CollectionController, DecksController, DeckController
from scr.models import DbManager
from scr.views.main_views import HearthstoneAppFrame
from scr.views.collection_view import CardCollectionFrame
from scr.views.decks_view import DecksViewFrame
from scr.views.deck_view import DeckViewFrame
from scr.views.builder.color_system import ColorTheme
from utyls import enu_glob as eg
from utyls import logger as log

__all_win__ = {
    eg.WindowKey.MAIN: HearthstoneAppFrame,
    eg.WindowKey.COLLECTION: CardCollectionFrame,
    eg.WindowKey.DECKS: DecksViewFrame,
    eg.WindowKey.DECK: DeckViewFrame,
}


class AppInitializer:
    """
    Classe responsabile dell'inizializzazione dell'applicazione con il nuovo framework.
    """

    def __init__(self):
        self.container = DependencyContainer()
        self.win_controller = None
        self.main_controller = None


    def initialize_app(self):
        """Inizializza l'applicazione con il nuovo framework."""

        log.debug("Inizializzazione dell'applicazione.")

        self._register_dependencies()                                                           # Registra le dipendenze
        self.win_controller = WinController(container=self.container)                           # Inizializza il WinController
        self._initialize_controllers()

        log.debug("Inizializzazione completata.")

    def _register_dependencies(self):
        """
        Registra le dipendenze nel container.
        """

        log.debug("Registrazione delle dipendenze nel container.")

        # Gestione colori e focus
        self.container.register("color_manager", lambda: ColorManager(theme=ColorTheme.DARK))
        self.container.register("focus_handler", lambda: FocusHandler())

        # Gestione del database
        db_manager = DbManager()
        self.container.register("db_manager", lambda: db_manager)

        # Controller
        self.container.register("WinController", lambda: WinController(container=self.container))
        self.container.register("collection_controller", lambda: CollectionController(db_manager=db_manager))
        self.container.register("decks_controller", lambda: DecksController(db_manager=db_manager))
        self.container.register("deck_controller", lambda: DeckController(db_manager=db_manager))

        self.container.register("main_controller", lambda: MainController(
            db_manager=db_manager,
            collection_controller=self.container.resolve("collection_controller"),
            decks_controller=self.container.resolve("decks_controller"),
            deck_controller=self.container.resolve("deck_controller")
        ))

        # gestione dizionario con le path delle classi per le finestre
        self.container.register("all_win", lambda: __all_win__)

        log.debug("Registrazione delle dipendenze completata.")

    def _initialize_controllers(self):
        log.debug("Inizializzazione dei controller tramite DependencyContainer.")
        self.main_controller = self.container.resolve("main_controller")


    def start_app(self):
        """
        Avvia l'applicazione.
        """

        log.debug("Avvio dell'applicazione.")
        #  Avvia l'interfaccia grafica delapplicazione
        import wx
        app = wx.App(False)

        # Crea e mostra la finestra principale
        self.win_controller.create_main_window(parent=None, controller=self.main_controller)
        self.win_controller.open_window(window_key=eg.WindowKey.MAIN)

        # Avvia il ciclo principale dell'applicazione
        app.MainLoop()






if __name__ == "__main__":
    log.debug(f"Carico: {__name__}")
