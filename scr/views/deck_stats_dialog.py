"""
    Modulo contenente la classe DeckStatsDialog, una finestra di dialogo per visualizzare le statistiche di un mazzo.

    path:
        scr/views/deck_stats_dialog.py

"""

# lib
import wx
from .view_components import BasicDialog, SingleCardView
from utyls.enu_glob import EnuCardType, EnuSpellType, EnuSpellSubType, EnuPetSubType, EnuHero, EnuRarity, EnuExpansion
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
        """ Inizializza gli elementi dell'interfaccia utente. """

        # Imposta il colore di sfondo della finestra
        self.SetBackgroundColour('yellowe')

        # Crea un panel e imposta il suo colore di sfondo
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.YELLOW)  # Imposta un colore di sfondo contrastante

        # Crea un sizer verticale per il panel
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Titolo
        title = wx.StaticText(self.panel, label="Statistiche del Mazzo")
        title.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.sizer.Add(title, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        # Statistiche
        stats = self.stats
        for key, value in stats.items():
            row = wx.BoxSizer(wx.HORIZONTAL)
            row.Add(wx.StaticText(self.panel, label=f"{key}:"), flag=wx.LEFT, border=20)
            row.Add(wx.StaticText(self.panel, label=str(value)), flag=wx.LEFT | wx.RIGHT, border=20)
            self.sizer.Add(row, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)

        # Separatore tra le statistiche e il pulsante Chiudi
        self.sizer.Add(wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        # Pulsante Chiudi
        btn_close = wx.Button(self.panel, label="Chiudi", size=(100, 30))
        btn_close.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        self.sizer.Add(btn_close, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        # Imposta il sizer per il panel
        self.panel.SetSizer(self.sizer)

        self.Layout()               # Forza il ridisegno del layout