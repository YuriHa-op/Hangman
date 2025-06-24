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
import javafx.scene.layout.VBox;
import javafx.scene.layout.HBox;
import javafx.scene.layout.StackPane;
import javafx.stage.Stage;
import javafx.scene.image.Image;
import javafx.animation.Timeline;
import javafx.util.Duration;
import java.util.*;
import client.player.helper.SpectatorManager;
import client.player.view.results.GameResultsView;
import javafx.scene.effect.DropShadow;
import javafx.animation.SequentialTransition;
import javafx.scene.paint.Color;
import javafx.animation.KeyFrame;
import client.player.helper.AfkCheckDialog;
import java.util.concurrent.atomic.AtomicBoolean;
import javafx.animation.TranslateTransition;

public class MultiplayerGameViewController implements MultiplayerGameModel.LobbyStateListener {
    @FXML private StackPane root;
    @FXML private ImageView hangmanImage;
    @FXML private Label wordDisplay;
    @FXML private Button backButton;
    @FXML private Label timerLabel;
    @FXML private Label roundLabel;
    @FXML private HBox scoresPanel;
    @FXML private VBox keyboardGrid;
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
    private SpectatorManager spectatorManager = new SpectatorManager();
    private String povPlayer = null; // Whose POV is being shown
    private StackPane spectateOverlay = null;
    private int lastEventCount = 0;

    // AFK Dialog related fields
    private static final long AFK_DIALOG_COOLDOWN_MS = 20000; // 20 seconds cooldown
    private long lastAfkDialogShownTime = 0;
    private AtomicBoolean afkDialogCooldownActive = new AtomicBoolean(false);
    private Timeline afkDialogCooldownTimer;
    private Timeline afkPreCheckDelayTimer; // Timer for the 2-second delay before showing AFK dialog
    private int roundAtAfkCheckStart = -1; // To store round number when AFK check delay starts
    private boolean afkDialogDelayTimerActive = false; // Flag to indicate if the 2s pre-check delay is active

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
        // Listen for spectated player changes
        spectatorManager.addListener(this::onSpectatedPlayerChanged);

        // Initialize AFK Dialog Cooldown Timer
        afkDialogCooldownTimer = new Timeline(new KeyFrame(Duration.millis(AFK_DIALOG_COOLDOWN_MS), e -> {
            afkDialogCooldownActive.set(false);
            System.out.println("AFK Dialog cooldown finished.");
        }));
        afkDialogCooldownTimer.setCycleCount(1); // Run once per start

        // Initialize AFK Pre-Check Delay Timer
        afkPreCheckDelayTimer = new Timeline();
        afkPreCheckDelayTimer.setCycleCount(1);
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
        // model.startGame(); // DO NOT start game again, HomeViewController already did.
        // Game is already started by HomeViewController, just start polling.
        // Instead of starting polling immediately, show match found dialog, then signal ready, then start polling
        model.playerReadyForFirstRound();
        showMatchFoundDialogAndSignalReady();
    }

    private void showMatchFoundDialogAndSignalReady() {
        // Show the match found dialog (implement this as needed)
        // After dialog and any animation, call model.playerReadyForFirstRound(), then start polling
        // For now, simulate with Platform.runLater (replace with actual dialog logic)
        javafx.application.Platform.runLater(() -> {
            // TODO: Replace with actual dialog and animation logic, then call this after they finish
            if (lobbyPoller != null) {
                lobbyPoller.play();
            }
            if (model != null) {
                model.updateLobbyState();
            }
        });
    }

    private void resetUI() {
        keyboardGrid.setVisible(false);
        hangmanImage.setImage(null);
        resetKeyboard();
        timerLabel.setText("");
        scoresPanel.getChildren().clear();
        playerScoreLabels.clear();
        gameStarted = false;
        lastEventCount = 0;
    }

    private void resetKeyboard() {
        keyboardHelper.resetKeyboard();
    }

    @Override
    public void onLobbyUpdate(LobbyState state) {
        Platform.runLater(() -> {
            // --- DEBUGGING: Print received playerWinStreaks --- 
            // if (state.getGameState() != null && state.getGameState().containsKey("playerWinStreaks")) {
            //     System.out.println("MultiplayerGameViewController: Received playerWinStreaks from server: " + state.getGameState().get("playerWinStreaks"));
            // } else {
            //     System.out.println("MultiplayerGameViewController: playerWinStreaks not found in received game state.");
            // }
            // --- END DEBUGGING ---

            int currentRound = state.getIntFromGameState("currentRound", 0);
            boolean roundInProgress = state.getGameState() != null && Boolean.TRUE.equals(state.getGameState().get("roundInProgress"));
            String roundWinner = state.getStringFromGameState("roundWinner", "");

            // If the server indicates the round is now in progress, close any lingering AFK dialog
            // and cancel any pending AFK dialog show attempts
            if (roundInProgress) {
                AfkCheckDialog.closeDialog(); // Closes the primary AFK dialog
                AfkCheckDialog.closeLastChanceDialog(); // Closes the "Last Chance" dialog if it's open
                if (afkPreCheckDelayTimer != null) afkPreCheckDelayTimer.stop();
                afkDialogDelayTimerActive = false; // Reset flag if round starts
            }

            boolean isStarted = "STARTED".equals(state.getState());
            boolean isWaiting = "WAITING".equals(state.getState());
            boolean isPlayerFinished = false; // This is for the current user, not necessarily the POV
            if (isStarted && state.getGameState() != null) {
                Object finishedObj = state.getGameState().get("playerFinishTimes");
                if (finishedObj instanceof Map) {
                    isPlayerFinished = ((Map<?,?>)finishedObj).containsKey(model.getUsername());
                }
                String povForFinishedCheck = povPlayer != null ? povPlayer : model.getUsername();
                if (state.getPlayerIncorrectGuesses(povForFinishedCheck) >= 5 || !state.getPlayerMaskedWord(povForFinishedCheck).contains("_")) {
                    // This was a local check, isPlayerFinished for the actual user is what matters for some UI elements
                    if (povForFinishedCheck.equals(model.getUsername())) {
                        isPlayerFinished = true;
                    }
                }
            }
            if (currentRound != lastRoundNumber && roundInProgress && isStarted) {
                resetForNewRound(state);
                lastRoundNumber = currentRound;
            }
            updateScoresPanel(state);

            // If spectating and the spectated player is now finished, or if the round itself has ended, return to own POV
            if (povPlayer != null && !povPlayer.equals(model.getUsername())) {
                int povIncorrect = state.getPlayerIncorrectGuesses(povPlayer);
                String povMasked = state.getPlayerMaskedWord(povPlayer);
                boolean povWordGuessed = (povMasked != null && !povMasked.isEmpty() && !povMasked.contains("_")); // check for non-empty mask
                boolean povMaxMisses = (povIncorrect >= 5);
                
                // Enhanced Debug Logging for spectator return logic
                System.out.println(String.format("[Spectator Debug] Timestamp: %d, POV: %s, Incorrect: %d (MaxMisses: %b), Masked: '%s' (WordGuessed: %b), RoundInProgress: %b, lobbyId: %s, modelUser: %s",
                                   System.currentTimeMillis(), povPlayer, povIncorrect, povMaxMisses, povMasked, povWordGuessed, roundInProgress, model.getLobbyId(), model.getUsername()));

                boolean spectatedPlayerFinishedRound = povMaxMisses || povWordGuessed; // Re-evaluating for clarity based on logged vars
                
                if (spectatedPlayerFinishedRound || !roundInProgress) {
                    System.out.println("[Spectator] POV return triggered for " + povPlayer + ". Reason: spectatedPlayerFinished=" + spectatedPlayerFinishedRound + " (MaxMisses: " + povMaxMisses + ", WordGuessed: " + povWordGuessed + "), roundInProgress=" + roundInProgress + ". Returning to " + model.getUsername());
                    spectatorManager.setSpectatedPlayer(model.getUsername());
                } else {
                     System.out.println("[Spectator Debug] POV return NOT triggered for " + povPlayer + ". spectatedPlayerFinished=" + spectatedPlayerFinishedRound + " (MaxMisses: " + povMaxMisses + ", WordGuessed: " + povWordGuessed + "), roundInProgress=" + roundInProgress);
                }
            }

            String currentActualPov = povPlayer != null ? povPlayer : model.getUsername(); // Determine the actual POV for UI updates
            wordDisplay.setText(state.getPlayerMaskedWord(currentActualPov));
            int incorrectGuessesForDisplay = state.getPlayerIncorrectGuesses(currentActualPov);
            updateHangmanImage(incorrectGuessesForDisplay);
            lastIncorrectGuesses = incorrectGuessesForDisplay; // This seems to be for the current POV
            updateKeyboardForPOV(state, currentActualPov); 

            String sessionResult = state.getStringFromGameState("sessionResult", "");
            boolean gameOver = "WIN".equals(sessionResult) || "LOSE".equals(sessionResult);
            if (gameOver && !gameOverDialogShown) {
                gameOverDialogShown = true;
                stopPolling();

                final String gameId = state.getGameId();

                // Prepare data for results screen
                final List<String> playerNames = new ArrayList<>(state.getAllPlayersEver());
                final Map<String, Integer> finalScores = new HashMap<>(state.getScoresFromGameState());

                Runnable showResultsAndGoHome = () -> {
                    // Defer showing the results view to allow the current dialog to fully close
                    Platform.runLater(() -> {
                        GameResultsView resultsView = new GameResultsView();
                        // Pass the main game stage (this.stage) as owner
                        resultsView.showResults(this.stage, playerNames, finalScores, model, gameId, this::handleBackToMenu);
                    });
                };

                if ("WIN".equals(sessionResult)) {
                    GameViewHelper.showWinCelebration(this.stage, state.getPlayerMaskedWord(currentActualPov), "You won the game!", showResultsAndGoHome);
                } else if ("LOSE".equals(sessionResult)) {
                    GameViewHelper.showGameOverDialog(this.stage, "You lost the game.", false, showResultsAndGoHome);
                }
                return;
            }

            if (isWaiting) {
                handleWaitingState(state);
                roundLabel.setText("Lobby");
                roundWinnerBanner.setVisible(false);
                AfkCheckDialog.closeDialog(); // Close if waiting for players
                AfkCheckDialog.closeLastChanceDialog(); // Also ensure last chance is closed if we regress to waiting
            } else if (isStarted) {
                roundLabel.setText("Round: " + (state.getIntFromGameState("currentRound", 0) + 1));
                boolean roundOver = incorrectGuessesForDisplay >= 5 || !state.getStringFromGameState("maskedWord", "_").contains("_");
                if (roundOver || isPlayerFinished) { // Check current player's finished state
                    disableAllKeys();
                    if (!gameOver) {
                        javafx.animation.PauseTransition pause = new javafx.animation.PauseTransition(javafx.util.Duration.seconds(3));
                        pause.setOnFinished(e -> {
                            model.startNextRound();
                        });
                        pause.play();
                    }
                } else {
                    // Keyboard state is handled by updateKeyboardForPOV
                    // No explicit enableAllKeys() here.
                }
                handleStartedState(state); // Ensures game elements are visible if started
                if (!roundInProgress) {
                    boolean isPlayerWinner = roundWinner.equals(model.getUsername());
                    if (!roundWinner.isEmpty()) {
                        if (isPlayerWinner) {
                            showRoundWinnerBanner("You won this round!", "#4CAF50", true);
                            AfkCheckDialog.closeDialog(); // Close dialog if there's a winner
                            AfkCheckDialog.closeLastChanceDialog(); // Also close last chance
                            if (afkPreCheckDelayTimer != null) afkPreCheckDelayTimer.stop(); // Stop pending AFK check
                            afkDialogDelayTimerActive = false; // Reset flag
                        } else {
                            showRoundWinnerBanner(roundWinner + " won this round!", "#4CAF50", false);
                            AfkCheckDialog.closeDialog(); // Close dialog if there's a winner
                            AfkCheckDialog.closeLastChanceDialog(); // Also close last chance
                            if (afkPreCheckDelayTimer != null) afkPreCheckDelayTimer.stop(); // Stop pending AFK check
                            afkDialogDelayTimerActive = false; // Reset flag
                        }
                    } else {
                        showRoundWinnerBanner("No one won this round.", null, false);
                        // Potentially show AFK dialog if conditions met
                        if (!gameOver && !AfkCheckDialog.isShowing() && !afkDialogCooldownActive.get() && !afkDialogDelayTimerActive) {
                            System.out.println("No round winner, initiating AFK dialog sequence. Current Round: " + currentRound);
                            roundAtAfkCheckStart = currentRound; // Capture current round
                            afkDialogDelayTimerActive = true; // Set flag that delay timer is now active

                            // Stop any existing pre-check timer (should not be necessary if logic is correct, but safe)
                            // if (afkPreCheckDelayTimer != null) afkPreCheckDelayTimer.stop(); 

                            afkPreCheckDelayTimer.getKeyFrames().setAll(
                                new KeyFrame(Duration.seconds(4), e -> { // Changed to 4 seconds
                                    afkDialogDelayTimerActive = false; // Timer has fired, reset the flag

                                    // Re-check if dialog is already showing or cooldown is active,
                                    // as these states might have changed during the 4s delay.
                                    if (AfkCheckDialog.isShowing() || afkDialogCooldownActive.get()) {
                                        System.out.println("AFK Dialog show cancelled (dialog already showing or cooldown active post-delay).");
                                        return;
                                    }

                                    int latestRoundFromServer = state.getIntFromGameState("currentRound", 0);
                                    boolean latestRoundInProgress = state.getGameState() != null && Boolean.TRUE.equals(state.getGameState().get("roundInProgress"));

                                    if (roundAtAfkCheckStart == latestRoundFromServer && !latestRoundInProgress) {
                                        System.out.println("AFK Pre-check delay ended. Round is still " + roundAtAfkCheckStart + " and not in progress. Showing AFK dialog.");
                                        AfkCheckDialog.show(stage,
                                            () -> { // onYesClicked
                                                System.out.println("AFK Dialog: Yes clicked. Attempting to start next round.");
                                                model.startNextRound();
                                                startAfkDialogCooldown();
                                                AfkCheckDialog.closeDialog();
                                            },
                                            () -> { // onTimedOut for the *original* AFK Dialog
                                                System.out.println("AFK Dialog: Timed out. Preparing for Last Chance Dialog.");
                                                startAfkDialogCooldown(); // Start cooldown as usual
                                                
                                                // Call method to show the new "Last Chance" dialog
                                                // This method will be created in AfkCheckDialog.java
                                                AfkCheckDialog.showLastChanceDialog(stage,
                                                    () -> { // onLastChanceClicked for the NEW dialog
                                                        System.out.println("Last Chance Dialog: Button clicked. Attempting to start next round.");
                                                        model.startNextRound();
                                                        // Cooldown is already started when original AFK timed out,
                                                        // If model.startNextRound() fails and leads to another stall, the cycle will repeat.
                                                    }
                                                );
                                            }
                                        );
                                    } else {
                                        System.out.println("AFK Dialog show cancelled. Round changed or is in progress. Was " + roundAtAfkCheckStart + ", now " + latestRoundFromServer + ", inProgress: " + latestRoundInProgress);
                                    }
                                })
                            );
                            afkPreCheckDelayTimer.playFromStart();
                        }
                    }
                } else if (isPlayerFinished) {
                    showRoundWinnerBanner("Opponents still guessing...", "#FFD600", false);
                } else {
                    roundWinnerBanner.setVisible(false);
                }
            } else if ("NOMATCH".equals(state.getState())) {
                handleNoMatchState();
            }

            int serverRemainingTime = state.getIntFromGameState("remainingTime", model.getGameService().getRoundTime());
            // Stop timer if round is not in progress
            if (!roundInProgress) {
                if (gameTimerHelper != null) {
                    gameTimerHelper.stopRoundTimer();
                }
                timerLabel.setText("0");
                new animatefx.animation.Shake(timerLabel).play();
            } else {
                // Always sync the timer to the server's value
                if (gameTimerHelper == null) {
                    gameTimerHelper = new GameTimerHelper(timerLabel, this::handleTimeUp);
                    gameTimerHelper.startRoundTimer(model.getGameService().getRoundTime(), serverRemainingTime);
                } else {
                    gameTimerHelper.setTime(serverRemainingTime);
                }
            }

            // Process Game Events
            List<String> events = state.getGameEvents();
            if (events != null && events.size() > lastEventCount) {
                List<String> newEvents = events.subList(lastEventCount, events.size());
                for (String event : newEvents) {
                    // Don't show the user their own leave message
                    if (!event.contains(model.getUsername())) {
                        showNotification(event);
                    }
                }
                lastEventCount = events.size();
            }
        });
    }

    private void handleWaitingState(LobbyState state) {
        // This method might be redundant now or need adjustment,
        // it don't explicitly call showWaitingUI() anymore in startNewGame.
        // The game should transition from HomeView's queue directly to a STARTED state.
        if (!gameStarted) {
            int playerCount = state.getPlayers().size();
            int maxPlayers = state.getMaxPlayers();
            // Update a generic status if needed, but primary update comes from handleStartedState
            // wordDisplay.setText(String.format("Waiting for players (%d/%d)...", playerCount, maxPlayers));
            roundLabel.setText("Preparing Game..."); // More appropriate if game is about to start
        }
    }

    private void handleStartedState(LobbyState state) {
        if (!gameStarted) {
            gameStarted = true;
            keyboardGrid.setVisible(true);
            // resetKeyboard(); // resetForNewRound will handle this if it's a new round
            
            // Start round timer
            if (gameTimerHelper != null) {
                gameTimerHelper.stopRoundTimer();
            }
            gameTimerHelper = new GameTimerHelper(timerLabel, this::handleTimeUp);
            int roundTime = model.getGameService().getRoundTime();
            int remainingTime = state.getIntFromGameState("remainingTime", roundTime);
            gameTimerHelper.startRoundTimer(roundTime, remainingTime);
            
            if (povPlayer == null) povPlayer = model.getUsername();
            String pov = povPlayer;
            wordDisplay.setText(state.getPlayerMaskedWord(pov));
            roundLabel.setText("Round: " + (state.getIntFromGameState("currentRound", 0) + 1));
            updateHangmanImage(state.getPlayerIncorrectGuesses(pov)); // Use POV-specific incorrect guesses
            updateKeyboardForPOV(state, pov);
            
            // Show game started message
            // GameViewHelper.animateWordDisplay(wordDisplay); // This can be distracting if round just started
        }
        // If game is already started, ensure UI elements like keyboard visibility are correct based on state
        boolean isPlayerFinished_local = isUserDoneGuessing(state, model.getUsername());
        boolean isSpectating = povPlayer != null && !povPlayer.equals(model.getUsername());

        if(isSpectating || isPlayerFinished_local){
            disableAllKeys();
        } else {
            // Ensure keyboard state (pressed keys) is also updated
            updateKeyboardForPOV(state, model.getUsername());
        }
        keyboardGrid.setVisible(true); // Should generally be visible in started state unless round is over
    }

    private boolean isCurrentPlayerActuallyFinished(LobbyState state) {
        String currentPlayerUsername = model.getUsername();
        String maskedWord = state.getPlayerMaskedWord(currentPlayerUsername);
        int incorrectGuesses = state.getPlayerIncorrectGuesses(currentPlayerUsername);
        return (incorrectGuesses >= 5) || (maskedWord != null && !maskedWord.contains("_"));
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
        
        // Stop animations for players no longer in the list or whose labels will be recreated
        List<String> currentPlayersInPanel = new ArrayList<>(playerScoreLabels.keySet());
        for (String existingPlayer : currentPlayersInPanel) {
            if (!state.getPlayers().contains(existingPlayer)) {
                playerScoreLabels.remove(existingPlayer);
            }
        }

        // Temporarily store new labels to avoid concurrent modification if we were iterating playerScoreLabels for stopping
        Map<String, Label> newPlayerScoreLabels = new HashMap<>();

        boolean canSpectate = isUserDoneGuessing(state);
        for (String player : state.getPlayers()) {
            int score = scores.getOrDefault(player, 0);
            Label label = playerScoreLabels.get(player); // Try to reuse existing label
            if (label == null) {
                label = new Label();
                label.getStyleClass().add("player-score");
            }
            label.setText(player + ":" + score); // Update text
            label.setStyle(""); // Clear any previous inline styles

            HBox playerBox = new HBox(5); // spacing between icon and label
            playerBox.setAlignment(javafx.geometry.Pos.CENTER_LEFT);
            playerBox.setPadding(new javafx.geometry.Insets(2, 5, 2, 5));

            if (player.equals(model.getUsername())) {
                if (!label.getStyleClass().contains("current-player")) {
                    label.getStyleClass().add("current-player");
                }
            } else {
                label.getStyleClass().remove("current-player");
            }

            // Win streak glow
            int winStreak = state.getPlayerWinStreak(player);

            if (winStreak >= 2) {
                playerBox.setStyle("-fx-background-color: #1A237E; -fx-background-radius: 5;");
            } else {
                playerBox.setStyle(""); // Reset to default
            }

            // Only show eye icon if user can spectate and not self
            if (canSpectate && !player.equals(model.getUsername())) {
                try {
                    Image eyeImg = new Image(getClass().getResourceAsStream("/eye.png"));
                    ImageView eyeView = new ImageView(eyeImg);
                    eyeView.setFitWidth(28);
                    eyeView.setFitHeight(28);
                    eyeView.setPreserveRatio(true);
                    eyeView.setStyle("-fx-cursor: hand;");
                    eyeView.setOnMouseClicked(e -> spectatorManager.setSpectatedPlayer(player));
                    playerBox.getChildren().add(eyeView);
                } catch (Exception e) {
                    System.err.println("Could not load eye.png for spectate icon: " + e.getMessage());
                }
            }
            playerBox.getChildren().add(label);
            newPlayerScoreLabels.put(player, label); // Store in new map
            scoresPanel.getChildren().add(playerBox);
        }
        playerScoreLabels = newPlayerScoreLabels; // Assign new map to the class field
    }

    private boolean isUserDoneGuessing(LobbyState state) { // Keep old signature for compatibility if used elsewhere
        return isUserDoneGuessing(state, model.getUsername());
    }

    private boolean isUserDoneGuessing(LobbyState state, String player) {
        // User is done if they have guessed the word or lost all lives
        String masked = state.getPlayerMaskedWord(player);
        int incorrect = state.getPlayerIncorrectGuesses(player);
        return (incorrect >= 5) || (masked != null && !masked.contains("_"));
    }

    @FXML
    private void handleKeyPress(javafx.event.ActionEvent event) {
        if (!gameStarted || keyboardGrid.isDisabled()) return;

        Button clickedButton = (Button) event.getSource();
        String letter = clickedButton.getText().toLowerCase();

        try {
            boolean correct = model.makeGuess(letter.charAt(0));

            // Always remove both classes before adding
            clickedButton.getStyleClass().removeAll("correct", "incorrect");
            // Color the key for correct/incorrect
            if (correct) {
                clickedButton.getStyleClass().add("correct");
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
        if (model != null) {
            model.leaveGame();
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
        AfkCheckDialog.closeDialog(); // Ensure dialog is closed when polling stops
        AfkCheckDialog.closeLastChanceDialog(); // Ensure last chance dialog is also closed
        if (afkDialogCooldownTimer != null) { // Stop cooldown timer
            afkDialogCooldownTimer.stop();
        }
        if (afkPreCheckDelayTimer != null) { // Stop pre-check delay timer
            afkPreCheckDelayTimer.stop();
        }
        afkDialogDelayTimerActive = false; // Reset flag here as well
    }


    private void resetForNewRound(LobbyState state) {
        // Round transition explosion animation (like 1v1)
        Runnable afterExplosion = () -> {
            resetKeyboard(); // This now correctly re-enables keys for a new round
            // keyboardGrid.setDisable(false); // resetKeyboard handles button states, grid interactivity via updateKeyboardForPOV
            
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
        
        wordDisplay.setVisible(false);
        keyboardGrid.setVisible(false);
        hangmanImage.setVisible(false);

        javafx.animation.PauseTransition pause = new javafx.animation.PauseTransition(javafx.util.Duration.seconds(2));
        pause.setOnFinished(event -> afterExplosion.run());
        pause.play();
    }

    private void showRoundWinnerBanner(String message, String color, boolean showConfetti) {
        roundWinnerBanner.setText(message);
        roundWinnerBanner.setVisible(true);
        roundWinnerBanner.setOpacity(1.0);
        if (showConfetti && root != null) {
            // Defer confetti call to ensure root pane is fully laid out
            Platform.runLater(() -> {
                // Confetti removed
            });
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

    private void onSpectatedPlayerChanged(String playerName) {
        this.povPlayer = playerName;
        showSpectateTransition(playerName);
    }

    private void showSpectateTransition(String playerName) {
        if (root == null) return;
        if (spectateOverlay == null) {
            spectateOverlay = new StackPane();
            spectateOverlay.setStyle("-fx-background-color: rgba(0,0,0,0.85); -fx-alignment: center;");
            Label label = new Label();
            label.setStyle("-fx-font-size: 38px; -fx-text-fill: #ffdd00; -fx-font-family: 'Minecraftia';");
            spectateOverlay.getChildren().add(label);
            root.getChildren().add(spectateOverlay);
            spectateOverlay.setMouseTransparent(true);
        }
        
        Label label = (Label) spectateOverlay.getChildren().get(0);
        if (playerName != null && !playerName.equals(model.getUsername())) {
            label.setText("Spectating: " + playerName);
        } else {
            label.setText("Returning to your POV");
        }
        
        spectateOverlay.setVisible(true);
        
        javafx.animation.PauseTransition pause = new javafx.animation.PauseTransition(javafx.util.Duration.seconds(1));
        pause.setOnFinished(e -> spectateOverlay.setVisible(false));
        pause.play();
    }

    private void updateKeyboardForPOV(LobbyState state, String povToUpdate) {
        Set<Character> serverGuessesForPov = state.getPlayerGuesses(povToUpdate);
        String actualWordForPov = state.getPlayerActualWord(povToUpdate).toUpperCase();
        boolean isCurrentPlayerPov = povToUpdate.equals(model.getUsername());
        boolean isSpectatorModeActive = povPlayer != null && !povPlayer.equals(model.getUsername());

        keyboardGrid.setDisable(isSpectatorModeActive && !isCurrentPlayerPov); // Grid disabled if spectating OTHERS

        keyboardHelper.getKeyboardButtons().forEach((keyLetterString, btn) -> {
            char kChar = keyLetterString.charAt(0);

            if (isSpectatorModeActive && povToUpdate.equals(this.povPlayer)) {
                // Viewing the spectated player (this.povPlayer)
                btn.getStyleClass().removeAll("correct", "incorrect"); // Clear previous spectator styles
                if (serverGuessesForPov.contains(kChar)) {
                    btn.setDisable(true);
                    if (actualWordForPov.contains(keyLetterString)) {
                        btn.getStyleClass().add("correct");
                    } else {
                        btn.getStyleClass().add("incorrect");
                    }
                } else {
                    btn.setDisable(false); // Key available for the spectated player
                }
            } else if (isCurrentPlayerPov && !isSpectatorModeActive) {
                // Active player's own view (not spectating anyone else)
                if (serverGuessesForPov.contains(kChar)) {
                    // Server has processed this guess for the current player
                    btn.getStyleClass().removeAll("correct", "incorrect"); // Clear local/old styles
                    btn.setDisable(true); // Server confirms guess, ensure disabled
                    if (actualWordForPov.contains(keyLetterString)) {
                        btn.getStyleClass().add("correct");
                    } else {
                        btn.getStyleClass().add("incorrect");
                    }
                } else {
                    // Server has NOT processed this guess for the current player yet.
                    // The button's state (disabled + styled .correct/.incorrect)
                    // should reflect what handleKeyPress set. We don't touch its styles or disabled state here.
                    // It remains disabled if handleKeyPress disabled it.
                    // It retains .correct/.incorrect if handleKeyPress set it.
                }
            } else {

                 if (!isCurrentPlayerPov) btn.setDisable(true);
            }
        });

        if (isCurrentPlayerPov && !isSpectatorModeActive) {
            boolean isPlayerFinishedForRound = isUserDoneGuessing(state, model.getUsername());
            if (isPlayerFinishedForRound) {
                disableAllKeys(); 
            } else {
                // Make sure grid itself is enabled if player is not finished and not spectating
                keyboardGrid.setDisable(false);
            }
        }
    }

    private void startAfkDialogCooldown() {
        afkDialogCooldownActive.set(true);
        afkDialogCooldownTimer.playFromStart(); // Restart the cooldown timer
        System.out.println("AFK Dialog cooldown started.");
    }

    private void showNotification(String message) {
        if (root == null) return;

        Label notificationLabel = new Label(message);
        notificationLabel.setStyle(
            "-fx-background-color: rgba(45, 45, 45, 0.95); " +
            "-fx-text-fill: white; " +
            "-fx-font-size: 14px; " +
            "-fx-padding: 10 20 10 20; " +
            "-fx-background-radius: 15; " +
            "-fx-border-radius: 15;"
        );
        notificationLabel.setEffect(new DropShadow(10, Color.BLACK));

        StackPane.setAlignment(notificationLabel, javafx.geometry.Pos.TOP_CENTER);
        notificationLabel.setTranslateY(-100); // Start off-screen

        root.getChildren().add(notificationLabel);

        // Animate in
        TranslateTransition slideIn = new TranslateTransition(Duration.millis(400), notificationLabel);
        slideIn.setToY(20); // Slide to 20px from the top

        // Pause
        javafx.animation.PauseTransition pause = new javafx.animation.PauseTransition(Duration.seconds(3));

        // Animate out
        TranslateTransition slideOut = new TranslateTransition(Duration.millis(400), notificationLabel);
        slideOut.setToY(-100);

        // Chain animations
        SequentialTransition sequence = new SequentialTransition(slideIn, pause, slideOut);
        sequence.setOnFinished(e -> root.getChildren().remove(notificationLabel));
        sequence.play();
    }
} 