"""
    Modulo contenente la classe DeckStatsDialog, una finestra di dialogo per visualizzare le statistiche di un mazzo.

    path:
        scr/views/deck_stats_dialog.py

"""

# lib
import wx
from .view_components import create_sizer, add_to_sizer, create_button
from .proto_views import BasicDialog
from utyls import enu_glob as eg
from utyls import helper as hp
from utyls import logger as log
#import pdb



class DeckStatsDialog(BasicDialog):
    """Finestra di dialogo per visualizzare le statistiche di un mazzo."""

    def __init__(self, parent, stats):
        super().__init__(parent, title="Statistiche Mazzo", size=(300, 390))
        self.parent = parent
        self.stats = stats              # Inizializza l'attributo stats
        self.init_ui_elements()         # Inizializza gli elementi dell'interfaccia utente

    def init_ui(self):
        pass

    def init_ui_elements(self):
        """Inizializza l'interfaccia utente utilizzando le funzioni helper."""

        # Impostazioni finestra principale
        self.SetBackgroundColour('yellow')
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.YELLOW)

        # Creazione degli elementi dell'interfaccia
        main_sizer = create_sizer(wx.VERTICAL)

        # Titolo
        title = wx.StaticText(self.panel, label="Statistiche del Mazzo")
        title.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        add_to_sizer(main_sizer, title, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        # Statistiche
        stats = self.stats
        for key, value in stats.items():
            row_sizer = create_sizer(wx.HORIZONTAL)
            add_to_sizer(row_sizer, wx.StaticText(self.panel, label=f"{key}:"), flag=wx.LEFT, border=20)
            add_to_sizer(row_sizer, wx.StaticText(self.panel, label=str(value)), flag=wx.LEFT | wx.RIGHT, border=20)
            add_to_sizer(main_sizer, row_sizer, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)

        # Separatore tra le statistiche e il pulsante Chiudi
        add_to_sizer(main_sizer, wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        # Pulsante Chiudi
        btn_close = create_button(self.panel, label="Chiudi", size=(100, 30), event_handler=lambda e: self.Close())
        add_to_sizer(main_sizer, btn_close, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        # Imposta il sizer principale
        self.panel.SetSizer(main_sizer)
        self.Layout()               # Forza il ridisegno del layout




#@@# End del modulo
if __name__ == "__main__":
    log.debug(f"Carico: {__name__}")
