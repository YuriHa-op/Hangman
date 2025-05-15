package client.admin.view;

import GameModule.GameService;
import client.admin.controller.AdminViewController;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

public class AdminView {
    private Stage stage;
    private AdminViewController controller;

    public void start(Stage primaryStage, GameService gameService, Runnable onLogout) {
        this.stage = primaryStage;
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/client/admin/view/AdminView.fxml"));
            Parent root = loader.load();
            controller = loader.getController();
            controller.setStage(stage);
            controller.setGameService(gameService);
            controller.setOnLogout(onLogout);

            Scene scene = new Scene(root);
            scene.getStylesheets().add(getClass().getResource("/client/admin/view/admin.css").toExternalForm());
            stage.setScene(scene);
            stage.setTitle("Admin Panel - What's The Word");
            stage.setResizable(false);
            stage.setWidth(1000);
            stage.setHeight(850);
        } catch (Exception e) {
            System.err.println("Error loading AdminView: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public void show() {
        stage.show();
    }

    public void close() {
        stage.close();
    }
}