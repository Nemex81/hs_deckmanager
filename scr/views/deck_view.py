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
from ..db import session, Card, DeckCard, Deck
from ..models import load_deck_from_db, load_cards
from .proto_views import BasicView
#from .view_components import CardManagerFrame
from .card_edit_dialog import CardEditDialog
from utyls.enu_glob import EnuColors, ENUCARD, EnuExtraCard, EnuCardType, EnuSpellType, EnuSpellSubType, EnuPetSubType, EnuHero, EnuRarity, EnuExpansion
from utyls import helper as hp
from utyls import logger as log
#import pdb



class DeckViewFrame(BasicView):
    """Finestra per gestire le carte di un mazzo."""

    def __init__(self, parent, deck_manager, deck_name):
        self.parent = parent
        self.deck_manager = deck_manager
        self.mode = "deck"                              # Modalità "deck" per gestire i mazzi
        self.deck_name = deck_name
        self.deck_content = self.deck_manager.get_deck(deck_name)  # Carica il mazzo
        
        if not self.deck_content:
            raise ValueError(f"Mazzo non trovato: {deck_name}")
        
        # Chiamata al costruttore della classe base
        super().__init__(parent, title=f"Mazzo: {deck_name}", size=(1200, 800))
        #self.Maximize()                                 # Massimizza la finestra

    def init_ui_elements(self):
        """Inizializza l'interfaccia utente."""

        # Lista delle carte
        self.card_list = wx.ListCtrl(
            self.panel,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN
        )
        self.card_list.AppendColumn("Nome", width=250)
        self.card_list.AppendColumn("Mana", width=50)
        self.card_list.AppendColumn("Quantità", width=80)
        self.card_list.AppendColumn("Tipo", width=120)
        self.card_list.AppendColumn("Tipo Magia", width=120)
        self.card_list.AppendColumn("Sottotipo", width=120)
        self.card_list.AppendColumn("Attacco", width=50)
        self.card_list.AppendColumn("Vita", width=50)
        self.card_list.AppendColumn("Durabilità", width=50)
        self.card_list.AppendColumn("Rarità", width=120)
        self.card_list.AppendColumn("Espansione", width=500)

        # Aggiungi la lista alla finestra
        self.sizer.Add(self.card_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Pulsanti azione
        btn_panel = wx.Panel(self.panel)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Aggiungi i pulsanti
        for label in ["Aggiorna", "Aggiungi Carta", "Modifica Carta", "Elimina Carta", "Chiudi"]:
            btn = wx.Button(btn_panel, label=label)
            btn_sizer.Add(btn, flag=wx.RIGHT, border=5)
            if label == "Aggiorna":
                btn.Bind(wx.EVT_BUTTON, self.on_reset)
            elif label == "Aggiungi Carta":
                btn.Bind(wx.EVT_BUTTON, self.on_add_card)
            elif label == "Modifica Carta":
                btn.Bind(wx.EVT_BUTTON, self.on_edit_card)
            elif label == "Elimina Carta":
                btn.Bind(wx.EVT_BUTTON, self.on_delete_card)
            else:
                btn.Bind(wx.EVT_BUTTON, lambda e: self.Close())

        # Aggiungi i pulsanti al pannello
        btn_panel.SetSizer(btn_sizer)
        self.sizer.Add(btn_panel, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        # Imposta il layout principale
        #self.panel.SetSizer(self.sizer)
        self.Layout()

        # Carica le carte
        self.load_cards()

        # Aggiungi eventi
        self.card_list.Bind(wx.EVT_LIST_COL_CLICK, self.on_column_click)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_press)

    def init_search(self):
        """Aggiunge la barra di ricerca."""
        panel = self.GetChildren()[0]  # Ottieni il pannello principale
        sizer = panel.GetSizer()

        # Barra di ricerca
        search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.search_ctrl = wx.SearchCtrl(panel)
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.on_search)
        search_sizer.Add(self.search_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        # Aggiungi la barra di ricerca al layout
        sizer.Insert(0, search_sizer, flag=wx.EXPAND | wx.ALL, border=10)

    def load_cards(self, filters=None):
        """Carica le carte nel mazzo."""
        load_cards(self.card_list, self.deck_content, self.mode, filters)

    def on_reset(self, event):
        """Ripristina la visualizzazione originale."""
        if hasattr(self, "search_ctrl"):
            self.search_ctrl.SetValue("")  # Resetta la barra di ricerca
        self.load_cards()  # Ricarica le carte senza filtri
        self.sort_cards(1)  # Ordina per "Mana" (colonna 1)
        self.card_list.SetFocus()
        self.card_list.Select(0)
        self.card_list.Focus(0)
        self.card_list.EnsureVisible(0)

    def on_add_card(self, event):
        """Aggiunge una nuova carta al mazzo."""
        dlg = CardEditDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            card_name = dlg.get_card_name()
            if card_name:
                card = session.query(Card).filter_by(name=card_name).first()
                if card:
                    self.deck_content["cards"].append({
                        "name": card.name,
                        "mana_cost": card.mana_cost,
                        "quantity": 1
                    })
                    self.load_cards()
                    wx.MessageBox(f"Carta '{card_name}' aggiunta al mazzo.", "Successo")
                else:
                    wx.MessageBox("Carta non trovata nel database.", "Errore")
        dlg.Destroy()

    def on_edit_card(self, event):
        """Modifica la carta selezionata."""
        selected = self.card_list.GetFirstSelected()
        if selected != -1:
            card_name = self.card_list.GetItemText(selected)
            card = session.query(Card).filter_by(name=card_name).first()
            if card:
                dlg = CardEditDialog(self, card)
                if dlg.ShowModal() == wx.ID_OK:
                    self.load_cards()
                    wx.MessageBox(f"Carta '{card_name}' modificata con successo.", "Successo")
                    self.select_card_by_name(card_name)
                dlg.Destroy()
            else:
                wx.MessageBox("Carta non trovata nel database.", "Errore")
        else:
            wx.MessageBox("Seleziona una carta da modificare.", "Errore")

    def on_delete_card(self, event):
        """Elimina la carta selezionata."""
        selected = self.card_list.GetFirstSelected()
        if selected != -1:
            card_name = self.card_list.GetItemText(selected)
            if wx.MessageBox(f"Eliminare la carta '{card_name}'?", "Conferma", wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
                self.deck_content["cards"] = [
                    card_data for card_data in self.deck_content["cards"]
                    if card_data["name"] != card_name
                ]
                self.load_cards()
                wx.MessageBox(f"Carta '{card_name}' eliminata dal mazzo.", "Successo")
        else:
            wx.MessageBox("Seleziona una carta da eliminare.", "Errore")

    def on_column_click(self, event):
        """Ordina le carte in base alla colonna selezionata."""
        col = event.GetColumn()
        self.sort_cards(col)

    def sort_cards(self, col):
        """Ordina le carte in base alla colonna selezionata."""
        items = []
        for i in range(self.card_list.GetItemCount()):
            item = [self.card_list.GetItemText(i, c) for c in range(self.card_list.GetColumnCount())]
            items.append(item)

        def safe_int(value):
            try:
                return int(value)
            except ValueError:
                return float('inf') if value == "-" else value

        if col == 1:  # Colonna "Mana" (numerica)
            items.sort(key=lambda x: safe_int(x[col]))
        else:  # Altre colonne (testuali)
            items.sort(key=lambda x: x[col])

        self.card_list.DeleteAllItems()
        for item in items:
            self.card_list.Append(item)

    def select_card_by_name(self, card_name):
        """Seleziona una carta nella lista in base al nome."""
        if not card_name:
            return
        for i in range(self.card_list.GetItemCount()):
            if self.card_list.GetItemText(i) == card_name:
                self.card_list.Select(i)
                self.card_list.Focus(i)
                self.card_list.EnsureVisible(i)
                self.card_list.SetFocus()
                break

    def on_key_press(self, event):
        """Gestisce i tasti premuti per ordinare la lista."""
        key_code = event.GetKeyCode()
        if ord('1') <= key_code <= ord('9'):
            col = key_code - ord('1')
            if col < self.card_list.GetColumnCount():
                self.sort_cards(col)
        event.Skip()

    def on_search(self, event):
        """Filtra le carte in base al testo di ricerca."""
        search_text = self.search_ctrl.GetValue().strip().lower()
        if search_text in ["", "tutti", "tutto", "all"]:
            self.on_reset(event)
        else:
            self.load_cards(filters={"name": search_text})

    def on_close(self, event):
        """Chiude la finestra."""
        self.parent.Show()
        self.Close()
        self.Destroy()



#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
