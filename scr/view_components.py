"""
        Modulo per la gestione dei componenti delle views

        path:
            ./scr/view_components.py

    Descrizione:
        Questo modulo contiene classi base per la creazione di finestre di dialogo e componenti dell'interfaccia utente.
        La classe BasicView fornisce un'interfaccia comune per le finestre di dialogo, mentre le classi derivate come 
        SingleCardView e ListView forniscono funzionalità specifiche per la gestione di carte e elenchi.

"""

# Lib
import wx
from abc import ABC, abstractmethod
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

        #self.panel = wx.Panel(self)                     # Crea un pannello
        #self.sizer = wx.BoxSizer(wx.VERTICAL)           # Crea un sizer verticale
        #self.panel.SetSizer(self.sizer)                 # Imposta il sizer per il pannello
        #self.Center()                                   # Centra la finestra
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



class SingleCardView(BasicView):
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





#@@# End del modulo
if __name__ == "__main__":
    print("Carico: %s" % __name__)