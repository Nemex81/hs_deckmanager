"""

    main_view.py

    Modulo per la finestra principale dell'applicazione.

    path:
        scr/views.py

    Note:
        - Questo modulo contiene la classe HearthstoneAppFrame, che rappresenta la finestra principale dell'applicazione.
        - La finestra principale include pulsanti per accedere alla gestione della collezione di carte, alla gestione dei mazzi, alla palestra e alle impostazioni.

"""

# lib
import wx, pyperclip
from .view_components import create_button
from .proto_views import BasicView
from utyls import enu_glob as eg
from utyls import helper as hp
from utyls import logger as log
#import pdb



class HearthstoneAppFrame(BasicView):
    """ Finestra principale dell'applicazione. """

    def __init__(self, parent, controller):
        title = "earthstone Deck Manager by Nemex81"
        super(HearthstoneAppFrame, self).__init__(parent, title=title, size=(900, 700))
        #font = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)    # Imposta il font per la finestra principale
        #self.SetFont(font)
        if not controller:
            log.error("Errore: controller non definito.")
            raise ValueError("Il controller non può essere nullo.")

        self.parent=parent
        self.controller = controller


    def init_ui_elements(self):
        """ Inizializza gli elementi dell'interfaccia utente. """

        # Aggiungo l'immagine
        image = wx.Image("img/background_magic.jpeg", wx.BITMAP_TYPE_ANY)
        image = image.Scale(1200, 790)  # Ridimensiona l'immagine
        bitmap = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(image))

        # Creazione pulsanti
        self.collection_button = create_button(
            self.panel, 
            label="Collezione", 
            event_handler=self.on_collection_button_click
        )

        self.decks_button = create_button(
            self.panel, 
            label="Gestione Mazzi", 
            event_handler=self.on_decks_button_click
        )

        self.quit_button = create_button(
            self.panel,
            label="Esci",
            event_handler=self.on_quit_button_click
        )

        # Aggiungo un sizer per allineare i pulsanti verticalmente
        button_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer.Add(self.collection_button, 0, wx.ALL, 20)
        button_sizer.Add(self.decks_button, 0, wx.ALL, 20)
        button_sizer.Add(self.quit_button, 0, wx.ALL, 20)

        # Creazione sizer principale orizzontale per allineare l'immagine e i pulsanti
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(bitmap, proportion=0, flag=wx.ALL, border=10)
        main_sizer.Add(button_sizer, 1, wx.ALIGN_CENTER | wx.ALL, 0)

        self.panel.SetSizer(main_sizer)
        self.Layout()


    #@@# sezione metodi collegati agli eventi

    def on_collection_button_click(self, event):
        """ Metodo per gestire il click sul pulsante 'Collezione'. """
        self.controller.run_collection_frame(parent=self)


    def on_decks_button_click(self, event):
        """ Metodo per gestire il click sul pulsante 'Collezione'. """
        self.controller.run_decks_frame(parent=self)


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
    log.debug(f"Carico: {__name__}")
