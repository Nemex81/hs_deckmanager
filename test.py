"""

    deck_view.py

    Modulo per la finestra di dialogo della gestione del mazzo.

    descrizione:
        Questo modulo contiene la classe DeckViewFrame, che rappresenta la finestra di dialogo per la gestione delle carte di un mazzo.
        La finestra di dialogo include una lista di carte, una barra di ricerca, filtri avanzati e pulsanti per aggiungere, modificare e rimuovere carte.

    path:
        scr/views/collection_view.py

    Note:
        - La finestra di dialogo DeckViewFrame eredita dalla classe CardManagerFrame, che a sua volta eredita dalla classe BasicView.
        - Questo modulo utilizza la libreria wxPython per la creazione delle finestre di dialogo dell'interfaccia utente.

"""

# lib
import wx, pyperclip
from sqlalchemy.exc import SQLAlchemyError
from scr.db import session, Card, DeckCard, Deck
from scr.models import load_deck_from_db, load_cards, DbManager
from scr.views.proto_views import BasicView
from scr.views.card_edit_dialog import CardEditDialog
from utyls.enu_glob import EnuColors, ENUCARD, EnuExtraCard, EnuCardType, EnuSpellType, EnuSpellSubType, EnuPetSubType, EnuHero, EnuRarity, EnuExpansion
from utyls import helper as hp
from utyls import logger as log
#import pdb



class DeckViewFrame(BasicView):
    """Finestra per gestire le carte di un mazzo."""

    def __init__(self, parent, deck_manager, deck_name):
        title = f"Deck: {deck_name}"
        super().__init__(parent, title=title)
        self.db_manager = deck_manager
        self.deck_name = deck_name
        self.deck_content = None

    def init_search(self):
        """Aggiunge la barra di ricerca."""

        # Barra di ricerca
        self.search_ctrl = wx.SearchCtrl(self)
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.on_search)
        self.search_ctrl.Bind(wx.EVT_TEXT, self.on_search)
        self.search_ctrl.ShowCancelButton(True)

        # Aggiungi la barra di ricerca al layout
        self.sizer.Add(self.search_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

    def init_list(self):
        """ Inizializza la lista delle carte. """
        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.list_ctrl.InsertColumn(0, "Nome", width=200)
        self.list_ctrl.InsertColumn(1, "Costo", width=50)
        self.list_ctrl.InsertColumn(2, "Tipo", width=100)
        self.list_ctrl.InsertColumn(3, "Rarità", width=100)
        self.list_ctrl.InsertColumn(4, "Espansione", width=100)
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_item_selected)
        self.sizer.Add(self.list_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

    def init_buttons(self):
        """ Inizializza i pulsanti. """
        self.btn_add = wx.Button(self, label="Aggiungi carta")
        self.btn_add.Bind(wx.EVT_BUTTON, self.on_add_card)
        self.sizer.Add(self.btn_add, flag=wx.ALL, border=5)

        self.btn_edit = wx.Button(self, label="Modifica carta")
        self.btn_edit.Bind(wx.EVT_BUTTON, self.on_edit_card)
        self.sizer.Add(self.btn_edit, flag=wx.ALL, border=5)

        self.btn_remove = wx.Button(self, label="Rimuovi carta")
        self.btn_remove.Bind(wx.EVT_BUTTON, self.on_remove_card)
        self.sizer.Add(self.btn_remove, flag=wx.ALL, border=5)

        self.btn_copy = wx.Button(self, label="Copia lista")
        self.btn_copy.Bind(wx.EVT_BUTTON, self.on_copy_list)
        self.sizer.Add(self.btn_copy, flag=wx.ALL, border=5)

    def load_deck(self):
        """ Carica il mazzo dal database. """
        self.deck_content = load_deck_from_db(self.db_manager, self.deck_name)
        self.load_cards()


    def init_ui_elements(self):
        """ Inizializza gli elementi dell'interfaccia utente. """
        self.init_search()
        self.init_list()
        self.init_buttons()
        self.load_deck()

    def load_cards(self, filters=None):
        """ Carica le carte del mazzo. """
        load_cards(self.list_ctrl, self.deck_content, filters)

    def on_search(self, event):
        """ Filtra le carte in base al testo di ricerca. """
        search_text = self.search_ctrl.GetValue()
        self.load_cards(filters=search_text)

    def on_add_card(self, event):
        """ Aggiunge una nuova carta al mazzo. """
        dlg = CardEditDialog(self, mode="add", deck_name=self.deck_name)
        dlg.ShowModal()
        self.load_deck()

    def on_edit_card(self, event):
        """ Modifica una carta del mazzo. """
        selected_index = self.list_ctrl.GetFirstSelected()
        if selected_index == -1:
            return
        card_name = self.list_ctrl.GetItemText(selected_index)
        dlg = CardEditDialog(self, mode="edit", deck_name=self.deck_name, card_name=card_name)
        dlg.ShowModal()
        self.load_deck()

    def on_delete_card(self, event):
        """ Rimuove una carta dal mazzo. """
        selected_index = self.list_ctrl.GetFirstSelected()
        if selected_index == -1:
            return
        card_name = self.list_ctrl.GetItemText(selected_index)
        card = self.deck_content.get_card_by_name(card_name)
        self.db_manager.remove_card_from_deck(self.deck_name, card)
        self.load_deck()

    def on_copy_list(self, event):
        """ Copia la lista delle carte negli appunti. """
        card_list = [card.name for card in self.deck_content.cards]
        card_list_str = "\n".join(card_list)
        pyperclip.copy(card_list_str)
        log.info("Lista delle carte copiata negli appunti.")

    def on_item_selected(self, event):
        """ Mostra le informazioni della carta selezionata. """
        selected_index = self.list_ctrl.GetFirstSelected()
        card_name = self.list_ctrl.GetItemText(selected_index)
        card = self.deck_content.get_card_by_name(card_name)
        log.info(f"Carta selezionata: {card}")
        hp.show_card_info(card)

    def on_close(self, event):
        """ Chiude la finestra. """
        self.Close()

    def on_exit(self, event):
        """ Chiude la finestra. """
        self.Close()


#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
    parent = None
    nome_mazzo = Deck(name="Mazzo di prova", player_class="Druido", game_format="Standard")
    db_manager = DbManager()
    app = wx.App(False)
    frame = DeckViewFrame(parent, db_manager, nome_mazzo)
    frame.Show()
    app.MainLoop()