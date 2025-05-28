package client.admin.controller;

import GameModule.GameService;
import client.admin.model.Player;
import client.admin.view.SystemStatisticsView;
import client.admin.view.WordManagementView;
import client.admin.view.PlayerManagementView;
import javafx.application.Platform;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.stage.Stage;

import java.util.*;
import java.util.function.Consumer;

public class AdminViewController {
    @FXML
    private Label adminNameLabel;

    @FXML
    private TextArea outputArea;

    private Stage stage;
    private GameService gameService;
    private Runnable onLogout;
    private WordManagementView wordManagementView;
    private PlayerManagementView playerManagementView;

    public void setStage(Stage stage) {
        this.stage = stage;
    }

    public void setGameService(GameService gameService) {
        this.gameService = gameService;
        // Initialize views after gameService is set
        initializeViews();
    }

    public void setOnLogout(Runnable onLogout) {
        this.onLogout = onLogout;
    }

private void initializeViews() {
    if (gameService != null) {
        wordManagementView = new WordManagementView(gameService, this::appendToOutput);
        playerManagementView = new PlayerManagementView(gameService, this::appendToOutput);
    } else {
        appendToOutput("Error: Game service is not initialized");
    }
}

    @FXML
    public void initialize() {
        // Views will be initialized when gameService is set
    }

    @FXML
    public void handleViewPlayers() {
        if (gameService == null) {
            showErrorDialog("Error", "Game service is not initialized.");
            return;
        }
        try {
            // Parse player data from GameService
            String playersList = gameService.viewPlayers();
            List<Player> players = parsePlayers(playersList);

            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/admin/view/PlayerLeaderboardsView.fxml"));
            Parent root = loader.load();
            PlayersLeaderboardController controller = loader.getController();
            
            // Set GameService and OutputCallback for the PlayerLeaderboardsController
            controller.setGameService(this.gameService);
            controller.setOutputCallback(this::appendToOutput);
            
            controller.setPlayers(players);

            Stage stage = new Stage();
            stage.setScene(new Scene(root));
            stage.setTitle("Players Leaderboard");
            stage.setWidth(800);
            stage.setHeight(650);
            stage.show();
        } catch (Exception e) {
            showErrorDialog("Error", "Failed to show players leaderboard: " + e.getMessage());
            e.printStackTrace(); // Also print stack trace for debugging
        }
    }

    private List<Player> parsePlayers(String playersData) {
        List<Player> players = new ArrayList<>();
        if (playersData == null || playersData.isEmpty()) {
            return players;
        }

        String[] lines = playersData.split("\n");
        int rank = 1;

        for (int i = 1; i < lines.length; i++) { // Start from i=1 to skip header if any
            String line = lines[i].trim();
            if (line.isEmpty()) continue;

            try {
                Player player = new Player();

                // Example line: "Username: user1 | Wins: 10 | Status: Online | Role: Player"
                // Adjust parsing based on the exact format from gameService.viewPlayers()
                
                int usernameStart = line.indexOf("Username: ") + "Username: ".length();
                int usernameEnd = line.indexOf(" | Wins:");
                if (usernameStart == -1 + "Username: ".length() || usernameEnd == -1 || usernameStart >= usernameEnd) {
                    System.err.println("Skipping malformed line (username): " + line);
                    continue;
                }
                String username = line.substring(usernameStart, usernameEnd).trim();
                player.setUsername(username);

                int winsStart = line.indexOf("Wins: ") + "Wins: ".length();
                int winsEnd = line.indexOf(" | Status:");
                if (winsStart == -1 + "Wins: ".length() || winsEnd == -1 || winsStart >= winsEnd) {
                    System.err.println("Skipping malformed line (wins): " + line);
                    continue;
                }
                int wins = Integer.parseInt(line.substring(winsStart, winsEnd).trim());
                player.setWins(wins);

                int statusStart = line.indexOf("Status: ") + "Status: ".length();
                int statusEnd = line.indexOf(" | Role:");
                if (statusStart == -1 + "Status: ".length() || statusEnd == -1 || statusStart >= statusEnd) {
                     System.err.println("Skipping malformed line (status): " + line);
                    continue;
                }
                String statusStr = line.substring(statusStart, statusEnd).trim();
                player.setOnline("Online".equalsIgnoreCase(statusStr));

                int roleStart = line.indexOf("Role: ") + "Role: ".length();
                if (roleStart == -1 + "Role: ".length() || roleStart >= line.length()) {
                    System.err.println("Skipping malformed line (role): " + line);
                    continue;
                }
                String role = line.substring(roleStart).trim();
                player.setRole(role);

                // Rank will be set after sorting
                players.add(player);
            } catch (Exception e) {
                System.err.println("Error parsing player data line: '" + line + "'. Error: " + e.getMessage());
                // appendToOutput("Error parsing a player data line: " + e.getMessage());
            }
        }

        // Sort by wins to assign rank
        players.sort(Comparator.comparingInt(Player::getWins).reversed());
        for (int i = 0; i < players.size(); i++) {
            players.get(i).setRank(i + 1);
        }

        return players;
    }

    private void showErrorDialog(String title, String message) {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.getDialogPane().getStyleClass().add("minecraft-dialog"); // Assuming this CSS class exists
        alert.showAndWait();
    }

    @FXML
    public void handleAddPlayer() {
        if (playerManagementView == null) initializeViews(); // Ensure view is initialized
        if (playerManagementView != null) playerManagementView.showAddPlayer();
        else showErrorDialog("Error", "Player Management View not initialized.");
    }

    @FXML
    public void handleUpdatePlayer() {
        if (playerManagementView == null) initializeViews();
        if (playerManagementView != null) playerManagementView.showUpdatePlayer();
        else showErrorDialog("Error", "Player Management View not initialized.");
    }

    @FXML
    public void handleDeletePlayer() {
        if (playerManagementView == null) initializeViews();
        if (playerManagementView != null) playerManagementView.showDeletePlayer();
        else showErrorDialog("Error", "Player Management View not initialized.");
    }

    @FXML
    public void handleViewWords() {
        if (wordManagementView == null) initializeViews();
        if (wordManagementView != null) wordManagementView.showViewWords();
        else showErrorDialog("Error", "Word Management View not initialized.");
    }

    @FXML
    public void handleAddWord() {
        if (wordManagementView == null) initializeViews();
        if (wordManagementView != null) wordManagementView.showAddWord();
        else showErrorDialog("Error", "Word Management View not initialized.");
    }

    @FXML
    public void handleUpdateWord() {
        if (wordManagementView == null) initializeViews();
        if (wordManagementView != null) wordManagementView.showUpdateWord();
        else showErrorDialog("Error", "Word Management View not initialized.");
    }

    @FXML
    public void handleDeleteWord() {
        if (wordManagementView == null) initializeViews();
        if (wordManagementView != null) wordManagementView.showDeleteWord();
        else showErrorDialog("Error", "Word Management View not initialized.");
    }

    @FXML
    public void handleViewLeaderboard() {
        appendToOutput("Coming soon: Game Hosting Feature.");
    }

    @FXML
    public void handleViewStatistics() {
        try {
            SystemStatisticsView statisticsView = new SystemStatisticsView(gameService, this::appendToOutput);
            statisticsView.initialize(); // Initialize might be called internally or not needed if FXML controller
            statisticsView.show();
            appendToOutput("Viewing system statistics and settings...");
        } catch (Exception e) {
            appendToOutput("Error showing statistics: " + e.getMessage());
            e.printStackTrace();
        }
    }

    @FXML
    public void handleLogout() {
        if (onLogout != null) {
            onLogout.run();
        }
    }

    private void appendToOutput(String text) {
        Platform.runLater(() -> {
            if (outputArea != null) {
                outputArea.appendText(text + "\n");
                outputArea.setScrollTop(Double.MAX_VALUE);
            } else {
                System.out.println("Admin Output: " + text); // Fallback if outputArea is not yet initialized
            }
        });
    }
}