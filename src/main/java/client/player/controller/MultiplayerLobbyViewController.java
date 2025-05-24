package client.player.controller;

import client.player.model.MultiplayerGameModel;
import client.player.model.MultiplayerGameModel.LobbyState;
import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.layout.VBox;
import javafx.scene.text.Text;
import javafx.util.Duration;
import java.util.List;

public class MultiplayerLobbyViewController {
    @FXML private Label playerCountLabel;
    @FXML private Label timerLabel;
    @FXML private VBox playerListBox;
    @FXML private Label statusLabel;
    @FXML private Button leaveButton;

    private MultiplayerGameModel model;
    private String username;
    private Runnable onStartGame;
    private Timeline poller;
    private int lastPlayerCount = 0;

    public void setModel(MultiplayerGameModel model, String username) {
        this.model = model;
        this.username = username;
        model.setLobbyStateListener(this::onLobbyUpdate);
        startPolling();
    }

    public void setOnStartGame(Runnable onStartGame) {
        this.onStartGame = onStartGame;
    }

    private void startPolling() {
        if (poller != null) poller.stop();
        poller = new Timeline(new KeyFrame(Duration.seconds(1), e -> {
            if (model != null) model.updateLobbyState();
        }));
        poller.setCycleCount(Timeline.INDEFINITE);
        poller.play();
    }

    private void stopPolling() {
        if (poller != null) poller.stop();
    }

    private void onLobbyUpdate(LobbyState state) {
        Platform.runLater(() -> {
            // Update player count
            int playerCount = state.getPlayers() != null ? state.getPlayers().size() : 0;
            int maxPlayers = state.getMaxPlayers();
            playerCountLabel.setText(playerCount + "/" + maxPlayers + " players");

            // Update timer
            long creationTime = state.getCreationTime();
            int queueTime = state.getQueueTimeSeconds();
            long now = System.currentTimeMillis();
            int secondsLeft = (int)Math.max(0, queueTime - (now - creationTime) / 1000);
            timerLabel.setText(String.valueOf(secondsLeft));

            // Update player list
            playerListBox.getChildren().clear();
            if (state.getPlayers() != null) {
                for (String player : state.getPlayers()) {
                    Label label = new Label(player);
                    label.getStyleClass().add("player-score");
                    if (player.equals(username)) {
                        label.getStyleClass().add("current-player");
                    }
                    playerListBox.getChildren().add(label);
                }
            }

            // Update status
            if ("WAITING".equals(state.getState())) {
                statusLabel.setText("Waiting for more players...");
            } else if ("STARTED".equals(state.getState())) {
                statusLabel.setText("Game starting!");
                stopPolling();
                if (onStartGame != null) onStartGame.run();
            } else if ("NOMATCH".equals(state.getState())) {
                statusLabel.setText("No match found. Returning to menu...");
                stopPolling();
                // Optionally, call a callback to return to menu
            }
        });
    }

    @FXML
    private void handleLeaveLobby() {
        stopPolling();
        // Optionally, notify the server to leave the lobby
        // Call a callback to return to menu if needed
        if (onStartGame != null) onStartGame.run(); // Reuse for now
    }
} 