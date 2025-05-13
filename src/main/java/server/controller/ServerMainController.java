package server.controller;

import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.TextArea;
import javafx.scene.text.Text;
import server.handler.GameServiceImpl;
import server.handler.ServerMain;

import java.time.Duration;
import java.time.Instant;
import java.util.Timer;
import java.util.TimerTask;

public class ServerMainController {
    @FXML private Text serverStatusText;
    @FXML private Button startButton;
    @FXML private Button pauseButton;
    @FXML private Button stopButton;
    @FXML private Text activePlayersText;
    @FXML private Text activeGamesText;
    @FXML private Text uptimeText;
    @FXML private Text memoryUsageText;
    @FXML private TextArea serverLogsArea;
    @FXML private Button clearLogsButton;

    private ServerMain serverMain;
    private GameServiceImpl gameService;
    private Timer statsTimer;
    private Instant serverStartTime;
    private Instant pauseStartTime;
    private Duration totalUptime = Duration.ZERO;
    private boolean isPaused = false;
    private boolean isRunning = false;

    public void setServerMain(ServerMain serverMain) {
        this.serverMain = serverMain;
        this.gameService = null; // Will be set after server is started
    }

    public void initialize() {
        // Do not create a new ServerMain here
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
            logMessage("Server resumed");
        } else {
            // Start new server
            try {
                serverMain.startServer();
                this.gameService = serverMain.getGameService(); // Set after server is started
                serverStartTime = Instant.now();
                totalUptime = Duration.ZERO;
                isRunning = true;
                isPaused = false;
                serverStatusText.setText("Online");
                serverStatusText.setStyle("-fx-fill: #4CAF50;");
                startButton.setDisable(true);
                pauseButton.setDisable(false);
                stopButton.setDisable(false);
                logMessage("Server started successfully");
            } catch (Exception e) {
                logMessage("Error starting server: " + e.getMessage());
            }
        }
    }

    @FXML
    private void handlePauseServer() {
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
        logMessage("Server paused");
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
            logMessage("Server stopped");
        } catch (Exception e) {
            logMessage("Error stopping server: " + e.getMessage());
        }
    }

    @FXML
    private void handleClearLogs() {
        serverLogsArea.clear();
    }

    private void updateStats() {
        if (isRunning && !isPaused) {
            Platform.runLater(() -> {
                try {
                    // Update active players
                    if (gameService != null) {
                        int activePlayers = gameService.getActivePlayers();
                        activePlayersText.setText(String.valueOf(activePlayers));

                        // Update active games
                        int activeGames = gameService.getActiveGames();
                        activeGamesText.setText(String.valueOf(activeGames));
                    } else {
                        activePlayersText.setText("0");
                        activeGamesText.setText("0");
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

                    // Update memory usage
                    long usedMemory = (Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory()) / (1024 * 1024);
                    memoryUsageText.setText(usedMemory + " MB");
                } catch (Exception e) {
                    logMessage("Error updating stats: " + e.getMessage());
                }
            });
        }
    }

    public void logMessage(String message) {
        Platform.runLater(() -> {
            String timestamp = java.time.LocalDateTime.now().format(java.time.format.DateTimeFormatter.ofPattern("HH:mm:ss"));
            serverLogsArea.appendText("[" + timestamp + "] " + message + "\n");
            // Auto-scroll to bottom
            serverLogsArea.setScrollTop(Double.MAX_VALUE);
        });
    }

    public void cleanup() {
        if (statsTimer != null) {
            statsTimer.cancel();
        }
    }
} 