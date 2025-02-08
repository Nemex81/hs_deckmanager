"""

    Modulo di utilità per la gestione di uso generico

    path:
        utyls/helper.py

"""


import sys, random
from gtts import gTTS
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





#@@@# Start del modulo
if __name__ != "__main__":
	print("Carico: %s" % __name__)
