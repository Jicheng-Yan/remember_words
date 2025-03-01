#!/usr/bin/env python3

import sys
import os
import unittest
import tempfile
import json
import shutil
from unittest.mock import patch, MagicMock, mock_open, call

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.session import Session
from app.deck import Deck
from app.word import Word, Card

class TestSession(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for session files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test words
        self.word1 = Word("apple", ["ap", "ple"], "ˈæpəl", "りんご")
        self.word2 = Word("banana", ["ba", "na", "na"], "bəˈnænə", "バナナ")
        self.word3 = Word("computer", ["com", "pu", "ter"], "kəmˈpjuːtər", "コンピュータ")
        
        # Create a test deck
        self.deck = Deck("test_deck", [self.word1, self.word2, self.word3])
        
        # Patch os.path.join to use our temp directory for session files
        self.patcher = patch('os.path.join')
        self.mock_join = self.patcher.start()
        self.mock_join.return_value = os.path.join(self.temp_dir, "test_deck_session.json")
        
        # Set up a patch for os.path.exists to avoid checking for real files
        self.exists_patcher = patch('os.path.exists')
        self.mock_exists = self.exists_patcher.start()
        self.mock_exists.return_value = False  # Default to file not existing
    
    def tearDown(self):
        # Clean up temporary files
        self.patcher.stop()
        self.exists_patcher.stop()
        shutil.rmtree(self.temp_dir)
    
    def test_session_initialization(self):
        """Test proper initialization of Session objects"""
        session = Session(self.deck)
        
        self.assertEqual(session.deck, self.deck)
        self.assertEqual(session.num_cards, 3)  # All words in deck
        self.assertEqual(len(session.cards), 0)  # Cards not prepared yet
        self.assertEqual(len(session.remaining_cards), 0)
        self.assertEqual(session.studied, 0)
        self.assertEqual(session.remembered, 0)
        self.assertEqual(session.start_time, 0)
        
        # Test with limited number of cards
        session2 = Session(self.deck, 2)
        self.assertEqual(session2.num_cards, 2)
        
        # Test with number larger than deck size
        session3 = Session(self.deck, 10)
        self.assertEqual(session3.num_cards, 3)  # Should be limited to deck size
    
    @patch('random.randint')
    @patch('random.sample')
    def test_prepare_cards(self, mock_sample, mock_randint):
        """Test preparation of cards for a session"""
        # Mock the random functions to be deterministic
        mock_sample.return_value = [self.word1, self.word2, self.word3]
        mock_randint.return_value = 0  # Always hide first syllable
        
        session = Session(self.deck)
        session.prepare_cards()
        
        # Check cards were created
        self.assertEqual(len(session.cards), 3)
        self.assertEqual(len(session.remaining_cards), 3)
        
        # Check cards contain the expected words
        words_in_cards = [card.word.word for card in session.cards]
        self.assertIn("apple", words_in_cards)
        self.assertIn("banana", words_in_cards)
        self.assertIn("computer", words_in_cards)
    
    @patch('builtins.open', new_callable=mock_open)
    def test_save_and_load_session(self, mock_file):
        """Test saving and loading a session"""
        # Set up mocks
        self.mock_exists.return_value = True  # Make the file "exist"
        
        # Mock the JSON data that would be loaded
        mock_data = {
            "deck_name": "test_deck",
            "cards": [
                {
                    "word": self.word1.to_dict(),
                    "hidden_index": 0,
                    "is_correct_first_attempt": True
                },
                {
                    "word": self.word2.to_dict(),
                    "hidden_index": 1,
                    "is_correct_first_attempt": False
                }
            ],
            "remaining_indices": [1],  # Only the second card remains
            "studied": 5,
            "start_time": 1000
        }
        
        # Set up the mock to return our data when reading
        mock_file.return_value.read.return_value = json.dumps(mock_data)
        
        # Create a session and load from "file"
        session = Session(self.deck)
        result = session._load_session()
        
        # Check session was loaded successfully
        self.assertTrue(result)
        self.assertEqual(len(session.cards), 2)
        self.assertEqual(session.studied, 5)
        self.assertEqual(session.start_time, 1000)
        self.assertEqual(len(session.remaining_cards), 1)
    
    @patch('os.remove')
    def test_delete_session(self, mock_remove):
        """Test deleting a saved session"""
        # Set the file to "exist"
        self.mock_exists.return_value = True
        
        session = Session(self.deck)
        session._delete_session()
        
        # Check file deletion was attempted
        mock_remove.assert_called_once_with(os.path.join(self.temp_dir, "test_deck_session.json"))
    
    @patch('time.time')
    def test_calculate_stats(self, mock_time):
        """Test calculation of session statistics"""
        # Set up mock time
        mock_time.return_value = 1600
        
        # Create session with prepared cards manually
        session = Session(self.deck)
        card1 = Card(self.word1, 0)
        card2 = Card(self.word2, 1)
        card3 = Card(self.word3, 0)
        session.cards = [card1, card2, card3]
        session.start_time = 1500  # 100 seconds ago
        
        # Set some cards as correct
        session.cards[0].is_correct_first_attempt = True
        session.cards[1].is_correct_first_attempt = False
        session.cards[2].is_correct_first_attempt = True
        
        # Calculate stats
        stats = session._calculate_stats()
        
        # Check stats
        self.assertEqual(stats["time_spent"], 100)
        self.assertEqual(stats["remembered_cards"], 2)
        self.assertEqual(stats["total_cards"], 3)
    
    def test_update_deck_stats(self):
        """Test updating deck statistics from session stats"""
        session = Session(self.deck)
        
        # Initial deck stats
        self.assertEqual(self.deck.stats["total_time"], 0)
        self.assertEqual(self.deck.stats["total_sessions"], 0)
        
        # Session stats
        stats = {
            "time_spent": 120,
            "studied_cards": 10,
            "remembered_cards": 7,
            "total_cards": 10
        }
        
        # Update stats
        session._update_deck_stats(stats)
        
        # Check updated stats
        self.assertEqual(self.deck.stats["total_time"], 120)
        self.assertEqual(self.deck.stats["total_sessions"], 1)
        self.assertEqual(self.deck.stats["total_studied"], 10)
        self.assertEqual(self.deck.stats["total_remembered"], 7)
    
    def test_format_time(self):
        """Test time formatting function"""
        session = Session(self.deck)
        
        self.assertEqual(session._format_time(30), "30s")
        self.assertEqual(session._format_time(90), "1m 30s")
        self.assertEqual(session._format_time(3675), "1h 1m 15s")
    
    def test_calculate_percentage(self):
        """Test percentage calculation"""
        session = Session(self.deck)
        
        self.assertEqual(session._calculate_percentage(75, 100), 75)
        self.assertEqual(session._calculate_percentage(1, 3), 33)
        self.assertEqual(session._calculate_percentage(0, 100), 0)
        self.assertEqual(session._calculate_percentage(10, 0), 0)  # Should handle division by zero
        
    @patch('builtins.input')
    @patch('builtins.print')
    @patch('time.time')
    @patch('random.choice')
    @patch('app.session.Session._load_session')
    @patch('app.session.Session._save_session')
    def test_run_session(self, mock_save, mock_load, mock_choice, mock_time, mock_print, mock_input):
        """Test running a complete session with character-by-character feedback"""
        # Set up mocks
        mock_time.return_value = 1600
        mock_load.return_value = False  # No saved session
        
        # Create specific test cards
        test_deck = Deck("test_deck")
        word1 = Word("apple", ["ap", "ple"])
        word2 = Word("banana", ["ba", "na", "na"])
        test_deck.add_word(word1)
        test_deck.add_word(word2)
        
        card1 = Card(word1, 0)  # Hide "ap"
        card2 = Card(word2, 1)  # Hide "na"
        
        # Set up a session with these cards
        session = Session(test_deck)
        session.cards = [card1, card2]
        session.remaining_cards = [card1, card2]
        session.start_time = 1500
        
        # Mock random.choice to return cards in sequence
        def mock_choice_impl(remaining_cards):
            if card1 in remaining_cards:
                return card1
            return card2
        mock_choice.side_effect = mock_choice_impl
        
        # Test cases for user input
        mock_input.side_effect = [
            "wrong",  # Wrong answer for first card
            "ap",     # Correct answer for first card
            "na"      # Correct answer for second card
        ]
        
        # Run the session
        stats = session.run()
        
        # Verify card behavior and feedback display
        expected_calls = [
            # Initial session info
            call("\nStarting session with 2 cards from deck 'test_deck'"),
            call("For each card, type the missing syllable (___)"),
            call("Type 'exit' to save and exit the session"),
            call("-" * 50),
            
            # First card (wrong answer)
            call('\nCard: ___-ple'),
            call("Incorrect. Here's what happened:"),
            call("Your input:  \x1b[91mw\x1b[0m\x1b[91mr\x1b[0m\x1b[91mo\x1b[0m\x1b[91mn\x1b[0m\x1b[91mg\x1b[0m"),
            call("Correct was: ap"),
            
            # First card again (correct answer)
            call('\nCard: ___-ple'),
            call("Correct!"),
            
            # Second card (correct answer)
            call('\nCard: ba-___-na'),
            call("Correct!"),
            
            # Session completion
            call("\nCongratulations! You've completed the session!"),
            
            # Stats display
            call("\nSession Statistics:")
        ]
        
        # Verify the print calls (excluding stats which are variable)
        mock_print.assert_has_calls(expected_calls, any_order=False)
        
        # Verify session statistics
        self.assertEqual(session.studied, 3)  # Three attempts total
        self.assertEqual(len(session.remaining_cards), 0)  # All cards completed
        self.assertEqual(test_deck.stats["total_sessions"], 1)
        self.assertEqual(test_deck.stats["total_studied"], 3)

    @patch('builtins.print')
    @patch('app.session.Session._load_session')
    def test_run_with_empty_cards(self, mock_load, mock_print):
        """Test running session with no cards available"""
        # No saved session
        mock_load.return_value = False
        
        # Create a deck with no words
        empty_deck = Deck("empty_deck")
        
        # Create session
        session = Session(empty_deck)
        
        result = session.run()
        
        # Should print a message about no cards
        mock_print.assert_any_call("No cards available for this session.")
        
        # Should return None
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()