package client.player.controller;

import GameModule.GameService;
import client.player.model.MultiplayerGameModel;
import client.player.model.MultiplayerGameModel.LobbyState;
import client.player.view.GameView;
import client.player.view.LeaderboardView;
import client.player.view.MultiplayerGameView;
import client.player.view.QueueStatusPane;
import client.player.view.MatchHistoryView;
import javafx.animation.KeyFrame;
import javafx.animation.ScaleTransition;
import javafx.animation.Timeline;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.stage.Modality;
import javafx.stage.Stage;
import javafx.util.Duration;
import java.util.List;
import java.util.Set;

public class HomeViewController {
    @FXML private Button startGameButton;
    @FXML private Button viewLeaderboardButton;
    @FXML private Button logoutButton;
    @FXML private Button multiplayerButton;
    @FXML private Button matchHistoryButton;
    @FXML private StackPane queueStatusContainer;
    private Stage stage;

    private GameService gameService;
    private String username;
    private Runnable onLogout; // Callback to return to login

    // Multiplayer queue state
    private QueueStatusPane queueStatusPane;
    private MultiplayerGameModel multiplayerModel;
    private Timeline queuePoller;
    private boolean isQueueing = false;
    private boolean matchFoundDialogShown = false;
    private int lastQueueSeconds = -1;

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
    public void initialize() {
        // No-op for now
    }

    @FXML
    private void handleMultiplayer() {
        if (isQueueing) return;
        isQueueing = true;
        matchFoundDialogShown = false;
        // Hide main menu buttons
        setMenuButtonsDisabled(true);

        // Show queue status pane
        queueStatusPane = new QueueStatusPane();
        queueStatusContainer.getChildren().setAll(queueStatusPane);

        // Create multiplayer model and start game (creates lobby or joins one)
        multiplayerModel = new MultiplayerGameModel(gameService, username);
        multiplayerModel.setLobbyStateListener(this::onLobbyUpdate);
        multiplayerModel.startGame();

        // Start polling lobby state
        queuePoller = new Timeline(new KeyFrame(Duration.seconds(1), e -> {
            if (multiplayerModel != null) multiplayerModel.updateLobbyState();
        }));
        queuePoller.setCycleCount(Timeline.INDEFINITE);
        queuePoller.play();

        // Cancel button logic
        queueStatusPane.getCancelButton().setOnAction(e -> cancelQueue());
    }

    private void cancelQueue() {
        isQueueing = false;
        if (queuePoller != null) queuePoller.stop();
        queueStatusContainer.getChildren().clear();
        setMenuButtonsDisabled(false);
        
        // Notify server that player is leaving the lobby
        if (multiplayerModel != null && username != null) {
            try {
                multiplayerModel.getGameService().cleanupPlayerSession(username);
            } catch (Exception ex) {
                System.err.println("Error trying to leave lobby: " + ex.getMessage());
                // Optionally show an error to the user, e.g., using an Alert
            }
        }
        multiplayerModel = null; // Release model
    }

    private void setMenuButtonsDisabled(boolean disabled) {
        startGameButton.setDisable(disabled);
        viewLeaderboardButton.setDisable(disabled);
        logoutButton.setDisable(disabled);
        multiplayerButton.setDisable(disabled);
        matchHistoryButton.setDisable(disabled);
    }

    private void onLobbyUpdate(LobbyState state) {
        Platform.runLater(() -> {
            if (!isQueueing || multiplayerModel == null) {
                 // If not queueing anymore (e.g. cancelled), or model is null, stop updates.
                if (queuePoller != null) queuePoller.stop();
                return;
            }
            // Update queue timer and player count
            int playerCount = state.getPlayers() != null ? state.getPlayers().size() : 0;
            int maxPlayers = state.getMaxPlayers();
            long creationTime = state.getCreationTime();
            int queueTime = state.getQueueTimeSeconds();
            long now = System.currentTimeMillis();
            int secondsLeft = (int)Math.max(0, queueTime - (now - creationTime) / 1000);
            
            if (queueStatusPane != null) { // Ensure pane still exists
                queueStatusPane.setTimer(secondsLeft);
                queueStatusPane.setPlayerCount(playerCount, maxPlayers);
            }
            lastQueueSeconds = secondsLeft;

            // Only show match found dialog after queue timer is finished and state is STARTED
            if (secondsLeft == 0) {
                if ("STARTED".equals(state.getState()) && !matchFoundDialogShown) {
                    matchFoundDialogShown = true;
                    if (queuePoller != null) queuePoller.stop(); // Stop polling HomeView queue
                    showMatchFoundDialog(state.getPlayers());
                } else if (!"STARTED".equals(state.getState()) && !matchFoundDialogShown) {
                    // Avoid showing 'no match' if already shown or game starting
                    matchFoundDialogShown = true; // Prevent repeated dialogs
                    if (queuePoller != null) queuePoller.stop();
                    showNoMatchFoundDialog();
                    cancelQueue(); // Clean up queue state
                }
            }
            // If lobby is gone or NOMATCH, and we haven't already handled it
            if ("NOMATCH".equals(state.getState()) && !matchFoundDialogShown) {
                 matchFoundDialogShown = true; // Prevent repeated dialogs
                 if (queuePoller != null) queuePoller.stop();
                 showNoMatchFoundDialog();
                 cancelQueue(); // Clean up queue state
            }
        });
    }

    private void showMatchFoundDialog(List<String> players) {
        Stage dialog = new Stage();
        dialog.initOwner(stage);
        dialog.initModality(Modality.APPLICATION_MODAL);
        dialog.setTitle("Match Found!");
        
        VBox box = new VBox(20); // Increased spacing
        box.setAlignment(javafx.geometry.Pos.CENTER);
        box.setStyle("-fx-background-image: url('matchfound_bg.png'); -fx-background-size: cover; -fx-background-radius: 16; -fx-padding: 30;");

        Label titleLabel = new Label("Match Found!");
        titleLabel.setStyle("-fx-font-size: 28px; -fx-text-fill: #4CAF50; -fx-font-family: 'Minecraftia';");

        GridPane playerGrid = new GridPane();
        playerGrid.setAlignment(javafx.geometry.Pos.CENTER);
        playerGrid.setHgap(15);
        playerGrid.setVgap(15);
        int col = 0;
        int row = 0;
        if (players != null) {
            for (String player : players) {
                Label playerLabel = new Label(player);
                playerLabel.setStyle("-fx-font-size: 18px; -fx-text-fill: #fff; -fx-font-family: 'Minecraftia'; -fx-background-color: rgba(0,0,0,0.5); -fx-padding: 5 10 5 10; -fx-background-radius: 5;");
                playerGrid.add(playerLabel, col, row);
                col++;
                if (col == 3) { // 3 players per row
                    col = 0;
                    row++;
                }
            }
        }

        Label countdownLabel = new Label("Game starts in 5");
        countdownLabel.setStyle("-fx-font-size: 30px; -fx-text-fill: #FFD600; -fx-font-family: 'Minecraftia';");
        
        box.getChildren().addAll(titleLabel, playerGrid, countdownLabel);
        // Increased dialog size
        javafx.scene.Scene scene = new javafx.scene.Scene(box, 600, 450);
        dialog.setScene(scene);
        dialog.setResizable(false);
        dialog.show();

        Timeline countdownTimeline = new Timeline(new KeyFrame(Duration.seconds(1), e -> {
            String text = countdownLabel.getText();
            int sec = Integer.parseInt(text.replaceAll("\\D", ""));
            if (sec > 1) {
                countdownLabel.setText("Game starts in " + (sec - 1));
                ScaleTransition st = new ScaleTransition(Duration.millis(400), countdownLabel);
                st.setFromX(1.0); st.setFromY(1.0);
                st.setToX(1.3); st.setToY(1.3);
                st.setAutoReverse(true);
                st.setCycleCount(2);
                st.play();
            } else {
                dialog.close();
                startMultiplayerGameWindow();
                cancelQueue(); // Clean up HomeView queue UI elements
            }
        }));
        countdownTimeline.setCycleCount(5);
        countdownTimeline.play();
    }

    private void showNoMatchFoundDialog() {
        Stage dialog = new Stage();
        dialog.initOwner(stage);
        dialog.initModality(Modality.APPLICATION_MODAL);
        dialog.setTitle("No Match Found");
        VBox box = new VBox(15);
        box.setAlignment(javafx.geometry.Pos.CENTER);
        box.setStyle("-fx-padding: 20px; -fx-background-color: rgba(0,0,0,0.7);");
        Label title = new Label("No Match Found");
        title.setStyle("-fx-font-size: 22px; -fx-text-fill: #d32f2f; -fx-font-family: 'Minecraftia';");
        Label message = new Label("No other players joined in time.\nPlease try again.");
        message.setStyle("-fx-font-size: 16px; -fx-text-fill: #fff; -fx-font-family: 'Minecraftia'; -fx-text-alignment: center;");
        Button closeBtn = new Button("OK");
        closeBtn.setStyle("-fx-font-size: 16px; -fx-background-color: #727272; -fx-text-fill: #fff; -fx-background-radius: 8; -fx-cursor: hand;");
        closeBtn.setOnAction(e -> dialog.close());
        box.getChildren().addAll(title, message, closeBtn);
        javafx.scene.Scene scene = new javafx.scene.Scene(box, 400, 220); // Increased height a bit
        dialog.setScene(scene);
        dialog.setResizable(false);
        dialog.show();
    }

    private void startMultiplayerGameWindow() {
        Stage multiplayerStage = new Stage();
        MultiplayerGameView multiplayerGameView = new MultiplayerGameView();
        multiplayerGameView.start(multiplayerStage, gameService, username, () -> {
            setMenuButtonsDisabled(false); // Re-enable menu buttons when game window closes
            stage.show(); 
        });
        stage.hide();
        multiplayerGameView.show();
    }

    @FXML
    private void handleStartGame() {
        Stage gameStage = new Stage();
        GameView gameView = new GameView();
        gameView.start(gameStage, gameService, username, () -> stage.show());
        stage.hide();
        gameView.show();
    }

   @FXML
   private void handleViewLeaderboard() {
       try {
           Stage leaderboardStage = new Stage();
           LeaderboardView leaderboardView = new LeaderboardView();
            leaderboardView.start(leaderboardStage, gameService, () -> stage.show());
           stage.hide();
           leaderboardView.show();
       } catch (Exception e) {
            // Optionally show error
       }
   }

    @FXML
    private void handleLogout() {
        if (isQueueing) {
            cancelQueue(); // Ensure queue is cancelled if logging out while queueing
        }
        try {
            if (gameService != null && username != null) {
                gameService.logout(username);
            }
        } catch (Exception e) {
            // Optionally log error
        }
        if (stage != null) stage.close();
        if (onLogout != null) onLogout.run();
    }

    @FXML
    private void handleMatchHistory() {
        Stage historyStage = new Stage();
        client.player.view.MatchHistoryView historyView = new client.player.view.MatchHistoryView();
        historyView.start(historyStage, gameService, username, () -> stage.show());
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

