#!/usr/bin/env python3

import json
import os
import csv
import random
import logging
from .word import Word

logger = logging.getLogger(__name__)

class Deck:
    """
    Manages a collection of words and associated statistics.
    """
    
    def __init__(self, name, words=None, stats=None):
        """
        Initialize a Deck object.
        
        Args:
            name (str): Name of the deck.
            words (list, optional): List of Word objects in the deck.
            stats (dict, optional): Cumulative statistics for the deck.
        """
        logger.info(f"Creating Deck: {name}")
        logger.debug(f"Initial words count: {len(words) if words else 0}")
        self.name = name
        self.words = words or []
        self.stats = stats or {
            "total_time": 0,
            "total_sessions": 0,
            "total_studied": 0,
            "total_remembered": 0
        }
        logger.debug(f"Initial stats: {self.stats}")
    
    def add_word(self, word):
        """
        Adds a Word object to the deck.
        
        Args:
            word (Word): Word object to add.
        """
        logger.info(f"Adding word '{word.word}' to deck '{self.name}'")
        self.words.append(word)
        logger.debug(f"Deck '{self.name}' now has {len(self.words)} words")
    
    def reset_stats(self):
        """
        Resets the deck's statistics to initial values.
        """
        logger.info(f"Resetting stats for deck '{self.name}'")
        logger.debug(f"Old stats: {self.stats}")
        self.stats = {
            "total_time": 0,
            "total_sessions": 0,
            "total_studied": 0,
            "total_remembered": 0
        }
        logger.debug(f"New stats: {self.stats}")
    
    def to_dict(self):
        """
        Converts the deck to a dictionary for JSON storage.
        
        Returns:
            dict: Dictionary representation of the deck.
        """
        logger.debug(f"Converting deck '{self.name}' to dictionary")
        return {
            "name": self.name,
            "words": [word.to_dict() for word in self.words],
            "stats": self.stats
        }
    
    @classmethod
    def from_dict(cls, deck_dict):
        """
        Create a Deck object from a dictionary.
        
        Args:
            deck_dict (dict): Dictionary containing deck data.
            
        Returns:
            Deck: A new Deck object.
        """
        logger.debug(f"Creating Deck from dictionary: {deck_dict['name']}")
        words = [Word.from_dict(word_dict) for word_dict in deck_dict.get("words", [])]
        deck = cls(
            name=deck_dict["name"],
            words=words,
            stats=deck_dict.get("stats", None)
        )
        logger.info(f"Created deck '{deck.name}' with {len(deck.words)} words")
        return deck


class DeckManager:
    """
    Handles deck creation, persistence, and importing.
    """
    
    def __init__(self, deck_dir="decks"):
        """
        Initialize a DeckManager object.
        
        Args:
            deck_dir (str): Directory path for storing deck files.
        """
        logger.info(f"Initializing DeckManager with directory: {deck_dir}")
        self.deck_dir = deck_dir
        os.makedirs(deck_dir, exist_ok=True)
        logger.debug(f"Ensuring deck directory exists: {deck_dir}")
    
    def create_deck(self, name):
        """
        Creates a new empty deck.
        
        Args:
            name (str): Name for the new deck.
            
        Returns:
            Deck: The newly created deck.
            
        Raises:
            ValueError: If a deck with the same name already exists.
        """
        logger.info(f"Creating new deck: {name}")
        if self._deck_exists(name):
            logger.warning(f"Attempt to create existing deck: {name}")
            raise ValueError(f"Deck '{name}' already exists.")
            
        deck = Deck(name)
        self.save_deck(deck)
        logger.info(f"Created and saved new empty deck: {name}")
        return deck
    
    def load_deck(self, name):
        """
        Loads a deck from a JSON file.
        
        Args:
            name (str): Name of the deck to load.
            
        Returns:
            Deck: The loaded deck.
            
        Raises:
            FileNotFoundError: If the deck file doesn't exist.
        """
        logger.info(f"Loading deck: {name}")
        file_path = self._get_deck_path(name)
        
        if not os.path.exists(file_path):
            logger.error(f"Deck file not found: {file_path}")
            raise FileNotFoundError(f"Deck '{name}' not found.")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            logger.debug(f"Reading deck file: {file_path}")
            deck_dict = json.load(f)
            
        deck = Deck.from_dict(deck_dict)
        logger.info(f"Successfully loaded deck '{name}' with {len(deck.words)} words")
        return deck
    
    def save_deck(self, deck):
        """
        Saves a deck to a JSON file.
        
        Args:
            deck (Deck): The deck to save.
        """
        logger.info(f"Saving deck: {deck.name}")
        file_path = self._get_deck_path(deck.name)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            logger.debug(f"Writing deck to file: {file_path}")
            json.dump(deck.to_dict(), f, ensure_ascii=False, indent=2)
        
        logger.info(f"Successfully saved deck '{deck.name}'")
    
    def list_decks(self):
        """
        Returns a list of available deck names.
        
        Returns:
            list: List of deck names.
        """
        logger.debug("Listing available decks")
        try:
            files = [f for f in os.listdir(self.deck_dir) if f.endswith('.json')]
            deck_names = [os.path.splitext(f)[0] for f in files]
            logger.info(f"Found {len(deck_names)} decks: {deck_names}")
            return deck_names
        except FileNotFoundError:
            logger.warning(f"Deck directory not found: {self.deck_dir}")
            return []
    
    def import_deck_from_csv(self, csv_file, deck_name):
        """
        Imports words from a CSV file into a new deck.
        
        Args:
            csv_file (str): Path to the CSV file.
            deck_name (str): Name for the new deck.
            
        Returns:
            Deck: The newly created deck.
            
        Raises:
            ValueError: If the deck already exists or the CSV format is invalid.
            FileNotFoundError: If the CSV file doesn't exist.
        """
        logger.info(f"Importing deck from CSV: {csv_file} -> {deck_name}")
        
        if self._deck_exists(deck_name):
            logger.warning(f"Attempt to import to existing deck: {deck_name}")
            raise ValueError(f"Deck '{deck_name}' already exists.")
            
        if not os.path.exists(csv_file):
            logger.error(f"CSV file not found: {csv_file}")
            raise FileNotFoundError(f"CSV file '{csv_file}' not found.")
            
        deck = Deck(deck_name)
        word_count = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                logger.debug(f"Reading CSV file: {csv_file}")
                reader = csv.DictReader(f)
                
                # Validate CSV columns
                required_fields = ['word']
                for field in required_fields:
                    if field not in reader.fieldnames:
                        logger.error(f"Required field missing in CSV: {field}")
                        raise ValueError(f"CSV file must contain a '{field}' column.")
                
                for row in reader:
                    word_text = row['word'].strip()
                    if not word_text:
                        logger.warning("Skipping empty word in CSV")
                        continue
                        
                    syllables = self._split_into_syllables(word_text)
                    ipa = row.get('IPA', '').strip()
                    japanese = row.get('japanese', '').strip()
                    
                    word = Word(word_text, syllables, ipa, japanese)
                    deck.add_word(word)
                    word_count += 1
                    
            logger.info(f"Successfully imported {word_count} words to deck '{deck_name}'")
            self.save_deck(deck)
            return deck
            
        except Exception as e:
            logger.error(f"Error importing CSV: {str(e)}")
            raise ValueError(f"Error importing CSV: {str(e)}")
    
    def _deck_exists(self, name):
        """
        Checks if a deck with the given name exists.
        
        Args:
            name (str): Name of the deck.
            
        Returns:
            bool: True if the deck exists, False otherwise.
        """
        exists = os.path.exists(self._get_deck_path(name))
        logger.debug(f"Checking if deck exists: {name} -> {exists}")
        return exists
    
    def _get_deck_path(self, name):
        """
        Returns the file path for a deck with the given name.
        
        Args:
            name (str): Name of the deck.
            
        Returns:
            str: File path for the deck.
        """
        path = os.path.join(self.deck_dir, f"{name}.json")
        logger.debug(f"Deck path for '{name}': {path}")
        return path
    
    def _split_into_syllables(self, word):
        """
        Splits a word into syllables.
        
        Args:
            word (str): The word to split.
            
        Returns:
            list: List of syllables.
        """
        logger.debug(f"Splitting word into syllables: {word}")
        # Try to use syllables library if available
        try:
            import syllables
            result = syllables.get_syllables(word)
            logger.debug(f"Syllables from library: {result}")
            return result
        except ImportError:
            logger.info("Syllables library not available, using fallback method")
            # Fallback to a simple split at hyphens if present
            if '-' in word:
                result = word.split('-')
                logger.debug(f"Split by hyphen: {result}")
                return result
            # Very basic fallback syllable estimation
            vowels = 'aeiouy'
            syllables = []
            current = ""
            
            for i, char in enumerate(word.lower()):
                current += char
                
                # Check if we should split here
                if (char in vowels and 
                    (i == len(word) - 1 or word[i+1] not in vowels) and
                    len(current) >= 2):
                    syllables.append(current)
                    current = ""
            
            # Add any remaining characters
            if current:
                if syllables:
                    syllables[-1] += current
                else:
                    syllables.append(current)
                    
            # If we couldn't split, just use the whole word
            result = syllables if syllables else [word]
            logger.debug(f"Syllables from fallback method: {result}")
            return result