"""
    Modulo per la creazione dell'eseguibile
"""



#import
import os
import shutil
import sys
from cx_Freeze import setup, Executable
from cx_Freeze.command.build_exe import build_exe as BuildExe


PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

if sys.platform == "win32":
    build_output_dir = os.path.join(
        os.environ.get("LOCALAPPDATA", PROJECT_DIR),
        "hs_deckmanager",
        "build",
    )
else:
    build_output_dir = os.path.join(PROJECT_DIR, "build")


class BuildExeCommand(BuildExe):
    """Esegue il build e rimuove porzioni di wx non usate dal progetto."""

    def run(self):
        super().run()
        self._prune_wx_bundle()

    def _prune_wx_bundle(self):
        build_dir = self.build_exe or build_output_dir
        wx_dir = os.path.join(build_dir, "lib", "wx")
        if not os.path.isdir(wx_dir):
            return

        self._prune_wx_locales(wx_dir)
        self._remove_tree(os.path.join(wx_dir, "py"))
        self._remove_tree(os.path.join(wx_dir, "tools"))

    def _prune_wx_locales(self, wx_dir: str) -> None:
        locale_dir = os.path.join(wx_dir, "locale")
        if not os.path.isdir(locale_dir):
            return

        allowed_locales = {"it", "en", "en_GB", "en_US"}
        for entry in os.listdir(locale_dir):
            entry_path = os.path.join(locale_dir, entry)
            if not os.path.isdir(entry_path):
                continue

            if entry in allowed_locales or entry.startswith("en"):
                continue

            self._remove_tree(entry_path)

    def _remove_tree(self, path: str) -> None:
        if os.path.isdir(path):
            shutil.rmtree(path)



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
        "greenlet",
    ],
    "includes": ["sqlalchemy.dialects.sqlite"],
    "excludes": [
        "archivio",
        "gtts",
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
    cmdclass={"build_exe": BuildExeCommand},
    executables=[Executable("main.py", base=base, target_name="hs_deckmanager.exe")]
)