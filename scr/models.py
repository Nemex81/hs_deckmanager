"""
    models.py

    Modulo per la gestione dei mazzi di Hearthstone e delle operazioni correlate.

    Path:
        scr/models.py   

    Descrizione:
 
        Questo modulo contiene funzioni utili per gestire:

            - Caricamento/salvataggio dei mazzi da/in file JSON
            - Parsing delle carte dai mazzi con verifica di validità
            - Sincronizzazione delle carte con il database
            - Calcolo delle statistiche e delle proprietà del mazzo
            - Manipolazione delle informazioni relative ai mazzi (aggiunta, eliminazione)
            - Gestione delle operazioni CRUD sulle carte
            - Caricamento delle carte dal database con filtri
            - Copia dei mazzi negli appunti
            - Estrazione delle informazioni di metadata da un mazzo
            - Verifica della validità di un mazzo
            - Aggiornamento di un mazzo esistente nel database
            - Caricamento dei mazzi dal database e visualizzazione in una lista

    Note:
        - Il modulo si occupa di gestire le operazioni di caricamento/salvataggio dei mazzi, la sincronizzazione delle carte con il database e la gestione delle operazioni CRUD sulle carte.
        - Le funzioni di caricamento dei mazzi e delle carte dal database sono utilizzate per popolare le viste dell'applicazione.
        - La classe DbManager fornisce metodi per gestire le operazioni sul database, mentre la classe AppController si occupa di coordinare le operazioni tra l'interfaccia utente e il DbManager.
        - Il modulo utilizza il logger per registrare gli eventi e le eccezioni.

"""

#lib
import re, pyperclip
from contextlib import contextmanager
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from .db import session, db_session, Deck, DeckCard, Card
from utyls import enu_glob as eg
from utyls import logger as log
#import pdb


filters_options = ["tutti", "Tutti", "qualsiasi", "Qualsiasi", "", "all", "All", "", None]



def serialize_card(card):
    """Serializza un oggetto Card in un dizionario."""

    return {
        "id": card.id,
        "name": card.name,
        "class_name": card.class_name,
        "mana_cost": card.mana_cost,
        "card_type": card.card_type,
        "spell_type": card.spell_type,
        "card_subtype": card.card_subtype,
        "attack": card.attack,
        "health": card.health,
        "durability": card.durability,
        "rarity": card.rarity,
        "expansion": card.expansion
    }


def load_cards_from_db(filters=None):
    with db_session() as session:
        query = session.query(Card)
        if filters:
            # Applica i filtri in modo combinato
            if filters.get("name"):
                query = query.filter(Card.name.ilike(f"%{filters['name']}%"))
            if filters.get("mana_cost") and filters["mana_cost"] not in filters_options:
                query = query.filter(Card.mana_cost == int(filters["mana_cost"]))
            
            if filters.get("card_type") and filters["card_type"] not in filters_options:
                query = query.filter(Card.card_type == filters["card_type"])

            if filters.get("spell_type") and filters["spell_type"] not in filters_options:
                query = query.filter(Card.spell_type == filters["spell_type"])

            if filters.get("card_subtype") and filters["card_subtype"] not in filters_options:
                query = query.filter(Card.card_subtype == filters["card_subtype"])

            if filters.get("attack") and filters["attack"] not in filters_options:
                query = query.filter(Card.attack == int(filters["attack"]))

            if filters.get("health") and filters["health"] not in filters_options:
                query = query.filter(Card.health == int(filters["health"]))

            if filters.get("durability") and filters["durability"] not in filters_options:
                query = query.filter(Card.durability == int(filters["durability"]))

            if filters.get("rarity") and filters["rarity"] not in filters_options:
                query = query.filter(Card.rarity == filters["rarity"])

            if filters.get("expansion") and filters["expansion"] not in filters_options:
                query = query.filter(Card.expansion == filters["expansion"])

        log.info(f"Carte trovate: {query.count()}")
        cards = query.order_by(Card.mana_cost, Card.name).all()
        return [serialize_card(card) for card in cards]  # Restituisci una lista di dizionari


def load_deck_from_db(deck_name=None, deck_content=None, filters=None, card_list=None):
    """Carica le carte di un mazzo dal database e le aggiunge alla lista."""

    if not deck_content:
        raise ValueError("Deck content non è stato inizializzato correttamente.")
    
    with db_session() as session:
        # Carica le carte del mazzo
        deck_cards = session.query(DeckCard).filter_by(deck_id=deck_content["id"]).all()
        for deck_card in deck_cards:
            card = session.query(Card).filter_by(id=deck_card.card_id).first()
            if card:
                card_dict = serialize_card(card)  # Serializza la carta in un dizionario
                # Applica i filtri (se presenti)
                if filters:
                    if filters.get("name") and filters["name"].lower() not in card_dict["name"].lower():
                        continue

                    if filters.get("mana_cost") and filters["mana_cost"] not in  filters_options and card_dict["mana_cost"] != int(filters["mana_cost"]):
                        continue

                    if filters.get("card_type") and filters["card_type"] not in filters_options and card_dict["card_type"] != filters["card_type"]:
                        continue

                    if filters.get("spell_type") and filters["spell_type"] not in filters_options and card_dict["spell_type"] != filters["spell_type"]:
                        continue

                    if filters.get("card_subtype") and filters["card_subtype"] not in filters_options and card_dict["card_subtype"] != filters["card_subtype"]:
                        continue

                    if filters.get("attack") and filters["attack"] not in filters_options and card_dict["attack"] != int(filters["attack"]):
                        continue

                    if filters.get("health") and filters["health"] not in filters_options and card_dict["health"] != int(filters["health"]):
                        continue

                    if filters.get("rarity") and filters["rarity"] not in filters_options and card_dict["rarity"] != filters["rarity"]:
                        continue

                    if filters.get("expansion") and filters["expansion"] not in filters_options and card_dict["expansion"] != filters["expansion"]:
                        continue

                # Aggiungi la carta alla lista
                card_list.Append([
                    card_dict["name"],
                    str(card_dict["mana_cost"]) if card_dict["mana_cost"] else "-",
                    str(deck_card.quantity) if deck_card.quantity else "-",
                    card_dict["card_type"] if card_dict["card_type"] else "-",
                    card_dict["spell_type"] if card_dict["spell_type"] else "-",
                    card_dict["card_subtype"] if card_dict["card_subtype"] else "-", 
                    str(card_dict["attack"]) if card_dict["attack"] is not None else "-",
                    str(card_dict["health"]) if card_dict["health"] is not None else "-",
                    str(card_dict["durability"]) if card_dict["durability"] is not None else "-",
                    card_dict["rarity"] if card_dict["rarity"] else "-",
                    card_dict["expansion"] if card_dict["expansion"] else "-"
                ])

        #log.info(f"Caricate {len(deck_cards)} carte dal mazzo '{deck_name}'.")
        return deck_cards


def load_cards(card_list=None, deck_content=None, mode="collection", filters=None):
    """Carica le carte nella lista."""

    card_list.DeleteAllItems()
    if mode == "collection":
        cards = load_cards_from_db(filters)  # Ora cards è una lista di dizionari
        for card in cards:
            card_list.Append([
                card["name"], 
                str(card["mana_cost"]) if card["mana_cost"] else "-",
                card["class_name"] if card["class_name"] else "-",
                card["card_type"] if card["card_type"] else "-",
                card["spell_type"] if card["spell_type"] else "-",
                card["card_subtype"] if card["card_subtype"] else "-",
                str(card["attack"]) if card["attack"] is not None else "-",
                str(card["health"]) if card["health"] is not None else "-",
                str(card["durability"]) if card["durability"] is not None else "-",
                card["rarity"] if card["rarity"] else "-",
                card["expansion"] if card["expansion"] else "-"
            ])

    elif mode == "deck":
        # Carica le carte del mazzo
        load_deck_from_db(deck_content=deck_content, filters=filters, card_list=card_list)



class DbManager:
    """ Classe per la gestione dei mazzi di Hearthstone. """

    def __init__(self):
        pass

    @staticmethod
    def parse_deck_metadata(deck_string):
        """ Estrae le informazioni di metadata da un mazzo. """
        lines = deck_string.splitlines()[:3]
        metadata = {
            "name": lines[0].replace("###", "").strip(),
            "player_class": "Neutrale",
            "game_format": "Standard"
        }
        
        for line in lines[1:]:
            if "Classe:" in line:
                metadata["player_class"] = line.split(":")[1].strip()
            elif "Formato:" in line:
                metadata["game_format"] = line.split(":")[1].strip()
        
        return metadata

    def is_valid_deck(self, deck_string):
        """Verifica se una stringa rappresenta un mazzo valido."""
        last_verify = "# Per utilizzare questo mazzo, copialo negli appunti e crea un nuovo mazzo in Hearthstone"
        return bool(
            deck_string and 
            deck_string.startswith("###") and 
            deck_string.splitlines()[-1].startswith(last_verify)
        )

    def copy_deck_to_clipboard(self, deck_name):
        """ Copia un mazzo dal database negli appunti. """
        with db_session():
            deck_content = self.get_deck(deck_name)
            if deck_content:
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
                return True
        return False

    def add_deck_from_clipboard(self, deck_string=None):
        """Aggiunge un mazzo copiato dagli appunti al database."""
        try:
            if not deck_string:
                deck_string = pyperclip.paste()

            if not self.is_valid_deck(deck_string):
                log.error("Il mazzo copiato non è valido.")
                return False

            # Sincronizza le carte prima di aggiungere il mazzo
            self.sync_cards_with_database(deck_string)

            # Estrae i metadati del mazzo
            metadata = self.parse_deck_metadata(deck_string)
            deck_name = metadata["name"]

            # Verifica se il mazzo esiste già
            if self.get_deck(deck_name):
                log.warning(f"Il mazzo '{deck_name}' è già presente nel database.")
                return False

            # Aggiungi il mazzo
            with db_session() as session:
                new_deck = Deck(
                    name=deck_name,
                    player_class=metadata["player_class"],
                    game_format=metadata["game_format"]
                )
                session.add(new_deck)
                session.flush()  # Ottieni l'ID del nuovo mazzo

                # Aggiungi le relazioni tra mazzo e carte
                cards = self.parse_cards_from_deck(deck_string)
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
                        session.flush()

                    # Aggiungi la relazione tra mazzo e carta
                    session.add(DeckCard(
                        deck_id=new_deck.id,
                        card_id=card.id,
                        quantity=card_data["quantity"]
                    ))

                session.commit()

            log.info(f"Mazzo '{deck_name}' aggiunto con successo.")
            return True

        except Exception as e:
            log.error(f"Errore durante l'aggiunta del mazzo: {str(e)}")
            return False


    def sync_cards_with_database(self, deck_string):
        """Sincronizza le carte del mazzo con il database."""
        log.info("Inizio sincronizzazione delle carte con il database.")
        try:
            cards = self.parse_cards_from_deck(deck_string)
            if not cards:
                log.error("Nessuna carta trovata nel mazzo.")
                return

            with db_session() as session:  # Usa il contesto db_session
                for card_data in cards:
                    card = session.query(Card).filter_by(name=card_data["name"]).first()
                    if not card:
                        log.debug(f"Carta '{card_data['name']}' non trovata nel database. Aggiunta in corso...")
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
                # Commit alla fine della transazione
                session.commit()

        except SQLAlchemyError as e:
            log.error(f"Errore del database durante la sincronizzazione delle carte: {str(e)}")
            raise
        except Exception as e:
            log.error(f"Errore durante la sincronizzazione delle carte: {str(e)}")
            raise

        log.debug("Sincronizzazione delle carte completata.")


    def parse_card_line(self, line):
        """ Estrae le informazioni da una riga di testo rappresentante una carta. """
        pattern = r'^#*\s*(\d+)x?\s*\((\d+)\)\s*(.+)$'
        match = re.match(pattern, line.strip())
        if match:
            return {
                "quantity": int(match.group(1)),
                "mana_cost": int(match.group(2)),
                "name": match.group(3).strip()
            }
        return None

    def parse_cards_from_deck(self, deck_string):
        """ Estrae le informazioni delle carte da un mazzo. """
        cards = []
        try:
            for line in deck_string.splitlines():
                card_data = self.parse_card_line(line)
                if card_data:
                    cards.append(card_data)
            return cards
        except Exception as e:
            log.error(f"Errore durante il parsing delle carte: {str(e)}")
            raise


    def parse_deck_from_clipboard(self):
        """ Estrae un mazzo copiato dagli appunti. """

        try:
            deck_string = pyperclip.paste()
            if self.is_valid_deck(deck_string):
                return deck_string
            return None

        except pyperclip.PyperclipException as e:
            log.error(f"Errore negli appunti: {str(e)}")
            return None


    def is_card_in_database(self, card_name):
        """Verifica se una carta esiste nel database."""
        with db_session():
            return session.query(Card).filter_by(name=card_name).first() is not None

    def add_card_to_database(self, card):
        """Aggiunge una nuova carta al database."""

        with db_session():
            new_card = Card(
                id=card["id"],
                name=card["name"],
                class_name="Unknown",
                mana_cost=card["mana_cost"],
                card_type="Unknown",
                spell_type="Unknown",
                card_subtype="Unknown",
                rarity="Unknown",
                expansion="Unknown"
            )

            session.add(new_card)
            session.commit()
            log.info(f"Carta '{card['name']}' aggiunta al database.")
            return True


    def get_deck(self, deck_name):
        """Restituisce il contenuto di un mazzo dal database."""
        with db_session() as session:  # Aggiungi il contesto
            deck = session.query(Deck).filter_by(name=deck_name).first()
            if deck:
                deck_cards = session.query(DeckCard).filter_by(deck_id=deck.id).all()
                cards = []
                for deck_card in deck_cards:
                    card = session.query(Card).filter_by(id=deck_card.card_id).first()
                    if card:
                        cards.append({
                            "id": card.id,
                            "name": card.name,
                            "mana_cost": card.mana_cost,
                            "quantity": deck_card.quantity,
                            "class_name": card.class_name,
                            "card_type": card.card_type,
                            "spell_type": card.spell_type,
                            "card_subtype": card.card_subtype,
                            "attack": card.attack,
                            "health": card.health,
                            "durability": card.durability,
                            "rarity": card.rarity,
                            "expansion": card.expansion
                        })
                return {
                    "id": deck.id,
                    "name": deck.name,
                    "player_class": deck.player_class,
                    "game_format": deck.game_format,
                    "cards": cards
                }
        return None


    def delete_deck(self, deck_name):
        """ Elimina un mazzo dal database. """
        try:
            with db_session():
                deck = session.query(Deck).filter_by(name=deck_name).first()
                if not deck:
                    log.warning(f"Tentativo di eliminazione del mazzo '{deck_name}' non trovato.")
                    return False

                # Elimina le carte associate al mazzo
                session.query(DeckCard).filter_by(deck_id=deck.id).delete()
                # Elimina il mazzo
                session.delete(deck)
                session.commit()

            log.info(f"Mazzo '{deck_name}' eliminato con successo.")
            return True

        except SQLAlchemyError as e:
            log.error(f"Errore del database durante l'eliminazione del mazzo '{deck_name}': {str(e)}")
            raise
        except Exception as e:
            log.error(f"Errore imprevisto durante l'eliminazione del mazzo '{deck_name}': {str(e)}")
            raise


    def get_deck_by_name(self, deck_name):
        """Restituisce i dettagli di un mazzo specifico."""
        with db_session() as session:  # Aggiungi il contesto
            deck = session.query(Deck).filter_by(name=deck_name).first()
            if deck:
                return {
                    "id": deck.id,
                    "name": deck.name,
                    "player_class": deck.player_class,
                    "game_format": deck.game_format,
                    "cards": self.get_deck_cards(deck.id)
                }
        return None


    def get_card_by_name(self, card_name):
        """Restituisce una carta dal database in base al nome."""
        with db_session() as session:  # Aggiungi il contesto
            card = session.query(Card).filter_by(name=card_name).first()
            if card:
                return serialize_card(card)
        return None


    def get_cards(self, filters=None):
        """Restituisce le carte dal database per la finestra collezzione generale in base ai filtri."""
        return load_cards_from_db(filters=filters)

    def get_deck_statistics(self, deck_name):
        """Calcola statistiche dettagliate per un mazzo."""
        with db_session():
            deck = self.get_deck(deck_name)
            if not deck:
                return None

            stats = {
                "Nome Mazzo": deck["name"],
                "Eroe": deck["player_class"],
                "Numero Carte": sum(card["quantity"] for card in deck["cards"]),
                "Creature": 0,
                "Magie": 0,
                "Armi": 0,
                "Luoghi": 0,
                "Costo Mana Medio": 0.0
            }

            total_mana = 0
            for card in deck["cards"]:
                db_card = session.query(Card).filter_by(name=card["name"]).first()
                if db_card:
                    card_type = db_card.card_type.lower()
                    if card_type == "creatura":
                        stats["Creature"] += card["quantity"]
                    elif card_type == "magia":
                        stats["Magie"] += card["quantity"]
                    elif card_type == "arma":
                        stats["Armi"] += card["quantity"]
                    elif card_type == "luogo":
                        stats["Luoghi"] += card["quantity"]

                    # Calcola il costo totale del mana
                    total_mana += db_card.mana_cost * card["quantity"]

            if stats["Numero Carte"] > 0:
                stats["Costo Mana Medio"] = total_mana / stats["Numero Carte"]

            # Arrotonda i valori a 2 decimali
            for key, value in stats.items():
                if isinstance(value, float):
                    stats[key] = round(value, 2)

            return stats


    def get_decks(self, filters=None):
        """Restituisce tutti i mazzi con opzioni di filtro."""
        with db_session() as session:  # Aggiungi il contesto
            query = session.query(Deck)
            if filters:
                if filters.get("name"):
                    query = query.filter(Deck.name.ilike(f"%{filters['name']}%"))
                if filters.get("player_class"):
                    query = query.filter(Deck.player_class.ilike(f"%{filters['player_class']}%"))
                if filters.get("game_format"):
                    query = query.filter(Deck.game_format.ilike(f"%{filters['game_format']}%"))
            return query.all()


    def get_deck_details(self, deck_name):
        """Restituisce i dettagli di un mazzo specifico."""

        with db_session() as session:
            deck = session.query(Deck).filter_by(name=deck_name).first()
            if deck:
                deck_cards = session.query(DeckCard).filter_by(deck_id=deck.id).all()
                cards = []
                for deck_card in deck_cards:
                    card = session.query(Card).filter_by(id=deck_card.card_id).first()
                    if card:
                        cards.append({
                            "name": card.name,
                            "mana_cost": card.mana_cost,
                            "quantity": deck_card.quantity
                        })
                return {
                    "name": deck.name,
                    "player_class": deck.player_class,
                    "game_format": deck.game_format,
                    "cards": cards
                }
            return None


    def get_total_cards_in_deck(self, deck_name):
        """Calcola il numero totale di carte in un mazzo."""

        try:
            with db_session() as session:
                deck = self.get_deck(deck_name)
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


    def apply_search_decks_filter(self, frame, search_text):
        """Applica il filtro di ricerca alla lista dei mazzi."""

        if not search_text or search_text in ["tutti", "tutto", "all"]:
            # Se il campo di ricerca è vuoto o contiene "tutti", ripulisci la list aprima di ricaricare i mazzi
            frame.card_list.DeleteAllItems()
            # mostra tutti i mazzi
            frame.load_decks()
            # sposta il cursore nella lista deimazzi
            frame.controller.set_focus_to_list(frame)    # Imposta il focus sul primo mazzo della lista

        else:
            # Filtra i mazzi in base al nome o alla classe
            frame.card_list.DeleteAllItems()
            with db_session() as session:
                decks = session.query(Deck).filter(Deck.name.ilike(f"%{search_text}%") | Deck.player_class.ilike(f"%{search_text}%")).all()
                for deck in decks:
                    index = frame.card_list.InsertItem(frame.card_list.GetItemCount(), deck.name)
                    frame.card_list.SetItem(index, 1, deck.player_class)
                    frame.card_list.SetItem(index, 2, deck.game_format)


    def load_collection(filters=None, card_list=None):
        """Carica le carte nella lista."""
        load_cards(filters=filters, card_list=card_list)


    def get_deck_cards(self, deck_id):
        """Restituisce le carte associate a un mazzo."""
        with db_session() as session:
            deck_cards = session.query(DeckCard).filter_by(deck_id=deck_id).all()
            cards = []
            for deck_card in deck_cards:
                card = session.query(Card).filter_by(id=deck_card.card_id).first()
                if card:
                    cards.append({
                        "name": card.name,
                        "mana_cost": card.mana_cost,
                        "quantity": deck_card.quantity
                    })

            return cards


    def new_load_decks(self, card_list=None):
        """Carica i mazzi dal database e restituisce una lista di dizionari."""

        # carichiamo i mazzi dal database usando db_session
        with db_session() as session:
            decks = session.query(Deck).all()
            if not decks:
                log.warning("Nessun mazzo trovato.")

        return decks


    def load_decks(self, card_list=None):
        """Carica i mazzi dal database."""
        if not card_list:
            log.error("Errore durante il caricamento dei mazzi. Nessuna lista passata.")
            raise ValueError("Errore durante il caricamento dei mazzi. Nessuna lista passata.")

        with db_session() as session:  # Aggiungi il contesto
            decks = session.query(Deck).all()
            if not decks:
                log.warning("Nessun mazzo trovato.")
                return False

            for deck in decks:
                log.info(f"Caricamento deck: {deck.name}")
                index = card_list.InsertItem(card_list.GetItemCount(), deck.name)
                card_list.SetItem(index, 1, deck.player_class)
                card_list.SetItem(index, 2, deck.game_format)
                stats = self.get_deck_statistics(deck.name)
                total_cards = stats.get("Numero Carte", 0)
                log.info(f"Totale carte per {deck.name}: {total_cards}")
                card_list.SetItem(index, 3, str(total_cards))
        return True


    def upgrade_deck(self, deck_name):
        """ Aggiorna un mazzo nel database. """

        try:
            deck_string = pyperclip.paste()
            if self.is_valid_deck(deck_string):
                with db_session() as session:  # Usa il contesto db_session
                    deck = session.query(Deck).filter_by(name=deck_name).first()
                    if deck:
                        # Elimina le carte associate al mazzo
                        session.query(DeckCard).filter_by(deck_id=deck.id).delete()
                        session.commit()

                        # Sincronizza le carte con il database
                        self.sync_cards_with_database(deck_string)

                        # Aggiungi le nuove carte al mazzo
                        cards = self.parse_cards_from_deck(deck_string)
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

                        return True

                    else:
                        log.error("Errore: Mazzo non trovato nel database.")
                        return False

            else:
                log.error("Il mazzo negli appunti non è valido.")
                return False

        except Exception as e:
            log.error(f"Errore durante l'aggiornamento del mazzo: {e}")
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



#@@@# Fine del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
