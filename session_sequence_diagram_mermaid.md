# Session Sequence Diagram

The following diagram illustrates the sequence of interactions during a study session in the English Word Memorization Application.

```mermaid
sequenceDiagram
    participant User
    participant MainApp as Main App
    participant Session
    participant Deck
    participant Card
    
    User->>MainApp: Start session
    MainApp->>MainApp: Select deck
    MainApp->>Session: Create Session(deck, num_cards)
    Session->>Deck: Initialize with deck reference
    
    Note over Session: prepare_cards()
    Session->>Session: _load_session()
    alt Saved session exists
        Session-->>Session: Load saved session state
    else No saved session
        Session->>Deck: Access deck words
        Session->>Session: Sample words from deck
        loop For each selected word
            Session->>Session: Generate hidden_index
            Session->>Card: Create Card(word, hidden_index)
        end
    end
    
    Note over Session: run()
    Session->>Session: Start timer
    
    loop While remaining_cards not empty
        Session->>Session: Select random card
        Session->>User: Display card prompt
        User->>Session: Input answer
        
        alt User inputs "exit"
            Session->>Session: _save_session()
            Session->>User: Confirm session saved
            Note over Session: Break loop
        else Continue session
            Session->>Session: Increment studied counter
            Session->>Card: check_answer(user_input)
            
            alt Answer correct
                Card-->>Session: Return true with feedback
                Session->>User: Display "Correct!"
                Session->>Session: Remove card from remaining_cards
            else Answer incorrect
                Card-->>Session: Return false with feedback
                Session->>User: Display character-by-character feedback
                Note over Session: Card remains in remaining_cards
                Note over User: Shows correct/wrong/missing/extra characters
            end
        end
    end
    
    alt Session completed
        Session->>Session: _delete_session()
        Session->>User: Display completion message
    end
    
    Session->>Session: _calculate_stats()
    Session->>Deck: _update_deck_stats()
    Session->>Session: _display_stats()
    Session->>User: Show statistics
    
    MainApp->>Deck: save_deck()
```

## Key Interactions in the Sequence

1. **Session Initialization**:
   - User selects to start a session through the main application
   - The application creates a Session object with the selected deck
   - Session initializes with a reference to the deck

2. **Card Preparation**:
   - Session attempts to load a previous session from a JSON file
   - If no saved session exists, it selects words from the deck and creates cards
   - Each card is created with a random syllable to hide

3. **Session Execution**:
   - The user is presented with cards one at a time in random order
   - For each card, the user inputs an answer or can choose to exit
   - The system checks the answer character by character and provides detailed feedback:
     - Correct characters shown in green
     - Wrong characters shown in red
     - Extra characters shown in yellow
     - Missing characters shown as blue underscores
   - Correct answers remove the card from rotation
   - Incorrect answers keep the card in rotation
   - If the user chooses to exit, the session state is saved

4. **Session Completion**:
   - When all cards are answered correctly, the session is complete
   - Session statistics are calculated and displayed to the user
   - The deck's statistics are updated with the session results

5. **Session State Management**:
   - The session can be saved and resumed later
   - Completed sessions are deleted from storage