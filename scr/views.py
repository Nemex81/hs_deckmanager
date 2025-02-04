"""
    views.py

    Modulo per le finestre di dialogo dell'interfaccia utente.

    path:
        scr/views.py

    Descrizione:
        Contiene le classi per:
        - DeckStatsDialog: Visualizza le statistiche di un mazzo
        - FilterDialog: Gestisce i filtri di ricerca
        - CardCollectionDialog: Mostra la collezione di carte
        - CardEditDialog: Finestra di dialogo per aggiungere o modificare una carta

    Note:
        Le finestre di dialogo sono implementate con wxPython.
        Per installare wxPython, eseguire il comando `pip install wxPython`.

"""

# lib
import wx
from .db import session, Card
from utyls.helper import disassemble_classes_string, assemble_classes_string
from utyls.enu_glob import EnuColors, ENUCARD, EnuExtraCard, EnuCardType, EnuSpellSubType, EnuPetSubType, EnuHero, EnuRarity, EnuExpansion
from utyls import logger as log
#import pdb



class FilterDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Filtri di Ricerca", size=(300, 300))
        self.parent = parent
        self.SetBackgroundColour('green')
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Elementi UI
        self.search_ctrl = wx.SearchCtrl(panel)
        self.mana_cost = wx.SpinCtrl(panel, min=0, max=20)
        self.card_type = wx.ComboBox(panel, choices=["Tutti"] + [t.value for t in EnuCardType], style=wx.CB_READONLY)  # Usa EnuCardType
        self.rarity = wx.ComboBox(panel, choices=["Tutti"] + [r.value for r in EnuRarity], style=wx.CB_READONLY)  # Usa EnuRarity

        # Layout
        controls = [
            ("Nome:", self.search_ctrl),
            ("Costo Mana:", self.mana_cost),
            ("Tipo:", self.card_type),
            ("Rarità:", self.rarity)
        ]
        for label, control in controls:
            row = wx.BoxSizer(wx.HORIZONTAL)
            row.Add(wx.StaticText(panel, label=label), flag=wx.LEFT|wx.RIGHT, border=10)
            row.Add(control, proportion=1)
            sizer.Add(row, flag=wx.EXPAND|wx.ALL, border=5)

        # Pulsanti
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_apply = wx.Button(panel, label="Applica")
        self.btn_cancel = wx.Button(panel, label="Annulla")
        btn_sizer.Add(self.btn_apply, flag=wx.RIGHT, border=10)
        btn_sizer.Add(self.btn_cancel)

        # Eventi
        self.btn_apply.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_OK))
        self.btn_cancel.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))

        sizer.Add(btn_sizer, flag=wx.ALIGN_RIGHT|wx.ALL, border=10)
        panel.SetSizer(sizer)
        self.Centre()



class DeckStatsDialog(wx.Dialog):
    """Finestra di dialogo per visualizzare le statistiche di un mazzo."""
    def __init__(self, parent, stats):
        super().__init__(parent, title="Statistiche Mazzo", size=(300, 390))
        self.parent = parent
        self.SetBackgroundColour('green')
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Titolo
        title = wx.StaticText(panel, label="Statistiche del Mazzo")
        title.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer.Add(title, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)
        
        # Statistiche
        for key, value in stats.items():
            row = wx.BoxSizer(wx.HORIZONTAL)
            row.Add(wx.StaticText(panel, label=f"{key}:"), flag=wx.LEFT, border=20)
            row.Add(wx.StaticText(panel, label=str(value)), flag=wx.LEFT|wx.RIGHT, border=20)
            sizer.Add(row, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=5)

        # impostiamo un separatore tra le statistiche delmazzo ed il pusante chiudi.
        sizer.Add(wx.StaticLine(panel), flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=10)

        # Pulsante Chiudi
        btn_close = wx.Button(panel, label="Chiudi", size=(100, 30))
        btn_close.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        sizer.Add(btn_close, flag=wx.ALIGN_CENTER|wx.ALL, border=10)
        
        panel.SetSizer(sizer)
        self.Centre()



class CardEditDialog(wx.Dialog):
    """Finestra di dialogo per aggiungere o modificare una carta."""

    def __init__(self, parent, card=None):
        title = "Modifica Carta" if card else "Aggiungi Carta"
        super().__init__(parent, title=title, size=(400, 500))
        self.parent = parent
        self.SetBackgroundColour('green')
        self.card = card
        self.card_name = card.name if card else None  # Memorizza il nome della carta per la modifica
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Campi di input
        fields = [
            ("Nome:", wx.TextCtrl(panel)),
            ("Costo Mana:", wx.SpinCtrl(panel, min=0, max=20)),
            ("Tipo:", wx.ComboBox(panel, choices=[t.value for t in EnuCardType], style=wx.CB_READONLY)),
            ("Sottotipo:", wx.ComboBox(panel, style=wx.CB_READONLY)),  # Sottotipo dinamico
            ("Rarità:", wx.ComboBox(panel, choices=[r.value for r in EnuRarity], style=wx.CB_READONLY)),
            ("Espansione:", wx.ComboBox(panel, choices=[e.value for e in EnuExpansion], style=wx.CB_READONLY))
        ]

        # Aggiungi i campi alla finestra
        for label, control in fields:
            row = wx.BoxSizer(wx.HORIZONTAL)
            row.Add(wx.StaticText(panel, label=label), flag=wx.LEFT | wx.RIGHT, border=10)
            row.Add(control, proportion=1)
            sizer.Add(row, flag=wx.EXPAND | wx.ALL, border=5)
            setattr(self, label.lower().replace(" ", "_").replace(":", ""), control)

        # Selezione multipla delle classi
        self.classes_listbox = wx.CheckListBox(panel, choices=[h.value for h in EnuHero])
        sizer.Add(wx.StaticText(panel, label="Classi:"), flag=wx.LEFT | wx.RIGHT, border=10)
        sizer.Add(self.classes_listbox, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        # Pulsanti
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_save = wx.Button(panel, label="Salva")
        btn_close = wx.Button(panel, label="Chiudi")
        btn_sizer.Add(btn_save, flag=wx.RIGHT, border=10)
        btn_sizer.Add(btn_close)

        # Eventi
        btn_save.Bind(wx.EVT_BUTTON, self.on_save)
        btn_close.Bind(wx.EVT_BUTTON, self.on_close)

        sizer.Add(btn_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)
        panel.SetSizer(sizer)
        self.Centre()

        # Se è una modifica, pre-carica i dati della carta
        if self.card:
            self.nome.SetValue(self.card.name)
            self.costo_mana.SetValue(self.card.mana_cost)
            self.tipo.SetValue(self.card.card_type)
            self.sottotipo.SetValue(self.card.card_subtype if self.card.card_subtype else "")
            self.rarità.SetValue(self.card.rarity)
            self.espansione.SetValue(self.card.expansion)

            # Seleziona le classi associate alla carta
            if self.card.class_name:
                #selected_classes = self.card.class_name.split(", ")
                selected_classes= disassemble_classes_string(self.card.class_name)
                for i, class_name in enumerate(self.classes_listbox.GetItems()):
                    if class_name in selected_classes:
                        self.classes_listbox.Check(i)

        # Aggiorna i sottotipi in base al tipo selezionato
        self.update_subtypes()

    def update_subtypes(self):
        """Aggiorna i sottotipi in base al tipo di carta selezionato."""
        card_type = self.tipo.GetValue()
        if card_type == EnuCardType.MAGIA.value:
            subtypes = [st.value for st in EnuSpellSubType]
        elif card_type == EnuCardType.CREATURA.value:
            subtypes = [st.value for st in EnuPetSubType]
        else:
            subtypes = []

        self.sottotipo.Clear()
        self.sottotipo.AppendItems(subtypes)

    def get_card_name(self):
        """Restituisce il nome della carta modificata o aggiunta."""
        return self.card_name

    def on_type_change(self, event):
        """Gestisce il cambio del tipo di carta."""
        self.update_subtypes()

    def on_save(self, event):
        """Salva la carta nel database."""

        self.card_name = None
        try:
            card_data = {
                "name": self.nome.GetValue(),
                "mana_cost": self.costo_mana.GetValue(),
                "card_type": self.tipo.GetValue(),
                "card_subtype": self.sottotipo.GetValue(),
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
                self.card.card_subtype = card_data["card_subtype"]
                self.card.rarity = card_data["rarity"]
                self.card.expansion = card_data["expansion"]
                self.card.class_name = card_data["class_name"]
                self.card_name = self.card.name  # Aggiorna il nome della carta
            else:
                # Aggiungi una nuova carta
                new_card = Card(**card_data)
                session.add(new_card)
                self.card_name = new_card.name  # Memorizza il nome della nuova carta

            session.commit()
            self.EndModal(wx.ID_OK)  # Chiudi la finestra e notifica che i dati sono stati salvati
            wx.MessageBox("Dati della carta salvati con successo!", "Successo")
            self.parent.select_card_by_name(self.card_name)
            self.Destroy()

        except Exception as e:
            log.error(f"Errore durante il salvataggio: {str(e)}")
            raise

    def on_close(self, event):
        """Chiude la finestra di dialogo."""

        self.EndModal(wx.ID_CANCEL)
        self.parent.select_card_by_name(self.card_name)
        self.Destroy()



class CardManagerDialog(wx.Dialog):
    """
        Finestra generica per gestire le carte (collezione o mazzo).

        :param parent:
                                Finestra principale (frame), genitore della finestra di dialogo
                                :param deck_manager: Gestore dei mazzi
                                :param mode: Modalità della finestra ("collection" o "deck")
                                :param deck_name: Nome del mazzo (se la modalità è "deck")
    """

class CardManagerDialog(wx.Dialog):
    """Finestra madre per gestire le carte (collezione o mazzo)."""

    def __init__(self, parent, deck_manager, mode="collection", deck_name=None):
        title = "Collezione Carte" if mode == "collection" else f"Mazzo: {deck_name}"
        super().__init__(parent, title=title, size=(1200, 800))
        self.parent = parent
        self.SetBackgroundColour('green')
        self.deck_manager = deck_manager
        self.mode = mode  # "collection" o "deck"
        self.deck_name = deck_name
        self.deck_content = self.deck_manager.get_deck(deck_name) if mode == "deck" else None
        self.Centre()  # Centra la finestra
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Informazioni generali (solo per la modalità "deck")
        if self.mode == "deck":
            info_sizer = wx.BoxSizer(wx.HORIZONTAL)
            info_sizer.Add(wx.StaticText(panel, label=f"Nome: {self.deck_content['name']}"), flag=wx.LEFT | wx.RIGHT, border=10)
            info_sizer.Add(wx.StaticText(panel, label=f"Classe: {self.deck_content['player_class']}"), flag=wx.LEFT | wx.RIGHT, border=10)
            info_sizer.Add(wx.StaticText(panel, label=f"Formato: {self.deck_content['game_format']}"), flag=wx.LEFT | wx.RIGHT, border=10)
            info_sizer.Add(wx.StaticText(panel, label=f"Carte: {len(self.deck_content['cards'])}"), flag=wx.LEFT | wx.RIGHT, border=10)
            sizer.Add(info_sizer, flag=wx.EXPAND | wx.ALL, border=10)

        # Lista delle carte
        self.card_list = wx.ListCtrl(
            panel,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN
        )
        self.card_list.AppendColumn("Nome", width=250)
        self.card_list.AppendColumn("Mana", width=50)
        self.card_list.AppendColumn("Quantità", width=80)
        self.card_list.AppendColumn("Tipo", width=120)
        self.card_list.AppendColumn("Rarità", width=120)
        self.card_list.AppendColumn("Espansione", width=500)
        sizer.Add(self.card_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Pulsanti azione
        btn_panel = wx.Panel(panel)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        for label in ["Aggiungi Carta", "Modifica Carta", "Elimina Carta", "Chiudi"]:
            btn = wx.Button(btn_panel, label=label)
            btn_sizer.Add(btn, flag=wx.RIGHT, border=5)
            if label == "Aggiungi Carta":
                btn.Bind(wx.EVT_BUTTON, self.on_add_card)
            elif label == "Modifica Carta":
                btn.Bind(wx.EVT_BUTTON, self.on_edit_card)
            elif label == "Elimina Carta":
                btn.Bind(wx.EVT_BUTTON, self.on_delete_card)
            else:
                btn.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        
        btn_panel.SetSizer(btn_sizer)
        sizer.Add(btn_panel, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        panel.SetSizer(sizer)
        self.load_cards()

    def load_cards(self):
        """Carica le carte nella lista in base alla modalità."""

        self.card_list.DeleteAllItems()
        if self.mode == "collection":
            # Carica tutte le carte della collezione
            cards = session.query(Card).all()
            for card in cards:
                self.card_list.Append([
                    card.name,
                    str(card.mana_cost),
                    "1",  # Quantità fissa per la collezione
                    card.card_type,
                    card.rarity,
                    card.expansion
                ])

        elif self.mode == "deck":
            # Carica le carte del mazzo
            for card_data in self.deck_content["cards"]:
                card = session.query(Card).filter_by(name=card_data["name"]).first()
                if card:
                    self.card_list.Append([
                        card.name,
                        str(card.mana_cost),
                        str(card_data["quantity"]),
                        card.card_type,
                        card.rarity,
                        card.expansion
                    ])

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
                elif self.mode == "deck":
                    # Aggiungi la carta al mazzo (se non è già presente)
                    for card_data in self.deck_content["cards"]:
                        if card_data["name"] == card_name:
                            wx.MessageBox("La carta è già presente nel mazzo.", "Errore")
                            return

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
                    self.load_cards()
                    wx.MessageBox(f"Carta '{card_name}' modificata.", "Successo")
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
            if wx.MessageBox(f"Eliminare la carta '{card_name}'?", "Conferma", wx.YES_NO) == wx.YES:
                if self.mode == "collection":
                    # Elimina la carta dalla collezione
                    card = session.query(Card).filter_by(name=card_name).first()
                    if card:
                        session.delete(card)
                        session.commit()
                        self.load_cards()
                        wx.MessageBox(f"Carta '{card_name}' eliminata dalla collezione.", "Successo")
                    else:
                        wx.MessageBox("Carta non trovata nel database.", "Errore")
                elif self.mode == "deck":
                    # Rimuovi la carta dal mazzo
                    self.deck_content["cards"] = [
                        card_data for card_data in self.deck_content["cards"]
                        if card_data["name"] != card_name
                    ]
                    self.load_cards()
                    wx.MessageBox(f"Carta '{card_name}' eliminata dal mazzo.", "Successo")
        else:
            wx.MessageBox("Seleziona una carta da eliminare.", "Errore")



class DeckViewDialog(CardManagerDialog):
    """Finestra per gestire le carte di un mazzo."""

    def __init__(self, parent, deck_manager, deck_name):
        super().__init__(parent, deck_manager, mode="deck", deck_name=deck_name)
        self.init_search()

    def init_search(self):
        """Aggiunge la barra di ricerca."""
        panel = self.GetChildren()[0]  # Ottieni il pannello principale
        sizer = panel.GetSizer()

        # Barra di ricerca
        search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.search_ctrl = wx.SearchCtrl(panel)
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.on_search)
        search_sizer.Add(self.search_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        # Aggiungi la barra di ricerca al layout
        sizer.Insert(0, search_sizer, flag=wx.EXPAND | wx.ALL, border=10)

    def on_search(self, event):
        """Gestisce la ricerca testuale."""
        search_text = self.search_ctrl.GetValue()
        self.load_cards(filters={"name": search_text})



#class CardCollectionDialog(wx.Dialog):
class CardCollectionDialog(CardManagerDialog):
    """Finestra per gestire la collezione di carte."""

    def __init__(self, parent, deck_manager):
        super().__init__(parent, deck_manager, mode="collection")
        self.init_search_and_filters()

    def init_search_and_filters(self):
        """Aggiunge la barra di ricerca e i filtri."""
        panel = self.GetChildren()[0]  # Ottieni il pannello principale
        sizer = panel.GetSizer()

        # Barra di ricerca
        search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.search_ctrl = wx.SearchCtrl(panel)
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.on_search)
        search_sizer.Add(self.search_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        # Pulsante filtri
        self.btn_filters = wx.Button(panel, label="Filtri Avanzati")
        self.btn_filters.Bind(wx.EVT_BUTTON, self.on_show_filters)
        search_sizer.Add(self.btn_filters, flag=wx.LEFT | wx.RIGHT, border=5)

        # Aggiungi la barra di ricerca e i filtri al layout
        sizer.Insert(0, search_sizer, flag=wx.EXPAND | wx.ALL, border=10)

    def on_search(self, event):
        """Gestisce la ricerca testuale."""
        search_text = self.search_ctrl.GetValue()
        self.load_cards(filters={"name": search_text})

    def on_show_filters(self, event):
        """Mostra la finestra dei filtri avanzati."""
        dlg = FilterDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            filters = {
                "name": dlg.search_ctrl.GetValue(),
                "mana_cost": dlg.mana_cost.GetValue(),
                "card_type": dlg.card_type.GetValue(),
                "rarity": dlg.rarity.GetValue()
            }
            self.load_cards(filters=filters)
        dlg.Destroy()





#@@@# Start del modulo
if __name__ != "__main__":
    print("Carico: %s." % __name__)
