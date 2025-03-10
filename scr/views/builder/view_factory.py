"""
    window_factory.py

    Modulo per la creazione dinamica di finestre e widget.

    path:
        scr/views/builder/view_factory.py

"""

# lib
import wx
import scr.views.builder.view_components as vc
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

    def __init__(self, color_manager, focus_handler, **kwargs):
        """
        Inizializza la factory con un container di dipendenze.
        Se non viene fornito un container, ne crea uno nuovo.
        """
        self.container = kwargs.get("container", None)

        log.info("Inizializzazione WidgetFactory.")

        # cerca il container di dipendenze nel kwargs
        if not self.container and "container" in kwargs:
            self.container = kwargs["container"]

        self.color_manager = color_manager
        if not self.color_manager:
            log.error("ColorManager non fornito al WidgetFactory.")
            raise ValueError("ColorManager non fornito al WidgetFactory.")
        else:
            log.info("ColorManager risolto correttamente in ViewFactory.")

        self.focus_handler = focus_handler
        if not self.focus_handler:
            log.error("FocusHandler non fornito al WidgetFactory.")
            raise ValueError("FocusHandler non fornito al WidgetFactory.")
            
        else:
            log.info("FocusHandler risolto correttamente in ViewFactory.")


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

        color_manager = self.color_manager
        focus_handler = self.focus_handler
        list_ctrl = vc.CustomListCtrl(
            parent,
            color_manager=color_manager,
            focus_handler=focus_handler,
            style=style
        )

        # Aggiungi le colonne alla lista
        for idx, (col_name, width) in enumerate(columns):
            list_ctrl.InsertColumn(idx, col_name, width=width)

        # Applica lo stile predefinito e collega gli eventi di focus
        self.color_manager.apply_default_style(list_ctrl)

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


    def create_sizer(self, orientation=wx.VERTICAL):
        """
        Crea un sizer per organizzare gli elementi dell'interfaccia utente.

        :param orientation: Orientamento del sizer (wx.VERTICAL o wx.HORIZONTAL). Default: wx.VERTICAL.
        :return: Un'istanza di wx.BoxSizer.
        """
        return wx.BoxSizer(orientation)

    def add_to_sizer(self, sizer, element, proportion=0, flag=wx.ALL, border=10):
        """
        Aggiunge un elemento a un sizer con parametri predefiniti.

        :param sizer: Il sizer a cui aggiungere l'elemento.
        :param element: L'elemento da aggiungere (es. un pulsante o una lista).
        :param proportion: Proporzione dell'elemento nel sizer. Default: 0.
        :param flag: Flag di allineamento. Default: wx.ALL.
        :param border: Spazio intorno all'elemento. Default: 10.
        """
        sizer.Add(element, proportion=proportion, flag=flag, border=border)

    def create_common_controls(self):
        """
        Crea controlli comuni per la ricerca di carte.

        :return: Un dizionario con i controlli creati.
        """
        common_controls = [
            ("nome", "Nome", wx.TextCtrl),
            ("costo_mana", "Costo Mana", wx.SpinCtrl, {"min": 0, "max": 20}),
            ("tipo", "Tipo", wx.ComboBox, {"choices": [t.value for t in eg.EnuCardType], "style": wx.CB_READONLY}),
            ("tipo_magia", "Tipo Magia", wx.ComboBox, {"choices": [st.value for st in eg.EnuSpellType], "style": wx.CB_READONLY}),
            ("sottotipo", "Sottotipo", wx.ComboBox, {"choices": [], "style": wx.CB_READONLY}),
            ("attacco", "Attacco", wx.SpinCtrl, {"min": 0, "max": 20}),
            ("vita", "Vita", wx.SpinCtrl, {"min": 0, "max": 20}),
            ("durability", "Durabilità", wx.SpinCtrl, {"min": 0, "max": 20}),
            ("rarita", "Rarità", wx.ComboBox, {"choices": [r.value for r in eg.EnuRarity], "style": wx.CB_READONLY}),
            ("espansione", "Espansione", wx.ComboBox, {"choices": [e.value for e in eg.EnuExpansion], "style": wx.CB_READONLY})
        ]
        return common_controls

    def create_checklistbox(self, parent, choices, event_handler=None):
        """
        Crea un controllo CheckListBox per la selezione multipla.

        :param parent: Il genitore del controllo.
        :param choices: Lista di scelte da mostrare nel CheckListBox.
        :param event_handler: Funzione da chiamare quando un elemento viene selezionato (opzionale).
        :return: Un'istanza di wx.CheckListBox.
        """
        checklistbox = wx.CheckListBox(parent, choices=choices)
        if event_handler:
            checklistbox.Bind(wx.EVT_CHECKLISTBOX, event_handler)
        return checklistbox

    def create_check_list_box(self, parent, choices, label=""):
        """
        Crea una casella di selezione multipla (wx.CheckListBox).

        :param parent: Il genitore del controllo.
        :param choices: Lista di opzioni da visualizzare.
        :param label: Etichetta da visualizzare sopra la casella di selezione (opzionale).
        :return: Un'istanza di wx.CheckListBox.
        """
        label_ctrl = wx.StaticText(parent, label=label)
        check_list_box = wx.CheckListBox(parent, choices=choices)
        return label_ctrl, check_list_box

    def create_separator(self, parent, style=wx.LI_HORIZONTAL, thickness=1, color=None):
        """
        Crea un separatore orizzontale o verticale per gli elementi dell'interfaccia utente.

        :param parent: Il genitore del separatore.
        :param style: Stile della linea (wx.LI_HORIZONTAL o wx.LI_VERTICAL). Default: wx.LI_HORIZONTAL.
        :param thickness: Spessore della linea. Default: 1.
        :param color: Colore della linea (opzionale). Esempio: wx.Colour(200, 200, 200).
        :return: Un'istanza di wx.StaticLine.
        """
        separator = wx.StaticLine(parent, style=style)
        if color:
            separator.SetBackgroundColour(color)
        separator.SetMinSize((-1, thickness))
        return separator





class ViewFactory:
    """Factory per la creazione delle view, supporta entrambi gli approcci."""

    def __init__(self, container=None, **kwargs):
        self.container = container
        if not self.container:
            raise ValueError("DependencyContainer non fornito alla ViewFactory.")

        self.kwargs = kwargs

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


    def question_box(self, parent, message, title="Conferma", style=wx.YES_NO | wx.ICON_QUESTION):
        """
        Crea una finestra di dialogo per messaggi di conferma.

        :param parent: Il genitore della finestra di dialogo.
        :param message: Il messaggio da visualizzare.
        :param title: Il titolo della finestra. Default: "Conferma".
        :param style: Lo stile della finestra. Default: wx.YES_NO | wx.ICON_QUESTION.
        :return: Un'istanza di wx.MessageDialog.
        """
        return wx.MessageDialog(parent, message, title, style)


#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
