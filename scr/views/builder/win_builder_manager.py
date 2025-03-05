"""
    Modulo per la gestione delle finestre dell'applicazione.

    path:
        scr/views/builder/win_builder_manager.py

"""

# lib
from .dependency_container import DependencyContainer
from .color_system import ColorManager
from .focus_handler import FocusHandler
from .view_factory import NewViewFactory
from utyls import enu_glob as eg
from utyls import logger as log



class WinBuildManager:
    """
    Gestore centralizzato per la creazione e gestione delle finestre.
    Utilizza WindowFactory per la creazione dinamica di finestre e widget.
    """

    def __init__(self):
        self.container = DependencyContainer()                  # Inizializza il container delle dipendenze
        self.factory = NewViewFactory(self.container)            # Inizializza la WindowFactory
        self._register_default_dependencies()                   # Registra le dipendenze di default
        self.windows = {}                                       # Dizionario per memorizzare le finestre attive
        self.current_window = None                              # Finestra corrente

    def _register_default_dependencies(self):
        """
        Registra le dipendenze di default nel container.
        """

        # Registra ColorManager
        self.container.register("color_manager", lambda: ColorManager(theme="DARK"))

        # Registra FocusHandler
        self.container.register("focus_handler", lambda: FocusHandler())


    def create_window(self, window_class, parent=None, **kwargs):
        """
        Crea una finestra utilizzando la WindowFactory e la memorizza.

        :param window_class: Classe della finestra da creare.
        :param parent: Finestra genitore (opzionale).
        :param kwargs: Parametri aggiuntivi per la creazione della finestra.
        :return: Istanza della finestra creata.
        """
        window = self.factory.create_window(window_class, parent, **kwargs)
        self.windows[window_class.__name__] = window  # Memorizza la finestra
        return window


    def open_window(self, window_class, parent=None, **kwargs):
        """
        Apre una finestra e nasconde la corrente.

        :param window_class: Classe della finestra da aprire.
        :param parent: Finestra genitore (opzionale).
        :param kwargs: Parametri aggiuntivi per la creazione della finestra.
        """
        if self.current_window:
            self.current_window.Hide()  # Nasconde la finestra corrente

        # Crea o ripristina la finestra
        if window_class.__name__ in self.windows:
            window = self.windows[window_class.__name__]
        else:
            window = self.create_window(window_class, parent, **kwargs)

        window.Show()  # Mostra la finestra
        self.current_window = window  # Imposta la finestra corrente


    def close_current_window(self):
        """
        Chiude la finestra corrente e ripristina il genitore.
        """
        if self.current_window:
            parent = self.current_window.GetParent()
            self.current_window.Hide()  # Nasconde la finestra corrente
            if parent:
                parent.Show()  # Mostra la finestra genitore
                self.current_window = parent  # Imposta il genitore come finestra corrente
            else:
                self.current_window = None  # Nessuna finestra corrente


    def get_window(self, window_class):
        """
        Restituisce una finestra esistente o None se non trovata.

        :param window_class: Classe della finestra da cercare.
        :return: Istanza della finestra o None.
        """
        return self.windows.get(window_class.__name__)



#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
