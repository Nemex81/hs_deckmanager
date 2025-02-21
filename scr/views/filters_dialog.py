"""
    Modulo Filter Dialog

    path:
        scr/views/filters_dialog.py

    Descrizione:
        Questo modulo contiene la classe FilterDialog, una finestra di dialogo per i filtri di ricerca delle carte.
        La finestra di dialogo permette all'utente di filtrare le carte per nome, costo in mana, tipo, sottotipo, attacco, vita, rarità ed espansione.
        I filtri sono implementati utilizzando wxPython e sono progettati per essere riutilizzabili in altre finestre dell'applicazione.
        La finestra di dialogo include anche pulsanti per applicare i filtri e annullare le modifiche.

"""

# Lib
import wx
from .proto_views import BasicDialog
from .view_components import create_sizer, add_to_sizer, create_button, create_separator
from utyls.enu_glob import EnuCardType, EnuSpellType, EnuPetSubType, EnuRarity, EnuExpansion
from utyls import helper as hp
from utyls import logger as log
#import pdb


class FilterDialog(BasicDialog):
    """ Finestra di dialogo per i filtri di ricerca. """

    def __init__(self, parent):
        super().__init__(parent, title="Filtri di Ricerca", size=(420, 600))
        self.parent = parent

    def init_ui_elements(self):
        """Inizializza l'interfaccia utente utilizzando le funzioni helper, mantenendo l'impaginazione originale."""

        # Impostazioni finestra principale
        self.SetBackgroundColour('red')
        self.panel.SetBackgroundColour(wx.RED)

        # Creazione degli elementi dell'interfaccia
        self.sizer = wx.BoxSizer(wx.VERTICAL)  # Sizer principale verticale

        # Definizione dei controlli UI
        controls = [
            ("nome", wx.TextCtrl),
            ("costo_mana", wx.ComboBox, {"choices": ["Qualsiasi"] + [str(i) for i in range(0, 21)], "style": wx.CB_READONLY}),
            ("tipo", wx.ComboBox, {"choices": ["Tutti"] + [t.value for t in EnuCardType], "style": wx.CB_READONLY}),
            ("tipo_magia", wx.ComboBox, {"choices": ["Qualsiasi"] + [st.value for st in EnuSpellType], "style": wx.CB_READONLY}),
            ("sottotipo", wx.ComboBox, {"choices": ["Tutti"] + [st.value for st in EnuPetSubType], "style": wx.CB_READONLY}),
            ("attacco", wx.ComboBox, {"choices": ["Qualsiasi"] + [str(i) for i in range(0, 21)], "style": wx.CB_READONLY}),
            ("vita", wx.ComboBox, {"choices": ["Qualsiasi"] + [str(i) for i in range(0, 21)], "style": wx.CB_READONLY}),
            ("rarita", wx.ComboBox, {"choices": ["Tutti"] + [r.value for r in EnuRarity], "style": wx.CB_READONLY}),
            ("espansione", wx.ComboBox, {"choices": ["Tutti"] + [e.value for e in EnuExpansion], "style": wx.CB_READONLY})
        ]

        # Creazione dei controlli UI utilizzando la funzione helper
        self.sizer, control_dict = hp.create_ui_controls(self.panel, controls)

        # Assegnazione dei controlli agli attributi della classe
        self.search_ctrl = control_dict["nome"]
        self.mana_cost = control_dict["costo_mana"]
        self.card_type = control_dict["tipo"]
        self.spell_type = control_dict["tipo_magia"]
        self.card_subtype = control_dict["sottotipo"]
        self.attack = control_dict["attacco"]
        self.health = control_dict["vita"]
        self.rarity = control_dict["rarita"]
        self.expansion = control_dict["espansione"]

        # Imposta i valori predefiniti
        self.reset_filters()

        # Collega l'evento di selezione del tipo di carta al metodo update_subtypes
        self.card_type.Bind(wx.EVT_COMBOBOX, self.on_type_change)

        # Pulsanti
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)  # Sizer orizzontale per i pulsanti

        # creazione di un separatore
        separator = create_separator(self.panel, style=wx.LI_HORIZONTAL, thickness=1, color=wx.Colour(200, 200, 200))
        add_to_sizer(self.sizer, separator, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=12)

        # Creazione dei pulsanti con font ridotto a 12 pt e dimensioni ridotte
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.btn_apply = create_button(
            self.panel, 
            label="Applica", 
            size=(100, 30),  # Dimensioni ridotte
            event_handler=lambda e: self.EndModal(wx.ID_OK)
        )
        self.btn_apply.SetFont(font)  # Imposta il font a 12 pt

        self.btn_cancel = create_button(
            self.panel, 
            label="Annulla", 
            size=(100, 30),  # Dimensioni ridotte
            event_handler=lambda e: self.EndModal(wx.ID_CANCEL)
        )
        self.btn_cancel.SetFont(font)  # Imposta il font a 12 pt

        # Aggiungi i pulsanti al sizer orizzontale con spaziatura
        btn_sizer.Add(self.btn_apply, flag=wx.RIGHT, border=10)
        btn_sizer.Add(self.btn_cancel)

        # Aggiungi il sizer dei pulsanti al sizer principale
        self.sizer.Add(btn_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        # Imposta il sizer principale per il pannello
        self.panel.SetSizer(self.sizer)
        self.Layout()

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