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



class DeckStatsDialog(wx.Dialog):
    """Finestra di dialogo per visualizzare le statistiche di un mazzo."""
    def __init__(self, parent, stats):
        super().__init__(parent, title="Statistiche Mazzo", size=(300, 333))
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
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Elementi UI
        self.search_ctrl = wx.SearchCtrl(panel)
        self.mana_cost = wx.SpinCtrl(panel, min=0, max=20)
        self.card_type = wx.ComboBox(panel, choices=["Tutti", "Creatura", "Magia", "Arma"], style=wx.CB_READONLY)
        self.rarity = wx.ComboBox(panel, choices=["Tutti", "Comune", "Rara", "Epica", "Leggendaria"], style=wx.CB_READONLY)

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
        super().__init__(parent, title="Collezione Carte", size=(700, 700))
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
        logging.info("Aggiunta di una nuova carta (non implementato)")
        wx.MessageBox("Funzionalità non implementata.", "Errore")
    
    def on_edit_card(self, event):
        """Apre modificare una carta esistente."""
        logging.info("Modifica una carta (non implementato)")
        wx.MessageBox("Funzionalità non implementata.", "Errore")
    
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
