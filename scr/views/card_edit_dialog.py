"""
    card_edit_dialog.py

    Modulo contenente la finestra di dialogo per aggiungere o modificare una carta.

    path:
        ./scr/views/card_edit_dialog.py

    Descrizione:

        Questo modulo contiene la classe CardEditDialog, una finestra di dialogo per aggiungere o modificare una carta.
        La finestra di dialogo permette all'utente di inserire i dettagli di una carta, come il nome, il costo in mana, il tipo, l'attacco, la vita, la durabilità, la rarità e l'espansione.
        La finestra di dialogo include anche un elenco di controllo per selezionare le classi associate alla carta e pulsanti per salvare le modifiche o chiudere la finestra.

"""

#lib
import wx
from sqlalchemy.exc import SQLAlchemyError
from ..db import session, Card
from ..models import load_cards
from .view_components import create_button, create_check_list_box, create_separator, create_common_controls
from .proto_views import CardFormDialog
from utyls.enu_glob import EnuCardType, EnuSpellType, EnuSpellSubType, EnuPetSubType, EnuHero, EnuRarity, EnuExpansion
from utyls import helper as hp
from utyls import logger as log
#import pdb



class CardEditDialog(CardFormDialog):
    """Finestra di dialogo per aggiungere o modificare una carta."""

    def __init__(self, parent, card=None):
        self.parent = parent
        title = "Modifica Carta" if card else "Aggiungi Carta"
        self.card = card
        super().__init__(parent, title=title, size=(400, 900))
        #self.init_specific_ui_elements()

    def init_ui_elements(self):
        """Inizializza i componenti specifici per CardEditDialog."""

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
        main_sizer.Add(classes_label, flag=wx.LEFT | wx.RIGHT, border=10)
        main_sizer.Add(self.classes_listbox, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Sizer per i pulsanti
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add_buttons(btn_sizer, [("Salva", self.on_save), ("Chiudi", self.on_close)])

        # Aggiungi il sizer dei pulsanti al sizer principale
        main_sizer.Add(btn_sizer, proportion=0, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        # Imposta il sizer principale per il pannello
        self.panel.SetSizer(main_sizer)
        main_sizer.Fit(self.panel)

        # Se è una modifica, pre-carica i dati della carta
        if self.card:
            self.load_card_data()

    def load_card_data(self):
        """Carica i dati della carta nei controlli UI."""
        if not self.card:
            return

        # Carica i dati della carta nei controlli
        self.controls["nome"].SetValue(self.card.name or "")
        self.controls["costo_mana"].SetValue(self.card.mana_cost or 0)
        self.controls["tipo"].SetValue(self.card.card_type or "Tutti")
        self.controls["tipo_magia"].SetValue(self.card.spell_type or "Qualsiasi")
        self.update_subtypes()
        self.controls["sottotipo"].SetValue(self.card.card_subtype or "Tutti")
        self.controls["attacco"].SetValue(self.card.attack or 0)
        self.controls["vita"].SetValue(self.card.health or 0)
        self.controls["durability"].SetValue(self.card.durability or 0)
        self.controls["rarita"].SetValue(self.card.rarity or "Tutti")
        self.controls["espansione"].SetValue(self.card.expansion or "Tutti")

        # Seleziona le classi associate alla carta
        if self.card.class_name:
            selected_classes = hp.disassemble_classes_string(self.card.class_name)
            for i, class_name in enumerate(self.classes_listbox.GetItems()):
                if class_name in selected_classes:
                    self.classes_listbox.Check(i)

    def update_subtypes(self):
        """Aggiorna i sottotipi in base al tipo di carta selezionato."""
        card_type = self.controls["tipo"].GetValue()
        subtypes = []

        if card_type == EnuCardType.MAGIA.value:
            subtypes = [st.value for st in EnuSpellSubType]
        elif card_type == EnuCardType.CREATURA.value:
            subtypes = [st.value for st in EnuPetSubType]

        # Salva il sottotipo corrente
        current_subtype = self.controls["sottotipo"].GetValue()
        self.controls["sottotipo"].Clear()
        self.controls["sottotipo"].AppendItems(["Tutti"] + subtypes)

        # Ripristina il sottotipo se presente nei nuovi sottotipi
        if current_subtype and current_subtype in subtypes:
            self.controls["sottotipo"].SetValue(current_subtype)
        else:
            self.controls["sottotipo"].SetValue("Tutti")

        # Abilita/disabilita i campi in base al tipo di carta
        self.on_type_change(None)

    def on_type_change(self, event):
        """Gestisce il cambio del tipo di carta."""
        card_type = self.controls["tipo"].GetValue()

        # Abilita/disabilita i campi in base al tipo di carta
        if card_type == EnuCardType.MAGIA.value:
            self.controls["tipo_magia"].Enable()
            self.controls["attacco"].Disable()
            self.controls["vita"].Disable()
            self.controls["durability"].Disable()
        elif card_type == EnuCardType.CREATURA.value:
            self.controls["tipo_magia"].Disable()
            self.controls["attacco"].Enable()
            self.controls["vita"].Enable()
            self.controls["durability"].Disable()
        elif card_type == EnuCardType.ARMA.value:
            self.controls["tipo_magia"].Disable()
            self.controls["attacco"].Enable()
            self.controls["vita"].Disable()
            self.controls["durability"].Enable()
        else:
            self.controls["tipo_magia"].Disable()
            self.controls["attacco"].Disable()
            self.controls["vita"].Disable()
            self.controls["durability"].Disable()

        # Imposta valori predefiniti per i campi disabilitati
        self.controls["tipo_magia"].SetValue("Qualsiasi")
        self.controls["attacco"].SetValue(0)
        self.controls["vita"].SetValue(0)
        self.controls["durability"].SetValue(0)

    def add_buttons(self, btn_sizer, buttons):
        """
        Aggiunge pulsanti alla finestra di dialogo.

        :param btn_sizer: Il sizer a cui aggiungere i pulsanti.
        :param buttons: Lista di tuple (label, handler) per i pulsanti.
        """
        for label, handler in buttons:
            btn = create_button(self.panel, label=label, event_handler=handler)
            btn_sizer.Add(btn, flag=wx.RIGHT, border=10)

    def on_save(self, event):
        """Salva la carta nel database."""
        try:
            card_data = {
                "name": self.controls["nome"].GetValue(),
                "mana_cost": self.controls["costo_mana"].GetValue(),
                "card_type": self.controls["tipo"].GetValue(),
                "spell_type": self.controls["tipo_magia"].GetValue() if self.controls["tipo_magia"].IsEnabled() else None,
                "card_subtype": self.controls["sottotipo"].GetValue() if self.controls["sottotipo"].GetValue() != "Tutti" else None,
                "attack": self.controls["attacco"].GetValue() if self.controls["attacco"].IsEnabled() else None,
                "health": self.controls["vita"].GetValue() if self.controls["vita"].IsEnabled() else None,
                "durability": self.controls["durability"].GetValue() if self.controls["durability"].IsEnabled() else None,
                "rarity": self.controls["rarita"].GetValue(),
                "expansion": self.controls["espansione"].GetValue()
            }

            # Ottieni le classi selezionate
            selected_classes = [self.classes_listbox.GetString(i) for i in self.classes_listbox.GetCheckedItems()]
            card_data["class_name"] = ", ".join(selected_classes)  # Salva come stringa separata da virgole

            if self.card:
                # Modifica la carta esistente
                for key, value in card_data.items():
                    setattr(self.card, key, value)
            else:
                # Aggiungi una nuova carta
                new_card = Card(**card_data)
                session.add(new_card)

            # Salva le modifiche nel database
            session.commit()
            self.EndModal(wx.ID_OK)  # Chiude la finestra
            self.parent.load_cards()  # Ricarica la lista delle carte
            self.parent.select_card_by_name(card_data["name"])  # Seleziona la carta appena salvata
            self.Destroy()

        except Exception as e:
            log.error(f"Errore durante il salvataggio: {str(e)}")
            wx.MessageBox(f"Errore durante il salvataggio: {str(e)}", "Errore", wx.OK | wx.ICON_ERROR)

    def on_close(self, event):
        """Chiude la finestra di dialogo."""
        self.parent.select_card_by_name(self.card)
        self.EndModal(wx.ID_CANCEL)



#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
