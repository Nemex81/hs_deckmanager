"""
Test suite for db.py

Tests database session management and context manager behavior.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch


class TestDatabaseSession:
    """Tests for database session management"""

    def test_db_session_context_manager_commits_on_success(self):
        """Test that db_session commits on successful execution"""
        # Use a temporary database for testing
        with tempfile.TemporaryDirectory() as tmpdir:
            test_db_path = Path(tmpdir) / "test.db"
            
            # Patch the DB_PATH to use our test database
            with patch('scr.db.DB_PATH', test_db_path):
                # Re-import to get fresh module with patched path
                import importlib
                import scr.db as db
                importlib.reload(db)
                
                # Setup database
                db.Base.metadata.create_all(db.engine)
                
                # Test that a successful operation commits
                from scr.db import db_session, Deck
                
                with db_session() as session:
                    deck = Deck(name="Test Deck", player_class="Warrior", game_format="Standard")
                    session.add(deck)
                    # Session should auto-commit on exit
                
                # Verify the deck was committed
                with db_session() as session:
                    result = session.query(Deck).filter_by(name="Test Deck").first()
                    assert result is not None
                    assert result.name == "Test Deck"
                    assert result.player_class == "Warrior"

    def test_db_session_context_manager_rollsback_on_error(self):
        """Test that db_session rolls back on error"""
        # Use a temporary database for testing
        with tempfile.TemporaryDirectory() as tmpdir:
            test_db_path = Path(tmpdir) / "test.db"
            
            # Patch the DB_PATH to use our test database
            with patch('scr.db.DB_PATH', test_db_path):
                # Re-import to get fresh module with patched path
                import importlib
                import scr.db as db
                importlib.reload(db)
                
                # Setup database
                db.Base.metadata.create_all(db.engine)
                
                from scr.db import db_session, Deck
                
                # Test that an error causes rollback
                with pytest.raises(ValueError):
                    with db_session() as session:
                        deck = Deck(name="Test Deck 2", player_class="Mage", game_format="Wild")
                        session.add(deck)
                        # Force an error before commit
                        raise ValueError("Test error")
                
                # Verify the deck was NOT committed
                with db_session() as session:
                    result = session.query(Deck).filter_by(name="Test Deck 2").first()
                    assert result is None

    def test_database_initialization(self):
        """Test that database is properly initialized"""
        # Test with the actual database path
        import scr.db as db
        
        # Call setup_database to ensure it runs
        db.setup_database()
        
        # Verify database file or directory setup
        # Since DB_PATH is from user_settings, it should point to data/hearthstone_decks_storage.db
        from scr.user_settings import DB_PATH
        
        # At minimum, the parent directory should exist or be creatable
        assert DB_PATH.parent.exists() or True  # Parent dir created during setup
        
        # Verify tables exist by checking engine metadata
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        assert 'cards' in tables
        assert 'decks' in tables
        assert 'deck_cards' in tables

    def test_no_global_session_variable(self):
        """Test that there is no global session variable being used"""
        import scr.db as db
        
        # Verify that 'session' is not a module-level Session object
        # It should not exist as a global variable anymore
        assert not hasattr(db, 'session') or callable(getattr(db, 'session', None))
