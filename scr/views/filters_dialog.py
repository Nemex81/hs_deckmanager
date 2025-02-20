"""

"""

# Lib
import wx
from .proto_views import BasicDialog
from utyls.enu_glob import EnuCardType, EnuSpellType, EnuPetSubType, EnuRarity, EnuExpansion
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