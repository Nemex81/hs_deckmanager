"""
    window_factory.py

    Modulo per la creazione dinamica di finestre e widget.

    path:
        scr/views/builder/view_factory.py

"""

# lib
import wx
from .color_system import ColorManager
from .focus_handler import FocusHandler
from scr.views.builder.dependency_container import DependencyContainer
from scr.views.main_views import  HearthstoneAppFrame
from scr.views.collection_view import CardCollectionFrame
from scr.views.decks_view import DecksViewFrame
from scr.views.deck_view import DeckViewFrame
from utyls import enu_glob as eg
from utyls import logger as log

__all_win__ = {
    eg.WindowKey.MAIN: HearthstoneAppFrame,
    eg.WindowKey.COLLECTION: CardCollectionFrame,
    eg.WindowKey.DECKS: DecksViewFrame,
    eg.WindowKey.DECK: DeckViewFrame,
}



class WidgetFactory:
    """
    Factory per la creazione centralizzata di widget.
    Utilizza il DependencyContainer per risolvere le dipendenze necessarie.
    """

    def __init__(self, container: DependencyContainer=None):
        """
        Inizializza la factory con un container di dipendenze.
        Se non viene fornito un container, ne crea uno nuovo.
        """

        self.container = container
        self.color_manager = self.container.resolve("color_manager")
        self.focus_handler = self.container.resolve("focus_handler")


    def create_button(self, parent, label, size=(180, 70), font_size=16, event_handler=None):
        """
        Crea un pulsante personalizzato con gestione del focus e temi.

        :param parent: Il genitore del pulsante (es. un pannello).
        :param label: Testo del pulsante.
        :param size: Dimensioni del pulsante (larghezza, altezza). Default: (180, 70).
        :param font_size: Dimensione del font. Default: 16.
        :param event_handler: Funzione da chiamare quando il pulsante viene cliccato (opzionale).
        :return: Un'istanza di wx.Button.
        """

        button = wx.Button(parent, label=label, size=size)
        button.SetFont(wx.Font(font_size, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        if event_handler:
            button.Bind(wx.EVT_BUTTON, event_handler)

        # Applica lo stile predefinito e collega gli eventi di focus
        self.color_manager.apply_default_style(button)
        self.focus_handler.bind_focus_events(button)

        log.debug(f"Creato pulsante: {label}")
        return button


    def create_list_ctrl(self, parent, columns, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN):
        """
        Crea una lista (wx.ListCtrl) con colonne personalizzabili.

        :param parent: Il genitore della lista.
        :param columns: Lista di tuple (nome_colonna, larghezza).
        :param style: Stile della lista. Default: wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN.
        :return: Un'istanza di wx.ListCtrl.
        """

        list_ctrl = wx.ListCtrl(parent, style=style)

        # Aggiungi le colonne alla lista
        for idx, (col_name, width) in enumerate(columns):
            list_ctrl.InsertColumn(idx, col_name, width=width)

        # Applica lo stile predefinito e collega gli eventi di focus
        self.color_manager.apply_default_style(list_ctrl)
        self.focus_handler.bind_focus_events(list_ctrl)

        log.debug(f"Creata ListCtrl con colonne: {columns}")
        return list_ctrl


    def create_search_bar(self, parent, placeholder="Cerca...", event_handler=None):
        """
        Crea una barra di ricerca (wx.SearchCtrl).

        :param parent: Il genitore della barra di ricerca.
        :param placeholder: Testo placeholder. Default: "Cerca...".
        :param event_handler: Funzione da chiamare quando si avvia la ricerca (opzionale).
        :return: Un'istanza di wx.SearchCtrl.
        """

        search_ctrl = wx.SearchCtrl(parent)
        search_ctrl.SetDescriptiveText(placeholder)
        if event_handler:
            search_ctrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, event_handler)

        # Applica lo stile predefinito e collega gli eventi di focus
        self.color_manager.apply_default_style(search_ctrl)
        self.focus_handler.bind_focus_events(search_ctrl)

        log.debug(f"Creata barra di ricerca con placeholder: {placeholder}")
        return search_ctrl



class NewViewFactory:
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

    def create_window(self, key, parent=None, controller=None, **kwargs):
        """
        Crea una finestra utilizzando la classe specificata.

        :param window_class: Classe della finestra da creare.
        :param parent: Finestra genitore (opzionale).
        :param kwargs: Parametri aggiuntivi per la creazione della finestra.
        :return: Istanza della finestra creata.
        """
        window_class = __all_win__.get(key)
        if not window_class:
            raise ValueError(f"Chiave finestra non valida: {key}")
        
        # Risolvi le dipendenze dal container
        color_manager = self.container.resolve("color_manager")
        focus_handler = self.container.resolve("focus_handler")

        # Crea la finestra
        return window_class(
            parent=parent,
            controller=controller,
            container=self.container,
            #**kwargs
        )

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




class OldViewFactory:
    """Factory per la creazione delle view, supporta entrambi gli approcci."""

    def __init__(self, container=None, **kwargs):
        self.use_new_framework = False
        self.container = container

    def create_window(self, key, parent=None, controller=None, **kwargs):
        window_class = __all_win__.get(key)
        if not window_class:
            raise ValueError(f"Chiave finestra non valida: {key}")

        # Crea la finestra
        return window_class(
            parent=parent,
            controller=controller,
            container=self.container,
            **kwargs
        )



#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
