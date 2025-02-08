"""
    controller.py

    Modulo principale per la gestione dell'applicazione Hearthstone Deck Manager.

    Path:
        scr/controller.py

    Componenti:

    - HearthstoneApp (Finestra principale):
        - Gestisce l'interfaccia utente principale tramite wxPython.
        - Visualizza l'elenco dei mazzi in un controllo (wx.ListCtrl) con colonne per nome, classe e formato.
        - Include una barra di ricerca per filtrare i mazzi.
        - Presenta vari pulsanti per operazioni quali aggiunta, copia, visualizzazione, aggiornamento, eliminazione dei mazzi, visualizzazione della collezione carte e uscita dall'applicazione.
        - Gestisce una barra di stato per mostrare messaggi informativi.
        
    - AppController (Controller):
        - Coordina le operazioni tra le interfacce utente e il gestore dei mazzi  e delle carte.

    Descrizione:

        Questo modulo rappresenta il cuore dell'applicazione, coordinando l'interazione tra le interfacce grafica, il database e la logica di gestione.

"""

# lib
import wx
import pyperclip
from sqlalchemy.exc import SQLAlchemyError
from scr.db import session, db_session,  Deck, DeckCard, Card
from scr.models import DbManager#, parse_deck_metadata
from scr.views import CardManagerDialog, CardCollectionDialog, DecksManagerDialog , DeckStatsDialog, DeckViewDialog
from scr.db import session
from utyls import enu_glob as eg
from utyls import logger as log
#import pdb



class AppController:
    """ Controller per la gestione delle operazioni dell'applicazione. """

    def __init__(self, db_manager, app):
        self.db_manager = db_manager
        self.app = app





class HearthstoneAppDialog(wx.Frame):
    """ Finestra principale dell'applicazione. """

    def __init__(self, parent, title):
        super(HearthstoneAppDialog, self).__init__(parent, title=title)
        self.db_manager = DbManager()
        self.app_controller = AppController(self.db_manager, self)
        # inizializzo l'istanza del giocatore
        font = wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.SetBackgroundColour(wx.BLACK)  # Imposta il colore di sfondo della finestra principale
        self.Maximize()

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


    #@@# sezione metodi di classe

    def on_collection_button_click(self, event):
        """ Metodo per gestire il click sul pulsante 'Collezione'. """
        collection_frame = CardCollectionDialog(self, self.app_controller)
        collection_frame.ShowModal()
        

    def on_decks_button_click(self, event):
        """ Metodo per gestire il click sul pulsante 'Gestione Mazzi'. """
        decks_frame = DecksManagerDialog(self, self.db_manager)
        decks_frame.Show()  # Mostra la finestra


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
