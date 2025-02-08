"""

    Modulo di utilità per la gestione di uso generico

    path:
        utyls/helper.py

"""

# lib
import wx
import sys, random
from gtts import gTTS
from utyls import logger as log
#import pdb


def assemble_classes_string(classes_list):
    """
        Assemblare una stringa da un elenco di classi, separate da virgole.

        param classes_list: 
                                Elenco dei nomi delle classi(e.g., ["Mago", "Guerriero"]).
        return: 
                                Una stringa con classi separate da virgole (e.g., "Mago, Guerriero").
    """
    return ", ".join(classes_list)

def disassemble_classes_string(classes_string):
    """
        Smontare una stringa di classi in un elenco di nomi di classe.
    
        :param classes_string: 
                                        Una stringa con classi separate da virgole (e.g., "Mago, Guerriero").
        :return: 
                                        Un elenco di nomi di classi(e.g., ["Mago", "Guerriero"]).
    """
    if not classes_string:
        return []
    return [class_name.strip() for class_name in classes_string.split(",")]





def create_speech_mp3():
    # per avviare inserire  create_speech_mp3()
    text = input("Inserisci la frase da convertire in MP3: ")
    filename = input("Inserisci il nome del file MP3 (senza estensione): ")
    language = input("Inserisci la lingua (es. it per italiano): ")
    tts = gTTS(text, lang=language)
    tts.save(f"{filename}.mp3")
    print(f"File MP3 {filename}.mp3 creato con successo!")



#@@@# sezione funzioni helper specifiche per wx

def create_control(panel, label, control_class, **kwargs):
    """
    Crea un controllo UI con una label associata.
    
    :param panel: Il pannello a cui aggiungere il controllo.
    :param label: La label del controllo.
    :param control_class: La classe del controllo da creare.
    :param kwargs: Argomenti aggiuntivi per il controllo.
    :return: Il controllo creato e la riga contenente la label e il controllo.
    """
    row = wx.BoxSizer(wx.HORIZONTAL)
    row.Add(wx.StaticText(panel, label=label), flag=wx.RIGHT, border=10)
    control = control_class(panel, **kwargs)
    row.Add(control, proportion=1, flag=wx.EXPAND)
    return control, row


def create_button(panel, label, event_handler=None):
    """
    Crea un pulsante e collega un gestore di eventi.
    
    :param panel: Il pannello a cui aggiungere il pulsante.
    :param label: La label del pulsante.
    :param event_handler: Il gestore di eventi da collegare.
    :return: Il pulsante creato.
    """
    btn = wx.Button(panel, label=label)
    btn.Bind(wx.EVT_BUTTON, event_handler)
    return btn


def create_ui_controls(panel, controls):
    """
    Crea e posiziona i controlli UI in un pannello.
    
    :param panel: Il pannello a cui aggiungere i controlli.
    :param controls: Lista di tuple (label, control_class, kwargs) per i controlli.
    :return: Il sizer contenente i controlli e un dizionario con i controlli creati.
    """

    sizer = wx.BoxSizer(wx.VERTICAL)
    control_dict = {}
    for control_info in controls:
        if len(control_info) == 2:
            label, control_class = control_info
            kwargs = {}

        elif len(control_info) == 3:
            label, control_class, kwargs = control_info

        else:
            raise ValueError("Ogni controllo deve essere una tupla di 2 o 3 elementi: (label, control_class[, kwargs])")

        # Crea il controllo e la riga
        control, row = create_control(panel=panel, label=label, control_class=control_class, **kwargs)
        sizer.Add(row, flag=wx.EXPAND | wx.ALL, border=5)
        control_dict[label.lower().replace(" ", "_")] = control

    return sizer, control_dict


def create_search_bar(panel, on_search_handler):
    """Crea una barra di ricerca."""

    search_sizer = wx.BoxSizer(wx.HORIZONTAL)
    search_ctrl = wx.SearchCtrl(panel)
    search_ctrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, on_search_handler)
    search_sizer.Add(search_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
    return search_sizer, search_ctrl






#@@@# Start del modulo
if __name__ != "__main__":
    print("Carico: %s" % __name__)
