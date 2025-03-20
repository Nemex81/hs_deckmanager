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
from .builder.view_components import create_button, create_check_list_box, create_separator, create_common_controls
from .builder.proto_views import SingleCardView
from utyls.enu_glob import EnuCardType, EnuSpellType, EnuSpellSubType, EnuPetSubType, EnuHero, EnuRarity, EnuExpansion
from utyls import enu_glob as eg
from utyls import helper as hp
from utyls import logger as log
#import pdb



class CardEditDialog(SingleCardView):
    """Finestra di dialogo per aggiungere o modificare una carta."""

    def __init__(self, parent, card=None):
        self.parent = parent
        title = "Modifica Carta" if card else "Aggiungi Carta"
        self.card = card
        super().__init__(parent, title=title, size=(400, 700))


    def init_ui_elements(self):
        """Inizializza i componenti specifici per CardEditDialog."""

        # Imposta il colore di sfondo del pannello a blu e il font a bianco
        self.panel.SetBackgroundColour(wx.Colour(0, 0, 255))  # Sfondo blu
        self.panel.SetForegroundColour(wx.Colour(255, 255, 255))  # Font bianco

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

            # Aggiungi il controllo al dizionario per accedervi facilmente
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

        # Aggiungi il sizer delle classi al sizer principale
        main_sizer.Add(classes_label, flag=wx.LEFT | wx.RIGHT, border=10)
        main_sizer.Add(self.classes_listbox, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Sizer per i pulsanti
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add_buttons(btn_sizer, [("Salva", self.on_save), ("Annulla", self.on_close)])

        # Centra i pulsanti rispetto al contenitore
        btn_container = wx.BoxSizer(wx.VERTICAL)
        btn_container.AddStretchSpacer()
        btn_container.Add(btn_sizer, 0, wx.ALIGN_CENTER)
        btn_container.AddStretchSpacer()

        # Aggiungi il sizer dei pulsanti al sizer principale
        main_sizer.Add(btn_container, proportion=0, flag=wx.EXPAND | wx.ALL, border=10)

        # Imposta il sizer principale per il pannello
        self.panel.SetSizer(main_sizer)
        main_sizer.Fit(self.panel)

        # Se è una modifica, pre-carica i dati della carta
        if self.card:
            self.load_card_data()

        # Aggiorna i sottotipi della carta
        self.update_subtypes()
        self.apply_type_change()

        # Importa il layout
        self.Layout()

    def last_init_ui_elements(self):
        """Inizializza i componenti specifici per CardEditDialog."""

        # coloro di verde il bg del pannello
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

            # Aggiungi il controllo al dizionario per accedervi facilmente
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

        # Aggiungi il sizer delle classi al sizer principale
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

        # aggiorno i sottotipo della carta
        self.update_subtypes()
        self.apply_type_change()

        # importo il layout
        self.Layout()


    def load_card_data(self):
        """Carica i dati della carta nei controlli UI."""

        if not self.card:
            log.error("Impossibile caricare i dati della carta: nessuna carta specificata.")
            return

        # Carica i dati della carta nei controlli
        self.controls["nome"].SetValue(self.card.name or "")
        self.controls["costo_mana"].SetValue(self.card.mana_cost or 0)
        self.controls["tipo"].SetValue(self.card.card_type or "-")
        self.controls["tipo_magia"].SetValue(self.card.spell_type or "-")
        self.update_subtypes()
        self.controls["sottotipo"].SetValue(self.card.card_subtype or "-")
        self.controls["attacco"].SetValue(self.card.attack or "-")
        self.controls["vita"].SetValue(self.card.health or "-")
        self.controls["durability"].SetValue(self.card.durability or "-")
        self.controls["rarita"].SetValue(self.card.rarity or "-")
        self.controls["espansione"].SetValue(self.card.expansion or "-")

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
        self.controls["sottotipo"].AppendItems(subtypes)

        # Ripristina il sottotipo se presente nei nuovi sottotipi
        if current_subtype and current_subtype in subtypes:
            self.controls["sottotipo"].SetValue(current_subtype)
        else:
            self.controls["sottotipo"].SetValue("-")


    def apply_type_change(self):
        """Applica il cambio del tipo di carta."""

        card_type = self.controls["tipo"].GetValue()

        # Abilita/disabilita i campi in base al tipo di carta
        if card_type == EnuCardType.MAGIA.value:
            self.controls["tipo_magia"].Enable()
            self.controls["sottotipo"].Enable()
            self.controls["attacco"].Disable()
            self.controls["vita"].Disable()
            self.controls["durability"].Disable()

        elif card_type == EnuCardType.CREATURA.value:
            self.controls["tipo_magia"].Disable()
            self.controls["durability"].Disable()
            self.controls["attacco"].Enable()
            self.controls["vita"].Enable()

        elif card_type == EnuCardType.ARMA.value:
            self.controls["tipo_magia"].Disable()
            self.controls["vita"].Disable()
            self.controls["attacco"].Enable()
            self.controls["durability"].Enable()

        else:
            self.controls["tipo_magia"].Disable()
            self.controls["attacco"].Disable()
            self.controls["vita"].Disable()
            self.controls["durability"].Disable()


    def on_type_change(self, event):
        """Gestisce il cambio del tipo di carta."""

        #card_type = self.controls["tipo"].GetValue()
        self.update_subtypes()
        self.apply_type_change()


    def add_buttons(self, btn_sizer, buttons):
        """
        Aggiunge pulsanti alla finestra di dialogo.

        :param btn_sizer: Il sizer a cui aggiungere i pulsanti.
        :param buttons: Lista di tuple (label, handler) per i pulsanti.
        """
        for label, handler in buttons:
            btn = create_button(self.panel, label=label, event_handler=handler)
            
            # Imposta lo stile dei pulsanti
            if label == "Salva":
                btn.SetBackgroundColour(wx.Colour('green')) 
                btn.SetForegroundColour(wx.Colour('black')) 
            elif label == "Annulla":
                btn.SetBackgroundColour(wx.Colour('red'))  # Sfondo rosso
                btn.SetForegroundColour(wx.Colour('black'))  # Font bianco

            btn_sizer.Add(btn, flag=wx.RIGHT, border=10)

    def last_add_buttons(self, btn_sizer, buttons):
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
                "card_subtype": self.controls["sottotipo"].GetValue() if self.controls["sottotipo"].GetValue() else None,
                "attack": self.controls["attacco"].GetValue() if self.controls["attacco"].IsEnabled() else None,
                "health": self.controls["vita"].GetValue() if self.controls["vita"].IsEnabled() else None,
                "durability": self.controls["durability"].GetValue() if self.controls["durability"].IsEnabled() else None,
                "rarity": self.controls["rarita"].GetValue() if self.controls["rarita"].GetValue() else None,
                "expansion": self.controls["espansione"].GetValue() if self.controls["espansione"].GetValue() else None,
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

            session.commit()            # Salva le modifiche nel database
            self.EndModal(wx.ID_OK)     # Chiude la finestra

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
