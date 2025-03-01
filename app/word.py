#!/usr/bin/env python3

class Word:
    """
    Represents an English word and its syllable breakdown.
    """
    
    def __init__(self, word, syllables=None, ipa="", japanese=""):
        """
        Initialize a Word object.
        
        Args:
            word (str): The full word (e.g., "apple").
            syllables (list of str, optional): List of syllables (e.g., ["ap", "ple"]).
            ipa (str, optional): American English IPA for pronunciation.
            japanese (str, optional): Japanese translation.
        """
        self.word = word
        self.syllables = syllables or []
        self.ipa = ipa
        self.japanese = japanese
    
    def get_hidden_representation(self, hidden_index):
        """
        Returns the word with the specified syllable hidden.
        
        Args:
            hidden_index (int): Index of the syllable to hide.
            
        Returns:
            str: Word with the specified syllable hidden (e.g., "ap-___").
        """
        if not self.syllables or hidden_index >= len(self.syllables):
            return f"{self.word}-___"
            
        hidden_repr = []
        for i, syllable in enumerate(self.syllables):
            if i == hidden_index:
                hidden_repr.append("___")
            else:
                hidden_repr.append(syllable)
                
        return "-".join(hidden_repr)
    
    def to_dict(self):
        """
        Convert the Word object to a dictionary for JSON serialization.
        
        Returns:
            dict: Dictionary representation of the Word.
        """
        return {
            "word": self.word,
            "syllables": self.syllables,
            "ipa": self.ipa,
            "japanese": self.japanese
        }
    
    @classmethod
    def from_dict(cls, word_dict):
        """
        Create a Word object from a dictionary.
        
        Args:
            word_dict (dict): Dictionary containing word data.
            
        Returns:
            Word: A new Word object.
        """
        return cls(
            word=word_dict["word"],
            syllables=word_dict.get("syllables", []),
            ipa=word_dict.get("ipa", ""),
            japanese=word_dict.get("japanese", "")
        )


class Card:
    """
    Represents a specific instance of a word with one hidden syllable for a session.
    """
    
    def __init__(self, word, hidden_index):
        """
        Initialize a Card object.
        
        Args:
            word (Word): Reference to the Word object.
            hidden_index (int): Index of the syllable to hide.
        """
        self.word = word
        self.hidden_index = hidden_index
        self.is_correct_first_attempt = None
    
    def get_prompt(self):
        """
        Returns the presentation string (e.g., "ap-___").
        
        Returns:
            str: The word with the hidden syllable.
        """
        return self.word.get_hidden_representation(self.hidden_index)
    
    def get_full_prompt(self):
        """
        Returns the full prompt with IPA and Japanese translation.
        
        Returns:
            str: Formatted prompt with hidden syllable, IPA, and Japanese.
        """
        prompt = self.get_prompt()
        details = []
        
        if self.word.ipa:
            details.append(f"[{self.word.ipa}]")
        
        if self.word.japanese:
            details.append(self.word.japanese)
            
        details_str = " ".join(details)
        return f"{prompt} {details_str}" if details_str else prompt
    
    def check_answer(self, user_input):
        """
        Checks if the user's input matches the hidden syllable.
        
        Args:
            user_input (str): The user's answer.
            
        Returns:
            bool: True if the answer is correct, False otherwise.
        """
        if not self.word.syllables or self.hidden_index >= len(self.word.syllables):
            return False
            
        correct = user_input.strip().lower() == self.word.syllables[self.hidden_index].lower()
        
        # Set first attempt flag if not already set
        if self.is_correct_first_attempt is None:
            self.is_correct_first_attempt = correct
            
        return correct