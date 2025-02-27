"""
    Modulo per la gestione sistemica dei colori

    path:
        scr/views/color_system.py

    Descrizione:
    
        Questo modulo contiene la classe ColorManager, che gestisce i colori dell'applicazione.
        La classe supporta temi e colori personalizzati, e fornisce metodi per applicare stili a elementi dell'interfaccia.

"""

# lib
import wx
from enum import Enum, auto


#@@# Sezione Enum per i colori e i temi

class ColorTheme(Enum):
    DARK = auto()
    LIGHT = auto()

class AppColors(Enum):
    DEFAULT_BG = auto()
    DEFAULT_TEXT = auto()
    FOCUS_BG = auto()
    FOCUS_TEXT = auto()
    ERROR_BG = auto()
    ERROR_TEXT = auto()


#@@# Sezione classe ColorManager

class ColorManager:
    """
    Classe per la gestione centralizzata dei colori nell'applicazione.
    Supporta temi e colori personalizzati.
    """

    def __init__(self, theme=ColorTheme.DARK):
        self.theme = theme
        self.colors = {
            ColorTheme.DARK: {
                AppColors.DEFAULT_BG: wx.BLACK,
                AppColors.DEFAULT_TEXT: wx.WHITE,
                AppColors.FOCUS_BG: wx.BLUE,
                AppColors.FOCUS_TEXT: wx.WHITE,
                AppColors.ERROR_BG: wx.RED,
                AppColors.ERROR_TEXT: wx.WHITE,
            },
            ColorTheme.LIGHT: {
                AppColors.DEFAULT_BG: wx.WHITE,
                AppColors.DEFAULT_TEXT: wx.BLACK,
                AppColors.FOCUS_BG: wx.BLUE,
                AppColors.FOCUS_TEXT: wx.WHITE,
                AppColors.ERROR_BG: wx.RED,
                AppColors.ERROR_TEXT: wx.WHITE,
            }
        }

    def get_color(self, color_name):
        """
        Restituisce il colore corrispondente al nome specificato.
        :param color_name: Un valore dell'enum AppColors.
        :return: Il colore wx.Colour corrispondente.
        """
        return self.colors[self.theme].get(color_name, wx.NullColour)

    def apply_style(self, element, bg_color, text_color):
        """
        Applica uno stile a un elemento dell'interfaccia.
        :param element: L'elemento a cui applicare lo stile.
        :param bg_color: Il colore di sfondo.
        :param text_color: Il colore del testo.
        """
        element.SetBackgroundColour(bg_color)
        element.SetForegroundColour(text_color)
        element.Refresh()

    def apply_default_style(self, element):
        """
        Applica lo stile predefinito a un elemento.
        :param element: L'elemento a cui applicare lo stile.
        """
        self.apply_style(
            element,
            self.get_color(AppColors.DEFAULT_BG),
            self.get_color(AppColors.DEFAULT_TEXT)
        )

    def apply_focus_style(self, element):
        """
        Applica lo stile di focus a un elemento.
        :param element: L'elemento a cui applicare lo stile.
        """
        self.apply_style(
            element,
            self.get_color(AppColors.FOCUS_BG),
            self.get_color(AppColors.FOCUS_TEXT)
        )

    def apply_error_style(self, element):
        """
        Applica lo stile di errore a un elemento.
        :param element: L'elemento a cui applicare lo stile.
        """
        self.apply_style(
            element,
            self.get_color(AppColors.ERROR_BG),
            self.get_color(AppColors.ERROR_TEXT)
        )


    def apply_default_style_to_list_item(self, list_ctrl, item_index):
        """
        Applica lo stile predefinito a un elemento di una ListCtrl.
        :param list_ctrl: La ListCtrl contenente l'elemento.
        :param item_index: L'indice dell'elemento da modificare.
        """
        list_ctrl.SetItemBackgroundColour(item_index, self.get_color(AppColors.DEFAULT_BG))
        list_ctrl.SetItemTextColour(item_index, self.get_color(AppColors.DEFAULT_TEXT))


    def apply_selection_style_to_list(self, list_ctrl, selected_item=None):
        """
        Applica lo stile di selezione a un elemento di una ListCtrl.
        :param list_ctrl: L'istanza di wx.ListCtrl.
        :param selected_item: L'indice della riga selezionata.
        """

        for i in range(list_ctrl.GetItemCount()):
            if i == selected_item:
                list_ctrl.SetItemBackgroundColour(i, self.get_color(AppColors.FOCUS_BG))
                list_ctrl.SetItemTextColour(i, self.get_color(AppColors.FOCUS_TEXT))

            else:
                list_ctrl.SetItemBackgroundColour(i, self.get_color(AppColors.DEFAULT_BG))
                list_ctrl.SetItemTextColour(i, self.get_color(AppColors.DEFAULT_TEXT))

        list_ctrl.Refresh()


    def reset_all_styles(self, container):
        """
        Resetta lo stile di tutti gli elementi figli di un contenitore.
        :param container: Il contenitore i cui figli devono essere resettati.
        """
        for child in container.GetChildren():
            if isinstance(child, (wx.Button, wx.ListCtrl)):
                self.apply_default_style(child)

    def set_theme(self, theme):
        """
        Imposta il tema corrente.
        :param theme: Un valore dell'enum ColorTheme.
        """
        self.theme = theme
