"""

    Progetto di gestione e salvataggio mazzi per Hearthstone

    Autore: Nemex81
    E-mail: nemex1981@gmail.com
    nome del progetto: Hearthstone Deck Manager
    Versione: 0.5

    path:
        ./main.py

    Descrizione:

        Questo progetto implementa un'applicazione per la gestione di mazzi del gioco di carte collezionabili Hearthstone.
        Permette di creare, salvare, caricare, modificare e visualizzare mazzi di Hearthstone.
        Include anche una funzionalità per la gestione di una collezione di carte, con la possibilità di filtrare le carte
        per nome, costo in mana, tipo, sottotipo, rarità ed espansione.

    Cartelle:
        - img:              Contiene le immagini utilizzate nell'applicazione.
        - scr:              Contiene i moduli principali dell'applicazione.
        - utyls:            Contiene funzioni, enum e costanti di utilità generiche in uso nel progetto.

    Moduli:

        - main.py:          Modulo principale. Avvia l'applicazione e gestisce le configurazioni generali.
        - app.py:           Contiene la logica dell'applicazione, incluse la finestra principale (HearthstoneAppDialog) e il controller (AppController).
        - db.py:            Gestisce l'interazione con il database SQLite per la memorizzazione delle carte. Definisce il modello Card e la funzione setup_database.
        - models.py:        Definisce la classe DeckManager per la gestione dei mazzi (caricamento, salvataggio, parsing, ecc.).
        - views.py:         Contiene le classi per le finestre di dialogo dell'interfaccia utente (CollectionDialog, FilterDialog, DeckStatsDialog).
        - config.py:        (Opzionale) Definisce le costanti di configurazione, come il percorso del database e altre costanti di sistema.
        - enu_glob.py:         Contiene le enum  globali in uso nel progetto.
        - helper.py:         Contiene funzioni di utilità generiche utilizzate in tutto il progetto.
        - logger.py:        Contiene la classe Logger per la gestione dei log dell'applicazione.
        - screen_reader.py:  Contiene la classe ScreenReader per la lettura dello schermo e l'interazione con le finestre di Hearthstone.

    Funzionamento:

        L'applicazione utilizza la libreria wxPython per l'interfaccia grafica e SQLAlchemy per la gestione del database.
        I mazzi sono salvati in un file JSON (decks.json, configurabile in config.py).
        Le carte sono memorizzate in un database SQLite (hearthstone_decks_storage.db, configurabile in config.py).

    Esecuzione:

        Per avviare l'applicazione, eseguire il comando:
            python main.py

---

    Note:
        - Il modulo sfrutta il pattern MVC in maniera semplificata, con HearthstoneAppDialog che rappresenta la vista e AppController che gestisce la logica applicativa.
        - La gestione dei mazzi si avvale di DbManager, il quale si occupa anche di importare mazzi dagli appunti, effettuare parsing dei dati e interfacciarsi con il database.
        - La classe AppController si occupa di coordinare le operazioni tra l'interfaccia utente e il DbManager, gestendo eventi e operazioni CRUD sui mazzi.

"""

# lib
import wx
from scr.controller import HearthstoneAppDialog
from scr.views import DecksManagerDialog


def start_app():
    app = wx.App(False)
    frame = HearthstoneAppDialog(None, "Hearthstone Deck Manager")
    frame.Show()
    app.MainLoop()



if __name__ == "__main__":
    start_app()