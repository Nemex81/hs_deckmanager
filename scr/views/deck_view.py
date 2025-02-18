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
from ..models import DbManager, AppController
from ..db import session, Card, DeckCard, Deck
from ..models import DbManager, AppController, load_cards_from_db, load_deck_from_db, load_cards
from .view_components import BasicView, BasicDialog, CardManagerFrame, SingleCardView, CardEditDialog
from utyls.enu_glob import EnuColors, ENUCARD, EnuExtraCard, EnuCardType, EnuSpellType, EnuSpellSubType, EnuPetSubType, EnuHero, EnuRarity, EnuExpansion
from utyls import helper as hp
from utyls import logger as log
#import pdb



class DeckViewFrame(CardManagerFrame):
    """Finestra per gestire le carte di un mazzo."""

    def __init__(self, parent, deck_manager, deck_name):
        super().__init__(parent, deck_manager, mode="deck", deck_name=deck_name)
        self.init_search()

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


        # eventi
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def load_cards(self, filters=None):
        """ carica le carte utilizzando le funzionihelper sopra definite"""
        load_cards(self.card_list, self.deck_content, self.mode, filters)

    def on_reset(self, event):
        """Ripristina la visualizzazione originale, rimuovendo i filtri e riordinando le colonne."""

        # Rimuovi i filtri
        if hasattr(self, "search_ctrl"):
            self.search_ctrl.SetValue("")  # Resetta la barra di ricerca

        if hasattr(self, "filters"):
            del self.filters  # Libera la memoria occupata dai filtri precedenti

        # Ricarica le carte senza filtri
        #self.load_cards()
        load_cards(self.card_list, self.deck_content, self.mode)

        # Ripristina l'ordinamento predefinito (ad esempio, per "Mana" e "Nome")
        self.sort_cards(1)  # Ordina per "Mana" (colonna 1)
        self.card_list.SetFocus()
        self.card_list.Select(0)
        self.card_list.Focus(0)
        self.card_list.EnsureVisible(0)


    def on_add_card(self, event):
        """Aggiunge una nuova carta (alla collezione o al mazzo)."""

        dlg = CardEditDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            card_name = dlg.get_card_name()
            if card_name:
                if self.mode == "collection":
                    # Aggiungi la carta alla collezione (se non esiste già)
                    card = session.query(Card).filter_by(name=card_name).first()
                    if not card:
                        wx.MessageBox("La carta non esiste nel database.", "Errore")

                    else:
                        self.load_cards()
                        wx.MessageBox(f"Carta '{card_name}' aggiunta alla collezione.", "Successo")

                elif self.mode == "deck":
                    # Aggiungi la carta al mazzo (se non è già presente)
                    for card_data in self.deck_content["cards"]:
                        if card_data["name"] == card_name:
                            wx.MessageBox("La carta è già presente nel mazzo.", "Errore")
                            return

                    # gestisco l'aggiunta della carta al mazzo
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
                    self.load_cards()  # Ricarica la lista delle carte
                    wx.MessageBox(f"Carta '{card_name}' modificata con successo.", "Successo")
                    self.select_card_by_name(card_name)  # Seleziona e mette a fuoco la carta modificata

                dlg.Destroy()

            else:
                wx.MessageBox("Carta non trovata nel database.", "Errore")

        else:
            wx.MessageBox("Seleziona una carta da modificare.", "Errore")


    def on_close(self, event):
        """Chiude la finestra di dialogo."""
        self.parent.Show()
        self.Close()
        self.Destroy()





#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
