# test_window_factory.py

import wx
import pytest
from scr.views.builder.dependency_container import DependencyContainer
from scr.views.builder.window_factory import WindowFactory
from scr.views.main_views import HearthstoneAppFrame

def test_window_factory():
    container = DependencyContainer()
    factory = WindowFactory(container)

    # Registra le dipendenze necessarie
    from scr.views.builder.color_system import ColorManager
    from scr.views.builder.focus_handler import FocusHandler
    container.register("color_manager", lambda: ColorManager(theme="DARK"))
    container.register("focus_handler", lambda: FocusHandler())

    # Crea una finestra
    main_window = factory.create_window(HearthstoneAppFrame)
    assert isinstance(main_window, HearthstoneAppFrame)
    assert hasattr(main_window, "color_manager")
    assert hasattr(main_window, "focus_handler")
    assert main_window.color_manager.theme == "DARK"
