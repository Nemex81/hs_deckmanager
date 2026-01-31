"""
        Modulo per la gestione dei log del gioco

        **Path:**
            ```
            utyls/logger.py
            ```

    ---

        **Versione:** 0.6
        **Data:** 31 gennaio 2026
        **Autore:** [Nemex]

    ---
            
"""

# lib
from logging.handlers import RotatingFileHandler
import logging
import os
from pathlib import Path

# Import centralized configuration
try:
    from scr.user_settings import LOGS_DIR, DEBUG_MODE
except ImportError:
    # Fallback if user_settings is not available
    LOGS_DIR = Path(__file__).parent.parent / "logs"
    DEBUG_MODE = False

# Ensure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Flag to prevent multiple initializations
_logging_initialized = False


def setup_logging(log_file=None, console_output=False):
    """ 
        Configura il logging dell'applicazione.

        Argomenti:
                    log_file (str|Path): Percorso del file di log. Se None, usa LOGS_DIR/hdm.log.
                    console_output (bool): Specifica se abilitare l'output su console.

            Note:
                    - Questa funzione deve essere chiamata all'inizio del programma per configurare il logging.
                    - Può essere chiamata solo una volta; chiamate successive saranno ignorate.
    """
    global _logging_initialized
    
    if _logging_initialized:
        logging.debug("Logging già inizializzato, ignoro la chiamata a setup_logging.")
        return
    
    if log_file is None:
        log_file = LOGS_DIR / "hdm.log"
    else:
        log_file = Path(log_file)
    
    # Ensure parent directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    handlers = [
        RotatingFileHandler(
            log_file, 
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=10, 
            encoding='utf-8'
        )
    ]
    
    if console_output:
        handlers.append(logging.StreamHandler())
    
    logging.basicConfig(
        handlers=handlers,
        level=logging.DEBUG if DEBUG_MODE else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    _logging_initialized = True
    logging.info("Sistema di logging inizializzato.")



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


# Initialize logging when module is imported (only if not already initialized)
if not _logging_initialized:
    setup_logging()


# start del modulo
if __name__ == '__main__':
    debug(f"Carico: {__name__}")
