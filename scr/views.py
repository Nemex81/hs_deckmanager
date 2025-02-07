"""
    views.py

    Modulo per le finestre di dialogo dell'interfaccia utente.

    path:
        scr/views.py

    Descrizione:
        Contiene le classi per:
        - CardManagerDialog: Finestra madre di dialogo per la gestione delle carte (collezione o mazzo)
        - DeckStatsDialog: Visualizza le statistiche di un mazzo
        - FilterDialog: Gestisce i filtri di ricerca
        - CardCollectionDialog: Mostra la collezione di carte
        - CardEditDialog: Finestra di dialogo per aggiungere o modificare una carta
        - DeckViewDialog: Visualizza i dettagli per un mazzo di carte selezionato

    Note:
        Questo modulo utilizza CardManagerDialog per la gestione delle carte, che può essere utilizzato per visualizzare la collezione di carte o i dettagli di un mazzo.

"""

# lib
import wx
from .db import session, Card, DeckCard, Deck
from utyls.helper import disassemble_classes_string, assemble_classes_string
from utyls.enu_glob import EnuColors, ENUCARD, EnuExtraCard, EnuCardType, EnuSpellSubType, EnuPetSubType, EnuHero, EnuRarity, EnuExpansion
from utyls import logger as log
#import pdb



#@@@# sezione funzioni helper specifiche per wx

def create_control(panel, label, control_class, **kwargs):
    """
    Crea un controllo UI con una label associata.
    
    :param panel: Il pannello a cui aggiungere il controllo.
    :param label: La label del controllo.
    :param control_class: La classe del controllo da creare.
    :param kwargs: Argomenti aggiuntivi per il controllo.
    :return: Il controllo creato e la riga contenente la label e il controllo.
    """
    row = wx.BoxSizer(wx.HORIZONTAL)
    row.Add(wx.StaticText(panel, label=label), flag=wx.RIGHT, border=10)
    control = control_class(panel, **kwargs)
    row.Add(control, proportion=1, flag=wx.EXPAND)
    return control, row


def create_button(panel, label, event_handler=None):
    """
    Crea un pulsante e collega un gestore di eventi.
    
    :param panel: Il pannello a cui aggiungere il pulsante.
    :param label: La label del pulsante.
    :param event_handler: Il gestore di eventi da collegare.
    :return: Il pulsante creato.
    """
    btn = wx.Button(panel, label=label)
    btn.Bind(wx.EVT_BUTTON, event_handler)
    return btn


def create_ui_controls(panel, controls):
    """
    Crea e posiziona i controlli UI in un pannello.
    
    :param panel: Il pannello a cui aggiungere i controlli.
    :param controls: Lista di tuple (label, control_class, kwargs) per i controlli.
    :return: Il sizer contenente i controlli e un dizionario con i controlli creati.
    """

    sizer = wx.BoxSizer(wx.VERTICAL)
    control_dict = {}
    for control_info in controls:
        if len(control_info) == 2:
            label, control_class = control_info
            kwargs = {}
        elif len(control_info) == 3:
            label, control_class, kwargs = control_info
        else:
            raise ValueError("Ogni controllo deve essere una tupla di 2 o 3 elementi: (label, control_class[, kwargs])")

        control, row = create_control(panel=panel, label=label, control_class=control_class, **kwargs)
        sizer.Add(row, flag=wx.EXPAND | wx.ALL, border=5)
        control_dict[label.lower().replace(" ", "_")] = control

    return sizer, control_dict



#@@@# sezione gestione delle finestre di dialogo



class FilterDialog(wx.Dialog):
    """ Finestra di dialogo per i filtri di ricerca. """

    def __init__(self, parent):
        super().__init__(parent, title="Filtri di Ricerca", size=(300, 300))
        self.parent = parent
        self.SetBackgroundColour('green')
        panel = wx.Panel(self)

        # Aggiungi "Qualsiasi" come prima opzione per il costo mana
        mana_choices = ["Qualsiasi"] + [str(i) for i in range(0, 21)]

        controls = [
            ("nome", wx.TextCtrl),
            ("costo_mana", wx.ComboBox, {"choices": mana_choices, "style": wx.CB_READONLY}),
            ("tipo", wx.ComboBox, {"choices": ["Tutti"] + [t.value for t in EnuCardType], "style": wx.CB_READONLY}),
            ("sottotipo", wx.ComboBox, {"choices": ["Tutti"] + [st.value for st in EnuSpellSubType], "style": wx.CB_READONLY}),
            ("rarita", wx.ComboBox, {"choices": ["Tutti"] + [r.value for r in EnuRarity], "style": wx.CB_READONLY}),
            ("espansione", wx.ComboBox, {"choices": ["Tutti"] + [e.value for e in EnuExpansion], "style": wx.CB_READONLY})
        ]

        sizer, control_dict = create_ui_controls(panel, controls)

        self.search_ctrl = control_dict["nome"]
        self.mana_cost = control_dict["costo_mana"]
        self.card_type = control_dict["tipo"]
        self.card_subtype = control_dict["sottotipo"]
        self.rarity = control_dict["rarita"]
        self.expansion = control_dict["espansione"]

        # Imposta i valori predefiniti
        self.reset_filters()

        # Collega l'evento di selezione del tipo di carta al metodo update_subtypes
        self.card_type.Bind(wx.EVT_COMBOBOX, self.on_type_change)

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
        # Aggiorna i sottotipi in base al tipo selezionato
        self.update_subtypes()

    def reset_filters(self):
        """ Resetta i filtri ai valori predefiniti. """
        self.search_ctrl.SetValue("")
        self.mana_cost.SetValue("Qualsiasi")  # Imposta "Qualsiasi" come valore predefinito
        self.card_type.SetValue("Tutti")
        self.card_subtype.SetValue("Tutti")
        self.rarity.SetValue("Tutti")
        self.expansion.SetValue("Tutti")

    def update_subtypes(self):
        """ Aggiorna i sottotipi in base al tipo di carta selezionato. """
        card_type = self.card_type.GetValue()
        if card_type == EnuCardType.MAGIA.value:
            subtypes = [st.value for st in EnuSpellSubType]
        elif card_type == EnuCardType.CREATURA.value:
            subtypes = [st.value for st in EnuPetSubType]
        else:
            subtypes = []

        current_subtype = self.card_subtype.GetValue()
        self.card_subtype.Clear()
        self.card_subtype.AppendItems(subtypes)
        if current_subtype not in subtypes:
            self.card_subtype.SetValue("")  # Resetta il sottotipo se non è valido

    def on_type_change(self, event):
        """Gestisce il cambio del tipo di carta."""
        self.update_subtypes()

    def on_save(self, event):
        """Salva i filtri e chiude la finestra di dialogo."""
        self.EndModal(wx.ID_OK)

    def on_save(self, event):
        """Salva i filtri e chiude la finestra di dialogo."""
        self.EndModal(wx.ID_OK)



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

        # Campi di input
        fields = [
            ("nome", wx.TextCtrl),  # Passa la classe wx.TextCtrl
            ("costo_mana", wx.SpinCtrl, {"min": 0, "max": 20}),  # Passa la classe wx.SpinCtrl e i kwargs
            ("tipo", wx.ComboBox, {"choices": [t.value for t in EnuCardType], "style": wx.CB_READONLY}),
            ("sottotipo", wx.ComboBox, {"choices": [], "style": wx.CB_READONLY}),  # Inizialmente vuoto
            ("rarita", wx.ComboBox, {"choices": [r.value for r in EnuRarity], "style": wx.CB_READONLY}),
            ("espansione", wx.ComboBox, {"choices": [e.value for e in EnuExpansion], "style": wx.CB_READONLY})
        ]

        # Crea i controlli UI e ottieni il sizer e il dizionario dei controlli
        sizer, control_dict = create_ui_controls(panel, fields)

        # Assegna i controlli agli attributi della classe
        self.nome = control_dict["nome"]
        self.costo_mana = control_dict["costo_mana"]
        self.tipo = control_dict["tipo"]
        self.sottotipo = control_dict["sottotipo"]
        self.rarità = control_dict["rarita"]
        self.espansione = control_dict["espansione"]

        # Collega l'evento di selezione del tipo di carta al metodo update_subtypes
        self.tipo.Bind(wx.EVT_COMBOBOX, self.on_type_change)

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

            # Aggiorna i sottotipi in base al tipo di carta selezionato
            self.update_subtypes()

            # Imposta il valore corrente del sottotipo
            self.sottotipo.SetValue(self.card.card_subtype)

            self.rarità.SetValue(self.card.rarity)
            self.espansione.SetValue(self.card.expansion)

            # Seleziona le classi associate alla carta
            if self.card.class_name:
                selected_classes = disassemble_classes_string(self.card.class_name)
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
            self.parent.load_cards()  # Ricarica la lista delle carte
            self.parent.select_card_by_name(self.card_name)  # Seleziona e mette a fuoco la carta modificata
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

    :param parent: Finestra principale (frame), genitore della finestra di dialogo
    :param deck_manager: Gestore dei mazzi
    :param mode: Modalità della finestra ("collection" o "deck")
    :param deck_name: Nome del mazzo (se la modalità è "deck")
    """

    def __init__(self, parent, deck_manager, mode="collection", deck_name=None):
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
        
        # Aggiungi la colonna "Quantità" o "Classe" in base alla modalità
        if self.mode == "deck":
            self.card_list.AppendColumn("Quantità", width=80)
        else:
            self.card_list.AppendColumn("Classe", width=120)
            
        self.card_list.AppendColumn("Tipo", width=120)
        self.card_list.AppendColumn("Sottotipo", width=120)
        self.card_list.AppendColumn("Rarità", width=120)
        self.card_list.AppendColumn("Espansione", width=500)
        sizer.Add(self.card_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Pulsanti azione
        btn_panel = wx.Panel(panel)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Aggiungi il pulsante "Aggiorna"
        #btn_reset = wx.Button(btn_panel, label="Aggiorna")
        #btn_reset.Bind(wx.EVT_BUTTON, self.on_reset)
        #btn_sizer.Add(btn_reset, flag=wx.RIGHT, border=5)

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
        """Carica le carte nella lista in base alla modalità e ai filtri."""
        self.card_list.DeleteAllItems()
        if self.mode == "collection":
            # Carica tutte le carte della collezione
            query = session.query(Card)
            if filters:
                # Applica i filtri in modo combinato
                if filters.get("name"):
                    query = query.filter(Card.name.ilike(f"%{filters['name']}%"))
                if filters.get("mana_cost") and filters["mana_cost"] not in ["Qualsiasi", ""]:
                    query = query.filter(Card.mana_cost == int(filters["mana_cost"]))
                if filters.get("card_type") not in [None, "Tutti", "tutti", "", " "]:
                    query = query.filter(Card.card_type == filters["card_type"])
                if filters.get("card_subtype") not in [None, "Tutti", "tutti", "", " "]:
                    query = query.filter(Card.card_subtype == filters["card_subtype"])
                if filters.get("rarity") not in [None, "Tutti", "tutti", "", " "]:
                    query = query.filter(Card.rarity == filters["rarity"])
                if filters.get("expansion") not in [None, "Tutti", "tutti", "", " "]:
                    query = query.filter(Card.expansion == filters["expansion"])


            log.info(f"Carte trovate: {query.count()}")
            cards = query.order_by(Card.mana_cost, Card.name).all()
            for card in cards:
                self.card_list.Append([
                    #card.id,
                    card.name,
                    str(card.mana_cost),
                    card.class_name if card.class_name else "Nessuna",  # Mostra la classe eroe
                    card.card_type,
                    card.card_subtype,
                    card.rarity,
                    card.expansion
                ])
        elif self.mode == "deck":
            if not self.deck_content:
                raise ValueError("Deck content non è stato inizializzato correttamente.")
            
            # Carica le carte del mazzo
            deck_cards = session.query(DeckCard).filter_by(deck_id=self.deck_content["id"]).all()
            for deck_card in deck_cards:
                card = session.query(Card).filter_by(id=deck_card.card_id).first()
                if card:
                    # Applica i filtri (se presenti)
                    if filters:
                        if filters.get("name") and filters["name"].lower() not in card.name.lower():
                            continue
                        if filters.get("mana_cost") and filters["mana_cost"] != "Qualsiasi" and card.mana_cost != int(filters["mana_cost"]):
                            continue
                        if filters.get("card_type") not in [None, "Tutti"] and card.card_type != filters["card_type"]:
                            continue
                        if filters.get("card_subtype") not in [None, "Tutti"] and card.card_subtype != filters["card_subtype"]:
                            continue
                        if filters.get("rarity") not in [None, "Tutti"] and card.rarity != filters["rarity"]:
                            continue
                        if filters.get("expansion") not in [None, "Tutti"] and card.expansion != filters["expansion"]:
                            continue

                    self.card_list.Append([
                        #card.id,
                        card.name,
                        str(card.mana_cost),
                        str(deck_card.quantity),  # Mostra la quantità nel mazzo
                        card.card_type,
                        card.card_subtype,
                        card.rarity,
                        card.expansion
                    ])

    def last_veri_load_cards(self, filters=None):
        """Carica le carte nella lista in base alla modalità e ai filtri."""

        self.card_list.DeleteAllItems()
        if self.mode == "collection":
            # Carica tutte le carte della collezione
            query = session.query(Card)
            if filters:
                # Applica i filtri in modo combinato
                if filters.get("name"):
                    query = query.filter(Card.name.ilike(f"%{filters['name']}%"))
                if filters.get("mana_cost") and filters["mana_cost"] != "Qualsiasi":
                    query = query.filter(Card.mana_cost == int(filters["mana_cost"]))
                if filters.get("card_type") not in [None, "Tutti"]:
                    query = query.filter(Card.card_type == filters["card_type"])
                if filters.get("card_subtype") not in [None, "Tutti"]:
                    query = query.filter(Card.card_subtype == filters["card_subtype"])
                if filters.get("rarity") not in [None, "Tutti"]:
                    query = query.filter(Card.rarity == filters["rarity"])
                if filters.get("expansion") not in [None, "Tutti"]:
                    query = query.filter(Card.expansion == filters["expansion"])

            cards = query.order_by(Card.mana_cost, Card.name).all()
            for card in cards:
                self.card_list.Append([
                    card.name,
                    str(card.mana_cost),
                    card.class_name if card.class_name else "Nessuna",  # Mostra la classe eroe
                    card.card_type,
                    card.card_subtype,
                    card.rarity,
                    card.expansion
                ])
        elif self.mode == "deck":
            # Carica le carte del mazzo
            deck_cards = session.query(DeckCard).filter_by(deck_id=self.deck_content["id"]).all()
            deck_cards = session.query(DeckCard).filter_by(deck_id=self.deck_content["id"]).all()
            for deck_card in deck_cards:
                card = session.query(Card).filter_by(id=deck_card.card_id).first()
                if card:
                    # Applica i filtri (se presenti)
                    if filters:
                        if filters.get("name") and filters["name"].lower() not in card.name.lower():
                            continue
                        if filters.get("mana_cost") and filters["mana_cost"] != "Qualsiasi" and card.mana_cost != int(filters["mana_cost"]):
                            continue
                        if filters.get("card_type") not in [None, "Tutti"] and card.card_type != filters["card_type"]:
                            continue
                        if filters.get("card_subtype") not in [None, "Tutti"] and card.card_subtype != filters["card_subtype"]:
                            continue
                        if filters.get("rarity") not in [None, "Tutti"] and card.rarity != filters["rarity"]:
                            continue
                        if filters.get("expansion") not in [None, "Tutti"] and card.expansion != filters["expansion"]:
                            continue

                    self.card_list.Append([
                        card.name,
                        str(card.mana_cost),
                        str(deck_card.quantity),  # Mostra la quantità nel mazzo
                        card.card_type,
                        card.card_subtype,
                        card.rarity,
                        card.expansion
                    ])

    def last_load_cards(self, filters=None):
        """Carica le carte nella lista in base alla modalità e ai filtri."""
        self.card_list.DeleteAllItems()
        if self.mode == "collection":
            # Carica tutte le carte della collezione
            query = session.query(Card)
            if filters:
                # Applica i filtri in modo combinato
                if filters.get("name"):
                    query = query.filter(Card.name.ilike(f"%{filters['name']}%"))
                if filters.get("mana_cost") and filters["mana_cost"] != "Qualsiasi":
                    query = query.filter(Card.mana_cost == int(filters["mana_cost"]))
                if filters.get("card_type") not in [None, "Tutti"]:
                    query = query.filter(Card.card_type == filters["card_type"])
                if filters.get("card_subtype") not in [None, "Tutti"]:
                    query = query.filter(Card.card_subtype == filters["card_subtype"])
                if filters.get("rarity") not in [None, "Tutti"]:
                    query = query.filter(Card.rarity == filters["rarity"])
                if filters.get("expansion") not in [None, "Tutti"]:
                    query = query.filter(Card.expansion == filters["expansion"])

            cards = query.order_by(Card.mana_cost, Card.name).all()
            for card in cards:
                self.card_list.Append([
                    card.name,
                    str(card.mana_cost),
                    card.class_name if card.class_name else "Nessuna",  # Mostra la classe eroe
                    card.card_type,
                    card.card_subtype,
                    card.rarity,
                    card.expansion
                ])
        elif self.mode == "deck":
            # Carica le carte del mazzo
            for card_data in self.deck_content["cards"]:
                card = session.query(Card).filter_by(name=card_data["name"]).first()
                if card:
                    # Applica i filtri (se presenti)
                    if filters:
                        if filters.get("name") and filters["name"].lower() not in card.name.lower():
                            continue
                        if filters.get("mana_cost") and filters["mana_cost"] != "Qualsiasi" and card.mana_cost != int(filters["mana_cost"]):
                            continue
                        if filters.get("card_type") not in [None, "Tutti"] and card.card_type != filters["card_type"]:
                            continue
                        if filters.get("card_subtype") not in [None, "Tutti"] and card.card_subtype != filters["card_subtype"]:
                            continue
                        if filters.get("rarity") not in [None, "Tutti"] and card.rarity != filters["rarity"]:
                            continue
                        if filters.get("expansion") not in [None, "Tutti"] and card.expansion != filters["expansion"]:
                            continue

                    self.card_list.Append([
                        card.name,
                        str(card.mana_cost),
                        str(card_data["quantity"]),  # Mostra la quantità nel mazzo
                        card.card_type,
                        card.card_subtype,
                        card.rarity,
                        card.expansion
                    ])


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
                self.card_list.Select(i)  # Seleziona la riga
                self.card_list.Focus(i)   # Sposta il focus alla riga selezionata
                self.card_list.EnsureVisible(i)  # Assicurati che la riga sia visibile
                self.card_list.SetFocus()  # Imposta il focus sulla lista
                break


    def on_reset(self, event):
        """Ripristina la visualizzazione originale, rimuovendo i filtri e riordinando le colonne."""
        # Rimuovi i filtri
        if hasattr(self, "search_ctrl"):
            self.search_ctrl.SetValue("")  # Resetta la barra di ricerca
        if hasattr(self, "filters"):
            del self.filters  # Libera la memoria occupata dai filtri precedenti

        # Ricarica le carte senza filtri
        self.load_cards()

        # Ripristina l'ordinamento predefinito (ad esempio, per "Mana" e "Nome")
        self.sort_cards(1)  # Ordina per "Mana" (colonna 1)
        self.card_list.SetFocus()
        self.card_list.Select(0)
        self.card_list.Focus(0)
        self.card_list.EnsureVisible(0)

    def last_on_reset(self, event):
        """Ripristina la visualizzazione originale, rimuovendo i filtri e riordinando le colonne."""

        # Rimuovi i filtri
        if hasattr(self, "search_ctrl"):
            self.search_ctrl.SetValue("")  # Resetta la barra di ricerca
        if hasattr(self, "filters"):
            self.filters = None  # Resetta i filtri avanzati

        # Ricarica le carte senza filtri
        self.load_cards()

        # Ripristina l'ordinamento predefinito (ad esempio, per "Mana" e "Nome")
        self.sort_cards(1)  # Ordina per "Mana" (colonna 1)
        #self.sort_cards(0)  # Ordina per "Nome" (colonna 0)

        #wx.MessageBox("Visualizzazione ripristinata con successo.", "Aggiornamento completato")
        # spostiamo il cursore sull'elenco delle carte, al primo indice
        self.card_list.SetFocus()
        self.card_list.Select(0)
        self.card_list.Focus(0)
        self.card_list.EnsureVisible(0)


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
                    self.load_cards()  # Ricarica la lista delle carte
                    wx.MessageBox(f"Carta '{card_name}' modificata con successo.", "Successo")
                    self.select_card_by_name(card_name)  # Seleziona e mette a fuoco la carta modificata
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
                        self.load_cards()
                        wx.MessageBox(f"Carta '{card_name}' eliminata dal mazzo.", "Successo", wx.OK | wx.ICON_INFORMATION)
                except Exception as e:
                    log.error(f"Errore durante l'eliminazione della carta: {str(e)}")
                    wx.MessageBox(f"Errore durante l'eliminazione della carta: {str(e)}", "Errore", wx.OK | wx.ICON_ERROR)
        else:
            wx.MessageBox("Seleziona una carta da eliminare.", "Errore", wx.OK | wx.ICON_ERROR)

    def last_on_delete_card(self, event):
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
        #self.load_cards(filters={"name": search_text})
        # Se la casella di ricerca è vuota o contiene "tutti" o "all", ripristina la visualizzazione
        if search_text is None or search_text == "" or search_text in ["tutti", "tutto", "all"]:
            self.on_reset(event)
        else:
            # Altrimenti, applica la ricerca
            self.load_cards(filters={"name": search_text})



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



class CardCollectionDialog(CardManagerDialog):
    """Finestra per gestire la collezione di carte."""

    def __init__(self, parent, deck_manager):
        super().__init__(parent, deck_manager, mode="collection")
        self.parent = parent
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

    def reset_filters(self):
        self.search_ctrl.SetValue("")
        self.load_cards()  # Ricarica la lista delle carte senza filtri


    def on_show_filters(self, event):
        """Mostra la finestra dei filtri avanzati."""
        dlg = FilterDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            # Applica i nuovi filtri
            filters = {
                "name": dlg.search_ctrl.GetValue(),
                "mana_cost": dlg.mana_cost.GetValue(),
                "card_type": dlg.card_type.GetValue(),
                "card_subtype": dlg.card_subtype.GetValue(),
                "rarity": dlg.rarity.GetValue(),
                "expansion": dlg.expansion.GetValue()
            }
            self.load_cards(filters=filters)
        else:
            # Se l'utente annulla, resetta i filtri
            self.load_cards(filters=None)
        dlg.Destroy()





#@@@# Start del modulo
if __name__ != "__main__":
    print("Carico: %s." % __name__)
