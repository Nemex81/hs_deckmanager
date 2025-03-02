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
from .builder.view_components import create_check_list_box, create_common_controls
from .proto_views import BasicDialog, SingleCardView
from utyls.enu_glob import EnuCardType, EnuSpellType , EnuSpellSubType, EnuPetSubType, EnuHero, EnuRarity, EnuExpansion
from utyls import enu_glob as eg
from utyls import helper as hp
from utyls import logger as log
#import pdb



class FilterDialog(SingleCardView):
    """Finestra di dialogo per i filtri di ricerca."""

    def __init__(self, parent):
        super().__init__(parent, title="Filtri di Ricerca", size=(420, 600))
        self.parent = parent
        #elf.init_specific_ui_elements()

    def init_ui_elements(self):
        """Inizializza i componenti specifici per CardEditDialog."""

        self.panel.SetBackgroundColour('blue')

        # Sizer per i campi
        fields_sizer = wx.FlexGridSizer(rows=0, cols=2, hgap=10, vgap=10)

        # Definizione dei campi comuni
        common_controls = create_common_controls()

        # Creazione dei controlli UI e aggiunta al sizer dei campi
        for key, label_text, control_type, *args in common_controls:
            label = wx.StaticText(self.panel, label=label_text)
            if args:
                control = control_type(self.panel, **args[0])
            else:
                control = control_type(self.panel)

            fields_sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
            fields_sizer.Add(control, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
            self.controls[key] = control

        # Collega l'evento di selezione del tipo di carta
        self.controls["tipo"].Bind(wx.EVT_COMBOBOX, self.on_type_change)

        # Aggiungi il sizer dei campi al sizer principale
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(fields_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border=10)

        # Selezione multipla delle classi
        classes_label, self.classes_listbox = create_check_list_box(
            self.panel,
            choices=[h.value for h in EnuHero],
            label="Classi:"
        )

        # Aggiungola lista delle classi al sizer principale
        main_sizer.Add(classes_label, flag=wx.LEFT | wx.RIGHT, border=10)
        main_sizer.Add(self.classes_listbox, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Sizer per i pulsanti
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add_buttons(btn_sizer)

        # Aggiungoil sizer dei pulsanti al sizer principale
        main_sizer.Add(btn_sizer, proportion=0, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        # Impostoil sizer principale per il pannello
        self.panel.SetSizer(main_sizer)
        main_sizer.Fit(self.panel)

        # Imposta i valori predefiniti
        self.reset_filters()

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
        card_type = self.controls["tipo"].GetValue()
        if card_type == EnuCardType.MAGIA.value:
            subtypes = [st.value for st in EnuSpellSubType]

        elif card_type == EnuCardType.CREATURA.value:
            subtypes = [st.value for st in EnuPetSubType]

        else:
            subtypes = []

        # Salva il sottotipo corrente
        current_subtype = self.controls["sottotipo"].GetValue()
        self.controls["sottotipo"].Clear()
        self.controls["sottotipo"].AppendItems(["Tutti"] + subtypes)
        # Se il sottotipo corrente è valido per il nuovo tipo di carta, mantienilo
        if current_subtype not in subtypes:
            self.controls["sottotipo"].SetValue("Tutti")

        if card_type == EnuCardType.MAGIA.value:
            self.controls["attacco"].Disable()
            self.controls["vita"].Disable()
            self.controls["durability"].Disable()
            self.controls["sottotipo"].Disable()
            self.controls["tipo_magia"].Enable()


        elif card_type == EnuCardType.CREATURA.value:
            self.controls["attacco"].Enable()
            self.controls["vita"].Enable()
            self.controls["durability"].Disable()
            self.controls["tipo_magia"].Disable()

        elif card_type == EnuCardType.LUOGO.value:
            self.controls["attacco"].Disable()
            self.controls["vita"].Disable()
            self.controls["sottotipo"].Disable()
            self.controls["tipo_magia"].Disable()
            self.controls["durability"].Enable()

        elif card_type == EnuCardType.ARMA.value:
            self.controls["attacco"].Disable()
            self.controls["vita"].Disable()
            self.controls["sottotipo"].Disable()
            self.controls["tipo_magia"].Disable()
            self.controls["durability"].Enable()

        elif card_type == EnuCardType.EROE.value:
            self.controls["attacco"].Enable()
            self.controls["vita"].Enable()
            self.controls["durability"].Disable()
            self.controls["tipo_magia"].Disable()

        else:
            self.controls["attacco"].Enable()
            self.controls["vita"].Enable()
            self.controls["durability"].Enable()
            self.controls["tipo_magia"].Enable()


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

        # Chiude la finestra di dialogo e carica le carte filtrate
        if filters:
            self.parent.load_cards(filters)
        else:
            # Resetta i filtri
            self.reset_filters()

        self.EndModal(wx.ID_OK)




#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
