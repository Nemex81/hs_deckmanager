---
initialized: true
scf_protected: true
scf_file_role: "config"
scf_merge_priority: 10
scf_merge_strategy: "user_protected"
active_plugins: []
scf_version: "1.2.0"
framework_edit_mode: false
scf_owner: "spark-base"
spark: true
framework_version: ""

project_name: "Hearthstone Deck Manager"
description: "Applicazione desktop Python per creare, salvare e gestire mazzi di Hearthstone. Usa SQLite/SQLAlchemy, interfaccia wxPython e mira all'accessibilità per screen reader."
primary_language: "Python"
secondary_languages: []
ui_framework: "wxPython"
test_runner: "pytest"
build_system: "cx_Freeze (setup.py)"
author:
	name: "Luca Profita (Nemex81)"
	email: "nemex1981@gmail.com"
version: "0.9.6"

---

# Project Profile — Generated

Questa versione di `project-profile.md` è stata generata automaticamente da Agent-Welcome a partire dalla documentazione del repository (`README.md`) e dalla configurazione di build (`setup.py`).

Campi principali inseriti:

- `project_name`: nome del progetto ricavato da `README.md`.
- `description`: descrizione sintetica estratta da `README.md`.
- `primary_language`: rilevato come `Python` (presenza di `main.py`, package `scr/` e `setup.py`).
- `ui_framework`: `wxPython` (indicazione esplicita in `README.md` e dipendenza in `requirements`).
- `test_runner`: `pytest` (cartella `pytests/` presente nel repository).
- `build_system`: `cx_Freeze` (definito in `setup.py`).

Se desideri modificare uno di questi campi, rispondi con "modifica <campo>" (es. `modifica description`).

Agent-Welcome: file generato — procedere al commit richiesto dall'utente.
