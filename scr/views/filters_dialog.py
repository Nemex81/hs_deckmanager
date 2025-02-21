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
from .proto_views import BasicDialog, CardFormDialog
from .view_components import create_sizer, add_to_sizer, create_button, create_separator
from utyls.enu_glob import EnuCardType, EnuSpellType , EnuSpellSubType, EnuPetSubType, EnuHero, EnuRarity, EnuExpansion
from utyls import helper as hp
from utyls import logger as log
#import pdb


class FilterDialog(CardFormDialog):
    """Finestra di dialogo per i filtri di ricerca."""

    def __init__(self, parent):
        super().__init__(parent, title="Filtri di Ricerca", size=(420, 600))
        self.parent = parent
        self.init_specific_ui_elements()

    def init_specific_ui_elements(self):
        """Inizializza i componenti specifici per FilterDialog."""

        # Aggiungi pulsanti "Applica" e "Annulla"
        self.add_buttons([
            ("Applica", lambda e: self.EndModal(wx.ID_OK)),
            ("Annulla", lambda e: self.EndModal(wx.ID_CANCEL))
        ])

        # Imposta i valori predefiniti
        self.reset_filters()


    def reset_filters(self):
        """Resetta i filtri ai valori predefiniti."""
        self.controls["nome"].SetValue("")
        self.controls["costo_mana"].SetValue("Qualsiasi")
        self.controls["tipo"].SetValue("Tutti")
        self.controls["tipo_magia"].SetValue("Qualsiasi")
        self.controls["sottotipo"].SetValue("Tutti")
        self.controls["attacco"].SetValue("Qualsiasi")
        self.controls["vita"].SetValue("Qualsiasi")
        self.controls["rarita"].SetValue("Tutti")
        self.controls["espansione"].SetValue("Tutti")


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


    def add_buttons(self, btn_sizer):
        """
        Aggiunge pulsanti alla finestra di dialogo.

        :param btn_sizer: Il sizer a cui aggiungere i pulsanti.
        """
        # Pulsante "Applica"
        apply_btn = wx.Button(self.panel, label="Applica")
        apply_btn.Bind(wx.EVT_BUTTON, self.on_apply_filters)
        btn_sizer.Add(apply_btn, flag=wx.ALL, border=5)

        # Pulsante "Annulla"
        cancel_btn = wx.Button(self.panel, label="Annulla")
        cancel_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        btn_sizer.Add(cancel_btn, flag=wx.ALL, border=5)


    def on_apply_filters(self, event):
        """Gestisce l'applicazione dei filtri."""
        filters = {
            "name": self.controls["nome"].GetValue(),
            "mana_cost": self.controls["costo_mana"].GetValue(),
            "card_type": self.controls["tipo"].GetValue(),
            "spell_type": self.controls["tipo_magia"].GetValue(),
            "card_subtype": self.controls["sottotipo"].GetValue(),
            "attack": self.controls["attacco"].GetValue(),
            "health": self.controls["vita"].GetValue(),
            "rarity": self.controls["rarita"].GetValue(),
            "expansion": self.controls["espansione"].GetValue()
        }

        # Chiude la finestra di dialogo
        if filters:
            self.parent.load_cards(filters)

        self.EndModal(wx.ID_OK)

    #def on_save(self, event):
        #"""Salva i filtri e chiude la finestra di dialogo."""
        #self.EndModal(wx.ID_OK)





#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
