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
build_output_dir = os.path.join(PROJECT_DIR, "build")

BUILD_EXCLUDES = [
    "archivio",
    "gtts",
    "pytest",
    "_pytest",
    "py",
    "pluggy",
    "pip",
    "setuptools",
    "pkg_resources",
    "distutils",
    "mypy",
    "mypy_extensions",
    "unittest",
    "doctest",
    "IPython",
    "ipython",
    "ipykernel",
    "numpy",
    "numpy.distutils",
    "numpy.testing",
    "greenlet.tests",
    "sqlalchemy.testing",
    "sqlalchemy.ext.mypy",
    "sqlalchemy.dialects.sqlite.aiosqlite",
    "sqlalchemy.dialects.sqlite.pysqlcipher",
    "sqlalchemy.dialects.mysql",
    "sqlalchemy.dialects.postgresql",
    "sqlalchemy.dialects.oracle",
    "sqlalchemy.dialects.mssql",
    "sqlalchemy.dialects.firebird",
    "sqlalchemy.dialects.asyncpg",
    "sqlalchemy.dialects.asyncmy",
    "PyQt5",
    "PyQt6",
    "PySide2",
    "PySide6",
    "qtpy",
    "accessible_output2.outputs.voiceover",
    "accessible_output2.outputs.e_speak",
    "accessible_output2.outputs.speech_dispatcher",
    "pysqlcipher3",
    "sqlcipher3",
]


class BuildExeCommand(BuildExe):
    """Esegue il build e rimuove porzioni di wx non usate dal progetto."""

    WX_LIB_KEEP_FILES = {"__init__.pyc", "newevent.pyc"}
    WX_TOP_LEVEL_REMOVALS = [
        "aui",
        "dataview",
        "gizmos",
        "glcanvas",
        "html",
        "html2",
        "media",
        "propgrid",
        "ribbon",
        "richtext",
        "stc",
        "xml",
        "xrc",
    ]
    WX_TOP_LEVEL_EXTRA_REMOVALS = [
        "WebView2Loader.dll",
        "wxbase32u_xml_vc140_x64.dll",
        "wxmsw32u_aui_vc140_x64.dll",
        "wxmsw32u_gl_vc140_x64.dll",
        "wxmsw32u_html_vc140_x64.dll",
        "wxmsw32u_media_vc140_x64.dll",
        "wxmsw32u_propgrid_vc140_x64.dll",
        "wxmsw32u_ribbon_vc140_x64.dll",
        "wxmsw32u_richtext_vc140_x64.dll",
        "wxmsw32u_stc_vc140_x64.dll",
        "wxmsw32u_webview_vc140_x64.dll",
        "wxmsw32u_xrc_vc140_x64.dll",
    ]

    def run(self):
        super().run()
        self._prune_wx_bundle()

    def _prune_wx_bundle(self):
        build_dir = self.build_exe or build_output_dir
        wx_dir = os.path.join(build_dir, "lib", "wx")
        if not os.path.isdir(wx_dir):
            return

        self._prune_wx_locales(wx_dir)
        self._prune_wx_lib(wx_dir)
        self._prune_wx_top_level_modules(wx_dir)
        self._remove_tree(os.path.join(wx_dir, "py"))
        self._remove_tree(os.path.join(wx_dir, "tools"))

    def _prune_wx_lib(self, wx_dir: str) -> None:
        lib_dir = os.path.join(wx_dir, "lib")
        if not os.path.isdir(lib_dir):
            return

        for entry in os.listdir(lib_dir):
            entry_path = os.path.join(lib_dir, entry)
            if entry in self.WX_LIB_KEEP_FILES:
                continue

            self._remove_path(entry_path)

    def _prune_wx_top_level_modules(self, wx_dir: str) -> None:
        removable_paths: list[str] = []
        for module_name in self.WX_TOP_LEVEL_REMOVALS:
            removable_paths.extend([
                os.path.join(wx_dir, f"{module_name}.pyc"),
                os.path.join(wx_dir, f"{module_name}.pyi"),
                os.path.join(wx_dir, f"_{module_name}.cp311-win_amd64.pyd"),
                os.path.join(wx_dir, module_name),
            ])

        for path in removable_paths:
            self._remove_path(path)

        for filename in self.WX_TOP_LEVEL_EXTRA_REMOVALS:
            self._remove_path(os.path.join(wx_dir, filename))

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

    def _remove_path(self, path: str) -> None:
        if os.path.isdir(path):
            shutil.rmtree(path)
            return

        if os.path.isfile(path):
            os.remove(path)



# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {
    "optimize": 1,
    "build_exe": build_output_dir,
    "packages": ["greenlet"],
    "includes": [
        "sqlalchemy.dialects.sqlite",
        "accessible_output2.outputs.auto",
        "wx.lib.newevent",
    ],
    "excludes": BUILD_EXCLUDES,
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