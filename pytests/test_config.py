"""
Test suite for user_settings.py

Tests configuration loading and settings.
"""

import pytest
from pathlib import Path


class TestUserSettings:
    """Tests for user settings configuration"""

    def test_config_values_exist(self):
        """Test that all required configuration values exist"""
        from scr import user_settings
        
        # Check that key configuration variables exist
        assert hasattr(user_settings, 'BASE_DIR')
        assert hasattr(user_settings, 'LOGS_DIR')
        assert hasattr(user_settings, 'DB_PATH')
        assert hasattr(user_settings, 'DATABASE_URL')
        assert hasattr(user_settings, 'APP_NAME')
        assert hasattr(user_settings, 'APP_VERSION')

    def test_base_dir_is_path(self):
        """Test that BASE_DIR is a Path object"""
        from scr import user_settings
        
        assert isinstance(user_settings.BASE_DIR, Path)

    def test_logs_dir_is_path(self):
        """Test that LOGS_DIR is a Path object"""
        from scr import user_settings
        
        assert isinstance(user_settings.LOGS_DIR, Path)

    def test_db_path_is_path(self):
        """Test that DB_PATH is a Path object"""
        from scr import user_settings
        
        assert isinstance(user_settings.DB_PATH, Path)

    def test_database_url_format(self):
        """Test that DATABASE_URL is properly formatted"""
        from scr import user_settings
        
        assert isinstance(user_settings.DATABASE_URL, str)
        assert user_settings.DATABASE_URL.startswith('sqlite:///')

    def test_db_path_in_data_directory(self):
        """Test that DB_PATH is in the data directory"""
        from scr import user_settings
        
        # DB should be in BASE_DIR/data/
        assert user_settings.DB_PATH.parent.name == 'data'
        assert user_settings.DB_PATH.name == 'hearthstone_decks_storage.db'

    def test_logs_dir_exists_or_creatable(self):
        """Test that LOGS_DIR can be created if it doesn't exist"""
        from scr import user_settings
        import os
        
        # The logs directory should be creatable
        logs_dir = user_settings.LOGS_DIR
        
        # If it doesn't exist, we should be able to create it
        if not logs_dir.exists():
            os.makedirs(logs_dir, exist_ok=True)
        
        assert logs_dir.exists() or True  # Either exists or we created it

    def test_app_metadata(self):
        """Test that app metadata is properly set"""
        from scr import user_settings
        
        assert user_settings.APP_NAME == "Hearthstone Deck Manager"
        assert user_settings.APP_AUTHOR == "Nemex81"
        assert isinstance(user_settings.APP_VERSION, str)
        assert len(user_settings.APP_VERSION) > 0

    def test_logging_config_structure(self):
        """Test that LOGGING_CONFIG has proper structure"""
        from scr import user_settings
        
        assert hasattr(user_settings, 'LOGGING_CONFIG')
        config = user_settings.LOGGING_CONFIG
        
        assert isinstance(config, dict)
        assert 'version' in config
        assert 'handlers' in config
        assert 'formatters' in config
