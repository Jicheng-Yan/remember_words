# English Word Memorization Application Design Document

---

## 1. Overview

The English Word Memorization Application is a Python-based tool designed to assist users in remembering English words through interactive study sessions. The application supports multiple decks, where each deck contains multiple cards representing words. Users can import decks from CSV files, select a deck and a specific number of cards for a study session, and practice spelling by typing hidden syllables. The app tracks performance statistics and provides a reset feature to allow users to restart a deck from scratch.

---

## 2. Functional Requirements

- **Deck Management:**
  - Support multiple decks, each with a unique name.
  - Allow importing decks from CSV files.
  - Provide a reset feature to clear deck progress and statistics.

- **Card Definition:**
  - Each card is derived from a word, with one or many syllables hidden during presentation (e.g., "ap-___" for "apple" with "ple" hidden).
  - Users type the hidden syllable to test their spelling.

- **Study Sessions:**
  - Users can start a session by selecting a deck and specifying the number of cards to study.
  - Cards are presented one at a time, showing the word with hidden syllables, along with American English IPA and Japanese translation (e.g., "ap-___" [ˈæpəl] りんご).
  - If the user correctly spells the hidden syllables, the card is removed from the session.
  - If incorrect, the card reappears later in the session along with remaining cards until all selected cards are correctly answered.
  - Sessions are saved automatically, allowing users to resume where they left off.

- **Statistics:**
  - Track session-specific stats:
    - **Time spent:** Total duration of the session.
    - **Studied cards:** Total number of card presentations (including repeats).
    - **Remembered cards:** Number of cards correctly answered on the first attempt.
  - Maintain cumulative stats per deck (e.g., total time, total studied cards, total remembered cards).

- **Reset Feature:**
  - Allow users to reset a deck's statistics, enabling them to start over as if the deck were new.

---

## 3. System Design

### 3.1 Classes

- **`Word`**
  - **Purpose:** Represents an English word and its syllable breakdown.
  - **Attributes:**
    - `word` (str): The full word (e.g., "apple").
    - `syllables` (list of str): List of syllables (e.g., ["ap", "ple"]).
    - `ipa` (str): American English IPA for pronunciation.
    - `japanese` (str): Japanese translation (e.g., "りんご").
  - **Methods:**
    - `get_hidden_representation(hidden_index)`: Returns the word with the specified syllable hidden (e.g., "ap-___" if `hidden_index=1`).
    - `to_dict()`: Converts the Word object to a dictionary for JSON serialization.
    - `from_dict(word_dict)`: Creates a Word object from a dictionary.

- **`Card`**
  - **Purpose:** Represents a specific instance of a word with one hidden syllable for a session.
  - **Attributes:**
    - `word` (Word): Reference to the Word object.
    - `hidden_index` (int): Index of the syllable to hide (e.g., 0 for "___-ple").
    - `is_correct_first_attempt` (bool or None): Tracks if the card was answered correctly on the first attempt.
  - **Methods:**
    - `get_prompt()`: Returns the presentation string (e.g., "ap-___").
    - `get_full_prompt()`: Returns the full prompt with IPA and Japanese translation.
    - `check_answer(user_input)`: Checks if the user's input matches the hidden syllable.

- **`Deck`**
  - **Purpose:** Manages a collection of words and associated statistics.
  - **Attributes:**
    - `name` (str): Name of the deck.
    - `words` (list of Word): List of Word objects in the deck.
    - `stats` (dict): Cumulative statistics (e.g., `{"total_time": 0, "total_sessions": 0, "total_studied": 0, "total_remembered": 0}`).
  - **Methods:**
    - `add_word(word)`: Adds a Word object to the deck.
    - `reset_stats()`: Resets the deck's statistics to initial values.
    - `to_dict()`: Converts the deck to a dictionary for JSON storage.
    - `from_dict(deck_dict)`: Creates a Deck object from a dictionary.

- **`DeckManager`**
  - **Purpose:** Handles deck creation, persistence, and importing.
  - **Attributes:**
    - `deck_dir` (str): Directory path for storing deck files (default: "decks").
  - **Methods:**
    - `create_deck(name)`: Creates a new empty deck.
    - `load_deck(name)`: Loads a deck from a JSON file.
    - `save_deck(deck)`: Saves a deck to a JSON file.
    - `list_decks()`: Returns a list of available deck names.
    - `import_deck_from_csv(csv_file, deck_name)`: Imports words from a CSV file into a new deck.

- **`Session`**
  - **Purpose:** Manages a study session with a subset of cards from a deck.
  - **Attributes:**
    - `deck` (Deck): The selected deck.
    - `num_cards` (int): Number of cards to study.
    - `cards` (list of Card): Initial list of selected cards.
    - `remaining_cards` (list of Card): Cards not yet correctly answered.
    - `studied` (int): Total number of card presentations.
    - `remembered` (int): Number of cards correct on first attempt.
    - `start_time` (float): Session start timestamp.
    - `session_file` (str): Path to the session save file.
  - **Methods:**
    - `prepare_cards()`: Prepares cards for the session, either creating new ones or loading from a saved session.
    - `run()`: Executes the study session, presenting cards until all are correctly answered.
    - `_save_session()`: Saves the current session state to a file.
    - `_load_session()`: Loads a saved session from a file.
    - `_delete_session()`: Deletes the saved session file when complete.

### 3.2 Functions

- **`split_into_syllables(word)`**
  - **Purpose:** Splits a word into its syllables using an external library (e.g., `syllables`).
  - **Input:** `word` (str): The word to split.
  - **Output:** List of syllables (e.g., ["run", "ning"] for "running").

### 3.3 Data Storage

- **Format:** Decks are stored as JSON files in a "decks" directory.
- **Structure:**
  ```json
  {
    "name": "deck_name",
    "words": [
    {"word": "apple", "syllables": ["ap", "ple"], "ipa": "ˈæpəl", "japanese": "りんご"},
    {"word": "running", "syllables": ["run", "ning"], "ipa": "ˈrʌnɪŋ", "japanese": "走ること"}
    ],
    "stats": {
      "total_time": 0,
      "total_sessions": 0,
      "total_studied": 0,
      "total_remembered": 0
    }
  }
  ```

- **Session Storage Format:**
  ```json
  {
    "deck_name": "deck_name",
    "cards": [
      {
        "word": {"word": "apple", "syllables": ["ap", "ple"], "ipa": "ˈæpəl", "japanese": "りんご"},
        "hidden_index": 1,
        "is_correct_first_attempt": null
      }
    ],
    "remaining_indices": [0],
    "studied": 0,
    "start_time": 1618225678.9
  }
  ```

- **CSV Import Format:**
    - Three-column CSV with a header:
        ```
        word,IPA,japanese
        apple,ˈæpəl,りんご
        running,ˈrʌnɪŋ,走ること
        computer,kəmˈpjuːtər,コンピュータ
        ```

---

## 4. User Interface

- **Type:** Command-line interface (CLI).
- **Main Menu:**
  ```
  1. List decks
  2. Create new deck
  3. Import deck from CSV
  4. Start session
  5. Reset deck
  6. Exit
  ```
- **Session Interaction:**
  - Prompt example: `Card: ap-___`
  - User input: `ple`
  - Feedback: `Correct!` or `Incorrect. Try again later.`
  - Users can type 'exit' to save and exit the session.

---

## 5. Workflow

1. **Main Loop:**
   - Display the menu and accept user input.
   - Route to appropriate functionality based on selection.

2. **Deck Creation/Import:**
   - Create: User enters a deck name; an empty deck is saved.
   - Import: User provides a CSV file path and deck name; words are imported, split into syllables, and saved.

3. **Study Session:**
   - User selects a deck and number of cards (`k`).
   - If a saved session exists, it's resumed; otherwise, `k` random (word, hidden_syllable) pairs are selected as cards.
   - Cards are presented in a random order:
     - Show prompt (e.g., "run-___").
     - Accept user input.
     - If correct, remove card; if incorrect, keep it for later.
   - Users can exit at any time, and session progress is saved.
   - Continue until all cards are correctly answered or the user exits.
   - Display session stats and update deck stats.

4. **Reset Deck:**
   - User selects a deck; its stats are reset to zero and saved.

---

## 6. Technical Considerations

- **Syllable Splitting:** Utilize a library like `syllables` for accurate syllable division. Fallback to manual rules if needed.
- **Randomization:** Use Python's `random.sample` and `random.choice` for card selection and presentation order.
- **Persistence:** JSON files ensure simple, human-readable storage.
- **Session Persistence:** Save session state to allow users to resume progress.
- **Error Handling:**
  - Validate CSV file format and existence.
  - Ensure sufficient cards are available for the requested session size.
  - Handle invalid menu inputs gracefully.

---

## 7. Future Enhancements

- **Graphical User Interface (GUI):** Replace CLI with a visual interface using Tkinter or PyQt.
- **Audio Support:** Add pronunciation playback for words.
- **Advanced Stats:** Track per-word performance or difficulty levels.
- **Export Feature:** Allow exporting deck stats or progress.

---

This design document outlines a robust and extensible Python application for English word memorization, meeting all specified requirements with a clear structure for implementation.