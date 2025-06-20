package server.controller;

import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.ScrollPane;
import javafx.scene.control.TextArea;
import javafx.scene.paint.Color;
import javafx.scene.text.Text;
import javafx.scene.text.TextFlow;
import server.handler.service.GameServiceImpl;
import server.handler.service.AdminServiceImpl;
import server.ServerMain;

import java.time.Duration;
import java.time.Instant;
import java.util.Timer;
import java.util.TimerTask;

public class ServerMainController {
    @FXML private Text serverStatusText;
    @FXML private Button startButton;
    @FXML private Button pauseButton;
    @FXML private Button stopButton;
    @FXML private Button restartButton;
    @FXML private Text activePlayersText;
    @FXML private Text activeGamesText;
    @FXML private Text uptimeText;
    @FXML private Text memoryUsageText;
    @FXML private ScrollPane scrollPane;
    @FXML private TextFlow serverLogsArea;
    @FXML private Button clearLogsButton;

    private ServerMain serverMain;
    private GameServiceImpl gameService;
    private AdminServiceImpl adminService;
    private Timer statsTimer;
    private Instant serverStartTime;
    private Instant pauseStartTime;
    private Duration totalUptime = Duration.ZERO;
    private boolean isPaused = false;
    private boolean isRunning = false;

    // Log level colors
    private static final String INFO_COLOR = "log-info";
    private static final String WARN_COLOR = "log-warn";
    private static final String ERROR_COLOR = "log-error";
    private static final String SUCCESS_COLOR = "log-success";
    private static final String DEBUG_COLOR = "log-debug";
    private static final String TIMESTAMP_COLOR = "log-timestamp";

    public void setServerMain(ServerMain serverMain) {
        this.serverMain = serverMain;
        this.gameService = null; // Will be set after server is started
        this.adminService = null; // Will be set after server is started
    }

    public void initialize() {
        // Ensure scroll pane properly sizes TextFlow width
        serverLogsArea.prefWidthProperty().bind(scrollPane.widthProperty().subtract(20));
        
        // Set up periodic stats update
        statsTimer = new Timer(true);
        statsTimer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                updateStats();
            }
        }, 0, 1000); // Update every second
    }

    @FXML
    private void handleStartServer() {
        if (isPaused) {
            // Resume server
            try {
                serverMain.resumeServer();
                isPaused = false;
                isRunning = true;
                // Add paused duration to totalUptime
                if (pauseStartTime != null) {
                    Duration pausedDuration = Duration.between(pauseStartTime, Instant.now());
                    serverStartTime = serverStartTime.plus(pausedDuration);
                }
                serverStatusText.setText("Online");
                serverStatusText.setStyle("-fx-fill: #4CAF50;");
                startButton.setDisable(true);
                pauseButton.setDisable(false);
                stopButton.setDisable(false);
                restartButton.setDisable(false);
                logInfo("Server resumed");
            } catch (Exception e) {
                logError("Error resuming server: " + e.getMessage());
            }
        } else {
            // Start new server
            try {
                serverMain.startServer();
                this.gameService = serverMain.getGameService(); // Set after server is started
                this.adminService = serverMain.getAdminService(); // Set after server is started
                serverStartTime = Instant.now();
                totalUptime = Duration.ZERO;
                isRunning = true;
                isPaused = false;
                serverStatusText.setText("Online");
                serverStatusText.setStyle("-fx-fill: #4CAF50;");
                startButton.setDisable(true);
                pauseButton.setDisable(false);
                stopButton.setDisable(false);
                restartButton.setDisable(false);
                logSuccess("Server started successfully");
                logInfo("GameService and AdminService registered and ready to accept connections");
            } catch (Exception e) {
                logError("Error starting server: " + e.getMessage());
            }
        }
    }

    @FXML
    private void handlePauseServer() {
        try {
            serverMain.pauseServer();
            isPaused = true;
            isRunning = false;
            pauseStartTime = Instant.now();
            // Add time since last start to totalUptime
            if (serverStartTime != null) {
                totalUptime = totalUptime.plus(Duration.between(serverStartTime, pauseStartTime));
            }
            serverStatusText.setText("Paused");
            serverStatusText.setStyle("-fx-fill: #FFC107;");
            startButton.setDisable(false);
            pauseButton.setDisable(true);
            stopButton.setDisable(false);
            restartButton.setDisable(false);
            logWarn("Server paused - new connections will be rejected");
        } catch (Exception e) {
            logError("Error pausing server: " + e.getMessage());
        }
    }

    @FXML
    private void handleStopServer() {
        try {
            serverMain.stopServer();
            isRunning = false;
            isPaused = false;
            // Add time since last start to totalUptime
            if (serverStartTime != null) {
                totalUptime = totalUptime.plus(Duration.between(serverStartTime, Instant.now()));
            }
            serverStartTime = null;
            pauseStartTime = null;
            totalUptime = Duration.ZERO;
            uptimeText.setText("00:00:00");
            serverStatusText.setText("Offline");
            serverStatusText.setStyle("-fx-fill: #ff4444;");
            startButton.setDisable(false);
            pauseButton.setDisable(true);
            stopButton.setDisable(true);
            restartButton.setDisable(true);
            
            // Reset stats
            activePlayersText.setText("0");
            activeGamesText.setText("0");
            
            logInfo("Server stopped");
        } catch (Exception e) {
            logError("Error stopping server: " + e.getMessage());
        }
    }
    
    @FXML
    private void handleRestartServer() {
        try {
            logInfo("Restarting server...");
            
            // First stop the server
            serverMain.stopServer();
            
            // Reset uptime and timing variables - important change here
            serverStartTime = null;
            pauseStartTime = null;
            totalUptime = Duration.ZERO;
            
            // Wait a bit for resources to be released
            Thread.sleep(2000);
            
            // Start the server again
            serverMain.startServer();
            this.gameService = serverMain.getGameService();
            this.adminService = serverMain.getAdminService();
            
            // Reset server time
            serverStartTime = Instant.now();
            isPaused = false;
            isRunning = true;
            
            // Update UI
            serverStatusText.setText("Online");
            serverStatusText.setStyle("-fx-fill: #4CAF50;");
            startButton.setDisable(true);
            pauseButton.setDisable(false);
            stopButton.setDisable(false);
            restartButton.setDisable(false);
            
            logSuccess("Server restarted successfully");
        } catch (Exception e) {
            logError("Error restarting server: " + e.getMessage());
            
            // Reset UI to offline state in case of failure
            serverStatusText.setText("Offline");
            serverStatusText.setStyle("-fx-fill: #ff4444;");
            startButton.setDisable(false);
            pauseButton.setDisable(true);
            stopButton.setDisable(true);
            restartButton.setDisable(true);
        }
    }

    @FXML
    private void handleClearLogs() {
        serverLogsArea.getChildren().clear();
    }

    private void updateStats() {
        Platform.runLater(() -> {
            try {
                // Always update memory usage regardless of server state
                long usedMemory = (Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory()) / (1024 * 1024);
                memoryUsageText.setText(usedMemory + " MB");
                
                // Only update player and game stats when server is running and not paused
                if (isRunning && !isPaused) {
                    if (gameService != null) {
                        // Get active player count from both single & multi mode
                        int activePlayers = gameService.getActivePlayers();
                        activePlayersText.setText(String.valueOf(activePlayers));

                        // Get active games from both single & multi mode
                        int activeGames = gameService.getActiveGames();
                        activeGamesText.setText(String.valueOf(activeGames));
                    }

                    // Update uptime
                    Duration uptime = totalUptime;
                    if (serverStartTime != null) {
                        uptime = uptime.plus(Duration.between(serverStartTime, Instant.now()));
                    }
                    uptimeText.setText(String.format("%02d:%02d:%02d",
                            uptime.toHours(),
                            uptime.toMinutes() % 60,
                            uptime.getSeconds() % 60));
                }
            } catch (Exception e) {
                logError("Error updating stats: " + e.getMessage());
            }
        });
    }

    // Enhanced logging methods with different levels
    public void logMessage(String message) {
        logInfo(message);
    }

    public void logInfo(String message) {
        logWithLevel(message, "INFO", INFO_COLOR);
    }

    public void logWarn(String message) {
        logWithLevel(message, "WARN", WARN_COLOR);
    }

    public void logError(String message) {
        logWithLevel(message, "ERROR", ERROR_COLOR);
    }

    public void logSuccess(String message) {
        logWithLevel(message, "SUCCESS", SUCCESS_COLOR);
    }

    public void logDebug(String message) {
        logWithLevel(message, "DEBUG", DEBUG_COLOR);
    }

    /**
     * Special high-visibility logging for game words
     */
    public void logWordInfo(String message) {
        // Create a distinct style for word logs
        Platform.runLater(() -> {
            // Create timestamp
            Text timestamp = new Text(
                java.time.LocalDateTime.now().format(
                    java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
                )
            );
            timestamp.getStyleClass().add(TIMESTAMP_COLOR);
            
            // Create special log level with bold and distinct color
            Text levelText = new Text(" [WORD] ");
            levelText.setFill(Color.PURPLE);
            levelText.setStyle("-fx-font-weight: bold;");
            
            // Create message with distinct style
            Text messageText = new Text(message + "\n");
            messageText.setFill(Color.PURPLE);
            messageText.setStyle("-fx-font-weight: bold;");
            
            // Add to TextFlow
            serverLogsArea.getChildren().addAll(
                new Text("["), timestamp, new Text("] "), levelText, messageText
            );
            
            // Auto-scroll to bottom
            scrollPane.setVvalue(1.0);
        });
    }

    private void logWithLevel(String message, String level, String styleClass) {
        Platform.runLater(() -> {
            // Create timestamp
            Text timestamp = new Text(
                java.time.LocalDateTime.now().format(
                    java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
                )
            );
            timestamp.getStyleClass().add(TIMESTAMP_COLOR);
            
            // Create log level
            Text levelText = new Text(" [" + level + "] ");
            levelText.getStyleClass().add(styleClass);
            
            // Create message
            Text messageText = new Text(message + "\n");
            messageText.getStyleClass().add(styleClass);
            
            // Add to TextFlow
            serverLogsArea.getChildren().addAll(
                new Text("["), timestamp, new Text("] "), levelText, messageText
            );
            
            // Auto-scroll to bottom
            scrollPane.setVvalue(1.0);
        });
    }

    public void cleanup() {
        if (statsTimer != null) {
            statsTimer.cancel();
        }
    }
} 