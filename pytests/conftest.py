"""
Pytest configuration and fixtures
"""

import sys
from unittest.mock import MagicMock

# Mock wx module if not available
if 'wx' not in sys.modules:
    sys.modules['wx'] = MagicMock()

# Mock gtts module if not available
if 'gtts' not in sys.modules:
    sys.modules['gtts'] = MagicMock()
    sys.modules['gtts'].gTTS = MagicMock()
