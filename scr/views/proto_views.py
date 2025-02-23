"""
        Modulo per la gestione dei prototipi delle finestre dell'interfaccia utente.

        path:
            ./scr/views/proto_views.py

    Descrizione:
        Questo modulo contiene classi base per la creazione di finestre di dialogo e componenti dell'interfaccia utente.
        La classe BasicView fornisce un'interfaccia comune per le finestre di dialogo, mentre le classi derivate come 
        La classe BasicDialog fornisce un'interfaccia comune per le finestre di dialogo, mentre le classi derivate come
        SingleCardView e ListView forniscono funzionalità specifiche per la gestione di carte e liste.

"""

# Lib
import wx
import wx.lib.newevent
from abc import ABC, abstractmethod
from sqlalchemy.exc import SQLAlchemyError
from ..db import session, Card, DeckCard, Deck
from ..models import load_cards
from .view_components import create_button, create_separator, add_to_sizer, create_list_ctrl, create_search_bar, create_sizer
from utyls.enu_glob import EnuCardType, EnuSpellSubType, EnuPetSubType, EnuRarity, EnuExpansion, EnuSpellType, EnuHero
from utyls import helper as hp
from utyls.enu_glob import EnuCardType, EnuSpellSubType, EnuPetSubType, EnuRarity, EnuExpansion, EnuSpellType
from utyls import logger as log

# Evento personalizzato per la ricerca in tempo reale
SearchEvent, EVT_SEARCH_EVENT = wx.lib.newevent.NewEvent()

class BasicDialog(wx.Dialog):
    """
        Classe base per le finestre di dialogo dell'interfaccia utente.
    """

    def __init__(self, parent, title, size=(500, 400), **kwargs):
        super().__init__(parent=parent, title=title, size=size)
        self.parent = parent
        self.init_ui()
        self.Centre()
        self.Show()

    def init_ui(self):
        """Inizializza l'interfaccia utente con le impostazioni comuni a tutte le finestre."""

        self.panel = wx.Panel(self)                     # Crea un pannello
        self.sizer = wx.BoxSizer(wx.VERTICAL)           # Crea un sizer verticale
        self.Center()                                   # Centra la finestra
        self.SetBackgroundColour('yellow')              # Imposta il colore di sfondo
        self.init_ui_elements()                         # Inizializza gli elementi dell'interfaccia utente

    @abstractmethod
    def init_ui_elements(self, *args, **kwargs):
        """Inizializza gli elementi dell'interfaccia utente."""
        pass

    def on_close(self, event):
        """Chiude la finestra."""
        self.Close()



class BasicView(wx.Frame):
    """
        Classe base per le finestre principali dell'interfaccia utente.
    """
    
    def __init__(self, parent, title, size=(500, 400)):
        super().__init__(parent=parent, title=title, size=size)
        self.parent = parent          # Finestra genitore
        self.controller = None        # Controller per l'interfaccia
        self.db_manager = None        # Gestore del database
        self.Maximize()               # Massimizza la finestra
        self.Centre()                 # Centra la finestra
        self.init_ui()                # Inizializza l'interfaccia utente
        self.Show()


    def set_controller(self, controller=None):
        """ Imposta il controller per l'interfaccia. """
        self.controller = controller

    def set_db_manager(self, db_manager=None):
        """ Imposta il controller del database. """
        self.db_manager = db_manager


    def init_ui(self):
        """Inizializza l'interfaccia utente con le impostazioni comuni a tutte le finestre."""

        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.sizer)

        # imposta i colori di spondo giallo per finestra e pannello
        self.BackgroundColour = 'black'
        self.panel.BackgroundColour = 'black'

        # imposta il font per il titolo
        font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        title = wx.StaticText(self.panel, label=self.Title)
        title.SetFont(font)
        self.init_ui_elements()

    @abstractmethod
    def init_ui_elements(self, *args, **kwargs):
        """Inizializza gli elementi dell'interfaccia utente."""
        pass

    def Close(self):
        """Chiude la finestra."""
        if self.parent:
            self.parent.Show()

        self.Destroy()

    def on_close(self, event):
        """Chiude la finestra."""
        self.Close()



class SingleCardView(BasicDialog):
    """
        Classe madre per le finestre di dialogo che gestiscono form per le carte.
        Gestisce i componenti grafici comuni tra CardEditDialog e FilterDialog.
    """

    def __init__(self, parent, title, size=(400, 500)):
        self.controls = {}  # Dizionario per memorizzare i controlli UI
        super().__init__(parent, title=title, size=size)


    def init_ui_elements(self):
        """Inizializza i componenti grafici comuni."""

        # Definizione dei controlli UI comuni
        common_controls = [
            ("nome", wx.TextCtrl),
            ("costo_mana", wx.ComboBox, {"choices": ["Qualsiasi"] + [str(i) for i in range(0, 21)], "style": wx.CB_READONLY}),
            ("tipo", wx.ComboBox, {"choices": ["Tutti"] + [t.value for t in EnuCardType], "style": wx.CB_READONLY}),
            ("tipo_magia", wx.ComboBox, {"choices": ["Qualsiasi"] + [st.value for st in EnuSpellType], "style": wx.CB_READONLY}),
            ("sottotipo", wx.ComboBox, {"choices": ["Tutti"] + [st.value for st in EnuPetSubType], "style": wx.CB_READONLY}),
            ("attacco", wx.ComboBox, {"choices": ["Qualsiasi"] + [str(i) for i in range(0, 21)], "style": wx.CB_READONLY}),
            ("vita", wx.ComboBox, {"choices": ["Qualsiasi"] + [str(i) for i in range(0, 21)], "style": wx.CB_READONLY}),
            ("rarita", wx.ComboBox, {"choices": ["Tutti"] + [r.value for r in EnuRarity], "style": wx.CB_READONLY}),
            ("espansione", wx.ComboBox, {"choices": ["Tutti"] + [e.value for e in EnuExpansion], "style": wx.CB_READONLY})
        ]

        # Creazione dei controlli UI e aggiunta al sizer principale
        for key, control_type, *args in common_controls:
            # Crea un sizer orizzontale per ogni controllo
            h_sizer = wx.BoxSizer(wx.HORIZONTAL)

            # Aggiungi un'etichetta
            label = wx.StaticText(self.panel, label=f"{key.capitalize()}:")
            h_sizer.Add(label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

            # Crea il controllo
            if args:
                control = control_type(self.panel, **args[0])
            else:
                control = control_type(self.panel)

            # Aggiungi il controllo al sizer orizzontale
            h_sizer.Add(control, 1, wx.EXPAND | wx.ALL, 5)

            # Aggiungi il sizer orizzontale al sizer principale
            self.sizer.Add(h_sizer, 0, wx.EXPAND | wx.ALL, 5)

            # Memorizza il controllo nel dizionario
            self.controls[key] = control

        # Collega l'evento di selezione del tipo di carta al metodo update_subtypes
        self.controls["tipo"].Bind(wx.EVT_COMBOBOX, self.on_type_change)

        # Imposta il sizer principale per il pannello
        self.panel.SetSizer(self.sizer)


    def on_type_change(self, event):
        """Aggiorna i sottotipi in base al tipo di carta selezionato."""
        card_type = self.controls["tipo"].GetValue()
        if card_type == EnuCardType.MAGIA.value:
            subtypes = [st.value for st in EnuSpellSubType]
        elif card_type == EnuCardType.CREATURA.value:
            subtypes = [st.value for st in EnuPetSubType]
        else:
            subtypes = []

        # Aggiorna i sottotipi
        self.controls["sottotipo"].Clear()
        self.controls["sottotipo"].AppendItems(subtypes)

    def add_buttons(self, btn_sizer):
        """
        Aggiunge pulsanti alla finestra di dialogo.

        :param btn_sizer: Il sizer a cui aggiungere i pulsanti.
        """
        # Pulsante "Applica"
        apply_btn = wx.Button(self.panel, label="Applica")
        apply_btn.Bind(wx.EVT_BUTTON, self.on_apply_filters)
        btn_sizer.Add(apply_btn, flag=wx.ALL, border=5)

        # Pulsante "Annulla"
        cancel_btn = wx.Button(self.panel, label="Annulla")
        cancel_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        btn_sizer.Add(cancel_btn, flag=wx.ALL, border=5)



class ListView(BasicView):
    """
    Classe base per finestre che gestiscono elenchi (carte, mazzi, ecc.).
    Utilizzata per finestre come "Collezione Carte", "Gestione Mazzi" o "Visualizza Mazzo".
    """

    def __init__(self, parent, title, size=(800, 600)):
        super().__init__(parent, title, size)
        self.mode = None                                    # Modalità di visualizzazione (es. "collection", "deck")
        self.card_list= None                                # ListCtrl per visualizzare l'elenco
        self.data = []                                      # Lista dei dati da visualizzare
        self.timer = wx.Timer(self)                         # Timer per il debounce
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)  # Aggiunge l'evento per il timer
        self.Bind(EVT_SEARCH_EVENT, self.on_search_event)   # Aggiunge l'evento per la ricerca

    def init_ui(self):
        """Inizializza l'interfaccia utente con le impostazioni comuni a tutte le finestre."""

        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.sizer)

        # imposta i colori di spondo giallo per finestra e pannello
        self.BackgroundColour = 'black'
        self.panel.BackgroundColour = 'black'

        # imposta il font per il titolo
        font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        title = wx.StaticText(self.panel, label=self.Title)
        title.SetFont(font)


    def init_ui_elements(self):
        """
        Inizializza gli elementi dell'interfaccia utente.
        Questo metodo deve essere esteso dalle classi derivate per aggiungere componenti specifici.
        """
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
        add_to_sizer(self.sizer, self.card_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Pulsanti azione
        btn_panel = wx.Panel(self.panel)
        btn_sizer = create_sizer(wx.HORIZONTAL)

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

        btn_panel.SetSizer(btn_sizer)
        add_to_sizer(self.sizer, btn_panel, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)
        #self.load_cards()
        self.Layout()

    def load_cards(self, filters=None):
        """
        Carica i dati nell'elenco.
        Deve essere implementato nelle classi derivate.
        """
        log.error("Il metodo load_cards deve essere implementato nelle classi derivate.")
        raise NotImplementedError("Il metodo load_cards deve essere implementato nelle classi derivate.")


    def on_refresh(self, event):
        """Aggiorna l'elenco."""

        self.load_cards()


    def on_search(self, event):
        """Gestisce la ricerca testuale."""
        search_text = self.search_ctrl.GetValue().strip().lower()
        self._apply_search_filter(search_text)
        self.set_focus_to_list()


    def on_search_text_change(self, event):
        """
        Gestisce la ricerca in tempo reale mentre l'utente digita.
        Avvia un timer per il debounce.
        """

        search_text = getattr(self, "search_ctrl", None)
        if search_text:
            search_text = search_text.GetValue().strip().lower()
            if not search_text:
                return

            # Ferma il timer precedente e avvia un nuovo debounce
            self.timer.Stop()
            self.timer.Start(500, oneShot=True)


    def on_timer(self, event):
        """
        Esegue la ricerca dopo il timeout del debounce.
        Genera un evento personalizzato per la ricerca.
        """

        search_text = getattr(self, "search_ctrl", None)
        if search_text:
            search_text = search_text.GetValue().strip().lower()
            evt = SearchEvent(search_text=search_text)
            wx.PostEvent(self, evt)


    def on_search_event(self, event):
        """
        Gestisce l'evento di ricerca con debounce.
        Applica il filtro di ricerca e imposta il focus sulla prima voce.
        """

        search_text = event.search_text
        self._apply_search_filter(search_text)
        self.set_focus_to_list()


    def _apply_search_filter(self, search_text):
        """
        Applica il filtro di ricerca alla lista delle carte.
        Se il testo di ricerca è vuoto, reimposta i dati originali.
        """
        if not search_text or search_text in ["tutti", "tutto", "all"]:
            self.load_cards()
        else:
            self.load_cards(filters={"name": search_text})


    def set_focus_to_list(self):
        """
        Imposta il focus sulla prima voce della lista.
        Deve essere chiamato solo dopo aver creato il ListCtrl.
        """

        list_ctrl = getattr(self, "list_ctrl", None)
        if list_ctrl and list_ctrl.GetItemCount() > 0:
            list_ctrl.SetFocus()
            list_ctrl.Select(0)
            list_ctrl.Focus(0)
            list_ctrl.EnsureVisible(0)


    def sort_cards(self, col):
        """
        Ordina le carte in base alla colonna selezionata.
        Funziona sia per colonne numeriche che testuali.
        """

        list_ctrl = getattr(self, "list_ctrl", None)
        if not list_ctrl:
            return

        items = []
        for i in range(list_ctrl.GetItemCount()):
            item = [list_ctrl.GetItemText(i, c) for c in range(list_ctrl.GetColumnCount())]
            items.append(item)

        def safe_int(value):
            try:
                return int(value)
            except ValueError:
                return float('inf') if value == "-" else value

        if col == 1:  # Colonna numerica (es. "Mana")
            items.sort(key=lambda x: safe_int(x[col]))
        else:  # Colonnes testuali
            items.sort(key=lambda x: x[col])

        list_ctrl.DeleteAllItems()
        for item in items:
            list_ctrl.Append(item)


    def on_column_click(self, event):
        """
        Gestisce il clic sulle intestazioni delle colonne per ordinare la lista.
        """

        col = event.GetColumn()
        self.sort_cards(col)

    def on_key_press(self, event):
        """
        Gestisce i tasti premuti per ordinare la lista.
        """
        key_code = event.GetKeyCode()
        if ord('1') <= key_code <= ord('9'):
            col = key_code - ord('1')
            self.sort_cards(col)



class CollectionsListView(ListView):
    """
        Classe per la visualizzazione della collezzione generale  di carte.
    """

    def __init__(self, parent, title="Collezione Carte", size=(1200, 800)):
        super().__init__(parent, title, size)
        self.mode = "collection"


    def init_ui(self):
        """Inizializza l'interfaccia utente con le impostazioni comuni a tutte le finestre."""

        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.sizer)

        # imposta i colori di spondo giallo per finestra e pannello
        self.BackgroundColour = 'black'
        self.panel.BackgroundColour = 'black'

        # imposta il font per il titolo
        font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        title = wx.StaticText(self.panel, label=self.Title)
        title.SetFont(font)


    def init_ui_elements(self):
        """
        Inizializza gli elementi dell'interfaccia utente.
        Questo metodo deve essere esteso dalle classi derivate per aggiungere componenti specifici.
        """
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
        add_to_sizer(self.sizer, self.card_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Pulsanti azione
        btn_panel = wx.Panel(self.panel)
        btn_sizer = create_sizer(wx.HORIZONTAL)

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

        btn_panel.SetSizer(btn_sizer)
        add_to_sizer(self.sizer, btn_panel, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)
        #self.load_cards()
        self.Layout()



class DecksListView(ListView):
    """
        Classe base per la visualizzazione di elenchi di mazzi.
    """

    def __init__(self, parent, title="Gestione Mazzi", size=(800, 600)):
        super().__init__(parent, title, size)
        #self.init_ui_elements()

    def _ui_elements(self):
        """Inizializza gli elementi dell'interfaccia utente specifici per la visualizzazione dei mazzi."""
        super().init_ui_elements()
        self.list_ctrl.AppendColumn("Mazzo", width=260)
        self.list_ctrl.AppendColumn("Classe", width=200)
        self.list_ctrl.AppendColumn("Formato", width=120)

    def load_data(self):
        """Carica i mazzi nella lista."""

        decks = session.query(Deck).all()
        self.list_ctrl.DeleteAllItems()
        for deck in decks:
            index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), deck.name)
            self.list_ctrl.SetItem(index, 1, deck.player_class)
            self.list_ctrl.SetItem(index, 2, deck.game_format)




#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
