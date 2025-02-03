"""
        Modulo per la gestione dei log del gioco

        **Path:**
            ```
                scr/logger.py
            ```

    ---

        **Versione:** 0.2
        **Data:** 11 ottobre 2024  
        **Autore:** [Nemex]

    ---
            
"""

import logging

# Configurazione del logging
logging.basicConfig(
    filename='hearthstone_manager.log',  # File di log
    level=logging.INFO,                  # Livello di log
    format='%(asctime)s - %(levelname)s - %(message)s',  # Formato del log
    datefmt='%Y-%m-%d %H:%M:%S'         # Formato della data
)



def setup_logging(log_file='hearthstone_manager.log', console_output=False):
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

def log_app_start():
    logging.info('Applicazione avviata.')

def log_app_end():
    logging.info('Applicazione terminata.')

def log_game_start():
    logging.info('La partita è iniziata.')

def log_game_end():
    logging.info('La partita è terminata.')

def log_player_action(player, action, details):
    logging.info(f'Azione del giocatore {player}: {action} - Dettagli: {details}')

def log_game_error(error):
    logging.error(f'Errore: {error}')

def log_game_warning(warning):
    logging.warning(f'Attenzione: {warning}')

def log_game_info(info):
    logging.info(f" {info}")

def log_game_debug(debug):
    logging.debug(f'Debug: {debug}')



# start del moodulo
if __name__ == '__main__':
    print("Carico: %s" % __file__)
