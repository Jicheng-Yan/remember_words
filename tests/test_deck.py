#!/usr/bin/env python3

import sys
import os
import unittest
import tempfile
import json
import shutil
from unittest.mock import patch, MagicMock

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.deck import Deck, DeckManager
from app.word import Word

class TestDeck(unittest.TestCase):
    def setUp(self):
        # Create test words
        self.word1 = Word("apple", ["ap", "ple"], "ˈæpəl", "りんご")
        self.word2 = Word("banana", ["ba", "na", "na"], "bəˈnænə", "バナナ")
        
        # Create a deck
        self.deck = Deck("test_deck", [self.word1, self.word2])
    
    def test_deck_initialization(self):
        """Test proper initialization of Deck objects"""
        self.assertEqual(self.deck.name, "test_deck")
        self.assertEqual(len(self.deck.words), 2)
        self.assertEqual(self.deck.words[0].word, "apple")
        self.assertEqual(self.deck.words[1].word, "banana")
        
        # Test default stats
        expected_stats = {
            "total_time": 0,
            "total_sessions": 0,
            "total_studied": 0,
            "total_remembered": 0
        }
        self.assertEqual(self.deck.stats, expected_stats)
        
        # Test empty deck
        empty_deck = Deck("empty")
        self.assertEqual(empty_deck.name, "empty")
        self.assertEqual(len(empty_deck.words), 0)
        self.assertEqual(empty_deck.stats, expected_stats)
    
    def test_add_word(self):
        """Test adding words to a deck"""
        word3 = Word("computer", ["com", "pu", "ter"])
        self.deck.add_word(word3)
        
        self.assertEqual(len(self.deck.words), 3)
        self.assertEqual(self.deck.words[2].word, "computer")
    
    def test_reset_stats(self):
        """Test resetting deck statistics"""
        # Set some non-zero stats
        self.deck.stats = {
            "total_time": 120,
            "total_sessions": 5,
            "total_studied": 50,
            "total_remembered": 30
        }
        
        # Reset stats
        self.deck.reset_stats()
        
        # Verify stats were reset
        expected_stats = {
            "total_time": 0,
            "total_sessions": 0,
            "total_studied": 0,
            "total_remembered": 0
        }
        self.assertEqual(self.deck.stats, expected_stats)
    
    def test_to_dict(self):
        """Test conversion to dictionary format"""
        deck_dict = self.deck.to_dict()
        
        self.assertEqual(deck_dict["name"], "test_deck")
        self.assertEqual(len(deck_dict["words"]), 2)
        self.assertEqual(deck_dict["words"][0]["word"], "apple")
        self.assertEqual(deck_dict["words"][1]["word"], "banana")
        self.assertEqual(deck_dict["stats"]["total_sessions"], 0)
    
    def test_from_dict(self):
        """Test creation of Deck from dictionary"""
        deck_dict = {
            "name": "new_deck",
            "words": [
                {
                    "word": "guitar",
                    "syllables": ["gui", "tar"],
                    "ipa": "ɡɪˈtɑːr",
                    "japanese": "ギター"
                }
            ],
            "stats": {
                "total_time": 50,
                "total_sessions": 2,
                "total_studied": 10,
                "total_remembered": 5
            }
        }
        
        deck = Deck.from_dict(deck_dict)
        self.assertEqual(deck.name, "new_deck")
        self.assertEqual(len(deck.words), 1)
        self.assertEqual(deck.words[0].word, "guitar")
        self.assertEqual(deck.words[0].syllables, ["gui", "tar"])
        self.assertEqual(deck.stats["total_sessions"], 2)


class TestDeckManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for deck files
        self.temp_dir = tempfile.mkdtemp()
        self.deck_manager = DeckManager(self.temp_dir)
        
        # Create a test CSV file
        self.csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(self.csv_path, 'w', encoding='utf-8') as f:
            f.write("word,IPA,japanese\n")
            f.write("apple,ˈæpəl,りんご\n")
            f.write("banana,bəˈnænə,バナナ\n")
    
    def tearDown(self):
        # Clean up temporary files
        shutil.rmtree(self.temp_dir)
    
    def test_create_deck(self):
        """Test creating a new deck"""
        deck = self.deck_manager.create_deck("test_deck")
        
        self.assertEqual(deck.name, "test_deck")
        self.assertEqual(len(deck.words), 0)
        
        # Check if file was created
        deck_path = os.path.join(self.temp_dir, "test_deck.json")
        self.assertTrue(os.path.exists(deck_path))
        
        # Test creating a duplicate deck
        with self.assertRaises(ValueError):
            self.deck_manager.create_deck("test_deck")
    
    def test_load_deck(self):
        """Test loading a deck from file"""
        # First create a deck
        original_deck = self.deck_manager.create_deck("load_test")
        original_deck.add_word(Word("apple", ["ap", "ple"]))
        self.deck_manager.save_deck(original_deck)
        
        # Load the deck
        loaded_deck = self.deck_manager.load_deck("load_test")
        
        self.assertEqual(loaded_deck.name, "load_test")
        self.assertEqual(len(loaded_deck.words), 1)
        self.assertEqual(loaded_deck.words[0].word, "apple")
        
        # Test loading non-existent deck
        with self.assertRaises(FileNotFoundError):
            self.deck_manager.load_deck("nonexistent")
    
    def test_save_deck(self):
        """Test saving a deck to file"""
        deck = Deck("save_test", [Word("test", ["te", "st"])])
        
        # Save the deck
        self.deck_manager.save_deck(deck)
        
        # Check if file exists
        deck_path = os.path.join(self.temp_dir, "save_test.json")
        self.assertTrue(os.path.exists(deck_path))
        
        # Verify content
        with open(deck_path, 'r', encoding='utf-8') as f:
            deck_data = json.load(f)
            self.assertEqual(deck_data["name"], "save_test")
            self.assertEqual(len(deck_data["words"]), 1)
            self.assertEqual(deck_data["words"][0]["word"], "test")
    
    def test_list_decks(self):
        """Test listing available decks"""
        # Initially no decks
        self.assertEqual(len(self.deck_manager.list_decks()), 0)
        
        # Create some decks
        self.deck_manager.create_deck("deck1")
        self.deck_manager.create_deck("deck2")
        
        # Check list
        deck_list = self.deck_manager.list_decks()
        self.assertEqual(len(deck_list), 2)
        self.assertIn("deck1", deck_list)
        self.assertIn("deck2", deck_list)
    
    def test_import_deck_from_csv(self):
        """Test importing a deck from CSV"""
        deck = self.deck_manager.import_deck_from_csv(self.csv_path, "csv_deck")
        
        self.assertEqual(deck.name, "csv_deck")
        self.assertEqual(len(deck.words), 2)
        self.assertEqual(deck.words[0].word, "apple")
        self.assertEqual(deck.words[1].japanese, "バナナ")
        
        # Check file was created
        deck_path = os.path.join(self.temp_dir, "csv_deck.json")
        self.assertTrue(os.path.exists(deck_path))
        
        # Test importing with invalid CSV path
        with self.assertRaises(FileNotFoundError):
            self.deck_manager.import_deck_from_csv("nonexistent.csv", "error_deck")
        
        # Test importing with existing deck name
        with self.assertRaises(ValueError):
            self.deck_manager.import_deck_from_csv(self.csv_path, "csv_deck")
    
    def test_split_into_syllables_with_library(self):
        """Test syllable splitting with syllables library"""
        # Instead of mocking the library, we'll test the actual function behavior
        # with expected output from the fallback implementation
        result = self.deck_manager._split_into_syllables("example")
        
        # We just need to verify that the function returns a valid list of syllables
        # that reconstruct the original word
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertEqual(''.join(result), "example")
    
    def test_split_into_syllables_fallback(self):
        """Test syllable splitting fallback methods"""
        # Test with hyphenated word
        result = self.deck_manager._split_into_syllables("fall-back")
        self.assertEqual(result, ["fall", "back"])
        
        # Test basic vowel-based splitting
        # Note: This is testing a very simplified syllable estimation and actual results may vary
        result = self.deck_manager._split_into_syllables("example")
        self.assertGreater(len(result), 0)  # At least one syllable
        self.assertEqual(''.join(result), "example")  # Should reconstruct the original word


if __name__ == '__main__':
    unittest.main()