"""
    controller.py

    Modulo principale per la gestione dell'applicazione Hearthstone Deck Manager.

    Path:
        scr/controller.py

    Descrizione:
                Questo modulo rappresenta il cuore dell'applicazione, coordinando l'interazione tra le interfacce grafiche, il database e la logica di gestione.

"""

# lib
import wx
from scr.views import HearthstoneAppDialog
from utyls import logger as log
#import pdb



class HearthstoneManager():
    """ gestore dell'applicazione. """

    def __init__(self, db_manager=None):
        self.db_manager = db_manager

    def run(self):
        app = wx.App(False)
        frame = HearthstoneAppDialog(None, title="Hearthstone Deck Manager, by Nemex81")
        frame.Show()
        app.MainLoop()


#@@@# Start del modulo
if __name__ != "__main__":
    print("Carico: %s." % __name__)
