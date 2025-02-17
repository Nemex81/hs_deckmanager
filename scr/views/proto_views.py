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
from abc import ABC, abstractmethod
from scr.models import load_cards_from_db
from utyls.enu_glob import EnuCardType, EnuSpellSubType, EnuPetSubType, EnuRarity, EnuExpansion, EnuSpellType, EnuHero
from utyls import helper as hp
from scr.db import session, Card, Deck
from utyls.enu_glob import EnuCardType, EnuSpellSubType, EnuPetSubType, EnuRarity, EnuExpansion, EnuSpellType
from utyls import logger as log




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
        self.panel.SetSizer(self.sizer)                 # Imposta il sizer per il pannello
        self.Center()                                   # Centra la finestra
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
        self.parent = parent
        self.init_ui()
        self.Centre()
        self.Show()
    
    def init_ui(self):
        """Inizializza l'interfaccia utente con le impostazioni comuni a tutte le finestre."""
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.sizer)
        self.init_ui_elements()

    @abstractmethod
    def init_ui_elements(self, *args, **kwargs):
        """Inizializza gli elementi dell'interfaccia utente."""
        pass

    def on_close(self, event):
        """Chiude la finestra."""
        self.parent.show()
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
        self.list_ctrl.AppendColumn("Durabilità", width=50)
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


class DecksListView(ListView):
    """
        Classe base per la visualizzazione di elenchi di mazzi.
    """

    def __init__(self, parent, title="Gestione Mazzi", size=(800, 600)):
        super().__init__(parent, title, size)
        #self.init_ui_elements()

    def init_ui_elements(self):
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
    print("Carico: %s." % __name__)
