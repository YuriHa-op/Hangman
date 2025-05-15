package client.player.controller;

import GameModule.GameService;
import javafx.fxml.FXML;
import javafx.scene.control.TextArea;
import javafx.stage.Stage;

public class LeaderboardController {
    @FXML private TextArea leaderboardArea;

    private GameService gameService;
    private Runnable onBackToMenu;
    private Stage stage; // Add stage reference

    public void setGameService(GameService gameService) {
        this.gameService = gameService;
        loadLeaderboardData(); // Load data after service is set
    }

    public void setStage(Stage stage) {
        this.stage = stage;
    }

    public void setOnBackToMenu(Runnable onBackToMenu) {
        this.onBackToMenu = onBackToMenu;
    }

    // Separate method to load leaderboard data
    public void loadLeaderboardData() {
        try {
            if (gameService != null) {
                String data = gameService.viewLeaderboard();
                leaderboardArea.setText(data);
            } else {
                leaderboardArea.setText("Game service unavailable.");
            }
        } catch (Exception e) {
            leaderboardArea.setText("Error loading leaderboard: " + e.getMessage());
        }
    }

    @FXML
    public void initialize() {
        // Initialize UI elements if needed, but don't load data yet
        leaderboardArea.setText("Loading leaderboard data...");
    }

    @FXML
    private void handleBackToMenu() {
        if (stage != null) {
            stage.close(); // Close the window
        }

        if (onBackToMenu != null) {
            onBackToMenu.run();
        }
    }
}