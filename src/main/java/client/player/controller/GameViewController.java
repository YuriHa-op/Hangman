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
        // Ensure the wordDisplay text is updated before animating
        wordDisplay.setText(model.getGameState().maskedWord);
        new Bounce(wordDisplay).play();
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
            if ("WAITING_FOR_MATCH".equals(state.maskedWord)) {
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
        if (gameTimerHelper != null) {
            gameTimerHelper.stopRoundTimer();
            gameTimerHelper = null;
        }
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
            wordDisplay.setVisible(true);
            timerLabel.setVisible(true);
            roundLabel.setVisible(true);
            scoreLabel.setVisible(true);
            gameOutput.setVisible(true);
            keyboardGrid.setVisible(true);
            if (maskedWord != null) {
                wordDisplay.setText(maskedWord);
                updateHangmanImage(0);
                if (gameTimerHelper != null) {
                    gameTimerHelper.stopRoundTimer();
                    gameTimerHelper = null;
                }
                GameStateDTO state = model.getGameState();
                // Try to infer opponent's username from the model or state
                String opponent = null;
                if (model != null && model.getUsername() != null) {
                    // Try to get the opponent from the match (if available)
                    // If you have a way to get the matched player's name, use it here
                    // For now, try to infer from GameStateDTO (not directly available)
                    // If not available, fallback to 'Opponent'
                    opponent = getOpponentUsername();
                }
                if (opponent == null || opponent.isEmpty()) opponent = "Opponent";
                MatchFoundDialogController.showDialog(stage, username, opponent, () -> {
                    gameTimerHelper = new GameTimerHelper(timerLabel, this::handleTimeUp);
                    gameTimerHelper.startRoundTimer(gameService.getRoundTime(), state.remainingTime);
                    new FadeInDown(wordDisplay).play();
                });
            }
        } catch (Exception e) {
            System.err.println("Error in onMatchFound: " + e.getMessage());
            e.printStackTrace();
        }
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
                // Use a new method in GameService if available, or infer from GameStateDTO
                GameStateDTO state = model.getGameState();
                // If roundWinner is not this user and not empty, use it as opponent
                if (state.roundWinner != null && !state.roundWinner.isEmpty() && !state.roundWinner.equals(username)) {
                    return state.roundWinner;
                }
                // If sessionResult is LOSE, roundWinner is the opponent
                if ("LOSE".equals(state.sessionResult) && state.roundWinner != null) {
                    return state.roundWinner;
                }
                // If more info is available in GameStateDTO, use it here
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
        // Only show Game Over message if sessionResult is WIN or LOSE
        if (state.sessionResult != null && ("WIN".equals(state.sessionResult) || "LOSE".equals(state.sessionResult))) {
            String result = state.sessionResult;
            gameOutput.appendText("\nGame Over! " + result + "\n");
        }
        // pollGameSessionResult() call removed as it is no longer needed
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
        resetKeyboard();  // Reset keyboard state
    }

    private void handleTimeUp() {
        if (timeUpHandled) return;
        timeUpHandled = true;
        gameOutput.appendText("Time's up! You didn't guess the word in time.\n");
        // Notify server that player finished with 0 time left and did not guess the word
        if (model != null) {
            model.finishRound(0, false);
            // Force UI update to show round result immediately
            updateUI();
        }
    }

    public void onReturned() {
        updateUI();
        GameStateDTO state = model.getGameState();
        if (!state.gameOver && state.maskedWord != null && !state.maskedWord.isEmpty() && !state.maskedWord.equals("WAITING_FOR_MATCH")) {
            keyboardGrid.setVisible(true);
            if (gameTimerHelper != null) {
                gameTimerHelper.stopRoundTimer();
                gameTimerHelper = null;
            }
            gameTimerHelper = new GameTimerHelper(timerLabel, this::handleTimeUp);
            gameTimerHelper.startRoundTimer(gameService.getRoundTime(), state.remainingTime);
        }
    }

    public void handleBackToMenu() {
        // Only reset local state, not server session (unless triggered from dialog)
        if (gameTimerHelper != null) {
            gameTimerHelper.stopRoundTimer();
            gameTimerHelper = null;
        }
        if (gameStatePoller != null) gameStatePoller.stop();
        gameOverDialogShown = false;
        timeUpHandled = false;
        lastRoundWinnerShown = -1;
        nextRoundStarted = false;
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
        // Handle waiting for match
        if (state.maskedWord == null || "WAITING_FOR_MATCH".equals(state.maskedWord)) {
            keyboardGrid.setVisible(false);
            timerLabel.setText("");
            if (gameTimerHelper != null) {
                gameTimerHelper.stopRoundTimer();
                gameTimerHelper = null;
            }
            return;
        }
       
        if (state.remainingTime <= 0 && !timeUpHandled && !state.roundOver && !state.gameOver) {
            handleTimeUp();
        }
        // Only show game over dialog and stop polling if sessionResult is WIN or LOSE
        if (state.sessionResult != null && ("WIN".equals(state.sessionResult) || "LOSE".equals(state.sessionResult))) {
            if (!gameOverDialogShown) {
                gameOverDialogShown = true;
                if (gameStatePoller != null) gameStatePoller.stop();
                if ("WIN".equals(state.sessionResult)) {
                    javafx.application.Platform.runLater(() -> GameViewHelper.showWinCelebration(stage, state.maskedWord, "You won the game!", () -> {
                        // Reset game session on server only after dialog
                        if (gameService != null && username != null) {
                            try { gameService.endGameSession(username); } catch (Exception e) { System.err.println("Error ending game session: " + e.getMessage()); }
                        }
                        handleBackToMenu();
                    }));
                } else if ("LOSE".equals(state.sessionResult)) {
                    javafx.application.Platform.runLater(() -> GameViewHelper.showGameOverDialog(stage, "You lost.", false, () -> {
                        // Reset game session on server only after dialog
                        if (gameService != null && username != null) {
                            try { gameService.endGameSession(username); } catch (Exception e) { System.err.println("Error ending game session: " + e.getMessage()); }
                        }
                        handleBackToMenu();
                    }));
                }
            }
            keyboardGrid.setVisible(false);
            return;
        }
        // Stop timer as soon as the round is over and not game over
        if (state.roundOver && !state.gameOver) {
            if (gameTimerHelper != null) {
                gameTimerHelper.stopRoundTimer();
                gameTimerHelper = null;
            }
        }
        // Always update score label to reflect latest value from server
        scoreLabel.setText("Words Guessed: " + state.playerWins);
        // Confetti animation: trigger if playerWins increased (and not game over)
        if (!state.gameOver && state.playerWins > lastPlayerWins) {
            ConfettiHelper.showConfetti(root);
        }
        lastPlayerWins = state.playerWins;
        // Show round winner if round is over, both players finished, and not game over
        if (state.roundOver && !state.gameOver && state.roundWinner != null && !state.roundWinner.isEmpty()) {
            int roundNum = state.currentRound;
            if (lastRoundWinnerShown != roundNum) {
                String opponent = null;
                if (state.roundWinner.equals(username)) {
                    opponent = "your opponent";
                } else {
                    opponent = state.roundWinner;
                }
                if (state.roundWinner.equals(username)) {
                    gameOutput.appendText("\nYou won round " + (roundNum + 1) + " against " + opponent + ".\n");
                    System.out.println("[DEBUG] Showed win message for round " + roundNum);
                } else {
                    gameOutput.appendText("\n" + opponent + " won round " + (roundNum + 1) + " against you.\n");
                    System.out.println("[DEBUG] Showed lose message for round " + roundNum);
                }
                lastRoundWinnerShown = roundNum;
            }
        } else if (state.roundOver && !state.gameOver && state.roundWinner == null) {
            gameOutput.appendText("\nNo one won this round.\n");
        }
        // Automatically start the next round if round is over, game is not over, and session is ongoing
        if (state.roundOver && !state.gameOver && "ONGOING".equals(state.sessionResult) && !nextRoundStarted) {
            nextRoundStarted = true;
            if (root != null) {
                System.out.println("[DEBUG] Starting next round transition animation");
                FadeOut fadeOut = new FadeOut(root);
                fadeOut.setOnFinished(e -> {
                    boolean started = model.getGameService().startNewRound(model.getUsername());
                    if (started) {
                        nextRoundStarted = false; // Allow next round transition for the new round
                        GameStateDTO newState = model.getGameState();
                        wordDisplay.setText(newState.maskedWord);
                        updateHangmanImage(newState.incorrectGuesses);
                        roundLabel.setText("Round: " + (newState.currentRound + 1));
                        scoreLabel.setText("Words Guessed: " + newState.playerWins);
                        timerLabel.setText(String.valueOf(gameService.getRoundTime()));
                        resetKeyboard();
                        keyboardGrid.setVisible(true);
                        if (gameTimerHelper != null) {
                            gameTimerHelper.stopRoundTimer();
                            gameTimerHelper = null;
                        }
                        gameTimerHelper = new GameTimerHelper(timerLabel, this::handleTimeUp);
                        System.out.println("[DEBUG] Starting new round timer");
                        gameTimerHelper.startRoundTimer(gameService.getRoundTime(), gameService.getRoundTime());
                        new FadeIn(root).play();
                    }
                });
                fadeOut.play();
            }
        }
    }
}
