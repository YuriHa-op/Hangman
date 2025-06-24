package client.player.controller;

import GameModule.GameService;
import client.player.model.MultiplayerGameModel;
import client.player.model.MultiplayerGameModel.LobbyState;
import client.player.view.GameView;
import client.player.view.LeaderboardView;
import client.player.view.MultiplayerGameView;
import client.player.view.QueueStatusPane;
import javafx.animation.KeyFrame;
import javafx.animation.ScaleTransition;
import javafx.animation.Timeline;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.scene.text.Text;
import javafx.stage.Modality;
import javafx.stage.Stage;
import javafx.util.Duration;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;

import javafx.scene.layout.HBox;
import javafx.scene.Scene;
import LoginModule.LoginService;

public class HomeViewController {
    @FXML private Button startGameButton;
    @FXML private Button viewLeaderboardButton;
    @FXML private Button logoutButton;
    @FXML private Button multiplayerButton;
    @FXML private Button matchHistoryButton;
    @FXML private StackPane queueStatusContainer;
    @FXML private Text splashText;
    @FXML private Label welcomeLabel;
    private Stage stage;

    private GameService gameService;
    private LoginService loginService;
    private String username;
    private Runnable onLogout; // Callback to return to login

    // Multiplayer queue state
    private QueueStatusPane queueStatusPane;
    private MultiplayerGameModel multiplayerModel;
    private Timeline queuePoller;
    private boolean isQueueing = false;
    private boolean matchFoundDialogShown = false;
    private int lastQueueSeconds = -1;

    // Session validation
    private String sessionId;
    private Timer sessionValidationTimer;
    private static final long SESSION_CHECK_INTERVAL = 1000; // Check every 1 second for faster detection
    private static final long KEEPALIVE_INTERVAL = 30000; // Send keepalive every 30 seconds
    private long lastKeepAliveTime = 0;
    
    // Flag to prevent multiple invalid session dialogs
    private boolean invalidSessionDialogShown = false;

    public void setGameService(GameService gameService) {
        this.gameService = gameService;
    }

    public void setLoginService(LoginService loginService) {
        this.loginService = loginService;
    }

    public void setUsername(String username) {
        this.username = username;
        if (welcomeLabel != null) {
            welcomeLabel.setText("Welcome, " + username + "!");
        }
    }

    public void setOnLogout(Runnable onLogout) {
        this.onLogout = onLogout;
    }

    @FXML
    public void initialize() {
        // Set welcome message with username
        if (welcomeLabel != null) {
            welcomeLabel.setText("Welcome, " + username + "!");
        }
        
        // Start session validation
        startSessionValidation();
    }

    private void registerSessionCallback() {
        try {
            // Check if we can register a session callback - using reflection
            java.lang.reflect.Method registerMethod = gameService.getClass().getMethod(
                "registerSessionCallback", String.class, java.util.function.Consumer.class);
            
            if (registerMethod != null) {
                // Create a consumer that will handle session invalidation
                java.util.function.Consumer<String> callback = this::handleInvalidSession;
                
                // Register the callback
                registerMethod.invoke(gameService, username, callback);
                System.out.println("Registered session callback for: " + username);
            }
        } catch (Exception e) {
            // Session callback not available, we'll rely on polling
            System.out.println("Could not register session callback, will rely on polling");
        }
    }
    
    public void startSessionValidation() {
        // Reset invalid session flag
        invalidSessionDialogShown = false;
        
        // Try to get the session ID
        try {
            // First try to get from LoginModel
            if (this.sessionId == null || this.sessionId.isEmpty()) {
                this.sessionId = getSessionIdFromLoginModel();
            }
            
            if (sessionId != null && !sessionId.isEmpty()) {
                System.out.println("Got session ID for validation: " + sessionId);
            } else {
                System.out.println("No session ID available, will use server-side validation only");
            }
        } catch (Exception e) {
            // Session ID not available, we'll rely on server-side validation only
            System.out.println("Could not get session ID for validation, will use server-only checks");
        }
        
        // Make sure any previous timer is cancelled
        if (sessionValidationTimer != null) {
            sessionValidationTimer.cancel();
            sessionValidationTimer = null;
        }
        
        // Start validation timer
        sessionValidationTimer = new Timer(true); // Daemon timer
        sessionValidationTimer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                validateSession();
            }
        }, SESSION_CHECK_INTERVAL, SESSION_CHECK_INTERVAL);
        
        // Set initial keepalive time
        lastKeepAliveTime = System.currentTimeMillis();
        
        // Register callback if available
        registerSessionCallback();
    }
    
    private String getSessionIdFromLoginModel() {
        try {
            // Try to get the LoginModel class and retrieve the session ID
            Class<?> loginModelClass = Class.forName("client.player.model.LoginModel");
            Object loginModel = null;
            
            // Try to get the instance
            try {
                java.lang.reflect.Method getInstance = loginModelClass.getMethod("getInstance");
                loginModel = getInstance.invoke(null);
            } catch (Exception e) {
                // No getInstance method, might not be a singleton
            }
            
            if (loginModel != null) {
                // Try to get session ID from instance
                java.lang.reflect.Method getSessionId = loginModelClass.getMethod("getSessionId");
                String sessionId = (String) getSessionId.invoke(loginModel);
                return sessionId;
            }
        } catch (Exception e) {
            // Ignore errors
        }
        return null;
    }
    
    private void validateSession() {
        if (username == null || username.isEmpty()) {
            return;
        }
        // Get session ID lazily if not yet cached
        if (sessionId == null || sessionId.isEmpty()) {
            sessionId = getSessionIdFromLoginModel();
        }

        try {
            // 1. Prefer validateSession with our current sessionId for fastest detection
            if (sessionId != null && !sessionId.isEmpty()) {
                try {
                    LoginModule.Bool isValid = loginService.validateSession(username, sessionId);
                    if (isValid == LoginModule.Bool.BOOL_FALSE) {
                        handleInvalidSession("Your session was invalidated.");
                        return;
                    }
                } catch (org.omg.CORBA.BAD_OPERATION e) {
                    // Method not available on server – fall back below
                }
            }

            // 2. Fallback – call checkSessionValid (works but less strict)
            try {
                LoginModule.Bool isValid = loginService.checkSessionValid(username);
                if (isValid == LoginModule.Bool.BOOL_FALSE) {
                    handleInvalidSession("Your session was invalidated.");
                    return;
                }
            } catch (org.omg.CORBA.BAD_OPERATION e) {
                // Neither validateSession nor checkSessionValid are available – continue to last-resort test
            }

            // 3. Last resort – simple call that will throw if session gone
            try {
                gameService.getPlayerWins(username);
            } catch (Exception ex) {
                handleInvalidSession("Session error: Unable to verify session – " + ex.getMessage());
                return;
            }

        } catch (Exception e) {
            handleInvalidSession("Session error: " + e.getMessage());
        }

        // Optional keep-alive every 30s so server knows we are active
        long now = System.currentTimeMillis();
        if ((now - lastKeepAliveTime) > KEEPALIVE_INTERVAL && sessionId != null && !sessionId.isEmpty()) {
            try {
                LoginModule.Bool keepAliveResult = loginService.keepAlive(username, sessionId);
                if (keepAliveResult == LoginModule.Bool.BOOL_FALSE) {
                    handleInvalidSession("Session keep-alive failed.");
                    return;
                }
                lastKeepAliveTime = now;
            } catch (org.omg.CORBA.BAD_OPERATION e) {
                // keepAlive not on server – ignore
            } catch (Exception ex) {
                handleInvalidSession("Session error: " + ex.getMessage());
            }
        }
    }
    
    private void handleInvalidSession(String message) {
        // Don't show multiple dialogs for the same session invalidation
        if (invalidSessionDialogShown) {
            return;
        }
        
        Platform.runLater(() -> {
            System.out.println("Session invalidated: " + message);
            
            // Set flag to prevent multiple dialogs
            invalidSessionDialogShown = true;
            
            // Stop validation timer to prevent multiple alerts
            if (sessionValidationTimer != null) {
                sessionValidationTimer.cancel();
                sessionValidationTimer = null;
            }
            
            // Create a custom styled dialog instead of using standard Alert
            createMinecraftStyledInvalidSessionDialog(message);
            
            // Clean logout without sending to server (as our session is already gone)
            cleanLogout();
        });
    }

    /**
     * Creates a custom styled dialog that matches the Minecraft theme of the game
     */
    private void createMinecraftStyledInvalidSessionDialog(String message) {
        Stage dialogStage = new Stage();
        dialogStage.initModality(javafx.stage.Modality.APPLICATION_MODAL);
        dialogStage.setTitle("Session Ended");
        dialogStage.initStyle(javafx.stage.StageStyle.UNDECORATED);
        dialogStage.setResizable(false);
        
        // Create root container with border
        VBox root = new VBox(15); // 15px spacing
        root.setPadding(new javafx.geometry.Insets(20));
        root.setAlignment(javafx.geometry.Pos.CENTER);
        root.setStyle("-fx-background-color: #c6c6c6; " + 
                     "-fx-border-color: #555555; " +
                     "-fx-border-width: 4px; " +
                     "-fx-effect: dropshadow(three-pass-box, rgba(0,0,0,0.6), 10, 0, 0, 0);");
        
        // Dialog header with icon
        HBox headerBox = new HBox(10);
        headerBox.setAlignment(javafx.geometry.Pos.CENTER);
        
        // Warning icon (using Unicode character for warning)
        Text warningIcon = new Text("⚠");
        warningIcon.setStyle("-fx-font-size: 32px; -fx-fill: #d32f2f;");
        
        // Title text
        Label titleLabel = new Label("Session Ended");
        titleLabel.setStyle("-fx-font-size: 24px; " +
                           "-fx-font-weight: bold; " +
                           "-fx-font-family: 'Minecraft', sans-serif; " +
                           "-fx-text-fill: #d32f2f;");
        
        headerBox.getChildren().addAll(warningIcon, titleLabel);
        
        // Message text
        Label messageLabel = new Label("You've been logged out.\n" + message + "\nPlease login again.");
        messageLabel.setStyle("-fx-font-size: 16px; " +
                             "-fx-font-family: 'Minecraft', sans-serif; " +
                             "-fx-text-alignment: center;");
        messageLabel.setWrapText(true);
        messageLabel.setAlignment(javafx.geometry.Pos.CENTER);
        
        // OK button styled like Minecraft
        Button okButton = new Button("OK");
        okButton.setPrefWidth(100);
        okButton.setPrefHeight(30);
        okButton.setStyle("-fx-font-size: 14px; " +
                         "-fx-font-family: 'Minecraft', sans-serif; " +
                         "-fx-background-color: #5c5c5c, linear-gradient(#9e9e9e, #707070); " +
                         "-fx-background-radius: 0; " +
                         "-fx-border-color: #2d2d2d; " +
                         "-fx-border-width: 2px; " +
                         "-fx-text-fill: white; " +
                         "-fx-cursor: hand;");
        
        // Button hover effect
        okButton.setOnMouseEntered(e -> 
            okButton.setStyle("-fx-font-size: 14px; " +
                             "-fx-font-family: 'Minecraft', sans-serif; " +
                             "-fx-background-color: #707070, linear-gradient(#9e9e9e, #8a8a8a); " +
                             "-fx-background-radius: 0; " +
                             "-fx-border-color: #2d2d2d; " +
                             "-fx-border-width: 2px; " +
                             "-fx-text-fill: white; " +
                             "-fx-cursor: hand;"));
        
        okButton.setOnMouseExited(e -> 
            okButton.setStyle("-fx-font-size: 14px; " +
                             "-fx-font-family: 'Minecraft', sans-serif; " +
                             "-fx-background-color: #5c5c5c, linear-gradient(#9e9e9e, #707070); " +
                             "-fx-background-radius: 0; " +
                             "-fx-border-color: #2d2d2d; " +
                             "-fx-border-width: 2px; " +
                             "-fx-text-fill: white; " +
                             "-fx-cursor: hand;"));
        
        okButton.setOnAction(e -> dialogStage.close());
        
        // Add shake animation for attention
        javafx.animation.TranslateTransition shakeTransition = 
            new javafx.animation.TranslateTransition(javafx.util.Duration.millis(70), root);
        shakeTransition.setFromX(0);
        shakeTransition.setByX(10);
        shakeTransition.setCycleCount(6);
        shakeTransition.setAutoReverse(true);
        
        // Show the dialog with an entrance animation
        root.setOpacity(0);
        root.getChildren().addAll(headerBox, messageLabel, okButton);
        
        Scene scene = new Scene(root);
        dialogStage.setScene(scene);
        dialogStage.setWidth(400);
        dialogStage.setHeight(250);
        
        // Center on screen
        dialogStage.setOnShown(e -> {
            dialogStage.setX((javafx.stage.Screen.getPrimary().getVisualBounds().getWidth() - dialogStage.getWidth()) / 2);
            dialogStage.setY((javafx.stage.Screen.getPrimary().getVisualBounds().getHeight() - dialogStage.getHeight()) / 2);
            
            // Fade in animation
            javafx.animation.FadeTransition fadeIn = 
                new javafx.animation.FadeTransition(javafx.util.Duration.millis(200), root);
            fadeIn.setFromValue(0);
            fadeIn.setToValue(1);
            fadeIn.setOnFinished(event -> shakeTransition.play());
            fadeIn.play();
        });
        
        // Show dialog and wait
        dialogStage.showAndWait();
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
        queueStatusPane.getCancelButton().setOnAction(e -> cancelQueue(true));
    }

    private void cancelQueue(boolean notifyServer) {
        isQueueing = false;
        if (queuePoller != null) queuePoller.stop();
        queueStatusContainer.getChildren().clear();
        setMenuButtonsDisabled(false);

        if (notifyServer && multiplayerModel != null && username != null) {
            try {
                multiplayerModel.getGameService().cleanupPlayerSession(username);
            } catch (Exception ex) {
                System.err.println("Error trying to leave lobby: " + ex.getMessage());
            }
        }
        multiplayerModel = null;
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
                    cancelQueue(false); // Clean up queue state
                }
            }
            // If lobby is gone or NOMATCH, and we haven't already handled it
            if ("NOMATCH".equals(state.getState()) && !matchFoundDialogShown) {
                 matchFoundDialogShown = true; // Prevent repeated dialogs
                 if (queuePoller != null) queuePoller.stop();
                 showNoMatchFoundDialog();
                 cancelQueue(false); // Clean up queue state
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
                cancelQueue(false); // Only clean UI; keep lobby intact for active game
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
            cancelQueue(true); // Ensure queue is cancelled if logging out while queueing
        }
        logout();
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

    private void logout() {
        // Cancel session validation timer
        if (sessionValidationTimer != null) {
            sessionValidationTimer.cancel();
            sessionValidationTimer = null;
        }
        
        try {
            loginService.logout(username);
        } catch (Exception e) {
            System.err.println("Error during logout: " + e.getMessage());
        }
        
        cleanLogout();
    }

    private void cleanLogout() {
        invalidSessionDialogShown = true;

        // Cancel validator timer
        if (sessionValidationTimer != null) {
            sessionValidationTimer.cancel();
            sessionValidationTimer = null;
        }

        // Close *all* visible stages except the hidden login window (which isn't showing)
        try {
            // JavaFX 8u40+ provides Window.getWindows()
            java.lang.reflect.Method getWindows = javafx.stage.Window.class.getMethod("getWindows");
            @SuppressWarnings("unchecked")
            java.util.List<javafx.stage.Window> winList = (java.util.List<javafx.stage.Window>) getWindows.invoke(null);
            for (javafx.stage.Window w : winList) {
                if (w instanceof javafx.stage.Stage && w.isShowing()) {
                    try { ((javafx.stage.Stage) w).close(); } catch (Exception ignored) {}
                }
            }
        } catch (Exception apiMissing) {
            // Fallback for older JavaFX: use internal StageHelper (may not be available on all distros)
            try {
                Class<?> helper = Class.forName("com.sun.javafx.stage.StageHelper");
                java.lang.reflect.Method getStages = helper.getDeclaredMethod("getStages");
                @SuppressWarnings("unchecked")
                java.util.List<javafx.stage.Stage> stages = (java.util.List<javafx.stage.Stage>) getStages.invoke(null);
                for (javafx.stage.Stage s : stages) {
                    if (s.isShowing()) {
                        try { s.close(); } catch (Exception ignored) {}
                    }
                }
            } catch (Exception ignored) {
                // If all else fails, just close the current stage
                if (stage != null) {
                    try { stage.close(); } catch (Exception ex) { /* ignore */ }
                }
            }
        }

        // Run the onLogout callback which will reshow login view
        if (onLogout != null) {
            onLogout.run();
        }
    }
}

