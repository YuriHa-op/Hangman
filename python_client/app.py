from models.game_model import GameModel
from views.app_view import HangmanApp # Updated import for HangmanApp
# Specific view and controller imports are handled within HangmanApp (app_view.py)

if __name__ == "__main__":
    model = GameModel()
    app_view = HangmanApp(model) # Pass model to HangmanApp constructor

    app_view.setup_frames_and_controllers() # Call the setup method on HangmanApp

    app_view.show_frame("Login") # Start with the login view
    app_view.run()  # Start the Tkinter main loop
