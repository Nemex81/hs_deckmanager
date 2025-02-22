"""
    Modulo per la gestione dei componenti delle finestre dell'applicazione

    path:
        ./scr/views/view_components.py

    Descrizione:
        Questo modulo contiene funzioni helper per la creazione di elementi dell'interfaccia utente
        comuni, come pulsanti, liste, barre di ricerca e sizer. Le funzioni sono progettate per
        essere riutilizzabili in tutte le finestre dell'applicazione, riducendo la duplicazione
        del codice e migliorando la manutenibilità.

    Spiegazione delle Funzioni
    1. create_button:
        ◦ Crea un pulsante con dimensioni, font e stile predefiniti.
        ◦ Permette di specificare un gestore di eventi per il clic.

    2. create_list_ctrl:
        ◦  Crea una lista (wx.ListCtrl) con colonne personalizzabili.
        ◦  Supporta l'aggiunta di colonne con larghezze specifiche.

    3. create_search_bar:
        ◦  Crea una barra di ricerca (wx.SearchCtrl) con un placeholder personalizzabile.
        ◦  Permette di specificare un gestore di eventi per la ricerca.

    4.  create_sizer:
        ◦  Crea un sizer (verticale o orizzontale) per organizzare gli elementi.

    5.  add_to_sizer:
        ◦  Aggiunge un elemento a un sizer con parametri predefiniti (proporzione, flag, bordo).

    6.  create_message_dialog:
        ◦  Crea una finestra di dialogo per messaggi di conferma con titolo e stile personalizzabili.

    None:
        ◦  Questo modulo non è progettato per essere eseguito
        ◦  Le funzioni sono progettate per essere importate in altri moduli
        ◦  Le funzioni sono progettate per essere utilizzate in combinazione con wxPython

"""

# Lib
import wx
from utyls import enu_glob as eg
from utyls import helper as hp
from utyls import logger as log
#import pdb



# Configurazione di default
DEFAULT_BUTTON_SIZE = (250, 90)
DEFAULT_FONT_SIZE = 20
DEFAULT_LIST_STYLE = wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN


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


def create_list_ctrl(parent, columns, style=DEFAULT_LIST_STYLE):
    """
    Crea una lista (wx.ListCtrl) con colonne predefinite.

    :param parent: Il genitore della lista.
    :param columns: Lista di tuple (nome_colonna, larghezza). Esempio: [("Nome", 250), ("Mana", 50)].
    :param style: Stile della lista. Default: wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN.
    :return: Un'istanza di wx.ListCtrl.
    """

    list_ctrl = wx.ListCtrl(parent, style=style)
    for idx, (col_name, width) in enumerate(columns):
        list_ctrl.AppendColumn(col_name, width=width)
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

def question_box(parent, message, title="Conferma", style=wx.YES_NO | wx.ICON_QUESTION):
    """
    Crea una finestra di dialogo per messaggi di conferma.

    :param parent: Il genitore della finestra di dialogo.
    :param message: Il messaggio da visualizzare.
    :param title: Il titolo della finestra. Default: "Conferma".
    :param style: Lo stile della finestra. Default: wx.YES_NO | wx.ICON_QUESTION.
    :return: Un'istanza di wx.MessageDialog.
    """
    return wx.MessageDialog(parent, message, title, style)



#@@# End del modulo
if __name__ == "__main__":
    log.debug(f"Carico: {__name__}")
