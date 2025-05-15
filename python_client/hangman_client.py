import sys
import os
import time
import traceback
from omniORB import CORBA
import GameModule
import GameModule__POA
from omniORB import CosNaming
import tkinter as tk
from tkinter import messagebox

# Default ORB settings (change if your server uses different host/port)
ORB_HOST = os.environ.get('ORB_HOST', 'localhost')
ORB_PORT = os.environ.get('ORB_PORT', '900')

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
        print("1. Start Game")
        print("2. View Leaderboard")
        print("3. Logout")
        choice = input("Select an option: ").strip()
        if choice == '1':
            start_game(game_service, username)
        elif choice == '2':
            print(game_service.viewLeaderboard())
        elif choice == '3':
            game_service.logout(username)
            print("Logged out.")
            break
        else:
            print("Invalid choice.")

def start_game(game_service, username):
    print("\nRequesting a match...")
    masked_word = game_service.startGame(username)
    if masked_word == 'WAITING_FOR_MATCH':
        print("Waiting for an opponent...")
        # Poll for match
        waiting_time = game_service.getWaitingTime()
        start = time.time()
        while time.time() - start < waiting_time:
            time.sleep(1)
            masked_word = game_service.getMaskedWord(username)
            if masked_word != 'WAITING_FOR_MATCH' and masked_word:
                break
        if masked_word == 'WAITING_FOR_MATCH' or not masked_word:
            print("No match found. Try again later.")
            show_no_match_popup()  # Show pop-up dialog
            game_service.endGameSession(username)
            return
    print("Game started! Let's play Hangman.")
    play_game_session(game_service, username)

def play_game_session(game_service, username):
    # Main game session loop (best of 3)
    while True:
        round_result = play_round(game_service, username)
        # After each round, show round winner and session result
        state = game_service.getGameState(username)
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
        correct = game_service.sendGuess(username, guess[0])
        if correct:
            print("Correct!")
        else:
            print("Incorrect.")
        # Refresh state after guess
        state = game_service.getGameState(username)
        if state.roundOver:
            # Call finishRound with remaining time and guessed status
            guessed_word = '_' not in state.maskedWord
            game_service.finishRound(username, state.remainingTime, guessed_word)
            print("\nRound over!")
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
            username = input("Choose a username: ").strip()
            password = input("Choose a password: ").strip()
            if game_service.createPlayer(username, password):
                print("Account created! You can now log in.")
            else:
                print("Account creation failed. Username may already exist.")
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