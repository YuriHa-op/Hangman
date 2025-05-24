package client.player.controller;

import GameModule.GameService;
import client.player.helper.GameTimerHelper;
import client.player.helper.GameViewHelper;
import client.player.helper.KeyboardHelper;
import client.player.model.GameModel;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.scene.image.ImageView;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.VBox;
import javafx.scene.layout.StackPane;
import javafx.stage.Stage;
import javafx.scene.image.Image;
import javafx.event.ActionEvent;
import javafx.animation.*;
import javafx.scene.paint.Color;
import javafx.util.Duration;
import GameModule.GameStateDTO;
import client.player.helper.GameStatePoller;
import animatefx.animation.Bounce;
import animatefx.animation.FadeOut;
import animatefx.animation.FadeIn;
import animatefx.animation.Pulse;
import animatefx.animation.FadeInDown;
import animatefx.animation.Tada;
import client.player.controller.MatchFoundDialogController;
import javafx.scene.layout.Pane;
import javafx.scene.shape.Rectangle;
import java.util.Random;
import client.player.helper.ConfettiHelper;

public class GameViewController implements GameModel.MatchListener {
    // Magic string constants
    private static final String WIN = "WIN";
    private static final String LOSE = "LOSE";
    private static final String ONGOING = "ONGOING";
    private static final String WAITING_FOR_MATCH = "WAITING_FOR_MATCH";

    private String username;
    private GameService gameService;
    @FXML
    private ImageView hangmanImage;
    @FXML
    private Label wordDisplay;
    @FXML
    private TextArea gameOutput;
    @FXML
    private Button backButton;
    @FXML
    private Label timerLabel;
    @FXML
    private Label timeLabel;
    // New UI elements
    @FXML
    private Label roundLabel;
    @FXML
    private Label scoreLabel;
    @FXML
    private javafx.scene.text.Text statusText;
    @FXML
    private ImageView exitGameButton;
    private GameModel model;
    private Stage stage;
    private Runnable onBackToMenu;
    private GameStatePoller gameStatePoller;
    private GameTimerHelper gameTimerHelper;
    @FXML
    private GridPane keyboardGrid;
    @FXML
    private Button keyQ, keyW, keyE, keyR, keyT, keyY, keyU, keyI, keyO, keyP;
    @FXML
    private Button keyA, keyS, keyD, keyF, keyG, keyH, keyJ, keyK, keyL;
    @FXML
    private Button keyZ, keyX, keyC, keyV, keyB, keyN, keyM;

    private KeyboardHelper keyboardHelper;
    private boolean gameOverDialogShown = false;
    private boolean timeUpHandled = false;
    private int lastRoundWinnerShown = -1;
    @FXML
    private StackPane root;
    private int lastPlayerWins = 0; // Track previous playerWins for confetti trigger
    private boolean nextRoundStarted = false;

    public void setStage(Stage stage) {
        this.stage = stage;
    }

    public void setOnBackToMenu(Runnable onBackToMenu) {
        this.onBackToMenu = onBackToMenu;
    }

    @FXML
    public void initialize() {
        loadHangmanImages();
        updateHangmanImage(0);

        // Set exit button image
        if (exitGameButton != null) {
            try {
                Image exitImage = new Image(getClass().getResourceAsStream("/leave.png"));
                exitGameButton.setImage(exitImage);
            } catch (Exception e) {
                System.err.println("Could not load leave.png for exit button: " + e.getMessage());
            }
        }

        if (roundLabel != null) roundLabel.setText("Best of: 3/3");
        if (scoreLabel != null) scoreLabel.setText("Words Guessed: 0");

        keyboardHelper = new KeyboardHelper(keyboardGrid, this::handleKeyPress);
        gameStatePoller = new GameStatePoller(this::updateUI, 1); // poll every 2 seconds
    }

    public void setModel(GameModel model) {
        this.model = model;
        model.setMatchListener(this);
        this.gameService = model.getGameService();

        // FIX: Always set username from model or session
        this.username = model.getUsername();

        Platform.runLater(() -> {
            try {
                Thread.sleep(500);
                if (gameStatePoller != null) {
                    gameStatePoller.start();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
    }

    private void loadHangmanImages() {
        // Call the parameterized version with a default value (usually 0 for initial state)
        loadHangmanImages(0);
    }

    private void loadHangmanImages(int incorrectGuesses) {
        try {
            // Ensure incorrectGuesses is within valid range (0-5)
            int imageIndex = Math.min(Math.max(incorrectGuesses, 0), 5);

            // Construct the image path
            String imagePath = "/hangman/hangman" + imageIndex + ".png";

            // Load the image
            Image hangmanImg = new Image(getClass().getResourceAsStream(imagePath));

            // Update the ImageView
            hangmanImage.setImage(hangmanImg);

            // Make sure the image is visible
            hangmanImage.setVisible(true);
        } catch (Exception e) {
            System.err.println("Error loading hangman image: " + e.getMessage());
            // Fallback - if image loading fails, don't crash the game
        }
    }

    private void animateCorrectGuess() {
        wordDisplay.setText(model.getGameState().maskedWord);
        GameViewHelper.animateWordDisplay(wordDisplay);
    }

    public void startNewGame() {
        if (gameStatePoller != null) gameStatePoller.stop();
        gameOverDialogShown = false;
        timeUpHandled = false;
        lastRoundWinnerShown = -1;
        nextRoundStarted = false;
        resetUI();
        resetKeyboard();
        gameOutput.clear();

        try {
            model.startNewGame();
            GameStateDTO state = model.getGameState();
            if (state.maskedWord == null) {
                gameOutput.appendText("Error: Could not get masked word from server\n");
                return;
            }
            if (WAITING_FOR_MATCH.equals(state.maskedWord)) {
                wordDisplay.setText("Waiting for another player...");
                keyboardGrid.setVisible(false);
                timeLabel.setText("Waiting time: " + model.getGameService().getWaitingTime() + "s");
            } else {
                onMatchFound(state.maskedWord);
            }
        } catch (Exception e) {
            System.err.println("Error starting new game: " + e.getMessage());
            gameOutput.appendText("Error starting game. Please try again.\n");
            e.printStackTrace();
        }
    }

    public void resumeGame() {
        resetUI();
        timeUpHandled = false;
        nextRoundStarted = false;
        GameStateDTO state = model.getGameState();
        wordDisplay.setText(state.maskedWord);
        updateHangmanImage(state.incorrectGuesses);
        keyboardGrid.setVisible(true);
        stopTimerIfRunning();
        gameTimerHelper = new GameTimerHelper(timerLabel, this::handleTimeUp);
        gameTimerHelper.startRoundTimer(gameService.getRoundTime(), state.remainingTime);
    }

    @FXML
    private void handleKeyPress(ActionEvent event) {
        GameStateDTO state = model.getGameState();
        if (model == null || state.gameOver || state.roundOver) {
            return;
        }
        Button clickedButton = (Button) event.getSource();
        String letter = clickedButton.getText().toLowerCase();
        try {
            int clientRemainingTime = (gameTimerHelper != null) ? gameTimerHelper.getRemainingTime() : 0;
            boolean correct = model.makeGuess(letter.charAt(0), clientRemainingTime);
            new Pulse(clickedButton).play();
            if (correct) {
                clickedButton.getStyleClass().add("correct");
                animateCorrectGuess();
            } else {
                clickedButton.getStyleClass().add("incorrect");
            }
            clickedButton.setDisable(true);
            GameStateDTO newState = model.getGameState();
            updateHangmanImage(newState.incorrectGuesses);
            updateUI();
            // If the round is over after this guess, call finishRound if not already called
            if (newState.roundOver && !timeUpHandled) {
                boolean guessedWord = !newState.maskedWord.contains("_");
                model.finishRound(clientRemainingTime, guessedWord);
                timeUpHandled = true;
                handleGameOver(newState);
                // Force UI update to show round result immediately
                updateUI();
            }
        } catch (Exception e) {
            System.err.println("Error handling key press: " + e.getMessage());
            e.printStackTrace();
        }
    }

    @Override
    public void onMatchFound(String maskedWord) {
        try {
            showGameUI();
            if (maskedWord != null) {
                wordDisplay.setText(maskedWord);
                updateHangmanImage(0);
                stopTimerIfRunning();
                GameStateDTO state = model.getGameState();
                String opponent = getOpponentUsername();
                if (opponent == null || opponent.isEmpty()) opponent = "Opponent";
                MatchFoundDialogController.showDialog(stage, username, opponent, () -> {
                    stopTimerIfRunning();
                    gameTimerHelper = new GameTimerHelper(timerLabel, this::handleTimeUp);
                    gameTimerHelper.startRoundTimer(gameService.getRoundTime(), state.remainingTime);
                    GameViewHelper.animateWordDisplay(wordDisplay);
                });
            }
        } catch (Exception e) {
            System.err.println("Error in onMatchFound: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private void showGameUI() {
        wordDisplay.setVisible(true);
        timerLabel.setVisible(true);
        roundLabel.setVisible(true);
        scoreLabel.setVisible(true);
        gameOutput.setVisible(true);
        keyboardGrid.setVisible(true);
    }

    @Override
    public void onMatchTimeout() {
        try {
            gameOutput.appendText("\nNo match found. Please try again.\n");
            keyboardGrid.setVisible(false);
            // Show a styled pop-up dialog to inform the user
            javafx.application.Platform.runLater(() -> {
                Alert alert = new Alert(Alert.AlertType.INFORMATION);
                alert.setTitle("No Match Found");
                alert.setHeaderText(null);
                alert.setContentText("No opponent was found. Please try again later.");
                alert.initOwner(stage);
                // Custom style: larger font and info icon
                DialogPane dialogPane = alert.getDialogPane();
                dialogPane.setStyle("-fx-font-size: 18px; -fx-font-family: 'Minecraftia', 'Arial Black', sans-serif; -fx-background-color: #222; -fx-text-fill: #ff5555;");
                // Optionally set a custom graphic (icon)
                ImageView icon = new ImageView(new Image(getClass().getResourceAsStream("/client/player/view/player1.png")));
                icon.setFitWidth(48);
                icon.setFitHeight(48);
                alert.setGraphic(icon);
                alert.showAndWait();
            });
        } catch (Exception e) {
            System.err.println("Error in onMatchTimeout: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private String getOpponentUsername() {
        try {
            if (gameService != null && username != null) {
                GameStateDTO state = model.getGameState();
                if (state.roundWinner != null && !state.roundWinner.isEmpty() && !state.roundWinner.equals(username)) {
                    return state.roundWinner;
                }
                if (LOSE.equals(state.sessionResult) && state.roundWinner != null) {
                    return state.roundWinner;
                }
            }
        } catch (Exception e) {
            // Fallback
        }
        return "Opponent";
    }

    private void resetKeyboard() {
        keyboardHelper.resetKeyboard();
    }

    private void handleGameOver(GameStateDTO state) {
        keyboardGrid.setVisible(false);
        if (state.sessionResult != null && (WIN.equals(state.sessionResult) || LOSE.equals(state.sessionResult))) {
            String result = state.sessionResult;
            gameOutput.appendText("\nGame Over! " + result + "\n");
            gameOutput.setScrollTop(Double.MAX_VALUE);
        }
    }

    private void updateHangmanImage(int incorrectGuesses) {
        String imagePath = "/hangman/hangman" + incorrectGuesses + ".png";
        Image image = new Image(getClass().getResourceAsStream(imagePath));
        hangmanImage.setImage(image);
    }

    private void resetUI() {
        keyboardGrid.setVisible(false);
        gameOutput.clear();
        hangmanImage.setImage(null);
        resetKeyboard();
        timerLabel.setText("");
    }

    private void handleTimeUp() {
        if (timeUpHandled) return;
        timeUpHandled = true;
        gameOutput.appendText("Time's up! You didn't guess the word in time.\n");
        if (model != null) {
            model.finishRound(0, false);
            updateUI();
        }
    }

    private void handleGameOverDialog(GameStateDTO state) {
        if (!gameOverDialogShown) {
            gameOverDialogShown = true;
            if (gameStatePoller != null) gameStatePoller.stop();
            // Hide all main game UI elements
            if (wordDisplay != null) wordDisplay.setVisible(false);
            if (keyboardGrid != null) keyboardGrid.setVisible(false);
            if (hangmanImage != null) hangmanImage.setVisible(false);
            if (timerLabel != null) timerLabel.setVisible(false);
            if (roundLabel != null) roundLabel.setVisible(false);
            if (scoreLabel != null) scoreLabel.setVisible(false);
            if (backButton != null) backButton.setVisible(false);
            if (statusText != null) statusText.setVisible(false);
            Platform.runLater(() -> {
                Runnable cleanupAndBack = () -> {
                    if (gameService != null && username != null) {
                        try { gameService.cleanupPlayerSession(username); } catch (Exception e) { System.err.println("Error cleaning up player session: " + e.getMessage()); }
                    }
                    handleBackToMenu();
                };
                if (WIN.equals(state.sessionResult)) {
                    GameViewHelper.showWinCelebration(stage, state.maskedWord, "You won the game!", cleanupAndBack);
                } else if (LOSE.equals(state.sessionResult)) {
                    GameViewHelper.showGameOverDialog(stage, "You lost.", false, cleanupAndBack);
                }
            });
        }
    }

    private void stopTimerIfRunning() {
        if (gameTimerHelper != null) {
            gameTimerHelper.stopRoundTimer();
            gameTimerHelper = null;
        }
    }

    public void onReturned() {
        updateUI();
        GameStateDTO state = model.getGameState();
        if (!state.gameOver && state.maskedWord != null && !state.maskedWord.isEmpty() && !WAITING_FOR_MATCH.equals(state.maskedWord)) {
            keyboardGrid.setVisible(true);
            stopTimerIfRunning();
            gameTimerHelper = new GameTimerHelper(timerLabel, this::handleTimeUp);
            gameTimerHelper.startRoundTimer(gameService.getRoundTime(), state.remainingTime);
            timerLabel.setText("");
        }
    }

    public void handleBackToMenu() {
        if (gameTimerHelper != null) {
            gameTimerHelper.stopRoundTimer();
            gameTimerHelper = null;
        }
        if (gameStatePoller != null) gameStatePoller.stop();
        gameOverDialogShown = false;
        timeUpHandled = false;
        lastRoundWinnerShown = -1;
        nextRoundStarted = false;
        // Do NOT clean up session state here; allow game to continue in background
        resetUI();
        if (onBackToMenu != null) {
            onBackToMenu.run();
        }
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public void setGameService(GameService gameService) {
        this.gameService = gameService;
    }

    private void updateUI() {
        GameStateDTO state = model.getGameState();
        if (isWaitingForMatch(state)) {
            handleWaitingForMatchUI();
            return;
        }
        if (shouldHandleTimeUp(state)) {
            handleTimeUp();
        }
        if (shouldShowGameOverDialog(state)) {
            if (root != null) root.setOpacity(1.0);
            handleGameOverDialog(state);
            keyboardGrid.setVisible(false);
            return;
        }
        if (state.roundOver && !state.gameOver) {
            stopTimerIfRunning();
        }
        updateScoreLabel(state);
        triggerConfettiIfNeeded(state);
        showRoundWinnerIfNeeded(state);
        autoStartNextRoundIfNeeded(state);
    }

    private boolean isWaitingForMatch(GameStateDTO state) {
        return state.maskedWord == null || WAITING_FOR_MATCH.equals(state.maskedWord);
    }

    private void handleWaitingForMatchUI() {
        keyboardGrid.setVisible(false);
        timerLabel.setText("");
        stopTimerIfRunning();
    }

    private boolean shouldHandleTimeUp(GameStateDTO state) {
        return state.remainingTime <= 0 && !timeUpHandled && !state.roundOver && !state.gameOver;
    }

    private boolean shouldShowGameOverDialog(GameStateDTO state) {
        return state.sessionResult != null && (WIN.equals(state.sessionResult) || LOSE.equals(state.sessionResult));
    }

    private void updateScoreLabel(GameStateDTO state) {
        scoreLabel.setText("Words Guessed: " + state.playerWins);
    }

    private void triggerConfettiIfNeeded(GameStateDTO state) {
        if (!state.gameOver && state.playerWins > lastPlayerWins) {
            ConfettiHelper.showConfetti(root);
        }
        lastPlayerWins = state.playerWins;
    }

    private void showRoundWinnerIfNeeded(GameStateDTO state) {
        if (state.roundOver && !state.gameOver && state.roundWinner != null && !state.roundWinner.isEmpty()) {
            int roundNum = state.currentRound;
            if (lastRoundWinnerShown != roundNum) {
                String opponent = state.roundWinner.equals(username) ? "your opponent" : state.roundWinner;
                boolean playerWon = state.roundWinner.equals(username);
                GameViewHelper.showRoundWinner(gameOutput, roundNum, opponent, playerWon);
                gameOutput.setScrollTop(Double.MAX_VALUE);
                lastRoundWinnerShown = roundNum;
            }
        } else if (state.roundOver && !state.gameOver && (state.roundWinner == null || state.roundWinner.isEmpty())) {
            GameViewHelper.showNoRoundWinner(gameOutput);
            gameOutput.setScrollTop(Double.MAX_VALUE);
        }
    }

    private void autoStartNextRoundIfNeeded(GameStateDTO state) {
        // Only auto-start next round if session is still ONGOING
        if (state.roundOver && !state.gameOver && ONGOING.equals(state.sessionResult) && !nextRoundStarted) {
            nextRoundStarted = true;
            stopTimerIfRunning();
            // Explode round UI elements instead of fading out root
            Runnable afterExplosion = () -> {
                GameStateDTO latestState = model.getGameState();
                if (!ONGOING.equals(latestState.sessionResult)) {
                    // If game is over, restore UI and show dialog immediately
                    wordDisplay.setVisible(true);
                    keyboardGrid.setVisible(true);
                    hangmanImage.setVisible(true);
                    handleGameOverDialog(latestState);
                    return;
                }
                boolean started = model.getGameService().startNewRound(model.getUsername());
                if (started) {
                    nextRoundStarted = false;
                    GameStateDTO newState = model.getGameState();
                    wordDisplay.setText(newState.maskedWord);
                    updateHangmanImage(newState.incorrectGuesses);
                    roundLabel.setText("Round: " + (newState.currentRound + 1));
                    scoreLabel.setText("Words Guessed: " + newState.playerWins);
                    timerLabel.setText(String.valueOf(gameService.getRoundTime()));
                    resetKeyboard();
                    wordDisplay.setVisible(true);
                    keyboardGrid.setVisible(true);
                    hangmanImage.setVisible(true);
                    stopTimerIfRunning();
                    gameTimerHelper = new GameTimerHelper(timerLabel, this::handleTimeUp);
                    gameTimerHelper.startRoundTimer(gameService.getRoundTime(), gameService.getRoundTime());
                }
            };
            // Chain explosions: wordDisplay -> keyboardGrid -> hangmanImage -> afterExplosion
            GameViewHelper.explodeNode(wordDisplay, () ->
                GameViewHelper.explodeNode(keyboardGrid, () ->
                    GameViewHelper.explodeNode(hangmanImage, afterExplosion)
                )
            );
        }
    }

    @FXML
    private void handleExitGame() {
        GameViewHelper.showExitGameDialog(stage, () -> {
            // End the game session on the server
            if (gameService != null && username != null) {
                try {
                    gameService.endGameSession(username);
                    gameService.cleanupPlayerSession(username);
                } catch (Exception e) {
                    System.err.println("Error ending or cleaning up game session: " + e.getMessage());
                }
            }
            // Stop timers and polling
            if (gameTimerHelper != null) {
                gameTimerHelper.stopRoundTimer();
                gameTimerHelper = null;
            }
            if (gameStatePoller != null) gameStatePoller.stop();
            // Go to home view/menu
            handleBackToMenu();
        });
    }
}
