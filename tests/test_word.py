#!/usr/bin/env python3

import sys
import os
import unittest

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.word import Word, Card

class TestWord(unittest.TestCase):
    def setUp(self):
        # Create test words
        self.word1 = Word("apple", ["ap", "ple"], "ˈæpəl", "りんご")
        self.word2 = Word("banana", ["ba", "na", "na"], "bəˈnænə", "バナナ")
        self.word3 = Word("test", [], "", "")  # Word with no syllables or translations
    
    def test_word_initialization(self):
        """Test proper initialization of Word objects"""
        self.assertEqual(self.word1.word, "apple")
        self.assertEqual(self.word1.syllables, ["ap", "ple"])
        self.assertEqual(self.word1.ipa, "ˈæpəl")
        self.assertEqual(self.word1.japanese, "りんご")
        
        # Test default values
        self.assertEqual(self.word3.syllables, [])
        self.assertEqual(self.word3.ipa, "")
        self.assertEqual(self.word3.japanese, "")
    
    def test_get_hidden_representation(self):
        """Test syllable hiding functionality"""
        self.assertEqual(self.word1.get_hidden_representation(0), "___-ple")
        self.assertEqual(self.word1.get_hidden_representation(1), "ap-___")
        
        # Test with word with no syllables
        self.assertEqual(self.word3.get_hidden_representation(0), "test-___")
        
        # Test with out-of-range index
        self.assertEqual(self.word1.get_hidden_representation(5), "apple-___")
    
    def test_to_dict(self):
        """Test conversion to dictionary format"""
        expected_dict = {
            "word": "apple",
            "syllables": ["ap", "ple"],
            "ipa": "ˈæpəl",
            "japanese": "りんご"
        }
        self.assertEqual(self.word1.to_dict(), expected_dict)
    
    def test_from_dict(self):
        """Test creation of Word from dictionary"""
        word_dict = {
            "word": "computer",
            "syllables": ["com", "pu", "ter"],
            "ipa": "kəmˈpjuːtər",
            "japanese": "コンピュータ"
        }
        
        word = Word.from_dict(word_dict)
        self.assertEqual(word.word, "computer")
        self.assertEqual(word.syllables, ["com", "pu", "ter"])
        self.assertEqual(word.ipa, "kəmˈpjuːtər")
        self.assertEqual(word.japanese, "コンピュータ")
        
        # Test with minimal dictionary
        minimal_dict = {"word": "minimal"}
        minimal_word = Word.from_dict(minimal_dict)
        self.assertEqual(minimal_word.word, "minimal")
        self.assertEqual(minimal_word.syllables, [])
        self.assertEqual(minimal_word.ipa, "")
        self.assertEqual(minimal_word.japanese, "")


class TestCard(unittest.TestCase):
    def setUp(self):
        # Create test words and cards
        self.word = Word("apple", ["ap", "ple"], "ˈæpəl", "りんご")
        self.card1 = Card(self.word, 0)  # Hide first syllable
        self.card2 = Card(self.word, 1)  # Hide second syllable
    
    def test_card_initialization(self):
        """Test proper initialization of Card objects"""
        self.assertEqual(self.card1.word, self.word)
        self.assertEqual(self.card1.hidden_index, 0)
        self.assertIsNone(self.card1.is_correct_first_attempt)
    
    def test_get_prompt(self):
        """Test prompt generation (hidden syllable representation)"""
        self.assertEqual(self.card1.get_prompt(), "___-ple")
        self.assertEqual(self.card2.get_prompt(), "ap-___")
    
    def test_get_full_prompt(self):
        """Test full prompt generation with IPA and translation"""
        self.assertEqual(self.card1.get_full_prompt(), "___-ple [ˈæpəl] りんご")
        
        # Test with word without IPA and Japanese
        word_no_extra = Word("test", ["te", "st"])
        card_no_extra = Card(word_no_extra, 0)
        self.assertEqual(card_no_extra.get_full_prompt(), "___-st")
    
    def test_check_answer(self):
        """Test answer checking functionality"""
        # Test correct answer
        self.assertTrue(self.card1.check_answer("ap"))
        self.assertTrue(self.card1.is_correct_first_attempt)
        
        # Test incorrect answer
        self.assertFalse(self.card2.check_answer("wrong"))
        self.assertFalse(self.card2.is_correct_first_attempt)
        
        # Test case-insensitivity
        card3 = Card(self.word, 0)
        self.assertTrue(card3.check_answer("AP"))
        
        # Test with out-of-range hidden_index
        card_invalid = Card(self.word, 5)
        self.assertFalse(card_invalid.check_answer("anything"))


if __name__ == '__main__':
    unittest.main()