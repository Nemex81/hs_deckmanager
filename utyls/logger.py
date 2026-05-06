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
from utyls.runtime_paths import get_log_file

# Configurazione del logging

#logging.basicConfig(
    #filename='/logs/hdm.log',                             # File di log
    #level=logging.DEBUG,                                        # Livello di log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    #format='%(asctime)s - %(levelname)s - %(message)s',             # Formato del log
    #datefmt='%Y-%m-%d %H:%M:%S'                                     # Formato della data
#)



# Configurazione del logging
DEFAULT_LOG_FILE = get_log_file("hdm.log")
handler = RotatingFileHandler(DEFAULT_LOG_FILE, maxBytes=10024 * 10024, backupCount=10, encoding='utf-8')
logging.basicConfig(handlers=[handler], level=logging.DEBUG)



def setup_logging(log_file=None, console_output=False):
    """ 
        Configura il logging dell'applicazione.

        Argomenti:
                    log_file (str): Percorso del file di log.
                    console_output (bool): Specifica se abilitare l'output su console.

            Note:
                    - Questa funzione deve essere chiamata all'inizio del programma per configurare il logging.
    """

    if log_file is None:
        log_file = DEFAULT_LOG_FILE
    elif not os.path.isabs(log_file):
        log_file = get_log_file(os.path.basename(log_file))

    handlers = [logging.FileHandler(log_file)]
    if console_output:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        handlers=handlers,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True
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



# start del moodulo
if __name__ == '__main__':
    debug(f"Carico: {__name__}")
