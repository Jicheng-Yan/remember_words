#!/usr/bin/env python3

import time
import random
import json
import os
import logging
from .word import Card

logger = logging.getLogger(__name__)

class Session:
    """
    Manages a study session with a subset of cards from a deck.
    """
    
    def __init__(self, deck, num_cards=None):
        """
        Initialize a Session object.
        
        Args:
            deck: The selected deck.
            num_cards (int, optional): Number of cards to study.
        """
        logger.info(f"Creating new session for deck '{deck.name}'")
        self.deck = deck
        self.num_cards = num_cards or len(deck.words)
        self.num_cards = min(self.num_cards, len(deck.words))
        logger.debug(f"Session initialized with {self.num_cards} cards")
        
        self.cards = []
        self.remaining_cards = []
        self.studied = 0
        self.remembered = 0
        self.start_time = 0
        self.session_file = os.path.join("decks", f"{deck.name}_session.json")
    
    def prepare_cards(self):
        """
        Prepare cards for the session, either by creating new cards or loading from a saved session.
        """
        logger.info("Preparing cards for session")
        if self._load_session():
            return
            
        logger.debug("No saved session found, creating new cards")
        selected_words = random.sample(self.deck.words, self.num_cards) if self.num_cards < len(self.deck.words) else self.deck.words
        logger.debug(f"Selected {len(selected_words)} words for session")
        
        for word in selected_words:
            # For each word, randomly select a syllable to hide
            if word.syllables:
                hidden_index = random.randint(0, len(word.syllables) - 1)
                card = Card(word, hidden_index)
                self.cards.append(card)
                self.remaining_cards.append(card)
                logger.debug(f"Created card for word '{word.word}' with hidden index {hidden_index}")
        
        logger.info(f"Session prepared with {len(self.cards)} cards")
    
    def run(self):
        """
        Executes the study session, presenting cards until all are correctly answered.
        
        Returns:
            dict: Session statistics.
        """
        logger.info("Starting session")
        self.prepare_cards()
        if not self.remaining_cards:
            logger.warning("No cards available for session")
            print("No cards available for this session.")
            return None
            
        self.start_time = time.time()
        logger.debug(f"Session start time: {self.start_time}")
        
        print(f"\nStarting session with {len(self.remaining_cards)} cards from deck '{self.deck.name}'")
        print("For each card, type the missing syllable (___)")
        print("Type 'exit' to save and exit the session")
        print("-" * 50)
        
        try:
            while self.remaining_cards:
                # Get a random card from remaining cards
                current_card = random.choice(self.remaining_cards)
                logger.debug(f"Selected card: {current_card.word.word}")
                
                # Present the card
                print(f"\nCard: {current_card.get_full_prompt()}")
                user_input = input("Your answer (or 'exit'): ").strip()
                
                if user_input.lower() == 'exit':
                    logger.info("User requested to exit session")
                    self._save_session()
                    print("\nSession saved. You can continue later.")
                    break
                    
                self.studied += 1
                logger.debug(f"Cards studied this session: {self.studied}")
                
                # Check the answer
                if current_card.check_answer(user_input):
                    print("Correct!")
                    self.remaining_cards.remove(current_card)
                    logger.info(f"Correct answer for '{current_card.word.word}'. {len(self.remaining_cards)} cards remaining")
                else:
                    correct_syllable = current_card.word.syllables[current_card.hidden_index]
                    print(f"Incorrect. The correct answer was: {correct_syllable}")
                    logger.info(f"Incorrect answer for '{current_card.word.word}'. Expected: {correct_syllable}, Got: {user_input}")
                    # The card stays in the remaining cards
        except KeyboardInterrupt:
            logger.warning("Session interrupted by user")
            print("\nSession interrupted.")
            self._save_session()
            print("Session saved. You can continue later.")
            
        session_stats = self._calculate_stats()
        logger.debug(f"Session stats: {session_stats}")
        
        if not self.remaining_cards:
            logger.info("Session completed successfully")
            print("\nCongratulations! You've completed the session.")
            # Delete saved session if complete
            self._delete_session()
            
        self._update_deck_stats(session_stats)
        self._display_stats(session_stats)
        
        return session_stats
    
    def _calculate_stats(self):
        """
        Calculate session statistics.
        
        Returns:
            dict: Session statistics.
        """
        logger.debug("Calculating session statistics")
        elapsed_time = time.time() - self.start_time
        
        remembered = sum(1 for card in self.cards if card.is_correct_first_attempt)
        
        stats = {
            "time_spent": elapsed_time,
            "studied_cards": self.studied,
            "remembered_cards": remembered,
            "total_cards": len(self.cards)
        }
        logger.debug(f"Calculated stats: {stats}")
        return stats
    
    def _update_deck_stats(self, session_stats):
        """
        Update deck statistics based on session results.
        
        Args:
            session_stats (dict): Session statistics.
        """
        logger.info("Updating deck statistics")
        logger.debug(f"Previous deck stats: {self.deck.stats}")
        
        self.deck.stats["total_time"] += session_stats["time_spent"]
        self.deck.stats["total_sessions"] += 1
        self.deck.stats["total_studied"] += session_stats["studied_cards"]
        self.deck.stats["total_remembered"] += session_stats["remembered_cards"]
        
        logger.debug(f"Updated deck stats: {self.deck.stats}")
    
    def _display_stats(self, stats):
        """
        Display session statistics.
        
        Args:
            stats (dict): Session statistics.
        """
        logger.debug("Displaying session statistics")
        print("\nSession Statistics:")
        print(f"Time spent: {self._format_time(stats['time_spent'])}")
        print(f"Cards studied: {stats['studied_cards']}")
        print(f"Cards remembered on first attempt: {stats['remembered_cards']} out of {stats['total_cards']} ({self._calculate_percentage(stats['remembered_cards'], stats['total_cards'])}%)")
    
    def _format_time(self, seconds):
        """
        Format seconds into a readable time string.
        
        Args:
            seconds (float): Time in seconds.
            
        Returns:
            str: Formatted time string.
        """
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def _calculate_percentage(self, part, total):
        """
        Calculate percentage.
        
        Args:
            part (int): Part value.
            total (int): Total value.
            
        Returns:
            int: Percentage value.
        """
        return int(part / total * 100) if total > 0 else 0
    
    def _save_session(self):
        """
        Save the current session state to a file.
        """
        logger.info(f"Saving session to file: {self.session_file}")
        session_data = {
            "deck_name": self.deck.name,
            "cards": [{
                "word": card.word.to_dict(),
                "hidden_index": card.hidden_index,
                "is_correct_first_attempt": card.is_correct_first_attempt
            } for card in self.cards],
            "remaining_indices": [self.cards.index(card) for card in self.remaining_cards],
            "studied": self.studied,
            "start_time": self.start_time
        }
        
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            logger.info("Session saved successfully")
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            raise
    
    def _load_session(self):
        """
        Load a saved session from a file.
        
        Returns:
            bool: True if session was loaded, False otherwise.
        """
        logger.info(f"Attempting to load saved session from: {self.session_file}")
        
        if not os.path.exists(self.session_file):
            logger.debug("No saved session file found")
            return False
            
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                
            # Verify the session is for the current deck
            if session_data["deck_name"] != self.deck.name:
                logger.warning(f"Session file exists but for different deck: {session_data['deck_name']}")
                return False
                
            # Reconstruct cards
            from .word import Word
            self.cards = []
            
            for card_data in session_data["cards"]:
                word = Word.from_dict(card_data["word"])
                card = Card(word, card_data["hidden_index"])
                card.is_correct_first_attempt = card_data["is_correct_first_attempt"]
                self.cards.append(card)
                
            # Reconstruct remaining cards
            self.remaining_cards = [self.cards[i] for i in session_data["remaining_indices"]]
            self.studied = session_data["studied"]
            self.start_time = session_data["start_time"]
            
            # Adjust num_cards based on loaded session
            self.num_cards = len(self.cards)
            
            logger.info(f"Successfully loaded session with {len(self.remaining_cards)} remaining cards")
            print(f"Resuming saved session with {len(self.remaining_cards)} remaining cards.")
            return True
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            print(f"Error loading session: {e}")
            return False
    
    def _delete_session(self):
        """
        Delete the saved session file.
        """
        logger.info(f"Deleting session file: {self.session_file}")
        if os.path.exists(self.session_file):
            try:
                os.remove(self.session_file)
                logger.info("Session file deleted successfully")
            except Exception as e:
                logger.error(f"Error deleting session file: {e}")
                raise