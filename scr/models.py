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



def load_cards_from_db(filters=None):
    """Carica le carte dal database e le restituisce come dizionari."""

    with db_session() as session:
        query = session.query(Card)
        if filters:
            # Applica i filtri
            if filters.get("name"):
                query = query.filter(Card.name.ilike(f"%{filters['name']}%"))
            if filters.get("mana_cost") and filters["mana_cost"] != "Qualsiasi":
                query = query.filter(Card.mana_cost == int(filters["mana_cost"]))
            if filters.get("card_type") and filters["card_type"] != "Tutti":
                query = query.filter(Card.card_type == filters["card_type"])
            if filters.get("spell_type") and filters["spell_type"] != "Qualsiasi":
                query = query.filter(Card.spell_type == filters["spell_type"])
            if filters.get("card_subtype") and filters["card_subtype"] != "Tutti":
                query = query.filter(Card.card_subtype == filters["card_subtype"])
            if filters.get("attack") and filters["attack"] != "Qualsiasi":
                query = query.filter(Card.attack == int(filters["attack"]))
            if filters.get("health") and filters["health"] != "Qualsiasi":
                query = query.filter(Card.health == int(filters["health"]))
            if filters.get("rarity") and filters["rarity"] != "Tutti":
                query = query.filter(Card.rarity == filters["rarity"])
            if filters.get("expansion") and filters["expansion"] != "Tutti":
                query = query.filter(Card.expansion == filters["expansion"])

        log.info(f"Carte trovate: {query.count()}")
        cards = query.order_by(Card.mana_cost, Card.name).all()

        # Serializza le carte in dizionari
        card_data = [
            {
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
            for card in cards
        ]
        return card_data


def load_deck_from_db(deck_name=None, filters=None):
    """Carica le carte di un mazzo dal database e le restituisce come dizionari."""
    with db_session() as session:
        deck = session.query(Deck).filter_by(name=deck_name).first()
        if not deck:
            log.warning(f"Mazzo '{deck_name}' non trovato.")
            return []

        # Recupera le relazioni tra mazzo e carte
        deck_cards = session.query(DeckCard).filter_by(deck_id=deck.id).all()

        # Serializza le carte in dizionari
        card_data = []
        for deck_card in deck_cards:
            card = session.query(Card).filter_by(id=deck_card.card_id).first()
            if card:
                # Applica i filtri (se presenti)
                if filters:
                    if filters.get("name") and filters["name"].lower() not in card.name.lower():
                        continue
                    if filters.get("mana_cost") and filters["mana_cost"] != "Qualsiasi" and card.mana_cost != int(filters["mana_cost"]):
                        continue
                    if filters.get("card_type") and filters["card_type"] != "Tutti" and card.card_type != filters["card_type"]:
                        continue

                card_data.append({
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
                    "expansion": card.expansion,
                    "quantity": deck_card.quantity
                })

        log.info(f"Carte trovate nel mazzo '{deck_name}': {len(card_data)}")
        return card_data


def load_cards(card_list=None, deck_content=None, mode="collection", filters=None):
    """Carica le carte nella lista."""
    card_list.DeleteAllItems()

    if mode == "collection":
        # Carica tutte le carte dalla collezione
        cards = load_cards_from_db(filters)
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
        # Carica le carte del mazzo specificato
        cards = load_deck_from_db(deck_name=deck_content["name"], filters=filters)
        for card in cards:
            card_list.Append([
                card["name"],
                str(card["mana_cost"]) if card["mana_cost"] else "-",
                str(card["quantity"]) if card["quantity"] else "-",
                card["card_type"] if card["card_type"] else "-",
                card["spell_type"] if card["spell_type"] else "-",
                card["card_subtype"] if card["card_subtype"] else "-",
                str(card["attack"]) if card["attack"] is not None else "-",
                str(card["health"]) if card["health"] is not None else "-",
                str(card["durability"]) if card["durability"] is not None else "-",
                card["rarity"] if card["rarity"] else "-",
                card["expansion"] if card["expansion"] else "-"
            ])


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

    def add_deck_from_clipboard(self):
        """ Aggiunge un mazzo copiato dagli appunti al database. """
        try:
            deck_string = pyperclip.paste()
            if not self.is_valid_deck(deck_string):
                log.error("Il mazzo copiato non è valido.")
                return False

            metadata = self.parse_deck_metadata(deck_string)
            deck_name = metadata["name"]
            cards = self.parse_cards_from_deck(deck_string)

            with db_session():
                # Creazione del nuovo mazzo
                new_deck = Deck(
                    name=deck_name,
                    player_class=metadata["player_class"],
                    game_format=metadata["game_format"]
                )
                session.add(new_deck)
                session.flush()  # Ottieni l'ID del nuovo mazzo

                # Sincronizzazione delle carte con il database
                self.sync_cards_with_database(deck_string)

                # Aggiunta delle relazioni tra mazzo e carte
                deck_cards = []
                for card_data in cards:
                    card = session.query(Card).filter_by(name=card_data["name"]).first()
                    if not card:
                        log.warning(f"Carta '{card_data['name']}' non trovata nel database.")
                        continue

                    deck_cards.append(DeckCard(deck_id=new_deck.id, card_id=card.id, quantity=card_data["quantity"]))
                
                session.bulk_save_objects(deck_cards)
                session.commit()

            log.info(f"Mazzo '{deck_name}' aggiunto con successo.")
            return True

        except pyperclip.PyperclipException as e:
            log.error(f"Errore negli appunti: {str(e)}")
            return False
        except ValueError as e:
            log.warning(f"Errore di validazione: {str(e)}")
            return False
        except SQLAlchemyError as e:
            log.error(f"Errore del database: {str(e)}")
            return False
        except Exception as e:
            log.error(f"Errore imprevisto durante l'aggiunta del mazzo: {str(e)}")
            return False

    def sync_cards_with_database(self, deck_string):
        """ Sincronizza le carte del mazzo con il database. """
        log.info("Inizio sincronizzazione delle carte con il database.")
        try:
            cards = self.parse_cards_from_deck(deck_string)
            card_names = [card["name"] for card in cards]

            with db_session():
                # Recupera tutte le carte esistenti in una singola query
                existing_cards = session.query(Card.name).filter(Card.name.in_(card_names)).all()
                existing_card_names = {card.name for card in existing_cards}

                # Filtra le nuove carte
                new_cards_data = [card for card in cards if card["name"] not in existing_card_names]

                # Crea una lista di oggetti Card per le nuove carte
                new_cards = [
                    Card(
                        id=card_data["id"],
                        name=card_data["name"],
                        class_name="Unknown",
                        mana_cost=card_data["mana_cost"],
                        card_type="Unknown",
                        spell_type="Unknown",
                        card_subtype="Unknown",
                        rarity="Unknown",
                        expansion="Unknown"
                    )
                    for card_data in new_cards_data
                ]

                # Inserisci tutte le nuove carte in una sola operazione
                session.bulk_save_objects(new_cards)
                session.commit()

            log.info("Sincronizzazione delle carte completata con successo.")
            return True

        except SQLAlchemyError as e:
            log.error(f"Errore del database durante la sincronizzazione: {str(e)}")
            raise
        except Exception as e:
            log.error(f"Errore imprevisto durante la sincronizzazione: {str(e)}")
            raise

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
        with db_session():
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
                            "quantity": deck_card.quantity
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


#@@@# Fine del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
