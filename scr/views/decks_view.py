"""

    decks_view.py

    Modulo per la finestra di gestione dei mazzi.

    path:
        scr/views/decks_view.py

    Note:
        Questo modulo contiene la definizione della finestra di gestione dei mazzi, che consente all'utente di visualizzare, creare, modificare, copiare, eliminare e visualizzare statistiche sui mazzi di carte di Hearthstone.
        Questo modulo utilizza la libreria wxPython per la creazione delle finestre di dialogo dell'interfaccia utente.

"""

# lib
import wx#, pyperclip
import wx.lib.newevent
from ..db import session, db_session, Card, DeckCard, Deck
from .proto_views import BasicView, ListView
from .deck_stats_dialog import DeckStatsDialog
import scr.views.builder.view_components as vc              # Componenti dell'interfaccia utente
from utyls import enu_glob as eg                    # Enumerazioni globali
from utyls import helper as hp                      # Funzioni helper
from utyls import logger as log                     # Modulo per la gestione dei log
#import pdb                                         # Modulo per il debug

# Creazione di un evento personalizzato per la ricerca con debounce
SearchEvent, EVT_SEARCH_EVENT = wx.lib.newevent.NewEvent()



#class DecksViewFrame(BasicView):
class DecksViewFrame(ListView):
    """ Finestra di gestione dei mazzi. """

    def __init__(self, parent=None, controller=None):
        title = "Gestione Mazzi"
        super().__init__(parent=parent, title=title, size=(800, 600))
        self.parent = parent
        self.controller = controller
        self.db_manager = self.parent.controller.db_manager
        #self.controller = self.parent.controller.decks_controller
        self.mode = "decks"

        # Timer per il debounce
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.Bind(EVT_SEARCH_EVENT, self.on_search_event)


    def init_ui_elements(self):
        """ Inizializza l'interfaccia utente utilizzando le funzioni helper. """

        # Creazione degli elementi dell'interfaccia

        # titolo della finestra
        lbl_title = wx.StaticText(self.panel, label="Elenco Mazzi")
        self.card_list = vc.create_list_ctrl(
            parent=self.panel,
            columns=[("Mazzo", 600), ("Classe", 500), ("Formato", 300), ("Carte Totali", 300)]  # 
        )

        # Collega gli eventi di focus alla lista
        #self.bind_focus_events(self.card_list)

        # Carichiamo i mazzi
        self.load_decks()

        # Barra di ricerca
        self.search_bar = vc.create_search_bar(
            self.panel,
            placeholder="Cerca mazzo...",
            event_handler=self.on_search
        )
        self.search_bar.Bind(wx.EVT_TEXT, self.on_search_text_change)  # Aggiunto per la ricerca dinamica

        # Pulsanti
        btn_add = vc.create_button(self.panel, label="Aggiungi Mazzo", event_handler=self.on_add_deck)
        btn_copy = vc.create_button(self.panel, label="Copia Mazzo", event_handler=self.on_copy_deck)
        btn_view = vc.create_button(self.panel, label="Visualizza Mazzo", event_handler=self.on_view_deck)
        btn_stats = vc.create_button(self.panel, label="Statistiche Mazzo", event_handler=self.on_view_stats)
        btn_update = vc.create_button(self.panel, label="Aggiorna Mazzo", event_handler=self.on_update_deck)
        btn_delete = vc.create_button(self.panel, label="Elimina Mazzo", event_handler=self.on_delete_deck)
        btn_collection = vc.create_button(self.panel, label="Collezione Carte", event_handler=self.on_view_collection)
        btn_exit = vc.create_button(self.panel, label="Chiudi", event_handler=self.on_close)

        # Layout principale
        main_sizer = vc.create_sizer(wx.VERTICAL)
        vc.add_to_sizer(main_sizer, lbl_title, flag=wx.CENTER | wx.TOP, border=10)
        vc.add_to_sizer(main_sizer, self.search_bar, flag=wx.EXPAND | wx.ALL, border=5)

        # Separatore tra barra di ricerca e lista dei mazzi
        vc.add_to_sizer(main_sizer, wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        # Aggiungi la lista dei mazzi al sizer
        vc.add_to_sizer(main_sizer, self.card_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Separatore tra lista dei mazzi e pulsanti
        vc.add_to_sizer(main_sizer, wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        # Layout pulsanti
        btn_sizer = wx.GridSizer(rows=4, cols=2, hgap=10, vgap=10)
        for btn in [btn_add, btn_copy, btn_view, btn_stats, btn_update, btn_delete, btn_collection, btn_exit]:
            self.bind_focus_events(btn)  # Collega gli eventi di focus
            btn_sizer.Add(btn, flag=wx.EXPAND | wx.ALL, border=5)

        #resetto i colori di tutti i pulsanti
        self.reset_focus_style_for_all_buttons(btn_sizer)

        # Aggiungi i pulsanti al sizer principale
        vc.add_to_sizer(main_sizer, btn_sizer, flag=wx.EXPAND | wx.ALL, border=10)

        # Separatore tra pulsanti e barra di stato
        vc.add_to_sizer(main_sizer, wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        # Imposta il sizer principale
        self.panel.SetSizer(main_sizer)

        # Barra di stato
        #self.status_bar = self.CreateStatusBar()
        #self.status_bar.SetStatusText("Pronto")

        # Imposta il focus sul search bar
        #self.search_bar.SetFocus()

        # Imposta il focus sul primo deck della lista delle carte
        self.select_and_focus_deck(self.card_list.GetItemText(0))
        #self.parent.controller.decks_controller.select_and_focus_deck(self, self.card_list.GetItemText(0))


        #aggiorna la lista
        #self.card_list.Refresh()

        # Imposta il layout principale
        #self.Layout()


    #def set_focus_to_list(self):
        """Imposta il focus sulla lista dei mazzi."""

        #controller = self.parent.controller.decks_controller
        #self.controller.set_focus_to_list(self)


    def load_decks(self):
        """ Carica i mazzi dal database. """

        # carichiamo i mazzi dal database usando db_session
        controller = self.parent.controller.decks_controller
        controller.load_decks(self.card_list)

        # Imposta il colore di sfondo predefinito per tutte le righe
        self.cm.reset_all_styles(self.card_list)

        # colora il mazzo selezionato nella lista
        self.parent.controller.decks_controller.select_list_element(self)


    def get_total_cards_in_deck(self, deck_name):
        """Calcola il numero totale di carte in un mazzo."""

        control = self.parent.controller.decks_controller
        return control.get_total_cards_in_deck(deck_name)


    def update_card_list(self):
        """ Aggiorna la lista dei mazzi. """

        controller = self.parent.controller.decks_controller
        controller.update_card_list(self.card_list)


    def update_status(self, message):
        """Aggiorna la barra di stato."""
        #self.status_bar.SetStatusText(message)
        pass


    def get_selected_deck(self):
        """Restituisce il mazzo selezionato nella lista."""

        controller = self.parent.controller.decks_controller
        #return controller.get_selected_deck(self)
        selection = self.card_list.GetFirstSelected()
        if selection != wx.NOT_FOUND:
            return self.card_list.GetItemText(selection)


    def select_and_focus_deck(self, deck_name):
        """
        Seleziona un mazzo nella lista e imposta il focus su di esso.

        :param frame: Il frame contenente la lista dei mazzi.
        :param deck_name: Il nome del mazzo da selezionare.
        """

        controller = self.parent.controller.decks_controller
        controller.select_and_focus_deck(self, deck_name)


    def _apply_search_filter(self, search_text):
        """Applica il filtro di ricerca alla lista dei mazzi."""

        #controller = self.parent.controller.decks_controller
        self.controller.apply_search_filter(self, search_text)

        # sposta il focus sul primo risultato ed evidezia la riga
        self.select_and_focus_deck(self.card_list.GetItemText(0))


    def on_timer(self, event):
        """Esegue la ricerca dopo il timeout del debounce."""

        search_text = self.search_bar.GetValue().strip().lower()
        evt = SearchEvent(search_text=search_text)
        wx.PostEvent(self, evt)


    def on_search_text_change(self, event):
        """Gestisce la ricerca in tempo reale mentre l'utente digita."""

        search_text = self.search_bar.GetValue().strip().lower()
        if not search_text:
            self.load_decks()  # Ricarica tutti i mazzi se la casella di ricerca è vuota

        # Avvia il timer per il debounce (es. 500 ms)
        self.timer.Stop()  # Ferma il timer precedente
        self.timer.Start(500, oneShot=True)


    def on_search_event(self, event):
        """Gestisce l'evento di ricerca con debounce."""

        search_text = event.search_text
        self._apply_search_filter(search_text)
        self.set_focus_to_list()


    def on_add_deck(self, event):
        """Aggiunge un mazzo tramite finestra di dialogo."""
 
        controller = self.parent.controller.decks_controller
        succ =  controller.question_for_add_deck(self)
        if succ != wx.ID_YES:
            wx.MessageBox("Operazione annullata.", "Annullato")
            return

        if controller.add_deck():
            self.parent.controller.decks_controller.select_last_deck(self)


    def on_copy_deck(self, event):
        """Copia il mazzo selezionato negli appunti."""

        #controller = self.parent.controller.decks_controller
        if self.controller.copy_deck(self):
            self.parent.controller.decks_controller.select_last_deck(self)


    def on_view_deck(self, event):
        """Mostra il mazzo selezionato in una finestra dettagliata."""

        deck_name = self.get_selected_deck()
        if deck_name:
            deck_content = self.controller.get_deck_details(deck_name)
            if deck_content:
                # Apri la finestra di visualizzazione del mazzo
                self.controller.run_deck_frame(parent=self, deck_name=deck_name)

            else:
                wx.MessageBox("Errore: Mazzo vuoto o non trovato.", "Errore")

        else:
            wx.MessageBox("Seleziona un mazzo prima di visualizzarlo.", "Errore")


    def on_update_deck(self, event):

        controller = self.parent.controller.decks_controller
        deck_name = self.get_selected_deck()
        if controller.upgrade_deck(deck_name):
                self.update_card_list()
                self.select_and_focus_deck(deck_name)  # Seleziona e mette a fuoco il mazzo                


    def on_view_stats(self, event):
        """Mostra le statistiche del mazzo selezionato."""

        deck_name = self.get_selected_deck()
        if deck_name:
            stats = self.db_manager.get_deck_statistics(deck_name)
            if stats:
                DeckStatsDialog(self, stats=stats).ShowModal()

            else:
                log.error(f"Impossibile calcolare le statistiche per il mazzo: {deck_name}")
                wx.MessageBox("Impossibile calcolare le statistiche per questo mazzo.", "Errore")

        else:
            log.error("Nessun mazzo selezionato.")
            wx.MessageBox("Seleziona un mazzo prima di visualizzare le statistiche.", "Errore")


    def on_view_collection(self, event):
        """Mostra la collezione delle carte."""
        app_controller = self.parent.controller
        app_controller.run_collection_frame(parent=self)


    def on_delete_deck(self, event):
        """ Elimina il mazzo selezionato. """

        controller = self.parent.controller.decks_controller
        deck_name = self.get_selected_deck()
        if deck_name:
            if wx.MessageBox(f"Sei sicuro di voler eliminare '{deck_name}'?", "Conferma", wx.YES_NO) == wx.YES:
                if controller.delete_deck(deck_name):
                    self.update_card_list()
                    controller.select_last_deck(self)
            else:
                log.info("Operazione annullata.")
                wx.MessageBox("Operazione annullata.", "Annullato")

        else:
            log.error("Nessun mazzo selezionato.")
            wx.MessageBox("Seleziona un mazzo prima di eliminarlo.", "Errore")


    def on_search(self, event):
        """Gestisce la ricerca testuale."""
        search_text = self.search_bar.GetValue().strip().lower()
        self._apply_search_filter(search_text)


    def last_on_search(self, event):
        """Filtra i mazzi in base al testo di ricerca."""

        # cerchiamo la parola richiesta dall'utente sia nei nomi dei mazzi sia nella classe
        search_text = self.search_bar.GetValue()
        self.card_list.DeleteAllItems()
        decks = session.query(Deck).filter(Deck.name.ilike(f"%{search_text}%") | Deck.player_class.ilike(f"%{search_text}%")).all()
        for deck in decks:
            Index = self.card_list.InsertItem(self.card_list.GetItemCount(), deck.name)
            self.card_list.SetItem(Index, 1, deck.player_class)
            self.card_list.SetItem(Index, 2, deck.game_format)


    def on_close(self, event):
        """Chiude l'applicazione."""
        self.parent.Show()  # Mostra la finestra principale
        self.Close()        # Chiude la finestra di gestione dei mazzi



#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
