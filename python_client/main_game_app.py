import sys
from models.game_model import GameModel
from views.main_view import HangmanApp
from controllers.game_controller import GameController

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main_game_app.py <username> <session_id>")
        sys.exit(1)

    username = sys.argv[1]
    session_id = sys.argv[2]

    model = GameModel()
    model.set_user_session(username, session_id)

    view = HangmanApp(None)  # Placeholder for controller
    controller = GameController(view, model)
    view.controller = controller  # Connect the controller to the view
    
    controller.start()  # Starts the app 