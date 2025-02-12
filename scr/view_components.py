"""
    Modulo per la gestione dei componenti delle views

    path:
        ./scr/view_components.py

    Descrizione:
    
        

"""

#lib
import os, re, shutil, pyperclip, wx
from .db import session, db_session, Deck, DeckCard, Card
from abc import ABC, abstractmethod
from utyls import enu_glob as eg
from utyls import logger as log
#import pdb



class BasicView(wx.Dialog):
    """
        Classe base per le finestre di dialogo dell'interfaccia utente.
    """
    def __init__(self, parent, title, size=(500, 400)):
        super().__init__(parent=parent, title=title, size=size)
        self.parent = parent
        self.init_ui()
        self.Centre()
        self.Show()

    def init_ui(self):
        """ Inizializza l'interfaccia utente. """
        self.SetBackgroundColour('black')
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.sizer)
        self.init_ui_elements()

    @abstractmethod
    def init_ui_elements(self, *args, **kwargs):
        """ Inizializza gli elementi dell'interfaccia utente. """
        pass

    def close(self, event):
        """ Chiude la finestra di dialogo. """
        self.close()






#@@# End del modulo
if __name__ == "__main__":
    print("Carico: %s" % __name__)
