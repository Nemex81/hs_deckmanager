"""
    Modulo per la gestione dei componenti delle finestre dell'applicazione

    path:
        ./scr/views/builder/view_components.py



"""

# Lib
import wx
from .focus_handler import FocusHandler
from .color_system import ColorManager
from utyls import enu_glob as eg
from utyls import helper as hp
from utyls import logger as log
#import pdb

cm = ColorManager()

#@@# sezioni costanti per la configurazione predefinita degli elementi dell'interfaccia utente

# Configurazione di default
DEFAULT_BUTTON_SIZE = (180, 70)
DEFAULT_FONT_SIZE = 16
DEFAULT_LIST_STYLE = wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN


#@@# sezione classi personalizzate per la gestione degli elementi dell'interfaccia utente

class CustomTextCtrl(wx.TextCtrl, wx.Accessible):
    """
    Casella di testo personalizzata con gestione del focus e temi.
    """

    def __init__(self, parent, color_manager, placeholder="", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        #wx.Accessible.__init__(self)  # Inizializza wx.Accessible
        self.cm = color_manager         # Gestione dei colori
        self.placeholder = placeholder  # Testo placeholder (opzionale)

        # Imposta lo stile predefinito
        self.cm.apply_default_style(self)
        self.SetHint(self.placeholder)  # Imposta il placeholder

        # Collega gli eventi di focus
        self.cm.bind_focus_events(self)


    def on_focus(self, event):
        """Gestisce l'evento di focus sulla casella di testo."""
        self.cm.apply_focus_style(self)
        event.Skip()

    def on_kill_focus(self, event):
        """Gestisce l'evento di perdita del focus dalla casella di testo."""
        self.cm.reset_focus_style(self)
        event.Skip()

    def bind_focus_events(self):
        """Collega gli eventi di focus alla casella di testo."""        
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)



    def GetName(self):
        """Restituisce il nome accessibile."""
        return "Casella di testo"

    def GetDescription(self):
        """Restituisce una descrizione accessibile."""
        return f"Casella di testo per: {self.placeholder}"

    def GetRole(self):
        """Restituisce il ruolo del widget."""
        return wx.ACC_ROLE_TEXT

    def GetState(self):
        """Restituisce lo stato corrente."""
        state = wx.ACC_STATE_FOCUSABLE
        if self.IsEnabled():
            state |= wx.ACC_STATE_ENABLED

        if self.HasFocus():
            state |= wx.ACC_STATE_FOCUSED

        return state

    def SetFocus(self):
        """Imposta il focus sulla casella di testo."""
        super().SetFocus()
        self.cm.apply_focus_style(self)

    def KillFocus(self):
        """Rimuove il focus dalla casella di testo."""
        super().KillFocus()
        self.cm.reset_focus_style(self)



class CustomCheckBox(wx.CheckBox, wx.Accessible):
    """
    Checkbox personalizzata con gestione del focus e temi.
    """

    def __init__(self, parent, color_manager, label="", *args, **kwargs):
        super().__init__(parent, label=label, *args, **kwargs)
        self.cm = color_manager  # Gestione dei colori

        # Imposta lo stile predefinito
        self.cm.apply_default_style(self)

        # Collega gli eventi di focus
        self.cm.bind_focus_events(self)

    def SetFocus(self):
        """Imposta il focus sulla checkbox."""
        super().SetFocus()
        self.cm.apply_focus_style(self)

    def KillFocus(self):
        """Rimuove il focus dalla checkbox."""
        super().KillFocus()
        self.cm.reset_focus_style(self)



class CustomComboBox(wx.ComboBox):
    """
    Combobox personalizzata con gestione del focus e temi.
    """

    def __init__(self, parent, color_manager, choices=None, *args, **kwargs):
        super().__init__(parent, choices=choices or [], *args, **kwargs)
        self.cm = color_manager  # Gestione dei colori
        #self.fh = focus_handler  # Gestione del focus

        # Imposta lo stile predefinito
        self.cm.apply_default_style(self)

        # Collega gli eventi di focus
        self.cm.bind_focus_events(self)

    def SetFocus(self):
        """Imposta il focus sulla combobox."""
        super().SetFocus()
        self.cm.apply_focus_style(self)

    def KillFocus(self):
        """Rimuove il focus dalla combobox."""
        super().KillFocus()
        self.cm.reset_focus_style(self)



class CustomRadioButton(wx.RadioButton):
    """
    Radio button personalizzato con gestione del focus e temi.
    """

    def __init__(self, parent, color_manager, label="", *args, **kwargs):
        super().__init__(parent, label=label, *args, **kwargs)
        self.cm = color_manager  # Gestione dei colori
        #self.fh = focus_handler  # Gestione del focus

        # Imposta lo stile predefinito
        self.cm.apply_default_style(self)

        # Collega gli eventi di focus
        self.cm.bind_focus_events(self)

    def SetFocus(self):
        """Imposta il focus sul radio button."""
        super().SetFocus()
        self.cm.apply_focus_style(self)

    def KillFocus(self):
        """Rimuove il focus dal radio button."""
        super().KillFocus()
        self.cm.reset_focus_style(self)



class CustomStaticText(wx.StaticText):
    """
    Etichetta di testo statico personalizzata con gestione del focus e temi.
    """

    def __init__(self, parent, color_manager, label="", *args, **kwargs):
        super().__init__(parent, label=label, *args, **kwargs)
        self.cm = color_manager  # Gestione dei colori
        #self.fh = focus_handler  # Gestione del focus

        # Imposta lo stile predefinito
        self.cm.apply_default_style(self)

        # Collega gli eventi di focus
        self.cm.bind_focus_events(self)

    def SetFocus(self):
        """Imposta il focus sull'etichetta."""
        super().SetFocus()
        self.cm.apply_focus_style(self)

    def KillFocus(self):
        """Rimuove il focus dall'etichetta."""
        super().KillFocus()
        self.cm.reset_focus_style(self)



class CustomSlider(wx.Slider):
    """
    Slider personalizzato con gestione del focus e temi.
    """

    def __init__(self, parent, color_manager, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.cm = color_manager  # Gestione dei colori
        #self.fh = focus_handler  # Gestione del focus

        # Imposta lo stile predefinito
        self.cm.apply_default_style(self)

        # Collega gli eventi di focus
        self.cm.bind_focus_events(self)

    def SetFocus(self):
        """Imposta il focus sullo slider."""
        super().SetFocus()
        self.cm.apply_focus_style(self)

    def KillFocus(self):
        """Rimuove il focus dallo slider."""
        super().KillFocus()
        self.cm.reset_focus_style(self)



class CustomButton(wx.Button):
    """
    Pulsante personalizzato con gestione centralizzata del focus.
    """

    def __init__(self, parent, color_manager, label, size=DEFAULT_BUTTON_SIZE, font_size=DEFAULT_FONT_SIZE, event_handler=None, *args, **kwargs):
        super().__init__(parent, label=label, size=size)
        self.cm = color_manager# Componente per la gestione del focus

        # Imposta il font e collega l'evento del pulsante
        self.SetFont(wx.Font(font_size, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        if event_handler:
            self.Bind(wx.EVT_BUTTON, event_handler)

        # Collega gli eventi di focus
        self.cm.apply_default_style(self)
        self.cm.bind_focus_events(self)


    def SetFocus(self):
        """Imposta il focus sul pulsante."""
        super().SetFocus()
        self.cm.apply_focus_style(self)


    def KillFocus(self):
        """Rimuove il focus dal pulsante."""
        super().KillFocus()
        self.cm.reset_focus_style(self)



class CustomListCtrl(wx.ListCtrl):
    """
    ListCtrl personalizzata con gestione centralizzata del focus e dei colori.
    """

    def __init__(self, parent, color_manager, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.cm = color_manager                     # Componente per la gestione dei colori
        #self.fh = focus_handler                     # Componente per la gestione del focus
        self.cm.apply_default_style(self)           # applica i colori di default per la lista

        # Collega gli eventi di focus
        #self.Bind(wx.EVT_SET_FOCUS, self.on_list_focus)
        #self.Bind(wx.EVT_KILL_FOCUS, self.on_list_kill_focus)

        # Collega l'evento di selezione degli elementi
        self.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.on_item_focused)

    def on_item_focused(self, event):
        """
        Gestisce l'evento di focus su una riga della lista.
        """
        selected_item = event.GetIndex()
        self.reset_focus_style_for_all_items(selected_item)
        self.apply_selection_style(selected_item)
        self.Refresh()
        event.Skip()

    def SetFocus(self):
        """Imposta il focus sulla ListCtrl e riapplica i colori corretti."""
        super().SetFocus()
        #self.reset_focus_style_for_all_items()  # Riapplica i colori dark a tutte le righe
        #self.apply_selection_style(self.GetFocusedItem())  # Riapplica lo stile di selezione
        #self.Refresh()


    def reset_focus_style_for_all_items(self, selected_item=None):
        """
        Resetta lo stile di tutte le righe tranne quella selezionata.
        """
        for i in range(self.GetItemCount()):
            if i != selected_item:
                self.cm.apply_default_style_to_list_item(self, i)

        self.Refresh()

    def apply_selection_style(self, item_index):
        """
        Applica lo stile di selezione a un elemento della lista.
        """
        self.cm.apply_selection_style_to_list_item(self, item_index)





#@@# sezione funzioni helper per la creazione di elementi dell'interfaccia utente

def create_button(parent, label, size=DEFAULT_BUTTON_SIZE, font_size=DEFAULT_FONT_SIZE, event_handler=None):
    """
    Crea un pulsante con stile predefinito.

    :param parent: Il genitore del pulsante (es. un pannello).
    :param label: Testo del pulsante.
    :param size: Dimensioni del pulsante (larghezza, altezza). Default: (250, 90).
    :param font_size: Dimensione del font. Default: 20.
    :param event_handler: Funzione da chiamare quando il pulsante viene cliccato (opzionale).
    :return: Un'istanza di wx.Button.
    """

    button = wx.Button(parent, label=label, size=size)
    button.SetFont(wx.Font(font_size, wx.DEFAULT, wx.NORMAL, wx.BOLD))
    if event_handler:
        button.Bind(wx.EVT_BUTTON, event_handler)

    return button


def create_list_ctrl(parent, columns, color_manager=cm, focus_handler=None, style=DEFAULT_LIST_STYLE):
    """

    Crea una lista (wx.ListCtrl) con colonne personalizzabili.
    :param parent: Il genitore della lista.
    :param columns: Lista di tuple (nome_colonna, larghezza).
    :param color_manager: Istanza di ColorManager.
    :param focus_handler: Istanza di FocusHandler.
    :param style: Stile della lista.
    :return: Un'istanza di CustomListCtrl.
    """

    list_ctrl = CustomListCtrl(
        parent,
        color_manager=color_manager,
        focus_handler=focus_handler,
        style=style
    )

    # Aggiungi le colonne alla lista
    for idx, (col_name, width) in enumerate(columns):
        list_ctrl.InsertColumn(idx, col_name, width=width)

    return list_ctrl


def create_search_bar(parent, placeholder="Cerca...", event_handler=None):
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
    return search_ctrl


def create_sizer(orientation=wx.VERTICAL):
    """
    Crea un sizer per organizzare gli elementi dell'interfaccia utente.

    :param orientation: Orientamento del sizer (wx.VERTICAL o wx.HORIZONTAL). Default: wx.VERTICAL.
    :return: Un'istanza di wx.BoxSizer.
    """
    return wx.BoxSizer(orientation)


def add_to_sizer(sizer, element, proportion=0, flag=wx.ALL, border=10):
    """
    Aggiunge un elemento a un sizer con parametri predefiniti.

    :param sizer: Il sizer a cui aggiungere l'elemento.
    :param element: L'elemento da aggiungere (es. un pulsante o una lista).
    :param proportion: Proporzione dell'elemento nel sizer. Default: 0.
    :param flag: Flag di allineamento. Default: wx.ALL.
    :param border: Spazio intorno all'elemento. Default: 10.
    """
    sizer.Add(element, proportion=proportion, flag=flag, border=border)

def create_common_controls():
    """
    Crea controlli comuni per la ricerca di carte.

    :return: Un dizionario con i controlli creati.
    """

    # Definizione dei campi comuni
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

def create_checklistbox(parent, choices, event_handler=None):
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

def create_check_list_box(parent, choices, label=""):
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

def create_separator(parent, style=wx.LI_HORIZONTAL, thickness=1, color=None):
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
    separator.SetMinSize((-1, thickness))  # Imposta lo spessore della linea
    return separator



#@@# End del modulo
if __name__ == "__main__":
    log.debug(f"Carico: {__name__}")
