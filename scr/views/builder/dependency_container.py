"""
    dependency_container.py

    Modulo per la gestione centralizzata delle dipendenze.

    path:
        scr/views/builder/dependency_container.py

"""

# Lib
from utyls import logger as log
from threading import Lock


class DependencyContainer:
    """
    Classe per la gestione centralizzata delle dipendenze.
    Permette di registrare e risolvere componenti in modo dinamico.
    """

    def __init__(self):
        self._dependencies = {}                 # Dizionario per memorizzare le dipendenze
        self._singleton_instances = {}          # Istanze delle dipendenze singleton
        self._resolving_stack = set()           # Per evitare dipendenze circolari
        self._lock = Lock()                     # Per thread-safety


    def register(self, key, factory, singleton=False):
        """
        Registra una dipendenza nel container.

        :param key: Chiave univoca per identificare la dipendenza.
        :param factory: Funzione o classe che crea l'istanza della dipendenza.
        """
        if key in self._dependencies:
            raise ValueError(f"La dipendenza con chiave '{key}' è già registrata.")
        self._dependencies[key] = factory

    def resolve(self, key, *args, **kwargs):
        """
        Risolve una dipendenza registrata.

        :param key: Chiave della dipendenza da risolvere.
        :return: Istanza della dipendenza.
        """
        if key not in self._dependencies:
            raise ValueError(f"La dipendenza con chiave '{key}' non è registrata.")
        return self._dependencies[key]()

    def resolve_optional(self, key, *args, **kwargs):
        """
        Risolve una dipendenza registrata in modo opzionale.
        """
        with self._lock:  # Thread-safety
            if key not in self._dependencies:
                return None
            return self.resolve(key, *args, **kwargs)

    def has(self, key):
        """
        Verifica se una dipendenza è registrata.

        :param key: Chiave della dipendenza da verificare.
        :return: True se la dipendenza è registrata, False altrimenti.
        """
        return key in self._dependencies




#@@@# Start del modulo
if __name__ != "__main__":
    log.debug(f"Carico: {__name__}")
