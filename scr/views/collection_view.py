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
import wx#, pyperclip
import wx.lib.newevent
#from sqlalchemy.exc import SQLAlchemyError
from ..db import session, db_session, Card, DeckCard, Deck
from ..models import load_cards
from .proto_views import BasicView, ListView, CollectionsListView
from .view_components import create_button, create_list_ctrl, create_sizer, add_to_sizer, create_search_bar
from .card_edit_dialog import CardEditDialog
from .filters_dialog import FilterDialog
from utyls import enu_glob as eg
from utyls import helper as hp
from utyls import logger as log
#import pdb

# Creazione di un evento personalizzato per la ricerca con debounce
SearchEvent, EVT_SEARCH_EVENT = wx.lib.newevent.NewEvent()



class CardCollectionFrame(BasicView):
    """Finestra per gestire la collezione di carte."""

    def __init__(self, parent, controller):
        if not controller:
            log.error("Il controller non può essere None.")
            raise ValueError("Il controller non può essere None.")

        self.mode = "collection"
        self.parent = parent
        self.controller = controller
        #self.controller = self.controller.collection_controller
        super().__init__(parent, title="Collezione")
        self.timer = wx.Timer(self)  # Timer per il debounce
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.Bind(EVT_SEARCH_EVENT, self.on_search_event)


    def init_ui_elements(self):
        """Inizializza l'interfaccia utente utilizzando le funzioni helper."""

        # Impostazioni finestra principale
        self.SetBackgroundColour('yellow')
        self.panel.SetBackgroundColour('blue')
        self.Centre()
        self.Maximize()

        # Creazione degli elementi dell'interfaccia

        # Barra di ricerca e filtri
        search_sizer = create_sizer(wx.HORIZONTAL)
        self.search_ctrl = create_search_bar(
            self.panel,
            placeholder="Cerca per nome...",
            event_handler=self.on_search
        )
        self.search_ctrl.Bind(wx.EVT_TEXT, self.on_search_text_change)  # Aggiunto per la ricerca dinamica
        add_to_sizer(search_sizer, self.search_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        # Pulsante filtri avanzati
        self.btn_filters = create_button(
            self.panel,
            label="Filtri Avanzati",
            event_handler=self.on_show_filters
        )
        add_to_sizer(search_sizer, self.btn_filters, flag=wx.LEFT | wx.RIGHT, border=5)

        # Aggiungo la barra di ricerca e i filtri al layout
        add_to_sizer(self.sizer, search_sizer, flag=wx.EXPAND | wx.ALL, border=10)

        # Lista delle carte
        self.card_list = create_list_ctrl(
            self.panel,
            columns=[
                ("Nome", 250),
                ("Mana", 50),
                ("Classe", 120),
                ("Tipo", 120),
                ("Tipo Magia", 120),
                ("Sottotipo", 120),
                ("Attacco", 50),
                ("Vita", 50),
                ("Durabilità", 50),
                ("Rarità", 120),
                ("Espansione", 500)
            ]
        )
        self.card_list.SetBackgroundColour('yellow')

        # Aggiungo la lista alla finestra
        add_to_sizer(self.sizer, self.card_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Pulsanti azione
        btn_panel = wx.Panel(self.panel)
        btn_sizer = create_sizer(wx.HORIZONTAL)

        # Creazione dei pulsanti
        buttons = [
            ("Aggiorna", self.on_reset),
            ("Aggiungi Carta", self.on_add_card),
            ("Modifica Carta", self.on_edit_card),
            ("Elimina Carta", self.on_delete_card),
            ("Chiudi", lambda e: self.Close())
        ]

        for label, handler in buttons:
            btn = create_button(btn_panel, label=label, event_handler=handler)
            add_to_sizer(btn_sizer, btn, flag=wx.RIGHT, border=5)

        # Aggiungo i pulsanti al pannello
        btn_panel.SetSizer(btn_sizer)
        add_to_sizer(self.sizer, btn_panel, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        # Imposta il layout principale
        self.Layout()

        # Carica le carte
        self.load_cards()

        # Aggiungi eventi
        self.card_list.Bind(wx.EVT_LIST_COL_CLICK, self.on_column_click)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_press)
        self.Bind(wx.EVT_CLOSE, self.on_close)


    def load_cards(self, filters=None):
        """Carica le carte utilizzando le funzioni helper sopra definite."""

        if not self.card_list:
            log.error("La lista delle carte non è stata inizializzata.")
            raise ValueError("La lista delle carte non è stata inizializzata.")

        load_cards(filters=filters, card_list=self.card_list)


    def reset_filters(self):
        """Resetta i filtri e ricarica la lista delle carte."""

        self.search_ctrl.SetValue("")
        self.load_cards()  # Ricarica la lista delle carte senza filtri


    def set_focus_to_list(self):
        """Imposta il focus sulla prima carta della lista carte."""

        if hasattr(self, "card_list"):
            self.card_list.SetFocus()
            self.card_list.Select(0)
            self.card_list.Focus(0)
            self.card_list.EnsureVisible(0)


    def on_show_filters(self, event):
        """Mostra la finestra dei filtri avanzati."""

        dlg = FilterDialog(self)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.reset_filters()
            self.load_cards(filters=None)

        # Sposta il focus sulla prima carta della lista carte di questa finestra
        self.set_focus_to_list()
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
        self.set_focus_to_list()  # Sposta il focus sulla prima carta della lista carte di questa finestra


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
        """Seleziona la carta nella lista in base al nome e sposta il focus di sistema a quella riga."""

        if not card_name:
            return

        # Trova l'indice della carta nella lista
        for i in range(self.card_list.GetItemCount()):
            if self.card_list.GetItemText(i) == card_name:
                self.card_list.Select(i)  # Seleziona la riga
                self.card_list.Focus(i)  # Sposta il focus alla riga selezionata
                self.card_list.EnsureVisible(i)  # Assicurati che la riga sia visibile
                self.card_list.SetFocus()  # Imposta il focus sulla lista
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


    def on_timer(self, event):
        """ Esegue la ricerca dopo il timeout del debounce."""

        """Esegue la ricerca dopo il timeout del debounce."""

        search_text = self.search_ctrl.GetValue().strip().lower()
        evt = SearchEvent(search_text=search_text)
        wx.PostEvent(self, evt)


    def search_from_name(self, search_text , event):
        """Gestisce la ricerca testuale."""

        # Se la casella di ricerca è vuota o contiene "tutti" o "all", ripristina la visualizzazione
        if search_text is None or search_text in ["Tutti", "tutti", "all", "Qualsiasi", "qualsiasi", "-", " ", ""]:
            self.on_reset(event)
        else:
            # Altrimenti, applica la ricerca
            self.load_cards(filters={"name": search_text})


    def on_search(self, event):
        """Gestisce la ricerca testuale."""

        search_text = self.search_ctrl.GetValue().strip().lower()
        self._apply_search_filter(search_text)
        self.set_focus_to_list()


    def on_search_text_change(self, event):
        """Gestisce la ricerca in tempo reale mentre l'utente digita."""

        search_text = self.search_ctrl.GetValue().strip().lower()
        if not search_text:
            self.load_cards()

        # Avvia il timer per il debounce (es. 300 ms)
        self.timer.Stop()  # Ferma il timer precedente
        self.timer.Start(500, oneShot=True)


    def on_search_event(self, event):
        """Gestisce l'evento di ricerca con debounce."""

        search_text = event.search_text
        self._apply_search_filter(search_text)
        self.set_focus_to_list()


    def _apply_search_filter(self, search_text):
        """Applica il filtro di ricerca alla lista delle carte."""

        if not search_text or search_text in ["tutti", "tutto", "all"]:
            # Se il campo di ricerca è vuoto o contiene "tutti", mostra tutte le carte
            self.load_cards()
        else:
            # Filtra le carte in base al nome
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
