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
import logging

# Configurazione del logging

#logging.basicConfig(
    #filename='/logs/hdm.log',                             # File di log
    #level=logging.DEBUG,                                        # Livello di log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    #format='%(asctime)s - %(levelname)s - %(message)s',             # Formato del log
    #datefmt='%Y-%m-%d %H:%M:%S'                                     # Formato della data
#)

handler = RotatingFileHandler('logs/hdm.log', maxBytes=10024 * 10024, backupCount=10)
logging.basicConfig(handlers=[handler], level=logging.DEBUG)



def setup_logging(log_file='logs/hdm.log', console_output=False):
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



# start del moodulo
if __name__ == '__main__':
    debug(f"Carico: {__name__}")
