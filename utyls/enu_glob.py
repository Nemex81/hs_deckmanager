"""
	Modulo per la gestione delle enumerazioni globali

	path:
		utyls/enu_glob.py
		
	Descrizione:
	Contiene le enumerazioni globali utilizzate nell'applicazione.

"""




from enum import Enum
#import pdb

# colori rgb
from enum import Enum

class Colors(Enum):
    BLACK = 'black'
    WHITE = 'white'
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    YELLOW = 'yellow'

# classi per la gestione degli stati del personaggio
class Position(Enum):
    REGLINING = 0
    SITTING = 1
    STANDING = 2
    FLOATING = 3


class ChStatus(Enum):
    CREAZIONE = -2
    MORTO = -1
    INATTIVO = 0
    FERMO = 1
    MOVIMENTO = 2



#@@@# Start del modulo
if __name__ != "__main__":
    print("Carico: %s" % __name__)
