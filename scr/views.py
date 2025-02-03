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

Utilizzo:
    Importare le classi necessarie e utilizzarle nell'interfaccia principale.
"""

import wx
import logging
from .db import session, Card
from utyls.enu_glob import EnuColors, ENUCARD, EnuExtraCard, EnuCardType, EnuHero, EnuRarity, EnuExpansion
from utyls import logger as log
#import pdb



class CardEditDialog(wx.Dialog):
    """Finestra di dialogo per aggiungere o modificare una carta."""

    def __init__(self, parent, card=None):
        title = "Modifica Carta" if card else "Aggiungi Carta"
        super().__init__(parent, title=title, size=(400, 400))
        self.SetBackgroundColour('green')
        self.card = card
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Campi di input
        fields = [
            ("Nome:", wx.TextCtrl(panel)),
            ("Classe:", wx.ComboBox(panel, choices=[h.value for h in EnuHero], style=wx.CB_READONLY)),
            ("Costo Mana:", wx.SpinCtrl(panel, min=0, max=20)),
            ("Tipo:", wx.ComboBox(panel, choices=[t.value for t in EnuCardType], style=wx.CB_READONLY)),
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

        # Pulsanti
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_save = wx.Button(panel, label="Salva")
        btn_close = wx.Button(panel, label="Chiudi")
        btn_sizer.Add(btn_save, flag=wx.RIGHT, border=10)
        btn_sizer.Add(btn_close)

        # Eventi
        btn_save.Bind(wx.EVT_BUTTON, self.on_save)
        btn_close.Bind(wx.EVT_BUTTON, lambda e: self.Close())

        sizer.Add(btn_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)
        panel.SetSizer(sizer)
        self.Centre()

        # Se è una modifica, pre-carica i dati della carta
        if self.card:
            self.nome.SetValue(self.card.name)
            self.classe.SetValue(self.card.class_name)
            self.costo_mana.SetValue(self.card.mana_cost)
            self.tipo.SetValue(self.card.card_type)
            self.rarità.SetValue(self.card.rarity)
            self.espansione.SetValue(self.card.expansion)

    def on_save(self, event):
        """Salva la carta nel database."""
        try:
            card_data = {
                "name": self.nome.GetValue(),
                "class_name": self.classe.GetValue(),
                "mana_cost": self.costo_mana.GetValue(),
                "card_type": self.tipo.GetValue(),
                "rarity": self.rarità.GetValue(),
                "expansion": self.espansione.GetValue()
            }

            if self.card:
                # Modifica la carta esistente
                self.card.name = card_data["name"]
                self.card.class_name = card_data["class_name"]
                self.card.mana_cost = card_data["mana_cost"]
                self.card.card_type = card_data["card_type"]
                self.card.rarity = card_data["rarity"]
                self.card.expansion = card_data["expansion"]
            else:
                # Aggiungi una nuova carta
                new_card = Card(**card_data)
                session.add(new_card)

            session.commit()
            self.EndModal(wx.ID_OK)  # Chiudi la finestra e notifica che i dati sono stati salvati

        except Exception as e:
            wx.MessageBox(f"Errore durante il salvataggio: {str(e)}", "Errore")



class DeckStatsDialog(wx.Dialog):
    """Finestra di dialogo per visualizzare le statistiche di un mazzo."""
    def __init__(self, parent, stats):
        super().__init__(parent, title="Statistiche Mazzo", size=(300, 390))
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

class FilterDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Filtri di Ricerca", size=(300, 300))
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



class CardCollectionDialog(wx.Dialog):
    def __init__(self, parent, deck_manager):
        super().__init__(parent, title="Collezione Carte", size=(800, 800))
        self.SetBackgroundColour('green')
        self.deck_manager = deck_manager
        self.current_filters = {}
        self.init_ui()
        self.load_cards()

    def init_ui(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Barra strumenti
        toolbar = wx.BoxSizer(wx.HORIZONTAL)
        self.search_ctrl = wx.SearchCtrl(panel)
        self.btn_filters = wx.Button(panel, label="Filtri Avanzati")
        toolbar.Add(self.search_ctrl, proportion=1, flag=wx.EXPAND)
        toolbar.Add(self.btn_filters, flag=wx.LEFT, border=10)
        
        # Lista carte
        self.card_list = wx.ListCtrl(
            panel, 
            style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.BORDER_SUNKEN
        )
        self.card_list.AppendColumn("Nome", width=200)
        self.card_list.AppendColumn("classe", width=150)
        self.card_list.AppendColumn("Mana", width=50)
        self.card_list.AppendColumn("Tipo", width=150)
        self.card_list.AppendColumn("Rarità", width=100)
        self.card_list.AppendColumn("Espansione", width=150)
        
        # Pulsanti azione
        btn_panel = wx.Panel(panel)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        for label in ["Aggiungi", "Modifica", "Elimina", "Chiudi"]:
            btn = wx.Button(btn_panel, label=label)
            btn_sizer.Add(btn, flag=wx.RIGHT, border=5)
            if label == "Aggiungi":
                btn.Bind(wx.EVT_BUTTON, self.on_add_card)
            elif label == "Modifica":
                btn.Bind(wx.EVT_BUTTON, self.on_edit_card)
            elif label == "Elimina":
                btn.Bind(wx.EVT_BUTTON, self.on_delete_card)
            else:
                btn.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        
        # Assemblaggio finale
        btn_panel.SetSizer(btn_sizer)
        sizer.Add(toolbar, flag=wx.EXPAND|wx.ALL, border=10)
        sizer.Add(self.card_list, proportion=1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        sizer.Add(btn_panel, flag=wx.ALIGN_RIGHT|wx.ALL, border=10)
        
        # Eventi
        self.search_ctrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.on_search)
        self.btn_filters.Bind(wx.EVT_BUTTON, self.on_show_filters)
        
        panel.SetSizer(sizer)
        self.Centre()
    
    def load_cards(self, filters=None):
        """Carica le carte dal database applicando i filtri."""
        self.card_list.DeleteAllItems()
        query = session.query(Card)
        
        if filters:
            if filters.get("name"):
                query = query.filter(Card.name.ilike(f"%{filters['name']}%"))
            if filters.get("mana_cost", 0) > 0:
                query = query.filter(Card.mana_cost == filters["mana_cost"])
            if filters.get("card_type") not in [None, "Tutti"]:
                query = query.filter(Card.card_type == filters["card_type"])
            if filters.get("rarity") not in [None, "Tutti"]:
                query = query.filter(Card.rarity == filters["rarity"])

        # Aggiungi le carte alla lista
        for card in query.order_by(Card.mana_cost, Card.name):
            self.card_list.Append([
                card.name,
                card.class_name,
                str(card.mana_cost),
                card.card_type,
                card.rarity,
                card.expansion
            ])

    def on_search(self, event):
        """Gestisce la ricerca testuale."""
        self.current_filters["name"] = self.search_ctrl.GetValue()
        self.load_cards(self.current_filters)
    
    def on_show_filters(self, event):
        """Mostra la finestra dei filtri avanzati."""
        dlg = FilterDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.current_filters.update({
                "name": dlg.search_ctrl.GetValue(),
                "mana_cost": dlg.mana_cost.GetValue(),
                "card_type": dlg.card_type.GetValue(),
                "rarity": dlg.rarity.GetValue()
            })
            self.load_cards(self.current_filters)
        dlg.Destroy()

    def on_add_card(self, event):
        """Apre la finestra per aggiungere una nuova carta."""
        dlg = CardEditDialog(self)
        if dlg.ShowModal() == wx.ID_OK:  # Se l'utente ha premuto "Salva"
            self.load_cards(self.current_filters)  # Ricarica la lista delle carte
        dlg.Destroy()

    def on_edit_card(self, event):
        """Apre la finestra per modificare una carta esistente."""
        selected = self.card_list.GetFirstSelected()
        if selected != -1:
            name = self.card_list.GetItemText(selected)
            card = session.query(Card).filter_by(name=name).first()
            if card:
                dlg = CardEditDialog(self, card)
                if dlg.ShowModal() == wx.ID_OK:  # Se l'utente ha premuto "Salva"
                    self.load_cards(self.current_filters)  # Ricarica la lista delle carte
                dlg.Destroy()
            else:
                wx.MessageBox("Carta non trovata nel database.", "Errore")
        else:
            wx.MessageBox("Seleziona una carta da modificare.", "Errore")

    def on_delete_card(self, event):
        """Elimina la carta selezionata."""

        selected = self.card_list.GetFirstSelected()
        if selected != -1:
            name = self.card_list.GetItemText(selected)
            if wx.MessageBox(f"Eliminare la carta '{name}'?", "Conferma", wx.YES_NO) == wx.YES:
                card = session.query(Card).filter_by(name=name).first()
                if card:
                    session.delete(card)
                    session.commit()
                    self.card_list.DeleteAllItems() # Svuota la lista delle carte
                    self.load_cards(self.current_filters)
                    logging.info(f"Carta '{name}' eliminata")
                else:
                    logging.error(f"Carta '{name}' non trovata")
                    wx.MessageBox("Carta non trovata nel database.", "Errore")
        else:
                logging.error("Nessuna carta selezionata")
                wx.MessageBox("Seleziona una carta da eliminare.", "Errore")




#@@@# Start del modulo
if __name__ != "__main__":
    print("Carico: %s." % __name__)
