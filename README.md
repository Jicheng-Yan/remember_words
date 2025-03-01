# English Word Memorization Application

A Python-based command-line tool designed to help users memorize English words through interactive study sessions with a focus on syllable-based learning.

## Overview

This application helps users practice and memorize English words by presenting them with partially hidden words where one syllable is replaced with blanks. Users need to guess the hidden syllable to complete the word. The application supports multiple decks, tracks learning progress, and provides a simple yet effective way to improve vocabulary retention.

## Features

- **Multiple Deck Management**: Create and manage multiple word decks
- **CSV Import**: Easily import words from CSV files with IPA pronunciation and translations
- **Syllable-based Learning**: Practice by guessing hidden syllables of words
- **Progress Tracking**: Statistics track your learning progress over time
- **Session Persistence**: Sessions can be saved and resumed later
- **IPA and Translation Support**: Words can include IPA pronunciation and Japanese translations

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/remembering_words.git
   cd remembering_words
   ```

2. (Optional) Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. (Optional) Install the `syllables` library for better syllable splitting:
   ```
   pip install syllables
   ```

## Usage

Run the application:
```
python main.py
```

### Main Menu

The application presents the following menu options:

1. **List decks**: View all available word decks
2. **Create new deck**: Create a new empty deck
3. **Import deck from CSV**: Import words from a CSV file
4. **Start session**: Begin a study session with a selected deck
5. **Reset deck**: Clear statistics for a deck
6. **Exit**: Quit the application

### CSV Format

When importing a deck from CSV, the file should have the following format:
```
word,IPA,japanese
apple,ˈæpəl,りんご
banana,bəˈnænə,バナナ
computer,kəmˈpjuːtər,コンピュータ
```

The `word` column is required, while `IPA` and `japanese` columns are optional.

### Study Session

During a study session:
- A word is presented with one syllable hidden (e.g., "ap-___" for "apple")
- Type the missing syllable to answer
- Correct answers remove the card from the session
- Incorrect answers keep the card in rotation
- Type 'exit' to save and exit the session

## Project Structure

```
remembering_words/
├── app/                # Core application modules
│   ├── __init__.py
│   ├── deck.py         # Deck and DeckManager classes
│   ├── session.py      # Session class for study sessions
│   └── word.py         # Word and Card classes
├── decks/              # Directory for saved deck files
├── tests/              # Test suite
├── design.md           # Design documentation
├── main.py             # Main application entry point
├── words.csv           # Sample CSV data
└── README.md           # This file
```

## Testing

Run the test suite with:
```
python -m unittest discover tests
```

## License

[MIT License](LICENSE) 