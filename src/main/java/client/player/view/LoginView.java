package client.player.view;

import client.player.controller.LoginViewController;
import client.player.model.LoginModel;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

import java.io.IOException;

public class LoginView {
    private Stage stage;
    private LoginViewController controller;

    public void start(Stage primaryStage) {
        this.stage = primaryStage;

        try {
            // Load the FXML file
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/player/view/LoginView.fxml"));
            Parent root = loader.load();

            // Get the controller
            controller = loader.getController();
            controller.setStage(stage);

            // Set up the scene
            Scene scene = new Scene(root);
            scene.getStylesheets().add(getClass().getResource("/client/player/view/login.css").toExternalForm()); // Apply CSS

            // Set the scene to the stage
            stage.setScene(scene);
            stage.setTitle("Minecraft Login");
            stage.setResizable(false);

            // Set the stage size before showing it
            stage.setWidth(450);
            stage.setHeight(450);

        } catch (IOException e) {
            System.err.println("Error loading FXML: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public LoginViewController getController() {
        return controller;
    }

    public void setVisible(boolean visible) {
        if (visible) {
            stage.show();
        } else {
            stage.hide();
        }
    }

    public String getUsername() {
        return controller.getUsername();
    }

    public String getPassword() {
        return controller.getPassword();
    }

    public void setStatus(String message, boolean isError) {
        controller.setStatus(message, isError);
    }


    public void close() {
        stage.close();
    }

    public void setModel(LoginModel model) {
        controller.setModel(model);
    }

    public void setShowLoginViewAgain(Runnable showLoginViewAgain) {
        controller.setShowLoginViewAgain(showLoginViewAgain);
    }

    public Stage getStage() {
        return stage;
    }
}
