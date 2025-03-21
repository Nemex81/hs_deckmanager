"""
        Modulo per la gestione dei log del gioco

        **Path:**
            ```
            utyls/logger.py
            ```

    ---

        **Versione:** 0.5
        **Data:** 08 marzo 2025
        **Autore:** [Nemex]

    ---
            
"""

# lib
from logging.handlers import RotatingFileHandler
import logging, os, sys

# Configurazione del logging

#logging.basicConfig(
    #filename='/logs/hdm.log',                             # File di log
    #level=logging.DEBUG,                                        # Livello di log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    #format='%(asctime)s - %(levelname)s - %(message)s',             # Formato del log
    #datefmt='%Y-%m-%d %H:%M:%S'                                     # Formato della data
#)



# Configurazione del logging
handler = RotatingFileHandler('logs/hdm.log', maxBytes=10024 * 10024, backupCount=10, encoding='utf-8')
logging.basicConfig(handlers=[handler], level=logging.DEBUG)



def setup_logging(log_file='logs/hdm.log', console_output=False):
    """ 
    Configura il logging dell'applicazione, creando la cartella e il file di log se non esistono.

    Argomenti:
        log_file (str): Percorso del file di log.
        console_output (bool): Specifica se abilitare l'output su console.

    Note:
        - Questa funzione deve essere chiamata all'inizio del programma per configurare il logging.
    """
    try:
        # Estrai il percorso della cartella dei log dal file di log
        log_dir = os.path.dirname(log_file)

        # Verifica e crea la cartella logs se non esiste
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            print(f"Cartella '{log_dir}' creata con successo.")  # Messaggio di debug

        # Verifica e crea il file di log se non esiste
        if not os.path.exists(log_file):
            with open(log_file, 'w') as f:
                pass  # Crea il file vuoto
            print(f"File di log '{log_file}' creato con successo.")  # Messaggio di debug

        # Configura gli handler per il logging
        handlers = [logging.FileHandler(log_file)]
        if console_output:
            handlers.append(logging.StreamHandler())

        # Configura il logging
        logging.basicConfig(
            handlers=handlers,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        logging.info("Sistema di logging configurato con successo.")

    except Exception as e:
        print(f"Errore durante la configurazione del logging: {e}")  # Messaggio di debug
        raise RuntimeError(f"Impossibile configurare il logging: {e}")


def last_setup_logging(log_file='logs/hdm.log', console_output=False):
    """ 
        Configura il logging dell'applicazione.

        Argomenti:
                    log_file (str): Percorso del file di log.
                    console_output (bool): Specifica se abilitare l'output su console.

            Note:
                    - Questa funzione deve essere chiamata all'inizio del programma per configurare il logging.
    """

    handlers = [logging.FileHandler(log_file)]
    if console_output:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        handlers=handlers,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )



#@@# funzioni per la gestione dei log #@@#

def app_start():
    logging.info('Applicazione avviata.')

def app_end():
    logging.info('Applicazione terminata.')

def game_start():
    logging.info('La partita è iniziata.')

def game_end():
    logging.info('La partita è terminata.')

def player_action(player, action, details):
    logging.info(f'Azione del giocatore {player}: {action} - Dettagli: {details}')

def error(error):
    logging.error(f'Errore: {error}')

def warning(warning):
    logging.warning(f'Attenzione: {warning}')

def info(info):
    logging.info(f" {info}")

def debug(debug):
    logging.debug(f'Debug: {debug}')



# se il file 'logs/hdm.log' non esiste, lo creo
if not os.path.exists('logs'):
    os.makedirs('logs')



# start del moodulo
if __name__ == '__main__':
    debug(f"Carico: {__name__}")
