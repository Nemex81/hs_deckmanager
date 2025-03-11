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
from ..db import Deck
from .builder.proto_views import BasicView, ListView
from .deck_stats_dialog import DeckStatsDialog
import scr.views.builder.view_components as vc              # Componenti dell'interfaccia utente
from utyls import enu_glob as eg                            # Enumerazioni globali
from utyls import helper as hp                              # Funzioni helper
from utyls import logger as log                             # Modulo per la gestione dei log
#import pdb                                                 # Modulo per il debug

# Creazione di un evento personalizzato per la ricerca con debounce
SearchEvent, EVT_SEARCH_EVENT = wx.lib.newevent.NewEvent()



class DecksViewFrame(ListView):
    """ Finestra di gestione dei mazzi. """

    def __init__(self, parent=None, controller=None, container=None, **kwargs):
        super().__init__(parent=parent, title="Gestione Mazzi", size=(800, 600), container=container, **kwargs)
        self.mode = "decks"

        # Timer per il debounce
        #self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.Bind(EVT_SEARCH_EVENT, self.on_search_event)
        #self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)


    #@@# metodi ausigliari della classe

    def init_ui_elements(self):
        """Inizializza gli elementi dell'interfaccia utente."""
        super().init_ui_elements()

        # Aggiungi pulsanti specifici per la gestione dei mazzi
        btn_add = self.widget_factory.create_button(
            parent=self.panel,
            label="Aggiungi Mazzo",
            event_handler=self.on_add_deck
        )

        btn_copy = self.widget_factory.create_button(
            parent=self.panel,
            label="Copia Mazzo",
            event_handler=self.on_copy_deck
        )

        btn_view = self.widget_factory.create_button(
            parent=self.panel,
            label="Visualizza Mazzo",
            event_handler=self.on_view_deck
        )

        btn_stats = self.widget_factory.create_button(
            parent=self.panel,
            label="Statistiche Mazzo",
            event_handler=self.on_view_stats
        )

        btn_update = self.widget_factory.create_button(
            parent=self.panel,
            label="Aggiorna Mazzo",
            event_handler=self.on_update_deck
        )

        btn_delete = self.widget_factory.create_button(
            parent=self.panel,
            label="Elimina Mazzo",
            event_handler=self.on_delete_deck
        )

        btn_collection = self.widget_factory.create_button(
            parent=self.panel,
            label="Collezione Carte",
            event_handler=self.on_view_collection
        )

        btn_exit = self.widget_factory.create_button(
            parent=self.panel,
            label="Chiudi",
            event_handler=self.on_close
        )

        # Layout pulsanti
        btn_sizer = wx.GridSizer(rows=4, cols=2, hgap=10, vgap=10)
        for btn in [btn_add, btn_copy, btn_view, btn_stats, btn_update, btn_delete, btn_collection, btn_exit]:
            self.bind_focus_events(btn)  # Collega gli eventi di focus
            btn_sizer.Add(btn, flag=wx.EXPAND | wx.ALL, border=5)

        # Resetta i colori di tutti i pulsanti
        self.reset_focus_style_for_all_buttons(btn_sizer)

        # Aggiungi i pulsanti al layout principale
        self.sizer.Add(btn_sizer, flag=wx.EXPAND | wx.ALL, border=10)

        # Carica i mazzi
        self.load_decks()

        # Imposta il focus sulla lista
        self.set_focus_to_list()


    def last_init_ui_elements(self):
        """ Inizializza l'interfaccia utente utilizzando le funzioni helper. """

        # Creazione degli elementi dell'interfaccia

        # titolo della finestra
        lbl_title = wx.StaticText(self.panel, label="Elenco Mazzi")
        self.card_list = self.widget_factory.create_list_ctrl(
            parent=self.panel,
            columns=[("Mazzo", 600), ("Classe", 500), ("Formato", 300), ("Carte Totali", 300)]  # 
        )
        self.color_manager.apply_theme_to_window(self.card_list)  # Applica il tema alla lista
        self.card_list.Bind(wx.EVT_LIST_COL_CLICK, self.on_column_click)  # Ordina la lista per colonna
        self.card_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item_activated)  # Doppio clic su un mazzo

        # Carichiamo i mazzi
        self.load_decks()

        # Barra di ricerca
        self.search_ctrl = self.widget_factory.create_search_bar(
            parent=self.panel,
            placeholder="Cerca mazzo...",
            event_handler=self.on_search
        )
        self.search_ctrl.Bind(wx.EVT_TEXT, self.on_search_text_change)  # Aggiunto per la ricerca dinamica

        # Pulsanti

        btn_add = self.widget_factory.create_button(
            parent=self.panel, 
            label="Aggiungi Mazzo", 
            event_handler=self.on_add_deck
        )

        btn_copy = self.widget_factory.create_button(
            parent=self.panel, 
            label="Copia Mazzo", 
            event_handler=self.on_copy_deck
        )

        btn_view = self.widget_factory.create_button(
            parent=self.panel, 
            label="Visualizza Mazzo",
            event_handler=self.on_view_deck
        )   

        btn_stats = self.widget_factory.create_button(
            parent=self.panel, 
            label="Statistiche Mazzo", 
            event_handler=self.on_view_stats
        )

        btn_update = self.widget_factory.create_button(
            parent=self.panel, 
            label="Aggiorna Mazzo", 
            event_handler=self.on_update_deck
        )

        btn_delete = self.widget_factory.create_button(
            parent=self.panel,
            label="Elimina Mazzo",
            event_handler=self.on_delete_deck
        )

        btn_collection = self.widget_factory.create_button(
            parent=self.panel, 
            label="Collezione Carte", 
            event_handler=self.on_view_collection
        )

        btn_exit = self.widget_factory.create_button(
            parent=self.panel, 
            label="Chiudi", 
            event_handler=self.on_close
        )

        # Layout principale
        main_sizer = self.widget_factory.create_sizer(wx.VERTICAL)
        self.widget_factory.add_to_sizer(main_sizer, lbl_title, flag=wx.CENTER | wx.TOP, border=10)
        self.widget_factory.add_to_sizer(main_sizer, self.search_ctrl, flag=wx.EXPAND | wx.ALL, border=5)

        # Separatore tra barra di ricerca e lista dei mazzi
        self.widget_factory.add_to_sizer(main_sizer, wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        # Aggiungi la lista dei mazzi al sizer
        self.widget_factory.add_to_sizer(main_sizer, self.card_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Separatore tra lista dei mazzi e pulsanti
        self.widget_factory.add_to_sizer(main_sizer, wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        # Layout pulsanti
        btn_sizer = wx.GridSizer(rows=4, cols=2, hgap=10, vgap=10)
        for btn in [btn_add, btn_copy, btn_view, btn_stats, btn_update, btn_delete, btn_collection, btn_exit]:
            self.bind_focus_events(btn)  # Collega gli eventi di focus
            btn_sizer.Add(btn, flag=wx.EXPAND | wx.ALL, border=5)

        #resetto i colori di tutti i pulsanti
        self.reset_focus_style_for_all_buttons(btn_sizer)

        # Aggiungi i pulsanti al sizer principale
        self.widget_factory.add_to_sizer(main_sizer, btn_sizer, flag=wx.EXPAND | wx.ALL, border=10)

        # Separatore tra pulsanti e barra di stato
        self.widget_factory.add_to_sizer(main_sizer, wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        # Imposta il sizer principale
        self.panel.SetSizer(main_sizer)

        # Barra di stato
        #self.status_bar = self.CreateStatusBar()
        #self.status_bar.SetStatusText("Pronto")

        # Imposta il focus sul search bar
        #self.search_ctrl.SetFocus()

        #self.card_list.Bind(wx.EVT_LIST_COL_CLICK, self.on_column_click)
        self.controller.select_and_focus_deck(self, self.card_list.GetItemText(0))


        #aggiorna la lista
        #self.card_list.Refresh()

        # Imposta il layout principale
        #self.Layout()


    def load_decks(self):
        """ Carica i mazzi dal database. """

        # carichiamo i mazzi dal database usando db_session
        #controller = self.parent.controller.decks_controller
        if not self.controller.load_decks(self.card_list):
            wx.MessageBox("Errore durante il caricamento dei mazzi.", "Errore")
            return

        # colora il mazzo selezionato nella lista
        self.controller.select_list_element(self)


    def update_status(self, message):
        """Aggiorna la barra di stato."""
        #self.status_bar.SetStatusText(message)
        pass


    def _get_list_columns(self):
        """Definisce le colonne specifiche per la gestione dei mazzi."""
        return [
            ("Mazzo", 600),
            ("Classe", 500),
            ("Formato", 300),
            ("Carte Totali", 300)
        ]

    def sort_cards(self, col):
        """Ordina i mazzi in base alla colonna selezionata, con logica specifica."""
        log.debug(f"Ordinamento per colonna: {col}")

        items = []
        for i in range(self.card_list.GetItemCount()):
            item = [self.card_list.GetItemText(i, c) for c in range(self.card_list.GetColumnCount())]
            items.append(item)


        def safe_int(value):
            try:
                return int(value)
            except ValueError:
                return float('inf') if value == "-" else value

        if col == 3:  # Colonna "Carte Totali" (numerica)
            items.sort(key=lambda x: safe_int(x[col]))
        else:  # Altre colonne (testuali)
            items.sort(key=lambda x: x[col])

        self.card_list.DeleteAllItems()
        for item in items:
            self.card_list.Append(item)

        # Applica lo stile predefinito a tutte le righe
        self.cm.apply_default_style(self.card_list)

        # Seleziona la prima riga, se presente
        if self.card_list.GetItemCount() > 0:
            self.cm.apply_selection_style_to_list_item(self.card_list, 0)

        # Aggiorna la visualizzazione della lista
        self.card_list.Refresh()


    def apply_search_filter(self, search_text):
        """Applica un filtro di ricerca alla lista dei mazzi."""
        if not search_text or search_text in ["tutti", "tutto", "all"]:
            self.load_decks()  # Ricarica tutti i mazzi se la casella di ricerca è vuota
        else:
            # Filtra i mazzi in base al nome
            items = []
            for i in range(self.card_list.GetItemCount()):
                item = [self.card_list.GetItemText(i, c) for c in range(self.card_list.GetColumnCount())]
                if search_text.lower() in item[0].lower():  # Filtra per nome del mazzo (colonna 0)
                    items.append(item)

            self.card_list.DeleteAllItems()
            for item in items:
                self.card_list.Append(item)


        #@@# sezione metodi collegati agli eventi

    def on_key_down(self, event):
        super().on_key_down(event)      # Chiamata al metodo della classe genitore


    def on_column_click(self, event):
        """Gestisce il click su una colonna per ordinare la lista."""
        col = event.GetColumn()
        self.sort_cards(col)


    def on_item_activated(self, event):
        """Gestisce il doppio clic su una riga per visualizzare il mazzo."""
        selected = self.card_list.GetFirstSelected()
        if selected != -1:
            deck_name = self.card_list.GetItemText(selected)
            self.on_view_deck(event)


    def on_timer(self, event):
        """Esegue la ricerca dopo il timeout del debounce."""

        search_text = self.search_ctrl.GetValue().strip().lower()
        evt = SearchEvent(search_text=search_text)
        wx.PostEvent(self, evt)


    def on_search_text_change(self, event):
        """Gestisce la ricerca in tempo reale mentre l'utente digita."""

        search_text = self.search_ctrl.GetValue().strip().lower()
        if not search_text:
            # ripulisci la list aprim adi ricaricare
            self.card_list.DeleteAllItems()
            self.load_decks()  # Ricarica tutti i mazzi se la casella di ricerca è vuota

        # Avvia il timer per il debounce (es. 500 ms)
        self.timer.Stop()  # Ferma il timer precedente
        self.timer.Start(500, oneShot=True)


    def on_search_event(self, event):
        """Gestisce l'evento di ricerca con debounce."""

        search_text = event.search_text
        self.controller.apply_search_decks_filter(frame=self, search_text=search_text)
        self.set_focus_to_list()


    def on_add_deck(self, event):
        """Aggiunge un mazzo tramite finestra di dialogo."""
 
        succ =  self.controller.question_for_add_deck(self)
        if succ != wx.ID_YES:
            wx.MessageBox("Operazione annullata.", "Annullato")
            return

        if self.controller.add_deck():
            self.controller.update_decks_list(self.card_list)
            self.controller.select_last_deck(self)
            wx.MessageBox("Mazzo aggiunto con successo.", "Successo")
        else:
            wx.messageBox("Errore durante l'aggiunta del mazzo.", "Errore")


    def on_copy_deck(self, event):
        """Copia il mazzo selezionato negli appunti."""

        #controller = self.parent.controller.decks_controller
        if self.controller.copy_deck(self):
            self.parent.controller.decks_controller.select_last_deck(self)


    def on_view_deck(self, event):
        """Mostra il mazzo selezionato in una finestra dettagliata."""

        deck_name = self.controller.get_selected_deck(self.card_list)
        if deck_name:
            deck_content = self.controller.get_deck_details(deck_name)
            if deck_content:
                # Apri la finestra di visualizzazione del mazzo
                self.win_controller.create_deck_window(parent=self, deck_name=deck_name)

            else:
                wx.MessageBox("Errore: Mazzo vuoto o non trovato.", "Errore")

        else:
            wx.MessageBox("Seleziona un mazzo prima di visualizzarlo.", "Errore")


    def on_update_deck(self, event):
        """ Aggiorna il mazzo selezionato. """

        deck_name = self.controller.get_selected_deck(self.card_list)
        if self.controller.upgrade_deck(deck_name):
                self.controller.update_decks_list(self.card_list)
                self.controller.select_and_focus_deck(frame=self, deck_name=deck_name)  # Seleziona e mette a fuoco il mazzo                


    def on_view_stats(self, event):
        """Mostra le statistiche del mazzo selezionato."""

        deck_name = self.controller.get_selected_deck(self.card_list)
        if deck_name:
            stats = self.controller.get_deck_statistics(deck_name)
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
        self.win_controller.create_collection_window(parent=self)


    def on_delete_deck(self, event):
        """ Elimina il mazzo selezionato. """

        #controller = self.parent.controller.decks_controller
        deck_name = self.controller.get_selected_deck(self.card_list)
        if deck_name:
            if wx.MessageBox(f"Sei sicuro di voler eliminare '{deck_name}'?", "Conferma", wx.YES_NO) == wx.YES:
                if self.controller.delete_deck(frame=self, deck_name=deck_name):
                    self.controller.update_decks_list(self.card_list)
                    self.controller.select_last_deck(self)
                    wx.MessageBox(f"Mazzo '{deck_name}' eliminato con successo.", "Successo")
                    
            else:
                log.info("Operazione annullata.")
                wx.MessageBox("Operazione annullata.", "Annullato")

        else:
            log.error("Nessun mazzo selezionato.")
            wx.MessageBox("Seleziona un mazzo prima di eliminarlo.", "Errore")


    def on_search(self, event):
        """Gestisce la ricerca testuale."""
        search_text = self.search_ctrl.GetValue().strip().lower()
        #self._apply_search_filter(search_text)
        self.apply_search_filter(search_text)


    def on_close(self, event):
        """Chiude l'applicazione."""
        self.parent.Show()  # Mostra la finestra principale
        self.Close()        # Chiude la finestra di gestione dei mazzi



#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
