"""
    deck_view.py

    Modulo per la finestra di dialogo della gestione del mazzo.

    descrizione:
        Questo modulo contiene la classe DeckViewFrame, che rappresenta la finestra di dialogo per la gestione delle carte di un mazzo.
        La finestra di dialogo include una lista di carte, una barra di ricerca, filtri avanzati e pulsanti per aggiungere, modificare e rimuovere carte.

    path:
        scr/views/deck_view.py

"""

# lib
import wx#, pyperclip
import wx.lib.newevent
from ..db import Card, session
from .builder.proto_views import BasicView, ListView
from .card_edit_dialog import CardEditDialog
from .builder.color_system import AppColors
from utyls import enu_glob as eg
from utyls import helper as hp
from utyls import logger as log

# Creazione di un evento personalizzato per la ricerca con debounce
SearchEvent, EVT_SEARCH_EVENT = wx.lib.newevent.NewEvent()



class DeckViewFrame(ListView):
    """Finestra per gestire le carte di un mazzo."""

    def __init__(self, parent=None, controller=None, container=None, deck_name="", **kwargs):
        super().__init__(parent=parent, title=f"Mazzo: {deck_name}", deck_name=deck_name, container=container, **kwargs)
        self.mode = "deck"  # Modalità "deck" per gestire i mazzi
        self.deck_name = deck_name
        self.deck_content = None

        # Se il mazzo non esiste, assembla il mazzo richeisto
        if not self.deck_content:
            self.deck_content = self.controller.db_manager.get_deck(deck_name)  # Carica il mazzo
            # aggiorna la lista delle carte
            self.load_cards()
            self.set_focus_to_list()


        # Timer per il debounce
        #self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.Bind(EVT_SEARCH_EVENT, self.on_search_event)


    def init_ui_elements(self):
        """Inizializza l'interfaccia utente utilizzando le funzioni helper."""

        # Impostazioni finestra principale

        # coloro il bg del pannello 
        self.SetBackgroundColour(self.cm.get_color(AppColors.DEFAULT_BG))
        self.panel.SetBackgroundColour(self.cm.get_color(AppColors.DEFAULT_BG))

        # Creazione degli elementi dell'interfaccia
        search_sizer = self.widget_factory.create_sizer(wx.HORIZONTAL)
        self.search_ctrl = self.widget_factory.create_search_bar(
            self.panel,
            placeholder="Cerca per nome...",
            event_handler=self.on_search
        )
        self.search_ctrl.Bind(wx.EVT_TEXT, self.on_search_text_change)
        self.widget_factory.add_to_sizer(search_sizer, self.search_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        # Aggiungo la barra di ricerca al layout
        self.widget_factory.add_to_sizer(self.sizer, search_sizer, flag=wx.EXPAND | wx.ALL, border=10)

        # Lista delle carte
        self.card_list = self.widget_factory.create_list_ctrl(
            parent=self.panel,
            columns=[
                ("Nome", 250),
                ("Mana", 50),
                ("Quantità", 50),
                ("Tipo", 200),
                ("Tipo Magia", 200),
                ("Sottotipo", 200),
                ("Attacco", 50),
                ("Vita", 50),
                ("Durabilità", 50),
                ("Rarità", 120),
                ("Espansione", 500)
            ]
        )

        # Collega gli eventi di focus alla lista
        self.bind_focus_events(self.card_list)

        # Applica lo stile predefinito alla lista
        #self.cm.apply_default_style(self.card_list)

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

        for label, handler in buttons:
            btn = self.widget_factory.create_button(btn_panel, label=label, event_handler=handler)
            self.bind_focus_events(btn)  # Collega gli eventi di focus
            self.widget_factory.add_to_sizer(btn_sizer, btn, flag=wx.CENTER | wx.ALL, border=10)

        # resetto i colori dei pulsanti
        self.reset_focus_style_for_all_buttons(btn_sizer)

        # Aggiungo i pulsanti al pannello
        btn_panel.SetSizer(btn_sizer)
        self.widget_factory.add_to_sizer(self.sizer, btn_panel, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        # Separatore tra pulsanti e fondo finestra
        self.widget_factory.add_to_sizer(self.sizer, wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        # Carica le carte SOLO se il mazzo è stato caricato correttamente
        if hasattr(self, "deck_content") and self.deck_content:
            #self.load_cards()
            self.refresh_card_list()
            self.set_focus_to_list()
            self.select_element(0)
            #self.cm.apply_selection_style_to_list(self.card_list, 0)  # Applica lo stile di selezione alla prima riga
            #self.cm.apply_focus_style(self.card_list)
            #self.cm.apply_selection_style_to_list(self.card_list)

            # Aggiorna la finestra
            #self.card_list.Refresh()

        # forza la riscrittura del layout
        #self.Layout()

        # Aggiungo eventi
        self.card_list.Bind(wx.EVT_LIST_COL_CLICK, self.on_column_click)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)


    def _get_list_columns(self):
        """Definisce le colonne specifiche per la gestione dei mazzi."""
        return [
            ("Nome", 250),
            ("Mana", 50),
            ("Quantità", 50),
            ("Tipo", 200),
            ("Tipo Magia", 200),
            ("Sottotipo", 200),
            ("Attacco", 50),
            ("Vita", 50),
            ("Durabilità", 50),
            ("Rarità", 120),
            ("Espansione", 500)
        ]

    def sort_cards(self, col):
        """Ordina le carte in base alla colonna selezionata, con logica specifica per i mazzi."""
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
        elif col == 2:  # Colonna "Quantità" (numerica)
            items.sort(key=lambda x: safe_int(x[col]))
        else:  # Altre colonne (testuali)
            items.sort(key=lambda x: x[col])

        self.card_list.DeleteAllItems()
        for item in items:
            self.card_list.Append(item)

    def on_item_activated(self, event):
        """Gestisce il doppio clic su una riga per modificare la carta."""
        selected = self.card_list.GetFirstSelected()
        if selected != -1:
            card_name = self.card_list.GetItemText(selected)
            self._edit_card_in_deck(card_name)


    #@@# sezione metodi collegati agli eventi

    def on_timer(self, event):
        """Esegue la ricerca dopo il timeout del debounce."""

        search_text = self.search_ctrl.GetValue().strip().lower()
        evt = SearchEvent(search_text=search_text)
        wx.PostEvent(self, evt)


    def on_search_text_change(self, event):
        """Gestisce la ricerca in tempo reale mentre l'utente digita."""

        search_text = self.search_ctrl.GetValue().strip().lower()
        if not search_text:
            # ricarica le carte del mazzo
            self.load_cards()

        # Avvia il timer per il debounce (es. 300 ms)
        self.timer.Stop()  # Ferma il timer precedente
        self.timer.Start(500, oneShot=True)


    def on_search_event(self, event):
        """Gestisce l'evento di ricerca con debounce."""
        search_text = event.search_text
        self._apply_search_filter(search_text)
        self.set_focus_to_list()


    def _add_card_to_list(self, card_data):
        """Aggiunge una singola carta alla lista."""

        self.card_list.Append([
            card_data.get("name", "-"),
            str(card_data.get("mana_cost", "-")) if card_data.get("mana_cost") is not None else "-",
            str(card_data.get("quantity", "-")) if card_data.get("quantity") else "-",
            card_data.get("card_type", "-") if card_data.get("card_type") else "-",
            card_data.get("spell_type", "-") if card_data.get("spell_type") else "-",
            card_data.get("card_subtype", "-") if card_data.get("card_subtype") else "-",
            str(card_data.get("attack", "-")) if card_data.get("attack") is not None else "-",
            str(card_data.get("health", "-")) if card_data.get("health") is not None else "-",
            str(card_data.get("durability", "-")) if card_data.get("durability") is not None else "-",
            card_data.get("rarity", "-") if card_data.get("rarity") else "-",
            card_data.get("expansion", "-") if card_data.get("expansion") else "-"
        ])


    def load_cards(self, filters=None):
        """Carica le carte nel mazzo, applicando eventuali filtri."""

        # Verifica che il mazzo sia stato caricato correttamente
        if not hasattr(self, "deck_content") or not self.deck_content:
            log.error("Mazzo non caricato correttamente.")
            raise ValueError("Mazzo non caricato correttamente.")
            return

        # Verifica che la card_list sia inizializzata
        if self.card_list is None:
            log.error("card_list non è stata inizializzata.")
            raise ValueError("card_list non è stata inizializzata.")
            return

        # Pulisce la lista delle carte
        self.card_list.DeleteAllItems()

        # Recupera le carte dal mazzo
        cards = self.deck_content.get("cards", [])
        if not cards:
            log.warning("Nessuna carta trovata nel mazzo.")
            return

        # Filtra le carte in base ai criteri specificati
        filtered_cards = []
        for card_data in cards:
            if filters and "name" in filters:
                if filters["name"].lower() not in card_data["name"].lower():
                    continue  # Salta le carte che non corrispondono al filtro

            filtered_cards.append(card_data)

        # Aggiunge le carte filtrate alla lista
        for card_data in filtered_cards:
            self._add_card_to_list(card_data)

        # Applica lo stile predefinito a tutte le righe
        self.cm.apply_default_style(self.card_list)

        # Seleziona la prima carta, se presente
        if self.card_list.GetItemCount() > 0:
            self.cm.apply_selection_style_to_list_item(self.card_list, 0)

        #aggiorna la visualizzazione della card_list
        self.card_list.Refresh()


    def refresh_card_list(self):
        """Aggiorna la lista delle carte con i dati più recenti dal database."""

        log.debug("Aggiornamento della lista delle carte...")        

        # Ricarica il contenuto del mazzo dal database
        self.deck_content = self.parent.controller.db_manager.get_deck(self.deck_name)

         # Ricarica le carte nella lista
        self.load_cards()
        self.card_list.Refresh()
        log.debug("Lista delle carte aggiornata.")


    def _apply_search_filter(self, search_text):
        """Applica il filtro di ricerca alla lista delle carte."""

        if not search_text or search_text in ["tutti", "tutto", "all"]:
            # Se il campo di ricerca è vuoto o contiene "tutti", mostra tutte le carte
            self.load_cards()
        else:
            # Filtra le carte in base al nome
            self.load_cards(filters={"name": search_text})


    #@@# sezione metodi collegati agli eventi

    def on_search(self, event):
        """Gestisce la ricerca testuale."""

        search_text = self.search_ctrl.GetValue().strip().lower()
        self._apply_search_filter(search_text)
        self.set_focus_to_list()


    def on_reset(self, event):
        """Ripristina la visualizzazione originale."""

        if hasattr(self, "search_ctrl"):
            self.search_ctrl.SetValue("")  # Resetta la barra di ricerca
            self.load_cards()  # Ricarica la lista delle carte senza filtri

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
                self._add_card_to_deck(card_name)

        dlg.Destroy()


    def on_edit_card(self, event):
        """Modifica la carta selezionata."""

        selected = self.card_list.GetFirstSelected()
        if selected != -1:
            card_name = self.card_list.GetItemText(selected)
            self._edit_card_in_deck(card_name)

        else:
            wx.MessageBox("Seleziona una carta da modificare.", "Errore")


    def on_delete_card(self, event):
        """Elimina la carta selezionata."""

        selected = self.card_list.GetFirstSelected()
        if selected != -1:
            card_name = self.card_list.GetItemText(selected)
            if wx.MessageBox(f"Eliminare la carta '{card_name}'?", "Conferma", wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
                self._delete_card_from_deck(card_name)

        else:
            wx.MessageBox("Seleziona una carta da eliminare.", "Errore")


    def on_column_click(self, event):
        """Ordina le carte in base alla colonna selezionata."""

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


    def on_close(self, event):
        """Chiude la finestra."""
        self.parent.Show()
        self.Close()


    #@@# sezione metodi ausigliari della classe

    def _add_card_to_deck(self, card_name):
        """Aggiunge una nuova carta al mazzo."""

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


    def _edit_card_in_deck(self, card_name):
        """Modifica la carta selezionata."""

        card = session.query(Card).filter_by(name=card_name).first()
        if card:
            dlg = CardEditDialog(self, card)
            if dlg.ShowModal() == wx.ID_OK:
                self.load_cards()
                self.refresh_card_list()
                wx.MessageBox(f"Carta '{card_name}' modificata con successo.", "Successo")
                self.select_card_by_name(card_name)

            dlg.Destroy()

        else:
            wx.MessageBox("Carta non trovata nel database.", "Errore")


    def _delete_card_from_deck(self, card_name):
        """Elimina la carta selezionata."""

        self.deck_content["cards"] = [
            card_data for card_data in self.deck_content["cards"]
            if card_data["name"] != card_name
        ]

        self.load_cards()
        wx.MessageBox(f"Carta '{card_name}' eliminata dal mazzo.", "Successo")


    def _sort_items(self, items, col):
        """Ordina gli elementi in base alla colonna selezionata."""

        def safe_int(value):
            try:
                return int(value)

            except ValueError:
                return float('inf') if value == "-" else value

        if col == 1:  # Colonna "Mana" (numerica)
            items.sort(key=lambda x: safe_int(x[col]))

        else:  # Altre colonne (testuali)
            items.sort(key=lambda x: x[col])


    def sort_cards(self, col):
        """Ordina le carte in base alla colonna selezionata."""

        items = []
        for i in range(self.card_list.GetItemCount()):
            item = [self.card_list.GetItemText(i, c) for c in range(self.card_list.GetColumnCount())]
            items.append(item)

        self._sort_items(items, col)

        self.card_list.DeleteAllItems()
        for item in items:
            self.card_list.Append(item)

        # Applica lo stile predefinito a tutte le righe
        self.cm.apply_default_style(self.card_list)

        # Seleziona la prima carta, se presente
        if self.card_list.GetItemCount() > 0:
            self.cm.apply_selection_style_to_list_item(self.card_list, 0)

        self.card_list.Refresh()





#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
