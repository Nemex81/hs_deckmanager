"""

    decks_view.py

    Modulo per la finestra di gestione dei mazzi.

    path:
        scr/views/decks_view.py

    Note:
        Questo modulo contiene la definizione della finestra di gestione dei mazzi, che consente all'utente di visualizzare, creare, modificare, copiare, eliminare e visualizzare statistiche sui mazzi di carte di Hearthstone.
        Questo modulo utilizza la libreria wxPython per la creazione delle finestre di dialogo dell'interfaccia utente.

"""

# lib
import wx, pyperclip
import wx.lib.newevent
from sqlalchemy.exc import SQLAlchemyError
from ..db import session, db_session, Card, DeckCard, Deck
#from ..models import load_cards_from_db, load_deck_from_db, load_cards
from .view_components import create_button, create_list_ctrl, create_sizer, add_to_sizer, create_search_bar
from .proto_views import BasicView
from .deck_stats_dialog import DeckStatsDialog
from .collection_view import CardCollectionFrame
from .deck_view import DeckViewFrame
#from utyls.enu_glob import EnuColors, ENUCARD, EnuExtraCard, EnuCardType, EnuSpellType, EnuSpellSubType, EnuPetSubType, EnuHero, EnuRarity, EnuExpansion
from utyls import enu_glob as eg
from utyls import helper as hp
from utyls import logger as log
#import pdb

# Creazione di un evento personalizzato per la ricerca con debounce
SearchEvent, EVT_SEARCH_EVENT = wx.lib.newevent.NewEvent()



class DecksManagerFrame(BasicView):
    """ Finestra di gestione dei mazzi. """

    def __init__(self, parent, controller):
        title = "Gestione Mazzi"
        super().__init__(parent, title=title, size=(800, 600))
        self.parent = parent
        self.controller = controller
        self.db_manager = self.controller.db_manager

        # Timer per il debounce
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.Bind(EVT_SEARCH_EVENT, self.on_search_event)


    def init_ui_elements(self):
        """ Inizializza l'interfaccia utente utilizzando le funzioni helper. """

        # Impostazioni finestra principale
        self.panel.SetBackgroundColour('black')

        # Creazione degli elementi dell'interfaccia
        lbl_title = wx.StaticText(self.panel, label="Elenco Mazzi")
        self.deck_list = create_list_ctrl(
            self.panel,
            columns=[("Mazzo", 260), ("Classe", 200), ("Formato", 120)]
        )

        # coloro la lista dei mazzi
        self.deck_list.SetBackgroundColour('yellow')

        # Carichiamo i mazzi
        self.load_decks()

        # Barra di ricerca
        self.search_bar = create_search_bar(
            self.panel,
            placeholder="Cerca mazzo...",
            event_handler=self.on_search
        )
        self.search_bar.Bind(wx.EVT_TEXT, self.on_search_text_change)  # Aggiunto per la ricerca dinamica

        # Pulsanti
        btn_add = create_button(self.panel, label="Aggiungi Mazzo", event_handler=self.on_add_deck)
        btn_copy = create_button(self.panel, label="Copia Mazzo", event_handler=self.on_copy_deck)
        btn_view = create_button(self.panel, label="Visualizza Mazzo", event_handler=self.on_view_deck)
        btn_stats = create_button(self.panel, label="Statistiche Mazzo", event_handler=self.on_view_stats)
        btn_update = create_button(self.panel, label="Aggiorna Mazzo", event_handler=self.on_update_deck)
        btn_delete = create_button(self.panel, label="Elimina Mazzo", event_handler=self.on_delete_deck)
        btn_collection = create_button(self.panel, label="Collezione Carte", event_handler=self.on_view_collection)
        btn_exit = create_button(self.panel, label="Chiudi", event_handler=self.on_close)

        # Layout principale
        main_sizer = create_sizer(wx.VERTICAL)
        add_to_sizer(main_sizer, lbl_title, flag=wx.CENTER | wx.TOP, border=10)
        add_to_sizer(main_sizer, self.search_bar, flag=wx.EXPAND | wx.ALL, border=5)

        # Separatore tra barra di ricerca e lista dei mazzi
        add_to_sizer(main_sizer, wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)
        add_to_sizer(main_sizer, self.deck_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # Separatore tra lista dei mazzi e pulsanti
        add_to_sizer(main_sizer, wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        # Layout pulsanti
        btn_sizer = wx.GridSizer(rows=4, cols=2, hgap=10, vgap=10)
        for btn in [btn_add, btn_copy, btn_view, btn_stats, btn_update, btn_delete, btn_collection, btn_exit]:
            self.bind_focus_events(btn)  # Collega gli eventi di focus
            btn_sizer.Add(btn, flag=wx.EXPAND | wx.ALL, border=5)

        #resetto i colori di tutti i pulsanti
        self.reset_focus_style_for_all_buttons(btn_sizer)

        add_to_sizer(main_sizer, btn_sizer, flag=wx.EXPAND | wx.ALL, border=10)

        # Separatore tra pulsanti e barra di stato
        add_to_sizer(main_sizer, wx.StaticLine(self.panel), flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=10)

        # Imposta il sizer principale
        self.panel.SetSizer(main_sizer)

        # Barra di stato
        #self.status_bar = self.CreateStatusBar()
        #self.status_bar.SetStatusText("Pronto")

        # Imposta il focus sul search bar
        self.search_bar.SetFocus()

        # forza il layout (facoltativo, forza la riscrittura e impaginazione degli elementi grafici)
        #self.Layout()


    def new_load_decks(self):
        """Carica i mazzi dal database."""

        decks = self.controller.load_decks()
        for deck in decks:
            index = self.deck_list.InsertItem(self.deck_list.GetItemCount(), deck.name)
            self.deck_list.SetItem(index, 1, deck.player_class)
            self.deck_list.SetItem(index, 2, deck.game_format)


    def set_focus_to_list(self):
        """
        Imposta il focus sulla lista dei mazzi e seleziona il primo elemento.
        """
        if hasattr(self, "deck_list") and self.deck_list.GetItemCount() > 0:
            self.deck_list.SetFocus()  # Imposta il focus sulla lista
            self.deck_list.Select(0)   # Seleziona il primo elemento
            self.deck_list.Focus(0)    # Sposta il focus sul primo elemento
            self.deck_list.EnsureVisible(0)  # Assicurati che il primo elemento sia visibile


    def load_decks(self):
        """Carica i mazzi ."""

        # carichiamo i mazzi
        decks = session.query(Deck).all()
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


    def update_status(self, message):
        """Aggiorna la barra di stato."""
        #self.status_bar.SetStatusText(message)
        pass


    def get_selected_deck(self):
        """Restituisce il mazzo selezionato nella lista."""
        selection = self.deck_list.GetFirstSelected()
        if selection != wx.NOT_FOUND:
            return self.deck_list.GetItemText(selection)
        return None


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


    def _apply_search_filter(self, search_text):
        """Applica il filtro di ricerca alla lista dei mazzi."""
        if not search_text or search_text in ["tutti", "tutto", "all"]:
            # Se il campo di ricerca è vuoto o contiene "tutti", mostra tutti i mazzi
            self.load_decks()
        else:
            # Filtra i mazzi in base al nome o alla classe
            self.deck_list.DeleteAllItems()
            decks = session.query(Deck).filter(Deck.name.ilike(f"%{search_text}%") | Deck.player_class.ilike(f"%{search_text}%")).all()
            for deck in decks:
                index = self.deck_list.InsertItem(self.deck_list.GetItemCount(), deck.name)
                self.deck_list.SetItem(index, 1, deck.player_class)
                self.deck_list.SetItem(index, 2, deck.game_format)

        self.set_focus_to_list()    # Imposta il focus sul primo mazzo della lista

    def on_timer(self, event):
        """Esegue la ricerca dopo il timeout del debounce."""

        search_text = self.search_bar.GetValue().strip().lower()
        evt = SearchEvent(search_text=search_text)
        wx.PostEvent(self, evt)

    def on_search_text_change(self, event):
        """Gestisce la ricerca in tempo reale mentre l'utente digita."""

        search_text = self.search_bar.GetValue().strip().lower()
        if not search_text:
            self.load_decks()  # Ricarica tutti i mazzi se la casella di ricerca è vuota

        # Avvia il timer per il debounce (es. 500 ms)
        self.timer.Stop()  # Ferma il timer precedente
        self.timer.Start(500, oneShot=True)


    def on_search_event(self, event):
        """Gestisce l'evento di ricerca con debounce."""

        search_text = event.search_text
        self._apply_search_filter(search_text)
        self.set_focus_to_list()


    def on_add_deck(self, event):

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
                        success = self.db_manager.add_deck_from_clipboard()
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
                self.update_deck_list()

        except pyperclip.PyperclipException as e:
            wx.MessageBox("Errore negli appunti. Assicurati di aver copiato un mazzo valido.", "Errore")

        except Exception as e:
            log.error(f"Errore durante l'aggiunta del mazzo: {e}")
            wx.MessageBox("Si è verificato un errore imprevisto.", "Errore")


    def on_copy_deck(self, event):
        """Copia il mazzo selezionato negli appunti."""

        deck_name = self.get_selected_deck()
        if deck_name:
            if self.db_manager.copy_deck_to_clipboard(deck_name):
                self.update_status(f"Mazzo '{deck_name}' copiato negli appunti.")
                wx.MessageBox(f"Mazzo '{deck_name}' copiato negli appunti.", "Successo")
                self.select_and_focus_deck(deck_name)

            else:
                wx.MessageBox("Errore: Mazzo vuoto o non trovato.", "Errore")

        else:
            wx.MessageBox("Seleziona un mazzo prima di copiarlo negli appunti.", "Errore")


    def on_view_deck(self, event):
        """Mostra il mazzo selezionato in una finestra dettagliata."""

        deck_name = self.get_selected_deck()
        if deck_name:
            deck_content = self.db_manager.get_deck_details(deck_name)
            if deck_content:
                # Apri la finestra di visualizzazione del mazzo
                self.controller.run_deck_frame(parent=self, deck_name=deck_name)

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
                    if self.db_manager.is_valid_deck(deck_string):
                        with db_session() as session:  # Usa il contesto db_session
                            deck = session.query(Deck).filter_by(name=deck_name).first()
                            if deck:
                                # Elimina le carte associate al mazzo
                                session.query(DeckCard).filter_by(deck_id=deck.id).delete()
                                session.commit()

                                # Sincronizza le carte con il database
                                self.db_manager.sync_cards_with_database(deck_string)

                                # Aggiungi le nuove carte al mazzo
                                cards = self.db_manager.parse_cards_from_deck(deck_string)
                                for card_data in cards:
                                    card = session.query(Card).filter_by(name=card_data["name"]).first()
                                    if not card:
                                        card = Card(
                                            name=card_data["name"],
                                            class_name="Unknown",
                                            mana_cost=card_data["mana_cost"],
                                            card_type="Unknown",
                                            spell_type="Unknown",
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
                    log.error(f"Errore durante l'aggiornamento del mazzo: {e}")
                    wx.MessageBox(f"Si è verificato un errore: {e}", "Errore")

        else:
            wx.MessageBox("Seleziona un mazzo prima di aggiornarlo.", "Errore")


    def on_view_stats(self, event):
        """Mostra le statistiche del mazzo selezionato."""

        deck_name = self.get_selected_deck()
        if deck_name:
            stats = self.db_manager.get_deck_statistics(deck_name)
            if stats:
                DeckStatsDialog(self, stats=stats).ShowModal()

            else:
                wx.MessageBox("Impossibile calcolare le statistiche per questo mazzo.", "Errore")

        else:
            wx.MessageBox("Seleziona un mazzo prima di visualizzare le statistiche.", "Errore")


    def on_view_collection(self, event):
        """Mostra la collezione delle carte."""
        self.controller.run_collection_frame(parent=self)
        self.Hide()                                                         # Nasconde la finestra di gestione dei mazzi
        #collection_dialog.Show()                                            # Mostra la finestra come modale


    def on_delete_deck(self, event):
        """Elimina il mazzo selezionato."""
        deck_name = self.get_selected_deck()
        if deck_name:
            if wx.MessageBox(f"Sei sicuro di voler eliminare '{deck_name}'?", "Conferma", wx.YES_NO) == wx.YES:
                try:
                    with db_session() as session:  # Usa il contesto db_session
                        success = self.db_manager.delete_deck(deck_name)
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
        """Gestisce la ricerca testuale."""
        search_text = self.search_bar.GetValue().strip().lower()
        self._apply_search_filter(search_text)


    def last_on_search(self, event):
        """Filtra i mazzi in base al testo di ricerca."""

        # cerchiamo la parola richiesta dall'utente sia nei nomi dei mazzi sia nella classe
        search_text = self.search_bar.GetValue()
        self.deck_list.DeleteAllItems()
        decks = session.query(Deck).filter(Deck.name.ilike(f"%{search_text}%") | Deck.player_class.ilike(f"%{search_text}%")).all()
        for deck in decks:
            Index = self.deck_list.InsertItem(self.deck_list.GetItemCount(), deck.name)
            self.deck_list.SetItem(Index, 1, deck.player_class)
            self.deck_list.SetItem(Index, 2, deck.game_format)


    def on_close(self, event):
        """Chiude l'applicazione."""
        self.parent.Show()  # Mostra la finestra principale
        self.Close()        # Chiude la finestra di gestione dei mazzi



#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
