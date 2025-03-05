"""

    Progetto di gestione e salvataggio mazzi per Hearthstone

    Autore: Nemex81
    E-mail: nemex1981@gmail.com
    nome del progetto: Hearthstone Deck Manager
    Versione: 0.9.2

    path:
        ./main.py

    Descrizione:

        Questo progetto implementa un'applicazione per la gestione di mazzi del gioco di carte collezionabili Hearthstone.
        Permette di creare, salvare, caricare, modificare e visualizzare mazzi di Hearthstone.
        
        Include anche una funzionalità per la gestione di una collezione di carte, con la possibilità di filtrare le carte
        per nome, costo in mana, tipo, sottotipo, rarità ed espansione.

    Note:
        - Il modulo sfrutta il pattern MVC in maniera semplificata, con HearthstoneAppDialog che rappresenta la vista e AppController che gestisce la logica applicativa.
        - La gestione dei mazzi si avvale di DbManager, il quale si occupa anche di importare mazzi dagli appunti, effettuare parsing dei dati e interfacciarsi con il database.
        - La classe AppController si occupa di coordinare le operazioni tra l'interfaccia utente e il DbManager, gestendo eventi e operazioni CRUD sui mazzi.

"""

# lib
import wx
from app_initializer import AppInitializer
from scr.hdm import AppBuilder
from utyls import logger as log
# import pdb



def last_start_app():
    """Avvia l'applicazione Hearthstone Deck Manager."""

    log.debug("Inizializzazione dell'applicazione.")

    app_builder = AppBuilder()
    app = app_builder.build_app()
    if app:
        log.debug("Avvio dell'applicazione.")
        app_builder.run_app()




def start_app(use_new_framework=False):
    """
    Avvia l'applicazione Hearthstone Deck Manager.
    
    Args:
        use_new_framework (bool): Se True, utilizza il nuovo framework per l'inizializzazione.
    """
    log.debug("Inizializzazione dell'applicazione.")

    if use_new_framework:
        # Utilizza il nuovo framework per l'inizializzazione
        app_initializer = AppInitializer(use_new_framework=True)
        app_initializer.initialize_app()
    else:
        # Utilizza l'inizializzazione tradizionale
        app_builder = AppBuilder()
        app = app_builder.build_app()
        if app:
            log.debug("Avvio dell'applicazione.")
            app_builder.run_app()




if __name__ == "__main__":
    # Decidi se utilizzare il nuovo framework o quello tradizionale
    #use_new_framework = True  # Cambia questo valore per testare il nuovo framework
    use_new_framework = False  # Cambia questo valore per testare il nuovo framework
    start_app(use_new_framework)
