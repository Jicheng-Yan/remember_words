#!/usr/bin/env python3
import logging
from itertools import zip_longest

logger = logging.getLogger(__name__)

class Word:
    """
    Represents an English word and its syllable breakdown.
    """
    
    def __init__(self, word, syllables=None, ipa="", japanese=""):
        """Initialize a Word object."""
        logger.info(f"Creating Word object: {word}")
        logger.debug(f"Word details - syllables: {syllables}, IPA: {ipa}, Japanese: {japanese}")
        self.word = word
        self.syllables = syllables or []
        self.ipa = ipa
        self.japanese = japanese
    
    def get_hidden_representation(self, hidden_index):
        """Returns the word with the specified syllable hidden."""
        logger.debug(f"Getting hidden representation for {self.word} with hidden_index {hidden_index}")
        if not self.syllables or hidden_index >= len(self.syllables):
            logger.warning(f"Invalid hidden_index {hidden_index} for word {self.word}")
            return f"{self.word}-___"
            
        hidden_repr = []
        for i, syllable in enumerate(self.syllables):
            if i == hidden_index:
                hidden_repr.append("___")
            else:
                hidden_repr.append(syllable)
        result = "-".join(hidden_repr)
        logger.debug(f"Hidden representation: {result}")
        return result
    
    def to_dict(self):
        """Convert the Word object to a dictionary for JSON serialization."""
        logger.debug(f"Converting word {self.word} to dictionary")
        return {
            "word": self.word,
            "syllables": self.syllables,
            "ipa": self.ipa,
            "japanese": self.japanese
        }
    
    @classmethod
    def from_dict(cls, word_dict):
        """Create a Word object from a dictionary."""
        logger.debug(f"Creating Word from dictionary: {word_dict}")
        return cls(
            word=word_dict["word"],
            syllables=word_dict.get("syllables", []),
            ipa=word_dict.get("ipa", ""),
            japanese=word_dict.get("japanese", "")
        )


class Card:
    """Represents a specific instance of a word with one hidden syllable for a session."""
    
    def __init__(self, word, hidden_index):
        """Initialize a Card object."""
        logger.info(f"Creating Card for word '{word.word}' with hidden_index {hidden_index}")
        self.word = word
        self.hidden_index = hidden_index
        self.is_correct_first_attempt = None
    
    def get_prompt(self):
        """Returns the presentation string."""
        logger.debug(f"Getting prompt for card with word '{self.word.word}'")
        return self.word.get_hidden_representation(self.hidden_index)
    
    def get_full_prompt(self):
        """Returns the full prompt with IPA and Japanese translation."""
        logger.debug(f"Getting full prompt for card with word '{self.word.word}'")
        prompt = self.get_prompt()
        details = []
        
        if self.word.ipa:
            details.append(f"[{self.word.ipa}]")
        
        if self.word.japanese:
            details.append(self.word.japanese)
            
        details_str = " ".join(details)
        result = f"{prompt} {details_str}" if details_str else prompt
        logger.debug(f"Full prompt: {result}")
        return result
    
    def check_answer(self, user_input):
        """
        Checks if the user's input matches the hidden syllable.
        
        Args:
            user_input (str): The user's answer.
            
        Returns:
            tuple: (bool, list) where bool indicates if answer is correct and list contains
                  tuples of (status, char) where status is one of:
                  'correct': character matches
                  'wrong': character doesn't match
                  'extra': extra character in input
                  'missing': missing character from correct answer
        """
        logger.info(f"Checking answer for word '{self.word.word}': {user_input}")
        if not self.word.syllables or self.hidden_index >= len(self.word.syllables):
            logger.warning(f"Invalid syllables or hidden_index for word '{self.word.word}'")
            return False, []
            
        correct_syllable = self.word.syllables[self.hidden_index].lower()
        user_input = user_input.strip().lower()
        
        # Compare character by character and create feedback
        feedback = []
        
        # Mark all characters up to the length of the longer string as wrong unless they match
        max_length = max(len(correct_syllable), len(user_input))
        for i in range(max_length):
            if i >= len(user_input):
                # Missing character from correct answer
                feedback.append(('missing', correct_syllable[i]))
            elif i >= len(correct_syllable):
                # Extra characters in user input
                feedback.append(('extra', user_input[i]))
            else:
                # Both strings have characters at this position
                if correct_syllable[i] == user_input[i]:
                    feedback.append(('correct', user_input[i]))
                else:
                    feedback.append(('wrong', user_input[i]))
        
        correct = user_input == correct_syllable
        
        # Set first attempt flag if not already set
        if self.is_correct_first_attempt is None:
            self.is_correct_first_attempt = correct
            logger.info(f"First attempt for word '{self.word.word}': {'correct' if correct else 'incorrect'}")
        
        logger.debug(f"Answer check result: {correct}, feedback: {feedback}")
        return correct, feedback