"""
    file screen_reader.py
    percorso: main/scr/screen_reader.py

    Modulo per la Classe ScreenReader per la gestione delle sintesi vocali.

    Questa classe si occupa della gestione degli screen reader, utilizzati per vocalizzare messaggi all'utente.

    Metodi:
        - __init__(): metodo di inizializzazione della classe.
        - Vocalizza(string): vocalizza il messaggio passato come argomento.
        - SayLog(): legge la voce selezionata nel log degli eventi.
        - SayLastLog(): legge l'ultima voce salvata nel log degli eventi.
        - NextLog(): scorrimento in avanti della lista log eventi e vocalizzazione.
        - PriorLog(): scorrimento in indietro della lista log eventi e vocalizzazione.
        - MoveToFirstLog(): sposta il cursore al primo log eventi e vocalizza.
        - MoveToLastLog(): sposta il cursore all'ultimo log eventi e vocalizza.
        - AddLogToList(testo): aggiunge un nuovo messaggio di sistema al dizionario di log degli eventi.
        - SaveLogToFile(): salva su file il log degli eventi di gioco.

"""

# lib
import os, sys, random, time
from enum import Enum
import accessible_output2.outputs.auto
from utyls import helper as mu
from utyls import logger as log
#import pdb #pdb.set_trace() da impostare dove si vuol far partire il debugger

# Imposta la configurazione del logger
#logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)

# inizializzo l'engine per la vocalizzazione
engine = accessible_output2.outputs.auto.Auto()

#@@@# classe per la gestione dell'interfaccia utente
class ScreenReader:
    def __init__(self):
        # costanti
        self.syspath = "./"  # path di sistema per la directory del gioco
        self.listlog = {}  # dizionario per la lista degli eventi da vocalizzare
        self.idlog = 0
        self.lastidlog = 0
        self.modlog = True  # interruttore per la modalità log degli eventi
        self.is_working = False  # su true abilita la progressione automatica della versione ad ogni compilazione
        self.engine = engine  # motore di sintesi vocale
        self.timers = {}  # Dizionario per memorizzare i timer degli elementi
        self.focus_delay = 2000  # Ritardo in millisecondi per la vocalizzazione (2 secondi)

    #@@# sezione metodi di classe

    def validate_log_string(self, string):
        lista = list(string.strip("\n"))
        num_tyles = len(lista)
        num = 0
        fineriga = 0
        nuova = []
        for i in lista:
            num += 1
            if i == "\n":
                fineriga += 1

        stat = f"caratteri nella stringa: {num}, carattteri di acapo rilevati: {fineriga}."
        return stat

    def speak(self, string):
        """
        Questo metodo vocalizza il testo passato come parametro utilizzando il motore di sintesi vocale.
        Inoltre, aggiunge il testo passato alla lista dei messaggi di log e lo salva su file, se la modalità log è attiva.

        Args:
            string (str): Il testo da vocalizzare.

        Returns:
            None
        """
        # verifichiamo la validità di string
        new_string = str(self.validate_log_string(string))
        if string:
            self.AddLogToList(string)
            self.engine.speak(string, interrupt=True)

    def register_element(self, element, description):
        """
        Registra un elemento dell'interfaccia per la gestione delle vocalizzazioni.

        :param element: L'elemento da registrare (es. wx.Button, wx.ListCtrl).
        :param description: La descrizione da vocalizzare.
        """
        if not element:
            log.error("Elemento non valido per la registrazione.")
            return

        # Collega gli eventi di focus
        element.Bind(wx.EVT_SET_FOCUS, lambda e: self.on_focus(element, description))
        element.Bind(wx.EVT_KILL_FOCUS, lambda e: self.on_kill_focus(element))

    def on_focus(self, element, description):
        """
        Gestisce l'evento di focus su un elemento.
        """
        if element in self.timers:
            self.timers[element].Stop()  # Ferma il timer precedente, se presente

        # Avvia un nuovo timer per la vocalizzazione
        timer = wx.Timer()
        timer.Bind(wx.EVT_TIMER, lambda e: self.speak_description(description))
        timer.Start(self.focus_delay, oneShot=True)
        self.timers[element] = timer

    def on_kill_focus(self, element):
        """
        Gestisce l'evento di perdita del focus su un elemento.
        """
        if element in self.timers:
            self.timers[element].Stop()  # Ferma il timer
            del self.timers[element]  # Rimuove il timer dal dizionario

    def speak_description(self, description):
        """
        Vocalizza la descrizione dell'elemento.
        """
        if description:
            self.engine.speak(description, interrupt=True)
        else:
            log.warning("Nessuna descrizione disponibile per l'elemento.")

    #@@# sezione creazione e gestione log degli eventi

    def SayLog(self):
        """ 
        legge l'attuale voce selezionata nel log degli eventi 

        Descrizione:
            Il metodo legge l'evento corrente selezionato nel log degli eventi e lo vocalizza utilizzando l'engine di sintesi vocale specificato.
            Viene composto un messaggio vocale concatenando l'indice dell'evento corrente e il relativo contenuto. 
            Se il messaggio vocale è stato composto correttamente, l'engine di sintesi vocale viene utilizzato per riprodurre il messaggio vocalmente.
        """
        lastlog = self.listlog[self.idlog]
        testo = "%s: %s" % (self.idlog, lastlog)
        if testo:
            self.engine.speak(testo, interrupt=True)

    def SayLastLog(self):
        """ 
        legge l'ultima voce salvata nel log degli eventi 

        Descrizione:
            Il metodo permette di leggere ad alta voce l'ultima voce salvata nel log degli eventi. 
            In particolare, il metodo determina l'ultima voce salvata nel log degli eventi e costruisce una stringa di testo contenente l'ID della voce e il suo contenuto, in modo simile al metodo  `SayLog`.
            Successivamente, il metodo utilizza il motore di sintesi vocale per leggere la stringa di testo ad alta voce.
        """
        lastidlog = mu.dlen(self.listlog)
        lastlog = self.listlog[lastidlog]
        self.idlog = lastidlog 
        testo = "%s: %s.  " % (self.idlog, lastlog)
        self.engine.speak(testo, interrupt=True)

    def NextLog(self):
        """ scorrimento in avanti della lista log eventi e vocalizzazione"""
        lastidlog = mu.dlen(self.listlog)
        if self.idlog < lastidlog:
            self.idlog += 1
            self.SayLog()
        else:
            self.idlog = lastidlog

    def PriorLog(self):
        """ scorrimento in indietro della lista log eventi e vocalizzazione"""
        lastidlog = mu.dlen(self.listlog)
        if self.idlog > 1:
            self.idlog -= 1
            self.SayLog()
        elif self.idlog <= 1:
            self.idlog = 1

    def MoveToFirstLog(self):
        self.idlog = 1
        testo = "%s: %s.  " % (self.idlog, self.listlog[self.idlog])
        self.SayLog()

    def MoveToLastLog(self):
        lastidlog = mu.dlen(self.listlog)
        self.idlog = lastidlog
        testo = "%s: %s.  " % (self.idlog, self.listlog[self.idlog])
        self.SayLog()

    def AddLogToList(self, testo):
        """
        Aggiunge il nuovo messaggio di sistema al dizionario log degli eventi.

        Args:
            testo (str): Il testo del messaggio da aggiungere al log degli eventi.

        Descrizione:
            Questo metodo è utilizzato per aggiungere un nuovo messaggio di sistema al dizionario del log degli eventi. 
            Il parametro è una stringa che rappresenta il testo del messaggio da aggiungere al log.`testo`
            Il metodo inizialmente controlla se non è una stringa vuota. In caso affermativo, determina la chiave del nuovo elemento del dizionario, incrementando il numero totale di elementi del dizionario e aggiungendo 1. 
            Quindi, viene utilizzato il metodo per aggiungere il nuovo messaggio al dizionario.`testo``setdefault()`
            Infine, se la modalità di log è abilitata, viene chiamato il metodo per salvare il log su file.
        """
        if testo:
            newkey = mu.dlen(self.listlog) + 1
            self.listlog.setdefault(newkey, testo)
            if not self.modlog:
                return

            #self.SaveLogToFile()

    def SaveLogToFile(self):
        """
        Salva il log degli eventi di gioco su un file.

        Descrizione:
            Il file viene salvato nella directory del gioco con il nome 'gamelog.txt'.
            Ogni voce del log è composta da un numero identificativo e la corrispondente voce.
            Il numero e la voce sono separati da uno spazio e ogni voce è separata da una nuova riga.
        """
        listlog = self.listlog
        path = self.syspath
        nomefile = "gamelog.txt"
        writefile = "%s%s" % (path, nomefile)
        with open(writefile, "w") as document:
            for k in listlog:
                value = listlog[k]
                string = "%s %s\n" % (k, value)
                document.write(string)

            document.close()



#@@@# Start del modulo
if __name__ == "__main__":
    print("compilazione di %s completata." % __name__)

else:
    log.debug(f"Carico: {__name__}")
