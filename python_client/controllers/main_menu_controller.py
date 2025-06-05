from .base_controller import BaseController

class MainMenuController(BaseController):
    def __init__(self, model, view):
        super().__init__(model, view)
        # self.view is QtMainMenuView, which has self.main_window

    def start_single_player(self):
        # print("MainMenuController: Navigating to Single Player Game")
        # Navigates to the 1v1 Single Player Game view
        self.view.main_window.show_view("SinglePlayer1v1Game")

    def go_to_multiplayer_queue(self):
        # print("MainMenuController: Navigating to Multiplayer Queue")
        # TODO: Create QtMultiplayerQueueView and its controller
        self.view.main_window.show_view("MultiplayerQueue") # Placeholder name

    def show_leaderboard(self):
        # print("MainMenuController: Navigating to Leaderboard")
        # TODO: Create QtLeaderboardView and its controller
        self.view.main_window.show_view("Leaderboard") # Placeholder name

    def show_match_history(self):
        # print("MainMenuController: Navigating to Match History")
        # TODO: Create QtMatchHistoryView and its controller
        self.view.main_window.show_view("MatchHistory") # Placeholder name

    # The logout action is connected in QtMainMenuView to call main_window.logout_user_and_show_login()
    # or self.logout() from BaseController can be used if wired up.
    # def perform_logout(self):
    #     self.logout() # Uses BaseController.logout()

    # get_username() is inherited from BaseController for the welcome message in MainMenuView
    # show_frame() is inherited from BaseController for navigation buttons in MainMenuView 