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

<<<<<<< HEAD
    private void initializeViews() {
        if (gameService != null) {
            wordManagementView = new WordManagementView(this::appendToOutput);
            wordManagementView.initialize();
            playerManagementView = new PlayerManagementView(gameService, this::appendToOutput);
        } else {
            appendToOutput("Error: Game service is not initialized");
        }
    }
=======
  private void initializeViews() {
      if (gameService != null) {
          wordManagementView = new WordManagementView(gameService, this::appendToOutput);
          wordManagementView.initialize();
          playerManagementView = new PlayerManagementView(gameService, this::appendToOutput);
      } else {
          appendToOutput("Error: Game service is not initialized");
      }
  }
>>>>>>> main

    @FXML
    public void initialize() {
        // Views will be initialized when gameService is set
    }

    @FXML
    public void handleViewPlayers() {
        try {
            // Parse player data from GameService
            String playersList = gameService.viewPlayers();
            List<Player> players = parsePlayers(playersList);

            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/admin/view/PlayerLeaderboardsView.fxml"));
            Parent root = loader.load();
            PlayersLeaderboardController controller = loader.getController();
            controller.setPlayers(players);

            Stage stage = new Stage();
            stage.setScene(new Scene(root));
            stage.setTitle("Players Leaderboard");
            stage.show();
        } catch (Exception e) {
            showErrorDialog("Error", "Failed to show players leaderboard: " + e.getMessage());
        }
    }

    private List<Player> parsePlayers(String playersData) {
        List<Player> players = new ArrayList<>();
        if (playersData == null || playersData.isEmpty()) {
            return players;
        }

        String[] lines = playersData.split("\n");
        int rank = 1;

        for (int i = 1; i < lines.length; i++) {
            String line = lines[i].trim();
            if (line.isEmpty()) continue;

            try {
                Player player = new Player();

                int usernameStart = line.indexOf("Username: ") + 10;
                int usernameEnd = line.indexOf(" | Wins:");
                String username = line.substring(usernameStart, usernameEnd);
                player.setUsername(username);

                int winsStart = line.indexOf("Wins: ") + 6;
                int winsEnd = line.indexOf(" | Status:");
                int wins = Integer.parseInt(line.substring(winsStart, winsEnd));
                player.setWins(wins);

                boolean isOnline = line.contains("Status: Online");
                player.setOnline(isOnline);

                // Extract role
                int roleStart = line.indexOf("Role: ") + 6;
                String role = line.substring(roleStart).trim();
                player.setRole(role);

                player.setRank(rank++);
                players.add(player);
            } catch (Exception e) {
                System.err.println("Error parsing player data: " + line);
                outputArea.appendText("Error parsing player data: " + e.getMessage() + "\n");
            }
        }

        players.sort(Comparator.comparing(Player::getWins).reversed());
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
        alert.getDialogPane().getStyleClass().add("minecraft-dialog");
        alert.showAndWait();
    }

    @FXML
    public void handleAddPlayer() {
        playerManagementView.showAddPlayer();
    }

    @FXML
    public void handleUpdatePlayer() {
        playerManagementView.showUpdatePlayer();
    }

    @FXML
    public void handleDeletePlayer() {
        playerManagementView.showDeletePlayer();
    }

    @FXML
    public void handleViewWords() {
        wordManagementView.showViewWords();
    }

    @FXML
    public void handleAddWord() {
        wordManagementView.showAddWord();
    }

    @FXML
    public void handleUpdateWord() {
        wordManagementView.showUpdateWord();
    }

    @FXML
    public void handleDeleteWord() {
        wordManagementView.showDeleteWord();
    }

    @FXML
    public void handleViewLeaderboard() {
        appendToOutput("Coming soon: View leaderboard feature.");
    }

    @FXML
    public void handleViewStatistics() {
        try {
            SystemStatisticsView statisticsView = new SystemStatisticsView(gameService, this::appendToOutput);
            statisticsView.initialize();
            statisticsView.show();
            appendToOutput("Viewing system statistics and settings...");
        } catch (Exception e) {
            appendToOutput("Error showing statistics: " + e.getMessage());
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
            outputArea.appendText(text + "\n");
            outputArea.setScrollTop(Double.MAX_VALUE);
        });
    }
}