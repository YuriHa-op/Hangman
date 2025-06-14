import sys
import os
import time
import traceback
import json
from omniORB import CORBA
import GameModule
import GameModule__POA
import CosNaming
import tkinter as tk
from tkinter import messagebox

# Default ORB settings (change if your server uses different host/port)
ORB_HOST = os.environ.get('ORB_HOST', 'localhost')
ORB_PORT = os.environ.get('ORB_PORT', '900')

# Debug mode - set to True to see more detailed information
DEBUG_MODE = True

def debug_print(message):
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")

# --- Helper function to show a pop-up if no match is found ---
def show_no_match_popup():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo(
        title="No Match Found",
        message="No opponent was found. Please try again later."
    )
    root.destroy()


def get_game_service():
    # Initialize the ORB
    orb = CORBA.ORB_init([
        '-ORBInitRef', f'NameService=corbaloc:iiop:{ORB_HOST}:{ORB_PORT}/NameService'
    ], CORBA.ORB_ID)

    # Obtain reference to the naming service
    obj = orb.resolve_initial_references('NameService')
    naming_context = obj._narrow(CosNaming.NamingContext)
    if naming_context is None:
        print('Failed to narrow the naming context')
        sys.exit(1)

    # Resolve the GameService object
    name = [CosNaming.NameComponent('GameService', '')]
    try:
        obj_ref = naming_context.resolve(name)
        game_service = obj_ref._narrow(GameModule.GameService)
        if game_service is None:
            print('GameService reference is not valid')
            sys.exit(1)
        return game_service
    except Exception as e:
        print('Could not resolve GameService:', e)
        sys.exit(1)


def main_menu(game_service, username):
    while True:
        print(f"\nWelcome, {username}!")
        print("1. Start Single Player Game")
        print("2. Start Multiplayer Game")
        print("3. View Leaderboard")
        print("4. View Match History")
        print("5. Logout")
        choice = input("Select an option: ").strip()
        if choice == '1':
            start_game(game_service, username)
        elif choice == '2':
            start_multiplayer_game(game_service, username)
        elif choice == '3':
            print(game_service.viewLeaderboard())
        elif choice == '4':
            view_match_history(game_service, username)
        elif choice == '5':
            game_service.logout(username)
            print("Logged out.")
            break
        else:
            print("Invalid choice.")

def start_multiplayer_game(game_service, username):
    print("\nStarting multiplayer game...")
    try:
        # Join or create a lobby
        lobby_id = game_service.startMultiplayerGame(username)
        if not lobby_id or lobby_id.startswith("ERROR:"):
            print(f"Failed to join multiplayer game: {lobby_id}")
            return

        print(f"Joined multiplayer lobby: {lobby_id}")
        print("Waiting for other players...")

        # Signal that player is ready for the first round
        game_service.playerReadyForFirstRound(username)
        
        # Poll for lobby state until game starts or timeout
        waiting_time = game_service.getWaitingTime()
        start_time = time.time()
        game_started = False
        
        while time.time() - start_time < waiting_time:
            lobby_state_json = game_service.getMultiplayerLobbyState(username)
            lobby_state = json.loads(lobby_state_json)
            
            if lobby_state.get("state") == "NOMATCH":
                print("No match found. Try again later.")
                return
                
            # Display current players in lobby
            players = lobby_state.get("players", [])
            max_players = lobby_state.get("maxPlayers", 8)
            print(f"\rPlayers in lobby: {len(players)}/{max_players} - {', '.join(players)}", end="")
            
            # Check if game has started
            if lobby_state.get("state") == "STARTED" and lobby_state.get("gameState"):
                game_started = True
                print("\nGame starting!")
                break
                
            time.sleep(1)
            
        if not game_started:
            print("\nWaiting time expired. Check if game started...")
            lobby_state_json = game_service.getMultiplayerLobbyState(username)
            lobby_state = json.loads(lobby_state_json)
            
            if lobby_state.get("state") != "STARTED" or not lobby_state.get("gameState"):
                print("Game did not start. Not enough players joined.")
                return
        
        # Game has started, play multiplayer game
        play_multiplayer_game(game_service, username)
        
    except Exception as e:
        print(f"Error in multiplayer game: {e}")
        traceback.print_exc()
    finally:
        # Make sure we leave the game properly
        try:
            game_service.leaveMultiplayerGame(username)
        except:
            pass

def play_multiplayer_game(game_service, username):
    print("\nMultiplayer game started!")
    
    try:
        while True:
            # Get current game state
            lobby_state_json = game_service.getMultiplayerLobbyState(username)
            lobby_state = json.loads(lobby_state_json)
            
            if lobby_state.get("state") == "NOMATCH":
                print("Game ended.")
                break
                
            game_state = lobby_state.get("gameState", {})
            if not game_state:
                print("No active game found.")
                break
                
            # Check if game is over
            game_winner = game_state.get("gameWinner")
            if game_winner:
                session_result = game_state.get("sessionResult", "")
                print(f"\nGame over! Winner: {game_winner}")
                if session_result == "WIN":
                    print("Congratulations! You won the game!")
                elif session_result == "LOSE":
                    print("You lost the game.")
                else:
                    print(f"Game result: {session_result}")
                break
                
            # Display round information
            current_round = game_state.get("currentRound", -1)
            round_in_progress = game_state.get("roundInProgress", False)
            
            if current_round == -1:
                print("Waiting for first round to start...")
                time.sleep(1)
                continue
                
            # Get player's masked word and other players' progress
            masked_words = game_state.get("maskedWords", {})
            my_word = masked_words.get(username, "")
            
            # Get incorrect guesses
            incorrect_guesses_map = game_state.get("incorrectGuessesMap", {})
            my_incorrect = incorrect_guesses_map.get(username, 0)
            
            # Get remaining time
            remaining_time = game_state.get("remainingTime", 0)
            
            # Display round status
            print(f"\nRound {current_round + 1}")
            print(f"Your word: {my_word}")
            print(f"Incorrect guesses: {my_incorrect}/5 | Time left: {remaining_time}s")
            
            # Check if round is over
            round_winner = game_state.get("roundWinner")
            if round_winner:
                # Show other players' progress when round is over
                print("\nOther players:")
                for player, word in masked_words.items():
                    if player != username:
                        incorrect = incorrect_guesses_map.get(player, 0)
                        print(f"{player}: {word} (Incorrect: {incorrect}/5)")
                        
                print(f"\nRound over! Winner: {round_winner}")
                
                # Wait for next round to start
                print("Waiting for next round...")
                game_service.startMultiplayerNextRound(username)
                time.sleep(2)
                continue
                
            # If round is in progress, allow player to make a guess
            if round_in_progress:
                guess = input("\nEnter a letter (or 'quit' to exit): ").strip().lower()
                if guess == 'quit':
                    print("Leaving game...")
                    return
                    
                if len(guess) != 1 or not guess.isalpha():
                    print("Please enter a single letter.")
                    continue
                    
                # Send guess to server
                correct = game_service.sendMultiplayerGuess(username, guess[0])
                if correct == GameModule.BOOL_TRUE:
                    print("Correct!")
                else:
                    print("Incorrect!")
                    
                # Show other players' progress after making a guess
                print("\nOther players:")
                for player, word in masked_words.items():
                    if player != username:
                        incorrect = incorrect_guesses_map.get(player, 0)
                        print(f"{player}: {word} (Incorrect: {incorrect}/5)")
            else:
                print("Waiting for round to start...")
                time.sleep(1)
                
    except Exception as e:
        print(f"Error during multiplayer game: {e}")
        traceback.print_exc()

def view_match_history(game_service, username):
    print("\n=== MATCH HISTORY ===")
    print("1. View Single Player History")
    print("2. View Multiplayer History")
    print("3. Return to Main Menu")
    
    choice = input("Select an option: ").strip()
    
    if choice == '1':
        # Get single player history
        try:
            history_json = game_service.getSinglePlayerMatchHistory(username)
            history = json.loads(history_json)
            
            if not history:
                print("No single player match history found.")
                return
                
            print("\nSingle Player Match History:")
            for i, game in enumerate(history):
                end_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(game.get('gameEndTime', 0)/1000))
                print(f"{i+1}. Game ID: {game.get('gameId', 'Unknown')}")
                print(f"   Date: {end_time_str}")
                print(f"   Total Rounds: {game.get('totalRounds', 0)}")
                print(f"   Result: {game.get('result', 'Unknown')}")
                print()
            
            # View details of a specific match
            game_choice = input("Enter game number to view details (or 0 to return): ").strip()
            if game_choice.isdigit() and 1 <= int(game_choice) <= len(history):
                game_id = history[int(game_choice)-1].get('gameId')
                view_match_details(game_service, game_id, is_multiplayer=False)
                
        except Exception as e:
            print(f"Error retrieving match history: {e}")
            
    elif choice == '2':
        # Get multiplayer history
        try:
            history_json = game_service.getMatchHistory(username)
            history = json.loads(history_json)
            
            if not history:
                print("No multiplayer match history found.")
                return
                
            print("\nMultiplayer Match History:")
            for i, game in enumerate(history):
                end_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(game.get('gameEndTime', 0)/1000))
                winner = game.get('overallWinner', 'Unknown')
                result = "WIN" if winner == username else "LOSE" if winner else "DRAW"
                
                print(f"{i+1}. Game ID: {game.get('gameId', 'Unknown')}")
                print(f"   Date: {end_time_str}")
                print(f"   Players: {', '.join(game.get('players', []))}")
                print(f"   Winner: {winner}")
                print(f"   Your Result: {result}")
                print()
            
            # View details of a specific match
            game_choice = input("Enter game number to view details (or 0 to return): ").strip()
            if game_choice.isdigit() and 1 <= int(game_choice) <= len(history):
                game_id = history[int(game_choice)-1].get('gameId')
                view_match_details(game_service, game_id, is_multiplayer=True)
                
        except Exception as e:
            print(f"Error retrieving match history: {e}")

def view_match_details(game_service, game_id, is_multiplayer=True):
    try:
        if is_multiplayer:
            details_json = game_service.getMatchDetails(game_id)
        else:
            details_json = game_service.getSinglePlayerMatchDetails(game_id)
            
        details = json.loads(details_json)
        
        if not details:
            print(f"No details found for game ID: {game_id}")
            return
            
        print("\n=== MATCH DETAILS ===")
        print(f"Game ID: {details.get('gameId', 'Unknown')}")
        
        # Format and display end time
        end_time = details.get('gameEndTime', 0)
        if end_time:
            end_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time/1000))
            print(f"Date: {end_time_str}")
        
        # Display players
        if is_multiplayer:
            print(f"Players: {', '.join(details.get('players', []))}")
            print(f"Winner: {details.get('overallWinner', 'None')}")
        else:
            print(f"Player: {details.get('username', 'Unknown')}")
            print(f"Result: {details.get('result', 'Unknown')}")
        
        print(f"Total Rounds: {details.get('totalRounds', 0)}")
        
        # Display rounds
        print("\nRounds:")
        rounds = details.get('rounds', [])
        for i, round_info in enumerate(rounds):
            round_num = round_info.get('roundNumber', i+1)
            word = round_info.get('word', 'Unknown')
            winner = round_info.get('winner', 'None')
            
            print(f"Round {round_num}: Word = {word}, Winner = {winner}")
        
        input("\nPress Enter to return...")
        
    except Exception as e:
        print(f"Error retrieving match details: {e}")

def start_game(game_service, username):
    print("\nRequesting a match...")
    masked_word = game_service.startGame(username)
    debug_print(f"Initial masked_word: {masked_word}")
    
    # Signal that player is ready for the first round immediately
    # This is important to do early to ensure proper matchmaking
    game_service.playerReadyForFirstRound(username)
    debug_print("Sent playerReadyForFirstRound signal")
    
    # Check if we need to wait for a match
    if masked_word == 'WAITING_FOR_MATCH':
        print("Waiting for an opponent...")
        # Poll for match
        waiting_time = game_service.getWaitingTime()
        debug_print(f"Waiting time: {waiting_time} seconds")
        start = time.time()
        
        # Keep polling until we find a match or time out
        while time.time() - start < waiting_time:
            time.sleep(1)
            masked_word = game_service.getMaskedWord(username)
            debug_print(f"Polling masked_word: {masked_word}")
            
            if masked_word != 'WAITING_FOR_MATCH' and masked_word:
                debug_print("Match found while polling")
                break
                
        # Check if we found a match after polling
        if masked_word == 'WAITING_FOR_MATCH' or not masked_word:
            print("No match found. Try again later.")
            debug_print("No match found after waiting period")
            show_no_match_popup()  # Show pop-up dialog
            game_service.endGameSession(username)
            return
    else:
        # If we didn't get WAITING_FOR_MATCH, it means we're in single player mode
        debug_print("Not waiting for match - starting single player mode")
    
    # At this point, we either found a match or we're in single player mode
    if masked_word == 'WAITING_FOR_MATCH':
        debug_print("ERROR: Still in waiting state after polling completed")
        print("Error finding match. Please try again.")
        game_service.endGameSession(username)
        return
    
    # If we're here, we have a valid masked_word
    if '_' in masked_word:  # Confirm we have a valid word to guess
        print("Game starting in 5 seconds...")
        # Send another ready signal just to be sure
        game_service.playerReadyForFirstRound(username)
        debug_print("Sent second playerReadyForFirstRound signal")
        
        for i in range(5, 0, -1):
            print(f"Starting in {i}...", end='\r')
            time.sleep(1)
        print(" " * 30, end='\r')  # Clear the line
        
        print("Game started! Let's play Hangman.")
        play_game_session(game_service, username)
    else:
        debug_print(f"Invalid masked word received: {masked_word}")
        print("Error starting game. Please try again.")
        game_service.endGameSession(username)

def play_game_session(game_service, username):
    # Main game session loop (best of 3)
    while True:
        round_result = play_round(game_service, username)
        # After each round, show round winner and session result
        state = game_service.getGameState(username)
        debug_print(f"After round - state: roundWinner={state.roundWinner}, sessionResult={state.sessionResult}")
        
        if state.roundWinner:
            if state.roundWinner == username:
                print(f"You won round {state.currentRound + 1}!")
            else:
                print(f"{state.roundWinner} won round {state.currentRound + 1}.")
        else:
            print("No one won this round.")
        
        if state.sessionResult and state.sessionResult != 'ONGOING':
            if state.sessionResult == 'WIN':
                print("\nCongratulations! You won the game session!")
            elif state.sessionResult == 'LOSE':
                print("\nYou lost the game session.")
            else:
                print(f"\nGame session result: {state.sessionResult}")
            game_service.endGameSession(username)
            break
            
        # Start next round if game is not over
        print("\nStarting next round...")
        started = game_service.startNewRound(username)
        debug_print(f"startNewRound result: {started}")
        
        if not started:
            print("Could not start new round. Returning to main menu.")
            break
            
    print("Returning to main menu.")

def play_round(game_service, username):
    # Play a single round
    while True:
        state = game_service.getGameState(username)
        masked_word = state.maskedWord
        incorrect = state.incorrectGuesses
        remaining = state.remainingTime
        print(f"\nWord: {masked_word}")
        print(f"Incorrect guesses: {incorrect}/5 | Time left: {remaining}s")
        guess = input("Enter a letter (or 'quit' to exit): ").strip().lower()
        if guess == 'quit':
            game_service.endGameSession(username)
            print("Game exited.")
            sys.exit(0)
        if len(guess) != 1 or not guess.isalpha():
            print("Please enter a single letter.")
            continue
        
        # Send the guess to the server
        correct = game_service.sendGuess(username, guess[0])
        if correct:
            print("Correct!")
        else:
            print("Incorrect.")
            
        # Refresh state after guess
        state = game_service.getGameState(username)
        
        # Check if the round is actually over (either word is fully guessed or max incorrect guesses reached)
        guessed_word = '_' not in state.maskedWord
        max_incorrect_reached = state.incorrectGuesses >= 5
        
        # Only finish the round if it's marked as over by the server
        if state.roundOver:
            # Check if the round is actually over due to word being guessed or max incorrect guesses
            if guessed_word or max_incorrect_reached:
                # Convert Python boolean to GameModule.Bool enum
                bool_guessed = GameModule.BOOL_TRUE if guessed_word else GameModule.BOOL_FALSE
                game_service.finishRound(username, state.remainingTime, bool_guessed)
                print("\nRound over!")
                return
            else:
                # If the round is marked as over but not due to guessing or max incorrect,
                # continue playing (this is to fix premature round ending)
                continue
        
        # If the word is fully guessed but state.roundOver is not set, still call finishRound
        if guessed_word:
            bool_guessed = GameModule.BOOL_TRUE
            game_service.finishRound(username, state.remainingTime, bool_guessed)
            print("\nRound over! You guessed the word!")
            return
            
        # If max incorrect guesses reached but state.roundOver is not set, still call finishRound
        if max_incorrect_reached:
            bool_guessed = GameModule.BOOL_FALSE
            game_service.finishRound(username, state.remainingTime, bool_guessed)
            print("\nRound over! Too many incorrect guesses.")
            return

def login_or_create(game_service):
    while True:
        print("\n1. Login\n2. Create Account\n3. Exit")
        choice = input("Select an option: ").strip()
        if choice == '1':
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            try:
                if game_service.login(username, password):
                    print("Login successful!")
                    return username
                else:
                    print("Login failed. Check your credentials.")
            except GameModule.AlreadyLoggedInException as e:
                print("Error:", e.message)
        elif choice == '2':
            while True:
                username = input("Choose a username: ").strip()
                if not username:
                    print("Username cannot be empty.")
                    continue
                    
                password = input("Choose a password: ").strip()
                if not password:
                    print("Password cannot be empty.")
                    continue
                
                # Try to create the account
                if game_service.createPlayer(username, password):
                    print("Account created! You can now log in.")
                    break
                else:
                    print("Account creation failed. Username may already exist.")
                    retry = input("Try a different username? (y/n): ").strip().lower()
                    if retry != 'y':
                        break
        elif choice == '3':
            sys.exit(0)
        else:
            print("Invalid choice.")

def main():
    print("Python CORBA Hangman Client")
    try:
        game_service = get_game_service()
        username = login_or_create(game_service)
        main_menu(game_service, username)
    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()

if __name__ == '__main__':
    main() 