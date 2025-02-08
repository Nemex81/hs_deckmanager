"""

    Progetto di gestione e salvataggio mazzi di Hearthstone

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

    librerie necessarie:
                            pip install wxPython sqlalchemy pyperclip
---

    db.py

    Modulo per la gestione del database SQLite e dei modelli SQLAlchemy.

    Path:
        scr/db.py

    Descrizione:

        Questo modulo gestisce la connessione a un database SQLite per la memorizzazione delle carte e dei mazzi di Hearthstone.
        Definisce tre modelli principali:

            - `Card`: Rappresenta una singola carta del gioco.
            - `Deck`: Rappresenta un mazzo di carte.
            - `DeckCard`: Gestisce la relazione tra mazzi e carte, inclusa la quantità di ciascuna carta in un mazzo.

        Include una funzione `setup_database` che crea le tabelle del database se non esistono già.

    Funzionalità principali:

        - Creazione, lettura, aggiornamento ed eliminazione (CRUD) di carte e mazzi.
        - Gestione delle relazioni tra mazzi e carte.
        - Configurazione automatica del database SQLite.

    Esempio di utilizzo:
        from db import session, Card, Deck, DeckCard

        # Aggiungere una nuova carta
        new_card = Card(name="Dragone Rosso", mana_cost=8, card_type="Creatura")
        session.add(new_card)
        session.commit()

        # Creare un nuovo mazzo
        new_deck = Deck(name="Aggro Mage", player_class="Mage", game_format="Standard")
        session.add(new_deck)
        session.commit()

        # Aggiungere una carta a un mazzo
        deck_card = DeckCard(deck_id=new_deck.id, card_id=new_card.id, quantity=2)
        session.add(deck_card)
        session.commit()

    Modelli:

        - `Card`: Definisce una carta di Hearthstone.
            Attributi principali:
            - id (int): Identificativo univoco della carta.
            - name (str): Nome della carta.
            - class_name (str): Classe della carta.
            - mana_cost (int): Costo in mana.
            - card_type (str): Tipo di carta (Creatura, Magia, ecc.).
            - card_subtype (str): Sottotipo della carta (es. Drago).
            - attack (int): Attacco (opzionale, per Creature).
            - health (int): Salute (opzionale, per Creature).
            - durability (int): Integrità (opzionale, per Armi).
            - rarity (str): Rarità della carta (Comune, Rara, ecc.).
            - expansion (str): Espansione di appartenenza.

        - `Deck`: Definisce un mazzo di Hearthstone.
            Attributi principali:
            - id (int): Identificativo univoco del mazzo.
            - name (str): Nome del mazzo.
            - player_class (str): Classe del giocatore (Mage, Warrior, ecc.).
            - game_format (str): Formato del mazzo (Standard, Wild).

        - `DeckCard`: Gestisce la relazione tra carte e mazzi.
            Attributi principali:
            - deck_id (int): Identificativo del mazzo.
            - card_id (int): Identificativo della carta.
            - quantity (int): Quantità di copie della carta nel mazzo.

    Funzioni:
        - `setup_database`: Crea il database e le tabelle necessarie se non esistono già.

    Dipendenze:
        - sqlalchemy: Per la gestione del database e dei modelli.

    Note:
        Il database viene configurato automaticamente all'importazione del modulo. Per modificare il percorso del database, aggiornare la costante `DATABASE_PATH`.

---

    models.py

    Modulo per la gestione dei mazzi di Hearthstone e delle operazioni correlate.

    Path:
        scr/models.py   

    Descrizione:
 
        Questo modulo contiene la classe DeckManager e funzioni utili per gestire:

            - Caricamento/salvataggio dei mazzi da/in file JSON
            - Parsing delle carte dai mazzi con verifica di validità
            - Sincronizzazione delle carte con il database
            - Calcolo delle statistiche e delle proprietà del mazzo
            - Manipolazione delle informazioni relative ai mazzi (aggiunta, eliminazione)

    Utilizzo:
        from models import DeckManager
        from db import session

        deck_manager = DeckManager()
        deck_manager.add_deck_from_clipboard()

    Classi:
        - DeckManager: Classe principale per la gestione dei mazzi.

    Funzioni:
        - parse_deck_metadata(deck_string): Estrae metadati (nome, classe, formato) dalla stringa del mazzo.
        - parse_cards_from_deck(deck_string): Estrae le carte da una stringa di mazzo utilizzando regex.

    Esempio di utilizzo:
        deck_manager = DeckManager()
        deck_manager.add_deck_from_clipboard()

    Note:
        Questo modulo utilizza il modulo `db` per l'interazione con il database SQLite.
        Le funzioni di parsing utilizzano regex per estrarre le informazioni dai mazzi.

---

    views.py

    Modulo per le finestre di dialogo dell'interfaccia utente.

    path:
        scr/views.py

    Descrizione:
        Contiene le classi per:
        - DeckStatsDialog: Visualizza le statistiche di un mazzo
        - FilterDialog: Gestisce i filtri di ricerca
        - CardCollectionDialog: Mostra la collezione di carte

    Utilizzo:
        Importare le classi necessarie e utilizzarle nell'interfaccia principale.

---

    app.py

    Modulo principale dell'applicazione Hearthstone Deck Manager.

    Path:
        scr/app.py

    Componenti:

    - HearthstoneAppDialog (Finestra principale):
        - Gestisce l'interfaccia utente principale tramite wxPython.
        - Visualizza l'elenco dei mazzi in un controllo (wx.ListCtrl) con colonne per nome, classe e formato.
        - Include una barra di ricerca per filtrare i mazzi.
        - Presenta vari pulsanti per operazioni quali aggiunta, copia, visualizzazione, aggiornamento, eliminazione dei mazzi, visualizzazione della collezione carte e uscita dall'applicazione.
        - Gestisce una barra di stato per mostrare messaggi informativi.
        
    - AppController (Controller):
        - Coordina le operazioni tra l'interfaccia utente e il gestore dei mazzi (DeckManager).
        - Gestisce eventi dell'interfaccia quali l'aggiunta di un mazzo (importandolo dagli appunti), la cancellazione di un mazzo e il recupero delle statistiche del mazzo.

    Descrizione:

        Questo modulo rappresenta il cuore dell'applicazione, coordinando l'interazione tra l'interfaccia grafica, il database e la logica di gestione dei mazzi.
        Le funzionalità principali includono:

          - Visualizzazione e aggiornamento dell'elenco dei mazzi.
          - Gestione degli eventi dell'utente per l'aggiunta (tramite contenuti copiati negli appunti), la copia (formattazione e copia negli appunti), la visualizzazione dettagliata, l'aggiornamento e l'eliminazione dei mazzi.
          - Calcolo e visualizzazione delle statistiche dei mazzi (attraverso l'integrazione con il DeckManager e l'utilizzo di dialoghi specifici come DeckStatsDialog).
          - Accesso alla collezione delle carte tramite CardCollectionDialog.
          
    Dipendenze:
        - wxPython: per l'interfaccia grafica.
        - pyperclip: per l'interazione con gli appunti.
        - logging: per la gestione e il tracciamento degli errori.
        - SQLAlchemy (attraverso scr.db): per la gestione del database contenente i mazzi e le carte.
        - Moduli interni (scr.models, scr.views, utyls.enu_glob, utyls.logger): per la gestione dei mazzi, dei dialoghi e per il logging personalizzato.

    Utilizzo:
        L'applicazione viene avviata creando un'istanza di wx.App, istanziando HearthstoneAppDialog e avviando il MainLoop di wxPython.

    Note:
        - Il modulo sfrutta il pattern MVC in maniera semplificata, con HearthstoneAppDialog che rappresenta la vista e AppController che gestisce la logica applicativa.
        - La gestione dei mazzi si avvale di DbManager, il quale si occupa anche di importare mazzi dagli appunti, effettuare parsing dei dati e interfacciarsi con il database.
        - La classe AppController si occupa di coordinare le operazioni tra l'interfaccia utente e il DbManager, gestendo eventi e operazioni CRUD sui mazzi.

"""

# lib
import wx
from scr.app import HearthstoneAppDialog



if __name__ == "__main__":
    app = wx.App(False)
    frame = HearthstoneAppDialog(None, title="Hearthstone Deck Manager", size=(650, 700))
    frame.Show()
    app.MainLoop()
