"""
        Modulo per la gestione delel finestre secondarie dell'applicazione

        path:
            ./scr/views/view_components.py

    Descrizione:
        Questo modulo contiene le classi per la gestione delle finestre secondarie dell'applicazione.
        Le classi base come SingleCardView e ListView forniscono funzionalità specifiche per la gestione di carte e elenchi.
        Le classi derivate come CardsListView e DecksListView implementano le finestre per la visualizzazione delle carte e dei mazzi.

"""

# Lib
import wx
from abc import ABC, abstractmethod
from scr.models import load_cards_from_db
from utyls.enu_glob import EnuCardType, EnuSpellSubType, EnuPetSubType, EnuRarity, EnuExpansion, EnuSpellType, EnuHero
from utyls import helper as hp
from ..db import session, Card, Deck
from .proto_views import BasicDialog, BasicView
from utyls.enu_glob import EnuCardType, EnuSpellSubType, EnuPetSubType, EnuRarity, EnuExpansion, EnuSpellType
from utyls import logger as log



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





class CardManagerFrame(wx.Frame):
    """

        Finestra generica per gestire le carte (collezione o mazzo).

        :param parent: Finestra principale (frame), genitore della finestra di dialogo
        :param deck_manager: Gestore dei mazzi
        :param mode: Modalità della finestra ("collection" o "deck")
        :param deck_name: Nome del mazzo (se la modalità è "deck")

    """

    def __init__(self, parent, deck_manager=None, mode="collection", deck_name=None):
        title = "Collezione Carte" if mode == "collection" else f"Mazzo: {deck_name}"
        super().__init__(parent, title=title, size=(1200, 800))
        self.parent = parent
        self.SetBackgroundColour('green')
        self.deck_manager = deck_manager
        self.mode = mode  # "collection" o "deck"
        self.deck_name = deck_name
        self.deck_content = self.deck_manager.get_deck(deck_name) if mode == "deck" else None
        if self.mode == "deck" and not self.deck_content:
            raise ValueError(f"Mazzo non trovato: {deck_name}")

        self.Centre()    # Centra la finestra
        self.Maximize()  # Massimizza la finestra
        self.init_ui()  # Inizializza l'interfaccia utente


    def init_ui(self):
        """ Inizializza l'interfaccia utente. """

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Lista delle carte
        self.card_list = wx.ListCtrl(
            panel,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN
        )
        self.card_list.AppendColumn("Nome", width=250)
        self.card_list.AppendColumn("Mana", width=50)
        
        # Aggiungi la colonna "Quantità" o "Classe" in base alla modalità
        if self.mode == "deck":
            self.card_list.AppendColumn("Quantità", width=80)
        else:
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
        sizer.Add(self.card_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Pulsanti azione
        btn_panel = wx.Panel(panel)
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
        sizer.Add(btn_panel, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        panel.SetSizer(sizer)
        self.load_cards()

        # Aggiungi l'evento per il clic sulle intestazioni delle colonne
        self.card_list.Bind(wx.EVT_LIST_COL_CLICK, self.on_column_click)

        # Aggiungi l'evento per i tasti premuti
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_press)


    def load_cards(self, filters=None):
        """ carica le carte utilizzando le funzionihelper sopra definite"""
        pass


    def on_column_click(self, event):
        """Gestisce il clic sulle intestazioni delle colonne per ordinare le carte."""
        col = event.GetColumn()
        self.sort_cards(col)


    def sort_cards(self, col):
        """Ordina le carte in base alla colonna selezionata."""

        # Ottieni i dati dalla lista
        items = []
        for i in range(self.card_list.GetItemCount()):
            item = [self.card_list.GetItemText(i, c) for c in range(self.card_list.GetColumnCount())]
            items.append(item)

        # Ordina i dati in base alla colonna selezionata
        if col == 1:  # Colonna "Mana" (numerica)
            items.sort(key=lambda x: int(x[col]))

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


    def on_reset(self, event):
        """Ripristina la visualizzazione originale, rimuovendo i filtri e riordinando le colonne."""
        pass


    def on_add_card(self, event):
        """Aggiunge una nuova carta (alla collezione o al mazzo)."""
        pass


    def on_edit_card(self, event):
        """Modifica la carta selezionata."""
        pass


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

                    elif self.mode == "deck":
                        # Rimuovi la carta dal mazzo
                        self.deck_content["cards"] = [
                            card_data for card_data in self.deck_content["cards"]
                            if card_data["name"] != card_name
                        ]

                        # Aggiorna il mazzo nel database
                        self.load_cards()
                        wx.MessageBox(f"Carta '{card_name}' eliminata dal mazzo.", "Successo", wx.OK | wx.ICON_INFORMATION)

                except Exception as e:
                    log.error(f"Errore durante l'eliminazione della carta: {str(e)}")
                    wx.MessageBox(f"Errore durante l'eliminazione della carta: {str(e)}", "Errore", wx.OK | wx.ICON_ERROR)

        else:
            wx.MessageBox("Seleziona una carta da eliminare.", "Errore", wx.OK | wx.ICON_ERROR)


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


    def on_close(self):
        """Chiude la finestra di dialogo."""
        self.parent.show()
        self.Close()
        self.Destroy()




class FilterDialog(BasicDialog):
    """ Finestra di dialogo per i filtri di ricerca. """

    def __init__(self, parent):
        super().__init__(parent, title="Filtri di Ricerca", size=(300, 400))
        self.parent = parent

    def init_ui_elements(self):
        """ Inizializza gli elementi dell'interfaccia utente. """

        # Pannello principale
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Aggiungo "Qualsiasi" come prima opzione per il costo mana
        mana_choices = ["Qualsiasi"] + [str(i) for i in range(0, 21)]
        attack_choices = ["Qualsiasi"] + [str(i) for i in range(0, 21)]
        health_choices = ["Qualsiasi"] + [str(i) for i in range(0, 21)]
        durability_choices = ["Qualsiasi"] + [str(i) for i in range(0, 21)]

        controls = [
            ("nome", wx.TextCtrl),
            ("costo_mana", wx.ComboBox, {"choices": mana_choices, "style": wx.CB_READONLY}),
            ("tipo", wx.ComboBox, {"choices": ["Tutti"] + [t.value for t in EnuCardType], "style": wx.CB_READONLY}),
            ("tipo_magia", wx.ComboBox, {"choices": ["Qualsiasi"] + [st.value for st in EnuSpellType], "style": wx.CB_READONLY}),
            ("sottotipo", wx.ComboBox, {"choices": ["Tutti"] + [st.value for st in EnuPetSubType], "style": wx.CB_READONLY}),
            ("attacco", wx.ComboBox, {"choices": attack_choices, "style": wx.CB_READONLY}),
            ("vita", wx.ComboBox, {"choices": health_choices, "style": wx.CB_READONLY}),
            #("durability", wx.ComboBox, {"choices": durability_choices, "style": wx.CB_READONLY}),
            ("rarita", wx.ComboBox, {"choices": ["Tutti"] + [r.value for r in EnuRarity], "style": wx.CB_READONLY}),
            ("espansione", wx.ComboBox, {"choices": ["Tutti"] + [e.value for e in EnuExpansion], "style": wx.CB_READONLY})
        ]

        self.sizer, control_dict = hp.create_ui_controls(self.panel, controls)

        self.search_ctrl = control_dict["nome"]
        self.mana_cost = control_dict["costo_mana"]
        self.card_type = control_dict["tipo"]
        self.spell_type = control_dict["tipo_magia"]
        self.card_subtype = control_dict["sottotipo"]
        self.attack = control_dict["attacco"]
        self.health = control_dict["vita"]
        #self.durability = control_dict["durability"]
        self.rarity = control_dict["rarita"]
        self.expansion = control_dict["espansione"]

        # Imposta i valori predefiniti
        self.reset_filters()

        # Collega l'evento di selezione del tipo di carta al metodo update_subtypes
        self.card_type.Bind(wx.EVT_COMBOBOX, self.on_type_change)

        # Pulsanti
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_apply = wx.Button(self.panel, label="Applica")
        self.btn_cancel = wx.Button(self.panel, label="Annulla")
        btn_sizer.Add(self.btn_apply, flag=wx.RIGHT, border=10)
        btn_sizer.Add(self.btn_cancel)

        # Eventi
        self.btn_apply.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_OK))
        self.btn_cancel.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))

        self.sizer.Add(btn_sizer, flag=wx.ALIGN_RIGHT|wx.ALL, border=10)
        self.panel.SetSizer(self.sizer)
        self.SetBackgroundColour('red')
        # Aggiorna i sottotipi in base al tipo selezionato
        self.update_subtypes()


    def reset_filters(self):
        """ Resetta i filtri ai valori predefiniti. """

        self.search_ctrl.SetValue("")
        self.mana_cost.SetValue("Qualsiasi")  # Imposta "Qualsiasi" come valore predefinito
        self.card_type.SetValue("Tutti")
        self.spell_type.SetValue("Qualsiasi")
        self.card_subtype.SetValue("Tutti")
        self.attack.SetValue("Qualsiasi")
        self.health.SetValue("Qualsiasi")
        #self.durability.SetValue("Qualsiasi")
        self.rarity.SetValue("Tutti")
        self.expansion.SetValue("Tutti")


    def update_subtypes(self):
        """ Aggiorna i sottotipi in base al tipo di carta selezionato. """

        subtypes = "-"
        card_type = self.card_type.GetValue()
        if card_type == EnuCardType.MAGIA.value:
            subtypes = [st.value for st in EnuSpellSubType]

        elif card_type == EnuCardType.CREATURA.value:
            subtypes = [st.value for st in EnuPetSubType]

        else:
            subtypes = []

        # Salva il sottotipo corrente
        current_subtype = self.card_subtype.GetValue()
        self.card_subtype.Clear()
        self.card_subtype.AppendItems(subtypes)
        # Se il sottotipo corrente è valido per il nuovo tipo di carta, mantienilo
        if current_subtype not in subtypes:
            self.card_subtype.SetValue("")  # Resetta il sottotipo se non è valido

        if card_type == EnuCardType.MAGIA.value:
            self.spell_type.Enable()
            self.attack.Disable()
            self.health.Disable()
            #self.durability.Disable()

        elif card_type == EnuCardType.CREATURA.value:
            self.attack.Enable()
            self.health.Enable()
            #self.durability.Disable()
            self.spell_type.Disable()

        elif card_type == EnuCardType.LUOGO.value:
            self.attack.Disable()
            self.health.Disable()
            #self.durability.Enable()
            self.spell_type.Disable()

        elif card_type == EnuCardType.ARMA.value:
            self.attack.Enable()
            self.health.Disable()
            #self.durability.Enable()
            self.spell_type.Disable()

        elif card_type == EnuCardType.EROE.value:
            self.attack.Enable()
            self.health.Disable()
            #self.durability.Disable()
            self.spell_type.Disable()

        else:
            self.attack.Enable()
            self.health.Enable()
            #self.durability.Enable()
            self.spell_type.Enable()


    def on_type_change(self, event):
        """Gestisce il cambio del tipo di carta."""
        self.update_subtypes()


    def on_save(self, event):
        """Salva i filtri e chiude la finestra di dialogo."""
        self.EndModal(wx.ID_OK)



class DeckStatsDialog(BasicDialog):
    """Finestra di dialogo per visualizzare le statistiche di un mazzo."""

    def __init__(self, parent, stats):
        super().__init__(parent, title="Statistiche Mazzo", size=(300, 390))
        self.parent = parent
        self.stats = stats              # Inizializza l'attributo stats
        self.init_ui_elements()         # Inizializza gli elementi dell'interfaccia utente

    def init_ui(self):
        pass

    def init_ui_elements(self):
        """ Inizializza gli elementi dell'interfaccia utente. """

        # Imposta il colore di sfondo della finestra
        self.SetBackgroundColour('yellowe')

        # Crea un panel e imposta il suo colore di sfondo
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.YELLOW)  # Imposta un colore di sfondo contrastante

        # Crea un sizer verticale per il panel
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Titolo
        title = wx.StaticText(self.panel, label="Statistiche del Mazzo")
        title.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.sizer.Add(title, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        # Statistiche
        stats = self.stats
        for key, value in stats.items():
            row = wx.BoxSizer(wx.HORIZONTAL)
            row.Add(wx.StaticText(self.panel, label=f"{key}:"), flag=wx.LEFT, border=20)
            row.Add(wx.StaticText(self.panel, label=str(value)), flag=wx.LEFT | wx.RIGHT, border=20)
            self.sizer.Add(row, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)

        # Separatore tra le statistiche e il pulsante Chiudi
        self.sizer.Add(wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        # Pulsante Chiudi
        btn_close = wx.Button(self.panel, label="Chiudi", size=(100, 30))
        btn_close.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        self.sizer.Add(btn_close, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        # Imposta il sizer per il panel
        self.panel.SetSizer(self.sizer)

        self.Layout()               # Forza il ridisegno del layout



class CardEditDialog(SingleCardView):
    """Finestra di dialogo per aggiungere o modificare una carta."""

    def __init__(self, parent, card=None):
        title = "Modifica Carta" if card else "Aggiungi Carta"
        self.parent = parent
        self.card = card
        self.card_name = card.name if card else None  # Memorizza il nome della carta per la modifica
        super().__init__(parent, title=title, size=(400, 500))

    def init_ui_elements(self):
        """ Inizializza l'interfaccia utente. """

        self.SetBackgroundColour('yellow')
        #panel = wx.Panel(self)

        # Campi di input
        fields = [
            ("nome", wx.TextCtrl),  # Passa la classe wx.TextCtrl
            ("costo_mana", wx.SpinCtrl, {"min": 0, "max": 20}),  # Passa la classe wx.SpinCtrl e i kwargs
            ("tipo", wx.ComboBox, {"choices": [t.value for t in EnuCardType], "style": wx.CB_READONLY}),
            ("tipo_magia", wx.ComboBox, {"choices": [t.value for t in EnuSpellType], "style": wx.CB_READONLY}),
            ("sottotipo", wx.ComboBox, {"choices": [], "style": wx.CB_READONLY}),  # Inizialmente vuoto
            ("attacco", wx.SpinCtrl, {"min": 0, "max": 20}),
            ("vita", wx.SpinCtrl, {"min": 0, "max": 20}),
            ("durability", wx.SpinCtrl, {"min": 0, "max": 20}),
            ("rarita", wx.ComboBox, {"choices": [r.value for r in EnuRarity], "style": wx.CB_READONLY}),
            ("espansione", wx.ComboBox, {"choices": [e.value for e in EnuExpansion], "style": wx.CB_READONLY})
        ]

        # Crea i controlli UI e ottieni il sizer e il dizionario dei controlli
        self.sizer, control_dict = hp.create_ui_controls(self.panel, fields)

        # Assegna i controlli agli attributi della classe
        self.nome = control_dict["nome"]
        self.costo_mana = control_dict["costo_mana"]
        self.tipo = control_dict["tipo"]
        self.tipo_magia = control_dict["tipo_magia"]
        self.sottotipo = control_dict["sottotipo"]
        self.attacco = control_dict["attacco"]
        self.vita = control_dict["vita"]
        self.durability = control_dict["durability"]
        self.rarità = control_dict["rarita"]
        self.espansione = control_dict["espansione"]

        # Disabilito la casella "tipo_magia e integrita" di default
        #self.tipo_magia.Disable()
        #self.durability.Disable()

        # Collego l'evento di selezione del tipo di carta al metodo update_subtypes
        self.tipo.Bind(wx.EVT_COMBOBOX, self.on_type_change)

        # Selezione multipla delle classi
        self.classes_listbox = wx.CheckListBox(self.panel, choices=[h.value for h in EnuHero])
        self.sizer.Add(wx.StaticText(self.panel, label="Classi:"), flag=wx.LEFT | wx.RIGHT, border=10)
        self.sizer.Add(self.classes_listbox, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        # Pulsanti
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_save = wx.Button(self.panel, label="Salva")
        btn_close = wx.Button(self.panel, label="Chiudi")
        btn_sizer.Add(btn_save, flag=wx.RIGHT, border=10)
        btn_sizer.Add(btn_close)
        
        # Eventi
        btn_save.Bind(wx.EVT_BUTTON, self.on_save)
        btn_close.Bind(wx.EVT_BUTTON, self.on_close)

        self.sizer.Add(btn_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)
        self.panel.SetSizer(self.sizer)
        self.Layout()  # Forza il ridisegno del layout

        # Se è una modifica, pre-carica i dati della carta
        if self.card:
            self.nome.SetValue(self.card.name)
            self.costo_mana.SetValue(self.card.mana_cost)
            self.tipo.SetValue(self.card.card_type)
            self.tipo_magia.SetValue(self.card.spell_type) if self.card.spell_type else self.tipo_magia.SetValue("-")

            # Aggiorna i sottotipi in base al tipo di carta selezionato
            self.update_subtypes()

            # Imposta il valore corrente del sottotipo
            self.sottotipo.SetValue(self.card.card_subtype)

            # Imposta i valori di attacco e vita (se presenti)
            self.attacco.SetValue(self.card.attack) if self.card.attack else self.attacco.SetValue("-")
            self.vita.SetValue(self.card.health) if self.card.health else self.vita.SetValue("-")

            # Imposta il valore di integrità (se presente)
            self.durability.SetValue(self.card.durability) if self.card.durability else self.durability.SetValue("-")

            # Imposta i valori di rarità ed espansione
            self.rarità.SetValue(self.card.rarity) if self.card.rarity else self.rarità.SetValue("-")
            self.espansione.SetValue(self.card.expansion) if self.card.expansion else self.espansione.SetValue("-")

            # Seleziona le classi associate alla carta
            if self.card.class_name:
                selected_classes = hp.disassemble_classes_string(self.card.class_name)
                for i, class_name in enumerate(self.classes_listbox.GetItems()):
                    if class_name in selected_classes:
                        self.classes_listbox.Check(i)


    def update_subtypes(self):
        """ Aggiorna i sottotipi in base al tipo di carta selezionato. """

        card_type = self.tipo.GetValue()
        if card_type == EnuCardType.MAGIA.value:
            subtypes = [st.value for st in EnuSpellSubType]

        elif card_type == EnuCardType.CREATURA.value:
            subtypes = [st.value for st in EnuPetSubType]

        else:
            subtypes = []

        # Salva il sottotipo corrente
        current_subtype = self.sottotipo.GetValue()
        self.sottotipo.Clear()
        self.sottotipo.AppendItems(subtypes)
        
        # Se il sottotipo corrente è valido per il nuovo tipo di carta, mantienilo
        if current_subtype in subtypes:
            self.sottotipo.SetValue(current_subtype)
        else:
            self.sottotipo.SetValue("")  # Resetta il sottotipo se non è valido


    def get_card_name(self):
        """Restituisce il nome della carta modificata o aggiunta."""
        return self.card_name


    def on_type_change(self, event):
        """Gestisce il cambio del tipo di carta."""

        card_type = self.tipo.GetValue()

        # Abilita o disabilita la casella "tipo_magia" in base al tipo selezionato
        if card_type == EnuCardType.MAGIA.value:
            self.tipo_magia.Enable()
            self.attacco.Disable()
            self.vita.Disable()
            self.durability.Disable()
        else:
            self.tipo_magia.Disable()
            self.tipo_magia.SetValue("-")  # Resetta il valore se non è una magia

        # Gestisci la casella "durability" per le armi
        if card_type == EnuCardType.ARMA.value:
            self.durability.Enable()
            self.attacco.Enable()
            self.vita.Disable()
            self.vita.SetValue("-")
        else:
            self.durability.Disable()
            self.durability.SetValue("-")  # Resetta il valore se non è un'arma

        # Gestisci la casella "attacco" per le creature
        if card_type == EnuCardType.CREATURA.value:
            self.attacco.Enable()
            self.vita.Enable()
        else:
            self.attacco.Disable()
            self.vita.Disable()
            self.attacco.SetValue("-")
            self.vita.SetValue("-")

        if card_type == EnuCardType.LUOGO.value:
            self.attacco.Disable()
            self.vita.Disable()
            self.durability.Enable()
        else:
            self.durability.Disable()
            self.durability.SetValue("-")

        if card_type == EnuCardType.EROE.value:
            self.attacco.Disable()
            self.vita.Disable()
            self.durability.Disable()
        else:
            self.attacco.Disable()
            self.vita.Disable()
            self.durability.Disable()

        # Aggiorna i sottotipi
        self.update_subtypes()


    def on_save(self, event):
        """Salva la carta nel database."""

        self.card_name = None
        try:
            card_data = {
                "name": self.nome.GetValue(),
                "mana_cost": self.costo_mana.GetValue(),
                "card_type": self.tipo.GetValue(),
                "spell_type": self.tipo_magia.GetValue(),
                "card_subtype": self.sottotipo.GetValue(),
                "attack": self.attacco.GetValue(),
                "health": self.vita.GetValue(),
                "durability": self.durability.GetValue() if self.durability.IsEnabled() else None,
                "rarity": self.rarità.GetValue(),
                "expansion": self.espansione.GetValue()
            }

            # Ottieni le classi selezionate
            selected_classes = [self.classes_listbox.GetString(i) for i in self.classes_listbox.GetCheckedItems()]
            card_data["class_name"] = ", ".join(selected_classes)  # Salva come stringa separata da virgole

            if self.card:
                # Modifica la carta esistente
                self.card.name = card_data["name"]
                self.card.mana_cost = card_data["mana_cost"]
                self.card.card_type = card_data["card_type"]
                self.card.spell_type = card_data["spell_type"]
                self.card.card_subtype = card_data["card_subtype"]
                self.card.attack = card_data["attack"]
                self.card.health = card_data["health"]
                self.card.durability = card_data["durability"]
                self.card.rarity = card_data["rarity"]
                self.card.expansion = card_data["expansion"]
                self.card.class_name = card_data["class_name"]
                # Aggiorno il nome della carta nella variabile locale
                self.card_name = self.card.name 
            else:
                # Aggiungi una nuova carta
                new_card = Card(**card_data)
                session.add(new_card)
                self.card_name = new_card.name  # Memorizza il nome della nuova carta

            # Salva le modifiche nel database
            session.commit()
            self.EndModal(wx.ID_OK)                          # Chiudi la finestra e notifica che i dati sono stati salvati
            self.parent.load_cards()                         # Ricarica la lista delle carte
            self.parent.select_card_by_name(self.card_name)  # Seleziona e mette a fuoco la carta modificata
            self.Destroy()

        except Exception as e:
            log.error(f"Errore durante il salvataggio: {str(e)}")
            raise


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


    def on_close(self, event):
        """Chiude la finestra di dialogo."""
        self.parent.select_card_by_name(self.card_name)
        self.EndModal(wx.ID_CANCEL)
        
        




#@@# End del modulo
if __name__ == "__main__":
    print("Carico: %s" % __name__)