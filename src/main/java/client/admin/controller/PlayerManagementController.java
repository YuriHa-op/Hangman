package client.admin.controller;

import AdminModule.AdminService;
import AdminModule.Bool;
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

    private AdminService adminService;
    private Consumer<String> outputCallback;
    private Stage stage;
    private String selectedUpdateType;
    private String existingUsername;
    private Runnable onSuccessfulActionCallback;

    public void setOnSuccessfulActionCallback(Runnable onSuccessfulActionCallback) {
        this.onSuccessfulActionCallback = onSuccessfulActionCallback;
    }

    @FXML
    public void initialize() {
        if (updateTypeComboBox != null) {
            ObservableList<String> updateTypes = FXCollections.observableArrayList(
                "Username", "Password", "Wins"
            );
            updateTypeComboBox.setItems(updateTypes);
        }
    }

    public void setAdminService(AdminService adminService) {
        this.adminService = adminService;
    }

    public void setOutputCallback(Consumer<String> outputCallback) {
        this.outputCallback = outputCallback;
    }

    public void setStage(Stage stage) {
        this.stage = stage;
    }

    public void setUsernameForUpdate(String username) {
        if (usernameField != null) {
            usernameField.setText(username);
            usernameField.setDisable(true);
        }
        this.existingUsername = username;
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
        if (adminService == null) {
            showError("Error", "Admin service is not initialized");
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
            String playersList = adminService.viewPlayers();
            if (playerExists(username, playersList)) {
                existingUsername = username;
                enableSelectedField(selectedUpdateType);
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
        newUsernameField.setDisable(true);
        passwordField.setDisable(true);
        winsField.setDisable(true);

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
            showError("Error", "Please check if player exists first or ensure player was selected.");
            return;
        }
        if (selectedUpdateType == null) {
            showError("Error", "Update type not selected. Please go back and select what to update or ensure it's selected.");
            return;
        }

        try {
            Bool success = Bool.BOOL_FALSE;
            switch (selectedUpdateType) {
                case "Username":
                    String newUsername = newUsernameField.getText().trim();
                    if (newUsername.isEmpty()) {
                        showError("Error", "New username cannot be empty");
                        return;
                    }
                    success = adminService.updatePlayerUsername(existingUsername, newUsername);
                    break;
                case "Password":
                    String newPassword = passwordField.getText().trim();
                    if (newPassword.isEmpty()) {
                        showError("Error", "New password cannot be empty");
                        return;
                    }
                    success = adminService.updatePlayerPassword(existingUsername, newPassword);
                    break;
                case "Wins":
                    String wins = winsField.getText().trim();
                    if (wins.isEmpty()) {
                        showError("Error", "Wins cannot be empty");
                        return;
                    }
                    success = adminService.updatePlayerWins(existingUsername, Integer.parseInt(wins));
                    break;
                default: 
                    showError("Error", "Update type not selected. Please go back and select what to update.");
                    return;
            }

            if (success == Bool.BOOL_TRUE) {
                outputCallback.accept("Player updated successfully: " + existingUsername);
                if (onSuccessfulActionCallback != null) {
                    onSuccessfulActionCallback.run();
                }
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
        if (playersList == null) {
            return false;
        }

        // Simple check - if the username appears anywhere in the player list
        // Could be improved with regex for exact matching
        return playersList.toLowerCase().contains("username: " + username.toLowerCase());
    }

    @FXML
    public void handleAddPlayer() {
        String username = usernameField.getText().trim();
        String password = passwordField.getText().trim();

        if (username.isEmpty() || password.isEmpty()) {
            showError("Error", "Username and password cannot be empty");
            return;
        }

        try {
            Bool success = adminService.createPlayer(username, password);
            if (success == Bool.BOOL_TRUE) {
                outputCallback.accept("Player created successfully: " + username);
                if (onSuccessfulActionCallback != null) {
                    onSuccessfulActionCallback.run();
                }
                if (stage != null) {
                    stage.close();
                }
            } else {
                showError("Error", "Failed to create player. Username may already exist.");
            }
        } catch (Exception e) {
            showError("Error", "Failed to create player: " + e.getMessage());
            e.printStackTrace();
        }
    }

    @FXML
    public void handleDeletePlayer() {
        String username = usernameField.getText().trim();
        if (username.isEmpty()) {
            showError("Error", "Username cannot be empty");
            return;
        }

        Alert confirmDialog = new Alert(Alert.AlertType.CONFIRMATION);
        confirmDialog.setTitle("Confirm Delete");
        confirmDialog.setHeaderText(null);
        confirmDialog.setContentText("Are you sure you want to delete player '" + username + "'?");
        confirmDialog.getDialogPane().getStyleClass().add("minecraft-dialog"); // Assuming this CSS class exists

        confirmDialog.showAndWait().ifPresent(result -> {
            if (result == ButtonType.OK) {
                try {
                    Bool success = adminService.deletePlayer(username);
                    if (success == Bool.BOOL_TRUE) {
                        outputCallback.accept("Player deleted successfully: " + username);
                        if (onSuccessfulActionCallback != null) {
                            onSuccessfulActionCallback.run();
                        }
                        if (stage != null) {
                            stage.close();
                        }
                    } else {
                        showError("Error", "Failed to delete player. Player might not exist.");
                    }
                } catch (Exception e) {
                    showError("Error", "Failed to delete player: " + e.getMessage());
                    e.printStackTrace();
                }
            }
        });
    }

    private void showError(String title, String message) {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.getDialogPane().getStyleClass().add("minecraft-dialog"); // Assuming this CSS class exists
        alert.showAndWait();
    }
} 