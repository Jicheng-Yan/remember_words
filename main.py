#!/usr/bin/env python3

import os
import sys
from app.deck import Deck, DeckManager
from app.session import Session

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    clear_screen()
    print("=" * 50)
    print("   English Word Memorization Application   ")
    print("=" * 50)
    print()

def print_menu():
    """Print the main menu options."""
    print("\nMain Menu:")
    print("1. List decks")
    print("2. Create new deck")
    print("3. Import deck from CSV")
    print("4. Start session")
    print("5. Reset deck")
    print("6. Exit")

def list_decks(deck_manager):
    """
    List all available decks.
    
    Args:
        deck_manager (DeckManager): The deck manager instance.
    """
    print_header()
    print("Available Decks:")
    
    deck_names = deck_manager.list_decks()
    if not deck_names:
        print("No decks available. Create or import a deck first.")
        return
        
    for i, name in enumerate(deck_names, 1):
        try:
            deck = deck_manager.load_deck(name)
            words_count = len(deck.words)
            sessions_count = deck.stats["total_sessions"]
            print(f"{i}. {name} ({words_count} words, {sessions_count} sessions)")
        except Exception as e:
            print(f"{i}. {name} (Error loading deck: {e})")
            
    print()
    input("Press Enter to continue...")

def create_deck(deck_manager):
    """
    Create a new empty deck.
    
    Args:
        deck_manager (DeckManager): The deck manager instance.
    """
    print_header()
    print("Create New Deck")
    
    name = input("Enter deck name: ").strip()
    if not name:
        print("Deck name cannot be empty.")
        input("Press Enter to continue...")
        return
        
    try:
        deck = deck_manager.create_deck(name)
        print(f"Deck '{name}' created successfully.")
    except ValueError as e:
        print(f"Error: {e}")
        
    input("Press Enter to continue...")

def import_deck(deck_manager):
    """
    Import a deck from a CSV file.
    
    Args:
        deck_manager (DeckManager): The deck manager instance.
    """
    print_header()
    print("Import Deck from CSV")
    print("CSV format should have columns: word,IPA,japanese")
    
    csv_file = input("Enter CSV file path: ").strip()
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found.")
        input("Press Enter to continue...")
        return
        
    name = input("Enter deck name: ").strip()
    if not name:
        print("Deck name cannot be empty.")
        input("Press Enter to continue...")
        return
        
    try:
        deck = deck_manager.import_deck_from_csv(csv_file, name)
        print(f"Deck '{name}' imported successfully with {len(deck.words)} words.")
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        
    input("Press Enter to continue...")

def start_session(deck_manager):
    """
    Start a study session with a selected deck.
    
    Args:
        deck_manager (DeckManager): The deck manager instance.
    """
    print_header()
    print("Start Session")
    
    deck_names = deck_manager.list_decks()
    if not deck_names:
        print("No decks available. Create or import a deck first.")
        input("Press Enter to continue...")
        return
        
    print("Available Decks:")
    for i, name in enumerate(deck_names, 1):
        print(f"{i}. {name}")
        
    choice = input("\nSelect deck (number): ").strip()
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(deck_names):
            raise ValueError("Invalid selection")
            
        deck_name = deck_names[idx]
        deck = deck_manager.load_deck(deck_name)
    except (ValueError, IndexError):
        print("Invalid selection.")
        input("Press Enter to continue...")
        return
        
    if not deck.words:
        print(f"Deck '{deck_name}' is empty. Add words before starting a session.")
        input("Press Enter to continue...")
        return
        
    num_cards = input(f"Enter number of cards to study (max {len(deck.words)}): ").strip()
    try:
        num_cards = int(num_cards)
        if num_cards <= 0:
            raise ValueError("Number of cards must be positive")
            
        if num_cards > len(deck.words):
            print(f"Limiting to {len(deck.words)} cards (all available).")
            num_cards = len(deck.words)
    except ValueError:
        print("Invalid number, using all available cards.")
        num_cards = len(deck.words)
        
    # Run the session
    session = Session(deck, num_cards)
    session.run()
    
    # Save updated deck stats
    deck_manager.save_deck(deck)
    
    input("Press Enter to continue...")

def reset_deck(deck_manager):
    """
    Reset statistics for a selected deck.
    
    Args:
        deck_manager (DeckManager): The deck manager instance.
    """
    print_header()
    print("Reset Deck")
    
    deck_names = deck_manager.list_decks()
    if not deck_names:
        print("No decks available.")
        input("Press Enter to continue...")
        return
        
    print("Available Decks:")
    for i, name in enumerate(deck_names, 1):
        print(f"{i}. {name}")
        
    choice = input("\nSelect deck to reset (number): ").strip()
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(deck_names):
            raise ValueError("Invalid selection")
            
        deck_name = deck_names[idx]
        deck = deck_manager.load_deck(deck_name)
    except (ValueError, IndexError):
        print("Invalid selection.")
        input("Press Enter to continue...")
        return
        
    confirm = input(f"Are you sure you want to reset all statistics for deck '{deck_name}'? (y/n): ").strip().lower()
    if confirm == 'y':
        deck.reset_stats()
        deck_manager.save_deck(deck)
        print(f"Deck '{deck_name}' has been reset.")
    else:
        print("Reset cancelled.")
        
    input("Press Enter to continue...")

def main():
    """Main application function."""
    # Initialize the deck manager
    deck_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "decks")
    deck_manager = DeckManager(deck_dir)
    
    while True:
        print_header()
        print_menu()
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            list_decks(deck_manager)
        elif choice == '2':
            create_deck(deck_manager)
        elif choice == '3':
            import_deck(deck_manager)
        elif choice == '4':
            start_session(deck_manager)
        elif choice == '5':
            reset_deck(deck_manager)
        elif choice == '6':
            print_header()
            print("Thank you for using the English Word Memorization Application!")
            break
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
        sys.exit(0)