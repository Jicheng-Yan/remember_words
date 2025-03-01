#!/usr/bin/env python3

import sys
import os
import unittest
import tempfile
import shutil
import json
from unittest.mock import patch, MagicMock, mock_open

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all components
from app.word import Word, Card
from app.deck import Deck, DeckManager
from app.session import Session
import main

class TestApplicationIntegration(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.decks_dir = os.path.join(self.temp_dir, "decks")
        os.makedirs(self.decks_dir, exist_ok=True)
        
        # Create a test CSV file
        self.csv_path = os.path.join(self.temp_dir, "test_words.csv")
        with open(self.csv_path, 'w', encoding='utf-8') as f:
            f.write("word,IPA,japanese\n")
            f.write("apple,ˈæpəl,りんご\n")
            f.write("banana,bəˈnænə,バナナ\n")
            f.write("computer,kəmˈpjuːtər,コンピュータ\n")
    
    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_create_deck_and_add_words(self):
        """Test creating a deck and adding words to it"""
        # Create a deck manager for this specific test
        deck_manager = DeckManager(self.decks_dir)
        
        # 1. Create a new deck
        deck = deck_manager.create_deck("test_deck")
        self.assertEqual(deck.name, "test_deck")
        self.assertEqual(len(deck.words), 0)
        
        # 2. Add words to the deck
        word1 = Word("apple", ["ap", "ple"], "ˈæpəl", "りんご")
        word2 = Word("banana", ["ba", "na", "na"], "bəˈnænə", "バナナ")
        deck.add_word(word1)
        deck.add_word(word2)
        deck_manager.save_deck(deck)
        
        # 3. Reload the deck and verify words
        reloaded_deck = deck_manager.load_deck("test_deck")
        self.assertEqual(len(reloaded_deck.words), 2)
        self.assertEqual(reloaded_deck.words[0].word, "apple")
    
    def test_import_from_csv(self):
        """Test importing a deck from CSV file"""
        # Create a deck manager for this specific test
        deck_manager = DeckManager(self.decks_dir)
        
        # Import from CSV
        deck = deck_manager.import_deck_from_csv(self.csv_path, "csv_deck")
        self.assertEqual(deck.name, "csv_deck")
        self.assertEqual(len(deck.words), 3)
        
        # Check that the deck was saved
        deck_path = os.path.join(self.decks_dir, "csv_deck.json")
        self.assertTrue(os.path.exists(deck_path))
    
    @patch('app.session.Session._save_session')
    @patch('app.session.Session._load_session')
    @patch('random.choice')
    @patch('random.sample')
    @patch('random.randint')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_session_with_mock(self, mock_print, mock_input, mock_randint, mock_sample, mock_choice, 
                               mock_load_session, mock_save_session):
        """Test session functionality with mocks"""
        # Set up the mocks
        mock_load_session.return_value = False  # No saved session
        mock_randint.return_value = 0  # Always hide first syllable
        
        # Create a deck with test words
        deck = Deck("test_deck")
        word1 = Word("apple", ["ap", "ple"], "ˈæpəl", "りんご")
        word2 = Word("banana", ["ba", "na", "na"], "bəˈnænə", "バナナ")
        deck.add_word(word1)
        deck.add_word(word2)
        
        # Set up sample to return both words
        mock_sample.return_value = [word1, word2]
        
        # Create a session
        session = Session(deck, 2)
        
        # Prepare cards
        session.prepare_cards()
        self.assertEqual(len(session.cards), 2)
        self.assertEqual(len(session.remaining_cards), 2)
        
        # Set up the mock to return card1 then card2
        card1 = session.remaining_cards[0]
        card2 = session.remaining_cards[1]
        mock_choice.side_effect = [card1, card2]
        
        # Set up user inputs: answer correctly and then exit
        mock_input.side_effect = ["ap", "exit"]
        
        # Run the session
        session.run()
        
        # Check that the first card was answered and removed from remaining cards
        self.assertEqual(session.studied, 1)
        self.assertEqual(len(session.remaining_cards), 1)
        
        # Verify the session was saved
        mock_save_session.assert_called()

    @patch('os.system')
    @patch('os.listdir')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('builtins.input')
    def test_main_menu_flow(self, mock_input, mock_json_load, mock_file, mock_listdir, mock_system):
        """Integration test: Test main menu navigation flow"""
        # Set up mocks for file operations
        mock_listdir.return_value = ["test_deck.json"]
        mock_json_load.return_value = {
            "name": "test_deck", 
            "words": [{"word": "apple", "syllables": ["ap", "ple"], "ipa": "", "japanese": ""}], 
            "stats": {"total_time": 0, "total_sessions": 0, "total_studied": 0, "total_remembered": 0}
        }
        
        # Create a patch for os.path.dirname to return our temp directory
        with patch('os.path.dirname', return_value=self.decks_dir), \
             patch('os.path.abspath', return_value=self.decks_dir), \
             patch('os.path.join', return_value=os.path.join(self.decks_dir, "test_deck.json")), \
             patch('os.path.exists', return_value=True), \
             patch('builtins.print') as mock_print:
            
            # Mock user interactions: list decks then exit
            mock_input.side_effect = [
                "1",  # List decks
                "",   # Press Enter to continue
                "6"   # Exit
            ]
            
            # Run the main function
            main.main()
            
            # Verify screen was cleared
            mock_system.assert_called()
            
            # Verify user was shown deck listing
            mock_print.assert_any_call("Available Decks:")


class TestMainFunctions(unittest.TestCase):
    """
    Test individual functions from the main.py file
    """
    
    def setUp(self):
        # Create a temporary directory for deck files
        self.temp_dir = tempfile.mkdtemp()
        self.deck_manager = DeckManager(self.temp_dir)
        
        # Create a test deck
        self.deck = self.deck_manager.create_deck("test_deck")
        word = Word("test", ["te", "st"])
        self.deck.add_word(word)
        self.deck_manager.save_deck(self.deck)
    
    def tearDown(self):
        # Clean up
        shutil.rmtree(self.temp_dir)
    
    @patch('builtins.print')
    @patch('main.clear_screen')
    def test_print_header(self, mock_clear, mock_print):
        """Test print_header function"""
        main.print_header()
        mock_clear.assert_called_once()
        self.assertTrue(mock_print.call_count >= 3)  # Should print at least 3 lines
    
    @patch('builtins.print')
    def test_print_menu(self, mock_print):
        """Test print_menu function"""
        main.print_menu()
        self.assertTrue(mock_print.call_count >= 6)  # Should print 6 menu options
    
    @patch('builtins.input', return_value="")
    @patch('builtins.print')
    @patch('main.print_header')
    def test_list_decks(self, mock_header, mock_print, mock_input):
        """Test list_decks function"""
        main.list_decks(self.deck_manager)
        mock_header.assert_called_once()
        mock_print.assert_called()
        mock_input.assert_called_once()
    
    @patch('builtins.input', side_effect=["test_deck2", ""])
    @patch('builtins.print')
    @patch('main.print_header')
    def test_create_deck(self, mock_header, mock_print, mock_input):
        """Test create_deck function"""
        main.create_deck(self.deck_manager)
        mock_header.assert_called_once()
        
        # Check if deck was created
        deck_path = os.path.join(self.temp_dir, "test_deck2.json")
        self.assertTrue(os.path.exists(deck_path))


if __name__ == '__main__':
    unittest.main()