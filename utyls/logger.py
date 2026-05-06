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
from pathlib import Path

# Import base directory from user_settings if available, otherwise use fallback
try:
    from scr.user_settings import BASE_DIR, LOGS_DIR
except ImportError:
    # Fallback if user_settings isn't available yet
    BASE_DIR = Path(__file__).parent.parent
    LOGS_DIR = BASE_DIR / "logs"

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

# Configurazione del logging - single setup
LOG_FILE = LOGS_DIR / "hdm.log"
_logging_configured = False

def setup_logging(log_file=None, console_output=False):
    """ 
        Configura il logging dell'applicazione.

        Argomenti:
                    log_file (str): Percorso del file di log. Default usa LOGS_DIR/hdm.log
                    console_output (bool): Specifica se abilitare l'output su console.

            Note:
                    - Questa funzione deve essere chiamata all'inizio del programma per configurare il logging.
    """
    global _logging_configured
    
    if _logging_configured:
        return  # Already configured, skip
    
    if log_file is None:
        log_file = LOG_FILE
    
    # Ensure parent directory exists
    log_path = Path(log_file)
    os.makedirs(log_path.parent, exist_ok=True)
    
    handlers = [RotatingFileHandler(log_file, maxBytes=10024 * 10024, backupCount=10, encoding='utf-8')]
    if console_output:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        handlers=handlers,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True  # Force reconfiguration if needed
    )
    
    _logging_configured = True


# Initialize logging with default settings
setup_logging()



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
