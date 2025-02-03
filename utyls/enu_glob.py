"""
    Modulo per la gestione delle enumerazioni globali

    path:
        utyls/enu_glob.py
        
    Descrizione:
    Contiene le enumerazioni globali utilizzate nell'applicazione.

"""




from enum import Enum
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import  Column, Integer, String, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from scr.db import Base, session, Card, Deck, DeckCard
# from utyls.logger import Logger
#import pdb

# colori rgb
class EnuColors(Enum):
    BLACK = 'black'
    WHITE = 'white'
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    YELLOW = 'yellow'

class ENUCARD(Enum):
    """ info base obblicagorie delel carte pe rl'interazione con il db. """

    Name = "name"
    ManaCost = "mana_cost"
    CardType = "card_type"

class EnuExtraCard(Enum):
    """ info extra delle carte pe rl'interazione con il db. """

    Name = "name"
    CLASS = "class"
    ManaCost = "mana_cost"
    CardType = "card_type"
    CardSubType = "card_subtype"
    Rarity = "rarity"
    Expansion = "expansion"
    Attack = "attack"
    Health = "health"
    Durability = "durability"


class EnuCardType(Enum):
    """ tipi di carte """

    CREATURA = "Creatura"
    MAGIA = "Magia"
    LUOGO = "Luogo"
    ARMA = "Arma"
    EROE = "Eroe"

class EnuSpellSubType(Enum):
    """ sottotipi delle carte Magia """

    ARCANO = "Arcano"
    FUOCO = "Fuoco"
    GELO = "Gelo"
    NATURA = "Natura"
    OMBRA = "Ombra"
    SACRO = "Sacra"
    FISICO = "Fisico"
    VENTO = "Vento"
    VENENO = "Veleno"
    SANGUE = "Sangue"
    EMPIETA = "Empietà"
    DIVINO = "Divino"
    FULMINE = "Fulmine"
    ACQUA = "Acqua"
    TERRA = "Terra"
    LUCE = "Luce"
    ANIMA = "Anima"
    VITA = "Vita"
    MORTE = "Morte"
    DEMONIACO = "Demoniaco"
    ANGELICO = "Angelico"

class EnuPetSubType(Enum):
    """ sottotipi delle carte Creatura """

    DRAGO = "Drago"
    FANTASMA = "Fantasma"
    BESTIA = "Bestia"
    ELEMENTALE = "Elementale"
    SPIRITO = "Spirito"
    TOTEM = "Totem"
    MECCANICO = "Meccanico"
    PIRATA = "Pirata"
    MURLOC = "Murloc"
    DRAGOIDE = "Dragoide"
    DEMONE = "Demone"
    ELFO = "Elfo"
    ORCO = "Orco"
    GNOMO = "Gnomo"
    UMANO = "Umano"
    NON_MORTO = "Non Morto"
    TROLL = "Troll"
    GOBLIN = "Goblin"
    NANO = "Nano"


class EnuHero(Enum):
    """ eroi delle carte """

    ALLCLASS = "Tutte le classi"
    CACCIATORE = "Cacciatore"
    DRUIDO = "Druido"
    GUERRIERO = "Guerriero"
    KNIGHTDEATH = "cavaliere della morte"
    LADRO = "Ladro"
    MAGO = "Mago"
    PALADINO = "Paladino"
    SACERDOTE = "Sacerdote"
    SCIAMANO = "Sciamano"
    SHADOHUNTER = "Cacciatore di demoni"
    STREGONE = "Stregone"

class EnuRarity(Enum):
    """ rarità delle carte """

    COMUNE = "Comune"
    RARA = "Rara"
    EPICA = "Epica"
    LEGGENDARIA = "Leggendaria"

    
class EnuExpansion(Enum):
    """ espansioni delle carte """

    # Set di base: la collezione iniziale con cui i nuovi giocatori partono.
    SET_BASE = "Set Principale"

    # Espansioni classiche (prime espansioni rilasciate)
    MALEDIZIONE_NAXXRAMAS = "La Maledizione di Naxxramas"          # Avventura/espansione che introduce nuove meccaniche come il deathrattle
    GOBLIN_VS_GNOMI = "Goblin vs Gnomi"                             # Espansione incentrata sul contrasto tra goblin e gnomi
    BLACKROCK_MOUNTAIN = "Blackrock Mountain"                       # Avventura ambientata in una montagna infestata da draghi e boss epici
    GRAN_TOURNAMENT = "Il Grande Torneo"                            # Espansione a tema torneo con meccaniche come il joust
    LEGA_DEGLI_ESPLORATORI = "La Lega degli Esploratori"             # Avventura con meccanica Discover e ambientazione ispirata alle rovine
    SUSSURRI_DEGLI_DEI_ANTICHI = "Sussurri degli Dei Antichi"        # Espansione che porta in gioco poteri oscuri e riferimenti agli antichi dei
    UNA_NOTTE_A_KARAZHAN = "Una Notte a Karazhan"                    # Avventura ambientata nell’iconica torre di Karazhan
    QUARTIERI_MALFAMATI_DI_GADGETZAN = "I Quartieri Malfamati di Gadgetzan"   
    VIAGGIO_A_UNGORO = "Viaggio a Un'Goro"                           # Espansione che esplora un ambiente preistorico e selvaggio
    CAVALIERI_DEL_TRONO_GELATO = "Cavalieri del Trono Gelato"        # Espansione a tema freddo e misterioso con un trono di ghiaccio
    KOBOLD_E_CATACOMBE = "Kobold e Catacombe"                       # Espansione che richiama atmosfere oscure e fantasy
    IL_BOSCO_STREGATO = "Il Bosco Stregato"                         # Espansione che evoca un ambiente magico e inquietante
    PROGETTO_BOOMSDAY = "Il Progetto Boomsday"                       # Espansione con tema futuristico e tecnologico
    RUMBLE_DI_RASTAKHAN = "Il Rumble di Rastakhan"                   # Espansione ispirata alle atmosfere esotiche e al combattimento in arena
    L_ASCESA_DELLE_OMBRE = "L'Ascesa delle Ombre"                     # Espansione che introduce tematiche oscure e minacciose
    I_SALVATORI_DI_ULDUM = "I Salvatori di Uldum"                   # Espansione ambientata in un’ambientazione esotica e misteriosa
    LA_DISCESA_DEI_DRAGHI = "La Discesa dei Draghi"                   # Espansione incentrata sui draghi e le loro forze
    LE_CENERI_DI_OUTLAND = "Le Ceneri di Outland"                     # Espansione che porta il giocatore in un mondo in rovina
    ACCADEMIA_SCHOLOMANCE = "L'Accademia Scholomance"                # Espansione con ambientazione gotica e scolastica
    DARKMOON_FAIRE = "La Follia alla Fiera di Darkmoon"             # Espansione ispirata al famoso evento Darkmoon, con meccaniche di corruzione

    # Espansioni e Core più recenti
    CORE_2021 = "Core 2021"                                           # Nuovo set base annuale introdotto nel 2021
    FORGED_IN_THE_BARRENS = "Forgiato nei Barrens"                   # Espansione che esplora i paesaggi aridi dei Barrens
    UNITED_IN_STORMWIND = "Uniti a Stormwind"                         # Espansione a tema urbano e regale, ambientata a Stormwind
    FRACTURED_IN_ALTERAC_VALLEY = "Fratturato nella Valle d'Alterac"   # Espansione che porta battaglie epiche nella valle di Alterac
    CORE_2022 = "Core 2022"                                           # Nuovo set base annuale per il 2022
    VOYAGE_TO_THE_SUNKEN_CITY = "Viaggio nella Città Sommersa"         # Espansione con ambientazione subacquea e nuove meccaniche
    ASSASSINIO_AL_CASTELLO_DI_NATHRIA = "Assassinio al Castello di Nathria"  # Espansione che fonde mistero e ambientazioni gotiche
    MARCH_OF_THE_LICH_KING = "Marcia del Re dei Lich"                # Espansione dedicata al tema dei Re dei Lich
    CORE_2023 = "Core 2023"                                           # Nuovo set base annuale per il 2023
    FESTIVAL_OF_LEGENDS = "Festival delle Leggende"                   # Espansione festiva con nuove carte e temi epici
    TITANS = "Titani"                                                 # Espansione che evoca il potere dei titani
    SHOWDOWN_IN_THE_BADLANDS = "Showdown nelle Terre Malfamate"      # Espansione che porta scontri intensi in ambientazioni desolate
    CORE_2024 = "Core 2024"                                           # Nuovo set base annuale per il 2024
    WHIZBANGS_WORKSHOP = "La Bottega di Whizbang"                    # Espansione che unisce creatività e tecnologia in un laboratorio unico
    PERILS_IN_PARADISE = "Pericoli nel Paradiso"                      # Espansione che mescola bellezze paradisiache e insidie
    THE_GREAT_DARK_BEYOND = "La Grande Oscurità"                 # Espansione che apre le porte a misteri e orrori oltre il conosciuto



#@@@# Start del modulo
if __name__ != "__main__":
    print("Carico: %s" % __name__)
