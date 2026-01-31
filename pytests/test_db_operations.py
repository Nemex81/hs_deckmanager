"""
Test suite for database operations (CRUD) for Hearthstone Deck Manager.

Tests cover:
- Card CRUD operations
- Deck CRUD operations  
- DeckCard relationship operations
- Database session management

Note: These tests use direct SQLAlchemy imports to avoid wx dependency during testing.
"""

import pytest
import tempfile
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define models directly for testing (to avoid wx import from scr.db)
Base = declarative_base()


class Card(Base):
    """Model for representing a Hearthstone card."""
    __tablename__ = 'cards'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    class_name = Column(String)
    mana_cost = Column(Integer, nullable=False)
    card_type = Column(String, nullable=False)
    spell_type = Column(String)
    card_subtype = Column(String)
    attack = Column(Integer)
    health = Column(Integer)
    durability = Column(Integer)
    rarity = Column(String)
    expansion = Column(String)

    __table_args__ = (
        Index('idx_card_name', 'name'),
    )


class Deck(Base):
    """Model for representing a Hearthstone deck."""
    __tablename__ = 'decks'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    player_class = Column(String, nullable=False)
    game_format = Column(String, nullable=False)


class DeckCard(Base):
    """Model for representing the relationship between decks and cards."""
    __tablename__ = 'deck_cards'
    deck_id = Column(Integer, ForeignKey('decks.id'), primary_key=True)
    card_id = Column(Integer, ForeignKey('cards.id'), primary_key=True)
    quantity = Column(Integer, nullable=False)


@pytest.fixture
def test_db_path():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_hearthstone.db"
    yield db_path
    # Cleanup is handled by temp_dir auto-deletion


@pytest.fixture
def test_engine(test_db_path):
    """Create a test database engine."""
    engine = create_engine(f'sqlite:///{test_db_path}', echo=False)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def test_session(test_engine):
    """Create a test database session."""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.close()


class TestCardCRUD:
    """Test Card CRUD operations."""

    def test_create_card(self, test_session):
        """Test creating a new card."""
        card = Card(
            name="Fireball",
            class_name="Mage",
            mana_cost=4,
            card_type="Spell",
            spell_type=None,
            card_subtype=None,
            attack=None,
            health=None,
            durability=None,
            rarity="Common",
            expansion="Basic"
        )
        test_session.add(card)
        test_session.commit()

        # Verify card was created
        retrieved_card = test_session.query(Card).filter_by(name="Fireball").first()
        assert retrieved_card is not None
        assert retrieved_card.name == "Fireball"
        assert retrieved_card.mana_cost == 4
        assert retrieved_card.card_type == "Spell"
        assert retrieved_card.rarity == "Common"

    def test_read_card(self, test_session):
        """Test reading a card from the database."""
        # Create a card
        card = Card(
            name="Boulderfist Ogre",
            class_name="Neutral",
            mana_cost=6,
            card_type="Minion",
            attack=6,
            health=7,
            rarity="Free",
            expansion="Basic"
        )
        test_session.add(card)
        test_session.commit()

        # Read the card
        retrieved_card = test_session.query(Card).filter_by(name="Boulderfist Ogre").first()
        assert retrieved_card is not None
        assert retrieved_card.attack == 6
        assert retrieved_card.health == 7

    def test_update_card(self, test_session):
        """Test updating a card in the database."""
        # Create a card
        card = Card(
            name="Test Card",
            class_name="Neutral",
            mana_cost=1,
            card_type="Minion",
            attack=1,
            health=1,
            rarity="Common",
            expansion="Test"
        )
        test_session.add(card)
        test_session.commit()

        # Update the card
        card.attack = 2
        card.health = 2
        test_session.commit()

        # Verify update
        retrieved_card = test_session.query(Card).filter_by(name="Test Card").first()
        assert retrieved_card.attack == 2
        assert retrieved_card.health == 2

    def test_delete_card(self, test_session):
        """Test deleting a card from the database."""
        # Create a card
        card = Card(
            name="To Be Deleted",
            class_name="Neutral",
            mana_cost=1,
            card_type="Minion",
            attack=1,
            health=1,
            rarity="Common",
            expansion="Test"
        )
        test_session.add(card)
        test_session.commit()

        # Delete the card
        test_session.delete(card)
        test_session.commit()

        # Verify deletion
        retrieved_card = test_session.query(Card).filter_by(name="To Be Deleted").first()
        assert retrieved_card is None


class TestDeckCRUD:
    """Test Deck CRUD operations."""

    def test_create_deck(self, test_session):
        """Test creating a new deck."""
        deck = Deck(
            name="Test Deck",
            player_class="Warrior",
            game_format="Standard"
        )
        test_session.add(deck)
        test_session.commit()

        # Verify deck was created
        retrieved_deck = test_session.query(Deck).filter_by(name="Test Deck").first()
        assert retrieved_deck is not None
        assert retrieved_deck.player_class == "Warrior"
        assert retrieved_deck.game_format == "Standard"

    def test_read_deck(self, test_session):
        """Test reading a deck from the database."""
        # Create a deck
        deck = Deck(
            name="Aggro Warrior",
            player_class="Warrior",
            game_format="Standard"
        )
        test_session.add(deck)
        test_session.commit()

        # Read the deck
        retrieved_deck = test_session.query(Deck).filter_by(name="Aggro Warrior").first()
        assert retrieved_deck is not None
        assert retrieved_deck.player_class == "Warrior"

    def test_update_deck(self, test_session):
        """Test updating a deck in the database."""
        # Create a deck
        deck = Deck(
            name="Test Deck Update",
            player_class="Mage",
            game_format="Standard"
        )
        test_session.add(deck)
        test_session.commit()

        # Update the deck
        deck.player_class = "Warlock"
        deck.game_format = "Wild"
        test_session.commit()

        # Verify update
        retrieved_deck = test_session.query(Deck).filter_by(name="Test Deck Update").first()
        assert retrieved_deck.player_class == "Warlock"
        assert retrieved_deck.game_format == "Wild"

    def test_delete_deck(self, test_session):
        """Test deleting a deck from the database."""
        # Create a deck
        deck = Deck(
            name="Deck to Delete",
            player_class="Paladin",
            game_format="Standard"
        )
        test_session.add(deck)
        test_session.commit()

        # Delete the deck
        test_session.delete(deck)
        test_session.commit()

        # Verify deletion
        retrieved_deck = test_session.query(Deck).filter_by(name="Deck to Delete").first()
        assert retrieved_deck is None


class TestDeckCardRelationship:
    """Test DeckCard relationship operations."""

    def test_add_card_to_deck(self, test_session):
        """Test adding a card to a deck."""
        # Create a card
        card = Card(
            name="Arcane Intellect",
            class_name="Mage",
            mana_cost=3,
            card_type="Spell",
            rarity="Free",
            expansion="Basic"
        )
        test_session.add(card)

        # Create a deck
        deck = Deck(
            name="Mage Deck",
            player_class="Mage",
            game_format="Standard"
        )
        test_session.add(deck)
        test_session.commit()

        # Add card to deck
        deck_card = DeckCard(
            deck_id=deck.id,
            card_id=card.id,
            quantity=2
        )
        test_session.add(deck_card)
        test_session.commit()

        # Verify relationship
        retrieved_deck_card = test_session.query(DeckCard).filter_by(
            deck_id=deck.id, 
            card_id=card.id
        ).first()
        assert retrieved_deck_card is not None
        assert retrieved_deck_card.quantity == 2

    def test_update_card_quantity(self, test_session):
        """Test updating card quantity in a deck."""
        # Create card and deck
        card = Card(
            name="Frostbolt",
            class_name="Mage",
            mana_cost=2,
            card_type="Spell",
            rarity="Common",
            expansion="Basic"
        )
        deck = Deck(
            name="Freeze Mage",
            player_class="Mage",
            game_format="Standard"
        )
        test_session.add_all([card, deck])
        test_session.commit()

        # Add card to deck with quantity 1
        deck_card = DeckCard(
            deck_id=deck.id,
            card_id=card.id,
            quantity=1
        )
        test_session.add(deck_card)
        test_session.commit()

        # Update quantity
        deck_card.quantity = 2
        test_session.commit()

        # Verify update
        retrieved_deck_card = test_session.query(DeckCard).filter_by(
            deck_id=deck.id,
            card_id=card.id
        ).first()
        assert retrieved_deck_card.quantity == 2

    def test_remove_card_from_deck(self, test_session):
        """Test removing a card from a deck."""
        # Create card and deck
        card = Card(
            name="Polymorph",
            class_name="Mage",
            mana_cost=4,
            card_type="Spell",
            rarity="Free",
            expansion="Basic"
        )
        deck = Deck(
            name="Control Mage",
            player_class="Mage",
            game_format="Standard"
        )
        test_session.add_all([card, deck])
        test_session.commit()

        # Add card to deck
        deck_card = DeckCard(
            deck_id=deck.id,
            card_id=card.id,
            quantity=1
        )
        test_session.add(deck_card)
        test_session.commit()

        # Remove card from deck
        test_session.delete(deck_card)
        test_session.commit()

        # Verify deletion
        retrieved_deck_card = test_session.query(DeckCard).filter_by(
            deck_id=deck.id,
            card_id=card.id
        ).first()
        assert retrieved_deck_card is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
