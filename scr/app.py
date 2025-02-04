"""
    app.py

    Modulo principale dell'applicazione Hearthstone Deck Manager.

    Path:
        scr/app.py

    Componenti:

    - HearthstoneApp (Finestra principale):
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
            - Gestione della barra di stato per mostrare messaggi informativi all'utente.

     Note:
        - Il modulo sfrutta il pattern MVC in maniera semplificata, con HearthstoneApp che rappresenta la vista e AppController che gestisce la logica applicativa.
        - La gestione dei mazzi si avvale di DeckManager, il quale si occupa anche di importare mazzi dagli appunti, effettuare parsing dei dati e interfacciarsi con il database.
        - La classe AppController si occupa di coordinare le operazioni tra l'interfaccia utente e il DeckManager, gestendo eventi e operazioni CRUD sui mazzi.

"""

# lib
import wx
import logging
import pyperclip
from scr.db import session, Deck, DeckCard, Card
from sqlalchemy.exc import SQLAlchemyError
from scr.models import Deck
from scr.models import DeckManager, parse_deck_metadata
from scr.views import CardCollectionDialog, DeckStatsDialog
from scr.db import session
from utyls import enu_glob as eg
from utyls import logger as log
#import pdb



class AppController:
    """ Controller per la gestione delle operazioni dell'applicazione. """

    def __init__(self, deck_manager, app):
        self.deck_manager = deck_manager
        self.app = app

    def add_deck(self, deck_name):
        try:
            self.deck_manager.add_deck_from_clipboard(deck_name)
            self.app.update_deck_list()
            self.app.update_status(f"Mazzo '{deck_name}' aggiunto con successo.")
            wx.MessageBox(f"Mazzo '{deck_name}' aggiunto con successo.", "Successo")
        except ValueError as e:
            wx.MessageBox(str(e), "Errore")
        except Exception as e:
            logging.error(f"Errore durante l'aggiunta del mazzo: {e}")
            wx.MessageBox(f"Si è verificato un errore: {e}", "Errore")

    def delete_deck(self, deck_name):
        try:
            if self.deck_manager.delete_deck(deck_name):
                self.app.update_deck_list()
                self.app.update_status(f"Mazzo '{deck_name}' eliminato con successo.")
                log.info(f"Mazzo '{deck_name}' eliminato con successo.")
                return True

        except SQLAlchemyError as e:
            wx.MessageBox("Errore del database. Verificare le procedure.", "Errore")

        except Exception as e:
            wx.MessageBox(f"Si è verificato un errore: {e}", "Errore")

    def get_deck_statistics(self, deck_name):
        """Restituisce le statistiche del mazzo."""
        return self.deck_manager.get_deck_statistics(deck_name)



class HearthstoneApp(wx.Frame):
    """ Finestra principale dell'applicazione. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.deck_manager = DeckManager()
        self.controller = AppController(self.deck_manager, self)
        self.init_ui()


    def init_ui(self):
        """ Inizializza l'interfaccia utente. """

        # Impostazioni finestra principale
        self.SetBackgroundColour('green')
        self.panel = wx.Panel(self)

        # Layout principale
        self.Centre()
        lbl_title = wx.StaticText(self.panel, label="Elenco Mazzi")
        #self.deck_list = wx.ListBox(self.panel)
        self.deck_list = wx.ListCtrl(
            self.panel,
            #style=wx.LC_REPORT | wx.BORDER_SUNKEN
            style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.BORDER_SUNKEN
        )

        # aggiungiamo le righe e le colonne
        self.deck_list.InsertColumn(0, "mazzo", width=260)
        self.deck_list.InsertColumn(1, "Classe ", width=200)
        self.deck_list.InsertColumn(2, "Formato ", width=120)

        # carichiamo i mazzi
        self.load_decks()

        # Barra di ricerca
        self.search_bar = wx.SearchCtrl(self.panel)
        self.search_bar.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.on_search)

        # Pulsanti
        btn_add = wx.Button(self.panel, label="Aggiungi Mazzo")
        btn_copy = wx.Button(self.panel, label="Copia Mazzo")
        btn_view = wx.Button(self.panel, label="Visualizza Mazzo")
        btn_stats = wx.Button(self.panel, label="Statistiche Mazzo")
        btn_update = wx.Button(self.panel, label="Aggiorna Mazzo")
        btn_delete = wx.Button(self.panel, label="Elimina Mazzo")
        btn_collection = wx.Button(self.panel, label="Collezione Carte")
        btn_exit = wx.Button(self.panel, label="Esci")

        # Layout principale
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(lbl_title, flag=wx.CENTER | wx.TOP, border=10)
        sizer.Add(self.search_bar, flag=wx.EXPAND | wx.ALL, border=5)

        # Separatore tra barra di ricerca e lista dei mazzi
        sizer.Add(wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)
        sizer.Add(self.deck_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Separatore tra lista dei mazzi e pulsanti
        sizer.Add(wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        # Layout pulsanti
        btn_sizer = wx.GridSizer(rows=4, cols=2, hgap=10, vgap=10)
        btn_sizer.Add(btn_add, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_copy, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_view, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_stats, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_update, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_delete, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_collection, flag=wx.EXPAND | wx.ALL, border=5)
        btn_sizer.Add(btn_exit, flag=wx.EXPAND | wx.ALL, border=5)
        sizer.Add(btn_sizer, flag=wx.EXPAND | wx.ALL, border=10)

        # Separatore tra pulsanti e barra di stato
        sizer.Add(wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        self.panel.SetSizer(sizer)

        # Barra di stato
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("Pronto")

        # Eventi
        btn_add.Bind(wx.EVT_BUTTON, self.on_add_deck)
        btn_copy.Bind(wx.EVT_BUTTON, self.on_copy_deck)
        btn_view.Bind(wx.EVT_BUTTON, self.on_view_deck)
        btn_update.Bind(wx.EVT_BUTTON, self.on_update_deck)
        btn_stats.Bind(wx.EVT_BUTTON, self.on_view_stats)
        btn_collection.Bind(wx.EVT_BUTTON, self.on_view_collection)
        btn_delete.Bind(wx.EVT_BUTTON, self.on_delete_deck)
        btn_exit.Bind(wx.EVT_BUTTON, self.on_exit)


    def load_decks(self):
        """Carica i mazzi ."""

        # svuotiamo la
        #self.deck_list.DeleteAllItems()

        # carichiamo i mazzi
        decks = session.query(Deck).all()
        # utilizzando insert
        for deck in decks:
            Index = self.deck_list.InsertItem(self.deck_list.GetItemCount(), deck.name)
            self.deck_list.SetItem(Index, 1, deck.player_class)
            self.deck_list.SetItem(Index, 2, deck.game_format)


    def update_deck_list(self):
        """Aggiorna la lista dei mazzi."""

        self.deck_list.DeleteAllItems()  # Pulisce la lista

        decks = session.query(Deck).all()
        for deck in decks:
            index = self.deck_list.InsertItem(self.deck_list.GetItemCount(), deck.name)  # Prima colonna
            self.deck_list.SetItem(index, 1, deck.player_class)  # Seconda colonna
            self.deck_list.SetItem(index, 2, deck.game_format)  # Terza colonna


    def select_and_focus_deck(self, deck_name):
        """
        Seleziona un mazzo nella lista e imposta il focus su di esso.
        
        :param deck_name: Il nome del mazzo da selezionare.
        """
        if not deck_name:
            return

        # Trova l'indice del mazzo nella lista
        for i in range(self.deck_list.GetItemCount()):
            if self.deck_list.GetItemText(i) == deck_name:
                self.deck_list.Select(i)  # Seleziona il mazzo
                self.deck_list.Focus(i)   # Imposta il focus sul mazzo
                self.deck_list.EnsureVisible(i)  # Assicurati che il mazzo sia visibile
                break

            self.deck_list.SetFocus() # Imposta il focus sulla lista dei mazzi


    def update_status(self, message):
        """Aggiorna la barra di stato."""
        self.status_bar.SetStatusText(message)


    def get_selected_deck(self):
        """Restituisce il mazzo selezionato nella lista."""

        selection = self.deck_list.GetFirstSelected()
        if selection != wx.NOT_FOUND:
            return self.deck_list.GetItemText(selection)
        return None


    def on_add_deck(self, event):
        """Aggiunge un mazzo dagli appunti con una finestra di conferma."""
        try:
            deck_string = pyperclip.paste()
            if not self.deck_manager.is_valid_deck(deck_string):
                wx.MessageBox("Il mazzo copiato non è valido.", "Errore")
                return

            metadata = parse_deck_metadata(deck_string)
            deck_name = metadata["name"]

            # Mostra una finestra di conferma con i dati estratti
            confirm_message = (
                f"È stato rilevato un mazzo valido negli appunti.\n\n"
                f"Nome: {deck_name}\n"
                f"Classe: {metadata['player_class']}\n"
                f"Formato: {metadata['game_format']}\n\n"
                f"Vuoi utilizzare questi dati per creare il mazzo?"
            )

            confirm_dialog = wx.MessageDialog(
                self,
                confirm_message,
                "Conferma Creazione Mazzo",
                wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION
            )

            result = confirm_dialog.ShowModal()
            if result == wx.ID_YES:
                success = self.deck_manager.add_deck_from_clipboard()
                if success:
                    self.update_deck_list()
                    self.update_status(f"Mazzo '{deck_name}' aggiunto con successo.")
                    wx.MessageBox(f"Mazzo '{deck_name}' aggiunto con successo.", "Successo")
                    self.select_and_focus_deck(deck_name)  # Seleziona e mette a fuoco il mazzo
            elif result == wx.ID_NO:
                name_dialog = wx.TextEntryDialog(
                    self,
                    "Inserisci il nome per il nuovo mazzo:",
                    "Nome del Mazzo",
                    deck_name
                )

                if name_dialog.ShowModal() == wx.ID_OK:
                    new_name = name_dialog.GetValue()
                    if new_name:
                        metadata["name"] = new_name
                        success = self.deck_manager.add_deck_from_clipboard()
                        if success:
                            self.update_deck_list()
                            self.update_status("Mazzo aggiunto con successo.")
                            wx.MessageBox("Mazzo aggiunto con successo.", "Successo")
                            self.select_and_focus_deck(new_name)  # Seleziona e mette a fuoco il mazzo
                    else:
                        wx.MessageBox("Il nome del mazzo non può essere vuoto.", "Errore")
            elif result == wx.ID_CANCEL:
                self.update_status("Operazione annullata.")
                wx.MessageBox("Operazione annullata.", "Annullato")

        except pyperclip.PyperclipException as e:
            wx.MessageBox("Errore negli appunti. Assicurati di aver copiato un mazzo valido.", "Errore")
        except Exception as e:
            log.error(f"Errore durante l'aggiunta del mazzo: {e}")
            wx.MessageBox("Si è verificato un errore imprevisto.", "Errore")


    def on_copy_deck(self, event):
        """Copia il mazzo selezionato negli appunti."""

        deck_name = self.get_selected_deck()
        if deck_name:
            deck_content = self.deck_manager.get_deck(deck_name)
            if deck_content:
                # Formatta il contenuto del mazzo in una stringa compatibile con Hearthstone
                deck_info = f"### {deck_content['name']}\n"
                deck_info += f"# Classe: {deck_content['player_class']}\n"
                deck_info += f"# Formato: {deck_content['game_format']}\n"
                deck_info += "# Anno del Pegaso\n"
                deck_info += "#\n"
                
                for card in deck_content["cards"]:
                    deck_info += f"# {card['quantity']}x ({card['mana_cost']}) {card['name']}\n"

                deck_info += "#\n"
                deck_info += "AAECAeSKBwaU1ATj+AXpngbSsAb3wAbO8QYMg58E0p8E7KAEx7AG7eoGn/EGwvEG3vEG4/EG5fEGqPcGiPgGAAA=\n#\n# Per utilizzare questo mazzo, copialo negli appunti e crea un nuovo mazzo in Hearthstone\n"

                pyperclip.copy(deck_info)
                self.update_status(f"Mazzo '{deck_name}' copiato negli appunti.")
                wx.MessageBox(f"Mazzo '{deck_name}' copiato negli appunti.", "Successo")
                self.select_and_focus_deck(deck_name)  # Seleziona e mette a fuoco il mazzo
            else:
                wx.MessageBox("Errore: Mazzo vuoto o non trovato.", "Errore")
        else:
            wx.MessageBox("Seleziona un mazzo prima di copiarlo negli appunti.", "Errore")


    def on_view_deck(self, event):
        """Mostra il mazzo selezionato."""

        deck_name = self.get_selected_deck()
        if deck_name:
            deck_content = self.deck_manager.get_deck(deck_name)
            if deck_content:
                # Formatta il contenuto del mazzo in una stringa leggibile
                deck_info = f"Mazzo: {deck_content['name']}\n"
                deck_info += f"Classe: {deck_content['player_class']}\n"
                deck_info += f"Formato: {deck_content['game_format']}\n\n"
                deck_info += "Carte:\n"
                for card in deck_content["cards"]:
                    deck_info += f"{card['quantity']}x {card['name']} (Mana: {card['mana_cost']})\n"
                
                # Mostra il contenuto del mazzo
                wx.MessageBox(deck_info, f"Mazzo: {deck_name}")
            else:
                wx.MessageBox("Errore: Mazzo vuoto o non trovato.", "Errore")
        else:
            wx.MessageBox("Seleziona un mazzo prima di visualizzarlo.", "Errore")


    def on_update_deck(self, event):
        """Aggiorna il mazzo selezionato con il contenuto degli appunti."""
        deck_name = self.get_selected_deck()
        if deck_name:
            if wx.MessageBox(
                f"Sei sicuro di voler aggiornare '{deck_name}' con il contenuto degli appunti?",
                "Conferma",
                wx.YES_NO
            ) == wx.YES:
                try:
                    deck_string = pyperclip.paste()
                    if self.deck_manager.is_valid_deck(deck_string):
                        deck = session.query(Deck).filter_by(name=deck_name).first()
                        if deck:
                            session.query(DeckCard).filter_by(deck_id=deck.id).delete()
                            session.commit()

                            self.deck_manager.sync_cards_with_database(deck_string)

                            cards = self.deck_manager.parse_cards_from_deck(deck_string)
                            for card_data in cards:
                                card = session.query(Card).filter_by(name=card_data["name"]).first()
                                if not card:
                                    card = Card(
                                        name=card_data["name"],
                                        class_name="Unknown",
                                        mana_cost=card_data["mana_cost"],
                                        card_type="Unknown",
                                        card_subtype="Unknown",
                                        rarity="Unknown",
                                        expansion="Unknown"
                                    )
                                    session.add(card)
                                    session.commit()

                                deck_card = DeckCard(deck_id=deck.id, card_id=card.id, quantity=card_data["quantity"])
                                session.add(deck_card)
                                session.commit()

                            self.update_deck_list()
                            self.update_status(f"Mazzo '{deck_name}' aggiornato con successo.")
                            wx.MessageBox(f"Mazzo '{deck_name}' aggiornato con successo.", "Successo")
                            self.select_and_focus_deck(deck_name)  # Seleziona e mette a fuoco il mazzo
                        else:
                            wx.MessageBox("Errore: Mazzo non trovato nel database.", "Errore")
                    else:
                        wx.MessageBox("Il mazzo negli appunti non è valido.", "Errore")
                except Exception as e:
                    logging.error(f"Errore durante l'aggiornamento del mazzo: {e}")
                    wx.MessageBox(f"Si è verificato un errore: {e}", "Errore")
        else:
            wx.MessageBox("Seleziona un mazzo prima di aggiornarlo.", "Errore")


    def on_view_stats(self, event):
        """Mostra le statistiche del mazzo selezionato."""

        deck_name = self.get_selected_deck()
        if deck_name:
            stats = self.controller.get_deck_statistics(deck_name)
            if stats:
                DeckStatsDialog(self, stats).ShowModal()  # Mostra la finestra come modale
            else:
                wx.MessageBox("Impossibile calcolare le statistiche per questo mazzo.", "Errore")
        else:
            wx.MessageBox("Seleziona un mazzo prima di visualizzare le statistiche.", "Errore")

    def on_view_collection(self, event):
        """Mostra la collezione delle carte."""

        collection_dialog = CardCollectionDialog(self, self.deck_manager)
        collection_dialog.ShowModal()  # Mostra la finestra come modale

    def on_delete_deck(self, event):
        """Elimina il mazzo selezionato."""

        deck_name = self.get_selected_deck()
        if deck_name:
            if wx.MessageBox(f"Sei sicuro di voler eliminare '{deck_name}'?", "Conferma", wx.YES_NO) == wx.YES:
                try:
                    #success = self.deck_manager.delete_deck(deck_name)
                    success = self.controller.delete_deck(deck_name)
                    if success:
                        self.update_deck_list()
                        self.update_status(f"Mazzo '{deck_name}' eliminato con successo.")
                        wx.MessageBox(f"Mazzo '{deck_name}' eliminato con successo.", "Successo")
                    else:
                        wx.MessageBox(f"Mazzo '{deck_name}' non trovato.", "Errore")

                except SQLAlchemyError as e:
                    wx.MessageBox("Errore del database. Verificare le procedure.", "Errore")

                except Exception as e:
                    wx.MessageBox("Si è verificato un errore imprevisto.", "Errore")
        else:
            wx.MessageBox("Seleziona un mazzo prima di eliminarlo.", "Errore")

    def on_search(self, event):
        """Filtra i mazzi in base al testo di ricerca."""

            # cerchiamo la parola richeista dall0utente sia nei nomi dei mazzi sia nella classe
        search_text = self.search_bar.GetValue()
        self.deck_list.DeleteAllItems()
        decks = session.query(Deck).filter(Deck.name.ilike(f"%{search_text}%") | Deck.player_class.ilike(f"%{search_text}%")).all()
        for deck in decks:
            Index = self.deck_list.InsertItem(self.deck_list.GetItemCount(), deck.name)
            self.deck_list.SetItem(Index, 1, deck.player_class)
            self.deck_list.SetItem(Index, 2, deck.game_format)


    def on_exit(self, event):
        """Chiude l'applicazione."""

        self.Close()




#@@@# Start del modulo
if __name__ != "__main__":
    print("Carico: %s." % __name__)
