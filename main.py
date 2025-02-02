"""
Progetto gestione e salvataggio mazzi di Hearthstone

Autore: Nemex81
E-mail: nemex1981@gmail.com
Versione: 0.5

path:
    ./main.py

Descrizione:

    Questo progetto implementa un'applicazione per la gestione di mazzi del gioco di carte collezionabili Hearthstone.
    Permette di creare, salvare, caricare, modificare e visualizzare mazzi di Hearthstone.
    Include anche una funzionalità per la gestione di una collezione di carte, con la possibilità di filtrare le carte
    per nome, costo in mana, tipo, sottotipo, rarità ed espansione.

Moduli:

    - main.py:          Modulo principale. Avvia l'applicazione e gestisce le configurazioni generali.
    - app.py:           Contiene la logica dell'applicazione, incluse la finestra principale (HearthstoneApp) e il controller (AppController).
    - db.py:            Gestisce l'interazione con il database SQLite per la memorizzazione delle carte. Definisce il modello Card e la funzione setup_database.
    - models.py:        Definisce la classe DeckManager per la gestione dei mazzi (caricamento, salvataggio, parsing, ecc.).
    - views.py:         Contiene le classi per le finestre di dialogo dell'interfaccia utente (CollectionDialog, FilterDialog, DeckStatsDialog).
    - config.py:        (Opzionale) Definisce le costanti di configurazione, come il percorso del database e il percorso del file JSON dei mazzi.

Funzionamento:

    L'applicazione utilizza la libreria wxPython per l'interfaccia grafica e SQLAlchemy per la gestione del database.
    I mazzi sono salvati in un file JSON (decks.json, configurabile in config.py).
    Le carte sono memorizzate in un database SQLite (hearthstone_decks_storage.db, configurabile in config.py).

Esecuzione:

    Per avviare l'applicazione, eseguire il comando:
        python main.py

librerie necessarie:
                        pip install wxPython sqlalchemy pyperclip

"""

"""
main.py

Punto di ingresso principale dell'applicazione.
"""

# lib
import wx
from scr.app import HearthstoneApp

if __name__ == "__main__":
    app = wx.App(False)
    frame = HearthstoneApp(None, title="Hearthstone Deck Manager", size=(650, 700))
    frame.Show()
    app.MainLoop()
