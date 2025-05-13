package client.admin.controller;

import GameModule.GameService;
import client.admin.model.SystemSettings;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.geometry.Insets;
import javafx.scene.chart.PieChart;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.stage.Stage;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.function.Consumer;

public class SystemStatisticsController {
    @FXML
    private Label totalGamesLabel;
    @FXML
    private Label winsLabel;
    @FXML
    private Label lossesLabel;
    @FXML
    private Label winRateLabel;
    @FXML
    private PieChart gameResultsChart;
    @FXML
    private TextField waitingTimeField;
    @FXML
    private TextField roundTimeField;

    private GameService gameService;
    private Stage stage;
    private Consumer<String> outputCallback;
    private SystemSettings currentSettings;

    // Database connection constants
<<<<<<< HEAD
    private static final String DB_URL = "jdbc:mysql://localhost:3306/game";
=======
    private static final String DB_URL = "jdbc:mysql://192.168.254.125:3306/game";
>>>>>>> main
    private static final String DB_USER = "root";
    private static final String DB_PASSWORD = "";

    public void initialize() {
        // Validation for time inputs (only allow numbers)
        waitingTimeField.textProperty().addListener((observable, oldValue, newValue) -> {
            if (!newValue.matches("\\d*")) {
                waitingTimeField.setText(oldValue);
            }
        });

        roundTimeField.textProperty().addListener((observable, oldValue, newValue) -> {
            if (!newValue.matches("\\d*")) {
                roundTimeField.setText(oldValue);
            }
        });
    }

    public void setGameService(GameService gameService) {
        this.gameService = gameService;
    }

    public void setStage(Stage stage) {
        this.stage = stage;
    }

    public void setOutputCallback(Consumer<String> outputCallback) {
        this.outputCallback = outputCallback;
    }

    public void loadStatistics() {
        try {
            // Fetch game statistics from database
            int totalGames = 0;
            int wins = 0;

            try (Connection conn = getConnection();
                 PreparedStatement totalGamesStmt = conn.prepareStatement("SELECT COUNT(*) FROM game_results");
                 PreparedStatement winsStmt = conn.prepareStatement("SELECT COUNT(*) FROM game_results WHERE win_status = 1")) {

                // Get total games
                ResultSet totalGamesRs = totalGamesStmt.executeQuery();
                if (totalGamesRs.next()) {
                    totalGames = totalGamesRs.getInt(1);
                }

                // Get wins
                ResultSet winsRs = winsStmt.executeQuery();
                if (winsRs.next()) {
                    wins = winsRs.getInt(1);
                }
            }

            int losses = totalGames - wins;
            double winRate = totalGames > 0 ? (double) wins / totalGames * 100 : 0;

            totalGamesLabel.setText(String.valueOf(totalGames));
            winsLabel.setText(String.valueOf(wins));
            lossesLabel.setText(String.valueOf(losses));
            winRateLabel.setText(String.format("%.1f%%", winRate));

            // Create pie chart data
            ObservableList<PieChart.Data> pieChartData = FXCollections.observableArrayList(
                    new PieChart.Data("Wins", wins),
                    new PieChart.Data("Losses", losses)
            );
            gameResultsChart.setData(pieChartData);

            // Apply colors to pie chart slices
            pieChartData.get(0).getNode().setStyle("-fx-pie-color: #4CAF50;"); // Green for wins
            pieChartData.get(1).getNode().setStyle("-fx-pie-color: #F44336;"); // Red for losses

            // Load current settings from database
            try (Connection conn = getConnection();
                 PreparedStatement settingsStmt = conn.prepareStatement("SELECT waiting_time_seconds, round_time_seconds FROM settings WHERE id = 1")) {

                ResultSet settingsRs = settingsStmt.executeQuery();
                if (settingsRs.next()) {
                    int waitingTime = settingsRs.getInt("waiting_time_seconds");
                    int roundTime = settingsRs.getInt("round_time_seconds");
                    currentSettings = new SystemSettings(waitingTime, roundTime);
                } else {
                    // If no settings in database, use default values
                    currentSettings = new SystemSettings(10, 30);
                }
            }

            // Display current settings in UI
            waitingTimeField.setText(String.valueOf(currentSettings.getWaitingTimeSeconds()));
            roundTimeField.setText(String.valueOf(currentSettings.getRoundTimeSeconds()));
        } catch (SQLException e) {
            e.printStackTrace();
            if (outputCallback != null) {
                outputCallback.accept("Error loading statistics: " + e.getMessage());
            }
            // Use default values if there's an error
            currentSettings = new SystemSettings(10, 30);
        }
    }

    @FXML
    private void handleSaveSettings() {
        try {
            int waitingTime = Integer.parseInt(waitingTimeField.getText());
            int roundTime = Integer.parseInt(roundTimeField.getText());

            // Validate inputs
            if (waitingTime < 5 || waitingTime > 60) {
                outputCallback.accept("Waiting time must be between 5 and 60 seconds");
                return;
            }

            if (roundTime < 10 || roundTime > 300) {
                outputCallback.accept("Round time must be between 10 and 300 seconds");
                return;
            }

            // Update settings using the gameService
            boolean success = gameService.updateSettings(waitingTime, roundTime);

            if (success) {
                currentSettings.setWaitingTimeSeconds(waitingTime);
                currentSettings.setRoundTimeSeconds(roundTime);
                outputCallback.accept("Game settings updated successfully");
            } else {
                outputCallback.accept("Failed to update game settings");
            }
        } catch (NumberFormatException e) {
            outputCallback.accept("Please enter valid numbers for time settings");
        } catch (Exception e) {
            outputCallback.accept("Error updating settings: " + e.getMessage());
        }
    }

    @FXML
    private void handleClose() {
        stage.close();
    }

    private Connection getConnection() throws SQLException {
        return DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
    }
}