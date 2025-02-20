"""
        Modulo per la gestione delle finestre secondarie dell'applicazione

        path:
            ./scr/views/view_components.py

    Descrizione:
        Questo modulo contiene le classi per la gestione delle finestre secondarie dell'applicazione.
        Le classi base come SingleCardView e ListView forniscono funzionalità specifiche per la gestione di carte e elenchi.
        Le classi derivate come CardsListView e DecksListView implementano le finestre per la visualizzazione delle carte e dei mazzi.

"""

# Lib
import wx
from abc import ABC, abstractmethod
#from scr.models import load_cards_from_db
from utyls import helper as hp
from ..db import session, Card, Deck
from .proto_views import BasicDialog, BasicView, SingleCardView, ListView
from utyls.enu_glob import EnuCardType, EnuSpellSubType, EnuPetSubType, EnuRarity, EnuExpansion, EnuSpellType
from utyls import logger as log



class CardManagerFrame(wx.Frame):
    """

        Finestra generica per gestire le carte (collezione o mazzo).

        :param parent: Finestra principale (frame), genitore della finestra di dialogo
        :param deck_manager: Gestore dei mazzi
        :param mode: Modalità della finestra ("collection" o "deck")
        :param deck_name: Nome del mazzo (se la modalità è "deck")

    """

    def __init__(self, parent, deck_manager=None, mode="collection", deck_name=None):
        title = "Collezione Carte" if mode == "collection" else f"Mazzo: {deck_name}"
        super().__init__(parent, title=title, size=(1200, 800))
        self.parent = parent
        self.SetBackgroundColour('yellow')
        self.deck_manager = deck_manager
        self.mode = mode  # "collection" o "deck"
        self.deck_name = deck_name
        self.deck_content = self.deck_manager.get_deck(deck_name) if mode == "deck" else None
        if self.mode == "deck" and not self.deck_content:
            raise ValueError(f"Mazzo non trovato: {deck_name}")

        self.Centre()    # Centra la finestra
        self.Maximize()  # Massimizza la finestra
        self.init_ui()  # Inizializza l'interfaccia utente


    def init_ui(self):
        """ Inizializza l'interfaccia utente. """

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Lista delle carte
        self.card_list = wx.ListCtrl(
            panel,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN
        )
        self.card_list.AppendColumn("Nome", width=250)
        self.card_list.AppendColumn("Mana", width=50)
        
        # Aggiungi la colonna "Quantità" o "Classe" in base alla modalità
        if self.mode == "deck":
            self.card_list.AppendColumn("Quantità", width=80)
        else:
            self.card_list.AppendColumn("Classe", width=120)
            
        self.card_list.AppendColumn("Tipo", width=120)
        self.card_list.AppendColumn("Tipo Magia", width=120)
        self.card_list.AppendColumn("Sottotipo", width=120)
        self.card_list.AppendColumn("Attacco", width=50)
        self.card_list.AppendColumn("Vita", width=50)
        self.card_list.AppendColumn("Durabilità", width=50)  # Aggiungi questa colonna
        self.card_list.AppendColumn("Rarità", width=120)
        self.card_list.AppendColumn("Espansione", width=500)
        
        # Aggiungo la lista alla finestra
        sizer.Add(self.card_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Pulsanti azione
        btn_panel = wx.Panel(panel)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Aggiungo gli altri pulsanti
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
        
        # Aggiungo i pulsanti al pannello
        btn_panel.SetSizer(btn_sizer)
        sizer.Add(btn_panel, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        panel.SetSizer(sizer)
        self.load_cards()

        # Aggiungi l'evento per il clic sulle intestazioni delle colonne
        self.card_list.Bind(wx.EVT_LIST_COL_CLICK, self.on_column_click)

        # Aggiungi l'evento per i tasti premuti
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_press)


    def load_cards(self, filters=None):
        """ carica le carte utilizzando le funzionihelper sopra definite"""
        pass


    def on_column_click(self, event):
        """Gestisce il clic sulle intestazioni delle colonne per ordinare le carte."""
        col = event.GetColumn()
        self.sort_cards(col)


    def sort_cards(self, col):
        """Ordina le carte in base alla colonna selezionata."""

        # Ottieni i dati dalla lista
        items = []
        for i in range(self.card_list.GetItemCount()):
            item = [self.card_list.GetItemText(i, c) for c in range(self.card_list.GetColumnCount())]
            items.append(item)

        # Funzione lambda per gestire la conversione sicura a intero
        def safe_int(value):
            try:
                return int(value)
            except ValueError:
                # Assegna un valore predefinito per valori non numerici
                return float('inf') if value == "-" else value

        # Ordina i dati in base alla colonna selezionata
        if col == 1:  # Colonna "Mana" (numerica)
            items.sort(key=lambda x: safe_int(x[col]))

        else:  # Altre colonne (testuali)
            items.sort(key=lambda x: x[col])

        # Aggiorna la lista con i dati ordinati
        self.card_list.DeleteAllItems()
        for item in items:
            self.card_list.Append(item)


    def select_card_by_name(self, card_name):
        """Seleziona la carta nella lista in base al nome e sposta il focus di sistema a quella riga.

        :param card_name: Nome della carta da selezionare
        """

        if not card_name:
            return

        # Trova l'indice della carta nella lista
        for i in range(self.card_list.GetItemCount()):
            if self.card_list.GetItemText(i) == card_name:
                self.card_list.Select(i)                            # Seleziona la riga
                self.card_list.Focus(i)                             # Sposta il focus alla riga selezionata
                self.card_list.EnsureVisible(i)                     # Assicurati che la riga sia visibile
                self.card_list.SetFocus()                           # Imposta il focus sulla lista
                break


    def on_reset(self, event):
        """Ripristina la visualizzazione originale, rimuovendo i filtri e riordinando le colonne."""
        pass


    def on_add_card(self, event):
        """Aggiunge una nuova carta (alla collezione o al mazzo)."""
        pass


    def on_edit_card(self, event):
        """Modifica la carta selezionata."""
        pass


    def on_delete_card(self, event):
        """Elimina la carta selezionata (dalla collezione o dal mazzo)."""

        selected = self.card_list.GetFirstSelected()
        if selected != -1:
            card_name = self.card_list.GetItemText(selected)
            if wx.MessageBox(f"Eliminare la carta '{card_name}'?", "Conferma", wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
                try:
                    if self.mode == "collection":
                        # Elimina la carta dalla collezione
                        card = session.query(Card).filter_by(name=card_name).first()
                        if card:
                            session.delete(card)
                            session.commit()
                            self.load_cards()
                            wx.MessageBox(f"Carta '{card_name}' eliminata dalla collezione.", "Successo", wx.OK | wx.ICON_INFORMATION)

                        else:
                            wx.MessageBox("Carta non trovata nel database.", "Errore", wx.OK | wx.ICON_ERROR)

                    elif self.mode == "deck":
                        # Rimuovi la carta dal mazzo
                        self.deck_content["cards"] = [
                            card_data for card_data in self.deck_content["cards"]
                            if card_data["name"] != card_name
                        ]

                        # Aggiorna il mazzo nel database
                        self.load_cards()
                        wx.MessageBox(f"Carta '{card_name}' eliminata dal mazzo.", "Successo", wx.OK | wx.ICON_INFORMATION)

                except Exception as e:
                    log.error(f"Errore durante l'eliminazione della carta: {str(e)}")
                    wx.MessageBox(f"Errore durante l'eliminazione della carta: {str(e)}", "Errore", wx.OK | wx.ICON_ERROR)

        else:
            wx.MessageBox("Seleziona una carta da eliminare.", "Errore", wx.OK | wx.ICON_ERROR)


    def on_column_click(self, event):
        """Gestisce il clic sulle intestazioni delle colonne per ordinare la lista."""

        col = event.GetColumn()
        self.sort_cards(col)


    def on_key_press(self, event):
        """Gestisce i tasti premuti per ordinare la lista."""

        key_code = event.GetKeyCode()
        if key_code >= ord('1') and key_code <= ord('9'):
            col = key_code - ord('1')  # Converti il tasto premuto in un indice di colonna (0-8)
            if col < self.card_list.GetColumnCount():
                self.sort_cards(col)

        event.Skip()


    def on_search(self, event):
        """Gestisce la ricerca testuale."""

        search_text = self.search_ctrl.GetValue().strip().lower()
        # Se la casella di ricerca è vuota o contiene "tutti" o "all", ripristina la visualizzazione
        if search_text is None or search_text == "" or search_text in ["tutti", "tutto", "all"]:
            self.on_reset(event)

        else:
            # Altrimenti, applica la ricerca
            self.load_cards(filters={"name": search_text})





#@@# End del modulo
if __name__ == "__main__":
    log.debug(f"Carico: {__name__}")