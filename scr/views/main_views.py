"""

    main_view.py

    Modulo per la finestra principale dell'applicazione.

    path:
        scr/views.py

    Note:
        - Questo modulo contiene la classe HearthstoneAppFrame, che rappresenta la finestra principale dell'applicazione.
        - La finestra principale include pulsanti per accedere alla gestione della collezione di carte, alla gestione dei mazzi, alla palestra e alle impostazioni.
        - Questo modulo utilizza la libreria wxPython per la creazione delle finestre di dialogo dell'interfaccia utente.

"""

# lib
import wx, pyperclip
from sqlalchemy.exc import SQLAlchemyError
from ..models import DbManager, AppController
from ..db import session, Card, DeckCard, Deck
from ..models import load_cards_from_db, load_deck_from_db, load_cards
from .view_components import BasicView
from .collection_view import CardCollectionFrame
from .decks_view import DecksManagerFrame
from utyls.enu_glob import EnuColors, ENUCARD, EnuExtraCard, EnuCardType, EnuSpellType, EnuSpellSubType, EnuPetSubType, EnuHero, EnuRarity, EnuExpansion
from utyls import helper as hp
from utyls import logger as log
#import pdb





class HearthstoneAppFrame(BasicView):
    """ Finestra principale dell'applicazione. """

    def __init__(self, parent, title):
        super(HearthstoneAppFrame, self).__init__(parent, title=title, size=(900, 700))
        self.db_manager = None
        font = wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)    # Imposta il font per la finestra principale
        self.SetBackgroundColour(wx.BLACK)                                                      # Imposta il colore di sfondo della finestra principale
        self.Maximize()                                                                         # Massimizza la finestra principale
        #self.init_ui_elements()                                                                 # Inizializza gli elementi dell'interfaccia utente

    def set_db_manager(self, db_manager):
        """ Imposta il controller del database. """
        self.db_manager = db_manager


    def init_ui_elements(self, *args, **kwargs):
        """ Inizializza gli elementi dell'interfaccia utente. """

        # pannello per contenere gli elementi dell'interfaccia utente
        #self.panel = wx.Panel(self)

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
    log.debug(f"Carico: {__name__}")
