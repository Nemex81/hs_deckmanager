"""

"""

#lib
import wx
from sqlalchemy.exc import SQLAlchemyError
from ..db import session, Card
from ..models import load_cards
from .view_components import SingleCardView
from utyls.enu_glob import EnuCardType, EnuSpellType, EnuSpellSubType, EnuPetSubType, EnuHero, EnuRarity, EnuExpansion
from utyls import helper as hp
from utyls import logger as log
#import pdb



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
        
        
