from models.game_model import GameModel
from views.main_view import HangmanApp
from controllers.game_controller import GameController

if __name__ == "__main__":
    model = GameModel()
    view = HangmanApp(None)  # Placeholder for controller
    controller = GameController(view, model)
    view.controller = controller  # Connect the controller to the view
    controller.start()  # Starts the app
