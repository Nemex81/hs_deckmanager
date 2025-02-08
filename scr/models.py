"""
    models.py

    Modulo per la gestione dei mazzi di Hearthstone e delle operazioni correlate.

    Path:
        scr/models.py   

    Descrizione:
 
        Questo modulo contiene la classe DeckManager e funzioni utili per gestire:

            - Caricamento/salvataggio dei mazzi da/in file JSON
            - Parsing delle carte dai mazzi con verifica di validità
            - Sincronizzazione delle carte con il database
            - Calcolo delle statistiche e delle proprietà del mazzo
            - Manipolazione delle informazioni relative ai mazzi (aggiunta, eliminazione)

    Note:
        Questo modulo utilizza il modulo `db` per l'interazione con il database SQLite.
        Le funzioni di parsing utilizzano regex per estrarre le informazioni dai mazzi.

"""

#lib
import os
import shutil
import re
import pyperclip
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from .db import session, db_session, Deck, DeckCard, Card
from utyls import enu_glob as eg
from utyls import logger as log
#import pdb



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
                return

            metadata = self.parse_deck_metadata(deck_string)
            deck_name = metadata["name"]
            cards = self.parse_cards_from_deck(deck_string)

            # Utilizzo di db_session per gestire la sessione
            with db_session():
                # Creazione del nuovo mazzo
                new_deck = Deck(
                    name=deck_name,
                    player_class=metadata["player_class"],
                    game_format=metadata["game_format"]
                )
                session.add(new_deck)

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
            raise

        except ValueError as e:
            log.warning(f"Errore di validazione: {str(e)}")
            raise

        except Exception as e:
            log.error(f"Errore imprevisto durante l'aggiunta del mazzo: {str(e)}")
            raise


    def sync_cards_with_database(self, deck_string):
        """ Sincronizza le carte del mazzo con il database. """
        log.info("Inizio sincronizzazione delle carte con il database.")
        try:
            cards = self.parse_cards_from_deck(deck_string)
            card_names = [card["name"] for card in cards]

            # Recupera tutte le carte esistenti in una singola query
            existing_cards = session.query(Card.name).filter(Card.name.in_(card_names)).all()
            existing_card_names = {card.name for card in existing_cards}

            # Filtra le nuove carte
            new_cards_data = [card for card in cards if card["name"] not in existing_card_names]

            # Crea una lista di oggetti Card per le nuove carte
            new_cards = [
                Card(
                    name=card_data["name"],
                    class_name="Unknown",
                    mana_cost=card_data["mana_cost"],
                    card_type="Unknown",
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

        except SQLAlchemyError as e:
            log.error(f"Errore del database durante la sincronizzazione: {str(e)}")
            session.rollback()
            wx.MessageBox(f"Errore del database durante la sincronizzazione: {str(e)}", "Errore", wx.OK | wx.ICON_ERROR)
            raise
        except Exception as e:
            log.error(f"Errore imprevisto durante la sincronizzazione: {str(e)}")
            wx.MessageBox(f"Errore imprevisto durante la sincronizzazione: {str(e)}", "Errore", wx.OK | wx.ICON_ERROR)
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
        return session.query(Card).filter_by(name=card_name).first() is not None


    def add_card_to_database(self, card):
        """Aggiunge una nuova carta al database."""

        new_card = Card(
            name=card["name"],
            class_name="Unknown",
            mana_cost=card["mana_cost"],
            card_type="Unknown",
            card_subtype="Unknown",
            rarity="Unknown",
            expansion="Unknown"
        )

        session.add(new_card)
        session.commit()
        log.info(f"Carta '{card['name']}' aggiunta al database.")


    def get_deck(self, deck_name):
        """Restituisce il contenuto di un mazzo dal database."""

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
                    return

                # Elimina le carte associate al mazzo
                session.query(DeckCard).filter_by(deck_id=deck.id).delete()
                # Elimina il mazzo
                session.delete(deck)

            log.info(f"Mazzo '{deck_name}' eliminato con successo.")
            return True


        except SQLAlchemyError as e:
            log.error(f"Errore del database durante l'eliminazione del mazzo '{deck_name}': {str(e)}")
            session.rollback() # Annulla le modifiche in caso di errore

        except Exception as e:
            log.error(f"Errore imprevisto durante l'eliminazione del mazzo '{deck_name}': {str(e)}")
            raise


    def get_deck_statistics(self, deck_name):
        """Calcola statistiche dettagliate per un mazzo."""

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



class AppController:
    """ Controller per la gestione delle operazioni dell'applicazione. """

    def __init__(self, db_manager, app):
        self.db_manager = db_manager
        self.app = app


    def add_deck(self, deck_name):
        """ Aggiunge un mazzo al database. """

        try:
            self.db_manager.add_deck_from_clipboard(deck_name)
            self.app.update_deck_list()
            self.app.update_status(f"Mazzo '{deck_name}' aggiunto con successo.")
            return True

        except ValueError as e:
            raise

        except Exception as e:
            log.error(f"Errore durante l'aggiunta del mazzo: {e}")
            raise


    def delete_deck(self, deck_name):
        """ Elimina un mazzo dal database. """

        try:
            if self.db_manager.delete_deck(deck_name):
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
        return self.db_manager.get_deck_statistics(deck_name)



#@@@# Fine del modulo
if __name__ != "__main__":
    print("Carico: %s" % __name__)
