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
from ..db import Card
from ..models import load_cards, session
from .builder.proto_views import BasicView, ListView
from .card_edit_dialog import CardEditDialog
from .filters_dialog import FilterDialog
from utyls import enu_glob as eg
from utyls import helper as hp
from utyls import logger as log
#import pdb

# Creazione di un evento personalizzato per la ricerca con debounce
SearchEvent, EVT_SEARCH_EVENT = wx.lib.newevent.NewEvent()



class CardCollectionFrame(ListView):
    """Finestra per gestire la collezione di carte."""

    def __init__(self, parent, controller, container, **kwargs):
        super().__init__(parent=parent, title="Collezione", container=container, **kwargs)
        self.mode = "collection"

        # Inizializza il timer per il debounce
        #self.timer = wx.Timer(self)                                 # Timer per il debounce
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)          # Aggiungi un gestore per il timer
        self.Bind(EVT_SEARCH_EVENT, self.on_search_event)           # Aggiungi un gestore per l'evento di ricerca


    def init_ui_elements(self):
        """Inizializza l'interfaccia utente utilizzando le funzioni helper."""

        # Impostazioni finestra principale
        #self.SetBackgroundColour(self.cm.get_color(AppColors.DEFAULT_BG))
        #self.panel.SetBackgroundColour(self.cm.get_color(AppColors.DEFAULT_BG))

        # Creazione degli elementi dell'interfaccia

        # Barra di ricerca e filtri
        search_sizer = self.widget_factory.create_sizer(wx.HORIZONTAL)
        self.search_ctrl = self.widget_factory.create_search_bar(
            self.panel,
            placeholder="Cerca per nome...",
            event_handler=self.on_search
        )
        self.search_ctrl.Bind(wx.EVT_TEXT, self.on_search_text_change)  # Aggiunto per la ricerca dinamica
        self.widget_factory.add_to_sizer(search_sizer, self.search_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        # Pulsante filtri avanzati
        self.btn_filters = self.widget_factory.create_button(
            self.panel,
            label="Filtri Avanzati",
            event_handler=self.on_show_filters
        )
        self.reset_focus_style(self.btn_filters)
        self.bind_focus_events(self.btn_filters)  # Collega gli eventi di focus
        self.widget_factory.add_to_sizer(search_sizer, self.btn_filters, flag=wx.LEFT | wx.RIGHT, border=5)

        # Aggiungo la barra di ricerca e i filtri al layout
        self.widget_factory.add_to_sizer(self.sizer, search_sizer, flag=wx.EXPAND | wx.ALL, border=10)

        # Lista delle carte
        self.card_list = self.widget_factory.create_list_ctrl(
            parent=self.panel,
            #color_manager=self.cm,
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

        # Collega gli eventi di focus alla lista
        #self.bind_focus_events(self.card_list)
        #self.card_list.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.on_item_focused)

        # Aggiungo la lista alla finestra
        self.widget_factory.add_to_sizer(self.sizer, self.card_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Pulsanti azione
        btn_panel = wx.Panel(self.panel)
        btn_sizer = self.widget_factory.create_sizer(wx.HORIZONTAL)

        # Creazione dei pulsanti
        buttons = [
            ("Aggiorna", self.on_reset),
            ("Aggiungi Carta", self.on_add_card),
            ("Modifica Carta", self.on_edit_card),
            ("Elimina Carta", self.on_delete_card),
            ("Chiudi", lambda e: self.Close())
        ]

        # Aggiungi i pulsanti al pannello
        for label, handler in buttons:
            btn = self.widget_factory.create_button(btn_panel, label=label, event_handler=handler)
            self.bind_focus_events(btn)  # Collega gli eventi di focus
            self.reset_focus_style(btn)
            self.widget_factory.add_to_sizer(btn_sizer, btn, flag=wx.CENTER | wx.ALL, border=10)

        #resetto i colori di tutti i pulsanti
        self.reset_focus_style_for_all_buttons(btn_sizer)

        # Aggiungo i pulsanti al pannello
        btn_panel.SetSizer(btn_sizer)
        self.widget_factory.add_to_sizer(self.sizer, btn_panel, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        # Separatore tra pulsanti e fondo finestra
        self.widget_factory.add_to_sizer(self.sizer, wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        # Carica le carte
        self.load_cards()

        # Imposta il colore di sfondo della riga selezionaata nella lista carte
        #self.card_list.SetBackgroundColour('blue')
        #self.card_list.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        #self.card_list.SetForegroundColour('white')

        # sposta il focus sulla lista
        self.set_focus_to_list()

        #aggiorna la lista
        self.card_list.Refresh()

        # Imposta il layout principale
        self.Layout()

        # Aggiungi eventi
        self.card_list.Bind(wx.EVT_LIST_COL_CLICK, self.on_column_click)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
        self.Bind(wx.EVT_CLOSE, self.on_close)


    def load_cards(self, filters=None):
        """Carica le carte utilizzando le funzioni helper sopra definite."""

        if not self.card_list:
            log.error("La lista delle carte non è stata inizializzata.")
            raise ValueError("La lista delle carte non è stata inizializzata.")

        load_cards(filters=filters, card_list=self.card_list)
        #self.parent.controller.collection_controller.load_collection(filters=filters, card_list=self.card_list)

        # Imposta il colore di sfondo predefinito per tutte le righe
        #self.reset_focus_style_for_card_list()
        self.cm.reset_all_styles(self.card_list)

        # colora la riga selezionata
        self.select_element(0)
        self.cm.apply_focus_style(self.card_list)
        #self.card_list.SetBackgroundColour('blue')
        #self.card_list.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        #self.card_list.SetForegroundColour('white')

        # Forza il ridisegno della lista
        self.card_list.Refresh()


    def _get_list_columns(self):
        """Definisce le colonne specifiche per la gestione della collezione."""
        return [
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


    def sort_cards(self, col):
        """Ordina le carte in base alla colonna selezionata."""

        # Ordina le carte in base alla colonna selezionata
        super().sort_cards(col)

        # sposta il focus sulla lista
        self.set_focus_to_list()

        # Forza il ridisegno della lista
        self.card_list.Refresh()


    def search_from_name(self, search_text , event):
        """Gestisce la ricerca testuale."""

        # Se la casella di ricerca è vuota o contiene "tutti" o "all", ripristina la visualizzazione
        if search_text is None or search_text in ["Tutti", "tutti", "all", "Qualsiasi", "qualsiasi", "-", " ", ""]:
            self.on_reset(event)
        else:
            # Altrimenti, applica la ricerca
            self.load_cards(filters={"name": search_text})


    def _apply_search_filter(self, search_text):
        """Applica il filtro di ricerca alla lista delle carte."""

        if not search_text or search_text in ["tutti", "tutto", "all"]:
            # Se il campo di ricerca è vuoto o contiene "tutti", mostra tutte le carte
            self.load_cards()
        else:
            # Filtra le carte in base al nome
            self.load_cards(filters={"name": search_text})


    #@@# sezione metodi collegati agli eventi

    def on_item_focused(self, event):
        """Gestisce l'evento di focus su una riga della lista."""

        # cattura l'indice della riga selezionata
        selected_item = event.GetIndex()

        # Resetta lo stile di tutte le righe
        #self.reset_focus_style_for_card_list(selected_item)

        # Imposta lo stile della riga selezionata
        self.select_element(selected_item)

        # Imposta lo stile della riga selezionata
        self.cm.apply_default_style(self.card_list)

        # Forza il ridisegno della lista
        self.card_list.Refresh()

        # forza il ridisegno della lista
        self.Layout()


    def on_item_activated(self, event):
        """Gestisce il doppio clic su una riga per modificare la carta."""
        selected = self.card_list.GetFirstSelected()
        if selected != -1:
            card_name = self.card_list.GetItemText(selected)
            self.on_edit_card(event)


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

        # Sposta il focus sulla prima carta della lista carte di questa finestra
        self.set_focus_to_list()


    def on_column_click(self, event):
        """Gestisce il clic sulle intestazioni delle colonne per ordinare la lista."""
        col = event.GetColumn()
        self.sort_cards(col)


    def on_key_down(self, event):
        """
                    Gestisce i tasti premuti .

        :param event: 
                        Evento di pressione di un tasto.

        Descrizione:
                    - La funzione gestisce la pressione dei tasti inoltrando l'evento al controller.
                    - Il metodo super è chiamato per garantire che l'evento venga gestito correttamente.
                    - Il metodo sfrutta la gestione del metodo della classe genitore coem base di partenza.
                    - PPer sovrascrivere completamente il comportamento è garantire una nuova ed indipendente 
                        gestione dell'evento è sufficente non chiamare il metodo super().

        """
        super().on_key_down(event)
        event.Skip()                    # Passa l'evento al prossimo handler (se presente, altrimenti lo cattura il sistema operativo)


    def on_timer(self, event):
        """ Esegue la ricerca dopo il timeout del debounce."""

        search_text = self.search_ctrl.GetValue().strip().lower()
        evt = SearchEvent(search_text=search_text)
        wx.PostEvent(self, evt)



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
