"""
    Modulo per l'inizializzazione dell'applicazione con il nuovo framework.

    path:
        ./app_initializer.py
"""

# Lib
from scr.views.builder.dependency_container import DependencyContainer
from scr.views.builder.color_system import ColorManager
from scr.views.builder.focus_handler import FocusHandler
from scr.views.builder.view_factory import WidgetFactory

from scr.views.collection_view import CardCollectionFrame
from scr.views.decks_view import DecksViewFrame
from scr.views.deck_view import DeckViewFrame

from scr.views.view_manager import WinController
from scr.controller import MainController
from scr.models import DbManager
from scr.views.main_views import HearthstoneAppFrame
from scr.views.builder.color_system import ColorTheme
from utyls.screen_reader import ScreenReader
from utyls import enu_glob as eg
from utyls import logger as log



class AppInitializer:
    """
    Classe responsabile dell'inizializzazione dell'applicazione con il nuovo framework.
    """

    def __init__(self):
        self.container = DependencyContainer()
        self.win_controller = None
        self.initialize_app()
        self.start_app()


    def initialize_app(self):
        """Inizializza l'applicazione con il nuovo framework."""

        log.info("Inizializzazione dell'applicazione avviata...")

        # Registra le dipendenze
        self._register_dependencies()
        self._initialize_controllers()
        log.info("Inizializzazione completata.")


    def _register_dependencies(self):
        """
        Registra le dipendenze nel container.
        """

        log.info("Registrazione delle dipendenze nel container.")

        # Registra ColorManager e FocusHandler
        self.container.register("color_manager", lambda: ColorManager(theme=ColorTheme.DARK))
        self.container.register("focus_handler", lambda: FocusHandler())

        # verifica che ColorManager sia registrato
        if not self.container.has("color_manager"):
            log.error("ColorManager non registrato correttamente.")

        # Verifica che FocusHandler sia registrato
        if not self.container.has("focus_handler"):
            log.error("FocusHandler non registrato correttamente.")

        # Registra WidgetFactory
        self.container.register("widget_factory", lambda: WidgetFactory(
            color_manager=self.container.resolve("color_manager"),
            focus_handler=self.container.resolve("focus_handler"),
        ))

        # Verifica che WidgetFactory sia registrata
        if not self.container.has("widget_factory"):
            log.error("WidgetFactory non registrata correttamente.")
        else:
            log.info("WidgetFactory registrata correttamente.")

        # Gestione del database
        db_manager = DbManager()
        self.container.register("db_manager", lambda: db_manager)
        if not self.container.has("db_manager"):
            log.error("DbManager non registrato correttamente.")

        # Registra ScreenReader
        self.container.register("vocalizer", lambda: ScreenReader())
        if not self.container.has("vocalizer"):
            log.error("ScreenReader non registrato correttamente.")

        # Registra i controller

        # Registra mainController
        self.container.register("main_controller", lambda: MainController(container=self.container))

        #Registra WinController
        self.container.register("win_controller", lambda: WinController(container=self.container))

        # Registra il dizionario delle finestre
        self.container.register("all_win", lambda: {
            eg.WindowKey.MAIN: HearthstoneAppFrame,
            eg.WindowKey.COLLECTION: CardCollectionFrame,
            eg.WindowKey.DECKS: DecksViewFrame,
            eg.WindowKey.DECK: DeckViewFrame,
        })

        log.info("Registrazione delle dipendenze completata.")


    def _initialize_controllers(self):
        """Inizializza i controller tramite DependencyContainer."""

        log.info("Inizializzazione dei controller tramite DependencyContainer.")
        self.main_controller = self.container.resolve("main_controller")
        self.win_controller = self.container.resolve("win_controller")
        log.info("Inizializzazione dei controller completata.")


    def start_app(self):
        """Avvia l'applicazione."""
        log.info("Avvio dell'applicazione.")
        self.main_controller = self.container.resolve("main_controller")
        self.main_controller.start_app()



if __name__ == "__main__":
    log.debug(f"Carico: {__name__}")
