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
            // Fetch statistics from server
            GameModule.SystemStatisticsDTO stats = gameService.getSystemStatistics();
            int totalGames = (int) stats.totalGames;
            int wins = (int) stats.wins;
            int losses = (int) stats.losses;
            double winRate = stats.winRate;
            int waitingTime = (int) stats.waitingTime;
            int roundTime = (int) stats.roundTime;

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
            if (pieChartData.size() > 0 && pieChartData.get(0).getNode() != null)
                pieChartData.get(0).getNode().setStyle("-fx-pie-color: #4CAF50;"); // Green for wins
            if (pieChartData.size() > 1 && pieChartData.get(1).getNode() != null)
                pieChartData.get(1).getNode().setStyle("-fx-pie-color: #F44336;"); // Red for losses

            // Display current settings in UI
            waitingTimeField.setText(String.valueOf(waitingTime));
            roundTimeField.setText(String.valueOf(roundTime));
            currentSettings = new SystemSettings(waitingTime, roundTime);
        } catch (Exception e) {
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

}