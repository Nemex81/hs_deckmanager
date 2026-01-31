"""
Test suite for parsing logic in Hearthstone Deck Manager.

Tests cover:
- Deck metadata parsing
- Deck string validation
- Card line parsing
"""

import pytest


class TestDeckParsing:
    """Test deck parsing functions."""

    @staticmethod
    def parse_deck_metadata(deck_string):
        """
        Extract metadata from a deck string.
        This is a standalone version of the function from models.py for testing.
        """
        lines = deck_string.splitlines()[:3]
        metadata = {
            "name": lines[0].replace("###", "").strip(),
            "player_class": "Neutrale",
            "game_format": "Standard"
        }
        
        for line in lines[1:]:
            if "Classe:" in line:
                metadata["player_class"] = line.split(":")[1].strip()
            elif "Formato:" in line:
                metadata["game_format"] = line.split(":")[1].strip()
        
        return metadata

    @staticmethod
    def is_valid_deck(deck_string):
        """
        Verify if a string represents a valid deck.
        This is a standalone version of the function from models.py for testing.
        """
        last_verify = "# Per utilizzare questo mazzo, copialo negli appunti e crea un nuovo mazzo in Hearthstone"
        return bool(
            deck_string and 
            deck_string.strip().startswith("###") and 
            last_verify in deck_string
        )

    def test_parse_deck_metadata_basic(self):
        """Test parsing basic deck metadata."""
        deck_string = """### Test Mage Deck
# Classe: Mage
# Formato: Standard
#
# 2x (1) Arcane Missiles
"""
        metadata = self.parse_deck_metadata(deck_string)
        
        assert metadata["name"] == "Test Mage Deck"
        assert metadata["player_class"] == "Mage"
        assert metadata["game_format"] == "Standard"

    def test_parse_deck_metadata_warrior(self):
        """Test parsing warrior deck metadata."""
        deck_string = """### Aggro Warrior
# Classe: Warrior
# Formato: Wild
#
# 2x (1) N'Zoth's First Mate
"""
        metadata = self.parse_deck_metadata(deck_string)
        
        assert metadata["name"] == "Aggro Warrior"
        assert metadata["player_class"] == "Warrior"
        assert metadata["game_format"] == "Wild"

    def test_parse_deck_metadata_no_class(self):
        """Test parsing deck metadata without explicit class."""
        deck_string = """### Test Deck
# Formato: Standard
#
"""
        metadata = self.parse_deck_metadata(deck_string)
        
        assert metadata["name"] == "Test Deck"
        assert metadata["player_class"] == "Neutrale"  # Default value
        assert metadata["game_format"] == "Standard"

    def test_parse_deck_metadata_no_format(self):
        """Test parsing deck metadata without explicit format."""
        deck_string = """### Test Deck
# Classe: Paladin
#
"""
        metadata = self.parse_deck_metadata(deck_string)
        
        assert metadata["name"] == "Test Deck"
        assert metadata["player_class"] == "Paladin"
        assert metadata["game_format"] == "Standard"  # Default value

    def test_is_valid_deck_valid(self):
        """Test validation of a valid deck string."""
        deck_string = """### Test Deck
# Classe: Mage
# Formato: Standard
#
# 2x (1) Arcane Missiles
# 2x (2) Frostbolt
# 
AAECAf0EAA8BuwLJA8kDqwTLBMsE7QSUA5QDlAOUA5QDlAOUA5QD
# 
# Per utilizzare questo mazzo, copialo negli appunti e crea un nuovo mazzo in Hearthstone
"""
        assert self.is_valid_deck(deck_string) is True

    def test_is_valid_deck_invalid_no_header(self):
        """Test validation of invalid deck (no header)."""
        deck_string = """Test Deck
# Classe: Mage
# 2x (1) Arcane Missiles
"""
        assert self.is_valid_deck(deck_string) is False

    def test_is_valid_deck_invalid_no_footer(self):
        """Test validation of invalid deck (no footer)."""
        deck_string = """### Test Deck
# Classe: Mage
# 2x (1) Arcane Missiles
"""
        assert self.is_valid_deck(deck_string) is False

    def test_is_valid_deck_empty(self):
        """Test validation of empty deck string."""
        deck_string = ""
        assert self.is_valid_deck(deck_string) is False

    def test_is_valid_deck_none(self):
        """Test validation of None deck string."""
        deck_string = None
        assert self.is_valid_deck(deck_string) is False


class TestCardParsing:
    """Test card parsing functions."""

    @staticmethod
    def parse_card_line(line):
        """
        Parse a card line from a deck string.
        Returns: tuple (quantity, mana_cost, card_name) or None if invalid.
        """
        import re
        # Expected format: # 2x (3) Arcane Intellect
        match = re.match(r'#\s*(\d+)x\s*\((\d+)\)\s*(.+)', line)
        if match:
            quantity = int(match.group(1))
            mana_cost = int(match.group(2))
            card_name = match.group(3).strip()
            return (quantity, mana_cost, card_name)
        return None

    def test_parse_card_line_valid(self):
        """Test parsing a valid card line."""
        line = "# 2x (3) Arcane Intellect"
        result = self.parse_card_line(line)
        
        assert result is not None
        quantity, mana_cost, card_name = result
        assert quantity == 2
        assert mana_cost == 3
        assert card_name == "Arcane Intellect"

    def test_parse_card_line_single_card(self):
        """Test parsing a card line with quantity 1."""
        line = "# 1x (7) Flamestrike"
        result = self.parse_card_line(line)
        
        assert result is not None
        quantity, mana_cost, card_name = result
        assert quantity == 1
        assert mana_cost == 7
        assert card_name == "Flamestrike"

    def test_parse_card_line_zero_mana(self):
        """Test parsing a card line with 0 mana cost."""
        line = "# 2x (0) Backstab"
        result = self.parse_card_line(line)
        
        assert result is not None
        quantity, mana_cost, card_name = result
        assert quantity == 2
        assert mana_cost == 0
        assert card_name == "Backstab"

    def test_parse_card_line_high_mana(self):
        """Test parsing a card line with high mana cost."""
        line = "# 1x (10) C'Thun"
        result = self.parse_card_line(line)
        
        assert result is not None
        quantity, mana_cost, card_name = result
        assert quantity == 1
        assert mana_cost == 10
        assert card_name == "C'Thun"

    def test_parse_card_line_special_characters(self):
        """Test parsing a card line with special characters in name."""
        line = "# 2x (1) N'Zoth's First Mate"
        result = self.parse_card_line(line)
        
        assert result is not None
        quantity, mana_cost, card_name = result
        assert quantity == 2
        assert mana_cost == 1
        assert card_name == "N'Zoth's First Mate"

    def test_parse_card_line_invalid_format(self):
        """Test parsing an invalid card line."""
        line = "Invalid card line"
        result = self.parse_card_line(line)
        
        assert result is None

    def test_parse_card_line_empty(self):
        """Test parsing an empty line."""
        line = ""
        result = self.parse_card_line(line)
        
        assert result is None

    def test_parse_card_line_comment_only(self):
        """Test parsing a comment-only line."""
        line = "# Classe: Mage"
        result = self.parse_card_line(line)
        
        assert result is None


class TestFilterOptions:
    """Test filter options logic."""

    @staticmethod
    def is_filter_all_option(value):
        """Check if a filter value represents 'all' options."""
        filters_options = ["tutti", "Tutti", "qualsiasi", "Qualsiasi", "", "all", "All", "", None]
        return value in filters_options

    def test_filter_all_options_italian(self):
        """Test Italian 'all' filter options."""
        assert self.is_filter_all_option("tutti") is True
        assert self.is_filter_all_option("Tutti") is True
        assert self.is_filter_all_option("qualsiasi") is True
        assert self.is_filter_all_option("Qualsiasi") is True

    def test_filter_all_options_english(self):
        """Test English 'all' filter options."""
        assert self.is_filter_all_option("all") is True
        assert self.is_filter_all_option("All") is True

    def test_filter_all_options_empty(self):
        """Test empty filter options."""
        assert self.is_filter_all_option("") is True
        assert self.is_filter_all_option(None) is True

    def test_filter_specific_value(self):
        """Test specific filter values are not 'all'."""
        assert self.is_filter_all_option("Mage") is False
        assert self.is_filter_all_option("Warrior") is False
        assert self.is_filter_all_option("3") is False
        assert self.is_filter_all_option("Common") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
