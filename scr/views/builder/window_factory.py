"""
    window_factory.py

    Modulo per la creazione dinamica di finestre e widget.

    path:
        scr/views/builder/window_factory.py

"""

# lib
import wx
from scr.views.builder.dependency_container import DependencyContainer
from utyls import logger as log



class WindowFactory:
    """
    Factory per la creazione dinamica di finestre e widget.
    Utilizza il DependencyContainer per risolvere le dipendenze necessarie.
    """

    def __init__(self, container: DependencyContainer):
        """
        Inizializza la WindowFactory con un DependencyContainer.

        :param container: Istanza di DependencyContainer per risolvere le dipendenze.
        """
        self.container = container

    def create_window(self, window_class, parent=None, **kwargs):
        """
        Crea una finestra utilizzando la classe specificata.

        :param window_class: Classe della finestra da creare.
        :param parent: Finestra genitore (opzionale).
        :param kwargs: Parametri aggiuntivi per la creazione della finestra.
        :return: Istanza della finestra creata.
        """
        if not hasattr(window_class, "__bases__") or wx.Frame not in window_class.__bases__:
            raise ValueError(f"La classe {window_class.__name__} non è una finestra valida (deve ereditare da wx.Frame).")

        # Risolve le dipendenze necessarie (es. ColorManager, FocusHandler)
        color_manager = self.container.resolve("color_manager")
        focus_handler = self.container.resolve("focus_handler")

        # Crea la finestra
        return window_class(parent, color_manager=color_manager, focus_handler=focus_handler, **kwargs)

    def create_widget(self, widget_class, parent=None, **kwargs):
        """
        Crea un widget utilizzando la classe specificata.

        :param widget_class: Classe del widget da creare.
        :param parent: Widget genitore (opzionale).
        :param kwargs: Parametri aggiuntivi per la creazione del widget.
        :return: Istanza del widget creato.
        """
        if not hasattr(widget_class, "__bases__") or wx.Window not in widget_class.__bases__:
            raise ValueError(f"La classe {widget_class.__name__} non è un widget valido (deve ereditare da wx.Window).")

        # Risolve le dipendenze necessarie (es. ColorManager, FocusHandler)
        color_manager = self.container.resolve("color_manager")
        focus_handler = self.container.resolve("focus_handler")

        # Crea il widget
        return widget_class(parent, color_manager=color_manager, focus_handler=focus_handler, **kwargs)




#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
