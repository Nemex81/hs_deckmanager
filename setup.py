"""
    Modulo per la creazione dell'eseguibile
"""



#import
import os
import sys
from cx_Freeze import setup, Executable


PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

if sys.platform == "win32":
    build_output_dir = os.path.join(
        os.environ.get("LOCALAPPDATA", PROJECT_DIR),
        "hs_deckmanager",
        "build",
    )
else:
    build_output_dir = os.path.join(PROJECT_DIR, "build")



# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {
    "optimize": 1,
    "build_exe": build_output_dir,
    "packages": [
        "sqlalchemy",
        "wx",
        "accessible_output2",
        "pyperclip",
        "gtts",
        "greenlet",
    ],
    "includes": ["sqlalchemy.dialects.sqlite"],
    "excludes": [
        "archivio",
        "PyQt5",
        "pytest",
        "_pytest",
        "py",
        "pluggy",
        "mypy",
        "mypy_extensions",
        "unittest",
        "doctest",
        "IPython",
        "ipython",
        "ipykernel",
    ],
    "include_files": ["img", "README.md"],
    "zip_exclude_packages": ["wx", "accessible_output2"],
    "include_msvcr": True,
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Heartstones Decks Manager",
    version="0.9.6",
    description="gestore di mazzi per heartstones accessibile agli screen reader!",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, target_name="hs_deckmanager.exe")]
)