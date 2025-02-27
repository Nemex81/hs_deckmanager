"""
    controller.py

    Modulo principale per la gestione dell'applicazione Hearthstone Deck Manager.

    Path:
        scr/controller.py

    Descrizione:
                Questo modulo rappresenta il cuore dell'applicazione, coordinando l'interazione tra le interfacce grafiche, il database e la logica di gestione.
                La classe HearthstoneManager si occupa di inizializzare l'applicazione, creare le finestre principali e gestire le operazioni di visualizzazione e modifica dei mazzi e delle carte.
                L'applicazione segue il pattern MVC, con la classe HearthstoneManager che funge da controller, le finestre come viste e il database come modello.

"""

# lib
import wx
import pyperclip
from sqlalchemy.exc import SQLAlchemyError
from .models import load_cards, db_session, Deck
from .views.main_views import HearthstoneAppFrame
from .views.collection_view import CardCollectionFrame
from .views.deck_view import DeckViewFrame
from .views.decks_view import DecksManagerFrame
from utyls import enu_glob as eg
from utyls import helper as hp
from utyls import logger as log
#import pdb



class CollectionController:
    """Controller per la vista della collezione di carte."""

    def __init__(self, parent=None, db_manager=None):
        self.parent = parent            # Riferimento al controller principale
        self.db_manager = db_manager    # Istanza di DbManager


    def load_collection(self, filters=None, card_list=None):
        """
        Carica la collezione di carte dal database, applicando eventuali filtri.

        Args:
            filters (dict, optional): Dizionario di filtri da applicare. Default è None.

        """

        try:
            # carica le carte della collezione dal db
            cards = self.db_manager.get_cards(filters=filters)

            # Aggiorna la lista delle carte nella vista
            card_list.cards = cards

            # Forza il ridisegno della lista
            card_list.Refresh()

        except Exception as e:
            log.error(f"Errore durante il caricamento della collezione: {str(e)}")
            return []

    def add_card(self, card_data):
        """
        Aggiunge una nuova carta alla collezione.

        Args:
            card_data (dict): Dati della carta da aggiungere.

        Returns:
            bool: True se l'operazione è riuscita, False altrimenti.
        """
        try:
            # Verifica se la carta esiste già nel database
            if self.db_manager.get_card_by_name(card_data["name"]):
                log.warning(f"Carta '{card_data['name']}' già esistente.")
                return False

            # Aggiunge la carta al database utilizzando DbManager
            self.db_manager.add_card_to_database(card_data)
            log.info(f"Carta '{card_data['name']}' aggiunta con successo.")
            return True
        except Exception as e:
            log.error(f"Errore durante l'aggiunta della carta: {str(e)}")
            return False

    def edit_card(self, card_name, new_data):
        """
        Modifica una carta esistente nella collezione.

        Args:
            card_name (str): Nome della carta da modificare.
            new_data (dict): Nuovi dati della carta.

        Returns:
            bool: True se l'operazione è riuscita, False altrimenti.
        """
        try:
            # Recupera la carta dal database
            card = self.db_manager.get_card_by_name(card_name)
            if not card:
                log.warning(f"Carta '{card_name}' non trovata.")
                return False

            # Aggiorna i dati della carta
            updated_card = {**card, **new_data}  # Unisce i dati esistenti con i nuovi dati
            self.db_manager.add_card_to_database(updated_card)  # Sovrascrive la carta esistente
            log.info(f"Carta '{card_name}' modificata con successo.")
            return True
        except Exception as e:
            log.error(f"Errore durante la modifica della carta: {str(e)}")
            return False

    def delete_card(self, card_name):
        """
        Rimuove una carta dalla collezione.

        Args:
            card_name (str): Nome della carta da rimuovere.

        Returns:
            bool: True se l'operazione è riuscita, False altrimenti.
        """
        try:
            # Verifica se la carta esiste nel database
            card = self.db_manager.get_card_by_name(card_name)
            if not card:
                log.warning(f"Carta '{card_name}' non trovata.")
                return False

            # Elimina la carta utilizzando DbManager
            self.db_manager.delete_card(card_name)
            log.info(f"Carta '{card_name}' rimossa con successo.")
            return True
        except Exception as e:
            log.error(f"Errore durante la rimozione della carta: {str(e)}")
            return False



class DeckController:
    """ Controller per la vista di un mazzo. """

    def __init__(self, parent=None, db_manager=None):
        self.parent= parent
        self.db_manager = db_manager



class DecksController:
    """ Controller per la vista dei mazzi. """

    def __init__(self, parent=None, db_manager=None):
        self.parent= parent
        self.db_manager = db_manager


    def run_deck_frame(self, parent=None, deck_name=None):
        """ carica l'interfaccia per la gestione di un mazzo. """

        frame = DeckViewFrame(parent, controller=self, deck_name=deck_name)
        frame.Show()
        parent.Hide()


    def load_decks(self, deck_list=None):
        """ carica i mazzi dal database. """

        if not self.db_manager.load_decks(deck_list=deck_list):
            log.warning("Nessun mazzo trovato.")
            return False

        return True


    def get_selected_deck(self):
        """Restituisce il mazzo selezionato nella lista."""
        selection = self.deck_list.GetFirstSelected()
        if selection != wx.NOT_FOUND:
            return self.deck_list.GetItemText(selection)
        return None


    def get_total_cards_in_deck(self, deck_name):
        """Calcola il numero totale di carte in un mazzo."""

        try:
            with db_session() as session:
                deck = self.db_manager.get_deck(deck_name)
                if deck:
                    #total_cards = session.query(DeckCard).filter_by(deck_id=deck.id).count()
                    total_cards = sum(card["quantity"] for card in deck["cards"])
                    return total_cards
                else:
                    return 0
        except Exception as e:
            log.error(f"Errore durante il calcolo delle carte totali per il mazzo {deck_name}: {e}")
            return 0


    def update_deck_list(self, deck_list=None):
        """Aggiorna la lista dei mazzi."""

        deck_list.DeleteAllItems()  # Pulisce la lista
        with db_session() as session:  # Usa il contesto db_session
            decks = session.query(Deck).all()
            for deck in decks:
                index = deck_list.InsertItem(self.deck_list.GetItemCount(), deck.name)  # Prima colonna
                deck_list.SetItem(index, 1, deck.player_class)  # Seconda colonna
                deck_list.SetItem(index, 2, deck.game_format)  # Terza colonna
                
                # Calcola e visualizza il numero totale di carte
                total_cards = self.get_total_cards_in_deck(deck.name)
                deck_list.SetItem(index, 3, str(total_cards))  # Aggiunge il numero totale di carte nella nuova colonna


    def select_and_focus_deck(self, deck_name):
        """
        Seleziona un mazzo nella lista e imposta il focus su di esso.
        
        :param deck_name: Il nome del mazzo da selezionare.
        """

        if not deck_name:
            return

        log.info(f"Tentativo di selezione e focus sul mazzo: {deck_name}")
        # Trova l'indice del mazzo nella lista
        for i in range(self.deck_list.GetItemCount()):
            if self.deck_list.GetItemText(i) == deck_name:
                log.info(f"Mazzo trovato all'indice: {i}")
                self.deck_list.Select(i)  # Seleziona il mazzo
                self.deck_list.Focus(i)   # Imposta il focus sul mazzo
                self.deck_list.EnsureVisible(i)  # Assicurati che il mazzo sia visibile
                self.deck_list.SetFocus() # Imposta il focus sulla lista dei mazzi
                break


    def add_deck(self, event=None):
        """Aggiunge un mazzo dagli appunti con una finestra di conferma."""
 
        try:
            deck_string = pyperclip.paste()
            if not self.db_manager.is_valid_deck(deck_string):
                wx.MessageBox("Il mazzo copiato non è valido.", "Errore")
                return

            #metadata = parse_deck_metadata(deck_string)
            metadata = self.db_manager.parse_deck_metadata(deck_string)
            deck_name = metadata["name"]

            # Mostra una finestra di conferma con i dati estratti
            confirm_message = (
                f"È stato rilevato un mazzo valido negli appunti.\n\n"
                f"Nome: {deck_name}\n"
                f"Classe: {metadata['player_class']}\n"
                f"Formato: {metadata['game_format']}\n\n"
                f"Vuoi utilizzare questi dati per creare il mazzo?"
            )

            # Mostra una finestra di conferma con i dati estratti
            confirm_dialog = wx.MessageDialog(
                self,
                confirm_message,
                "Conferma Creazione Mazzo",
                wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION
            )

            # Gestione della risposta
            result = confirm_dialog.ShowModal()
            if result == wx.ID_YES:
                success = self.db_manager.add_deck_from_clipboard()
                if success:
                    self.update_deck_list()
                    #self.update_status(f"Mazzo '{deck_name}' aggiunto con successo.")
                    wx.MessageBox(f"Mazzo '{deck_name}' aggiunto con successo.", "Successo")
                    self.select_and_focus_deck(deck_name)  # Seleziona e mette a fuoco il mazzo
                    return True

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
                        success = self.db_manager.add_deck_from_clipboard()
                        if success:
                            self.update_deck_list()
                            #self.update_status("Mazzo aggiunto con successo.")
                            wx.MessageBox("Mazzo aggiunto con successo.", "Successo")
                            self.select_and_focus_deck(new_name)  # Seleziona e mette a fuoco il mazzo
                            return True
                    else:
                        wx.MessageBox("Il nome del mazzo non può essere vuoto.", "Errore")

            elif result == wx.ID_CANCEL:
                #self.update_status("Operazione annullata.")
                log.info("Operazione annullata.")
                wx.MessageBox("Operazione annullata.", "Annullato")
                self.update_deck_list()

        except pyperclip.PyperclipException as e:
            log.error(f"Errore negli appunti: {e}")
            wx.MessageBox("Errore negli appunti. Assicurati di aver copiato un mazzo valido.", "Errore")

        except Exception as e:
            log.error(f"Errore durante l'aggiunta del mazzo: {e}")
            wx.MessageBox("Si è verificato un errore imprevisto.", "Errore")


    def delete_deck(self, deck_name):
        """ Elimina un mazzo dal database. """

        try:
            with db_session() as session:  # Usa il contesto db_session
                success = self.db_manager.delete_deck(deck_name)
                if success:
                    return True

        except SQLAlchemyError as e:
            log.error("Errore del database. Verificare le procedure.")

        except Exception as e:
            log.error("Si è verificato un errore imprevisto.")


    def copy_deck(self, deck_name):
        """ Copia un mazzo negli appunti. """
        return self.db_manager.copy_deck_to_clipboard(deck_name)

    def get_deck_details(self, deck_name):
        """ Restituisce i dettagli di un mazzo. """
        return self.db_manager.get_deck_details(deck_name)

    def get_deck_statistics(self, deck_name):
        """ Restituisce le statistiche di un mazzo. """
        return self.db_manager.get_deck_statistics(deck_name)



class MainController():
    """ gestore dell'applicazione. """

    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.collection_controller = CollectionController(parent=self, db_manager=db_manager)
        self.decks_controller = DecksController(parent=self, db_manager=db_manager)
        self.deck_controller = DeckController(parent=self, db_manager=db_manager)


    def run_decks_frame(self, parent=None):
        """ carica l'interfaccia per la gestione dei mazzi. """

        frame = DecksManagerFrame(parent, controller=self)
        frame.Show()
        parent.Hide()


    def run_collection_frame(self, parent=None):
        """ carica l'interfaccia pe rla collezzione completa di carte. """

        frame = CardCollectionFrame(parent=parent)#, controller=self)
        frame.Show()
        parent.Hide()


    def run(self):
        """ avvia l'applicazione. """

        app = wx.App(False)
        frame = HearthstoneAppFrame(parent=None, controller=self)
        frame.Show()
        app.MainLoop()


    def load_decks(self):
        """ carica i mazzi dal database. """

        return self.db_manager.get_decks()




#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
