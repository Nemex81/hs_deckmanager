"""

    Progetto di gestione e salvataggio mazzi per Hearthstone

    Autore: Nemex81
    E-mail: nemex1981@gmail.com
    nome del progetto: Hearthstone Deck Manager
    Versione: 0.9

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
from scr.models import DbManager
from scr.controller import MainController



def start_app():
    """ Start dell'applicazione Hearthstone Deck Manager. """

    db_manager = DbManager()
    app = MainController(db_manager=db_manager)
    if app:
        app.run()



if __name__ == "__main__":
    start_app()
