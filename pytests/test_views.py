# tests/test_views.py

# lib
import wx
from scr.views.builder.view_components import CustomButton
from scr.views.builder.view_factory import ViewFactory
from scr.views.builder.dependency_container import DependencyContainer
from scr.views.builder.color_system import ColorManager
from scr.views.builder.focus_handler import FocusHandler
from utyls import enu_glob as eg
from utyls import logger as log



vc = ViewFactory()


def test_custom_button_creation():
    parent = wx.Frame(None)
    container = DependencyContainer()
    container.register("color_manager", lambda: ColorManager())
    container.register("focus_handler", lambda: FocusHandler())

    button = vc.create_button(
        parent=parent,
        label="Test",
        size=(100, 50),
        font_size=12,
        event_handler=lambda e: None,
        container=container
    )
    assert isinstance(button, CustomButton)
    assert button.GetLabel() == "Test"
    assert button.GetSize() == (100, 50)
    assert button.GetFont().GetPointSize() == 12
    assert button.GetEventHandler() is not None
