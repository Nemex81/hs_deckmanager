"""

    collection_view.py

    Modulo per la finestra di dialogo della collezione di carte.

    descrizioone:
        Questo modulo contiene la classe CardCollectionFrame, che rappresenta la finestra di dialogo per la gestione della collezione di carte.
        La finestra di dialogo include una lista di carte, una barra di ricerca, filtri avanzati e pulsanti per aggiungere, modificare e rimuovere carte.
        La finestra di dialogo viene aperta dall'utente tramite il pulsante "Collezione" nella finestra principale.

    path:
        scr/views/collection_view.py

    Note:
        - La finestra di dialogo CardCollectionFrame eredita dalla classe CardManagerFrame, che a sua volta eredita dalla classe BasicView.
        Questo modulo utilizza la libreria wxPython per la creazione delle finestre di dialogo dell'interfaccia utente.

"""

# lib
import wx, pyperclip
from sqlalchemy.exc import SQLAlchemyError
from ..db import session, db_session, Card, DeckCard, Deck
from ..models import load_cards
from .proto_views import BasicView
from .view_components import  CardManagerFrame
from .card_edit_dialog import CardEditDialog
from .filters_dialog import FilterDialog
from utyls.enu_glob import EnuColors, ENUCARD, EnuExtraCard, EnuCardType, EnuSpellType, EnuSpellSubType, EnuPetSubType, EnuHero, EnuRarity, EnuExpansion
from utyls import helper as hp
from utyls import logger as log
#import pdb





#class CardCollectionFrame(CardManagerFrame):
class CardCollectionFrame(BasicView):
    """Finestra per gestire la collezione di carte."""

    def __init__(self, parent, db_manager):
        #self.mode = "collection"
        #self.deck_content = None
        #self.card_list = None
        super().__init__(parent, title="Collezione")
        self.parent = parent
        self.db_manager = db_manager

    def init_ui_elements(self):
        """Aggiunge la barra di ricerca e i filtri."""

        self.panel = self.GetChildren()[0]  # ottengo il pannello principale
        self.sizer = self.panel.GetSizer()
        self.SetBackgroundColour('yellow')
        self.panel.SetBackgroundColour('yellow')
        self.Maximize()

        # Lista delle carte
        self.card_list = wx.ListCtrl(    
            self.panel,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN
        )

        # Aggiungo il colore di sfondo alla lista
        self.card_list.SetBackgroundColour('yellow')

        # Aggiungo le colonne alla lista
        self.card_list.AppendColumn("Nome", width=250)
        self.card_list.AppendColumn("Mana", width=50)
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
        self.sizer.Add(self.card_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Pulsanti azione
        btn_panel = wx.Panel(self.panel)
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
        self.sizer.Add(btn_panel, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        self.panel.SetSizer(self.sizer)
        self.load_cards()

        # Aggiungi l'evento per il clic sulle intestazioni delle colonne
        self.card_list.Bind(wx.EVT_LIST_COL_CLICK, self.on_column_click)

        # Aggiungi l'evento per i tasti premuti
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_press)


        # Barra di ricerca
        search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.search_ctrl = wx.SearchCtrl(self.panel)
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.on_search)
        search_sizer.Add(self.search_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        # Pulsante filtri
        self.btn_filters = wx.Button(self.panel, label="Filtri Avanzati")
        self.btn_filters.Bind(wx.EVT_BUTTON, self.on_show_filters)
        search_sizer.Add(self.btn_filters, flag=wx.LEFT | wx.RIGHT, border=5)

        # Aggiungi la barra di ricerca e i filtri al layout
        self.sizer.Insert(0, search_sizer, flag=wx.EXPAND | wx.ALL, border=10)

        # eventi
        self.Bind(wx.EVT_CLOSE, self.on_close)


    def load_cards(self, filters=None):
        """ carica le carte utilizzando le funzionihelper sopra definite"""
        load_cards(filters=filters, card_list=self.card_list)


    def reset_filters(self):
        self.search_ctrl.SetValue("")
        self.load_cards()  # Ricarica la lista delle carte senza filtri


    def on_show_filters(self, event):
        """Mostra la finestra dei filtri avanzati."""

        dlg = FilterDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            # Applica i nuovi filtri
            filters = {
                "name": dlg.search_ctrl.GetValue(),
                "mana_cost": dlg.mana_cost.GetValue(),
                "card_type": dlg.card_type.GetValue(),
                "spell_type": dlg.spell_type.GetValue(),
                "card_subtype": dlg.card_subtype.GetValue(),
                "attack": dlg.attack.GetValue(),
                "health": dlg.health.GetValue(),
                "rarity": dlg.rarity.GetValue(),
                "expansion": dlg.expansion.GetValue()
            }
            self.load_cards(filters=filters)

        else:
            # Se l'utente annulla, resetta i filtri
            self.load_cards(filters=None)

        dlg.Destroy()


    def on_reset(self, event):
        """Ripristina la visualizzazione originale, rimuovendo i filtri e riordinando le colonne."""

        # Rimuovi i filtri
        if hasattr(self, "search_ctrl"):
            self.search_ctrl.SetValue("")  # Resetta la barra di ricerca

        if hasattr(self, "filters"):
            del self.filters  # Libera la memoria occupata dai filtri precedenti
        # Ricarica le carte senza filtri
        self.load_cards()

        # Ripristina l'ordinamento predefinito (ad esempio, per "Mana" e "Nome")
        self.sort_cards(1)  # Ordina per "Mana" (colonna 1)
        self.card_list.SetFocus()
        self.card_list.Select(0)
        self.card_list.Focus(0)
        self.card_list.EnsureVisible(0)


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

                except Exception as e:
                    log.error(f"Errore durante l'eliminazione della carta: {str(e)}")
                    wx.MessageBox(f"Errore durante l'eliminazione della carta: {str(e)}", "Errore", wx.OK | wx.ICON_ERROR)

        else:
            wx.MessageBox("Seleziona una carta da eliminare.", "Errore", wx.OK | wx.ICON_ERROR)



#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
