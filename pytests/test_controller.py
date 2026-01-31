"""
Test suite for controller.py

Tests the current_window property to ensure it doesn't recurse infinitely.
"""

import pytest
from unittest.mock import Mock, MagicMock


class TestDefaultController:
    """Tests for DefaultController class"""

    def test_current_window_returns_window(self):
        """Test that current_window property returns the window from win_controller"""
        from scr.controller import DefaultController
        
        # Create a mock container
        mock_container = Mock()
        mock_win_controller = Mock()
        mock_window = Mock()
        
        # Setup the mock
        mock_win_controller.get_current_window.return_value = mock_window
        mock_container.resolve.side_effect = lambda name: {
            'db_manager': Mock(),
            'vocalizer': Mock(),
            'win_controller': mock_win_controller
        }[name]
        
        # Create controller instance
        controller = DefaultController(container=mock_container)
        
        # Test that current_window returns the window
        result = controller.current_window
        assert result == mock_window
        mock_win_controller.get_current_window.assert_called_once()

    def test_current_window_returns_none_when_no_window(self):
        """Test that current_window property returns None when no window exists"""
        from scr.controller import DefaultController
        
        # Create a mock container
        mock_container = Mock()
        mock_win_controller = Mock()
        
        # Setup the mock to return None
        mock_win_controller.get_current_window.return_value = None
        mock_container.resolve.side_effect = lambda name: {
            'db_manager': Mock(),
            'vocalizer': Mock(),
            'win_controller': mock_win_controller
        }[name]
        
        # Create controller instance
        controller = DefaultController(container=mock_container)
        
        # Test that current_window returns None
        result = controller.current_window
        assert result is None
        mock_win_controller.get_current_window.assert_called_once()

    def test_current_window_no_infinite_recursion(self):
        """Test that current_window property does not cause infinite recursion"""
        from scr.controller import DefaultController
        
        # Create a mock container
        mock_container = Mock()
        mock_win_controller = Mock()
        mock_window = Mock()
        
        # Setup the mock
        mock_win_controller.get_current_window.return_value = mock_window
        mock_container.resolve.side_effect = lambda name: {
            'db_manager': Mock(),
            'vocalizer': Mock(),
            'win_controller': mock_win_controller
        }[name]
        
        # Create controller instance
        controller = DefaultController(container=mock_container)
        
        # Multiple calls should not cause recursion
        result1 = controller.current_window
        result2 = controller.current_window
        result3 = controller.current_window
        
        assert result1 == mock_window
        assert result2 == mock_window
        assert result3 == mock_window
        # Should be called 3 times, not infinitely
        assert mock_win_controller.get_current_window.call_count == 3
