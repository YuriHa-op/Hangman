package client.admin.controller;

import GameModule.GameService;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import java.util.function.Consumer;

public class PlayerManagementController {
    @FXML
    private TextField usernameField;
    
    @FXML
    private TextField newUsernameField;
    
    @FXML
    private TextField passwordField;
    
    @FXML
    private TextField winsField;

    @FXML
    private ComboBox<String> updateTypeComboBox;

    @FXML
    private VBox firstStage;

    @FXML
    private VBox secondStage;

    private GameService gameService;
    private Consumer<String> outputCallback;
    private Stage stage;
    private String selectedUpdateType;
    private String existingUsername;

    @FXML
    public void initialize() {
        // Only initialize the combo box if it exists (Update Player view)
        if (updateTypeComboBox != null) {
            ObservableList<String> updateTypes = FXCollections.observableArrayList(
                "Username", "Password", "Wins"
            );
            updateTypeComboBox.setItems(updateTypes);
        }
    }

    public void setGameService(GameService gameService) {
        this.gameService = gameService;
    }

    public void setOutputCallback(Consumer<String> outputCallback) {
        this.outputCallback = outputCallback;
    }

    public void setStage(Stage stage) {
        this.stage = stage;
    }

    @FXML
    public void handleCancel() {
        if (stage != null) {
            stage.close();
        }
    }

    @FXML
    public void handleBack() {
        firstStage.setVisible(true);
        secondStage.setVisible(false);
    }

    @FXML
    public void handleCheckPlayer() {
        if (gameService == null) {
            showError("Error", "Game service is not initialized");
            return;
        }

        String username = usernameField.getText().trim();
        if (username.isEmpty()) {
            showError("Error", "Username cannot be empty");
            return;
        }

        selectedUpdateType = updateTypeComboBox.getValue();
        if (selectedUpdateType == null) {
            showError("Error", "Please select what to update");
            return;
        }

        try {
            String playersList = gameService.viewPlayers();
            if (playerExists(username, playersList)) {
                existingUsername = username;
                // Enable only the selected field in the second stage
                enableSelectedField(selectedUpdateType);
                // Show second stage
                firstStage.setVisible(false);
                secondStage.setVisible(true);
            } else {
                showError("Error", "Player '" + username + "' does not exist");
            }
        } catch (Exception e) {
            showError("Error", "Failed to check player: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private void enableSelectedField(String updateType) {
        // Disable all fields first
        newUsernameField.setDisable(true);
        passwordField.setDisable(true);
        winsField.setDisable(true);

        // Enable only the selected field
        switch (updateType) {
            case "Username":
                newUsernameField.setDisable(false);
                break;
            case "Password":
                passwordField.setDisable(false);
                break;
            case "Wins":
                winsField.setDisable(false);
                break;
        }
    }

    @FXML
    public void handleUpdatePlayer() {
        if (existingUsername == null) {
            showError("Error", "Please check if player exists first");
            return;
        }

        try {
            boolean success = false;
            switch (selectedUpdateType) {
                case "Username":
                    String newUsername = newUsernameField.getText().trim();
                    if (newUsername.isEmpty()) {
                        showError("Error", "New username cannot be empty");
                        return;
                    }
                    success = gameService.updatePlayerUsername(existingUsername, newUsername);
                    break;
                case "Password":
                    String newPassword = passwordField.getText().trim();
                    if (newPassword.isEmpty()) {
                        showError("Error", "New password cannot be empty");
                        return;
                    }
                    success = gameService.updatePlayerPassword(existingUsername, newPassword);
                    break;
                case "Wins":
                    String wins = winsField.getText().trim();
                    if (wins.isEmpty()) {
                        showError("Error", "Wins cannot be empty");
                        return;
                    }
                    success = gameService.updatePlayerWins(existingUsername, Integer.parseInt(wins));
                    break;
            }

            if (success) {
                outputCallback.accept("Player updated successfully: " + existingUsername);
                if (stage != null) {
                    stage.close();
                }
            } else {
                showError("Error", "Failed to update player");
            }
        } catch (NumberFormatException e) {
            showError("Error", "Wins must be a valid number");
        } catch (Exception e) {
            showError("Error", "Failed to update player: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private boolean playerExists(String username, String playersList) {
        String normalizedUsername = username.toLowerCase().trim();
        String[] lines = playersList.split("\n");

        for (String line : lines) {
            if (line.contains("Username:")) {
                int start = line.indexOf("Username:") + 10;
                int end = line.indexOf("|", start);
                if (end > start) {
                    String playerName = line.substring(start, end).trim().toLowerCase();
                    if (playerName.equals(normalizedUsername)) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    @FXML
    public void handleAddPlayer() {
        if (gameService == null) {
            showError("Error", "Game service is not initialized");
            return;
        }

        String username = usernameField.getText().trim();
        String password = passwordField.getText().trim();

        if (username.isEmpty() || password.isEmpty()) {
            showError("Error", "Username and password cannot be empty");
            return;
        }

        try {
            boolean success = gameService.createPlayer(username, password);
            if (success) {
                outputCallback.accept("Player created successfully: " + username);
                if (stage != null) {
                    stage.close();
                }
            } else {
                showError("Error", "Failed to create player. Username may already exist.");
            }
        } catch (Exception e) {
            showError("Error", "Failed to create player: " + e.getMessage());
            e.printStackTrace(); // Add stack trace for debugging
        }
    }

    @FXML
    public void handleDeletePlayer() {
        if (gameService == null) {
            showError("Error", "Game service is not initialized");
            return;
        }

        String username = usernameField.getText().trim();

        if (username.isEmpty()) {
            showError("Error", "Username cannot be empty");
            return;
        }

        try {
            // Check if player exists first
            String playersList = gameService.viewPlayers();
            if (!playerExists(username, playersList)) {
                showError("Error", "Player '" + username + "' does not exist");
                return;
            }

            Alert confirm = new Alert(Alert.AlertType.CONFIRMATION);
            confirm.setTitle("Confirm Deletion");
            confirm.setHeaderText("Delete player: " + username);
            confirm.setContentText("Are you sure you want to delete this player?");
            
            // Style the dialog
            DialogPane dialogPane = confirm.getDialogPane();
            dialogPane.getStyleClass().add("minecraft-dialog");
            dialogPane.getStylesheets().add(getClass().getResource("/client/admin/view/player-management.css").toExternalForm());
            
            // Set custom button text
            ButtonType yesButton = new ButtonType("Yes", ButtonBar.ButtonData.OK_DONE);
            ButtonType noButton = new ButtonType("No", ButtonBar.ButtonData.CANCEL_CLOSE);
            confirm.getButtonTypes().setAll(yesButton, noButton);

            // Style the buttons
            for (ButtonType buttonType : confirm.getButtonTypes()) {
                Button button = (Button) dialogPane.lookupButton(buttonType);
                if (buttonType == yesButton) {
                    button.getStyleClass().add("minecraft-button-delete");
                } else {
                    button.getStyleClass().add("minecraft-button-cancel");
                }
            }

            if (confirm.showAndWait().get() == yesButton) {
                boolean success = gameService.deletePlayer(username);
                if (success) {
                    outputCallback.accept("Player deleted successfully: " + username);
                    if (stage != null) {
                        stage.close();
                    }
                } else {
                    showError("Error", "Failed to delete player");
                }
            }
        } catch (Exception e) {
            showError("Error", "Failed to delete player: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private void showError(String title, String message) {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.getDialogPane().getStyleClass().add("minecraft-dialog");
        alert.showAndWait();
    }
} 