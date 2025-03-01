#!/usr/bin/env python3
import json
import os
import csv
import random
from .word import Word

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
        self.name = name
        self.words = words or []
        self.stats = stats or {
            "total_time": 0,
            "total_sessions": 0,
            "total_studied": 0,
            "total_remembered": 0
        }
    
    def add_word(self, word):
        """
        Adds a Word object to the deck.
        
        Args:
            word (Word): Word object to add.
        """
        self.words.append(word)
    
    def reset_stats(self):
        """
        Resets the deck's statistics to initial values.
        """
        self.stats = {
            "total_time": 0,
            "total_sessions": 0,
            "total_studied": 0,
            "total_remembered": 0
        }
    
    def to_dict(self):
        """
        Converts the deck to a dictionary for JSON storage.
        
        Returns:
            dict: Dictionary representation of the deck.
        """
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
        words = [Word.from_dict(word_dict) for word_dict in deck_dict.get("words", [])]
        return cls(
            name=deck_dict["name"],
            words=words,
            stats=deck_dict.get("stats", None)
        )


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
        self.deck_dir = deck_dir
        os.makedirs(deck_dir, exist_ok=True)
    
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
        if self._deck_exists(name):
            raise ValueError(f"Deck '{name}' already exists.")
            
        deck = Deck(name)
        self.save_deck(deck)
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
        file_path = self._get_deck_path(name)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Deck '{name}' not found.")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            deck_dict = json.load(f)
            
        return Deck.from_dict(deck_dict)
    
    def save_deck(self, deck):
        """
        Saves a deck to a JSON file.
        
        Args:
            deck (Deck): The deck to save.
        """
        file_path = self._get_deck_path(deck.name)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(deck.to_dict(), f, ensure_ascii=False, indent=2)
    
    def list_decks(self):
        """
        Returns a list of available deck names.
        
        Returns:
            list: List of deck names.
        """
        try:
            files = [f for f in os.listdir(self.deck_dir) if f.endswith('.json')]
            return [os.path.splitext(f)[0] for f in files]
        except FileNotFoundError:
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
        if self._deck_exists(deck_name):
            raise ValueError(f"Deck '{deck_name}' already exists.")
            
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV file '{csv_file}' not found.")
            
        deck = Deck(deck_name)
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Validate CSV columns
                required_fields = ['word']
                for field in required_fields:
                    if field not in reader.fieldnames:
                        raise ValueError(f"CSV file must contain a '{field}' column.")
                
                for row in reader:
                    word_text = row['word'].strip()
                    if not word_text:
                        continue
                        
                    syllables = self._split_into_syllables(word_text)
                    ipa = row.get('IPA', '').strip()
                    japanese = row.get('japanese', '').strip()
                    
                    word = Word(word_text, syllables, ipa, japanese)
                    deck.add_word(word)
        except Exception as e:
            raise ValueError(f"Error importing CSV: {str(e)}")
            
        self.save_deck(deck)
        return deck
    
    def _deck_exists(self, name):
        """
        Checks if a deck with the given name exists.
        
        Args:
            name (str): Name of the deck.
            
        Returns:
            bool: True if the deck exists, False otherwise.
        """
        return os.path.exists(self._get_deck_path(name))
    
    def _get_deck_path(self, name):
        """
        Returns the file path for a deck with the given name.
        
        Args:
            name (str): Name of the deck.
            
        Returns:
            str: File path for the deck.
        """
        return os.path.join(self.deck_dir, f"{name}.json")
    
    def _split_into_syllables(self, word):
        """
        Splits a word into syllables.
        
        Args:
            word (str): The word to split.
            
        Returns:
            list: List of syllables.
        """
        # Try to use syllables library if available
        try:
            import syllables
            return syllables.get_syllables(word)
        except ImportError:
            # Fallback to a simple split at hyphens if present
            if '-' in word:
                return word.split('-')
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
            return syllables if syllables else [word]