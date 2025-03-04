"""
    dependency_container.py

    Modulo per la gestione centralizzata delle dipendenze.

    path:
        scr/views/builder/dependency_container.py

"""



class DependencyContainer:
    """
    Classe per la gestione centralizzata delle dipendenze.
    Permette di registrare e risolvere componenti in modo dinamico.
    """

    def __init__(self):
        self._dependencies = {}  # Dizionario per memorizzare le dipendenze

    def register(self, key, factory):
        """
        Registra una dipendenza nel container.

        :param key: Chiave univoca per identificare la dipendenza.
        :param factory: Funzione o classe che crea l'istanza della dipendenza.
        """
        if key in self._dependencies:
            raise ValueError(f"La dipendenza con chiave '{key}' è già registrata.")
        self._dependencies[key] = factory

    def resolve(self, key):
        """
        Risolve una dipendenza registrata.

        :param key: Chiave della dipendenza da risolvere.
        :return: Istanza della dipendenza.
        """
        if key not in self._dependencies:
            raise ValueError(f"La dipendenza con chiave '{key}' non è registrata.")
        return self._dependencies[key]()

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
