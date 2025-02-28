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
    """ Controller per la view di un singoolo mazzo. """

    def __init__(self, parent=None, db_manager=None):
        self.parent= parent
        self.db_manager = db_manager


    def get_deck_details(self, deck_name):
        """ Restituisce i dettagli di un mazzo. """
        return self.db_manager.get_deck_details(deck_name)



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


    def get_selected_deck(self, frame):
        """Restituisce il mazzo selezionato nella lista."""

        selection = frame.deck_list.GetFirstSelected()
        if selection != wx.NOT_FOUND:
            return frame.deck_list.GetItemText(selection)


    def apply_search_filter(self, frame, search_text):
        """Applica il filtro di ricerca alla lista dei mazzi."""

        if not search_text or search_text in ["tutti", "tutto", "all"]:
            # Se il campo di ricerca è vuoto o contiene "tutti", mostra tutti i mazzi
            frame.load_decks()
        else:
            # Filtra i mazzi in base al nome o alla classe
            frame.deck_list.DeleteAllItems()
            with db_session() as session:
                decks = session.query(Deck).filter(Deck.name.ilike(f"%{search_text}%") | Deck.player_class.ilike(f"%{search_text}%")).all()
                for deck in decks:
                    index = frame.deck_list.InsertItem(frame.deck_list.GetItemCount(), deck.name)
                    frame.deck_list.SetItem(index, 1, deck.player_class)
                    frame.deck_list.SetItem(index, 2, deck.game_format)

        frame.set_focus_to_list()    # Imposta il focus sul primo mazzo della lista


    def set_focus_to_list(self, frame):
        """
        Imposta il focus sulla lista dei mazzi e seleziona il primo elemento.
        """
        
        if hasattr(frame, "deck_list") and frame.deck_list.GetItemCount() > 0:
            frame.deck_list.SetFocus()  # Imposta il focus sulla lista
            frame.deck_list.Select(0)   # Seleziona il primo elemento
            frame.deck_list.Focus(0)    # Sposta il focus sul primo elemento
            frame.deck_list.EnsureVisible(0)  # Assicurati che il primo elemento sia visibile


    def get_total_cards_in_deck(self, deck_name):
        """Calcola il numero totale di carte in un mazzo."""

        try:
            with db_session() as session:
                deck = self.db_manager.get_deck(deck_name)
                if deck:
                    #total_cards = session.query(DeckCard).filter_by(deck_id=deck.id).count()
                    total_cards = sum(card["quantity"] for card in deck["cards"])
                    log.info(f"Mazzo '{deck_name}' contiene {total_cards} carte.")
                    return total_cards
                else:
                    log.error(f"Mazzo '{deck_name}' non trovato.")
                    return 0

        except Exception as e:
            log.error(f"Errore durante il calcolo delle carte totali per il mazzo {deck_name}: {e}")
            return 0


    def select_last_deck(self, frame):
        """Seleziona l'ultimo mazzo nella lista."""

        deck_list = frame.deck_list
        self.update_deck_list(deck_list)
        frame.set_focus_to_list()
        end_list = deck_list.GetItemCount()
        deck_list.Select(end_list-1)
        deck_list.Focus(end_list-1)
        deck_list.EnsureVisible(end_list-1)
        deck_list.SetFocus()
        deck_list.Refresh()


    def select_list_element(self, frame=None):
        """ colora la riga del mazzo selezionato nell'elenco. """

        if not frame:
            log.error("Errore durante la selezione dell ariga. Nessun frame passato.")
            wx.MessageBox("Errore durante la selezione della riga.", "Errore")
            return

        # colora la riga selezionata
        frame.deck_list.SetBackgroundColour('blue')
        frame.deck_list.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        frame.deck_list.SetForegroundColour('white')


    def select_and_focus_deck(self, frame, deck_name):
        """
        Seleziona un mazzo nella lista e imposta il focus su di esso.
        
        Args:
            frame: L'istanza del frame dei mazzi.
            deck_name: Il nome del mazzo da selezionare.

        """

        if not deck_name:
            return

        log.info(f"Tentativo di selezione e focus sul mazzo: {deck_name}")
        # Trova l'indice del mazzo nella lista
        for i in range(frame.deck_list.GetItemCount()):
            if frame.deck_list.GetItemText(i) == deck_name:
                log.info(f"Mazzo trovato all'indice: {i}")
                frame.deck_list.Select(i)  # Seleziona il mazzo
                frame.deck_list.Focus(i)   # Imposta il focus sul mazzo
                frame.deck_list.EnsureVisible(i)  # Assicurati che il mazzo sia visibile
                frame.deck_list.SetFocus() # Imposta il focus sulla lista dei mazzi
                break


    def question_for_add_deck(self, parent=None):
        """ Chiede all'utente se vuole aggiungere un mazzo. """

        deck_string = pyperclip.paste()
        if not self.db_manager.is_valid_deck(deck_string):
            wx.MessageBox("Il mazzo copiato non è valido.", "Errore")
            return False

        # Estrae i metadati del mazzo
        metadata = self.db_manager.parse_deck_metadata(deck_string)
        deck_name = metadata["name"]

        # Verifica se il mazzo esiste già
        if self.db_manager.get_deck(deck_name):
            log.error("Il mazzo è già presente nella collezione.")
            wx.MessageBox("Il mazzo è già presente nella collezione.", "Errore")
            return False

        # Mostra una finestra di conferma con i dati estratti
        confirm_message = (
            f"È stato rilevato un mazzo valido negli appunti.\n\n"
            f"Nome: {deck_name}\n"
            f"Classe: {metadata['player_class']}\n"
            f"Formato: {metadata['game_format']}\n\n"
            f"Vuoi utilizzare questi dati per creare il mazzo?"
        )

        confirm_dialog = wx.MessageDialog(
            parent,
            confirm_message,
            "Conferma Creazione Mazzo",
            wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION
        )

        result = confirm_dialog.ShowModal()
        if result == wx.ID_YES:
            return wx.ID_YES


    def add_deck(self):
        """Aggiunge un mazzo dagli appunti."""

        try:
            deck_string = pyperclip.paste()
            if not self.db_manager.is_valid_deck(deck_string):
                wx.MessageBox("Il mazzo copiato non è valido.", "Errore")
                return False

            # Estrae i metadati del mazzo
            metadata = self.db_manager.parse_deck_metadata(deck_string)
            deck_name = metadata["name"]

            # Verifica se il mazzo esiste già
            if self.db_manager.get_deck(deck_name):
                log.error("Il mazzo è già presente nella collezione.")
                wx.MessageBox("Il mazzo è già presente nella collezione.", "Errore")
                return False

            # Aggiunge il mazzo al database
            success = self.db_manager.add_deck_from_clipboard(deck_string)
            if success:
                deck_name = metadata["name"]
                log.info(f"Mazzo '{deck_name}' aggiunto con successo.")
                wx.MessageBox(f"Mazzo {deck_name} aggiunto con successo.", "Successo")
                return True
            else:
                log.error(f"Errore durante l'aggiunta del mazzo '{deck_name}'.")
                wx.MessageBox(f"Errore durante l'aggiunta del mazzo{deck_name}.", "Errore")
                return False

        except Exception as e:
            log.error(f"Errore imprevisto durante l'aggiunta del mazzo: {e}")
            wx.MessageBox("Si è verificato un errore imprevisto.", "Errore")
            return False


    def delete_deck(self, deck_name):
        """ Elimina un mazzo dal database. """

        try:
            with db_session() as session:  # Usa il contesto db_session
                success = self.db_manager.delete_deck(deck_name)
                if success:
                    log.info(f"Mazzo '{deck_name}' eliminato con successo.")
                    wx.MessageBox(f"Mazzo '{deck_name}' eliminato con successo.", "Successo")
                    return True
                else:
                    log.error(f"Errore durante l'eliminazione del mazzo '{deck_name}'.")
                    wx.MessageBox(f"Errore durante l'eliminazione del mazzo '{deck_name}'.", "Errore")
                    return False

        except SQLAlchemyError as e:
            log.error("Errore del database. Verificare le procedure.")
            wx.MessageBox("Errore del database. Verificare le procedure.", "Errore")
            return False

        except Exception as e:
            log.error("Si è verificato un errore imprevisto.")
            wx.MessageBox("Si è verificato un errore imprevisto.", "Errore")
            return False


    def copy_deck(self, frame):
        """ Copia un mazzo negli appunti. """

        deck_name = frame.get_selected_deck()
        if deck_name:
            if self.db_manager.copy_deck_to_clipboard(deck_name):
                #self.update_status(f"Mazzo '{deck_name}' copiato negli appunti.")
                wx.MessageBox(f"Mazzo '{deck_name}' copiato negli appunti.", "Successo")
                self.select_and_focus_deck(deck_name)

            else:
                wx.MessageBox("Errore: Mazzo vuoto o non trovato.", "Errore")

        else:
            wx.MessageBox("Seleziona un mazzo prima di copiarlo negli appunti.", "Errore")


    def get_deck_details(self, deck_name):
        """ Restituisce i dettagli di un mazzo. """
        return self.db_manager.get_deck_details(deck_name)


    def get_deck_statistics(self, deck_name):
        """ Restituisce le statistiche di un mazzo. """
        return self.db_manager.get_deck_statistics(deck_name)


    def update_deck_list(self, deck_list =None):
        """Aggiorna la lista dei mazzi."""

        #deck_list = frame.deck_list
        deck_list.DeleteAllItems()  # Pulisce la lista
        with db_session() as session:  # Usa il contesto db_session
            decks = session.query(Deck).all()
            for deck in decks:
                index = deck_list.InsertItem(deck_list.GetItemCount(), deck.name)  # Prima colonna
                deck_list.SetItem(index, 1, deck.player_class)  # Seconda colonna
                deck_list.SetItem(index, 2, deck.game_format)  # Terza colonna
                
                # Calcola e visualizza il numero totale di carte
                total_cards = self.get_total_cards_in_deck(deck.name)
                deck_list.SetItem(index, 3, str(total_cards))  # Aggiunge il numero totale di carte nella nuova colonna


    def upgrade_deck(self, deck_name):
        """ Aggiorna un mazzo. """

        if deck_name:
            if wx.MessageBox(
                f"Sei sicuro di voler aggiornare '{deck_name}' con il contenuto degli appunti?",
                "Conferma",
                wx.YES_NO
            ) == wx.YES:
                if self.db_manager.upgrade_deck(deck_name):
                    #self.update_status(f"Mazzo '{deck_name}' aggiornato con successo.")
                    wx.MessageBox(f"Mazzo '{deck_name}' aggiornato con successo.", "Successo")
                    return True

                else:
                    wx.MessageBox("Errore durante l'aggiornamento del mazzo.", "Errore")
                    return False

        else:
            wx.MessageBox("Seleziona un mazzo prima di aggiornarlo.", "Errore")
            return False





class MainController():
    """ gestore dell'applicazione. """

    #def __init__(self, db_manager=None):
    def __init__(self, db_manager=None, collection_controller=None, decks_controller=None, deck_controller=None):
        self.db_manager = db_manager
        self.collection_controller = collection_controller
        self.decks_controller = decks_controller
        self.deck_controller = deck_controller


    def run(self):
        """Avvia l'applicazione."""
        app = wx.App(False)
        frame = HearthstoneAppFrame(parent=None, controller=self)
        frame.Show()
        app.MainLoop()

    def run_collection_frame(self, parent=None):
        """Carica l'interfaccia per la collezione completa di carte."""
        frame = CardCollectionFrame(parent=parent, controller=self.collection_controller)
        frame.Show()
        parent.Hide()

    def run_decks_frame(self, parent=None):
        """Carica l'interfaccia per la gestione dei mazzi."""
        frame = DecksManagerFrame(parent=parent, controller=self.decks_controller)
        frame.Show()
        parent.Hide()


    def last_run_decks_frame(self, parent=None):
        """ carica l'interfaccia per la gestione dei mazzi. """

        frame = DecksManagerFrame(parent, controller=self)
        frame.set_controller(self.decks_controller)
        frame.Show()
        parent.Hide()


    def last_run_collection_frame(self, parent=None):
        """ carica l'interfaccia pe rla collezzione completa di carte. """

        frame = CardCollectionFrame(parent=parent)#, controller=self)
        frame.Show()
        parent.Hide()


    def last_run(self):
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
