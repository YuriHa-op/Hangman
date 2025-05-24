package client.player.controller;

import GameModule.GameService;
import client.player.view.GameView;
import client.player.view.LeaderboardView;
import client.player.view.MultiplayerGameView;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.TextArea;
import javafx.stage.Stage;

public class HomeViewController {
    @FXML private Button startGameButton;
    @FXML private Button viewLeaderboardButton;
    @FXML private Button logoutButton;
    @FXML private TextArea outputArea;
    private Stage stage;

    private GameService gameService;
    private String username;
    private Runnable onLogout; // Callback to return to login

    public void setGameService(GameService gameService) {
        this.gameService = gameService;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public void setOnLogout(Runnable onLogout) {
        this.onLogout = onLogout;
    }

    @FXML
    public void initialize(GameService gameService, String username) {
        this.gameService = gameService;
        this.username = username;
        outputArea.setText("");
    }

    @FXML
    private void handleStartGame() {
        Stage gameStage = new Stage();
        GameView gameView = new GameView();

        gameView.start(gameStage, gameService, username, () -> {
            // This will run when the player returns to the menu
            stage.show();
        });

        stage.hide();

        gameView.show();
    }

   @FXML
   private void handleViewLeaderboard() {
       try {
           Stage leaderboardStage = new Stage();
           LeaderboardView leaderboardView = new LeaderboardView();

           leaderboardView.start(leaderboardStage, gameService, () -> {
               stage.show();
           });
           stage.hide();

           leaderboardView.show();
       } catch (Exception e) {
           outputArea.setText("Error displaying leaderboard: " + e.getMessage());
           e.printStackTrace();
       }
   }

    @FXML
    private void handleLogout() {
        try {
            if (gameService != null && username != null) {
                gameService.logout(username);
            }
        } catch (Exception e) {
            // Optionally log error, but ignore for now
        }
        if (stage != null) stage.close();
        if (onLogout != null) onLogout.run();
    }

    @FXML
    private void handleMultiplayer() {
        Stage multiplayerStage = new Stage();
        MultiplayerGameView multiplayerGameView = new MultiplayerGameView();

        multiplayerGameView.start(multiplayerStage, gameService, username, () -> {
            stage.show(); // Show menu again when multiplayer closes
        });

        stage.hide();
        multiplayerGameView.show();
    }

    @FXML
    private void handleMatchHistory() {
        Stage historyStage = new Stage();
        client.player.view.MatchHistoryView historyView = new client.player.view.MatchHistoryView();
        historyView.start(historyStage, gameService, username, () -> {
            stage.show();
        });
        stage.hide();
        historyView.show();
    }

    public void setStage(Stage stage) {
        this.stage = stage;
    }

    public Stage getStage() {
        return stage;
    }
}