package client.admin;

import client.admin.view.AdminLoginView;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.scene.control.Alert;
import javafx.stage.Stage;

public class AdminApplication extends Application {
    @Override
    public void start(Stage primaryStage) {
        try {
            // Start the AdminLoginView which handles its own connection and navigation
            AdminLoginView loginView = new AdminLoginView();
            loginView.start(primaryStage);
        } catch (Exception e) {
            showError("Error", "Could not start Admin Login: " + e.getMessage());
            Platform.exit();
        }
    }

    private void showError(String title, String message) {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }

    public static void main(String[] args) {
        launch(args);
    }
}