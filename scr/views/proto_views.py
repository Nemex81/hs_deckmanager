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
from .view_components import create_button, create_separator, add_to_sizer
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
        self.Maximize()               # Massimizza la finestra
        self.Centre()                 # Centra la finestra
        self.init_ui()                # Inizializza l'interfaccia utente
        self.Show()
    
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

    def load_cards(self, filters=None):
        """ carica le carte utilizzando le funzionihelper sopra definite"""
        load_cards(filters=filters, card_list=self.card_list)

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
        Classe base per finestre che gestiscono i campi di una singola carta.
        Utilizzata per finestre come "Aggiungi Carta", "Modifica Carta" o "Filtri".
    """

    def __init__(self, parent, title, size=(400, 500)):
        super().__init__(parent, title, size)
        self.card_data = {}  # Dizionario per memorizzare i dati della carta

    def init_ui_elements(self):
        """Inizializza i campi comuni per una singola carta."""

        self.fields = [
            ("nome", wx.TextCtrl),
            ("costo_mana", wx.SpinCtrl, {"min": 0, "max": 20}),
            ("tipo", wx.ComboBox, {"choices": [t.value for t in EnuCardType], "style": wx.CB_READONLY}),
            ("tipo_magia", wx.ComboBox, {"choices": [t.value for t in EnuSpellType], "style": wx.CB_READONLY}),
            ("sottotipo", wx.ComboBox, {"choices": [], "style": wx.CB_READONLY}),
            ("attacco", wx.SpinCtrl, {"min": 0, "max": 20}),
            ("vita", wx.SpinCtrl, {"min": 0, "max": 20}),
            ("durability", wx.SpinCtrl, {"min": 0, "max": 20}),
            ("rarita", wx.ComboBox, {"choices": [r.value for r in EnuRarity], "style": wx.CB_READONLY}),
            ("espansione", wx.ComboBox, {"choices": [e.value for e in EnuExpansion], "style": wx.CB_READONLY})
        ]

        self.sizer, self.control_dict = hp.create_ui_controls(self.panel, self.fields)

        # Collega l'evento di selezione del tipo di carta al metodo update_subtypes
        self.control_dict["tipo"].Bind(wx.EVT_COMBOBOX, self.on_type_change)

    def on_type_change(self, event):
        """Aggiorna i sottotipi in base al tipo di carta selezionato."""

        card_type = self.control_dict["tipo"].GetValue()
        if card_type == EnuCardType.MAGIA.value:
            subtypes = [st.value for st in EnuSpellSubType]
        elif card_type == EnuCardType.CREATURA.value:
            subtypes = [st.value for st in EnuPetSubType]
        else:
            subtypes = []

        # Aggiorna i sottotipi
        self.control_dict["sottotipo"].Clear()
        self.control_dict["sottotipo"].AppendItems(subtypes)

    def get_card_data(self):
        """Restituisce i dati della carta inseriti dall'utente."""

        return {
            "name": self.control_dict["nome"].GetValue(),
            "mana_cost": self.control_dict["costo_mana"].GetValue(),
            "card_type": self.control_dict["tipo"].GetValue(),
            "spell_type": self.control_dict["tipo_magia"].GetValue(),
            "card_subtype": self.control_dict["sottotipo"].GetValue(),
            "attack": self.control_dict["attacco"].GetValue(),
            "health": self.control_dict["vita"].GetValue(),
            "durability": self.control_dict["durability"].GetValue(),
            "rarity": self.control_dict["rarita"].GetValue(),
            "expansion": self.control_dict["espansione"].GetValue()
        }



class ListView(BasicView):
    """
    Classe base per finestre che gestiscono elenchi (carte, mazzi, ecc.).
    Utilizzata per finestre come "Collezione Carte", "Gestione Mazzi" o "Visualizza Mazzo".
    """

    def __init__(self, parent, title, size=(800, 600)):
        super().__init__(parent, title, size)
        self.list_ctrl = None  # ListCtrl per visualizzare l'elenco
        self.data = []  # Lista dei dati da visualizzare
        self.timer = wx.Timer(self)  # Timer per il debounce
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.Bind(EVT_SEARCH_EVENT, self.on_search_event)

    def init_ui_elements(self):
        """Inizializza la lista e i pulsanti comuni."""

        self.list_ctrl = wx.ListCtrl(
            self.panel,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN
        )
        self.sizer.Add(self.list_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Pulsanti comuni
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        for label in ["Aggiorna", "Chiudi"]:
            btn = wx.Button(self.panel, label=label)
            btn_sizer.Add(btn, flag=wx.RIGHT, border=5)
            if label == "Aggiorna":
                btn.Bind(wx.EVT_BUTTON, self.on_refresh)
            elif label == "Chiudi":
                btn.Bind(wx.EVT_BUTTON, self.on_close)

        self.sizer.Add(btn_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

    def load_data(self):
        """Carica i dati nell'elenco (da implementare nelle classi derivate)."""
        raise NotImplementedError("Il metodo load_data deve essere implementato nelle classi derivate.")


    def on_refresh(self, event):
        """Aggiorna l'elenco."""
        self.load_data()

    def on_search_text_change(self, event):
        """Gestisce la ricerca in tempo reale mentre l'utente digita."""
        search_text = self.search_ctrl.GetValue().strip().lower()
        if not search_text:
            return

        # Avvia il timer per il debounce (es. 500 ms)
        self.timer.Stop()  # Ferma il timer precedente
        self.timer.Start(500, oneShot=True)

    def on_timer(self, event):
        """Esegue la ricerca dopo il timeout del debounce."""
        search_text = self.search_ctrl.GetValue().strip().lower()
        evt = SearchEvent(search_text=search_text)
        wx.PostEvent(self, evt)

    def on_search_event(self, event):
        """Gestisce l'evento di ricerca con debounce."""
        search_text = event.search_text
        self._apply_search_filter(search_text)
        self.set_focus_to_list()

    def _apply_search_filter(self, search_text):
        """Applica il filtro di ricerca alla lista delle carte."""
        if not search_text or search_text in ["tutti", "tutto", "all"]:
            self.load_data()
        else:
            self.load_data(filters={"name": search_text})

    def set_focus_to_list(self):
        """Imposta il focus sulla prima carta della lista carte."""
        if hasattr(self, "list_ctrl"):
            self.list_ctrl.SetFocus()
            self.list_ctrl.Select(0)
            self.list_ctrl.Focus(0)
            self.list_ctrl.EnsureVisible(0)

    def sort_cards(self, col):
        """Ordina le carte in base alla colonna selezionata."""
        items = []
        for i in range(self.list_ctrl.GetItemCount()):
            item = [self.list_ctrl.GetItemText(i, c) for c in range(self.list_ctrl.GetColumnCount())]
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

        self.list_ctrl.DeleteAllItems()
        for item in items:
            self.list_ctrl.Append(item)

    def on_column_click(self, event):
        """Ordina le carte in base alla colonna selezionata."""
        col = event.GetColumn()
        self.sort_cards(col)

    def on_key_press(self, event):
        """Gestisce i tasti premuti per ordinare la lista."""
        key_code = event.GetKeyCode()
        if ord('1') <= key_code <= ord('9'):
            col = key_code - ord('1')
            if col < self.list_ctrl.GetColumnCount():
                self.sort_cards(col)

        event.Skip()



class CardsListView(ListView):
    """
        Classe base per la visualizzazione di elenchi di carte.
    """

    def __init__(self, parent, title="Collezione Carte", size=(1200, 800)):
        super().__init__(parent, title, size)
        #self.init_ui_elements()

    def init_ui_elements(self):
        """Inizializza gli elementi dell'interfaccia utente specifici per la visualizzazione delle carte."""
        super().init_ui_elements()
        self.list_ctrl.AppendColumn("Nome", width=250)
        self.list_ctrl.AppendColumn("Mana", width=50)
        self.list_ctrl.AppendColumn("Classe", width=120)
        self.list_ctrl.AppendColumn("Tipo", width=120)
        self.list_ctrl.AppendColumn("Tipo Magia", width=120)
        self.list_ctrl.AppendColumn("Sottotipo", width=120)
        self.list_ctrl.AppendColumn("Attacco", width=50)
        self.list_ctrl.AppendColumn("Vita", width=50)
        self.list_ctrl.AppendColumn("Integrità", width=50)
        self.list_ctrl.AppendColumn("Rarità", width=120)
        self.list_ctrl.AppendColumn("Espansione", width=500)

    def load_data(self, filters=None):
        """Carica le carte nella lista."""
        cards = load_cards_from_db(filters)
        self.list_ctrl.DeleteAllItems()
        for card in cards:
            self.list_ctrl.Append([
                card.name,
                str(card.mana_cost) if card.mana_cost else "-",
                card.class_name if card.class_name else "-",
                card.card_type if card.card_type else "-",
                card.spell_type if card.spell_type else "-",
                card.card_subtype if card.card_subtype else "-",
                str(card.attack) if card.attack is not None else "-",
                str(card.health) if card.health is not None else "-",
                str(card.durability) if card.durability is not None else "-",
                card.rarity if card.rarity else "-",
                card.expansion if card.expansion else "-"
            ])



class CardFormDialog(BasicDialog):
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
