package client.player.controller;

import GameModule.GameService;
import client.player.helper.GameTimerHelper;
import client.player.helper.GameViewHelper;
import client.player.helper.KeyboardHelper;
import client.player.model.MultiplayerGameModel;
import client.player.model.MultiplayerGameModel.LobbyState;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.scene.image.ImageView;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.StackPane;
import javafx.stage.Stage;
import javafx.scene.image.Image;
import javafx.animation.Timeline;
import javafx.util.Duration;
import java.util.*;
import client.player.helper.ConfettiHelper;

public class MultiplayerGameViewController implements MultiplayerGameModel.LobbyStateListener {
    @FXML private StackPane root;
    @FXML private ImageView hangmanImage;
    @FXML private Label wordDisplay;
    @FXML private Button backButton;
    @FXML private Label timerLabel;
    @FXML private Label roundLabel;
    @FXML private HBox scoresPanel;
    @FXML private GridPane keyboardGrid;
    @FXML private ImageView exitGameButton;
    @FXML private Label roundWinnerBanner;

    private Stage stage;
    private MultiplayerGameModel model;
    private Runnable onBackToMenu;
    private KeyboardHelper keyboardHelper;
    private GameTimerHelper gameTimerHelper;
    private Timeline lobbyPoller;
    private Map<String, Label> playerScoreLabels = new HashMap<>();
    private boolean gameStarted = false;
    private int lastRoundNumber = -1;
    private boolean gameOverDialogShown = false;
    // Track last incorrect guess count for immediate feedback
    private int lastIncorrectGuesses = 0;

    @FXML
    public void initialize() {
        keyboardHelper = new KeyboardHelper(keyboardGrid, this::handleKeyPress);
        setupLobbyPolling();
        
        // Set exit button image
        if (exitGameButton != null) {
            try {
                Image exitImage = new Image(getClass().getResourceAsStream("/leave.png"));
                exitGameButton.setImage(exitImage);
            } catch (Exception e) {
                System.err.println("Could not load leave.png for exit button: " + e.getMessage());
            }
        }
    }

    private void setupLobbyPolling() {
        lobbyPoller = new Timeline(
            new javafx.animation.KeyFrame(Duration.seconds(1), event -> {
                if (model != null) {
                    model.updateLobbyState();
                }
            })
        );
        lobbyPoller.setCycleCount(Timeline.INDEFINITE);
    }

    public void setStage(Stage stage) {
        this.stage = stage;
    }

    public void setModel(MultiplayerGameModel model) {
        this.model = model;
        model.setLobbyStateListener(this);
    }

    public void setOnBackToMenu(Runnable onBackToMenu) {
        this.onBackToMenu = onBackToMenu;
    }

    public void startNewGame() {
        resetUI();
        model.startGame();
        lobbyPoller.play();
        showWaitingUI();
    }

    private void showWaitingUI() {
        wordDisplay.setText("Waiting for players...");
        keyboardGrid.setVisible(false);
        timerLabel.setText("");
        roundLabel.setText("Lobby");
    }

    private void resetUI() {
        keyboardGrid.setVisible(false);
        hangmanImage.setImage(null);
        resetKeyboard();
        timerLabel.setText("");
        scoresPanel.getChildren().clear();
        playerScoreLabels.clear();
        gameStarted = false;
    }

    private void resetKeyboard() {
        keyboardHelper.resetKeyboard();
    }

    @Override
    public void onLobbyUpdate(LobbyState state) {
        Platform.runLater(() -> {
            int currentRound = state.getIntFromGameState("currentRound", 0);
            boolean roundInProgress = state.getGameState() != null && Boolean.TRUE.equals(state.getGameState().get("roundInProgress"));
            String roundWinner = state.getStringFromGameState("roundWinner", "");
            boolean isStarted = "STARTED".equals(state.getState());
            boolean isWaiting = "WAITING".equals(state.getState());
            boolean isPlayerFinished = false;
            if (isStarted && state.getGameState() != null) {
                Object finishedObj = state.getGameState().get("playerFinishTimes");
                if (finishedObj instanceof Map) {
                    isPlayerFinished = ((Map<?,?>)finishedObj).containsKey(model.getUsername());
                }
                if (state.getIntFromGameState("incorrectGuesses", 0) >= 5 || !state.getStringFromGameState("maskedWord", "_").contains("_")) {
                    isPlayerFinished = true;
                }
            }
            if (currentRound != lastRoundNumber && roundInProgress && isStarted) {
                resetForNewRound(state);
                lastRoundNumber = currentRound;
            }
            updateScoresPanel(state);

            wordDisplay.setText(state.getStringFromGameState("maskedWord", ""));
            int incorrectGuesses = state.getIntFromGameState("incorrectGuesses", 0);
            updateHangmanImage(incorrectGuesses);
            lastIncorrectGuesses = incorrectGuesses;

            String sessionResult = state.getStringFromGameState("sessionResult", "");
            boolean gameOver = "WIN".equals(sessionResult) || "LOSE".equals(sessionResult);
            if (gameOver && !gameOverDialogShown) {
                gameOverDialogShown = true;
                stopPolling();
                if ("WIN".equals(sessionResult)) {
                    GameViewHelper.showWinCelebration(stage, state.getStringFromGameState("maskedWord", ""), "You won the game!", this::handleBackToMenu);
                } else if ("LOSE".equals(sessionResult)) {
                    GameViewHelper.showGameOverDialog(stage, "You lost the game.", false, this::handleBackToMenu);
                }
                return;
            }

            if (isWaiting) {
                handleWaitingState(state);
                roundLabel.setText("Lobby");
                roundWinnerBanner.setVisible(false);
            } else if (isStarted) {
                roundLabel.setText("Round: " + (state.getIntFromGameState("currentRound", 0) + 1));
                boolean roundOver = incorrectGuesses >= 5 || !state.getStringFromGameState("maskedWord", "_").contains("_");
                if (roundOver) {
                    disableAllKeys();
                    if (!gameOver) {
                        javafx.animation.PauseTransition pause = new javafx.animation.PauseTransition(javafx.util.Duration.seconds(3));
                        pause.setOnFinished(e -> {
                            model.startNextRound();
                        });
                        pause.play();
                    }
                } else {
                    // Disable all keys if player is finished, else enable
                    if (isPlayerFinished) {
                        disableAllKeys();
                    } else {
                        enableAllKeys();
                    }
                }
                handleStartedState(state);
                if (!roundInProgress) {
                    boolean isPlayerWinner = roundWinner.equals(model.getUsername());
                    if (!roundWinner.isEmpty()) {
                        if (isPlayerWinner) {
                            showRoundWinnerBanner("You won this round!", "#4CAF50", true);
                        } else {
                            showRoundWinnerBanner(roundWinner + " won this round!", "#4CAF50", false);
                        }
                    } else {
                        showRoundWinnerBanner("No one won this round.", null, false);
                    }
                } else if (isPlayerFinished) {
                    showRoundWinnerBanner("Opponents still guessing...", "#FFD600", false);
                } else {
                    roundWinnerBanner.setVisible(false);
                }
            } else if ("NOMATCH".equals(state.getState())) {
                handleNoMatchState();
            }
        });
    }

    private void handleWaitingState(LobbyState state) {
        if (!gameStarted) {
            int playerCount = state.getPlayers().size();
            int maxPlayers = state.getMaxPlayers();
            wordDisplay.setText(String.format("Waiting for players (%d/%d)...", playerCount, maxPlayers));
        }
    }

    private void handleStartedState(LobbyState state) {
        if (!gameStarted) {
            gameStarted = true;
            keyboardGrid.setVisible(true);
            resetKeyboard();
            
            // Start round timer
            if (gameTimerHelper != null) {
                gameTimerHelper.stopRoundTimer();
            }
            gameTimerHelper = new GameTimerHelper(timerLabel, this::handleTimeUp);
            gameTimerHelper.startRoundTimer(model.getGameService().getRoundTime(), state.getIntFromGameState("remainingTime", 60));
            
            // Update UI
            wordDisplay.setText(state.getStringFromGameState("maskedWord", ""));
            roundLabel.setText("Round: " + (state.getIntFromGameState("currentRound", 0) + 1));
            updateHangmanImage(state.getIntFromGameState("incorrectGuesses", 0));
            
            // Show game started message
            GameViewHelper.animateWordDisplay(wordDisplay);
        }
    }

    private void handleNoMatchState() {
        stopPolling();
        GameViewHelper.showGameOverDialog(stage, "No match found. Please try again.", false, () -> {
            if (onBackToMenu != null) {
                onBackToMenu.run();
            }
        });
    }

    private void updateScoresPanel(LobbyState state) {
        if (state.getPlayers() == null) return;
        Map<String, Integer> scores = state.getScoresFromGameState();
        if (scores == null) return;
        scoresPanel.getChildren().clear();
        playerScoreLabels.clear();
        for (String player : state.getPlayers()) {
            int score = scores.getOrDefault(player, 0);
            Label scoreLabel = new Label(player + ":" + score);
            scoreLabel.getStyleClass().add("player-score");
            if (player.equals(model.getUsername())) {
                scoreLabel.getStyleClass().add("current-player");
            }
            playerScoreLabels.put(player, scoreLabel);
            scoresPanel.getChildren().add(scoreLabel);
        }
    }

    @FXML
    private void handleKeyPress(javafx.event.ActionEvent event) {
        if (!gameStarted || keyboardGrid.isDisabled()) return;

        Button clickedButton = (Button) event.getSource();
        String letter = clickedButton.getText().toLowerCase();

        try {
            boolean correct = model.makeGuess(letter.charAt(0));
            new animatefx.animation.Pulse(clickedButton).play();

            // Color the key for correct/incorrect
            if (correct) {
                clickedButton.getStyleClass().add("correct");
                GameViewHelper.animateWordDisplay(wordDisplay); // Bounce animation for correct guess
            } else {
                clickedButton.getStyleClass().add("incorrect");
            }
            clickedButton.setDisable(true);

            // Always trigger a poll to update UI and enforce disables and image
            model.updateLobbyState();
        } catch (Exception e) {
            System.err.println("Error handling key press: " + e.getMessage());
        }
    }

    private void handleTimeUp() {
        if (!gameStarted) return;
        // When timer runs out, disable all keys, show banner, and trigger poll
        disableAllKeys();
        showRoundWinnerBanner("Opponents still guessing...", "yellow");
        model.startNextRound(); // Force next round automatically
    }

    private void updateHangmanImage(int incorrectGuesses) {
        String imagePath = "/hangman/hangman" + incorrectGuesses + ".png";
        Image image = new Image(getClass().getResourceAsStream(imagePath));
        hangmanImage.setImage(image);
    }

    @FXML
    public void handleBackToMenu() {
        stopPolling();
        if (model != null && model.getUsername() != null) {
            try {
                model.getGameService().endGameSession(model.getUsername());
                model.getGameService().cleanupPlayerSession(model.getUsername());
            } catch (Exception e) {
                System.err.println("Error cleaning up session: " + e.getMessage());
            }
        }
        if (onBackToMenu != null) {
            onBackToMenu.run();
        }
    }

    @FXML
    private void handleExitGame() {
        GameViewHelper.showExitGameDialog(stage, this::handleBackToMenu);
    }

    public void stopPolling() {
        if (lobbyPoller != null) {
            lobbyPoller.stop();
        }
        if (gameTimerHelper != null) {
            gameTimerHelper.stopRoundTimer();
            gameTimerHelper = null;
        }
    }

    public void onReturned() {
        if (model != null) {
            model.updateLobbyState();
        }
    }

    private void resetForNewRound(LobbyState state) {
        // Round transition explosion animation (like 1v1)
        Runnable afterExplosion = () -> {
            resetKeyboard();
            enableAllKeys();
            keyboardGrid.setDisable(false);
            // Start timer for the new round using the round time from the server/database
            if (gameTimerHelper != null) {
                gameTimerHelper.stopRoundTimer();
            }
            gameTimerHelper = new GameTimerHelper(timerLabel, this::handleTimeUp);
            int roundTime = model.getGameService().getRoundTime();
            int remainingTime = state.getIntFromGameState("remainingTime", roundTime);
            gameTimerHelper.startRoundTimer(roundTime, remainingTime);
            // Update round label and word
            roundLabel.setText("Round: " + (state.getIntFromGameState("currentRound", 0) + 1));
            wordDisplay.setText(state.getStringFromGameState("maskedWord", ""));
            wordDisplay.setVisible(true);
            keyboardGrid.setVisible(true);
            hangmanImage.setVisible(true);
        };
        GameViewHelper.explodeNode(wordDisplay, () ->
            GameViewHelper.explodeNode(keyboardGrid, () ->
                GameViewHelper.explodeNode(hangmanImage, afterExplosion)
            )
        );
    }

    private void showRoundWinnerBanner(String message, String color, boolean showConfetti) {
        roundWinnerBanner.setText(message);
        roundWinnerBanner.setVisible(true);
        roundWinnerBanner.setOpacity(1.0);
        if (showConfetti && root != null) {
            ConfettiHelper.showConfetti(root);
        }
        if (color != null) {
            roundWinnerBanner.setStyle("-fx-font-size: 22px; -fx-font-family: 'Minecraftia'; -fx-background-color: rgba(0,0,0,0.7); -fx-padding: 8 24 8 24; -fx-background-radius: 12; -fx-border-radius: 12; -fx-border-color: #ffdd00; -fx-border-width: 2px; -fx-text-fill: " + color + ";");
        } else {
            roundWinnerBanner.setStyle("-fx-font-size: 22px; -fx-font-family: 'Minecraftia'; -fx-background-color: rgba(0,0,0,0.7); -fx-padding: 8 24 8 24; -fx-background-radius: 12; -fx-border-radius: 12; -fx-border-color: #ffdd00; -fx-border-width: 2px;");
        }
        javafx.animation.FadeTransition fade = new javafx.animation.FadeTransition(javafx.util.Duration.seconds(2.5), roundWinnerBanner);
        fade.setFromValue(1.0);
        fade.setToValue(0.0);
        fade.setDelay(javafx.util.Duration.seconds(1));
        fade.setOnFinished(e -> roundWinnerBanner.setVisible(false));
        fade.play();
    }

    // Keep the old two-argument showRoundWinnerBanner for compatibility
    private void showRoundWinnerBanner(String message, String color) {
        showRoundWinnerBanner(message, color, false);
    }
    private void showRoundWinnerBanner(String message) {
        showRoundWinnerBanner(message, null, false);
    }

    // Helper to disable all keys
    private void disableAllKeys() {
        keyboardGrid.setDisable(true);
        keyboardHelper.getKeyboardButtons().values().forEach(btn -> btn.setDisable(true));
    }
    // Helper to enable all keys
    private void enableAllKeys() {
        keyboardGrid.setDisable(false);
        keyboardHelper.getKeyboardButtons().values().forEach(btn -> btn.setDisable(false));
    }
} 