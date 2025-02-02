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
