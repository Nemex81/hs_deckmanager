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
from .views.main_views import HearthstoneAppFrame
from utyls import enu_glob as eg
from utyls import helper as hp
from utyls import logger as log
#import pdb



class HearthstoneManager():
    """ gestore dell'applicazione. """

    def __init__(self, db_manager=None):
        self.db_manager = db_manager

    def run(self):
        app = wx.App(False)
        frame = HearthstoneAppFrame(None, title="Hearthstone Deck Manager, by Nemex81")
        frame.set_db_manager(self.db_manager)
        frame.Show()
        app.MainLoop()



#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
