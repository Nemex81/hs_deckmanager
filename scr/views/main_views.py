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
import wx#, pyperclip
from .builder.proto_views import BasicView
from utyls import enu_glob as eg
from utyls import helper as hp
from utyls import logger as log
#import pdb



class HearthstoneAppFrame(BasicView):
    """ Finestra principale dell'applicazione. """

    def __init__(self, parent=None, controller=None, container=None, **kwargs):
        super().__init__(parent=parent, title="Hearthstone Deck Manager by Nemex81", size=(900, 700), container=container)
        log.debug("Creazione finestra principale.")

        # catturo gli eventi da tastiera
        #self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
        #self.Bind(wx.EVT_SET_FOCUS, self.read_focused_element)

        log.info("Finestra principale creata.")


    def init_ui_elements(self):
        """ Inizializza gli elementi dell'interfaccia utente. """

        # Aggiungo l'immagine
        image = wx.Image("img/background_magic.jpeg", wx.BITMAP_TYPE_ANY)
        image = image.Scale(1200, 790)  # Ridimensiona l'immagine
        bitmap = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(image))

        # Creazione pulsanti tramite WidgetFactory
        self.collection_button = self.widget_factory.create_button(
            parent=self.panel, 
            label="Collezione", 
            event_handler=self.on_collection_button_click
        )
        #self.collection_button.Bind(wx.EVT_SET_FOCUS, self.on_focus)

        self.decks_button = self.widget_factory.create_button(
            parent=self.panel, 
            label="Gestione Mazzi", 
            event_handler=self.on_decks_button_click
        )

        self.quit_button = self.widget_factory.create_button(
            parent=self.panel,
            label="Esci",
            event_handler=self.on_quit_button_click
        )

        # Aggiungo un sizer per allineare i pulsanti verticalmente
        button_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer.Add(self.collection_button, 0, wx.ALL, 20)
        button_sizer.Add(self.decks_button, 0, wx.ALL, 20)
        button_sizer.Add(self.quit_button, 0, wx.ALL, 20)

        for child in button_sizer.GetChildren():
            button = child.GetWindow()
            self.bind_focus_events(button)  # Collega gli eventi di focus

        # Creazione sizer principale orizzontale per allineare l'immagine e i pulsanti
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(bitmap, proportion=0, flag=wx.ALL, border=10)
        main_sizer.Add(button_sizer, 1, wx.ALIGN_CENTER | wx.ALL, 0)

        self.panel.SetSizer(main_sizer)
        self.Layout()


    def read_focused_element(self, event):
        """Legge l'elemento attualmente in focus."""
        self.controller.read_focused_element(event=event, frame=self)
        event.Skip()

    #@@# sezione metodi collegati agli eventi

    def on_focus(self, event):
        """Gestisce l'evento di focus."""
        self.controller.on_focus(event=event, frame=self)
        event.Skip()

    def on_kill_focus(self, event):
        """Gestisce l'evento di perdita del focus."""
        self.controller.on_kill_focus(event=event, frame=self)
        event.Skip()


    def on_key_down(self, event):
        """
            Gestisce i tasti premuti .
            :param event:   l'evento generato dalla pressione di un tasto
        """
        super().on_key_down(event)      # Chiamata al metodo della classe genitore
        #event.skip(False)



    def on_collection_button_click(self, event):
        """Apre la finestra della collezione."""
        self.win_controller.create_collection_window(parent=self)


    def on_decks_button_click(self, event):
        """Apre la finestra dei mazzi."""
        self.win_controller.create_decks_window(parent=self)


    def on_quit_button_click(self, event):
        """Chiude l'applicazione."""
        self.controller.question_quit_app(frame=self)



#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
