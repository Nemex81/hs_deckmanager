"""

    views.py

    Modulo per le finestre di dialogo dell'interfaccia utente.

    path:
        scr/views.py

    Note:
        Questo modulo utilizza la libreria wxPython per la creazione delle finestre di dialogo dell'interfaccia utente.

"""

# lib
import wx, pyperclip
from sqlalchemy.exc import SQLAlchemyError
from scr.models import DbManager, AppController
from .db import session, Card, DeckCard, Deck
from .models import DbManager, AppController, load_cards_from_db, load_deck_from_db, load_cards
from .view_components import BasicView, BasicDialog, CardManagerFrame, SingleCardView
from utyls.enu_glob import EnuColors, ENUCARD, EnuExtraCard, EnuCardType, EnuSpellType, EnuSpellSubType, EnuPetSubType, EnuHero, EnuRarity, EnuExpansion
from utyls import helper as hp
from utyls import logger as log
#import pdb



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
        panel = wx.Panel(self)

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
        sizer, control_dict = hp.create_ui_controls(panel, fields)

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
        
        



class DeckViewFrame(CardManagerFrame):
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


        # eventi
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def load_cards(self, filters=None):
        """ carica le carte utilizzando le funzionihelper sopra definite"""
        load_cards(self.card_list, self.deck_content, self.mode, filters)

    def on_reset(self, event):
        """Ripristina la visualizzazione originale, rimuovendo i filtri e riordinando le colonne."""

        # Rimuovi i filtri
        if hasattr(self, "search_ctrl"):
            self.search_ctrl.SetValue("")  # Resetta la barra di ricerca

        if hasattr(self, "filters"):
            del self.filters  # Libera la memoria occupata dai filtri precedenti

        # Ricarica le carte senza filtri
        #self.load_cards()
        load_cards(self.card_list, self.deck_content, self.mode)

        # Ripristina l'ordinamento predefinito (ad esempio, per "Mana" e "Nome")
        self.sort_cards(1)  # Ordina per "Mana" (colonna 1)
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

                    # gestisco l'aggiunta della carta al mazzo
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


    def on_close(self, event):
        """Chiude la finestra di dialogo."""
        self.parent.Show()
        self.Close()
        self.Destroy()



class CardCollectionFrame(CardManagerFrame):
    """Finestra per gestire la collezione di carte."""

    def __init__(self, parent, deck_manager):
        super().__init__(parent, deck_manager, mode="collection")
        self.parent = parent
        self.init_search_and_filters()

    def init_search_and_filters(self):
        """Aggiunge la barra di ricerca e i filtri."""

        panel = self.GetChildren()[0]  # Ottieni il pannello principale
        sizer = panel.GetSizer()
        self.Center()
        self.Maximize()

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

        # eventi
        self.Bind(wx.EVT_CLOSE, self.on_close)


    def load_cards(self, filters=None):
        """ carica le carte utilizzando le funzionihelper sopra definite"""
        load_cards(self.card_list, self.deck_content, self.mode, filters)


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
                "spell_type": dlg.spell_type.GetValue(),
                "card_subtype": dlg.card_subtype.GetValue(),
                "attack": dlg.attack.GetValue(),
                "health": dlg.health.GetValue(),
                "rarity": dlg.rarity.GetValue(),
                "expansion": dlg.expansion.GetValue()
            }
            self.load_cards(filters=filters)

        else:
            # Se l'utente annulla, resetta i filtri
            self.load_cards(filters=None)

        dlg.Destroy()


    def on_reset(self, event):
        """Ripristina la visualizzazione originale, rimuovendo i filtri e riordinando le colonne."""

        # Rimuovi i filtri
        if hasattr(self, "search_ctrl"):
            self.search_ctrl.SetValue("")  # Resetta la barra di ricerca

        if hasattr(self, "filters"):
            del self.filters  # Libera la memoria occupata dai filtri precedenti

        # Ricarica le carte senza filtri
        #self.load_cards()
        load_cards(self.card_list, self.deck_content, self.mode)

        # Ripristina l'ordinamento predefinito (ad esempio, per "Mana" e "Nome")
        self.sort_cards(1)  # Ordina per "Mana" (colonna 1)
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

                    # gestisco l'aggiunta della carta al mazzo
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


    def on_close(self, event):
        """Chiude la finestra di dialogo."""
        self.parent.Show()
        self.Close()
        self.Destroy()




class DecksManagerFrame(wx.Frame):
#class DecksManagerFrame(BasicView):
    """ Finestra di gestione dei mazzi. """

    def __init__(self, parent, db_manager):
        title = "Gestione Mazzi"
        super().__init__(parent, title=title, size=(800, 600))
        self.parent = parent
        self.db_manager = db_manager
        self.controller = AppController(self.db_manager, self)
        self.init_ui_elements()


    def init_ui(self):
        pass

    def init_ui_elements(self):
        """ Inizializza l'interfaccia utente. """

        # Impostazioni finestra principale
        self.SetBackgroundColour('green')
        self.panel = wx.Panel(self)

        # Layout principale
        self.Centre()
        self.Maximize()
        lbl_title = wx.StaticText(self.panel, label="Elenco Mazzi")
        #self.deck_list = wx.ListBox(self.panel)
        self.deck_list = wx.ListCtrl(
            self.panel,
            #style=wx.LC_REPORT | wx.BORDER_SUNKEN
            style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.BORDER_SUNKEN
        )

        # aggiungiamo le righe e le colonne
        self.deck_list.InsertColumn(0, "mazzo", width=260)
        self.deck_list.InsertColumn(1, "Classe ", width=200)
        self.deck_list.InsertColumn(2, "Formato ", width=120)

        # carichiamo i mazzi
        self.load_decks()

        # Barra di ricerca
        self.search_bar = wx.SearchCtrl(self.panel)
        self.search_bar.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.on_search)

        # Pulsanti
        btn_add = wx.Button(self.panel, label="Aggiungi Mazzo")
        btn_copy = wx.Button(self.panel, label="Copia Mazzo")
        btn_view = wx.Button(self.panel, label="Visualizza Mazzo")
        btn_stats = wx.Button(self.panel, label="Statistiche Mazzo")
        btn_update = wx.Button(self.panel, label="Aggiorna Mazzo")
        btn_delete = wx.Button(self.panel, label="Elimina Mazzo")
        btn_collection = wx.Button(self.panel, label="Collezione Carte")
        btn_exit = wx.Button(self.panel, label="Chiudi")

        # Layout principale
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(lbl_title, flag=wx.CENTER | wx.TOP, border=10)
        sizer.Add(self.search_bar, flag=wx.EXPAND | wx.ALL, border=5)

        # Separatore tra barra di ricerca e lista dei mazzi
        sizer.Add(wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)
        sizer.Add(self.deck_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Separatore tra lista dei mazzi e pulsanti
        sizer.Add(wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        # Layout pulsanti
        btn_sizer = wx.GridSizer(rows=4, cols=2, hgap=10, vgap=10)
        btn_sizer.Add(btn_add, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_copy, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_view, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_stats, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_update, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_delete, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_collection, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_exit, flag=wx.EXPAND | wx.ALL, border=5)
        sizer.Add(btn_sizer, flag=wx.EXPAND | wx.ALL, border=10)

        # Separatore tra pulsanti e barra di stato
        sizer.Add(wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        self.panel.SetSizer(sizer)

        # Barra di stato
        #self.status_bar = self.CreateStatusBar()
        #self.status_bar.SetStatusText("Pronto")

        # Eventi
        btn_add.Bind(wx.EVT_BUTTON, self.on_add_deck)
        btn_copy.Bind(wx.EVT_BUTTON, self.on_copy_deck)
        btn_view.Bind(wx.EVT_BUTTON, self.on_view_deck)
        btn_update.Bind(wx.EVT_BUTTON, self.on_update_deck)
        btn_stats.Bind(wx.EVT_BUTTON, self.on_view_stats)
        btn_collection.Bind(wx.EVT_BUTTON, self.on_view_collection)
        btn_delete.Bind(wx.EVT_BUTTON, self.on_delete_deck)
        btn_exit.Bind(wx.EVT_BUTTON, self.on_close)


    def load_decks(self):
        """Carica i mazzi ."""

        # carichiamo i mazzi
        decks = session.query(Deck).all()
        # utilizzando insert
        for deck in decks:
            Index = self.deck_list.InsertItem(self.deck_list.GetItemCount(), deck.name)
            self.deck_list.SetItem(Index, 1, deck.player_class)
            self.deck_list.SetItem(Index, 2, deck.game_format)


    def update_deck_list(self):
        """Aggiorna la lista dei mazzi."""

        self.deck_list.DeleteAllItems()  # Pulisce la lista
        decks = session.query(Deck).all()
        for deck in decks:
            index = self.deck_list.InsertItem(self.deck_list.GetItemCount(), deck.name)  # Prima colonna
            self.deck_list.SetItem(index, 1, deck.player_class)  # Seconda colonna
            self.deck_list.SetItem(index, 2, deck.game_format)  # Terza colonna


    def update_status(self, message):
        """Aggiorna la barra di stato."""
        #self.status_bar.SetStatusText(message)
        pass


    def get_selected_deck(self):
        """Restituisce il mazzo selezionato nella lista."""
        selection = self.deck_list.GetFirstSelected()
        if selection != wx.NOT_FOUND:
            return self.deck_list.GetItemText(selection)
        return None


    def select_and_focus_deck(self, deck_name):
        """
        Seleziona un mazzo nella lista e imposta il focus su di esso.
        
        :param deck_name: Il nome del mazzo da selezionare.
        """

        if not deck_name:
            return

        log.info(f"Tentativo di selezione e focus sul mazzo: {deck_name}")
        # Trova l'indice del mazzo nella lista
        for i in range(self.deck_list.GetItemCount()):
            if self.deck_list.GetItemText(i) == deck_name:
                log.info(f"Mazzo trovato all'indice: {i}")
                self.deck_list.Select(i)  # Seleziona il mazzo
                self.deck_list.Focus(i)   # Imposta il focus sul mazzo
                self.deck_list.EnsureVisible(i)  # Assicurati che il mazzo sia visibile
                self.deck_list.SetFocus() # Imposta il focus sulla lista dei mazzi
                break


    def on_add_deck(self, event):
        """Aggiunge un mazzo dagli appunti con una finestra di conferma."""
 
        try:
            deck_string = pyperclip.paste()
            if not self.db_manager.is_valid_deck(deck_string):
                wx.MessageBox("Il mazzo copiato non è valido.", "Errore")
                return

            #metadata = parse_deck_metadata(deck_string)
            metadata = DbManager.parse_deck_metadata(deck_string)
            deck_name = metadata["name"]

            # Mostra una finestra di conferma con i dati estratti
            confirm_message = (
                f"È stato rilevato un mazzo valido negli appunti.\n\n"
                f"Nome: {deck_name}\n"
                f"Classe: {metadata['player_class']}\n"
                f"Formato: {metadata['game_format']}\n\n"
                f"Vuoi utilizzare questi dati per creare il mazzo?"
            )

            # Mostra una finestra di conferma con i dati estratti
            confirm_dialog = wx.MessageDialog(
                self,
                confirm_message,
                "Conferma Creazione Mazzo",
                wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION
            )

            # Gestione della risposta
            result = confirm_dialog.ShowModal()
            if result == wx.ID_YES:
                success = self.db_manager.add_deck_from_clipboard()
                if success:
                    self.update_deck_list()
                    self.update_status(f"Mazzo '{deck_name}' aggiunto con successo.")
                    wx.MessageBox(f"Mazzo '{deck_name}' aggiunto con successo.", "Successo")
                    self.select_and_focus_deck(deck_name)  # Seleziona e mette a fuoco il mazzo

            elif result == wx.ID_NO:
                name_dialog = wx.TextEntryDialog(
                    self,
                    "Inserisci il nome per il nuovo mazzo:",
                    "Nome del Mazzo",
                    deck_name
                )

                if name_dialog.ShowModal() == wx.ID_OK:
                    new_name = name_dialog.GetValue()
                    if new_name:
                        metadata["name"] = new_name
                        success = self.db_manager.add_deck_from_clipboard()
                        if success:
                            self.update_deck_list()
                            self.update_status("Mazzo aggiunto con successo.")
                            wx.MessageBox("Mazzo aggiunto con successo.", "Successo")
                            self.select_and_focus_deck(new_name)  # Seleziona e mette a fuoco il mazzo
                    else:
                        wx.MessageBox("Il nome del mazzo non può essere vuoto.", "Errore")

            elif result == wx.ID_CANCEL:
                self.update_status("Operazione annullata.")
                wx.MessageBox("Operazione annullata.", "Annullato")
                self.update_deck_list()

        except pyperclip.PyperclipException as e:
            wx.MessageBox("Errore negli appunti. Assicurati di aver copiato un mazzo valido.", "Errore")

        except Exception as e:
            log.error(f"Errore durante l'aggiunta del mazzo: {e}")
            wx.MessageBox("Si è verificato un errore imprevisto.", "Errore")


    def on_copy_deck(self, event):
        """Copia il mazzo selezionato negli appunti."""

        deck_name = self.get_selected_deck()
        if deck_name:
            if self.db_manager.copy_deck_to_clipboard(deck_name):
                self.update_status(f"Mazzo '{deck_name}' copiato negli appunti.")
                wx.MessageBox(f"Mazzo '{deck_name}' copiato negli appunti.", "Successo")
                self.select_and_focus_deck(deck_name)

            else:
                wx.MessageBox("Errore: Mazzo vuoto o non trovato.", "Errore")

        else:
            wx.MessageBox("Seleziona un mazzo prima di copiarlo negli appunti.", "Errore")


    def on_view_deck(self, event):
        """Mostra il mazzo selezionato in una finestra dettagliata."""

        deck_name = self.get_selected_deck()
        if deck_name:
            deck_content = self.db_manager.get_deck(deck_name)
            if deck_content:
                # Apri la finestra di visualizzazione del mazzo
                #deck_view_dialog = DeckViewDialog(self, self.db_manager, deck_name)
                deck_view_dialog = DeckViewFrame(self, self.db_manager, deck_name=deck_name)
                #deck_view_dialog.ShowModal()
                self.Hide()
                deck_view_dialog.Show()

            else:
                wx.MessageBox("Errore: Mazzo vuoto o non trovato.", "Errore")

        else:
            wx.MessageBox("Seleziona un mazzo prima di visualizzarlo.", "Errore")


    def on_update_deck(self, event):
        """Aggiorna il mazzo selezionato con il contenuto degli appunti."""

        deck_name = self.get_selected_deck()
        if deck_name:
            if wx.MessageBox(
                f"Sei sicuro di voler aggiornare '{deck_name}' con il contenuto degli appunti?",
                "Conferma",
                wx.YES_NO
            ) == wx.YES:
                try:
                    deck_string = pyperclip.paste()
                    if self.db_manager.is_valid_deck(deck_string):
                        deck = session.query(Deck).filter_by(name=deck_name).first()
                        if deck:
                            session.query(DeckCard).filter_by(deck_id=deck.id).delete()
                            session.commit()

                            self.db_manager.sync_cards_with_database(deck_string)

                            cards = self.db_manager.parse_cards_from_deck(deck_string)
                            for card_data in cards:
                                card = session.query(Card).filter_by(name=card_data["name"]).first()
                                if not card:
                                    card = Card(
                                        name=card_data["name"],
                                        class_name="Unknown",
                                        mana_cost=card_data["mana_cost"],
                                        card_type="Unknown",
                                        spell_type="Unknown",
                                        card_subtype="Unknown",
                                        rarity="Unknown",
                                        expansion="Unknown"
                                    )
                                    session.add(card)
                                    session.commit()

                                deck_card = DeckCard(deck_id=deck.id, card_id=card.id, quantity=card_data["quantity"])
                                session.add(deck_card)
                                session.commit()

                            self.update_deck_list()
                            self.update_status(f"Mazzo '{deck_name}' aggiornato con successo.")
                            wx.MessageBox(f"Mazzo '{deck_name}' aggiornato con successo.", "Successo")
                            self.select_and_focus_deck(deck_name)  # Seleziona e mette a fuoco il mazzo

                        else:
                            wx.MessageBox("Errore: Mazzo non trovato nel database.", "Errore")

                    else:
                        wx.MessageBox("Il mazzo negli appunti non è valido.", "Errore")

                except Exception as e:
                    log.error(f"Errore durante l'aggiornamento del mazzo: {e}")
                    wx.MessageBox(f"Si è verificato un errore: {e}", "Errore")

        else:
            wx.MessageBox("Seleziona un mazzo prima di aggiornarlo.", "Errore")


    def on_view_stats(self, event):
        """Mostra le statistiche del mazzo selezionato."""

        deck_name = self.get_selected_deck()
        if deck_name:
            stats = self.controller.get_deck_statistics(deck_name)
            if stats:
                DeckStatsDialog(self, stats=stats).ShowModal()

            else:
                wx.MessageBox("Impossibile calcolare le statistiche per questo mazzo.", "Errore")

        else:
            wx.MessageBox("Seleziona un mazzo prima di visualizzare le statistiche.", "Errore")


    def on_view_collection(self, event):
        """Mostra la collezione delle carte."""
        #collection_dialog = CardCollectionDialog(self, self.db_manager)
        collection_dialog = CardCollectionFrame(self, self.controller)
        self.Hide()                     # Nasconde la finestra di gestione dei mazzi
        collection_dialog.Show()  # Mostra la finestra come modale


    def on_delete_deck(self, event):
        """Elimina il mazzo selezionato."""

        deck_name = self.get_selected_deck()
        if deck_name:
            if wx.MessageBox(f"Sei sicuro di voler eliminare '{deck_name}'?", "Conferma", wx.YES_NO) == wx.YES:
                try:
                    #success = self.db_manager.delete_deck(deck_name)
                    success = self.controller.delete_deck(deck_name)
                    if success:
                        self.update_deck_list()
                        self.update_status(f"Mazzo '{deck_name}' eliminato con successo.")
                        wx.MessageBox(f"Mazzo '{deck_name}' eliminato con successo.", "Successo")
                    else:
                        wx.MessageBox(f"Mazzo '{deck_name}' non trovato.", "Errore")

                except SQLAlchemyError as e:
                    wx.MessageBox("Errore del database. Verificare le procedure.", "Errore")

                except Exception as e:
                    wx.MessageBox("Si è verificato un errore imprevisto.", "Errore")
        else:
            wx.MessageBox("Seleziona un mazzo prima di eliminarlo.", "Errore")


    def on_search(self, event):
        """Filtra i mazzi in base al testo di ricerca."""

        # cerchiamo la parola richiesta dall0utente sia nei nomi dei mazzi sia nella classe
        search_text = self.search_bar.GetValue()
        self.deck_list.DeleteAllItems()
        decks = session.query(Deck).filter(Deck.name.ilike(f"%{search_text}%") | Deck.player_class.ilike(f"%{search_text}%")).all()
        for deck in decks:
            Index = self.deck_list.InsertItem(self.deck_list.GetItemCount(), deck.name)
            self.deck_list.SetItem(Index, 1, deck.player_class)
            self.deck_list.SetItem(Index, 2, deck.game_format)


    def on_close(self, event):
        """Chiude l'applicazione."""
        self.parent.Show()  # Mostra la finestra principale
        self.Close()        # Chiude la finestra di gestione dei mazzi



class HearthstoneAppFrame(wx.Frame):
#class HearthstoneAppFrame(BasicView):
    """ Finestra principale dell'applicazione. """

    def __init__(self, parent, title):
        super(HearthstoneAppFrame, self).__init__(parent, title=title, size=(900, 700))
        self.db_manager = DbManager()
        #self.app_controller = AppController(self.db_manager, self)
        font = wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)    # Imposta il font per la finestra principale
        self.SetBackgroundColour(wx.BLACK)                                                      # Imposta il colore di sfondo della finestra principale
        self.Maximize()                                                                         # Massimizza la finestra principale
        self.init_ui_elements()                                                                 # Inizializza gli elementi dell'interfaccia utente

    def init_ui(self):
        pass

    def init_ui_elements(self, *args, **kwargs):
        """ Inizializza gli elementi dell'interfaccia utente. """

        # pannello per contenere gli elementi dell'interfaccia utente
        self.panel = wx.Panel(self)

        # Aggiungo l'immagine
        image = wx.Image("img/background_magic.jpeg", wx.BITMAP_TYPE_ANY)
        image = image.Scale(1200, 790)  # Ridimensiona l'immagine
        bitmap = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(image))

        # Aggiungo i pulsanti
        self.collection_button = wx.Button(self.panel, label="Collezione")
        self.collection_button.Bind(wx.EVT_BUTTON, self.on_collection_button_click)

        self.decks_button = wx.Button(self.panel, label="Gestione Mazzi")
        self.decks_button.Bind(wx.EVT_BUTTON, self.on_decks_button_click)

        #self.match_button = wx.Button(self.panel, label="Palestra")
        #self.match_button.Bind(wx.EVT_BUTTON, self.on_match_button_click)

        #self.settings_button = wx.Button(self.panel, label="Impostazioni")
        #self.settings_button.Bind(wx.EVT_BUTTON, self.on_settings_button_click)

        self.quit_button = wx.Button(self.panel, label="Esci")
        self.quit_button.Bind(wx.EVT_BUTTON, self.on_quit_button_click)

        button_size = (250, 90)
        self.collection_button.SetMinSize(button_size)
        self.decks_button.SetMinSize(button_size)
        #self.match_button.SetMinSize(button_size)
        #self.settings_button.SetMinSize(button_size)
        self.quit_button.SetMinSize(button_size)

        font = wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD)  # 20 è la dimensione del font, regola secondo necessità
        self.collection_button.SetFont(font)
        self.decks_button.SetFont(font)
        #self.match_button.SetFont(font)
        #self.settings_button.SetFont(font)
        self.quit_button.SetFont(font)

        # Aggiungo un sizer per allineare i pulsanti verticalmente
        button_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer.Add(self.collection_button, 0, wx.ALL, 20)
        button_sizer.Add(self.decks_button, 0, wx.ALL, 20)
        #button_sizer.Add(self.match_button, 0, wx.ALL, 20)
        #button_sizer.Add(self.settings_button, 0, wx.ALL, 20)
        button_sizer.Add(self.quit_button, 0, wx.ALL, 20)

        # Aggiungo un sizer principale per allineare il bitmap e il sizer dei pulsanti
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(bitmap, proportion=0, flag=wx.ALL, border=10)
        main_sizer.Add(button_sizer, 1, wx.ALIGN_CENTER | wx.ALL, 0)
        self.panel.SetSizerAndFit(main_sizer)

    #@@# sezione metodi collegati agli eventi

    def on_collection_button_click(self, event):
        """ Metodo per gestire il click sul pulsante 'Collezione'. """
        collection_frame = CardCollectionFrame(self, self.db_manager)
        #collection_frame.ShowModal()
        self.Hide()                     # Nasconde la finestra principale
        collection_frame.Show()         # Mostra la finestra di gestione della collezione 
        

    def on_decks_button_click(self, event):
        """ Metodo per gestire il click sul pulsante 'Gestione Mazzi'. """
        #decks_frame = DecksManagerDialog(self, self.db_manager)
        decks_frame = DecksManagerFrame(self, self.db_manager)     # Crea un'istanza della finestra di gestione dei mazzi
        self.Hide()                                                 # nascondo la finestra principale
        decks_frame.Show()                                          # Mostro la finestra


    #def on_match_button_click(self, event):
        #match_frame = GamePrak(self)
        #match_frame.ShowModal()  # Apri come dialogo modale


    #def on_settings_button_click(self, event):
            #settings_frame = SettingsFrame(self)  # Crea un'istanza della finestra di impostazioni
            #settings_frame.ShowModal()  # Apri come dialogo modale


    def on_quit_button_click(self, event):
        # Mostra una finestra di dialogo di conferma
        dlg = wx.MessageDialog(
            self,
            "Confermi l'uscita dall'applicazione?",
            "Conferma Uscita",
            wx.YES_NO | wx.ICON_QUESTION
        )

        # Se l'utente conferma, esci dall'applicazione
        if dlg.ShowModal() == wx.ID_YES:
            dlg.Destroy()  # Distruggi la finestra di dialogo
            self.Close()   # Chiudi la finestra impostazioni account



#@@@# Start del modulo
if __name__ != "__main__":
    print("Carico: %s." % __name__)
