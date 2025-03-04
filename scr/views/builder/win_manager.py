"""
    Modulo per la gestione delle finestre dell'applicazione.

    path:
        scr/views/builder/win_manager.py

"""

# lib
from .dependency_container import DependencyContainer
from .window_factory import WindowFactory
from utyls import logger as log



from .dependency_container import DependencyContainer
from .window_factory import WindowFactory

class WinManager:
    """
    Gestore centralizzato per la creazione e gestione delle finestre.
    Utilizza WindowFactory per la creazione dinamica di finestre e widget.
    """

    def __init__(self):
        self.container = DependencyContainer()  # Inizializza il container delle dipendenze
        self.factory = WindowFactory(self.container)  # Inizializza la WindowFactory
        self._register_default_dependencies()   # Registra le dipendenze di default

    def _register_default_dependencies(self):
        """
        Registra le dipendenze di default nel container.
        """
        from .color_system import ColorManager
        from .focus_handler import FocusHandler

        # Registra ColorManager
        self.container.register("color_manager", lambda: ColorManager(theme="DARK"))

        # Registra FocusHandler
        self.container.register("focus_handler", lambda: FocusHandler())

    def create_window(self, window_class, parent=None, **kwargs):
        """
        Crea una finestra utilizzando la WindowFactory.

        :param window_class: Classe della finestra da creare.
        :param parent: Finestra genitore (opzionale).
        :param kwargs: Parametri aggiuntivi per la creazione della finestra.
        :return: Istanza della finestra creata.
        """
        return self.factory.create_window(window_class, parent, **kwargs)

    def create_widget(self, widget_class, parent=None, **kwargs):
        """
        Crea un widget utilizzando la WindowFactory.

        :param widget_class: Classe del widget da creare.
        :param parent: Widget genitore (opzionale).
        :param kwargs: Parametri aggiuntivi per la creazione del widget.
        :return: Istanza del widget creato.
        """
        return self.factory.create_widget(widget_class, parent, **kwargs)



#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
