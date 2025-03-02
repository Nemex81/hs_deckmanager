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
from .builder.color_system import ColorManager, AppColors, ColorTheme
import scr.views.builder.view_components as vc
from utyls import helper as hp
from utyls import enu_glob as eg
from utyls import logger as log
#import pdb

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
    
    def __init__(self, parent, title, size=(900, 700)):
        super().__init__(parent=parent, title=title, size=size)
        self.parent = parent               # Finestra genitore
        self.controller = None             # Controller per l'interfaccia
        self.db_manager = None             # Gestore del database
        self.cm = ColorManager()           # Gestore dei colori

        # Colori personalizzati per lo stato attivo e inattivo
        self.FOCUS_BG_COLOR = self.cm.get_color(AppColors.FOCUS_BG)
        self.FOCUS_TEXT_COLOR = self.cm.get_color(AppColors.FOCUS_TEXT)
        self.DEFAULT_BG_COLOR = self.cm.get_color(AppColors.DEFAULT_BG)
        self.DEFAULT_TEXT_COLOR = self.cm.get_color(AppColors.DEFAULT_TEXT)
        self.error_bg_color = self.cm.get_color(AppColors.ERROR_BG)
        self.error_text_color = self.cm.get_color(AppColors.ERROR_TEXT)

        # applica il tema dark
        self.cm.set_theme_dark()

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

    def bind_focus_events(self, element):
        """
        Collega gli eventi di focus a un elemento dell'interfaccia grafica.
        """
        element.Bind(wx.EVT_SET_FOCUS, lambda e: self.set_focus_style(element))
        element.Bind(wx.EVT_KILL_FOCUS, lambda e: self.reset_focus_style(element))

    def set_focus_style(self, element):
        """
        Imposta il colore di sfondo e del font quando l'elemento riceve il focus.
        """
        self.reset_focus_style_for_all_buttons()
        log.debug(f"Elemento {element.GetLabel()} ha ricevuto il focus.")
        self.cm.apply_focus_style(element)          # Applica lo stile di focus all'elemento
        #element.Refresh()                           # Forza il ridisegno dell'elemento

    def reset_focus_style(self, element):
        """
        Ripristina il colore di sfondo e del font predefiniti quando l'elemento perde il focus.
        """
        log.debug(f"Elemento {element.GetLabel()} ha perso il focus.")
        self.cm.apply_default_style(element)
        #element.Refresh()

    def reset_focus_style_for_all_buttons(self, btn_sizer=None):
        """ Ripristina il colore di sfondo e del font per tutti i pulsanti. """
        if not btn_sizer:
            for child in self.panel.GetChildren():
                if isinstance(child, wx.Button):
                    self.reset_focus_style(child)
        else:
            for i in range(btn_sizer.GetItemCount()):
                btn = btn_sizer.GetItem(i).GetWindow()
                self.reset_focus_style(btn)

    def reset_focus_style_for_card_list(self, selected_item=None):
        """ Resetta lo stile di tutte le righe. """


        for i in range(self.card_list.GetItemCount()):
            if i != selected_item:
                self.cm.apply_default_style_to_list_item(self.card_list, i)

        # Forza il ridisegno della lista
        self.card_list.Refresh()


    def select_element(self, row):
        """ Seleziona l'elemento attivo. """

        if hasattr(self, "card_list"):
            self.card_list.SetItemBackgroundColour(row, eg.BLUE)
            self.card_list.SetItemTextColour(row, eg.WHITE)
            self.card_list.Refresh()


    def on_item_focused(self, event):
        """Gestisce l'evento di focus su una riga della lista."""

        # Imposta lo stile della riga selezionata
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

    def init_ui(self):
        """ Inizializza l'interfaccia utente con le impostazioni comuni a tutte le finestre. """
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.sizer)

        # Imposta i colori di sfondo per finestra e pannello
        self.SetBackgroundColour(self.cm.get_color(AppColors.DEFAULT_BG))
        self.panel.SetBackgroundColour(self.cm.get_color(AppColors.DEFAULT_BG))

        # Imposta il font per il titolo
        font = wx.Font(32, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        title = wx.StaticText(self.panel, label=self.Title)
        title.SetFont(font)
        self.init_ui_elements() # Inizializza gli elementi dell'interfaccia utente

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
            ("tipo", wx.ComboBox, {"choices": ["Tutti"] + [t.value for t in eg.EnuCardType], "style": wx.CB_READONLY}),
            ("tipo_magia", wx.ComboBox, {"choices": ["Qualsiasi"] + [st.value for st in EnuSpellType], "style": wx.CB_READONLY}),
            ("sottotipo", wx.ComboBox, {"choices": ["Tutti"] + [st.value for st in EnuPetSubType], "style": wx.CB_READONLY}),
            ("attacco", wx.ComboBox, {"choices": ["Qualsiasi"] + [str(i) for i in range(0, 21)], "style": wx.CB_READONLY}),
            ("vita", wx.ComboBox, {"choices": ["Qualsiasi"] + [str(i) for i in range(0, 21)], "style": wx.CB_READONLY}),
            ("rarita", wx.ComboBox, {"choices": ["Tutti"] + [r.value for r in EnuRarity], "style": wx.CB_READONLY}),
            ("espansione", wx.ComboBox, {"choices": [e.value for e in EnuExpansion], "style": wx.CB_READONLY})
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
        if card_type == eg.EnuCardType.MAGIA.value:
            subtypes = [st.value for st in eg.EnuSpellSubType]

        elif card_type == eg.EnuCardType.CREATURA.value:
            subtypes = [st.value for st in eg.EnuPetSubType]

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
        self.mode = None                                  # Modalità di visualizzazione (es. "collection", "decks", "deck")

        # Timer per il debounce
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.Bind(EVT_SEARCH_EVENT, self.on_search_event)


    def set_focus_style(self, element):
        """
        Imposta il colore di sfondo e del font quando l'elemento riceve il focus.
        """
        self.reset_focus_style_for_all_buttons()
        log.debug(f"Elemento {element.GetLabel()} ha ricevuto il focus.")
        self.cm.apply_focus_style(element)          # Applica lo stile di focus all'elemento
        #element.Refresh()                           # Forza il ridisegno dell'elemento


    def reset_focus_style(self, element):
        """
        Ripristina il colore di sfondo e del font predefiniti quando l'elemento perde il focus.
        """
        log.debug(f"Elemento {element.GetLabel()} ha perso il focus.")
        self.cm.apply_default_style(element)
        #element.Refresh()


    def init_ui_elements(self):
        """
        Inizializza gli elementi dell'interfaccia utente.
        Questo metodo deve essere esteso dalle classi derivate per aggiungere componenti specifici.
        """
        log.error("Il metodo load_cards deve essere implementato nelle classi derivate.")
        raise NotImplementedError("Il metodo load_cards deve essere implementato nelle classi derivate.")


    def load_cards(self, filters=None):
        """
        Carica le carte nella lista.
        Questo metodo deve essere implementato nelle classi derivate.
        """
        log.error("Il metodo load_cards deve essere implementato nelle classi derivate.")
        raise NotImplementedError("Il metodo load_cards deve essere implementato nelle classi derivate.")


    def refresh_card_list(self):
        """Aggiorna la lista delle carte con i dati più recenti dal database."""

        log.debug("Aggiornamento della lista delle carte...")        
        raise NotImplementedError("Il metodo load_cards deve essere implementato nelle classi derivate.")


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


    def select_card_by_name(self, card_name):
        """Seleziona una carta nella lista in base al nome."""

        if not card_name:
            return

        for i in range(self.card_list.GetItemCount()):
            if self.card_list.GetItemText(i) == card_name:
                self.card_list.Select(i)
                self.card_list.Focus(i)
                self.card_list.EnsureVisible(i)
                self.card_list.SetFocus()
                break


    def select_element(self, row):
        """Seleziona l'elemento attivo e applica lo stile di focus."""

        if hasattr(self, "card_list"):
            # Applica lo stile di focus alla riga selezionata
            #self.cm.apply_focus_style(row)
            self.cm.apply_selection_style_to_list(self.card_list, row)

            # Resetta lo stile delle altre righe
            for i in range(self.card_list.GetItemCount()):
                if i != row:
                    self.cm.apply_default_style_to_list_item(self.card_list, i)

            # Forza il ridisegno della lista
            self.card_list.Refresh()


    def set_focus_to_list(self):
        """Imposta il focus sulla prima carta della lista carte."""

        if hasattr(self, "card_list"):
            self.card_list.SetFocus()
            self.card_list.Select(0)
            self.card_list.Focus(0)
            self.card_list.EnsureVisible(0)


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


    def on_search(self, event):
        """Gestisce la ricerca testuale."""

        search_text = self.search_ctrl.GetValue().strip().lower()
        self._apply_search_filter(search_text)


    def on_item_focused(self, event):
        """Gestisce l'evento di focus su una riga della lista."""

        selected_item = event.GetIndex()
        self.select_element(selected_item)  # Applica lo stile di focus alla riga selezionata
        self.card_list.Refresh()  # Forza il ridisegno della lista



#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
