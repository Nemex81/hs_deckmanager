---

# **Hearthstone Deck Manager**

## **Descrizione del Progetto**
Hearthstone Deck Manager è un'applicazione desktop per la gestione di mazzi di carte del gioco **Hearthstone** di Blizzard. L'applicazione permette di:

    - Creare, salvare, modificare ed eliminare mazzi di carte.
    - Importare mazzi direttamente dagli appunti di sistema.
    - Visualizzare e filtrare la collezione di carte.
    - Calcolare statistiche dettagliate sui mazzi.
    - Gestire un database SQLite per memorizzare mazzi e carte.

L'applicazione è sviluppata in Python e utilizza le seguenti librerie:

    - **wxPython**: Per l'interfaccia grafica.
    - **SQLAlchemy**: Per la gestione del database SQLite.
    - **pyperclip**: Per interagire con gli appunti di sistema.

---

## **Funzionalità Principali**

    ### **Gestione dei Mazzi**
        - **Aggiunta di Mazzi**: Importa mazzi dagli appunti di sistema. L'applicazione verifica la validità del mazzo e lo salva nel database.
        - **Visualizzazione dei Mazzi**: Mostra l'elenco dei mazzi salvati, con dettagli come nome, classe e formato.
        - **Modifica dei Mazzi**: Aggiorna i mazzi esistenti con nuovi contenuti copiati dagli appunti.
        - **Eliminazione dei Mazzi**: Rimuove mazzi dal database.
        - **Copia dei Mazzi**: Copia il contenuto di un mazzo negli appunti, pronto per essere importato in Hearthstone.

### **Gestione delle Carte**
    - **Collezione di Carte**: Visualizza tutte le carte memorizzate nel database, con filtri per nome, costo mana, tipo, rarità ed espansione.
    - **Aggiunta e Modifica di Carte**: Permette di aggiungere nuove carte o modificare quelle esistenti.
    - **Eliminazione di Carte**: Rimuove carte dalla collezione.

### **Statistiche dei Mazzi**
    - Calcola statistiche dettagliate sui mazzi, tra cui:
    - Numero di carte.
    - Distribuzione dei tipi di carte (creature, magie, armi).
    - Costo medio del mana.

---

## **Struttura del Progetto**
Il progetto è organizzato in diversi moduli:

### **1. `main.py`**
    - Punto di ingresso dell'applicazione.
    - Avvia l'interfaccia grafica e gestisce il ciclo di vita dell'applicazione.

### **2. `app.py`**
    - Contiene la logica principale dell'applicazione.
    - Gestisce l'interfaccia utente e coordina le operazioni tra i moduli `models.py` e `views.py`.

### **3. `db.py`**
    - Gestisce il database SQLite.
    - Definisce i modelli SQLAlchemy per le carte (`Card`), i mazzi (`Deck`) e le relazioni tra mazzi e carte (`DeckCard`).
    - Include una funzione per la creazione automatica del database (`setup_database`).

### **4. `models.py`**
    - Contiene la classe `DeckManager`, che gestisce la logica di business per i mazzi e le carte.
    - Include funzioni per:
    - Parsing dei mazzi dagli appunti.
    - Sincronizzazione delle carte con il database.
    - Calcolo delle statistiche dei mazzi.

### **5. `views.py`**
    - Definisce le finestre di dialogo dell'interfaccia utente:
    - **CardCollectionDialog**: Mostra la collezione di carte.
    - **FilterDialog**: Permette di filtrare le carte in base a vari criteri.
    - **DeckStatsDialog**: Visualizza le statistiche di un mazzo.
    - **CardEditDialog**: Finestra per aggiungere o modificare una carta.

### **6. `enu_glob.py`**
    - Contiene enumerazioni globali utilizzate nel progetto, come:
    - Tipi di carte (`EnuCardType`).
    - Rarità delle carte (`EnuRarity`).
    - Espansioni (`EnuExpansion`).
    - Classi degli eroi (`EnuHero`).

---

## **Installazione**
    1. Clona il repository del progetto:
    ```bash
    git clone https://github.com/tuo-repository/hearthstone-deck-manager.git
    ```
    2. Installa le dipendenze necessarie:
    ```bash
    pip install wxPython sqlalchemy pyperclip
    ```
    3. Avvia l'applicazione:
    ```bash
    python main.py
    ```

---

## **Utilizzo**

    ### **Interfaccia Principale**
        - **Barra di Ricerca**: Filtra i mazzi per nome.
        - **Lista Mazzi**: Visualizza l'elenco dei mazzi salvati.
        - **Pulsanti**:
        - **Aggiungi Mazzo**: Importa un mazzo dagli appunti.
        - **Copia Mazzo**: Copia il contenuto di un mazzo negli appunti.
        - **Visualizza Mazzo**: Mostra il contenuto di un mazzo.
        - **Statistiche Mazzo**: Visualizza le statistiche di un mazzo.
        - **Aggiorna Mazzo**: Aggiorna un mazzo con nuovi contenuti dagli appunti.
        - **Elimina Mazzo**: Rimuove un mazzo dal database.
        - **Collezione Carte**: Apre la finestra per gestire la collezione di carte.
        - **Esci**: Chiude l'applicazione.

### **Collezione di Carte**
    - **Filtri Avanzati**: Filtra le carte per nome, costo mana, tipo, rarità ed espansione.
    - **Aggiungi/Modifica Carta**: Apre una finestra per aggiungere o modificare una carta.
    - **Elimina Carta**: Rimuove una carta dalla collezione.

---

## **Esempi di Utilizzo**

    ### **Aggiungere un Mazzo**
        1. Copia il codice di un mazzo da Hearthstone.
        2. Nell'applicazione, clicca su **Aggiungi Mazzo**.
        3. Il mazzo verrà importato e salvato nel database.

### **Modificare una Carta**
    1. Apri la **Collezione Carte**.
    2. Seleziona una carta e clicca su **Modifica**.
    3. Modifica i dettagli della carta e clicca su **Salva**.

### **Visualizzare le Statistiche di un Mazzo**
    1. Seleziona un mazzo dalla lista.
    2. Clicca su **Statistiche Mazzo**.
    3. Verranno mostrate le statistiche dettagliate del mazzo.

---

## **Dipendenze**
    - **wxPython**: Per l'interfaccia grafica.
    - **SQLAlchemy**: Per la gestione del database.
    - **pyperclip**: Per interagire con gli appunti di sistema.

---

## **Autore**
    - **Nome**: Luca Profita (Nemex81)
    - **Email**: nemex1981@gmail.com
    - **Versione**: 0.9.2

---

## **Licenza**
Il progetto è rilasciato sotto licenza MIT. Per ulteriori dettagli, consulta il file `LICENSE`.

---

## **Contributi**
    Se desideri contribuire al progetto, segui questi passaggi:
        1. Forka il repository.
        2. Crea un nuovo branch per la tua feature (`git checkout -b feature/nuova-feature`).
        3. Fai commit delle tue modifiche (`git commit -m 'Aggiunta nuova feature'`).
        4. Pusha il branch (`git push origin feature/nuova-feature`).
        5. Apri una Pull Request.

---

## **Note**
    - Il progetto è in fase di sviluppo e potrebbe contenere bug o funzionalità incomplete.
    - Per segnalare problemi o suggerire miglioramenti, apri una issue su GitHub.

---