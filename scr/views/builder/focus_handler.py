"""
    focus_handler.py

    path:
        scr/views/builder/focus_handler.py
"""

# lib
import wx
from utyls import enu_glob as eg
from utyls import logger as log
#import pdb



class FocusHandler:
    """
    Classe per la gestione centralizzata degli eventi di focus e selezione.
    """

    def __init__(self):
        self.selected_item = None  # Memorizza l'elemento selezionato
        self.focus_style_applied = False  # Flag per lo stile di focus

    def bind_focus_events(self, element):
        """
        Collega gli eventi di focus a un elemento.
        :param element: L'elemento a cui collegare gli eventi (es. wx.ListCtrl, wx.Button, ecc.).
        """
        element.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        element.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)

    def on_focus(self, event):
        """
        Gestisce l'evento di focus.
        :param event: L'evento di focus.
        """
        self.selected_item = event.GetEventObject()
        self.apply_focus_style(self.selected_item)
        event.Skip()

    def on_kill_focus(self, event):
        """
        Gestisce l'evento di perdita del focus.
        :param event: L'evento di perdita del focus.
        """
        self.reset_focus_style(self.selected_item)
        self.selected_item = None
        event.Skip()

    def apply_focus_style(self, element):
        """
        Applica lo stile di focus a un elemento.
        :param element: L'elemento a cui applicare lo stile.
        """
        if element and not self.focus_style_applied:
            # Applica lo stile di focus (es. cambia colore di sfondo)
            element.SetBackgroundColour(wx.Colour(200, 200, 255))  # Esempio: colore azzurro
            element.Refresh()
            self.focus_style_applied = True

    def reset_focus_style(self, element):
        """
        Ripristina lo stile predefinito di un elemento.
        :param element: L'elemento a cui ripristinare lo stile.
        """
        if element and self.focus_style_applied:
            # Ripristina lo stile predefinito
            element.SetBackgroundColour(wx.NullColour)  # Ripristina il colore predefinito
            element.Refresh()
            self.focus_style_applied = False



#@@# End del modulo
if __name__ == "__main__":
    log.debug(f"Carico: {__name__}")
