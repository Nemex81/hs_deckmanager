"""
    Modulo per la creazione dell'eseguibile
"""



#import
import sys, os, platform
from cx_Freeze import setup, Executable



# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {
    "optimize": 1,
    "packages": ["os"],
    "excludes": ["archivio"],
    "include_files": ["img", "README.md"],
}

base="Win32GUI"
#base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Heartstones Decks Manager",
    version="0.9.6",
    description="gestore di mazzi per heartstones accessibile agli screen reader!",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)]
)