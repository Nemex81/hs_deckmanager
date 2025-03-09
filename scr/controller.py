"""
    controller.py

    Modulo principale per la gestione dell'applicazione Hearthstone Deck Manager.

    Path:
        scr/controller.py

"""

# lib
import wx
import pyperclip
from sqlalchemy.exc import SQLAlchemyError
from .models import db_session, Deck
from utyls import enu_glob as eg
from utyls import helper as hp
from utyls import logger as log
#import pdb



class DefaultController:
    """ Controller predefinito per la gestione delle finestre. """
    
    def __init__(self, container=None, **kwargs):
        self.container = container  # Memorizza il container
        self.db_manager = self.container.resolve("db_manager")
        self.vocalizer = self.container.resolve("vocalizer")  # Risolve Vocalizer
        self.win_controller = self.container.resolve("win_controller")  # Risolve WinController
        self.widget_factory = self.container.resolve("widget_factory")  # Risolve WidgetFactory


        """ Vocalizza un testo. """
    def speak(self, text):
        self.vocalizer.speak(text)


    def on_focus(self, event, frame):
        """
        Gestisce l'evento di focus su un elemento e vocalizza la descrizione.
        """

        element = event.GetEventObject()
        name = element.GetName()
        #description = element.GetName()
        if name:# and description:
            output = f"Elemento in focus: {name}."
            self.speak(output)

        event.Skip()


    def on_kill_focus(self, event):
        """
        Gestisce l'evento di perdita del focus su un elemento.
        """
        element = event.GetEventObject()
        event.Skip()


    def on_key_down(self, event, frame):
        """
        Gestisce l'evento di pressione di un tasto.
        """

        key_code = event.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
            #log.debug(f"Finestra da chiudere: {frame}")
            self.question_quit_app(frame=frame)
            event.Skip(False)  # Impedisce la propagazione al sistema operativo
            return

        elif key_code == ord("F"):
            self.read_focused_element(event=event, frame=frame)

        else:
            nome_tasto = chr(key_code)
            log.warning(f"Tasto premuto non gestito: {key_code} che corrisponde al tasto: {nome_tasto}")

        event.Skip()


    def read_focused_element(self, event, frame):
        """
        Legge il nome dell'elemento che ha attualmente il focus.
        """

        focused_element = wx.Window.FindFocus()                                # Ottieni l'elemento con il focus
        if focused_element:
            description = focused_element.GetName()                            # Recupera la descrizione
            if description:
                description += f". Tipo: {focused_element.GetClassName()}"      # Aggiungi il tipo di elemento
                self.speak(description)                                         # Vocalizza la descrizione

            else:
                self.speak("Nessuna descrizione disponibile per questo elemento.")

        event.skip()


    #@@# sezione per gestione deicomandi  generici disponibiliin ogni finestra

    def get_deck_details(self, deck_name):
        """ Restituisce i dettagli di un mazzo. """
        return self.db_manager.get_deck_details(deck_name)


    def get_deck_statistics(self, deck_name):
        """ Restituisce le statistiche di un mazzo. """
        return self.db_manager.get_deck_statistics(deck_name)

    def set_focus_to_list(self, frame):
        """
        Imposta il focus sulla lista dei mazzi e seleziona il primo elemento.
        """
        
        if hasattr(frame, "card_list") and frame.card_list.GetItemCount() > 0:
            frame.card_list.SetFocus()  # Imposta il focus sulla lista
            frame.card_list.Select(0)   # Seleziona il primo elemento
            frame.card_list.Focus(0)    # Sposta il focus sul primo elemento
            frame.card_list.EnsureVisible(0)  # Assicurati che il primo elemento sia visibile

    def select_list_element(self, frame=None):
        """ colora la riga del mazzo selezionato nell'elenco. """

        if not frame:
            log.error("Errore durante la selezione dell ariga. Nessun frame passato.")
            wx.MessageBox("Errore durante la selezione della riga.", "Errore")
            return

        # colora la riga selezionata
        frame.card_list.SetBackgroundColour('blue')
        frame.card_list.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        frame.card_list.SetForegroundColour('white')


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


    def question_quit_app(self, frame):
        """Gestisce la richiesta di chiusura applicazione."""

        dlg = wx.MessageDialog(
            frame,
            "Confermi l'uscita dall'applicazione?",
            "Conferma Uscita",
            wx.YES_NO | wx.ICON_QUESTION
        )
        if dlg.ShowModal() == wx.ID_YES:
            dlg.Destroy()
            frame.Close()


    #@@# sezione collezzione di carte

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


    #@@# sezione mazzi 

    def load_decks(self, card_list=None):
        """ carica i mazzi dal database. """

        if not self.db_manager.load_decks(card_list=card_list):
            log.warning("Nessun mazzo trovato.")
            return False

        return True


    def get_selected_deck(self, card_list=None):
        """Restituisce il mazzo selezionato nella lista."""

        if not card_list:
            log.error("Errore durante la selezione del mazzo. Nessuna lista di carte rilevata.")
            wx.MessageBox("Errore durante la selezione del mazzo, nessuna lista di carte rilevata!", "Errore")
            return

        selection = card_list.GetFirstSelected()
        if selection != wx.NOT_FOUND:
            return card_list.GetItemText(selection)

        else:
            log.warning("Nessun mazzo selezionato.")
            wx.MessageBox("Seleziona un mazzo prima di procedere.", "Errore")
            return False


    def select_last_deck(self, frame):
        """Seleziona l'ultimo mazzo nella lista."""

        card_list = frame.card_list
        self.update_decks_list(card_list)
        frame.set_focus_to_list()
        end_list = card_list.GetItemCount()
        card_list.Select(end_list-1)
        card_list.Focus(end_list-1)
        card_list.EnsureVisible(end_list-1)
        card_list.SetFocus()
        card_list.Refresh()


    def select_and_focus_deck(self, frame, deck_name):
        """
        Seleziona un mazzo nella lista e imposta il focus su di esso.
        
        Args:
            frame: L'istanza del frame dei mazzi.
            deck_name: Il nome del mazzo da selezionare.

        """

        if not frame:
            log.error("Errore durante la selezione del mazzo. Nessun frame passato.")
            wx.MessageBox("Errore durante la selezione del mazzo.", "Errore")
            raise ValueError("Errore durante la selezione del mazzo. Nessun frame passato.")

        if not frame.card_list:
            log.error("Errore durante la selezione del mazzo. Nessuna lista di mazzi rilevata.")
            raise ValueError("Errore durante la selezione del mazzo. Nessuna lista di mazzi rilevata.")

        if not deck_name:
            log.error("Errore durante la selezione del mazzo. Nessun mazzo specificato.")
            raise ValueError("Errore durante la selezione del mazzo. Nessun mazzo specificato.")

        log.info(f"Tentativo di selezione e focus sul mazzo: {deck_name}")
        # Trova l'indice del mazzo nella lista
        for i in range(frame.card_list.GetItemCount()):
            if frame.card_list.GetItemText(i) == deck_name:
                log.info(f"Mazzo trovato all'indice: {i}")
                frame.card_list.Select(i)  # Seleziona il mazzo
                frame.card_list.Focus(i)   # Imposta il focus sul mazzo
                frame.card_list.EnsureVisible(i)  # Assicurati che il mazzo sia visibile
                frame.card_list.SetFocus() # Imposta il focus sulla lista dei mazzi
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


    def add_deck(self):#, frame):
        """Aggiunge un mazzo utilizzando DbManager."""

        if not self.db_manager.add_deck_from_clipboard():
            log.error("Errore durante l'aggiunta del mazzo.")
            return False

        log.info("Mazzo aggiunto con successo.")
        return True


    def delete_deck(self, frame, deck_name):
        """Elimina un mazzo utilizzando DbManager."""

        if not  self.db_manager.delete_deck(deck_name):
            log.error(f"Errore durante l'eliminazione del mazzo '{deck_name}'.")
            wx.MessageBox(f"Errore durante l'eliminazione del mazzo '{deck_name}'.", "Errore")
            return False

        card_list = frame.card_list
        self.update_decks_list(card_list)
        self.select_last_deck(frame)
        log.info(f"Mazzo '{deck_name}' eliminato con successo.")
        wx.MessageBox(f"Mazzo '{deck_name}' eliminato con successo.", "Successo")


    def copy_deck(self, frame):
        """ Copia un mazzo negli appunti. """

        deck_name = self.get_selected_deck(frame.card_list)
        if deck_name:
            if self.db_manager.copy_deck_to_clipboard(deck_name):
                self.select_and_focus_deck(frame, deck_name)
                #self.update_status(f"Mazzo '{deck_name}' copiato negli appunti.")
                wx.MessageBox(f"Mazzo '{deck_name}' copiato negli appunti.", "Successo")

            else:
                wx.MessageBox("Errore: Mazzo vuoto o non trovato.", "Errore")

        else:
            wx.MessageBox("Seleziona un mazzo prima di copiarlo negli appunti.", "Errore")


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


    def update_decks_list(self, card_list =None):
        """Aggiorna la lista dei mazzi."""

        #card_list = frame.card_list
        card_list.DeleteAllItems()  # Pulisce la lista
        with db_session() as session:  # Usa il contesto db_session
            decks = session.query(Deck).all()
            for deck in decks:
                index = card_list.InsertItem(card_list.GetItemCount(), deck.name)  # Prima colonna
                card_list.SetItem(index, 1, deck.player_class)  # Seconda colonna
                card_list.SetItem(index, 2, deck.game_format)  # Terza colonna
                
                # Calcola e visualizza il numero totale di carte
                total_cards = self.get_total_cards_in_deck(deck.name)
                card_list.SetItem(index, 3, str(total_cards))  # Aggiunge il numero totale di carte nella nuova colonna


    #def update_card_list(self, card_list):
        """Aggiorna la lista di carte."""

        #card_list.DeleteAllItems()
        #self.load_collection(card_list=card_list)



class CollectionController(DefaultController):
    """Controller per la vista della collezione di carte."""

    def __init__(self, container=None, **kwargs):
        super().__init__(container, **kwargs)
        self.container = container  # Memorizza il container
        self.db_manager = self.container.resolve("db_manager")
        self.widget_factory = self.container.resolve("widget_factory")  # Risolve WidgetFactory



class DeckController(DefaultController):
    """ Controller per la view di un singoolo mazzo. """

    def __init__(self, container=None, **kwargs):
        super().__init__(container, **kwargs)
        self.container = container  # Memorizza il container
        self.db_manager = self.container.resolve("db_manager")
        self.widget_factory = self.container.resolve("widget_factory")  # Risolve WidgetFactory



class DecksController(DefaultController):
    """ Controller per la vista dei mazzi. """

    def __init__(self, container=None, **kwargs):
        super().__init__(container, **kwargs)
        self.container = container  # Memorizza il container
        self.db_manager = self.container.resolve("db_manager")
        self.widget_factory = self.container.resolve("widget_factory")  # Risolve WidgetFactory
        self.deck_controller = None


    def apply_search_filter(self, frame, search_text):
        """Applica il filtro di ricerca alla lista dei mazzi."""

        if not search_text or search_text in ["tutti", "tutto", "all"]:
            # Se il campo di ricerca è vuoto o contiene "tutti", ripulisci la list aprima di ricaricare i mazzi
            frame.card_list.DeleteAllItems()
            # mostra tutti i mazzi
            frame.load_decks()
            # sposta il cursore nella lista deimazzi
            self.set_focus_to_list(frame)    # Imposta il focus sul primo mazzo della lista

        else:
            # Filtra i mazzi in base al nome o alla classe
            frame.card_list.DeleteAllItems()
            with db_session() as session:
                decks = session.query(Deck).filter(Deck.name.ilike(f"%{search_text}%") | Deck.player_class.ilike(f"%{search_text}%")).all()
                for deck in decks:
                    index = frame.card_list.InsertItem(frame.card_list.GetItemCount(), deck.name)
                    frame.card_list.SetItem(index, 1, deck.player_class)
                    frame.card_list.SetItem(index, 2, deck.game_format)

        self.set_focus_to_list(frame)    # Imposta il focus sul primo mazzo della lista






class MainController(DefaultController):

    def __init__(self, container=None, **kwargs):
        super().__init__(container, **kwargs)
        self.container = container  # Memorizza il container
        self.db_manager = self.container.resolve("db_manager")
        self.collection_controller = self.container.resolve("collection_controller")
        self.decks_controller = self.container.resolve("decks_controller")
        self.deck_controller = self.container.resolve("deck_controller")
        self.win_controller = self.container.resolve("win_controller")



#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
